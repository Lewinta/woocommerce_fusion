# Copyright (c) 2025, Dirk van der Laarse and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder import Criterion
from frappe.utils.nestedset import get_descendants_of

def execute(filters=None):
	return get_columns(), get_data(filters)

def get_columns():
	return [
		{
			"fieldname": "warehouse",
			"fieldtype": "Data",
			"label": "Warehouse",
			"width": 200
		},
		{
			"fieldname": "actual_qty",
			"fieldtype": "Float",
			"label": "Actual Qty",
			"width": 150
		},
		{
			"fieldname": "reserved_qty",
			"fieldtype": "Float",
			"label": "Reserved Qty",
			"width": 150
		},
		{
			"fieldname": "qty",
			"fieldtype": "Float",
			"label": "Actual Qty",
			"width": 150
		},
	]

def get_data(filters):
	valid_warehouses = get_descendants_of("Warehouse", """Kenzie's Main - KO""")
	B = frappe.qb.DocType('Bin')
	W = frappe.qb.DocType('Warehouse')
	S = frappe.qb.DocType('Sales Order')

	conditions = [
		B.item_code == filters.get('item'),
		S.name == filters.get('sales_order'),
		W.disabled == 0,
		W.name.isin(valid_warehouses),
		W.name != "Receiving - KO"
	]

	return frappe.qb.from_(B).join(W).on(
		W.name == B.warehouse
	).join(S).on(
		W.company == S.company
	).select(
		B.warehouse,
		B.actual_qty,
		B.reserved_qty,
		(B.actual_qty - B.reserved_qty).as_('qty')
	).where(
		Criterion.all(conditions)
	).run(as_dict=True)

@frappe.whitelist()
def get_items_from_sales_order(doctype, txt, searchfield, start, page_len, filters):
	sales_order = filters.get("sales_order")

	if not sales_order:
		return []

	return frappe.db.sql("""
		SELECT DISTINCT sii.item_code, sii.item_name
		FROM `tabSales Order Item` sii
		WHERE sii.parent = %s AND (sii.item_code LIKE %s OR sii.item_name LIKE %s)
		ORDER BY sii.item_code
		LIMIT %s OFFSET %s
	""", (sales_order, f"%{txt}%", f"%{txt}%", page_len, start))