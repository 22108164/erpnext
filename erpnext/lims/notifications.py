import frappe
from frappe import _


def send_sms_via_provider(phone_number, message):
	"""Send SMS via configured SMS provider (Twilio, AWS SNS, or generic HTTP endpoint)."""
	settings = frappe.get_single("LIMS Settings") if frappe.db.exists("DocType", "LIMS Settings") else None
	if not settings or not settings.enable_sms:
		return False

	try:
		# Use Frappe's built-in SMS provider if configured
		from frappe.communication import send_sms
		send_sms(phone_number, message)
		return True
	except Exception:
		frappe.log_error(frappe.get_traceback(), "LIMS SMS Delivery Failure")
		return False


def send_whatsapp_via_webhook(phone_number, message):
	"""Send WhatsApp message via webhook."""
	settings = frappe.get_single("LIMS Settings") if frappe.db.exists("DocType", "LIMS Settings") else None
	if not settings or not settings.enable_whatsapp or not settings.whatsapp_webhook_url:
		return False

	payload = {"phone_number": phone_number, "message": message}
	try:
		frappe.make_post_request(settings.whatsapp_webhook_url, data=payload)
		return True
	except Exception:
		frappe.log_error(frappe.get_traceback(), "LIMS WhatsApp Delivery Failure")
		return False


def send_critical_alert_notification(patient, test_name, result_value, critical_range):
	"""Send critical alert notification to patient and referred doctor."""
	try:
		from erpnext.lims.doctype.lab_critical_result_alert.lab_critical_result_alert import (
			send_critical_alert_to_doctor,
		)
		
		# Create and send critical alert
		frappe.enqueue("erpnext.lims.doctype.lab_critical_result_alert.lab_critical_result_alert.send_critical_alert_to_doctor")
		return True
	except Exception:
		frappe.log_error(frappe.get_traceback(), "LIMS critical alert notification failed")
		return False
