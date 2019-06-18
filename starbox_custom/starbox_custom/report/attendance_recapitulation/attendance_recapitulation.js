// Copyright (c) 2016, Starboxes India and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Attendance Recapitulation"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_start(),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee"
		},
		{
			"fieldname": "employment_type",
			"label": __("Employment Type"),
			"fieldtype": "Link",
			"options": "Employment Type"
		},
		{
			"fieldname": "department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department"
		},
		// {
		// 	"fieldname": "user",
		// 	"label": __("Employee"),
		// 	"fieldtype": "Data",
		// 	"default": frappe.session.user,
		// 	"hidden": 1
		// },
	],
	"formatter": function (value, row, column, data, default_formatter) {
		
		if (column.id == "Status") {
			value = data.Status
			if(value == "Absent" || value == "Miss Punch"){
				column.link_onclick =
					"frappe.query_reports['Attendance Recapitulation'].open_att_adjust(" + JSON.stringify(data) + ")";
			}else{
				column.link_onclick =
				"frappe.query_reports['Attendance Recapitulation'].open_att_adjust1(" + JSON.stringify(data) + ")";
			}
		}
		value = default_formatter(value, row, column, data);
		return value
	},
		"open_att_adjust": function (data) {
			var d1 = new frappe.ui.Dialog({
				'fields': [
					{ fieldtype: "Button", fieldname: "apply_od", label: __("Apply OD"), reqd: 0 },
					{ fieldtype: "Button", fieldname: "apply_leave", label: __("Apply Leave"), reqd: 0 },
					{ fieldtype: "Button", fieldname: "apply_mr", label: __("Apply Movement Register"), reqd: 0 },
					{ fieldtype: "Button", fieldname: "apply_mp", label: __("Apply Miss Punch"), reqd: 0 },
	
				],
				primary_action: function () {
					var status = d1.get_values()
				}
			})
			d1.fields_dict.apply_od.input.onclick = function () {
				frappe.set_route("Form", "On Duty Application", "New On Duty Application", { "is_from_ar": "Yes","employee":data['Employee'] })
			}
			d1.fields_dict.apply_leave.input.onclick = function () {
				frappe.set_route("Form", "Leave Application", "New Leave Application", { "is_from_ar": "Yes","employee":data['Employee'] })
			}
			d1.fields_dict.apply_mr.input.onclick = function () {
				frappe.set_route("Form", "Movement Register", "New Movement Register", { "is_from_ar": "Yes","employee":data['Employee'] })
			}
			d1.fields_dict.apply_mp.input.onclick = function () {
				var in_time = "00:00:00"  
				var out_time = "00:00:00"
				if(data['In Time'] != "-"){
					in_time = data['In Time']
				}
				if(data['Out Time'] != "-"){
					out_time = data['Out Time']
				}				
				attendance_date = data["Attendance Date"]
				frappe.set_route("Form", "Manual Attendance Correction", "New Manual Attendance Correction", { "is_from_ar": "Yes","employee":data['Employee'],"in_time":in_time,"out_time": out_time,"attendance_date":attendance_date })
			}
			d1.show();
		},
		"open_att_adjust1": function (data) {
			frappe.msgprint("Attendance Already Marked,Contact HR")
		},
	}