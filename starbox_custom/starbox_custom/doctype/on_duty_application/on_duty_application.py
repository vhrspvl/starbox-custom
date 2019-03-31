# -*- coding: utf-8 -*-
# Copyright (c) 2019, Starboxes India and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime,timedelta
from frappe import _
from frappe.utils import today,flt,add_days,date_diff,getdate,cint,formatdate, getdate, get_link_to_form, \
    comma_or, get_fullname

class LeaveApproverIdentityError(frappe.ValidationError): pass
class OverlapError(frappe.ValidationError): pass
class InvalidApproverError(frappe.ValidationError): pass
class AttendanceAlreadyMarkedError(frappe.ValidationError): pass    

class OnDutyApplication(Document):
    # def autoname(self):
    #     self.name = self.employee_name+"/"+self.from_date
    def on_submit(self):
        if self.status == "Applied":
            frappe.throw(_("Only Applications with status 'Approved' and 'Rejected' can be submitted"))

    def validate(self):
        self.validate_approver()
        self.validate_od_overlap()	

    def validate_approver(self):
        if not frappe.session.user == 'hr.hdi@hunterdouglas.asia':
            employee = frappe.get_doc("Employee", self.employee)
            approvers = [l.leave_approver for l in employee.get("leave_approvers")]

            if len(approvers) and self.approver not in approvers:
                frappe.throw(_("Approver must be one of {0}")
                    .format(comma_or(approvers)), InvalidApproverError)

            elif self.approver and not frappe.db.sql("""select name from `tabHas Role`
                where parent=%s and role='Leave Approver'""", self.approver):
                frappe.throw(_("{0} ({1}) must have role 'Approver'")\
                    .format(get_fullname(self.approver), self.approver), InvalidApproverError)

            elif self.docstatus==0 and len(approvers) and self.approver != frappe.session.user:
                self.status = 'Applied'
                
            elif self.docstatus==1 and len(approvers) and self.approver != frappe.session.user:
                frappe.throw(_("Only the selected Approver can submit this Application"),
                    LeaveApproverIdentityError)
    
    def validate_od_overlap(self):
        if not self.name:
            # hack! if name is null, it could cause problems with !=
            self.name = "New On Duty Application"

        for d in frappe.db.sql("""
            select
                name, on_duty_type, posting_date, from_date, to_date, total_number_of_days, half_day_date
            from `tabOn Duty Application`
            where employee = %(employee)s and docstatus < 2 and status in ("Open","Applied", "Approved")
            and to_date >= %(from_date)s and from_date <= %(to_date)s
            and name != %(name)s""", {
                "employee": self.employee,
                "from_date": self.from_date,
                "to_date": self.to_date,
                "name": self.name
            }, as_dict = 1):

            if cint(self.half_day)==1 and getdate(self.half_day_date) == getdate(d.half_day_date) and (
                flt(self.total_number_of_days)==0.5
                or getdate(self.from_date) == getdate(d.to_date)
                or getdate(self.to_date) == getdate(d.from_date)):

                total_leaves_on_half_day = self.get_total_leaves_on_half_day()
                if total_leaves_on_half_day >= 1:
                    self.throw_overlap_error(d)
            else:
                self.throw_overlap_error(d)

    def throw_overlap_error(self, d):
        msg = _("Employee {0} has already applied for {1} between {2} and {3}").format(self.employee,
            d['on_duty_type'], formatdate(d['from_date']), formatdate(d['to_date'])) \
            + """ <br><b><a href="#Form/On Duty Application/{0}">{0}</a></b>""".format(d["name"])
        frappe.throw(msg, OverlapError)

    def get_total_leaves_on_half_day(self):
        leave_count_on_half_day_date = frappe.db.sql("""select count(name) from `tabOn Duty Application`
            where employee = %(employee)s
            and docstatus < 2
            and status in ("Open","Applied", "Approved")
            and half_day = 1
            and half_day_date = %(half_day_date)s
            and name != %(name)s""", {
                "employee": self.employee,
                "half_day_date": self.half_day_date,
                "name": self.name
            })[0][0]

        return leave_count_on_half_day_date * 0.5
    



@frappe.whitelist()
def get_number_of_leave_days(employee, from_date, to_date,from_date_session=None,  to_date_session=None, date_dif=None):
    number_of_days = 0
    if from_date == to_date:
        if from_date_session != 'Full Day':
            number_of_days = 0.5
        else:
            number_of_days = 1
    else:
        if from_date_session == "Full Day" and to_date_session == "Full Day":
            number_of_days = flt(date_dif)
        if from_date_session == "Full Day" and to_date_session == "First Half":
            number_of_days = flt(date_dif) - 0.5
        if from_date_session == "Second Half" and to_date_session == "Full Day":
            number_of_days = flt(date_dif) - 0.5
        if from_date_session == "Second Half" and to_date_session == "First Half":
            number_of_days = flt(date_dif) - 1
    return number_of_days

@frappe.whitelist()
def attendance(employee,from_date,to_date):
    # frappe.errprint("hi")
    att = frappe.db.sql("""select * from  `tabAttendance` where employee = %s and attendance_date between %s and %s""", (employee,from_date,to_date), as_dict=True)  
    for i in att:
        i.update({
            "attendance_type":"OD"
        })
        i.save(ignore_permissions=True)
        frappe.db.commit()
    return "ok"



    # def on_cancel(self):
    #     attendance_list = frappe.get_list("Attendance", {'employee': self.employee, 'on_duty_application': self.name})
    #     if attendance_list:
    #         for attendance in attendance_list:
    #             attendance_obj = frappe.get_doc("Attendance", attendance['name'])
    #             attendance_obj.cancel()


@frappe.whitelist()
def on_duty_mark(doc,method):
    if doc.status == "Approved": 
        request_days = date_diff(doc.to_date, doc.from_date) +1
        for number in range(request_days):
            attendance_date = add_days(doc.from_date, number)
            skip_attendance = validate_if_attendance_not_applicable(doc.employee,attendance_date)
            if not skip_attendance:
                att = frappe.db.exists("Attendance",{"employee":doc.employee,"attendance_date":attendance_date})
                if doc.half_day and date_diff(getdate(doc.half_day_date), getdate(attendance_date)) == 0:
                    status = "Half Day"
                else:
                    status = "On Duty"
                if att:
                    attendance = frappe.get_doc("Attendance",att)
                    attendance.update({
                    "status":status,
                    "on_duty_application":doc.name
                    })
                    attendance.db_update()
                    frappe.db.commit()
                else:
                    attendance = frappe.new_doc("Attendance")
                    attendance.employee = doc.employee
                    attendance.employee_name = doc.employee_name
                    attendance.status = status
                    attendance.attendance_date = attendance_date
                    attendance.late_in = "00:00:0"
                    attendance.work_time = "00:00:0"
                    attendance.early_out = "00:00:0"
                    attendance.overtime = "00:00:0"
                    attendance.on_duty_application = doc.name
                    attendance.company = doc.company
                    attendance.save(ignore_permissions=True)
                    attendance.submit()



@frappe.whitelist()
def check_attendance(employee, from_date, to_date):
    if employee:        
        attendance = frappe.db.sql("""select status,attendance_date from `tabAttendance`
                    where employee = %s and attendance_date between %s and %s
                    and docstatus = 1""", (employee, from_date, to_date), as_dict=True)
        return attendance
