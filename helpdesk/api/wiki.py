import frappe
from frappe import _


@frappe.whitelist()
def get_wiki_sidebar_data():
	"""Return wiki spaces with their pages grouped by parent_label, for sidebar rendering."""
	if not frappe.db.exists("DocType", "Wiki Space"):
		return []

	spaces = frappe.get_all(
		"Wiki Space",
		fields=["name", "route", "space_name"],
		order_by="creation asc",
	)

	result = []
	for space in spaces:
		items = frappe.get_all(
			"Wiki Group Item",
			filters={"parent": space.name, "hide_on_sidebar": 0},
			fields=["wiki_page", "parent_label"],
			order_by="idx asc",
		)

		groups = {}
		for item in items:
			page = frappe.db.get_value(
				"Wiki Page",
				item.wiki_page,
				["name", "title", "route", "published"],
				as_dict=True,
			)
			if not page or not page.published:
				continue

			group_name = item.parent_label
			if group_name not in groups:
				groups[group_name] = []
			groups[group_name].append(
				{
					"name": page.name,
					"title": page.title,
					"route": page.route,
				}
			)

		if groups:
			result.append(
				{
					"space_name": space.space_name or space.route,
					"route": space.route,
					"groups": groups,
				}
			)

	return result


@frappe.whitelist()
def get_wiki_page_content(wiki_page_name):
	"""Fetch rendered HTML content of a wiki page."""
	if not frappe.db.exists("DocType", "Wiki Page"):
		frappe.throw(_("Wiki app is not installed"))

	from wiki.wiki.doctype.wiki_page.wiki_page import get_page_content

	return get_page_content(wiki_page_name)


@frappe.whitelist()
def resolve_wiki_route(route):
	"""Given a wiki page route (e.g. 'my-space/my-page'), return the Wiki Page name if it exists."""
	if not frappe.db.exists("DocType", "Wiki Page"):
		return None

	# Strip leading slash
	route = route.lstrip("/")

	page_name = frappe.db.get_value("Wiki Page", {"route": route, "published": 1}, "name")
	return page_name
