frappe.ui.form.on("Mode of Payment", {
    refresh(frm) {
        frm.trigger("set_queries");
    },
    set_queries(frm) {
		frm.set_query("default_account", "accounts", function (doc, cdt, cdn) {
			let d = locals[cdt][cdn];
			return {
				filters: [
					["Account", "account_type", "in", "Bank, Cash, Receivable, Chargeable" ],
					["Account", "is_group", "=", 0],
					["Account", "company", "=", d.company],
				],
			};
		});
    }
});