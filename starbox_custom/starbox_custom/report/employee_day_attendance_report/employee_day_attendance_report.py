# Copyright (c) 2013, Starboxes India and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate, today
from frappe import msgprint, _


def execute(filters=None):
    if not filters:
        filters = {}

    if not filters.get("date"):
        msgprint(_("Please select date"), raise_exception=1)

    columns = get_columns(filters)
    date = filters.get("date")

    data = []
    row = []
    for emp in frappe.get_list('Employee', fields=['name', 'employee_name', 'designation', 'department'], filters={'status': 'Active'}):
        row = [emp.name, emp.employee_name, emp.designation, emp.department]
        att_details = frappe.db.get_value("Attendance", {'attendance_date': date, 'employee': emp.name}, [
                                          'name', 'status', 'in_time', 'out_time'], as_dict=True)
        if att_details:
            if att_details.name:
                row += [att_details.name]
            else:
                row += [""]

            if att_details.in_time:
                row += [att_details.in_time]
            else:
                row += [""]

            if att_details.out_time:
                row += [att_details.out_time]
            else:
                row += [""]

            if att_details.status:
                row += [att_details.status]
            else:
                row += [""]
        else:
            pass

        data.append(row)
    return columns, data


def get_columns(filters):
    columns = [
        _("Employee") + ":Link/Employee:90",
        _("Employee Name") + "::150",
        _("Designation") + "::180",
        _("Department") + "::180",
        _("Attendance") + ":Link/Attendance:90",
        _("In Time") + "::120",
        _("Out Time") + "::120",
        _("Status") + "::120",
    ]
    return columns
