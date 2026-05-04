import frappe
from frappe import _, msgprint

@frappe.whitelist()
def get_invoice_items(scan_input):
	"""
	Fetch items from a Sales Invoice given its standard name or WooCommerce po_no.
	If an item has packed items (Product Bundle), fetch those instead of the parent.
	"""
	try:
		# Check standard name first using fast db get
		invoice_name = frappe.db.get_value("Sales Invoice", {"name": scan_input}, "name")
		
		# Check po_no if standard name fails
		if not invoice_name:
			invoice_name = frappe.db.get_value("Sales Invoice", {"po_no": scan_input}, "name")
			
		if not invoice_name:
			return {"error": f"Sales Invoice not found for: {scan_input}"}

		invoice_doc = frappe.get_doc("Sales Invoice", invoice_name)
		
		# Prevent scanning if already picked and ready
		if getattr(invoice_doc, "custom_ready_to_dispatch", 0) == 1:
			return {"error": f"Sales Invoice {invoice_name} has already been marked as picked!"}

		items_to_pick = {}
		EXCLUDED_ITEMS = {"SRV-001"}

		# Safe extraction of packed items
		packed_items = invoice_doc.get("packed_items") or []
		bundle_parent_items = set([getattr(p, "parent_item", "") for p in packed_items if getattr(p, "parent_item", "")])

		# Safe extraction of normal items
		for item in invoice_doc.get("items") or []:
			i_code = getattr(item, "item_code", None) or getattr(item, "item_name", "Unknown")
			if i_code in EXCLUDED_ITEMS:
				continue
			barcode = getattr(item, "barcode", "")
			if not barcode and i_code:
				barcode = frappe.db.get_value("Item Barcode", {"parent": i_code}, "barcode") or ""

			if i_code not in bundle_parent_items:
				if i_code not in items_to_pick:
					item_info = frappe.db.get_value("Item", i_code, ["item_name", "image"], as_dict=True) or {}
					items_to_pick[i_code] = {
						"qty": 0, 
						"barcode": barcode,
						"item_name": getattr(item, "item_name", "") or item_info.get("item_name", "Unknown"),
						"image": getattr(item, "image", "") or item_info.get("image", "")
					}
				items_to_pick[i_code]["qty"] += getattr(item, "qty", 0)
				if barcode and not items_to_pick[i_code]["barcode"]:
					items_to_pick[i_code]["barcode"] = barcode

		# Include packed items safely
		for p_item in packed_items:
			p_code = getattr(p_item, "item_code", None) or getattr(p_item, "item_name", "Unknown")
			if p_code in EXCLUDED_ITEMS:
				continue
			if p_code not in items_to_pick:
				p_item_info = frappe.db.get_value("Item", p_code, ["item_name", "image"], as_dict=True) or {}
				items_to_pick[p_code] = {
					"qty": 0, 
					"barcode": frappe.db.get_value("Item Barcode", {"parent": p_code}, "barcode") or "",
					"item_name": getattr(p_item, "item_name", "") or p_item_info.get("item_name", "Unknown"),
					"image": getattr(p_item, "image", "") or p_item_info.get("image", "")
				}
			items_to_pick[p_code]["qty"] += getattr(p_item, "qty", 0)

		# Format response
		return {
			"invoice_name": invoice_doc.name,
			"po_no": getattr(invoice_doc, "po_no", ""),
			"status": getattr(invoice_doc, "status", ""),
			"items": [{
				"item_code": k, 
				"qty": v["qty"], 
				"barcode": v["barcode"],
				"item_name": v["item_name"],
				"image": v["image"]
			} for k, v in items_to_pick.items() if v["qty"] > 0]
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), f"Order Picking Error: {scan_input}")
		return {"error": f"Backend Error: {str(e)}"}

