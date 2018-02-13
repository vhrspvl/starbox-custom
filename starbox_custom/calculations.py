# -*- coding: utf-8 -*-
# Copyright (c) 2017, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
import time
from frappe.utils.data import today, get_timestamp
from frappe.utils import getdate, cint, add_months, date_diff, add_days, flt, nowdate, \
    get_datetime_str, cstr, get_datetime, time_diff, time_diff_in_seconds
from datetime import datetime, timedelta


@frappe.whitelist()
def create_ts(doc, method):
    if doc.in_time and doc.out_time:
        emp_type = frappe.db.get_value(
            "Employee", doc.employee, "employment_type")
        ot_hours = calculate_hours(doc.in_time, doc.out_time, doc.employee)
        if ot_hours:
            from_time = str(doc.attendance_date) + " " + doc.in_time
            from_time_f = datetime.strptime(
                from_time, '%Y-%m-%d %H:%M:%S')
            to_time = str(doc.attendance_date) + " " + doc.out_time
            to_time_f = datetime.strptime(
                to_time, '%Y-%m-%d %H:%M:%S')
            ts_id = frappe.db.get_value(
                "Timesheet", {"employee": doc.employee, "start_date": doc.attendance_date, "end_date": doc.attendance_date})
            if ts_id:
                ts = frappe.get_doc("Timesheet", ts_id)
                ts.update({
                    "company": doc.company,
                    "employee": doc.employee,
                    "start_date": doc.attendance_date,
                    "end_date": doc.attendance_date,
                })
                ts.time_logs[0].activity_type = "OT"
                ts.time_logs[0].hours = flt(ot_hours / 3600)
                ts.time_logs[0].from_time = from_time_f
                ts.time_logs[0].to_time = to_time_f
                ts.save(ignore_permissions=True)
                if emp_type == 'Contract':
                    ts.submit()
                frappe.db.commit
            else:
                ts = frappe.new_doc("Timesheet")
                ts.company = doc.company
                ts.employee = doc.employee
                ts.start_date = doc.attendance_date
                ts.end_date = doc.attendance_date
                ts.append("time_logs", {
                    "activity_type": "OT",
                    "hours": flt(ot_hours / 3600),
                    "from_time": from_time_f,
                    "to_time": to_time_f
                })
                ts.insert()
                ts.save(ignore_permissions=True)
                if emp_type == 'Contract':
                    ts.submit()
                frappe.db.commit


def calculate_hours(in_time, out_time, employee):
    working_hrs = frappe.db.get_value("Employee", employee, "working_hours")
    shift_hrs = working_hrs.seconds
    in_time_f = datetime.strptime(
        in_time, '%H:%M:%S')
    out_time_f = datetime.strptime(
        out_time, '%H:%M:%S')
    worked_hrs = time_diff_in_seconds(
        out_time_f, in_time_f)
    overtime = cint(worked_hrs - shift_hrs)
    # overtime_f = datetime.strptime(
    #     overtime, '%H:%M:%S')
    min_hr = timedelta(seconds=3600)
    ot_f = timedelta(seconds=overtime)
    if ot_f > min_hr:
        return ot_f.seconds


# if ot_hours:
#             # from_time = doc.attendance_date + " " + doc.in_time
#             # frappe.errprint(type(from_time))
#             ts = frappe.new_doc("Timesheet")
#             ts.company = doc.company
#             ts.employee = doc.employee
#             ts.start_date = doc.attendance_date
#             ts.end_date = doc.attendance_date
#             ts.append("time_logs", {
#                 "activity_type": "OT",
#                 "hours": ot_hours
#                 # "from_time": from_time,
#                 # "to_time": doc.attendance_date + " " + doc.out_time
#             })
#             ts.insert()
#             ts.save(ignore_permissions=True)
