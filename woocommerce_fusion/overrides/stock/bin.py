import frappe
from erpnext.stock.doctype.bin.bin import Bin as ERPNExtBin
from woocommerce_fusion.tasks.stock_update import update_stock_levels_on_woocommerce_site, update_stock_levels_on_variants
from ecommerce_integrations.amazon.doctype.amazon_sp_listing.amazon_sp_listing import sync_item_stock_to_amazon
from erpnext_ebay.erpnext_ebay.doctype.ebay_listing.ebay_listing import sync_item_stock_to_ebay
from walmart.walmart.doctype.walmart_product.walmart_product import sync_item_stock_to_walmart

class Bin(ERPNExtBin):
    def set_projected_qty(self):
        self.run_method("before_projected_qty_change")
        super().set_projected_qty()
        self.run_method("after_projected_qty_change")

    def after_projected_qty_change(self):
        self.enqueue_projected_qty_notify()

    def enqueue_projected_qty_notify(self):
        frappe.enqueue(
            method="woocommerce_fusion.overrides.stock.bin.notify_of_projected_qty_change",
            bin_id=self.name,
            job_name=f"Update Projected Qty for Bin {self.name}",
            queue="long",
            timeout=1500,
            enqueue_after_commit=True,
        )

def notify_of_projected_qty_change(bin_id):
    doc = frappe.get_doc("Bin", bin_id)

    # Update WooCommerce main item stock
    try:
        update_stock_levels_on_woocommerce_site(doc.item_code)
    except Exception as e:
        frappe.log_error(f"[Stock Sync] WooCommerce Site Failed for {doc.item_code}", frappe.get_traceback())

    # Update WooCommerce variants
    try:
        update_stock_levels_on_variants(doc.item_code)
    except Exception as e:
        frappe.log_error(f"[Stock Sync] WooCommerce Variants Failed for {doc.item_code}", frappe.get_traceback())

    # Update Amazon listing
    try:
        sync_item_stock_to_amazon(doc.item_code)
    except Exception as e:
        frappe.log_error(f"[Stock Sync] Amazon Sync Failed for {doc.item_code}", frappe.get_traceback())

    # Update eBay listing
    try:
        sync_item_stock_to_ebay(doc.item_code)
    except Exception as e:
        frappe.log_error(f"[Stock Sync] eBay Sync Failed for {doc.item_code}", frappe.get_traceback())

    # Update Walmart listing
    try:
        sync_item_stock_to_walmart(doc.item_code)
    except Exception as e:
        frappe.log_error(f"[Stock Sync] Walmart Sync Failed for {doc.item_code}", frappe.get_traceback())