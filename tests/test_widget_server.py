import importlib.util
from functools import partial
from http.client import HTTPConnection
from http.server import HTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
import unittest

spec = importlib.util.spec_from_file_location('widget_server', Path(__file__).resolve().parents[1] / 'tools/widget-server.py')
server_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server_module)


class WidgetServerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        Path(self.tmp.name, 'widgetlist.xml').write_text('<rsp/>', encoding='utf-8')
        handler = partial(server_module.Handler, tv='127.0.0.1', directory=self.tmp.name)
        self.server = HTTPServer(('127.0.0.1', 0), handler)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.tmp.cleanup()

    def get(self, path, method='GET'):
        conn = HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        conn.request(method, path)
        response = conn.getresponse()
        result = (response.status, response.read())
        conn.close()
        return result

    def test_manifest_with_query(self):
        self.assertEqual(self.get('/widgetlist.xml?test=1'), (200, b'<rsp/>'))

    def test_unknown_path_and_client_are_denied(self):
        self.assertEqual(self.get('/other?next=widgetlist.xml')[0], 404)
        self.server.RequestHandlerClass = partial(server_module.Handler, tv='192.0.2.1', directory=self.tmp.name)
        self.assertEqual(self.get('/widgetlist.xml?test=1')[0], 404)

    def test_head_obeys_the_same_client_and_path_restrictions(self):
        Path(self.tmp.name, 'private.txt').write_text('private', encoding='utf-8')
        self.assertEqual(self.get('/widgetlist.xml', 'HEAD')[0], 200)
        self.assertEqual(self.get('/private.txt', 'HEAD')[0], 404)
        self.server.RequestHandlerClass = partial(server_module.Handler, tv='192.0.2.1', directory=self.tmp.name)
        self.assertEqual(self.get('/widgetlist.xml', 'HEAD')[0], 404)


if __name__ == '__main__':
    unittest.main()
