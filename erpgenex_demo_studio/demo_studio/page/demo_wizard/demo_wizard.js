frappe.pages["demo_wizard"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Demo Deployment Wizard"),
		single_column: true,
	});

	frappe.breadcrumbs.add("Demo Studio");

	page.main.html(
		`<div class="text-muted" style="padding: 24px;">${__("Loading wizard...")}</div>`
	);

	frappe.call({
		method:
			"erpgenex_demo_studio.demo_studio.page.demo_wizard.demo_wizard.get_rendered_page_html",
		freeze: true,
		callback(r) {
			if (r.exc) {
				page.main.html(
					`<div class="alert alert-danger" style="margin: 16px;">${__(
						"Could not load the demo wizard. Please refresh or contact support."
					)}</div>`
				);
				return;
			}

			page.main.html(r.message || "");
			frappe.require("/assets/erpgenex_demo_studio/js/demo_wizard.js");
		},
	});
};
