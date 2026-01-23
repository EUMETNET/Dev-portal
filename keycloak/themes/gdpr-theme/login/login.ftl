<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>MeteoGate - Login</title>
    <link href="${url.resourcesPath}/css/custom-common.css" rel="stylesheet" />
    <link href="${url.resourcesPath}/css/custom-login.css" rel="stylesheet" />
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