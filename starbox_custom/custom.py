# -*- coding: utf-8 -*-
# Copyright (c) 2017, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils.data import today
from frappe.utils import formatdate, getdate, cint, add_months, date_diff, add_days, flt, cstr
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
import requests


@frappe.whitelist()
def test_ctc():
    for cl in get_active_cl():
        ctc = frappe.db.get_value("Contractor", {'name': cl.contractor}, [
            'ctc_per_day'], as_dict=True)


@frappe.whitelist()
def update_in_biometric_machine(uid, uname):
    stgids = frappe.db.get_all("Service Tag")
    for stgid in stgids:
        url = "http://robot.camsunit.com/external/1.0/user/update?uid=%s&uname=%s&stgid=%s" % (
            uid, uname, stgid.name)
        r = requests.post(url)
    return r.content


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
        recipients=['abdulla.pi@voltechgroup.com', 'hari@starboxes.in',
                    'hr@starboxes.in', 'thiru@starboxes.in'],
        subject='Employee Attendance Report - ' +
        formatdate(add_days(today(), -1)),
        message=html
    )


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
        recipients=['abdulla.pi@voltechgroup.com', 'hari@starboxes.in',
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
    # days = ["2018-04-01", "2018-04-04", "2018-04-03", "2018-04-05", "2018-04-06", "2018-04-07", "2018-04-08", "2018-04-09", "2018-04-10", "2018-04-12", "2018-04-13", "2018-04-14",
    #         "2018-04-15", "2018-04-16", "2018-04-17", "2018-04-19", "2018-04-20", "2018-04-21", "2018-04-22", "2018-04-23", "2018-04-24", "2018-04-26", "2018-04-27", "2018-04-28"]
    lap = frappe.get_doc("Leave Application", doc.name)
    if lap.status == 'Approved':
        if lap.leave_type == 'Leave Without Pay':
            status = 'Absent'
        else:
            status = "On Leave"
        attendances = frappe.db.sql("""select name,status from `tabAttendance`
                    where employee = %s and attendance_date between %s and %s
                and docstatus = 1""", (lap.employee, lap.from_date, lap.to_date), as_dict=True)
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
def convert2present():
    from_date = '2018-03-01'
    to_date = '2018-03-31'
    attendances = frappe.db.sql("""select name,status from `tabAttendance` where status='Late'
    and attendance_date between %s and %s""", (from_date, to_date), as_dict=True)
    print len(attendances)
    for attendance in attendances:
        att = frappe.get_doc("Attendance", attendance)
        att.update({
            "status": "Present"
        })
        att.save(ignore_permissions=True)
        frappe.db.commit()

    # for day in days:
    # employees = frappe.get_all('Employee', filters={"status": "Active"})
    # for employee in employees:
    #     lwp = get_leave(employee.name, day)
    #     if lwp:
    #         attendance_id = frappe.db.get_value("Attendance", {
    #             "employee": employee, "attendance_date": day})
    #         if attendance_id:
    #             attendance = frappe.get_doc(
    #                 "Attendance", attendance_id)
    #             attendance.out_time = "00:00:00"
    #             attendance.in_time = "00:00:00"
    #             attendance.status = "On Leave"
    #             attendance.db_update()
    #             frappe.db.commit()


@frappe.whitelist()
def emp_absent_today():
    day = add_days(today(), -1)
    # day = datetime.strptime('18042018', "%d%m%Y").date()
    holiday = frappe.get_list("Holiday List", filters={
                              'holiday_date': day})
    if holiday:
        pass
    else:
        query = """SELECT emp.name FROM `tabAttendance` att, `tabEmployee` emp
		WHERE att.employee = emp.name AND att.attendance_date = '%s'""" % (day)
        present_emp = frappe.db.sql(query, as_dict=True)
        for emp in frappe.get_list('Employee', filters={'status': 'Active'}):
            joining_date = frappe.db.get_value(
                "Employee", emp, ["date_of_joining"])
            if day < joining_date:
                pass
            elif emp in present_emp:
                pass
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
def removelop(doc, method):
    if doc.status == 'Present':
        lop = frappe.get_list("Leave Application", filters={
            'from_date': doc.attendance_date, 'to_date': doc.attendance_date, 'employee': doc.employee, 'leave_type': 'Leave without Pay'})
        for l in lop:
            lop = frappe.get_doc("Leave Application", l)
            if lop.leave_type == 'Leave Without Pay':
                lop.db_set("docstatus", "Cancelled")
                frappe.delete_doc("Leave Application", lop.name)
                frappe.db.commit()


@frappe.whitelist()
def bulkremovelop():
    employees = frappe.get_all('Employee', fields=['name'], filters={
                               "status": "Active", "employment_type": ("!=", "Contract")})
    days = ["2018-04-01", "2018-04-02", "2018-04-03", "2018-04-04", "2018-04-05", "2018-04-06", "2018-04-07", "2018-04-08", "2018-04-09", "2018-04-10", "2018-04-11", "2018-04-12", "2018-04-13", "2018-04-14",
            "2018-04-15", "2018-04-16", "2018-04-17", "2018-04-18", "2018-04-19", "2018-04-20", "2018-04-21", "2018-04-22", "2018-04-23", "2018-04-24", "2018-04-25", "2018-04-26", "2018-04-27", "2018-04-28", "2018-04-29", "2018-04-30"]
    for day in days:
        query = """SELECT emp.name FROM `tabAttendance` att, `tabEmployee` emp
            WHERE att.employee = emp.name AND att.status='Present' AND att.attendance_date = '%s'""" % (day)
        present_emp = frappe.db.sql(query, as_dict=True)
        for emp in employees:
            if emp in present_emp:
                doc = frappe.get_doc('Employee', emp)
                leave = get_leave(doc.name, day)
                if leave:
                    for l in leave:
                        lop = frappe.get_doc("Leave Application", l)
                        if lop.leave_type == 'Leave Without Pay':
                            lop.db_set("docstatus", "Cancelled")
                            frappe.delete_doc("Leave Application", lop.name)
                            frappe.db.commit()


@frappe.whitelist()
def update_leave_application():
    day = add_days(today(), -1)
    employees = frappe.get_all('Employee', filters={"status": "Active"})
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
				where employee = %s and %s between from_date and to_date and status = 'Approved'
			and docstatus = 1""", (emp, day), as_dict=1)
    return leave


@frappe.whitelist()
def mark_comp_off():
    day = add_days(today(), -1)
    from_date = add_days(day, 1)
    to_date = add_months(day, 1)
    query = """SELECT emp.name FROM `tabAttendance` att, `tabEmployee` emp
		WHERE att.employee = emp.name AND att.attendance_date = '%s'""" % (day)
    present_emp = frappe.db.sql(query, as_dict=True)

    for emp in frappe.get_list('Employee', filters={'status': 'Active', 'employment_type': ("!=", "Contract")}):
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


@frappe.whitelist()
def daily_punch_record():
    from zk import ZK, const
    conn = None
    zk = ZK('192.168.10.141', port=4370, timeout=5)
    try:
        conn = zk.connect()
        attendance = conn.get_attendance()
        curdate = datetime.now().date()
        # curdate = datetime.strptime('18042018', "%d%m%Y").date()
        for att in attendance:
            # if att.user_id == '170':
            date = att.timestamp.date()
            # print date
            if date == curdate:
                mtime = att.timestamp.time()
                userid = att.user_id
                employee = frappe.db.get_value("Employee", {
                    "biometric_id": userid, "status": "Active"})
                if employee:
                    doc = frappe.get_doc("Employee", employee)
                    pr_id = frappe.db.get_value("Punch Record", {
                        "employee": employee, "attendance_date": date})
                    if pr_id:
                        pr = frappe.get_doc("Punch Record", pr_id)
                        pr.append("time_table", {
                            "punch_time": str(mtime)
                        })
                        pr.save(ignore_permissions=True)
                        frappe.db.commit()
                    else:
                        pr = frappe.new_doc("Punch Record")
                        pr.employee = employee
                        pr.employee_name = doc.employee_name
                        pr.attendance_date = date
                        pr.append("time_table", {
                            "punch_time": mtime
                        })
                        pr.insert()
                        pr.save(ignore_permissions=True)
                        frappe.db.commit()
    except Exception, e:
        print "Process terminate : {}".format(e)
    finally:
        if conn:
            conn.disconnect()
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
