import itertools
from pathlib import Path
import random
import struct
import subprocess
import sys
from contextlib import contextmanager
import uuid
import unittest

import huff


@contextmanager
def project_test_directory():
    # tempfile.mkdtemp's restrictive mode causes Windows ACL failures in
    # this runtime; ordinary mkdir inherits the project's usable ACL.
    directory = Path(__file__).parent / ('test-run-' + uuid.uuid4().hex)
    directory.mkdir()
    try:
        yield directory
    finally:
        for child in directory.iterdir():
            child.unlink()
        directory.rmdir()


class HuffmanTests(unittest.TestCase):
    def test_roundtrip_edge_cases_and_seeded_random_inputs(self):
        rng = random.Random(41052)
        cases = [b'', b'x', b'x' * 10000, bytes(range(256)), bytes(range(256)) * 10,
                 'Huffman: café 日本語 🐈\n'.encode(), b'ABRACADABRA']
        cases += [rng.randbytes(n) for n in [2, 7, 8, 9, 255, 1000, 10000]]
        cases += [bytes(rng.choices(range(7), weights=[40, 20, 10, 5, 3, 2, 1], k=n))
                  for n in range(1, 300, 11)]
        for data in cases:
            with self.subTest(size=len(data)):
                archive = huff.compress(data)
                self.assertEqual(huff.decompress(archive), data)
                self.assertEqual(huff.compress(data), archive)

    def test_known_weighted_cost(self):
        # Classic frequencies: optimal cost is 224, not just a roundtrip.
        data = b'a' * 45 + b'b' * 13 + b'c' * 12 + b'd' * 16 + b'e' * 9 + b'f' * 5
        lengths = huff.code_lengths(data)
        self.assertEqual(sum(data.count(symbol) * length for symbol, length in lengths.items()), 224)

    def test_optimal_against_exhaustive_merging_small_alphabets(self):
        # Independent exhaustive search considers ALL merge sequences.
        def optimum(weights):
            if len(weights) == 1:
                return 0
            best = float('inf')
            for a, b in itertools.combinations(range(len(weights)), 2):
                joined = weights[a] + weights[b]
                remaining = [w for i, w in enumerate(weights) if i not in (a, b)]
                best = min(best, joined + optimum(remaining + [joined]))
            return best
        for weights in [(1, 1), (1, 2, 3), (2, 2, 3, 7), (1, 1, 2, 3, 5)]:
            data = b''.join(bytes([i]) * w for i, w in enumerate(weights))
            lengths = huff.code_lengths(data)
            self.assertEqual(sum(w * lengths[i] for i, w in enumerate(weights)), optimum(list(weights)))

    def test_codes_are_prefix_free(self):
        data = b''.join(bytes([i]) * (i + 1) for i in range(256))
        codes = [format(code, f'0{length}b') for code, length in huff.canonical_codes(huff.code_lengths(data)).values()]
        for a, b in itertools.permutations(codes, 2):
            self.assertFalse(b.startswith(a))

    def test_truncation_and_trailing_data(self):
        archive = huff.compress(b'abracadabra' * 20)
        for end in range(len(archive)):
            with self.subTest(end=end), self.assertRaises(huff.FormatError):
                huff.decompress(archive[:end])
        with self.assertRaises(huff.FormatError):
            huff.decompress(archive + b'\x00')

    def test_corruption_checks(self):
        archive = huff.compress(b'AAAAABBBBCCCDDE')
        mutations = []
        wrong_magic = bytearray(archive); wrong_magic[0] ^= 1; mutations.append(wrong_magic)
        wrong_crc = bytearray(archive); wrong_crc[20] ^= 1; mutations.append(wrong_crc)
        duplicate = bytearray(archive); duplicate[huff.HEADER.size + 2] = duplicate[huff.HEADER.size]; mutations.append(duplicate)
        zero_length = bytearray(archive); zero_length[huff.HEADER.size + 1] = 0; mutations.append(zero_length)
        wrong_size = bytearray(archive); wrong_size[11] += 1; mutations.append(wrong_size)
        payload_flip = bytearray(archive); payload_flip[-1] ^= 128; mutations.append(payload_flip)
        for corrupted in mutations:
            with self.subTest(corrupted=bytes(corrupted).hex()), self.assertRaises(huff.FormatError):
                huff.decompress(bytes(corrupted))

    def test_padding_and_output_limit(self):
        archive = huff.compress(b'A')
        corrupted = bytearray(archive); corrupted[-1] |= 1
        with self.assertRaisesRegex(huff.FormatError, 'padding'):
            huff.decompress(bytes(corrupted))
        with self.assertRaisesRegex(huff.FormatError, 'limit'):
            huff.decompress(huff.compress(b'AAAA'), max_output=3)

    def test_invalid_tables(self):
        for lengths in [{0: 1, 1: 1, 2: 1}, {0: 2, 1: 2}, {0: 2}]:
            with self.assertRaises(huff.FormatError):
                huff.canonical_codes(lengths)

    def test_cli_roundtrip_and_no_overwrite(self):
        # Keep test files in the project so restricted runtimes can write them.
        with project_test_directory() as directory:
            root = Path(directory)
            source, archive, restored = [root / name for name in ['input.txt', 'input.huf', 'restored.txt']]
            source.write_bytes(b'hello Huffman\n' * 100)
            def run(*args):
                return subprocess.run([sys.executable, str(Path(huff.__file__)), *map(str, args)], capture_output=True, text=True)
            self.assertEqual(run('compress', source, archive).returncode, 0)
            before = archive.read_bytes()
            self.assertEqual(run('compress', source, archive).returncode, 2)
            self.assertEqual(archive.read_bytes(), before)
            self.assertEqual(run('inspect', archive).returncode, 0)
            self.assertEqual(run('decompress', archive, restored).returncode, 0)
            self.assertEqual(restored.read_bytes(), source.read_bytes())
            self.assertEqual(run('compress', source, source, '--force').returncode, 2)
            self.assertEqual(source.read_bytes(), b'hello Huffman\n' * 100)


if __name__ == '__main__':
    unittest.main()
