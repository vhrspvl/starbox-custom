# Copyright (c) 2013, Starboxes India and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from datetime import datetime


def execute(filters=None):
    if not filters:
        filters = {}
    columns = get_columns()

    data = []
    row = []
    leave_type = from_date_session = to_date_session = ""
    conditions, filters = get_conditions(filters)
    total = from_time = late_in = early_out = shift_in_time = dt = 0
    attendance = get_attendance(conditions, filters)
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    for att in attendance:
        if att:
            working_shift = frappe.db.get_value("Employee", {'employee':att.employee},['shift']) 
            assigned_shift = frappe.db.sql("""select shift from `tabShift Assignment`
                        where employee = %s and %s between from_date and to_date""", (att.employee, att.attendance_date), as_dict=True)
            if assigned_shift:
                working_shift = assigned_shift[0]['shift']
            if att.name:
                row = [att.name]
            else:
                row = ["-"]

            if att.attendance_date:
                row += [att.attendance_date]
            else:
                row += ["-"]

            if att.employee:
                
                row += [att.employee]
            else:
                row += ["-"]

            if att.employee_name:
                row += [att.employee_name]
            else:
                row += ["-"]

            
            if att.employment_type:
                row += [ att.employment_type]
            else:
                row += ["-"]

            if att.department:
                row += [att.department]
            else:
                row += ["-"]

            if working_shift:
                row += [working_shift]
            else:
                row += ["-"]

            if att.in_time:
                try:            
                    dt = datetime.strptime(att.in_time, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    dt = datetime.strptime(att.in_time, '%H:%M:%S')
                from_time = dt.time()
                row += [from_time.isoformat()]
            else:
                row += ["-"]

            if att.out_time:
                try:            
                    dt = datetime.strptime(att.out_time, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    dt = datetime.strptime(att.out_time, '%H:%M:%S')
                to_time = dt.time()
                row += [to_time.isoformat()]
            else:
                row += ["-"]    

            if att.total_working_hours:
                row += [att.total_working_hours]
            else:
                row += ["-"]

            if att.status:
                if att.in_time and not att.out_time:
                    if frappe.db.exists("Manual Attendance Correction", {'employee':att.employee,"attendance_date": att.attendance_date,"docstatus":0}):
                        row += ["MP Applied"] 
                    else:
                        row += ["Miss Punch"]
                elif not att.in_time and att.out_time:
                    if frappe.db.exists("Manual Attendance Correction", {'employee':att.employee,"attendance_date": att.attendance_date,"docstatus":0}):
                        row += ["MP Applied"] 
                    else:
                        row += ["Miss Punch"]
                elif not att.in_time and not att.out_time:
                    if frappe.db.exists("Manual Attendance Correction", {'employee':att.employee,"attendance_date": att.attendance_date,"docstatus":0}):
                        row += ["MP Applied"]       
                    elif att.status == 'On Leave':
                        row += [att.leave_type]
                    else:
                        row += [att.status]
                else:
                    row += [att.status]
            else:
                row += ["-"]

            if att.modified_status:
                row += [att.modified_status]
            else:
                row += ["-"]      
            

            data.append(row)
    return columns, data


def get_columns():
    columns = [
        _("Name") + ":Link/Attendance:180",
        _("Attendance Date") + ":Date:80",
        _("Employee") + ":Link/Employee:80",
        _("Employee Name") + ":Data:150",
        _("Employment Type") + ":Data:180",
        _("Department") + ":Data:80",
        _("Shift") + ":Data:90",
        _("In Time") + ":Time:90",
        _("Out Time") + ":Rime:90",
        _("Working Hours") + ":Time:90",
        _("Status") + ":Link/Attendance:90",
        _("Modified Status") + ":Data:90",
    ]
    return columns


def get_attendance(conditions, filters):
    attendance = frappe.db.sql("""
    select
    att.leave_type,att.name as name,att.attendance_date as attendance_date,att.employee as employee,att.modified_status as modified_status, att.employee_name as employee_name,emp.employment_type as employment_type,att.department as department,att.shift as shift,att.in_time as in_time,att.out_time as out_time,att.total_working_hours as total_working_hours,att.status as status 
    from `tabAttendance` att 
    left join `tabEmployee` emp on att.employee = emp.employee
    where  
    att.docstatus != 2
     %s 
    order by emp.employment_type,att.attendance_date""" % conditions, filters, as_dict=1)
    return attendance


def get_conditions(filters):
    conditions = ""
    if filters.get("from_date"):
        conditions += "and att.attendance_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " and att.attendance_date <= %(to_date)s"
    if filters.get("status_in"):
        conditions += " and att.in_time > 0"
    if filters.get("employee"):
        conditions += "AND att.employee = '%s'" % filters["employee"]
    if filters.get("employment_type"):
        conditions += "AND emp.employment_type = '%s'" % filters["employment_type"]    
    if filters.get("department"):
        conditions += " AND att.department = '%s'" % filters["department"]
    if filters.get("location"):
        conditions += " AND att.location = '%s'" % filters["location"]

    if not frappe.get_doc("User", frappe.session.user).get("roles", {"role": "System Manager"}):
        employee = frappe.db.get_value(
            "Employee", {"user_id": filters.get("user")})
        if filters.get("user"):
            conditions += " and att.employee = %s" % employee
    return conditions, filters
