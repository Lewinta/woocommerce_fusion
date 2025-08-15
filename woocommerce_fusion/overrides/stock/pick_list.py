import frappe
from frappe import _
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
    Called when a Pick List is submitted.
    Automatically creates a Delivery Note unless the fulfillment method is WooCommerce.
    """
    if not doc.locations:
        return

    sales_order = doc.locations[0].sales_order
    if sales_order:
        fulfillment_method = frappe.db.get_value(
            "Sales Order", sales_order, "fulfillment_method"
        )
        if fulfillment_method in ["WooCommerce", "eBay"]:
            frappe.logger().info(f"Skipping Delivery Note for WooCommerce Pick List {doc.name}")
            return

    try:
        if not sales_order:
            return
        dn = create_delivery_note(doc.name)
        dn.submit()
    except Exception:
        frappe.log_error(f"Failed to create Delivery Note for Pick List {doc.name}", frappe.get_traceback())
        frappe.throw(_("Failed to create Delivery Note automatically. Please check the error log."))
    