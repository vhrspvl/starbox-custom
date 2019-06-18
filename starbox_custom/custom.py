# -*- coding: utf-8 -*-
# Copyright (c) 2017, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _
from frappe.utils.data import today
from frappe.utils import formatdate, getdate, cint, add_months, date_diff, add_days, flt, cstr, time_diff, time_diff_in_seconds, time_diff_in_hours, today
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
import requests
import math



@frappe.whitelist()
def bulk_update_in_biometric_machine():
    employees = frappe.get_list("Employee", filters={"status": "Active","employment_type":("not in",["Operator","Contract","Staff"])}, fields=["biometric_id","employee_name"])
    for emp in employees:
        empid = frappe.get_doc("Employee",emp)
        print empid.employment_type
        uid = emp.biometric_id
        uname = emp.employee_name
        stgids = frappe.db.get_all("Service Tag")
        for stgid in stgids:
            url = "http://robot.camsunit.com/external/1.0/user/add?uid=%s&uname=%s&stgid=%s" % (
                uid, uname, stgid.name)
            r = requests.post(url)
            print r.content



@frappe.whitelist()
def update_in_biometric_machine(uid, uname):
    stgids = frappe.db.get_all("Service Tag")
    for stgid in stgids:
        url = "http://robot.camsunit.com/external/1.0/user/add?uid=%s&uname=%s&stgid=%s" % (
            uid, uname, stgid.name)
        r = requests.post(url)
        frappe.errprint(r.content)
    return r.content



@frappe.whitelist()
def delete_from_biometric_machine(uid, uname):
    left_employee = frappe.get_doc("Employee", uid)
    # for l in left_employees:
    stgids = frappe.db.get_all("Service Tag")
    for stgid in stgids:
        url = "http://robot.camsunit.com/external/1.0/user/delete?uid=%s&stgid=%s" % (
            uid, stgid.name)
        r = requests.post(url)
    return r.content

@frappe.whitelist()
def delete_bulk():
    left_employees = frappe.get_list(
        "Employee", fields=["biometric_id", "name"], filters={"status": "Left"}, limit=1)
    for l in left_employees:
        stgids = frappe.db.get_all("Service Tag")
        for stgid in stgids:
            uid = l.biometric_id
            url = "http://robot.camsunit.com/external/1.0/user/delete?uid=%s&stgid=%s" % (
                uid, stgid.name)
            print url
            r = requests.post(url)
            print r.content


@frappe.whitelist()
def get_employee_attendance(doc, method):
    employee_attendance = frappe.db.sql("""select count(*) as count from `tabAttendance` where \
                                            docstatus = 1 and status = 'Present' and employee= %s and attendance_date between %s and %s""", (doc.employee, doc.start_date, doc.end_date), as_dict=1)
    return employee_attendance


def get_active_cl():
    active_cl = frappe.db.sql(
        """select emp.name,emp.employee_name,emp.contractor,emp.employment_type from `tabEmployee` emp where emp.status = "Active" and emp.employment_type="Contract" order by emp.name""", as_dict=1)
    return active_cl


@frappe.whitelist()
def send_daily_report():
    custom_filter = {'date': add_days(today(), -1)}
    report = frappe.get_doc('Report', "Employee Day Attendance Report")
    columns, data = report.get_data(
        limit=500 or 500, filters=custom_filter, as_dict=True)
    html = frappe.render_template(
        'frappe/templates/includes/print_table.html', {'columns': columns, 'data': data})
    frappe.sendmail(
        recipients=['hari@starboxes.in',
                    'hr@starboxes.in', 'thiru@starboxes.in'],
        subject='Employee Attendance Report - ' +
        formatdate(add_days(today(), -1)),
        message=html
    )


@frappe.whitelist()
def removeduplicatepunch():
    # day = '2019-04-10'
    day = today()
    get_att = frappe.db.sql("""SELECT name FROM `tabPunch Record` WHERE attendance_date = %s GROUP BY employee
                    HAVING COUNT(employee) >1""", (day), as_dict=1)

    if get_att:
        for att in get_att:
            obj = frappe.get_doc("Punch Record", att["name"])
            frappe.delete_doc("Punch Record", obj.name)
            frappe.db.commit()
        removeduplicatepunch()


@frappe.whitelist()
def send_ctc_report():
    from_date = str(date.today() - relativedelta(months=1))
    to_date = add_days(today(), -1)
    # print type(from_date)
    custom_filter = {'from_date': from_date, 'to_date': to_date}
    report = frappe.get_doc('Report', "CTC Report")
    columns, data = report.get_data(
        limit=500 or 500, filters=custom_filter, as_dict=True)
    html = frappe.render_template(
        'frappe/templates/includes/print_table.html', {'columns': columns, 'data': data})
    msg = "Kindly find the attached CTC Report Dated From" + \
        formatdate(from_date) + " To " + formatdate(to_date)
    frappe.sendmail(
        recipients=['hari@starboxes.in',
                    'hr@starboxes.in', 'thiru@starboxes.in'],
        subject='CTC Report Upto - ' +
        formatdate(add_days(today(), -1)),
        message=msg + html
    )


