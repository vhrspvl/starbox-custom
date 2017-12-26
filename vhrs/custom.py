# -*- coding: utf-8 -*-
# Copyright (c) 2017, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import today


@frappe.whitelist()
def get_candidates(customer):
    candidate_list = frappe.get_list("Closure", fields=["name", "passport_no"], filters={
        "customer": customer})
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
