import frappe
from frappe import _
from frappe.utils import today, now_datetime, add_to_date, get_datetime, now
from frappe.core.doctype.communication.email import make


def _get_approvers(role):
    """Return list of users with a given role."""
    return frappe.get_all(
        "Has Role",
        filters={"role": role, "parenttype": "User"},
        pluck="parent"
    )


def _send_email(template_name, recipients, doc, subject_extra=""):
    if not recipients:
        return
    template = frappe.db.get_value("Email Template", template_name, ["subject", "response"], as_dict=True)
    if not template:
        return

    context = {
        "doc": doc,
        "url": frappe.utils.get_url(),
    }

    subject = frappe.render_template(template.subject, context)
    if subject_extra:
        subject = f"{subject} {subject_extra}"
    message = frappe.render_template(template.response, context)

    # de-duplicate recipients
    if isinstance(recipients, str):
        recipients = [recipients]
    recipients = list(set(recipients))

    for r in recipients:
        try:
            make(
                recipients=r,
                subject=subject,
                content=message,
                doctype="Project Update",
                name=doc.name,
                send_email=True,
            )
        except Exception:
            frappe.log_error(frappe.get_traceback(), f"Email send failed: {r}")


def notify_l1_approvers(doc):
    settings = frappe.get_single("Project Tracker Settings")
    role = settings.l1_approvers_role or "Project Approver L1"
    approvers = _get_approvers(role)
    template = settings.email_template_submit or "Project Update - Submitted for L1"
    _send_email(template, approvers, doc)

    # Also create notifications in desk
    for a in approvers:
        _create_notification(a, doc,
            subject=f"Project Update {doc.name} pending L1 approval",
            link=f"/projects/review/{doc.name}")


def notify_l2_approvers(doc):
    settings = frappe.get_single("Project Tracker Settings")
    role = settings.l2_approvers_role or "Project Approver L2"
    approvers = _get_approvers(role)
    template = settings.email_template_l1 or "Project Update - L1 Approved"
    _send_email(template, approvers, doc)

    for a in approvers:
        _create_notification(a, doc,
            subject=f"Project Update {doc.name} pending L2 approval",
            link=f"/projects/review/{doc.name}")


def notify_team_member_approved(doc):
    settings = frappe.get_single("Project Tracker Settings")
    template = settings.email_template_l2 or "Project Update - L2 Approved"
    _send_email(template, [doc.team_member_email], doc)

    _create_notification(doc.team_member, doc,
        subject=f"Your project update {doc.name} has been approved",
        link=f"/projects/view/{doc.project}")


def notify_team_member_rejected(doc):
    settings = frappe.get_single("Project Tracker Settings")
    template = settings.email_template_reject or "Project Update - Rejected"
    _send_email(template, [doc.team_member_email], doc)

    _create_notification(doc.team_member, doc,
        subject=f"Your project update {doc.name} was rejected",
        link=f"/projects/my")


def _create_notification(user, doc, subject, link):
    """Create an in-app notification."""
    try:
        n = frappe.get_doc({
            "doctype": "Notification Log",
            "subject": subject,
            "for_user": user,
            "document_type": "Project Update",
            "document_name": doc.name,
            "email_content": f"<a href='{link}'>{subject}</a>",
        })
        n.insert(ignore_permissions=True)
    except Exception:
        pass


def send_daily_update_reminders():
    """Daily scheduler: remind team members who haven't submitted today."""
    settings = frappe.get_single("Project Tracker Settings")
    if not settings.enable_daily_reminder:
        return

    today_str = today()

    # Get all active projects
    projects = frappe.get_all("Project", filters={"status": "Open"}, pluck="name")

    for project in projects:
        # Get team members
        members = frappe.get_all(
            "Project User",
            filters={"parent": project},
            pluck="user"
        )
        if not members:
            # Fall back to project manager
            pm = frappe.db.get_value("Project", project, "project_manager") if frappe.db.has_column("Project", "project_manager") else None
            if pm:
                members = [pm]

        for member in members:
            # Check if already submitted today
            existing = frappe.db.exists("Project Update", {
                "project": project,
                "team_member": member,
                "update_date": today_str,
                "docstatus": ["<", 2]
            })
            if existing:
                continue

            # Send reminder
            template = settings.email_template_daily or "Project Update - Daily Reminder"
            user = frappe.get_doc("User", member)
            pseudo_doc = frappe._dict({
                "project_name": frappe.db.get_value("Project", project, "project_name") or project,
                "team_member_name": user.full_name,
                "update_date": today_str,
                "name": project,
            })
            _send_email(template, [user.email], pseudo_doc)


def check_pending_approvals():
    """Hourly: escalate pending approvals beyond threshold."""
    settings = frappe.get_single("Project Tracker Settings")
    threshold_hours = settings.escalation_after_hours or 24
    escalation_role = settings.escalation_role or "Project Manager"
    cutoff = add_to_date(now_datetime(), hours=-threshold_hours)

    # Pending L1 beyond threshold
    pending_l1 = frappe.get_all("Project Update", filters={
        "workflow_state": "Pending L1 Approval",
        "docstatus": 0,
        "modified": ["<", cutoff],
    }, pluck="name")

    pending_l2 = frappe.get_all("Project Update", filters={
        "workflow_state": "Pending L2 Approval",
        "docstatus": 0,
        "modified": ["<", cutoff],
    }, pluck="name")

    escalators = _get_approvers(escalation_role)
    if not escalators:
        return

    for name in pending_l1 + pending_l2:
        doc = frappe.get_doc("Project Update", name)
        for e in escalators:
            _create_notification(e, doc,
                subject=f"ESCALATION: Project Update {name} pending beyond {threshold_hours}h",
                link=f"/projects/review/{name}")
