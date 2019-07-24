# -*- coding: utf-8 -*-
# Copyright (c) 2019, Starboxes India and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from datetime import date, datetime, timedelta
from frappe.utils import add_days


class AttendanceAlreadyMarkedError(frappe.ValidationError): pass

class ManualAttendanceCorrection(Document):
    def autoname(self):
        self.name = self.employee + "/" + self.attendance_date


@frappe.whitelist()
def bulk_update_mac():
    macs = frappe.get_all("Manual Attendance Correction",{'status':'Approved','docstatus':1})
    for mac in macs:
        m = frappe.get_doc('Manual Attendance Correction',mac)
        update_attendance_time(m.employee, str(m.attendance_date), str(m.in_time), str(m.out_time))

@frappe.whitelist()
def update_attendance_time(employee, attendance_date, in_time, out_time):
    twh= ''
    if attendance_date:
        attendance_date = out_date = datetime.strptime(
                attendance_date, '%Y-%m-%d')
        if in_time and out_time:        
            in_time_f = datetime.strptime(in_time,'%H:%M:%S').time()
            out_time_f = datetime.strptime(out_time,'%H:%M:%S').time()
            if out_time_f < in_time_f:
                out_date = (add_days(attendance_date,1)).date()                  
            in_time = datetime.strptime(in_time,'%H:%M:%S').time()
            in_time = datetime.combine(attendance_date, in_time)
            out_time = datetime.strptime(out_time,'%H:%M:%S').time()
            out_time = datetime.combine(out_date, out_time)
        
            twh = out_time - in_time
            status = 'Absent'
            if twh > timedelta(hours=4):
                status = 'Half Day'
            if twh >= timedelta(hours=8):
                status = 'Present'
            if twh:
                twh_seconds = twh.total_seconds()
                minutes = twh_seconds // 60
                hours = minutes // 60
                twh =  "%02d hr %02d min" % (hours, minutes % 60)    
            if frappe.db.exists("Attendance", {"employee": employee,"attendance_date": attendance_date}):
                att = frappe.db.get_value("Attendance", {"employee": employee,"attendance_date":attendance_date},"name")
                    # frappe.errprint(att)
                exist_att = frappe.get_doc("Attendance", att)
                if not exist_att.in_time or not exist_att.out_time:
                    exist_att.update({
                        "biometric_id": employee,
                        "attendance_date": attendance_date,
                        "status":status,
                        "in_time": in_time,
                        "out_time": out_time,
                        "total_working_hours":twh,
                        "modified_status": "Miss Punch"
                    })
                    exist_att.save(ignore_permissions=True)
                    frappe.db.commit()
            else:
                exist_att = frappe.new_doc("Attendance")
                exist_att.update({
                    "employee": employee,
                    "biometric_id": employee,
                    "attendance_date": attendance_date,
                    "in_time": in_time,
                    "status":status,
                    "out_time": out_time,
                    "total_working_hours":twh,
                    "modified_status": "Miss Punch"
                })
                exist_att.save(ignore_permissions=True)
                exist_att.submit()
                frappe.db.commit()
        return "Ok"


@frappe.whitelist()
def check_attendance(employee,attendance_date):
    if frappe.db.exists("Attendance", {"employee": employee,"attendance_date": attendance_date}):
        att = frappe.get_doc("Attendance",{"employee": employee,"attendance_date": attendance_date})
        if att:
            return att
    else:
        return "OK"