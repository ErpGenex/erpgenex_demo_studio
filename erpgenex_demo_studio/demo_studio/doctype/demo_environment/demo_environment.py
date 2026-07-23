import frappe
from frappe.model.document import Document
from frappe import _
import uuid
import json

class DemoEnvironment(Document):
	def before_save(self):
		self.generate_demo_id()
		self.set_metadata()
		self.set_language()
	
	def generate_demo_id(self):
		"""Generate unique demo ID"""
		if not self.demo_id:
			self.demo_id = f"DEMO-{uuid.uuid4().hex[:8].upper()}"
	
	def set_metadata(self):
		"""Set metadata fields"""
		if not self.created_by:
			self.created_by = frappe.session.user
		if not self.created_time:
			self.created_time = frappe.utils.now()
		self.last_updated = frappe.utils.now()

	def set_language(self):
		"""Persist the UI language used to create this demo."""
		if getattr(self, 'language', None):
			return
		user_lang = frappe.db.get_value("User", frappe.session.user, "language")
		self.language = getattr(frappe.local, "lang", None) or user_lang or frappe.get_system_settings("language") or "en"
	
	def validate(self):
		"""Validate demo environment"""
		self.validate_unique_demo_name()
		self.validate_template()
	
	def validate_unique_demo_name(self):
		"""Ensure demo name is unique"""
		if self.demo_name:
			existing = frappe.db.exists("Demo Environment", {"demo_name": self.demo_name, "name": ["!=", self.name]})
			if existing:
				frappe.throw(_("Demo name already exists"))
	
	def validate_template(self):
		"""Validate template if specified"""
		if self.template:
			template = frappe.get_doc("Demo Template", self.template)
			if template.status != "Active":
				frappe.throw(_("Template must be active"))
			self.template_version = template.version
	
	def on_trash(self):
		"""Handle deletion - cleanup demo data"""
		if self.is_demo:
			self.cleanup_demo_data()
	
	def cleanup_demo_data(self):
		"""Clean up all demo data associated with this environment"""
		# This will be implemented with the generation engine
		pass

@frappe.whitelist()
def generate_demo(demo_name, template, industry, company_name, language=None):
	"""Generate a new demo environment"""
	demo = frappe.new_doc("Demo Environment")
	demo.demo_name = demo_name
	demo.template = template
	demo.industry = industry
	demo.company_name = company_name
	if language:
		demo.language = language
	demo.status = "Generating"
	demo.save()
	
	# Trigger background job for generation
	frappe.enqueue("erpgenex_demo_studio.generators.demo_generator.generate_demo_environment",
		demo_name=demo.name, queue="long")
	
	return demo.name

@frappe.whitelist()
def reset_demo(demo_name):
	"""Reset a demo environment to initial state"""
	demo = frappe.get_doc("Demo Environment", demo_name)
	if not demo.is_demo:
		frappe.throw(_("Can only reset demo environments"))
	
	demo.status = "Generating"
	demo.save()
	
	frappe.enqueue("erpgenex_demo_studio.generators.demo_generator.reset_demo_environment",
		demo_name=demo.name, queue="long")
	
	return demo.name

@frappe.whitelist()
def delete_demo(demo_name):
	"""Delete a demo environment and all its data"""
	demo = frappe.get_doc("Demo Environment", demo_name)
	if not demo.is_demo:
		frappe.throw(_("Can only delete demo environments"))
	
	demo.delete()
	return True
	return True
