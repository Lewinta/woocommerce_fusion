import frappe
import qrcode
import base64
import json
from frappe.utils import get_datetime, now, format_datetime
from frappe.utils.data import flt
from io import BytesIO
from frappe.query_builder import Query, Criterion
from frappe.query_builder.custom import ConstantColumn

def generate_qr(data: str) -> str:
    """Generate a base64 PNG QR code from data."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=4,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{img_str}"

@frappe.whitelist()
def get_document(name, doctype=None):
    """Fetch a document by name and doctype."""
    PL = frappe.qb.DocType("Pick List")
    SO = frappe.qb.DocType("Sales Order")
    I = frappe.qb.DocType("Item")


    pick_lists = Query.from_(PL).select(
        ConstantColumn("Pick List").as_("doctype"),
        PL.name
    )

    sales_orders = Query.from_(SO).select(
        ConstantColumn("Sales Order").as_("doctype"),
        SO.name
    )

    items = Query.from_(I).select(
        ConstantColumn("Item").as_("doctype"),
        SO.name
    )

    query = pick_lists + sales_orders + items

    conditions = [
        query.name == name,
    ]
    if doctype:
        conditions.append(query.doctype == doctype)

    result = frappe.qb.from_(query).select('*').where(
        Criterion.all(conditions)
    ).run(as_dict=True)

    return result[0] if result else None


def _loads_json_maybe(value, default):
    """Return parsed JSON if value is a JSON string; pass dict/list through; else default."""
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str) and value.strip():
        try:
            return json.loads(value)
        except Exception:
            return default
    return default

def _format_woo_address(addr: dict) -> str:
    if not addr:
        return ""
    parts = [
        " ".join([p for p in [addr.get("first_name"), addr.get("last_name")] if p]),
        addr.get("company"),
        " ".join([p for p in [addr.get("address_1"), addr.get("address_2")] if p]),
        ", ".join([p for p in [addr.get("city"), addr.get("state"), addr.get("postcode")] if p]),
        addr.get("country"),
        addr.get("phone"),
        addr.get("email"),
    ]
    return ", ".join([p for p in parts if p])

def _flatten_items(line_items):
    """Normalize Woo line_items to a simple list the template can iterate."""
    out = []
    for it in (line_items or []):
        qty = int(it.get("quantity") or 0)
        price = flt(it.get("price") if it.get("price") is not None else it.get("total"))
        tax = flt(it.get("total_tax") or 0)
        # Some payloads have numeric "price"; others only totals as strings
        # If price is 0 but subtotal exists, derive per-unit price from subtotal/qty.
        if price == 0 and qty > 0:
            sub = flt(it.get("subtotal") or it.get("total") or 0)
            price = sub / qty if qty else 0
        line_total = qty * price + tax

        out.append({
            "sku": it.get("sku") or "",
            "title": it.get("name") or "",
            "qty": qty,
            "price": price,
            "tax": tax,
            "line_total": line_total,
            "attributes": [(md.get("display_key") or md.get("key"), md.get("display_value") or md.get("value"))
                           for md in _loads_json_maybe(it.get("meta_data"), [])]
        })
    return out


def notify_users_woo(order: dict, e: Exception, tb: str):
    """
    Send email notification about error creating Sales Invoice for a WooCommerce order.
    Expects 'order' to be the dict you showed (with some JSON-string fields).
    Returns rendered HTML (you can send it with frappe.sendmail).
    """
    # Core identifiers
    order_id = order.get("number") or order.get("id") or order.get("name") or "—"
    channel = "WooCommerce"
    subject = f"Error creating Sales Invoice · Woo Order {order_id}"
    server  = order.get("woocommerce_server")

    # Dates
    created_dt = None
    for key in ("date_created", "date_created_gmt", "modified", "date_modified_gmt"):
        if order.get(key):
            try:
                created_dt = get_datetime(order[key])
                break
            except Exception:
                pass

    # Currency & totals
    currency = order.get("currency") or "USD"
    total = flt(order.get("total") or 0)
    total_tax = flt(order.get("total_tax") or 0)
    shipping_total = flt(order.get("shipping_total") or 0)
    discount_total = flt(order.get("discount_total") or 0)

    # Nested blobs that often arrive as JSON strings
    billing = _loads_json_maybe(order.get("billing"), {})
    shipping = _loads_json_maybe(order.get("shipping"), {})
    line_items = _loads_json_maybe(order.get("line_items"), [])
    tax_lines = _loads_json_maybe(order.get("tax_lines"), [])
    shipping_lines = _loads_json_maybe(order.get("shipping_lines"), [])
    fee_lines = _loads_json_maybe(order.get("fee_lines"), [])
    coupon_lines = _loads_json_maybe(order.get("coupon_lines"), [])
    meta_data = _loads_json_maybe(order.get("meta_data"), [])

    # Buyer email: prefer billing.email
    buyer_email = (billing or {}).get("email") or ""
    buyer_name = " ".join([p for p in [(billing or {}).get("first_name"), (billing or {}).get("last_name")] if p]) or None

    # Shipping method label (if any)
    ship_level = None
    if shipping_lines:
        # Can be multiple; take first label/method_title if present
        first_ship = shipping_lines[0]
        ship_level = first_ship.get("method_title") or first_ship.get("method_id")

    # Make a compact items list for the template
    items_flat = _flatten_items(line_items)

    # Compose addresses
    billing_address = _format_woo_address(billing)
    shipping_address = _format_woo_address(shipping)

    # Build a compact meta dict for quick consumption in the template if you like
    meta_compact = {m.get("key"): m.get("value") for m in meta_data if isinstance(m, dict) and m.get("key")}

    context = {
        "subject": subject,
        "channel": channel,
        "fulfillment": ship_level,
        "order": order,                         
        "order_id": order_id,
        "status": order.get("status"),
        "site": server,
        "buyer_user": None,                     
        "buyer_email": buyer_email,
        "buyer_name": buyer_name,
        "created_local": format_datetime(created_dt) if created_dt else "—",
        "ship_level": ship_level,
        "shipping_address": shipping_address,
        "billing_address": billing_address,
        "currency": currency,
        "totals": {
            "items_total": sum(i["line_total"] for i in items_flat),
            "shipping_total": shipping_total,
            "discount_total": discount_total,
            "tax_total": total_tax,
            "grand_total": total if total else sum(i["line_total"] for i in items_flat) + shipping_total - discount_total,
        },
        "items": items_flat,
        "tax_lines": tax_lines,
        "shipping_lines": shipping_lines,
        "fee_lines": fee_lines,
        "coupon_lines": coupon_lines,
        "meta": meta_compact,

        "error_message": str(e),
        "traceback": tb,
        "payload_pretty": json.dumps(order, indent=2, ensure_ascii=False, default=str),
        "now_str": format_datetime(now()),
    }

    html = frappe.render_template("templates/email/woocommerce_import_error.html", context)
    if not server:
        return
    
    notify_to = frappe.get_value("WooCommerce Server", server, "notify_users")
    if notify_to:
        recipients = [u.strip() for u in notify_to.split("\n") if u.strip()]
        if recipients:
            frappe.sendmail(recipients=recipients, subject=subject, message=html)