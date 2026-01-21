<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>MeteoGate - Login</title>
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
        #kc-login {
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

        /* Login Box */
        .login-box {
            background: var(--color-sherpa800);
            border: 1px solid var(--color-sherpa600);
            border-radius: 8px;
            padding: 40px;
            max-width: 500px;
            width: 100%;
        }

        .login-box h2 {
            color: var(--color-white);
            font-family: "Exo 2", sans-serif;
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 24px;
            text-align: center;
        }

        /* Form Styles */
        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            color: var(--color-sherpa200);
            font-size: 14px;
            margin-bottom: 8px;
            font-weight: 600;
        }

        input[type="text"],
        input[type="password"] {
            width: 100%;
            padding: 12px;
            border: 2px solid var(--color-sherpa600);
            border-radius: 4px;
            background: rgba(255, 255, 255, 0.1);
            color: var(--color-white);
            font-size: 16px;
        }

        input[type="text"]:focus,
        input[type="password"]:focus {
            outline: none;
            border-color: var(--color-sherpa400);
        }

        /* Login Button (matching Dev Portal btn--green) */
        button.btn-login {
            width: 100%;
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

        button.btn-login:hover {
            background: var(--color-sherpa200);
        }

        button.btn-login:active {
            background: var(--color-sherpa300);
        }

        button.btn-login:focus {
            border-color: var(--color-yellow);
            outline: none;
        }

        /* Social Login */
        .social-login {
            margin-top: 30px;
            padding-top: 30px;
            border-top: 1px solid var(--color-sherpa600);
        }

        .social-login p {
            color: var(--color-sherpa200);
            text-align: center;
            margin-bottom: 15px;
            font-weight: 600;
        }

        .social-btn {
            width: 100%;
            padding: 12px;
            margin-bottom: 10px;
            border: 2px solid var(--color-sherpa600);
            border-radius: 4px;
            background: rgba(255, 255, 255, 0.1);
            color: var(--color-white);
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .social-btn:hover {
            background: rgba(255, 255, 255, 0.2);
            border-color: var(--color-sherpa400);
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
            #kc-login {
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

            .login-box {
                padding: 32px;
            }

            .footer-content {
                padding: 0 32px;
            }
        }

        /* Responsive - Mobile */
        @media (max-width: 599px) {
            #kc-login {
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

            .login-box {
                padding: 24px;
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
        <div id="kc-login">
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
            <p class="description">Please sign in to continue.</p>

            <!-- Error Message -->
            <#if message?has_content && (message.type != 'warning' || !isAppInitiatedAction??)>
                <div class="error-message">
                    ⚠️ ${kcSanitize(message.summary)?no_esc}
                </div>
            </#if>

            <!-- Main Content -->
            <div id="content-container">
                <div class="login-box">
                    <h2>Sign In</h2>
                    
                    <form id="kc-form-login" action="${url.loginAction}" method="post">
                        <div class="form-group">
                            <label for="username">
                                <#if !realm.loginWithEmailAllowed>${msg("username")}<#elseif !realm.registrationEmailAsUsername>${msg("usernameOrEmail")}<#else>${msg("email")}</#if>
                            </label>
                            <input 
                                type="text" 
                                id="username" 
                                name="username" 
                                value="${(login.username!'')}"
                                autofocus
                                autocomplete="off"
                            />
                        </div>

                        <div class="form-group">
                            <label for="password">${msg("password")}</label>
                            <input 
                                type="password" 
                                id="password" 
                                name="password"
                                autocomplete="off"
                            />
                        </div>

                        <button type="submit" class="btn-login">Sign In</button>
                    </form>

                    <!-- Social Login Options -->
                    <#if realm.password && social.providers??>
                        <div class="social-login">
                            <p>Or sign in with:</p>
                            <#list social.providers as p>
                                <form action="${p.loginUrl}" method="post">
                                    <button type="submit" class="social-btn">
                                        ${p.displayName}
                                    </button>
                                </form>
                            </#list>
                        </div>
                    </#if>
                </div>
            </div>
        </div>

        <!-- Footer (moved OUTSIDE #kc-login for full width) -->
        <div class="footer-container">
            <div class="footer-content">
                <div class="footer-row">
                    <p>Copyright EUMETNET SNC ©2026</p>
                    <a href="https://www.eumetnet.eu/legal-information" target="_blank" rel="noopener noreferrer">Legal information</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>