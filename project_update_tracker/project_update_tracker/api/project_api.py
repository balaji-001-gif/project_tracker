import frappe
from frappe import _
from frappe.utils import today


@frappe.whitelist()
def get_project_users_query(doctype, txt, searchfield, start, page_len, filters):
    """Query for team members — those with Project Team Member role."""
    return frappe.db.sql("""
        SELECT u.name, u.full_name
        FROM `tabUser` u
        INNER JOIN `tabHas Role` hr ON hr.parent = u.name AND hr.parenttype = 'User'
        INNER JOIN `tabRole` r ON r.name = hr.role
        WHERE u.enabled = 1
          AND r.name IN ('Project Team Member', 'Project Manager')
          AND (u.name LIKE %(txt)s OR u.full_name LIKE %(txt)s)
        LIMIT %(start)s, %(page_len)s
    """, {"txt": f"%{txt}%", "start": start, "page_len": page_len}, as_list=True)


@frappe.whitelist()
def get_list_override(*args, **kwargs):
    """Fallback to default get_list — kept for permission hooking."""
    from frappe.desk.list.get_list import get_list as original
    return original(*args, **kwargs)


@frappe.whitelist()
def get_my_projects():
    """Get projects the current user is assigned to."""
    user = frappe.session.user
    projects = frappe.db.sql("""
        SELECT DISTINCT p.name, p.project_name, p.status, p.expected_end_date,
               p.percent_complete,
               (SELECT COUNT(*) FROM `tabProject Update` pu
                WHERE pu.project = p.name AND pu.team_member = %(user)s
                  AND pu.update_date = %(today)s AND pu.docstatus < 2) as today_updates
        FROM `tabProject` p
        LEFT JOIN `tabProject User` pu ON pu.parent = p.name
        WHERE p.status = 'Open'
          AND (pu.user = %(user)s OR p.project_manager = %(user)s OR %(admin)s = 1)
        ORDER BY p.project_name
    """, {"user": user, "today": today(), "admin": 1 if user == "Administrator" else 0}, as_dict=True)
    return projects


@frappe.whitelist()
def get_all_projects():
    """Get all projects — for viewers and listing."""
    projects = frappe.db.sql("""
        SELECT p.name, p.project_name, p.status, p.expected_end_date, p.percent_complete,
               c.customer_name,
               (SELECT COUNT(*) FROM `tabProject Update` pu
                WHERE pu.project = p.name AND pu.is_published = 1 AND pu.docstatus = 1) as published_updates
        FROM `tabProject` p
        LEFT JOIN `tabCustomer` c ON c.name = p.customer
        WHERE p.status IN ('Open', 'Completed')
        ORDER BY p.modified DESC
    """, as_dict=True)
    return projects


@frappe.whitelist()
def get_project_detail(project):
    """Get full project detail with published updates."""
    if not project:
        frappe.throw(_("Project required"))

    proj = frappe.get_doc("Project", project).as_dict()
    proj["customer_name"] = frappe.db.get_value("Customer", proj.get("customer"), "customer_name") if proj.get("customer") else None

    # Get published updates
    is_team = frappe.has_role(["Project Team Member", "Project Manager", "Project Approver L1", "Project Approver L2"])
    filters = {"project": project, "docstatus": 1}
    if not is_team:
        filters["is_published"] = 1

    updates = frappe.get_all(
        "Project Update",
        filters=filters,
        fields=[
            "name", "team_member_name", "update_date", "overall_status",
            "progress_percentage", "workflow_state", "work_done_today",
            "work_planned_tomorrow", "blockers", "blocker_severity",
            "needs_attention", "hours_spent", "tasks_completed",
            "is_published", "l1_approver", "l2_approver"
        ],
        order_by="update_date desc, creation desc"
    )
    proj["updates"] = updates
    proj["can_update"] = is_team
    return proj


@frappe.whitelist()
def create_update(project, work_done_today, work_planned_tomorrow="",
                  blockers="", blocker_severity="", progress_percentage=0,
                  overall_status="On Track", hours_spent=0, tasks_completed=0,
                  needs_attention=0, update_date=None):
    """Create a new project update from the website."""
    user = frappe.session.user
    if not frappe.has_role(["Project Team Member", "Project Manager"]):
        frappe.throw(_("You do not have permission to create updates."), frappe.PermissionError)

    doc = frappe.get_doc({
        "doctype": "Project Update",
        "project": project,
        "team_member": user,
        "update_date": update_date or today(),
        "work_done_today": work_done_today,
        "work_planned_tomorrow": work_planned_tomorrow,
        "blockers": blockers,
        "blocker_severity": blocker_severity,
        "progress_percentage": progress_percentage,
        "overall_status": overall_status,
        "hours_spent": hours_spent,
        "tasks_completed": tasks_completed,
        "needs_attention": needs_attention,
        "workflow_state": "Draft",
    })
    doc.flags.ignore_duplicate_check = False
    doc.insert(ignore_permissions=False)
    return doc.name


@frappe.whitelist()
def get_update_detail(name):
    """Get a single project update for review."""
    doc = frappe.get_doc("Project Update", name)
    if not _can_access(doc):
        frappe.throw(_("No access to this update."), frappe.PermissionError)
    data = doc.as_dict()
    data["can_approve_l1"] = (doc.workflow_state == "Pending L1 Approval" and
        frappe.has_role(["Project Approver L1", "Project Manager"]))
    data["can_approve_l2"] = (doc.workflow_state == "Pending L2 Approval" and
        frappe.has_role(["Project Approver L2", "Project Manager"]))
    data["can_publish"] = (doc.workflow_state == "Approved" and
        frappe.has_role(["Project Manager", "System Manager"]))
    data["can_resubmit"] = (doc.workflow_state == "Rejected" and
        frappe.has_role(["Project Team Member", "Project Manager"]) and
        doc.team_member == frappe.session.user)
    return data


def _can_access(doc):
    user = frappe.session.user
    if user == "Administrator" or frappe.has_role("System Manager"):
        return True
    if doc.is_published and frappe.has_role("Project Viewer"):
        return True
    if doc.team_member == user:
        return True
    if frappe.has_role("Project Manager"):
        return True
    if doc.workflow_state == "Pending L1 Approval" and frappe.has_role("Project Approver L1"):
        return True
    if doc.workflow_state == "Pending L2 Approval" and frappe.has_role("Project Approver L2"):
        return True
    return False
