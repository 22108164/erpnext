import frappe
from frappe.permissions import add_permission, update_permission_property

ROLES = ("LIMS Manager", "LIMS Reception", "LIMS Technician", "LIMS Billing")

DOC_ROLE_MATRIX = {
	"LIMS Patient": {
		"LIMS Reception": ("read", "write", "create"),
		"LIMS Manager": ("read", "write", "create", "delete"),
	},
	"Lab Test Catalog": {
		"LIMS Manager": ("read", "write", "create", "delete"),
		"LIMS Reception": ("read",),
	},
	"Lab Test Registration": {
		"LIMS Reception": ("read", "write", "create", "submit"),
		"LIMS Manager": ("read", "write", "create", "submit", "delete"),
	},
	"Lab Sample": {
		"LIMS Technician": ("read", "write", "create", "submit"),
		"LIMS Manager": ("read", "write", "create", "submit", "delete"),
	},
	"Lab Result Entry": {
		"LIMS Technician": ("read", "write", "create", "submit"),
		"LIMS Manager": ("read", "write", "create", "submit", "delete"),
	},
	"Lab Quality Control": {
		"LIMS Technician": ("read", "write", "create", "submit"),
		"LIMS Manager": ("read", "write", "create", "submit", "delete"),
	},
	"Lab Reagent": {
		"LIMS Technician": ("read", "write", "create"),
		"LIMS Manager": ("read", "write", "create", "delete"),
	},
	"Lab Expense": {
		"LIMS Billing": ("read", "write", "create", "submit"),
		"LIMS Manager": ("read", "write", "create", "submit", "delete"),
	},
	"LIMS Settings": {
		"LIMS Manager": ("read", "write"),
	},
	"LIMS Sync Event": {
		"LIMS Manager": ("read",),
	},
}


def execute():
	for role in ROLES:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({"doctype": "Role", "role_name": role}).insert(ignore_permissions=True)

	for doctype, role_map in DOC_ROLE_MATRIX.items():
		if not frappe.db.exists("DocType", doctype):
			continue
		for role, perms in role_map.items():
			add_permission(doctype, role, 0)
			for perm in perms:
				update_permission_property(doctype, role, 0, perm, 1)
