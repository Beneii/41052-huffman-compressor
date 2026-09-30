"""Repeatable demonstration: python demo.py. Never touches original input."""
import hashlib
from pathlib import Path
import subprocess
import sys

import huff


def main():
    root = Path(__file__).resolve().parent
    output = root / 'demo-output'
    output.mkdir(exist_ok=True)
    source = root / 'examples' / 'message.txt'
    archive, restored = output / 'message.huf', output / 'restored.txt'
    def run(*args):
        print('\n> python huff.py ' + ' '.join(str(arg) for arg in args), flush=True)
        subprocess.run([sys.executable, str(root / 'huff.py'), *map(str, args)], check=True)
    run('compress', source, archive, '--force')
    run('inspect', archive)
    run('decompress', archive, restored, '--force')
    original, decoded = source.read_bytes(), restored.read_bytes()
    print('\nOriginal SHA256:', hashlib.sha256(original).hexdigest())
    print('Restored SHA256:', hashlib.sha256(decoded).hexdigest())
    assert original == decoded
    print('PASS: restored bytes exactly match the original')
    damaged = bytearray(archive.read_bytes())
    damaged[20] ^= 1  # Change the checksum, keeping format and payload intact.
    try:
        huff.decompress(bytes(damaged))
    except huff.FormatError as error:
        print('PASS: corrupted archive rejected:', error)
    else:
        raise AssertionError('corrupted archive was accepted')


if __name__ == '__main__':
    main()
