from __future__ import annotations

import json
from html import escape

import frappe
from frappe import _

from erpgenex_demo_studio.demo_studio.setup.demo_templates import ensure_annual_demo_templates


def _parse_json(value, default=None):
	if default is None:
		default = {}
	if not value:
		return default
	if isinstance(value, dict):
		return value
	try:
		return json.loads(value)
	except Exception:
		return default


def _safe_int(value, default=0):
	try:
		return int(value or default)
	except Exception:
		return default


def _first_non_empty(*values, default=""):
	for value in values:
		if value not in (None, "", [], {}):
			return value
	return default


def _estimate_template_profile(template_doc):
	manifest = _parse_json(template_doc.template_manifest, {})
	company = manifest.get("company_config", {})
	branch = manifest.get("branch_config", {})
	employee = manifest.get("employee_config", {})
	customer = manifest.get("customer_config", {})
	supplier = manifest.get("supplier_config", {})
	transaction = manifest.get("transaction_config", {})
	business_rules = manifest.get("business_rules", {})

	sample = company.get("sample_data_seed") or {}
	branch_names = branch.get("branch_names") or []
	department_names = employee.get("department_names") or []
	report_profiles = business_rules.get("report_profiles") or []
	kpi_focus = business_rules.get("kpi_focus") or []

	metrics = {
		"branches": _safe_int(_first_non_empty(branch.get("branch_count"), len(branch_names), default=0)),
		"departments": _safe_int(len(department_names)),
		"employees": _safe_int(_first_non_empty(employee.get("employee_count"), sample.get("employees"), default=0)),
		"customers": _safe_int(_first_non_empty(customer.get("customer_count"), sample.get("customers"), sample.get("patients"), sample.get("students"), sample.get("rental_contracts"), default=0)),
		"suppliers": _safe_int(_first_non_empty(supplier.get("supplier_count"), sample.get("suppliers"), default=0)),
		"items": _safe_int(_first_non_empty(sample.get("items"), sample.get("products"), sample.get("vehicles"), sample.get("crops"), sample.get("projects"), default=0)),
		"transactions": _safe_int(
			_first_non_empty(
				transaction.get("annual_transactions"),
				_safe_int(transaction.get("transaction_months"), 12) * _safe_int(transaction.get("transactions_per_month"), 100),
				default=12 * 100,
			)
		),
	}
	total = sum(metrics.values())
	scale = "خفيف" if total < 500 else "متوسط" if total < 1500 else "كامل"
	priority = "مقترح" if template_doc.is_standard else "جاهز"
	return {
		"metrics": metrics,
		"total_estimated_records": total,
		"scale": scale,
		"priority": priority,
		"customer_label": manifest.get("customer_party_label") or "Customer",
		"kpi_focus": kpi_focus,
		"report_profiles": report_profiles,
		"branch_names": branch_names,
		"department_names": department_names,
		"manifest": manifest,
	}


def _build_template_card(template_doc):
	profile = _estimate_template_profile(template_doc)
	manifest = profile["manifest"]
	return {
		"name": template_doc.name,
		"template_name": template_doc.template_name,
		"industry": template_doc.industry,
		"version": template_doc.version,
		"provider": template_doc.provider,
		"description": template_doc.description,
		"is_standard": bool(template_doc.is_standard),
		"is_active": bool(template_doc.is_active),
		"summary_html": template_doc.template_summary or "",
		"metrics": profile["metrics"],
		"total_estimated_records": profile["total_estimated_records"],
		"scale": profile["scale"],
		"priority": profile["priority"],
		"customer_label": profile["customer_label"],
		"kpi_focus": profile["kpi_focus"],
		"report_profiles": profile["report_profiles"],
		"branch_names": profile["branch_names"],
		"department_names": profile["department_names"],
		"manifest": manifest,
		"tags": [
			template_doc.industry,
			profile["scale"],
			"مقترح" if template_doc.is_standard else "جاهز",
		],
	}


def _load_template_cards():
	templates = frappe.get_all(
		"Demo Template",
		filters={"status": "Active", "is_active": 1},
		fields=["name", "template_name", "industry", "version", "provider", "description", "is_standard", "is_active", "template_summary", "template_manifest"],
		order_by="is_standard desc, modified desc, template_name asc",
	)

	if not templates:
		ensure_annual_demo_templates()
		templates = frappe.get_all(
			"Demo Template",
			filters={"status": "Active", "is_active": 1},
			fields=["name", "template_name", "industry", "version", "provider", "description", "is_standard", "is_active", "template_summary", "template_manifest"],
			order_by="is_standard desc, modified desc, template_name asc",
		)

	cards = [_build_template_card(frappe.get_doc("Demo Template", row.name)) for row in templates]
	return cards


def _build_wizard_payload():
	templates = _load_template_cards()
	industries = []
	for template in templates:
		if template["industry"] and template["industry"] not in industries:
			industries.append(template["industry"])

	providers = frappe.get_all(
		"Demo Provider",
		filters={"is_active": 1, "status": "Active"},
		fields=["name", "provider_name", "provider_type", "description"],
		order_by="provider_name asc",
	)

	recommended = next((t for t in templates if t["is_standard"]), templates[0] if templates else None)
	stats = {
		"templates": len(templates),
		"industries": len(industries),
		"providers": len(providers),
		"ready_to_launch": bool(templates),
	}

	return {
		"title": _("Demo Deployment Wizard"),
		"templates": templates,
		"industries": industries,
		"providers": providers,
		"recommended_template": recommended,
		"stats": stats,
		"defaults": {
			"demo_name": _("Live Demo"),
			"company_name": _("Live Demo Company"),
			"language": "ar",
		},
		"steps": [
			{"key": "template", "title": _("1. اختر القالب"), "description": _("اختر ديمو جاهز حسب النشاط والحجم")},
			{"key": "details", "title": _("2. البيانات الأساسية"), "description": _("اسم الديمو، اسم الشركة، واللغة")},
			{"key": "review", "title": _("3. المراجعة والتشغيل"), "description": _("راجع الملخص ثم ابدأ النشر")},
		],
	}


