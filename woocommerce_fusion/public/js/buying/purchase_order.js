frappe.ui.form.on("Purchase Order", {
    refresh(frm){
        frm.trigger("set_queries");
    },
    set_queries(frm) {
       frm.set_query("item_code", "items", function() {
            return {
                query: "woocommerce_fusion.overrides.buying.buying_controller.get_supplier_items",
                filters: {
                    "supplier": frm.doc.supplier || "",
                    "is_purchase_item": 1,
                    "disabled": 0,
                    "has_variants": 0
                }
            };
        });
    },
});