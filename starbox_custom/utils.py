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
from frappe.utils import getdate, cint, add_months, date_diff, add_days, get_last_day,get_first_day,nowdate, \
    get_datetime_str, cstr, get_datetime, time_diff, time_diff_in_seconds
from datetime import datetime, timedelta
from werkzeug.wrappers import Response
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee




@frappe.whitelist(allow_guest=True)
def attendance(**args):
    args = frappe._dict(args)
    global attendance_date, att_time
    userid = args.get("userid")
    biotime = args.get("att_time")
    att_type = args.get("att_type")
    stgid = args.get("stgid")
    token = args.get("auth_token")
    employee = frappe.db.get_value("Employee", {
        "biometric_id": userid, "status": "Active"})
    response = Response()
    response.mimetype = 'text/plain'
    response.charset = 'utf-8'
    response.data = "ok"  
    auth_token = frappe.db.get_value("Biometric Settings", {"device_id": stgid}, "auth_token")
    if not auth_token or (auth_token and auth_token != token):
        log_error("device auth error", args)
        return response  
    if employee:
        log_error("att", args)
        create_pr(userid, biotime, employee)
        date = time.strftime("%Y-%m-%d", time.gmtime(
            int(frappe.form_dict.get("att_time"))))
        date = datetime.strptime(date, "%Y-%m-%d").date()
        attendance_date = time.strftime("%Y-%m-%d %X", time.gmtime(
            int(frappe.form_dict.get("att_time"))))

        time_m = time.strftime("%H:%M:%S", time.gmtime(
            int(frappe.form_dict.get("att_time"))))
        frappe.errprint(time_m)
        time_m = datetime.strptime(time_m, '%H:%M:%S').time()
        m_time = datetime.combine(date, time_m)
        total_working_hours = 0
        doc = frappe.get_doc("Employee", employee)
        if doc.date_of_joining > date:
            log_error("Attendance date can not be less than employee's joining date", args)
            return response  


        if doc.employment_type == 'Contract' or doc.employment_type == 'Operator' or doc.designation == 'Operator':
        # if doc.select_biometric_machine ! = 'Reception':    
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
            if att_type == 'in':
                attendance_id = frappe.db.exists("Attendance", {
                "employee": doc.name, "attendance_date": date})
                if attendance_id:
                    attendance = frappe.get_doc(
                                "Attendance", attendance_id)
                    attendance.update({
                    "in_time": m_time  
                    })  
                    attendance.db_update()        
                else:
                    intime = datetime.strptime(
                        str(time_m), '%H:%M:%S')
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
                    attendance = frappe.new_doc("Attendance")
                    attendance.update({
                        "employee": employee,
                        "employee_name": doc.employee_name,
                        "employment_type":doc.employment_type,
                        "attendance_date": date,
                        "shift": shift,
                        "status": "Present",
                        "in_time": m_time,
                        "company": doc.company
                    })
                attendance.save(ignore_permissions=True)
                attendance.submit()
                frappe.db.commit()
                return response
            if att_type == 'out':  
                attendance_id = frappe.db.exists("Attendance", {
                "employee": doc.name, "attendance_date": date})
                if attendance_id:
                    attendance = frappe.get_doc(
                                "Attendance", attendance_id)
                    if attendance.in_time:            
                        attendance_in_time = datetime.strptime(attendance.in_time, '%Y-%m-%d %H:%M:%S').time()
                        times = [time_m, attendance_in_time]
                        attendance.out_date = date
                        in_time = min(times)
                        out_time = max(times)
                        final_out_time = datetime.combine(date, out_time)
                        attendance.out_time = final_out_time
                        final_in_time = datetime.combine(date, in_time)
                        attendance.in_time = final_in_time
                        attendance.status = "Present"
                        in_time_f = timedelta(
                                hours=in_time.hour, minutes=in_time.minute, seconds=in_time.second)
                        out_time_f = timedelta(
                                hours=out_time.hour, minutes=out_time.minute, seconds=out_time.second)
                        actual_working_hours = frappe.db.get_value(
                            "Employee", doc.employee, "working_hours")
                        if actual_working_hours:
                            diff2 = (out_time_f - in_time_f)
                            td = diff2 - actual_working_hours
                            if actual_working_hours > (out_time_f - in_time_f):
                                td = (out_time_f - in_time_f)
                            worked_hrs = time_diff_in_seconds(
                                out_time_f, in_time_f)
                            total_working_hours = (worked_hrs / 3600.00)
                            if td.seconds >= 2700:
                                total_working_hours = math.ceil(
                                    total_working_hours)
                            else:
                                total_working_hours = math.floor(
                                    total_working_hours)
                        attendance.total_working_hours = total_working_hours  
                    else:
                        attendance.out_time = datetime.combine(date, time_m)
                    attendance.db_update()
                    frappe.db.commit()
                    return response
                else:    
                    prev_attendance_id = frappe.db.get_value("Attendance", {
                        "employee": doc.name, "attendance_date": add_days(date, -1)})
                    if prev_attendance_id:
                        attendance = frappe.get_doc(
                            "Attendance", prev_attendance_id)
                        if attendance.in_time and not attendance.out_time:
                            in_time = datetime.strptime(attendance.in_time, '%Y-%m-%d %H:%M:%S').time()
                            attendance.out_date = date
                            out_time = time_m
                            final_out_time = datetime.combine(date, out_time)
                            attendance.out_time = final_out_time
                            in_time_f = timedelta(
                                hours=in_time.hour, minutes=in_time.minute, seconds=in_time.second)
                            out_time_f = timedelta(
                                hours=out_time.hour, minutes=out_time.minute, seconds=out_time.second)
                            actual_working_hours = frappe.db.get_value(
                                "Employee", doc.employee, "working_hours")
                            if actual_working_hours:
                                td = (out_time_f - in_time_f) - actual_working_hours
                                if actual_working_hours > (out_time_f - in_time_f):
                                    td = (out_time_f - in_time_f)
                                if out_time_f <= in_time_f:
                                    min_hr = timedelta(hours=24)
                                    worked_hrs = time_diff_in_seconds(
                                        out_time_f + min_hr, in_time_f)
                                else:
                                    worked_hrs = time_diff_in_seconds(
                                        out_time_f, in_time_f)
                                total_working_hours = (worked_hrs / 3600.00)
                                if td.seconds >= 2700:
                                    total_working_hours = math.ceil(
                                        total_working_hours)
                                else:
                                    total_working_hours = math.floor(
                                        total_working_hours)
                                attendance.total_working_hours = total_working_hours
                            attendance.db_update()
                            frappe.db.commit()
                        log_error("no in today,prev day full punch", args)    
                        return response 
                    else:
                        log_error("no in today,prev day no punch", args)
                        return response
        else:
            return response

    else:
        employee = frappe.form_dict.get("userid")
        date = time.strftime("%Y-%m-%d", time.gmtime(
            int(frappe.form_dict.get("att_time"))))
        date = datetime.strptime(date, "%Y-%m-%d").date()
        ure_id = frappe.db.get_value("Unregistered Employee", {
            "employee": employee, "attendance_date": date})
        if ure_id:
            attendance = frappe.get_doc(
                "Unregistered Employee", ure_id)
            out_time = time.strftime("%H:%M:%S", time.gmtime(
                int(frappe.form_dict.get("att_time"))))
            times = [out_time, attendance.in_time]
            out_time = max(times)
            in_time = min(times)
            attendance.in_time = in_time
            attendance.out_time = out_time
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
        return response


