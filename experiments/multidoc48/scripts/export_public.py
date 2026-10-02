#!/usr/bin/env python3
"""Copy only the verified retained public allowlist; never modify frozen science."""
from pathlib import Path
import argparse
import json
import shutil
import sys
sys.dont_write_bytecode = True
from verify_export import ROOT, verify, load

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    result = verify()
    destination = args.destination.resolve()
    assert not destination.exists(), 'Refuse overwriting an artifact'
    destination.mkdir(parents=True)
    for name in sorted(set(load(ROOT / 'FILE_SHA256.json')) | {'FILE_SHA256.json'}):
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    assert verify(destination) == result
    print(json.dumps(result, indent=2))

if __name__ == '__main__': main()
