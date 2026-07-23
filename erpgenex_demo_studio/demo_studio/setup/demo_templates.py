from __future__ import annotations

import json

import frappe


DEFAULT_TEMPLATE_VERSION = "1.0.0"
BASE_SAMPLE_DATA_SEED = {
	"contacts": 48,
	"addresses": 32,
	"banks": 4,
	"accounts": 24,
	"cost_centers": 8,
	"profit_centers": 6,
	"projects": 12,
	"assets": 18,
	"warehouses": 3,
	"documents": 40,
	"reports": 6,
	"dashboards": 4,
}


INDUSTRY_TEMPLATE_CATALOG = [
	{
		"industry": "Education",
		"template_name": "Education - Annual Demo",
		"description": "Twelve-month education demo covering schools, students, staff, fees, and recurring academic operations.",
		"branch_count": 3,
		"employee_count": 85,
		"customer_count": 600,
		"supplier_count": 90,
		"transactions_per_month": 140,
		"business_activity": "Education",
		"industry_sector": "Education",
		"branch_names": ["Head Office", "Main Campus", "Admissions Center"],
		"department_names": [
			"Academic Affairs",
			"Admissions",
			"Student Services",
			"Finance",
			"HR",
			"IT",
			"Procurement",
		],
		"seasonality": "Academic year driven; peak enrollment before term start and fee collection at term boundaries.",
		"monthly_weights": [0.05, 0.06, 0.08, 0.09, 0.10, 0.11, 0.13, 0.11, 0.09, 0.08, 0.15, 0.05],
		"kpi_focus": ["Enrollment", "Attendance", "Fee Collection", "Pass Rate", "Staff Utilization"],
		"report_profiles": [
			"Admissions pipeline report",
			"Student attendance summary",
			"Fee collection aging",
			"Academic performance dashboard",
			"Staff workload report",
		],
		"sample_data_seed": {
			**BASE_SAMPLE_DATA_SEED,
			"employees": 85,
			"customers": 600,
			"suppliers": 90,
			"items": 140,
			"students": 600,
			"teachers": 48,
			"classes": 24,
		},
	},
	{
		"industry": "Healthcare",
		"template_name": "Healthcare - Annual Demo",
		"description": "Twelve-month healthcare demo covering clinics, patients, staff, billing, and recurring care workflows.",
		"branch_count": 4,
		"employee_count": 120,
		"customer_count": 900,
		"supplier_count": 140,
		"transactions_per_month": 180,
		"business_activity": "Healthcare",
		"industry_sector": "Healthcare",
		"branch_names": ["Head Office", "Outpatient Clinic", "Diagnostics Center", "Pharmacy Branch"],
		"department_names": [
			"Outpatient",
			"Inpatient",
			"Pharmacy",
			"Laboratory",
			"Billing",
			"Nursing",
			"Finance",
			"HR",
		],
		"seasonality": "Care activity is steady year-round with recurring appointments, pharmacy sales, and billing cycles.",
		"monthly_weights": [0.08, 0.08, 0.08, 0.08, 0.09, 0.09, 0.09, 0.09, 0.08, 0.09, 0.08, 0.08],
		"kpi_focus": ["Patient Volume", "Bed Occupancy", "Pharmacy Sales", "Revenue per Visit", "Wait Time"],
		"report_profiles": [
			"Patient census report",
			"Outpatient visit trend",
			"Pharmacy sales by branch",
			"Billing and collections aging",
			"Clinical utilization dashboard",
		],
		"sample_data_seed": {
			**BASE_SAMPLE_DATA_SEED,
			"employees": 120,
			"customers": 900,
			"suppliers": 140,
			"items": 180,
			"patients": 900,
			"appointments": 3600,
			"care_teams": 12,
		},
	},
	{
		"industry": "Manufacturing",
		"template_name": "Manufacturing - Annual Demo",
		"description": "Twelve-month manufacturing demo covering plants, inventory, production, procurement, and shop-floor operations.",
		"branch_count": 4,
		"employee_count": 150,
		"customer_count": 220,
		"supplier_count": 180,
		"transactions_per_month": 220,
		"business_activity": "Manufacturing",
		"industry_sector": "Manufacturing",
		"branch_names": ["Head Office", "Plant 1", "Plant 2", "Warehouse Hub"],
		"department_names": [
			"Production",
			"Planning",
			"Procurement",
			"Quality",
			"Maintenance",
			"Warehouse",
			"Finance",
		],
		"seasonality": "Production runs continuously with month-end planning, purchase ordering, and inventory close cycles.",
		"monthly_weights": [0.06, 0.07, 0.08, 0.08, 0.09, 0.10, 0.10, 0.09, 0.09, 0.09, 0.10, 0.05],
		"kpi_focus": ["OEE", "Yield", "Scrap Rate", "On-Time Completion", "Inventory Turnover"],
		"report_profiles": [
			"Production output summary",
			"Material consumption report",
			"Quality defects analysis",
			"Machine uptime dashboard",
			"Purchase variance report",
		],
		"sample_data_seed": {
			**BASE_SAMPLE_DATA_SEED,
			"employees": 150,
			"customers": 220,
			"suppliers": 180,
			"items": 220,
			"products": 180,
			"bom_variants": 42,
			"machines": 26,
		},
	},
	{
		"industry": "Trading and Distribution",
		"template_name": "Trading and Distribution - Annual Demo",
		"description": "Twelve-month trading and distribution demo covering warehouses, sales, purchases, logistics, and fulfillment.",
		"branch_count": 5,
		"employee_count": 95,
		"customer_count": 750,
		"supplier_count": 220,
		"transactions_per_month": 260,
		"business_activity": "Trading",
		"industry_sector": "Trading",
		"branch_names": ["Head Office", "Central Warehouse", "North Depot", "South Depot", "Sales Office"],
		"department_names": [
			"Sales",
			"Purchasing",
			"Logistics",
			"Warehouse",
			"Customer Service",
			"Finance",
		],
		"seasonality": "Trade flows are steady with promotional spikes and replenishment cycles across the year.",
		"monthly_weights": [0.07, 0.07, 0.08, 0.08, 0.09, 0.09, 0.11, 0.11, 0.08, 0.08, 0.09, 0.05],
		"kpi_focus": ["Order Fill Rate", "Gross Margin", "Inventory Turnover", "Delivery Cycle Time", "Customer Retention"],
		"report_profiles": [
			"Sales by channel report",
			"Stock turnover dashboard",
			"Backorder and fulfillment report",
			"Customer retention analysis",
			"Supplier lead time report",
		],
		"sample_data_seed": {
			**BASE_SAMPLE_DATA_SEED,
			"employees": 95,
			"customers": 750,
			"suppliers": 220,
			"items": 420,
			"products": 420,
			"warehouses": 4,
		},
	},
	{
		"industry": "Agriculture",
		"template_name": "Agriculture - Annual Demo",
		"description": "Twelve-month agriculture demo covering farms, seasonal activity, inputs, output, and supply tracking.",
		"branch_count": 3,
		"employee_count": 70,
		"customer_count": 260,
		"supplier_count": 110,
		"transactions_per_month": 130,
		"business_activity": "Agriculture",
		"industry_sector": "Agriculture",
		"branch_names": ["Head Office", "Farm Operations", "Collection Center"],
		"department_names": [
			"Farm Operations",
			"Irrigation",
			"Procurement",
			"Harvest",
			"Logistics",
			"Finance",
		],
		"seasonality": "Strong seasonal cycles around planting, irrigation, harvesting, and distribution windows.",
		"monthly_weights": [0.03, 0.04, 0.07, 0.08, 0.10, 0.12, 0.14, 0.13, 0.10, 0.08, 0.07, 0.04],
		"kpi_focus": ["Yield", "Water Use", "Harvest Volume", "Input Cost", "Distribution Loss"],
		"report_profiles": [
			"Crop yield report",
			"Irrigation usage dashboard",
			"Harvest planning report",
			"Input consumption summary",
			"Collection and dispatch analysis",
		],
		"sample_data_seed": {
			**BASE_SAMPLE_DATA_SEED,
			"employees": 70,
			"customers": 260,
			"suppliers": 110,
			"items": 130,
			"farms": 5,
			"crops": 14,
			"seasons": 4,
		},
	},
	{
		"industry": "Car Rental",
		"template_name": "Car Rental - Annual Demo",
		"description": "Twelve-month car rental demo covering fleet planning, bookings, contracts, invoicing, and maintenance.",
		"branch_count": 4,
		"employee_count": 60,
		"customer_count": 520,
		"supplier_count": 80,
		"transactions_per_month": 170,
		"business_activity": "Services",
		"industry_sector": "Services",
		"branch_names": ["Head Office", "Airport Counter", "City Branch", "Maintenance Yard"],
		"department_names": [
			"Reservations",
			"Fleet",
			"Maintenance",
			"Billing",
			"Customer Service",
			"Finance",
		],
		"seasonality": "Peak rentals during holidays, weekends, and travel-heavy months with ongoing fleet maintenance.",
		"monthly_weights": [0.09, 0.08, 0.08, 0.08, 0.09, 0.10, 0.11, 0.11, 0.08, 0.08, 0.06, 0.04],
		"kpi_focus": ["Fleet Utilization", "Booking Conversion", "Vehicle Downtime", "Revenue per Vehicle", "Late Returns"],
		"report_profiles": [
			"Fleet utilization dashboard",
			"Rental booking conversion",
			"Vehicle downtime report",
			"Contract expiry tracker",
			"Damage and claims log",
		],
		"sample_data_seed": {
			**BASE_SAMPLE_DATA_SEED,
			"employees": 60,
			"customers": 520,
			"suppliers": 80,
			"items": 140,
			"vehicles": 140,
			"rental_contracts": 520,
			"service_jobs": 240,
		},
	},
	{
		"industry": "Construction",
		"template_name": "Construction - Annual Demo",
		"description": "Twelve-month construction demo covering projects, sites, subcontractors, materials, and billing cycles.",
		"branch_count": 4,
		"employee_count": 110,
		"customer_count": 180,
		"supplier_count": 240,
		"transactions_per_month": 210,
		"business_activity": "Construction",
		"industry_sector": "Construction",
		"branch_names": ["Head Office", "Project Site A", "Project Site B", "Materials Yard"],
		"department_names": [
			"Projects",
			"Site Operations",
			"Procurement",
			"Estimating",
			"QS / Contracts",
			"Finance",
			"Logistics",
		],
		"seasonality": "Project-based operations with milestone billing, progress certification, and materials procurement cycles.",
		"monthly_weights": [0.06, 0.06, 0.08, 0.09, 0.10, 0.10, 0.10, 0.09, 0.09, 0.09, 0.09, 0.05],
		"kpi_focus": ["Progress Billing", "Project Margin", "Material Variance", "Site Productivity", "Change Order Cycle"],
		"report_profiles": [
			"Project progress summary",
			"Milestone billing report",
			"Subcontractor performance tracker",
			"Material variance analysis",
			"Project margin dashboard",
		],
		"sample_data_seed": {
			**BASE_SAMPLE_DATA_SEED,
			"employees": 110,
			"customers": 180,
			"suppliers": 240,
			"items": 210,
			"projects": 18,
			"sites": 6,
			"subcontractors": 32,
		},
	},
	{
		"industry": "Engineering Consulting",
		"template_name": "Engineering Consulting - Annual Demo",
		"description": "Twelve-month engineering consulting demo covering projects, engagements, milestones, billing, and delivery.",
		"branch_count": 3,
		"employee_count": 75,
		"customer_count": 260,
		"supplier_count": 60,
		"transactions_per_month": 120,
		"business_activity": "Engineering Consulting",
		"industry_sector": "Engineering Consulting",
		"branch_names": ["Head Office", "Design Studio", "Project Delivery Office"],
		"department_names": [
			"Design",
			"Project Management",
			"Business Development",
			"Finance",
			"HR",
			"Quality",
		],
		"seasonality": "Consulting engagements run on proposals, milestones, change requests, and delivery acceptance cycles.",
		"monthly_weights": [0.07, 0.07, 0.08, 0.08, 0.09, 0.10, 0.10, 0.09, 0.08, 0.08, 0.08, 0.08],
		"kpi_focus": ["Utilization", "Billable Hours", "Proposal Win Rate", "Delivery Margin", "Client Satisfaction"],
		"report_profiles": [
			"Billable utilization dashboard",
			"Proposal pipeline report",
			"Project delivery milestones",
			"Consultant timesheet summary",
			"Client satisfaction tracker",
		],
		"sample_data_seed": {
			**BASE_SAMPLE_DATA_SEED,
			"employees": 75,
			"customers": 260,
			"suppliers": 60,
			"items": 120,
			"engagements": 24,
			"consultants": 28,
			"proposals": 40,
		},
	},
]


