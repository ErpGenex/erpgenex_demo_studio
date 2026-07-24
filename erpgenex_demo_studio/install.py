from __future__ import annotations

import json
import os

import frappe
from frappe import _

from erpgenex_demo_studio.demo_studio.setup.demo_templates import ensure_annual_demo_templates


def before_install():
	"""Before installation hook"""
	pass


def after_install():
	"""After installation hook - create initial setup"""
	create_demo_studio_module()
	create_demo_studio_role()
	create_demo_studio_workspace()
	ensure_annual_demo_templates()


def create_demo_studio_module():
	"""Create Demo Studio module"""
	if not frappe.db.exists("Module Def", "Demo Studio"):
		frappe.get_doc({
			"doctype": "Module Def",
			"module_name": "Demo Studio",
			"app_name": "erpgenex_demo_studio",
			"custom": 0,
		}).insert()
		frappe.db.commit()


def create_demo_studio_role():
	"""Create Demo Studio Manager role"""
	if not frappe.db.exists("Role", "Demo Studio Manager"):
		frappe.get_doc({
			"doctype": "Role",
			"role_name": "Demo Studio Manager",
			"desk_access": 1,
			"is_standard": 1,
			"description": _("Manager role for ERPGenex Demo Studio - can create and manage demo environments"),
		}).insert()
		frappe.db.commit()


def _workspace_json_path() -> str:
	return os.path.join(
		frappe.get_app_path("erpgenex_demo_studio"),
		"demo_studio",
		"workspace",
		"demo_studio",
		"demo_studio.json",
	)


def _load_workspace_data() -> dict | None:
	path = _workspace_json_path()
	if not os.path.isfile(path):
		frappe.log_error(
			f"Demo Studio workspace file not found at {path}",
			"ERPGenex Demo Studio Install",
		)
		return None

	with open(path, encoding="utf-8") as workspace_file:
		return json.load(workspace_file)


def _strip_workspace_meta(data: dict) -> dict:
	# Only keep fields that are actual workspace data, not DocType definition
	workspace_fields = {
		"name", "label", "title", "module", "icon", "is_standard", "public",
		"links", "shortcuts", "charts", "cards", "quick_lists", "number_cards",
		"custom_blocks", "onboarding", "extends", "restrict_to_domain",
		"hide_links", "app", "disable_user_customization", "include_in_global_search",
		"description", "indicator_color", "category"
	}
	return {key: value for key, value in data.items() if key in workspace_fields}


def _replace_child_rows(doc, fieldname: str, rows: list[dict] | None):
	doc.set(fieldname, [])
	for row in rows or []:
		doc.append(fieldname, row)


def create_demo_studio_workspace():
	"""Create or update the Demo Studio workspace from the standard JSON file."""
	workspace_data = _load_workspace_data()
	if not workspace_data:
		return

	workspace_data = _strip_workspace_meta(workspace_data)
	workspace_name = workspace_data.get("name") or workspace_data.get("label") or "Demo Studio"
	workspace_data["name"] = workspace_name

	if frappe.db.exists("Workspace", workspace_name):
		workspace = frappe.get_doc("Workspace", workspace_name)
		workspace.update({k: v for k, v in workspace_data.items() if k not in {"links", "shortcuts", "charts", "cards", "quick_lists", "number_cards", "custom_blocks"}})
		_replace_child_rows(workspace, "links", workspace_data.get("links"))
		_replace_child_rows(workspace, "shortcuts", workspace_data.get("shortcuts"))
		_replace_child_rows(workspace, "charts", workspace_data.get("charts"))
		_replace_child_rows(workspace, "cards", workspace_data.get("cards"))
		_replace_child_rows(workspace, "quick_lists", workspace_data.get("quick_lists"))
		_replace_child_rows(workspace, "number_cards", workspace_data.get("number_cards"))
		_replace_child_rows(workspace, "custom_blocks", workspace_data.get("custom_blocks"))
		workspace.save(ignore_permissions=True)
	else:
		workspace = frappe.get_doc({"doctype": "Workspace", **workspace_data})
		workspace.insert(ignore_permissions=True)

	frappe.db.commit()
	frappe.clear_cache(doctype="Workspace")
