import frappe

tickets = frappe.get_all(
    "HD Ticket",
    fields=["name", "subject", "status", "response_by", "resolution_by",
            "first_responded_on", "resolution_date", "agreement_status",
            "creation", "sla"],
    order_by="creation desc",
    limit=5
)

for ticket in tickets:
    print(f"\nTicket: {ticket.name}")
    print(f"  Status: {ticket.status}")
    print(f"  Agreement Status: {ticket.agreement_status}")
    print(f"  Response By: {ticket.response_by}")
    print(f"  Resolution By: {ticket.resolution_by}")