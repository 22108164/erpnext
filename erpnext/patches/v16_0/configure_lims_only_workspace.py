import frappe


LIMS_DESKTOP_ICON = "NxLIMS"
ALLOWED_WORKSPACES = {"NxLIMS"}


def execute():
	if not frappe.db.exists("Desktop Icon", LIMS_DESKTOP_ICON):
		return

	# Show only NxLIMS desktop icon for LIMS-focused deployments.
	frappe.db.sql(
		"""
		update `tabDesktop Icon`
		set hidden = case when name = %s then 0 else 1 end
		""",
		(LIMS_DESKTOP_ICON,),
	)

	workspaces = frappe.get_all("Workspace", pluck="name")
	for ws in workspaces:
		frappe.db.set_value("Workspace", ws, "is_hidden", 0 if ws in ALLOWED_WORKSPACES else 1)
