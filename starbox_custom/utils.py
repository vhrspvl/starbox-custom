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
from frappe.utils import getdate, cint, add_months, date_diff, add_days, nowdate, \
    get_datetime_str, cstr, get_datetime, time_diff, time_diff_in_seconds
from datetime import datetime, timedelta


@frappe.whitelist(allow_guest=True)
def attendance():
    global attendance_date, att_time
    userid = frappe.form_dict.get("userid")
    employee = frappe.db.get_value("Employee", {
        "biometric_id": userid, "status": "Active"})
    if employee:
        date = time.strftime("%Y-%m-%d", time.gmtime(
            int(frappe.form_dict.get("att_time"))))

        attendance_date = time.strftime("%Y-%m-%d %X", time.gmtime(
            int(frappe.form_dict.get("att_time"))))

        doc = frappe.get_doc("Employee", employee)
        query = """SELECT ro.name, ro.shift FROM `tabRoster` ro, `tabRoster Details` rod
		WHERE rod.parent = ro.name AND ro.from_date <= '%s' AND ro.to_date >= '%s' 
		AND rod.employee = '%s' """ % (attendance_date, attendance_date, doc.employee)
        roster = frappe.db.sql(query, as_list=1)
        if len(roster) < 1:
            attendance_id = frappe.db.get_value("Attendance", {
                "employee": employee, "attendance_date": date})
            if attendance_id:
                attendance = frappe.get_doc(
                    "Attendance", attendance_id)
                out_time = time.strftime("%H:%M:%S", time.gmtime(
                    int(frappe.form_dict.get("att_time"))))
                times = [out_time, attendance.in_time]
                attendance.out_time = max(times)
                attendance.in_time = min(times)
                attendance.status = "Present"
                attendance.db_update()
                frappe.db.commit()
            else:
                attendance = frappe.new_doc("Attendance")
                in_time = time.strftime("%H:%M:%S", time.gmtime(
                    int(frappe.form_dict.get("att_time"))))
                attendance.update({
                    "employee": employee,
                    "employee_name": doc.employee_name,
                    "attendance_date": date,
                    "stgid": frappe.form_dict.get("stgid"),
                    "status": "Present",
                    "in_time": in_time,
                    "company": doc.company
                })
                attendance.save(ignore_permissions=True)
                attendance.submit()
                frappe.db.commit()
            frappe.response.type = "text"
            return "ok"
        else:
            doc.shift = roster[0][1]

            shft = frappe.get_doc("Shift Details", doc.shift)
            att_date = datetime.strptime(
                attendance_date, '%Y-%m-%d %H:%M:%S')

            if shft.in_out_required:
                shft_hrs = shft.hours_required_per_day.seconds

                shft_indate = datetime.combine(att_date, datetime.min.time())
                shft_intime = shft_indate + timedelta(0, shft.in_time.seconds)
                shft_intime_max = shft_intime + \
                    timedelta(0, shft.delayed_entry_allowed_time.seconds)
                shft_intime_min = shft_intime - \
                    timedelta(0, shft.early_entry_allowed_time.seconds)

                attendance_id = frappe.db.get_value("Attendance", {
                    "employee": employee, "attendance_date": date})
                if attendance_id:
                    attendance = frappe.get_doc(
                        "Attendance", attendance_id)
                    out_time = time.strftime("%H:%M:%S", time.gmtime(
                        int(frappe.form_dict.get("att_time"))))
                    times = [out_time, attendance.in_time]
                    attendance.out_time = max(times)
                    attendance.in_time = min(times)
                    total_hrs = time_diff_in_seconds(
                        attendance.out_time, attendance.in_time)
                    attendance.overtime = (total_hrs - shft_hrs) / 3600
                    attendance.db_update()
                    frappe.db.commit()
                else:
                    if att_date >= shft_intime_min and att_date <= shft_intime_max:
                        attendance = frappe.new_doc(
                            "Attendance")
                        intime = time.strftime("%H:%M:%S", time.gmtime(
                            int(frappe.form_dict.get("att_time"))))
                        attendance.update({
                            "employee": employee,
                            "employee_name": doc.employee_name,
                            "attendance_date": shft_indate,
                            "status": "Present",
                            "in_time": intime,
                            "company": doc.company
                        })
                        attendance.save(
                            ignore_permissions=True)
                        attendance.submit()
                        frappe.db.commit()
                    else:
                        attendance = frappe.new_doc(
                            "Attendance")
                        intime = time.strftime("%H:%M:%S", time.gmtime(
                            int(frappe.form_dict.get("att_time"))))
                        attendance.update({
                            "employee": employee,
                            "employee_name": doc.employee_name,
                            "attendance_date": shft_indate,
                            "status": "Late",
                            "in_time": intime,
                            "company": doc.company
                        })
                        attendance.save(
                            ignore_permissions=True)
                        frappe.db.commit()
                frappe.response.type = "text"
                return "ok"
    else:
        employee = frappe.form_dict.get("userid")
        date = time.strftime("%Y-%m-%d", time.gmtime(
            int(frappe.form_dict.get("att_time"))))
        ure_id = frappe.db.get_value("Unregistered Employee", {
            "employee": employee, "attendance_date": date})
        if ure_id:
            attendance = frappe.get_doc(
                "Unregistered Employee", ure_id)
            out_time = time.strftime("%H:%M:%S", time.gmtime(
                int(frappe.form_dict.get("att_time"))))
            times = [out_time, attendance.in_time]
            attendance.out_time = max(times)
            attendance.in_time = min(times)
            attendance.db_update()
            frappe.db.commit()
        else:
            attendance = frappe.new_doc("Unregistered Employee")
            in_time = time.strftime("%H:%M:%S", time.gmtime(
                int(frappe.form_dict.get("att_time"))))
            attendance.update({
                "employee": employee,
                "attendance_date": date,
                "stgid": frappe.form_dict.get("stgid"),
                "in_time": in_time,
            })
            attendance.save(ignore_permissions=True)
            frappe.db.commit()
        frappe.response.type = "text"
        return "ok"