@frappe.whitelist()
def calculate_total(doc, method):
    total, total_w = 0, 0
    for d in doc.get('personal_qualities'):
        if d.score:
            d.score_earned = flt(d.score) * flt(d.per_weightage) / 100
            total = total + d.score_earned
        total_w += flt(d.per_weightage)

    if int(total_w) != 100:
        frappe.throw(_("Total weightage assigned should be 100%. It is {0}").format(
            str(total_w) + "%"))

    if total == 0:
        frappe.throw(_("Total cannot be zero"))

    doc.total_score = total


@frappe.whitelist()
def mark_on_leave(doc, method):
    lap = frappe.get_doc("Leave Application", doc.name)
    if lap.status == 'Approved':
        if lap.leave_type == 'Leave Without Pay':
            status = 'Absent'
        else:
            status = "On Leave"
        attendances = frappe.db.sql("""select name,status from `tabAttendance`
                    where employee = %s and attendance_date between %s and %s
                and docstatus = 1""", (lap.employee, lap.from_date, lap.to_date), as_dict=True)
        if attendances:
            for attendance in attendances:
                att = frappe.get_doc("Attendance", attendance)
                att.update({
                    "status": status,
                    "leave_type": lap.leave_type
                })
                att.db_update()
                frappe.db.commit()


@frappe.whitelist()
def cancel_on_leave(doc, method):
    lap = frappe.get_doc("Leave Application", doc.name)
    attendances = frappe.db.sql("""select name,status from `tabAttendance`
                where employee = %s and attendance_date between %s and %s
            and docstatus = 1""", (lap.employee, lap.from_date, lap.to_date), as_dict=True)
    for attendance in attendances:
        att = frappe.get_doc("Attendance", attendance)
        if att.status == 'On Leave':
            att.update({
                "status": 'Absent',
            })
            att.db_update()
            frappe.db.commit()


@frappe.whitelist()
def removeduplicateatt():
    get_att = frappe.db.sql("""SELECT name FROM `tabAttendance` WHERE attendance_date = %s GROUP BY employee
                    HAVING COUNT(employee) >1""", (today()), as_dict=1)
    if get_att:
        for att in get_att:
            obj = frappe.get_doc("Attendance", att["name"])
            obj.db_set("docstatus", 2)
            frappe.delete_doc("Attendance", obj.name)
            frappe.db.commit()

# @frappe.whitelist()
# def removeduplicateatt():
#     for dt in daterange(date(2018, 12, 1), date(2018, 12, 31)):
#         day = dt
#         # day = add_days(today(), -1)
#         get_att = frappe.db.sql("""SELECT name FROM `tabAttendance` WHERE attendance_date = %s GROUP BY employee
#                         HAVING COUNT(employee) >1""", (day), as_dict=1)
#         if get_att:
#             for att in get_att:
#                 obj = frappe.get_doc("Attendance", att["name"])
#                 obj.db_set("docstatus", 2)
#                 frappe.delete_doc("Attendance", obj.name)
#                 frappe.db.commit()


# def daterange(date1, date2):
#     for n in range(int((date2 - date1).days)+1):
#         yield date1 + timedelta(n)