def _json(value: dict) -> str:
	return json.dumps(value, indent=2)


def _company_config(country: str = "United States", currency: str = "USD") -> dict:
	return {
		"create_company": True,
		"default_country": country,
		"default_currency": currency,
	}


def _branch_config(branch_count: int) -> dict:
	return {
		"create_branches": True,
		"branch_count": branch_count,
	}


def _employee_config(employee_count: int) -> dict:
	return {
		"create_employees": True,
		"employee_count": employee_count,
	}


def _customer_config(customer_count: int) -> dict:
	return {
		"create_customers": True,
		"customer_count": customer_count,
	}


def _supplier_config(supplier_count: int) -> dict:
	return {
		"create_suppliers": True,
		"supplier_count": supplier_count,
	}


def _transaction_config(months: int, transactions_per_month: int) -> dict:
	return {
		"create_transactions": True,
		"transaction_months": months,
		"transactions_per_month": transactions_per_month,
	}


def _ensure_industry(industry_name: str, description: str) -> None:
	if not frappe.db.exists("Industry", industry_name):
		frappe.get_doc(
			{
				"doctype": "Industry",
				"industry_name": industry_name,
				"description": description,
			}
		).insert(ignore_permissions=True)


def _template_payload(item: dict) -> dict:
	return {
		"doctype": "Demo Template",
		"template_name": item["template_name"],
		"version": DEFAULT_TEMPLATE_VERSION,
		"status": "Active",
		"industry": item["industry"],
		"description": item["description"],
		"is_standard": 1,
		"is_active": 1,
		"company_config": _json(
			{
				**_company_config(),
				"industry": item["industry"],
				"business_activity": item["business_activity"],
				"industry_sector": item["industry_sector"],
				"seasonality": item["seasonality"],
				"kpi_focus": item["kpi_focus"],
				"report_profiles": item["report_profiles"],
				"sample_data_seed": item["sample_data_seed"],
			}
		),
		"branch_config": _json(
			{
				**_branch_config(len(item["branch_names"])),
				"branch_names": item["branch_names"],
			}
		),
		"employee_config": _json(
			{
				**_employee_config(item["employee_count"]),
				"department_names": item["department_names"],
			}
		),
		"customer_config": _json(_customer_config(item["customer_count"])),
		"supplier_config": _json(_supplier_config(item["supplier_count"])),
		"transaction_config": _json(
			{
				**_transaction_config(12, item["transactions_per_month"]),
				"annual_cycle": True,
				"seasonality": item["seasonality"],
				"monthly_weights": item["monthly_weights"],
				"annual_transactions": item["transactions_per_month"] * 12,
			}
		),
		"business_rules": _json(
			{
				"annual_scope": True,
				"scope_months": 12,
				"industry": item["industry"],
				"business_activity": item["business_activity"],
				"operating_model": "Annual recurring operations with realistic transactional cadence.",
				"kpi_focus": item["kpi_focus"],
				"report_profiles": item["report_profiles"],
			}
		),
		"validation_rules": _json(
			{
				"require_company": True,
				"require_branches": True,
				"require_employees": True,
				"require_customers": True,
				"require_suppliers": True,
				"require_transactions": True,
				"min_activity_months": 12,
				"require_industry_match": True,
				"require_branch_profile": True,
				"require_department_profile": True,
			}
		),
	}


def ensure_annual_demo_templates() -> list[str]:
	created_templates: list[str] = []

	for item in INDUSTRY_TEMPLATE_CATALOG:
		_ensure_industry(item["industry"], item["description"])
		template_name = item["template_name"]
		template_data = _template_payload(item)
		update_data = dict(template_data)
		update_data.pop("doctype", None)

		if frappe.db.exists("Demo Template", template_name):
			doc = frappe.get_doc("Demo Template", template_name)
			doc.update(update_data)
			doc.save(ignore_permissions=True)
		else:
			frappe.get_doc(template_data).insert(ignore_permissions=True)
			created_templates.append(template_name)

	return created_templates
