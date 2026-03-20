import frappe


def send_whatsapp_via_webhook(phone_number, message):
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
