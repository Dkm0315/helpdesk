import json

import frappe
from frappe import _

from helpdesk.api.dynamic_user_assignment import get_users_for_assignment


@frappe.whitelist()
def get_assignment_rules_list():
    assignment_rules = []
    for docname in frappe.get_all("Assignment Rule", filters={"document_type": "HD Ticket"}):
        doc = frappe.get_value(
            "Assignment Rule",
            docname,
            fieldname=[
                "name",
                "description",
                "disabled",
                "priority",
            ],
            as_dict=True,
        )
        users_exists = bool(
            frappe.db.exists("Assignment Rule User", {"parent": docname.name})
        )
        assignment_rules.append({**doc, "users_exists": users_exists})
    return assignment_rules


@frappe.whitelist()
def duplicate_assignment_rule(docname, new_name):
    doc = frappe.get_doc("Assignment Rule", docname)
    doc.name = new_name
    doc.assignment_rule_name = new_name
    doc.insert()
    return doc


@frappe.whitelist()
def get_assignment_rule_details(name):
    """Get detailed assignment rule with all fields"""
    try:
        doc = frappe.get_doc("Assignment Rule", name)

        rule_data = doc.as_dict()
        rule_data["users"] = [{"user": user.user} for user in (doc.users or [])]

        # Include JSON condition payloads for desk UI
        rule_data["assignConditionJson"] = json.loads(doc.assign_condition_json or "[]") if getattr(doc, "assign_condition_json", None) else []
        rule_data["unassignConditionJson"] = json.loads(doc.unassign_condition_json or "[]") if getattr(doc, "unassign_condition_json", None) else []

        # Assignment days simplified to list of day strings
        rule_data["assignmentDays"] = [row.day for row in (doc.assignment_days or [])]

        # Gather dynamic user assignments (new multi-select + legacy link fallback)
        dynamic_assignments = []
        if getattr(doc, "custom_dynamic_user_assignment", None):
            for row in doc.custom_dynamic_user_assignment:
                assignment_id = getattr(row, "assignment_id", None)
                if not assignment_id:
                    continue
                dynamic_assignments.append(_get_dynamic_assignment_details(assignment_id))
        elif getattr(doc, "custom_user_assignment", None):
            dynamic_assignments.append(_get_dynamic_assignment_details(doc.custom_user_assignment))
        rule_data["dynamicUserAssignments"] = [entry for entry in dynamic_assignments if entry]

        # Resolve linked holidays
        holidays = []
        if getattr(doc, "custom_holiday_lists", None):
            for row in doc.custom_holiday_lists:
                holiday_name = getattr(row, "holiday", None)
                if not holiday_name:
                    continue
                holiday = frappe.db.get_value(
                    "Holidays",
                    holiday_name,
                    ["name", "holiday_name", "date", "type", "repeat_next_year"],
                    as_dict=True,
                )
                if holiday:
                    holidays.append(holiday)
        rule_data["holidays"] = holidays

        return rule_data
    except Exception as e:
        frappe.log_error(f"Error fetching assignment rule details: {str(e)}")
        frappe.throw(_("Could not fetch assignment rule: {0}").format(e))


