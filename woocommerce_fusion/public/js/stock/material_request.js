frappe.ui.form.on("Material Request", {
   refresh(frm){
        frm.trigger("set_queries");
   },
   set_queries(frm) {
        frm.set_query("from_warehouse", "items", function(doc, cdt, cdn) {
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

frappe.ui.form.on("Material Request Item", {
    item_code: function(frm, cdt, cdn) {
        set_available_qty(frm, cdt, cdn);
    },
    from_warehouse: function(frm, cdt, cdn) {
        set_available_qty(frm, cdt, cdn);
    },
});

function set_available_qty(frm, cdt, cdn) {
    const method = "woocommerce_fusion.overrides.stock.material_request.get_available_qty";
    const item = locals[cdt][cdn];
    const args = {
        item: item.item_code,
        warehouse: item.from_warehouse,
    }
    if (!item.item_code || !item.from_warehouse) {
        frappe.model.set_value(cdt, cdn, "available_qty", 0);
        return;
    }
    frappe.call({
        method: method,
        args: args,
        callback: function(r) {
            if (r.message) {
                frappe.model.set_value(cdt, cdn, "available_qty", r.message);
            } else {
                frappe.model.set_value(cdt, cdn, "available_qty", 0);
            }
        },
    });

}