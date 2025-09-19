import frappe
from frappe.utils import get_datetime, now_datetime

# Test what happens when response_by is None
response_by = None
try:
    result = get_datetime(response_by) < now_datetime()
    print(f"Result when response_by is None: {result}")
except Exception as e:
    print(f"Error when response_by is None: {e}")

# Test what happens when response_by is empty string
response_by = ""
try:
    result = get_datetime(response_by) < now_datetime()
    print(f"Result when response_by is empty string: {result}")
except Exception as e:
    print(f"Error when response_by is empty string: {e}")