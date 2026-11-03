#!/usr/bin/env python3
"""Serve the Apps Sync manifest and package to one TV."""
import argparse
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, tv, **kwargs):
        self.tv = tv
        super().__init__(*args, **kwargs)

    def allowed(self):
        if self.client_address[0] != self.tv or urlsplit(self.path).path not in ('/widgetlist.xml', '/sushatv.zip'):
            self.send_error(404)
            return False
        return True

    def do_GET(self):
        if self.allowed():
            super().do_GET()

    def do_HEAD(self):
        if self.allowed():
            super().do_HEAD()

    def log_message(self, *args):
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bind', required=True)
    parser.add_argument('--tv', required=True)
    parser.add_argument('--port', type=int, default=80)
    parser.add_argument('--directory', type=Path, required=True)
    args = parser.parse_args()
    HTTPServer((args.bind, args.port), partial(Handler, tv=args.tv, directory=str(args.directory))).serve_forever()


if __name__ == '__main__':
    main()
