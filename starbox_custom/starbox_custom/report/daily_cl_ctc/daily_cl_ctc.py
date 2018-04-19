# Copyright (c) 2013, Starboxes India and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _, msgprint
import math
from frappe.utils import (cint, cstr, date_diff, flt, getdate, money_in_words,
                          nowdate, rounded, today)


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns(filters)

    data = []
    row = []
    grand_earnings = 0
    grand_totals = 0
    present_hours = 0
    total_earnings = 0

    active_cl = get_active_cl()
    for cl in active_cl:
        total_earnings = 0
        present_hours = 0
        total_working_hours = 0

        row = [cl.name, cl.biometric_id, cl.employee_name,
               cl.contractor, cl.employment_type]
        cl_present_days = get_cl_attendance(cl.name, filters)
        working_hours = cl.working_hours
        actual_working_hours = math.ceil(working_hours.seconds / 3600)
        for present in cl_present_days:
            in_time = present.in_time
            out_time = present.out_time
            total_working_hours = present.total_working_hours
        if cl_present_days:
            if in_time:
                row += [in_time]
            else:
                row += ["00:00:00"]
            if out_time:
                row += [out_time]
            else:
                row += ["00:00:00"]
            if in_time:
                row += [total_working_hours]
            else:
                row += ["0.00"]
        else:
            row += ["", "", ""]

        ctc = frappe.db.get_value("Contractor", {'name': cl.contractor}, [
            'ctc_per_day'], as_dict=True)
        if ctc:
            ctc_day = ctc.ctc_per_day
            if ctc_day:
                row += [ctc_day]
                if total_working_hours > 0:
                    actual_hours = total_working_hours - actual_working_hours
                    if total_working_hours > actual_working_hours:
                        earned_ctc = flt((total_working_hours - actual_hours) *
                                         (ctc_day / actual_working_hours))
                    else:
                        earned_ctc = flt(total_working_hours *
                                         (ctc_day / actual_working_hours))
                    if earned_ctc:
                        row += [round(earned_ctc)]
                        total_earnings += earned_ctc
                        grand_earnings += earned_ctc
                    else:
                        row += ["0"]
                else:
                    row += ["0"]
            else:
                row += ["0", "0"]

        ot_hours = total_working_hours - actual_working_hours
        if ot_hours > 0:
            row += [ot_hours]
        else:
            row += ["0"]

        ot_day = (ctc_day / actual_working_hours) * 2
        if ot_hours > 0:
            row += [ot_day]
            earned_ot = flt(ot_hours * ot_day)
            if earned_ot:
                row += [round(earned_ot)]
                total_earnings += earned_ot
            else:
                row += ["0"]
        else:
            row += ["0", "0"]

        if total_earnings:
            grand_totals += total_earnings
            row += [round(total_earnings)]
        else:
            row += [""]
        data.append(row)

    return columns, data


def get_columns(attendance):
    columns = [
        _("Employee") + ":Link/Employee:90",
        _("Employee ID") + ":Link/Employee:90",
        _("Employee Name") + "::150",
        _("Contractor") + ":Link/Contractor:180",
        _("Employment Type") + ":Link/Employment Type:130",
        _("In Time") + ":Data:80",
        _("Out Time") + ":Data:80",
        _("Total Working Hours") + ":Float:80",
        _("CTC Per Day") + ":Currency:100",
        _("Earned CTC") + ":Currency:100",
        _("OT Hours ") + ":Float:80",
        _("OT Cost") + ":Currency:100",
        _("OT Earnings") + ":Currency:100",
        _("Total Earnings") + ":Currency:100"
    ]

    return columns


def get_active_cl():
    active_cl = frappe.db.sql(
        """select emp.name,emp.biometric_id,emp.working_hours,emp.employee_name,emp.contractor,emp.employment_type from `tabEmployee` emp where emp.status = "Active" and emp.employment_type="Contract" order by emp.name""", as_dict=1)
    return active_cl


def get_cl_attendance(employee, filters):
    cl_attendance = frappe.db.sql("""select in_time,out_time,total_working_hours from `tabAttendance` where \
        status = 'Present' and employee= %s and attendance_date=%s""", (employee, filters.get("date")), as_dict=1)
    return cl_attendance


def get_ts(employee, filters):
    emp_ts = frappe.db.sql("""select total_hours as count from `tabTimesheet` where \
        docstatus = 1 and employee= %s and start_date between %s and %s""", (employee, filters.get("from_date"), filters.get("to_date")), as_dict=1)
    return emp_ts
