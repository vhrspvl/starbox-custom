# Copyright (c) 2013, Starboxes India and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _, msgprint
import math
from frappe.utils import (cint, cstr, date_diff, flt, getdate, money_in_words,
                          nowdate, rounded, today, time_diff_in_seconds)
from datetime import date,datetime, timedelta


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns(filters)
    conditions, filters = get_conditions(filters)
    data = []
    row = []
    cl_attendance  = get_cl_attendance(conditions,filters)
    frappe.errprint(cl_attendance)
    for cl in  cl_attendance :
        if cl.employee:
			row += [cl.employee]
		
    return columns, data
def get_columns(attendance):
    columns = [
        _("Employee") + ":Link/Employee:90",
        _("Employee Name") + "::150",
        _("Contractor") + ":Link/Contractor:180",
        _("Department") + ":Link/Department:130",
        _("Employment Type") + ":Link/Employment Type:130",
        _("CTC Per Day") + ":Currency:100",
    ]

    return columns
def get_cl_attendance(conditions,filters):

    cl_attendance = frappe.db.sql("""select * from `tabAttendance`  where
        status = 'Present' and employment_type = 'Contract' %s""" % conditions, filters, as_dict=1)
    frappe.errprint(cl_attendance)
    return cl_attendance
    

# def get_active_emp():
#     active_emp = frappe.db.sql(
#         """select emp.working_hours from `tabEmployee` emp where emp.status = "Active" and emp.employment_type="Contract" order by emp.name""", as_dict=1)
#     return active_emp

def get_conditions(filters):
    conditions = ""
    if filters.get("employee"):
        conditions += " name = %(employee)s and"
    if filters.get("contractor"):
        conditions += " emp.contractor = %(contractor)s and"
    return conditions, filters