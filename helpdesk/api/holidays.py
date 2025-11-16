import frappe
from frappe import _

@frappe.whitelist()
def get_holidays():
    """Get all holidays from the Holidays doctype"""
    try:
        holidays = frappe.get_all(
            "Holidays",
            fields=[
                "name",
                "holiday_name",
                "date",
                "type",
                "repeat_next_year"
            ],
            order_by="date desc"
        )
        return holidays
    except Exception as e:
        frappe.log_error(f"Error fetching holidays: {str(e)}")
        return []

@frappe.whitelist()
def get_holiday_details(holiday_name):
    """Get details of a specific holiday"""
    try:
        holiday = frappe.get_doc("Holidays", holiday_name)
        return holiday.as_dict()
    except Exception as e:
        frappe.log_error(f"Error fetching holiday details: {str(e)}")
        frappe.throw(_("Error fetching holiday details"))

@frappe.whitelist()
def create_holiday(holiday_data):
    """Create a new holiday"""
    try:
        if isinstance(holiday_data, str):
            import json
            holiday_data = json.loads(holiday_data)
        
        holiday = frappe.new_doc("Holidays")
        holiday.holiday_name = holiday_data.get("holiday_name")
        holiday.date = holiday_data.get("date")
        holiday.type = holiday_data.get("type")
        holiday.repeat_next_year = holiday_data.get("repeat_next_year", 0)
        
        # Handle official_location if provided
        if holiday_data.get("official_location"):
            for location in holiday_data["official_location"]:
                holiday.append("official_location", {
                    "assignment_group": location
                })
        
        holiday.insert()
        frappe.db.commit()
        
        return {
            "success": True,
            "message": _("Holiday created successfully"),
            "name": holiday.name
        }
    except Exception as e:
        frappe.log_error(f"Error creating holiday: {str(e)}")
        return {
            "success": False,
            "message": str(e)
        }

@frappe.whitelist()
def update_holiday(holiday_name, holiday_data):
    """Update an existing holiday"""
    try:
        if isinstance(holiday_data, str):
            import json
            holiday_data = json.loads(holiday_data)
        
        holiday = frappe.get_doc("Holidays", holiday_name)
        
        if holiday_data.get("holiday_name"):
            holiday.holiday_name = holiday_data["holiday_name"]
        if holiday_data.get("date"):
            holiday.date = holiday_data["date"]
        if holiday_data.get("type"):
            holiday.type = holiday_data["type"]
        if "repeat_next_year" in holiday_data:
            holiday.repeat_next_year = holiday_data["repeat_next_year"]
        
        # Handle official_location if provided
        if "official_location" in holiday_data:
            holiday.official_location = []
            for location in holiday_data["official_location"]:
                holiday.append("official_location", {
                    "assignment_group": location
                })
        
        holiday.save()
        frappe.db.commit()
        
        return {
            "success": True,
            "message": _("Holiday updated successfully")
        }
    except Exception as e:
        frappe.log_error(f"Error updating holiday: {str(e)}")
        return {
            "success": False,
            "message": str(e)
        }

@frappe.whitelist()
def delete_holiday(holiday_name):
    """Delete a holiday"""
    try:
        frappe.delete_doc("Holidays", holiday_name)
        frappe.db.commit()
        
        return {
            "success": True,
            "message": _("Holiday deleted successfully")
        }
    except Exception as e:
        frappe.log_error(f"Error deleting holiday: {str(e)}")
        return {
            "success": False,
            "message": str(e)
        }

