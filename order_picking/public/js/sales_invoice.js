// Sales Invoice form customisations.
//
// Adds two quick-print actions under the form's Print menu that open the
// printview directly with the correct Jinja format and auto-fire the
// browser print dialog — no need to open the Print page and pick a format.

frappe.ui.form.on('Sales Invoice', {
	refresh(frm) {
		if (frm.is_new()) return;

		const print_with_format = (format_name) => {
			// no_letterhead=1 because both formats render their own branded
			// header (brand logo + meta) and we don't want duplication.
			// trigger_print=1 fires window.print() once the page loads.
			const params = new URLSearchParams({
				doctype: frm.doctype,
				name: frm.docname,
				format: format_name,
				trigger_print: '1',
				no_letterhead: '1',
			});
			window.open('/printview?' + params.toString(), '_blank');
		};

		frm.add_custom_button(
			__('Customer Invoice'),
			() => print_with_format('Customer Invoice'),
			__('Print')
		);

		frm.add_custom_button(
			__('Pick List'),
			() => print_with_format('Sales Invoice Pick List'),
			__('Print')
		);
	},
});