@frappe.whitelist()
def emp_absent_today():
    # day = add_days(today(), -1)
    # days = ["2018-09-03", "2018-09-04","2018-09-05", "2018-09-06",
    #         "2018-09-07", "2018-09-08", "2018-09-09", "2018-09-10", "2018-09-11", "2018-09-12", "2018-09-13",
    #         "2018-09-14", "2018-09-15", "2018-09-16", "2018-09-17", "2018-09-18", "2018-09-19", "2018-09-20","2018-09-21","2018-09-22","2018-09-23","2018-09-24","2018-09-25","2018-09-26","2018-09-27","2018-09-28","2018-09-29"]
    days = ["2018-09-30"]
    for day in days:
        query = """SELECT emp.name FROM `tabAttendance` att, `tabEmployee` emp
        WHERE att.employee = emp.name AND att.attendance_date = '%s'""" % (day)
        present_emp = frappe.db.sql(query, as_dict=True)
        pre_abs = False
        next_abs = False
        for emp in frappe.get_list('Employee', filters={'status': 'Active', 'employment_type': ('!=', 'Contract')}):
            joining_date = frappe.db.get_value(
                "Employee", emp, ["date_of_joining"])
            holiday = frappe.get_list("Holiday List", filters={
                'holiday_date': day})
            if datetime.strptime(day, '%Y-%m-%d').date() < joining_date:
                pass
            elif emp in present_emp:
                pass
            elif holiday:
                pre_day = frappe.db.get_value("Attendance", {
                    "employee": emp.name, "status": "Absent", "attendance_date": add_days(day, -1)})
                next_day = frappe.db.get_value("Attendance", {
                    "employee": emp.name, "status": "Absent", "attendance_date": add_days(day, 1)})
                if pre_day and next_day:
                    doc = frappe.get_doc('Employee', emp)
                    leave = get_leave(doc.name, day)
                    if leave:
                        status = 'On Leave'
                    else:
                        status = 'Absent'
                    attendance = frappe.new_doc("Attendance")
                    attendance.update({
                        "employee": doc.name,
                        "employee_name": doc.employee_name,
                        "attendance_date": day,
                        "status": status,
                        "company": doc.company
                    })
                    attendance.save(ignore_permissions=True)
                    attendance.submit()
                    frappe.db.commit()
            else:
                doc = frappe.get_doc('Employee', emp)
                leave = get_leave(doc.name, day)
                if leave:
                    status = 'On Leave'
                else:
                    status = 'Absent'
                attendance = frappe.new_doc("Attendance")
                attendance.update({
                    "employee": doc.name,
                    "employee_name": doc.employee_name,
                    "attendance_date": day,
                    "status": status,
                    "company": doc.company
                })
                attendance.save(ignore_permissions=True)
                attendance.submit()
                frappe.db.commit()


@frappe.whitelist()
def update_leave_application():
    # day = add_days(today(), -1)
    days = ["2018-09-01", "2018-09-02", "2018-09-03", "2018-09-04", "2018-09-05", "2018-09-06",
            "2018-09-07", "2018-09-08", "2018-09-09", "2018-09-10", "2018-09-11", "2018-09-12", "2018-09-13",
            "2018-09-14", "2018-09-15", "2018-09-16", "2018-09-17", "2018-09-18", "2018-09-19", "2018-09-20",
            "2018-09-21", "2018-09-22", "2018-09-23", "2018-09-24", "2018-09-25", "2018-09-26", "2018-09-27",
            "2018-09-28", "2018-09-29", "2018-09-30"]
    for day in days:
        employees = frappe.get_all(
            'Employee', filters={"status": "Active", 'employment_type': 'DET'})
        for employee in employees:
            lwp = get_leave(employee.name, day)
            if lwp:
                pass
            else:
                query = """SELECT emp.name FROM `tabAttendance` att, `tabEmployee` emp
                        WHERE att.employee = emp.name AND att.status = 'Absent' AND att.attendance_date = '%s'""" % (day)
                absent_emp = frappe.db.sql(query, as_dict=True)
                if employee in absent_emp:
                    leave_approvers = [l.leave_approver for l in frappe.db.sql("""select leave_approver from `tabEmployee Leave Approver` where parent = %s""",
                                                                               (employee.name), as_dict=True)]
                    lap = frappe.new_doc("Leave Application")
                    lap.leave_type = "Leave Without Pay"
                    lap.status = "Approved"
                    lap.follow_via_email = 0
                    lap.description = "Absent Auto Marked"
                    lap.from_date = day
                    lap.to_date = day
                    lap.employee = employee.name
                    if leave_approvers:
                        lap.leave_approver = leave_approvers[0]
                    else:
                        lap.leave_approver = "Administrator"
                    lap.posting_date = day
                    lap.company = frappe.db.get_value(
                        "Employee", employee.name, "company")
                    lap.save(ignore_permissions=True)
                    lap.submit()
                    frappe.db.commit()


def get_leave(emp, day):
    leave = frappe.db.sql("""select name from `tabLeave Application`
                where employee = %s and %s between from_date and to_date and docstatus = 1""", (emp, day), as_dict=1)
    return leave


@frappe.whitelist()
def mark_comp_off():
    day = add_days(today(), -1)
    from_date = add_days(day, 1)
    to_date = add_months(day, 1)
    query = """SELECT emp.name FROM `tabAttendance` att, `tabEmployee` emp
        WHERE att.employee = emp.name AND att.attendance_date = '%s'""" % (day)
    present_emp = frappe.db.sql(query, as_dict=True)

    for emp in frappe.get_list('Employee', filters={'status': 'Active', 'employment_type': ("=", "Staff")}):
        holidays = get_holidays_for_employee(emp.name, day)
        if emp in present_emp and day in holidays:
            lal_ids = get_lal(emp.name, day)
            if lal_ids:
                for lal_id in lal_ids:
                    lal = frappe.get_doc("Leave Allocation", lal_id['name'])
                    lal.new_leaves_allocated += 1.00
                    lal.total_leaves_allocated += 1.00
                    if lal.description:
                        lal.description += '<br>' + \
                            'Comp-off for {0}'.format(day)
                    else:
                        lal.description = '<br>' + \
                            'Comp-off for {0}'.format(day)

                    lal.db_update()
                    frappe.db.commit
            else:
                lal = frappe.new_doc("Leave Allocation")
                lal.employee = emp.name
                lal.leave_type = 'Compensatory Off'
                lal.from_date = from_date
                lal.to_date = to_date
                lal.new_leaves_allocated = 1
                lal.description = 'Comp-off for {0}'.format(day)
                lal.save(ignore_permissions=True)
                lal.submit()
                frappe.db.commit()


