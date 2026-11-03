# Agent installation guide

SushaIPTV Orsay SmartHub (widget ID `SushaTV`) and SushaMedia Orsay SmartHub (widget ID `SushaMegaTV`) are separate applications. Confirm the repository root and `git status --short` before working; preserve unrelated changes and do not modify the other project or its installed service.

Read [README.en.md](README.en.md) and [the test record](TESTING.md). The current source embeds playlist snapshots, but physical TV installation and standalone playback remain unverified. The previously observed 0.109 installation used `tools/playlist-bridge.py`; check current service state before removing or stopping anything.

For an authorized deployment:

1. Identify the TV's current IP, a stable local sync IP, the active Apps Sync server, its manifest and every installed user widget's package and download URL. Do not assume historical IPs, host paths or developer menu availability are current. Preserve a known-good manifest and ZIPs for rollback.
2. Download or obtain the three M3U snapshots into a private temporary directory. Build the package using the commands in [README.en.md](README.en.md) and inspect its manifest and ZIP. Do not publish playlist snapshots, URLs containing credentials or private package data.
3. The builder creates a manifest containing only SushaTV, and `tools/widget-server.py` serves only that manifest and SushaTV's ZIP. If other widgets are installed, retain all their entries and keep their ZIPs reachable at their original URLs; a combined manifest alone does not preserve their packages. Adapt the sync serving setup or use the existing one without overwriting unrelated applications. Verify the selected address and port are available before starting a server.
4. Use Apps Sync only on the owner's authorized TV; request physical interaction only when necessary. Avoid resetting Smart Hub or removing another app. Confirm the installation after a full TV restart and verify the other applications remain intact.
5. Test all three tabs, remote controls, picture, sound and Return. To verify true standalone operation, disable only the relevant bridge after confirming that doing so will not disrupt another service, then play a compatible stream with the PC service unavailable. Playback and source availability are not guaranteed by a successful build or HTTP response.

Run the local checks listed in the README. Report the exact commit and package version, the installation and real-device observations, the state of other applications, and anything unverified. Never report autonomous playback as confirmed without that device test.
