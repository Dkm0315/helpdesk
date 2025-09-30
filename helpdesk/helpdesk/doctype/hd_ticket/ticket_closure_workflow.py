import frappe
from frappe import _
from helpdesk.utils import is_agent, is_admin


@frappe.whitelist()
def request_closure(ticket_id: str, resolution_notes: str = ""):
    """
    Request closure of a ticket. This can be called by:
    - Employees/agents responsible for the resolution of the ticket
    - User who raised the ticket or for whom it is raised
    - System manager
    """
    ticket_doc = frappe.get_doc("HD Ticket", ticket_id)
    user = frappe.session.user

    # Check authorization
    if not _can_request_closure(ticket_doc, user):
        frappe.throw(_("You are not authorized to request closure for this ticket"), frappe.PermissionError)

    # Check if ticket is already closed
    if ticket_doc.status == "Closed":
        frappe.throw(_("Ticket is already closed"), frappe.ValidationError)

    # Store resolution notes
    if resolution_notes:
        ticket_doc.resolution = resolution_notes
        ticket_doc.save(ignore_permissions=True)

    # Create a comment about the closure request
    comment = frappe.new_doc("HD Ticket Comment")
    comment.commented_by = user
    comment.content = f"Requested closure of ticket. Resolution notes: {resolution_notes or 'No resolution notes provided.'}"
    comment.reference_ticket = ticket_id
    comment.save(ignore_permissions=True)

    # Send notification to assigned agents (if user is not an agent)
    if not is_agent(user):
        _notify_agents_of_closure_request(ticket_doc, user, resolution_notes)

    # Set status to indicate closure is requested
    ticket_doc.status = "Pending Closure"
    ticket_doc.save(ignore_permissions=True)

    return {"success": True, "message": "Closure request submitted"}


@frappe.whitelist()
def mark_as_resolved(ticket_id: str, resolution_notes: str = ""):
    """
    Mark ticket as resolved/closed. This can be called by:
    - Assigned agents
    - System manager
    - User who raised the ticket (if they have permission)
    """
    ticket_doc = frappe.get_doc("HD Ticket", ticket_id)
    user = frappe.session.user

    # Check authorization
    if not _can_close_ticket(ticket_doc, user):
        frappe.throw(_("You are not authorized to close this ticket"), frappe.PermissionError)

    # Check if ticket is already closed
    if ticket_doc.status == "Closed":
        frappe.throw(_("Ticket is already closed"), frappe.ValidationError)

    # Validate resolution notes if required
    settings = frappe.get_single("HD Settings")
    if getattr(settings, "require_resolution_notes", False) and not resolution_notes:
        frappe.throw(_("Resolution notes are required to close this ticket"), frappe.ValidationError)

    # Store resolution notes
    if resolution_notes:
        ticket_doc.resolution = resolution_notes

    # Set status to closed
    ticket_doc.status = "Closed"
    ticket_doc.resolution_date = frappe.utils.now_datetime()
    ticket_doc.save(ignore_permissions=True)

    # Create a comment about the closure
    comment = frappe.new_doc("HD Ticket Comment")
    comment.commented_by = user
    comment.content = f"Ticket closed. Resolution: {resolution_notes or 'No resolution notes provided.'}"
    comment.reference_ticket = ticket_id
    comment.save(ignore_permissions=True)

    # Send notification to ticket raiser if closed by agent
    if is_agent(user) and user != ticket_doc.raised_by:
        _notify_customer_of_closure(ticket_doc, resolution_notes)

    return {"success": True, "message": "Ticket closed successfully"}


def _can_request_closure(ticket_doc, user):
    """
    Check if user can request closure for this ticket
    """
    # System manager can always request closure
    if is_admin(user):
        return True

    # User who raised the ticket can request closure
    if ticket_doc.raised_by == user:
        return True

    # User for whom the ticket is raised (contact) can request closure
    if ticket_doc.contact == user:
        return True

    # Assigned agents can request closure
    if is_agent(user):
        assigned_agents = ticket_doc.get_assigned_agents()
        if assigned_agents:
            agent_names = [agent.get("name") for agent in assigned_agents]
            if user in agent_names:
                return True

        # Agents from the same team can request closure
        if ticket_doc.agent_group:
            team_members = frappe.get_all(
                "HD Team Member",
                filters={"parent": ticket_doc.agent_group},
                pluck="user"
            )
            if user in team_members:
                return True

    return False


def _can_close_ticket(ticket_doc, user):
    """
    Check if user can directly close this ticket
    """
    # System manager can always close
    if is_admin(user):
        return True

    # Assigned agents can close
    if is_agent(user):
        assigned_agents = ticket_doc.get_assigned_agents()
        if assigned_agents:
            agent_names = [agent.get("name") for agent in assigned_agents]
            if user in agent_names:
                return True

        # Agents from the same team can close
        if ticket_doc.agent_group:
            team_members = frappe.get_all(
                "HD Team Member",
                filters={"parent": ticket_doc.agent_group},
                pluck="user"
            )
            if user in team_members:
                return True

    # User who raised the ticket can close (if setting allows)
    settings = frappe.get_single("HD Settings")
    if getattr(settings, "allow_customer_to_close", True) and ticket_doc.raised_by == user:
        return True

    return False


def _notify_agents_of_closure_request(ticket_doc, requester, resolution_notes):
    """
    Notify assigned agents about closure request
    """
    assigned_agents = ticket_doc.get_assigned_agents()
    if not assigned_agents:
        return

    recipients = [agent.get("name") for agent in assigned_agents]

    subject = f"Closure requested for Ticket #{ticket_doc.name}"
    message = f"""
    <p>A closure request has been submitted for Ticket #{ticket_doc.name} by {requester}.</p>
    <p><strong>Subject:</strong> {ticket_doc.subject}</p>
    <p><strong>Resolution Notes:</strong> {resolution_notes or 'No resolution notes provided.'}</p>
    <p><a href="{frappe.utils.get_url()}/helpdesk/tickets/{ticket_doc.name}">View Ticket</a></p>
    """

    frappe.sendmail(
        recipients=recipients,
        subject=subject,
        message=message,
        reference_doctype="HD Ticket",
        reference_name=ticket_doc.name,
        now=True
    )


def _notify_customer_of_closure(ticket_doc, resolution_notes):
    """
    Notify customer about ticket closure
    """
    subject = f"Ticket #{ticket_doc.name} has been resolved"
    message = f"""
    <p>Hello,</p>
    <p>Your support ticket #{ticket_doc.name} has been resolved.</p>
    <p><strong>Subject:</strong> {ticket_doc.subject}</p>
    <p><strong>Resolution:</strong> {resolution_notes or 'No resolution details provided.'}</p>
    <p>If you have any further questions, please feel free to reach out to us.</p>
    <p>Best regards,<br>Support Team</p>
    """

    frappe.sendmail(
        recipients=[ticket_doc.raised_by],
        subject=subject,
        message=message,
        reference_doctype="HD Ticket",
        reference_name=ticket_doc.name,
        now=True
    )