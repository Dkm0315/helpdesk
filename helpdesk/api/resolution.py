import frappe
from frappe import _
from typing import List, Dict, Any


@frappe.whitelist()
def get_resolution_history(ticket_id: str) -> List[Dict[str, Any]]:
    """
    Get resolution history for a ticket
    """
    ticket_doc = frappe.get_doc("HD Ticket", ticket_id)

    # Check permissions
    if not frappe.has_permission("HD Ticket", "read", ticket_doc):
        frappe.throw(_("You don't have permission to view this ticket"), frappe.PermissionError)

    # Get resolution history
    history = frappe.get_all(
        "HD Resolution History",
        filters={"ticket": ticket_id},
        fields=[
            "name",
            "version_number",
            "resolution_content",
            "submitted_by",
            "submitted_on",
            "satisfaction_status",
            "satisfaction_by",
            "satisfaction_on",
            "rejection_reason",
            "is_current_version"
        ],
        order_by="version_number desc"
    )

    # Add user full names for better display
    for item in history:
        if item.submitted_by:
            item.submitted_by_name = frappe.get_value("User", item.submitted_by, "full_name") or item.submitted_by
        if item.satisfaction_by:
            item.satisfaction_by_name = frappe.get_value("User", item.satisfaction_by, "full_name") or item.satisfaction_by

    return history


@frappe.whitelist()
def create_resolution_history(ticket_id: str, resolution_content: str) -> Dict[str, Any]:
    """
    Create a new resolution history entry when agent submits resolution
    """
    ticket_doc = frappe.get_doc("HD Ticket", ticket_id)

    # Check permissions - only agents should be able to create resolutions
    from helpdesk.utils import is_agent, is_admin
    if not (is_agent() or is_admin()):
        frappe.throw(_("Only agents can submit resolutions"), frappe.PermissionError)

    if not resolution_content.strip():
        frappe.throw(_("Resolution content cannot be empty"), frappe.ValidationError)

    # Create new resolution history entry
    resolution_doc = frappe.get_doc({
        "doctype": "HD Resolution History",
        "ticket": ticket_id,
        "resolution_content": resolution_content,
        "submitted_by": frappe.session.user,
        "satisfaction_status": "Pending",
        "is_current_version": 1
    })

    resolution_doc.insert(ignore_permissions=True)

    # Update ticket with current resolution info
    ticket_doc.resolution_details = resolution_content
    ticket_doc.resolution_submitted = 1
    ticket_doc.resolution_submitted_on = frappe.utils.now_datetime()
    ticket_doc.resolution_ever_submitted = 1
    ticket_doc.status = "Resolved"

    ticket_doc.save(ignore_permissions=True)

    return {
        "success": True,
        "message": "Resolution submitted successfully",
        "resolution_id": resolution_doc.name,
        "version_number": resolution_doc.version_number
    }


@frappe.whitelist()
def get_resolution_satisfaction_permissions(ticket_id: str) -> Dict[str, bool]:
    """
    Check what resolution satisfaction actions the current user can perform
    """
    ticket_doc = frappe.get_doc("HD Ticket", ticket_id)
    user = frappe.session.user

    from helpdesk.utils import is_admin

    # Check basic permissions
    can_reject = False
    can_mark_satisfied = False

    # System manager can always manage satisfaction
    if is_admin(user):
        can_reject = True
        can_mark_satisfied = True
    else:
        # User who raised the ticket can manage satisfaction
        if ticket_doc.raised_by == user:
            can_reject = True
            can_mark_satisfied = True

        # User for whom the ticket is raised (contact) can manage satisfaction
        if ticket_doc.contact == user:
            can_reject = True
            can_mark_satisfied = True

    # Additional checks based on current state
    if not ticket_doc.resolution_ever_submitted:
        can_reject = False
        can_mark_satisfied = False

    if ticket_doc.status not in ["Resolved", "Closed"]:
        can_reject = False
        can_mark_satisfied = False

    # Check resolution history for satisfaction status
    current_resolution_status = "Pending"
    if ticket_doc.resolution_ever_submitted:
        # Get current resolution satisfaction status from history
        resolution_history = frappe.db.get_value(
            "HD Resolution History",
            {
                "ticket": ticket_id,
                "is_current_version": 1
            },
            "satisfaction_status"
        )
        if resolution_history:
            current_resolution_status = resolution_history
            if resolution_history == "Satisfied":
                can_mark_satisfied = False
            elif resolution_history == "Not Satisfied":
                can_reject = False

    return {
        "can_reject": can_reject,
        "can_mark_satisfied": can_mark_satisfied,
        "current_status": current_resolution_status,
        "ticket_status": ticket_doc.status
    }


