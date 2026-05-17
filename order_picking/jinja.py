"""
Jinja helpers exposed to Print Formats and other templates via the
`jenv.methods` hook in hooks.py.

Registered names:
    render_barcode          -> render_barcode(value, ...)
    brand_for_cost_center   -> brand_for_cost_center(cost_center)
"""

from __future__ import annotations

import html
from io import BytesIO

import frappe


# ─────────────────────────────────────────────────────────────────────────────
# Brand resolution
# ─────────────────────────────────────────────────────────────────────────────

def brand_for_cost_center(cost_center: str | None) -> dict:
	"""
	Resolve the ERPNext Brand for a given cost center.

	Tries several strategies in order so it works regardless of how cost
	centers are named:

	  1. Strip company-abbreviation suffix and look up by exact name:
	     "Ahuhu - KPG" -> Brand "Ahuhu"
	  2. If that misses, try the first word of the stripped name:
	     "Ahuhu Body Care - KPG" -> Brand "Ahuhu"
	  3. If that misses, try the raw cost-center string itself.

	When the Brand row is found, the `image` URL is normalised to an
	absolute URL so PDF renderers (wkhtmltopdf / Chrome PDF) can fetch
	the file. The dict also returns `tried` (list of names attempted)
	to make debugging from the rendered HTML straightforward.

	Returns: {name, image, found, tried}
	  - `name` always has a value (falls back to the cleaned cost center)
	  - `image` is None if the Brand doesn't exist or has no image
	"""
	cleaned = (cost_center or "").rsplit(" - ", 1)[0].strip()
	tried: list[str] = []

	def _lookup(candidate: str):
		if not candidate or candidate in tried:
			return None
		tried.append(candidate)
		return frappe.db.get_value(
			"Brand", candidate, ["name", "image"], as_dict=True
		)

	row = _lookup(cleaned)
	if not row and " " in cleaned:
		row = _lookup(cleaned.split(" ", 1)[0])
	if not row and cost_center:
		row = _lookup(cost_center)

	if row:
		image = row.image or None
		if image and not image.startswith(("http://", "https://", "data:")):
			# Make absolute so wkhtmltopdf / Chrome PDF can fetch it.
			try:
				image = frappe.utils.get_url(image)
			except Exception:
				pass
		return {
			"name": row.name,
			"image": image,
			"found": True,
			"tried": tried,
		}

	return {
		"name": cleaned or (cost_center or ""),
		"image": None,
		"found": False,
		"tried": tried,
	}


# ─────────────────────────────────────────────────────────────────────────────
# Barcode rendering
# ─────────────────────────────────────────────────────────────────────────────

def render_barcode(
	value: str | None,
	barcode_type: str = "code128",
	height: float = 10.0,
	module_width: float = 0.32,
	quiet_zone: float = 1.5,
) -> str:
	"""
	Render `value` as an inline Code-128 SVG using python-barcode.
	Falls back to a styled monospace span if python-barcode isn't installed
	or the value can't be encoded.

	Returns a string of HTML that the print format should output with
	`| safe` (HTML is trusted — generated server-side from own data).
	"""
	if not value:
		return ""

	value_str = str(value)

	try:
		import barcode  # python-barcode
		from barcode.writer import SVGWriter

		writer = SVGWriter()
		code = barcode.get(barcode_type, value_str, writer=writer)
		buf = BytesIO()
		code.write(
			buf,
			options={
				"module_height": float(height),
				"module_width": float(module_width),
				"quiet_zone": float(quiet_zone),
				"font_size": 0,           # we render the text ourselves
				"text_distance": 0,
				"write_text": False,
				"background": "white",
				"foreground": "black",
			},
		)
		svg = buf.getvalue().decode("utf-8", errors="ignore")
		# Strip the XML preamble and DOCTYPE so the SVG inlines cleanly
		# inside another HTML document.
		if "<svg" in svg:
			svg = svg[svg.index("<svg"):]
		return (
			'<span class="bc-wrap">'
			f'{svg}'
			f'<span class="bc-text">{html.escape(value_str)}</span>'
			'</span>'
		)
	except Exception:
		# Graceful fallback — still useful, still readable.
		return (
			f'<span class="bc-fallback">{html.escape(value_str)}</span>'
		)
