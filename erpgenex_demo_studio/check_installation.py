import frappe

def check_demo_studio_installation():
	"""Check Demo Studio installation status"""
	
	results = {}
	
	# Check workspace
	workspace_exists = frappe.db.exists('Workspace', 'Demo Studio')
	results['workspace'] = workspace_exists
	frappe.msgprint(f"Workspace exists: {workspace_exists}")
	
	if workspace_exists:
		workspace = frappe.get_doc('Workspace', 'Demo Studio')
		frappe.msgprint(f"Workspace - Name: {workspace.name}, Module: {workspace.module}, Public: {workspace.public}")
	
	# Check module
	module_exists = frappe.db.exists('Module Def', 'Demo Studio')
	results['module'] = module_exists
	frappe.msgprint(f"Module exists: {module_exists}")
	
	# Check DocTypes
	doctypes = ['Demo Environment', 'Demo Template', 'Demo Provider', 'Demo Generation Job']
	doctype_results = {}
	for doctype in doctypes:
		exists = frappe.db.exists('DocType', doctype)
		doctype_results[doctype] = exists
		frappe.msgprint(f"DocType {doctype}: {exists}")
	
	results['doctypes'] = doctype_results
	
	# Check role
	role_exists = frappe.db.exists('Role', 'Demo Studio Manager')
	results['role'] = role_exists
	frappe.msgprint(f"Role exists: {role_exists}")
	
	return results
