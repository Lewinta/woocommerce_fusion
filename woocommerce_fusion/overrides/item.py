import frappe
from erpnext.stock.doctype.item.item import Item as ERPNextItem

class Item(ERPNextItem):
    @property
    def custom_external_image(self):
        # Let's make sure we return the full URL
        # If you have SSL in the site please make sure you 
        # Add the hostname in the site_config.json
        if self.image:
            return frappe.utils.get_url(self.image)
