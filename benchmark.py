"""Reproducible Track B comparison; gzip uses its normal DEFLATE algorithm."""
import csv
import gzip
import json
import platform
from pathlib import Path
import random
import statistics
import sys
import time

import huff


def main():
    rng = random.Random(41052)
    text = ('Huffman coding assigns short codes to frequent symbols. '
            'A prefix-free code can be decoded without separators.\n').encode()
    datasets = {
        'empty': b'',
        'tiny_text': b'hello Huffman',
        'single_symbol': b'A' * 65536,
        'repeated_text': (text * (65536 // len(text) + 1))[:65536],
        'skewed_symbols': bytes(rng.choices(range(8), weights=[60, 20, 8, 4, 3, 2, 2, 1], k=65536)),
        'uniform_bytes': bytes(range(256)) * 256,
        'random_bytes': rng.randbytes(65536),
        'source_code': Path(huff.__file__).read_bytes(),
    }
    rows = []
    for name, data in datasets.items():
        for codec, encode, decode in [('Huffman', huff.compress, huff.decompress),
                                     ('gzip', lambda b: gzip.compress(b, compresslevel=9, mtime=0), gzip.decompress)]:
            encode_times, decode_times = [], []
            for _ in range(5):
                start = time.perf_counter(); archive = encode(data); encode_times.append((time.perf_counter() - start) * 1000)
                start = time.perf_counter(); restored = decode(archive); decode_times.append((time.perf_counter() - start) * 1000)
                assert restored == data, (name, codec)
            rows.append({'dataset': name, 'codec': codec, 'input_bytes': len(data), 'archive_bytes': len(archive),
                         'ratio': round(len(archive) / len(data), 4) if data else '',
                         'compress_ms': round(statistics.median(encode_times), 3),
                         'decompress_ms': round(statistics.median(decode_times), 3)})
    output = Path('results'); output.mkdir(exist_ok=True)
    with (output / 'benchmark.csv').open('w', newline='') as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    (output / 'environment.json').write_text(json.dumps({'python': sys.version, 'platform': platform.platform(),
        'seed': 41052, 'repetitions': 5, 'timing': 'median wall time; in-memory encode/decode; excludes disk I/O',
        'gzip_level': 9, 'notes': 'Python Huffman versus native zlib; speed reflects implementation language as well as algorithms.'}, indent=2))
    lines = ['| Dataset | Bytes in | HUF bytes | gzip bytes | HUF encode ms | gzip encode ms |',
             '|---|---:|---:|---:|---:|---:|']
    for index in range(0, len(rows), 2):
        a, b = rows[index:index + 2]
        lines.append(f"| {a['dataset']} | {a['input_bytes']} | {a['archive_bytes']} | {b['archive_bytes']} | {a['compress_ms']} | {b['compress_ms']} |")
    (output / 'table.md').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
