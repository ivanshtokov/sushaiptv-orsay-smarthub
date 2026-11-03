# Architecture

`app/` is an ES5 Samsung Orsay widget. It displays three playlist tabs and passes stream URLs to the TV player. The widget cannot add unsupported codecs or request headers.

`tools/build-widget.py` embeds three M3U snapshots in a private ZIP. Rebuild and sync to update them. The widget ID is `SushaTV`.

`tools/widget-server.py` serves that ZIP and a one-app manifest to the specified TV. Preserve other widget entries and ZIPs with a combined server before multi-app sync. The optional playlist bridge supports older installations; the snapshot build does not use it.

Local tests use sample playlists and simulated remote keys. Verify playback and standalone operation on the physical TV.
