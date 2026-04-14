frappe.ui.form.on('B2B Pick Report', {
	refresh(frm) {
		frm.add_custom_button(__('Print Summary'), () => {
			frm.call_button_print_summary();
		}, __('Print'));

		frm.add_custom_button(__('Customer Order'), () => {
			frm.call_button_customer_order();
		}, __('Print'));

		frm.page.set_secondary_action(__('Print Summary'), () => {
			frm.call_button_print_summary();
		});
	},

	onload(frm) {
		// ── Print Summary ────────────────────────────────────────────────
		frm.call_button_print_summary = async function () {
			const doc = frm.doc;

			// Build item_code → scanned barcode from scan log (only barcodes actually scanned)
			const scannedBarcodeMap = {};
			(doc.log || []).forEach(log => {
				if (log.item_code && log.barcode && log.barcode !== '(F9 override)') {
					scannedBarcodeMap[log.item_code] = log.barcode;
				}
			});

			const td = (content, style) =>
				`<td style="padding:6px 10px;border:1px solid #ddd;font-size:12px;${style||''}">${content}</td>`;

			const rows = (doc.items || []).map((item, idx) => {
				const over = item.picked_qty > item.order_qty && item.order_qty > 0;
				const scannedBC = scannedBarcodeMap[item.item_code] || '';
				const skuCell = item.item_code + (scannedBC
					? `<br><span style="font-weight:normal;font-size:10px;color:#888;font-family:monospace">${scannedBC}</span>`
					: '');
				return `<tr>
					${td(idx + 1, 'color:#999')}
					${td(`<strong>${skuCell}</strong>`)}
					${td(item.item_name || '')}
					${td(item.order_qty, 'text-align:right')}
					${td(item.picked_qty + (over ? ' &#9888;' : ''), `text-align:right;font-weight:bold;color:${over ? '#dc2626' : '#16a34a'}`)}
					${td(item.uom || 'Nos')}
					${td(item.source_warehouse || '', 'font-size:11px;color:#888')}
					${td(item.target_warehouse || '', 'font-size:11px;color:#888')}
				</tr>`;
			}).join('');

			const logRows = (doc.log || []).map((log, idx) =>
				`<tr>
					<td style="padding:4px 8px;border:1px solid #eee;font-size:11px;color:#999">${idx + 1}</td>
					<td style="padding:4px 8px;border:1px solid #eee;font-size:11px">${log.time || ''}</td>
					<td style="padding:4px 8px;border:1px solid #eee;font-size:11px;font-weight:bold">${log.item_code || ''}</td>
					<td style="padding:4px 8px;border:1px solid #eee;font-size:11px;font-family:monospace">${log.barcode || ''}</td>
					<td style="padding:4px 8px;border:1px solid #eee;font-size:11px;text-align:right;font-weight:bold">${log.qty || 0}</td>
					<td style="padding:4px 8px;border:1px solid #eee;font-size:11px">&times;${log.multiplier || ''} (${log.uom_factor || ''})</td>
				</tr>`
			).join('');

			const badge = (text, bg, color) =>
				`<span style="display:inline-block;padding:3px 10px;border-radius:6px;font-size:11px;font-weight:bold;margin-right:6px;background:${bg};color:${color}">${text}</span>`;

			const html = `<html><head><title>B2B Pick Summary — ${doc.sales_order || doc.name}</title>
<style>
  body{font-family:system-ui,sans-serif;padding:30px;color:#333}
  h1{margin:0 0 6px;font-size:20px}
  h3{margin:24px 0 8px;font-size:13px;text-transform:uppercase;color:#555}
  table{border-collapse:collapse;width:100%}
  th{background:#f3f4f6;text-align:left;padding:8px 10px;border:1px solid #ddd;font-size:11px;text-transform:uppercase}
  .meta{color:#666;font-size:12px;margin:0 0 4px}
  .sub{color:#999;font-size:11px;margin:0 0 20px}
  hr{border:none;border-top:1px dashed #ddd;margin:20px 0}
</style>
</head><body>
<h1>B2B Order Pick &mdash; Completion Summary</h1>
<p class="meta"><strong>Sales Order:</strong> ${doc.sales_order || '&mdash;'} &nbsp; <strong>Customer:</strong> ${doc.customer_name || '&mdash;'}</p>
<p class="meta">
  ${badge('MR: ' + (doc.material_request || '&mdash;'), '#fef3c7', '#92400e')}
  ${badge('SE: ' + (doc.stock_entry || '&mdash;'), '#d1fae5', '#065f46')}
  ${doc.is_partial ? badge('Partial Pick', '#fde8d8', '#9a3412') : badge('Fully Picked', '#d1fae5', '#065f46')}
</p>
<p class="meta"><strong>Picked By:</strong> ${doc.picked_by || '&mdash;'} &nbsp; <strong>Pick Date:</strong> ${doc.pick_date || '&mdash;'}</p>
<p class="sub">Printed: ${new Date().toLocaleString()}</p>
<hr>
<h3>Transfer Items</h3>
<table>
  <thead><tr>
    <th>#</th><th>Item Code / Barcode</th><th>Item Name</th>
    <th style="text-align:right">Order Qty</th><th style="text-align:right">Picked Qty</th>
    <th>UOM</th><th>Source WH</th><th>Dest WH</th>
  </tr></thead>
  <tbody>${rows}</tbody>
</table>
${logRows ? `<h3>Scan Log (${(doc.log || []).length} scans)</h3>
<table>
  <thead><tr><th>#</th><th>Time</th><th>Item</th><th>Barcode</th><th style="text-align:right">Qty</th><th>Details</th></tr></thead>
  <tbody>${logRows}</tbody>
</table>` : ''}
</body></html>`;

			const w = window.open('', '_blank');
			w.document.write(html);
			w.document.close();
			w.focus();
			w.print();
		};

		// ── Customer Order ───────────────────────────────────────────────
		frm.call_button_customer_order = async function () {
			const doc = frm.doc;
			if (!doc.sales_order) {
				frappe.msgprint(__('No Sales Order linked to this report.'));
				return;
			}

			frappe.show_progress(__('Loading...'), 0, 100);

			const res = await frappe.call({
				method: 'order_picking.api.api.get_sales_order_print_data',
				args: { so_name: doc.sales_order }
			});

			frappe.hide_progress();

			const so = res.message;
			if (!so) { frappe.msgprint(__('Failed to load Sales Order data.')); return; }

			// Build item-code → picked qty map from BPR items
			const pickedMap = {};
			(doc.items || []).forEach(i => {
				pickedMap[i.item_code] = (pickedMap[i.item_code] || 0) + (i.picked_qty || 0);
			});

			// Build item-code → scanned barcode map from scan log (only barcodes actually scanned)
			const scannedBarcodeMap = {};
			(doc.log || []).forEach(log => {
				if (log.item_code && log.barcode && log.barcode !== '(F9 override)') {
					scannedBarcodeMap[log.item_code] = log.barcode;
				}
			});

			const fmt = (n) => parseFloat(n || 0).toLocaleString('en-KW', { minimumFractionDigits: 3, maximumFractionDigits: 3 });
			const cur = so.currency || 'KWD';

			let totalOrderQty = 0, totalPickedQty = 0, grandTotal = 0;

			const bcSvg = (value) =>
				`<svg data-bc="${value}" style="display:block;width:130px;height:36px;margin-top:2px"></svg>`;

			const rows = so.items.map((item, idx) => {
				const scannedBC = scannedBarcodeMap[item.item_code] || '';
				const picked = pickedMap[item.item_code] || 0;
				const amount = (item.rate || 0) * picked;
				totalOrderQty += item.qty || 0;
				totalPickedQty += picked;
				grandTotal += amount;

				const skuCell = `<strong style="font-size:12px">${item.item_code}</strong>`
					+ (scannedBC
						? `<br><span style="font-family:monospace;font-size:10px;color:#888">${scannedBC}</span>`
						  + bcSvg(scannedBC)
						: '');

				return `<tr>
					<td style="${S.td}">${idx + 1}</td>
					<td style="${S.td}">${skuCell}</td>
					<td style="${S.td}">${item.item_name || ''}</td>
					<td style="${S.td}${S.num}">${item.qty}</td>
					<td style="${S.td}${S.num}${picked < item.qty ? 'color:#dc2626;' : 'color:#16a34a;'}font-weight:bold">${picked}</td>
					<td style="${S.td}${S.num}">${cur} ${fmt(item.rate)}</td>
					<td style="${S.td}${S.num}font-weight:bold">${cur} ${fmt(amount)}</td>
				</tr>`;
			}).join('');

			// Discount row
			const discountRow = so.discount_amount > 0
				? `<tr><td colspan="6" style="${S.td}text-align:right;color:#dc2626">Discount</td><td style="${S.td}${S.num}color:#dc2626;font-weight:bold">- ${cur} ${fmt(so.discount_amount)}</td></tr>`
				: '';

			// Tax row
			const taxRow = so.total_taxes_and_charges > 0
				? `<tr><td colspan="6" style="${S.td}text-align:right;color:#555">${so.taxes_and_charges || 'Tax'}</td><td style="${S.td}${S.num}">${cur} ${fmt(so.total_taxes_and_charges)}</td></tr>`
				: '';

			const html = `<html><head><title>Customer Order — ${so.so_name}</title>
<style>
  @page { margin: 15mm 18mm; }
  body { font-family: system-ui, Arial, sans-serif; color: #222; font-size: 13px; }
  h2 { margin: 0 0 2px; font-size: 22px; color: #1a1a2e; letter-spacing: 0.5px; }
  .header-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px 24px; margin-bottom: 18px; }
  .lbl { font-size: 10px; font-weight: bold; text-transform: uppercase; color: #888; margin-bottom: 1px; }
  .val { font-size: 13px; color: #222; }
  .divider { border: none; border-top: 2px solid #1a1a2e; margin: 14px 0 18px; }
  table { border-collapse: collapse; width: 100%; }
  th { background: #1a1a2e; color: #fff; text-align: left; padding: 8px 10px; font-size: 11px; text-transform: uppercase; }
  th.r { text-align: right; }
  .total-row td { font-weight: bold; font-size: 13px; border-top: 2px solid #1a1a2e; }
  .footer { text-align: center; margin-top: 40px; padding-top: 14px; border-top: 1px solid #ddd; font-size: 11px; color: #666; line-height: 1.7; }
  .footer strong { font-size: 13px; color: #1a1a2e; display: block; margin-bottom: 2px; }
</style>
</head><body>

<h2>Kuwait Projects Group</h2>
<p style="margin:0 0 14px;color:#555;font-size:12px">Kuwait Cairo Street, Cairo Tower, 9th Floor</p>
<hr class="divider">

<div class="header-grid">
  <div>
    <div class="lbl">Customer</div>
    <div class="val"><strong>${so.customer}</strong></div>
  </div>
  <div>
    <div class="lbl">Sales Order</div>
    <div class="val">${so.so_name}</div>
    <svg data-bc="${so.so_name}" style="display:block;width:130px;height:36px;margin-top:2px"></svg>
  </div>
  <div>
    <div class="lbl">Address</div>
    <div class="val">${so.address || '&mdash;'}</div>
  </div>
  <div>
    <div class="lbl">Date</div>
    <div class="val">${so.date || '&mdash;'}</div>
  </div>
  ${so.po_number ? `<div>
    <div class="lbl">Customer's Purchase Order</div>
    <div class="val">${so.po_number}</div>
  </div>` : ''}
  ${so.contact ? `<div>
    <div class="lbl">Contact</div>
    <div class="val">${so.contact}</div>
  </div>` : ''}
</div>

<table>
  <thead>
    <tr>
      <th>#</th>
      <th>Item Code / Barcode</th>
      <th>Item Name</th>
      <th class="r">Qty Ordered</th>
      <th class="r">Order Sent</th>
      <th class="r">Rate (${cur})</th>
      <th class="r">Amount (${cur})</th>
    </tr>
  </thead>
  <tbody>
    ${rows}
    <tr style="background:#f9f9f9">
      <td colspan="3" style="${S.td}font-weight:bold;text-align:right;color:#555">TOTALS</td>
      <td style="${S.td}${S.num}font-weight:bold">${totalOrderQty}</td>
      <td style="${S.td}${S.num}font-weight:bold">${totalPickedQty}</td>
      <td style="${S.td}"></td>
      <td style="${S.td}${S.num}font-weight:bold">${cur} ${fmt(grandTotal)}</td>
    </tr>
    ${discountRow}
    ${taxRow}
    <tr class="total-row">
      <td colspan="6" style="${S.td}text-align:right">Grand Total</td>
      <td style="${S.td}${S.num}font-size:15px">${cur} ${fmt(grandTotal)}</td>
    </tr>
  </tbody>
</table>

<div class="footer">
  <strong>Kuwait Projects Group</strong>
  Kuwait Cairo Street, Cairo Tower, 9th Floor<br>
  Contact: +965 97419902 &nbsp;|&nbsp; Email: info@kuwaitgroupco.com
</div>
</body></html>`;

			const w = window.open('', '_blank');
			w.document.write(html);
			w.document.close();

			// Load JsBarcode then render all [data-bc] SVGs before printing
			const script = w.document.createElement('script');
			script.src = 'https://cdn.jsdelivr.net/npm/jsbarcode@3.11.6/dist/JsBarcode.all.min.js';
			script.onload = () => {
				w.document.querySelectorAll('svg[data-bc]').forEach(el => {
					try {
						w.JsBarcode(el, el.getAttribute('data-bc'), {
							format: 'CODE128',
							width: 1.2,
							height: 28,
							displayValue: false,
							margin: 0,
						});
					} catch(e) {}
				});
				w.focus();
				w.print();
			};
			script.onerror = () => { w.focus(); w.print(); };
			w.document.head.appendChild(script);
		};
	}
});

// Shared styles object (defined outside handler to keep rows DRY)
const S = {
	td: 'padding:7px 10px;border:1px solid #ddd;font-size:12px;',
	num: 'text-align:right;',
};
