import frappe


def execute():
	"""Rename wiki sidebar groups and KB categories to 'OSS Manager'."""
	# Rename all Wiki Group Item parent_labels to OSS Manager
	if frappe.db.exists("DocType", "Wiki Group Item"):
		frappe.db.sql(
			"""UPDATE `tabWiki Group Item`
			SET `parent_label` = 'OSS Manager'
			WHERE `parent_label` != 'OSS Manager'"""
		)

	# Rename the default KB article category
	if frappe.db.exists("HD Article Category", "General"):
		frappe.rename_doc(
			"HD Article Category", "General", "OSS Manager", force=True
		)

	frappe.db.commit()
