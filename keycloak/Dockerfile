FROM busybox:1.36.1

# Copy theme files
COPY themes/gdpr-theme /theme/gdpr-theme
COPY themes/gdpr-theme-only-idp /theme/gdpr-theme-only-idp

# Verify critical files exist (catches build errors early)
RUN test -f /theme/gdpr-theme/login/theme.properties && \
    test -f /theme/gdpr-theme/login/login.ftl && \
    test -f /theme/gdpr-theme/login/terms.ftl && \
    test -f /theme/gdpr-theme/login/resources/css/custom-common.css && \
    test -f /theme/gdpr-theme/login/resources/css/custom-login.css && \
    test -f /theme/gdpr-theme/login/resources/css/custom-terms.css && \
    test -d /theme/gdpr-theme/login/resources/fonts && \
    test -d /theme/gdpr-theme/login/resources/img && \
    test -f /theme/gdpr-theme/login/resources/js/custom-terms.js && \
    test -f /theme/gdpr-theme-only-idp/login/theme.properties && \
    test -f /theme/gdpr-theme-only-idp/login/login.ftl && \
    test -f /theme/gdpr-theme-only-idp/login/terms.ftl && \
    test -f /theme/gdpr-theme-only-idp/login/resources/css/custom-common.css && \
    test -f /theme/gdpr-theme-only-idp/login/resources/css/custom-login.css && \
    test -f /theme/gdpr-theme-only-idp/login/resources/css/custom-terms.css && \
    test -d /theme/gdpr-theme-only-idp/login/resources/fonts && \
    test -d /theme/gdpr-theme-only-idp/login/resources/img && \
    test -f /theme/gdpr-theme-only-idp/login/resources/js/custom-terms.js && \
    echo "✓ Theme files verified successfully"
