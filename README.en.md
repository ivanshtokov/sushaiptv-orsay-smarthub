# SushaIPTV Orsay SmartHub

[Русский](README.md) | English

SushaIPTV Orsay SmartHub (formerly SushaTV) is an IPTV widget for Samsung Smart TV Legacy / Orsay. Device testing targeted the Samsung UA32J4303 running firmware T-N14MJUABC-1080.0. This is a separate project and does not replace SushaMedia Orsay SmartHub (formerly SushaMegaTV). The widget interface is in Russian.

## Features and status

The widget contains three user-selected playlist tabs: FILMS, kinofilm and kino-plus. Left and right switch tabs; up and down select an item. OK starts a stream, a second OK switches to full screen, and Return restores the list. VOL+/VOL− and Mute control sound; CH+/CH− switch items within the current playlist.

Starting with version 0.110, the build embeds snapshots of the three playlists in its ZIP. Viewing does not require a computer, but streams still require internet access. Playlists are refreshed when the widget is rebuilt and synced. **Version 0.110 was checked locally in a browser; the renamed version 0.111 and independent playback have not yet been checked on the physical TV.** At the time of the 2 November 2026 check, version 0.109 was installed on the target TV and used a local playlist service. See the [test record](TESTING.md) for details.

The existing Apps Sync widget ID `SushaTV` is retained for compatibility; `sushaiptv-orsay-smarthub` is a suggested repository name.

[Architecture and trade-offs](docs/architecture.md) describes the widget, playlist snapshots and sync server.

The Telegram QR code for `@AIShtokov` opens using the INFO remote key or the Telegram button in the header. The physical INFO key on the target TV has not yet been verified.

## Build

You need Python 3.9+, `curl` and three M3U files. The commands below create separate temporary directories; they do not change the TV.

```sh
PLAYLISTS_DIR="$(mktemp -d)"
SYNC_DIR="$(mktemp -d)"
SYNC_IP="192.168.1.20"  # example: replace with the computer's actual LAN address

curl -fL --max-time 60 -o "$PLAYLISTS_DIR/films.m3u" \
  'https://raw.githubusercontent.com/Dimonovich/TV/Dimonovich/FREE/FILMS.m3u'
curl -fL --max-time 60 -o "$PLAYLISTS_DIR/kinofilm.m3u" \
  'https://raw.githubusercontent.com/slava-67/TV/refs/heads/IPTV/kinofilm.m3u'
curl -fL --max-time 60 -o "$PLAYLISTS_DIR/kino-plus.m3u" \
  'https://raw.githubusercontent.com/slava-67/TV/refs/heads/IPTV/kino-plus.m3u'

python3 tools/build-widget.py \
  --playlists-dir "$PLAYLISTS_DIR" --output "$SYNC_DIR/widget.zip" \
  --server-dir "$SYNC_DIR" --server-ip "$SYNC_IP"
```

The builder verifies the ZIP and writes `sushatv.zip` and `widgetlist.xml` to `SYNC_DIR`. Both package copies use mode `0600`; run the sync server as their owner or arrange access explicitly. The generated manifest contains **only SushaTV**. Playlists and the resulting ZIP may contain links that should not be published without review. Refreshing the lists requires a new build.

## Install with Apps Sync

Before syncing, preserve the current manifest and packages of installed applications. If SushaMegaTV or other user widgets are installed, use a combined manifest and ensure every ZIP remains reachable at its download address. Keeping XML entries alone is insufficient. Do not replace the existing manifest with the single-app SushaTV manifest.

`tools/widget-server.py` serves only `widgetlist.xml` and `sushatv.zip` to the specified TV IP. A multi-app sync requires a server that also serves the other packages. Check that the selected IP is assigned to the computer, that the port is free and that existing applications remain available. On the tested firmware, Samsung Apps → Options → IP Settings and Apps Sync were available after signing in as `develop`; menu names and availability may differ.

Both `--bind` and `--tv` are required when running `tools/widget-server.py` or the optional playlist bridge. The builder also requires an explicit IPv4 `--server-ip`; no address from the author's network is assumed.

After syncing, open the widget and check tabs, picture, sound and remote controls; restart the TV and check again. Keep the prior ZIP and manifest for rollback. An [agent guide](AGENTS.md) describes the deployment workflow.

## Project checks

```sh
node --check app/app.js
node tests/test-remote.js
python3 -m unittest discover -s tests -v
git diff --check
```

Network tests use local loopback sockets. Neither these tests nor browser checks establish installation or playback on a physical TV.

GitHub Actions also runs Ruff and an ES5 syntax check. The optional QR browser test requires [agent-browser](https://github.com/vercel-labs/agent-browser) with its browser installed; set `AGENT_BROWSER` if a custom executable is needed.

## Limitations

Third-party providers control playlist contents and availability. Some URLs may require authorization, custom headers, a specific region or codecs the TV cannot decode. The widget does not send custom M3U headers or bypass provider restrictions. Not every entry is a working stream. The project has no stated license; playlists and content are supplied by third parties.
