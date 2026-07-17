// Project Tracker website JS
$(document).ready(function() {
  // Search filter on project list
  $('#put-search').on('input', function() {
    const term = $(this).val().toLowerCase();
    $('.project-card').each(function() {
      const text = $(this).text().toLowerCase();
      $(this).toggle(text.includes(term));
    });
  });

  // Status filter
  $('#put-status-filter').on('change', function() {
    const val = $(this).val().toLowerCase();
    $('.project-card').each(function() {
      if (!val) { $(this).show(); return; }
      const status = $(this).data('status') || '';
      $(this).toggle(status.includes(val));
    });
  });

  // Update form submit
  $('#put-update-form').on('submit', function(e) {
    e.preventDefault();
    const formData = {};
    $(this).serializeArray().forEach(item => {
      formData[item.name] = item.value;
    });

    // Convert checkboxes
    formData.needs_attention = $('input[name=needs_attention]').is(':checked') ? 1 : 0;
    formData.cmd = 'project_tracker.api.project_api.create_update';

    frappe.call({
      method: formData.cmd,
      args: formData,
      callback: function(r) {
        if (r.exc) {
          frappe.msgprint(r.exc);
        } else {
          frappe.msgprint({
            title: 'Success',
            indicator: 'green',
            message: 'Update created. Submitting for L1 approval...'
          });
          // Now submit for L1
          frappe.call({
            method: 'project_tracker.api.approval_api.submit_for_l1',
            args: { name: r.message },
            callback: function(r2) {
              if (r2.exc) {
                frappe.msgprint(r2.exc);
              } else {
                window.location.href = '/projects/my';
              }
            }
          });
        }
      }
    });
  });
});
