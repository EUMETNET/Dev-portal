"""
Global constants used in the application.
"""

# This value must match with the key name in VaultUser (app.models.vault.VaultUser)
# In other words there must be a key that equals this value
VAULT_API_KEY_FIELD_NAME = "auth_key"

USER_GROUP = "User"

EUMETNET_USER_GROUP = "EumetnetUser"

ADMIN_GROUP = "Admin"

GROUPS = [USER_GROUP, EUMETNET_USER_GROUP, ADMIN_GROUP]