def floor_dt(dt):
    # how many secs have passed this hour
    nsecs = dt.minute*60 + dt.second + dt.microsecond*1e-6
    # number of seconds to next quarter hour mark
    # Non-analytic (brute force is fun) way:
    #   delta = next(x for x in xrange(0,3601,900) if x>=nsecs) - nsecs
    # analytic way:
    delta = math.floor(nsecs / 900) * 900 - nsecs
    return dt + timedelta(seconds=delta)
    # time + number of seconds to quarter hour mark.

def log_error(method, message):
    # employee = message["userid"]
    message = frappe.utils.cstr(message) + "\n" if message else ""
    d = frappe.new_doc("Error Log")
    d.method = method
    d.error = message
    d.insert(ignore_permissions=True)
    # if employee:
    # 	user = frappe.db.get_value("Employee", employee, "user_id")
    # 	if user:
    # 		frappe.get_doc({
    # 			"doctype": "ToDo",
    # 			"description": "Failed to update attendance<br>" + method + "<br>"+ message,
    # 			"owner": user,
    # 			"status": "Open"}
    # 		).insert(ignore_permissions=True)
    # 		frappe.db.commit()

def create_pr(user, ptime, employee):
    date = time.strftime("%Y-%m-%d", time.gmtime(
        int(ptime)))

    attendance_date = time.strftime("%Y-%m-%d %X", time.gmtime(
        int(ptime)))

    time_m = time.strftime("%H:%M:%S", time.gmtime(
        int(ptime)))

    doc = frappe.get_doc("Employee", employee)
    pr_id = frappe.db.get_value("Punch Record", {
        "employee": employee, "attendance_date": date})
    if pr_id:
        pr = frappe.get_doc("Punch Record", pr_id)
        already_exist = False
        for t in pr.time_table:
            if str(t.punch_time) == time_m:
                already_exist = True
        if not already_exist:
            pr.append("time_table", {
                "punch_time": time_m
            })
            pr.save(ignore_permissions=True)
    else:
        pr = frappe.new_doc("Punch Record")
        pr.employee = employee
        pr.employee_name = doc.employee_name
        pr.attendance_date = date
        pr.append("time_table", {
            "punch_time": time_m
        })
        pr.insert()
        pr.save(ignore_permissions=True)
        frappe.db.commit()