@frappe.whitelist()
def get_active_order_pick(force_new=0):
	"""
	Returns the current Draft Order Pick session for the user, or creates one, along with the user's name.
	"""
	user_info = frappe.db.get_value("User", frappe.session.user, ["full_name", "user_image"], as_dict=True) or {}
	user_name = user_info.get("full_name") or frappe.session.user
	user_image = user_info.get("user_image") or ""
	
	if not frappe.utils.cint(force_new):
		active_picks = frappe.get_all("Order Pick", filters={"docstatus": 0, "owner": frappe.session.user}, limit=1)
		if active_picks:
			return {
				"order_pick_id": active_picks[0].name,
				"user_name": user_name,
				"user_image": user_image
			}

	new_pick = frappe.new_doc("Order Pick")
	new_pick.picking_date = frappe.utils.now()
	new_pick.picked_by = frappe.session.user
	new_pick.insert(ignore_permissions=True)
	
	return {
		"order_pick_id": new_pick.name,
		"user_name": user_name,
		"user_image": user_image
	}

@frappe.whitelist()
def mark_invoice_as_ready(invoice_name, order_pick_id=None):
	"""
	Check the 'custom_ready_to_dispatch' field on the submitted invoice.
	If order_pick_id is provided, also attach the invoice to the Order Pick session.
	"""
	if not frappe.db.exists("Sales Invoice", invoice_name):
		frappe.throw(_("Sales Invoice {0} not found").format(invoice_name))

	# Update the field specifically on the database to bypass submit restrictions
	# using update_modified=False to prevent status recalculations
	frappe.db.set_value(
		"Sales Invoice", invoice_name, 
		{
			"custom_ready_to_dispatch": 1,
			"custom_order_ready_to_dispatch": 1
		},
		update_modified=False
	)
	
	# Attach to the active session
	if order_pick_id:
		order_pick = frappe.get_doc("Order Pick", order_pick_id)
		if order_pick.owner != frappe.session.user:
			frappe.throw(_("You are not authorized to modify this Order Pick session."))
		# Ensure it's not already added
		exists = next((i for i in order_pick.invoices if i.sales_invoice == invoice_name), None)
		if not exists:
			order_pick.append("invoices", {
				"sales_invoice": invoice_name
			})
			order_pick.save(ignore_permissions=True)

	# Add a comment to the timeline for visibility
	invoice_doc = frappe.get_doc("Sales Invoice", invoice_name)
	invoice_doc.add_comment("Info", _("Order fully picked and marked as Ready to Dispatch via Order Picking App."))

	return True

@frappe.whitelist()
def submit_order_pick(order_pick_id):
	"""
	Submits the Order Pick session. The document's on_submit logic will
	create the Dispatch Order draft automatically.
	"""
	try:
		doc = frappe.get_doc("Order Pick", order_pick_id)
		doc.flags.ignore_permissions = True
		doc.submit()
		return {"status": "success"}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Order Pick Submit Error")
		frappe.throw(f"Submission failed: {str(e)}")


@frappe.whitelist()
def submit_sales_invoice(invoice_name):
	"""
	Submits the given Sales Invoice from the UI if it is in Draft status.
	"""
	try:
		doc = frappe.get_doc("Sales Invoice", invoice_name)
		if doc.docstatus == 0:
			doc.submit()
			# Fetch the updated status
			new_status = frappe.db.get_value("Sales Invoice", invoice_name, "status")
			return {"status": "success", "new_status": new_status}
		else:
			return {"error": f"Sales Invoice {invoice_name} is already submitted."}
	except frappe.exceptions.ValidationError as e:
		frappe.throw(str(e))
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), f"Sales Invoice Submit Error: {invoice_name}")
		return {"error": f"Submission failed: {str(e)}"}


# ──────────────────────────────────────────────────────────────────────
# B2B ORDER PICKING — Sales Order + Material Request + Stock Entry
# ──────────────────────────────────────────────────────────────────────

def get_item_barcode_map(item_codes):
	"""
	Build a flat barcode → {item_code, qty} mapping for a list of item codes.
	Each Item Barcode row has a `uom` field; we look up the conversion_factor
	from `UOM Conversion Detail` (child of Item) for that UOM.
	Barcodes without a UOM default to qty=1.
	Also returns item_code itself and item_name as fallback barcodes with qty=1.
	"""
	barcode_map = {}
	if not item_codes:
		return barcode_map

	# Fetch all barcodes for the given items
	barcodes = frappe.get_all(
		"Item Barcode",
		filters={"parent": ["in", item_codes]},
		fields=["parent as item_code", "barcode", "uom"]
	)

	for bc in barcodes:
		conversion = 1
		if bc.uom:
			cf = frappe.db.get_value(
				"UOM Conversion Detail",
				{"parent": bc.item_code, "uom": bc.uom},
				"conversion_factor"
			)
			if cf:
				conversion = float(cf)
		barcode_map[bc.barcode] = {
			"item_code": bc.item_code,
			"qty": conversion
		}

	return barcode_map


