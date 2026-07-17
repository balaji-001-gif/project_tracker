import frappe
from frappe.tests.utils import FrappeTestCase


class TestProjectUpdate(FrappeTestCase):
    def setUp(self):
        if not frappe.db.exists("Project", "_TEST_PROJECT"):
            project = frappe.get_doc({
                "doctype": "Project",
                "project_name": "_TEST_PROJECT",
                "status": "Open",
            })
            project.insert(ignore_permissions=True)

    def test_create_update(self):
        update = frappe.get_doc({
            "doctype": "Project Update",
            "project": "_TEST_PROJECT",
            "team_member": "Administrator",
            "update_date": frappe.utils.today(),
            "work_done_today": "Implemented test cases",
            "progress_percentage": 50,
        })
        update.flags.ignore_duplicate_check = True
        update.insert(ignore_permissions=True)
        self.assertEqual(update.workflow_state, "Draft")
        self.assertEqual(update.status, "Draft")

    def tearDown(self):
        frappe.db.delete("Project Update", {"project": "_TEST_PROJECT"})
        frappe.db.delete("Project", {"name": "_TEST_PROJECT"})
