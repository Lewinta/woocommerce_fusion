frappe.ui.form.on("Material Request", {

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