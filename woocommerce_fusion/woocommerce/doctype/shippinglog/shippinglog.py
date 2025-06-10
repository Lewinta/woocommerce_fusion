# Copyright (c) 2024, ahmadragheb and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.query_builder import functions as fn
class ShippingLog(Document):
	def autoname(self):
		SL = frappe.qb.DocType("ShippingLog")
		name = frappe.qb.from_(SL).select(fn.Max(SL.name)).run()
		self.name = str((name[0][0]) + 1)
	
	def before_insert(self):
		# We get the ship date and time on a variable called ship timestamp
		# We need to extract these values 
		if not self.ship_date and not self.ship_time:
			self.ship_date, self.ship_time = str(self.ship_timestamp).split(" ")
		


def update_shipping_log_scheduler():
	frappe.db.sql("""
		UPDATE 
			`tabShippingLog`
		SET 
			ship_date = DATE(ship_timestamp),
			ship_time = TIME(ship_timestamp)
		WHERE 
			ship_date IS NULL;
	""")