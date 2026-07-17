import frappe
from frappe import _
from frappe.utils import cint


def has_permission(doc, ptype="read", user=None):
    """Custom has_permission for Project Update."""
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return True

    # System Manager can do everything
    if frappe.has_role("System Manager", user=user):
        return True

    # Project Manager can do everything
    if frappe.has_role("Project Manager", user=user):
        return True

    # Published updates — anyone with read role can read
    if ptype == "read" and doc.is_published:
        if frappe.has_role(["Project Viewer", "Project Team Member",
                            "Project Approver L1", "Project Approver L2"], user=user):
            return True

    # Team member can manage their own
    if frappe.has_role("Project Team Member", user=user):
        if doc.team_member == user:
            if ptype in ["read", "write", "create", "submit"]:
                return True
            if ptype == "delete" and doc.docstatus == 0:
                return True

    # L1 approver can act on Pending L1 Approval
    if frappe.has_role("Project Approver L1", user=user):
        if ptype in ["read", "write", "submit"]:
            return True

    # L2 approver can act on Pending L2 Approval
    if frappe.has_role("Project Approver L2", user=user):
        if ptype in ["read", "write", "submit"]:
            return True

    # Read-only for Project Viewer
    if frappe.has_role("Project Viewer", user=user):
        if ptype == "read":
            return True

    return False


def get_permission_query_conditions(user=None):
    """Filter list view based on role."""
    if not user:
        user = frappe.session.user

    if user == "Administrator":
        return ""

    conditions = []

    if frappe.has_role("System Manager", user=user) or frappe.has_role("Project Manager", user=user):
        return ""

    # Published updates are visible to viewers
    if frappe.has_role("Project Viewer", user=user):
        return "(`tabProject Update`.`is_published` = 1)"

    parts = []

    # Team member sees own updates
    if frappe.has_role("Project Team Member", user=user):
        parts.append("(`tabProject Update`.`team_member` = '{user}')".format(user=user))

    # Approvers see pending approvals + published
    if frappe.has_role("Project Approver L1", user=user):
        parts.append(
            "(`tabProject Update`.`workflow_state` = 'Pending L1 Approval' "
            "OR `tabProject Update`.`is_published` = 1)"
        )

    if frappe.has_role("Project Approver L2", user=user):
        parts.append(
            "(`tabProject Update`.`workflow_state` = 'Pending L2 Approval' "
            "OR `tabProject Update`.`is_published` = 1)"
        )

    if not parts:
        return "1=0"

    return "(" + " OR ".join(parts) + ")"
