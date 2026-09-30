@echo off
cd /d "%~dp0"
start "Huffman read along" http://localhost:8767/read-along.html
python serve.py
