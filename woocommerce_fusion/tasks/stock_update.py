import math

import frappe
from frappe.utils import flt
from frappe.utils.nestedset import get_descendants_of
from frappe.query_builder import Criterion, functions as fn
from woocommerce_fusion.tasks.utils import APIWithRequestLogging


def update_stock_levels_for_woocommerce_item(doc, method):
    if not frappe.flags.in_test:
        if doc.doctype in ("Stock Entry", "Stock Reconciliation", "Sales Invoice", "Delivery Note"):
            # Check if there are any enabled WooCommerce Servers with stock sync enabled
            if (
                len(
                    frappe.get_list(
                        "WooCommerce Server", filters={"enable_sync": 1, "enable_stock_level_synchronisation": 1}
                    )
                )
                > 0
            ):
                if doc.doctype == "Sales Invoice":
                    if doc.update_stock == 0:
                        return
                item_codes = [row.item_code for row in doc.items]
                for item_code in item_codes:
                    frappe.enqueue(
                        "woocommerce_fusion.tasks.stock_update.update_stock_levels_on_woocommerce_site",
                        enqueue_after_commit=True,
                        item_code=item_code,
                    )


def update_stock_levels_for_all_enabled_items_in_background():
    """
    Get all enabled ERPNext Items and post stock updates to WooCommerce
    """
    erpnext_items = []
    current_page_length = 500
    start = 0

    # Get all items, 500 records at a time
    while current_page_length == 500:
        items = frappe.db.get_all(
            doctype="Item",
            filters={"disabled": 0},
            fields=["name"],
            start=start,
            page_length=500,
        )
        erpnext_items.extend(items)
        current_page_length = len(items)
        start += current_page_length

    for item in erpnext_items:
        frappe.enqueue(
            "woocommerce_fusion.tasks.stock_update.update_stock_levels_on_woocommerce_site",
            item_code=item.name,
        )


@frappe.whitelist()
def update_stock_levels_on_woocommerce_site(item_code):
    """
    Updates stock levels of an item on all its associated WooCommerce sites.

    This function fetches the item from the database, then for each associated
    WooCommerce site, it retrieves the current inventory, calculates the new stock quantity,
    and posts the updated stock levels back to the WooCommerce site.
    """
    item = frappe.get_doc("Item", item_code)

    if len(item.woocommerce_servers) == 0 or not item.is_stock_item or item.disabled:
        return False
    else:
        from frappe.utils.nestedset import get_descendants_of

        bins = frappe.get_list(
            "Bin", {"item_code": item_code}, ["name", "warehouse", "reserved_qty", "actual_qty", "projected_qty"]
        )

        for wc_site in item.woocommerce_servers:
            if wc_site.woocommerce_id:
                woocommerce_id = wc_site.woocommerce_id
                woocommerce_server = wc_site.woocommerce_server
                wc_server = frappe.get_cached_doc("WooCommerce Server", woocommerce_server)

                if (
                    not wc_server
                    or not wc_server.enable_sync
                    or not wc_site.enabled
                    # or not wc_server.enable_stock_level_synchronisation
                ):
                    continue

                wc_api = APIWithRequestLogging(
                    url=wc_server.woocommerce_server_url,
                    consumer_key=wc_server.api_consumer_key,
                    consumer_secret=wc_server.api_consumer_secret,
                    version="wc/v3",
                    timeout=40,
                )

                # Build list of all relevant warehouses, expanding groups
                relevant_warehouses = set()
                for row in wc_server.warehouses:
                    if frappe.db.get_value("Warehouse", row.warehouse, "is_group"):
                        descendants = get_descendants_of("Warehouse", row.warehouse)
                        relevant_warehouses.update(descendants)
                    else:
                        relevant_warehouses.add(row.warehouse)

                qty = math.floor(
                        sum(
                            flt(bin.actual_qty - bin.reserved_qty)
                            for bin in bins
                            if bin.warehouse in relevant_warehouses
                        )
                    )
                
                data_to_post = {
                    "stock_quantity": qty if qty >= 0 else 0,  # Ensure stock quantity is not negative
                }

                response = None
                try:
                    woo_product = frappe.get_doc("WooCommerce Product", f"{woocommerce_server}~{woocommerce_id}")
                    
                    print(data_to_post)
                    if woo_product.type == "simple":
                        print("Updating simple product")
                        response = wc_api.put(endpoint=f"products/{woocommerce_id}", data=data_to_post)
                    
                    if woo_product.type == "variation":
                        print("Updating product variation")
                        response = wc_api.put(
                            endpoint=f"products/{woo_product.parent_id}/variations/{woo_product.woocommerce_id}", data=data_to_post
                        )

                except Exception as err:
                    error_message = f"{frappe.get_traceback()}\n\nData in PUT request: \n{str(data_to_post)}"
                    frappe.log_error("WooCommerce Error", error_message)
                    raise err
                if response and response.status_code != 200:
                    error_message = f"Status Code not 200\n\nData in PUT request: \n{str(data_to_post)}"
                    error_message += (
                        f"\n\nResponse: \n{response.status_code}\nResponse Text: {response.text}\nRequest URL: {response.request.url}\nRequest Body: {response.request.body}"
                        if response is not None
                        else ""
                    )
                    frappe.log_error("WooCommerce Error", error_message)
                    raise ValueError(error_message)

        return True

