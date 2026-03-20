import hashlib

from frappe.model.document import Document


class LIMSPatient(Document):
	def validate(self):
		identifier = (self.patient_identifier or "").strip().lower()
		self.patient_identifier_hash = hashlib.sha256(identifier.encode("utf-8")).hexdigest() if identifier else ""
