import frappe
from frappe import _
import json
import uuid
from datetime import datetime, timedelta

class DemoGenerator:
	"""Main demo generation engine"""
	
	def __init__(self, demo_environment_name):
		self.demo_environment = frappe.get_doc("Demo Environment", demo_environment_name)
		self.job = None
		self.generation_id = f"GEN-{uuid.uuid4().hex[:12].upper()}"
	
	def generate_demo_environment(self):
		"""Generate complete demo environment"""
		try:
			self.demo_environment.is_demo = 1
			self.create_generation_job()
			self.demo_environment.generation_id = self.generation_id
			self.demo_environment.generator_version = "1.0.0"
			self.demo_environment.status = "Generating"
			self.demo_environment.save()
			
			steps = self.get_generation_steps()
			total_steps = len(steps)
			
			for i, step in enumerate(steps):
				if self.check_cancel_requested():
					self.job.mark_cancelled()
					self.demo_environment.status = "Error"
					self.demo_environment.save()
					return
				
				self.execute_step(step, i + 1, total_steps)
			
			self.job.mark_completed()
			self.demo_environment.status = "Ready"
			self.demo_environment.health_status = "Healthy"
			self.demo_environment.save()
			
		except Exception as e:
			if self.job:
				self.job.mark_failed(str(e), frappe.get_traceback())
			self.demo_environment.status = "Error"
			self.demo_environment.save()
			raise
	
	def create_generation_job(self):
		"""Create generation job record"""
		self.job = frappe.new_doc("Demo Generation Job")
		self.job.job_name = f"{self.demo_environment.demo_name}-Generation"
		self.job.job_type = "Generation"
		self.job.demo_environment = self.demo_environment.name
		self.job.template = self.demo_environment.template
		self.job.status = "Running"
		self.job.started_by = frappe.session.user
		self.job.started_at = frappe.utils.now()
		self.job.save()
		
		# Add generation steps
		steps = self.get_generation_steps()
		for step in steps:
			self.job.append("generation_steps", {
				"step_name": step["name"],
				"step_type": step["type"],
				"status": "Pending"
			})
		self.job.save()
	
	def get_generation_steps(self):
		"""Get generation steps based on template"""
		steps = [
			{"name": "Generate Company", "type": "Company"},
			{"name": "Generate Branches", "type": "Branch"},
			{"name": "Generate Departments", "type": "Department"},
			{"name": "Generate Employees", "type": "Employee"},
			{"name": "Generate Customers", "type": "Customer"},
			{"name": "Generate Suppliers", "type": "Supplier"},
			{"name": "Generate Items", "type": "Item"},
			{"name": "Generate Transactions", "type": "Transaction"},
			{"name": "Generate Accounting Entries", "type": "Accounting"},
			{"name": "Validate Environment", "type": "Validation"}
		]
		return steps
	
	def execute_step(self, step, current_step, total_steps):
		"""Execute a generation step"""
		step_index = current_step - 1
		step_doc = self.job.generation_steps[step_index]
		step_doc.status = "Running"
		step_doc.started_at = frappe.utils.now()
		self.job.save()
		
		try:
			# Execute step based on type
			if step["type"] == "Company":
				self.generate_company()
			elif step["type"] == "Branch":
				self.generate_branches()
			elif step["type"] == "Department":
				self.generate_departments()
			elif step["type"] == "Employee":
				self.generate_employees()
			elif step["type"] == "Customer":
				self.generate_customers()
			elif step["type"] == "Supplier":
				self.generate_suppliers()
			elif step["type"] == "Item":
				self.generate_items()
			elif step["type"] == "Transaction":
				self.generate_transactions()
			elif step["type"] == "Accounting":
				self.generate_accounting_entries()
			elif step["type"] == "Validation":
				self.validate_environment()
			
			step_doc.status = "Completed"
			step_doc.completed_at = frappe.utils.now()
			
			# Update progress
			progress = int((current_step / total_steps) * 100)
			self.job.update_progress(current_step, total_steps, progress)
			self.job.add_log_entry({
				"step": step["name"],
				"status": "Completed",
				"message": f"Step {step['name']} completed successfully"
			})
			
		except Exception as e:
			step_doc.status = "Failed"
			step_doc.error_message = str(e)
			step_doc.completed_at = frappe.utils.now()
			self.job.add_log_entry({
				"step": step["name"],
				"status": "Failed",
				"message": str(e)
			})
			raise
		
		self.job.save()
	
	def generate_company(self):
		"""Generate company"""
		if not self.demo_environment.company_name:
			self.demo_environment.company_name = f"{self.demo_environment.demo_name} Company"
		
		# Check if company already exists
		if frappe.db.exists("Company", self.demo_environment.company_name):
			self.demo_environment.company = self.demo_environment.company_name
			return
		
		company = frappe.new_doc("Company")
		company.company_name = self.demo_environment.company_name
		company.abbr = self.demo_environment.company_name[:3].upper()
		company.country = "United States"
		company.default_currency = "USD"
		company.enable_perpetual_inventory = 1
		self.apply_template_company_profile(company)
		company.insert()
		
		self.demo_environment.company = company.name
		self.demo_environment.save()
	
	def generate_branches(self):
		"""Generate branches"""
		template_config = self.get_template_config("branch_config", {"branch_count": 3})
		branch_names = template_config.get("branch_names") or []
		branch_count = max(template_config.get("branch_count", 3), len(branch_names))
		created_branches = []
		
		for i in range(branch_count):
			branch_name = branch_names[i] if i < len(branch_names) else f"{self.demo_environment.company_name} - Branch {i+1}"
			if not frappe.db.exists("Branch", branch_name):
				branch = frappe.new_doc("Branch")
				branch.branch = branch_name
				branch.company = self.demo_environment.company
				branch.insert()
				created_branches.append(branch.name)
			else:
				created_branches.append(branch_name)
		
		self.branch_records = created_branches
		self.demo_environment.branches = len(created_branches)
		self.demo_environment.save()
	
	def generate_departments(self):
		"""Generate departments"""
		template_config = self.get_template_config("employee_config", {})
		departments = template_config.get("department_names") or [
			"Sales", "Purchase", "HR", "Finance", "Operations", "IT"
		]
		dept_count = len(departments)
		
		for dept_name in departments:
			if not frappe.db.exists("Department", dept_name):
				dept = frappe.new_doc("Department")
				dept.department_name = dept_name
				dept.company = self.demo_environment.company
				dept.insert()
		
		self.demo_environment.departments = dept_count
		self.demo_environment.save()
	
	def generate_employees(self):
		"""Generate employees"""
		template_config = self.get_template_config("employee_config", {"employee_count": 50})
		employee_count = template_config.get("employee_count", 50)
		seed = self.get_template_config("company_config", {}).get("sample_data_seed", {})
		employee_count = seed.get("employees", seed.get("consultants", seed.get("teachers", seed.get("care_teams", employee_count))))
		
		# This is a placeholder - actual implementation would create realistic employee data
		self.demo_environment.employees = employee_count
		self.demo_environment.save()
	
	def generate_customers(self):
		"""Generate customers"""
		template_config = self.get_template_config("customer_config", {"customer_count": 100})
		customer_count = template_config.get("customer_count", 100)
		seed = self.get_template_config("company_config", {}).get("sample_data_seed", {})
		customer_count = seed.get("customers", seed.get("patients", seed.get("students", seed.get("rental_contracts", customer_count))))
		customer_records = self.create_master_records(
			doctype="Customer",
			count=customer_count,
			name_prefix=self.get_customer_prefix(),
			data_factory=self.build_customer_payload,
		)
		self.customer_records = customer_records
		self.create_master_contacts_and_addresses("Customer", customer_records)
		self.demo_environment.customers = len(customer_records)
		self.demo_environment.save()
	
	def generate_suppliers(self):
		"""Generate suppliers"""
		template_config = self.get_template_config("supplier_config", {"supplier_count": 50})
		supplier_count = template_config.get("supplier_count", 50)
		seed = self.get_template_config("company_config", {}).get("sample_data_seed", {})
		supplier_count = seed.get("suppliers", seed.get("subcontractors", seed.get("service_jobs", supplier_count)))
		supplier_records = self.create_master_records(
			doctype="Supplier",
			count=supplier_count,
			name_prefix=self.get_supplier_prefix(),
			data_factory=self.build_supplier_payload,
		)
		self.supplier_records = supplier_records
		self.create_master_contacts_and_addresses("Supplier", supplier_records)
		self.demo_environment.suppliers = len(supplier_records)
		self.demo_environment.save()
	
	def generate_items(self):
		"""Generate items"""
		seed = self.get_template_config("company_config", {}).get("sample_data_seed", {})
		item_count = seed.get("items", seed.get("products", seed.get("vehicles", seed.get("crops", seed.get("projects", 200)))))
		item_records = self.create_master_records(
			doctype="Item",
			count=item_count,
			name_prefix=self.get_item_prefix(),
			data_factory=self.build_item_payload,
		)
		self.item_records = item_records
		self.demo_environment.items = len(item_records)
		self.demo_environment.save()
	
	def generate_transactions(self):
		"""Generate transactions"""
		template_config = self.get_template_config("transaction_config", {"transaction_months": 12, "transactions_per_month": 100})
		months = template_config.get("transaction_months", 12)
		per_month = template_config.get("transactions_per_month", 100)
		monthly_weights = template_config.get("monthly_weights") or [1 / months] * months
		template_company = self.get_template_config("company_config", {})
		report_profiles = template_company.get("report_profiles") or []
		kpi_focus = template_company.get("kpi_focus") or []
		sample_data_seed = template_company.get("sample_data_seed") or {}
		
		total_transactions = months * per_month
		monthly_projection = self.build_monthly_projection(months, per_month, monthly_weights)
		financial_summary = self.generate_financial_documents(monthly_projection)
		
		self.demo_environment.transactions = financial_summary.get("total_created", 0)
		self.demo_environment.generation_log = json.dumps(
			{
				"annual_cycle": True,
				"months": months,
				"transactions_per_month_base": per_month,
				"planned_volume": total_transactions,
				"actual_documents_created": financial_summary.get("total_created", 0),
				"customer_party_label": self.get_customer_party_label(),
				"monthly_projection": monthly_projection,
				"report_profiles": report_profiles,
				"kpi_focus": kpi_focus,
				"sample_data_seed": sample_data_seed,
				"financial_summary": financial_summary,
			},
			indent=2,
		)
		self.demo_environment.save()
	
	def generate_accounting_entries(self):
		"""Generate accounting entries"""
		# Placeholder for accounting entry generation
		pass
	
	def validate_environment(self):
		"""Validate generated environment"""
		validation_log = {
			"company": bool(self.demo_environment.company),
			"branches": self.demo_environment.branches > 0,
			"departments": self.demo_environment.departments > 0,
			"employees": self.demo_environment.employees > 0,
			"customers": self.demo_environment.customers > 0,
			"suppliers": self.demo_environment.suppliers > 0,
			"items": self.demo_environment.items > 0,
			"transactions": self.demo_environment.transactions > 0
		}
		
		self.demo_environment.validation_log = json.dumps(validation_log, indent=2)
		self.demo_environment.save()

	def apply_template_company_profile(self, company):
		"""Apply safe company-level template values when the field options allow them."""
		template_company = self.get_template_config("company_config", {})
		self.safe_set_field(company, "business_activity", template_company.get("business_activity"))
		self.safe_set_field(company, "industry_sector", template_company.get("industry_sector"))

	def safe_set_field(self, doc, fieldname, value):
		"""Set a field only when the target field exists and accepts the value safely."""
		if not value or not hasattr(doc, fieldname):
			return

		meta = frappe.get_meta(doc.doctype)
		field = meta.get_field(fieldname)
		if not field:
			return

		options = (field.options or "").splitlines()
		if options and value not in options:
			return

		setattr(doc, fieldname, value)

	def build_monthly_projection(self, months, per_month, monthly_weights):
		"""Build a stable 12-month projection from template weights."""
		if not monthly_weights:
			monthly_weights = [1 / months] * months

		weights = list(monthly_weights)[:months]
		if len(weights) < months:
			weights.extend([0] * (months - len(weights)))

		total_weight = sum(weights) or months
		total_transactions = months * per_month
		projection = []
		running_total = 0

		for index, weight in enumerate(weights):
			if index == months - 1:
				count = total_transactions - running_total
			else:
				count = int(round(total_transactions * (weight / total_weight)))
				running_total += count
			projection.append({
				"month": index + 1,
				"target_transactions": max(count, 0),
			})

		return projection

	def create_master_records(self, doctype, count, name_prefix, data_factory):
		"""Create simple master records when the target DocType exists."""
		if not frappe.db.exists("DocType", doctype):
			return []

		created = []
		for index in range(1, count + 1):
			record_data = data_factory(index=index, prefix=name_prefix)
			unique_name = record_data.pop("unique_name", None)
			if unique_name and frappe.db.exists(doctype, unique_name):
				created.append(unique_name)
				continue

			try:
				doc = frappe.get_doc({"doctype": doctype, **record_data})
				doc.insert(ignore_permissions=True)
				created.append(doc.name)
			except Exception as exc:
				frappe.log_error(
					f"Failed to create {doctype} {unique_name or index}: {exc}",
					f"Demo seed failed for {doctype}",
				)

		return created

	def create_master_contacts_and_addresses(self, parent_doctype, parent_names):
		"""Attach a minimal contact and address to a subset of generated masters."""
		if not parent_names:
			return
		if not frappe.db.exists("DocType", "Contact") or not frappe.db.exists("DocType", "Address"):
			return

		for name in parent_names[: min(10, len(parent_names))]:
			self.ensure_contact_for_parent(parent_doctype, name)
			self.ensure_address_for_parent(parent_doctype, name)

	def ensure_contact_for_parent(self, parent_doctype, parent_name):
		"""Create a contact linked to the given parent if it doesn't already exist."""
		contact_name = f"{parent_name} Contact"
		if frappe.db.exists("Contact", contact_name):
			return

		contact = frappe.get_doc({
			"doctype": "Contact",
			"first_name": parent_name,
			"email_id": f"{parent_name.lower().replace(' ', '.')}@example.com",
		})
		contact.append("links", {"link_doctype": parent_doctype, "link_name": parent_name})
		contact.insert(ignore_permissions=True)

	def ensure_address_for_parent(self, parent_doctype, parent_name):
		"""Create an address linked to the given parent if it doesn't already exist."""
		address_name = f"{parent_name} Address"
		if frappe.db.exists("Address", address_name):
			return

		address = frappe.get_doc({
			"doctype": "Address",
			"address_title": address_name,
			"address_line1": f"{parent_name} Main Street",
			"city": "Demo City",
			"country": "United States",
			"address_type": "Billing",
		})
		address.append("links", {"link_doctype": parent_doctype, "link_name": parent_name})
		address.insert(ignore_permissions=True)

	def build_customer_payload(self, index, prefix):
		"""Build a customer payload for a specific index."""
		party_label = self.get_customer_party_label()
		return {
			"customer_name": f"{prefix} {party_label} {index:03d}",
			"customer_group": self.get_default_customer_group(),
			"territory": self.get_default_territory(),
			"unique_name": f"{prefix} {party_label} {index:03d}",
		}

	def build_supplier_payload(self, index, prefix):
		"""Build a supplier payload for a specific index."""
		return {
			"supplier_name": f"{prefix} Supplier {index:03d}",
			"supplier_group": self.get_default_supplier_group(),
			"unique_name": f"{prefix} Supplier {index:03d}",
		}

	def build_item_payload(self, index, prefix):
		"""Build an item payload for a specific index."""
		item_code = f"{prefix[:3].upper()}-ITEM-{index:04d}"
		return {
			"item_code": item_code,
			"item_name": f"{prefix} Item {index:04d}",
			"item_group": self.get_default_item_group(),
			"stock_uom": self.get_default_uom(),
			"is_stock_item": 1,
			"unique_name": item_code,
		}

	def get_customer_prefix(self):
		"""Derive a customer prefix from the template."""
		return self.get_template_config("company_config", {}).get("business_activity") or self.demo_environment.demo_name

	def get_customer_party_label(self):
		"""Return the user-facing label for customer-like master records."""
		lang = self.get_ui_language()
		return self.get_localized_party_label(lang)

	def get_localized_party_label(self, lang):
		"""Map the party label to the current UI language."""
		company_config = self.get_template_config("company_config", {})
		business_activity = (company_config.get("business_activity") or "").strip().lower()
		industry_sector = (company_config.get("industry_sector") or "").strip().lower()
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

	def get_supplier_prefix(self):
		"""Derive a supplier prefix from the template."""
		return self.get_template_config("company_config", {}).get("industry") or self.demo_environment.demo_name

	def get_item_prefix(self):
		"""Derive an item prefix from the template."""
		return self.get_template_config("company_config", {}).get("business_activity") or self.demo_environment.demo_name

	def get_default_customer_group(self):
		"""Get a safe customer group fallback."""
		return self.get_or_create_root_group("Customer Group", "customer_group_name", "All Customer Groups")

	def get_default_supplier_group(self):
		"""Get a safe supplier group fallback."""
		return self.get_or_create_root_group("Supplier Group", "supplier_group_name", "All Supplier Groups")

	def get_default_item_group(self):
		"""Get a safe item group fallback."""
		return self.get_or_create_root_group("Item Group", "item_group_name", "All Item Groups")

	def get_default_territory(self):
		"""Get a safe territory fallback."""
		return self.get_or_create_root_group("Territory", "territory_name", "All Territories")

	def get_default_uom(self):
		"""Get a safe stock UOM fallback."""
		if frappe.db.exists("UOM", "Nos"):
			return "Nos"

		if not frappe.db.exists("DocType", "UOM"):
			return "Nos"

		uoms = frappe.get_all("UOM", pluck="name", limit=1)
		uom = uoms[0] if uoms else None
		return uom or "Nos"

	def generate_financial_documents(self, monthly_projection):
		"""Generate an annual chain of orders and invoices when the doctypes exist."""
		summary = {
			"sales_orders": 0,
			"sales_invoices": 0,
			"delivery_notes": 0,
			"purchase_orders": 0,
			"purchase_invoices": 0,
			"purchase_receipts": 0,
			"stock_entries": 0,
			"journal_entries": 0,
			"monthly_batches": 0,
			"total_created": 0,
		}

		if not self.demo_environment.company:
			return summary

		service_item = self.ensure_service_item()
		stock_item = self.ensure_stock_item()
		warehouse = self.ensure_primary_warehouse()
		customer = self.get_primary_customer()
		supplier = self.get_primary_supplier()
		monthly_dates = [frappe.utils.add_months(frappe.utils.getdate(), idx) for idx in range(len(monthly_projection))]

		if not service_item and not stock_item:
			return summary

		for index, month_data in enumerate(monthly_projection):
			posting_date = monthly_dates[index]
			batch_created = 0
			if customer:
				so_name = self.create_sales_order(customer, service_item, posting_date, index, month_data)
				if so_name:
					summary["sales_orders"] += 1
					batch_created += 1
				si_name = self.create_sales_invoice(customer, service_item, posting_date, index, month_data, so_name)
				if si_name:
					summary["sales_invoices"] += 1
					batch_created += 1
				dn_name = self.create_delivery_note(customer, stock_item, warehouse, posting_date, index, month_data, so_name)
				if dn_name:
					summary["delivery_notes"] += 1
					batch_created += 1
			if supplier:
				po_name = self.create_purchase_order(supplier, service_item, posting_date, index, month_data)
				if po_name:
					summary["purchase_orders"] += 1
					batch_created += 1
				pi_name = self.create_purchase_invoice(supplier, service_item, posting_date, index, month_data, po_name)
				if pi_name:
					summary["purchase_invoices"] += 1
					batch_created += 1
				pr_name = self.create_purchase_receipt(supplier, stock_item, warehouse, posting_date, index, month_data, po_name)
				if pr_name:
					summary["purchase_receipts"] += 1
					batch_created += 1
			if stock_item and warehouse:
				se_name = self.create_stock_entry(stock_item, warehouse, posting_date, index, month_data)
				if se_name:
					summary["stock_entries"] += 1
					batch_created += 1
			je_name = self.create_monthly_journal_entry(posting_date, index, month_data)
			if je_name:
				summary["journal_entries"] += 1
				batch_created += 1

			if batch_created:
				summary["monthly_batches"] += 1
				summary["total_created"] += batch_created

		return summary

	def ensure_service_item(self):
		"""Create or resolve a generic service item for financial docs."""
		if not frappe.db.exists("DocType", "Item"):
			return None

		existing = frappe.db.get_value("Item", {"item_code": "DEMO-SERVICE"}, "name")
		if existing:
			return existing

		payload = {
			"doctype": "Item",
			"item_code": "DEMO-SERVICE",
			"item_name": f"{self.get_template_config('company_config', {}).get('business_activity') or 'Demo'} Service",
			"item_group": self.get_default_item_group(),
			"stock_uom": self.get_default_uom(),
			"is_stock_item": 0,
		}
		for field in ("is_sales_item", "is_purchase_item"):
			payload[field] = 1
		try:
			doc = frappe.get_doc(payload)
			doc.insert(ignore_permissions=True)
			return doc.name
		except Exception:
			return frappe.db.get_value("Item", {"item_code": "DEMO-SERVICE"}, "name")

	def ensure_stock_item(self):
		"""Create or resolve a stock item for inventory documents."""
		if not frappe.db.exists("DocType", "Item"):
			return None

		existing = frappe.db.get_value("Item", {"item_code": "DEMO-STOCK"}, "name")
		if existing:
			return existing

		payload = {
			"doctype": "Item",
			"item_code": "DEMO-STOCK",
			"item_name": f"{self.get_template_config('company_config', {}).get('business_activity') or 'Demo'} Stock Item",
			"item_group": self.get_default_item_group(),
			"stock_uom": self.get_default_uom(),
			"is_stock_item": 1,
		}
		try:
			doc = frappe.get_doc(payload)
			doc.insert(ignore_permissions=True)
			return doc.name
		except Exception:
			return frappe.db.get_value("Item", {"item_code": "DEMO-STOCK"}, "name")

	def ensure_primary_warehouse(self):
		"""Create or resolve a warehouse for demo stock movement."""
		if not frappe.db.exists("DocType", "Warehouse"):
			return None

		existing = frappe.db.get_value("Warehouse", {"warehouse_name": "Demo Warehouse", "company": self.demo_environment.company}, "name")
		if existing:
			return existing

		payload = {
			"doctype": "Warehouse",
			"warehouse_name": "Demo Warehouse",
			"company": self.demo_environment.company,
		}
		if frappe.db.exists("DocType", "Warehouse"):
			try:
				doc = frappe.get_doc(payload)
				doc.insert(ignore_permissions=True)
				return doc.name
			except Exception:
				return frappe.db.get_value("Warehouse", {"warehouse_name": "Demo Warehouse", "company": self.demo_environment.company}, "name")

		return None

	def get_primary_customer(self):
		"""Return the first generated or existing customer."""
		if getattr(self, "customer_records", None):
			return self.customer_records[0]
		customers = frappe.get_all("Customer", pluck="name", limit=1)
		return customers[0] if customers else None

	def get_primary_supplier(self):
		"""Return the first generated or existing supplier."""
		if getattr(self, "supplier_records", None):
			return self.supplier_records[0]
		suppliers = frappe.get_all("Supplier", pluck="name", limit=1)
		return suppliers[0] if suppliers else None

	def create_sales_order(self, customer, item, posting_date, index, month_data):
		"""Create a sales order for one monthly batch."""
		if not frappe.db.exists("DocType", "Sales Order"):
			return None

		meta = frappe.get_meta("Sales Order")
		payload = {
			"doctype": "Sales Order",
			"company": self.demo_environment.company,
			"customer": customer,
			"transaction_date": posting_date,
			"items": [
				{
					"item_code": item,
					"qty": max(1, int(month_data["target_transactions"] / 40) or 1),
					"rate": 250 + (index * 10),
				}
			],
		}
		if meta.has_field("branch") and self.demo_environment.company:
			payload["branch"] = self.get_primary_branch()
		return self._insert_optional_submit("Sales Order", payload)

	def create_sales_invoice(self, customer, item, posting_date, index, month_data, sales_order):
		"""Create a sales invoice for one monthly batch."""
		if not frappe.db.exists("DocType", "Sales Invoice"):
			return None

		meta = frappe.get_meta("Sales Invoice")
		payload = {
			"doctype": "Sales Invoice",
			"company": self.demo_environment.company,
			"customer": customer,
			"posting_date": posting_date,
			"due_date": frappe.utils.add_days(posting_date, 30),
			"items": [
				{
					"item_code": item,
					"qty": max(1, int(month_data["target_transactions"] / 50) or 1),
					"rate": 300 + (index * 15),
				}
			],
		}
		if sales_order and meta.has_field("sales_order"):
			payload["sales_order"] = sales_order
		if meta.has_field("branch"):
			payload["branch"] = self.get_primary_branch()
		return self._insert_optional_submit("Sales Invoice", payload)

	def create_purchase_order(self, supplier, item, posting_date, index, month_data):
		"""Create a purchase order for one monthly batch."""
		if not frappe.db.exists("DocType", "Purchase Order"):
			return None

		meta = frappe.get_meta("Purchase Order")
		payload = {
			"doctype": "Purchase Order",
			"company": self.demo_environment.company,
			"supplier": supplier,
			"transaction_date": posting_date,
			"items": [
				{
					"item_code": item,
					"qty": max(1, int(month_data["target_transactions"] / 60) or 1),
					"rate": 180 + (index * 8),
				}
			],
		}
		if meta.has_field("branch"):
			payload["branch"] = self.get_primary_branch()
		return self._insert_optional_submit("Purchase Order", payload)

	def create_purchase_invoice(self, supplier, item, posting_date, index, month_data, purchase_order):
		"""Create a purchase invoice for one monthly batch."""
		if not frappe.db.exists("DocType", "Purchase Invoice"):
			return None

		meta = frappe.get_meta("Purchase Invoice")
		payload = {
			"doctype": "Purchase Invoice",
			"company": self.demo_environment.company,
			"supplier": supplier,
			"posting_date": posting_date,
			"due_date": frappe.utils.add_days(posting_date, 30),
			"items": [
				{
					"item_code": item,
					"qty": max(1, int(month_data["target_transactions"] / 60) or 1),
					"rate": 180 + (index * 8),
				}
			],
		}
		if purchase_order and meta.has_field("purchase_order"):
			payload["purchase_order"] = purchase_order
		if meta.has_field("branch"):
			payload["branch"] = self.get_primary_branch()
		return self._insert_optional_submit("Purchase Invoice", payload)

	def create_delivery_note(self, customer, item, warehouse, posting_date, index, month_data, sales_order):
		"""Create a delivery note for inventory-based activities when possible."""
		if not item or not warehouse or not frappe.db.exists("DocType", "Delivery Note"):
			return None

		meta = frappe.get_meta("Delivery Note")
		payload = {
			"doctype": "Delivery Note",
			"company": self.demo_environment.company,
			"customer": customer,
			"posting_date": posting_date,
			"items": [
				{
					"item_code": item,
					"qty": max(1, int(month_data["target_transactions"] / 80) or 1),
					"rate": 300 + (index * 12),
					"warehouse": warehouse,
				}
			],
		}
		if sales_order and meta.has_field("sales_order"):
			payload["sales_order"] = sales_order
		if meta.has_field("branch"):
			payload["branch"] = self.get_primary_branch()
		return self._insert_optional_submit("Delivery Note", payload)

	def create_purchase_receipt(self, supplier, item, warehouse, posting_date, index, month_data, purchase_order):
		"""Create a purchase receipt for inventory-based activities when possible."""
		if not item or not warehouse or not frappe.db.exists("DocType", "Purchase Receipt"):
			return None

		meta = frappe.get_meta("Purchase Receipt")
		payload = {
			"doctype": "Purchase Receipt",
			"company": self.demo_environment.company,
			"supplier": supplier,
			"posting_date": posting_date,
			"items": [
				{
					"item_code": item,
					"qty": max(1, int(month_data["target_transactions"] / 80) or 1),
					"rate": 180 + (index * 8),
					"warehouse": warehouse,
				}
			],
		}
		if purchase_order and meta.has_field("purchase_order"):
			payload["purchase_order"] = purchase_order
		if meta.has_field("branch"):
			payload["branch"] = self.get_primary_branch()
		return self._insert_optional_submit("Purchase Receipt", payload)

	def create_stock_entry(self, item, warehouse, posting_date, index, month_data):
		"""Create a stock entry for inventory movement when possible."""
		if not item or not warehouse or not frappe.db.exists("DocType", "Stock Entry"):
			return None

		meta = frappe.get_meta("Stock Entry")
		payload = {
			"doctype": "Stock Entry",
			"company": self.demo_environment.company,
			"posting_date": posting_date,
			"purpose": "Material Receipt" if meta.has_field("purpose") else None,
			"items": [
				{
					"item_code": item,
					"qty": max(1, int(month_data["target_transactions"] / 100) or 1),
					"basic_rate": 150 + (index * 5),
					"t_warehouse": warehouse,
				}
			],
		}
		if meta.has_field("to_warehouse"):
			payload["to_warehouse"] = warehouse
		if meta.has_field("branch"):
			payload["branch"] = self.get_primary_branch()
		return self._insert_optional_submit("Stock Entry", payload)

	def create_monthly_journal_entry(self, posting_date, index, month_data):
		"""Create a simple balanced journal entry when accounts are available."""
		if not frappe.db.exists("DocType", "Journal Entry"):
			return None

		accounts = frappe.get_all(
			"Account",
			filters={"company": self.demo_environment.company, "is_group": 0},
			pluck="name",
			limit=2,
		)
		if len(accounts) < 2:
			return None

		meta = frappe.get_meta("Journal Entry")
		debit_account, credit_account = accounts[0], accounts[1]
		payload = {
			"doctype": "Journal Entry",
			"company": self.demo_environment.company,
			"posting_date": posting_date,
			"remarks": f"Annual demo monthly adjustment {index + 1}",
			"accounts": [
				self.build_journal_row(meta, debit_account, debit=500 + (index * 20)),
				self.build_journal_row(meta, credit_account, credit=500 + (index * 20)),
			],
		}
		if meta.has_field("branch"):
			payload["branch"] = self.get_primary_branch()
		return self._insert_optional_submit("Journal Entry", payload)

	def build_journal_row(self, meta, account, debit=0, credit=0):
		"""Build a journal entry account row compatible with common ERPNext fields."""
		row = {"account": account}
		if meta.has_field("debit"):
			row["debit"] = debit
		if meta.has_field("credit"):
			row["credit"] = credit
		if meta.has_field("debit_in_account_currency"):
			row["debit_in_account_currency"] = debit
		if meta.has_field("credit_in_account_currency"):
			row["credit_in_account_currency"] = credit
		return row

	def _insert_optional_submit(self, doctype, payload):
		"""Insert a document and try to submit it if the workflow allows it."""
		try:
			payload = {k: v for k, v in payload.items() if v is not None}
			doc = frappe.get_doc(payload)
			doc.insert(ignore_permissions=True)
			if getattr(doc.meta, "is_submittable", False) and doc.docstatus == 0:
				try:
					doc.submit()
				except Exception:
					frappe.log_error(
						frappe.get_traceback(),
						f"Demo submission skipped for {doctype} {doc.name}",
					)
			return doc.name
		except Exception as exc:
			frappe.log_error(
				f"Failed to create demo {doctype}: {exc}",
				f"Demo transaction seed failed for {doctype}",
			)
			return None

	def get_primary_branch(self):
		"""Return the first generated or existing branch."""
		if getattr(self, "branch_records", None):
			return self.branch_records[0]
		branches = frappe.db.get_all("Branch", filters={"company": self.demo_environment.company}, pluck="name", limit=1)
		return branches[0] if branches else None

	def get_or_create_root_group(self, doctype, name_field, group_name):
		"""Get or create a root group record used by seeded masters."""
		if not frappe.db.exists("DocType", doctype):
			return None

		if frappe.db.exists(doctype, group_name):
			return group_name

		try:
			doc = frappe.get_doc({
				"doctype": doctype,
				name_field: group_name,
				"is_group": 1,
			})
			doc.insert(ignore_permissions=True)
			return doc.name
		except Exception:
			# If the schema is stricter than expected, fail softly and let callers decide.
			return None

	def get_template_config(self, config_key, default=None):
		"""Get configuration from template"""
		if not self.demo_environment.template:
			return default or {}
		
		template = frappe.get_doc("Demo Template", self.demo_environment.template)
		config_value = template.get(config_key)
		
		if config_value:
			try:
				return json.loads(config_value)
			except json.JSONDecodeError:
				return default or {}
		
		return default or {}
	
	def check_cancel_requested(self):
		"""Check if job cancellation was requested"""
		if self.job and self.job.cancel_requested:
			return True
		return False

def generate_demo_environment(demo_name):
	"""Background job entry point for demo generation"""
	generator = DemoGenerator(demo_name)
	generator.generate_demo_environment()

def reset_demo_environment(demo_name):
	"""Reset a demo environment to initial state"""
	demo = frappe.get_doc("Demo Environment", demo_name)
	
	# Delete all demo data
	# This would be implemented with proper cleanup logic
	
	demo.status = "Ready"
	demo.health_status = "Healthy"
	demo.save()
