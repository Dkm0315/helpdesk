import frappe
from frappe import _
from frappe.automation.doctype.assignment_rule.assignment_rule import AssignmentRule

def _safe_debug_log(msg):
    """
    Safely log debug messages without causing BrokenPipeError.
    Logs in developer mode or dev sites to help with debugging.
    """
    try:
        # Log in developer mode or if site is a dev site
        is_dev = frappe.conf.developer_mode or frappe.conf.get("dev_site", False)
        if is_dev:
            frappe.log_error(msg, "Assignment Rule Debug")
    except (BrokenPipeError, OSError, IOError):
        # Silently ignore broken pipe and IO errors
        pass

def on_assignment_rule_apply(doc, method=None):
    """
    Hook to populate users from Dynamic User Assignment when Assignment Rule is applied
    """
    try:
        # Check if the rule has dynamic user assignments
        if hasattr(doc, 'custom_dynamic_user_assignment') and doc.custom_dynamic_user_assignment:
            users_to_add = []
            user_emails = set()

            # Get users from each Dynamic User Assignment (filtered by leave/holidays)
            for assignment_ref in doc.custom_dynamic_user_assignment:
                assignment_id = getattr(assignment_ref, 'assignment_id', None) or assignment_ref.get('assignment_id')
                if assignment_id:
                    # Filter users based on leave/holidays
                    from helpdesk.api.dynamic_user_assignment import get_users_for_assignment
                    users = get_users_for_assignment(assignment_id, assignment_rule_name=doc.name)
                    for user in users:
                        email = user.get('email') or user.get('user')
                        if email and email not in user_emails:
                            user_emails.add(email)
                            users_to_add.append({**user, 'email': email})
            
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


def get_users_from_dynamic_assignment(assignment_id, assignment_rule_name=None, check_date=None):
    """
    Get users from a Dynamic User Assignment document, excluding users on leave/holidays
    """
    try:
        # Use the filtered version from dynamic_user_assignment module
        from helpdesk.api.dynamic_user_assignment import get_users_for_assignment
        return get_users_for_assignment(assignment_id, assignment_rule_name, check_date)
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