def get_lal(emp, day):
    lal = frappe.db.sql("""select name from `tabLeave Allocation`
                where employee = %s and %s between from_date and to_date and leave_type='Compensatory Off'
            and docstatus = 1""", (emp, day), as_dict=True)
    return lal


def get_holidays_for_employee(employee, day):
    holiday_list = get_holiday_list_for_employee(employee)
    holidays = frappe.db.sql_list('''select holiday_date from `tabHoliday`
            where
                parent=%(holiday_list)s
                and holiday_date >= %(start_date)s
                and holiday_date <= %(end_date)s''', {
        "holiday_list": holiday_list,
        "start_date": day,
        "end_date": day
    })

    holidays = [cstr(i) for i in holidays]

    return holidays


def get_active_emp():
    active_emp = frappe.db.sql(
        """select emp.working_hours from `tabEmployee` emp where emp.status = "Active" and emp.employment_type="Contract" order by emp.name""", as_dict=1)
    return active_emp


@frappe.whitelist()
def emp_ot():
    day = add_days(today(), -1)
    for day in days:
        holiday = frappe.get_list(
            "Holiday List", filters={'holiday_date': day})
        if holiday:
            attendance_list = frappe.get_list(
                "Attendance", filters={"attendance_date": day, "status": "Present", "employment_type": "Operator"})
            for attendance in attendance_list:
                att = frappe.get_doc("Attendance", attendance)
                from_time = str(att.attendance_date) + " " + att.in_time
                from_time_f = datetime.strptime(
                    from_time,  '%Y-%m-%d %H:%M:%S')
                to_time = str(att.attendance_date) + " " + att.out_time
                to_time_f = datetime.strptime(
                    to_time, '%Y-%m-%d %H:%M:%S')
                ts = frappe.new_doc("Timesheet")
                ts.company = att.company
                ts.employee = att.employee
                ts.start_date = att.attendance_date
                ts.end_date = att.attendance_date
                ts.note = "Holiday OT"
                ts.append("time_logs", {
                    "activity_type": "OT",
                    "hours": att.total_working_hours,
                    "from_time": from_time_f,
                    "to_time": to_time_f
                })
                ts.save(ignore_permissions=True)
                frappe.db.commit()


@frappe.whitelist()
def send_reference_mail(job_title, role):
    from frappe.utils.user import get_enabled_system_users
    users = None
    if not users:
        users = [u.email_id or u.name for u in get_enabled_system_users()]
        for u in users:
            frappe.sendmail(recipients=("ramya.a@voltechgroup.com"),
                            subject=_("New Job Opening"),
                            message=_("""Job Title:{0},
                                        Role Specification:{1}""").format(
                                job_title, role),
                            now=True)
        return "ok"
        # reply_to=e.company_email or e.personal_email or e.user_id)


@frappe.whitelist()
def update_comp_off(child):
    parts = child.split(",")
    for p in parts:
        la = frappe.get_doc("Leave Allocation", p)
        la.update({
            "leave_taken": 1
        })
        la.db_update()
        frappe.db.commit()


# @frappe.whitelist()
# def emp_sunday_attendance():

#     days = ['2018-07-01', '2018-07-08',
#             '2018-07-15', '2018-07-22', '2018-07-29']
#     for day in days:
#         attendance_list = frappe.get_list(
#             "Attendance", filters={"attendance_date": day, "status": "Present"})
#         for attendance in attendance_list:
#             att = frappe.get_doc("Attendance", attendance)
#             sunday_attendance = frappe.new_doc("Sunday Attendance")
#             sunday_attendance.update({
#                 "employee": att.employee,
#                 "employee_name": att.employee_name,
#                 "attendance_date": att.attendance_date,
#                 "in_time": att.in_time,
#                 "out_time": att.out_time,
#                 "total_working_hours": att.total_working_hours,
#                 "out_date": att.out_date,
#                 "status": att.status,
#                 "company": att.company
#             })
#             sunday_attendance.save(ignore_permissions=True)
#             sunday_attendance.submit()
#             frappe.db.commit()

