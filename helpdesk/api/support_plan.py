import frappe


@frappe.whitelist()
def get_support_plan_content():
    support_plan = frappe.get_single("HD Support Plan")

    return {
        "title": support_plan.title or "Support Plan",
        "content": support_plan.content or "",
        "enabled": bool(support_plan.enabled),
    }
