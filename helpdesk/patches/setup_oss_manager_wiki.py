import frappe


# Groups to remove entirely - their wiki pages and group items get deleted
GROUPS_TO_REMOVE = [
	"FAQ",
	"FAQ - Support Best Practices",
	"Frequently Asked Questions",
]


def execute():
	"""Clean up wiki sidebar groups and KB categories."""
	if frappe.db.exists("DocType", "Wiki Group Item"):
		# Delete wiki group items and their pages for FAQ-related groups
		for group_label in GROUPS_TO_REMOVE:
			items = frappe.get_all(
				"Wiki Group Item",
				filters={"parent_label": group_label},
				fields=["name", "wiki_page"],
			)
			for item in items:
				# Delete the group item
				frappe.db.delete("Wiki Group Item", {"name": item.name})
				# Delete the wiki page if it exists and isn't linked elsewhere
				if item.wiki_page and frappe.db.exists("Wiki Page", item.wiki_page):
					other_refs = frappe.db.count(
						"Wiki Group Item", {"wiki_page": item.wiki_page}
					)
					if other_refs == 0:
						frappe.delete_doc(
							"Wiki Page", item.wiki_page,
							ignore_permissions=True, force=True
						)

		# Rename all remaining group labels to "OSS Manager"
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
