from __future__ import annotations

import json
import os
from html import escape
from pathlib import Path

import frappe
from frappe import _
from jinja2 import Environment, FileSystemLoader, select_autoescape

from erpgenex_demo_studio.demo_studio.setup.demo_templates import ensure_annual_demo_templates
from erpgenex_demo_studio.demo_studio.utils.party_labels import classify_party_context, resolve_customer_party_label


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


def _resolve_unique_demo_name(base_name: str) -> str:
	"""Return a demo_name that does not collide with an existing Demo Environment."""
	base_name = (base_name or _("Live Demo")).strip()
	if not frappe.db.exists("Demo Environment", base_name):
		return base_name
	for index in range(2, 100):
		candidate = f"{base_name} ({index})"
		if not frappe.db.exists("Demo Environment", candidate):
			return candidate
	return f"{base_name} {frappe.generate_hash(length=6)}"


def _resolve_unique_company_name(base_name: str) -> str:
	"""Return a company_name that does not collide with an existing Company."""
	base_name = (base_name or _("Live Demo Company")).strip()
	if not frappe.db.exists("Company", {"company_name": base_name}):
		return base_name
	for index in range(2, 100):
		candidate = f"{base_name} ({index})"
		if not frappe.db.exists("Company", {"company_name": candidate}):
			return candidate
	return f"{base_name} {frappe.generate_hash(length=6)}"


def _template_company_config(template_doc, manifest: dict) -> dict:
	company = manifest.get("company_config") if isinstance(manifest.get("company_config"), dict) else {}
	if not company and template_doc.get("company_config"):
		company = _parse_json(template_doc.company_config, {})
	return company


def _template_business_rules(template_doc, manifest: dict) -> dict:
	rules = manifest.get("business_rules") if isinstance(manifest.get("business_rules"), dict) else {}
	if not rules and template_doc.get("business_rules"):
		rules = _parse_json(template_doc.business_rules, {})
	return rules


def _resolve_template_customer_label(template_doc, manifest: dict, lang: str = "ar") -> str:
	company = _template_company_config(template_doc, manifest)
	rules = _template_business_rules(template_doc, manifest)
	return resolve_customer_party_label(
		business_activity=_first_non_empty(company.get("business_activity"), rules.get("business_activity")),
		industry_sector=_first_non_empty(company.get("industry_sector"), rules.get("industry_sector")),
		industry=_first_non_empty(template_doc.industry, manifest.get("industry")),
		lang=lang,
		plural=True,
	)


def _estimate_template_profile(template_doc, lang: str = "ar"):
	manifest = _parse_json(template_doc.template_manifest, {})
	company = _template_company_config(template_doc, manifest)
	branch = manifest.get("branch_config", {}) if isinstance(manifest.get("branch_config"), dict) else _parse_json(template_doc.branch_config, {})
	employee = manifest.get("employee_config", {}) if isinstance(manifest.get("employee_config"), dict) else _parse_json(template_doc.employee_config, {})
	customer = manifest.get("customer_config", {}) if isinstance(manifest.get("customer_config"), dict) else _parse_json(template_doc.customer_config, {})
	supplier = manifest.get("supplier_config", {}) if isinstance(manifest.get("supplier_config"), dict) else _parse_json(template_doc.supplier_config, {})
	transaction = manifest.get("transaction_config", {}) if isinstance(manifest.get("transaction_config"), dict) else _parse_json(template_doc.transaction_config, {})
	business_rules = _template_business_rules(template_doc, manifest)

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
		"assets": _safe_int(_first_non_empty(sample.get("assets"), default=0)),
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
	customer_label = _resolve_template_customer_label(template_doc, manifest, lang)
	party_context = classify_party_context(
		business_activity=_first_non_empty(company.get("business_activity"), business_rules.get("business_activity")),
		industry_sector=_first_non_empty(company.get("industry_sector"), business_rules.get("industry_sector")),
		industry=_first_non_empty(template_doc.industry, manifest.get("industry")),
	)
	return {
		"metrics": metrics,
		"total_estimated_records": total,
		"scale": scale,
		"priority": priority,
		"customer_label": customer_label,
		"party_context": party_context,
		"kpi_focus": kpi_focus,
		"report_profiles": report_profiles,
		"branch_names": branch_names,
		"department_names": department_names,
		"manifest": manifest,
	}


