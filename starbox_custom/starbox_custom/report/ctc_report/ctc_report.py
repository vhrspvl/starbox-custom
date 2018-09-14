# Copyright (c) 2013, Starboxes India and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _, msgprint
from frappe.utils import (cint, cstr, date_diff, flt, getdate, money_in_words,
                          nowdate, rounded, today)
from datetime import datetime
from calendar import monthrange
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee


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
    grand_oa = 0
    grand_ma = 0
    grand_ca = 0
    grand_wa = 0
    grand_da = 0
    grand_hra = 0
    grand_basic = 0
    pf = 0
    esi = 0
    canteen = 0
    pt = 0
    total_deduction = 0
    from_date = datetime.strptime(filters.get("from_date"), '%Y-%m-%d')
    present_days = 0
    working_days = monthrange(
        cint(from_date.year), from_date.month)[1]
    payable_days = 0
    for emp in active_employees:
        row = [emp.name, emp.employee_name, emp.designation,
               emp.department, emp.employment_type]

        emp_present_days = get_employee_attendance(emp.name, filters)

        for present in emp_present_days:
            present_days = present.count
        holidays = get_holidays_for_employee(emp.name, filters)
        leaves = get_leave(emp.name, filters)
        joining_date, relieving_date = frappe.db.get_value(
            "Employee", emp.name, ["date_of_joining", "relieving_date"])
        no_of_holidays = 0
        for holiday in holidays:
            if datetime.strptime(holiday, '%Y-%m-%d').date() > joining_date:
                no_of_holidays += 1

        if emp_present_days:
            row += [present_days]
        else:
            row += [""]

        if leaves:
            row += [leaves]
        else:
            row += [""]

        if no_of_holidays:
            row += [no_of_holidays]
        else:
            row += [""]

        payable_days = present_days

        if emp_present_days > 0:
            payable_days = present_days + no_of_holidays + leaves

        if payable_days:
            row += [payable_days]
        else:
            row += [""]

        # if emp_present_days and no_of_holidays:
        #     payable_days = present_days + no_of_holidays
        #     row += [payable_days]
        # else:
        #     row += [""]
        sse = frappe.db.get_value("Salary Structure Employee", {'employee': emp.name}, ['base'], as_dict=True)

        if sse:
            gross = sse.base
            if gross:
                row += [gross]

                act_basic = (flt(gross) * .45)
                daily_basic = (act_basic / flt(working_days))
                act_hra = (flt(gross) * .225)
                daily_hra = (act_hra / flt(working_days))
                act_da = (flt(gross) * .25)
                daily_da = (act_da / flt(working_days))
                act_wa = flt("150")
                daily_wa = (act_wa / flt(working_days))
                act_ca = flt("1600")
                daily_ca = flt(act_ca) / flt(working_days)
                act_ma = flt("1250")
                daily_ma = flt(act_ma) / flt(working_days)

                
                if emp.employment_type == 'Staff':
                    act_oa = flt(gross) - (act_basic +
                                           act_hra + act_ca + act_ma)
                    daily_oa = flt(act_oa) / flt(working_days)
                if emp.employment_type == 'Operator':
                    act_oa = flt(gross) - (act_basic + act_hra +
                                           act_wa + act_da)
                    daily_oa = flt(act_oa) / flt(working_days)

                total_actuals = 0
                if act_basic:
                    row += [round(act_basic)]
                    total_actuals += act_basic
                else:
                    row += ["0"]
                if act_hra:
                    row += [round(act_hra)]
                    total_actuals += act_hra
                else:
                    row += ["0"]
                if emp.employment_type == 'Operator':
                    if act_da:
                        row += [round(act_da)]
                        total_actuals += act_da
                    else:
                        row += [""]
                    if act_wa:
                        row += [round(act_wa)]
                        total_actuals += act_wa
                    else:
                        row += [""]
                else:
                    row += ["", ""]
                if emp.employment_type == 'Staff':
                    if act_ca:
                        row += [round(act_ca)]
                        total_actuals += act_ca
                    else:
                        row += ["0"]
                    if act_ma:
                        row += [round(act_ma)]
                        total_actuals += act_ma
                    else:
                        row += ["0"]
                else:
                    row += ["", ""]
                if act_oa:
                    row += [round(act_oa)]
                    total_actuals += act_oa
                else:
                    row += ["0"]

                if total_actuals:
                    row += [round(total_actuals)]
                else:
                    row += [""]

                if present_days > 0:
                    earned_basic = flt(daily_basic) * flt(payable_days)
                    earned_hra = flt(daily_hra) * flt(payable_days)
                    earned_da = flt(daily_da) * flt(payable_days)
                    earned_wa = flt(daily_wa) * flt(payable_days)
                    earned_ca = flt(daily_ca) * flt(payable_days)
                    earned_ma = flt(daily_ma) * flt(payable_days)
                    earned_oa = flt(daily_oa) * flt(payable_days)
                    total_earnings = 0
                    
             
                    if earned_basic:
                        row += [round(earned_basic)]
                        grand_basic += earned_basic
                        total_earnings += earned_basic
                    else:
                        row += ["0"]
                    if earned_hra:
                        row += [round(earned_hra)]
                        grand_hra += earned_hra
                        total_earnings += earned_hra
                    else:
                        row += ["0"]
                    if emp.employment_type == 'Operator':
                        if earned_da:
                            row += [round(earned_da)]
                            grand_da += earned_da
                            total_earnings += earned_da
                        else:
                            row += ["0"]
                        if earned_wa:
                            row += [round(earned_wa)]
                            grand_wa += earned_wa
                            total_earnings += earned_wa
                        else:
                            row += ["0"]
                    else:
                        row += ["", ""]
                    if emp.employment_type == 'Staff':
                        if earned_ca:
                            row += [round(earned_ca)]
                            grand_ca += earned_ca
                            total_earnings += earned_ca
                        else:
                            row += ["0"]
                        if earned_ma:
                            row += [round(earned_ma)]
                            grand_ma += earned_ma
                            total_earnings += earned_ma
                        else:
                            row += ["0"]
                    else:
                        row += ["", ""]
                    if earned_oa:
                        grand_oa += earned_oa
                        row += [round(earned_oa)]
                        total_earnings += earned_oa
                    else:
                        row += ["0"]
                    if total_earnings:
                        grand_earnings += total_earnings
                        row += [round(total_earnings)]
                    else:
                        row += ["0"]
                    if earned_basic :
                        pf = (earned_basic)*0.12
                        row += [round(pf)]
                    else:
                        row += [""]
                    if gross:
                        if act_basic <= 21000:
                            esi =(gross)*0.0175
                            row += [round(esi)]
                        else:
                            row +=[""]

                    else:
                        row += [""]
                    if emp.employment_type == 'Staff' or  emp.employment_type == 'DET': 
                        canteen = (365.00/ flt(working_days)) * flt(present_days) 
                        row += [round(canteen)]
                    elif emp.employment_type == 'Operator':
                        canteen = (265.00/ flt(working_days)) * flt(present_days) 
                        row += [round(canteen)]  
                    else:
                        row += [""]
                    
                    if gross >= 3501 and gross <= 5000:
                        pt = flt("20")
                        row += [round(pt)]
                    elif gross > 5001 and gross < 7500:
                        pt = flt("50")
                        row += [round(pt)]
                    elif gross >= 7501 and gross <= 10000:
                        pt = flt("98")
                        row += [round(pt)]
                    elif gross >= 10001 and gross <= 12500:
                        pt = flt("147")
                        row += [round(pt)]
                    elif gross >= 12501:
                        pt = flt("196")
                        row += [round(pt)]
                    else:
                        row += [""]
                    if pf and esi and canteen and pt:
                        total_deduction = (pf + esi + canteen + pt)
                        row += [round(total_deduction)]
                    else:
                        row += [""]

                else:
                    row += [""]
            else:
                row += ["0"]
        else:
            row += ["0"]
        totals = ["Totals", "", "", "", "", "", "", "", "", "",
                  "", "", "", "", "", "", "", grand_basic, grand_hra, grand_da, grand_wa, grand_ca, grand_ma, grand_oa, grand_earnings,pf,esi,canteen,pt,total_deduction]
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
        _("Leaves") + ":Int:50",
        _("Holidays") + ":Int:50",
        _("Payable Days") + ":Int:50",
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
        _("Total Earnings") + ":Currency:100",
        _("PF") + ":Currency:100",
        _("ESI") + ":Currency:100",
        _("Canteen") + ":Currency:100",
        _("PT") + ":Currency:100",
        _("Total Deduction") + ":Currency:100"
    
    ]
    return columns


