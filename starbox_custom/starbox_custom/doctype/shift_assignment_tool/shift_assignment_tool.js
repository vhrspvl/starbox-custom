// Copyright (c) 2019, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Shift Assignment Tool', {
	refresh: function (frm) {
		frm.disable_save();
	},
	contractor: function (frm) {
		if (frm.doc.contractor) {
			frm.clear_table("shift_assignment_tool_kit")
			refresh_field("shift_assignment_tool_kit")
			frappe.call({
				"method": "frappe.client.get_list",
				args: {
					"doctype": "Employee",
					filters: {
						"contractor": frm.doc.contractor,
						"status": "Active"
					},
					limit_page_length: 100,
				},
				callback: function (r) {
					$.each(r.message, function (i, d) {
						if (r.message) {
							frappe.call({
								"method": "frappe.client.get",
								args: {
									"doctype": "Employee",
									"name": d.name
								},
								freeze: true,
								freeze_message: "Fetching....",
								callback: function (r) {
									if (frm.doc.contractor && frm.doc.department && frm.doc.designation) {
										if ((frm.doc.designation == r.message.designation) && (frm.doc.contractor == r.message.contractor) && (frm.doc.department == r.message.department)) {
											var row = frappe.model.add_child(frm.doc, "Shift Assignment Tool Kit", "shift_assignment_tool_kit");
											row.employee = r.message.biometric_id
											row.employee_name = r.message.employee_name
											refresh_field("shift_assignment_tool_kit")
										}
									} else if (frm.doc.department && frm.doc.designation) {
										if ((frm.doc.designation == r.message.designation) && (frm.doc.department == r.message.department)) {
											var row = frappe.model.add_child(frm.doc, "Shift Assignment Tool Kit", "shift_assignment_tool_kit");
											row.employee = r.message.biometric_id
											row.employee_name = r.message.employee_name
											refresh_field("shift_assignment_tool_kit")
										}
									} else if (frm.doc.contractor && frm.doc.designation) {
										if ((frm.doc.designation == r.message.designation) && (frm.doc.contractor == r.message.contractor)) {
											var row = frappe.model.add_child(frm.doc, "Shift Assignment Tool Kit", "shift_assignment_tool_kit");
											row.employee = r.message.biometric_id
											row.employee_name = r.message.employee_name
											refresh_field("shift_assignment_tool_kit")
										}
									} else if (frm.doc.contractor) {
										if (frm.doc.contractor == r.message.contractor) {
											var row = frappe.model.add_child(frm.doc, "Shift Assignment Tool Kit", "shift_assignment_tool_kit");
											row.employee = r.message.biometric_id
											row.employee_name = r.message.employee_name
											refresh_field("shift_assignment_tool_kit")
										}
									}

								}
							})
						}
					})

				}

			})
		}
	},
	designation: function (frm) {
		frm.clear_table("shift_assignment_tool_kit")
		refresh_field("shift_assignment_tool_kit")
		if (frm.doc.designation) {
			frappe.call({
				"method": "frappe.client.get_list",
				args: {
					"doctype": "Employee",
					filters: {
						"designation": frm.doc.designation,
						"status": "Active"
					},
					limit_page_length: 100,
				},
				callback: function (r) {
					$.each(r.message, function (i, d) {
						if (r.message) {
							frappe.call({
								"method": "frappe.client.get",
								args: {
									"doctype": "Employee",
									"name": d.name
								},
								freeze: true,
								freeze_message: "Fetching....",
								callback: function (r) {
									if (frm.doc.contractor && frm.doc.department && frm.doc.designation) {
										if ((frm.doc.designation == r.message.designation) && (frm.doc.contractor == r.message.contractor) && (frm.doc.department == r.message.department)) {
											var row = frappe.model.add_child(frm.doc, "Shift Assignment Tool Kit", "shift_assignment_tool_kit");
											row.employee = r.message.biometric_id
											row.employee_name = r.message.employee_name
											refresh_field("shift_assignment_tool_kit")
										}
									} else if (frm.doc.department && frm.doc.designation) {
										if ((frm.doc.designation == r.message.designation) && (frm.doc.department == r.message.department)) {
											var row = frappe.model.add_child(frm.doc, "Shift Assignment Tool Kit", "shift_assignment_tool_kit");
											row.employee = r.message.biometric_id
											row.employee_name = r.message.employee_name
											refresh_field("shift_assignment_tool_kit")
										}
									} else if (frm.doc.contractor && frm.doc.designation) {
										if ((frm.doc.designation == r.message.designation) && (frm.doc.contractor == r.message.contractor)) {
											var row = frappe.model.add_child(frm.doc, "Shift Assignment Tool Kit", "shift_assignment_tool_kit");
											row.employee = r.message.biometric_id
											row.employee_name = r.message.employee_name
											refresh_field("shift_assignment_tool_kit")
										}
									}
									// else if (frm.doc.designation) {
									// 	if (frm.doc.designation == r.message.designation) {
									// 		var row = frappe.model.add_child(frm.doc, "Shift Assignment Tool Kit", "shift_assignment_tool_kit");
									// 		row.employee = r.message.biometric_id
									// 		row.employee_name = r.message.employee_name
									// 		refresh_field("shift_assignment_tool_kit")
									// 	}
									// }

								}
							})
						}
					})

				}

			})
		}
	},
	department: function (frm) {
		frm.clear_table("shift_assignment_tool_kit")
		refresh_field("shift_assignment_tool_kit")
		if (frm.doc.department) {
			frappe.call({
				"method": "frappe.client.get_list",
				args: {
					"doctype": "Employee",
					filters: {
						"department": frm.doc.department,
						"status": "Active"
					},
					limit_page_length: 100,
				},
				callback: function (r) {
					$.each(r.message, function (i, d) {
						if (r.message) {
							frappe.call({
								"method": "frappe.client.get",
								args: {
									"doctype": "Employee",
									"name": d.name
								},
								freeze: true,
								freeze_message: "Fetching....",
								callback: function (r) {
									if (frm.doc.contractor && frm.doc.department && frm.doc.designation) {
										if ((frm.doc.designation == r.message.designation) && (frm.doc.contractor == r.message.contractor) && (frm.doc.department == r.message.department)) {
											var row = frappe.model.add_child(frm.doc, "Shift Assignment Tool Kit", "shift_assignment_tool_kit");
											row.employee = r.message.biometric_id
											row.employee_name = r.message.employee_name
											refresh_field("shift_assignment_tool_kit")
										}
									} else if (frm.doc.department && frm.doc.designation) {
										if ((frm.doc.designation == r.message.designation) && (frm.doc.department == r.message.department)) {
											var row = frappe.model.add_child(frm.doc, "Shift Assignment Tool Kit", "shift_assignment_tool_kit");
											row.employee = r.message.biometric_id
											row.employee_name = r.message.employee_name
											refresh_field("shift_assignment_tool_kit")
										}
									} else if (frm.doc.contractor && frm.doc.designation) {
										if ((frm.doc.designation == r.message.designation) && (frm.doc.contractor == r.message.contractor)) {
											var row = frappe.model.add_child(frm.doc, "Shift Assignment Tool Kit", "shift_assignment_tool_kit");
											row.employee = r.message.biometric_id
											row.employee_name = r.message.employee_name
											refresh_field("shift_assignment_tool_kit")
										}
									} else if (frm.doc.department) {
										if (frm.doc.department == r.message.department) {
											var row = frappe.model.add_child(frm.doc, "Shift Assignment Tool Kit", "shift_assignment_tool_kit");
											row.employee = r.message.biometric_id
											row.employee_name = r.message.employee_name
											refresh_field("shift_assignment_tool_kit")
										}
									}

								}
							})
						}
					})

				}

			})
		}
	},
	employee: function (frm) {
		if (!frm.doc.choose_multiple_employee) {
			frm.clear_table("shift_assignment_tool_kit")
			refresh_field("shift_assignment_tool_kit")
		}
		if (frm.doc.employee) {
			frappe.call({
				"method": "frappe.client.get",
				args: {
					"doctype": "Employee",
					"name": frm.doc.employee
				},
				freeze: true,
				freeze_message: "Fetching....",
				callback: function (r) {
					if (r.message) {
						var row = frappe.model.add_child(frm.doc, "Shift Assignment Tool Kit", "shift_assignment_tool_kit");
						row.employee = r.message.biometric_id
						row.employee_name = r.message.employee_name
						refresh_field("shift_assignment_tool_kit")

					}

				}
			})

		}

	},
	from_date: function (frm, cdt, cdn) {
		var grid = frm.fields_dict["shift_assignment_tool_kit"].grid;
		if (frm.doc.from_date != "") {
			if (grid.get_selected_children().length !== 0) {
				$.each(grid.get_selected_children(), function (i, d) {
					d.from_date = frm.doc.from_date;
				})
				refresh_field("shift_assignment_tool_kit")
			} else if (frm.doc.from_date) {
				frm.set_value("from_date", "")
				frappe.msgprint("Select the Row")
			}
		}
		if (frm.doc.to_date) {
			if (frm.doc.from_date > frm.doc.to_date) {
				frappe.msgprint("From Date Cannot Greater than To Date")
				frm.set_value("from_date", "")
			}
		}
	},
	to_date: function (frm, cdt, cdn) {
		var grid = frm.fields_dict["shift_assignment_tool_kit"].grid;
		if (frm.doc.to_date != "") {
			if (grid.get_selected_children().length !== 0) {
				$.each(grid.get_selected_children(), function (i, d) {
					d.to_date = frm.doc.to_date;
				})
				refresh_field("shift_assignment_tool_kit")
			} else if (frm.doc.to_date) {
				frm.set_value("to_date", "")
				frappe.msgprint("Select the Row")
			}
		}
		if (frm.doc.from_date) {
			if (frm.doc.from_date > frm.doc.to_date) {
				frappe.msgprint("To Date Cannot Lesser than From Date")
				frm.set_value("to_date", "")
			}
		}
	},
	shift: function (frm, cdt, cdn) {
		var grid = frm.fields_dict["shift_assignment_tool_kit"].grid;
		if (frm.doc.shift != "") {
			if (grid.get_selected_children().length !== 0) {
				$.each(grid.get_selected_children(), function (i, d) {
					d.shift = frm.doc.shift;
				})
				refresh_field("shift_assignment_tool_kit")
			} else if (frm.doc.shift) {
				frm.set_value("shift", "")
				frappe.msgprint("Select the Row")
			}
		}
		// frappe.call({
		// 	"method": "frappe.client.get",
		// 	args: {
		// 		"doctype": "Shift",
		// 		"name": frm.doc.shift
		// 	},
		// 	callback: function (r) {
		// 		var shift_time = r.message.in_time + "-" + r.message.out_time;
		// 		frm.set_value("shift_time", shift_time)
		// 	}
		// })
	},
	assign: function (frm, cdt, cdn) {
		if (!frm.doc.from_date) {
			frappe.msgprint("Choose the From Date")
		} else if (!frm.doc.to_date) {
			frappe.msgprint("Choose the To Date")
		} else if (!frm.doc.shift) {
			frappe.msgprint("Choose the Shift")
		} else if (frm.doc.from_date && frm.doc.to_date && frm.doc.shift) {
			frappe.call({
				"method": "starbox_custom.starbox_custom.doctype.shift_assignment_tool.shift_assignment_tool.update_shift",
				args: {
					"shift_assignment_tool_kit": frm.doc.shift_assignment_tool_kit,
				},
				freeze: true,
				freeze_message: "Fetching....",
				callback: function (r) {
					frappe.msgprint("Updated")
					setTimeout(function () { location.reload() }, 1000);
				}
			})
		}
	},
});