# @frappe.whitelist()
# def bulk_mark_on_leave():
#     days = ["2018-05-01", "2018-05-02", "2018-05-03", "2018-05-04", "2018-05-05", "2018-05-06", "2018-05-07", "2018-05-08", "2018-05-09", "2018-05-10", "2018-05-11", "2018-05-12", "2018-05-13", "2018-05-14",
#             "2018-05-15", "2018-05-16", "2018-05-17", "2018-05-18", "2018-05-19", "2018-05-20", "2018-05-21", "2018-05-22", "2018-05-23", "2018-05-24", "2018-05-25", "2018-05-26", "2018-05-27", "2018-05-28", "2018-05-29", "2018-05-30", "2018-05-31"]
#     for day in days:
#         for emp in frappe.get_list('Employee', filters={'status': 'Active'}):
#             lop = frappe.get_list("Leave Application", filters={
#                 'from_date': day, 'to_date': day, 'employee': emp})
#             for l in lop:
#                 lap = frappe.get_doc("Leave Application", l)
#                 if lap.status == 'Approved':
#                     if lap.leave_type == 'Leave Without Pay':
#                         status = 'Absent'
#                     else:
#                         status = "On Leave"
#                         print status
#                     attendances = frappe.db.sql("""select name,status from `tabAttendance`
#                                 where employee = %s and attendance_date between %s and %s
#                             and docstatus = 1""", (lap.employee, lap.from_date, lap.to_date), as_dict=True)
#                     for attendance in attendances:
#                         att = frappe.get_doc("Attendance", attendance)
#                         att.update({
#                             "status": status,
#                             "leave_type": lap.leave_type
#                         })
#                         att.db_update()
#                         frappe.db.commit()
# @frappe.whitelist()
# def convert2present():
#     from_date = '2018-03-01'
#     to_date = '2018-03-31'
#     attendances = frappe.db.sql("""select name,status from `tabAttendance` where status='Late'
#     and attendance_date between %s and %s""", (from_date, to_date), as_dict=True)
#     print len(attendances)
#     for attendance in attendances:
#         att = frappe.get_doc("Attendance", attendance)
#         att.update({
#             "status": "Present"
#         })
#         att.save(ignore_permissions=True)
#         frappe.db.commit()

# @frappe.whitelist()
# def bulkremovelop():
#     employees = frappe.get_all('Employee', fields=['name'], filters={
#         "status": "Active", "employment_type": ("!=", "Contract")})
#     days = ["2018-04-01", "2018-04-02", "2018-04-03", "2018-04-04", "2018-04-05", "2018-04-06", "2018-04-07", "2018-04-08", "2018-04-09", "2018-04-10", "2018-04-11", "2018-04-12", "2018-04-13", "2018-04-14",
#             "2018-04-15", "2018-04-16", "2018-04-17", "2018-04-18", "2018-04-19", "2018-04-20", "2018-04-21", "2018-04-22", "2018-04-23", "2018-04-24", "2018-04-25", "2018-04-26", "2018-04-27", "2018-04-28", "2018-04-29", "2018-04-30"]
#     for day in days:
#         query = """SELECT emp.name FROM `tabAttendance` att, `tabEmployee` emp
#             WHERE att.employee = emp.name AND att.status='Present' AND att.attendance_date = '%s'""" % (day)
#         present_emp = frappe.db.sql(query, as_dict=True)
#         for emp in employees:
#             if emp in present_emp:
#                 doc = frappe.get_doc('Employee', emp)
#                 leave = get_leave(doc.name, day)
#                 if leave:
#                     for l in leave:
#                         lop = frappe.get_doc("Leave Application", l)
#                         if lop.leave_type == 'Leave Without Pay':
#                             lop.db_set("docstatus", "Cancelled")
#                             frappe.delete_doc("Leave Application", lop.name)
#                             frappe.db.commit()

