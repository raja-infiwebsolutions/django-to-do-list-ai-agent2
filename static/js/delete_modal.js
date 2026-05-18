document.addEventListener('DOMContentLoaded', function () {
  var deleteModalEl = document.getElementById('deleteModal');
  if (!deleteModalEl) return;

  // Safe guard to avoid duplicate listeners
  if (deleteModalEl.dataset.deleteInit === '1') return;
  deleteModalEl.dataset.deleteInit = '1';

  deleteModalEl.addEventListener('show.bs.modal', function (event) {
    var button = event.relatedTarget; // Button that triggered the modal
    if (!button) return;
    var title = button.getAttribute('data-title') || 'this item';
    var url = button.getAttribute('data-url') || '#';
    var form = deleteModalEl.querySelector('#deleteForm');
    var nameEl = deleteModalEl.querySelector('#deleteItemName');
    if (form) form.action = url;
    if (nameEl) nameEl.textContent = title;
  });
});