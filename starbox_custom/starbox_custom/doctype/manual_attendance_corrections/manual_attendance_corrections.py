# -*- coding: utf-8 -*-
# Copyright (c) 2019, Starboxes India and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class ManualAttendanceCorrections(Document):
    pass


@frappe.whitelist()
def update_attendance_time(employee, attendance_date, in_time, out_time,out_date):
    if attendance_date:
        att = frappe.db.get_value("Attendance", {"biometric_id": employee})
        if att:
            exist_att = frappe.get_doc("Attendance", att)
        else:
            exist_att = frappe.new_doc("Attendance")
        exist_att.update({
            "employee": employee,
            "biometric_id": employee,
            "attendance_date": attendance_date,
            "out_date": out_date,
            "in_time": in_time,
            "out_time": out_time
        })
        exist_att.save(ignore_permissions=True)
        frappe.db.commit()
    return "Ok"
