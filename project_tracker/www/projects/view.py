import frappe
from frappe import _

def get_context(context):
    project_name = frappe.form_dict.get("name") or frappe.form_dict.get("project")
    if not project_name:
        frappe.throw(_("Project name required"))

    context.is_team_member = frappe.has_role("Project Team Member")
    context.is_project_manager = frappe.has_role("Project Manager")
    context.is_l1_approver = frappe.has_role("Project Approver L1")
    context.is_l2_approver = frappe.has_role("Project Approver L2")
    context.is_project_viewer = frappe.has_role("Project Viewer")

    from project_tracker.utils import get_pending_approvals_count
    context.pending_count = get_pending_approvals_count()

    context.project = frappe.call("project_tracker.api.project_api.get_project_detail", project=project_name)
    context.title = context.project.get("project_name", "Project Detail")
    context.can_update = context.is_team_member or context.is_project_manager
    context.is_completed = context.project.get("status") == "Completed"
    return context
