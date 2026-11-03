#!/usr/bin/env python3
"""Serve the three user-selected playlists to the specified TV only."""
import argparse
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import threading
import time

SOURCES = {
    'films': 'https://raw.githubusercontent.com/Dimonovich/TV/Dimonovich/FREE/FILMS.m3u',
    'kinofilm': 'https://raw.githubusercontent.com/slava-67/TV/refs/heads/IPTV/kinofilm.m3u',
    'kino-plus': 'https://raw.githubusercontent.com/slava-67/TV/refs/heads/IPTV/kino-plus.m3u',
}
MAX_BYTES = 8 * 1024 * 1024


def refresh(cache):
    while True:
        for name, url in SOURCES.items():
            temporary = cache / (name + '.download')
            try:
                result = subprocess.run(['curl', '--fail', '--silent', '--show-error', '--location',
                                         '--max-time', '40', '--max-filesize', str(MAX_BYTES),
                                         '--output', str(temporary), url], capture_output=True, timeout=45)
                if result.returncode == 0 and 0 < temporary.stat().st_size <= MAX_BYTES and temporary.read_bytes().startswith(b'#EXTM3U'):
                    temporary.replace(cache / (name + '.m3u'))
            except (OSError, subprocess.SubprocessError):
                pass
            finally:
                temporary.unlink(missing_ok=True)
        time.sleep(1800)


class Handler(BaseHTTPRequestHandler):
    def __init__(self, *args, cache, tv, **kwargs):
        self.cache, self.tv = cache, tv
        super().__init__(*args, **kwargs)

    def do_GET(self):
        name = self.path.removeprefix('/').removesuffix('.m3u')
        if self.client_address[0] != self.tv or self.path != '/' + name + '.m3u' or name not in SOURCES:
            self.send_error(404)
            return
        try:
            body = (self.cache / (name + '.m3u')).read_bytes()
        except OSError:
            self.send_error(503, 'Playlist unavailable')
            return
        self.send_response(200)
        self.send_header('Content-Type', 'application/vnd.apple.mpegurl; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def log_message(self, *args):
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bind', required=True)
    parser.add_argument('--tv', required=True)
    parser.add_argument('--port', type=int, default=18767)
    parser.add_argument('--cache', type=Path, required=True)
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    threading.Thread(target=refresh, args=(args.cache,), daemon=True).start()
    ThreadingHTTPServer((args.bind, args.port), partial(Handler, cache=args.cache, tv=args.tv)).serve_forever()


if __name__ == '__main__':
    main()
