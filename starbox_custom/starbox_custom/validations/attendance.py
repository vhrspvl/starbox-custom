# -*- coding: utf-8 -*-
# Copyright (c) 2017, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
import frappe
from frappe import _
import time
import math
from frappe.utils.data import today, get_timestamp
from frappe.utils import getdate, cint, add_months, date_diff, add_days, flt, nowdate, \
    get_datetime_str, cstr, get_datetime, time_diff, time_diff_in_seconds, time_diff_in_hours
from datetime import datetime, timedelta

def onsubmit(doc,method):
    removelop(doc, method)
    total_working_hours(doc, method)
    removedoublepunch(doc,method)

def updateaftersubmit(doc, method):
    removelop(doc, method)
    total_working_hours(doc, method)
    removedoublepunch(doc,method)


def total_working_hours(doc, method):
    if doc.in_time and doc.out_time:
        in_time_f = datetime.strptime(
            doc.in_time, '%H:%M:%S')
        out_time_f = datetime.strptime(
            doc.out_time, '%H:%M:%S')
        frappe.errprint(type(doc.attendance_date))
        frappe.errprint(type(doc.out_date))
        actual_working_hours = frappe.db.get_value(
            "Employee", doc.employee, "working_hours")
        td = (out_time_f - in_time_f) - actual_working_hours
        if actual_working_hours > (out_time_f - in_time_f):
            td = (out_time_f - in_time_f)
        if doc.out_date > doc.attendance_date:
            next_day = timedelta(hours=24)
            worked_hrs = time_diff_in_seconds(
                out_time_f + next_day, in_time_f)
        else:
            worked_hrs = time_diff_in_seconds(
                out_time_f, in_time_f)
        total_working_hours = (worked_hrs / 3600.00)
        if td.seconds >= 2700:
            total_working_hours = math.ceil(total_working_hours)
        else:
            total_working_hours = math.floor(total_working_hours)
        att = frappe.get_doc("Attendance", doc.name)
        att.update({
            "total_working_hours": total_working_hours
        })
        att.db_update()
        frappe.db.commit()


def removelop(doc, method):
    if doc.status == 'Present' or doc.status == 'On Duty' or doc.status == 'Late':
        lop = frappe.get_list("Leave Application", filters={
            'from_date': doc.attendance_date, 'to_date': doc.attendance_date, 'employee': doc.employee, 'leave_type': 'Leave without Pay'})
        for l in lop:
            lop = frappe.get_doc("Leave Application", l)
            if lop.leave_type == 'Leave Without Pay':
                lop.db_set("docstatus", "Cancelled")
                frappe.delete_doc("Leave Application", lop.name)
                frappe.db.commit()
    elif doc.status == 'Absent':
        day = doc.attendance_date
        leave_approvers = [l.leave_approver for l in frappe.db.sql("""select leave_approver from `tabEmployee Leave Approver` where parent = %s""",
                                                                   (doc.employee), as_dict=True)]
        lap = frappe.new_doc("Leave Application")
        lap.leave_type = "Leave Without Pay"
        lap.status = "Approved"
        lap.follow_via_email = 0
        lap.description = "Absent Auto Marked"
        lap.from_date = day
        lap.to_date = day
        lap.employee = doc.employee
        if leave_approvers:
            lap.leave_approver = leave_approvers[0]
        else:
            lap.leave_approver = "Administrator"
        lap.posting_date = day
        lap.company = frappe.db.get_value(
            "Employee", doc.employee, "company")
        lap.save(ignore_permissions=True)
        lap.submit()
        frappe.db.commit()

@frappe.whitelist()
def removedoublepunch(doc,method):
    if doc.in_time and doc.out_time:
        if doc.in_time == doc.out_time:
            att = frappe.get_doc("Attendance",doc.name)
            att.update({
            "out_time": ""
                })  
            att.db_update()
            frappe.db.commit()