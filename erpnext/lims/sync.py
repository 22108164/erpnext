from __future__ import annotations

from datetime import datetime

import frappe
from frappe import _

ALLOWED_SYNC_DOCTYPES = {
	"LIMS Patient",
	"Lab Test Registration",
	"Lab Sample",
	"Lab Result Entry",
	"Lab Quality Control",
	"Lab Reagent",
	"Lab Expense",
}


@frappe.whitelist()
def push_sync_events(events=None, device_id: str | None = None):
	"""Apply offline events with idempotency checks for reconnect sync."""
	_settings_guard()
	events = frappe.parse_json(events) if events else []
	if not isinstance(events, list):
		frappe.throw(_("events must be a list"))
	if not device_id:
		frappe.throw(_("device_id is required"))

	results = []
	for event in events:
		event = event or {}
		event_id = event.get("event_id")
		target_doctype = event.get("doctype")
		operation = (event.get("operation") or "update").lower()
		payload = event.get("payload") or {}

		if not event_id or not target_doctype:
			results.append({"event_id": event_id, "status": "failed", "error": "Missing event_id or doctype"})
			continue

		if target_doctype not in ALLOWED_SYNC_DOCTYPES:
			results.append({"event_id": event_id, "status": "failed", "error": "Doctype not allowed"})
			continue

		existing = frappe.db.get_value("LIMS Sync Event", {"event_id": event_id}, ["name", "status"], as_dict=True)
		if existing and existing.status == "Applied":
			results.append({"event_id": event_id, "status": "duplicate"})
			continue

		sync_event_name = existing.name if existing else _create_sync_event(event_id, device_id, target_doctype, operation, payload)

		try:
			target_docname = _apply_event(target_doctype, operation, payload)
			frappe.db.set_value(
				"LIMS Sync Event",
				sync_event_name,
				{
					"target_docname": target_docname,
					"status": "Applied",
					"applied_on": frappe.utils.now_datetime(),
					"error_message": "",
				},
			)
			results.append({"event_id": event_id, "status": "applied", "docname": target_docname})
		except Exception:
			frappe.db.set_value(
				"LIMS Sync Event",
				sync_event_name,
				{"status": "Failed", "error_message": frappe.get_traceback()},
			)
			results.append({"event_id": event_id, "status": "failed", "error": "Apply failed"})

	return {
		"device_id": device_id,
		"server_timestamp": frappe.utils.now_datetime().isoformat(),
		"results": results,
	}


@frappe.whitelist()
def pull_sync_changes(since: str | None = None, limit: int = 200):
	"""Return latest LIMS document snapshots since a timestamp for pull sync."""
	settings = _settings_guard()
	configured_limit = int(settings.sync_batch_limit or 200)
	limit = max(1, min(int(limit), configured_limit))
	since_dt = _parse_since(since)

	changes = {}
	for doctype in ALLOWED_SYNC_DOCTYPES:
		rows = frappe.get_all(
			doctype,
			fields=["name", "modified"],
			filters={"modified": [">", since_dt]} if since_dt else None,
			order_by="modified asc",
			limit_page_length=limit,
		)
		if not rows:
			continue

		documents = []
		for row in rows:
			doc = frappe.get_doc(doctype, row.name)
			documents.append(doc.as_dict())
		changes[doctype] = documents

	return {
		"server_timestamp": frappe.utils.now_datetime().isoformat(),
		"changes": changes,
	}


def _apply_event(target_doctype: str, operation: str, payload: dict) -> str:
	if not isinstance(payload, dict):
		frappe.throw(_("payload must be an object"))

	if operation not in {"insert", "update"}:
		frappe.throw(_("operation must be insert or update"))

	docname = payload.get("name")
	if operation == "insert" and not docname:
		doc = frappe.get_doc({"doctype": target_doctype, **payload})
		doc.insert(ignore_permissions=False)
		return doc.name

	if not docname:
		frappe.throw(_("payload.name is required for update operations"))

	if not frappe.db.exists(target_doctype, docname):
		if operation == "insert":
			doc = frappe.get_doc({"doctype": target_doctype, **payload})
			doc.insert(ignore_permissions=False)
			return doc.name
		frappe.throw(_("Document {0} does not exist in {1}").format(docname, target_doctype))

	doc = frappe.get_doc(target_doctype, docname)
	doc.update(payload)
	doc.save(ignore_permissions=False)
	return doc.name


def _create_sync_event(event_id: str, device_id: str, doctype: str, operation: str, payload: dict) -> str:
	sync_event = frappe.get_doc(
		{
			"doctype": "LIMS Sync Event",
			"event_id": event_id,
			"device_id": device_id,
			"target_doctype": doctype,
			"operation": operation,
			"payload_json": frappe.as_json(payload),
		}
	)
	sync_event.insert(ignore_permissions=True)
	return sync_event.name


def _parse_since(since: str | None):
	if not since:
		return None
	try:
		return datetime.fromisoformat(since)
	except ValueError:
		frappe.throw(_("since must be an ISO timestamp"))


def _settings_guard():
	settings = frappe.get_single("LIMS Settings") if frappe.db.exists("DocType", "LIMS Settings") else None
	if not settings or not settings.enable_offline_sync:
		frappe.throw(_("Offline sync is disabled in LIMS Settings"))
	return settings
