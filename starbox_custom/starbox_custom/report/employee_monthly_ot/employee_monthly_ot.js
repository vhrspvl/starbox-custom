// Copyright (c) 2016, Minda Sai Pvt LTd and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee Monthly OT"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
    ],
}