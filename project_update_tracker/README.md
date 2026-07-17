# Project Update Tracker

Advanced daily project update tool for ERPNext v15+ with:
- Daily project status updates
- Multi-level approval workflow (L1 → L2)
- Role-based permissions
- View-only access after completion
- Website screens for team (no desk needed)
- Backend desk view for crosscheck
- Email & in-app notifications
- Auto reminders via scheduler

## Installation

```bash
bench get-app https://github.com/yourorg/project_update_tracker
bench --site yoursite install-app project_update_tracker
bench --site yoursite migrate
bench --site yoursite clear-cache
```

## Roles

- Project Team Member
- Project Approver L1
- Project Approver L2
- Project Manager
- Project Viewer

## Workflow States

Draft → Pending L1 → Pending L2 → Approved → Completed → Published
  ↓           ↓
  Rejected    Rejected

## Website Routes

- /projects — All projects (view only)
- /projects/my — My projects
- /projects/view/<name> — Project detail
- /projects/update/<name> — Add daily update
- /projects/approvals — Approval queue
- /projects/review/<update> — Review update
