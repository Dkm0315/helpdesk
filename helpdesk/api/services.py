import frappe
from frappe import _


@frappe.whitelist()
def get_supported_technologies():
	"""Return all enabled supported technologies for the services landing page."""
	if not frappe.db.exists("DocType", "HD Supported Technology"):
		return []

	technologies = frappe.get_all(
		"HD Supported Technology",
		filters={"enabled": 1},
		fields=["name", "technology_name", "description", "icon_letter", "icon_color", "sort_order"],
		order_by="sort_order asc, technology_name asc",
	)

	return technologies


@frappe.whitelist()
def get_services_page_content():
	"""Return the Our Services page content from HD Settings."""
	settings = frappe.get_single("HD Settings")
	return {
		"sla_disclaimer": settings.our_services_sla_disclaimer or "",
		"non_production_response_time": settings.non_production_response_time or "4 Hours",
		"non_production_availability": settings.non_production_availability or "Business Hours",
		"production_response_time": settings.production_response_time or "1 Hour",
		"production_availability": settings.production_availability or "24/7",
	}


@frappe.whitelist()
def get_technology_detail(technology_name):
	"""Return a single technology with its service tiers for the detail page."""
	if not frappe.db.exists("DocType", "HD Supported Technology"):
		frappe.throw(_("Supported Technology DocType is not installed"))

	if not frappe.db.exists("HD Supported Technology", technology_name):
		frappe.throw(_("Technology {0} not found").format(technology_name))

	doc = frappe.get_doc("HD Supported Technology", technology_name)

	return {
		"technology_name": doc.technology_name,
		"description": doc.description,
		"detail_intro": doc.detail_intro,
		"icon_letter": doc.icon_letter,
		"icon_color": doc.icon_color,
		"service_tiers": [
			{
				"tier_name": tier.tier_name,
				"tier_description": tier.tier_description,
				"responsibilities": tier.responsibilities,
				"out_of_scope": tier.out_of_scope,
				"tools_methods": tier.tools_methods,
			}
			for tier in doc.service_tiers
		],
	}
