import frappe


LIMS_DESKTOP_ICON = "NxLIMS"
ALLOWED_MODULES = {"LIMS"}
ALLOWED_WORKSPACES = {"NxLIMS"}


def execute():
	# Disable all non-LIMS modules
	modules = frappe.get_all("Module Def", pluck="name")
	for module in modules:
		if module not in ALLOWED_MODULES:
			frappe.db.set_value("Module Def", module, "disabled", 1)

	# Show only NxLIMS desktop icon
	frappe.db.sql(
		"""
		update `tabDesktop Icon`
		set hidden = case when name = %s then 0 else 1 end
		""",
		(LIMS_DESKTOP_ICON,),
	)

	# Hide all non-NxLIMS workspaces
	workspaces = frappe.get_all("Workspace", pluck="name")
	for ws in workspaces:
		frappe.db.set_value("Workspace", ws, "is_hidden", 0 if ws in ALLOWED_WORKSPACES else 1)

	# Set NxLIMS as home page
	frappe.db.set_value("System Settings", None, "home_page", "/app/home")
