# -*- coding: utf-8 -*-
# Copyright (c) 2017, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import today

# @frappe.whitelist(allow_guest=True)
# def attendance():
#     userid = frappe.form_dict.get("userid")
#     employee = frappe.db.get_value("Employee", {
#         "biometric_id": userid})
#     if employee:
#         date = time.strftime("%Y-%m-%d", time.gmtime(
#             int(frappe.form_dict.get("att_time"))))
#         name, company = frappe.db.get_value(
#             "Employee", employee, ["employee_name", "company"])
#         attendance_id = frappe.db.get_value("Attendance", {
#             "employee": employee, "attendance_date": today()})
#     attendance = frappe.new_doc("Attendance")
#     attendance.update({
#         "employee": employee,
#         "attendance_date": time.strftime("%Y-%m-%d", time.gmtime(
#             int(frappe.form_dict.get("att_time")))),
#         "status": "Present",
#         "company": company
#     })
#     attendance.append("timetable", {
#         "type": frappe.form_dict.get("att_type"),
#         "time": time.strftime("%Y-%m-%d %X", time.gmtime(
#             int(frappe.form_dict.get("att_time"))))
#     })
#     attendance.save(ignore_permissions=True)
#     frappe.response.type = "text"
#     return "ok"
# restrict request list of IP addresses
# userid = frappe.form_dict.get("userid")
# employee = frappe.db.get_value("Employee", {
#     "biometric_id": userid})
# if employee:
#     date = time.strftime("%Y-%m-%d", time.gmtime(
#         int(frappe.form_dict.get("att_time"))))
#     name, company = frappe.db.get_value(
#         "Employee", employee, ["employee_name", "company"])
#     attendance_id = frappe.db.get_value("Attendance", {
#         "employee": employee, "attendance_date": date})
#     if attendance_id:
#         attendance = frappe.get_doc("Attendance", attendance_id)
#         out_time = time.strftime("%H:%M:%S", time.gmtime(
#             int(frappe.form_dict.get("att_time"))))
#         attendance.out_time = out_time
#         attendance.db_update()
#     else:
#         attendance = frappe.new_doc("Attendance")
#         in_time = time.strftime("%H:%M:%S", time.gmtime(
#             int(frappe.form_dict.get("att_time"))))
#         attendance.update({
#             "employee": employee,
#             "employee_name": name,
#             "attendance_date": date,
#             "status": "Present",
#             "in_time": in_time,
#             "company": company
#         })
#     attendance.save(ignore_permissions=True)
#     attendance.submit()
#     frappe.db.commit()
# frappe.response.type = "text"
# return "ok"

@frappe.whitelist()
def get_candidates():
    candidate_list = frappe.get_list("Closure", fields=["name", "passport_no"],limit=1)
    return candidate_list


@frappe.whitelist()
def add_customer(doc, method):
    customer = frappe.db.get_value("User", {"email": frappe.session.user},
                                   ["customer"])
    doc.customer = customer


# @frappe.whitelist(allow_guest=True)
# def update_leave_application():
#     employees = frappe.get_all('Employee')
#     for employee in employees:
#         attendance = frappe.db.get_all('Attendance', fields={'employee', 'attendance_date', 'status'}, filters={
#             'attendance_date': today(), 'employee': employee.name})
#         if not attendance:
#             lap = frappe.new_doc("Leave Application")
#             lap.leave_type = "Leave Without Pay"
#             lap.status = "Approved"
#             lap.from_date = today()
#             lap.to_date = today()
#             lap.employee = employee.name
#             lap.leave_approver = "Administrator"
#             lap.posting_date = today()
#             lap.company = frappe.db.get_value(
#                 "Employee", employee.name, "company")
#             lap.save(ignore_permissions=True)
#             lap.submit()
#             frappe.db.commit()

@frappe.whitelist()
def create_sales_order(closure):
    doc = frappe.get_doc("Closure", closure)

    item_candidate_id = frappe.db.get_value(
        "Item", {"name": doc.name + "_Candidate"})
    if item_candidate_id:
        pass
    else:
        if doc.candidate_payment_applicable:
            item = frappe.new_doc("Item")
            item.standard_rate = doc.candidate_sc
            item.payment_type = "Candidate"
            item.item_code = doc.name + "_Candidate"
            item.item_name = doc.name1
            item.item_group = "Recruitment"
            item.stock_uom = "Nos"
            item.description = doc.customer
            item.insert()
            item.save(ignore_permissions=True)

            so = frappe.new_doc("Sales Order")
            so.customer = doc.customer
            so.payment_type = "Candidate"
            so.append("items", {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "description": item.description,
                "uom": item.stock_uom,
                "rate": item.standard_rate,
                "delivery_date": today()
            })
            so.insert()
            so.submit()
            so.save(ignore_permissions=True)

    item_client_id = frappe.db.get_value(
        "Item", {"name": doc.name + "_Client"})

    if item_client_id:
        pass
    else:
        if doc.client_payment_applicable:
            item = frappe.new_doc("Item")
            item.standard_rate = doc.client_sc
            item.payment_type = "Client"
            item.item_code = doc.name + "_Client"
            item.item_name = doc.name1
            item.item_group = "Recruitment"
            item.stock_uom = "Nos"
            item.description = doc.customer
            item.save(ignore_permissions=True)

            so = frappe.new_doc("Sales Order")
            so.customer = doc.customer
            so.payment_type = "Client"
            so.append("items", {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "description": item.description,
                "uom": item.stock_uom,
                "rate": item.standard_rate,
                "delivery_date": today()
            })
            so.insert()
            so.submit()
            so.save(ignore_permissions=True)


