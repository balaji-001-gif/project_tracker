from . import __version__ as app_version

app_name = "project_update_tracker"
app_title = "Project Update Tracker"
app_publisher = "Your Company"
app_description = "Advanced daily project update tool with multi-level approval workflow"
app_icon = "octicon octicon-checklist"
app_color = "#3498db"
app_email = "admin@example.com"
app_license = "MIT"

# Include CSS/JS in website pages
web_include_css = "/assets/project_update_tracker/css/project.css"
web_include_js = "/assets/project_update_tracker/js/project.js"

# Website home page
home_page = "projects"

# Website route rules
website_route_rules = [
    {"from_route": "/projects/<path:name>", "to_route": "projects/view"},
]

# Permissions
has_permission = {
    "Project Update": "project_update_tracker.utils.permissions.has_permission",
}

permission_query_conditions = {
    "Project Update": "project_update_tracker.utils.permissions.get_permission_query_conditions",
}

# Document Events
doc_events = {
    "Project Update": {
        "before_submit": "project_update_tracker.utils.workflow.before_submit_handler",
        "on_update": "project_update_tracker.utils.workflow.on_update_handler",
        "after_insert": "project_update_tracker.utils.workflow.after_insert_handler",
        "on_cancel": "project_update_tracker.utils.workflow.on_cancel_handler",
        "validate": "project_update_tracker.utils.workflow.validate_project_update",
    }
}

# Scheduled Tasks
scheduler_events = {
    "daily": [
        "project_update_tracker.utils.notifications.send_daily_update_reminders"
    ],
    "hourly": [
        "project_update_tracker.utils.notifications.check_pending_approvals"
    ],
}

# Fixtures
fixtures = [
    "Role",
    "Workflow",
    "Workflow State",
    "Workflow Transition",
    "Email Template",
    "Notification",
    "Custom DocPerm",
]

# Boot session additions
boot_session = "project_update_tracker.utils.boot_session"

# Install
after_install = "project_update_tracker.install.after_install"

# Override whitelisted methods
override_whitelisted_methods = {
    "frappe.desk.list.get_list.get_list": "project_update_tracker.api.project_api.get_list_override"
}

# Jinja
jinja = {
    "methods": "project_update_tracker.utils.jinja_methods"
}
