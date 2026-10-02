"""Plan first; explicitly install an isolated pinned runtime, verify, optionally smoke.

Run from the repository root with Python 3.12. Default: JSON plan, no mutation,
network, Torch import or model loading. See docs/AGENT_SETUP.md for the contract.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import venv

from runtime.device_profiles import MIN_RAM_GIB, PROFILES, PROFILE_STATUS, is_cpu
from runtime.hardware_probe import GIB, probe
from runtime.model_registry import DEFAULT_MODEL, MODEL_KEYS, get_model, validation_status
from runtime.model_assets import inspect_files, load_manifest

ROOT = Path(__file__).resolve().parents[1]
MARKER = '.clef-managed-environment.json'


class SetupError(RuntimeError):
    def __init__(self, message, exit_code=2):
        super().__init__(message)
        self.exit_code = exit_code


def requirements(profile):
    filename = 'requirements_frozen.txt' if is_cpu(profile) else 'requirements_rocm.txt'
    lines = (ROOT / 'runtime' / filename).read_text().splitlines()
    pins = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
    if any('==' not in line or any(ch in line for ch in (' ', '/', '@', ';')) for line in pins):
        raise SetupError('Runtime requirements must contain exact package==version pins only')
    return pins


def env_python(folder):
    return Path(folder) / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')


def dependency_fingerprint(profile):
    return hashlib.sha256('\n'.join(requirements(profile)).encode()).hexdigest()


def make_plan(args, hardware=None):
    model = get_model(args.model)
    model_dir = args.model_dir.expanduser().resolve()
    environment = args.venv.expanduser().resolve()
    hardware = probe(model_dir) if hardware is None else hardware
    manifest = load_manifest(args.model)
    files = inspect_files(model_dir, manifest, hashes=False)
    blocked = []
    notes = []
    environment_install_needed = True
    if not (args.use_existing_runtime or args.verify):
        active = {Path(sys.prefix).resolve()}
        if os.environ.get('VIRTUAL_ENV'):
            active.add(Path(os.environ['VIRTUAL_ENV']).expanduser().resolve())
        if environment in active:
            blocked.append('The selected venv is active. Use --use-existing-runtime for read-only checks, or choose a separate --venv; active packages will not be changed.')
    if hardware['python'].split('.')[:2] != ['3', '12']:
        blocked.append('Use Python 3.12 for this pinned setup (tested version: 3.12.14); the offline viewer is separate.')
    if hardware['architecture'].lower() not in ('x86_64', 'amd64') or hardware['os'] not in ('Linux', 'Windows'):
        blocked.append('Automatic setup is prepared only for Linux/Windows x86-64; other platforms require a reviewed new dependency profile.')
    if hardware['os'] == 'Windows':
        notes.append('Windows execution is prepared, not validated. It still must pass package, kernel and actual-model smoke checks.')
        if not args.allow_untested_platform:
            blocked.append('Windows execution requires explicitly acknowledging its unvalidated status with --allow-untested-platform.')
    if is_cpu(args.profile):
        if hardware['cpu']['avx2'] is False:
            blocked.append('This x86 CPU lacks AVX2; the pinned CPU quantizer is unsupported. No alternate backend is selected.')
        if hardware['os'] == 'Linux':
            libc, version = hardware['libc']
            if libc != 'glibc' or not version:
                blocked.append('Pinned Linux wheels require glibc; musl/unknown libc is not an automatic-install target.')
            elif tuple(int(p) for p in version.split('.')[:2]) < (2, 28):
                blocked.append('Use a supported OS with glibc >= 2.28 for the combined pinned runtime wheels; do not replace libc in place.')
    else:
        notes.append('ROCm requires an existing, separately approved AMD Torch/Torchvision environment for the exact OS and device. This tool never installs GPU drivers or GPU wheels.')
        if not args.use_existing_runtime:
            blocked.append('For ROCm, supply --venv PATH --use-existing-runtime after preparing the matched AMD environment in docs/AMD_GPU.md.')
    available = hardware['memory']['available_bytes']
    if available is None:
        blocked.append('Available physical RAM could not be measured; no model setup/load is authorized by this probe.')
    elif available < model['min_ram_gib'][args.profile] * GIB:
        blocked.append(f"Only {available / GIB:.2f} GiB available RAM; {args.model}/{args.profile} requires at least {model['min_ram_gib'][args.profile]:g} GiB before loading. Close other models yourself and retry; swap is not a substitute.")
    # Same-size existing files are only potential reuse until execution hashes them.
    model_reserve = files['missing_bytes'] + (3 * GIB if files['missing'] else 0)
    if hardware['disk']['free_bytes'] < model_reserve:
        blocked.append(f'Model filesystem needs {model_reserve} free bytes for missing files plus reserve; select another --model-dir or free space yourself.')
    if files['invalid']:
        blocked.append('Wrong-size/invalid model files exist: ' + ', '.join(files['invalid']) + '. They will not be overwritten.')
    if args.offline and files['missing']:
        blocked.append('Offline mode cannot fetch missing model files; supply a complete previously verified model directory.')
    if args.use_existing_runtime or args.verify:
        if not env_python(environment).is_file():
            blocked.append(f'Existing runtime Python is missing: {env_python(environment)}')
    elif environment.exists():
        marker = environment / MARKER
        if not marker.is_file():
            blocked.append('Selected venv already exists and is not managed by this setup; choose a new path or --use-existing-runtime (read-only dependency checks).')
        else:
            try:
                saved = json.loads(marker.read_text())
            except (OSError, ValueError):
                saved = {}
            if saved.get('dependency_sha256') != dependency_fingerprint(args.profile):
                blocked.append('Managed venv was created with a different dependency lock. Choose a fresh --venv; no in-place upgrades.')
            elif saved.get('complete') and env_python(environment).is_file():
                environment_install_needed = False
    if args.offline and environment_install_needed and not (args.use_existing_runtime or args.verify):
        blocked.append('Offline execution requires a complete existing runtime; use --verify with the prepared venv or permit an online isolated install.')
    if not args.use_existing_runtime and not args.verify and environment_install_needed:
        # Check both filesystems independently; reserve model bytes as well if
        # using one filesystem. Actual writes are rechecked before downloading.
        from runtime.hardware_probe import existing_parent
        import shutil
        base = existing_parent(environment)
        same_fs = base.stat().st_dev == existing_parent(model_dir).stat().st_dev
        needed = 8 * GIB + (model_reserve if same_fs else 0)
        if shutil.disk_usage(base).free < needed:
            blocked.append(f'Venv filesystem needs {needed} free bytes (8 GiB environment reserve plus same-filesystem model download).')
    if validation_status(args.model, args.profile) != 'tested_linux_x86_64':
        notes.append('This profile is prepared and mock-tested only. A successful probe is not a Clef forward-pass or accuracy result.')
    notes.extend(['9B/27B is the explicit model family; NF4/BF16/FP16 is a separate precision choice.',
                  'NF4 quantizes on load from the SAME full BF16 release; it does not reduce this download.',
                  'No GGUF, NPU, NVIDIA, DirectML or automatic backend/model fallback is implemented.',
                  'Do not run setup/model smoke concurrently with another model, live server or benchmark process.'])
    python = str(env_python(environment))
    return {'schema_version': 1, 'status': 'blocked' if blocked else 'plan_ready', 'mode': 'plan',
            'mutations_performed': False, 'model_loaded': False,
            'profile': args.profile, 'profile_validation': validation_status(args.model, args.profile),
            'hardware': hardware, 'blockers': blocked, 'notes': notes,
            'model': {'key': args.model, 'id': model['repo_id'], 'size': model['model_size'], 'revision': model['revision'], 'dir': str(model_dir),
                      'release_bytes': sum(item['bytes'] for item in manifest.values()),
                      'files': files, 'hashes_checked': False},
            'runtime': {'venv': str(environment), 'python': python,
                        'dependency_sha256': dependency_fingerprint(args.profile),
                        'pins': requirements(args.profile), 'existing_read_only': args.use_existing_runtime},
            'steps': ['Check platform, RAM, disk and ownership', 'Create isolated venv/install exact CPU pins (unless existing runtime)',
                      'Check package versions and pip check', 'Test tiny selected-backend kernels without loading Clef',
                      'Hash existing release, download only missing pinned files if permitted, verify every SHA-256',
                      'Run one synthetic actual-model smoke' if args.smoke else 'Stop before model loading; actual-model readiness remains unverified'],
            'start_server_argv': [python, 'server.py', '--enable-inference', '--model-dir', str(model_dir),
                                  '--model', args.model, '--inference-profile', args.profile, '--device-index', str(args.device_index)],
            'verify_argv': [sys.executable, '-m', 'runtime.setup', '--model', args.model, '--profile', args.profile, '--venv', str(environment),
                            '--model-dir', str(model_dir), '--verify', '--offline']}


def run(command, json_output=False, exit_code=3, env=None):
    print('Running: ' + ' '.join(str(part) for part in command), file=sys.stderr, flush=True)
    process = subprocess.run([str(part) for part in command], cwd=ROOT, env=env,
                             stdout=subprocess.PIPE if json_output else sys.stderr,
                             stderr=subprocess.PIPE if json_output else None, text=True)
    if process.returncode:
        detail = ((process.stderr or '') + '\n' + (process.stdout or '')).strip()[-6000:] if json_output else 'See command output above.'
        raise SetupError(f'Command exited {process.returncode}: {detail}', exit_code)
    if json_output:
        try:
            return json.loads(process.stdout)
        except ValueError as error:
            raise SetupError('Command did not return valid JSON; see runtime compatibility guidance', exit_code) from error


def check_dependencies(python, profile):
    code = "import importlib.metadata as m,json,sys; wanted=json.loads(sys.argv[1]); got={}; missing=[]\nfor p in wanted:\n n,v=p.split('==');\n try: got[n]=m.version(n)\n except m.PackageNotFoundError: missing.append(n)\nprint(json.dumps({'python':list(sys.version_info[:2]),'versions':got,'missing':missing,'mismatched':[p for p in wanted if p.split('==')[0] in got and got[p.split('==')[0]] != p.split('==')[1]]}))"
    found = run([python, '-c', code, json.dumps(requirements(profile))], json_output=True)
    if found['missing'] or found['mismatched'] or found['python'] != [3, 12]:
        raise SetupError('Dependency check failed: ' + json.dumps(found)
                         + '. Use a fresh managed CPU venv or complete the separately approved AMD environment; no automatic upgrades.', 3)
    run([python, '-m', 'pip', 'check'])
    return found


def install_cpu_environment(args):
    folder = args.venv.expanduser().resolve()
    python = env_python(folder)
    marker = folder / MARKER
    if not marker.is_file():
        folder.mkdir(parents=True, exist_ok=False)
        marker.write_text(json.dumps({'schema_version': 1, 'dependency_sha256': dependency_fingerprint(args.profile),
                                      'purpose': 'isolated Clef CPU setup', 'complete': False}, indent=2) + '\n')
    if not python.is_file():
        try:
            venv.EnvBuilder(with_pip=True, system_site_packages=False).create(folder)
        except (OSError, subprocess.SubprocessError) as error:
            raise SetupError('Could not create the isolated venv. Ensure Python 3.12 venv/ensurepip support is installed; no system package was changed. ' + str(error), 3) from error
    # A completed owned environment is checked, never silently changed/upgraded.
    if json.loads(marker.read_text()).get('complete'):
        return check_dependencies(python, args.profile)
    if args.offline:
        raise SetupError('Offline mode cannot install packages. Use --verify with a complete venv or retry the same command online.', 3)
    pins = requirements(args.profile)
    torch_pins = [pin for pin in pins if pin.split('==')[0] in ('torch', 'torchvision')]
    app_pins = [pin for pin in pins if pin not in torch_pins]
    clean_env = {key: value for key, value in os.environ.items() if not key.startswith('PIP_')}
    clean_env.update(PIP_CONFIG_FILE=os.devnull, PIP_NO_INPUT='1', PIP_DISABLE_PIP_VERSION_CHECK='1', PIP_NO_CACHE_DIR='1')
    for index, selected in [('https://download.pytorch.org/whl/cpu', torch_pins), ('https://pypi.org/simple', app_pins)]:
        run([python, '-m', 'pip', 'install', '--no-deps', '--only-binary=:all:', '--index-url', index, *selected], env=clean_env)
    found = check_dependencies(python, args.profile)
    record = json.loads(marker.read_text())
    record['complete'] = True
    marker.write_text(json.dumps(record, indent=2) + '\n')
    return found


@contextmanager
def execution_lock():
    folder = ROOT / '.clef'
    folder.mkdir(exist_ok=True)
    path = folder / 'setup.lock'
    try:
        handle = path.open('x')
    except FileExistsError as error:
        raise SetupError('Another setup may be active (.clef/setup.lock). Do not start a second model. If interrupted, confirm its PID has stopped before removing the lock.', 2) from error
    try:
        with handle:
            handle.write(json.dumps({'pid': os.getpid(), 'started': datetime.now(timezone.utc).isoformat()}))
        yield
    finally:
        path.unlink(missing_ok=True)


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument('--profile', choices=PROFILES, default='cpu-nf4')
    result.add_argument('--model', choices=MODEL_KEYS, default=DEFAULT_MODEL, help='Explicit model selection; never auto-downloads the larger variant')
    result.add_argument('--venv', type=Path, help='Default: .venvs/clef-PROFILE; never reuse an active/unowned environment')
    result.add_argument('--model-dir', type=Path, help='Defaults to a separate folder for each model')
    result.add_argument('--device-index', type=int, default=0)
    mode = result.add_mutually_exclusive_group()
    mode.add_argument('--plan', '--dry-run', action='store_true', help='Read-only JSON plan (the default)')
    mode.add_argument('--execute', action='store_true', help='Explicitly permit isolated package install and pinned public model download')
    mode.add_argument('--verify', action='store_true', help='Check an existing runtime/model only; no package install or network')
    result.add_argument('--smoke', action='store_true', help='Also explicitly permit loading the full selected model and a synthetic forward pass')
    result.add_argument('--offline', action='store_true', help='Require all packages and model files to be present already')
    result.add_argument('--use-existing-runtime', action='store_true', help='Only inspect packages; never install/upgrade this venv (required for ROCm)')
    result.add_argument('--allow-untested-platform', action='store_true', help='Acknowledge prepared-but-unvalidated Windows execution')
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    if args.venv is None:
        args.venv = ROOT / '.venvs' / ('clef-' + args.profile)
    if args.model_dir is None:
        args.model_dir = ROOT / get_model(args.model)['default_model_dir']
    args.venv = args.venv.expanduser().resolve()
    args.model_dir = args.model_dir.expanduser().resolve()
    from runtime.device_profiles import validate_profile
    try:
        validate_profile(args.profile, args.device_index)
        plan = make_plan(args)
        if not (args.execute or args.verify):
            print(json.dumps(plan, indent=2))
            return 0
        if plan['blockers']:
            raise SetupError('; '.join(plan['blockers']))
        if args.verify:
            args.offline = True
        with execution_lock():
            python = env_python(args.venv.expanduser().resolve())
            packages = check_dependencies(python, args.profile) if args.verify or args.use_existing_runtime else install_cpu_environment(args)
            backend = run([python, '-m', 'runtime.check_backend', '--profile', args.profile,
                           '--model', args.model, '--device-index', args.device_index, '--test-kernel'], json_output=True, exit_code=5)
            command = [python, '-m', 'runtime.model_assets', '--model', args.model, '--model-dir', args.model_dir]
            command += ['--offline'] if args.offline else ['--download']
            model = run(command, json_output=True, exit_code=4)
            smoke = None
            if args.smoke:
                smoke = run([python, '-m', 'runtime.smoke_ready', '--profile', args.profile,
                             '--model', args.model, '--device-index', args.device_index, '--model-dir', args.model_dir], json_output=True, exit_code=6)
            report = {'schema_version': 1, 'status': 'model_smoke_passed' if smoke else 'environment_prepared_model_not_loaded',
                      'timestamp': datetime.now(timezone.utc).isoformat(), 'profile': args.profile,
                      'profile_validation': validation_status(args.model, args.profile), 'model': model, 'backend': backend,
                      'packages': packages, 'runtime': plan['runtime'], 'smoke': smoke,
                      'start_server_argv': plan['start_server_argv'],
                      'limitations': ['A smoke is not an accuracy, performance, or production-safety benchmark.']}
            if args.execute:
                (ROOT / '.clef' / f'setup-{args.model}-{args.profile}.json').write_text(json.dumps(report, indent=2) + '\n')
            print(json.dumps(report, indent=2))
        return 0
    except (SetupError, OSError, ValueError) as error:
        code = getattr(error, 'exit_code', 2)
        print(json.dumps({'status': 'blocked', 'exit_code': code, 'error': str(error),
                          'no_fallback': True, 'help': 'docs/AGENT_SETUP.md'}, indent=2), file=sys.stderr)
        return code


if __name__ == '__main__':
    raise SystemExit(main())
