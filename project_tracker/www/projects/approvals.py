import frappe
from frappe import _

def get_context(context):
    if not frappe.has_role(["Project Approver L1", "Project Approver L2", "Project Manager"]):
        frappe.throw(_("Only approvers can view approvals."), frappe.PermissionError)

    context.is_l1_approver = frappe.has_role("Project Approver L1")
    context.is_l2_approver = frappe.has_role("Project Approver L2")
    context.is_project_manager = frappe.has_role("Project Manager")
    context.is_team_member = frappe.has_role("Project Team Member")

    from project_tracker.utils import get_pending_approvals_count
    context.pending_count = get_pending_approvals_count()

    context.l1_pending = []
    context.l2_pending = []

    if context.is_l1_approver or context.is_project_manager:
        context.l1_pending = frappe.get_all("Project Update",
            filters={"workflow_state": "Pending L1 Approval", "docstatus": 0},
            fields=["name", "project_name", "team_member_name", "update_date",
                    "overall_status", "progress_percentage", "blocker_severity",
                    "needs_attention", "work_done_today", "blockers"],
            order_by="needs_attention desc, update_date asc"
        )

    if context.is_l2_approver or context.is_project_manager:
        context.l2_pending = frappe.get_all("Project Update",
            filters={"workflow_state": "Pending L2 Approval", "docstatus": 0},
            fields=["name", "project_name", "team_member_name", "update_date",
                    "overall_status", "progress_percentage", "blocker_severity",
                    "needs_attention", "work_done_today", "blockers", "l1_approver"],
            order_by="needs_attention desc, update_date asc"
        )

    context.title = "Approvals"
    return context
