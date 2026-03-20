import frappe
from frappe import _


class LabCriticalResultAlert(frappe.Document):
	"""Doctype for managing critical lab result alerts to referred doctors."""

	def before_insert(self):
		"""Auto-populate doctor contact information from LIMS Patient."""
		if self.lab_result_entry:
			result_entry = frappe.get_doc("Lab Result Entry", self.lab_result_entry)
			if result_entry.patient:
				patient = frappe.get_doc("LIMS Patient", result_entry.patient)
				self.patient_id = patient.name
				self.patient_name = patient.patient_name
				self.referred_doctor_name = patient.referred_doctor_name
				self.referred_doctor_email = patient.referred_doctor_email
				self.referred_doctor_mobile = patient.referred_doctor_mobile
				self.referred_doctor_whatsapp = patient.referred_doctor_whatsapp


@frappe.whitelist()
def send_critical_alert_to_doctor(alert_name):
	"""Send critical result notification to referred doctor via all configured channels."""
	alert = frappe.get_doc("Lab Critical Result Alert", alert_name)
	
	if not alert.referred_doctor_name or not alert.referred_doctor_email:
		frappe.throw(_("Referred doctor information is incomplete"))
	
	results = {
		"email_status": "Not Configured",
		"sms_status": "Not Configured",
		"whatsapp_status": "Not Configured",
	}
	
	# Email notification
	if alert.referred_doctor_email:
		try:
			_send_critical_result_email(alert)
			results["email_status"] = "Sent"
		except Exception:
			results["email_status"] = "Failed"
			frappe.log_error(frappe.get_traceback(), f"Critical Alert Email Failed: {alert_name}")
	
	# SMS notification
	if alert.referred_doctor_mobile:
		settings = frappe.get_single("LIMS Settings") if frappe.db.exists("DocType", "LIMS Settings") else None
		if settings and settings.enable_sms:
			try:
				_send_critical_result_sms(alert)
				results["sms_status"] = "Sent"
			except Exception:
				results["sms_status"] = "Failed"
				frappe.log_error(frappe.get_traceback(), f"Critical Alert SMS Failed: {alert_name}")
	
	# WhatsApp notification
	if alert.referred_doctor_whatsapp:
		settings = frappe.get_single("LIMS Settings") if frappe.db.exists("DocType", "LIMS Settings") else None
		if settings and settings.enable_whatsapp:
			try:
				_send_critical_result_whatsapp(alert)
				results["whatsapp_status"] = "Sent"
			except Exception:
				results["whatsapp_status"] = "Failed"
				frappe.log_error(frappe.get_traceback(), f"Critical Alert WhatsApp Failed: {alert_name}")
	
	# Update alert status
	frappe.db.set_value(
		"Lab Critical Result Alert",
		alert_name,
		{
			"notification_status": "Sent" if results["email_status"] == "Sent" or results["sms_status"] == "Sent" or results["whatsapp_status"] == "Sent" else "Failed",
			"email_status": results["email_status"],
			"sms_status": results["sms_status"],
			"whatsapp_status": results["whatsapp_status"],
			"alert_sent_on": frappe.utils.now_datetime(),
		},
	)
	
	return results


def _send_critical_result_email(alert):
	"""Send critical result notification email."""
	subject = _("URGENT: Critical Lab Result for Patient {0}").format(alert.patient_name)
	message = f"""
	<h3>CRITICAL LAB RESULT ALERT</h3>
	<p><strong>Alert Type:</strong> Automatic Critical Value Notification</p>
	<p><strong>Patient Name:</strong> {alert.patient_name}</p>
	<p><strong>Patient ID:</strong> {alert.patient_id}</p>
	<p><strong>Test Name:</strong> {alert.test_catalog}</p>
	<p><strong>Result Value:</strong> <span style="color: red; font-weight: bold;">{alert.result_value}</span></p>
	<p><strong>Critical Range:</strong> {alert.critical_value}</p>
	<p><strong>Alert Time:</strong> {frappe.utils.now()}</p>
	<hr>
	<p>Please review this critical result immediately and take appropriate action.</p>
	"""
	
	frappe.sendmail(
		recipients=[alert.referred_doctor_email],
		subject=subject,
		message=message,
	)


def _send_critical_result_sms(alert):
	"""Send critical result notification SMS."""
	from erpnext.lims.notifications import send_sms_via_provider
	
	message = f"CRITICAL LAB ALERT: {alert.test_catalog} for {alert.patient_name} is {alert.result_value} (Critical: {alert.critical_value}). Review immediately. Time: {frappe.utils.now()}"
	send_sms_via_provider(alert.referred_doctor_mobile, message)


def _send_critical_result_whatsapp(alert):
	"""Send critical result notification WhatsApp."""
	from erpnext.lims.notifications import send_whatsapp_via_webhook
	
	message = f"🚨 CRITICAL LAB ALERT\n\nPatient: {alert.patient_name}\nTest: {alert.test_catalog}\nResult: {alert.result_value}\nCritical Range: {alert.critical_value}\n\n⚠️ Please review immediately!"
	send_whatsapp_via_webhook(alert.referred_doctor_whatsapp, message)


@frappe.whitelist()
def check_and_create_critical_alerts_for_result(result_entry_name):
	"""Check if result contains critical values and create alert documents."""
	result_entry = frappe.get_doc("Lab Result Entry", result_entry_name)
	
	if not result_entry.patient:
		return []
	
	patient = frappe.get_doc("LIMS Patient", result_entry.patient)
	if not patient.referred_doctor_name:
		return []
	
	created_alerts = []
	
	# Check each test in the result entry for critical values
	for item in result_entry.get("test_items", []):
		if _is_critical_value(item):
			alert = frappe.get_doc(
				{
					"doctype": "Lab Critical Result Alert",
					"lab_result_entry": result_entry_name,
					"test_catalog": item.test_catalog_name,
					"critical_value": item.critical_value or "Not Defined",
					"result_value": item.result_value,
					"alert_type": "Automatic",
					"notification_status": "Pending",
				}
			)
			alert.insert(ignore_permissions=False)
			created_alerts.append(alert.name)
	
	return created_alerts


def _is_critical_value(test_item):
	"""Check if test item contains a critical value."""
	# This is a basic check - should be enhanced based on lab protocols
	if not test_item.critical_value or not test_item.result_value:
		return False
	
	# Simple range check for numeric values
	try:
		critical_range = str(test_item.critical_value).strip()
		result_val = float(test_item.result_value)
		
		# Handle ranges like "< 50" or "> 150" or "100-200"
		if "<" in critical_range:
			threshold = float(critical_range.replace("<", "").strip())
			return result_val < threshold
		elif ">" in critical_range:
			threshold = float(critical_range.replace(">", "").strip())
			return result_val > threshold
		elif "-" in critical_range:
			parts = critical_range.split("-")
			if len(parts) == 2:
				min_val, max_val = float(parts[0].strip()), float(parts[1].strip())
				return result_val < min_val or result_val > max_val
	except (ValueError, TypeError):
		pass
	
	return False
