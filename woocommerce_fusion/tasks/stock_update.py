import math
import frappe
from frappe.utils import flt
from frappe.utils.nestedset import get_descendants_of
from frappe.query_builder import Criterion, functions as fn
from woocommerce_fusion.tasks.utils import APIWithRequestLogging
from frappe.utils.background_jobs import get_redis_conn

DEBOUNCE_SECONDS_DEFAULT = 120


def _debounced_enqueue_inventory(item_code: str, dedupe_seconds: int = DEBOUNCE_SECONDS_DEFAULT) -> None:
    if not item_code:
        return
    r = get_redis_conn()
    site = frappe.local.site
    key = f"inv-sync:{site}:{item_code}"
    if r.set(key, "1", nx=True, ex=dedupe_seconds):
        frappe.enqueue(
            "woocommerce_fusion.tasks.stock_update.update_stock_levels_on_woocommerce_site",
            queue="long",
            job_name=f"long:woo:{item_code}",
            # kwargs={"item_code": item_code},
            item_code=item_code,
            deduplicate=True,
            deduplicate_timeout=dedupe_seconds,
            enqueue_after_commit=True,
        )


def update_stock_levels_for_woocommerce_item(doc, method):
    if frappe.flags.in_test:
        return
    if doc.doctype not in ("Stock Entry", "Stock Reconciliation", "Sales Invoice", "Delivery Note"):
        return
    if doc.doctype == "Sales Invoice" and getattr(doc, "update_stock", 0) == 0:
        return
    if not frappe.get_list(
        "WooCommerce Server",
        filters={"enable_sync": 1, "enable_stock_level_synchronisation": 1},
        limit=1,
    ):
        return
    item_codes = {row.item_code for row in getattr(doc, "items", []) if getattr(row, "item_code", None)}
    for item_code in item_codes:
        _debounced_enqueue_inventory(item_code)


def update_stock_levels_for_all_enabled_items_in_background():
    start = 0
    page_len = 500
    while True:
        items = frappe.db.get_all(
            doctype="Item",
            filters={"disabled": 0},
            fields=["name"],
            start=start,
            page_length=page_len,
        )
        if not items:
            break
        for it in items:
            _debounced_enqueue_inventory(it["name"], dedupe_seconds=300)
        start += len(items)
        if len(items) < page_len:
            break


@frappe.whitelist()
def update_stock_levels_on_woocommerce_site(item_code: str, **_):
    item = frappe.get_doc("Item", item_code)
    if not item.is_stock_item or item.disabled or len(item.woocommerce_servers) == 0:
        return False

    bins = frappe.get_list(
        "Bin",
        {"item_code": item_code},
        ["name", "warehouse", "reserved_qty", "actual_qty", "projected_qty"],
    )

    for wc_site in item.woocommerce_servers:
        if not wc_site.woocommerce_id:
            continue

        wc_server = frappe.get_cached_doc("WooCommerce Server", wc_site.woocommerce_server)
        if (not wc_server) or (not wc_server.enable_sync) or (not wc_site.enabled):
            continue

        wc_api = APIWithRequestLogging(
            url=wc_server.woocommerce_server_url,
            consumer_key=wc_server.api_consumer_key,
            consumer_secret=wc_server.api_consumer_secret,
            version="wc/v3",
            timeout=40,
        )

        relevant_warehouses = set()
        for row in wc_server.warehouses:
            if frappe.db.get_value("Warehouse", row.warehouse, "is_group"):
                relevant_warehouses.update(get_descendants_of("Warehouse", row.warehouse))
            else:
                relevant_warehouses.add(row.warehouse)

        qty = math.floor(
            sum(
                flt(b.actual_qty - b.reserved_qty)
                for b in bins
                if b.warehouse in relevant_warehouses
            )
        )

        data_to_post = {"stock_quantity": qty if qty >= 0 else 0}
        response = None

        try:
            product_name = f"{wc_site.woocommerce_server}~{wc_site.woocommerce_id}"
            woo_product = frappe.get_doc("WooCommerce Product", product_name)

            if woo_product.type == "simple":
                response = wc_api.put(endpoint=f"products/{wc_site.woocommerce_id}", data=data_to_post)
            elif woo_product.type == "variation":
                response = wc_api.put(
                    endpoint=f"products/{woo_product.parent_id}/variations/{woo_product.woocommerce_id}",
                    data=data_to_post,
                )
            else:
                continue

        except Exception as err:
            error_message = f"{frappe.get_traceback()}\n\nData in PUT request: \n{str(data_to_post)}"
            frappe.log_error("WooCommerce Error", error_message)
            raise err

        if response and response.status_code != 200:
            error_message = f"Status Code not 200\n\nData in PUT request: \n{str(data_to_post)}"
            error_message += (
                f"\n\nResponse: \n{response.status_code}\nResponse Text: {response.text}"
                f"\nRequest URL: {getattr(response.request, 'url', '')}"
                f"\nRequest Body: {getattr(response.request, 'body', '')}"
                if response is not None
                else ""
            )
            frappe.log_error("WooCommerce Error", error_message)
            raise ValueError(error_message)

    return True


