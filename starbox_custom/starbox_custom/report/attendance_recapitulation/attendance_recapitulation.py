# Copyright (c) 2013, Starboxes India and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


def execute(filters=None):
    if not filters:
        filters = {}
    columns = get_columns()

    data = []
    row = []
    leave_type = from_date_session = to_date_session = ""
    conditions, filters = get_conditions(filters)
    total = from_time = late_in = early_out = shift_in_time = dt = 0
    attendance = get_attendance(conditions, filters)
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    for att in attendance:
        if att:
            if att.name:
                row = [att.name]
            else:
                row = ["-"]

            if att.attendance_date:
                row += [att.attendance_date]
            else:
                row = ["-"]

            if att.employee:
                row += [att.employee]
            else:
                row += ["-"]

            if att.employee_name:
                row += [att.employee_name]
            else:
                row += ["-"]

            if att.employment_type:
                row += [att.employment_type]
            else:
                row += ["-"]

            if att.department:
                row += [att.department]
            else:
                row += ["-"]

            if att.shift:
                row += [att.shift]
            else:
                row += ["-"]

            if att.in_time:
                row += [att.in_time]
            else:
                row += ["-"]

            if att.out_time:
                row += [att.out_time]
            else:
                row += ["-"]

            if att.total_working_hours:
                row += [att.total_working_hours]
            else:
                row += ["-"]

            if att.status:
                row += [att.status]
            else:
                row += ["-"]

            data.append(row)
    return columns, data


def get_columns():
    columns = [
        _("Name") + ":Link/Attendance:100",
        _("Attendance Date") + ":Date:100",
        _("Employee") + ":Link/Employee:100",
        _("Employee Name") + ":Data:150",
        _("Employment Type") + ":Data:150",
        _("Department") + ":Data:150",
        _("Shift") + ":Data:90",
        _("In Time") + ":Data:90",
        _("Out Time") + ":Data:90",
        _("Working Hours") + ":Data:90",
        _("Status") + ":Data:90"
    ]
    return columns


def get_attendance(conditions, filters):
    attendance = frappe.db.sql("""select att.name as name,att.attendance_date as attendance_date,att.employee as employee, att.employee_name as employee_name,att.employment_type as employment_type,att.department as department,att.shift as shift,att.in_time as in_time,att.out_time as out_time,att.total_working_hours as total_working_hours,att.status as status from `tabAttendance` att 
    where  docstatus = 1 %s order by att.attendance_date,att.employee""" % conditions, filters, as_dict=1)
    return attendance


def get_conditions(filters):
    conditions = ""
    if filters.get("from_date"):
        conditions += "and att.attendance_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " and att.attendance_date <= %(to_date)s"
    if filters.get("status_in"):
        conditions += " and att.in_time > 0"
    if filters.get("employee"):
        conditions += "AND att.employee = '%s'" % filters["employee"]
    if filters.get("department"):
        conditions += " AND att.department = '%s'" % filters["department"]
    if filters.get("location"):
        conditions += " AND att.location = '%s'" % filters["location"]

    if not frappe.get_doc("User", frappe.session.user).get("roles", {"role": "System Manager"}):
        employee = frappe.db.get_value(
            "Employee", {"user_id": filters.get("user")})
        if filters.get("user"):
            conditions += " and att.employee = %s" % employee
    return conditions, filters
