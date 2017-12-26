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


@frappe.whitelist(allow_guest=True)
def attendance():
    userid = frappe.form_dict.get("userid")
    employee = frappe.db.get_value("Employee", {
        "biometric_id": userid})
    if employee:
        date = time.strftime("%Y-%m-%d", time.gmtime(
            int(frappe.form_dict.get("att_time"))))
        name, company = frappe.db.get_value(
            "Employee", employee, ["employee_name", "company"])
        attendance_id = frappe.db.get_value("Attendance", {
            "employee": employee, "attendance_date": today()})
    attendance = frappe.new_doc("Attendance")
    attendance.update({
        "employee": employee,
        "attendance_date": today(),
        "status": "Present",
        "company": company
    })
    attendance.append("attendance_time", {
        "time_type": "In Time",
        "date_time": date
    })
    attendance.save(ignore_permissions=True)
    frappe.response.type = "text"
    return "ok"
    # restrict request list of IP addresses
    # userid = frappe.form_dict.get("userid")
    # employee = frappe.db.get_value("Employee", {
    #     "biometric_id": userid})
    # if employee:
    #     date = time.strftime("%Y-%m-%d", time.gmtime(
    #         int(frappe.form_dict.get("att_time"))))
    #     name, company = frappe.db.get_value(
    #         "Employee", employee, ["employee_name", "company"])
    #     attendance_id = frappe.db.get_value("Attendance", {
    #         "employee": employee, "attendance_date": date})
    #     if attendance_id:
    #         attendance = frappe.get_doc("Attendance", attendance_id)
    #         out_time = time.strftime("%H:%M:%S", time.gmtime(
    #             int(frappe.form_dict.get("att_time"))))
    #         attendance.out_time = out_time
    #         attendance.db_update()
    #     else:
    #         attendance = frappe.new_doc("Attendance")
    #         in_time = time.strftime("%H:%M:%S", time.gmtime(
    #             int(frappe.form_dict.get("att_time"))))
    #         attendance.update({
    #             "employee": employee,
    #             "employee_name": name,
    #             "attendance_date": date,
    #             "status": "Present",
    #             "in_time": in_time,
    #             "company": company
    #         })
    #     attendance.save(ignore_permissions=True)
    #     attendance.submit()
    #     frappe.db.commit()
    # frappe.response.type = "text"
    # return "ok"
