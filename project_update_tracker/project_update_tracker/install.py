import frappe
from frappe import _


def after_install():
    """Run after app installation - create roles, workflow, etc."""
    create_custom_roles()
    create_workflow()
    create_email_templates()
    create_default_settings()
    frappe.db.commit()


def create_custom_roles():
    roles = [
        {
            "role_name": "Project Team Member",
            "desk_access": 1,
            "is_custom": 1,
        },
        {
            "role_name": "Project Approver L1",
            "desk_access": 1,
            "is_custom": 1,
        },
        {
            "role_name": "Project Approver L2",
            "desk_access": 1,
            "is_custom": 1,
        },
        {
            "role_name": "Project Manager",
            "desk_access": 1,
            "is_custom": 1,
        },
        {
            "role_name": "Project Viewer",
            "desk_access": 0,
            "is_custom": 1,
        },
    ]
    for r in roles:
        if not frappe.db.exists("Role", r["role_name"]):
            doc = frappe.get_doc({"doctype": "Role", **r})
            doc.insert(ignore_permissions=True)


def create_workflow():
    """Create the multi-level approval workflow for Project Update."""
    workflow_name = "Project Update Approval"

    if frappe.db.exists("Workflow", workflow_name):
        frappe.delete_doc("Workflow", workflow_name)

    wf = frappe.get_doc({
        "doctype": "Workflow",
        "workflow_name": workflow_name,
        "document_type": "Project Update",
        "is_active": 1,
        "send_email_alert": 1,
        "workflow_state_field": "workflow_state",
    })

    states = [
        ("Draft", "Draft"),
        ("Pending L1 Approval", "Pending L1 Approval"),
        ("Pending L2 Approval", "Pending L2 Approval"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
        ("Completed", "Completed"),
    ]
    for state, style in states:
        wf.append("states", {
            "state": state,
            "doc_status": "0" if state == "Draft" else "1",
            "update_field": "workflow_state",
            "update_value": state,
        })

    transitions = [
        ("Draft", "Submit for L1", "Pending L1 Approval", "Project Team Member"),
        ("Pending L1 Approval", "Approve", "Pending L2 Approval", "Project Approver L1"),
        ("Pending L1 Approval", "Reject", "Rejected", "Project Approver L1"),
        ("Pending L2 Approval", "Approve", "Approved", "Project Approver L2"),
        ("Pending L2 Approval", "Reject", "Rejected", "Project Approver L2"),
        ("Rejected", "Resubmit", "Pending L1 Approval", "Project Team Member"),
        ("Approved", "Mark Completed", "Completed", "Project Manager"),
        ("Pending L1 Approval", "Approve", "Pending L2 Approval", "Project Manager"),
        ("Pending L2 Approval", "Approve", "Approved", "Project Manager"),
    ]
    for state, action, next_state, role in transitions:
        wf.append("transitions", {
            "state": state,
            "action": action,
            "next_state": next_state,
            "allowed": role,
            "allow_self_approval": 1,
            "condition": "",
        })

    wf.insert(ignore_permissions=True)


def create_email_templates():
    templates = [
        {
            "name": "Project Update - Daily Reminder",
            "subject": "Daily Project Update Reminder: {{ doc.project_name }}",
            "response": """<p>Hello {{ doc.team_member_name }},</p>
<p>This is a reminder to submit your daily update for project: <strong>{{ doc.project_name }}</strong></p>
<p>Please visit: <a href="{{ url }}/projects/my">My Projects</a></p>"""
        },
        {
            "name": "Project Update - Submitted for L1",
            "subject": "Project Update Submitted for L1 Approval: {{ doc.name }}",
            "response": """<p>Hello,</p>
<p>A project update has been submitted for L1 approval.</p>
<p><strong>Project:</strong> {{ doc.project_name }}<br>
<strong>Submitted by:</strong> {{ doc.team_member_name }}<br>
<strong>Date:</strong> {{ doc.update_date }}</p>
<p><a href="{{ url }}/projects/review/{{ doc.name }}">Review Update</a></p>"""
        },
        {
            "name": "Project Update - L1 Approved",
            "subject": "Project Update L1 Approved - Pending L2: {{ doc.name }}",
            "response": """<p>Hello,</p>
<p>Project update L1 approved, pending L2 approval.</p>
<p><strong>Project:</strong> {{ doc.project_name }}</p>
<p><a href="{{ url }}/projects/review/{{ doc.name }}">Review Update</a></p>"""
        },
        {
            "name": "Project Update - L2 Approved",
            "subject": "Project Update Approved: {{ doc.name }}",
            "response": """<p>Hello {{ doc.team_member_name }},</p>
<p>Your project update has been fully approved.</p>
<p><strong>Project:</strong> {{ doc.project_name }}<br>
<strong>Status:</strong> Approved</p>"""
        },
        {
            "name": "Project Update - Rejected",
            "subject": "Project Update Rejected: {{ doc.name }}",
            "response": """<p>Hello {{ doc.team_member_name }},</p>
<p>Your project update has been rejected.</p>
<p><strong>Project:</strong> {{ doc.project_name }}<br>
<strong>Rejection Reason:</strong> {{ doc.rejection_reason }}</p>
<p>Please update and resubmit: <a href="{{ url }}/projects/my">My Projects</a></p>"""
        },
    ]
    for t in templates:
        if not frappe.db.exists("Email Template", t["name"]):
            doc = frappe.get_doc({
                "doctype": "Email Template",
                **t,
            })
            doc.insert(ignore_permissions=True)


def create_default_settings():
    if not frappe.db.exists("Project Tracker Settings", "Project Tracker Settings"):
        settings = frappe.get_doc({
            "doctype": "Project Tracker Settings",
            "enable_daily_reminder": 1,
            "reminder_time": "09:00:00",
            "enable_auto_publish": 1,
            "l1_approvers_role": "Project Approver L1",
            "l2_approvers_role": "Project Approver L2",
            "allow_resubmission": 1,
        })
        settings.insert(ignore_permissions=True)
