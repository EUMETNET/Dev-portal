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
3. Go to **Manage realms** and select the **meteogate** realm
4. Go to **Realm Settings** → **Themes** tab
5. Set **Login theme** to `gdpr-theme`
6. Click **Save**

## Required Keycloak Configuration

### Enable Required Action

To display the Terms & Conditions page to users, enable the **Terms and Conditions** required action:

1. Go to **Manage realms** and select the **meteogate** realm
2. Go to **Authentication** → **Required actions** tab
3. Find **Terms and Conditions**
4. Check **Enabled**
5. Check **Set as default action**

To apply the **Terms and Conditions** required action to any existing users:

1. Go to **Users**
2. Find and click on the user
3. Select **Terms and Conditions** from the **Required user actions** dropdown
4. Click **Save**

**Bulk action:** To apply to all users, use the Keycloak REST API.

## References

- [Keycloak Documentation](https://www.keycloak.org/docs/latest/server_development/)
- [Working with themes](https://www.keycloak.org/ui-customization/themes)
- [Theme CI/CD Workflow](../.github/workflows/keycloak_theme_ci_cd.yml)