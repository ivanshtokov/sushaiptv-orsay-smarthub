# Architecture

## Constraints and responsibilities

The target is a Samsung Legacy/Orsay TV with an older browser and a remote control. The ES5 widget in `app/` displays three playlist tabs, handles remote focus and audio controls, and hands stream URLs to the TV player. It cannot add missing codecs or provider-specific request headers.

`tools/build-widget.py` converts three user-provided M3U snapshots into JavaScript data included in a private widget ZIP. The installed widget reads these local snapshots; playback still requires the stream to be reachable. A new playlist snapshot requires rebuilding and Apps Sync. The optional playlist bridge is retained for older installations; it is not required by the snapshot-based widget.

The widget ID remains `SushaTV`. `tools/widget-server.py` serves one manifest and one ZIP to a configured TV IP. A multi-app installation needs a combined manifest and reachable packages for every app; this server alone does not supply other packages.

## Decisions and trade-offs

- **Playlist snapshots instead of a permanent bridge.** This removes the computer from the widget's playlist-loading path, but lists become stale until the next build and sync. External streams, compatibility and a successful standalone installation on a physical TV remain separate checks.
- **Build-time data instead of runtime M3U parsing.** The builder encodes titles and URLs as JSON in local JavaScript files compatible with the older browser. Snapshots and ZIPs may contain private URLs and must not be committed or published without review.
- **Separate app and explicit network addresses.** SushaIPTV does not share code or deployment state with SushaMedia. Sync tools require the caller to specify the host and TV addresses; an owner must preserve the existing manifest and packages when deploying.

## Verification boundary

Unit tests use local servers and sample lists. Browser tests simulate the Samsung remote. The [test record](../TESTING.md) distinguishes those checks from observations on the physical TV; they do not prove that all third-party playlist entries work.
