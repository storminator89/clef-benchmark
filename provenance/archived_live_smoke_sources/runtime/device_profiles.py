"""Explicit live-inference profiles; importing this module never imports Torch.

ROCm exposes AMD GPUs through Torch's cuda namespace. No profile selection
silently changes device, precision, or quantization, and no NPU path is provided.
"""
from __future__ import annotations

PROFILES = ('cpu-nf4', 'rocm-bf16', 'rocm-fp16')
MIN_GPU_FREE_GIB = 22


class BackendUnavailable(RuntimeError):
    """A safe, actionable error that can also be displayed by the local UI."""


def validate_profile(profile, device_index=0):
    if profile not in PROFILES:
        raise ValueError(f'profile must be one of {", ".join(PROFILES)}')
    if type(device_index) is not int or device_index < 0:
        raise ValueError('device_index must be a nonnegative integer')
    if profile == 'cpu-nf4' and device_index != 0:
        raise ValueError('device_index only applies to a ROCm profile')


def resolve_profile(torch, profile='cpu-nf4', device_index=0):
    """Inspect the selected backend without loading weights or running a kernel."""
    validate_profile(profile, device_index)
    info = {
        'profile': profile,
        'backend': 'cpu' if profile == 'cpu-nf4' else 'rocm',
        'device': 'cpu' if profile == 'cpu-nf4' else f'cuda:{device_index}',
        'device_name': 'CPU',
        'precision': {
            'cpu-nf4': 'NF4 backbone; BF16 joint head and lexical output embeddings',
            'rocm-bf16': 'BF16 native weights; original joint head and lexical output embeddings',
            'rocm-fp16': 'FP16 conversion of release weights, original joint head and lexical output embeddings',
        }[profile],
        'quantization': 'nf4-double' if profile == 'cpu-nf4' else 'none',
        'torch_version': str(torch.__version__),
        'hip_version': getattr(torch.version, 'hip', None),
        'gpu_architecture': None,
        'gpu_free_gib_before_load': None,
        'gpu_total_gib': None,
    }
    if profile == 'cpu-nf4':
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
    if free < MIN_GPU_FREE_GIB * 1024**3:
        raise BackendUnavailable(f'ROCm meldet nur {free / 1024**3:.1f} GiB freien GPU-Speicher. Dieses unquantisierte Profil verlangt vor dem Laden mindestens {MIN_GPU_FREE_GIB} GiB (keine Erfolgsgarantie). APU-System-RAM ist nicht automatisch vollständig GPU-Speicher. Kein CPU-Fallback.')
    return info


def dtype_for_profile(torch, profile):
    validate_profile(profile)
    return torch.float16 if profile == 'rocm-fp16' else torch.bfloat16
