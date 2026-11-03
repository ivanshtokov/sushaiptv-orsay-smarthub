# Agent installation runbook

Use this runbook when the owner asks you to install SushaIPTV. Run the computer-side work yourself. Ask the owner only for actions that need the TV screen or physical remote.

## 1. Find the setup

Check `git rev-parse --show-toplevel`, `git status --short`, the TV model and its IP. Inspect the computer's network addresses, listeners and existing Apps Sync server. On Linux, start with `ip -4 -br addr` and `ss -ltnp`. Do not assume old addresses still apply.

Find the current sync manifest, package files and any other installed user widgets. Back up the manifest and ZIPs before changes. The included `widget-server.py` serves only SushaTV. If the TV has other user widgets, prepare a combined manifest and a server that keeps their ZIP URLs reachable. If you cannot preserve them, stop before Apps Sync and explain what is missing.

Ask for three playlist files or URLs. If the owner wants the project defaults, use the three URLs in [installation.md](installation.md). Never paste credential-bearing URLs into chat or logs.

## 2. Build and serve

Follow [installation.md](installation.md) using the actual computer and TV addresses. Build in a private temporary directory and verify the ZIP and manifest. Check port 80 before starting the sync server; keep any existing services running. A privileged port may need authorized elevation.

Leave the server running through Apps Sync. It permits requests from the configured TV IP; a 404 from another computer does not prove it is down.

## 3. Tell the owner

Once the server is ready, substitute the real sync IP:

> На телевизоре открой Samsung Apps и войди как `develop`. В Options → IP Settings укажи `<IP сервера>`, затем выбери Apps Sync. Напиши, когда синхронизация завершится.

If those menu items are absent, ask for the screen or a photo and adapt the steps to that model. Do not suggest a Smart Hub reset as the first fix.

After sync:

> Открой SushaIPTV. Проверь переключение вкладок, запуск канала, звук и Return. Затем перезапусти телевизор и открой приложение ещё раз.

## 4. Verify and report

Check the installed version if a TV debug channel exists. For a standalone claim, verify playback with the playlist bridge unavailable and avoid stopping a service used by another app. Ask the owner to confirm picture and sound when you cannot observe them.

Report the version, whether sync completed, what ran on the physical TV, and what remains untested. Do not treat a built ZIP, browser fixture or HTTP response as TV playback.
