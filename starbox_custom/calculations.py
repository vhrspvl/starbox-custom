# -*- coding: utf-8 -*-
# Copyright (c) 2017, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
import time
import math
from frappe.utils.data import today, get_timestamp
from frappe.utils import getdate, cint, add_months, date_diff, add_days, flt, nowdate, \
    get_datetime_str, cstr, get_datetime, time_diff, time_diff_in_seconds
from datetime import datetime, timedelta
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee


@frappe.whitelist()
def create_ts():
    day = add_days(today(), -1)
    # day = datetime.strptime('25042018', "%d%m%Y").date()
    attendance = frappe.get_all("Attendance", fields=[
                                'name', 'employee', 'attendance_date', 'in_time', 'out_time'], filters={'attendance_date': day})
    for doc in attendance:
        if doc.in_time and doc.out_time:
            employee = frappe.get_doc("Employee", doc.employee)
            if employee.employment_type == 'Operator':
                ot_hours = calculate_hours(
                    doc.in_time, doc.out_time, doc.employee)
                if ot_hours:
                    from_date = doc.attendance_date
                    if doc.out_time <= doc.in_time:
                        to_date = add_days(doc.attendance_date, -1)
                    else:
                        to_date = doc.attendance_date
                    from_time = str(from_date) + " " + doc.in_time
                    from_time_f = datetime.strptime(
                        from_time, '%Y-%m-%d %H:%M:%S')
                    to_time = str(to_date) + " " + doc.out_time
                    to_time_f = datetime.strptime(
                        to_time, '%Y-%m-%d %H:%M:%S')
                    ts_id = frappe.db.get_value(
                        "Timesheet", {"employee": doc.employee, "start_date": from_date, "end_date": to_date})
                    if ts_id:
                        ts = frappe.get_doc("Timesheet", ts_id)
                        ts.update({
                            "company": doc.company,
                            "employee": doc.employee,
                            "start_date": from_date,
                            "end_date": to_date,
                        })
                        ts.time_logs[0].activity_type = "OT"
                        ts.time_logs[0].hours = flt(ot_hours / 3600)
                        ts.time_logs[0].from_time = from_time_f
                        ts.time_logs[0].to_time = to_time_f
                        ts.save(ignore_permissions=True)
                        frappe.db.commit()
                    else:
                        ts = frappe.new_doc("Timesheet")
                        ts.company = doc.company
                        ts.employee = doc.employee
                        ts.start_date = from_date
                        ts.end_date = to_date
                        ts.append("time_logs", {
                            "activity_type": "OT",
                            "hours": flt(ot_hours / 3600),
                            "from_time": from_time_f,
                            "to_time": to_time_f
                        })
                        ts.insert()
                        ts.save(ignore_permissions=True)
                        frappe.db.commit()


def calculate_hours(in_time, out_time, employee):
    working_hrs = frappe.db.get_value("Employee", employee, "working_hours")
    if working_hrs:
        shift_hrs = working_hrs.seconds
        in_time_f = datetime.strptime(
            in_time, '%H:%M:%S')
        out_time_f = datetime.strptime(
            out_time, '%H:%M:%S')

        if out_time_f <= in_time_f:
            next_day = timedelta(hours=24)
            worked_hrs = time_diff_in_seconds(
                out_time_f + next_day, in_time_f)
        else:
            worked_hrs = time_diff_in_seconds(
                out_time_f, in_time_f)
        overtime = cint(worked_hrs - shift_hrs)
        # overtime_f = datetime.strptime(
        #     overtime, '%H:%M:%S')
        min_hr = timedelta(seconds=3600)
        ot_f = timedelta(seconds=overtime)
        if ot_f > min_hr:
            return ot_f.seconds


def calculate_present_days(doc, method):
    present_days = 0
    holidays = get_holidays_for_employee(doc.employee,
                                         doc.start_date, doc.end_date)
    employee_attendance = frappe.db.sql("""select name,attendance_date from `tabAttendance` where \
        docstatus = 1 and status = 'Present' and employee= %s and attendance_date between %s and %s""", (doc.employee, doc.start_date, doc.end_date), as_dict=1)
    present_days = len(employee_attendance)
    for present in employee_attendance:
        if (present["attendance_date"].strftime('%Y-%m-%d')) in holidays:
            present_days -= 1
    doc.present_days = present_days
    doc.holidays = len(holidays)
    leave = get_leave(doc.employee,
                      doc.start_date, doc.end_date)
    doc.leaves_availed = leave


def get_holidays_for_employee(emp, start_date, end_date):
    holiday_list = get_holiday_list_for_employee(emp)
    holidays = frappe.db.sql_list('''select holiday_date from `tabHoliday`
        where
            parent=%(holiday_list)s
            and holiday_date >= %(start_date)s
            and holiday_date <= %(end_date)s''', {
        "holiday_list": holiday_list,
        "start_date": start_date,
        "end_date": end_date
    })

    holidays = [cstr(i) for i in holidays]

    return holidays


