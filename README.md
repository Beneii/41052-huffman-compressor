# Huffman file compressor

41052 Advanced Algorithms - Programming Assignment 1, Track B.

A working binary file compressor using canonical Huffman coding. Written in Python 3.11+ using only the standard library. No installation or build step is required.

## Quick start

Open PowerShell in this folder:

```powershell
python demo.py
python -m unittest -v
```

The demo compresses a sample file, inspects its metadata, restores it, verifies the exact bytes and SHA256 hashes, and demonstrates rejection of a corrupted archive. It uses its own `demo-output` folder.

## Commands

```powershell
python huff.py compress examples/message.txt message.huf
python huff.py inspect message.huf
python huff.py decompress message.huf restored.txt
python benchmark.py
```

Outputs are never overwritten unless `--force` is supplied. Input and output must be different paths. Decompression has a default 256 MiB output limit; override it with `--max-output BYTES`. `inspect` validates metadata, not the decoded checksum; decompression validates both data and CRC32. Invalid input returns exit code 2 with a readable error.

## Files

- `huff.py`: algorithm, HUF1 binary format, defensive decoder and CLI.
- `test_huff.py`: nine tests including exhaustive small-alphabet optimality, prefix freedom, corruption and real CLI file operations.
- `demo.py`: repeatable demonstration for the video.
- `benchmark.py`: reproducible gzip comparison across eight datasets, five repetitions each.
- `results/benchmark.csv`, `results/environment.json`, `results/table.md`: measured results and environment.
- `REPORT.md` and `REPORT.pdf`: written report, including honest AI disclosure and a reflection section requiring student review.
- `VIDEO_GUIDE.md`: code walkthrough and understanding checks; preparation notes, not a claim of understanding.
- `SUBMISSION.md`: verified sources and remaining submission steps.

## Algorithm and format

Count byte frequencies. Repeatedly merge the two lightest trees with a priority queue. Tree leaf depths become code lengths. Sort by `(length, symbol)` and assign canonical codes. Pack them most-significant bit first. Decompression reconstructs the canonical table and follows a prefix trie.

HUF1 header: magic (4 bytes), original size (8), payload bit count (8), CRC32 (4), symbol count (2); all integers big-endian. Then `(symbol, code length)` byte pairs, followed by packed payload with zero padding in its last byte. Empty inputs have an empty table and payload. Single-symbol inputs use a one-bit code.

## Limits

This is an educational whole-file compressor, not a replacement for gzip. It models single-byte frequencies rather than repeated substrings, stores a per-file table, reads inputs into memory and runs its bit decoder in Python. CRC32 detects many accidental changes but is not authentication. No claim of hostile-input security or large-file streaming support is made.

AI assistance: Codex generated the implementation, tests, benchmark, documentation and report draft, and executed validation. See the report for actual corrections and the distinction between AI verification and student understanding.
