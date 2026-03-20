import frappe
from frappe import _


PERIODS = [
	(_("Last 7 Days"), "7 day"),
	(_("Fortnightly"), "14 day"),
	(_("Monthly"), "30 day"),
]


def execute(filters=None):
	columns = [
		{"label": _("Period"), "fieldname": "period", "fieldtype": "Data", "width": 140},
		{"label": _("Revenue"), "fieldname": "revenue", "fieldtype": "Currency", "width": 150},
		{"label": _("General Expense"), "fieldname": "general_expense", "fieldtype": "Currency", "width": 150},
		{
			"label": _("Lab Performance Expense"),
			"fieldname": "lab_performance_expense",
			"fieldtype": "Currency",
			"width": 170,
		},
		{
			"label": _("Machinery & Tool Purchase"),
			"fieldname": "machinery_tool_expense",
			"fieldtype": "Currency",
			"width": 190,
		},
		{"label": _("Total Expense"), "fieldname": "total_expense", "fieldtype": "Currency", "width": 150},
		{"label": _("Profit"), "fieldname": "profit", "fieldtype": "Currency", "width": 150},
	]

	data = [build_period_row(label, interval) for label, interval in PERIODS]

	chart = {
		"data": {
			"labels": [d["period"] for d in data],
			"datasets": [
				{"name": _("Revenue"), "values": [d["revenue"] for d in data]},
				{"name": _("Expense"), "values": [d["total_expense"] for d in data]},
				{"name": _("Profit"), "values": [d["profit"] for d in data]},
			],
		},
		"type": "line",
	}

	return columns, data, None, chart


def build_period_row(label, interval):
	revenue = (
		frappe.db.sql(
			f"""
			select ifnull(sum(total_amount), 0)
			from `tabLab Test Registration`
			where docstatus < 2 and registration_date >= date_sub(curdate(), interval {interval})
			"""
		)[0][0]
		or 0
	)

	general_expense = get_expense_total(interval, "General Expense")
	lab_performance_expense = get_expense_total(interval, "Lab Performance Expense")
	machinery_tool_expense = get_grouped_expense_total(interval, ["Machinery Purchase", "Tool Purchase"])
	all_expense = general_expense + lab_performance_expense + machinery_tool_expense

	return {
		"period": label,
		"revenue": revenue,
		"general_expense": general_expense,
		"lab_performance_expense": lab_performance_expense,
		"machinery_tool_expense": machinery_tool_expense,
		"total_expense": all_expense,
		"profit": revenue - all_expense,
	}


def get_expense_total(interval, expense_type):
	return (
		frappe.db.sql(
			f"""
			select ifnull(sum(amount), 0)
			from `tabLab Expense`
			where expense_type = %s and expense_date >= date_sub(curdate(), interval {interval})
			""",
			expense_type,
		)[0][0]
		or 0
	)


def get_grouped_expense_total(interval, expense_types):
	if not expense_types:
		return 0

	placeholders = ", ".join(["%s"] * len(expense_types))
	return (
		frappe.db.sql(
			f"""
			select ifnull(sum(amount), 0)
			from `tabLab Expense`
			where expense_type in ({placeholders})
			  and expense_date >= date_sub(curdate(), interval {interval})
			""",
			expense_types,
		)[0][0]
		or 0
	)
