"""Read-only, standard-library hardware/resource inventory. Never loads Torch/models."""
from __future__ import annotations

import argparse
import ctypes
import json
import os
from pathlib import Path
import platform
import shutil
import sys

GIB = 1024 ** 3


def _read(path):
    try:
        return Path(path).read_text()
    except (OSError, ValueError):
        return ''


def effective_memory():
    """Available physical memory, bounded by a visible Linux cgroup limit.

    Swap is never counted. Unknown values remain None, never guessed as enough.
    """
    total = available = None
    source = 'unavailable'
    if sys.platform.startswith('linux'):
        values = {}
        for line in _read('/proc/meminfo').splitlines():
            key, _, value = line.partition(':')
            if value.strip():
                values[key] = int(value.split()[0]) * 1024
        total, available = values.get('MemTotal'), values.get('MemAvailable')
        source = '/proc/meminfo'
        # A cgroup namespace may expose the limit at the mount root or at the
        # process's own relative path. Inspect both plus visible ancestors.
        roots = {Path('/sys/fs/cgroup')}
        for line in _read('/proc/self/cgroup').splitlines():
            parts = line.split(':', 2)
            if len(parts) == 3 and parts[0] == '0':
                relative = Path(parts[2].lstrip('/'))
                if '..' not in relative.parts:
                    current = Path('/sys/fs/cgroup') / relative
                    roots.update([current, *[p for p in current.parents if p.is_relative_to('/sys/fs/cgroup')]])
        for root in roots:
            limit, usage = _read(root / 'memory.max').strip(), _read(root / 'memory.current').strip()
            if limit.isdigit() and usage.isdigit():
                remaining = max(0, int(limit) - int(usage))
                available = remaining if available is None else min(available, remaining)
                total = int(limit) if total is None else min(total, int(limit))
                source += '+cgroup_v2'
        # Legacy cgroup v1 where present; huge sentinel values have no effect.
        limit = _read('/sys/fs/cgroup/memory/memory.limit_in_bytes').strip()
        usage = _read('/sys/fs/cgroup/memory/memory.usage_in_bytes').strip()
        if limit.isdigit() and usage.isdigit():
            remaining = max(0, int(limit) - int(usage))
            available = remaining if available is None else min(available, remaining)
            total = int(limit) if total is None else min(total, int(limit))
            source += '+cgroup_v1'
    elif os.name == 'nt':
        class MemoryStatus(ctypes.Structure):
            _fields_ = [('length', ctypes.c_ulong), ('load', ctypes.c_ulong),
                        *[(name, ctypes.c_ulonglong) for name in
                          ('total', 'available', 'total_page', 'available_page',
                           'total_virtual', 'available_virtual', 'extended')]]
        memory = MemoryStatus()
        memory.length = ctypes.sizeof(memory)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory)):
            total, available, source = memory.total, memory.available, 'GlobalMemoryStatusEx'
    return {'total_bytes': total, 'available_bytes': available, 'source': source,
            'swap_counted': False}


def existing_parent(path):
    path = Path(path).expanduser().absolute()
    while not path.exists() and path != path.parent:
        path = path.parent
    return path


def probe(path=Path('.')):
    cpu = _read('/proc/cpuinfo')
    flags = next((line.split(':', 1)[1].split() for line in cpu.splitlines()
                  if line.startswith('flags') and ':' in line), None)
    name = next((line.split(':', 1)[1].strip() for line in cpu.splitlines()
                 if line.startswith('model name') and ':' in line), platform.processor() or None)
    disk_path = existing_parent(path)
    disk = shutil.disk_usage(disk_path)
    try:
        distribution = platform.freedesktop_os_release()
    except OSError:
        distribution = {}
    return {
        'schema_version': 1, 'read_only': True, 'model_loaded': False,
        'os': platform.system(), 'os_release': platform.release(),
        'distribution': {key: distribution[key] for key in ('ID', 'VERSION_ID', 'PRETTY_NAME') if key in distribution},
        'architecture': platform.machine(), 'libc': list(platform.libc_ver()),
        'python': platform.python_version(), 'python_executable': sys.executable,
        'cpu': {'name': name, 'logical_count': os.cpu_count(),
                'available_count': len(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else os.cpu_count(),
                'avx2': 'avx2' in flags if flags is not None else None},
        'memory': effective_memory(),
        'disk': {'checked_path': str(disk_path), 'free_bytes': disk.free, 'total_bytes': disk.total},
        'gpu': {'status': 'not_probed', 'reason': 'Use the selected environment: python -m runtime.check_backend --profile rocm-bf16'},
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--path', type=Path, default=Path('.'), help='Check the filesystem intended for model storage')
    args = parser.parse_args(argv)
    print(json.dumps(probe(args.path), indent=2))


if __name__ == '__main__':
    main()
