import frappe
from frappe.query_builder import functions as fn


@frappe.whitelist()
def get_available_qty(item, warehouse=None):    
    if not warehouse:
        return 0.0
    
    if not item:
        return 0.0
    
    B = frappe.qb.DocType("Bin")
    
    return frappe.qb.from_(B).select(
        fn.Sum(fn.Coalesce(B.actual_qty, 0)).as_("available_qty")
    ).where(
        (B.item_code == item) &
        (B.warehouse == warehouse) 
    ).run()[0][0]