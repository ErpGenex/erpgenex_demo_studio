(function () {
	const pageIds = ["demo_wizard", "demo-wizard"];

	function mountRenderedHtml(wrapper, html) {
		const parsed = new DOMParser().parseFromString(html || "", "text/html");
		parsed.querySelectorAll("style").forEach((style) => {
			if (style.id && document.getElementById(style.id)) return;
			document.head.appendChild(style.cloneNode(true));
		});

		const container = wrapper.querySelector(".demo-wizard-host") || wrapper;
		container.innerHTML = parsed.body ? parsed.body.innerHTML : html;

		parsed.querySelectorAll("script").forEach((script) => {
			if (!script.textContent || !script.textContent.trim()) return;
			const tag = document.createElement("script");
			tag.textContent = script.textContent;
			document.body.appendChild(tag);
			tag.remove();
		});
	}

	function renderFallback(wrapper, error) {
		const page = frappe.ui.make_app_page({
			parent: wrapper,
			title: __("Demo Deployment Wizard"),
			single_column: true,
		});
		$(page.main).html(`
			<div class="alert alert-warning" style="margin: 24px;">
				<strong>${__("Demo Wizard")}</strong><br>
				${__("Unable to load the wizard UI right now.")}<br>
				<small>${frappe.utils.escape_html(String(error || ""))}</small>
			</div>
		`);
	}

	function boot(wrapper) {
		const page = frappe.ui.make_app_page({
			parent: wrapper,
			title: __("Demo Deployment Wizard"),
			single_column: true,
		});
		$(page.main).html('<div class="demo-wizard-host"><div class="text-muted" style="padding: 24px;">' + __("Loading demo wizard...") + '</div></div>');

		frappe.call({
			method: "erpgenex_demo_studio.demo_studio.page.demo_wizard.demo_wizard.get_rendered_page_html",
			callback: function (r) {
				try {
					const html = r && r.message ? r.message : "";
					mountRenderedHtml(page.main, html);
				} catch (err) {
					renderFallback(wrapper, err);
				}
			},
			error: function (err) {
				renderFallback(wrapper, err);
			}
		});
	}

	pageIds.forEach((pageId) => {
		frappe.pages[pageId] = {
			on_page_load: boot,
		};
	});
})();
