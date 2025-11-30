from woocommerce_fusion import woo_skus
from woocommerce_fusion.tasks.stock_update import update_stock_levels_on_woocommerce_site
from woocommerce_fusion.tasks.sync_items import run_item_sync
from frappe.utils import flt

server = "www.kenziesoptics.com"

def insert(sku, post_id, status="Success", details=None):
    frappe.db.sql("""
        INSERT INTO product_status (sku, post_id, status, details)
        VALUES (%s, %s, %s, %s)
    """,  (sku, post_id, status, details))

def update_or_insert(item):
    item.set("woocommerce_servers", [])
    item.append("woocommerce_servers", {
        "woocommerce_id":  row.woocommerce_id,
        "woocommerce_server": "www.kenziesoptics.com",
        "enabled": 1
    })
    item.save()

for idx, row in enumerate(woo_skus, 1):
    # if idx % 100 == 0:
    print(f"Processing ({idx} / {len(woo_skus)})\t{flt(idx / len(woo_skus) * 100, 2)}%")
    row = frappe._dict(row)
    try :
        if name := frappe.db.exists("Item", {"custom_sku":  row.sku}):
            item = frappe.get_doc("Item", name)
            
            if item.woocommerce_servers and item.woocommerce_servers[0].woocommerce_id == row.woocommerce_id:
                insert(row.sku, row.woocommerce_id, "Success", "Already exists")

            if item.woocommerce_servers and item.woocommerce_servers[0].woocommerce_id != row.woocommerce_id:
                update_or_insert(item)
                insert(row.sku, row.woocommerce_id, "Success", "Item updated with new WooCommerce ID")
            
            if not item.woocommerce_servers:
                update_or_insert(item)
                insert(row.sku, row.woocommerce_id, "Success", "Item inserted with WooCommerce ID")
            
            update_stock_levels_on_woocommerce_site(name)
            
        else:
            woocommerce_product_name = f"{server}~{row.woocommerce_id}"
            run_item_sync(woocommerce_product_name)
            insert(row.sku, row.woocommerce_id,  "Success", "Item inserted from WooCommerce Product")
    except Exception as e:
        msg = f"Error processing SKU {row.sku} with WooCommerce ID {row.woocommerce_id}: {str(e)}"
        msg += f"\n{frappe.get_traceback()}"
        
        frappe.log_error("Error in WooCommerce SKU Processing", msg)
        insert(row.sku, row.woocommerce_id, "Error", str(e))
        continue
        