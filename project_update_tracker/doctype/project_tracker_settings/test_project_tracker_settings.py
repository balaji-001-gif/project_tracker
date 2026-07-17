import frappe
from frappe.tests.utils import FrappeTestCase


class TestProjectTrackerSettings(FrappeTestCase):
    def test_settings_exist(self):
        s = frappe.get_single("Project Tracker Settings")
        self.assertTrue(s.enable_daily_reminder)