# @frappe.whitelist()
# def daily_punch_record():
#     from zk import ZK, const
#     conn = None
#     zk = ZK('192.168.10.143', port=4370, timeout=5)
#     try:
#         conn = zk.connect()
#         attendance = conn.get_attendance()
#         curdate = add_days(today, -1)
#         curdate = datetime.strptime('30042018', "%d%m%Y").date()
#         for att in attendance:
#             # if att.user_id == '170':
#             date = att.timestamp.date()
#             # print date
#             if date == curdate:
#                 mtime = att.timestamp.time()
#                 userid = att.user_id
#                 employee = frappe.db.get_value("Employee", {
#                     "biometric_id": userid, "status": mmonth"Active"})
#                 if employee:
#                     doc = frappe.get_doc("Employee", employee)
#                     pr_id = frappe.db.get_value("Punch Record", {
#                         "employee": employee, "attendance_date": date})
#                     if pr_id:
#                         pr = frappe.get_doc("Punch Record", pr_id)
#                         pr.append("time_table", {
#                             "punch_time": str(mtime)
#                         })
#                         pr.save(ignore_permissions=True)
#                         frappe.db.commit()
#                     else:
#                         pr = frappe.new_doc("Punch Record")
#                         pr.employee = employee
#                         pr.employee_name = doc.employee_name
#                         pr.attendance_date = date
#                         pr.append("time_table", {
#                             "punch_time": mtime
#                         })
#                         pr.insert()
#                         pr.save(ignore_permissions=True)
#                         frappe.db.commit()
#         print "Process terminate : {}".format(e)
#     finally:
#         if conn:
#             conn.disconnect()

    # Default Attendance
    # @frappe.whitelist(allow_guest=True)
    # def attendance():
    #     userid = frappe.form_dict.get("userid")
    #     employee = frappe.db.get_value("Employee", {
    #         "biometric_id": userid})
    #     if employee:
    #             date = time.strftime("%Y-%m-%d", time.gmtime(
    #                 int(frappe.form_dict.get("att_time"))))
    #             name, company = frappe.db.get_value(
    #                 "Employee", employee, ["employee_name", "company"])
    #             attendance_id = frappe.db.get_value("Attendance", {
    #                 "employee": employee, "attendance_date": date})
    #             if attendance_id:
    #                 attendance = frappe.get_doc("Attendance", attendance_id)
    #                 out_time = time.strftime("%H:%M:%S", time.gmtime(
    #                     int(frappe.form_dict.get("att_time"))))
    #                 times = [out_time, attendance.in_time]
    #                 attendance.out_time = max(times)
    #                 attendance.in_time = min(times)
    #                 attendance.db_update()
    #             else:
    #                 attendance = frappe.new_doc("Attendance")
    #                 in_time = time.strftime("%H:%M:%S", time.gmtime(
    #                     int(frappe.form_dict.get("att_time"))))
    #                 attendance.update({
    #                     "employee": employee,
    #                     "employee_name": name,
    #                     "attendance_date": date,
    #                     "status": "Present",
    #                     "in_time": in_time,
    #                     "company": company
    #                 })
    #             attendance.save(ignore_permissions=True)
    #             attendance.submit()
    #             frappe.db.commit()
    #     frappe.response.type = "text"
    #     return "ok"

    # Shift Based need to work out
    # @frappe.whitelist(allow_guest=True)
    # def attendance():
    #     userid = frappe.form_dict.get("userid")
    #     employee = frappe.db.get_value("Employee", {
    #         "biometric_id": userid})
    #     if employee:
    #         doc = frappe.get_doc("Employee", employee)
    #         query = """SELECT ro.name, ro.shift FROM `tabRoster` ro, `tabRoster Details` rod
    # 		WHERE rod.parent = ro.name AND ro.from_date <= '%s' AND ro.to_date >= '%s'
    # 		AND rod.employee = '%s' """ % (attendance_date, attendance_date, doc.employee)
    #         roster = frappe.db.sql(query, as_list=1)
    #         if len(roster) < 1:
    #             attendance_id = frappe.db.get_value("Attendance", {
    #                 "employee": employee, "attendance_date": date})
    #             if attendance_id:
    #                 atteirirdance = frappe.get_doc(
    #                     "Attendance", attendance_id)
    #                 out_time = time.strftime("%H:%M:%S", time.gmtime(
    #                     int(frappe.form_dict.get("att_time"))))
    #                 attendance.out_time = out_time
    #                 attendance.db_update()
    #             else:
    #                 attendance = frappe.new_doc("Attendance")
    #                 in_time = time.strftime("%H:%M:%S", time.gmtime(
    #                     int(frappe.form_dict.get("att_time"))))
    #                 attendance.update({
    #                     "employee": employee,
    #                     "employee_name": doc.employee_name,
    #                     "attendance_date": date,
    #                     "status": "Present",
    #                     "in_time": in_time,
    #                     "company": doc.company
    #                 })
    #                 attendance.save(ignore_permissions=True)
    #                 attendance.submit()
    #                 frappe.db.commit()
    #             frappe.response.type = "text"
    #             return "ok"
    #         else:
    #             doc.shift = roster[0][1]

    #         shft = frappe.get_doc("Shift Details", doc.shift)
    #         att_date = datetime.strptime(
    #             attendance_date, '%Y-%m-%d %H:%M:%S')

    #         if shft.in_out_required:

    #             if shft.in_time > shft.out_time:
    #                 # this shows night shift
    #                 if shft.next_day == 1:
    #                     # this shows night shift is starting on previous day
    #                     shft_indate = datetime.combine(
    #                         att_date, datetime.min.time())

    #                     shft_outdate = datetime.combine(
    #                         add_days(att_date, -1), datetime.min.time())
    #                 else:
    #                     shft_indate = datetime.combine(
    #                         att_date, datetime.min.time())
    #             else:
    #                 shft_indate = datetime.combine(att_date, datetime.min.time())
    #             shft_intime = shft_indate + timedelta(0, shft.in_time.seconds)
    #             shft_intime_max = shft_intime + \
    #                 timedelta(0, shft.delayed_entry_allowed_time.seconds)
    #             shft_intime_min = shft_intime - \
    #                 timedelta(0, shft.early_entry_allowed_time.seconds)
    #             if shft.next_day == 1:
    #                 attendance_id = frappe.db.get_value("Attendance", {
    #                     "employee": employee, "attendance_date": shft_outdate})
    #                 # return shft_outdate
    #                 if attendance_id:
    #                     attendance = frappe.get_doc("Attendance", attendance_id)
    #                     # return attendance
    #                     if attendance and not attendance.out_time:
    #                         return "hi"
    #                         out_time = time.strftime("%Y-%m-%d %X", time.gmtime(
    #                             int(frappe.form_dict.get("att_time"))))
    #                         attendance.out_time = out_time
    #                         attendance.db_update()
    #                     else:
    #                         if att_date >= shft_intime_min and att_date <= shft_intime_max:
    #                             attendance = frappe.new_doc(
    #                                 "Attendance")
    #                             intime = time.strftime("%Y-%m-%d %X", time.gmtime(
    #                                 int(frappe.form_dict.get("att_time"))))
    #                             attendance.update({
    #                                 "employee": employee,
    #                                 "employee_name": doc.employee_name,
    #                                 "attendance_date": shft_indate,
    #                                 "status": "Present",
    #                                 "in_time": intime,
    #                                 "company": doc.company
    #                             })
    #                             attendance.save(
    #                                 ignore_permissions=True)
    #                             attendance.submit()
    #                             frappe.db.commit()
    #                         else:
    #                             attendance = frappe.new_doc(
    #                                 "Attendance")
    #                             intime = time.strftime("%Y-%m-%d %X", time.gmtime(
    #                                 int(frappe.form_dict.get("att_time"))))
    #                             attendance.update({
    #                                 "employee": employee,
    #                                 "employee_name": doc.employee_name,
    #                                 "attendance_date": shft_indate,
    #                                 "status": "Absent",
    #                                 "in_time": intime,
    #                                 "company": doc.company
    #                             })
    #                             attendance.save(
    #                                 ignore_permissions=True)
    #                             attendance.submit()
    #                             frappe.db.commit()
    #                         frappe.response.type = "text"
    #                         return "ok"
    #                 else:
    #                     if att_date >= shft_intime_min and att_date <= shft_intime_max:
    #                         attendance = frappe.new_doc(
    #                             "Attendance")
    #                         intime = time.strftime("%Y-%m-%d %X", time.gmtime(
    #                             int(frappe.form_dict.get("att_time"))))
    #                         attendance.update({
    #                             "employee": employee,
    #                             "employee_name": doc.employee_name,
    #                             "attendance_date": shft_indate,
    #                             "status": "Present",
    #                             "in_time": intime,
    #                             "company": doc.company
    #                         })
    #                         attendance.save(
    #                             ignore_permissions=True)
    #                         attendance.submit()
    #                         frappe.db.commit()
    #                     else:
    #                         attendance = frappe.new_doc(
    #                             "Attendance")
    #                         intime = time.strftime("%Y-%m-%d %X", time.gmtime(
    #                             int(frappe.form_dict.get("att_time"))))
    #                         attendance.update({
    #                             "employee": employee,
    #                             "employee_name": doc.employee_name,
    #                             "attendance_date": shft_indate,
    #                             "status": "Present",
    #                             "in_time": intime,
    #                             "company": doc.company
    #                         })
    #                         attendance.save(
    #                             ignore_permissions=True)
    #                         attendance.submit()
    #                         frappe.db.commit()
    #                     frappe.response.type = "text"
    #                     return "ok"
    #             else:
    #                 attendance_id = frappe.db.get_value("Attendance", {
    #                     "employee": employee, "attendance_date": shft_indate})
    #                 if attendance_id:
    #                     attendance = frappe.get_doc(
    #                         "Attendance", attendance_id)
    #                     out_time = time.strftime("%H:%M:%S", time.gmtime(
    #                         int(frappe.form_dict.get("att_time"))))
    #                     attendance.out_time = out_time
    #                     attendance.db_update()
    #                 else:
    #                     if att_date >= shft_intime_min and att_date <= shft_intime_max:
    #                         attendance = frappe.new_doc("Attendance")
    #                         in_time = time.strftime("%H:%M:%S", time.gmtime(
    #                             int(frappe.form_dict.get("att_time"))))
    #                         attendance.update({
    #                             "employee": employee,
    #                             "employee_name": doc.employee_name,
    #                             "attendance_date": shft_indate,
    #                             "status": "Present",
    #                             "in_time": in_time,
    #                             "company": doc.company
    #                         })
    #                         attendance.save(ignore_permissions=True)
    #                         attendance.submit()
    #                         frappe.db.commit()
    #                     else:
    #                         attendance = frappe.new_doc("Attendance")
    #                         in_time = time.strftime("%H:%M:%S", time.gmtime(
    #                             int(frappe.form_dict.get("att_time"))))
    #                         attendance.update({
    #                             "employee": employee,
    #                             "employee_name": doc.employee_name,
    #                             "attendance_date": shft_indate,
    #                             "status": "Absent",
    #                             "in_time": in_time,
    #                             "company": doc.company
    #                         })
    #                         attendance.save(ignore_permissions=True)
    #                         attendance.submit()
    #                         frappe.db.commit()
    #             frappe.response.type = "text"
    #             return "ok"


