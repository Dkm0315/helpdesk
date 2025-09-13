import frappe
from frappe import _


@frappe.whitelist()
def get_list(**kwargs):
    """Get list of HD Teams"""
    filters = kwargs.get("filters", {})
    fields = kwargs.get("fields", ["name", "team_name", "team_lead"])
    order_by = kwargs.get("order_by", "modified desc")
    limit_start = kwargs.get("limit_start", 0)
    limit_page_length = kwargs.get("limit_page_length", 20)

    teams = frappe.get_list(
        "HD Team",
        filters=filters,
        fields=fields,
        order_by=order_by,
        limit_start=limit_start,
        limit_page_length=limit_page_length
    )

    return teams