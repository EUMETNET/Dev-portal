const errorMessageDiv = document.getElementById('error-message');
const form = document.getElementById('kc-terms-form');

form.addEventListener('submit', function(e) {
    const submitButton = e.submitter || document.activeElement;

    // Check if user clicked "Accept" button
    if (submitButton && submitButton.name === 'accept') {
        const systemUpdates = document.getElementById('system-updates-consent').checked;
        const dataUsage = document.getElementById('data-usage-consent').checked;
        
        // Require BOTH checkboxes to be checked
        if (!systemUpdates || !dataUsage) {
            e.preventDefault();
            // Show error message
            errorMessageDiv.textContent = '⚠️ Please accept both of the terms to continue.';
            errorMessageDiv.classList.add('visible');
            // Scroll to error message
            errorMessageDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
            return false;
        }
    }
    // Hide error message on valid submission
    errorMessageDiv.classList.remove('visible');
    return true;
});

// Hide error message when user checks both checkboxes
const checkboxes = document.querySelectorAll('input[type="checkbox"]');
checkboxes.forEach(checkbox => {
    checkbox.addEventListener('change', function() {
        const systemUpdates = document.getElementById('system-updates-consent').checked;
        const dataUsage = document.getElementById('data-usage-consent').checked;
        
        // Hide error only when BOTH are checked
        if (systemUpdates && dataUsage) {
            errorMessageDiv.classList.remove('visible');
        }
    });
});