def update_status():
    projects = frappe.get_all('Project', fields={'name', 'status'})
    for project in projects:
        tasks = frappe.db.get_all('Task', fields={'name', 'project', 'status'}, filters={
            'project': project.name})
        if tasks:
            if any(task.status == 'Open' or task.status == 'Working' or task.status == 'Pending Review' or task.status == 'Overdue' for task in tasks):
                frappe.db.set_value(
                    "Project", project.name, "status", "Open")
            elif all(task.status == 'Cancelled' for task in tasks):
                frappe.db.set_value(
                    "Project", project.name, "status", "Cancelled")
            elif all(task.status == 'DnD' for task in tasks):
                frappe.db.set_value(
                    "Project", project.name, "status", "Completed")

    customers = frappe.get_all('Customer', fields={'name', 'status'})
    for customer in customers:
        projects = frappe.db.get_all('Project', fields={'name', 'customer', 'status'}, filters={
            'customer': customer.name})
        if projects:
            if all(project.status == 'Open' or project.status == 'Overdue' or project.status == 'DnD' for project in projects):
                frappe.db.set_value(
                    "Customer", customer.name, "status", "Open")
            else:
                frappe.db.set_value(
                    "Customer", customer.name, "status", "Active")


# @frappe.whitelist(allow_guest=True)
# def attendance():
#     global attendance_date, att_time
#     userid = frappe.form_dict.get("userid")
#     employee = frappe.db.get_value("Employee", {
#         "biometric_id": userid})
#     if employee:
#     	date = time.strftime("%Y-%m-%d", time.gmtime(
#             int(frappe.form_dict.get("att_time"))))

#         attendance_date = time.strftime("%Y-%m-%d %X", time.gmtime(
#             int(frappe.form_dict.get("att_time"))))

#         doc = frappe.get_doc("Employee", employee)
# 	query = """SELECT ro.name, ro.shift FROM `tabRoster` ro, `tabRoster Details` rod
# 		WHERE rod.parent = ro.name AND ro.from_date <= '%s' AND ro.to_date >= '%s'
# 		AND rod.employee = '%s' """ % (attendance_date, attendance_date, doc.employee)
# 	roster = frappe.db.sql(query, as_list=1)
# 	if len(roster) < 1:
# 		frappe.throw(("No Roster defined for {0} for date {1}").format(
# 			doc.employee, attendance_date))
# 	else:
# 		doc.shift = roster[0][1]

# 	shft = frappe.get_doc("Shift Details", doc.shift)
# 	att_date = datetime.strptime(
# 	    attendance_date, '%Y-%m-%d %H:%M:%S')

# 	if shft.in_out_required:
# 		shft_hrs = shft.hours_required_per_day.seconds

# 		if shft.in_time > shft.out_time:
# 			#this shows night shift
# 			if shft.next_day != 1:
# 				#this shows night shift is starting on previous day
# 				shft_indate = datetime.combine(
# 				    add_days(att_date, -1), datetime.min.time())
# 			else:
# 				shft_indate = datetime.combine(att_date, datetime.min.time())
# 		else:
# 			shft_indate = datetime.combine(att_date, datetime.min.time())

# 		shft_intime = shft_indate + timedelta(0, shft.in_time.seconds)
# 		shft_intime_max = shft_intime + \
# 		    timedelta(0, shft.delayed_entry_allowed_time.seconds)
# 		shft_intime_min = shft_intime - \
# 		    timedelta(0, shft.early_entry_allowed_time.seconds)

# 		if att_date >= shft_intime_min and att_date <= shft_intime_max:
# 			attendance = frappe.new_doc(
#                             "Attendance")
# 			intime = time.strftime("%H:%M:%S", time.gmtime(
# 				int(frappe.form_dict.get("att_time"))))
# 			attendance.update({
# 				"employee": employee,
# 				"employee_name": doc.employee_name,
# 				"attendance_date": date,
# 				"status": "Present",
# 				"in_time": intime,
# 				"company": doc.company
# 			})
# 			attendance.save(
#                             ignore_permissions=True)
# 			frappe.response.type = "text"
# 			return "ok"
# 		else:
#     		frappe.response.type = "text"
#     		return "ok"
