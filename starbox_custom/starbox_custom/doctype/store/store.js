// Copyright (c) 2019, Starboxes India and contributors
// For license information, please see license.txt

frappe.ui.form.on('Store Keeper', {
	refresh: function(frm) {

	},
	onload: function(frm) {
		frappe.call({
			"method": "frappe.client.get_list",
			args:{
				"doctype": "Stationery Item",
			},
			callback: function(r){
				if(r.message){
					$.each(r.message, function (i, d) {
						frappe.call({
							"method": "frappe.client.get",
							args:{
								"doctype": "Stationery Item",
								"name": d.name
							},
							callback: function(r){
								var row = frappe.model.add_child(frm.doc, "Store Child", "store_child");
								row.item_code = r.message.item_code
								row.item_name = r.message.item_name
								row.unit = r.message.unit
								row.available_qty = r.message.available_quantity
								refresh_field("store_child")
							}
						})
						
					})
				}
			}
		})
	},
	purchase_request: function(frm){
		frappe.set_route("Form","Purchase Request","New Purchase Request")
	}
})