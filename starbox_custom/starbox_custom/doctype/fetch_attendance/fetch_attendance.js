// Copyright (c) 2019, Starboxes India and contributors
// For license information, please see license.txt

frappe.ui.form.on('Fetch Attendance', {
	refresh:function(frm){
		frm.disable_save()
	},
	fetch: function(frm) {
		frappe.call({
			method:"starbox_custom.utils.fetch_from_ui",
			args:{
				"from_date":frm.doc.from_date,
				"to_date":frm.doc.to_date
			},
			freeze:true,
			freeze_message:"Fetching",
			callback:function(r){
				if(r){
					frappe.msgprint(__("Attendance Fetched"));
				}
			}
		})

	}
});