# -*- coding: utf-8 -*-
# Copyright (c) 2019, Starboxes India and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime,timedelta,date,time
from frappe.utils import (flt, getdate, get_first_day,get_last_day, add_months, add_days, formatdate)

class MovementRegister(Document):
    pass



@frappe.whitelist()
def check_count(employee, from_time):
    if employee:
        from_date = (datetime.strptime(str(from_time), '%Y-%m-%d %H:%M:%S')).date()
        first_date = get_first_day(from_date)
        last_date = get_last_day(from_date)
        count = 1
        mr_list = frappe.db.sql("""select name from `tabMovement Register`
                        where employee = %s """, (employee), as_dict=True)
        for mr in mr_list:
            doc = frappe.get_doc("Movement Register", mr.name)
            doc_date = (datetime.strptime(str(doc.from_time), '%Y-%m-%d %H:%M:%S')).date()
            if doc_date > first_date and doc_date < last_date:
                count += 1
        if count > 2:
            return "NA"
