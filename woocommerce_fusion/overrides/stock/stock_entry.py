import frappe
from frappe.query_builder import Criterion

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_source_warehouses(doctype, txt, searchfield, start, page_len, filters):
    I = frappe.qb.DocType("Item")
    B = frappe.qb.DocType("Bin")
    W = frappe.qb.DocType("Warehouse")

    conditions = [
        W.is_group == 0,
        W.disabled == 0
    ]
    if not filters.get("company"):
        frappe.throw("Company is required to filter warehouses.")


    if filters.get("item_code"):
        # Let's show only warehouses that have stock for the given item
        conditions.append(B.item_code == filters.get("item_code"))
        conditions.append(W.company == filters.get("company"))
        conditions.append(B.actual_qty > 0)
        
        return frappe.qb.from_(I).join(B).on(
            I.name == B.item_code
        ).join(W).on(
            B.warehouse == W.name
        ).select(
            B.warehouse,
            B.warehouse
        ).where(
            Criterion.all(conditions)
        ).limit(page_len).offset(start).run(debug=True)
    else:
        # Let's show all warehouses
        return frappe.qb.from_(W).select(
            W.name.as_('warehouse'),
            W.name.as_('warehouse')
        ).where(
            Criterion.all(conditions)
        ).limit(page_len).offset(start).run(debug=True)
