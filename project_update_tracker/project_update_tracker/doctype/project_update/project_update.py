import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today, now_datetime, getdate, date_diff, cint


class ProjectUpdate(Document):
    def before_validate(self):
        self.populate_project_details()
        self.populate_team_member_details()
        self.calculate_days_remaining()
        self.set_default_workflow_state()

    def validate(self):
        self.validate_update_date()
        self.validate_daily_duplicate()
        self.validate_critical_blocker()

    def before_save(self):
        self.sync_status_with_workflow()

    def before_submit(self):
        if not self.workflow_state or self.workflow_state == "Draft":
            frappe.throw(_("Please use the Submit for L1 action to submit this update."))

    def on_submit(self):
        self.handle_workflow_completion()

    # ---------------------- Helpers ----------------------

    def populate_project_details(self):
        if self.project:
            project = frappe.get_doc("Project", self.project)
            self.project_name = project.project_name
            self.project_manager = project.project_manager if hasattr(project, "project_manager") else None
            self.customer = project.customer if hasattr(project, "customer") else None
            self.planned_end_date = project.expected_end_date if hasattr(project, "expected_end_date") else None

    def populate_team_member_details(self):
        if self.team_member:
            user = frappe.get_doc("User", self.team_member)
            self.team_member_name = user.full_name
            self.team_member_email = user.email

    def calculate_days_remaining(self):
        if self.planned_end_date:
            self.days_remaining = date_diff(getdate(self.planned_end_date), getdate(today()))

    def set_default_workflow_state(self):
        if not self.workflow_state:
            self.workflow_state = "Draft"

    def sync_status_with_workflow(self):
        if self.workflow_state:
            self.status = self.workflow_state

    def validate_update_date(self):
        if getdate(self.update_date) > getdate(today()):
            frappe.throw(_("Update date cannot be in the future."))

    def validate_daily_duplicate(self):
        if self.flags.ignore_duplicate_check:
            return
        existing = frappe.db.exists(
            "Project Update",
            {
                "project": self.project,
                "team_member": self.team_member,
                "update_date": self.update_date,
                "docstatus": ["<", 2],
                "name": ["!=", self.name or ""],
            },
        )
        if existing:
            frappe.throw(
                _("A project update already exists for this project and team member on {0}: {1}").format(
                    self.update_date, existing
                )
            )

    def validate_critical_blocker(self):
        if self.blocker_severity == "Critical" and not self.needs_attention:
            self.needs_attention = 1
            frappe.msgprint(_("Critical blocker detected — flagged for manager attention."))

    def handle_workflow_completion(self):
        """Called on submit — finalizes state based on workflow_state."""
        if self.workflow_state == "Completed":
            self.mark_published()
        elif self.workflow_state == "Approved":
            # Auto-publish if settings allow
            settings = frappe.get_single("Project Tracker Settings")
            if settings.enable_auto_publish:
                self.mark_published()

    def mark_published(self):
        self.is_published = 1
        self.db_set("is_published", 1)
        # Update parent project status
        if self.project and self.overall_status == "Completed":
            try:
                project = frappe.get_doc("Project", self.project)
                project.status = "Completed"
                project.save(ignore_permissions=True)
            except Exception:
                frappe.log_error(frappe.get_traceback(), "Project status update failed")

    @frappe.whitelist()
    def add_comment_log(self, action, comment=""):
        """Append a comment in the timeline."""
        self.add_comment("Comment", f"{action}: {comment}" if comment else action)


# ---------- Whitelisted API Helpers ----------

@frappe.whitelist()
def get_project_team_members(project):
    """Get list of team members assigned to a project."""
    members = []
    if not project:
        return members
    # Try Project User child table
    pu = frappe.get_all(
        "Project User",
        filters={"parent": project},
        fields=["user", "full_name"],
    )
    for m in pu:
        members.append({"user": m.user, "full_name": m.full_name or m.user})
    return members


@frappe.whitelist()
def get_recent_updates(project, limit=5):
    """Get recent updates for a project (published only for non-team)."""
    user = frappe.session.user
    is_team = frappe.has_permission("Project Update", "write", user=user)
    filters = {"project": project, "docstatus": 1}
    if not is_team:
        filters["is_published"] = 1
    updates = frappe.get_all(
        "Project Update",
        filters=filters,
        fields=[
            "name", "team_member_name", "update_date",
            "overall_status", "progress_percentage", "workflow_state",
            "work_done_today", "blockers", "blocker_severity"
        ],
        order_by="update_date desc",
        limit_page_length=cint(limit),
    )
    return updates


@frappe.whitelist()
def get_project_metrics(project):
    """Aggregate metrics for a project."""
    updates = frappe.get_all(
        "Project Update",
        filters={"project": project, "docstatus": 1},
        fields=["hours_spent", "overtime_hours", "tasks_completed", "progress_percentage"],
    )
    return {
        "total_hours": sum((u.hours_spent or 0) for u in updates),
        "total_overtime": sum((u.overtime_hours or 0) for u in updates),
        "total_tasks_completed": sum((u.tasks_completed or 0) for u in updates),
        "updates_count": len(updates),
        "latest_progress": updates[0].progress_percentage if updates else 0,
    }
