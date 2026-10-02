"""Model-free installer/profile tests. No package install or weight download."""
from contextlib import redirect_stdout
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from runtime import hardware_probe, model_assets, setup
from runtime.device_profiles import BackendUnavailable, required_host_ram_gib, resolve_profile
from runtime.live_adapter import ClefRuntime, MODEL_ID, REVISION
from runtime.model_registry import DEFAULT_MODEL, MODEL_KEYS, get_model, model_manifest
import test_device_profiles as profile_tests
fake_torch = profile_tests.fake_torch


class RegistryTests(unittest.TestCase):
    def test_default_and_flash_constants_unchanged(self):
        self.assertEqual(DEFAULT_MODEL, 'flash-9b')
        self.assertEqual((get_model()['repo_id'], get_model()['revision']), (MODEL_ID, REVISION))
        self.assertEqual(get_model()['hidden_size'], 4096)
        self.assertEqual(get_model('clef-27b')['hidden_size'], 5120)

    def test_larger_model_has_independent_complete_manifest(self):
        expected = {'flash-9b': (17, 19083377402, 4), 'clef-27b': (25, 54989894057, 12)}
        for key in MODEL_KEYS:
            manifest = model_assets.load_manifest(key)
            count, total, shards = expected[key]
            self.assertEqual(len(manifest), count)
            self.assertEqual(sum(item['bytes'] for item in manifest.values()), total)
            self.assertEqual(sum(name.startswith('model-') for name in manifest), shards)
            self.assertEqual({item['hf_commit'] for item in manifest.values()}, {get_model(key)['revision']})

    def test_registry_copies_and_unknown_model_cannot_fallback(self):
        model = get_model()
        model['min_ram_gib']['cpu-nf4'] = 0
        self.assertEqual(get_model()['min_ram_gib']['cpu-nf4'], 7.5)
        with self.assertRaises(ValueError):
            get_model('auto')

    def test_27b_reviewed_small_files_match_manifest_and_loader(self):
        root = Path(__file__).resolve().parents[1] / 'runtime/models/clef-27b'
        manifest = model_manifest('clef-27b')
        for name in ('config.json', 'joint_head_config.json', 'joint_schema_model.py', 'model.safetensors.index.json'):
            self.assertEqual(hashlib.sha256((root / name).read_bytes()).hexdigest(), manifest[name]['sha256'])
        config = json.loads((root / 'config.json').read_text())
        head = json.loads((root / 'joint_head_config.json').read_text())
        model = get_model('clef-27b')
        self.assertEqual(config['text_config']['hidden_size'], head['hidden_size'])
        self.assertEqual(config['text_config']['hidden_size'], model['hidden_size'])
        self.assertEqual(config['text_config']['vocab_size'], model['vocab_size'])
        self.assertEqual(manifest['joint_schema_model.py']['sha256'], model['source_sha256'])
        self.assertEqual(manifest['joint_schema_model.py']['sha256'], get_model()['source_sha256'])

    def test_27b_index_names_exactly_pinned_shards(self):
        root = Path(__file__).resolve().parents[1] / 'runtime/models/clef-27b'
        index = json.loads((root / 'model.safetensors.index.json').read_text())
        manifest = model_manifest('clef-27b')
        self.assertEqual(set(index['weight_map'].values()), {name for name in manifest if name.startswith('model-')})


class FullPrecisionAndModelTests(unittest.TestCase):
    def test_cpu_bf16_does_not_probe_gpu_or_import_quantizer(self):
        torch = fake_torch()
        runtime = ClefRuntime(Path('.'), profile='cpu-bf16')
        runtime._runtime_info = resolve_profile(torch, 'cpu-bf16')
        vendor = MagicMock()
        with patch.dict(sys.modules, {'bitsandbytes': None, 'transformers': None}):
            runtime._load_model(vendor, torch)
        self.assertEqual(vendor.load_release_model.call_args.kwargs,
                         {'device': 'cpu', 'dtype': 'bf16', 'local_files_only': True})
        torch.cuda.is_available.assert_not_called()
        runtime._torch = torch
        runtime._synchronize()
        torch.cuda.synchronize.assert_not_called()

    def test_larger_embedding_shape_is_validated(self):
        torch = fake_torch()
        runtime = ClefRuntime(Path('.'), profile='cpu-bf16', model_key='clef-27b')
        runtime._runtime_info = resolve_profile(torch, 'cpu-bf16', model_key='clef-27b')
        model, embedding, head = profile_tests.AdapterProfileTests().model(device='cpu')
        with self.assertRaisesRegex(RuntimeError, 'embedding'):
            runtime._validate_model(model, torch)
        embedding.shape = (248320, 5120)
        runtime._validate_model(model, torch)
        self.assertEqual(runtime.status()['model_id'], 'Cloudflare/clef')
        self.assertEqual(runtime.status()['revision'], get_model('clef-27b')['revision'])

    def test_27b_gpu_guard_and_apu_combined_ram(self):
        with self.assertRaises(BackendUnavailable):
            resolve_profile(fake_torch(free_gib=59), 'rocm-bf16', model_key='clef-27b')
        info = resolve_profile(fake_torch(free_gib=80), 'rocm-bf16', model_key='clef-27b')
        self.assertTrue(info['gpu_shares_system_ram'])
        self.assertEqual(required_host_ram_gib('clef-27b', 'rocm-bf16', info), 64)
        self.assertEqual(required_host_ram_gib('flash-9b', 'rocm-bf16', info), 24)
        self.assertEqual(info['validation_status'], 'prepared_not_hardware_validated')

    def test_27b_nf4_is_never_labeled_tested(self):
        info = resolve_profile(fake_torch(), 'cpu-nf4', model_key='clef-27b')
        self.assertEqual(info['model_size'], '27B')
        self.assertEqual(info['validation_status'], 'prepared_not_hardware_validated')
        self.assertEqual(required_host_ram_gib('clef-27b', 'cpu-nf4'), 24)


class ModelAssetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.payload = b'pinned test fixture'
        self.manifest = {'config.json': {'bytes': len(self.payload), 'sha256': hashlib.sha256(self.payload).hexdigest(), 'hf_commit': REVISION}}

    def tearDown(self):
        self.temp.cleanup()

    def test_same_size_is_unverified_until_hash_checked(self):
        (self.root / 'config.json').write_bytes(self.payload)
        plan = model_assets.inspect_files(self.root, self.manifest, hashes=False)
        self.assertFalse(plan['verified_complete'])
        self.assertEqual(plan['present_unverified'], ['config.json'])
        self.assertTrue(model_assets.inspect_files(self.root, self.manifest)['verified_complete'])

    def test_wrong_hash_same_size_is_refused_without_repair_or_import(self):
        (self.root / 'config.json').write_bytes(b'X' * len(self.payload))
        with patch.object(model_assets, 'load_manifest', return_value=self.manifest), patch.dict(sys.modules, {'huggingface_hub': None}):
            with self.assertRaisesRegex(ValueError, 'nothing overwritten'):
                model_assets.prepare_model(self.root, download=True)
        self.assertEqual((self.root / 'config.json').read_bytes(), b'X' * len(self.payload))

    def test_verified_cache_is_reused_without_network_package(self):
        (self.root / 'config.json').write_bytes(self.payload)
        with patch.object(model_assets, 'load_manifest', return_value=self.manifest), patch.dict(sys.modules, {'huggingface_hub': None}):
            result = model_assets.prepare_model(self.root, download=True)
        self.assertEqual(result['downloaded_files'], 0)
        self.assertEqual(result['reused_files'], 1)

    def test_missing_offline_file_cannot_download(self):
        with patch.object(model_assets, 'load_manifest', return_value=self.manifest), patch.dict(sys.modules, {'huggingface_hub': None}):
            with self.assertRaises(FileNotFoundError):
                model_assets.prepare_model(self.root, download=True, offline=True)

    def test_only_missing_official_pinned_files_download_without_token(self):
        def download(**kwargs):
            (self.root / kwargs['filename']).write_bytes(self.payload)
            return str(self.root / kwargs['filename'])
        fetch = MagicMock(side_effect=download)
        with patch.object(model_assets, 'load_manifest', return_value=self.manifest), \
             patch.dict(sys.modules, {'huggingface_hub': SimpleNamespace(hf_hub_download=fetch)}), \
             patch.object(model_assets.shutil, 'disk_usage', return_value=SimpleNamespace(free=100 * 1024**3)), \
             patch.dict(os.environ, {'HF_ENDPOINT': 'https://huggingface.co'}):
            result = model_assets.prepare_model(self.root, download=True)
        self.assertEqual(result['downloaded_files'], 1)
        self.assertEqual(fetch.call_args.kwargs['repo_id'], MODEL_ID)
        self.assertEqual(fetch.call_args.kwargs['revision'], REVISION)
        self.assertIs(fetch.call_args.kwargs['token'], False)

    def test_custom_mirror_is_rejected_before_any_download(self):
        with patch.object(model_assets, 'load_manifest', return_value=self.manifest), patch.dict(os.environ, {'HF_ENDPOINT': 'https://example.invalid'}):
            with self.assertRaisesRegex(ValueError, 'HF_ENDPOINT'):
                model_assets.prepare_model(self.root, download=True)


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.args = setup.parser().parse_args(['--venv', str(self.root/'env'), '--model-dir', str(self.root/'model')])
        self.hardware = {'python': '3.12.14', 'os': 'Linux', 'architecture': 'x86_64',
                         'cpu': {'avx2': True}, 'libc': ['glibc', '2.41'],
                         'memory': {'available_bytes': 128 * 1024**3},
                         'disk': {'free_bytes': 200 * 1024**3}}

    def tearDown(self):
        self.temp.cleanup()

    def plan(self):
        with patch('shutil.disk_usage', return_value=SimpleNamespace(free=200 * 1024**3)):
            return setup.make_plan(self.args, copy.deepcopy(self.hardware))

    def test_default_plan_has_no_mutations_or_model_load(self):
        plan = self.plan()
        self.assertEqual(plan['status'], 'plan_ready')
        self.assertEqual(plan['model']['key'], 'flash-9b')
        self.assertFalse(plan['mutations_performed'])
        self.assertFalse(plan['model_loaded'])
        self.assertEqual(list(self.root.iterdir()), [])

    def test_27b_needs_explicit_choice_and_uses_own_resources(self):
        self.args.model = 'clef-27b'
        self.hardware['memory']['available_bytes'] = 16 * 1024**3
        plan = self.plan()
        self.assertEqual(plan['model']['release_bytes'], 54989894057)
        self.assertTrue(any('24 GiB' in item for item in plan['blockers']))
        self.assertIn('--model', plan['start_server_argv'])
        self.assertIn('clef-27b', plan['start_server_argv'])

    def test_unknown_ram_and_wrong_python_block(self):
        self.hardware['memory']['available_bytes'] = None
        self.hardware['python'] = '3.14.0'
        plan = self.plan()
        self.assertTrue(any('RAM could not' in item for item in plan['blockers']))
        self.assertTrue(any('Python 3.12' in item for item in plan['blockers']))

    def test_existing_unowned_venv_not_mutated(self):
        self.args.venv.mkdir()
        (self.args.venv / 'important.txt').write_text('preserve')
        self.assertTrue(any('not managed' in item for item in self.plan()['blockers']))
        self.assertEqual((self.args.venv / 'important.txt').read_text(), 'preserve')

    def test_changed_managed_lock_refuses_upgrade(self):
        self.args.venv.mkdir()
        (self.args.venv / setup.MARKER).write_text(json.dumps({'dependency_sha256': 'different'}))
        self.assertTrue(any('different dependency' in item for item in self.plan()['blockers']))

    def test_active_venv_requires_read_only_mode(self):
        with patch.dict(os.environ, {'VIRTUAL_ENV': str(self.args.venv)}):
            self.assertTrue(any('venv is active' in item for item in self.plan()['blockers']))

    def test_verified_existing_env_needs_no_fresh_install_disk_reserve(self):
        self.args.venv.mkdir()
        python = setup.env_python(self.args.venv)
        python.parent.mkdir(parents=True, exist_ok=True)
        python.touch()
        (self.args.venv/setup.MARKER).write_text(json.dumps({'dependency_sha256': setup.dependency_fingerprint('cpu-nf4'), 'complete': True}))
        with patch('shutil.disk_usage', return_value=SimpleNamespace(free=1)):
            result = setup.make_plan(self.args, self.hardware)
        self.assertFalse(any('Venv filesystem' in item for item in result['blockers']))

    def test_rocm_requires_explicit_existing_runtime(self):
        self.args.profile = 'rocm-bf16'
        self.assertTrue(any('use-existing-runtime' in item for item in self.plan()['blockers']))

    def test_windows_is_explicitly_prepared_not_validated(self):
        self.hardware['os'] = 'Windows'
        self.assertTrue(any('allow-untested-platform' in item for item in self.plan()['blockers']))
        self.args.allow_untested_platform = True
        self.assertFalse(any('allow-untested-platform' in item for item in self.plan()['blockers']))

    def test_cpu_full_bf16_requires_28_available_gib(self):
        self.args.profile = 'cpu-bf16'
        self.hardware['memory']['available_bytes'] = 27 * 1024**3
        self.assertTrue(any('28 GiB' in item for item in self.plan()['blockers']))

    def test_cli_plan_does_not_import_torch_or_touch_paths(self):
        code = "import sys; from runtime.setup import main; code=main(sys.argv[1:]); assert 'torch' not in sys.modules; raise SystemExit(code)"
        result = subprocess.run([sys.executable, '-B', '-c', code, '--plan', '--venv', str(self.root/'env'),
                                 '--model-dir', str(self.root/'model')], cwd=setup.ROOT, capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout)['mode'], 'plan')
        self.assertEqual(list(self.root.iterdir()), [])

    def test_blocked_execute_never_installs(self):
        with patch.object(setup, 'make_plan', return_value={'blockers': ['not enough memory']}), \
             patch.object(setup, 'install_cpu_environment') as install, \
             patch('sys.stderr', new_callable=io.StringIO):
            self.assertEqual(setup.main(['--execute']), 2)
        install.assert_not_called()


