import traceback

import frappe
import requests
from woocommerce import API

DEFAULT_TIMEOUT = 30
DEFAULT_UA = "TZCode-ERPNext-WooSync/1.0"

class APIWithRequestLogging(API):
    """WooCommerce API with Request Logging + sane defaults."""

    def __init__(self, *args, **kwargs):
        # Set persistent defaults on the client.
        kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
        kwargs.setdefault("user_agent", DEFAULT_UA)
        # Cloudflare often blocks Basic; query param auth worked for your store.
        kwargs.setdefault("query_string_auth", True)
        super().__init__(*args, **kwargs)

    def _API__request(self, method, endpoint, data=None, params=None, **kwargs):
        params = params or {}

        # DO NOT pass timeout or headers via kwargs (parent already passes both).
        kwargs.pop("timeout", None)
        kwargs.pop("headers", None)

        try:
            # First attempt with current settings (query-string auth by default).
            return super()._API__request(method, endpoint, data, params, **kwargs)
        except requests.HTTPError as e:
            r = getattr(e, "response", None)
            if r is not None and r.status_code == 403 and method.upper() == "GET":
                # Defensive fallback: force creds into query if stripped upstream.
                ck = getattr(self, "consumer_key", None)
                cs = getattr(self, "consumer_secret", None)
                if ck and cs:
                    q = dict(params)
                    q.setdefault("consumer_key", ck)
                    q.setdefault("consumer_secret", cs)
                    return super()._API__request(method, endpoint, data, q, **kwargs)
            raise

def log_woocommerce_request(
	url: str,
	endpoint: str,
	request_method: str,
	params: dict,
	data: dict,
	res: requests.Response | None = None,
	traceback: str = None,
):
	request_log = frappe.get_doc(
		{
			"doctype": "WooCommerce Request Log",
			"user": frappe.session.user if frappe.session.user else None,
			"url": url,
			"endpoint": endpoint,
			"method": request_method,
			"params": frappe.as_json(params) if params else None,
			"data": frappe.as_json(data) if data else None,
			"response": f"{str(res)}\n{res.text}" if res is not None else None,
			"error": frappe.get_traceback(),
			"status": "Success" if res and res.status_code in [200, 201] else "Error",
			"traceback": traceback,
			"time_elapsed": res.elapsed.total_seconds() if res is not None else None,
		}
	)
	# request_log.db_insert(ignore_permissions=True)
	return