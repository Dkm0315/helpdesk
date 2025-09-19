#!/usr/bin/env python3
import frappe
from frappe.utils import now_datetime, get_datetime

frappe.init(site="site1.local")
frappe.connect()

# Get recent tickets
tickets = frappe.get_all(
    "HD Ticket",
    fields=["name", "subject", "status", "response_by", "resolution_by",
            "first_responded_on", "resolution_date", "agreement_status",
            "creation", "sla"],
    order_by="creation desc",
    limit=5
)

print("\n=== Recent Tickets SLA Status ===\n")
for ticket in tickets:
    print(f"Ticket: {ticket.name} - {ticket.subject[:30]}...")
    print(f"  Status: {ticket.status}")
    print(f"  Agreement Status: {ticket.agreement_status}")
    print(f"  SLA: {ticket.sla}")
    print(f"  Response By: {ticket.response_by}")
    print(f"  First Responded On: {ticket.first_responded_on}")
    print(f"  Resolution By: {ticket.resolution_by}")
    print(f"  Resolution Date: {ticket.resolution_date}")

    # Check if dates are in the past
    if ticket.response_by:
        response_by_dt = get_datetime(ticket.response_by)
        now = now_datetime()
        if not ticket.first_responded_on and response_by_dt < now:
            print(f"  ⚠️ Response deadline passed without response!")
        elif ticket.first_responded_on:
            first_responded_dt = get_datetime(ticket.first_responded_on)
            if response_by_dt < first_responded_dt:
                print(f"  ⚠️ Response was after deadline!")

    if ticket.resolution_by:
        resolution_by_dt = get_datetime(ticket.resolution_by)
        now = now_datetime()
        if not ticket.resolution_date and resolution_by_dt < now:
            print(f"  ⚠️ Resolution deadline passed without resolution!")
        elif ticket.resolution_date:
            resolution_date_dt = get_datetime(ticket.resolution_date)
            if resolution_by_dt < resolution_date_dt:
                print(f"  ⚠️ Resolution was after deadline!")

    print()

# Check SLA configuration
sla_docs = frappe.get_all("HD Service Level Agreement",
                          fields=["name", "enabled", "default_sla", "condition"],
                          filters={"enabled": 1})

print("\n=== Active SLA Configurations ===\n")
for sla in sla_docs:
    print(f"SLA: {sla.name}")
    print(f"  Default: {sla.default_sla}")
    print(f"  Condition: {sla.condition or 'None'}")
    print()

frappe.db.commit()
frappe.destroy()