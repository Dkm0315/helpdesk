import frappe


def after_insert(doc, method=None):
    """
    Update TODO description for HD Ticket assignments
    """
    # Only process TODOs related to HD Tickets
    if not doc.reference_type or doc.reference_type != "HD Ticket":
        return

    if not doc.reference_name:
        return

    # Build a rich description from the ticket's subject + description
    try:
        ticket_data = frappe.db.get_value(
            "HD Ticket", doc.reference_name, ["subject", "description"], as_dict=True
        )
        if ticket_data:
            subj = ticket_data.get("subject") or ""
            desc = (ticket_data.get("description") or "")[:200]
            new_description = f"Subject: {subj} | Description: {desc}"
        else:
            new_description = f"Ticket {doc.reference_name} has been assigned to you"

        # Only update if the current description is generic/default
        if doc.description and any(keyword in doc.description.lower() for keyword in ["automatic", "assignment", "assigned"]):
            frappe.db.set_value("ToDo", doc.name, "description", new_description, update_modified=False)
        elif not doc.description:
            frappe.db.set_value("ToDo", doc.name, "description", new_description, update_modified=False)

        # Ensure type is set
        if not doc.type:
            frappe.db.set_value("ToDo", doc.name, "type", "Help Desk", update_modified=False)

    except Exception as e:
        frappe.log_error(f"Error updating TODO description for ticket assignment: {str(e)}")