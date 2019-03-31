// Copyright (c) 2019, Starboxes India and contributors
// For license information, please see license.txt

frappe.ui.form.on('Manual Attendance Correction', {
	validate: function(frm){
		frm.trigger("attendance_date")
		frm.trigger("out_date")
		frm.set_value("status","Applied")
		frm.set_df_property('status', 'read_only', 1);
		// if(frappe.user.has_role("Employee")) {
		// 	frm.set_value("status","Applied")
		// 	frm.set_df_property('status', 'read_only', 1);
		// 	}
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
	out_date: function(frm){
		if((frm.doc.out_date >= frappe.datetime.nowdate()) && frm.doc.out_date){
			validated = false
			frm.set_value("out_date","")
			frappe.throw("Attendance Can't be marked for Future Date")			
		}
		if(frm.doc.attendance_date && frm.doc.out_date){
			if(frm.doc.attendance_date > frm.doc.out_date){
				frm.set_value("out_date","")
				frappe.throw("Out Date must be greater than or Equal to Attendance Date ")
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
	},
	on_submit: function (frm) {
		if(frm.doc.status == "Approved"){
			frappe.call({
				"method": "starbox_custom.starbox_custom.doctype.manual_attendance_correction.manual_attendance_correction.update_attendance_time",
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
	}
})

