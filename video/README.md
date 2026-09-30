# Record your four-minute explanation

1. Run `START_PROMPTER.cmd` in this folder.
2. Preview the actual VS Code screen recording. Edit the script to words you can explain yourself.
3. Click **Record my voice + start video**. Allow your microphone. Your voice stays local and downloads as `narration.webm`.
4. Run `python combine_narration.py "path/to/narration.webm"` in this folder.
5. Watch `walkthrough-with-my-voice.mp4` before submitting.

The silent footage is a genuine capture of the assignment's VS Code window, navigated automatically. It shows original text, actual file sizes, the binary archive, restored text, real CLI verification output saved to a file, implementation, tests, and benchmark results. It does not represent the student personally operating the mouse. The narration must be the student's own voice.

Capture uses Windows window screenshots at approximately two frames per second, encoded as a 10 fps MP4. Original captures are local in `live-frames`; no other application windows are recorded. The four explanation sections are paced to 40 seconds each. The terminal capture experiment produced black frames and is not used.
