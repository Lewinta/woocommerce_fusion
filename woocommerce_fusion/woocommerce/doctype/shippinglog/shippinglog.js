// Copyright (c) 2024, ahmadragheb and contributors
// For license information, please see license.txt

frappe.ui.form.on('ShippingLog', {
	refresh: function(frm) {
		frm.trigger("add_custom_button");
	},
	add_custom_button(frm){
		if (frm.doc.tracking_number)
			frm.add_custom_button(__("Publish Tracking Number"), function () {
				const opts = {
					method: "publish_tracking_number",
					doc: frm.doc,
					freeze: 1,
					freeze_message: __("Publishing Tracking Number..."), 
				}
				frm.call(opts).then(r => {
					if (r.message) {
						frappe.utils.play_sound("submit");
						frappe.show_alert({
							message: __("Tracking Number Published Successfully"),
							indicator: 'green'
						});
					}
					else {
						frappe.show_alert({
							message: __("Tracking Number Not Published"),
	  						indicator: 'red'
						});
					}	
				});
		}, __('Actions'));
	}
});
