app_name = "order_picking"
app_title = "Order Picking"
app_publisher = "Your Company"
app_description = "Order Picking App for ERPNext to ensure 100% accurate deliveries"
app_email = "hello@example.com"
app_license = "mit"

required_apps = ["erpnext"]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/order_picking/css/order_picking.css"
# app_include_js = "/assets/order_picking/js/order_picking.js"

# include js, css files in header of web template
# web_include_css = "/assets/order_picking/css/order_picking.css"
# web_include_js = "/assets/order_picking/js/order_picking.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "order_picking/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Sales Order": "public/js/sales_order.js",
	"B2B Pick Report": "public/js/b2b_pick_report.js"
}
doctype_list_js = {"Sales Invoice": "public/js/sales_invoice_list.js"}

# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

website_route_rules = [
	{"from_route": "/order-picking/<path:app_path>", "to_route": "order_picking"},
	{"from_route": "/order-picking", "to_route": "order_picking"}
]

after_migrate = "order_picking.setup.after_migrate"

fixtures = [
	{"dt": "Workspace", "filters": [["name", "=", "Order Picking"]]},
	{"dt": "Print Format", "filters": [["name", "in", [
		"B2B Pick Report Summary",
		"Customer Invoice",
		"Sales Invoice Pick List",
	]]]}
]
