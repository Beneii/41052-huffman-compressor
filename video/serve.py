"""Local-only server with byte ranges for reliable video seeking."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re


class Handler(SimpleHTTPRequestHandler):
    def send_head(self):
        self.range_end = None
        path = Path(self.translate_path(self.path))
        if not path.is_file() or 'Range' not in self.headers:
            return super().send_head()
        match = re.fullmatch(r'bytes=(\d+)-(\d*)', self.headers['Range'])
        if not match:
            self.send_error(416); return None
        size = path.stat().st_size
        start = int(match[1]); end = min(int(match[2]) if match[2] else size - 1, size - 1)
        if start > end:
            self.send_error(416); return None
        source = path.open('rb'); source.seek(start)
        self.range_end = end - start + 1
        self.send_response(206)
        self.send_header('Content-Type', self.guess_type(str(path)))
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.send_header('Content-Length', str(self.range_end))
        self.end_headers()
        return source

    def copyfile(self, source, outputfile):
        if self.range_end is None:
            return super().copyfile(source, outputfile)
        remaining = self.range_end
        while remaining:
            chunk = source.read(min(65536, remaining))
            if not chunk:
                break
            outputfile.write(chunk); remaining -= len(chunk)


if __name__ == '__main__':
    import os
    os.chdir(Path(__file__).resolve().parent)
    print('Teleprompter: http://localhost:8767/teleprompter.html', flush=True)
    ThreadingHTTPServer(('127.0.0.1', 8767), Handler).serve_forever()
