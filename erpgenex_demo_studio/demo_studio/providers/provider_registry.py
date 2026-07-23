import frappe
from frappe import _
import importlib

class ProviderRegistry:
	"""Registry for demo data providers"""
	
	_providers = {}
	
	@classmethod
	def register_provider(cls, provider_name, provider_class):
		"""Register a demo provider"""
		cls._providers[provider_name] = provider_class
	
	@classmethod
	def get_provider(cls, provider_name):
		"""Get a registered provider"""
		return cls._providers.get(provider_name)
	
	@classmethod
	def discover_providers(cls):
		"""Discover providers from installed apps"""
		providers = frappe.get_all("Demo Provider", filters={"is_active": 1, "status": "Active"})
		
		for provider_doc in providers:
			provider = frappe.get_doc("Demo Provider", provider_doc.name)
			cls.load_provider(provider)
	
	@classmethod
	def load_provider(cls, provider_doc):
		"""Load a provider from its configuration"""
		try:
			if provider_doc.app_name and provider_doc.module_name and provider_doc.class_name:
				# Dynamic import of provider class
				module = importlib.import_module(f"{provider_doc.app_name}.{provider_doc.module_name}")
				provider_class = getattr(module, provider_doc.class_name)
				cls.register_provider(provider_doc.provider_name, provider_class)
		except Exception as e:
			frappe.log_error(f"Failed to load provider {provider_doc.provider_name}: {str(e)}")
	
	@classmethod
	def get_providers_by_industry(cls, industry):
		"""Get providers for a specific industry"""
		providers = frappe.get_all("Demo Provider",
			filters={"is_active": 1, "status": "Active"},
			fields=["name", "provider_name", "provider_type"]
		)

		matching_providers = []
		for provider in providers:
			provider_doc = frappe.get_doc("Demo Provider", provider.name)
			for industry_row in provider_doc.supported_industries:
				if industry_row.industry == industry:
					matching_providers.append(provider)
					break

		return matching_providers

	@classmethod
	def get_providers_by_doctype(cls, doctype):
		"""Get providers that support a specific doctype"""
		providers = frappe.get_all("Demo Provider",
			filters={"is_active": 1, "status": "Active"},
			fields=["name", "provider_name", "provider_type"]
		)

		matching_providers = []
		for provider in providers:
			provider_doc = frappe.get_doc("Demo Provider", provider.name)
			for doctype_row in provider_doc.supported_doctypes:
				if doctype_row.doctype == doctype:
					matching_providers.append(provider)
					break

		return matching_providers

@frappe.whitelist()
def refresh_provider_registry():
	"""Refresh the provider registry"""
	ProviderRegistry.discover_providers()
	return {"status": "success", "message": "Provider registry refreshed"}

@frappe.whitelist()
def get_available_providers():
	"""Get all available providers"""
	return ProviderRegistry._providers.keys()
