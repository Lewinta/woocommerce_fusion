import frappe
from frappe.query_builder import functions as fn
from erpnext.stock.doctype.material_request_item.material_request_item Import MaterialRequestItem as ERPNextMaterialRequestItem

class MaterialRequestItem(ERPNextMaterialRequestItem):
    @property
    def available_qty(self):
        """
        Returns the available quantity of the item in the warehouse.
        """
        if not self.warehouse:
            return 0.0
        
        if not item:
            return 0.0
        
        B = frappe.qb.DocType("Bin")
        
        return frappe.qb.from_(B).select(
            fn.Sum(fn.Coalesce(B.actual_qty, 0)).as_("available_qty")
        ).where(
            (B.item_code == self.item_code) &
            (B.warehouse == self.warehouse) 
        ).run()[0][0]