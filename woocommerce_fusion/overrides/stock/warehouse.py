import frappe

from erpnext.stock.doctype.warehouse.warehouse import Warehouse as ERPNextWarehouse

class Warehouse(ERPNextWarehouse):
    @property
    def zone(self):
        """
        Returns the zone of the warehouse.
        """
        return self.get_zone()

    def get_zone(self):
        if not self.parent_warehouse:
            return None
        
        parent_warehouse = frappe.get_doc("Warehouse", self.parent_warehouse)
        
        return parent_warehouse.name if parent_warehouse.warehouse_type == "Zones" \
            else parent_warehouse.get_zone() 