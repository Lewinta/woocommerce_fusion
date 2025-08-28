# Copyright (c) 2024, ahmadragheb and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.query_builder import functions as fn
from erpnext.stock.doctype.pick_list.pick_list import create_delivery_note

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
		
	
	@frappe.whitelist()
	def publish_tracking_number(self):
		"""
		Publishes the tracking number to the E-commerce platforms
		"""
		if not self.tracking_number:
			return
		
		if not self.sales_order:
			frappe.msgprint(""""
				No Sales Order associated with this Shipping Log.
				Cannot publish tracking number.
			""")
			return
		so_doc = frappe.get_doc("Sales Order", self.sales_order)
		fulfillment_method = so_doc.fulfillment_method
		try:
			if so_doc.per_delivered < 100:
				dn = create_delivery_note(self.pick_list)
				dn.submit()
			response = None
			if fulfillment_method == "WooCommerce":
				self.publish_tracking_number_to_woocommerce()
			elif fulfillment_method == "eBay":
				response = self.publish_tracking_number_to_ebay()	
			elif fulfillment_method == "Amazon":
				self.publish_tracking_number_to_amazon()
			
			if response:
				self.log_shipment_update(
					fulfillment_method,
					"Success",
					response
				)
				self.save()
				return True
		except Exception as e:
			self.log_shipment_update(
				fulfillment_method,
				"Failed",
				message=str(e),
			)
			return False

	def publish_tracking_number_to_woocommerce(self):
		order = frappe.get_doc("Sales Order", self.sales_order)
		if not order.po_no or order.fulfillment_method != "WooCommerce":
			return
		
		name = f"{order.woocommerce_server}~{order.po_no}"
		
		wc_order = frappe.get_doc("WooCommerce Order", name)
		wc_order.update_shipment_tracking()
		wc_order.mark_order_completed()

	def publish_tracking_number_to_ebay(self):
		if not self.sales_order:
			return
		order = frappe.get_doc("Sales Order", self.sales_order)
		
		if not order.po_no or order.fulfillment_method != "eBay":
			return
		ebay_order = frappe.get_doc("eBay order", order.po_no)
		
		if not self.carrier_id:
			self.carrier_id = order.carrier_id

		return ebay_order.update_shipment_tracking(self.tracking_number, self.carrier_id)
		
	
	def publish_tracking_number_to_amazon(self):
		# TODO: Implement Amazon tracking number publishing
		pass

	def log_shipment_update(self, fulfillment_channel, status, message=None, published=None):
		if not published:
			published = frappe.utils.now()
		# Let's make sure we don't have an entry for this fulfillment channel
		row = list(filter(
			lambda x: x.fulfillment_channel == fulfillment_channel,
			self.sales_channels_update
		))
		if row:
			row = row[0]
			row.update({
				"fulfillment_channel": fulfillment_channel,
				"status": status,
	   			"published": published,
				"message": message,
			})
		else:
			self.append("sales_channels_update", {
				"fulfillment_channel": fulfillment_channel,
				"status": status,
				"published": published,
				"message": message,
			})


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

def publish_shipping_to_ecommerce():
	SL = frappe.qb.DocType("ShippingLog")
	STU = frappe.qb.DocType("Shipment Tracking Update")
	SO = frappe.qb.DocType("Sales Order")
	PL = frappe.qb.DocType("Pick List")

	pending_logs = frappe.qb.from_(SL).join(SO).on(
		SL.sales_order == SO.name
	).join(PL).on(
		SL.pick_list == PL.name
	).left_join(STU).on(	
		SL.name == STU.parent
	).select(
		SL.name
	).where(
		(SO.fulfillment_method.isin(["WooCommerce", "eBay"]))&
		(PL.status != "Completed")&
		(STU.name.isnull())
	).run(as_dict=True)
	
	for row in pending_logs:
		sl = frappe.get_doc("ShippingLog", row.name)
		# Create a Delivery Note to release the stock
		try:
			# Publish the tracking number to the E-Commerce 
			sl.publish_tracking_number()
			frappe.db.commit()
		except Exception as e:
			frappe.db.rollback()
			msg = f"Payload: {sl.as_json()}"
			msg += f"\nTraceback: {frappe.get_traceback()}"
			frappe.log_error("Failed to publish to e-commerce", msg)
			frappe.db.commit()

			
