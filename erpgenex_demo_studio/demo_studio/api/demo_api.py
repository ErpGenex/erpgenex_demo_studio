import frappe
from frappe import _
import json

@frappe.whitelist()
def get_demo_statistics():
	"""Get overall demo statistics"""
	stats = {
		"total_environments": frappe.db.count("Demo Environment"),
		"active_environments": frappe.db.count("Demo Environment", {"is_active": 1, "status": "Ready"}),
		"total_templates": frappe.db.count("Demo Template"),
		"active_templates": frappe.db.count("Demo Template", {"is_active": 1, "status": "Active"}),
		"total_providers": frappe.db.count("Demo Provider"),
		"active_providers": frappe.db.count("Demo Provider", {"is_active": 1, "status": "Active"}),
		"running_jobs": frappe.db.count("Demo Generation Job", {"status": "Running"}),
		"completed_jobs": frappe.db.count("Demo Generation Job", {"status": "Completed"}),
		"failed_jobs": frappe.db.count("Demo Generation Job", {"status": "Failed"})
	}
	return stats

@frappe.whitelist()
def get_demo_environments(filters=None):
	"""Get demo environments with optional filters"""
	if filters:
		filters = json.loads(filters)
	else:
		filters = {}
	
	environments = frappe.get_all("Demo Environment",
		filters=filters,
		fields=["name", "demo_name", "demo_id", "status", "industry", "company_name", 
				"is_active", "health_status", "created_time", "last_updated"],
		order_by="created_time desc"
	)
	return environments

@frappe.whitelist()
def get_demo_templates(filters=None):
	"""Get demo templates with optional filters"""
	if filters:
		filters = json.loads(filters)
	else:
		filters = {}
	
	templates = frappe.get_all("Demo Template",
		filters=filters,
		fields=["name", "template_name", "version", "status", "industry", "is_standard", "is_active"],
		order_by="template_name"
	)
	return templates

@frappe.whitelist()
def validate_demo_environment(demo_name):
	"""Validate a demo environment"""
	demo = frappe.get_doc("Demo Environment", demo_name)
	
	validation_results = {
		"environment": demo_name,
		"validation_time": frappe.utils.now(),
		"checks": []
	}
	
	# Check company
	if demo.company:
		validation_results["checks"].append({
			"check": "Company exists",
			"status": "Passed" if frappe.db.exists("Company", demo.company) else "Failed"
		})
	
	# Check branches
	if demo.branches > 0:
		validation_results["checks"].append({
			"check": "Branches created",
			"status": "Passed"
		})
	
	# Check overall health
	validation_results["overall_status"] = "Healthy" if demo.health_status == "Healthy" else "Warning"
	
	return validation_results

@frappe.whitelist()
def export_demo_environment(demo_name):
	"""Export a demo environment configuration"""
	demo = frappe.get_doc("Demo Environment", demo_name)
	
	export_data = {
		"demo_name": demo.demo_name,
		"demo_id": demo.demo_id,
		"industry": demo.industry,
		"company_name": demo.company_name,
		"template": demo.template,
		"template_version": demo.template_version,
		"statistics": {
			"branches": demo.branches,
			"departments": demo.departments,
			"employees": demo.employees,
			"customers": demo.customers,
			"suppliers": demo.suppliers,
			"items": demo.items,
			"transactions": demo.transactions
		},
		"export_time": frappe.utils.now()
	}
	
	return export_data

@frappe.whitelist()
def import_demo_environment(export_data):
	"""Import a demo environment configuration"""
	data = json.loads(export_data)
	
	# Create new demo environment from export
	demo = frappe.new_doc("Demo Environment")
	demo.demo_name = f"{data['demo_name']} (Imported)"
	demo.industry = data.get("industry")
	demo.company_name = data.get("company_name")
	demo.template = data.get("template")
	demo.save()
	
	return demo.name

@frappe.whitelist()
def get_industries():
	"""Get available industries from Industry DocType"""
	industries = frappe.get_all("Industry", fields=["name", "industry_name"])
	return industries

@frappe.whitelist()
def health_check():
	"""Perform health check on demo studio"""
	health_status = {
		"status": "Healthy",
		"checks": [],
		"timestamp": frappe.utils.now()
	}
	
	# Check if required DocTypes exist
	required_doctypes = ["Demo Environment", "Demo Template", "Demo Provider", "Demo Generation Job"]
	for doctype in required_doctypes:
		if frappe.db.exists("DocType", doctype):
			health_status["checks"].append({
				"check": f"DocType {doctype} exists",
				"status": "Passed"
			})
		else:
			health_status["checks"].append({
				"check": f"DocType {doctype} exists",
				"status": "Failed"
			})
			health_status["status"] = "Critical"
	
	# Check workspace
	if frappe.db.exists("Workspace", "Demo Studio"):
		health_status["checks"].append({
			"check": "Demo Studio Workspace exists",
			"status": "Passed"
		})
	else:
		health_status["checks"].append({
			"check": "Demo Studio Workspace exists",
			"status": "Failed"
		})
		health_status["status"] = "Warning"
	
	return health_status
