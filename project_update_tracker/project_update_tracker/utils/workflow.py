import frappe
from frappe import _
from frappe.utils import now_datetime, today


def validate_project_update(doc, method=None):
    """Pre-validation hook."""
    if not doc.work_done_today or len(doc.work_done_today.strip()) < 10:
        frappe.throw(_("Please provide meaningful details in 'Work Done Today' (min 10 chars)."))


def after_insert_handler(doc, method=None):
    """Set initial state."""
    if not doc.workflow_state:
        doc.workflow_state = "Draft"
        doc.db_set("workflow_state", "Draft")


def before_submit_handler(doc, method=None):
    """Validate proper workflow state before submission."""
    valid_states = [
        "Pending L1 Approval",
        "Pending L2 Approval",
        "Approved",
        "Completed",
        "Rejected"
    ]
    if doc.workflow_state not in valid_states:
        frappe.throw(_("Document must be in a valid workflow state before submission. "
                       "Use the Submit for L1 Approval action."))


def on_update_handler(doc, method=None):
    """Trigger notifications based on workflow_state changes."""
    state = doc.workflow_state
    settings = frappe.get_single("Project Tracker Settings")

    from project_update_tracker.utils import notifications

    if state == "Pending L1 Approval" and settings.notify_on_submit:
        notifications.notify_l1_approvers(doc)

    elif state == "Pending L2 Approval" and settings.notify_on_l1_approval:
        notifications.notify_l2_approvers(doc)

    elif state == "Approved" and settings.notify_on_l2_approval:
        notifications.notify_team_member_approved(doc)

    elif state == "Rejected" and settings.notify_on_rejection:
        notifications.notify_team_member_rejected(doc)

    elif state == "Completed":
        doc.is_published = 1
        doc.db_set("is_published", 1)


def on_cancel_handler(doc, method=None):
    """Handle cancellation — revert state."""
    frappe.db.set_value("Project Update", doc.name, "workflow_state", "Rejected", update_modified=False)
