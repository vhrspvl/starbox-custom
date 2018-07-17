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

        time_m = time.strftime("%H:%M:%S", time.gmtime(
            int(frappe.form_dict.get("att_time"))))

        doc = frappe.get_doc("Employee", employee)
        # return doc.employment_type
        if doc.employment_type == 'Staff' or doc.employment_type == 'Contract' or doc.employment_type == 'Aparajita':
            a_min_time = datetime.strptime('06:30', '%H:%M')
            a_max_time = datetime.strptime('07:30', '%H:%M')
            b_min_time = datetime.strptime('08:00', '%H:%M')
            b_max_time = datetime.strptime('09:00', '%H:%M')
            c_min_time = datetime.strptime('12:30', '%H:%M')
            c_max_time = datetime.strptime('13:30', '%H:%M')
            d_min_time = datetime.strptime('20:00', '%H:%M')
            d_max_time = datetime.strptime('21:00', '%H:%M')
            e_min_time = datetime.strptime('18:30', '%H:%M')
            e_max_time = datetime.strptime('19:30', '%H:%M')
        if doc.employment_type == 'Operator':
            a_min_time = datetime.strptime('07:30', '%H:%M')
            a_max_time = datetime.strptime('08:30', '%H:%M')
            b_min_time = datetime.strptime('04:30', '%H:%M')
            b_max_time = datetime.strptime('05:30', '%H:%M')
            c_min_time = datetime.strptime('00:30', '%H:%M')
            c_max_time = datetime.strptime('01:30', '%H:%M')
            d_min_time = datetime.strptime('20:00', '%H:%M')
            d_max_time = datetime.strptime('21:00', '%H:%M')
            e_min_time = datetime.strptime('18:30', '%H:%M')
            e_max_time = datetime.strptime('19:30', '%H:%M')

        if doc.employment_type == 'Contract' or doc.employment_type == 'Operator' or doc.employment_type == 'Aparajita':
            prev_attendance_id = frappe.db.get_value("Attendance", {
                "employee": doc.name, "attendance_date": add_days(date, -1)})
            attendance_id = frappe.db.get_value("Attendance", {
                "employee": doc.name, "attendance_date": date})
            if prev_attendance_id:
                attendance = frappe.get_doc(
                    "Attendance", prev_attendance_id)
                if attendance.in_time and not attendance.out_time:
                    attendance.out_date = date
                    attendance.out_time = time_m
                    in_time_f = datetime.strptime(
                        attendance.in_time, '%H:%M:%S')
                    out_time_f = datetime.strptime(
                        attendance.out_time, '%H:%M:%S')
                    maxhr = timedelta(seconds=1200)
                    actual_working_hours = frappe.db.get_value("Employee",doc.employee,"working_hours")
                    difftime = actual_working_hours - timedelta(seconds=(out_time_f - in_time_f).seconds)    
                    if difftime <= maxhr:
                        out_time_f = out_time_f + timedelta(seconds=1200)    
                    if out_time_f <= in_time_f:
                        min_hr = timedelta(hours=24)
                        worked_hrs = time_diff_in_seconds(
                            out_time_f + min_hr, in_time_f)
                    else:
                        worked_hrs = time_diff_in_seconds(
                            out_time_f, in_time_f)
                    total_working_hours = (
                        worked_hrs // 3600.00)
                    attendance.total_working_hours = total_working_hours
                    attendance.db_update()
                    frappe.db.commit()
                    frappe.response.type = "text"
                    return "ok"
                else:
                    if attendance_id:
                        attendance = frappe.get_doc(
                            "Attendance", attendance_id)
                        if not attendance.in_time:
                            attendance.in_time = time_m
                            attendance.status = "Present"
                        else:
                            # times = [time_m, attendance.in_time]
                            attendance.out_date = date
                            attendance.out_time = time_m
                            # attendance.in_time = min(times)
                            attendance.status = "Present"
                            in_time_f = datetime.strptime(
                                attendance.in_time, '%H:%M:%S')
                            out_time_f = datetime.strptime(
                                attendance.out_time, '%H:%M:%S')
                            maxhr = timedelta(seconds=1200)
                            actual_working_hours = frappe.db.get_value("Employee",doc.employee,"working_hours")
                            difftime = actual_working_hours - timedelta(seconds=(out_time_f - in_time_f).seconds)    
                            if difftime <= maxhr:
                                out_time_f = out_time_f + timedelta(seconds=1200)    
                        
                            worked_hrs = time_diff_in_seconds(
                                out_time_f, in_time_f)
                            total_working_hours = (
                                worked_hrs // 3600.00)
                            attendance.total_working_hours = total_working_hours
                        attendance.db_update()
                        frappe.db.commit()
                        frappe.response.type = "text"
                        return "ok"
                    else:
                        attendance = frappe.new_doc("Attendance")
                        in_time = time_m
                        intime = datetime.strptime(
                            in_time, '%H:%M:%S')
                        if intime >= a_min_time and intime <= a_max_time:
                            shift = "A"
                        elif intime >= b_min_time and intime <= b_max_time:
                            shift = "B"
                        elif intime >= c_min_time and intime <= c_max_time:
                            shift = "C"
                        elif intime >= d_min_time and intime <= d_max_time:
                            shift = "D"
                        elif intime >= e_min_time and intime <= e_max_time:
                            shift = "E"
                        else:
                            shift = "NA"
                        # return type(a_min_time)
                        attendance.update({
                            "employee": employee,
                            "employee_name": doc.employee_name,
                            "attendance_date": date,
                            "shift": shift,
                            "status": "Present",
                            "in_time": in_time,
                            "company": doc.company
                        })
                        attendance.save(ignore_permissions=True)
                        attendance.submit()
                        frappe.db.commit()
                        frappe.response.type = "text"
                        return "ok"
            if attendance_id:
                attendance = frappe.get_doc(
                    "Attendance", attendance_id)
                if not attendance.in_time:
                    attendance.in_time = time_m
                    attendance.status = "Present"
                else:
                    times = [time_m, attendance.in_time]
                    attendance.out_date = date
                    attendance.out_time = max(times)
                    attendance.in_time = min(times)
                    attendance.status = "Present"
                    in_time_f = datetime.strptime(
                        attendance.in_time, '%H:%M:%S')
                    out_time_f = datetime.strptime(
                        attendance.out_time, '%H:%M:%S')
                    maxhr = timedelta(seconds=1200)
                    actual_working_hours = frappe.db.get_value("Employee",doc.employee,"working_hours")
                    difftime = actual_working_hours - timedelta(seconds=(out_time_f - in_time_f).seconds)    
                    if difftime <= maxhr:
                        out_time_f = out_time_f + timedelta(seconds=1200)    
                        
                    worked_hrs = time_diff_in_seconds(
                        out_time_f, in_time_f)
                    total_working_hours = (
                        worked_hrs // 3600.00)
                    attendance.total_working_hours = total_working_hours
                attendance.db_update()
                frappe.db.commit()
                frappe.response.type = "text"
                return "ok"
            else:
                attendance = frappe.new_doc("Attendance")
                in_time = time_m
                intime = datetime.strptime(
                    in_time, '%H:%M:%S')
                if intime >= a_min_time and intime <= a_max_time:
                    shift = "A"
                elif intime >= b_min_time and intime <= b_max_time:
                    shift = "B"
                elif intime >= c_min_time and intime <= c_max_time:
                    shift = "C"
                elif intime >= d_min_time and intime <= d_max_time:
                    shift = "D"
                elif intime >= e_min_time and intime <= e_max_time:
                    shift = "E"
                else:
                    shift = "NA"
                attendance.update({
                    "employee": employee,
                    "employee_name": doc.employee_name,
                    "attendance_date": date,
                    "shift": shift,
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
            date = time.strftime("%Y-%m-%d", time.gmtime(
                int(frappe.form_dict.get("att_time"))))

            attendance_date = time.strftime("%Y-%m-%d %X", time.gmtime(
                int(frappe.form_dict.get("att_time"))))

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
                    m_time = time.strftime("%H:%M:%S", time.gmtime(
                        int(frappe.form_dict.get("att_time"))))
                    if not attendance.in_time:
                        attendance.in_time = m_time
                        attendance.status = "Present"
                    else:
                        times = [m_time, attendance.in_time]
                        attendance.out_date = date
                        attendance.out_time = max(times)
                        attendance.in_time = min(times)
                        attendance.status = "Present"
                        in_time_f = datetime.strptime(
                            attendance.in_time, '%H:%M:%S')
                        out_time_f = datetime.strptime(
                            attendance.out_time, '%H:%M:%S')
                        worked_hrs = time_diff_in_seconds(
                            out_time_f, in_time_f)
                        total_working_hours = math.floor(
                            worked_hrs / 60 / 60)
                        attendance.total_working_hours = total_working_hours
                    attendance.db_update()
                    frappe.db.commit()
                    frappe.response.type = "text"
                    return "ok"
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

                    shft_indate = datetime.combine(
                        att_date, datetime.min.time())
                    shft_intime = shft_indate + \
                        timedelta(0, shft.in_time.seconds)
                    shft_intime_max = shft_intime + \
                        timedelta(0, shft.delayed_entry_allowed_time.seconds)
                    shft_intime_min = shft_intime - \
                        timedelta(0, shft.early_entry_allowed_time.seconds)

                    attendance_id = frappe.db.get_value("Attendance", {
                        "employee": employee, "attendance_date": date})
                    if attendance_id:
                        attendance = frappe.get_doc(
                            "Attendance", attendance_id)
                        m_time = time.strftime("%H:%M:%S", time.gmtime(
                            int(frappe.form_dict.get("att_time"))))
                        if not attendance.in_time:
                            attendance.in_time = m_time
                            attendance.status = "Present"
                        else:
                            times = [m_time, attendance.in_time]
                            attendance.out_date = date
                            attendance.out_time = max(times)
                            attendance.in_time = min(times)
                            attendance.status = "Present"
                            in_time_f = datetime.strptime(
                                attendance.in_time, '%H:%M:%S')
                            out_time_f = datetime.strptime(
                                attendance.out_time, '%H:%M:%S')
                            worked_hrs = time_diff_in_seconds(
                                out_time_f, in_time_f)
                            total_working_hours = math.floor(
                                worked_hrs / 60 / 60)
                            attendance.total_working_hours = total_working_hours
                        attendance.db_update()
                        frappe.db.commit()
                        frappe.response.type = "text"
                        return "ok"
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
