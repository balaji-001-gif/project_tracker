# Project Update Tracker

> **Advanced Daily Project Update Tool with Multi-Level Approval Workflow for ERPNext v15+**

A complete Frappe/ERPNext app that enables teams to submit daily project updates, route them through a structured L1 → L2 approval chain, publish approved updates for view-only access, and receive automated reminders — all from website screens without needing desk access.

---

## 📋 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Roles & Permissions](#-roles--permissions)
- [Setup Guide](#-setup-guide)
- [Workflow Overview](#-workflow-overview)
- [User Guide by Role](#-user-guide-by-role)
  - [Project Team Member](#project-team-member)
  - [Project Approver L1](#project-approver-l1)
  - [Project Approver L2](#project-approver-l2)
  - [Project Manager](#project-manager)
  - [Project Viewer](#project-viewer)
- [Website Routes](#-website-routes)
- [Notification System](#-notification-system)
- [Scheduled Jobs](#-scheduled-jobs)
- [DocType Fields Reference](#-doctype-fields-reference)
- [Project Tracker Settings](#-project-tracker-settings)
- [Developer Guide](#-developer-guide)
- [License](#-license)

---

## ✨ Features

- **Daily Update Submission** — Team members submit structured daily updates via `/projects/update/<project>`
- **Multi-Level Approval Workflow** — 6-state workflow: Draft → Pending L1 → Pending L2 → Approved → Completed → Published
- **Rejection & Resubmission** — Updates rejected at any level can be revised and resubmitted
- **Role-Based Permissions** — 5 custom roles with granular read/write/submit permissions
- **View-Only Access After Completion** — Published updates are read-only for Project Viewers
- **Website Screens** — All team interactions happen via `/projects/*` — no desk access required for team members
- **Backend Desk View** — Managers and admins can cross-check all data via the standard Frappe desk
- **Email & In-App Notifications** — Automatic email alerts on each workflow transition
- **Daily Reminders** — Automated email reminders at 9:00 AM for pending updates
- **Escalation Alerts** — Hourly check escalates approvals pending beyond configurable threshold (default: 24 hours)
- **GitHub Repo Integration** — Each update can include a link to the associated GitHub repository
- **File Attachments** — Documents/images can be attached to each update
- **Auto-Publish** — Updates can be automatically published after L2 approval
- **Project Status Sync** — When a team member marks 100% completion, the parent project status updates to "Completed"

---

## 📦 Installation

### Prerequisites

- ERPNext v15.0+ / Frappe v15.0+
- Bench environment set up

### Steps

```bash
# 1. Get the app (--skip-assets is required for apps without frontend builds)
bench get-app --skip-assets https://github.com/balaji-001-gif/project_tracker

# 2. Install on your site
bench --site yoursite.local install-app project_tracker

# 3. Run migrations
bench --site yoursite.local migrate

# 4. Clear cache
bench --site yoursite.local clear-cache

# 5. (Optional) Run tests
bench --site yoursite.local run-tests --app project_tracker
```

> **Note:** The `--skip-assets` flag is required because this app has no frontend build pipeline (it uses Frappe's built-in website framework). Frappe v15's esbuild builds its app path map from `sites/apps.txt` at startup, but during `bench get-app` the app hasn't been registered there yet, causing the asset build step to fail. Use `--skip-assets` to bypass this step safely.

### What Gets Created Automatically

On first install, the app automatically creates:

| Resource | Details |
|----------|---------|
| **Roles** | `Project Team Member`, `Project Approver L1`, `Project Approver L2`, `Project Manager`, `Project Viewer` |
| **Workflow** | `Project Update Approval` — complete 6-state workflow with 9 transitions |
| **Email Templates** | 5 pre-built templates for daily reminders, submissions, approvals, and rejections |
| **Default Settings** | `Project Tracker Settings` with sensible defaults (auto-publish ON, reminders at 9 AM, resubmission allowed) |

---

## 👥 Roles & Permissions

### Role Descriptions

| Role | Desk Access | Can Create Updates | Can Approve L1 | Can Approve L2 | Can Publish | Can View Published | Can Manage Settings |
|------|:-----------:|:------------------:|:--------------:|:--------------:|:-----------:|:-----------------:|:------------------:|
| **System Manager** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Project Team Member** | ✅ | ✅ (own only) | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Project Approver L1** | ✅ | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ |
| **Project Approver L2** | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ |
| **Project Manager** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Project Viewer** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ (published only) | ❌ |

### Permission Rules

- **Team Members** can only see and edit their **own** updates
- **L1 Approvers** see all updates in "Pending L1 Approval" state + published updates
- **L2 Approvers** see all updates in "Pending L2 Approval" state + published updates
- **Project Managers** see **everything** (all updates, all states)
- **Project Viewers** see **only published** updates (read-only)
- **Project Managers** can override approval at any level (they can approve at both L1 and L2)

---

## 🔧 Setup Guide

### Step 1: Assign Roles to Users

After installation, go to the Frappe Desk:

1. Go to **User** list
2. Open each user who needs access
3. Under **Roles & Permissions**, add the appropriate role(s):
   - Add `Project Team Member` for team members who submit daily updates
   - Add `Project Approver L1` for first-level approvers
   - Add `Project Approver L2` for second-level approvers
   - Add `Project Manager` for project managers (has full access)
   - Add `Project Viewer` for stakeholders who only need to view published data
4. Save

> **Note:** A user can hold multiple roles. E.g., a user can be both "Project Team Member" AND "Project Approver L1" if needed.

### Step 2: Configure Project Tracker Settings

1. Go to **Project Tracker Settings** (single doctype, accessible from the desk)
2. Configure the following:

| Setting | Default | Description |
|---------|---------|-------------|
| Enable Daily Reminder | ✅ | Send automated reminder emails at configured time |
| Reminder Time | 09:00 | Time of day to send daily reminders |
| Enable Auto Publish | ✅ | Automatically publish updates after L2 approval |
| Allow Resubmission | ✅ | Allow team members to resubmit rejected updates |
| L1 Approvers Role | Project Approver L1 | Role that can approve at L1 |
| L2 Approvers Role | Project Approver L2 | Role that can approve at L2 |
| Escalation After Hours | 24 | Hours after which pending approvals trigger escalation |
| Escalation Role | Project Manager | Role that receives escalation notifications |

### Step 3: Ensure Projects Exist

This app works with the standard ERPNext **Project** doctype. Make sure you have:
- Projects created with status "Open"
- Team members assigned to projects via the **Project User** child table
- (Optional) A customer linked to each project

### Step 4: Access the Website

All users can access the app at:

```
http://yoursite.local/projects
```

---

## 🔄 Workflow Overview

### State Diagram

```
                  ┌─────────────┐
                  │    DRAFT    │
                  └──────┬──────┘
                         │ Submit for L1
                         ▼
              ┌─────────────────────┐
              │ PENDING L1 APPROVAL │◄──── Resubmit (after Rejection)
              └──────────┬──────────┘
                    ┌────┴────┐
                    │         │
               Approve    Reject
                    │         │
                    ▼         ▼
         ┌────────────────┐  ┌──────────┐
         │ PENDING L2     │  │ REJECTED │
         │ APPROVAL       │  └─────┬────┘
         └───────┬────────┘        │ Resubmit
            ┌────┴────┐            │
       Approve    Reject           │
            │         │            │
            ▼         ▼            │
      ┌──────────┐  ┌──────────┐   │
      │ APPROVED │  │ REJECTED │───┘
      └─────┬────┘  └──────────┘
            │ Mark Completed
            ▼
      ┌───────────┐
      │ COMPLETED │
      └─────┬─────┘
            │ Auto-publish
            ▼
      ┌───────────┐
      │ PUBLISHED │  ← is_published=1 (visible to all roles)
      └───────────┘
```

### Transitions Table

| Current State | Action | Performed By | Next State | Notification Sent To |
|---------------|--------|-------------|------------|---------------------|
| Draft | Submit for L1 | Team Member | Pending L1 Approval | L1 Approvers |
| Pending L1 Approval | Approve | L1 Approver / PM | Pending L2 Approval | L2 Approvers |
| Pending L1 Approval | Reject | L1 Approver / PM | Rejected | Team Member |
| Pending L2 Approval | Approve | L2 Approver / PM | Approved | Team Member |
| Pending L2 Approval | Reject | L2 Approver / PM | Rejected | Team Member |
| Approved | Mark Completed | Project Manager | Completed | — |
| Rejected | Resubmit | Team Member | Pending L1 Approval | L1 Approvers |
| Approved / Completed | Auto-Publish | System | Published (is_published=1) | — |

---

## 📖 User Guide by Role

### Project Team Member

#### Overview
As a **Project Team Member**, you submit daily updates on your assigned projects. You can only see and manage your own updates.

#### Step-by-Step

**1. View Your Projects**
- Visit `/projects/my`
- You'll see all projects assigned to you
- Each card shows: project name, progress %, and whether you've submitted today's update
- Click **"Add Daily Update"** or **"Update Again"** to submit

**2. Submit a Daily Update**
- Navigate to `/projects/update/<project-name>`
- Fill in the form:

| Field | Required | Description |
|-------|----------|-------------|
| Work Done Today | ✅ | Describe what you accomplished (min 10 characters) |
| Work Planned Tomorrow | ❌ | What you plan to work on next |
| Blockers / Issues | ❌ | Any obstacles you're facing |
| Blocker Severity | ❌ | Low / Medium / High / Critical |
| Progress % | ❌ | Your estimate of overall project completion |
| Overall Status | ❌ | On Track / At Risk / Off Track / On Hold / Completed |
| Hours Spent | ❌ | Number of hours worked today |
| Tasks Completed | ❌ | Number of tasks finished today |
| GitHub Repo Link | ❌ | Link to the relevant GitHub repository |
| Needs Manager Attention | ❌ | Check if management needs to be alerted |

- Click **"Save & Submit for L1 Approval"**
- The update is automatically created in "Draft" state and then submitted to "Pending L1 Approval"

**3. Check Your Update Status**
- Visit `/projects/my` — your projects show today's submission status
- Visit `/projects/view/<project>` to see all your updates and their current workflow state

**4. Resubmit a Rejected Update**
- If your update is rejected, you'll receive an email notification
- Go to the review page at `/projects/review/<update-name>`
- Click **"Resubmit for L1"** to send it back through the approval chain
- You can also edit the update via the desk before resubmitting

---

### Project Approver L1

#### Overview
As an **L1 Approver**, you are the first line of approval. You review team members' updates and decide whether to forward them to L2 or reject them.

#### Step-by-Step

**1. View Pending Approvals**
- Visit `/projects/approvals`
- The **"Pending L1 Approval"** section shows all updates waiting for your review
- Updates flagged as **"Needs Attention"** appear first (highlighted in red)

**2. Review and Approve**
- Click **"Review"** on any update card, or go directly to `/projects/review/<update-name>`
- Read through:
  - Work done today
  - Work planned
  - Blockers and their severity
  - Metrics (progress %, hours, tasks)
  - GitHub repo link (if provided)
  - File attachments (if any)
- To **approve**: Add optional comments and click **"Approve (L1)"**
  - This moves the update to "Pending L2 Approval"
  - L2 Approvers are notified via email and in-app notification
- To **reject**: Click **"Reject"**, provide a reason (min 5 characters), and confirm
  - The team member is notified with the rejection reason
  - They can edit and resubmit

---

### Project Approver L2

#### Overview
As an **L2 Approver**, you do the final review. Once you approve, the update is fully approved and (if auto-publish is enabled) becomes publicly visible.

#### Step-by-Step

**1. View Pending Approvals**
- Visit `/projects/approvals`
- The **"Pending L2 Approval"** section shows all updates that passed L1

**2. Review and Finalize**
- Click **"Review"** on any update card
- You can see who approved at L1 and their comments
- To **approve**: Click **"Approve (L2)"**
  - The update moves to "Approved" state
  - If auto-publish is enabled in settings, the update becomes published immediately
  - The team member receives a success notification
- To **reject**: Click **"Reject"**, provide the reason
  - The update goes back to "Rejected" state
  - The team member is notified and can resubmit

---

### Project Manager

#### Overview
As a **Project Manager**, you have full access to everything. You can:
- Submit updates (just like a team member)
- Approve at both L1 and L2 levels (override approvals)
- Publish updates manually
- Mark updates as "Completed"
- View all projects and all updates

#### Step-by-Step

**1. Approve at Any Level**
- Visit `/projects/approvals`
- You'll see **both** L1 and L2 pending updates
- You can approve at either level regardless of your assigned role

**2. Publish an Approved Update**
- On the review page of an approved update (`/projects/review/<name>`)
- Click **"Publish (View-Only)"** to make it visible to Project Viewers

**3. Mark as Completed**
- On the review page of an approved update
- Click **"Mark Completed"** to finalize the update
- This also publishes it and, if progress is 100%, updates the parent Project status to "Completed"

**4. Backend Desk View**
- Log into the Frappe Desk
- Go to **Project Update** doctype to see all updates (all users, all states)
- Use standard Frappe features: filters, reports, exports, print formats

---

### Project Viewer

#### Overview
As a **Project Viewer**, you have read-only access to published updates. You do not have desk access — everything is available via the website.

#### Step-by-Step

**1. Browse All Projects**
- Visit `/projects`
- See all active and completed projects with their latest progress

**2. View Project Detail & Updates**
- Click on any project to view its details at `/projects/view/<project>`
- See all published updates with:
  - Work descriptions
  - Progress percentage
  - Overall status
  - Team member names
  - Blockers and their severity
  - GitHub repository links

**3. Limitations**
- You **cannot** create or edit updates
- You **cannot** approve or reject
- You only see updates that have been published (is_published=1)

---

## 🌐 Website Routes

| Route | Access | Description |
|-------|--------|-------------|
| `/projects` | All roles | Browse all active and completed projects |
| `/projects/my` | Team Members, Managers | View your assigned projects and today's update status |
| `/projects/view/<name>` | All roles | View project details and all published updates |
| `/projects/update/<name>` | Team Members, Managers | Submit a new daily update |
| `/projects/approvals` | L1 Approvers, L2 Approvers, Managers | View approval queue with pending updates grouped by level |
| `/projects/review/<update>` | Approvers, Managers, Team Member (own) | Full update detail with approve/reject/publish actions |

---

## 🔔 Notification System

### Email Templates

5 pre-built email templates are created on install:

| Template | Trigger | Recipients |
|----------|---------|------------|
| Daily Reminder | Scheduled daily at 9 AM | Team members who haven't submitted today |
| Submitted for L1 | Team member submits for approval | L1 Approvers |
| L1 Approved | L1 approves update | L2 Approvers |
| L2 Approved | L2 approves update | The team member who submitted |
| Rejected | L1 or L2 rejects update | The team member who submitted |

### In-App Notifications

In addition to emails, the app creates **Notification Log** entries in the Frappe desk notification system for:
- Pending L1 approvals
- Pending L2 approvals
- Approved updates
- Rejected updates
- Escalated approvals

---

## ⏰ Scheduled Jobs

| Job | Frequency | Description |
|-----|-----------|-------------|
| `send_daily_update_reminders` | Daily (9:00 AM) | Emails all team members who haven't submitted an update for today on their active projects |
| `check_pending_approvals` | Hourly | Identifies updates pending approval beyond the configured threshold (default: 24 hours) and sends escalation notifications to the escalation role |

---

## 📄 DocType Fields Reference

### Project Update

| Field | Type | Description |
|-------|------|-------------|
| `project` | Link → Project | The project this update belongs to |
| `project_name` | Read-only Data | Auto-populated from linked Project |
| `project_manager` | Read-only Link → User | Auto-populated from linked Project |
| `customer` | Read-only Link → Customer | Auto-populated from linked Project |
| `github_repo_link` | Data (URL) | Link to the GitHub repository |
| `team_member` | Link → User | Who submitted this update |
| `team_member_name` | Read-only Data | Auto-populated from User |
| `team_member_email` | Read-only Data | Auto-populated from User |
| `update_date` | Date | Date of the update (cannot be in the future) |
| `status` | Select | Current status (synced with workflow state) |
| `workflow_state` | Data (hidden) | Internal workflow state tracking |
| `is_published` | Check | Whether the update is view-only visible |
| `progress_percentage` | Percent | Estimated completion % |
| `overall_status` | Select | On Track / At Risk / Off Track / Completed / On Hold |
| `planned_end_date` | Read-only Date | Project's expected end date |
| `days_remaining` | Read-only Int | Days until planned end date |
| `work_done_today` | Text Editor | Description of work completed |
| `work_planned_tomorrow` | Text Editor | Description of planned work |
| `blockers` | Text Editor | Issues or blockers |
| `blocker_severity` | Select | Low / Medium / High / Critical |
| `needs_attention` | Check | Flag for manager attention |
| `hours_spent` | Float | Hours worked today |
| `overtime_hours` | Float | Overtime hours |
| `tasks_completed` | Int | Tasks finished today |
| `tasks_pending` | Int | Tasks still pending |
| `l1_approver` | Read-only Link → User | Who approved at L1 |
| `l1_approved_on` | Read-only Datetime | When L1 approval happened |
| `l1_comments` | Read-only Small Text | L1 approver's comments |
| `l2_approver` | Read-only Link → User | Who approved at L2 |
| `l2_approved_on` | Read-only Datetime | When L2 approval happened |
| `l2_comments` | Read-only Small Text | L2 approver's comments |
| `rejection_reason` | Read-only Text | Why the update was rejected |
| `attachments` | Table (Project Update Attachment) | Uploaded files/documents |

### Project Update Attachment (Child Table)

| Field | Type | Description |
|-------|------|-------------|
| `attachment` | Attach | Uploaded file |
| `attachment_name` | Read-only Data | Original file name |
| `description` | Small Text | Description of the attachment |

### Project Tracker Settings (Single)

See [Setup Guide](#step-2-configure-project-tracker-settings) for full field descriptions.

---

## ⚙️ Project Tracker Settings

The `Project Tracker Settings` doctype (single) allows admins to configure the app's behavior:

- **General** section: Enable/disable reminders, auto-publish, and resubmission
- **Approvers** section: Configure which roles are L1/L2 approvers and escalation parameters
- **Notifications** section: Toggle email notifications for each workflow transition and assign custom email templates

Access it from the Frappe Desk → Project Tracker Settings.

---

## 🛠 Developer Guide

### App Structure

```
project_tracker/
├── __init__.py
├── hooks.py                      # App hooks, permissions, events, scheduler
├── patches.txt
├── setup.py
├── requirements.txt
├── README.md
├── LICENSE.txt
├── MANIFEST.in
└── project_tracker/
    ├── __init__.py
    ├── modules.txt
    ├── install.py                # After-install setup (roles, workflow, templates)
    ├── api/
    │   ├── __init__.py
    │   ├── project_api.py        # Public API endpoints (CRUD, queries)
    │   └── approval_api.py       # Workflow action endpoints (submit, approve, reject)
    ├── utils/
    │   ├── __init__.py           # Boot session, jinja methods, pending count
    │   ├── permissions.py        # Custom has_permission & query conditions
    │   ├── notifications.py      # Email & in-app notification helpers
    │   └── workflow.py           # DocEvents handlers (validate, after_insert, etc.)
    ├── doctype/
    │   ├── project_update/       # Main submittable doctype with workflow
    │   ├── project_tracker_settings/  # Single doctype for configuration
    │   └── project_update_attachment/ # Child table for file attachments
    ├── templates/includes/       # Jinja templates (nav, cards)
    ├── www/projects/             # Website pages (6 routes)
    └── public/
        ├── css/project.css       # Styling for website pages
        └── js/project.js         # Client-side interactivity
```

### Key Hooks

All configuration is in `hooks.py`:

```python
# Document Events — validate, before_submit, on_update, etc.
doc_events = {
    "Project Update": {
        "validate": "project_tracker.utils.workflow.validate_project_update",
        "before_submit": "project_tracker.utils.workflow.before_submit_handler",
        "on_update": "project_tracker.utils.workflow.on_update_handler",
        "after_insert": "project_tracker.utils.workflow.after_insert_handler",
        "on_cancel": "project_tracker.utils.workflow.on_cancel_handler",
    }
}

# Custom permission hooks
has_permission = {
    "Project Update": "project_tracker.utils.permissions.has_permission",
}
permission_query_conditions = {
    "Project Update": "project_tracker.utils.permissions.get_permission_query_conditions",
}

# Scheduler
scheduler_events = {
    "daily": ["project_tracker.utils.notifications.send_daily_update_reminders"],
    "hourly": ["project_tracker.utils.notifications.check_pending_approvals"],
}
```

### Extending the App

To add custom fields to the standard ERPNext **Project** doctype (e.g., a GitHub repo link at the project level), add to `hooks.py`:

```python
custom_fields = {
    "Project": [
        {
            "fieldname": "custom_github_repo_link",
            "fieldtype": "Data",
            "label": "GitHub Repo Link",
            "options": "URL",
            "insert_after": "project_name",
        }
    ]
}
```

The app already supports auto-populating this field into Project Updates if it exists.

---

## 📄 License

MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions...

---

> Built for ERPNext v15+ | [GitHub Repository](https://github.com/balaji-001-gif/project_tracker)
