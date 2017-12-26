// Copyright (c) 2017, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('VHRS Changenote', {
	refresh: function (frm) {

	},
	test: function (frm) {
		frappe.prompt([
			{ 'fieldname': 'birth', 'fieldtype': 'DateRange', 'label': 'Birth Date', 'reqd': 1 }
		],
			function (values) {
				show_alert(values, 5);
			},
			'Age verification',
			'Subscribe me'
		)
	}
});
