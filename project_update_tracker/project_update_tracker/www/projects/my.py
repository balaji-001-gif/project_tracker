import frappe
from frappe import _

def get_context(context):
    context.title = "My Projects"

    if not frappe.has_role(["Project Team Member", "Project Manager"]):
        frappe.throw(_("Only team members can access My Projects."), frappe.PermissionError)

    context.is_team_member = True
    context.is_project_manager = frappe.has_role("Project Manager")
    context.is_l1_approver = frappe.has_role("Project Approver L1")
    context.is_l2_approver = frappe.has_role("Project Approver L2")

    from project_update_tracker.utils import get_pending_approvals_count
    context.pending_count = get_pending_approvals_count()

    context.projects = frappe.call("project_update_tracker.api.project_api.get_my_projects")
    return context