def get_item_projected_qty(item_code, company):
    """
        Get the projected quantity of an item in a specific warehouse.
    """
    B = frappe.qb.DocType("Bin")
    W = frappe.qb.DocType("Warehouse")
    valid_warehouses = get_descendants_of("Warehouse", """Kenzie's Main - KO""")

    data = frappe.qb.from_(B).join(W).on(
        B.warehouse == W.name
    ).select(
        fn.Sum(B.actual_qty - B.reserved_qty).as_("projected_qty")
    ).where(
        (B.item_code == item_code)&
        (W.company == company)&
        (W.name.isin(valid_warehouses))&
        # (W.name != "Receiving - KO")&
        (W.disabled == 0)
    ).groupby(
        B.item_code
    ).run()

    return data[0][0] if data else 0


def update_stock_levels_on_variants(item_code):
    """
    Updates stock levels for all variants of a given item code on WooCommerce.
    """
    IWS = frappe.qb.DocType("Item WooCommerce Server")
    WS = frappe.qb.DocType("WooCommerce Server")
    conditions = [
        IWS.parent.like(f"%{item_code}%"),
        IWS.parent.like(f"%+%"),
        IWS.woocommerce_id.isnotnull(),
    ]
    
    variants = frappe.qb.from_(IWS).join(WS).on(
        IWS.woocommerce_server == WS.name
    ).select(
        IWS.parent.as_("item_code"),
        IWS.woocommerce_server,
        IWS.woocommerce_id,
        WS.company,
        WS.woocommerce_server_url,
        WS.api_consumer_key,
        WS.api_consumer_secret
    ).where(
        Criterion.all(conditions)
    ).run(as_dict=True)

    for variant in variants:
        item_stocks = []
        for item in variant.item_code.split("+"):
            item_stocks.append(get_item_projected_qty(item, variant.company))
        
        stock_qty = min(item_stocks) if item_stocks else 0

        # Get parent WooCommerce product
        product_name = f"{variant.woocommerce_server}~{variant.woocommerce_id}"
        woo_product = frappe.get_doc("WooCommerce Product", product_name)
        if woo_product.type != "variation":
            continue  # Skip if the product is not a variation
        parent_id = woo_product.parent_id
        variation_id = variant.woocommerce_id

        # Init API client
        wc_api = APIWithRequestLogging(
            url=variant.woocommerce_server_url,
            consumer_key=variant.api_consumer_key,
            consumer_secret=variant.api_consumer_secret,
            version="wc/v3",
            timeout=40,
        )
        # Prepare payload
        data_to_post = {
            "stock_quantity": math.floor(stock_qty) if stock_qty >= 0 else 0,  # Ensure stock quantity is not negative
        }

        endpoint = f"products/{parent_id}/variations/{variation_id}"

        try:
            print(data_to_post)
            response = wc_api.put(endpoint=endpoint, data=data_to_post)
        except Exception as err:
            error_message = f"{frappe.get_traceback()}\n\nData in PUT request: \n{str(data_to_post)}"
            frappe.log_error("WooCommerce Variant Stock Update Error", error_message)
            raise err

        if response.status_code != 200:
            error_message = f"Status Code not 200\n\nData in PUT request: \n{str(data_to_post)}"
            error_message += (
                f"\n\nResponse: \n{response.status_code}\nResponse Text: {response.text}\nRequest URL: {response.request.url}\nRequest Body: {response.request.body}"
                if response is not None
                else ""
            )
            frappe.log_error("WooCommerce Variant Stock Update Error", error_message)
            raise ValueError(error_message)



