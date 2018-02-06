# Copyright (c) 2013, Starboxes India and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _, msgprint
from frappe.utils import (cint, cstr, date_diff, flt, getdate, money_in_words,
                          nowdate, rounded, today)


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns(filters)

    data = []
    row = []
    # conditions_emp = get_conditions(filters)
    # active_employees = get_active_employees(filters, conditions_emp)
    active_employees = get_active_employees()
    grand_earnings = 0
    # grand_actuals = 0
    for emp in active_employees:
        row = [emp.name, emp.employee_name, emp.designation,
               emp.department, emp.employment_type]

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

                act_basic = (flt(gross) * .45)
                daily_basic = (act_basic / flt('26'))
                act_hra = (flt(gross) * .225)
                daily_hra = (act_hra / flt('26'))
                act_da = (flt(gross) * .25)
                daily_da = (act_da / flt('26'))
                act_wa = flt("150")
                daily_wa = (act_wa / flt('26'))
                act_ca = flt("1600")
                daily_ca = flt(act_ca) / flt('26')
                act_ma = flt("1250")
                daily_ma = flt(act_ma) / flt('26')
                if emp.employment_type == 'Staff':
                    act_oa = flt(gross) - (act_basic +
                                           act_hra + act_ca + act_ma)
                    daily_oa = flt(act_oa) / flt('26')
                if emp.employment_type == 'Operator':
                    act_oa = flt(gross) - (act_basic + act_hra +
                                           act_wa + act_da)
                    daily_oa = flt(act_oa) / flt('26')

                total_actuals = 0
                if act_basic:
                    row += [act_basic]
                    total_actuals += act_basic
                if act_hra:
                    row += [act_hra]
                    total_actuals += act_hra
                if emp.employment_type == 'Operator':
                    if act_da:
                        row += [act_da]
                        total_actuals += act_da
                    else:
                        row += [""]
                    if act_wa:
                        row += [act_wa]
                        total_actuals += act_wa
                    else:
                        row += [""]
                else:
                    row += ["", ""]
                if emp.employment_type == 'Staff':
                    if act_ca:
                        row += [act_ca]
                        total_actuals += act_ca
                    if act_ma:
                        row += [act_ma]
                        total_actuals += act_ma
                else:
                    row += ["", ""]
                if act_oa:
                    row += [act_oa]
                    total_actuals += act_oa

                if total_actuals:
                    row += [total_actuals]
                else:
                    row += [""]

                if present_days > 0:
                    earned_basic = flt(daily_basic) * flt(present_days)
                    earned_hra = flt(daily_hra) * flt(present_days)
                    earned_da = flt(daily_da) * flt(present_days)
                    earned_wa = flt(daily_wa) * flt(present_days)
                    earned_ca = flt(daily_ca) * flt(present_days)
                    earned_ma = flt(daily_ma) * flt(present_days)
                    earned_oa = flt(daily_oa) * flt(present_days)
                    total_earnings = 0
                    if earned_basic:
                        row += [earned_basic]
                        total_earnings += earned_basic
                    if earned_hra:
                        row += [earned_hra]
                        total_earnings += earned_hra
                    if emp.employment_type == 'Operator':
                        if earned_da:
                            row += [earned_da]
                            total_earnings += earned_da
                        if earned_wa:
                            row += [earned_wa]
                            total_earnings += earned_wa
                    else:
                        row += ["", ""]
                    if emp.employment_type == 'Staff':
                        if earned_ca:
                            row += [earned_ca]
                            total_earnings += earned_ca
                        if earned_ma:
                            row += [earned_ma]
                            total_earnings += earned_ma
                    else:
                        row += ["", ""]
                    if earned_oa:
                        # grand_oa += earned_oa
                        row += [earned_oa]
                        total_earnings += earned_oa
                    if total_earnings:
                        grand_earnings += total_earnings
                        row += [total_earnings]
                else:
                    row += [""]
        totals = ["Totals", "", "", "", "", "", "", "",
                  "", "", "", "", "", "", "", "", "", "", "", "", "", "", grand_earnings]
        data.append(row)
    data.append(totals)

    return columns, data


def get_columns(attendance):
    columns = [
        _("Employee") + ":Link/Employee:90",
        _("Employee Name") + ":Data:150",
        _("Designation") + ":Data:180",
        _("Department") + ":Data:180",
        _("Employment Type") + ":Data:180",
        _("PD") + ":Int:50",
        _("Gross") + ":Currency:100",
        _("Actual Basic") + ":Currency:100",
        _("Actual HRA") + ":Currency:100",
        _("Actual DA") + ":Currency:100",
        _("Actual WA") + ":Currency:100",
        _("Actual CA") + ":Currency:100",
        _("Actual MA") + ":Currency:100",
        _("Actual OA") + ":Currency:100",
        _("Actual Totals") + ":Currency:100",
        _("Earned Basic") + ":Currency:100",
        _("Earned HRA") + ":Currency:100",
        _("Earned DA") + ":Currency:100",
        _("Earned WA") + ":Currency:100",
        _("Earned CA") + ":Currency:100",
        _("Earned MA") + ":Currency:100",
        _("Earned OA") + ":Currency:100",
        _("Total Earnings") + ":Currency:100"

    ]
    return columns


def get_active_employees():
    active_employees = frappe.db.sql(
        """select emp.name,emp.employee_name,emp.department,emp.designation,emp.employment_type from `tabEmployee` emp where emp.status = "Active" order by emp.name""", as_dict=1)
    return active_employees


# def get_active_employees(filters, conditions_emp):
#     active_employees = frappe.db.sql(
#         """select * from `tabEmployee` emp where emp.status = "Active" %s order by emp.name""" % (conditions_emp), as_dict=1)
#     return active_employees


def get_employee_attendance(employee, filters):
    employee_attendance = frappe.db.sql("""select count(*) as count from `tabAttendance` where \
        docstatus = 1 and status = 'Present' and employee= %s and attendance_date between %s and %s""", (employee, filters.get("from_date"), filters.get("to_date")), as_dict=1)
    return employee_attendance


def get_conditions(filters):
    conditions_emp = ""

    if filters.get("department"):
        conditions_emp += " AND emp.department = '%s'" % filters["department"]

    if filters.get("designation"):
        conditions_emp += " AND emp.designation = '%s'" % filters["designation"]

    return filters, conditions_emp