@frappe.whitelist()
def mark_att_temp():
    day = '2019-05-21'
    in_time = out_time = ""
    # days = ["2019-05-10","2019-05-09","2019-05-08","2019-05-07","2019-05-06","2019-05-05","2019-05-04","2019-05-03","2019-05-02","2019-05-01"]
    # employees = ['2073']
    employees = frappe.get_all(
        "Employee", {"status": "Active", "employment_type": ("in", ["Contract"])})
    for emp in employees:
        emp = emp.name
        # if emp == '4063':
        # for day in days:
        holidays = get_holidays_for_employee(emp, day)
        if holidays:
            pass
        else:
            ntimes = []
            times = []
            twh = ""
            status = 'Absent'
            punch_record = frappe.db.exists(
                "Punch Record", {"attendance_date": day, "employee": emp})
            if punch_record:
                pr = frappe.get_doc("Punch Record", punch_record)
            working_shift = "G"
            if punch_record:
                for t in pr.time_table:
                    times.append(t.punch_time)
                in_time = min(times)
                in_time = (datetime.min + in_time).time()
                in_time = datetime.combine(pr.attendance_date, in_time)
                out_time = max(times)
                out_time = (datetime.min + out_time).time()
                out_time = datetime.combine(pr.attendance_date, out_time)
                if in_time == out_time:
                    out_time = ""
                att_id = frappe.get_value(
                        "Attendance", {"attendance_date": day, "employee": emp})
                if att_id:
                    if in_time and out_time:
                        twh = out_time - in_time
                        if twh > timedelta(hours=4):
                            status = 'Half Day'
                        if twh >= timedelta(hours=8):
                            status = 'Present'
                        # in_time = (datetime.min + in_time).time()
                        # out_time = (datetime.min + out_time).time()
                    # if not punch_record and att_id['in_time'] and att_id['out_time']:
                    #     in_time = in_time
                    #     out_time = out_time
                    if twh:
                        twh_seconds = twh.total_seconds()
                        minutes = twh_seconds // 60
                        hours = minutes // 60
                        twh =  "%02d hr %02d min" % (hours, minutes % 60)
                    att = frappe.get_doc("Attendance", att_id)
                    att.update({
                        "in_time": in_time,
                        "out_time": out_time,
                        "total_working_hours": twh,
                        "status": status
                    })
                    if att.docstatus == 1:
                        att.db_update()
                        frappe.db.commit()
                    else:
                        att.save(ignore_permissions=True)
                        att.submit()
                        frappe.db.commit()
                else:                
                    att = frappe.new_doc("Attendance")
                    att.update({
                        "employee": emp,
                        "employment_type": frappe.get_value("Employee", emp, "employment_type"),
                        "attendance_date": day,
                        "biometric_id": emp,
                        "shift": working_shift,
                        "status": status,
                        "in_time": in_time,
                    })
                    att.save(ignore_permissions=True)
                    frappe.db.commit()     
