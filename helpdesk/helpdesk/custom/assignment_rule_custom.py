import frappe
from frappe import _

def on_assignment_rule_apply(doc, method=None):
    """
    Hook to populate users from Dynamic User Assignment when Assignment Rule is applied
    """
    try:
        # Check if the rule has dynamic user assignments
        if hasattr(doc, 'custom_dynamic_user_assignments') and doc.custom_dynamic_user_assignments:
            users_to_add = []
            user_emails = set()
            
            # Get users from each Dynamic User Assignment
            for assignment_ref in doc.custom_dynamic_user_assignments:
                if assignment_ref.get('assignment_id'):
                    users = get_users_from_dynamic_assignment(assignment_ref.get('assignment_id'))
                    for user in users:
                        if user['email'] not in user_emails:
                            user_emails.add(user['email'])
                            users_to_add.append(user)
            
            # Add users to the assignment rule if not already present
            existing_users = set([u.user for u in (doc.users or [])])
            for user in users_to_add:
                if user['email'] not in existing_users:
                    doc.append('users', {
                        'user': user['email']
                    })
            
            frappe.msgprint(_("Added {0} users from Dynamic User Assignment").format(len(users_to_add)))
        
    except Exception as e:
        frappe.log_error(f"Error applying Dynamic User Assignment to Assignment Rule: {str(e)}")


def get_users_from_dynamic_assignment(assignment_id):
    """
    Get users from a Dynamic User Assignment document
    """
    try:
        assignment = frappe.get_doc("Dynamic User Assignment", assignment_id)
        users = []
        
        # Handle the Nextai module's Dynamic User Assignment structure
        if hasattr(assignment, 'assigned_users'):
            for assigned_user in assignment.assigned_users:
                if assigned_user.user_id:
                    try:
                        user = frappe.get_doc("User", assigned_user.user_id)
                        users.append({
                            "user": user.name,
                            "full_name": user.full_name,
                            "user_image": user.user_image,
                            "email": user.email
                        })
                    except:
                        pass
        
        # Also check for 'users' field (alternate structure)
        elif hasattr(assignment, 'users'):
            for user_row in assignment.users:
                if user_row.user:
                    try:
                        user = frappe.get_doc("User", user_row.user)
                        users.append({
                            "user": user.name,
                            "full_name": user.full_name,
                            "user_image": user.user_image,
                            "email": user.email
                        })
                    except:
                        pass
        
        return users
    except Exception as e:
        frappe.log_error(f"Error getting users from Dynamic User Assignment {assignment_id}: {str(e)}")
        return []


@frappe.whitelist()
def get_dynamic_user_assignment_users(assignment_id):
    """
    API method to get users from a Dynamic User Assignment
    """
    return get_users_from_dynamic_assignment(assignment_id)


@frappe.whitelist()
def apply_dynamic_assignments_to_rule(assignment_rule, dynamic_assignment_ids):
    """
    Apply multiple Dynamic User Assignments to an Assignment Rule
    """
    try:
        if isinstance(dynamic_assignment_ids, str):
            import json
            dynamic_assignment_ids = json.loads(dynamic_assignment_ids)
        
        rule = frappe.get_doc("Assignment Rule", assignment_rule)
        users_added = []
        existing_users = set([u.user for u in (rule.users or [])])
        
        for assignment_id in dynamic_assignment_ids:
            users = get_users_from_dynamic_assignment(assignment_id)
            for user in users:
                if user['email'] not in existing_users:
                    rule.append('users', {
                        'user': user['email']
                    })
                    users_added.append(user['email'])
                    existing_users.add(user['email'])
        
        if users_added:
            rule.save()
            frappe.db.commit()
            return {
                "success": True,
                "message": f"Added {len(users_added)} users to Assignment Rule",
                "users": users_added
            }
        else:
            return {
                "success": True,
                "message": "No new users to add",
                "users": []
            }
    
    except Exception as e:
        frappe.log_error(f"Error applying Dynamic Assignments: {str(e)}")
        return {
            "success": False,
            "message": str(e),
            "users": []
        }