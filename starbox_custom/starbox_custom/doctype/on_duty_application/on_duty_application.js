// Copyright (c) 2019, Starboxes India and contributors
// For license information, please see license.txt

frappe.ui.form.on('On Duty Application', {

		from_date: function (frm) {
			frm.trigger("calculate_total_days");
		},
		to_date: function (frm) {
			frm.trigger("calculate_total_days");
		},
		to_date_session: function (frm) {
			frm.trigger("calculate_total_days")
		},
		from_date_session: function (frm) {
			frm.trigger("calculate_total_days")
			if (frm.doc.from_date == frm.doc.to_date) {
				frm.set_value("to_date_session", frm.doc.from_date_session)
			}
		},
		to_date_session: function (frm) {
			frm.trigger("calculate_total_days")
			if (frm.doc.from_date == frm.doc.to_date) {
				frm.set_value("from_date_session", frm.doc.to_date_session)
			}
		},
		calculate_total_days: function (frm) {
			if (frm.doc.from_date && frm.doc.to_date && frm.doc.employee) {
				var date_dif = frappe.datetime.get_diff(frm.doc.to_date, frm.doc.from_date) + 1
				return frappe.call({
					"method": 'starbox_custom.starbox_custom.doctype.on_duty_application.on_duty_application.get_number_of_leave_days',
					args: {
						"employee": frm.doc.employee,
						"from_date": frm.doc.from_date,
						"from_date_session": frm.doc.from_date_session,
						"to_date": frm.doc.to_date,
						"to_date_session": frm.doc.to_date_session,
						"date_dif": date_dif
					},
					callback: function (r) {
						if (r.message) {
							frm.set_value('total_number_of_days', r.message);
							frm.trigger("get_leave_balance");
						}
					}
				});
			}
		},
		validate: function (frm) {
			frappe.call({
				"method": 'starbox_custom.starbox_custom.doctype.on_duty_application.on_duty_application.check_attendance',
				args: {
					"employee": frm.doc.employee,
					"from_date": frm.doc.from_date,
					"to_date": frm.doc.to_date
				},
				callback: function (r) {
					if (r.message) {
						$.each(r.message, function (i, d) {
							if (d.status == "Present") {
								frappe.msgprint("Attendance already Marked as Present for " + d.attendance_date)
								frappe.validated = false;
							} else if (d.status == "Half Day") {
								if (frm.doc.from_date == frm.doc.to_date) {
									if (frm.doc.from_date_session == "Full Day") {
										frappe.msgprint("Attendance already Marked as Half Day for " + d.attendance_date)
										frappe.validated = false;
									}
								} else if (frm.doc.from_date != frm.doc.to_date) {
									if ((frm.doc.from_date_session == "Full Day") || (frm.doc.to_date_session == "Full Day")) {
										frappe.msgprint("Attendance already Marked as Half Day for " + d.attendance_date)
										frappe.validated = false;
									}
	
								}
							}
						})
					}
				}
			});
		},
		on_submit:function(frm)
		{
			frappe.call({
				"method": 'starbox_custom.starbox_custom.doctype.on_duty_application.on_duty_application.attendance',
				args: {
					"employee":frm.doc.employee,
					"from_date":frm.doc.from_date,
					"to_date": frm.doc.to_date,
				},
				callback:function(r){
					frappe.msgprint(__("Approved successful"));
				}
			});
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
		after_save: function(frm){
			if(frm.doc.is_from_ar && frm.doc.status == "Applied"){
				frappe.set_route("query-report", "Attendance Recapitulation")
			}
		},
		refresh: function(frm){
			if(frm.doc.is_from_ar){
				frm.add_custom_button(__('Back'), function () {
					frappe.set_route("query-report", "Attendance Recapitulation")
				});
			}
		},
	});
