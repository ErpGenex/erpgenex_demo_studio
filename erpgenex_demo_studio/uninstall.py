import frappe
from frappe import _

def before_uninstall():
	"""Before uninstallation hook - cleanup demo data"""
	cleanup_demo_environments()

def after_uninstall():
	"""After uninstallation hook"""
	pass

def cleanup_demo_environments():
	"""Clean up all demo environments created by this app"""
	if frappe.db.table_exists("Demo Environment"):
		demo_environments = frappe.get_all("Demo Environment", filters={"is_demo": 1})
		for env in demo_environments:
			try:
				doc = frappe.get_doc("Demo Environment", env.name)
				doc.delete()
			except Exception:
				pass
		frappe.db.commit()
