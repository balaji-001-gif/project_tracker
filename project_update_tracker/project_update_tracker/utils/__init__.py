import frappe
from frappe import _


def boot_session(session):
    """Add custom session data for website."""
    session["project_tracker_roles"] = {
        "is_team_member": frappe.has_role("Project Team Member"),
        "is_l1_approver": frappe.has_role("Project Approver L1"),
        "is_l2_approver": frappe.has_role("Project Approver L2"),
        "is_project_manager": frappe.has_role("Project Manager"),
        "is_project_viewer": frappe.has_role("Project Viewer"),
    }
    return session


def jinja_methods():
    return {
        "has_project_role": lambda role: frappe.has_role(role),
        "get_pending_approvals_count": get_pending_approvals_count,
    }


def get_pending_approvals_count():
    """Returns count of pending approvals for current user."""
    user = frappe.session.user
    count = 0
    if frappe.has_role("Project Approver L1"):
        count += frappe.db.count("Project Update", {
            "workflow_state": "Pending L1 Approval",
            "docstatus": 0,
        })
    if frappe.has_role("Project Approver L2"):
        count += frappe.db.count("Project Update", {
            "workflow_state": "Pending L2 Approval",
            "docstatus": 0,
        })
    return count
