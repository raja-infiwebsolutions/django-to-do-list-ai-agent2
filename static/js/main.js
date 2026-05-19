/**
 * Main application JavaScript
 * Handles common functionality across all pages
 */

document.addEventListener('DOMContentLoaded', function() {
  // Initialize tooltips
  initializeTooltips();
  
  // Setup form handling
  setupFormHandling();
  
  // Initialize alerts auto-dismiss
  initializeAlerts();
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
}

/**
 * Setup form validation and handling
 */
function setupFormHandling() {
  const forms = document.querySelectorAll('form[novalidate]');
  
  forms.forEach(form => {
    form.addEventListener('submit', function(e) {
      // Show loading state if form has submit button
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        const submitSpinner = submitBtn.querySelector('.spinner-border');
        const submitText = submitBtn.querySelector('#submitText');
        
        if (submitSpinner) {
          submitSpinner.classList.remove('d-none');
        }
        submitBtn.disabled = true;
        
        if (submitText) {
          submitText.textContent = submitText.textContent.replace(/Create|Update/, 'Saving');
        }
      }
    });
  });
}

/**
 * Initialize auto-dismissing alerts
 */
function initializeAlerts() {
  const alerts = document.querySelectorAll('.alert:not(.alert-persistent)');
  
  alerts.forEach(alert => {
    // Auto dismiss after 5 seconds
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 5000);
  });
}

/**
 * Get CSRF token from DOM
 * @returns {string} CSRF token
 */
function getCsrfToken() {
  return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

/**
 * Make AJAX request with proper headers
 * @param {string} url - Request URL
 * @param {object} options - Fetch options
 * @returns {Promise} Fetch promise
 */
function makeRequest(url, options = {}) {
  const defaultHeaders = {
    'X-CSRFToken': getCsrfToken(),
    'X-Requested-With': 'XMLHttpRequest',
  };
  
  return fetch(url, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });
}

/**
 * Show notification
 * @param {string} message - Message to display
 * @param {string} type - Notification type (success, error, warning, info)
 * @param {number} duration - Duration in milliseconds (0 = persistent)
 */
function showNotification(message, type = 'info', duration = 5000) {
  const alertHTML = `
    <div class="alert alert-${type} alert-dismissible fade show" role="alert">
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
  `;
  
  const mainContent = document.querySelector('main#main-content');
  const alertContainer = mainContent?.querySelector('div:first-child') || mainContent;
  
  if (alertContainer) {
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = alertHTML;
    const alert = tempDiv.firstElementChild;
    alertContainer.insertAdjacentElement('afterbegin', alert);
    
    if (duration > 0) {
      setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
      }, duration);
    }
  }
}

/**
 * Format date for display
 * @param {Date|string} date - Date to format
 * @param {string} format - Format pattern (e.g., 'M j, Y')
 * @returns {string} Formatted date
 */
function formatDate(date, format = 'M j, Y') {
  if (typeof date === 'string') {
    date = new Date(date);
  }
  
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  
  return format
    .replace('M', months[date.getMonth()])
    .replace('m', String(date.getMonth() + 1).padStart(2, '0'))
    .replace('j', date.getDate())
    .replace('d', String(date.getDate()).padStart(2, '0'))
    .replace('Y', date.getFullYear());
}

// Export for use in other scripts
window.appUtils = {
  getCsrfToken,
  makeRequest,
  showNotification,
  formatDate,
};
