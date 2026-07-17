import frappe
from frappe import _

def get_context(context):
    context.no_cache = 0
    context.title = "Projects"

    # Role flags
    context.is_team_member = frappe.has_role("Project Team Member")
    context.is_project_manager = frappe.has_role("Project Manager")
    context.is_l1_approver = frappe.has_role("Project Approver L1")
    context.is_l2_approver = frappe.has_role("Project Approver L2")
    context.is_project_viewer = frappe.has_role("Project Viewer")

    from project_tracker.utils import get_pending_approvals_count
    context.pending_count = get_pending_approvals_count()

    # All projects
    context.projects = frappe.call("project_tracker.api.project_api.get_all_projects")

    # Role check
    if not (context.is_team_member or context.is_project_manager or
            context.is_l1_approver or context.is_l2_approver or context.is_project_viewer):
        frappe.throw(_("You don't have permission to view projects."), frappe.PermissionError)

    return context
