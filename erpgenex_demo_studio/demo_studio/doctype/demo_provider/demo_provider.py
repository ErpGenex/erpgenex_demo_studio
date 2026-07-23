import frappe
from frappe.model.document import Document
from frappe import _
import json

class DemoProvider(Document):
	def validate(self):
		self.validate_unique_provider_name()
		self.validate_implementation()
		self.validate_json_fields()
	
	def validate_unique_provider_name(self):
		"""Ensure provider name is unique"""
		if self.provider_name:
			existing = frappe.db.exists("Demo Provider", {"provider_name": self.provider_name, "name": ["!=", self.name]})
			if existing:
				frappe.throw(_("Provider name already exists"))
	
	def validate_implementation(self):
		"""Validate implementation details"""
		if self.provider_type in ["Industry Provider", "Data Provider"]:
			if not (self.app_name and self.module_name and self.class_name and self.method_name):
				frappe.throw(_("Implementation details required for this provider type"))
	
	def validate_json_fields(self):
		"""Validate JSON configuration fields"""
		json_fields = ["capabilities", "requirements", "dependencies", "configuration"]
		
		for field in json_fields:
			value = self.get(field)
			if value:
				try:
					json.loads(value)
				except json.JSONDecodeError:
					frappe.throw(_(f"{field} must be valid JSON"))
	
	def register_provider(self):
		"""Register provider with the demo studio"""
		# This will be used to discover and register providers from other apps
		pass

@frappe.whitelist()
def discover_providers():
	"""Discover all registered providers from installed apps"""
	providers = frappe.get_all("Demo Provider", filters={"is_active": 1, "status": "Active"})
	return providers

@frappe.whitelist()
def get_provider_capabilities(provider_name):
	"""Get capabilities of a specific provider"""
	provider = frappe.get_doc("Demo Provider", provider_name)
	if provider.capabilities:
		return json.loads(provider.capabilities)
	return {}
