import frappe
from frappe.model.document import Document


class LabSample(Document):
    def on_submit(self):
        if self.registration:
            frappe.db.set_value("Lab Test Registration", self.registration, "status", "Sample Collected")