# Override Assignment Rule methods to filter users based on leave/holidays
def get_user_round_robin_filtered(self):
    """
    Get next user based on round robin, excluding users on leave/holidays
    Fetches users from both self.users and Dynamic User Assignment, then filters them
    """
    from helpdesk.api.holidays import should_exclude_user_from_assignment
    from frappe.utils import today
    
    check_date = today()
    all_users = []
    user_to_obj_map = {}  # Map user email to user object for round robin tracking
    
    _safe_debug_log(f"[ASSIGNMENT DEBUG] Round Robin - Rule: {self.name}, Date: {check_date}")
    
    # Get users from self.users (directly added users)
    if self.users:
        _safe_debug_log(f"[ASSIGNMENT DEBUG] Found {len(self.users)} direct users in rule")
        for user_obj in self.users:
            if user_obj.user:
                all_users.append(user_obj.user)
                user_to_obj_map[user_obj.user] = user_obj
                _safe_debug_log(f"[ASSIGNMENT DEBUG] Added direct user: {user_obj.user}")
    
    # Fetch users from Dynamic User Assignment if exists
    if hasattr(self, 'custom_dynamic_user_assignment') and self.custom_dynamic_user_assignment:
        _safe_debug_log(f"[ASSIGNMENT DEBUG] Found {len(self.custom_dynamic_user_assignment)} dynamic user assignments")
        for row in self.custom_dynamic_user_assignment:
            assignment_id = getattr(row, 'assignment_id', None)
            if assignment_id:
                _safe_debug_log(f"[ASSIGNMENT DEBUG] Fetching users from Dynamic Assignment: {assignment_id}")
                # Get users from Dynamic User Assignment (already filtered by get_users_for_assignment)
                users = get_users_from_dynamic_assignment(assignment_id, self.name, check_date)
                _safe_debug_log(f"[ASSIGNMENT DEBUG] Got {len(users)} users from Dynamic Assignment {assignment_id}")
                for user_dict in users:
                    user_email = user_dict.get('email') or user_dict.get('user')
                    if user_email and user_email not in all_users:
                        all_users.append(user_email)
                        # Create a mock user object for round robin tracking
                        user_to_obj_map[user_email] = frappe._dict({'user': user_email})
                        _safe_debug_log(f"[ASSIGNMENT DEBUG] Added user from Dynamic Assignment: {user_email}")
    
    # Also check custom_user_assignment (single assignment)
    if not all_users and hasattr(self, 'custom_user_assignment') and self.custom_user_assignment:
        _safe_debug_log(f"[ASSIGNMENT DEBUG] No users found, checking custom_user_assignment: {self.custom_user_assignment}")
        users = get_users_from_dynamic_assignment(self.custom_user_assignment, self.name, check_date)
        _safe_debug_log(f"[ASSIGNMENT DEBUG] Got {len(users)} users from custom_user_assignment")
        for user_dict in users:
            user_email = user_dict.get('email') or user_dict.get('user')
            if user_email and user_email not in all_users:
                all_users.append(user_email)
                user_to_obj_map[user_email] = frappe._dict({'user': user_email})
                _safe_debug_log(f"[ASSIGNMENT DEBUG] Added user from custom_user_assignment: {user_email}")
    
    _safe_debug_log(f"[ASSIGNMENT DEBUG] Total users before filtering: {len(all_users)}")
    if not all_users:
        _safe_debug_log(f"[ASSIGNMENT DEBUG] No users found for assignment rule {self.name}")
        return None
    
    # Filter users based on leave/holidays - exclude users on leave or holidays
    available_users = []
    excluded_users = []
    for user in all_users:
        should_exclude = should_exclude_user_from_assignment(user, assignment_rule_name=self.name, check_date=check_date)
        if not should_exclude:
            available_users.append(user)
        else:
            excluded_users.append(user)
            _safe_debug_log(f"[ASSIGNMENT DEBUG] Excluded user {user} (on leave/holiday)")
    
    _safe_debug_log(f"[ASSIGNMENT DEBUG] Available users after filtering: {len(available_users)}")
    _safe_debug_log(f"[ASSIGNMENT DEBUG] Excluded users: {excluded_users}")
    
    # If no users available after filtering, log warning but don't assign
    if not available_users:
        error_msg = f"No available users after filtering for assignment rule {self.name}. All {len(all_users)} users are on leave/holiday. Excluded: {excluded_users}"
        _safe_debug_log(f"[ASSIGNMENT DEBUG] ERROR: {error_msg}")
        frappe.log_error(error_msg, "Assignment Rule Filtering")
        # Return None to prevent assignment
        return None
    
    # Get filtered user objects (preserve order for round robin)
    filtered_user_objects = []
    for user in available_users:
        if user in user_to_obj_map:
            filtered_user_objects.append(user_to_obj_map[user])
    
    if not filtered_user_objects:
        _safe_debug_log(f"[ASSIGNMENT DEBUG] No filtered user objects found")
        return None
    
    # first time, or last in list, pick the first
    if not self.last_user or self.last_user == filtered_user_objects[-1].user:
        selected_user = filtered_user_objects[0].user
        _safe_debug_log(f"[ASSIGNMENT DEBUG] Selected user (first/last): {selected_user}")
        return selected_user
    
    # find out the next user in the filtered list
    for i, d in enumerate(filtered_user_objects):
        if self.last_user == d.user:
            if i + 1 < len(filtered_user_objects):
                selected_user = filtered_user_objects[i + 1].user
                _safe_debug_log(f"[ASSIGNMENT DEBUG] Selected user (next): {selected_user}")
                return selected_user
            else:
                selected_user = filtered_user_objects[0].user
                _safe_debug_log(f"[ASSIGNMENT DEBUG] Selected user (wrap around): {selected_user}")
                return selected_user
    
    # bad last user, assign to the first one
    selected_user = filtered_user_objects[0].user
    _safe_debug_log(f"[ASSIGNMENT DEBUG] Selected user (fallback): {selected_user}")
    return selected_user


