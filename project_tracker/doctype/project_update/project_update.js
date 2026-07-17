// Client-side logic for Project Update doctype (desk view)

frappe.ui.form.on("Project Update", {
    setup: function(frm) {
        frm.set_query("project", function() {
            return {
                filters: {
                    status: ["not in", ["Completed", "Cancelled"]]
                }
            };
        });

        frm.set_query("team_member", function() {
            return {
                query: "project_tracker.api.project_api.get_project_users_query"
            };
        });
    },

    refresh: function(frm) {
        // Show approval buttons only when relevant
        if (frm.doc.docstatus === 0 && frm.doc.workflow_state === "Draft") {
            frm.add_custom_button(__("Submit for L1 Approval"), function() {
                frappe.call({
                    method: "project_tracker.api.approval_api.submit_for_l1",
                    args: { name: frm.doc.name },
                    callback: function(r) {
                        if (!r.exc) {
                            frm.reload_doc();
                        }
                    }
                });
            }).addClass("btn-primary");
        }

        if (frm.doc.workflow_state === "Rejected" && frappe.has_role("Project Team Member")) {
            frm.add_custom_button(__("Resubmit"), function() {
                frappe.call({
                    method: "project_tracker.api.approval_api.resubmit_update",
                    args: { name: frm.doc.name },
                    callback: function(r) {
                        if (!r.exc) frm.reload_doc();
                    }
                });
            }).addClass("btn-warning");
        }

        // Show publish button when approved
        if (frm.doc.workflow_state === "Approved" && !frm.doc.is_published) {
            frm.add_custom_button(__("Publish (View-Only)"), function() {
                frappe.call({
                    method: "project_tracker.api.approval_api.publish_update",
                    args: { name: frm.doc.name },
                    callback: function(r) {
                        if (!r.exc) frm.reload_doc();
                    }
                });
            }).addClass("btn-success");
        }
    },

    project: function(frm) {
        if (frm.doc.project) {
            frappe.db.get_value("Project", frm.doc.project, ["project_name", "expected_end_date", "custom_github_repo_link"])
                .then(r => {
                    if (r && r.message) {
                        frm.set_value("project_name", r.message.project_name);
                        frm.set_value("planned_end_date", r.message.expected_end_date);
                        if (r.message.custom_github_repo_link) {
                            frm.set_value("github_repo_link", r.message.custom_github_repo_link);
                        }
                    }
                });
        }
    },

    blocker_severity: function(frm) {
        if (frm.doc.blocker_severity === "Critical") {
            frm.set_value("needs_attention", 1);
        }
    }
});
