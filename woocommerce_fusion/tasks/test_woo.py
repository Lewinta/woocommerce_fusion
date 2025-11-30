# woocommerce_fusion/tasks/test_woo.py

import requests
import frappe
from frappe import _
from frappe.utils import cstr

@frappe.whitelist()
def probe_wc_product(server_name: str, woocommerce_id: str | None = None, sku: str | None = None):
    # Treat a non-numeric "woocommerce_id" as a SKU if user passed it positionally
    if woocommerce_id and not str(woocommerce_id).isdigit() and not sku:
        sku, woocommerce_id = woocommerce_id, None

    if not (woocommerce_id or sku):
        frappe.throw(_("Provide either woocommerce_id or sku"))

    if not frappe.db.exists("WooCommerce Server", server_name):
        frappe.throw(_("WooCommerce Server {0} not found").format(server_name))

    server = frappe.get_cached_doc("WooCommerce Server", server_name)
    base = server.woocommerce_server_url.rstrip("/")

    # Build URL + params for QUERY auth (like your working curl)
    if woocommerce_id:
        url = f"{base}/wp-json/wc/v3/products/{woocommerce_id}"
        params = {
            "consumer_key": server.api_consumer_key,
            "consumer_secret": server.api_consumer_secret,
            "_fields": "id,sku,modified,name,permalink,images,type",
        }
    else:
        url = f"{base}/wp-json/wc/v3/products"
        params = {
            "sku": sku,
            "per_page": 1,
            "consumer_key": server.api_consumer_key,
            "consumer_secret": server.api_consumer_secret,
            "_fields": "id,sku,modified,name,permalink,images,type",
        }

    headers = {"User-Agent": "TZCode-ERPNext-WooSync/1.0"}

    try:
        r = requests.get(url, params=params, headers=headers, timeout=15)
        status = r.status_code
        body = r.json() if r.headers.get("content-type","").startswith("application/json") else r.text

        frappe.logger("woocommerce_probe").info({
            "url": url, "params": {k: ('***' if 'consumer_' in k else v) for k,v in params.items()},
            "status": status,
            "x-wp-total": r.headers.get("X-WP-Total"),
            "x-wp-totalpages": r.headers.get("X-WP-TotalPages"),
            "content-length": r.headers.get("Content-Length"),
        })

        if status >= 400:
            frappe.throw(_("WooCommerce probe failed: {0} – {1}").format(status, cstr(body)))

        # Normalize to list for consistent handling
        if woocommerce_id and isinstance(body, dict):
            body = [body]

        frappe.msgprint(_("Probe OK: fetched {0} product(s).").format(len(body)))
        return body

    except requests.Timeout:
        frappe.throw(_("WooCommerce probe timed out (15s)."))
    except requests.RequestException as e:
        frappe.throw(_("WooCommerce probe error: {0}").format(cstr(e)))