@frappe.whitelist()
def get_sales_order_items(scan_input):
	"""
	Fetch items from a Sales Order given its standard name or po_no.
	Returns customer name, status, items with pending qty, and a barcode map.
	"""
	try:
		# Resolve by name first
		so_name = frappe.db.get_value("Sales Order", {"name": scan_input}, "name")
		if not so_name:
			so_name = frappe.db.get_value("Sales Order", {"po_no": scan_input}, "name")
		if not so_name:
			return {"error": f"Sales Order not found for: {scan_input}"}

		so_doc = frappe.get_doc("Sales Order", so_name)

		# Prevent re-scan if already picked
		if getattr(so_doc, "custom_b2b_picked", 0) == 1:
			return {"error": f"Sales Order {so_name} has already been picked by B2B Order Pick!"}

		EXCLUDED_ITEMS = {"SRV-001"}
		items_to_pick = {}

		for item in so_doc.get("items") or []:
			i_code = getattr(item, "item_code", None) or getattr(item, "item_name", "Unknown")
			if i_code in EXCLUDED_ITEMS:
				continue
			qty = getattr(item, "qty", 0)
			if qty <= 0:
				continue

			if i_code not in items_to_pick:
				item_info = frappe.db.get_value("Item", i_code, ["item_name", "image", "stock_uom"], as_dict=True) or {}
				items_to_pick[i_code] = {
					"qty": 0,
					"item_name": getattr(item, "item_name", "") or item_info.get("item_name", "Unknown"),
					"image": getattr(item, "image", "") or item_info.get("image", ""),
					"uom": getattr(item, "uom", "") or item_info.get("stock_uom", "Nos"),
				}
			items_to_pick[i_code]["qty"] += qty

		# Build barcode map for all items
		barcode_map = get_item_barcode_map(list(items_to_pick.keys()))

		# Also add item_code itself as a barcode with qty=1
		for i_code in items_to_pick:
			if i_code not in barcode_map:
				barcode_map[i_code] = {"item_code": i_code, "qty": 1}

		return {
			"so_name": so_doc.name,
			"customer_name": getattr(so_doc, "customer_name", "") or getattr(so_doc, "customer", ""),
			"status": getattr(so_doc, "status", ""),
			"items": [{
				"item_code": k,
				"qty": v["qty"],
				"item_name": v["item_name"],
				"image": v["image"],
				"uom": v["uom"],
			} for k, v in items_to_pick.items() if v["qty"] > 0],
			"barcode_map": barcode_map
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), f"B2B Order Picking Error: {scan_input}")
		return {"error": f"Backend Error: {str(e)}"}


@frappe.whitelist()
def get_stock_for_items(item_codes, warehouse):
	"""
	Return actual stock balance for a list of item codes in a given warehouse.
	Used to validate stock availability before picking.
	`item_codes` is a JSON string list.
	"""
	import json as _json
	from erpnext.stock.utils import get_stock_balance

	if isinstance(item_codes, str):
		item_codes = _json.loads(item_codes)

	stock = {}
	for item_code in item_codes:
		try:
			balance = get_stock_balance(item_code, warehouse) or 0
			stock[item_code] = float(balance)
		except Exception:
			stock[item_code] = 0

	return stock