def _build_template_card(template_doc, lang: str = "ar"):
	profile = _estimate_template_profile(template_doc, lang)
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
		"summary_html": getattr(template_doc, "template_summary", None) or "",
		"metrics": profile["metrics"],
		"total_estimated_records": profile["total_estimated_records"],
		"scale": profile["scale"],
		"priority": profile["priority"],
		"customer_label": profile["customer_label"],
		"party_context": profile["party_context"],
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


def _load_template_cards(lang: str = "ar"):
	list_fields = [
		"name",
		"template_name",
		"industry",
		"version",
		"provider",
		"description",
		"is_standard",
		"is_active",
		"template_manifest",
	]

	templates = frappe.get_all(
		"Demo Template",
		filters={"status": "Active", "is_active": 1},
		fields=list_fields,
		order_by="is_standard desc, modified desc, template_name asc",
	)

	if not templates:
		ensure_annual_demo_templates()
		templates = frappe.get_all(
			"Demo Template",
			filters={"status": "Active", "is_active": 1},
			fields=list_fields,
			order_by="is_standard desc, modified desc, template_name asc",
		)

	cards = [_build_template_card(frappe.get_doc("Demo Template", row.name), lang) for row in templates]
	return cards


def _site_activity_context() -> dict:
	"""Align wizard defaults with the site's company business activity when possible."""
	activity = "General"
	industry_hint = ""
	try:
		from omnexa_core.omnexa_core.app_visibility import get_user_company_activity

		activity = get_user_company_activity() or "General"
	except Exception:
		pass

	# Map company activity → Demo Template industry labels (catalog uses industry field).
	activity_to_industry = {
		"Healthcare": "Healthcare",
		"Education": "Education",
		"Construction": "Construction",
		"Engineering Consulting": "Engineering Consulting",
		"Financial Services": "Financial Services",
		"Trading": "Trading",
		"Manufacturing": "Manufacturing",
		"Agriculture": "Agriculture",
		"Tourism": "Tourism",
		"Hotel Assets": "Hotel Assets",
		"Bakeries": "Restaurant",
		"Services": "Services",
		"Legal": "Legal",
		"Statutory Audit": "Statutory Audit",
	}
	industry_hint = activity_to_industry.get(activity, "")
	return {"company_activity": activity, "suggested_industry": industry_hint}


def _pick_recommended_template(templates: list[dict], site_ctx: dict) -> dict | None:
	if not templates:
		return None
	industry_hint = (site_ctx or {}).get("suggested_industry") or ""
	if industry_hint:
		for template in templates:
			if template.get("industry") == industry_hint and template.get("is_standard"):
				return template
		for template in templates:
			if template.get("industry") == industry_hint:
				return template
	return next((t for t in templates if t.get("is_standard")), templates[0])


def _build_wizard_payload(lang: str = "ar"):
	templates = _load_template_cards(lang)
	site_ctx = _site_activity_context()
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

	recommended = _pick_recommended_template(templates, site_ctx)
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
		"site_context": site_ctx,
		"stats": stats,
		"defaults": {
			"demo_name": _("Live Demo"),
			"company_name": _("Live Demo Company"),
			"language": lang,
		},
		"steps": [
			{"key": "template", "title": _("1. اختر القالب"), "description": _("اختر ديمو جاهز حسب النشاط والحجم")},
			{"key": "details", "title": _("2. البيانات الأساسية"), "description": _("اسم الديمو، اسم الشركة، واللغة")},
			{"key": "review", "title": _("3. المراجعة والتشغيل"), "description": _("راجع الملخص ثم ابدأ النشر")},
		],
	}


