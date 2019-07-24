# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate
from frappe import msgprint, _
from calendar import monthrange
import time
import math
from datetime import datetime, timedelta, date
from frappe.utils import getdate, cint, add_months, date_diff, add_days, nowdate, \
    get_datetime_str, cstr, get_datetime, time_diff, time_diff_in_seconds
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee


def execute(filters=None):
    if not filters:
        filters = {}
    data = []

    conditions, filters = get_conditions(filters)
    columns = [
        _("Employee") + ":Link/Employee:120", _("Employee Name") +
        "::140", _("Branch") + ":Link/Branch:120",
        _("Department") + ":Link/Department:120", _("Designation") +
        ":Link/Designation:120", _("Employment Type") +
        ":Link/Employment Type:120"
    ]
    for day in range(filters["total_days_in_month"]):
        columns.append(cstr(day+1) + "::40")
    emp_list = get_employee_details(filters)
    for emp in emp_list:
        p = ab  = od = wo = ph = l = 0.0
        row = [emp.name, emp.employee_name, emp.branch, emp.department, emp.designation, emp.employment_type]
        working_shift = frappe.db.get_value("Employee", {'employee':emp.name},['shift']) or 'General'
        for day in range(filters["total_days_in_month"]):
            day += 1
            if day:
                day_f = str(filters.year) + '-'+str(filters.month)+'-'+str(day)
                
            day_f = datetime.strptime(day_f, "%Y-%m-%d").date()
            # holiday_list = get_holiday_list_for_employee(emp.name)
            holiday_list = frappe.db.get_value("Employee", {'employee':emp.name},['holiday_list'])
            if not holiday_list:
                # company = frappe.db.get_value("Employee", emp.name, ["company"])
                company = frappe.db.get_value("Global Defaults", None, "default_company")
                holiday_list = frappe.db.get_value("Company", company, "default_holiday_list")
            holiday_date = frappe.db.get_all("Holiday", filters={'holiday_date':day_f,'parent': holiday_list},fields=['holiday_date','description'])
            att = frappe.get_value("Attendance",{"employee":emp.name,"attendance_date":day_f},['name','attendance_date','status','employee','in_time','out_time','total_working_hours','overtime'],as_dict=True)
            if att:
                assigned_shift = frappe.db.sql("""select shift from `tabShift Assignment`
                        where employee = %s and %s between from_date and to_date""", (att.employee, att.attendance_date), as_dict=True)
                if assigned_shift:
                    working_shift = assigned_shift[0]['shift']
                if att.in_time:
                    dt = datetime.strptime(att.in_time, "%Y-%m-%d %H:%M:%S")
                    from_time = dt.time()
                    shift_in_time = frappe.db.get_value("Shift Details",working_shift,"in_time")
                    emp_in_time = timedelta(hours=from_time.hour,minutes=from_time.minute,seconds=from_time.second)
                     #Check Movement Register
                    # if get_mr_in(att.employee,att.attendance_date):
                    #     emp_in_time = emp_in_time - get_mr_in(att.employee,att.attendance_date)
                    if emp_in_time and shift_in_time:
                        if emp_in_time > shift_in_time:
                            late_in = emp_in_time - shift_in_time
                        else:
                            late_in = timedelta(seconds=0)  

                if att.out_time:
                    end_time = datetime.strptime(att.out_time, "%Y-%m-%d %H:%M:%S")
                    end_time = end_time.time()
                    shift_out_time = frappe.db.get_value("Shift Details",working_shift,"out_time")
                    emp_out_time = timedelta(hours=end_time.hour,minutes=end_time.minute,seconds=end_time.second)
                    #Check Movement Register
                    # if get_mr_out(att.employee,att.attendance_date):
                    #     emp_out_time = emp_out_time + get_mr_out(att.employee,att.attendance_date)
                    if emp_out_time and shift_out_time:
                        if emp_out_time < shift_out_time:
                            early_out = shift_out_time - emp_out_time
                        else:
                            early_out = timedelta(seconds=0)

                if holiday_date:
                    
                    for h in holiday_date:
                        leave_record = get_leaves(att.employee,att.attendance_date)
                        if att.status == "Present":
                            status = 'P'
                        # od_record = get_od(att.employee,att.attendance_date)
                        # elif get_continuous_absents(att.employee,att.attendance_date):
                        #     status = 'A'
                        elif leave_record[0]:
                            status = [leave_record[0]]
                            l += 1.0   
                        # elif od_record[0]:
                        #     status =  ["OD"]
                        #     od += 1.0
                        else:    
                            if h['description'] != 'Sunday':
                                status = 'PH'
                                ph += 1.0
                            else:
                                status = 'WO'
                                wo += 1.0
                    row += [status]

                elif att.admin_approved_status == 'Present':
                    row += ['P']
                    p += 1.0

                elif att.admin_approved_status == 'Absent':
                    row += ['A']
                    ab += 1.0

                elif att.admin_approved_status == 'WO' or att.admin_approved_status == 'PH':
                    if att.admin_approved_status == 'WO':
                        wo += 1.0
                    if att.admin_approved_status == 'PH':
                        ph += 1.0    
                    row += [att.admin_approved_status]

                elif att.status == "Absent":
                # Check if employee on Leave
                    leave_record = get_leaves(att.employee,att.attendance_date)
                    od_record = get_od(att.employee,att.attendance_date)
                    if leave_record[0]:
                        if leave_record[1] == "First Half":
                            for lv in leave_record[0]:
                                row +=[lv+'/'+'A']
                                ab += 0.5
                                l += 0.5
                        elif leave_record[1] == "Second Half":
                            for lv in leave_record[0]:
                                row +=["A"+'/'+lv]
                                ab += 0.5
                                l += 0.5
                        else:
                            row += [leave_record[0]]
                            l += 1.0
                    if od_record[0]:
                        frappe.errprint(od_record[0])
                        frappe.errprint(att.employee)
                        frappe.errprint(od_record[1])
                        if od_record[1] == "First Half":
                            for lv in od_record[0]:
                                row +=[lv+'/'+'A']
                                od += 0.5
                                l += 0.5
                        elif od_record[1] == "Second Half":
                            for lv in od_record[0]:
                                row +=["A"+'/'+lv]
                                od += 0.5
                                l += 0.5
                        else:
                            row += [od_record[0]]
                            od += 1.0
                    elif att.in_time and not att.out_time:
                        row += ["In/A"]
                        ab += 0.5
                    elif not att.in_time and not att.out_time:
                        row += ["A"]
                        ab += 1.0
                    else:   
                        row += ["A"]
                        ab += 1.0

                elif att.status == "On Leave":
                    leave_record = get_leaves(att.employee,att.attendance_date)
                    if leave_record:
                        row += [leave_record[0]]
                        l += 1.0
                    else:    
                        row += ["A"]
                        ab += 1.0
                
                elif att.status == "Half Day":
                    leave_session = get_leaves(att.employee,att.attendance_date)
                    # od_session = get_od(att.employee,att.attendance_date)
                    if leave_session[1]:
                        if leave_session[1] == "Second Half":
                            for lv in leave_session[0]:
                                row +=["P"+'/'+lv]
                                p += 0.5
                                l += 0.5  
                        else: 
                            for lv in leave_session[0]:
                                row +=[lv+'/'+"P"]
                                p += 0.5
                                l += 0.5  
                            # row +=["P/A"]    
                    else: 
                        row +=["P/A"]
                        p += 0.5
                        ab += 0.5
                    # elif od_session[1]:
                    #     if od_session[1] == "Second Half":
                    #         for o in od_session[0]:row +=["P"+'/'+o]
                    #         p += 0.5
                    #         od += 0.5
                    #     else: 
                    #         row +=["P/A"]       

                elif att.status == "Present":
                    row += ["P"]
                    p += 1.0
                    # elif late_in and late_in > timedelta(minutes=15) and early_out and early_out > timedelta(minutes=5):
                    #     row += ["A"]
                    #     ab += 1.0
                    # elif late_in and late_in > timedelta(minutes=15):
                    #     row += ["A/P"]
                    #     ab += 0.5
                    #     p += 0.5
                    # elif early_out and early_out > timedelta(minutes=5):
                    #     row += ["P/A"]
                    #     p += 0.5
                    #     ab += 0.5   
            elif holiday_date:
                    for h in holiday_date:
                        leave_record = get_leaves(emp.name,day_f)
                        # od_record = get_od(att.employee,att.attendance_date)
                        # elif get_continuous_absents(att.employee,att.attendance_date):
                        #     status = 'A'
                        if leave_record[0]:
                            status = [leave_record[0]]
                            l += 1.0   
                        # elif od_record[0]:
                        #     status =  ["OD"]
                        #     od += 1.0
                        else:    
                            if h['description'] != 'Sunday':
                                status = 'PH'
                                ph += 1.0
                            else:
                                status = 'WO'
                                wo += 1.0
                    row += [status]
            else:
                row += [""]
            #     ab += 1.0    
        row += [p,ab,l,wo,ph,od]
        data.append(row)

    columns += [_("P") + ":Float:40", _("A") + ":Float:40",  _("L") + ":Float:40",_("WO") + ":Float:40",_("PH") + ":Float:40", _("OD") + ":Float:40"]
    return columns, data


