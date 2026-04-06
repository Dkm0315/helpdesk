import frappe


@frappe.whitelist(allow_guest=True)
def get_config():
    fields = [
        "brand_name",
        "brand_logo",
        "favicon",
        "prefer_knowledge_base",
        "setup_complete",
        "skip_email_workflow",
        "is_feedback_mandatory",
        "restrict_tickets_by_agent_group",
        "assign_within_team",
        "disable_saved_replies_global_scope",
        "enable_comment_reactions",
        "enable_our_services",
        "enable_buy_services",
        "enable_wiki",
    ]
    settings = frappe.get_single("HD Settings")
    res = frappe._dict({f: getattr(settings, f, None) for f in fields})
    if frappe.db.exists("DocType", "HD Support Plan"):
        res.enable_support_plan = bool(
            frappe.db.get_single_value("HD Support Plan", "enabled")
        )
    else:
        res.enable_support_plan = False

    res.favicon = (
        res.favicon
        or frappe.db.get_single_value("Website Settings", "favicon")
        or "/assets/helpdesk/desk/favicon.svg"
    )
    return res
