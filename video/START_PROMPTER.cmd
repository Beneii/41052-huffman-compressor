@echo off
cd /d "%~dp0"
start "Huffman teleprompter" http://localhost:8767/teleprompter.html
python serve.py
