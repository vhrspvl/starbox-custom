# -*- coding: utf-8 -*-
# Copyright (c) 2017, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import today
from frappe.utils import getdate, cint, add_months, date_diff, add_days


@frappe.whitelist()
def send_daily_report():
	custom_filter = {'date': add_days(today(), -1)}
	report = frappe.get_doc('Report', "Employee Day Attendance Report")
	columns, data = report.get_data(
	    limit=100 or 100, filters=custom_filter, as_dict=True)
	html = frappe.render_template(
	    'frappe/templates/includes/print_table.html', {'columns': columns, 'data': data})
        frappe.sendmail(
            recipients=['abdulla.pi@voltechgroup.com'],
            subject='Employee Attendance Report - ' +
            formatdate(add_days(today(), -1)),
            message=html
        )

@frappe.whitelist()
def emp_absent_today():
    day = add_days(today(), -1)
    holiday = frappe.get_list("Holiday List", filters={
                              'holiday_date': day})
    if holiday:
        pass
    else:
        query = """SELECT emp.name FROM `tabAttendance` att, `tabEmployee` emp
		WHERE att.employee = emp.name AND att.attendance_date = '%s'""" % (day)
        present_emp = frappe.db.sql(query, as_dict=True)
        for emp in frappe.get_list('Employee', filters={'status': 'Active'}):
            if emp in present_emp:
                pass
            else:
                doc = frappe.get_doc('Employee', emp)
                leave = frappe.db.sql("""select name from `tabLeave Application`
				where employee = %s and %s between from_date and to_date and status = 'Approved'
				and docstatus = 1""", (doc.name, day))
                if leave:
                    status = 'On Leave'
                else:
                    status = 'Absent'
                attendance = frappe.new_doc("Attendance")
                attendance.update({
                    "employee": doc.name,
                    "employee_name": doc.employee_name,
                    "attendance_date": day,
                    "in_time":'00:00',
                    "out_time":'00:00',
                    "status": status,
                    "company": doc.company
                })
                attendance.save(ignore_permissions=True)
                attendance.submit()
                frappe.db.commit()

#Default Attendance 
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

#Shift Based need to work out
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

# @frappe.whitelist(allow_guest=True)
# def update_leave_application():
#     employees = frappe.get_all('Employee')
#     for employee in employees:
#         attendance = frappe.db.get_all('Attendance', fields={'employee', 'attendance_date', 'status'}, filters={
#             'attendance_date': today(), 'employee': employee.name})
#         if not attendance:
#             lap = frappe.new_doc("Leave Application")
#             lap.leave_type = "Leave Without Pay"
#             lap.status = "Approved"
#             lap.from_date = today()
#             lap.to_date = today()
#             lap.employee = employee.name
#             lap.leave_approver = "Administrator"
#             lap.posting_date = today()
#             lap.company = frappe.db.get_value(
#                 "Employee", employee.name, "company")
#             lap.save(ignore_permissions=True)
#             lap.submit()
#             frappe.db.commit()
