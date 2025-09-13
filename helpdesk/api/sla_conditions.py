import frappe
from frappe import _


@frappe.whitelist()
def get_employee_fields():
    """Get employee fields that can be used in SLA conditions"""
    try:
        # Check if Employee doctype exists
        if not frappe.db.exists("DocType", "Employee"):
            return []
        
        # Get important employee fields for SLA conditions
        fields = [
            {"fieldname": "employee.department", "label": "Employee Department", "fieldtype": "Link", "options": "Department"},
            {"fieldname": "employee.designation", "label": "Employee Designation", "fieldtype": "Link", "options": "Designation"},
            {"fieldname": "employee.branch", "label": "Employee Branch", "fieldtype": "Link", "options": "Branch"},
            {"fieldname": "employee.employment_type", "label": "Employment Type", "fieldtype": "Link", "options": "Employment Type"},
            {"fieldname": "employee.grade", "label": "Employee Grade", "fieldtype": "Link", "options": "Employee Grade"},
            {"fieldname": "employee.company", "label": "Employee Company", "fieldtype": "Link", "options": "Company"},
            {"fieldname": "employee.reports_to", "label": "Reports To", "fieldtype": "Link", "options": "Employee"},
            {"fieldname": "employee.status", "label": "Employee Status", "fieldtype": "Select", "options": "Active\nInactive\nSuspended\nLeft"},
        ]
        
        return fields
    except Exception as e:
        frappe.log_error(f"Error fetching employee fields: {str(e)}")
        return []


@frappe.whitelist()
def get_ticket_fields_for_conditions():
    """Get all ticket fields that can be used in SLA conditions"""
    try:
        fields = []
        
        # Standard HD Ticket fields
        standard_fields = [
            {"fieldname": "status", "label": "Status", "fieldtype": "Select"},
            {"fieldname": "priority", "label": "Priority", "fieldtype": "Link", "options": "HD Ticket Priority"},
            {"fieldname": "ticket_type", "label": "Ticket Type", "fieldtype": "Link", "options": "HD Ticket Type"},
            {"fieldname": "agent_group", "label": "Team", "fieldtype": "Link", "options": "HD Team"},
            {"fieldname": "subject", "label": "Subject", "fieldtype": "Data"},
            {"fieldname": "raised_by", "label": "Raised By", "fieldtype": "Data"},
            {"fieldname": "contact", "label": "Contact", "fieldtype": "Link", "options": "Contact"},
            {"fieldname": "customer", "label": "Customer", "fieldtype": "Link", "options": "Customer"},
        ]
        
        fields.extend(standard_fields)
        
        # Add custom fields if they exist
        custom_fields = frappe.get_all(
            "Custom Field",
            filters={"dt": "HD Ticket"},
            fields=["fieldname", "label", "fieldtype", "options"]
        )
        
        for field in custom_fields:
            fields.append({
                "fieldname": field.fieldname,
                "label": field.label,
                "fieldtype": field.fieldtype,
                "options": field.options,
                "is_custom": True
            })
        
        # Add employee-related fields
        employee_fields = get_employee_fields()
        fields.extend(employee_fields)
        
        return fields
    except Exception as e:
        frappe.log_error(f"Error fetching ticket fields: {str(e)}")
        return []


@frappe.whitelist()
def evaluate_sla_condition(condition, ticket_name=None):
    """Evaluate SLA condition for a ticket with employee context"""
    try:
        if not condition:
            return True
        
        if ticket_name:
            doc = frappe.get_doc("HD Ticket", ticket_name)
        else:
            # Create a test document for validation
            doc = frappe.new_doc("HD Ticket")
        
        # Get employee context if ticket has assigned user
        employee = None
        if hasattr(doc, "_assign") and doc._assign:
            import json
            assignees = json.loads(doc._assign) if isinstance(doc._assign, str) else doc._assign
            if assignees and len(assignees) > 0:
                user_id = assignees[0]
                employee = frappe.db.get_value("Employee", {"user_id": user_id}, "*", as_dict=True)
        
        # Build context for evaluation
        context = {
            "doc": doc,
            "employee": employee,
            "frappe": frappe
        }
        
        # Evaluate condition
        result = frappe.safe_eval(condition, None, context)
        return bool(result)
        
    except Exception as e:
        frappe.log_error(f"Error evaluating SLA condition: {str(e)}")
        return False


@frappe.whitelist()
def get_condition_builder_options():
    """Get options for building SLA conditions"""
    return {
        "fields": get_ticket_fields_for_conditions(),
        "operators": [
            {"value": "==", "label": "Equals"},
            {"value": "!=", "label": "Not Equals"},
            {"value": "in", "label": "In"},
            {"value": "not in", "label": "Not In"},
            {"value": ">", "label": "Greater Than"},
            {"value": "<", "label": "Less Than"},
            {"value": ">=", "label": "Greater Than or Equal"},
            {"value": "<=", "label": "Less Than or Equal"},
            {"value": "like", "label": "Contains"},
            {"value": "not like", "label": "Does Not Contain"},
        ],
        "logical_operators": [
            {"value": "and", "label": "AND"},
            {"value": "or", "label": "OR"},
        ]
    }