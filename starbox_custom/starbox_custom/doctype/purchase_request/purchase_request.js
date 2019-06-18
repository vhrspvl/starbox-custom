// Copyright (c) 2019, Starboxes India and contributors
// For license information, please see license.txt

frappe.ui.form.on('Purchase Request', {
	refresh: function(frm) {
		if(!frm.doc.store_keeper_name){
			frm.set_value("store_keeper_name", frappe.session.user)
		}
		if(!frm.doc.date){
			frm.set_value("date",frappe.datetime.nowdate())
		}
		if(frm.doc.approver == frappe.session.user){
			if(frm.doc.status == "PO Attached"){
				frm.set_df_property('status', 'read_only', 0);
			}
		}
	},
	validate: function(frm){
		if(frm.doc.store_keeper_name == frappe.session.user){
			if(!frm.doc.status){
				frm.set_value("status","Requested")
			}
		}
		if(frm.doc.approver == frappe.session.user){
			if(frm.doc.status == "PO Attached"){
				frm.set_df_property('status', 'read_only', 0);
			}
			if(frm.doc.status == "Requested"){
				frm.set_value("status","Validated")
			}
		}
	},
	before_submit: function(frm){
		if(frm.doc.approver != frappe.session.user){
			validated = false
			frappe.msgprint("Approver only can Submit")
		} 
	}
})

frappe.ui.form.on("Purchase Child", {
	item_code: function(frm, cdt, cdn) {
		var child = locals[cdt][cdn];
		frappe.call({
			"method": "frappe.client.get",
			args:{
				"doctype": "Stationery Item",
				"name": child.item_code
			},
			callback: function(r){
				if(r.message){
					frappe.model.set_value(child.doctype, child.name, "item_name", r.message.item_name);
					frappe.model.set_value(child.doctype, child.name, "unit", r.message.unit);
				}
			}
		})
	},
});

