from erpgenex_demo_studio.install import (
	create_demo_studio_module,
	create_demo_studio_role,
)


def execute():
	create_demo_studio_module()
	create_demo_studio_role()
	# Skip workspace creation in patch - it's handled by install hook