def get_conditions(filters):
    if not (filters.get("month") and filters.get("year")):
        msgprint(_("Please select month and year"), raise_exception=1)

    filters["month"] = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
                        "Dec"].index(filters.month) + 1

    filters["total_days_in_month"] = monthrange(
        cint(filters.year), filters.month)[1]

    conditions = " and month(attendance_date) = %(month)s and year(attendance_date) = %(year)s"

    if filters.get("company"):
        conditions += " and company = %(company)s"
    if filters.get("employee"):
        conditions += " and employee = %(employee)s"

    return conditions, filters


def get_employee_details(filters):
    conditions = ""
    if filters.get("company"):
        conditions += " and company = '%s'" % filters.get("company")
    if filters.get("employee"):
        conditions += " and employee = '%s'" % filters.get("employee")   
    if filters.get("employment_type"):
        conditions += " and employment_type = '%s'" % filters.get("employment_type")    
    query = """SELECT name, employee_name, biometric_id,designation,contractor,department, branch, employment_type, company FROM `tabEmployee` WHERE status='Active' %s and employment_type != 'Contract'
        ORDER BY employee""" % conditions
    emp_list = frappe.db.sql(query, as_dict=1)
    return emp_list

def get_leaves(emp,day):
    leave_type = from_date_session = to_date_session = leave = session = ""
    leave_record = frappe.db.sql("""select from_date,to_date,half_day,leave_type,half_day_date,from_date_session,to_date_session from `tabLeave Application`
                        where employee = %s and %s between from_date and to_date
                        and docstatus = 1 and status='Approved'""", (emp, day), as_dict=True)          
    if leave_record:
        for l in leave_record:
            leave_type = l.leave_type
            half_day = l.half_day                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
            half_day_date = l.half_day_date
            from_date = l.from_date
            to_date = l.to_date
            from_date_session = l.from_date_session
            to_date_session = l.to_date_session
        if half_day:
            if from_date_session:
                if day == half_day_date:
                    session = from_date_session
            if to_date_session:
                if day == half_day_date:
                    session = to_date_session
                    
        
            # if day == half_day_date:
            #     session = ["HD"] 
        if leave_type == "Privilege Leave":
            leave = ["PL"]
        elif leave_type == "Casual Leave":
            leave = ["CL"]
        elif leave_type == "Sick Leave":
            leave = ["SL"]
        elif leave_type == "Compensatory Off":
            leave = ["C-OFF"]    
        else:
            leave = ["LOP"]  
    return leave,session

