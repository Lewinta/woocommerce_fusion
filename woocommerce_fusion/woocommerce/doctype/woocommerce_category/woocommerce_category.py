# Copyright (c) 2025, Dirk van der Laarse and contributors
# For license information, please see license.txt

import frappe
import requests
from frappe.model.document import Document

class WoocommerceCategory(Document):	
	pass

def get_categories(id=None):
	# WooCommerce API Credentials
	WOOCOMMERCE_URL = "https://mratest.makereadyarmz.com"  # Replace with your store URL
	CONSUMER_KEY = "ck_90b725c58ab79c25f23fdc185ee5b70e6b76fa30"  # Replace with API key from WooCommerce
	CONSUMER_SECRET = "cs_412c69b5e725ea2cca4412cadbee4902bb401296"  # Replace with API secret from WooCommerce

	# API Endpoint
	endpoint = f"{WOOCOMMERCE_URL}/wp-json/wc/v3/products/categories"
	if id:
		endpoint += f"/{id}"

	# Make the request
	response = requests.get(endpoint, auth=(CONSUMER_KEY, CONSUMER_SECRET))

	# Parse and print the categories
	if response.status_code == 200:
		# Categories can be an array or a single object if not id is specified
		# If id is specified, categories will be a single object
		categories = response.json()

		if isinstance(categories, dict):
			return map_category(categories)
		else:
			docs = []
			for category in categories:
				docs.append(map_category(category))
			return docs[0] if id else docs
	else:
		return []

def map_category(category):
	return {
		"name": category["id"],
		"category_name": category["name"],
		"slug": category["slug"]
	}