@frappe.whitelist()
def get_holidays_for_employee(employee_id, from_date=None, to_date=None):
    """Get holidays applicable for a specific employee based on their location"""
    try:
        # Get employee's location/assignment group
        employee = frappe.get_doc("Employee", employee_id)
        employee_location = getattr(employee, "location", None) or getattr(employee, "branch", None)
        
        filters = {}
        if from_date:
            filters["date"] = [">=", from_date]
        if to_date:
            if "date" in filters:
                filters["date"] = ["between", [from_date, to_date]]
            else:
                filters["date"] = ["<=", to_date]
        
        # Get all holidays
        holidays = frappe.get_all(
            "Holidays",
            fields=["name", "holiday_name", "date", "type", "repeat_next_year"],
            filters=filters,
            order_by="date asc"
        )
        
        # Filter holidays based on employee location if applicable
        applicable_holidays = []
        for holiday in holidays:
            holiday_doc = frappe.get_doc("Holidays", holiday["name"])
            
            # If no location specified, holiday applies to all
            if not holiday_doc.official_location or len(holiday_doc.official_location) == 0:
                applicable_holidays.append(holiday)
            # Check if employee's location matches
            elif employee_location:
                for loc in holiday_doc.official_location:
                    if loc.assignment_group == employee_location:
                        applicable_holidays.append(holiday)
                        break
        
        return applicable_holidays
    except Exception as e:
        frappe.log_error(f"Error fetching holidays for employee {employee_id}: {str(e)}")
        return []