def get_item_projected_qty(item_code, company):
    B = frappe.qb.DocType("Bin")
    W = frappe.qb.DocType("Warehouse")
    valid_warehouses = get_descendants_of("Warehouse", """Kenzie's Main - KO""")

    data = (
        frappe.qb.from_(B)
        .join(W)
        .on(B.warehouse == W.name)
        .select(fn.Sum(B.actual_qty - B.reserved_qty).as_("projected_qty"))
        .where(
            (B.item_code == item_code)
            & (W.company == company)
            & (W.name.isin(valid_warehouses))
            & (W.disabled == 0)
        )
        .groupby(B.item_code)
        .run()
    )

    return data[0][0] if data else 0


def update_stock_levels_on_variants(item_code):
    IWS = frappe.qb.DocType("Item WooCommerce Server")
    WS = frappe.qb.DocType("WooCommerce Server")

    conditions = [
        IWS.parent.like(f"%{item_code}%"),
        IWS.parent.like(f"%+%"),
        IWS.woocommerce_id.isnotnull(),
    ]

    variants = (
        frappe.qb.from_(IWS)
        .join(WS)
        .on(IWS.woocommerce_server == WS.name)
        .select(
            IWS.parent.as_("item_code"),
            IWS.woocommerce_server,
            IWS.woocommerce_id,
            WS.company,
            WS.woocommerce_server_url,
            WS.api_consumer_key,
            WS.api_consumer_secret,
        )
        .where(Criterion.all(conditions))
        .run(as_dict=True)
    )

    for variant in variants:
        item_stocks = []
        for it_code in variant["item_code"].split("+"):
            item_stocks.append(get_item_projected_qty(it_code, variant["company"]))

        stock_qty = min(item_stocks) if item_stocks else 0

        product_name = f"{variant['woocommerce_server']}~{variant['woocommerce_id']}"
        woo_product = frappe.get_doc("WooCommerce Product", product_name)
        if woo_product.type != "variation":
            continue

        parent_id = woo_product.parent_id
        variation_id = variant["woocommerce_id"]

        wc_api = APIWithRequestLogging(
            url=variant["woocommerce_server_url"],
            consumer_key=variant["api_consumer_key"],
            consumer_secret=variant["api_consumer_secret"],
            version="wc/v3",
            timeout=40,
        )

        data_to_post = {"stock_quantity": math.floor(stock_qty) if stock_qty >= 0 else 0}
        endpoint = f"products/{parent_id}/variations/{variation_id}"

        try:
            response = wc_api.put(endpoint=endpoint, data=data_to_post)
        except Exception:
            error_message = f"{frappe.get_traceback()}\n\nData in PUT request: \n{str(data_to_post)}"
            frappe.log_error("WooCommerce Variant Stock Update Error", error_message)
            raise

        if response.status_code != 200:
            error_message = f"Status Code not 200\n\nData in PUT request: \n{str(data_to_post)}"
            error_message += (
                f"\n\nResponse: \n{response.status_code}\nResponse Text: {response.text}"
                f"\nRequest URL: {getattr(response.request, 'url', '')}"
                f"\nRequest Body: {getattr(response.request, 'body', '')}"
                if response is not None
                else ""
            )
            frappe.log_error("WooCommerce Variant Stock Update Error", error_message)
            raise ValueError(error_message)