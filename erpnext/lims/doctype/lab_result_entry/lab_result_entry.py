import frappe
from frappe import _
from frappe.core.doctype.sms_settings.sms_settings import send_sms
from frappe.model.document import Document

from erpnext.lims.notifications import send_whatsapp_via_webhook


class LabResultEntry(Document):
	def on_submit(self):
		self.update_registration_status()
		self.dispatch_report_notifications()

	def update_registration_status(self):
		if self.registration:
			frappe.db.set_value("Lab Test Registration", self.registration, "status", "Completed")

	def dispatch_report_notifications(self):
		patient = frappe.get_cached_doc("LIMS Patient", self.patient) if self.patient else None
		channels = []
		settings = frappe.get_single("LIMS Settings") if frappe.db.exists("DocType", "LIMS Settings") else None

		if self.send_to_patient and patient:
			channels.extend(self._notify_patient(patient, settings))

		if self.send_to_referred_doctor and patient:
			channels.extend(self._notify_doctor(patient, settings))

		self.db_set("communication_status", ", ".join(channels) if channels else "No channels triggered")

	def _notify_patient(self, patient, settings):
		channels = []
		subject = _("Lab Result {0}").format(self.name)
		message = self._build_message("Patient")

		if patient.email:
			frappe.sendmail(recipients=[patient.email], subject=subject, message=message)
			channels.append("Email:Patient")

		if settings and settings.enable_sms and patient.mobile_no:
			send_sms([patient.mobile_no], _("Your report {0} is ready. {1}").format(self.name, self.report_url or ""))
			channels.append("SMS:Patient")

		if patient.mobile_no and send_whatsapp_via_webhook(patient.mobile_no, message):
			channels.append("WhatsApp:Patient")

		return channels

	def _notify_doctor(self, patient, settings):
		channels = []

		if patient.referred_doctor_email:
			frappe.sendmail(
				recipients=[patient.referred_doctor_email],
				subject=_("Lab Result Shared: {0}").format(self.name),
				message=self._build_message("Referred Doctor"),
			)
			channels.append("Email:Doctor")

		if settings and settings.enable_sms and patient.referred_doctor_mobile:
			sms_message = (
				_("Critical result alert for report {0}. Please review immediately.").format(self.name)
				if self.critical_result
				else _("Lab result {0} is now available.").format(self.name)
			)
			send_sms([patient.referred_doctor_mobile], sms_message)
			channels.append("SMS:Doctor")

		doctor_whatsapp = patient.referred_doctor_whatsapp or patient.referred_doctor_mobile
		if doctor_whatsapp and send_whatsapp_via_webhook(doctor_whatsapp, self._build_message("Referred Doctor")):
			channels.append("WhatsApp:Doctor")

		return channels

	def _build_message(self, receiver_label):
		return _(
			"<p>{0},</p><p>Your lab result is now available.</p><p><b>Report:</b> {1}</p>"
			"<p><b>Critical:</b> {2}</p><p><b>Result Summary:</b><br>{3}</p>"
		).format(
			receiver_label,
			self.report_url or self.name,
			_("Yes") if self.critical_result else _("No"),
			frappe.safe_decode(self.result_values or ""),
		)
