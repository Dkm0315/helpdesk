import frappe


DEFAULT_SUPPORT_PLAN_TITLE = "Support Plan"

DEFAULT_SUPPORT_PLAN_CONTENT = """
<table>
  <thead>
    <tr>
      <th>Feature / Service Area</th>
      <th>Basic Support</th>
      <th>Enterprise Support</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Support Coverage</td>
      <td>Standard operational support for day-to-day issues and platform guidance</td>
      <td>Premium support with faster response times, advanced troubleshooting, and continuous coverage</td>
    </tr>
    <tr>
      <td>P1 Incident Response</td>
      <td>8 business hours</td>
      <td>1 hour</td>
    </tr>
    <tr>
      <td>P2 Incident Response</td>
      <td>16 business hours</td>
      <td>4 hours</td>
    </tr>
    <tr>
      <td>P3 / General Query Response</td>
      <td>Next business day</td>
      <td>Within 8 business hours</td>
    </tr>
    <tr>
      <td>Technical Support Availability</td>
      <td>Business hours only</td>
      <td>24x7 coverage including weekends and holidays</td>
    </tr>
    <tr>
      <td>Working Model</td>
      <td>Remote support only</td>
      <td>Remote support only</td>
    </tr>
    <tr>
      <td>Support Portal Access</td>
      <td>Included</td>
      <td>Included</td>
    </tr>
    <tr>
      <td>Ticket-Based Support</td>
      <td>Included via support portal</td>
      <td>Included via support portal</td>
    </tr>
    <tr>
      <td>Email Support</td>
      <td>Included</td>
      <td>Included</td>
    </tr>
    <tr>
      <td>Monitoring Guidance</td>
      <td>Included</td>
      <td>Included</td>
    </tr>
    <tr>
      <td>Incident Troubleshooting</td>
      <td>Included</td>
      <td>Included with priority handling</td>
    </tr>
    <tr>
      <td>Root Cause Analysis (RCA)</td>
      <td>Not included</td>
      <td>Included for major incidents and repeated failures</td>
    </tr>
    <tr>
      <td>Escalation Management</td>
      <td>Standard escalation process</td>
      <td>Priority escalation with faster turnaround</td>
    </tr>
    <tr>
      <td>Configuration Review</td>
      <td>Basic, For expert guidance contact Professional services</td>
      <td>Basic, For expert guidance contact Professional services</td>
    </tr>
    <tr>
      <td>Upgrade Advisory</td>
      <td>Basic, For expert guidance contact Professional services</td>
      <td>Basic, For expert guidance contact Professional services</td>
    </tr>
    <tr>
      <td>Performance Tuning Recommendations</td>
      <td>Basic, For expert guidance contact Professional services</td>
      <td>Basic, For expert guidance contact Professional services</td>
    </tr>
    <tr>
      <td>Architecture Advisory</td>
      <td>Contact Solution Consultant Teams</td>
      <td>Contact Solution Consultant Teams</td>
    </tr>
    <tr>
      <td>Professional Services</td>
      <td>Available at additional cost</td>
      <td>Available at additional cost</td>
    </tr>
    <tr>
      <td>Dedicated L1 Resource</td>
      <td>Available at additional cost</td>
      <td>Available at additional cost</td>
    </tr>
    <tr>
      <td>Dedicated L2 / Technical Expert</td>
      <td>Not included</td>
      <td>Available at additional cost</td>
    </tr>
    <tr>
      <td>Solution Consultancy / Architect Support</td>
      <td>Available at additional cost</td>
      <td>Available at additional cost</td>
    </tr>
    <tr>
      <td>Training &amp; Knowledge Transfer</td>
      <td>Not included</td>
      <td>Available as optional service</td>
    </tr>
    <tr>
      <td>New OSS Manager Releases</td>
      <td>Included</td>
      <td>Included</td>
    </tr>
    <tr>
      <td>Product Documentation Access</td>
      <td>Included</td>
      <td>Included</td>
    </tr>
    <tr>
      <td>Best Practices &amp; Runbooks</td>
      <td>Included</td>
      <td>Included</td>
    </tr>
    <tr>
      <td>Support Channels</td>
      <td>Portal and Email</td>
      <td>Portal and Email</td>
    </tr>
    <tr>
      <td>Intended Customers</td>
      <td>Smaller teams with internal technical capability and standard business-hour needs</td>
      <td>Enterprises requiring faster response, 24/7 coverage, RCA, and critical issue handling</td>
    </tr>
  </tbody>
</table>
""".strip()


def ensure_support_plan():
    if not frappe.db.exists("DocType", "HD Support Plan"):
        return

    support_plan = frappe.get_single("HD Support Plan")
    is_uninitialized = not support_plan.title or not support_plan.content
    updates = {}

    if not support_plan.title:
        updates["title"] = DEFAULT_SUPPORT_PLAN_TITLE
    if not support_plan.content:
        updates["content"] = DEFAULT_SUPPORT_PLAN_CONTENT
    if is_uninitialized and not support_plan.enabled:
        updates["enabled"] = 1

    if updates:
        for fieldname, value in updates.items():
            frappe.db.set_single_value(
                "HD Support Plan", fieldname, value, update_modified=False
            )
        frappe.db.commit()
