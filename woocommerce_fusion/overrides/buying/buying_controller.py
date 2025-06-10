import frappe
from frappe.query_builder import Criterion,Case, functions as fn

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_supplier_items(doctype, txt, searchfield, start, page_len, filters):
    I = frappe.qb.DocType("Item")
    SI = frappe.qb.DocType("Item Supplier")
    
    conditions = []
    
    if filters.get("disabled") is not None:
        conditions.append(
            I.disabled == filters.get("disabled")
        )
    if filters.get("is_purchase_item") is not None:
        conditions.append(
            I.is_purchase_item == filters.get("is_purchase_item")
        )
    if filters.get("has_variants") is not None:
        conditions.append(
            I.has_variants == filters.get("has_variants")
        )
    if filters.get("supplier"):
        conditions.append(
            SI.supplier == filters.get("supplier")
        )
    
    if txt and len(txt) > 0:
        conditions.append(
            (I.item_code.like(f"%{txt}%") | I.item_name.like(f"%{txt}%"))
        )

    return frappe.qb.from_(I).join(SI).on(
            I.name == SI.parent
        ).select(
            I.name,
            I.item_group,
            I.item_name,
            Case().when(
                fn.Length(I.description) > 40,
                fn.Concat(fn.Substring(I.description, 0, 40), "...")
            ).else_(I.description).as_("description")
        ).where(
            Criterion.all(conditions)
        ).orderby(I.item_code).limit(20).run(as_list=True)        
