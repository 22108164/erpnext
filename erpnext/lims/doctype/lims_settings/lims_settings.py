from frappe.model.document import Document


class LIMSSettings(Document):
	def validate(self):
		if self.sync_batch_limit and int(self.sync_batch_limit) < 1:
			self.sync_batch_limit = 200
