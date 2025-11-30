// Copyright (c) 2024, Dirk van der Laarse and contributors
// For license information, please see license.txt

frappe.ui.form.on("WooCommerce Product", {
	refresh(frm) {
		// Add a custom button to sync this WooCommerce order to a Sales Order
		frm.add_custom_button(__("Sync this Item to ERPNext"), function () {
			frm.trigger("sync_product");
		}, __('Actions'));
		
		frm.add_custom_button(__("Delete from Wordpress"), function () {
			frm.trigger("delete_product");
		}, __('Actions'));

		// Set intro text
		const intro_txt = __(
			"Note: This is a Virtual Document. Saving changes on this document will update this resource on WooCommerce."
		);
		frm.set_intro(intro_txt, "orange");
	},
	sync_product: function(frm) {
		// Sync this WooCommerce Product
		frappe.dom.freeze(__("Sync Product with ERPNext..."));
		frappe.call({
			method: "woocommerce_fusion.tasks.sync_items.run_item_sync",
			args: {
				woocommerce_product_name: frm.doc.name
			},
			callback: function(r) {
				console.log(r);
				frappe.dom.unfreeze();
				frappe.show_alert({
					message:__('Sync completed successfully'),
					indicator:'green'
				}, 5);
				frm.reload_doc();
			},
			error: (r) => {
				frappe.dom.unfreeze();
				frappe.show_alert({
					message: __('There was an error processing the request. See Error Log.'),
					indicator: 'red'
				}, 5);
			}
		});
	},
	delete_product(frm){
		// First let's prompt the user to confirm the deletion
		frappe.confirm(
			__('Are you sure you want to delete this product from WooCommerce?'),
			function(){
				// User has confirmed deletion
				frappe.dom.freeze(__("Deleting Product from WooCommerce..."));
				const {woocommerce_server,woocommerce_id} = frm.doc;
				frappe.call({
					method: "woocommerce_fusion.tasks.sync_items.delete_product_from_woocommerce",
					args: { woocommerce_server, woocommerce_id },
					callback: function(r) {
						console.log(r);
						frappe.dom.unfreeze();
						frappe.show_alert({
							message:__('Product deleted successfully'),
							indicator:'green'
						}, 5);
						frm.reload_doc();
					},
					error: (r) => {
						frappe.dom.unfreeze();
						frappe.show_alert({
							message: __('There was an error processing the request. See Error Log.'),
							indicator: 'red'
						}, 5);
					}
				});
			},
			function(){
				// User has cancelled deletion
			}
		);
	}
});

