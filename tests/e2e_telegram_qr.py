"""Verify the packaged IPTV widget's remote-accessible Telegram QR in a browser."""
import os
import json
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SESSION, PORT = 'sushatv-telegram-qr', '18794'


def run(*args):
    result = subprocess.run([os.environ.get('AGENT_BROWSER', 'agent-browser'), '--session', SESSION, *args], capture_output=True, text=True, timeout=45)
    if result.returncode:
        raise AssertionError(str(args) + '\n' + result.stdout + result.stderr)
    return result.stdout.strip()


def data(expression):
    return json.loads(json.loads(run('eval', 'JSON.stringify(' + expression + ')')))


def main():
    with tempfile.TemporaryDirectory(prefix='sushatv-qr-') as tmp:
        directory = Path(tmp); playlists = directory / 'lists'; playlists.mkdir()
        for name in ('films', 'kinofilm', 'kino-plus'):
            (playlists / (name + '.m3u')).write_text('#EXTM3U\n#EXTINF:-1,Test\nhttps://example.invalid/a.m3u8\n')
        package, init, site = directory / 'widget.zip', directory / 'init.js', directory / 'site'
        subprocess.run(['python3', 'tools/build-widget.py', '--playlists-dir', str(playlists), '--output', str(package),
                        '--server-dir', str(directory / 'stage'), '--server-ip', '127.0.0.1'], cwd=ROOT, check=True, capture_output=True)
        with zipfile.ZipFile(package) as archive: archive.extractall(site)
        init.write_text("""Object.defineProperty(window.screen,'width',{value:960,configurable:true});Object.defineProperty(window.screen,'height',{value:540,configurable:true});
        window.Common={API:{Widget:function(){this.sendReadyEvent=function(){};this.sendReturnEvent=function(){};},
        TVKeyValue:function(){this.KEY_INFO=31;this.KEY_RETURN=88;this.KEY_ENTER=29443;this.KEY_VOL_UP=7;this.KEY_VOL_DOWN=11;this.KEY_MUTE=27;},
        Plugin:function(){this.registKey=function(){};}}};""", encoding='utf-8')
        server = subprocess.Popen(['python3', '-m', 'http.server', PORT, '--bind', '127.0.0.1'], cwd=site,
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            run('--init-script', str(init), 'open', 'http://127.0.0.1:' + PORT)
            run('set', 'viewport', '1280', '720'); run('reload'); run('wait', '--text', 'SushaIPTV')
            shortcut = data("(function(){var r=document.getElementById('telegram-shortcut').getBoundingClientRect();return {left:r.left,right:r.right}}())")
            assert shortcut['left'] >= 0 and shortcut['right'] <= 960, shortcut
            run('eval', 'App.onKey({keyCode:31})'); run('wait', '--text', '@AIShtokov'); run('wait', '500')
            qr = data("(function(){var d=document.getElementById('telegram-dialog'),r=d.getBoundingClientRect(),i=d.querySelector('img');return {visible:d.className!=='hidden',loaded:i.complete&&i.naturalWidth>0,left:r.left,right:r.right,top:r.top,bottom:r.bottom}}())")
            assert qr['visible'] and qr['loaded'] and qr['left'] >= 0 and qr['right'] <= 960 and qr['bottom'] <= 540, qr
            run('screenshot', '/tmp/sushatv-telegram-qr.png')
            run('eval', 'App.onKey({keyCode:88})')
            assert data("({closed:document.getElementById('telegram-dialog').className==='hidden'})")['closed']
            print('PASS: packaged QR, INFO and Return with a simulated Samsung remote')
            print('LIMIT: the real remote and physical TV were not tested')
        finally:
            subprocess.run([os.environ.get('AGENT_BROWSER', 'agent-browser'), '--session', SESSION, 'close'], capture_output=True, timeout=15)
            server.terminate(); server.wait(timeout=5)


if __name__ == '__main__': main()