@frappe.whitelist()
def get_sales_order_print_data(so_name):
	"""Return all data needed for the customer-facing order print."""
	if not frappe.db.exists("Sales Order", so_name):
		frappe.throw(f"Sales Order {so_name} not found")

	so = frappe.get_doc("Sales Order", so_name)

	# Customer address
	address_text = ""
	if so.customer_address:
		addr = frappe.get_doc("Address", so.customer_address)
		parts = [
			addr.address_line1,
			addr.address_line2,
			addr.city,
			addr.state,
			addr.country,
		]
		address_text = ", ".join(p for p in parts if p)

	# Contact details
	contact_text = ""
	if so.contact_person:
		try:
			contact = frappe.get_doc("Contact", so.contact_person)
			name_parts = [contact.first_name, contact.last_name]
			contact_name = " ".join(p for p in name_parts if p)
			phones = [p.phone for p in (contact.phone_nos or []) if p.phone]
			emails = [e.email_id for e in (contact.email_ids or []) if e.email_id]
			parts = [contact_name] + phones + emails
			contact_text = " | ".join(p for p in parts if p)
		except Exception:
			pass

	items = []
	for item in so.items:
		barcodes = frappe.db.get_all(
			"Item Barcode",
			filters={"parent": item.item_code},
			fields=["barcode"],
			order_by="idx asc"
		)
		bc_list = [b.barcode for b in barcodes if b.barcode]
		items.append({
			"item_code": item.item_code,
			"item_name": item.item_name or "",
			"barcodes": bc_list,
			"qty": item.qty,
			"uom": item.uom or "Nos",
			"rate": item.rate,
			"amount": item.amount,
			"discount_percentage": item.discount_percentage or 0,
			"price_list_rate": item.price_list_rate or 0,
		})

	return {
		"so_name": so.name,
		"customer": so.customer_name or so.customer,
		"address": address_text,
		"contact": contact_text,
		"date": str(so.transaction_date or ""),
		"po_number": so.po_no or "",
		"currency": so.currency or "KWD",
		"total_qty": so.total_qty or 0,
		"total": so.total or 0,
		"discount_amount": so.discount_amount or 0,
		"grand_total": so.grand_total or 0,
		"taxes_and_charges": so.taxes_and_charges or "",
		"total_taxes_and_charges": so.total_taxes_and_charges or 0,
		"items": items,
	}


@frappe.whitelist()
def get_item_barcodes(item_codes):
	"""Return all barcodes for a list of item codes. item_codes is a JSON string list."""
	import json as _json
	if isinstance(item_codes, str):
		item_codes = _json.loads(item_codes)
	result = {}
	for item_code in item_codes:
		rows = frappe.db.get_all(
			"Item Barcode",
			filters={"parent": item_code},
			fields=["barcode"],
			order_by="idx asc"
		)
		result[item_code] = [r.barcode for r in rows if r.barcode]
	return result


@frappe.whitelist()
def get_warehouses_and_cost_centers():
	"""Return active warehouses and cost centers for dropdown selection."""
	warehouses = frappe.get_all(
		"Warehouse",
		filters={"is_group": 0, "disabled": 0},
		fields=["name"],
		order_by="name asc",
		limit_page_length=0
	)
	cost_centers = frappe.get_all(
		"Cost Center",
		filters={"is_group": 0, "disabled": 0},
		fields=["name"],
		order_by="name asc",
		limit_page_length=0
	)
	return {
		"warehouses": [w.name for w in warehouses],
		"cost_centers": [c.name for c in cost_centers]
	}


@frappe.whitelist()
def create_b2b_material_request(so_name, items, source_warehouse, target_warehouse, required_by_date):
	"""
	Create a Draft Material Request (Material Transfer) linked to a Sales Order.
	`items` is a JSON string: [{"item_code": "...", "qty": ..., "uom": "...", "source_warehouse": "...", "target_warehouse": "..."}]
	Each item can optionally specify its own source/target warehouse for multi-warehouse transfers.
	Falls back to the top-level source_warehouse/target_warehouse if not provided per item.
	"""
	import json as _json

	if isinstance(items, str):
		items = _json.loads(items)

	if not frappe.db.exists("Sales Order", so_name):
		frappe.throw(_("Sales Order {0} not found").format(so_name))

	mr = frappe.new_doc("Material Request")
	mr.material_request_type = "Material Transfer"
	mr.schedule_date = required_by_date or frappe.utils.today()

	for item in items:
		mr.append("items", {
			"item_code": item["item_code"],
			"qty": item["qty"],
			"uom": item.get("uom", "Nos"),
			"schedule_date": required_by_date or frappe.utils.today(),
			"warehouse": item.get("target_warehouse") or target_warehouse,
			"from_warehouse": item.get("source_warehouse") or source_warehouse,
			"sales_order": so_name,
		})

	mr.insert(ignore_permissions=True)
	frappe.db.commit()

	return {"mr_name": mr.name}


