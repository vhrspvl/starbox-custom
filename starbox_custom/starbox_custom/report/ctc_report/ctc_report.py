# Copyright (c) 2013, Starboxes India and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate, today,nowdate
from frappe import msgprint, _


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns(filters)
    date = filters.get("date")

    data = []
    row = []
    for att in frappe.get_list('Attendance', fields=['name', 'employee'], filters={'attendance_date': date, 'docstatus': 1, 'status': 'Present'}):
        emp = frappe.db.get_value("Employee", {'employee': att.employee}, [
                                  'name', 'employee_name', 'designation', 'department'], as_dict=True)
        row = [att.name, emp.employee_name, emp.designation, emp.department]
        ss_base = frappe.db.get_value("Salary Structure Employee", {'employee': emp.name}, [
            'base'], as_dict=True)

	if ss_base:
		if ss_base.base:
			row += [ss_base.base]
		else:
			row += [""]

    data.append(row)

    return columns, data


def get_columns(attendance):
    columns = [
        _("Employee") + ":Link/Employee:90",
        _("Employee Name") + "::150",
        _("Designation") + "::180",
        _("Department") + "::180",
        _("Gross") + ":Currency:180"
    ]
    return columns


def get_attendance(filters):
    filters.update({"from_date": filters.get("date_range")[
                   0], "to_date": filters.get("date_range")[1]})

    conditions, filters = get_conditions(filters)
    # attendance = frappe.db.sql(
    # 	"""select
    # """)
    # attendance = frappe.db.sql(
    # 	"""select emp.name,emp.designation,emp.department,sse.base
    # 	from `tabEmployee` emp,`tabSalary Structure Employee` sse
    # 	where emp.status='Active' and sse.employee =
    # 	order by employee""" % date as_dict=1)


def get_conditions(filters):
    conditions = ""
    if filters.get("date_range"):
        conditions += " and attendance_date between %(from_date)s and %(to_date)s"
    if filters.get("company"):
        conditions += " and company = %(company)s"
    if filters.get("employee"):
        conditions += " and employee = %(employee)s"

    return conditions, filters
