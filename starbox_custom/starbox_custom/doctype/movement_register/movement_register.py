# -*- coding: utf-8 -*-
# Copyright (c) 2019, Starboxes India and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime,timedelta,date,time
from frappe.utils import (flt, getdate, get_first_day,get_last_day, add_months, add_days, formatdate)

class MovementRegister(Document):
    pass
    def on_submit(self):
        if self.status == "Open":
            frappe.throw(_("Only Applications with status 'Approved' and 'Rejected' can be submitted"))
@frappe.whitelist()
def check_count(employee, from_time):
    if employee:
        from_date = (datetime.strptime(str(from_time), '%Y-%m-%d %H:%M:%S')).date()
        first_date = get_first_day(from_date)
        last_date = get_last_day(from_date)
        count = 1
        mr_list = frappe.db.sql("""select name from `tabMovement Register`
                        where employee = %s """, (employee), as_dict=True)
        for mr in mr_list:
            doc = frappe.get_doc("Movement Register", mr.name)
            doc_date = (datetime.strptime(str(doc.from_time), '%Y-%m-%d %H:%M:%S')).date()
            if doc_date > first_date and doc_date < last_date:
                count += 1
        if count > 2:
            return "NA"

@frappe.whitelist()
def update_att(employee,time_diff,status,date):
    d = (datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S')).date()
    if status =="Approved":
        attendance = frappe.db.sql("""select attendance_date, in_time,out_time, total_working_hours from `tabAttendance` where employee = %s and attendance_date = %s""",(employee,d),as_dict = True)
        for att in attendance:
            in_t = datetime.strptime(att.in_time, '%Y-%m-%d %H:%M:%S').time()
            out_t = datetime.strptime(att.out_time, '%Y-%m-%d %H:%M:%S').time()
            i_time = timedelta(
                    hours=in_t.hour, minutes=in_t.minute, seconds=in_t.second).total_seconds()
            o_time = timedelta(
                    hours=out_t.hour, minutes=out_t.minute, seconds=out_t.second).total_seconds()
            diff = o_time - i_time
            p_time = float(time_diff) * 3600
            total_wh = diff + p_time
            minutes = total_wh // 60
            hours = minutes // 60
            twh =  "%02d hr %02d min" % (hours, minutes % 60)
            # t = timedelta(seconds=total_wh)
            # frappe.errprint(in_t)
            # frappe.errprint(i_time)
            # frappe.errprint(out_t)
            # frappe.errprint(o_time)
            # frappe.errprint(diff)
            # frappe.errprint(p_time)
            # frappe.errprint(total_wh)
            # frappe.errprint(twh)
            att.update({
                "total_working_hours": twh
                    })
            att.save(ignore_permissions=True)
            att.submit()
            frappe.db.commit()