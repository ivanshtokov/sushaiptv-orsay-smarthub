import importlib.util
from functools import partial
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
import unittest

spec = importlib.util.spec_from_file_location('playlist_bridge', Path(__file__).resolve().parents[1] / 'tools/playlist-bridge.py')
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


class BridgeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.cache = Path(self.tmp.name)
        (self.cache / 'films.m3u').write_text('#EXTM3U\n', encoding='utf-8')
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), partial(bridge.Handler, cache=self.cache, tv='127.0.0.1'))
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.tmp.cleanup()

    def get(self, path):
        conn = HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        conn.request('GET', path)
        response = conn.getresponse()
        result = (response.status, response.getheader('Access-Control-Allow-Origin'), response.read())
        conn.close()
        return result

    def test_allowlisted_playlist(self):
        self.assertEqual(self.get('/films.m3u'), (200, '*', b'#EXTM3U\n'))

    def test_missing_cache_and_paths(self):
        self.assertEqual(self.get('/kino-plus.m3u')[0], 503)
        for path in ('/other.m3u', '/../films.m3u', '/films.m3u?x=1'):
            self.assertEqual(self.get(path)[0], 404)

    def test_other_clients_cannot_read(self):
        self.server.RequestHandlerClass = partial(bridge.Handler, cache=self.cache, tv='192.0.2.1')
        self.assertEqual(self.get('/films.m3u')[0], 404)


if __name__ == '__main__':
    unittest.main()
