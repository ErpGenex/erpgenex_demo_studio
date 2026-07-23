import frappe
from frappe import _

class DemoSafety:
	"""Safety utilities for demo operations"""
	
	@staticmethod
	def is_demo_record(doctype, docname):
		"""Check if a record is a demo record"""
		try:
			doc = frappe.get_doc(doctype, docname)
			if hasattr(doc, 'is_demo') and doc.is_demo:
				return True
			if hasattr(doc, 'demo_id'):
				return True
			if hasattr(doc, 'generation_id'):
				return True
		except Exception:
			pass
		return False
	
	@staticmethod
	def mark_as_demo(doc):
		"""Mark a document as demo record"""
		if hasattr(doc, 'is_demo'):
			doc.is_demo = 1
		if hasattr(doc, 'demo_id'):
			if not getattr(doc, 'demo_id', None):
				import uuid
				doc.demo_id = f"DEMO-{uuid.uuid4().hex[:8].upper()}"
		if hasattr(doc, 'generation_id'):
			if not getattr(doc, 'generation_id', None):
				import uuid
				doc.generation_id = f"GEN-{uuid.uuid4().hex[:12].upper()}"
		if hasattr(doc, 'generator_version'):
			doc.generator_version = "1.0.0"
	
	@staticmethod
	def safe_delete(doctype, docname):
		"""Safely delete a record - only if it's a demo record"""
		if DemoSafety.is_demo_record(doctype, docname):
			frappe.delete_doc(doctype, docname)
			return True
		else:
			frappe.throw(_("Cannot delete non-demo record"))
	
	@staticmethod
	def get_demo_records(doctype):
		"""Get all demo records of a doctype"""
		if frappe.db.has_column(doctype, 'is_demo'):
			return frappe.get_all(doctype, filters={'is_demo': 1})
		elif frappe.db.has_column(doctype, 'demo_id'):
			return frappe.get_all(doctype, filters={'demo_id': ('is not set', '')})
		return []
	
	@staticmethod
	def cleanup_demo_data(demo_id):
		"""Clean up all demo data associated with a demo ID"""
		# This would scan all doctypes and delete records matching the demo_id
		# Implementation would be added based on requirements
		pass

@frappe.whitelist()
def check_demo_safety(doctype, docname):
	"""Check if it's safe to perform an operation on a record"""
	return {
		"is_demo": DemoSafety.is_demo_record(doctype, docname),
		"safe_to_delete": DemoSafety.is_demo_record(doctype, docname)
	}
