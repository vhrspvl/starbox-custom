// Copyright (c) 2016, Starboxes India and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["CL CTC"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": [frappe.datetime.add_months(frappe.datetime.get_today())],
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": [frappe.datetime.add_months(frappe.datetime.get_today())],
			"reqd": 1
		},
	]
}