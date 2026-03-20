import frappe
from frappe.model.document import Document
from frappe.utils import flt


class LabTestRegistration(Document):
	def validate(self):
		total = 0
		for row in self.tests:
			if row.test:
				test_meta = frappe.db.get_value(
					"Lab Test Catalog", row.test, ["test_fee", "is_critical_test"], as_dict=True
				)
				if test_meta:
					row.rate = flt(row.rate or test_meta.test_fee)
					row.is_critical_test = row.is_critical_test or test_meta.is_critical_test
			row.amount = flt(row.rate)
			total += flt(row.amount)

		self.total_amount = total
