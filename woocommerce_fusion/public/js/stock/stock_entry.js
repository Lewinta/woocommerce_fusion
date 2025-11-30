frappe.ui.form.on("Stock Entry", {
   refresh(frm){
        frm.trigger("set_queries");
   },
   set_queries(frm) {
        frm.set_query("s_warehouse", "items", function(doc, cdt, cdn) {
            const row = locals[cdt][cdn];
            return {
                query: "woocommerce_fusion.overrides.stock.stock_entry.get_source_warehouses",
                filters: {
                    is_group: 0,
                    company: frm.doc.company,
                    item_code: row.item_code,
                    stock_qty: [">", 0]
                }
            };
        });
   }
});