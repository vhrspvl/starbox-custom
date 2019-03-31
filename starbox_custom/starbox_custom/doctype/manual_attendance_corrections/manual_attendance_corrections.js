// Copyright (c) 2019, Starboxes India and contributors
// For license information, please see license.txt

frappe.ui.form.on('Manual Attendance Corrections', {
	refresh: function (frm) {
		frm.disable_save();
	},
	employee: function (frm) {
		frappe.call({
			"method": "frappe.client.get",
			args: {
				doctype: "Employee",
				name: frm.doc.employee
			},
			callback: function (r) {
				if (r.message) {
					frm.set_value("employee_name", r.message.employee_name)
				}
			}
		})
	},
	process: function (frm) {
		frappe.call({
			"method": "starbox_custom.starbox_custom.doctype.manual_attendance_corrections.manual_attendance_corrections.update_attendance_time",
			args: {
				"employee": frm.doc.employee,
				"attendance_date": frm.doc.attendance_date,
				"in_time": frm.doc.in_time,
				"out_time": frm.doc.out_time,
				"out_date": frm.doc.out_date
			},
			callback: function (r) {
				if (r.message) {
					frappe.msgprint("Updated")
				}
			}
		})
	}
})
