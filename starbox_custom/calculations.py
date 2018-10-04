# -*- coding: utf-8 -*-
# Copyright (c) 2017, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
import time
import math,calendar
from dateutil.parser import parse
from frappe.utils.data import today, get_timestamp
from frappe.utils import getdate, cint, add_months, date_diff, add_days, flt, nowdate, \
    get_datetime_str, cstr, get_datetime, time_diff, time_diff_in_seconds, time_diff_in_hours
from datetime import datetime, timedelta
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
from frappe.core.doctype.sms_settings.sms_settings import send_sms


@frappe.whitelist()
def create_ts_submit(doc, method):
    if doc.in_time and doc.out_time:
        employee = frappe.get_doc("Employee", doc.employee)
        if employee.employment_type == 'Operator':
            ot_hours = calculate_hours(
                doc.in_time, doc.out_time, doc.employee)
            if ot_hours:
                from_date = doc.attendance_date
                to_date = doc.out_date
                from_time = str(from_date) + " " + doc.in_time
                # extra_hours = doc.total_working_hours - \
                #     ((employee.working_hours).seconds // 3600)
                from_time_f = datetime.strptime(
                    from_time, '%Y-%m-%d %H:%M:%S') + timedelta(hours=((employee.working_hours).seconds // 3600))
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

    # year = datetime.now().year
    # month = datetime.now().month
    # num_days = calendar.monthrange(year, month)[1]
    # print num_days
    # days1 = [datetime.date(year, month, day) for day in range(1, num_days+1)]
    # for day1 in days1:
    #     print day1
    
    # days = ["2018-09-01", "2018-09-02", "2018-09-03", "2018-09-04","2018-09-05", "2018-09-06",
    #         "2018-09-07", "2018-09-08", "2018-09-09", "2018-09-10", "2018-09-11", "2018-09-12", "2018-09-13",
    #         "2018-09-14", "2018-09-15", "2018-09-16", "2018-09-17", "2018-09-18", "2018-09-19", "2018-09-20","2018-09-21","2018-09-22","2018-09-23","2018-09-24","2018-09-25","2018-09-26","2018-09-27","2018-09-28","2018-09-29"]
    # for day in days:

@frappe.whitelist()
def create_ts():
    # days = ["2018-09-01", "2018-09-02", "2018-09-03", "2018-09-04","2018-09-05", "2018-09-06",
    #         "2018-09-07", "2018-09-08", "2018-09-09", "2018-09-10", "2018-09-11", "2018-09-12", "2018-09-13",
    #         "2018-09-14", "2018-09-15", "2018-09-16", "2018-09-17", "2018-09-18", "2018-09-19", "2018-09-20","2018-09-21","2018-09-22","2018-09-23","2018-09-24","2018-09-25","2018-09-26","2018-09-27","2018-09-28","2018-09-29","2018-09-30"]
    day = add_days(today(), -1)
    # day = "2018-09-01"
    # for day in days:
    attendance = frappe.get_all("Attendance", fields=[
                                'name', 'employee', 'attendance_date', 'out_date', 'in_time', 'out_time', 'total_working_hours'], filters={'attendance_date': day})
    for doc in attendance:
        if doc.attendance_date and doc.out_date and doc.in_time and doc.out_time:
            employee = frappe.get_doc("Employee", doc.employee)
            if employee.employment_type == 'Operator':
                ot_hours = calculate_hours(
                    doc.attendance_date, doc.out_date, doc.in_time, doc.out_time, doc.employee)
                if ot_hours:
                    from_date = doc.attendance_date
                    to_date = doc.out_date
                    from_time = str(from_date) + " " + doc.in_time
                    from_time_f = datetime.strptime(
                        from_time, '%Y-%m-%d %H:%M:%S') + timedelta(hours=((employee.working_hours).seconds // 3600))
                    to_time = str(to_date) + " " + doc.out_time
                    to_time_f = datetime.strptime(
                        to_time, '%Y-%m-%d %H:%M:%S')
                    timediff = to_time_f - from_time_f
                    dt = parse(str(timediff))
                    if dt.minute < 25:
                        ot = math.floor(ot_hours)
                    if dt.minute in range(25,45): 
                        ot = dt.hour + 0.5
                    if dt.minute > 45:    
                        ot = math.ceil(ot_hours)
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
                        ts.time_logs[0].hours = ot
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
                            "hours": ot,
                            "from_time": from_time_f,
                            "to_time": to_time_f
                        })
                        ts.insert()
                        ts.save(ignore_permissions=True)
                        frappe.db.commit()

def calculate_hours(in_date, out_date, in_time, out_time, employee):
    working_hrs = frappe.db.get_value("Employee", employee, "working_hours")
    if working_hrs:
        shift_hrs = working_hrs.seconds
        in_time_f = datetime.strptime(
            in_time, '%H:%M:%S')
        out_time_f = datetime.strptime(
            out_time, '%H:%M:%S')

        if in_date < out_date:
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
            return (ot_f.seconds / 3600.00)

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
        counr = ['8939837002']
    # send_st += l["total_leave_days"]
    return count

@frappe.whitelist()
def send_message():
    day = add_days(today(), -1)
    query = """select department as Department,count(*) as Count from `tabAttendance` where attendance_date = '%s' group by department""" % day
    att = frappe.db.sql(query, as_dict=1)
    if att:
        message = "DEPTWISE PRESENT COUNT - %s " % frappe.utils.formatdate(day)
        for at in att:
            message += "%(Department)s : %(Count)s\n" % at
        number = ['8939837002']
        send_sms(number, message)

def floor_dt(dt):
    nsecs = dt.minute*60+dt.second+dt.microsecond*1e-6
    delta = math.floor(nsecs / 900) * 900 - nsecs
    return dt + timedelta(seconds=delta)


def ceil_dt(dt):
    nsecs = dt.minute*60 + dt.second + dt.microsecond*1e-6
    delta = math.ceil(nsecs / 900) * 900 - nsecs
    return dt + timedelta(seconds=delta)


@frappe.whitelist()
def bulk_total_working_hours():
    # days = ["2018-07-01", "2018-07-02", "2018-07-03", "2018-07-04", "2018-07-06",
    #         "2018-07-07", "2018-07-08", "2018-07-09", "2018-07-10", "2018-07-11", "2018-07-12", "2018-07-13",
    #         "2018-07-14", "2018-07-15", "2018-07-16", "2018-07-17", "2018-07-18", "2018-07-19", "2018-07-20"]
    days = ["2018-07-22"]
    # # day = datetime.strptime('25042018', "%d%m%Y").date()
    for day in days:
        attendance = frappe.get_all("Attendance", fields=[
            'name', 'employee', 'attendance_date', 'out_date', 'in_time', 'out_time', 'total_working_hours'], filters={'attendance_date': day})
        for doc in attendance:
            if doc.attendance_date and doc.out_date and doc.in_time and doc.out_time:
                in_time_f = datetime.strptime(
                    doc.in_time, '%H:%M:%S')
                out_time_f = datetime.strptime(
                    doc.out_time, '%H:%M:%S')
                maxhr = timedelta(seconds=2400)
                actual_working_hours = frappe.db.get_value(
                    "Employee", doc.employee, "working_hours")
                td = (out_time_f - in_time_f)-actual_working_hours
                if actual_working_hours > (out_time_f - in_time_f):
                    td = (out_time_f - in_time_f)
                if doc.attendance_date < doc.out_date:
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


def round_dt(dt, dttype):
    # how many secs have passed this hour
    nsecs = dt.minute*60 + dt.second + dt.microsecond*1e-6
    # number of seconds to next quarter hour mark
    # Non-analytic (brute force is fun) way:
    #   delta = next(x for x in xrange(0,3601,900) if x>=nsecs) - nsecs
    # analytic way:
    if dttype == 'out':
        delta = math.floor(nsecs / 1800) * 1800 - nsecs
    else:
        delta = math.ceil(nsecs / 1800) * 1800 - nsecs
    # time + number of seconds to quarter hour mark.
    return dt + timedelta(seconds=delta)


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

@frappe.whitelist()
def clc_calculator():
    # day = (today(), -1)
    days = ["2018-09-18","2018-09-19"]
    for day in days:
        attendance_list = frappe.get_list("Attendance", fields=['name', 'employee', 'employee_name', 'employment_type', 'in_time', 'out_time',
                                                            'total_working_hours', 'department', 'contractor', 'attendance_date'], filters={"attendance_date": day, "status": "Present", "employment_type": "Contract"})
    for attendance in attendance_list:
        ctc_per_day = 0
        ot_earnings = 0
        actual_hours = 0
        ot_hours = 0
        ot_cost = 0
        total = 0
        earned_ctc = 0
        if attendance.in_time and attendance.out_time:
            att = frappe.get_doc("Attendance", attendance['name'])
            ctc_per_day = frappe.get_value(
                "Employee", attendance["employee"], "cost")
            # print (ctc_per_day)
            working_hours = frappe.db.get_value(
                "Employee", attendance['employee'], 'working_hours')
            actual_working_hours = (working_hours.seconds / 3600.00)
        if ctc_per_day:
            total_working_hours = att.total_working_hours
            if total_working_hours > 0:
                earned_ctc = flt(total_working_hours *
                                 (ctc_per_day / actual_working_hours))
            if total_working_hours > actual_working_hours:
                ot_hours = total_working_hours - actual_working_hours
                earned_ctc = flt((total_working_hours - ot_hours) *
                                 (ctc_per_day / actual_working_hours))
                ot_cost = (ctc_per_day / actual_working_hours)
                ot_earnings = flt(ot_hours * ot_cost)
        total = earned_ctc + ot_earnings
        clc = frappe.new_doc("Contract Labour Costing")
        clc.update({
            "attendance_id": att.name,
            "employee": att.employee,
            "employee_name": att.employee_name,
            "employment_type": att.employment_type,
            "attendance_date": att.attendance_date,
            "department": att.department,
            "in_time": att.in_time,
            "out_time": att.out_time,
            "total_working_hours": att.total_working_hours,
            "actual_working_hours": actual_working_hours,
            "contractor": att.contractor,
            "ctc_per_day": ctc_per_day,
            "earned_ctc": earned_ctc,
            "ot_hours": ot_hours,
            "ot_cost": ot_cost,
            "ot_earnings": ot_earnings,
            "total": round(flt(total)),
        })
        clc.save(ignore_permissions=True)




    # try:
    #     time.strptime(doc.in_time, '%H:%M:%S')
    #     return True
    # except ValueError:
    #     frappe.msgprint(_('Kindly check the in time format'))
