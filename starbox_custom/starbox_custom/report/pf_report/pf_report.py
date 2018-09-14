# Copyright (c) 2013, Starboxes India and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from datetime import datetime
from calendar import monthrange
from frappe import _, msgprint
from frappe.utils import flt


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()

    data = []
    row = []
    conditions, filters = get_conditions(filters)
    total = 0
    epsw = 0
    edlic = 0
    salary_slips = get_salary_slips(conditions,filters)
    
    for ss in salary_slips:
        pfno = frappe.db.get_value("Employee", {'employee':ss.employee},['pf_number'])
        if pfno:row = [pfno]
        else:row = [""]

        if ss.employee:row += [ss.employee]
        else:row += [""]

        if ss.employee_name:row += [ss.employee_name]
        else:row += [""]

        if ss.gp:row += [ss.gp]
        else:row += [""] 
        
        basic = frappe.db.get_value("Salary Detail", {'abbr':'B','parent':ss.name},['amount'])
        if basic:row += [basic]
        else:row += [""] 

        epsw = flt("15000")
        if basic >= epsw:
            epfw = epsw
        else:
            epfw = basic

        if epfw:row +=[epfw,epfw]
        else:row += ["",""]

        epf = frappe.db.get_value("Salary Detail", {'abbr':'PF','parent':ss.name},['amount'])
        if epf:row += [epf]
        else:row += [""]

        eps = frappe.db.get_value("Salary Detail", {'abbr':'EPS','parent':ss.name},['amount'])
        if eps:row += [eps]
        else:row += [""]

        ee = frappe.db.get_value("Salary Detail", {'abbr':'EPF','parent':ss.name},['amount'])
        if ee:row += [ee]
        else:row += [""]

        if ss.lop:row += [ss.lop]
        else:row += [""]

        data.append(row)

    return columns, data


def get_columns():
    columns = [
        _("UAN Number") + ":Data:120",
        _("Employee") + ":Data:50",
        _("Employee Name") + ":Data:90",
        _("Gross Pay") + ":Currency:100",
        _("EPF Wages") + ":Currency:100",
        _("EPS Wages") + ":Currency:100",
        _("EDLIC Wages") + ":Currency:100",
        _("EPF Contribution") + ":Currency:100",
        _("EPS Contribution") + ":Currency:100",
        _("Difference EPF & EPS ") + ":Currency:100",
        _("NCP Days ") + ":Currency:100",
        _("Refund of Advances") + ":Currency:100",

        
    ]
    return columns

def get_salary_slips(conditions,filters):
    salary_slips = frappe.db.sql("""select ss.employee as employee,ss.employee_name as employee_name,ss.name as name,ss.leave_without_pay as lop,ss.gross_pay as gp from `tabSalary Slip` ss 
    where ss.docstatus = 0 %s order by employee""" % conditions, filters, as_dict=1)
    return salary_slips


def get_conditions(filters):
    conditions = ""
    if filters.get("from_date"): conditions += " and start_date >= %(from_date)s"
    if filters.get("to_date"): conditions += " and end_date >= %(to_date)s"   
    if filters.get("employee"): conditions += " and employee = %(employee)s"
    return conditions, filters