@frappe.whitelist()
def submit_b2b_material_request(mr_name):
	"""Submit a Draft Material Request."""
	if not frappe.db.exists("Material Request", mr_name):
		frappe.throw(_("Material Request {0} not found").format(mr_name))

	doc = frappe.get_doc("Material Request", mr_name)
	doc.flags.ignore_permissions = True
	doc.submit()

	return {"status": "success", "mr_name": doc.name}


def _fmt_qty(q):
	f = float(q or 0)
	return "{:.0f}".format(f) if f == int(f) else "{:.3f}".format(f).rstrip("0").rstrip(".")


def _sync_so_to_picked(so_name, mr_doc):
	"""
	Align a submitted Sales Order with what was actually picked (called only on partial picks).
	- Items not picked at all are removed.
	- Items picked in lower qty have their qty reduced.
	- Fully-picked items (and over-picks) are left unchanged.
	Uses ERPNext's update_child_qty_rate so the SO can be modified post-submit.
	Returns a list of human-readable change strings.
	"""
	from erpnext.controllers.accounts_controller import update_child_qty_rate
	import json as _json

	picked_qty_map = {}
	for it in mr_doc.items:
		picked_qty_map[it.item_code] = picked_qty_map.get(it.item_code, 0) + (it.qty or 0)

	so_doc = frappe.get_doc("Sales Order", so_name)
	if so_doc.docstatus != 1:
		return []

	rows_by_code = {}
	for row in so_doc.items:
		rows_by_code.setdefault(row.item_code, []).append(row)

	trans_items = []
	changes = []

	for item_code, rows in rows_by_code.items():
		total_orig = sum(r.qty for r in rows)
		picked = picked_qty_map.get(item_code, 0)

		if picked <= 0:
			changes.append(_("Removed: {0} (was {1}, not picked)").format(item_code, _fmt_qty(total_orig)))
			continue

		if picked >= total_orig:
			for r in rows:
				trans_items.append({
					"item_code": r.item_code,
					"qty": r.qty,
					"rate": r.rate,
					"docname": r.name,
				})
			continue

		remaining = picked
		for r in rows:
			if remaining <= 0:
				break
			allocate = min(r.qty, remaining)
			trans_items.append({
				"item_code": r.item_code,
				"qty": allocate,
				"rate": r.rate,
				"docname": r.name,
			})
			remaining -= allocate
		changes.append(_("Reduced: {0} qty {1} → {2}").format(item_code, _fmt_qty(total_orig), _fmt_qty(picked)))

	if not changes:
		return []

	prev_ignore = frappe.flags.ignore_permissions
	frappe.flags.ignore_permissions = True
	try:
		update_child_qty_rate("Sales Order", _json.dumps(trans_items), so_name)
	finally:
		frappe.flags.ignore_permissions = prev_ignore

	return changes


