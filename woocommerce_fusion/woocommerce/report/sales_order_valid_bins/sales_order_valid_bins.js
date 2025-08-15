// Copyright (c) 2025, Dirk van der Laarse and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Order Valid Bins"] = {
	"filters": [
		{
			"fieldname": "sales_order",
			"label": "Sales Order",
			"fieldtype": "Link",
			"options": "Sales Order",
			"reqd": 1,
			"on_change": function(report) {
				// Reset the Item field if sales order changes
				frappe.query_report.set_filter_value("item", null);
			}
		},
		{
			"fieldname": "item",
			"label": "Item",
			"fieldtype": "Link",
			"options": "Item",
			"reqd": 1,
			"get_query": () => {
				let sales_order = frappe.query_report.get_filter_value("sales_order");
				if (!sales_order) return;

				return {
					query: "woocommerce_fusion.woocommerce.report.sales_order_valid_bins.sales_order_valid_bins.get_items_from_sales_order",
					filters: { sales_order: sales_order }
				};
			}
		}
	]
};
