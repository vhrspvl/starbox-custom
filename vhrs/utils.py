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
        "biometric_id": userid})
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
            frappe.throw(("No Roster defined for {0} for date {1}").format(
                doc.employee, attendance_date))
        else:
            doc.shift = roster[0][1]

        shft = frappe.get_doc("Shift Details", doc.shift)
        att_date = datetime.strptime(
            attendance_date, '%Y-%m-%d %H:%M:%S')

        if shft.in_out_required:

            if shft.in_time > shft.out_time:
                # this shows night shift
                if shft.next_day == 1:
                    # this shows night shift is starting on previous day
                    shft_indate = datetime.combine(
                        att_date, datetime.min.time())

                    shft_outdate = datetime.combine(
                        add_days(att_date, -1), datetime.min.time())
                else:
                    shft_indate = datetime.combine(
                        att_date, datetime.min.time())
            else:
                shft_indate = datetime.combine(att_date, datetime.min.time())
            shft_intime = shft_indate + timedelta(0, shft.in_time.seconds)
            shft_intime_max = shft_intime + \
                timedelta(0, shft.delayed_entry_allowed_time.seconds)
            shft_intime_min = shft_intime - \
                timedelta(0, shft.early_entry_allowed_time.seconds)
            if shft.next_day == 1:
                attendance_id = frappe.db.get_value("Attendance", {
                    "employee": employee, "attendance_date": shft_outdate})
                # return shft_outdate    
                if attendance_id:
                    attendance = frappe.get_doc("Attendance", attendance_id)
                    # return attendance
                    if attendance and not attendance.out_time:
                        out_time = time.strftime("%Y-%m-%d %X", time.gmtime(
                            int(frappe.form_dict.get("att_time"))))
                        attendance.out_time = out_time
                        attendance.db_update()
                    else:
                        if att_date >= shft_intime_min and att_date <= shft_intime_max:
                            attendance = frappe.new_doc(
                                "Attendance")
                            intime = time.strftime("%Y-%m-%d %X", time.gmtime(
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
                            frappe.response.type = "text"
                            return "ok"
                        else:
                            return "out of time2"
                else:
                    if att_date >= shft_intime_min and att_date <= shft_intime_max:
                        attendance = frappe.new_doc(
                            "Attendance")
                        intime = time.strftime("%Y-%m-%d %X", time.gmtime(
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
                        frappe.response.type = "text"
                        return "ok"
                    else:
                        return "out of time"
            else:
                attendance_id = frappe.db.get_value("Attendance", {
                    "employee": employee, "attendance_date": shft_indate})
                if attendance_id:
                    attendance = frappe.get_doc(
                        "Attendance", attendance_id)
                    out_time = time.strftime("%H:%M:%S", time.gmtime(
                        int(frappe.form_dict.get("att_time"))))
                    attendance.out_time = out_time
                    attendance.db_update()
                else:
                    if att_date >= shft_intime_min and att_date <= shft_intime_max:
                        attendance = frappe.new_doc("Attendance")
                        in_time = time.strftime("%H:%M:%S", time.gmtime(
                            int(frappe.form_dict.get("att_time"))))
                        attendance.update({
                            "employee": employee,
                            "employee_name": doc.employee_name,
                            "attendance_date": shft_indate,
                            "status": "Present",
                            "in_time": in_time,
                            "company": doc.company
                        })
                        attendance.save(ignore_permissions=True)
                        attendance.submit()
                        frappe.db.commit()
            frappe.response.type = "text"
            return "ok"
