import json

import frappe
from frappe.model.document import Document


class LIMSSyncEvent(Document):
	def validate(self):
		if self.payload_json:
			try:
				json.loads(self.payload_json)
			except ValueError as exc:
				frappe.throw(f"Invalid payload_json: {exc}")
