import json

import frappe
from erpnext.selling.doctype.sales_order.sales_order import SalesOrder
from frappe import _
from six import string_types
from frappe.model.naming import get_default_naming_series, make_autoname
from erpnext.selling.doctype.sales_order.sales_order import create_pick_list

from woocommerce_fusion.tasks.sync_sales_orders import run_sales_order_sync
from woocommerce_fusion.woocommerce.woocommerce_api import (
	generate_woocommerce_record_name_from_domain_and_id,
)


class CustomSalesOrder(SalesOrder):
	@property
	def tracking_number(self):
		SL = frappe.qb.DocType("ShippingLog")
		numbers = frappe.qb.from_(SL).select(SL.tracking_number).where(
			SL.sales_order == self.name
		).run(as_dict=True)
		tracking_numbers = [d.tracking_number for d in numbers]
		return "\n".join(tracking_numbers) if tracking_numbers else ""
	
	@property
	def serial(self):
		SL = frappe.qb.DocType("ShippingLog")
		serials = frappe.qb.from_(SL).select(SL.serial).where(
			SL.sales_order == self.name
		).run(as_dict=True)
		out = [d.serial for d in serials]
		return "\n".join(out) if out else ""
	
	@property
	def document(self):
		return self.name
	
	def validate(self):
		# Let's call the parent validate method first
		super(CustomSalesOrder, self).validate()
		self.copy_address()
		self.set_default_mode_of_delivery()
	
	def on_update_after_submit(self):
		self.set_default_mode_of_delivery()
	
	def copy_address(self):
		"""
		Copies the billing and shipping address from the Address DocType.
		"""
		if not self.shipping_address_name:
			return
		shipping_address = frappe.get_doc("Address", self.shipping_address_name)
		self.update({
			"ship_to": shipping_address.address_title,
			"address_line_1": shipping_address.address_line1,
			"address_line_2": shipping_address.address_line2,
			"city": shipping_address.city,
			"state": shipping_address.state,
			"pincode": shipping_address.pincode,
			"country": shipping_address.country,
		})
	
	def set_default_mode_of_delivery(self):
		if self.mode_of_delivery:
			return
		# If Order total
		# 0 - $99.99 USPS ground advantage
		# $100 - $500 USPS priority
		# $500+ UPS ground
		if self.base_grand_total < 100:
			self.mode_of_delivery = "USPS Ground Advantage"
		elif self.base_grand_total < 500:
			self.mode_of_delivery = "Priority Mail"
		else:
			self.mode_of_delivery = "UPS Ground"
		
		if not frappe.db.exists("Mode of Delivery", self.mode_of_delivery):
			frappe.throw(
				_("Mode of Delivery '{0}' does not exist. Please create it before proceeding.").format(self.mode_of_delivery)
			)
		mode_of_delivery = frappe.get_doc("Mode of Delivery", self.mode_of_delivery)
		self.update({
			"carrier_id": mode_of_delivery.carrier_company,
			"account_code": mode_of_delivery.carrier_account_code,
			"signature_required": mode_of_delivery.signature_required,
			"residential_destination": mode_of_delivery.residential,
			"bill_transportation_to": "Sender",
		})

@frappe.whitelist()
def get_woocommerce_order_shipment_trackings(doc):
	"""
	Fetches shipment tracking details from a WooCommerce order.
	"""
	doc = frappe._dict(json.loads(doc))
	if doc.woocommerce_server and doc.woocommerce_id:
		wc_order = get_woocommerce_order(doc.woocommerce_server, doc.woocommerce_id)
		if wc_order.shipment_trackings:
			return json.loads(wc_order.shipment_trackings)

	return []

@frappe.whitelist()
def update_woocommerce_order_shipment_trackings(doc, shipment_trackings):
	"""
	Updates the shipment tracking details of a specific WooCommerce order.
	"""
	doc = frappe._dict(json.loads(doc))
	if doc.woocommerce_server and doc.woocommerce_id:
		wc_order = get_woocommerce_order(doc.woocommerce_server, doc.woocommerce_id)
	wc_order.shipment_trackings = shipment_trackings
	wc_order.save()
	return wc_order.shipment_trackings

@frappe.whitelist()
def create_pick_lists(sales_orders):
	if isinstance(sales_orders, string_types):
		sales_orders = json.loads(sales_orders)
	success = []
	try:
		for name in sales_orders:
			pick_list = create_pick_list(name)
			pick_list.pick_manually = 1
			pick_list.scan_mode = 1
			pick_list.save()
			success.append(name)
		return success
	except Exception as e:
		title = _("Error creating Pick List")
		message = _("An error occurred while creating the Pick List for Sales Order {0}: {1}").format(name, str(e))
		message += f"<br><br>Traceback: {frappe.get_traceback()}"
		frappe.log_error(title, message)

def get_woocommerce_order(woocommerce_server, woocommerce_id):
	"""
	Retrieves a specific WooCommerce order based on its site and ID.
	"""
	# First verify if the WooCommerce site exits, and it sync is enabled
	wc_order_name = generate_woocommerce_record_name_from_domain_and_id(
		woocommerce_server, woocommerce_id
	)
	wc_server = frappe.get_cached_doc("WooCommerce Server", woocommerce_server)

	if not wc_server:
		frappe.throw(
			_(
				"This Sales Order is linked to WooCommerce site '{0}', but this site can not be found in 'WooCommerce Servers'"
			).format(woocommerce_server)
		)

	if not wc_server.enable_sync:
		frappe.throw(
			_(
				"This Sales Order is linked to WooCommerce site '{0}', but Synchronisation for this site is disabled in 'WooCommerce Server'"
			).format(woocommerce_server)
		)

	wc_order = frappe.get_doc({"doctype": "WooCommerce Order", "name": wc_order_name})
	wc_order.load_from_db()
	return wc_order

