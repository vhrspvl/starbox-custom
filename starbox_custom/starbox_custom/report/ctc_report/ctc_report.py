# Copyright (c) 2013, Starboxes India and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, flt, getdate, today, nowdate, rounded, date_diff, money_in_words
from frappe import msgprint, _


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns(filters)

    data = []
    row = []
    active_employees = get_active_employees()
    for emp in active_employees:
        row = [emp.name, emp.employee_name, emp.designation, emp.department]

        emp_present_days = get_employee_attendance(emp.name, filters)

        for present in emp_present_days:
            present_days = present.count
        if emp_present_days:
            row += [present_days]
        else:
            row += ["0"]

        sse = frappe.db.get_value("Salary Structure Employee", {'employee': emp.name}, [
            'base'], as_dict=True)
        if sse:    
            gross = sse.base    
            if gross:
                row += [gross]
                if present_days > 0:
                    daily_basic = (((flt(gross) * .35)/flt('26')))
                    act_basic = (flt(gross) * .35)
                    act_ca = flt("1600")
                    daily_ca = flt(act_ca) / flt('26')
                    act_ma = flt("1250")
                    daily_ma = flt(act_ma) / flt('26')
                    act_oa = flt(gross)-(act_basic + act_ca + act_ma)
                    daily_oa = flt(act_oa) / flt('26')
                    earned_basic = flt(daily_basic) * flt(present_days)
                    earned_ca = flt(daily_ca) * flt(present_days)
                    earned_ma = flt(daily_ma) * flt(present_days)
                    earned_oa = flt(daily_oa) * flt(present_days)
                    if act_basic:
                        row += [act_basic]
                    if earned_basic:
                        row += [earned_basic]
                    if act_ca:
                            row += [act_ca]
                    if earned_ca:
                        row += [earned_ca]
                    if act_ma:
                            row += [act_ma]
                    if earned_ma:
                        row += [earned_ma]
                    if act_oa:
                        row += [act_oa]
                    if earned_oa:
                        row += [earned_oa]
            else:
                row += [""]

        
        

        data.append(row)

    return columns, data


def get_columns(attendance):
    columns = [
        _("Employee") + ":Link/Employee:90",
        _("Employee Name") + "::150",
        _("Designation") + "::180",
        _("Department") + "::180",
        _("PD") + "::50",
        _("Gross") + ":Currency:100",
        _("Actual Basic") + ":Currency:100",
        _("Earned Basic") + ":Currency:100",
        _("Actual CA") + ":Currency:100",
        _("Earned CA") + ":Currency:100",
        _("Actual MA") + ":Currency:100",
        _("Earned MA") + ":Currency:100",
        _("Actual OA") + ":Currency:100",
        _("Earned OA") + ":Currency:100"
        
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