def get_context(context):
	"""Server-side context for the demo wizard page."""
	wizard_payload = _build_wizard_payload()
	context.title = wizard_payload["title"]
	context.wizard_payload = wizard_payload
	context.no_cache = 1
	context.show_sidebar = False
	return context


@frappe.whitelist()
def get_template_details(template_name):
	"""Return an enriched template snapshot for the selected template."""
	template = frappe.get_doc("Demo Template", template_name)
	return _build_template_card(template)


@frappe.whitelist()
def start_demo_generation(demo_data):
	"""Create a demo environment and enqueue the generator."""
	try:
		if isinstance(demo_data, str):
			demo_info = json.loads(demo_data)
		else:
			demo_info = frappe.parse_json(demo_data) if demo_data else {}

		template_name = demo_info.get("template")
		if not template_name:
			frappe.throw(_("Please choose a demo template first."))

		template = frappe.get_doc("Demo Template", template_name)
		if template.status != "Active" or not template.is_active:
			frappe.throw(_("Selected template is not active."))

		demo_name = (demo_info.get("demo_name") or template.template_name or _("Live Demo")).strip()
		company_name = (demo_info.get("company_name") or demo_name or template.template_name or _("Live Demo Company")).strip()
		language = (demo_info.get("language") or "ar").strip()

		demo = frappe.new_doc("Demo Environment")
		demo.demo_name = demo_name
		demo.template = template.name
		demo.industry = template.industry
		demo.company_name = company_name
		demo.language = language
		demo.status = "Generating"
		demo.is_demo = 1
		demo.health_status = "Warning"
		demo.generation_log = json.dumps(
			{
				"template": template.template_name,
				"industry": template.industry,
				"launch_mode": demo_info.get("launch_mode", "guided"),
				"source": "demo_wizard",
			},
			ensure_ascii=False,
			indent=2,
		)
		demo.save(ignore_permissions=True)

		frappe.enqueue(
			"erpgenex_demo_studio.demo_studio.generators.demo_generator.generate_demo_environment",
			demo_name=demo.name,
			queue="long",
			now=False,
		)

		return {
			"success": True,
			"demo_name": demo.name,
			"demo_id": demo.demo_id,
			"template": template.template_name,
			"status": demo.status,
			"redirect_url": f"/app/demo-environment/{demo.name}",
			"message": _("تم بدء إنشاء الديمو بنجاح"),
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), _("Demo Wizard Error"))
		return {
			"success": False,
			"error": str(e),
		}


@frappe.whitelist()
def get_demo_progress(demo_name):
	"""Get the current progress for a demo environment."""
	try:
		demo = frappe.get_doc("Demo Environment", demo_name)
		job_rows = frappe.get_all(
			"Demo Generation Job",
			filters={"demo_environment": demo.name},
			fields=["name", "job_name", "status", "progress", "current_step", "total_steps", "error_message", "job_log"],
			order_by="modified desc",
			limit=1,
		)
		job = frappe.get_doc("Demo Generation Job", job_rows[0]["name"]) if job_rows else None

		if job:
			progress = _safe_int(job.progress)
			if job.status == "Running" and not progress:
				total_steps = _safe_int(job.total_steps, 1)
				current_step = _safe_int(job.current_step)
				progress = int((current_step / total_steps) * 100) if total_steps else 35

			if job.status == "Completed":
				progress = 100
				status_message = _("تم إنشاء الديمو بنجاح")
			elif job.status == "Failed":
				progress = max(progress, 0)
				status_message = job.error_message or _("حدث خطأ أثناء النشر")
			elif demo.status == "Generating":
				status_message = _("جاري تجهيز الشركة والبيانات...")
			else:
				status_message = _("جاري النشر...")
		else:
			progress = 100 if demo.status == "Ready" else 0
			status_message = _("تم إنشاء الديمو بنجاح") if demo.status == "Ready" else _("جاري التحضير...")

		recent_events = []
		if job and job.job_log:
			try:
				recent_events = json.loads(job.job_log)[-5:]
			except Exception:
				recent_events = []

		return {
			"progress": progress,
			"status": demo.status,
			"message": status_message,
			"demo_id": demo.demo_id,
			"demo_name": demo.demo_name,
			"company_name": demo.company_name,
			"template": demo.template,
			"industry": demo.industry,
			"job": {
				"name": job.name if job else None,
				"status": job.status if job else None,
				"current_step": job.current_step if job else None,
				"total_steps": job.total_steps if job else None,
				"error_message": job.error_message if job else None,
			},
			"recent_events": recent_events,
			"redirect_url": f"/app/demo-environment/{demo.name}" if demo.status == "Ready" else None,
		}
	except Exception as e:
		return {
			"progress": 0,
			"status": "Error",
			"message": str(e),
		}
