# -*- coding: utf-8 -*-
# Copyright (c) 2019, Starboxes India and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.model.document import Document


class ShiftAssignmentTool(Document):
    pass


@frappe.whitelist()
def update_shift(shift_assignment_tool_kit):
    sat = {}
    sat = json.loads(shift_assignment_tool_kit)
    for sa in sat:
        checked = sa.get("__checked")
        frappe.errprint(checked)
        employee = sa.get("employee")
        from_date = sa.get("from_date")
        to_date = sa.get("to_date")
        shift = sa.get("shift")
        if employee:
            emp = frappe.get_doc("Employee", employee)
        if checked == 1:
            nsa = frappe.new_doc("Shift Assignment")
            nsa.update({
                "employee": employee,
                "from_date": from_date,
                "to_date": to_date,
                "shift": shift,
                "employee_name": emp.employee_name,
                "employment_type": emp.employment_type,
                "department": emp.department,
                "designation": emp.designation,
                "contractor": emp.contractor
            })
            nsa.save(ignore_permissions=True)
    return "Ok"
