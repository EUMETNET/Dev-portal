# Keycloak Custom Theme

Custom Keycloak theme for the MeteoGate Dev Portal with GDPR compliance features.

## Purpose

Provides a branded login experience with:
- Custom MeteoGate branding and styling
- GDPR-compliant Terms & Conditions acceptance

## Theme Structure

```
keycloak/
├── Dockerfile              # Builds theme as a Docker image
└── themes/
    └── gdpr-theme/
        └── login/
            ├── theme.properties      # Theme configuration
            ├── login.ftl             # Login page template
            ├── terms.ftl             # Terms & Conditions page
            └── resources/
                ├── css/              # Custom styles
                ├── fonts/            # Custom fonts
                ├── img/              # Images and logos
                └── js/               # JavaScript
```

## Applying the Theme

### Configure in Keycloak Admin UI

1. Navigate to http://localhost:8080/admin
2. Login with admin credentials (`admin`/`admin`)
3. Select the **meteogate** realm
4. Go to **Realm Settings** → **Themes**
5. Set **Login theme** to `gdpr-theme`
6. Click **Save**

## Required Keycloak Configuration

### Enable Required Action

To display the Terms & Conditions page to users, enable the **Terms and Conditions** required action:

1. Go to **Authentication** → **Required Actions**
2. Find **Terms and Conditions**
3. Check **Enabled**
4. Check **Default Action**
5. Click **Save**

To apply the **Terms and Conditions** required action to any existing users:

1. Go to **Users** in the left sidebar
2. Find and click on the user
3. Go to the **Required Actions** tab
4. Select **Terms and Conditions** from the dropdown
5. Click **Add**
6. Click **Save**

**Bulk action:** To apply to all users, use the Keycloak REST API.

## References

- [Keycloak Documentation](https://www.keycloak.org/docs/latest/server_development/)
- [Working with themes](https://www.keycloak.org/ui-customization/themes)