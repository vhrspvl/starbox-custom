// Copyright (c) 2019, Starboxes India and contributors
// For license information, please see license.txt

frappe.ui.form.on('Movement Register', {
	refresh: function(frm){
		if(frm.doc.is_from_ar){
			frm.add_custom_button(__('Back'), function () {
				frappe.set_route("query-report", "Attendance Recapitulation")
			});
		}
	},
	employee: function(frm){
		frm.trigger("set_leave_approver")
	},
	set_leave_approver: function(frm) {
		if(frm.doc.employee) {
				// server call is done to include holidays in leave days calculations
			return frappe.call({
				method: 'erpnext.hr.doctype.leave_application.leave_application.get_leave_approver',
				args: {
					"employee": frm.doc.employee,
				},
				callback: function(r) {
					if (r && r.message) {
						frm.set_value('approver', r.message);
					}
				}
			});
		}
	},
	validate: function(frm){
		if(frm.doc.from_time && frm.doc.to_time){
			frappe.call({
				"method": "starbox_custom.starbox_custom.doctype.movement_register.movement_register.check_count",
				args:{
					"employee": frm.doc.employee,
					"from_time": frm.doc.from_time,
					"to_time": frm.doc.to_time
				},
				callback: function(r){
					if(r.message == "NA"){
						frappe.validated = false
						frappe.msgprint("You are Already Reached the Maximum Count")
					}
				}
			})
		}
	},
	after_save: function(frm){
		if(frm.doc.is_from_ar && (frm.doc.approver != frappe.session.user)){
			frappe.set_route("query-report", "Attendance Recapitulation")
		}
	}
});
