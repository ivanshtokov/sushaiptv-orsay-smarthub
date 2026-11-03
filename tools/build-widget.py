#!/usr/bin/env python3
"""Build a self-contained Legacy widget from three user-selected playlist snapshots."""
import argparse
import ipaddress
import json
import os
import re
import tempfile
from pathlib import Path
import shutil
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parent.parent
FILES = ('config.xml', 'widget.info', 'index.html', 'app/app.js', 'app/style.css',
         'icon/icon.png', 'icon/icon-big.png', 'icon/list.png', 'icon/list-big.png', 'assets/telegram-qr.png')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--playlists-dir', type=Path, required=True, help='directory with films.m3u, kinofilm.m3u and kino-plus.m3u')
    parser.add_argument('--server-dir', type=Path, required=True)
    parser.add_argument('--server-ip', required=True, type=ipaddress.IPv4Address)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.server_dir.mkdir(parents=True, exist_ok=True)
    snapshots = {}
    for index, name in enumerate(('films', 'kinofilm', 'kino-plus')):
        text = (args.playlists_dir / (name + '.m3u')).read_text(encoding='utf-8-sig')
        if not text.startswith('#EXTM3U') or len(text) > 8 * 1024 * 1024:
            raise ValueError('Invalid playlist: ' + name)
        rows, title = [], ''
        for raw in text.splitlines():
            line = raw.strip()
            if line.startswith('#EXTINF:'):
                title = line.partition(',')[2].strip()
            elif re.match(r'^https?://', line, re.I):
                rows.append({'name': title or 'Канал ' + str(len(rows) + 1), 'url': line})
                title = ''
        if not rows: raise ValueError('Playlist is empty: ' + name)
        snapshots['playlists/' + name + '.js'] = ('window.SUSHA_PLAYLISTS=window.SUSHA_PLAYLISTS||[];window.SUSHA_PLAYLISTS[' + str(index) + ']=' + json.dumps(rows, ensure_ascii=True, separators=(',', ':')) + ';').encode('ascii')
        print(name + ': ' + str(len(rows)) + ' entries')
    fd = os.open(args.output, os.O_CREAT | os.O_TRUNC | os.O_WRONLY | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    with os.fdopen(fd, 'wb') as stream:
        os.fchmod(stream.fileno(), 0o600)
        with ZipFile(stream, 'w', compression=ZIP_DEFLATED) as package:
            for name in FILES:
                info = ZipInfo(name, (1980, 1, 1, 0, 0, 0))
                info.compress_type = ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                package.writestr(info, (ROOT / name).read_bytes())
            for name, data in snapshots.items():
                info = ZipInfo(name, (1980, 1, 1, 0, 0, 0)); info.compress_type = ZIP_DEFLATED; info.external_attr = 0o644 << 16
                package.writestr(info, data)
    with ZipFile(args.output) as package:
        if package.testzip() is not None or set(package.namelist()) != set(FILES) | set(snapshots):
            raise RuntimeError('Invalid widget ZIP')
    fd, temporary = tempfile.mkstemp(prefix='.sushatv-', suffix='.zip', dir=args.server_dir)
    staged = Path(temporary)
    try:
        with os.fdopen(fd, 'wb') as dest, args.output.open('rb') as source:
            shutil.copyfileobj(source, dest)
        staged.replace(args.server_dir / 'sushatv.zip')
    finally:
        staged.unlink(missing_ok=True)
    manifest = ('<?xml version="1.0" encoding="UTF-8"?><rsp stat="ok"><list>'
                '<widget id="SushaTV"><title>SushaIPTV Orsay SmartHub</title><compression size="{}" type="zip"/>'
                '<description>IPTV</description><download>http://{}/sushatv.zip</download>'
                '</widget></list></rsp>').format(args.output.stat().st_size, escape(str(args.server_ip)))
    manifest_tmp = args.server_dir / 'widgetlist.xml.tmp'
    manifest_tmp.write_text(manifest, encoding='utf-8')
    manifest_tmp.replace(args.server_dir / 'widgetlist.xml')
    print('Built widget: {} bytes'.format(args.output.stat().st_size))


if __name__ == '__main__':
    main()
