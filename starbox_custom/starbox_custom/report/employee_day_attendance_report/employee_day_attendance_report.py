# Copyright (c) 2013, Starboxes India and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate, today, nowdate
from frappe import msgprint, _


def execute(filters=None):
    if not filters:
        filters = {}

    if not filters.get("date"):
        msgprint(_("Please select date"), raise_exception=1)

    columns = get_columns(filters)
    date = filters.get("date")
    if date and getdate(date) > getdate(nowdate()):
        frappe.throw(_("Date cannot be in the Future"))
    data = []
    row = []
    for emp in get_employees():
        row = [emp.name, emp.biometric_id, emp.employee_name,emp.employment_type,
               emp.designation, emp.department, emp.contractor]
        att_details = frappe.db.get_value("Attendance", {'attendance_date': date, 'employee': emp.name}, [
                                          'name', 'total_working_hours', 'attendance_date', 'status', 'in_time', 'out_time'], as_dict=True)
        holiday = frappe.get_list("Holiday List", filters={
            'holiday_date': date})
        is_leave = check_leave_record(emp.name, date)
        if holiday:
            row += ["", "", "", "", "Holiday", ""]
        elif is_leave:
            row += ["", "", "", "", is_leave[1], ""]
        else:
            if att_details:
                if att_details.attendance_date:
                    row += [att_details.attendance_date]
                else:
                    row += [""]

                if att_details.in_time:
                    row += [att_details.in_time]
                else:
                    row += ["00:00:00"]

                if att_details.out_time:
                    row += [att_details.out_time]
                else:
                    row += ["00:00:00"]

                if att_details.total_working_hours:
                    row += [att_details.total_working_hours]
                else:
                    row += ["00:00:00"]

                if att_details.status:
                    row += [att_details.status]
                else:
                    row += [""]

                if att_details.in_time and not att_details.out_time:
                    row += ['Miss Punch']
                else:
                    row += [""]

            else:
                row += [date, "", "", "", "Absent", ""]
        data.append(row)
    return columns, data


def get_columns(filters):
    columns = [
        _("Employee") + ":Link/Employee:90",
        _("Employee ID") + ":Data:90",
        _("Employee Name") + "::150",
         _("Employment Type") + "::150",
        _("Designation") + "::180",
        _("Department") + "::180",
        _("Contractor") + "::180",
        _("Attendance Date") + ":Date:90",
        _("In Time") + "::120",
        _("Out Time") + "::120",
        _("Total Working Hours") + ":Float:120",
        _("Status") + "::120",
        _("Remarks") + "::120",
    ]
    return columns


def get_employees():
    employees = frappe.db.sql(
        """select name,biometric_id,employee_name,employment_type,designation,department,contractor from tabEmployee where status = 'Active'""", as_dict=1)
    return employees


def check_leave_record(employee, date):
    leave_record = frappe.db.sql("""select leave_type, half_day from `tabLeave Application`
    where employee = %s and %s between from_date and to_date and status = 'Approved'
    and docstatus = 1""", (employee, date), as_dict=True)
    if leave_record:
        if leave_record[0].half_day:
            status = 'Half Day'
        else:
            status = 'On Leave'
            leave_type = leave_record[0].leave_type

        return status, leave_type
