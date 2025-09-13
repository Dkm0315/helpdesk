import frappe
from frappe import _

@frappe.whitelist()
def get_assignments():
    """Get all Dynamic User Assignments"""
    try:
        # Check if the doctype exists
        if not frappe.db.exists("DocType", "Dynamic User Assignment"):
            return []
        
        assignments = frappe.get_all(
            "Dynamic User Assignment",
            fields=[
                "name",
                "assignment_name",
                "assignment_code",
                "description",
                "default"
            ],
            order_by="assignment_name asc"
        )
        
        # Get user count for each assignment
        for assignment in assignments:
            # Direct count from the database for better performance
            user_count = frappe.db.count("Assigned Users", {"parent": assignment["name"]})
            assignment["user_count"] = user_count
            assignment["is_active"] = 1  # All assignments are considered active
        
        return assignments
    except Exception as e:
        frappe.log_error(f"Error fetching dynamic user assignments: {str(e)}")
        return []

@frappe.whitelist()
def apply_assignment(assignment_id):
    """Apply a Dynamic User Assignment and return the list of users"""
    try:
        if not frappe.db.exists("Dynamic User Assignment", assignment_id):
            frappe.throw(_("Dynamic User Assignment not found"))
        
        users = get_users_for_assignment(assignment_id)
        return users
    except Exception as e:
        frappe.log_error(f"Error applying dynamic user assignment: {str(e)}")
        frappe.throw(_("Error applying assignment: {0}").format(str(e)))

def get_users_for_assignment(assignment_id):
    """Get users based on Dynamic User Assignment conditions"""
    try:
        assignment = frappe.get_doc("Dynamic User Assignment", assignment_id)
        
        # Get assigned users from the child table
        users = []
        if hasattr(assignment, 'assigned_users'):
            for assigned_user in assignment.assigned_users:
                # Check both user and user_id fields for compatibility
                user_email = assigned_user.user_id or assigned_user.user
                if user_email:
                    try:
                        user = frappe.get_doc("User", user_email)
                        users.append({
                            "user": user.name,
                            "full_name": user.full_name or user.name,
                            "user_image": user.user_image,
                            "email": user.email
                        })
                    except Exception as e:
                        # If user doesn't exist, create a basic entry with the user_id
                        users.append({
                            "user": user_email,
                            "full_name": user_email,
                            "user_image": None,
                            "email": user_email
                        })
        
        return users
    except Exception as e:
        frappe.log_error(f"Error getting users for assignment {assignment_id}: {str(e)}")
        return []

def build_filters_from_conditions(conditions):
    """Build Frappe filters from Dynamic User Assignment conditions"""
    filters = {}
    
    for condition in conditions:
        field = condition.get("field")
        operator = condition.get("operator", "=")
        value = condition.get("value")
        
        if field and value:
            if operator == "in":
                filters[field] = ["in", value.split(",")]
            elif operator == "not in":
                filters[field] = ["not in", value.split(",")]
            elif operator == "like":
                filters[field] = ["like", f"%{value}%"]
            else:
                filters[field] = [operator, value]
    
    return filters

@frappe.whitelist()
def get_assignment_users(assignment_ids):
    """Get all users from multiple Dynamic User Assignments"""
    if isinstance(assignment_ids, str):
        assignment_ids = frappe.parse_json(assignment_ids)
    
    all_users = []
    user_emails = set()
    
    for assignment_id in assignment_ids:
        users = get_users_for_assignment(assignment_id)
        for user in users:
            if user["email"] not in user_emails:
                all_users.append(user)
                user_emails.add(user["email"])
    
    return all_users