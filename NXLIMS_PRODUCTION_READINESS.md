# NxLIMS Production Readiness Guide

This repository now includes core NxLIMS workflows, branding assets, offline sync APIs, and a Windows desktop installer project.

## 1) Production baseline checklist

- Configure HTTPS with valid TLS certificates.
- Enable regular database backups and offsite backup retention.
- Restrict database and Redis network exposure to private subnets.
- Set up SMTP, SMS provider, and WhatsApp webhook in `LIMS Settings`.
- Create and enforce role-based users for reception, technicians, and managers.
- Enable audit and log retention monitoring.
- Run periodic restore drills from backups.

## 2) Branding assets

The following assets are wired for NxLIMS:

- App logo: `/assets/erpnext/images/nxlims-logo.svg`
- Favicon: `/assets/erpnext/images/nxlims-favicon.ico`
- Splash animation JSON: `/assets/erpnext/images/branding/nxlims-splash-screen.json`
- Theme overrides: `/assets/erpnext/css/nxlims-brand.css`

## 3) Offline sync APIs

Two backend sync APIs are available in `erpnext.lims.sync`:

- `push_sync_events(events, device_id)`
- `pull_sync_changes(since, limit)`

### Sync guarantees

- Idempotent replay by `event_id` via `LIMS Sync Event`.
- Duplicate `event_id` requests are acknowledged without reapplying.
- Events are persisted with `Applied` or `Failed` status for operational traceability.

### Example push payload

```json
{
  "device_id": "device-001",
  "events": [
    {
      "event_id": "evt-20260320-0001",
      "doctype": "LIMS Patient",
      "operation": "update",
      "payload": {
        "name": "LIM-PAT-2026-0001",
        "mobile_no": "+1555000001"
      }
    }
  ]
}
```

## 4) Windows executable installer

Desktop wrapper project:

- `desktop/nxlims-desktop`

Build steps on Windows:

```powershell
cd desktop\nxlims-desktop
npm install
npm run dist:win
```

Generated output:

- Installer `.exe` under `desktop/nxlims-desktop/dist/`

## 5) Go-live validation

- Validate patient registration to billing to result dispatch flow.
- Validate critical result notification path to referred doctor.
- Validate offline event capture and replay with temporary network cut.
- Validate profitability reports for 7, 14, and 30 day windows.