@frappe.whitelist()
def mark_attendance(day):
    # day = "2019-05-22"
    in_time = out_time = ""
    # days = ["2019-05-10","2019-05-09","2019-05-08","2019-05-07","2019-05-06","2019-05-05","2019-05-04","2019-05-03","2019-05-02","2019-05-01"]
    # employees = ['2073']
    employees = frappe.get_all(
        "Employee", {"status": "Active", "employment_type": ("not in", ["Contract","Operator"]) })
    # employees = frappe.get_all(
    #     "Employee", {"status": "Active", "select_biometric_machine": 'Reception' })
    for emp in employees:
        emp = emp.name
        # if emp == '405':
        # for day in days:
        holidays = get_holidays_for_employee(emp, day)
        if holidays:
            pass
        else:
            ntimes = []
            times = []
            twh = ""
            status = 'Absent'
            punch_record = frappe.db.exists(
                "Punch Record", {"attendance_date": day, "employee": emp})
            if punch_record:
                pr = frappe.get_doc("Punch Record", punch_record)

            working_shift = frappe.db.get_value(
                "Employee", {'employee': emp}, ['shift'])
            assigned_shift = frappe.db.sql("""select shift from `tabShift Assignment`
                        where employee = %s and %s between from_date and to_date""", (emp, day), as_dict=True)
            if assigned_shift:
                working_shift = assigned_shift[0]['shift']
            shift = frappe.db.exists(
                "Shift Type", working_shift)
            if shift:
                shift = frappe.get_doc("Shift Type", working_shift)
            else:    
                shift = frappe.get_doc("Shift Type", "G")

            if punch_record:
                for t in pr.time_table:
                    times.append(t.punch_time)
                if shift.shift_type == 'Regular':
                    in_time = min(times)
                    in_time = (datetime.min + in_time).time()
                    in_time = datetime.combine(pr.attendance_date, in_time)
                    out_time = max(times)
                    out_time = (datetime.min + out_time).time()
                    out_time = datetime.combine(pr.attendance_date, out_time)
                    if in_time == out_time:
                        out_time = ""
                if shift.shift_type == 'Night':
                    in_time = max(times)
                    in_time = (datetime.min + in_time).time()
                    in_time = datetime.combine(pr.attendance_date, in_time)
                    next_day_punch = frappe.db.exists("Punch Record",{"attendance_date":add_days(day,1),"employee":emp})
                    npr = ""
                    if next_day_punch:
                        npr = frappe.get_doc("Punch Record",next_day_punch)
                    if npr:
                        frappe.errprint(npr.attendance_date)
                        # ntimes = []
                        for t in npr.time_table:
                            ntimes.append(t.punch_time)
                        frappe.errprint(ntimes)
                        out_time = min(ntimes)
                        out_time = (datetime.min + out_time).time()
                        out_time = datetime.combine(npr.attendance_date, out_time)
                att_id = frappe.get_value(
                    "Attendance", {"attendance_date": day, "employee": emp})
                if att_id:
                    if in_time and out_time:
                        twh = out_time - in_time
                        if twh > timedelta(hours=4):
                            status = 'Half Day'
                        # if twh >= timedelta(hours=8) and shift.end_time <= timedelta(hours=out_time.hour,minutes=out_time.minute,seconds=out_time.second):
                        if twh >= timedelta(hours=8):
                            status = 'Present'
                        # in_time = (datetime.min + in_time).time()
                        # out_time = (datetime.min + out_time).time()
                    # if not punch_record and att_id['in_time'] and att_id['out_time']:
                    #     in_time = in_time
                    #     out_time = out_time
                    if twh:
                        twh_seconds = twh.total_seconds()
                        minutes = twh_seconds // 60
                        hours = minutes // 60
                        twh =  "%02d hr %02d min" % (hours, minutes % 60)
                    att = frappe.get_doc("Attendance", att_id)
                    att.update({
                        "in_time": in_time,
                        "out_time": out_time,
                        "total_working_hours": twh,
                        "status": status
                    })
                    if att.docstatus == 1:
                        att.db_update()
                        frappe.db.commit()
                    else:
                        att.save(ignore_permissions=True)
                        att.submit()
                        frappe.db.commit()
                else:
                    # in_time = str(in_time)
                    # dt = datetime.strptime(in_time, "%Y-%m-%d %H:%M:%S")
                    # emp_in_time = dt.time()
                    emp_in_time = in_time.strftime("%H:%M:%S")
                    emp_in_time = datetime.strptime(emp_in_time, "%H:%M:%S")
                    shift_in_time = frappe.get_value("Shift Type", working_shift, "start_time")
                    shift_in_time = str(shift_in_time)
                    shift_in_time = datetime.strptime(shift_in_time, "%H:%M:%S")
                    permission_count = ""
                    if emp_in_time > shift_in_time:                            
                        first_date = get_first_day(day)
                        last_date = get_last_day(day)
                        count = frappe.db.sql("""select * from `tabAttendance Permission`
                            where employee = %s and permission_date between %s and %s""", (emp, first_date,last_date), as_dict=True)
                        if len(count) > 3:
                            status = "Half Day"
                        if frappe.db.exists("Attendance Permission",{"permission_date": day,"employee":emp}):
                            ap = frappe.get_doc("Attendance Permission",{"permission_date": day,"employee":emp})
                        else:
                            ap = frappe.new_doc("Attendance Permission")
                        ap.update({
                            "employee": emp,
                            "employee_name": frappe.get_value("Employee", emp, "first_name"),
                            "permission_date": day,
                            "department": frappe.get_value("Employee", emp, "department"),
                            "company": frappe.get_value("Employee", emp, "company"),
                        })
                        ap.save(ignore_permissions=True)
                        ap.submit()
                        frappe.db.commit()
                        frappe.errprint(status)
                    att = frappe.new_doc("Attendance")
                    att.update({
                        "employee": emp,
                        "employment_type": frappe.get_value("Employee", emp, "employment_type"),
                        "attendance_date": day,
                        "biometric_id": emp,
                        "shift": working_shift,
                        "status": status,
                        "in_time": in_time,
                    })
                    att.save(ignore_permissions=True)
                    frappe.db.commit()                      
            else:
                att_id = frappe.get_value(
                    "Attendance", {"attendance_date": day, "employee": emp})
                if att_id:
                    pass
                else:
                    att = frappe.new_doc("Attendance")
                    att.update({
                        "employee": emp,
                        "employment_type": frappe.get_value("Employee", emp, "employment_type"),
                        "attendance_date": day,
                        "biometric_id": emp,
                        "shift": working_shift,
                        "status": status,
                        # "in_time": in_time,
                    })
                    att.save(ignore_permissions=True)
                    att.submit()
                    frappe.db.commit()