# @ frappe.whitelist()
# def holiday_lop():
#     days = ["2018-07-01", "2018-07-02", "2018-07-03", "2018-07-04", "2018-07-05", "2018-07-06",
#             "2018-07-07", "2018-07-08", "2018-07-09", "2018-07-10", "2018-07-11", "2018-07-12", "2018-07-13",
#             "2018-07-14", "2018-07-15", "2018-07-16", "2018-07-17", "2018-07-18", "2018-07-19", "2018-07-20",
#             "2018-07-21", "2018-07-22", "2018-07-23", "2018-07-24", "2018-07-25", "2018-07-26", "2018-07-27", "2018-07-28", "2018-07-29", "2018-07-30"]
#     for day in days:
#         employees = frappe.get_list('Employee', filters={"status": "Active"})
#         for employee in employees:
#             holiday = frappe.get_list(
#                 "Holiday List", filters={'holiday_date': day})
#             if holiday:
#                 count = 0
#                 pre_day = frappe.db.get_value("Attendance", {
#                     "employee": employee.name, "status": "Absent", "attendance_date": add_days(day, -1)})
#                 next_day = frappe.db.get_value("Attendance", {
#                     "employee": employee.name, "status": "Absent", "attendance_date": add_days(day, 1)})
#                 if pre_day and next_day:
#                     print employee


