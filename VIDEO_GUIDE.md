# Start here before recording

Spend 15-20 minutes running the demo and explaining the four code points below in your own words. The brief asks for a single take, code visible, your own voice, 3-5 minutes. This guide is preparation; do not claim understanding just by reading it aloud.

## Run the demonstration

```powershell
cd C:\Users\Admin\Life\assignment\41052-huffman
python demo.py
python -m unittest -v
```

Have `huff.py` and `results/table.md` open beside the terminal. Use Win+Alt+R if Windows Game Bar recording is already available, or your existing screen recorder. Record code and terminal; production quality does not matter.

## Suggested 4 minute route

1. **0:00-0:40 - What the tool does.** Track B compressor. Run `python demo.py`. Point out compression size, matching hashes and rejected corruption. It handles bytes so text encodings and binary files use the same algorithm.
2. **0:40-1:35 - Core algorithm.** Show `code_lengths`. Each leaf starts with a frequency; the priority queue supplies the two lightest trees; their combined weight goes back into the heap. Leaves deeper in the final tree get longer codes. The serial number stops Python comparing a tuple tree against an integer when weights tie.
3. **1:35-2:35 - Tricky part.** Show `canonical_codes` and the bit-packing loop in `compress`. Canonical codes are sorted by length then byte value; shift to the next length, assign and increment. Only lengths need to be stored. Explain how a 3-bit code can straddle a byte boundary, and why the header stores the exact valid bit count.
4. **2:35-3:25 - Invariant and what breaks.** Heap trees always partition the alphabet, and each weight equals the sum of frequencies underneath it. Established when leaves are created; preserved by two-minimum merging. Then show `node = trie` in `decompress`: after a leaf is emitted the next code must start at the root. Removing that reset makes decoding continue below a leaf and reject or misdecode the following bits.
5. **3:25-4:15 - Findings and AI.** Show the gzip results. Single-byte Huffman modelling cannot exploit repeated substrings, while gzip can. Name the Counter rescan correction and the test-directory ACL failure. Say honestly that Codex generated most of the project, and identify what you can now explain versus what you still accept on trust.

## Four checks you should answer without reading

- Why do frequent symbols usually get shorter codes? Moving high weights deeper costs more in the weighted path length; merging light weights minimises that cost.
- Why are codes unambiguous without separators? No code is a prefix of another, so reaching a leaf identifies exactly one byte.
- Why store the bit count as well as original size? The last byte is padded; the count distinguishes real bits from padding, and the original size adds a consistency check.
- Why did gzip win on repeated text? It can refer to repeated sequences; this tool only models the frequency of individual bytes.

If you cannot explain a step, describe that uncertainty in the AI-use section. Review `REPORT.md` before submission; its reflection is based on real project findings but has not been confirmed as your personal learning.