def get_context(context):
	"""Server-side context for the demo wizard page."""
	context.title = "Demo Deployment Wizard"
	context.no_cache = 1
	context.show_sidebar = False
	return context


@frappe.whitelist()
def get_rendered_page_html():
	"""Return the rendered wizard HTML for Desk mounting."""
	templates_dir = Path(frappe.get_app_path("erpgenex_demo_studio", "demo_studio", "templates"))
	env = Environment(
		loader=FileSystemLoader(str(templates_dir)),
		autoescape=select_autoescape(["html", "xml"]),
	)
	template = env.get_template("demo_wizard_desk.html")
	return template.render(wizard_payload=_build_wizard_payload())


@frappe.whitelist()
def get_wizard_payload(lang: str = "ar"):
	"""Return the wizard payload as JSON for client-side initialization."""
	return _build_wizard_payload(lang or "ar")


@frappe.whitelist()
def get_template_details(template_name, lang: str = "ar"):
	"""Return an enriched template snapshot for the selected template."""
	template = frappe.get_doc("Demo Template", template_name)
	return _build_template_card(template, lang or "ar")


@frappe.whitelist()
def quick_register_demo(template: str | None = None, language: str = "ar"):
	"""One-shot demo registration: recommended or chosen template + auto unique names."""
	site_ctx = _site_activity_context()
	templates = _load_template_cards(language or "ar")
	if not templates:
		frappe.throw(_("No demo templates are available. Sync templates first."))

	chosen = None
	if template:
		chosen = next((t for t in templates if t["name"] == template), None)
		if not chosen:
			frappe.throw(_("Unknown demo template."))
	else:
		chosen = _pick_recommended_template(templates, site_ctx)
	if not chosen:
		frappe.throw(_("No demo template could be selected."))

	demo_name = _resolve_unique_demo_name(suggest_demo_name(chosen["template_name"]))
	company_name = _resolve_unique_company_name(suggest_company_name(chosen["template_name"]))
	payload = {
		"template": chosen["name"],
		"demo_name": demo_name,
		"company_name": company_name,
		"language": (language or "ar").strip(),
		"launch_mode": "guided",
	}
	return start_demo_generation(json.dumps(payload))


def suggest_demo_name(template_title: str) -> str:
	from frappe.utils import now_datetime

	stamp = now_datetime().strftime("%Y-%m-%d %H:%M")
	return f"{template_title} — {stamp}"


def suggest_company_name(template_title: str) -> str:
	from frappe.utils import today

	stamp = today()
	return f"{template_title} Company — {stamp}"


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

		demo_name = _resolve_unique_demo_name(
			(demo_info.get("demo_name") or template.template_name or _("Live Demo")).strip()
		)
		company_name = _resolve_unique_company_name(
			(demo_info.get("company_name") or demo_name or template.template_name or _("Live Demo Company")).strip()
		)
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

		# Run inline so the wizard shows progress without requiring a background worker.
		run_now = True

		frappe.enqueue(
			"erpgenex_demo_studio.demo_studio.generators.demo_generator.generate_demo_environment",
			demo_name=demo.name,
			queue="long",
			now=run_now,
		)

		demo.reload()
		is_ready = demo.status == "Ready"
		return {
			"success": True,
			"demo_name": demo.name,
			"demo_id": demo.demo_id,
			"template": template.template_name,
			"status": demo.status,
			"redirect_url": f"/app/demo-environment/{demo.name}" if is_ready else None,
			"message": _("تم إنشاء الديمو بنجاح") if is_ready else _("تم بدء إنشاء الديمو بنجاح"),
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

		if job and not recent_events and getattr(job, "generation_steps", None):
			status_map = {
				"Pending": _("قيد الانتظار"),
				"Running": _("جاري التنفيذ"),
				"Completed": _("مكتمل"),
				"Failed": _("فشل"),
				"Skipped": _("تم التخطي"),
			}
			recent_events = [
				{
					"step": step.step_name,
					"status": status_map.get(step.status, step.status),
				}
				for step in job.generation_steps
			]

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
