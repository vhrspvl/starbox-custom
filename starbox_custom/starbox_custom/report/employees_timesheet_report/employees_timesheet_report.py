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


def execute(filters=None):
    totalrate=0
    fulltotal=0
    total_amount=0
    if not filters:
        filters = {}
    data = []
    data1 = []
    row = []
    total_row = []
    amount=0.0
    conditions, filters = get_conditions(filters)
    columns = [
        _("Employee") + ":Link/Employee:120", _("Employee Name") +
        "::140", _("Department") + ":Link/Department:120", _("Designation") +
        ":Link/Designation:120"
    ]
    for day in range(filters["total_days_in_month"]):
        columns.append(cstr(day+1) + "::40")
    columns += [_("Total Hours") +"::140",_("Rate/hr") +"::140",_("Amount") +"::140"]
    emp_list = get_employee_details(filters)
    for emp in emp_list:
        total = 0.0
        rate = 0.0
        amount=0.0
        row = [emp.name, emp.employee_name, emp.department, emp.designation]
        for day in range(filters["total_days_in_month"]):
            day = day + 1
            day_f = str(filters.year) +'-'+str(filters.month)+'-'+str(day)
            emp_id = emp.biometric_id
            timesheet = get_timesheet_details(emp_id,day_f)
            if timesheet:
                row += [timesheet]
                total = total + timesheet
            else:
                row += [0]
        fulltotal = fulltotal +total
        row += [total]
        if emp.designation =="Foreman":
            rate = 10
            row += [10]
            totalrate=totalrate + rate          
        if emp.designation == "Operator":
            rate = 14
            row += [14]
            totalrate=totalrate + rate
        if (rate != 0.0 and total != 0.0):
            amount = rate * total
            total_amount= total_amount + amount
        row += [amount]
        data.append(row)
    total_row = ["TOTAL","","",""]   
    for day in range(filters["total_days_in_month"]):
        day = day + 1
        day_f = str(filters.year) +'-'+str(filters.month)+'-'+str(day)    
        total_row += [""]
    total_row += [fulltotal,totalrate,total_amount]
    data.append(total_row)    
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
    if filters.get("employee"):
        conditions += " and employee = '%s'" % filters.get("employee")   
    if filters.get("employment_type"):
        conditions += " and employment_type = '%s'" % filters.get("employment_type")    
    query = """SELECT name, employee_name, biometric_id,designation,department FROM `tabEmployee` WHERE status='Active' %s
        ORDER BY employee""" % conditions
    emp_list = frappe.db.sql(query, as_dict=1)
    return emp_list

def get_timesheet_details(emp_id,day_f):   
    emp_list = frappe.db.get_value("Timesheet", {
                                 "employee": emp_id,"start_date":day_f}, "total_hours")
    # emp_list = frappe.db.sql("""SELECT total_hours,employee FROM `tabTimesheet` where employee = %s """,(emp_id), as_dict=1)
    #frappe.errprint(emp_list)
    return emp_list
 
