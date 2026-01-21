<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>MeteoGate - Terms and Conditions</title>
    <style>
        /* Font Faces (matching Dev Portal) */
        @font-face {
            font-family: 'Exo 2';
            font-style: normal;
            font-weight: 400;
            font-display: swap;
            src: url('${url.resourcesPath}/fonts/exo-2-v26-latin-regular.woff2') format('woff2');
        }

        @font-face {
            font-family: 'Exo 2';
            font-style: normal;
            font-weight: 600;
            font-display: swap;
            src: url('${url.resourcesPath}/fonts/exo-2-v26-latin-600.woff2') format('woff2');
        }

        @font-face {
            font-family: 'Heebo';
            font-style: normal;
            font-weight: 400;
            font-display: swap;
            src: url('${url.resourcesPath}/fonts/heebo-v28-latin-regular.woff2') format('woff2');
        }

        @font-face {
            font-family: 'Heebo';
            font-style: normal;
            font-weight: 600;
            font-display: swap;
            src: url('${url.resourcesPath}/fonts/heebo-v28-latin-600.woff2') format('woff2');
        }
        /* Color Variables (matching Dev Portal) */
        :root {
            --color-sherpa100: #D9F4F4;
            --color-sherpa200: #B8E8E9;
            --color-sherpa300: #86D6DA;
            --color-sherpa400: #63CBCF;
            --color-sherpa500: #009AA1;
            --color-sherpa600: #087a82;
            --color-sherpa700: #0C646D;
            --color-sherpa800: #004F59;
            --color-sherpa900: #0C3B41;
            --color-white: #FFFFFF;
            --color-black: #000000;
            --color-yellow: #F1B828;
        }

        /* Reset and Base Styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html {
            height: 100%;
        }

        body {
            font-family: 'Heebo', sans-serif;
            background: #0C3B41;
            min-height: 100%;
            margin: 0;
            display: flex;
            flex-direction: column;
        }

        /* Main Wrapper - Push footer to bottom */
        #page-wrapper {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: linear-gradient(180deg, rgba(0, 0, 0, 0.30) 0%, rgba(0, 0, 0, 0.00) 15.58%),
                        radial-gradient(68.05% 68.05% at 50.79% 4.4%, rgba(12, 59, 65, 0.30) 0%, rgba(12, 59, 65, 0.00) 100%);
        }

        /* Container */
        #kc-terms {
            max-width: 1280px;
            margin: 0 auto;
            padding: 0 40px;
            width: 100%;
            flex: 1;
        }

        /* Header Wrapper (matching Dev Portal Header.css) */
        .header-wrapper {
            width: 100%;
            padding: 48px 0 32px 0;
            background: transparent;
        }

        /* Logos Container */
        .header-logos {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 32px;
        }

        .header-logo-left img {
            height: 32px;
            width: auto;
        }

        .header-logo-right img {
            height: 56px;
            width: auto;
        }

        /* Header Content (Title Section) */
        .header-content {
            text-align: center;
            padding-top: 32px;
            border-top: 1px solid var(--color-white);
        }

        .header-content h1 {
            color: var(--color-white);
            font-family: "Exo 2", sans-serif;
            font-size: 48px;
            font-weight: 600;
            line-height: 48px;
            margin: 0 0 16px 0;
            padding-bottom: 32px;
        }

        .header-content .subtitle {
            color: var(--color-white);
            font-family: "Exo 2", sans-serif;
            font-size: 36px;
            font-weight: 600;
            line-height: 36px;
            margin: 0;
            padding-top: 36px;
            border-top: 1px solid var(--color-white);
        }

        /* Highlighted text in subtitle */
        .header-content .subtitle .highlight {
            color: var(--color-sherpa400);
        }

        /* Description */
        .description {
            color: var(--color-sherpa200);
            font-size: 16px;
            line-height: 24px;
            max-width: 600px;
            margin: 24px auto 0 auto;
            text-align: center;
        }

        /* Main Content */
        #content-container {
            display: flex;
            justify-content: center;
            padding: 40px 0 80px 0;
        }

        /* Consent Box - Centered */
        .consent-box {
            background: var(--color-sherpa800);
            border: 1px solid var(--color-sherpa600);
            border-radius: 8px;
            padding: 40px;
            max-width: 700px;
            width: 100%;
        }

        .consent-box h2 {
            color: var(--color-white);
            font-family: "Exo 2", sans-serif;
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 24px;
            text-align: center;
        }

        /* Consent Checkboxes */
        .consent-item {
            background: rgba(255, 255, 255, 0.05);
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 16px;
            border: 2px solid transparent;
            transition: all 0.3s ease;
        }

        .consent-item:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: var(--color-sherpa400);
        }

        .consent-checkbox {
            display: flex;
            align-items: flex-start;
            gap: 12px;
            cursor: pointer;
        }

        .consent-checkbox input[type="checkbox"] {
            width: 20px;
            height: 20px;
            cursor: pointer;
            margin-top: 2px;
            flex-shrink: 0;
            accent-color: var(--color-sherpa400);
        }

        .consent-text {
            flex: 1;
            color: var(--color-white);
            font-size: 16px;
            line-height: 24px;
        }

        /* Button Container */
        .button-container {
            display: flex;
            gap: 16px;
            margin-top: 32px;
        }

        /* Buttons (matching Dev Portal btn--green) */
        button.btn-accept {
            flex: 1;
            padding: 14px 24px;
            border-radius: 4px;
            border: 4px solid var(--color-white);
            background: var(--color-white);
            color: var(--color-sherpa800);
            font-family: Heebo, sans-serif;
            font-size: 16px;
            font-weight: 600;
            line-height: 24px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        button.btn-accept:hover {
            background: var(--color-sherpa200);
        }

        button.btn-accept:active {
            background: var(--color-sherpa300);
        }

        button.btn-accept:focus {
            border-color: var(--color-yellow);
            outline: none;
        }

        button.btn-decline {
            flex: 1;
            padding: 14px 24px;
            border-radius: 4px;
            border: 4px solid var(--color-white);
            background: transparent;
            color: var(--color-white);
            font-family: Heebo, sans-serif;
            font-size: 16px;
            font-weight: 600;
            line-height: 24px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        button.btn-decline:hover {
            background: rgba(255, 255, 255, 0.1);
            border-width: 2px;
            padding: 15px 25px;
        }

        button.btn-decline:focus {
            border-color: var(--color-yellow);
            outline: none;
        }

        /* Error Message */
        .error-message {
            background: #fff3cd;
            border: 2px solid #ffc107;
            border-radius: 8px;
            padding: 15px;
            margin: 20px auto;
            color: #856404;
            font-weight: 600;
            text-align: center;
            display: none;
        }

        .error-message.visible {
            display: block;
        }

        /* Footer - Full Width, Sticky to Bottom */
        .footer-container {
            width: 100%;
            background: #00282D;
            padding: 64px 0;
            border-top: 1px solid var(--color-sherpa600);
            margin-top: auto;
        }

        .footer-content {
            max-width: 1280px;
            margin: 0 auto;
            padding: 0 40px;
        }

        .footer-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }

        .footer-content p {
            color: var(--color-sherpa400);
            font-family: Heebo, sans-serif;
            font-size: 16px;
            font-weight: 400;
            line-height: 24px;
            margin: 0;
        }

        .footer-content a {
            color: var(--color-sherpa400);
            text-decoration: none;
            font-family: Heebo, sans-serif;
            font-size: 16px;
            transition: color 0.3s ease;
        }

        .footer-content a:hover {
            color: var(--color-white);
            text-decoration: underline;
        }

        /* Responsive - Tablet */
        @media (min-width: 600px) and (max-width: 1023px) {
            #kc-terms {
                padding: 0 32px;
            }

            .header-wrapper {
                padding: 40px 0 24px 0;
            }

            .header-logos {
                padding-bottom: 24px;
            }

            .header-logo-left img {
                height: 28px;
            }

            .header-logo-right img {
                height: 48px;
            }

            .header-content {
                padding-top: 24px;
            }

            .header-content h1 {
                font-size: 38px;
                line-height: 44px;
            }

            .header-content .subtitle {
                font-size: 28px;
                line-height: 32px;
            }

            .consent-box {
                padding: 32px;
            }

            .footer-content {
                padding: 0 32px;
            }
        }

        /* Responsive - Mobile */
        @media (max-width: 599px) {
            #kc-terms {
                padding: 0 20px;
            }

            .header-wrapper {
                padding: 24px 0;
            }

            .header-logos {
                flex-direction: column;
                gap: 24px;
                padding-bottom: 24px;
            }

            .header-logo-left img {
                height: 24px;
            }

            .header-logo-right img {
                height: 40px;
            }

            .header-content {
                padding-top: 24px;
            }

            .header-content h1 {
                font-size: 32px;
                line-height: 36px;
            }

            .header-content .subtitle {
                font-size: 24px;
                line-height: 28px;
            }

            .consent-box {
                padding: 24px;
            }

            .button-container {
                flex-direction: column;
            }

            button.btn-accept,
            button.btn-decline {
                width: 100%;
            }

            .footer-container {
                padding: 40px 0;
            }

            .footer-content {
                padding: 0 20px;
            }

            .footer-row {
                flex-direction: column;
                align-items: flex-start;
                gap: 16px;
            }

            .footer-content p,
            .footer-content a {
                font-size: 14px;
                line-height: 20px;
            }
        }
    </style>
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