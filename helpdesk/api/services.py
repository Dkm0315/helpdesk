import frappe
from frappe import _
from frappe.utils import md_to_html


@frappe.whitelist()
def get_our_services_content():
	"""Return the Our Services page content as rendered HTML."""
	settings = frappe.get_single("HD Settings")
	content_md = getattr(settings, "our_services_content", "") or ""
	content_html = md_to_html(content_md) if content_md else ""
	return {
		"content": content_html,
	}
