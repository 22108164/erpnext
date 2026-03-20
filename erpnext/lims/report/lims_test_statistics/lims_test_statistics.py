import frappe
from frappe import _


def execute(filters=None):
	columns = [
		{"label": _("Metric"), "fieldname": "metric", "fieldtype": "Data", "width": 260},
		{"label": _("Value"), "fieldname": "value", "fieldtype": "Float", "width": 180},
	]

	total_registrations = frappe.db.count("Lab Test Registration")
	completed_registrations = frappe.db.count("Lab Test Registration", {"status": "Completed"})
	total_samples = frappe.db.count("Lab Sample")
	critical_results = frappe.db.count("Lab Result Entry", {"critical_result": 1, "docstatus": 1})
	avg_test_fee = (
		frappe.db.sql(
			"""
			select avg(total_amount)
			from `tabLab Test Registration`
			where docstatus < 2
			"""
		)[0][0]
		or 0
	)

	data = [
		{"metric": _("Total Test Registrations"), "value": total_registrations},
		{"metric": _("Completed Registrations"), "value": completed_registrations},
		{"metric": _("Total Samples Managed"), "value": total_samples},
		{"metric": _("Critical Results Reported"), "value": critical_results},
		{"metric": _("Average Registration Value"), "value": avg_test_fee},
	]

	chart = {
		"data": {
			"labels": [d["metric"] for d in data],
			"datasets": [{"name": _("Lab Performance"), "values": [d["value"] for d in data]}],
		},
		"type": "bar",
	}

	return columns, data, None, chart