@frappe.whitelist()
def prev_day_attendance():
    mark_attendance(add_days(today(), -1))


@frappe.whitelist()
def current_day_attendance():
    mark_attendance(today())


@frappe.whitelist()
def fetch_from_ui(from_date, to_date):
    from_date = (datetime.strptime(str(from_date), '%Y-%m-%d')).date()
    to_date = (datetime.strptime(str(to_date), '%Y-%m-%d')).date()
    for preday in daterange(from_date, to_date):
        mark_attendance(preday)


@frappe.whitelist()
def mark_emp_type():
    att = frappe.get_all("Attendance", ['employee', 'name'])
    for at in att:
        emp_type = frappe.get_value("Employee", at.employee, "employment_type")
        frappe.db.set_value("Attendance", at.name, "employment_type", emp_type)


@frappe.whitelist()
def get_punch_from_machine(from_date, to_date, bioip=None):
    from zk import ZK, const
    conn = None
    from_date = (datetime.strptime(str(from_date), '%Y-%m-%d')).date()
    to_date = (datetime.strptime(str(to_date), '%Y-%m-%d')).date()
    if not bioip:
        bioip = ['192.168.10.143']
    for bio in bioip:
        zk = ZK(bio, port=4370, timeout=5)
        try:
            conn = zk.connect()
            for curdate in daterange(from_date, to_date):
                attendance = conn.get_attendance()
                for att in attendance:
                    # if att.user_id == '170':
                    date = att.timestamp.date()
                    if date == curdate:
                        mtime = att.timestamp.time()
                        mtimef = timedelta(
                            hours=mtime.hour, minutes=mtime.minute, seconds=mtime.second)
                        userid = att.user_id
                        employee = frappe.db.get_value("Employee", {
                            "biometric_id": userid, "status": "Active"})
                        if employee:
                            print employee, att.timestamp
                            doc = frappe.get_doc("Employee", employee)
                            already_exist = False
                            pr_id = frappe.db.get_value("Punch Record", {
                                "employee": employee, "attendance_date": date})
                            if pr_id:
                                pr = frappe.get_doc("Punch Record", pr_id)
                                # max(i.punchtime)
                                for i in pr.time_table:
                                    if i.punch_time == mtimef:
                                        already_exist = True
                                if not already_exist:
                                    pr.append("time_table", {
                                        "punch_time": str(mtime)
                                    })
                                    pr.save(ignore_permissions=True)
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
        # return "Fetched"
        except Exception, e:
            frappe.errprint(e)
            return "Process terminate : {}".format(e)
        finally:
            if conn:
                conn.disconnect()


def daterange(date1, date2):
    for n in range(int((date2 - date1).days)+1):
        yield date1 + timedelta(n)

@frappe.whitelist()
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