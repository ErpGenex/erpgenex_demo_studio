app_name = "erpgenex_demo_studio"
app_title = "ERPGenex Demo Studio"
app_publisher = "ErpGenEx"
app_description = "Enterprise Demo Lifecycle Management Platform for ERPGenex"
app_email = "dev@erpgenex.com"
app_license = "mit"

# Apps
# ------------------

required_apps = ["omnexa_core"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "erpgenex_demo_studio",
# 		"logo": "/assets/erpgenex_demo_studio/logo.png",
# 		"title": "Erpgenex Demo Studio",
# 		"route": "/erpgenex_demo_studio",
# 		"has_permission": "erpgenex_demo_studio.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/erpgenex_demo_studio/css/erpgenex_demo_studio.css"
# app_include_js = "/assets/erpgenex_demo_studio/js/erpgenex_demo_studio.js"

# include js, css files in header of web template
# web_include_css = "/assets/erpgenex_demo_studio/css/erpgenex_demo_studio.css"
# web_include_js = "/assets/erpgenex_demo_studio/js/erpgenex_demo_studio.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "erpgenex_demo_studio/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "erpgenex_demo_studio/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "erpgenex_demo_studio.utils.jinja_methods",
# 	"filters": "erpgenex_demo_studio.utils.jinja_filters"
# }

# Installation
# ------------

before_install = "erpgenex_demo_studio.install.before_install"
after_install = "erpgenex_demo_studio.install.after_install"

# Uninstallation
# ------------

before_uninstall = "erpgenex_demo_studio.uninstall.before_uninstall"
after_uninstall = "erpgenex_demo_studio.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "erpgenex_demo_studio.utils.before_app_install"
# after_app_install = "erpgenex_demo_studio.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "erpgenex_demo_studio.utils.before_app_uninstall"
# after_app_uninstall = "erpgenex_demo_studio.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "erpgenex_demo_studio.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"erpgenex_demo_studio.tasks.all"
# 	],
# 	"daily": [
# 		"erpgenex_demo_studio.tasks.daily"
# 	],
# 	"hourly": [
# 		"erpgenex_demo_studio.tasks.hourly"
# 	],
# 	"weekly": [
# 		"erpgenex_demo_studio.tasks.weekly"
# 	],
# 	"monthly": [
# 		"erpgenex_demo_studio.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "erpgenex_demo_studio.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "erpgenex_demo_studio.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "erpgenex_demo_studio.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["erpgenex_demo_studio.utils.before_request"]
# after_request = ["erpgenex_demo_studio.utils.after_request"]

# Job Events
# ----------
# before_job = ["erpgenex_demo_studio.utils.before_job"]
# after_job = ["erpgenex_demo_studio.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"erpgenex_demo_studio.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

# Fixtures
# ------------
fixtures = [
	{"dt": "Role", "filters": [["name", "in", ["Demo Studio Manager"]]]},
	{"dt": "Page", "filters": [["name", "=", "demo_wizard"]]},
]

# Whitelisted Methods
# ------------------
whitelisted_methods = [
	"erpgenex_demo_studio.api.demo_api.health_check",
	"erpgenex_demo_studio.api.demo_api.get_demo_statistics",
	"erpgenex_demo_studio.api.demo_api.get_demo_environments",
	"erpgenex_demo_studio.api.demo_api.get_demo_templates",
	"erpgenex_demo_studio.api.demo_api.validate_demo_environment",
	"erpgenex_demo_studio.api.demo_api.export_demo_environment",
	"erpgenex_demo_studio.api.demo_api.import_demo_environment",
	"erpgenex_demo_studio.api.demo_api.get_industries",
	"erpgenex_demo_studio.providers.provider_registry.refresh_provider_registry",
	"erpgenex_demo_studio.providers.provider_registry.get_available_providers",
	"erpgenex_demo_studio.utils.safety.check_demo_safety",
]
