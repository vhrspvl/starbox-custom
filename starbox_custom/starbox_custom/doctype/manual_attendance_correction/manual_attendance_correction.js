// Copyright (c) 2019, Starboxes India and contributors
// For license information, please see license.txt

frappe.ui.form.on('Manual Attendance Correction', {
	validate: function(frm){
		frm.trigger("attendance_date")
		// if(frm.doc.is_from_ar){
		// 	frm.set_value("status","Approved")
		// 	frm.set_df_property('status', 'read_only', 1);
		// }		
		// if(frappe.user.has_role("Employee")) {
			// frm.set_value("status","Applied")
			// frm.set_df_property('status', 'read_only', 1);
			// }
		if(frm.doc.attendance_date < frappe.datetime.nowdate() ){
			frappe.call({
				"method": "starbox_custom.starbox_custom.doctype.manual_attendance_correction.manual_attendance_correction.check_attendance",
				args:{
					"attendance_date":frm.doc.attendance_date,
					"employee": frm.doc.employee
				},
				callback: function(r){
					if(r.message != "OK"){
						if(r.message.in_time && r.message.out_time){
							validated = false;
							frappe.msgprint("Attendance Already Marked")
						}
					} else {
						frappe.msgprint("Miss Punch Applied Successfully")
					}
				}
			})
		}
	},
	attendance_date: function(frm){
		if((frm.doc.attendance_date >= frappe.datetime.nowdate()) && frm.doc.attendance_date){
			validated = false
			frm.set_value("attendance_date","")
			frappe.throw("Attendance Can't be marked for Future Date")			
		}
		if(frm.doc.out_date && frm.doc.attendance_date){
			if(frm.doc.attendance_date > frm.doc.out_date){
				frm.set_value("attendance_date","")
				frappe.throw("Attendance Date must be Lesser than or Equal to Out Date ")
			}
		}
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
	before_submit:function(frm){
		if(frappe.session.user != frm.doc.approver){
			frappe.validated = false;
			frappe.msgprint(__("The Selected Approver only can submit this Document"));
		}
	}, 
	onload: function(frm){
		if(frappe.session.user == frm.doc.approver){
			frm.set_df_property('status', 'read_only', 0);
		}
	},
	on_submit: function (frm) {
		if(frappe.session.user == frm.doc.approver || frappe.user.has_role("System Manager")){
			frm.set_value("status", "Approved")
			if(frm.doc.status){
				frappe.call({
					"method": "starbox_custom.starbox_custom.doctype.manual_attendance_correction.manual_attendance_correction.update_attendance_time",
					args: {
						"employee": frm.doc.employee,
						"attendance_date": frm.doc.attendance_date,
						"in_time": frm.doc.in_time,
						"out_time": frm.doc.out_time,
					},
					callback: function (r) {
						if (r.message) {
							frappe.msgprint("Updated")
						}
					}
				})
			}
		}
	},
	// after_save: function(frm){
	// 	// if(frm.doc.is_from_ar && (frm.doc.approver != frappe.session.user)){
	// 	// 	frappe.set_route("query-report", "Attendance Recapitulation")
	// 	// }
	// },
	refresh: function(frm){
		if(frm.doc.is_from_ar){
			frm.add_custom_button(__('Back'), function () {
				frappe.set_route("query-report", "Attendance Recapitulation")
			});
		}
	},
})