def get_active_employees():
    active_employees = frappe.db.sql(
        """select emp.name,emp.employee_name,emp.department,emp.designation,emp.employment_type from `tabEmployee` emp where emp.status = "Active" and emp.employment_type != 'Contract' order by emp.name""", as_dict=1)
    return active_employees


def get_holidays_for_employee(employee, filters):
    holiday_list = get_holiday_list_for_employee(employee)
    holidays = frappe.db.sql_list('''select holiday_date from `tabHoliday`
            where
                parent=%(holiday_list)s
                and holiday_date >= %(start_date)s
                and holiday_date <= %(end_date)s''', {
        "holiday_list": holiday_list,
        "start_date": filters.get("from_date"),
        "end_date": filters.get("to_date")
    })

    holidays = [cstr(i) for i in holidays]

    return holidays


def get_employee_attendance(employee, filters):
    employee_attendance = frappe.db.sql("""select count(*) as count from `tabAttendance` where \
        docstatus = 1 and status = 'Present' and employee= %s and attendance_date between %s and %s""", (employee, filters.get("from_date"), filters.get("to_date")), as_dict=1)
    return employee_attendance


def get_leave(employee, filters):
    count = 0
    leave = frappe.db.sql('''select name,total_leave_days from `tabLeave Application`
            where
                employee=%(emp)s
                and from_date >= %(start_date)s
                and to_date <= %(end_date)s
                and leave_type !='Leave without Pay'
                and docstatus = 1
                and status = 'Approved'
                ''', {
        "emp": employee,
        "start_date": filters.from_date,
        "end_date": filters.to_date
    }, as_dict=1)

    for l in leave:
        count += l["total_leave_days"]
    return count


def get_conditions(filters):
    conditions_emp = ""

    if filters.get("department"):
        conditions_emp += " AND emp.department = '%s'" % filters["department"]

    if filters.get("designation"):
        conditions_emp += " AND emp.designation = '%s'" % filters["designation"]

    return filters, conditions_emp
