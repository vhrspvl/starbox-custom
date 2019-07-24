// Copyright (c) 2019, Starboxes India and contributors
// For license information, please see license.txt

frappe.ui.form.on('Fetch From Machine', {
	refresh: function (frm) {
		frm.disable_save()
	},
	fetch: function (frm) {
		frappe.call({
			method: "starbox_custom.utils.get_punch_from_machine",
			args: {
				"from_date": frm.doc.from_date,
				"to_date": frm.doc.to_date,
				"bioip": frm.doc.ip
			},
			freeze: true,
			freeze_message: "Fetching",
			callback: function (r) {
				if (r) {
					frappe.msgprint(r);
				}
			}
		})

	}
});
