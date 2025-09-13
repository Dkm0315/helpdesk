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