import frappe


# Wiki group labels to remove (ticket-related and Our Services)
GROUPS_TO_REMOVE = [
	"FAQ",
	"FAQ - Support Best Practices",
	"Frequently Asked Questions",
	"Our Services",
]


def execute():
	"""Clean up wiki groups and rename KB category."""
	if frappe.db.exists("DocType", "Wiki Group Item"):
		# Remove ticket/FAQ/Our Services wiki group items and orphaned pages
		for group_label in GROUPS_TO_REMOVE:
			items = frappe.get_all(
				"Wiki Group Item",
				filters={"parent_label": group_label},
				fields=["name", "wiki_page"],
			)
			for item in items:
				frappe.db.delete("Wiki Group Item", {"name": item.name})
				# Delete the wiki page if no other group references it
				if item.wiki_page and frappe.db.exists("Wiki Page", item.wiki_page):
					other_refs = frappe.db.count(
						"Wiki Group Item", {"wiki_page": item.wiki_page}
					)
					if other_refs == 0:
						frappe.delete_doc(
							"Wiki Page", item.wiki_page,
							ignore_permissions=True, force=True
						)

		# Rename remaining group labels to "OSS Manager"
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
