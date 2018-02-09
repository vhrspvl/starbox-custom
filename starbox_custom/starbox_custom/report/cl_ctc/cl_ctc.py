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
    grand_earnings = 0
    grand_totals = 0
    active_cl = get_active_cl()
    for cl in active_cl:
        row = [cl.name, cl.employee_name, cl.contractor, cl.employment_type]
        cl_present_days = get_cl_attendance(cl.name, filters)
        cl_ot_hours = get_ts(cl.name, filters)
        for present in cl_present_days:
            present_days = present.count
        if cl_present_days:
            row += [present_days]
        else:
            row += ["0"]

        ctc = frappe.db.get_value("Contractor", {'name': cl.contractor}, [
            'ctc_per_day'], as_dict=True)
        if ctc:
            ctc_day = ctc.ctc_per_day
            if ctc_day:
                row += [ctc_day]
                total_earnings = 0
                if present_days > 0:
                    earned_ctc = flt(ctc_day) * flt(present_days)
                    if earned_ctc:
                        row += [earned_ctc]
                        total_earnings += earned_ctc
                        grand_earnings += earned_ctc
        for hour in cl_ot_hours:
            present_hours = hour.count
        if cl_ot_hours:
            row += [present_hours]
        else:
            row += ["0"]
        ot = frappe.db.get_value("Contractor", {'name': cl.contractor}, [
            'ot_per_hour'], as_dict=True)
        if ot:
            ot_day = ot.ot_per_hour
            if ot_day:
                row += [ot_day]
                if present_hours > 0:
                    earned_ot = flt(ot_day) * flt(present_hours)
                    if earned_ot:
                        row += [earned_ot]
                        total_earnings += earned_ot
                if total_earnings:
                    grand_totals += total_earnings
                    row += [total_earnings]

        totals = ["Totals", "", "", "", "", "",
                  grand_earnings, "", "", "", grand_totals]
        data.append(row)
    data.append(totals)

    return columns, data


def get_columns(attendance):
    columns = [
        _("Employee") + ":Link/Employee:90",
        _("Employee Name") + ":Data:150",
        _("Contractor") + ":Data:180",
        _("Employment Type") + ":Data:180",
        _("PD") + ":Int:50",
        _("CTC Per Day") + ":Currency:100",
        _("Earned CTC") + ":Currency:100",
        _("OT Hours ") + ":Data:50",
        _("OT Cost") + ":Currency:50",
        _("OT Earnings") + ":Currency:50",
        _("Total Earnings") + ":Currency:100"

    ]
    return columns


def get_active_cl():
    active_cl = frappe.db.sql(
        """select emp.name,emp.employee_name,emp.contractor,emp.employment_type from `tabEmployee` emp where emp.status = "Active" and emp.employment_type="Contract" order by emp.name""", as_dict=1)
    return active_cl


def get_cl_attendance(employee, filters):
    cl_attendance = frappe.db.sql("""select count(*) as count from `tabAttendance` where \
        docstatus = 1 and status = 'Present' and employee= %s and attendance_date between %s and %s""", (employee, filters.get("from_date"), filters.get("to_date")), as_dict=1)
    return cl_attendance


def get_ts(employee, filters):
    emp_ts = frappe.db.sql("""select total_hours as count from `tabTimesheet` where \
        docstatus = 1 and employee= %s and start_date between %s and %s""", (employee, filters.get("from_date"), filters.get("to_date")), as_dict=1)
    return emp_ts
