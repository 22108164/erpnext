# NxLIMS Desktop (Windows Installer)

This folder contains a desktop wrapper for NxLIMS with Windows installer packaging.

## What it provides

- `NxLIMS.exe` desktop launcher (Electron)
- NSIS installer (`.exe`) for end users
- Configurable server URL (defaults to `http://127.0.0.1:8000`)
- Offline fallback screen with automatic reconnect attempts

## Build on Windows

1. Install Node.js LTS.
2. Open PowerShell in this folder.
3. Run:

```powershell
npm install
npm run dist:win
```

Installer output is generated in `dist/`.

## Offline and sync behavior

- Offline-only deployment: run NxLIMS server locally and keep `baseUrl` as `http://127.0.0.1:8000`.
- Online/offline with reconnect: use the backend sync APIs:
  - `erpnext.lims.sync.push_sync_events`
  - `erpnext.lims.sync.pull_sync_changes`

These APIs are idempotent through `event_id` and are designed for reliable data synchronization when clients reconnect.
