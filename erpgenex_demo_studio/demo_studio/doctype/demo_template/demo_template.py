import frappe
from frappe.model.document import Document
from frappe import _
import json
from html import escape

class DemoTemplate(Document):
	def validate(self):
		self.validate_unique_template_name()
		self.validate_provider()
		self.validate_config_json()
	
	def validate_unique_template_name(self):
		"""Ensure template name is unique"""
		if self.template_name:
			existing = frappe.db.exists("Demo Template", {"template_name": self.template_name, "name": ["!=", self.name]})
			if existing:
				frappe.throw(_("Template name already exists"))
	
	def validate_provider(self):
		"""Validate provider if specified"""
		if self.provider:
			provider = frappe.get_doc("Demo Provider", self.provider)
			if provider.status != "Active":
				frappe.throw(_("Provider must be active"))
			self.provider_version = provider.version
	
	def validate_config_json(self):
		"""Validate JSON configuration fields"""
		json_fields = [
			"company_config", "branch_config", "employee_config",
			"customer_config", "supplier_config", "transaction_config",
			"business_rules", "validation_rules", "template_manifest"
		]
		
		for field in json_fields:
			value = self.get(field)
			if value:
				try:
					json.loads(value)
				except json.JSONDecodeError:
					frappe.throw(_(f"{field} must be valid JSON"))
	
	def before_save(self):
		"""Set default configurations if not provided"""
		self.set_default_configs()
		self.set_template_manifest()
		self.set_template_summary()
		self.set_template_data_generators()
	
	def set_default_configs(self):
		"""Set default JSON configurations"""
		default_configs = {
			"company_config": {
				"create_company": True,
				"default_country": "United States",
				"default_currency": "USD"
			},
			"branch_config": {
				"create_branches": True,
				"branch_count": 3
			},
			"employee_config": {
				"create_employees": True,
				"employee_count": 50
			},
			"customer_config": {
				"create_customers": True,
				"customer_count": 100
			},
			"supplier_config": {
				"create_suppliers": True,
				"supplier_count": 50
			},
			"transaction_config": {
				"create_transactions": True,
				"transaction_months": 12,
				"transactions_per_month": 100
			}
		}
		
		for field, default_value in default_configs.items():
			if not self.get(field):
				self.set(field, json.dumps(default_value, indent=2))

	def set_template_manifest(self):
		"""Build a user-facing manifest for the template."""
		customer_party_label = self.get_customer_party_label()
		manifest = {
			"template_name": self.template_name,
			"industry": self.industry,
			"version": self.version,
			"status": self.status,
			"description": self.description,
			"customer_party_label": customer_party_label,
			"report_profiles": self._json_or_empty("business_rules").get("report_profiles", []),
			"kpi_focus": self._json_or_empty("business_rules").get("kpi_focus", []),
			"sample_data_seed": self._json_or_empty("company_config").get("sample_data_seed", {}),
			"branch_names": self._json_or_empty("branch_config").get("branch_names", []),
			"department_names": self._json_or_empty("employee_config").get("department_names", []),
			"monthly_weights": self._json_or_empty("transaction_config").get("monthly_weights", []),
			"company_config": self._json_or_empty("company_config"),
			"branch_config": self._json_or_empty("branch_config"),
			"employee_config": self._json_or_empty("employee_config"),
			"customer_config": self._json_or_empty("customer_config"),
			"supplier_config": self._json_or_empty("supplier_config"),
			"transaction_config": self._json_or_empty("transaction_config"),
			"business_rules": self._json_or_empty("business_rules"),
			"validation_rules": self._json_or_empty("validation_rules"),
		}
		self.template_manifest = json.dumps(manifest, indent=2)

	def set_template_summary(self):
		"""Build a friendly HTML summary for the form."""
		manifest = self._manifest_dict()
		company = manifest.get("company_config", {})
		branch = manifest.get("branch_config", {})
		employee = manifest.get("employee_config", {})
		customer = manifest.get("customer_config", {})
		supplier = manifest.get("supplier_config", {})
		transaction = manifest.get("transaction_config", {})
		business_rules = manifest.get("business_rules", {})
		kpis = business_rules.get("kpi_focus") or []
		reports = business_rules.get("report_profiles") or []
		branch_names = branch.get("branch_names") or []
		department_names = employee.get("department_names") or []
		seasonality = company.get("seasonality") or business_rules.get("operating_model") or ""
		sample = company.get("sample_data_seed") or {}
		customer_party_label = manifest.get("customer_party_label") or self.get_customer_party_label()
		transaction_months = transaction.get("transaction_months", 12)
		per_month = transaction.get("transactions_per_month", 100)
		total_transactions = transaction_months * per_month

		summary = f"""
			<div class="text-muted small">
				<p><b>{escape(self.template_name or '')}</b> supports <b>{escape(self.industry or '')}</b> as a full annual demo template.</p>
				<ul>
					<li>Branches: {len(branch_names) or branch.get("branch_count", 0)}</li>
					<li>Departments: {len(department_names)}</li>
					<li>Employees target: {employee.get("employee_count", 0)}</li>
					<li>Customer label: {escape(customer_party_label)}</li>
					<li>Customers target: {customer.get("customer_count", 0)}</li>
					<li>Suppliers target: {supplier.get("supplier_count", 0)}</li>
					<li>Monthly transactions baseline: {per_month}</li>
					<li>Annual transactions baseline: {total_transactions}</li>
				</ul>
				<p><b>Seasonality:</b> {escape(seasonality)}</p>
				<p><b>KPI focus:</b> {", ".join(kpis) if kpis else "General"}</p>
				<p><b>Reports:</b> {", ".join(reports) if reports else "General reports"}</p>
				<p><b>Sample data seed:</b> {", ".join(f"{k}={v}" for k, v in sample.items()) if sample else "Default seed"}</p>
			</div>
		"""
		self.template_summary = summary

	def set_template_data_generators(self):
		"""Populate generator rows so the template shows what data it will create."""
		if not self.is_standard and self.get("data_generators"):
			return

		manifest = self._manifest_dict()
		company = manifest.get("company_config", {})
		branch = manifest.get("branch_config", {})
		employee = manifest.get("employee_config", {})
		customer = manifest.get("customer_config", {})
		supplier = manifest.get("supplier_config", {})
		transaction = manifest.get("transaction_config", {})
		business_rules = manifest.get("business_rules", {})
		sample = company.get("sample_data_seed") or {}
		customer_party_label = manifest.get("customer_party_label") or self.get_customer_party_label()
		rows = [
			{"generator_type": "Company", "generator_name": "Annual company profile", "config": json.dumps(company, indent=2), "enabled": 1, "priority": 10},
			{"generator_type": "Branch", "generator_name": "Branch network", "config": json.dumps(branch, indent=2), "enabled": 1, "priority": 20},
			{"generator_type": "Employee", "generator_name": "Workforce profile", "config": json.dumps({**employee, "sample_data_seed": {k: v for k, v in sample.items() if k in {"employees", "teachers", "care_teams", "consultants"}}}, indent=2), "enabled": 1, "priority": 30},
			{"generator_type": "Customer", "generator_name": f"{customer_party_label} base", "config": json.dumps(customer, indent=2), "enabled": 1, "priority": 40},
			{"generator_type": "Supplier", "generator_name": "Supplier base", "config": json.dumps(supplier, indent=2), "enabled": 1, "priority": 50},
			{"generator_type": "Item", "generator_name": "Item and asset seed", "config": json.dumps(sample, indent=2), "enabled": 1, "priority": 60},
			{"generator_type": "Transaction", "generator_name": "12-month activity curve", "config": json.dumps(transaction, indent=2), "enabled": 1, "priority": 70},
			{"generator_type": "Accounting", "generator_name": "Accounting and control profile", "config": json.dumps(business_rules, indent=2), "enabled": 1, "priority": 80},
		]

		if not self.get("data_generators"):
			self.set("data_generators", [])

		self.set("data_generators", [])
		for row in rows:
			self.append("data_generators", row)

	def _manifest_dict(self):
		"""Return the template manifest as a dict."""
		try:
			return json.loads(self.template_manifest) if self.template_manifest else {}
		except json.JSONDecodeError:
			return {}

	def _json_or_empty(self, fieldname):
		"""Parse a JSON field safely."""
		value = self.get(fieldname)
		if not value:
			return {}
		try:
			return json.loads(value)
		except json.JSONDecodeError:
			return {}

	def get_customer_party_label(self):
		"""Return the user-facing label for customer-like master records."""
		lang = self.get_ui_language()
		return self.get_localized_party_label(lang)

	def get_localized_party_label(self, lang):
		"""Map the party label to the current UI language."""
		company = self._json_or_empty("company_config")
		business_activity = (company.get("business_activity") or "").strip().lower()
		industry_sector = (company.get("industry_sector") or "").strip().lower()
		healthcare_tokens = {"healthcare", "health care", "medical", "hospital", "clinic"}
		education_tokens = {"education", "nursery", "school", "academy", "training"}
		arabic = (lang or "").lower().startswith("ar")
		if business_activity in healthcare_tokens or industry_sector in healthcare_tokens:
			return "مريض" if arabic else "Patient"
		if business_activity in education_tokens or industry_sector in education_tokens:
			return "طالب" if arabic else "Student"
		return "عميل" if arabic else "Customer"

	def get_ui_language(self):
		"""Resolve the current UI language as safely as possible."""
		lang = getattr(frappe.local, "lang", None)
		if lang:
			return lang
		user_lang = frappe.db.get_value("User", frappe.session.user, "language")
		if user_lang:
			return user_lang
		return frappe.get_system_settings("language") or "en"