def get_user_load_balancing_filtered(self):
    """
    Assign to the user with least number of open assignments, excluding users on leave/holidays
    Fetches users from both self.users and Dynamic User Assignment, then filters them
    """
    from helpdesk.api.holidays import should_exclude_user_from_assignment
    from frappe.utils import today
    
    check_date = today()
    all_users = []
    
    _safe_debug_log(f"[ASSIGNMENT DEBUG] Load Balancing - Rule: {self.name}, Date: {check_date}")
    
    # Get users from self.users (directly added users)
    if self.users:
        _safe_debug_log(f"[ASSIGNMENT DEBUG] Found {len(self.users)} direct users in rule")
        for user_obj in self.users:
            if user_obj.user:
                all_users.append(user_obj.user)
                _safe_debug_log(f"[ASSIGNMENT DEBUG] Added direct user: {user_obj.user}")
    
    # Fetch users from Dynamic User Assignment if exists
    if hasattr(self, 'custom_dynamic_user_assignment') and self.custom_dynamic_user_assignment:
        _safe_debug_log(f"[ASSIGNMENT DEBUG] Found {len(self.custom_dynamic_user_assignment)} dynamic user assignments")
        for row in self.custom_dynamic_user_assignment:
            assignment_id = getattr(row, 'assignment_id', None)
            if assignment_id:
                _safe_debug_log(f"[ASSIGNMENT DEBUG] Fetching users from Dynamic Assignment: {assignment_id}")
                # Get users from Dynamic User Assignment (already filtered by get_users_for_assignment)
                users = get_users_from_dynamic_assignment(assignment_id, self.name, check_date)
                _safe_debug_log(f"[ASSIGNMENT DEBUG] Got {len(users)} users from Dynamic Assignment {assignment_id}")
                for user_dict in users:
                    user_email = user_dict.get('email') or user_dict.get('user')
                    if user_email and user_email not in all_users:
                        all_users.append(user_email)
                        _safe_debug_log(f"[ASSIGNMENT DEBUG] Added user from Dynamic Assignment: {user_email}")
    
    # Also check custom_user_assignment (single assignment)
    if not all_users and hasattr(self, 'custom_user_assignment') and self.custom_user_assignment:
        _safe_debug_log(f"[ASSIGNMENT DEBUG] No users found, checking custom_user_assignment: {self.custom_user_assignment}")
        users = get_users_from_dynamic_assignment(self.custom_user_assignment, self.name, check_date)
        _safe_debug_log(f"[ASSIGNMENT DEBUG] Got {len(users)} users from custom_user_assignment")
        for user_dict in users:
            user_email = user_dict.get('email') or user_dict.get('user')
            if user_email and user_email not in all_users:
                all_users.append(user_email)
                _safe_debug_log(f"[ASSIGNMENT DEBUG] Added user from custom_user_assignment: {user_email}")
    
    _safe_debug_log(f"[ASSIGNMENT DEBUG] Total users before filtering: {len(all_users)}")
    if not all_users:
        _safe_debug_log(f"[ASSIGNMENT DEBUG] No users found for assignment rule {self.name}")
        return None
    
    # Filter users based on leave/holidays - exclude users on leave or holidays
    available_users = []
    excluded_users = []
    for user in all_users:
        should_exclude = should_exclude_user_from_assignment(user, assignment_rule_name=self.name, check_date=check_date)
        if not should_exclude:
            available_users.append(user)
        else:
            excluded_users.append(user)
            _safe_debug_log(f"[ASSIGNMENT DEBUG] Excluded user {user} (on leave/holiday)")
    
    _safe_debug_log(f"[ASSIGNMENT DEBUG] Available users after filtering: {len(available_users)}")
    _safe_debug_log(f"[ASSIGNMENT DEBUG] Excluded users: {excluded_users}")
    
    # If no users available after filtering, log warning but don't assign
    if not available_users:
        error_msg = f"No available users after filtering for assignment rule {self.name}. All {len(all_users)} users are on leave/holiday. Excluded: {excluded_users}"
        _safe_debug_log(f"[ASSIGNMENT DEBUG] ERROR: {error_msg}")
        frappe.log_error(error_msg, "Assignment Rule Filtering")
        # Return None to prevent assignment
        return None
    
    # Calculate load for each available user
    counts = []
    for user in available_users:
        count = frappe.db.count(
            "ToDo",
            dict(
                reference_type=self.document_type,
                allocated_to=user,
                status="Open",
            ),
        )
        counts.append(dict(user=user, count=count))
        _safe_debug_log(f"[ASSIGNMENT DEBUG] User {user} has {count} open assignments")
    
    # sort by dict value
    sorted_counts = sorted(counts, key=lambda k: k["count"])
    
    # pick the first user
    selected_user = sorted_counts[0].get("user") if sorted_counts else None
    _safe_debug_log(f"[ASSIGNMENT DEBUG] Selected user (load balancing): {selected_user}")
    return selected_user


