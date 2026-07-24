import frappe
from frappe import _

def execute():
	"""Register demo_wizard page in the database"""
	
	if frappe.db.exists('Page', 'demo_wizard'):
		print("Page 'demo_wizard' already exists, updating...")
		page = frappe.get_doc('Page', 'demo_wizard')
	else:
		print("Creating new page 'demo_wizard'...")
		page = frappe.new_doc('Page')
	
	page.page_name = 'demo_wizard'
	page.title = 'Demo Deployment Wizard'
	page.module = 'Demo Studio'
	page.app = 'erpgenex_demo_studio'
	page.standard = 'Yes'
	page.route = 'demo_wizard'
	page.is_hidden = 0
	
	page.save()
	
	print("✓ Page 'demo_wizard' registered successfully")
