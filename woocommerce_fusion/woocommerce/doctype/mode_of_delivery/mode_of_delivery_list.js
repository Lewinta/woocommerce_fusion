frappe.listview_settings["Mode of Delivery"] = {
	add_fields: ["carrier_company"],
	get_indicator: function (doc) {
		if (doc.carrier_company == "USPS") {
			return [doc.carrier_company, "blue", "carrier_company,=,USPS"];
		} else if (doc.carrier_company === "UPS") {
			return [doc.carrier_company, "orange", "carrier_company,=,UPS"];
		} else if (doc.carrier_company === "FedEx") {
            return [doc.carrier_company, "purple", "carrier_company,=,FedEx"];
        } else if (doc.carrier_company === "DHL") {
            return [doc.carrier_company, "green", "carrier_company,=,DHL"];
        } else {
            return [doc.carrier_company || __("Unknown"), "grey", "carrier_company,=," + (doc.carrier_company || "Unknown")];
        }
	},
};