import frappe


def execute():
	from erpgenex_demo_studio.demo_studio.setup.demo_templates import ensure_annual_demo_templates

	ensure_annual_demo_templates()
	frappe.db.commit()
