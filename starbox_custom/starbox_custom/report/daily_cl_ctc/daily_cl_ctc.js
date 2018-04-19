// Copyright (c) 2016, Starboxes India and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily CL CTC"] = {
	"filters": [
		{
			"fieldname": "date",
			"label": __("Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "contractor",
			"label": __("Contractor"),
			"fieldtype": "Link",
			"options": "Contractor"
		},
	]
}