class MemoryProbeTests(unittest.TestCase):
    def test_cgroup_limit_bounds_host_memavailable_and_never_counts_swap(self):
        files = {'/proc/meminfo': 'MemTotal: 67108864 kB\nMemAvailable: 60000000 kB\nSwapFree: 90000000 kB\n',
                 '/proc/self/cgroup': '0::/\n', '/sys/fs/cgroup/memory.max': str(10 * 1024**3),
                 '/sys/fs/cgroup/memory.current': str(8 * 1024**3)}
        with patch.object(hardware_probe.sys, 'platform', 'linux'), \
             patch.object(hardware_probe, '_read', side_effect=lambda p: files.get(str(p), '')):
            result = hardware_probe.effective_memory()
        self.assertEqual(result['available_bytes'], 2 * 1024**3)
        self.assertFalse(result['swap_counted'])


class EnvironmentLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.args = setup.parser().parse_args(['--venv', str(self.root/'env')])

    def tearDown(self):
        self.temp.cleanup()

    def builder(self, folder):
        python = setup.env_python(folder)
        python.parent.mkdir(parents=True, exist_ok=True)
        python.touch()

    def test_fresh_cpu_installs_only_exact_binary_registry_pins(self):
        builder = MagicMock()
        builder.create.side_effect = self.builder
        with patch.object(setup.venv, 'EnvBuilder', return_value=builder) as factory, \
             patch.object(setup, 'run') as run, \
             patch.object(setup, 'check_dependencies', return_value={'verified': True}):
            setup.install_cpu_environment(self.args)
        factory.assert_called_once_with(with_pip=True, system_site_packages=False)
        commands = [call.args[0] for call in run.call_args_list]
        self.assertEqual(len(commands), 2)
        for command in commands:
            self.assertIn('--no-deps', command)
            self.assertIn('--only-binary=:all:', command)
        self.assertIn('https://download.pytorch.org/whl/cpu', commands[0])
        self.assertIn('torch==2.11.0+cpu', commands[0])
        self.assertIn('https://pypi.org/simple', commands[1])
        self.assertNotIn('--upgrade', commands[1])
        self.assertTrue(json.loads((self.args.venv/setup.MARKER).read_text())['complete'])

    def test_completed_owned_env_is_only_checked_not_reinstalled(self):
        self.builder(self.args.venv)
        (self.args.venv/setup.MARKER).write_text(json.dumps({'dependency_sha256': setup.dependency_fingerprint('cpu-nf4'), 'complete': True}))
        with patch.object(setup, 'run') as run, patch.object(setup.venv, 'EnvBuilder') as builder, \
             patch.object(setup, 'check_dependencies', return_value={'verified': True}) as check:
            setup.install_cpu_environment(self.args)
        run.assert_not_called()
        builder.assert_not_called()
        check.assert_called_once()

    def test_interrupted_install_stays_owned_and_resumable(self):
        builder = MagicMock()
        builder.create.side_effect = self.builder
        with patch.object(setup.venv, 'EnvBuilder', return_value=builder), \
             patch.object(setup, 'run', side_effect=setup.SetupError('network unavailable', 3)):
            with self.assertRaises(setup.SetupError):
                setup.install_cpu_environment(self.args)
        self.assertFalse(json.loads((self.args.venv/setup.MARKER).read_text())['complete'])
        with patch.object(setup.venv, 'EnvBuilder') as builder, patch.object(setup, 'run') as run, \
             patch.object(setup, 'check_dependencies', return_value={'verified': True}):
            setup.install_cpu_environment(self.args)
        builder.assert_not_called()
        self.assertEqual(run.call_count, 2)

    def test_changed_dependency_version_is_blocker_without_install(self):
        result = {'python': [3, 12], 'missing': [], 'mismatched': ['torch==2.11.0+cpu'], 'versions': {'torch': 'other'}}
        with patch.object(setup, 'run', return_value=result) as run:
            with self.assertRaisesRegex(setup.SetupError, 'no automatic upgrades'):
                setup.check_dependencies('fake-python', 'cpu-nf4')
        self.assertEqual(run.call_count, 1)

    def test_existing_target_python_version_checked(self):
        result = {'python': [3, 14], 'missing': [], 'mismatched': [], 'versions': {}}
        with patch.object(setup, 'run', return_value=result):
            with self.assertRaises(setup.SetupError):
                setup.check_dependencies('fake-python', 'cpu-nf4')

    def test_dependency_lists_have_no_unpinned_or_remote_source_requirements(self):
        for profile in ('cpu-nf4', 'cpu-bf16', 'rocm-bf16', 'rocm-fp16'):
            for pin in setup.requirements(profile):
                self.assertEqual(pin.count('=='), 1)
                self.assertNotIn('https://', pin)
                self.assertNotIn('git+', pin)


if __name__ == '__main__':
    unittest.main()
