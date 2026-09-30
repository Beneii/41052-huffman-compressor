# Laptop handoff — 41052 PA1

Latest submission preparation: REPORT.md and REPORT.pdf now use a concise, balanced AI disclosure while retaining the substantial initial implementation, test and report drafting assistance. Repetitive draft warnings have been removed. The final narrated video was published as unlisted: https://youtu.be/tCK9hSSQ6ZI . README links it and the GitHub release. It uses edited screen footage with separately recorded narration and captions; it is not a simultaneous single-take recording. The repository is still private, so marker access needs resolving. No assignment submission has been made. Do not invent student coding contributions or replace the final video with the older silent footage.

## Immediate objective
Benjamin will record the screen himself on his laptop, using his own voice and normal cursor. Help him run and explain the project in VS Code. Do not start mouse/keyboard automation or recording scripts unless he explicitly asks again. Desktop automation was stopped and verified to have no running processes.

Repository: https://github.com/Beneii/41052-huffman-compressor (private). Clone or pull `main`. Python 3.11+; compressor and tests use only the standard library. Run `python demo.py` and `python -m unittest -v` from the repository root. `demo.py` generates `demo-output`, which is deliberately ignored by Git.

## Recording support
Run `python video/serve.py`, then open http://localhost:8767/read-along.html for the standalone teleprompter. It has no screen capture, microphone access, or computer control. Start/pause the timer and advance sections manually while recording VS Code with your own recorder. Text is editable per section. Keep it off the recorded screen if possible.

`video/teleprompter.html` is the older video-synchronized microphone recorder; `walkthrough-silent.mp4` is the older automated footage. The student rejected that footage because it showed the automation cursor and saved output rather than a live terminal run. Do not present it as a finished submission video. `VIDEO_GUIDE.md`, `video/cues.json`, and the standalone read-along are useful narration drafts.

## What to show live
1. Open `examples/message.txt` in VS Code and show the original text.
2. In the VS Code terminal run the following commands individually:

```powershell
New-Item -ItemType Directory -Force demo-output
python huff.py compress examples/message.txt demo-output/message.huf --force
python huff.py inspect demo-output/message.huf
python huff.py decompress demo-output/message.huf demo-output/restored.txt --force
Get-Item examples/message.txt, demo-output/message.huf, demo-output/restored.txt | Format-Table Name,Length
python demo.py
python -m unittest -q
```

3. Open `demo-output/restored.txt` and compare it with the original. The sample is 530 bytes; archive is 362 bytes; restored file is 530 bytes. `python demo.py` checks identical SHA256 hashes and shows deliberate checksum corruption being rejected.
4. Explain `huff.py`: tree construction at line 21, canonical codes at line 53, compression at line 75, decompression at line 127. Invariant: heap trees partition symbols and each weight is the total frequency of its leaves. Tricky part: deterministic canonical reconstruction from symbol/code lengths. What breaks: removing `node = trie` at line 149 prevents resetting after each decoded symbol.
5. Show `results/table.md` and explain why gzip exploits repeated sequences and often does better. Keep the total screen recording 3–5 minutes with code visible and the student's own voice.

## Verified assignment context
41052 Advanced Algorithms PA1, individual, Track B. Huffman coding is an approved topic. The simulated annealing signup row was for a separate presentation. The brief requires repository/README, working tool, report, and a 3–5 minute narrated screencast showing code, a tricky part, an invariant, and a specific what-breaks example. AI is allowed/expected with honest disclosure of tools, extent/purposes, at least two real AI errors and corrections, and understanding versus trust.

Sources inspected on September 30, 2026 (Australia/Sydney):
- Brief: https://edstem.org/au/courses/37005/lessons/115269/slides/792282
- Approved list: https://edstem.org/au/courses/37005/lessons/111579/slides/768994
- Submission: https://edstem.org/au/courses/37005/lessons/117549/slides/817595
- Extension announcement (23:59 September 30 Sydney): https://edstem.org/au/courses/37005/discussion/3603319
- Report in repository clarification: https://edstem.org/au/courses/37005/discussion/3608605
- Canvas: course 40896, assignment 277915.

No assignment was submitted. The submission lesson exposed a Project Repository Link field. Confirm marker access to the private repository and add the final student-recorded video or accessible link before submission. See `SUBMISSION.md`.

## Completed work and remaining checks
Code, nine passing tests, eight verified benchmark cases, README, REPORT.md, five-page REPORT.pdf, and video guides are committed. No runtime dependencies. Actual AI corrections: repeated Counter construction in a comprehension was replaced by a single count; Windows restrictive temporary-directory permissions were fixed by creating ordinary project-local test directories.

Codex generated most code, tests, and report draft. The report does not fabricate personal reflection; Benjamin must review its claims and endorse or replace the reflection with his own understanding. His own narrated video is still outstanding. Do not invent personal experiences or claim he independently authored the implementation. Preserve truthful AI disclosure.

Suggested next prompt: "Read CODEX_HANDOFF.md. Help me run the demo in VS Code and record my own 3–5 minute explanation. Keep computer automation off."