def should_exclude_user_from_assignment(user, assignment_rule_name=None, check_date=None):
    """
    Check if a user should be excluded from assignment based on:
    1. Leave applications (submitted/approved) for the user's employee
    2. Holidays - check if user belongs to any Dynamic User Assignment in holiday's official_location
    
    Simple logic: If user has holiday OR leave on check_date, exclude them from ALL assignments.
    
    Args:
        user: User email/name
        assignment_rule_name: Name of the assignment rule (not used, kept for compatibility)
        check_date: Date to check (defaults to today)
    
    Returns:
        bool: True if user should be excluded, False otherwise
    """
    try:
        from frappe.utils import getdate, today
        
        print(f"[HOLIDAY FILTER] Checking user: {user}, assignment_rule: {assignment_rule_name}, check_date: {check_date}")
        
        if not check_date:
            check_date = today()
        else:
        check_date = getdate(check_date)
        
        print(f"[HOLIDAY FILTER] Using check_date: {check_date}")
        
        # 1. Check leave applications
        # Get employee for the user
        employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
        print(f"[HOLIDAY FILTER] User {user} -> Employee: {employee}")
        
        if employee:
            # Check for leave applications (submitted/approved) for this employee
            leave_applications = frappe.get_all(
                "Leave Application",
                filters={
                    "employee": employee,
                    "status": ["in", ["Open", "Approved"]],
                    "docstatus": ["<", 2],  # Not cancelled
                },
                fields=["from_date", "to_date"],
            )
            
            print(f"[HOLIDAY FILTER] Found {len(leave_applications)} leave applications for employee {employee}")
            
            # Check if check_date falls within any leave application date range
            for leave in leave_applications:
                if leave.from_date and leave.to_date:
                    leave_from = getdate(leave.from_date)
                    leave_to = getdate(leave.to_date)
                    print(f"[HOLIDAY FILTER] Checking leave: {leave_from} to {leave_to} against {check_date}")
                    if leave_from <= check_date <= leave_to:
                        # User is on leave for this date - exclude them
                        print(f"[HOLIDAY FILTER] EXCLUDING user {user} - has leave application from {leave_from} to {leave_to}")
                        return True
        else:
            print(f"[HOLIDAY FILTER] No employee found for user {user}, skipping leave check")
        
        # 2. Check holidays
        # Fetch ALL holidays for the check date
        holidays = frappe.get_all(
            "Holidays",
            filters={"date": check_date},
            fields=["name"]
        )
        
        print(f"[HOLIDAY FILTER] Found {len(holidays)} holidays for date {check_date}")
        
        # Check each holiday to see if user belongs to any Dynamic User Assignment in official_location
            for holiday in holidays:
                try:
                print(f"[HOLIDAY FILTER] Checking holiday: {holiday.name}")
                holiday_doc = frappe.get_doc("Holidays", holiday.name)
                
                # If holiday has no official_location, skip it
                if not hasattr(holiday_doc, 'official_location') or not holiday_doc.official_location:
                    print(f"[HOLIDAY FILTER] Holiday {holiday.name} has no official_location, skipping")
                    continue
                
                print(f"[HOLIDAY FILTER] Holiday {holiday.name} has {len(holiday_doc.official_location)} official_location entries")
                
                # For each Assignment Group in official_location
                for loc in holiday_doc.official_location:
                    # Get the dynamic_user_assignment from Assignment Group
                    dynamic_user_assignment_id = getattr(loc, 'dynamic_user_assignment', None)
                    print(f"[HOLIDAY FILTER] Assignment Group -> dynamic_user_assignment: {dynamic_user_assignment_id}")
                
                    if not dynamic_user_assignment_id:
                        continue
                    
                    try:
                        # Get the Dynamic User Assignment document
                        dynamic_assignment = frappe.get_doc("Dynamic User Assignment", dynamic_user_assignment_id)
                        print(f"[HOLIDAY FILTER] Loaded Dynamic User Assignment: {dynamic_user_assignment_id}")
                        
                        # Check if user is in this Dynamic User Assignment's assigned_users
                        if hasattr(dynamic_assignment, 'assigned_users') and dynamic_assignment.assigned_users:
                            print(f"[HOLIDAY FILTER] Dynamic User Assignment has {len(dynamic_assignment.assigned_users)} assigned_users")
                            for assigned_user in dynamic_assignment.assigned_users:
                                # Check user_id field (AssignedUsers table has user_id, not user)
                                user_id = getattr(assigned_user, 'user_id', None)
                                print(f"[HOLIDAY FILTER] Checking assigned_user.user_id: {user_id} against user: {user}")
                                if user_id == user:
                                    # User is in a Dynamic User Assignment that has a holiday today - exclude them
                                    print(f"[HOLIDAY FILTER] EXCLUDING user {user} - found in Dynamic User Assignment {dynamic_user_assignment_id} which has holiday {holiday.name}")
                                    return True
                        else:
                            print(f"[HOLIDAY FILTER] Dynamic User Assignment {dynamic_user_assignment_id} has no assigned_users")
                    except Exception as e:
                        # If Dynamic User Assignment doesn't exist or can't be loaded, log and continue
                        print(f"[HOLIDAY FILTER] ERROR loading Dynamic User Assignment {dynamic_user_assignment_id}: {str(e)}")
                        frappe.log_error(f"Error loading Dynamic User Assignment {dynamic_user_assignment_id}: {str(e)}")
                        continue
                        
            except Exception as e:
                # If we can't load a holiday doc, log and continue
                print(f"[HOLIDAY FILTER] ERROR loading holiday {holiday.name}: {str(e)}")
                frappe.log_error(f"Error loading holiday {holiday.name}: {str(e)}")
                continue
        
        # User is not on leave and not in any Dynamic User Assignment with a holiday
        print(f"[HOLIDAY FILTER] NOT EXCLUDING user {user} - no leave or holiday match found")
        return False
        
    except Exception as e:
        print(f"[HOLIDAY FILTER] EXCEPTION checking user {user}: {str(e)}")
        frappe.log_error(f"Error checking if user should be excluded: {str(e)}")
        # On error, don't exclude the user (fail open)
        return False


def filter_users_for_assignment(users, assignment_rule_name=None, check_date=None):
    """
    Filter a list of users to exclude those on leave or holidays
    
    Args:
        users: List of user emails/names or list of dicts with 'user' or 'email' key
        assignment_rule_name: Name of the assignment rule
        check_date: Date to check (defaults to today)
    
    Returns:
        list: Filtered list of users
    """
    try:
        filtered_users = []
        
        for user in users:
            # Extract user email/name from different formats
            if isinstance(user, dict):
                user_email = user.get("email") or user.get("user") or user.get("name")
            else:
                user_email = user
            
            if not user_email:
                continue
            
            # Check if user should be excluded
            if not should_exclude_user_from_assignment(user_email, assignment_rule_name, check_date):
                filtered_users.append(user)
        
        return filtered_users
        
    except Exception as e:
        frappe.log_error(f"Error filtering users for assignment: {str(e)}")
        # On error, return original list
        return users