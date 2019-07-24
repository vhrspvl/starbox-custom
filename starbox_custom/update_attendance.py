from __future__ import unicode_literals
import json, frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
import time, math
from frappe.utils.data import today, get_timestamp
from frappe.utils import getdate, cint, add_months, date_diff, add_days, nowdate, get_datetime_str, cstr, get_datetime, time_diff, time_diff_in_seconds
from datetime import datetime, timedelta

@frappe.whitelist()
def update_twh():
    from_date = '2019-05-01'
    to_date = '2019-05-08'
    attendance = frappe.db.sql("select att.employee as employee,att.status as status,att.total_working_hours as twh from `tabAttendance` att \n    where att.docstatus = 1 and att.attendance_date between '%s' and '%s' " % (from_date, to_date), as_dict=1)
    for att in attendance:
        if att.twh:
            twh_f = att.twh
            twhs = twh_f.split(':')
            if len(twhs) > 1:
                twh_seconds = timedelta(hours=int(twhs[0]), minutes=int(twhs[1]), seconds=int(twhs[2])).total_seconds()
                minutes = twh_seconds // 60
                hours = minutes // 60
                t3 = '%02d hr %02d min' % (hours, minutes % 60)
                print t3


@frappe.whitelist()
def update_attendance_time():
    attendance = frappe.db.sql("select * from `tabAttendance` where docstatus = 1 and attendance_date between '%s' and '%s' " % (u'2019-05-01',
                                                                                                                                 u'2019-05-22'), as_dict=1)
    attendance_in_time = ''
    attendance_out_time = ''
    for att in attendance:
        if att.out_time:
            try:
                attendance_out_time = datetime.strptime(att.out_time, '%H:%M:%S').time()
            except ValueError:
                attendance_out_time = datetime.strptime(att.out_time, '%Y-%m-%d %H:%M:%S').time()

            if attendance_out_time:
                attendance_out_time = datetime.combine(att.attendance_date, attendance_out_time)
                frappe.errprint(attendance_out_time)
                frappe.db.set_value('Attendance', att.name, 'out_time', attendance_out_time)