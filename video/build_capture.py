"""Encode genuine Windows window captures; preserve navigation and pacing."""
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parent
data = json.loads((root / 'capture-index.json').read_text())
frames, marks = data['frames'], data['marks']
entries = []
for begin, end in zip(marks, marks[1:]):
    section = frames[begin:end]
    times = [f['time'] for f in section]
    durations = [max(.02, b-a) for a,b in zip(times,times[1:])] + [.5]
    scale = 40 / sum(durations)
    for frame, duration in zip(section,durations):
        entries.extend(["file '" + frame['path'] + "'", f'duration {duration*scale:.6f}'])
entries.append("file '" + frames[-1]['path'] + "'")
(root / 'capture.ffconcat').write_text('\n'.join(entries))
subprocess.run(['C:/Users/Admin/Life/tools/ffmpeg/bin/ffmpeg.exe', '-hide_banner',
    '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i',
    str(root / 'capture.ffconcat'), '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2',
    '-r', '10', '-t', '240', '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
    '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
    str(root / 'walkthrough-silent.mp4')], check=True)
print('Encoded four minutes of real VS Code window capture.')
