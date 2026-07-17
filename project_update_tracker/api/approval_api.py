import frappe
from frappe import _
from frappe.utils import now_datetime


def _check_role_for_state(state):
    user = frappe.session.user
    if user == "Administrator" or frappe.has_role("System Manager"):
        return True
    if frappe.has_role("Project Manager"):
        return True
    if state == "Pending L1 Approval" and frappe.has_role("Project Approver L1"):
        return True
    if state == "Pending L2 Approval" and frappe.has_role("Project Approver L2"):
        return True
    return False


@frappe.whitelist()
def submit_for_l1(name):
    """Team member submits update for L1 approval."""
    doc = frappe.get_doc("Project Update", name)
    if doc.team_member != frappe.session.user and not frappe.has_role("Project Manager"):
        frappe.throw(_("Only the team member can submit this update."), frappe.PermissionError)
    if doc.workflow_state != "Draft":
        frappe.throw(_("Update must be in Draft state to submit."))

    doc.workflow_state = "Pending L1 Approval"
    doc.status = "Pending L1 Approval"
    doc.save(ignore_permissions=False)
    # Apply workflow transition
    _apply_workflow_action(doc, "Submit for L1")
    return {"ok": True, "state": doc.workflow_state}


@frappe.whitelist()
def approve_l1(name, comments=""):
    """L1 approver approves."""
    doc = frappe.get_doc("Project Update", name)
    if not _check_role_for_state(doc.workflow_state):
        frappe.throw(_("You don't have permission to approve at L1."), frappe.PermissionError)
    if doc.workflow_state != "Pending L1 Approval":
        frappe.throw(_("Update is not pending L1 approval."))

    doc.l1_approver = frappe.session.user
    doc.l1_approved_on = now_datetime()
    doc.l1_comments = comments
    doc.workflow_state = "Pending L2 Approval"
    doc.status = "Pending L2 Approval"
    doc.save(ignore_permissions=False)
    _apply_workflow_action(doc, "Approve")
    return {"ok": True, "state": doc.workflow_state}


@frappe.whitelist()
def approve_l2(name, comments=""):
    """L2 approver approves."""
    doc = frappe.get_doc("Project Update", name)
    if not _check_role_for_state(doc.workflow_state):
        frappe.throw(_("You don't have permission to approve at L2."), frappe.PermissionError)
    if doc.workflow_state != "Pending L2 Approval":
        frappe.throw(_("Update is not pending L2 approval."))

    doc.l2_approver = frappe.session.user
    doc.l2_approved_on = now_datetime()
    doc.l2_comments = comments
    doc.workflow_state = "Approved"
    doc.status = "Approved"
    doc.save(ignore_permissions=False)
    _apply_workflow_action(doc, "Approve")

    # Auto-publish
    settings = frappe.get_single("Project Tracker Settings")
    if settings.enable_auto_publish:
        publish_update(name)
    return {"ok": True, "state": doc.workflow_state}


@frappe.whitelist()
def reject_update(name, reason, level="L1"):
    """Reject the update at current level."""
    doc = frappe.get_doc("Project Update", name)
    if not _check_role_for_state(doc.workflow_state):
        frappe.throw(_("You don't have permission to reject."), frappe.PermissionError)

    doc.rejection_reason = reason
    doc.workflow_state = "Rejected"
    doc.status = "Rejected"
    if level == "L1":
        doc.l1_approver = frappe.session.user
        doc.l1_approved_on = now_datetime()
        doc.l1_comments = f"REJECTED: {reason}"
    else:
        doc.l2_approver = frappe.session.user
        doc.l2_approved_on = now_datetime()
        doc.l2_comments = f"REJECTED: {reason}"
    doc.save(ignore_permissions=False)
    _apply_workflow_action(doc, "Reject")
    return {"ok": True, "state": doc.workflow_state}


@frappe.whitelist()
def resubmit_update(name):
    """Team member resubmits a rejected update."""
    doc = frappe.get_doc("Project Update", name)
    settings = frappe.get_single("Project Tracker Settings")
    if not settings.allow_resubmission:
        frappe.throw(_("Resubmission is disabled."))
    if doc.team_member != frappe.session.user and not frappe.has_role("Project Manager"):
        frappe.throw(_("Only the team member can resubmit."), frappe.PermissionError)
    if doc.workflow_state != "Rejected":
        frappe.throw(_("Only rejected updates can be resubmitted."))

    doc.workflow_state = "Pending L1 Approval"
    doc.status = "Pending L1 Approval"
    doc.rejection_reason = ""
    doc.save(ignore_permissions=False)
    _apply_workflow_action(doc, "Resubmit")
    return {"ok": True, "state": doc.workflow_state}


@frappe.whitelist()
def publish_update(name):
    """Make the update published (view-only for others)."""
    doc = frappe.get_doc("Project Update", name)
    if not frappe.has_role(["Project Manager", "System Manager"]):
        frappe.throw(_("Only Project Manager can publish."), frappe.PermissionError)
    if doc.workflow_state not in ["Approved", "Completed"]:
        frappe.throw(_("Update must be Approved to publish."))

    doc.is_published = 1
    doc.db_set("is_published", 1)
    return {"ok": True}


@frappe.whitelist()
def mark_completed(name):
    """Project Manager marks update as Completed (publishes project)."""
    doc = frappe.get_doc("Project Update", name)
    if not frappe.has_role(["Project Manager", "System Manager"]):
        frappe.throw(_("Only Project Manager can mark completed."), frappe.PermissionError)
    if doc.workflow_state != "Approved":
        frappe.throw(_("Update must be Approved first."))

    doc.workflow_state = "Completed"
    doc.status = "Completed"
    doc.is_published = 1
    doc.save(ignore_permissions=False)
    _apply_workflow_action(doc, "Mark Completed")
    return {"ok": True}


def _apply_workflow_action(doc, action):
    """Apply workflow action via Frappe's apply_workflow."""
    try:
        from frappe.model.workflow import apply_workflow
        # Reload to get current state
        fresh = frappe.get_doc(doc.doctype, doc.name)
        wf_name = frappe.db.get_value("Workflow", {"document_type": doc.doctype, "is_active": 1})
        if not wf_name:
            return
        # Find transition matching action
        transitions = frappe.get_all("Workflow Transition",
            filters={"parent": wf_name, "action": action, "state": fresh.workflow_state},
            fields=["next_state", "allowed"])
        if not transitions:
            return
        apply_workflow(fresh, action)
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Workflow action failed: {action}")
