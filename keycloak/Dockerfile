FROM busybox:1.36.1

# Copy theme files
COPY themes/gdpr-theme /theme/gdpr-theme

# Verify critical files exist (catches build errors early)
RUN test -f /theme/gdpr-theme/login/theme.properties && \
    test -f /theme/gdpr-theme/login/login.ftl && \
    test -f /theme/gdpr-theme/login/terms.ftl && \
    test -d /theme/gdpr-theme/login/resources/fonts && \
    test -d /theme/gdpr-theme/login/resources/img && \
    echo "✓ Theme files verified successfully"