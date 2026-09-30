"""Byte-oriented canonical Huffman compressor. Standard library only."""
from __future__ import annotations

import argparse
from collections import Counter
import heapq
from pathlib import Path
import struct
import sys
import zlib

MAGIC = b'HUF1'
# magic, original byte count, payload bit count, CRC32, symbol count
HEADER = struct.Struct('>4sQQIH')


class FormatError(ValueError):
    """An archive is malformed, truncated, or fails its integrity check."""


def code_lengths(data: bytes) -> dict[int, int]:
    """Construct a Huffman tree; return depths, not tree-dependent bit codes."""
    frequencies = Counter(data)
    if not frequencies:
        return {}
    heap = []
    serial = 0
    for symbol, weight in sorted(frequencies.items()):
        heap.append((weight, serial, symbol))
        serial += 1
    heapq.heapify(heap)
    while len(heap) > 1:
        weight_a, _, a = heapq.heappop(heap)
        weight_b, _, b = heapq.heappop(heap)
        # Invariant: heap trees partition the symbols; each weight is the
        # sum of leaf frequencies. Merging the two minima preserves it.
        heapq.heappush(heap, (weight_a + weight_b, serial, (a, b)))
        serial += 1
    lengths = {}
    stack = [(heap[0][2], 0)]
    while stack:
        tree, depth = stack.pop()
        if isinstance(tree, int):
            # A singleton still needs a one-bit code, so its repetitions
            # can be represented and checked like other inputs.
            lengths[tree] = max(1, depth)
        else:
            stack.append((tree[0], depth + 1))
            stack.append((tree[1], depth + 1))
    return lengths


def canonical_codes(lengths: dict[int, int]) -> dict[int, tuple[int, int]]:
    """Assign codes in (length, symbol) order, validating prefix capacity."""
    codes = {}
    code = previous_length = 0
    for symbol, length in sorted(lengths.items(), key=lambda item: (item[1], item[0])):
        if not 0 <= symbol <= 255 or not 1 <= length <= 255:
            raise FormatError('symbol or code length is out of range')
        code <<= length - previous_length
        if code >= (1 << length):
            raise FormatError('oversubscribed code lengths')
        codes[symbol] = (code, length)
        code += 1
        previous_length = length
    # Huffman's tree is full, except for the one-symbol special case.
    if len(lengths) == 1:
        if previous_length != 1:
            raise FormatError('singleton code must have length one')
    elif lengths and code != (1 << previous_length):
        raise FormatError('incomplete code table')
    return codes


def compress(data: bytes) -> bytes:
    lengths = code_lengths(data)
    codes = canonical_codes(lengths)
    frequencies = Counter(data)
    bit_count = sum(frequencies[symbol] * length for symbol, length in lengths.items())
    payload = bytearray()
    accumulator = buffered = 0
    for symbol in data:
        code, length = codes[symbol]
        accumulator = (accumulator << length) | code
        buffered += length
        while buffered >= 8:
            buffered -= 8
            payload.append((accumulator >> buffered) & 255)
        accumulator &= (1 << buffered) - 1
    if buffered:
        payload.append(accumulator << (8 - buffered))
    table = b''.join(bytes((symbol, length)) for symbol, length in sorted(lengths.items()))
    return HEADER.pack(MAGIC, len(data), bit_count, zlib.crc32(data), len(lengths)) + table + payload


def inspect_archive(archive: bytes) -> tuple[int, int, int, dict[int, int], bytes]:
    if len(archive) < HEADER.size:
        raise FormatError('truncated header')
    magic, original_size, bit_count, checksum, count = HEADER.unpack_from(archive)
    if magic != MAGIC:
        raise FormatError('not a HUF1 archive')
    if count > 256:
        raise FormatError('too many symbols')
    table_end = HEADER.size + count * 2
    if len(archive) < table_end:
        raise FormatError('truncated symbol table')
    lengths = {}
    for offset in range(HEADER.size, table_end, 2):
        symbol, length = archive[offset:offset + 2]
        if symbol in lengths:
            raise FormatError('duplicate symbol')
        lengths[symbol] = length
    canonical_codes(lengths)
    payload = archive[table_end:]
    if len(payload) != (bit_count + 7) // 8:
        raise FormatError('payload length does not match declared bit count')
    if bit_count % 8 and payload[-1] & ((1 << (8 - bit_count % 8)) - 1):
        raise FormatError('nonzero padding bits')
    if original_size == 0:
        if count or bit_count or checksum:
            raise FormatError('invalid empty archive')
    elif not count or bit_count < original_size or bit_count > original_size * 255:
        raise FormatError('inconsistent size and code table')
    return original_size, bit_count, checksum, lengths, payload


def decompress(archive: bytes, max_output: int = 256 * 1024 * 1024) -> bytes:
    original_size, bit_count, checksum, lengths, payload = inspect_archive(archive)
    if original_size > max_output:
        raise FormatError('declared output exceeds limit; use --max-output to raise it')
    codes = canonical_codes(lengths)
    trie = {}
    for symbol, (code, length) in codes.items():
        node = trie
        for shift in range(length - 1, -1, -1):
            node = node.setdefault((code >> shift) & 1, {})
        node['symbol'] = symbol
    output = bytearray()
    node = trie
    for index in range(bit_count):
        bit = (payload[index // 8] >> (7 - index % 8)) & 1
        if bit not in node:
            raise FormatError('payload contains an invalid code')
        node = node[bit]
        if 'symbol' in node:
            output.append(node['symbol'])
            if len(output) > original_size:
                raise FormatError('decoded output exceeds declared size')
            node = trie
    if node is not trie:
        raise FormatError('payload ends inside a code')
    if len(output) != original_size:
        raise FormatError('decoded size does not match original size')
    if zlib.crc32(output) != checksum:
        raise FormatError('CRC32 integrity check failed')
    return bytes(output)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Canonical Huffman file compressor (HUF1)')
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('compress', 'decompress'):
        command = commands.add_parser(name)
        command.add_argument('input', type=Path)
        command.add_argument('output', type=Path)
        command.add_argument('--force', action='store_true', help='replace an existing output file')
        if name == 'decompress':
            command.add_argument('--max-output', type=int, default=256 * 1024 * 1024,
                                 help='maximum decoded bytes (default: 268435456)')
    command = commands.add_parser('inspect')
    command.add_argument('input', type=Path)
    args = parser.parse_args(argv)
    try:
        data = args.input.read_bytes()
        if args.command == 'inspect':
            size, bits, checksum, lengths, _ = inspect_archive(data)
            print(f'Format: HUF1 | Original: {size} bytes | Archive: {len(data)} bytes')
            print(f'Symbols: {len(lengths)} | Payload: {bits} bits | CRC32: {checksum:08x}')
            print('Metadata validated; use decompress to verify decoded data and CRC32.')
            return 0
        if args.input.resolve() == args.output.resolve():
            raise ValueError('input and output must be different files')
        if args.command == 'compress':
            result = compress(data)
        else:
            if args.max_output < 0:
                raise ValueError('--max-output must be nonnegative')
            result = decompress(data, args.max_output)
        # Exclusive creation protects existing files by default, including
        # when a file appears between an existence check and this write.
        with args.output.open('wb' if args.force else 'xb') as target:
            target.write(result)
        ratio = len(result) / len(data) if data else 0
        print(f'{args.command}: {len(data)} -> {len(result)} bytes (output/input: {ratio:.3f})')
        print(f'Wrote {args.output}')
        return 0
    except (OSError, ValueError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
