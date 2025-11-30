import frappe
from erpnext.stock.doctype.bin.bin import Bin as ERPNExtBin
from frappe.utils.background_jobs import get_redis_conn
from woocommerce_fusion.tasks.stock_update import (
    update_stock_levels_on_woocommerce_site,
    update_stock_levels_on_variants,
)
from ecommerce_integrations.amazon.doctype.amazon_sp_listing.amazon_sp_listing import sync_item_stock_to_amazon
from erpnext_ebay.erpnext_ebay.doctype.ebay_listing.ebay_listing import sync_item_stock_to_ebay
from walmart.walmart.doctype.walmart_product.walmart_product import sync_item_stock_to_walmart

DEBOUNCE_SECONDS = 120  # merge bursts of stock changes that happen close in time

class Bin(ERPNExtBin):
    def set_projected_qty(self):
        self.run_method("before_projected_qty_change")
        super().set_projected_qty()
        self.run_method("after_projected_qty_change")

    def after_projected_qty_change(self):
        self.enqueue_projected_qty_notify()

    def enqueue_projected_qty_notify(self):
        """
        Debounce by item_code to avoid N enqueues per Bin touch.
        """
        # If item not set for any channel, skip fast:
        item_code = self.item_code
        if not item_code:
            return

        r = get_redis_conn()
        site = frappe.local.site
        key = f"inv-sync:{site}:{item_code}"
        # set if not exists + expiry (debounce window)
        if r.set(key, "1", nx=True, ex=DEBOUNCE_SECONDS):
            frappe.enqueue(
                method="woocommerce_fusion.overrides.stock.bin.notify_of_projected_qty_change",
                queue="long",
                job_name=f"long:sync_all_channels:{item_code}",
                enqueue_after_commit=True,
                deduplicate=True,
                deduplicate_timeout=DEBOUNCE_SECONDS,
                kwargs={"item_code": item_code},
            )

def notify_of_projected_qty_change(item_code: str = None, bin_id: str = None, **kwargs):
    """
    Backward-compatible entry point.
    Old queued jobs call with bin_id=..., new ones call with item_code=....
    """
    try:
        if not item_code and bin_id:
            # Resolve item_code from the old payload
            item_code = frappe.db.get_value("Bin", bin_id, "item_code")

        if not item_code:
            # Nothing we can do
            return

        # Fast guards
        item = frappe.get_cached_doc("Item", item_code)
        if item.disabled or not item.is_stock_item:
            return

        # Update WooCommerce main item stock
        try:
            update_stock_levels_on_woocommerce_site(item_code)
        except Exception:
            frappe.log_error(f"[Stock Sync] WooCommerce Site Failed for {item_code}", frappe.get_traceback())

        # Update WooCommerce variants
        try:
            update_stock_levels_on_variants(item_code)
        except Exception:
            frappe.log_error(f"[Stock Sync] WooCommerce Variants Failed for {item_code}", frappe.get_traceback())

        # Update Amazon listing
        try:
            sync_item_stock_to_amazon(item_code)
        except Exception:
            frappe.log_error(f"[Stock Sync] Amazon Sync Failed for {item_code}", frappe.get_traceback())

        # Update eBay listing
        try:
            sync_item_stock_to_ebay(item_code)
        except Exception:
            frappe.log_error(f"[Stock Sync] eBay Sync Failed for {item_code}", frappe.get_traceback())

        # Update Walmart listing (only if product reference exists)
        try:
            if frappe.db.exists("Walmart Product Reference", {"parent": item_code}):
                sync_item_stock_to_walmart(item_code)
        except Exception:
            frappe.log_error(f"[Stock Sync] Walmart Sync Failed for {item_code}", frappe.get_traceback())

    except Exception:
        frappe.log_error("notify_of_projected_qty_change crashed", frappe.get_traceback())
        raise