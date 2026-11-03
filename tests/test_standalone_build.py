import subprocess
import sys
import tempfile
import unittest
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]

class StandaloneBuildTest(unittest.TestCase):
    @unittest.skipUnless(hasattr(os, 'O_NOFOLLOW'), 'requires O_NOFOLLOW')
    def test_package_does_not_follow_output_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            playlists = root / 'lists'
            playlists.mkdir()
            for name in ('films', 'kinofilm', 'kino-plus'):
                (playlists / (name + '.m3u')).write_text('#EXTM3U\n#EXTINF:-1,Test\nhttps://example.invalid/a.m3u8\n')
            target = root / 'important.txt'
            target.write_text('keep')
            output = root / 'widget.zip'
            output.symlink_to(target)
            command = [sys.executable, str(ROOT / 'tools/build-widget.py'), '--playlists-dir', str(playlists),
                       '--output', str(output), '--server-dir', str(root / 'stage'), '--server-ip', '192.0.2.1']
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(target.read_text(), 'keep')
            self.assertFalse((root / 'stage' / 'sushatv.zip').exists())

    def test_sync_address_must_be_explicit_ipv4(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            command = [sys.executable, str(ROOT / 'tools/build-widget.py'), '--playlists-dir', str(root),
                       '--output', str(root / 'widget.zip'), '--server-dir', str(root / 'stage')]
            for args in ([], ['--server-ip', 'invalid.example']):
                result = subprocess.run(command + args, capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((root / 'stage').exists())

    def test_pack_contains_three_playlists_and_no_pc_bridge(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            playlists = root / 'lists'; playlists.mkdir()
            for name in ('films', 'kinofilm', 'kino-plus'):
                (playlists / (name + '.m3u')).write_text('\ufeff#EXTM3U\n#EXTINF:-1,Тест\nhttps://example.invalid/video.m3u8\n', encoding='utf-8')
            output = root / 'widget.zip'
            result = subprocess.run([sys.executable, str(ROOT / 'tools/build-widget.py'), '--playlists-dir', str(playlists), '--output', str(output), '--server-dir', str(root / 'stage'), '--server-ip', '192.0.2.1'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = ET.parse(root / 'stage' / 'widgetlist.xml').getroot()
            entry = manifest.find('./list/widget')
            self.assertEqual(entry.get('id'), 'SushaTV')
            self.assertEqual(entry.findtext('download'), 'http://192.0.2.1/sushatv.zip')
            self.assertEqual(entry.findtext('title'), 'SushaIPTV Orsay SmartHub')
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)
            self.assertEqual((root / 'stage' / 'sushatv.zip').stat().st_mode & 0o777, 0o600)
            with ZipFile(output) as z:
                self.assertIsNone(z.testzip())
                self.assertEqual(z.read('assets/telegram-qr.png'), (ROOT / 'assets/telegram-qr.png').read_bytes())
                self.assertIn(b'SushaIPTV Orsay SmartHub', z.read('config.xml'))
                self.assertIn(b'app/app.js?v=111', z.read('index.html'))
                self.assertNotIn(b'192.168.1.17:18767', z.read('app/app.js'))
                for name in ('films', 'kinofilm', 'kino-plus'):
                    data = z.read('playlists/' + name + '.js').decode('ascii')
                    self.assertIn('example.invalid/video.m3u8', data)
                    self.assertIn(r'\u0422\u0435\u0441\u0442', data)

if __name__ == '__main__': unittest.main()
