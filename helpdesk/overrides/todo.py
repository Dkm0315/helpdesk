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

    # Check if this TODO is for ticket assignment by looking at the description
    # The default assignment creates TODOs with descriptions like "Automatic Assignment" or similar
    # We want to update it to be more specific for helpdesk tickets
    try:
        ticket_number = doc.reference_name
        new_description = f"Ticket {ticket_number} has been assigned to you"

        # Only update if the current description is generic/default
        # This prevents overwriting user-customized descriptions
        if doc.description and any(keyword in doc.description.lower() for keyword in ["automatic", "assignment", "assigned"]):
            # Update the description
            frappe.db.set_value("ToDo", doc.name, "description", new_description, update_modified=False)
        elif not doc.description:
            # If no description exists, set our custom one
            frappe.db.set_value("ToDo", doc.name, "description", new_description, update_modified=False)

    except Exception as e:
        frappe.log_error(f"Error updating TODO description for ticket assignment: {str(e)}")