@frappe.whitelist()
def get_current_resolution_details(ticket_id: str) -> Dict[str, Any]:
    """
    Get details of the current resolution
    """
    ticket_doc = frappe.get_doc("HD Ticket", ticket_id)

    # Check permissions
    if not frappe.has_permission("HD Ticket", "read", ticket_doc):
        frappe.throw(_("You don't have permission to view this ticket"), frappe.PermissionError)

    current_resolution = None
    if ticket_doc.current_resolution_version:
        current_resolution = frappe.db.get_value(
            "HD Resolution History",
            {
                "ticket": ticket_id,
                "is_current_version": 1
            },
            [
                "name",
                "version_number",
                "resolution_content",
                "submitted_by",
                "submitted_on",
                "satisfaction_status",
                "satisfaction_by",
                "satisfaction_on",
                "rejection_reason"
            ],
            as_dict=True
        )

        if current_resolution and current_resolution.submitted_by:
            current_resolution.submitted_by_name = frappe.get_value(
                "User", current_resolution.submitted_by, "full_name"
            ) or current_resolution.submitted_by

        if current_resolution and current_resolution.satisfaction_by:
            current_resolution.satisfaction_by_name = frappe.get_value(
                "User", current_resolution.satisfaction_by, "full_name"
            ) or current_resolution.satisfaction_by

    # Get satisfaction status from current resolution history
    satisfaction_status = "Pending"
    if current_resolution:
        satisfaction_status = current_resolution.get("satisfaction_status", "Pending")

    return {
        "current_resolution": current_resolution,
        "ticket_resolution_details": ticket_doc.resolution_details,
        "ticket_satisfaction_status": satisfaction_status,
        "total_versions": frappe.db.count("HD Resolution History", {"ticket": ticket_id})
    }


@frappe.whitelist()
def compare_resolution_versions(ticket_id: str, version1: int, version2: int) -> Dict[str, Any]:
    """
    Compare two resolution versions
    """
    ticket_doc = frappe.get_doc("HD Ticket", ticket_id)

    # Check permissions
    if not frappe.has_permission("HD Ticket", "read", ticket_doc):
        frappe.throw(_("You don't have permission to view this ticket"), frappe.PermissionError)

    # Get both versions
    version1_data = frappe.db.get_value(
        "HD Resolution History",
        {"ticket": ticket_id, "version_number": version1},
        [
            "name", "version_number", "resolution_content", "submitted_by",
            "submitted_on", "satisfaction_status", "rejection_reason"
        ],
        as_dict=True
    )

    version2_data = frappe.db.get_value(
        "HD Resolution History",
        {"ticket": ticket_id, "version_number": version2},
        [
            "name", "version_number", "resolution_content", "submitted_by",
            "submitted_on", "satisfaction_status", "rejection_reason"
        ],
        as_dict=True
    )

    if not version1_data or not version2_data:
        frappe.throw(_("One or both versions not found"), frappe.ValidationError)

    # Add user names
    for version_data in [version1_data, version2_data]:
        if version_data.submitted_by:
            version_data.submitted_by_name = frappe.get_value(
                "User", version_data.submitted_by, "full_name"
            ) or version_data.submitted_by

    return {
        "version1": version1_data,
        "version2": version2_data
    }