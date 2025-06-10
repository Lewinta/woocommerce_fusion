import frappe
from frappe.utils import flt
from erpnext.stock.doctype.pick_list.pick_list import create_delivery_note

def validate(doc, method=None):
    total_weight = 0.0
    for row in doc.locations:
        if not row.warehouse:
            continue
        warehouse = frappe.get_doc("Warehouse", row.warehouse)
        row.zone = warehouse.get_zone()
        if row.weight_per_unit:
            total_weight += flt(row.weight_per_unit)
    doc.weight = total_weight

def on_submit(doc, method=None):
    """
    This function is called when a Pick List is submitted.
    It updates the stock ledger entries for the items in the pick list.
    """
    dn = create_delivery_note(doc.name)
    dn.submit()
    