# Override the get_user method to ensure doc is a dict
def get_user_filtered(self, doc):
    """
    Get the next user for assignment with filtering
    """
    # Ensure doc is a dict for safe_eval
    if not isinstance(doc, dict):
        doc = doc.as_dict() if hasattr(doc, 'as_dict') else dict(doc) if doc else {}
    
    _safe_debug_log(f"[ASSIGNMENT DEBUG] get_user_filtered - Rule: {self.name}, Rule Type: {self.rule}")
    _safe_debug_log(f"[ASSIGNMENT DEBUG] Document: {doc.get('name')}, Category: {doc.get('custom_category')}, Status: {doc.get('status')}")
    
    if self.rule == "Round Robin":
        return self.get_user_round_robin()
    elif self.rule == "Load Balancing":
        return self.get_user_load_balancing()
    elif self.rule == "Based on Field":
        return self.get_user_based_on_field(doc)


# Override safe_eval to ensure doc is always a dict
def safe_eval_filtered(self, fieldname, doc):
    """
    Safe eval with proper dict conversion - ensures doc is always a dict (mapping)
    """
    try:
        condition = self.get(fieldname)
        if not condition:
            # No condition set, return False silently
            return False
        
        # Ensure doc is a dict (mapping) for safe_eval
        # frappe.safe_eval requires the third parameter (eval_locals) to be a dict
        if doc is None:
            doc = {}
        elif not isinstance(doc, dict):
            # Try to convert to dict
            if hasattr(doc, 'as_dict'):
                try:
                    doc = doc.as_dict()
                except Exception:
                    doc = {}
            elif isinstance(doc, (list, tuple)):
                # If it's a list/tuple, create empty dict
                doc = {}
            else:
                # Try dict() constructor
                try:
                    doc = dict(doc) if hasattr(doc, '__iter__') and not isinstance(doc, str) else {}
                except (TypeError, ValueError):
                    doc = {}
        
        # Final check - ensure it's a dict
        if not isinstance(doc, dict):
            error_msg = f"safe_eval: Failed to convert doc to dict, type: {type(doc)}, rule: {self.name}"
            frappe.log_error(error_msg, "Assignment Rule Error")
            return False
        
        # Call frappe.safe_eval with proper dict
        result = frappe.safe_eval(condition, None, doc)
        return result
        
    except Exception as e:
        # when assignment fails, don't block the document as it may be
        # a part of the email pulling
        error_msg = str(e)
        # Only log if it's not a BrokenPipeError (which happens when client disconnects)
        if not isinstance(e, BrokenPipeError):
            frappe.log_error(
                f"safe_eval error in assignment rule {self.name}: {error_msg}, doc type: {type(doc) if 'doc' in locals() else 'unknown'}",
                "Assignment Rule Error"
            )
            # Only show message if not a broken pipe error
            try:
                frappe.msgprint(frappe._("Auto assignment failed: {0}").format(error_msg), indicator="orange")
            except (BrokenPipeError, OSError):
                # Ignore broken pipe errors when trying to send message
                pass

    return False


