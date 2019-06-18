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
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.id == "Status") {
			if (data["Status"] === "Present") {
				if (data["Remarks"] === "Failed Out Punch") {
					value = "<span style='color:dark-yellow!important;font-weight:bold'>" + value + "</span>";
				} else {
					value = "<span style='color:green!important;font-weight:bold'>" + value + "</span>";
				}
			}
			if (data["Status"] === "Absent") {
				value = "<span style='color:red!important;font-weight:bold'>" + value + "</span>";
			}

		}

		return value;
	}
}
