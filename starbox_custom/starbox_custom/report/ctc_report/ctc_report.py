# Copyright (c) 2013, Starboxes India and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate, today, nowdate
from frappe import msgprint, _


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns(filters)
    date = filters.get("date")

    data = []
    row = []
    active_employees = get_active_employees()
    for emp in active_employees:
        row = [emp.name, emp.employee_name, emp.designation, emp.department]

        base = frappe.db.get_value("Salary Structure Employee", {'employee': emp.name}, [
            'base'], as_dict=True)
        if base:
            row += [base.base]
        else:
             row += [""]

        present_days = 0
        emp_present_days = get_employee_attendance(emp.name, filters)

        for present in emp_present_days:
            present_days = present.count
        if emp_present_days:
            row += [present_days]
        else:
            row += ["0"]

        data.append(row)

    return columns, data


def get_columns(attendance):
    columns = [
        _("Employee") + ":Link/Employee:90",
        _("Employee Name") + "::150",
        _("Designation") + "::180",
        _("Department") + "::180",
        _("Gross") + ":Currency:180",
        _("PD") + "::50"
    ]
    return columns


def get_active_employees():
    active_employees = frappe.db.sql(
        """select * from `tabEmployee` where status = "Active" order by name""", as_dict=1)
    return active_employees


def get_employee_attendance(employee, filters):
    employee_attendance = frappe.db.sql("""select count(*) as count from `tabAttendance` where \
        docstatus = 1 and status = 'Present' and employee= %s and attendance_date between %s and %s""", (employee, filters.get("from_date"), filters.get("to_date")), as_dict=1)
    return employee_attendance


def get_conditions(filters):
    conditions = ""
    if filters.get("date_range"):
        conditions += " "
