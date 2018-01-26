# Copyright (c) 2013, Starboxes India and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate, today,nowdate
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
        row = [emp.name, emp.employee_name, emp.designation, emp.department]
        att_details = frappe.db.get_value("Attendance", {'attendance_date': date, 'employee': emp.name}, [
                                          'name', 'attendance_date','status', 'in_time', 'out_time'], as_dict=True)
        holiday = frappe.get_list("Holiday List", filters={
            'holiday_date': date})
        if holiday:
            row += ["", "", "", "Holiday", ""]
        else:    
            if att_details:
                if att_details.attendance_date:
                    row += [att_details.attendance_date]
                else:
                    row += [""]

                if att_details.in_time:
                    row += [att_details.in_time]
                else:
                    row += ["00:00"]

                if att_details.out_time:
                    row += [att_details.out_time]
                else:
                    row += ["00:00"]

                if att_details.status:    
                    row += [att_details.status]
                else:
                    row += [""]

                if att_details.in_time > 0 and att_details.status == 'Absent':
                    row += ['Late']
                elif att_details.in_time and not att_details.out_time:
                    row += ['Failed Out Punch']    
                else:
                    row += [""]

            else:
                row +=["","","","Absent",""]

        data.append(row)
    return columns, data


def get_columns(filters):
    columns = [
        _("Employee") + ":Link/Employee:90",
        _("Employee Name") + "::150",
        _("Designation") + "::180",
        _("Department") + "::180",
        _("Attendance Date") + ":Date:90",
        _("In Time") + "::120",
        _("Out Time") + "::120",
        _("Status") + "::120",
        _("Remarks") + "::120",
    ]
    return columns

def get_employees():
    employees = frappe.db.sql("""select name,employee_name,designation,department from tabEmployee where status = 'Active'""",as_dict=1)
    return employees
