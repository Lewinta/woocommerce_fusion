import frappe
import qrcode
import base64
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