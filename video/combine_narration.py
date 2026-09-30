"""python combine_narration.py path/to/downloaded-narration.webm"""
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
if len(sys.argv) != 2:
    raise SystemExit('Usage: python combine_narration.py path/to/narration.webm')
audio = Path(sys.argv[1]).resolve()
if not audio.is_file():
    raise SystemExit('Narration file not found')
subprocess.run(['C:/Users/Admin/Life/tools/ffmpeg/bin/ffmpeg.exe', '-y',
    '-i', str(root / 'walkthrough-silent.mp4'), '-i', str(audio),
    '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac',
    '-af', 'apad', '-t', '240', '-movflags', '+faststart',
    str(root / 'walkthrough-with-my-voice.mp4')], check=True)
print('Created walkthrough-with-my-voice.mp4; watch it to check timing before submitting.')
