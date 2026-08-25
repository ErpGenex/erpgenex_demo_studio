# Copyright (c) 2026, Omnexa
from frappe.tests.utils import FrappeTestCase


class TestWave5SessionScope(FrappeTestCase):
	def test_vertical_dashboard(self):
		from erpgenex_demo_studio.vertical_dashboard_api import get_vertical_dashboard

		out = get_vertical_dashboard()
		self.assertEqual(out.get("app"), "erpgenex_demo_studio")
		self.assertIn("uses_session_context", out)
