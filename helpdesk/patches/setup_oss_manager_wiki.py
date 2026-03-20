import frappe


def execute():
	"""Rename wiki sidebar groups and KB categories to 'OSS Manager'."""
	# Rename Wiki Group Item parent_labels
	if frappe.db.exists("DocType", "Wiki Group Item"):
		frappe.db.sql(
			"""UPDATE `tabWiki Group Item` SET `parent_label` = 'OSS Manager'"""
		)

	# Rename the default KB article category from "General" to "OSS Manager"
	if frappe.db.exists("HD Article Category", "General"):
		frappe.rename_doc(
			"HD Article Category", "General", "OSS Manager", force=True
		)

	frappe.db.commit()
