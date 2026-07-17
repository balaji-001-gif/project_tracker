import frappe
from frappe import _

def get_context(context):
    name = frappe.form_dict.get("name") or frappe.form_dict.get("update")
    if not name:
        frappe.throw(_("Update name required"))

    context.update = frappe.call("project_tracker.api.project_api.get_update_detail", name=name)
    context.title = f"Review: {context.update.get('name')}"

    context.is_l1_approver = frappe.has_role("Project Approver L1")
    context.is_l2_approver = frappe.has_role("Project Approver L2")
    context.is_project_manager = frappe.has_role("Project Manager")
    context.is_team_member = frappe.has_role("Project Team Member")

    from project_tracker.utils import get_pending_approvals_count
    context.pending_count = get_pending_approvals_count()

    return context