def get_leave(emp, start_date, end_date):
    count = 0
    leave = frappe.db.sql('''select name,total_leave_days from `tabLeave Application`
        where
            employee=%(emp)s
            and from_date >= %(start_date)s
            and to_date <= %(end_date)s
            and leave_type !='Leave without Pay'
            ''', {
        "emp": emp,
        "start_date": start_date,
        "end_date": end_date
    }, as_dict=1)

    for l in leave:
        count += l["total_leave_days"]
    return count


def total_working_hours(doc, method):
    if doc.in_time:
        in_time_f = datetime.strptime(
            doc.in_time, '%H:%M:%S')
        out_time_f = datetime.strptime(
            doc.out_time, '%H:%M:%S')
        worked_hrs = time_diff_in_seconds(
            out_time_f, in_time_f)
        att = frappe.get_doc("Attendance", doc.name)
        att.update({
            "total_working_hours": math.ceil(worked_hrs / 60 / 60)
        })
        att.db_update()
        frappe.db.commit()


@frappe.whitelist()
def daily_punch_record():
    from zk import ZK, const
    conn = None
    zk = ZK('192.168.10.65', port=4370, timeout=5)
    try:
        conn = zk.connect()
        attendance = conn.get_attendance()
        curdate = datetime.now().date()
        for att in attendance:
            # if att.user_id == '170':
            date = att.timestamp.date()
            if date == curdate:
                mtime = att.timestamp.time()
                userid = att.user_id
                employee = frappe.db.get_value("Employee", {
                    "employee_no": userid, "status": "Active"})
                if employee:
                    doc = frappe.get_doc("Employee", employee)
                    pr_id = frappe.db.get_value("Punch Record", {
                        "employee": employee, "attendance_date": date})
                if pr_id:
                    pr = frappe.get_doc("Punch Record", pr_id)
                    pr.append("timetable", {
                        "punch_time": str(mtime)
                    })
                    pr.save(ignore_permissions=True)
                else:
                    pr = frappe.new_doc("Punch Record")
                    pr.employee = employee
                    pr.employee_name = doc.employee_name
                    pr.attendance_date = date
                    pr.append("timetable", {
                        "punch_time": mtime
                    })
                    pr.insert()
                    pr.save(ignore_permissions=True)
    except Exception, e:
        print "Process terminate : {}".format(e)
    finally:
        if conn:
            conn.disconnect()


@frappe.whitelist()
def punch_record(att_date):
    from zk import ZK, const
    conn = None
    zk = ZK('192.168.1.65', port=4370, timeout=5)
    try:
        conn = zk.connect()
        attendance = conn.get_attendance()
        for att in attendance:
            # if att.user_id == '170':
            date = att.timestamp.date()
            if date == att_date:
                mtime = att.timestamp.time()
                userid = att.user_id
                employee = frappe.db.get_value("Employee", {
                    "employee_no": userid, "status": "Active"})
                if employee:
                    doc = frappe.get_doc("Employee", employee)
                    pr_id = frappe.db.get_value("Punch Record", {
                        "employee": employee, "attendance_date": date})
                if pr_id:
                    pr = frappe.get_doc("Punch Record", pr_id)
                    pr.append("timetable", {
                        "punch_time": str(mtime)
                    })
                    pr.save(ignore_permissions=True)
                else:
                    pr = frappe.new_doc("Punch Record")
                    pr.employee = employee
                    pr.employee_name = doc.employee_name
                    pr.attendance_date = date
                    pr.append("timetable", {
                        "punch_time": mtime
                    })
                    pr.insert()
                    pr.save(ignore_permissions=True)
                    frappe.response.type = "text"
                    return "ok"
    except Exception, e:
        return "Process terminate : {}".format(e)
    finally:
        if conn:
            conn.disconnect()


@frappe.whitelist()
def markshift():
    attendances = frappe.get_all("Attendance", fields=['name', 'status', 'in_time'], filters={
        'status': 'Present'})
    a_min_time = datetime.strptime('07:30', '%H:%M')
    a_max_time = datetime.strptime('09:30', '%H:%M')
    b_min_time = datetime.strptime('19:30', '%H:%M')
    b_max_time = datetime.strptime('21:30', '%H:%M')
    for att in attendances:
        if att.in_time:
            intime = datetime.strptime(att.in_time, '%H:%M:%S')
            if intime >= a_min_time and intime <= a_max_time:
                shift = "A"
            elif intime >= b_min_time and intime <= b_max_time:
                shift = "B"
            else:
                shift = "General"
            attendance = frappe.get_doc("Attendance", att)
            attendance.update({
                "shift": shift
            })
            attendance.db_update()
            frappe.db.commit()


@frappe.whitelist()
def markattfrompr():
    date = datetime.strptime('18042018', "%d%m%Y").date()
    employee = frappe.get_list("Employee", filters={"status": "Active"})
    for emp in employee:
        pr_id = frappe.db.get_value(
            "Punch Record", {"employee": emp["name"], "attendance_date": date})
        if pr_id:
            pr = frappe.get_doc("Punch Record", pr_id)
            prt = frappe.get_doc("Punch Time", max(pr.time_table))
            print prt