# @frappe.whitelist(allow_guest=True)
# def attendance():
#     global attendance_date, att_time
#     userid = frappe.form_dict.get("userid")
#     employee = frappe.db.get_value("Employee", {
#         "biometric_id": userid})
#     if employee:
#         date = time.strftime("%Y-%m-%d", time.gmtime(
#             int(frappe.form_dict.get("att_time"))))

#         attendance_date = time.strftime("%Y-%m-%d %X", time.gmtime(
#             int(frappe.form_dict.get("att_time"))))

#         doc = frappe.get_doc("Employee", employee)
#         query = """SELECT ro.name, ro.shift FROM `tabRoster` ro, `tabRoster Details` rod
# 		WHERE rod.parent = ro.name AND ro.from_date <= '%s' AND ro.to_date >= '%s'
# 		AND rod.employee = '%s' """ % (attendance_date, attendance_date, doc.employee)
#         roster = frappe.db.sql(query, as_list=1)
#         if len(roster) < 1:
#             attendance_id = frappe.db.get_value("Attendance", {
#                 "employee": employee, "attendance_date": date})
#             if attendance_id:
#                 attendance = frappe.get_doc(
#                     "Attendance", attendance_id)
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

#             shft = frappe.get_doc("Shift Details", doc.shift)
#             att_date = datetime.strptime(
#                 attendance_date, '%Y-%m-%d %H:%M:%S')

#             if shft.in_out_required:
#                 shft_indate = datetime.combine(att_date, datetime.min.time())
#                 shft_intime = shft_indate + timedelta(0, shft.in_time.seconds)
#                 shft_intime_max = shft_intime + \
#                     timedelta(0, shft.delayed_entry_allowed_time.seconds)
#                 shft_intime_min = shft_intime - \
#                     timedelta(0, shft.early_entry_allowed_time.seconds)

#                 attendance_id = frappe.db.get_value("Attendance", {
#                     "employee": employee, "attendance_date": date})
#                 if attendance_id:
#                     attendance = frappe.get_doc(
#                         "Attendance", attendance_id)
#                     out_time = time.strftime("%H:%M:%S", time.gmtime(
#                         int(frappe.form_dict.get("att_time"))))
#                     times = [out_time, attendance.in_time]
#                     attendance.out_time = max(times)
#                     attendance.in_time = min(times)
#                     attendance.db_update()
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
#                             "status": "Absent",
#                             "in_time": intime,
#                             "company": doc.company
#                         })
#                         attendance.save(
#                             ignore_permissions=True)
#                 frappe.response.type = "text"
#                 return "ok"