@frappe.whitelist()
def create_b2b_stock_entry(mr_name, cost_center, purpose_of_transfer="", is_partial=0, original_items=None, picking_log=None):
	"""
	Create and submit a Stock Entry (Material Transfer) from a submitted Material Request.
	Sets custom_cost_center on header and cost_center on each detail row.
	Sets custom_perpose_of_transfer on header.
	Marks the linked Sales Order as picked.
	If is_partial=1, status is set to "Consignment Partially Delivered".
	"""
	if not frappe.db.exists("Material Request", mr_name):
		frappe.throw(_("Material Request {0} not found").format(mr_name))

	mr_doc = frappe.get_doc("Material Request", mr_name)
	if mr_doc.docstatus != 1:
		frappe.throw(_("Material Request {0} must be submitted first").format(mr_name))

	# Determine the linked Sales Order and customer
	so_name = None
	customer_name = ""
	for item in mr_doc.items:
		if item.sales_order:
			so_name = item.sales_order
			customer_name = frappe.db.get_value("Sales Order", so_name, "customer_name") or ""
			break

	se = frappe.new_doc("Stock Entry")
	se.stock_entry_type = "Material Transfer"
	se.custom_cost_center = cost_center
	se.custom_perpose_of_transfer = purpose_of_transfer or f"Transfer by B2B Order Pick for {customer_name}".strip()

	for item in mr_doc.items:
		se.append("items", {
			"item_code": item.item_code,
			"qty": item.qty,
			"uom": item.uom,
			"s_warehouse": item.from_warehouse,
			"t_warehouse": item.warehouse,
			"cost_center": cost_center,
			"material_request": mr_doc.name,
			"material_request_item": item.name,
		})

	se.insert(ignore_permissions=True)
	se.flags.ignore_permissions = True
	se.submit()

	# Determine status based on partial flag
	is_partial = int(is_partial or 0)
	b2b_status = "Consignment Partially Delivered" if is_partial else "Consignment Delivered"

	# Mark the Sales Order as B2B picked + set custom status
	if so_name:
		try:
			frappe.db.set_value(
				"Sales Order", so_name,
				{
					"custom_b2b_picked": 1,
					"custom_b2b_status": b2b_status
				},
				update_modified=False
			)
		except Exception as e:
			frappe.log_error(
				f"Could not set custom_b2b fields on {so_name}: {str(e)}",
				"B2B Order Pick - Mark SO"
			)

		# On partial picks: align Sales Order items with what was actually picked
		# (drop unpicked items, reduce qty for partially picked items).
		so_change_msg = ""
		if is_partial:
			try:
				changes = _sync_so_to_picked(so_name, mr_doc)
				if changes:
					so_change_msg = "<br>" + _("Items adjusted to match pick:") + "<br>" + "<br>".join(changes)
			except Exception as e:
				frappe.log_error(
					frappe.get_traceback(),
					f"B2B Order Pick - Sync SO Items {so_name}"
				)
				so_change_msg = "<br>" + _("(Item sync failed: {0})").format(str(e))

		so_doc = frappe.get_doc("Sales Order", so_name)
		so_doc.add_comment(
			"Info",
			_(
				"Order picked and processed via B2B Order Pick App. "
				"Status: {2}. "
				"Material Request: {0}, Stock Entry: {1}"
			).format(mr_doc.name, se.name, b2b_status) + so_change_msg
		)

	frappe.db.commit()

	# Build items summary for return and pick report
	import json as _json
	order_qty_map = {}
	if original_items:
		try:
			for oi in _json.loads(original_items):
				code = oi.get("item_code")
				if code:
					order_qty_map[code] = order_qty_map.get(code, 0) + (oi.get("qty") or 0)
		except Exception:
			pass

	items_summary = []
	for item in mr_doc.items:
		item_name = frappe.db.get_value("Item", item.item_code, "item_name") or item.item_code
		items_summary.append({
			"item_code": item.item_code,
			"item_name": item_name,
			"qty": item.qty,
			"uom": item.uom,
			"from_warehouse": item.from_warehouse,
			"to_warehouse": item.warehouse,
		})

	# Save a B2B Pick Report document for later reference
	try:
		report = frappe.new_doc("B2B Pick Report")
		report.sales_order = so_name or ""
		report.customer_name = customer_name
		report.material_request = mr_doc.name
		report.stock_entry = se.name
		report.picked_by = frappe.session.user
		report.pick_date = frappe.utils.now()
		report.is_partial = int(is_partial or 0)
		for item in mr_doc.items:
			item_name = frappe.db.get_value("Item", item.item_code, "item_name") or item.item_code
			report.append("items", {
				"item_code": item.item_code,
				"item_name": item_name,
				"order_qty": order_qty_map.get(item.item_code, 0),
				"picked_qty": item.qty,
				"uom": item.uom,
				"source_warehouse": item.from_warehouse,
				"target_warehouse": item.warehouse,
			})
		# Save scan log entries
		if picking_log:
			try:
				log_entries = _json.loads(picking_log) if isinstance(picking_log, str) else picking_log
				for entry in log_entries:
					report.append("log", {
						"time": entry.get("time", ""),
						"item_code": entry.get("item_code", ""),
						"barcode": entry.get("barcode", ""),
						"qty": entry.get("qty", 0),
						"multiplier": str(entry.get("multiplier", "")),
						"uom_factor": entry.get("uom_factor", ""),
					})
			except Exception:
				pass
		report.insert(ignore_permissions=True)
		frappe.db.commit()
	except Exception as e:
		frappe.log_error(f"Could not save B2B Pick Report for {so_name}: {str(e)}", "B2B Pick Report Save")

	return {
		"se_name": se.name,
		"mr_name": mr_doc.name,
		"so_name": so_name or "",
		"customer_name": customer_name,
		"items": items_summary,
	}
