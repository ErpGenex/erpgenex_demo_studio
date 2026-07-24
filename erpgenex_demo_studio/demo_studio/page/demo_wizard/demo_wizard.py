import frappe
from frappe import _

def get_context(context):
	"""Demo Wizard context - step-by-step demo deployment"""
	
	# Get available templates
	templates = frappe.get_all("Demo Template", 
		filters={"status": "Active", "is_active": 1},
		fields=["name", "template_name", "industry", "description"]
	)
	
	# Get industries
	industries = frappe.get_all("Industry", 
		fields=["industry_name", "description"]
	)
	
	# Get companies
	companies = frappe.get_all("Company",
		fields=["name", "company_name"],
		limit=20
	)
	
	context.templates = templates
	context.industries = industries
	context.companies = companies
	context.wizard_steps = [
		{
			"step": 1,
			"title": "اختر القالب",
			"description": "اختر قالب الديمو المناسب لنشاطك التجاري",
			"icon": "fa-file-alt"
		},
		{
			"step": 2,
			"title": "معلومات الديمو",
			"description": "أدخل اسم الديمو والشركة",
			"icon": "fa-info-circle"
		},
		{
			"step": 3,
			"title": "تأكيد",
			"description": "راجع المعلومات وابدأ النشر",
			"icon": "fa-check-circle"
		},
		{
			"step": 4,
			"title": "جاري النشر",
			"description": "شريط تقدم إنشاء الديمو",
			"icon": "fa-spinner"
		}
	]
	
	return context

@frappe.whitelist()
def get_template_details(template_name):
	"""Get template details for selected template"""
	try:
		template = frappe.get_doc("Demo Template", template_name)
		return {
			"template_name": template.template_name,
			"industry": template.industry,
			"description": template.description,
			"version": template.version
		}
	except Exception as e:
		frappe.throw(_("Template not found: {0}").format(template_name))

@frappe.whitelist()
def start_demo_generation(demo_data):
	"""Start demo generation process"""
	import json
	
	try:
		demo_info = json.loads(demo_data)
		
		# Create Demo Environment
		demo = frappe.new_doc("Demo Environment")
		demo.demo_name = demo_info.get("demo_name")
		demo.template = demo_info.get("template")
		demo.industry = demo_info.get("industry")
		demo.company_name = demo_info.get("company_name")
		demo.language = demo_info.get("language", "en")
		demo.status = "Generating"
		demo.save()
		
		# Trigger background job for generation
		frappe.enqueue("erpgenex_demo_studio.generators.demo_generator.generate_demo_environment",
			demo_name=demo.name, queue="long")
		
		return {
			"success": True,
			"demo_name": demo.name,
			"message": "تم بدء إنشاء الديمو بنجاح"
		}
		
	except Exception as e:
		frappe.log_error(f"Demo generation error: {str(e)}", "Demo Wizard Error")
		return {
			"success": False,
			"error": str(e)
		}

@frappe.whitelist()
def get_demo_progress(demo_name):
	"""Get demo generation progress"""
	try:
		demo = frappe.get_doc("Demo Environment", demo_name)
		
		progress = 0
		status_message = "جاري التحضير..."
		
		if demo.status == "Generating":
			progress = 25
			status_message = "جاري إنشاء البيانات..."
		elif demo.status == "Ready":
			progress = 100
			status_message = "تم إنشاء الديمو بنجاح"
		elif demo.status == "Error":
			progress = 0
			status_message = "حدث خطأ في إنشاء الديمو"
		
		return {
			"progress": progress,
			"status": demo.status,
			"message": status_message,
			"demo_id": demo.demo_id
		}
		
	except Exception as e:
		return {
			"progress": 0,
			"status": "Error",
			"message": str(e)
		}