# @frappe.whitelist()
# def remove_left_employee_list():
#     temp = frappe.get_list("Temproary")

#     for emp in temp:
#         emp_no = frappe.db.get_value(
#             "Employee", emp.name, "employee")
#         emp_att = frappe.get_list("Attendance", filters={
#             "employee": emp_no}, fields=['name'])
#         for att in emp_att:
#             if frappe.db.exists("Attendance", att.name):
#                 at = frappe.get_doc("Attendance", att.name)
#                 print at.name
#                 at.cancel()
#                 frappe.delete_doc('Attendance', att.name)
#                 frappe.db.commit()
#         emp_la = frappe.get_list("Leave Application", filters={
#             "employee": emp_no})
#         for la in emp_la:
#             if frappe.db.exists("Leave Application", la.name):
#                 ela = frappe.get_doc("Leave Application", la.name)
#                 ela.cancel()
#                 frappe.delete_doc('Leave Application', la.name)
#                 frappe.db.commit()
#         emp_sa = frappe.get_list("Sunday Attendance", filters={
#             "employee": emp_no})
#         for sa in emp_sa:
#             if frappe.db.exists("Sunday Attendance", sa.name):
#                 esa = frappe.get_doc("Sunday Attendance", sa.name)
#                 esa.cancel()
#                 frappe.delete_doc('Sunday Attendance', sa.name)
#                 frappe.db.commit()
#         if frappe.db.exists("Employee", emp.name):
#             print frappe.db.exists("Employee", emp.name)
#             frappe.delete_doc('Employee', emp.name)
#             frappe.db.commit()

        #         emp_lat = frappe.get_list("Leave Allocation", filters={
        #             "employee": emp_no})
        #         # for lat in emp_lat:
        #         # if frappe.db.exists("Leave Allocation", lat.name):
        #         # elat = frappe.get_doc("Leave Allocation", lat.name)
        #         # elat.cancel()
        #         # frappe.delete_doc('Leave Allocation', lat.name)
        #         # frappe.db.commit()

        #         emp_up = frappe.get_list("User Permission", filters={
        #             "for_value": emp_no})
        #         # for up in emp_up:
        #         # if frappe.db.exists("User Permission", up.name):
        #         #     eup = frappe.get_doc("User Permission", up.name)
        #         # up.cancel()
        #         # frappe.delete_doc('User Permission', up.name)
        #         # frappe.db.commit()
