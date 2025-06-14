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

	# override
	def before_insert(self):
		self.auto_select_warehouse(replace=True)

	def auto_select_warehouse(self, replace=False):
		# if order is from an online store auto-select warehouse for each item
		# based on their availability (if there is stock)
		if self.fulfillment_method not in {"MFN", "eBay", "WooCommerce"}:
			return # only for online orders (add more if needed)

		for item in self.items.copy(): # use copy to avoid modifying the original list while iterating
			if item.warehouse and not replace:
				continue

			warehouse = self._get_warehouse_based_on_availability(item)
			if warehouse:
				item.warehouse = warehouse
			else:
				self._distribute_based_on_availability(item)
			
	def _distribute_based_on_availability(self, item):
		# check to see if the item is availabe at different locations (warehouses)
		# if so, we need to select the first and assign the available qty at that warehouse
		# and then duplicate the item line for each warehouse until the qty is met
		warehouses = frappe.get_all(
			"Bin",
			fields=["warehouse", "actual_qty"],
			filters={
				"item_code": item.item_code,
				"actual_qty": [">", 0]
			},
			order_by="actual_qty DESC",
		)

		# we are working on the assumption that the warehouse available qty is lesser than the item qty
		if warehouses:
			original_qty = item.qty

			for idx, warehouse in enumerate(warehouses):
				# first warehouse will be mapped to the current item
				if idx == 0:
					item.warehouse = warehouse.warehouse
					item.qty = min(original_qty, warehouse.actual_qty)
					original_qty -= item.qty
					if original_qty <= 0: # unlikely to happen but just in case
						break

					continue
				# for subsequent warehouses, we need to create a new item row
				# with the warehouse and the qty available at that warehouse
				# if the original qty is already met, we can break

				if original_qty <= 0:
					break

				# create a new item row for each warehouse
				new_item = frappe.copy_doc(item)
				new_item.docstatus = 0  # reset docstatus to draft
				new_item.warehouse = warehouse.warehouse
				new_item.qty = min(original_qty, warehouse.actual_qty)
				new_item.stock_qty = new_item.qty * new_item.conversion_factor
				new_item.amount = new_item.qty * new_item.rate
				new_item.base_amount = new_item.qty * new_item.base_rate
				self.append("items", new_item).db_insert()

				# reduce the original qty by the qty assigned to the new item
				original_qty -= new_item.qty

			if original_qty > 0:
				# if there is still some qty left, we can log an error
				frappe.log_error(
					_("Not enough stock available for item {0}").format(item.item_code),
					_("Sales Order {0}").format(self.name)
				)
			else:
				# if we have successfully assigned all the qty, we can remove the original item
				...


			# refresh idxs in because we have added new items
			for idx, item in enumerate(self.items):
				item.idx = idx + 1


			self.calculate_taxes_and_totals()
		else:
			frappe.log_error(
				_("No stock available for item {0}").format(item.item_code),
				_("Sales Order {0}").format(self.name)
			)
 		

	def _get_warehouse_based_on_availability(self, item):
		"""
		Returns the warehouse with the highest stock for the item.
		If no stock is available, returns None.
		"""
		if not item.item_code:
			return None

		warehouses = frappe.get_all(
			"Bin",
			fields=["warehouse"],
			filters={
				"item_code": item.item_code,
				"actual_qty": [">", item.qty or 0],
			},
			order_by="actual_qty DESC", # Ideally this should be FIFO
			limit=1
		)

		return warehouses[0].warehouse if warehouses else None

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
