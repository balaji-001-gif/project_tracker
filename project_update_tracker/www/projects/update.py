import frappe
from frappe import _

def get_context(context):
    project_name = frappe.form_dict.get("name") or frappe.form_dict.get("project")
    if not project_name:
        frappe.throw(_("Project name required"))

    if not frappe.has_role(["Project Team Member", "Project Manager"]):
        frappe.throw(_("Only team members can add updates."), frappe.PermissionError)

    context.is_team_member = True
    context.is_project_manager = frappe.has_role("Project Manager")
    context.is_l1_approver = frappe.has_role("Project Approver L1")
    context.is_l2_approver = frappe.has_role("Project Approver L2")

    from project_update_tracker.utils import get_pending_approvals_count
    context.pending_count = get_pending_approvals_count()

    # Project info
    context.project = frappe.db.get_value(
        "Project", project_name,
        ["name", "project_name", "status", "expected_end_date", "percent_complete"],
        as_dict=True
    )
    if not context.project:
        frappe.throw(_("Project not found"))
    if context.project.status == "Completed":
        frappe.throw(_("Cannot add updates to a completed project."))

    context.title = f"Update: {context.project.project_name}"

    # Today's existing updates
    context.today_updates = frappe.get_all("Project Update",
        filters={"project": project_name, "team_member": frappe.session.user, "update_date": frappe.utils.today()},
        fields=["name", "workflow_state", "status", "work_done_today", "progress_percentage"]
    )

    return context
