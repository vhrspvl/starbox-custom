// Copyright (c) 2016, Starboxes India and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee Day Attendance Report"] = {
	"filters": [
		{
			"fieldname": "date",
			"label": __("Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
	],
	"formatter": function (row, cell, value, columnDef, dataContext, default_formatter) {
		value = default_formatter(row, cell, value, columnDef, dataContext)
		if (columnDef.id == "Status") {
			if (dataContext["Status"] === "Present") {
				if (dataContext["Remarks"] === "Failed Out Punch") {
					value = "<span style='color:yellow!important;font-weight:bold'>" + value + "</span>";
				} else {
					value = "<span style='color:green!important;font-weight:bold'>" + value + "</span>";
				}
			}
			if (dataContext["Status"] === "Absent") {
				value = "<span style='color:red!important;font-weight:bold'>" + value + "</span>";
			}

		}

		return value;
	}
}
