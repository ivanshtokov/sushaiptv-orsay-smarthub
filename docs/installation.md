# Install SushaIPTV

You need an Orsay TV with Apps Sync, Python 3.9+, `curl`, and three M3U files. Connect the TV and computer to the same network.

## Build

Set the computer's LAN address and prepare a private directory:

```sh
SYNC_IP="192.168.1.10"  # replace with the computer's address
WORK_DIR="$(mktemp -d)"
mkdir -p "$WORK_DIR/playlists" "$WORK_DIR/sync"
```

Place your files in `$WORK_DIR/playlists` as `films.m3u`, `kinofilm.m3u`, and `kino-plus.m3u`. The project was tested with these public lists:

```sh
curl -fL --max-time 60 -o "$WORK_DIR/playlists/films.m3u" 'https://raw.githubusercontent.com/Dimonovich/TV/Dimonovich/FREE/FILMS.m3u'
curl -fL --max-time 60 -o "$WORK_DIR/playlists/kinofilm.m3u" 'https://raw.githubusercontent.com/slava-67/TV/refs/heads/IPTV/kinofilm.m3u'
curl -fL --max-time 60 -o "$WORK_DIR/playlists/kino-plus.m3u" 'https://raw.githubusercontent.com/slava-67/TV/refs/heads/IPTV/kino-plus.m3u'
python3 tools/build-widget.py --playlists-dir "$WORK_DIR/playlists" \
  --output "$WORK_DIR/widget.zip" --server-dir "$WORK_DIR/sync" --server-ip "$SYNC_IP"
```

Both ZIP copies use mode `0600` and can contain private stream URLs. Keep `$WORK_DIR` private. Rebuild and sync when you want fresh playlist snapshots.

## Sync

The generated `widgetlist.xml` contains only SushaTV. If other user-installed widgets exist, preserve their manifest entries and make every ZIP reachable at its original address before running Apps Sync. `widget-server.py` serves only SushaTV; use a server that serves the combined manifest and other ZIPs for a multi-app setup.

For a TV with no other user-installed widgets, set its address and start the server:

```sh
TV_IP="192.168.1.20"  # replace with the TV's address
python3 tools/widget-server.py --bind "$SYNC_IP" --tv "$TV_IP" \
  --port 80 --directory "$WORK_DIR/sync"
```

Use the package owner's account. Port 80 may require privileges; do not stop an existing server to free it. On the tested TV, sign in as `develop`, open Samsung Apps → Options → IP Settings, enter `SYNC_IP`, then choose Apps Sync. Menu names vary by model.

Open SushaIPTV and check the tabs, a stream, sound and Return. Restart the TV and repeat. To check standalone playback, stop the playlist bridge only if it serves no other app, then play a compatible stream with the computer service unavailable.
