import frappe


def get_lims_sidebar_items(sidebar_items):
	"""Filter sidebar to show only LIMS module items."""
	filtered = []
	for item in sidebar_items:
		# Keep NxLIMS workspace
		if item.get("label") == "NxLIMS":
			filtered.append(item)
		# Keep Help and Developer sections
		elif item.get("label") in ("Help", "Developer", "Administrator"):
			filtered.append(item)
	return filtered
