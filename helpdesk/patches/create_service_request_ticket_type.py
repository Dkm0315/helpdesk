import frappe


def execute():
	if not frappe.db.exists("HD Ticket Type", "Service Request"):
		frappe.get_doc(
			{
				"doctype": "HD Ticket Type",
				"name": "Service Request",
				"description": "Request for professional services, consultancy, or support hours",
				"is_system": 1,
			}
		).insert(ignore_permissions=True)