@frappe.whitelist()
def save_assignment_rule(data):
    """Save assignment rule with all custom fields"""
    try:
        if isinstance(data, str):
            data = frappe.parse_json(data)

        data = data or {}
        name = data.get("name")
        if name:
            doc = frappe.get_doc("Assignment Rule", name)
        else:
            doc = frappe.new_doc("Assignment Rule")
            doc.document_type = data.get("document_type", "HD Ticket")

        doc.document_type = data.get("document_type", doc.document_type or "HD Ticket")
        doc.assignment_rule_name = (
            data.get("assignmentRuleName")
            or data.get("name")
            or getattr(doc, "assignment_rule_name", None)
            or doc.name
        )
        doc.description = data.get("description", "")
        doc.disabled = int(data.get("disabled", 0))
        doc.priority = int(data.get("priority", doc.priority or 1))
        doc.rule = data.get("rule", doc.rule or "Round Robin")

        assign_condition_json = data.get("assignConditionJson")
        if assign_condition_json is not None:
            doc.assign_condition_json = json.dumps(assign_condition_json)
        elif data.get("assign_condition_json") is not None:
            doc.assign_condition_json = data["assign_condition_json"]

        assign_condition = data.get("assignCondition")
        if assign_condition is not None:
            doc.assign_condition = assign_condition

        unassign_condition_json = data.get("unassignConditionJson")
        if unassign_condition_json is not None:
            doc.unassign_condition_json = json.dumps(unassign_condition_json)
        elif data.get("unassign_condition_json") is not None:
            doc.unassign_condition_json = data["unassign_condition_json"]

        unassign_condition = data.get("unassignCondition")
        if unassign_condition is not None:
            doc.unassign_condition = unassign_condition

        # Assignment days
        doc.assignment_days = []
        for day in data.get("assignmentDays") or []:
            if day:
                doc.append("assignment_days", {"day": day})

        # Users
        doc.users = []
        seen_users = set()
        for user in data.get("users", []):
            user_id = user.get("user") or user.get("email")
            if user_id and user_id not in seen_users:
                doc.append("users", {"user": user_id})
                seen_users.add(user_id)

        # Dynamic user assignments (multi-select + legacy link)
        doc.custom_dynamic_user_assignment = []
        dynamic_assignment_ids = []
        for assignment in data.get("dynamicUserAssignments", []):
            assignment_id = assignment.get("name") or assignment.get("assignment_id")
            if assignment_id:
                doc.append("custom_dynamic_user_assignment", {"assignment_id": assignment_id})
                dynamic_assignment_ids.append(assignment_id)

        # Handle legacy custom_user_assignment field
        legacy_assignment = data.get("custom_user_assignment")
        if legacy_assignment:
            doc.custom_user_assignment = legacy_assignment
            # If legacy assignment is not already in dynamic_assignment_ids, add its users
            if legacy_assignment not in dynamic_assignment_ids:
                for user in get_users_for_assignment(legacy_assignment) or []:
                    user_id = user.get("email") or user.get("user")
                    if user_id and user_id not in seen_users:
                        doc.append("users", {"user": user_id})
                        seen_users.add(user_id)

        # Add users from all dynamic assignments
        for assignment_id in dynamic_assignment_ids:
            for user in get_users_for_assignment(assignment_id) or []:
                user_id = user.get("email") or user.get("user")
                if user_id and user_id not in seen_users:
                    doc.append("users", {"user": user_id})
                    seen_users.add(user_id)

        # Holiday lists
        doc.custom_holiday_lists = []
        for holiday in data.get("holidays", []):
            holiday_name = holiday.get("name") or holiday.get("holiday")
            if holiday_name:
                doc.append("custom_holiday_lists", {"holiday": holiday_name})

        if not name and doc.assignment_rule_name:
            doc.name = doc.assignment_rule_name

        doc.save(ignore_permissions=True)

        new_name = data.get("assignmentRuleName")
        if new_name and doc.name != new_name:
            frappe.rename_doc("Assignment Rule", doc.name, new_name, force=1, ignore_permissions=True)
            doc = frappe.get_doc("Assignment Rule", new_name)

        frappe.db.commit()

        return {"name": doc.name, "message": _("Assignment rule saved successfully")}
    except Exception as e:
        frappe.log_error(f"Error saving assignment rule: {str(e)}")
        frappe.throw(_("Could not save assignment rule: {0}").format(e))


def _get_dynamic_assignment_details(assignment_id):
    if not assignment_id:
        return None

    try:
        assignment = frappe.get_doc("Dynamic User Assignment", assignment_id)
        resolved_users = get_users_for_assignment(assignment.name) or []

        if hasattr(assignment, "assigned_users") and assignment.assigned_users:
            user_count = len(assignment.assigned_users)
        elif hasattr(assignment, "users") and assignment.users:
            user_count = len(assignment.users)
        else:
            user_count = len(resolved_users)

        return {
            "name": assignment.name,
            "assignment_name": getattr(assignment, "assignment_name", assignment.name),
            "assignment_code": getattr(assignment, "assignment_code", None),
            "description": getattr(assignment, "description", None),
            "default": getattr(assignment, "default", 0),
            "user_count": user_count,
            "users": resolved_users,
        }
    except Exception:
        return {"name": assignment_id}


@frappe.whitelist()
def get_work_schedules():
    """Get available work schedules"""
    schedules = []
    
    # Add default schedules
    schedules.append({
        "name": "standard_9_to_5",
        "label": "Standard (9 AM - 5 PM)",
        "description": "Monday to Friday, 9:00 AM - 5:00 PM",
        "working_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "start_time": "09:00:00",
        "end_time": "17:00:00"
    })
    
    schedules.append({
        "name": "extended_8_to_6",
        "label": "Extended (8 AM - 6 PM)",
        "description": "Monday to Friday, 8:00 AM - 6:00 PM",
        "working_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "start_time": "08:00:00",
        "end_time": "18:00:00"
    })
    
    schedules.append({
        "name": "24_7",
        "label": "24/7 Support",
        "description": "All days, 24 hours",
        "working_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "start_time": "00:00:00",
        "end_time": "23:59:59"
    })
    
    schedules.append({
        "name": "weekend_support",
        "label": "Weekend Support",
        "description": "Saturday and Sunday, 10:00 AM - 4:00 PM",
        "working_days": ["Saturday", "Sunday"],
        "start_time": "10:00:00",
        "end_time": "16:00:00"
    })
    
    return schedules