def get_mr_out(emp,day):
    from_time = to_time = 0
    dt = datetime.combine(day, datetime.min.time())
    mrs = frappe.db.sql("""select from_time,to_time from `tabMovement Register` where employee= '%s' and docstatus = 1 and status='Approved' and from_time between '%s' and '%s' """ % (emp,dt,add_days(dt,1)),as_dict=True)
    for mr in mrs:
        from_time = mr.from_time
        to_time = mr.to_time
    out_time = frappe.get_value("Attendance",{"employee":emp,"attendance_date":day},["out_time"])  
    if out_time:
        att_out_time = datetime.strptime(out_time,'%d/%m/%Y %H:%M:%S')
        if from_time:
            if att_out_time >= (from_time + timedelta(minutes=-10)) :
                return to_time - from_time

def get_mr_in(emp,day):
    from_time = to_time = 0
    dt = datetime.combine(day, datetime.min.time())
    mrs = frappe.db.sql("""select from_time,to_time from `tabMovement Register` where employee= '%s' and docstatus = 1 and status='Approved' and from_time between '%s' and '%s' """ % (emp,dt,add_days(dt,1)),as_dict=True)
    for mr in mrs:
        from_time = mr.from_time
        to_time = mr.to_time
    in_time = frappe.get_value("Attendance",{"employee":emp,"attendance_date":day},["in_time"])
    if in_time:    
        att_in_time = datetime.strptime(in_time,'%d/%m/%Y %H:%M:%S')
        if from_time:
            if att_in_time >= (from_time + timedelta(minutes=-10)):
                return to_time - from_time

def get_od(emp,day):
    from_date_session = to_date_session = od = session = ""
    od_record = frappe.db.sql("""select from_date,to_date,half_day,from_date_session,to_date_session from `tabOn Duty Application`
                        where employee = %s and %s between from_date and to_date
                        and docstatus = 1 and status='Approved'""", (emp, day), as_dict=True)
    if od_record:
        for o in od_record:
            half_day = o.half_day
            from_date = o.from_date
            to_date = o.to_date
            from_date_session = o.from_date_session
            to_date_session = o.to_date_session
            session = from_date_session
            frappe.errprint(session)
        if half_day:
            if from_date == to_date:
               session = from_date_session 
            else:   
                if from_date == day:
                    session = from_date_session
                elif to_date == day:
                    session = to_date_session  
        od = ["OD"]  
    return od,session    
