<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>MeteoGate - Terms and Conditions</title>
    <link href="${url.resourcesPath}/css/custom-common.css" rel="stylesheet" />
    <link href="${url.resourcesPath}/css/custom-terms.css" rel="stylesheet" />
</head>
<body>
    <div id="page-wrapper">
        <div id="kc-terms">
            <!-- Header (matching Dev Portal) -->
            <div class="header-wrapper">
                <div class="header-logos">
                    <div class="header-logo-left">
                        <img src="${url.resourcesPath}/img/eumetnet_meteogate-logo.svg" alt="MeteoGate Logo" />
                    </div>
                    <div class="header-logo-right">
                        <img src="${url.resourcesPath}/img/co-funded_by_the_eu_white.png" alt="Co-funded by the European Union" />
                    </div>
                </div>
                <div class="header-content">
                    <h1>MeteoGate</h1>
                    <p class="subtitle">
                        <span class="highlight">Secure</span> access to your <span class="highlight">MeteoGate</span> data and services
                    </p>
                </div>
            </div>

            <!-- Description -->
            <p class="description">Please review the terms and conditions to continue.</p>

            <!-- Error Message -->
            <div id="error-message" class="error-message <#if message?has_content && message.type = 'error'>visible</#if>">
                <#if message?has_content && message.type = 'error'>
                    ⚠️ ${kcSanitize(message.summary)?no_esc}
                <#else>
                    ⚠️ Please accept both of the terms to continue.
                </#if>
            </div>

            <!-- Main Content - Centered -->
            <div id="content-container">
                <div class="consent-box">
                    <h2>Terms and Conditions</h2>
                    
                    <form id="kc-terms-form" action="${url.loginAction}" method="post">
                        <!-- First Consent Checkbox -->
                        <div class="consent-item">
                            <label class="consent-checkbox">
                                <input type="checkbox" 
                                       id="system-updates-consent" 
                                       name="system-updates-consent" />
                                <span class="consent-text">
                                    I agree that the MeteoGate operators can contact me with information 
                                    such as system updates and issues
                                </span>
                            </label>
                        </div>

                        <!-- Second Consent Checkbox -->
                        <div class="consent-item">
                            <label class="consent-checkbox">
                                <input type="checkbox" 
                                       id="data-usage-consent" 
                                       name="data-usage-consent" />
                                <span class="consent-text">
                                    I agree that the MeteoGate owners can contact me to find out more 
                                    about my data usage interests
                                </span>
                            </label>
                        </div>

                        <!-- Action Buttons -->
                        <div class="button-container">
                            <button type="submit" name="accept" class="btn-accept">I Accept</button>
                            <button type="submit" name="cancel" class="btn-decline">I Decline</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <!-- Footer (moved OUTSIDE #kc-terms for full width) -->
        <div class="footer-container">
            <div class="footer-content">
                <div class="footer-row">
                    <p>Copyright EUMETNET SNC ©2026</p>
                    <a href="https://www.eumetnet.eu/legal-information" target="_blank" rel="noopener noreferrer">Legal information</a>
                </div>
            </div>
        </div>
    </div>

    <script type="text/javascript">
        const errorMessageDiv = document.getElementById('error-message');
        const form = document.getElementById('kc-terms-form');
        
        form.addEventListener('submit', function(e) {
            const acceptButton = e.submitter;
            
            if (acceptButton && acceptButton.name === 'accept') {
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
    </script>
</body>
</html>