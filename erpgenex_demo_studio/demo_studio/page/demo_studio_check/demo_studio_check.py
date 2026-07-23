import frappe

def get_context(context):
	"""Check Demo Studio installation status"""
	
	context.check_results = {}
	
	# Check workspace
	workspace_exists = frappe.db.exists('Workspace', 'Demo Studio')
	context.check_results['workspace'] = {
		'exists': workspace_exists,
		'name': 'Demo Studio'
	}
	
	if workspace_exists:
		try:
			workspace = frappe.get_doc('Workspace', 'Demo Studio')
			context.check_results['workspace']['details'] = {
				'module': workspace.module,
				'public': workspace.public,
				'is_standard': workspace.is_standard
			}
		except Exception as e:
			context.check_results['workspace']['error'] = str(e)
	
	# Check module
	module_exists = frappe.db.exists('Module Def', 'Demo Studio')
	context.check_results['module'] = {
		'exists': module_exists,
		'name': 'Demo Studio'
	}
	
	if module_exists:
		try:
			module = frappe.get_doc('Module Def', 'Demo Studio')
			context.check_results['module']['details'] = {
				'module_name': module.module_name,
				'app_name': module.app_name
			}
		except Exception as e:
			context.check_results['module']['error'] = str(e)
	
	# Check DocTypes
	doctypes = ['Demo Environment', 'Demo Template', 'Demo Provider', 'Demo Generation Job']
	doctype_results = {}
	for doctype in doctypes:
		exists = frappe.db.exists('DocType', doctype)
		doctype_results[doctype] = {
			'exists': exists
		}
	
	context.check_results['doctypes'] = doctype_results
	
	# Check role
	role_exists = frappe.db.exists('Role', 'Demo Studio Manager')
	context.check_results['role'] = {
		'exists': role_exists,
		'name': 'Demo Studio Manager'
	}
	
	# Overall status
	all_good = (
		workspace_exists and 
		module_exists and 
		all(dt['exists'] for dt in doctype_results.values()) and 
		role_exists
	)
	
	context.check_results['overall_status'] = 'Success' if all_good else 'Partial'
	
	return context