# Override do_assignment to ensure doc is converted to dict for render_template
def do_assignment_filtered(self, doc):
    """
    Override do_assignment to ensure doc is converted to dict for render_template
    """
    from frappe.desk.form import assign_to
    
    doctype = doc.get("doctype") if isinstance(doc, dict) else doc.doctype
    name_str = str(doc.get("name", "")) if isinstance(doc, dict) else str(doc.name)
    
    _safe_debug_log(f"[ASSIGNMENT DEBUG] do_assignment_filtered - Rule: {self.name}, DocType: {doctype}, Name: {name_str}")
    
    # Clear existing assignment (doc.get() works on Document objects)
    assign_to.clear(doctype, name_str, ignore_permissions=True)
    
    # Get user (this will use our filtered method which handles dict conversion)
    user = self.get_user(doc)
    
    if user:
        _safe_debug_log(f"[ASSIGNMENT DEBUG] Selected user for assignment: {user}")
        
        # Double-check for duplicate assignments after clearing
        duplicate_check = frappe.get_all("ToDo", filters={
            "reference_type": doctype,
            "reference_name": name_str,
            "status": "Open",
            "allocated_to": user,
        })
        
        if duplicate_check:
            _safe_debug_log(f"[ASSIGNMENT DEBUG] WARNING: Duplicate assignment detected! ToDo IDs: {[d.name for d in duplicate_check]}")
            # Don't create duplicate, but still update last_user for round robin
            self.db_set("last_user", user)
            return True
        
        # Convert doc to dict for render_template (Jinja2 requires dict context)
        if not isinstance(doc, dict):
            if hasattr(doc, 'as_dict'):
                render_context = doc.as_dict()
            else:
                # Fallback: create a dict with required fields
                render_context = {}
                if hasattr(doc, 'doctype'):
                    render_context['doctype'] = doc.doctype
                if hasattr(doc, 'name'):
                    render_context['name'] = doc.name
                # Copy other attributes that might be needed for template
                for attr in ['subject', 'status', 'priority', 'agent_group', 'raised_by']:
                    if hasattr(doc, attr):
                        render_context[attr] = getattr(doc, attr)
        else:
            render_context = doc
        
        # Use safe assignment to avoid link validation errors
        from frappe.utils import nowdate
        
        description = frappe.render_template(self.description, render_context)
        assignment_rule = self.name
        date = doc.get(self.due_date_based_on) if isinstance(doc, dict) else (getattr(doc, self.due_date_based_on, None) if self.due_date_based_on else None)
        
        # Create ToDo with ignore_links=True to bypass link validation
        todo_doc = frappe.get_doc({
            "doctype": "ToDo",
            "allocated_to": user,
            "reference_type": doctype,
            "reference_name": name_str,
            "description": description or f"Assignment for {doctype} {name_str}",
            "priority": "Medium",
            "status": "Open",
            "date": date or nowdate(),
            "assigned_by": frappe.session.user,
            "assignment_rule": assignment_rule,
        })
        
        # Initialize _assignment attribute to prevent AttributeError in on_update
        todo_doc._assignment = None
        
        # Set flags to bypass all validations
        todo_doc.flags.ignore_links = True
        todo_doc.flags.ignore_validate = True
        todo_doc.flags.ignore_mandatory = True
        
        # Insert with all ignore flags
        todo_doc.insert(ignore_permissions=True, ignore_links=True)
        _safe_debug_log(f"[ASSIGNMENT DEBUG] Created ToDo {todo_doc.name} for user {user}")
        
        # Update _assign field on the document so frontend can display assignees
        try:
            # Check if document exists before trying to update
            if frappe.db.exists(doctype, name_str):
                # Get current _assign value or create new list
                doc = frappe.get_doc(doctype, name_str)
                current_assign = []
                if hasattr(doc, '_assign') and doc._assign:
                    try:
                        current_assign = frappe.parse_json(doc._assign) or []
                    except:
                        current_assign = []
                
                # Add new assignee if not already in list
                if user not in current_assign:
                    current_assign.append(user)
                
                # Update _assign field
                frappe.db.set_value(doctype, name_str, "_assign", frappe.as_json(current_assign), update_modified=False)
                _safe_debug_log(f"[ASSIGNMENT DEBUG] Updated _assign field for {doctype} {name_str} to {frappe.as_json(current_assign)}")
                
                # Also update assigned_to field if it exists
                if frappe.get_meta(doctype).get_field("assigned_to"):
                    frappe.db.set_value(doctype, name_str, "assigned_to", user)
                    _safe_debug_log(f"[ASSIGNMENT DEBUG] Updated assigned_to field to {user}")
        except Exception as e:
            _safe_debug_log(f"[ASSIGNMENT DEBUG] Could not update _assign/assigned_to field: {str(e)}")
        
        # set for reference in round robin
        self.db_set("last_user", user)
        return True
    else:
        _safe_debug_log(f"[ASSIGNMENT DEBUG] No user selected for assignment")
    
    return False


# Monkey patch the Assignment Rule class
# Store original methods before patching
AssignmentRule._original_do_assignment = AssignmentRule.do_assignment
AssignmentRule.get_user_round_robin = get_user_round_robin_filtered
AssignmentRule.get_user_load_balancing = get_user_load_balancing_filtered
AssignmentRule.get_user = get_user_filtered
AssignmentRule.safe_eval = safe_eval_filtered
AssignmentRule.do_assignment = do_assignment_filtered
