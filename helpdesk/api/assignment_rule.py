import frappe
import json


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
        
        # Convert to dict and include custom fields
        rule_data = doc.as_dict()
        
        # Ensure users are properly formatted
        if doc.users:
            rule_data["users"] = [{"user": user.user} for user in doc.users]
        
        # Get associated Dynamic User Assignment if exists
        if hasattr(doc, "custom_user_assignment") and doc.custom_user_assignment:
            try:
                dynamic_assignment = frappe.get_doc("Dynamic User Assignment", doc.custom_user_assignment)
                rule_data["dynamicUserAssignments"] = [{
                    "name": dynamic_assignment.name,
                    "assignment_name": dynamic_assignment.assignment_name,
                    "users": [{"user": u.user} for u in dynamic_assignment.users]
                }]
            except:
                rule_data["dynamicUserAssignments"] = []
        else:
            rule_data["dynamicUserAssignments"] = []
        
        # Get associated holidays
        rule_data["holidays"] = []
        if hasattr(doc, "custom_holiday_lists"):
            # Parse holiday lists if stored as JSON string
            if isinstance(doc.custom_holiday_lists, str):
                try:
                    holiday_names = json.loads(doc.custom_holiday_lists)
                    for holiday_name in holiday_names:
                        rule_data["holidays"].append({
                            "name": holiday_name,
                            "holiday_list_name": holiday_name
                        })
                except:
                    pass
        
        return rule_data
    except Exception as e:
        frappe.log_error(f"Error fetching assignment rule details: {str(e)}")
        frappe.throw(f"Could not fetch assignment rule: {str(e)}")


@frappe.whitelist()
def save_assignment_rule(data):
    """Save assignment rule with all custom fields"""
    try:
        if isinstance(data, str):
            data = json.loads(data)
        
        if data.get("name"):
            # Update existing
            doc = frappe.get_doc("Assignment Rule", data["name"])
        else:
            # Create new
            doc = frappe.new_doc("Assignment Rule")
            doc.document_type = "HD Ticket"
        
        # Set basic fields
        doc.assignment_rule_name = data.get("assignmentRuleName") or data.get("name")
        doc.description = data.get("description", "")
        doc.disabled = data.get("disabled", 0)
        doc.priority = data.get("priority", 1)
        doc.rule = data.get("rule", "Round Robin")
        
        # Set conditions
        if data.get("assignCondition"):
            doc.condition = data["assignCondition"]
        if data.get("unassignCondition"):
            doc.unassign_condition = data["unassignCondition"]
        
        # Set users
        doc.users = []
        for user in data.get("users", []):
            doc.append("users", {"user": user.get("user")})
        
        # Set dynamic user assignment
        if data.get("dynamicUserAssignments"):
            for assignment in data["dynamicUserAssignments"]:
                if assignment.get("name"):
                    doc.custom_user_assignment = assignment["name"]
                    break
        
        # Set holidays as JSON string
        if data.get("holidays"):
            holiday_names = [h.get("name") for h in data["holidays"] if h.get("name")]
            doc.custom_holiday_lists = json.dumps(holiday_names) if holiday_names else None
        
        # Set assignment days
        if data.get("assignmentDays"):
            days_map = {
                "Monday": "custom_monday",
                "Tuesday": "custom_tuesday",
                "Wednesday": "custom_wednesday",
                "Thursday": "custom_thursday",
                "Friday": "custom_friday",
                "Saturday": "custom_saturday",
                "Sunday": "custom_sunday"
            }
            for day, field in days_map.items():
                if hasattr(doc, field):
                    setattr(doc, field, 1 if day in data["assignmentDays"] else 0)
        
        doc.save()
        frappe.db.commit()
        
        return {"name": doc.name, "message": "Assignment rule saved successfully"}
    except Exception as e:
        frappe.log_error(f"Error saving assignment rule: {str(e)}")
        frappe.throw(f"Could not save assignment rule: {str(e)}")


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
