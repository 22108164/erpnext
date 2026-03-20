import frappe
from frappe.model.document import Document


class LabReagent(Document):
	def validate(self):
		if self.current_stock is not None and self.reorder_level is not None and self.current_stock < self.reorder_level:
			frappe.msgprint("Current stock is below reorder level.")
