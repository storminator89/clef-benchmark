"""Explicit live-inference profiles; importing this module never imports Torch.

ROCm exposes AMD GPUs through Torch's cuda namespace. No profile selection
silently changes device, precision, or quantization, and no NPU path is provided.
"""
from __future__ import annotations

try:
    from runtime.model_registry import get_model, validation_status
except ModuleNotFoundError as error:
    if error.name != 'runtime':
        raise
    import importlib.util
    from pathlib import Path
    _spec = importlib.util.spec_from_file_location('_clef_model_registry', Path(__file__).with_name('model_registry.py'))
    _registry = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_registry)
    get_model, validation_status = _registry.get_model, _registry.validation_status

PROFILES = ('cpu-nf4', 'cpu-bf16', 'rocm-bf16', 'rocm-fp16')
MIN_GPU_FREE_GIB = 22
MIN_RAM_GIB = {'cpu-nf4': 7.5, 'cpu-bf16': 28, 'rocm-bf16': 2, 'rocm-fp16': 2}
PROFILE_STATUS = {'cpu-nf4': 'tested_linux_x86_64', 'cpu-bf16': 'prepared_not_hardware_validated',
                  'rocm-bf16': 'prepared_not_hardware_validated', 'rocm-fp16': 'prepared_not_hardware_validated'}


def is_cpu(profile):
    return profile in ('cpu-nf4', 'cpu-bf16')


def required_host_ram_gib(model_key, profile, runtime_info=None):
    model = get_model(model_key)
    host = model['min_ram_gib'][profile]
    if runtime_info and runtime_info.get('gpu_shares_system_ram'):
        # APU pools overlap; a large GPU number does not establish enough free
        # physical system memory for both the model and the remaining process.
        host = max(host, model['min_gpu_free_gib'] + host)
    return host


class BackendUnavailable(RuntimeError):
    """A safe, actionable error that can also be displayed by the local UI."""


def validate_profile(profile, device_index=0):
    if profile not in PROFILES:
        raise ValueError(f'profile must be one of {", ".join(PROFILES)}')
    if type(device_index) is not int or device_index < 0:
        raise ValueError('device_index must be a nonnegative integer')
    if is_cpu(profile) and device_index != 0:
        raise ValueError('device_index only applies to a ROCm profile')


def resolve_profile(torch, profile='cpu-nf4', device_index=0, model_key='flash-9b'):
    """Inspect the selected backend without loading weights or running a kernel."""
    validate_profile(profile, device_index)
    model = get_model(model_key)
    info = {
        'profile': profile,
        'backend': 'cpu' if is_cpu(profile) else 'rocm',
        'device': 'cpu' if is_cpu(profile) else f'cuda:{device_index}',
        'device_name': 'CPU',
        'precision': {
            'cpu-nf4': 'NF4 backbone; BF16 joint head and lexical output embeddings',
            'cpu-bf16': 'BF16 native weights; original joint head and lexical output embeddings',
            'rocm-bf16': 'BF16 native weights; original joint head and lexical output embeddings',
            'rocm-fp16': 'FP16 conversion of release weights, original joint head and lexical output embeddings',
        }[profile],
        'quantization': 'nf4-double' if profile == 'cpu-nf4' else 'none',
        'model_key': model_key, 'model_id': model['repo_id'], 'revision': model['revision'],
        'model_size': model['model_size'],
        'validation_status': validation_status(model_key, profile),
        'torch_version': str(torch.__version__),
        'hip_version': getattr(torch.version, 'hip', None),
        'gpu_architecture': None,
        'gpu_free_gib_before_load': None,
        'gpu_total_gib': None,
        'gpu_shares_system_ram': False,
    }
    if is_cpu(profile):
        return info
    if not info['hip_version']:
        raise BackendUnavailable('ROCm wurde angefordert, aber dieses PyTorch hat keine HIP/ROCm-Unterstützung. Verwende eine separate AMD-PyTorch-Umgebung laut docs/AMD_GPU.md; die CPU-Umgebung genügt nicht. Kein CPU-Fallback.')
    if not torch.cuda.is_available():
        raise BackendUnavailable('ROCm-PyTorch ist installiert, aber keine AMD-GPU ist erreichbar. Prüfe Treiber, Kernel, GPU-Berechtigungen und unterstützte Hardware laut docs/AMD_GPU.md. Kein CPU-Fallback.')
    if device_index >= torch.cuda.device_count():
        raise BackendUnavailable('Der angeforderte GPU-Index ist nicht sichtbar. Prüfe --device-index und die sichtbaren Geräte. Kein CPU-Fallback.')
    try:
        properties = torch.cuda.get_device_properties(device_index)
        with torch.cuda.device(device_index):
            if profile == 'rocm-bf16' and not torch.cuda.is_bf16_supported():
                raise BackendUnavailable('Die gewählte GPU meldet keine BF16-Unterstützung. Prüfe den Software-Stack oder wähle ausdrücklich --inference-profile rocm-fp16. Kein automatischer Präzisionswechsel.')
            free, total = torch.cuda.mem_get_info(device_index)
    except BackendUnavailable:
        raise
    except Exception as exc:
        raise BackendUnavailable('ROCm-Geräte- oder Speicherprüfung fehlgeschlagen. Führe python -m runtime.check_backend aus und prüfe den AMD-Software-Stack. Kein CPU-Fallback.') from exc
    info.update(device_name=str(properties.name),
                gpu_architecture=getattr(properties, 'gcnArchName', None),
                gpu_free_gib_before_load=free / 1024**3,
                gpu_total_gib=total / 1024**3)
    architecture = str(info['gpu_architecture'] or '').split(':')[0]
    info['gpu_shares_system_ram'] = bool(getattr(properties, 'integrated', False)) or architecture in {
        'gfx1150', 'gfx1151', 'gfx1152', 'gfx1153', 'gfx1103'}
    minimum_gpu = model['min_gpu_free_gib']
    if free < minimum_gpu * 1024**3:
        raise BackendUnavailable(f'ROCm meldet nur {free / 1024**3:.1f} GiB freien GPU-Speicher. Dieses unquantisierte {model["model_size"]}-Profil verlangt vor dem Laden mindestens {minimum_gpu} GiB (keine Erfolgsgarantie). APU-System-RAM ist nicht automatisch vollständig GPU-Speicher. Kein CPU-Fallback.')
    return info


def dtype_for_profile(torch, profile):
    validate_profile(profile)
    return torch.float16 if profile == 'rocm-fp16' else torch.bfloat16
