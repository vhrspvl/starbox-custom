# -*- coding: utf-8 -*-
# Copyright (c) 2019, Starboxes India and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class ShiftAssignment(Document):
    def autoname(self):
        self.name = self.employee + "/" + self.from_date + "/" + self.to_date
