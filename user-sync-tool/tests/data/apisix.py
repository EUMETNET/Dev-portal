"""
APISix test data
"""

# lisää tänne testikäyttäjiä jsonin mukaisesti
CONSUMERS: list = [
    {
        "create_time": "1234567890",
        "username": "00000000000000000001a",
        "plugins": {"key-auth": {"key": "$secret://vault/1/00000000000000000001a/auth_key"}},
        "update_time": "1234567890",
        "key": "",
        "modifiedIndex": "002",
        "createdIndex": "002",
    },
    {
        "create_time": "1234567891",
        "username": "00000000000000000002b",
        "plugins": {"key-auth": {"key": "$secret://vault/1/00000000000000000002b/auth_key"}},
        "update_time": "1234567891",
        "key": "",
        "modifiedIndex": "003",
        "createdIndex": "003",
    },
    {
        "create_time": "1234567892",
        "username": "00000000000000000003c",
        "plugins": {"key-auth": {"key": "$secret://vault/1/00000000000000000003c/auth_key"}},
        "update_time": "1234567892",
        "key": "",
        "modifiedIndex": "004",
        "createdIndex": "004",
    },
    {
        "create_time": "1234567893",
        "username": "00000000000000000004d",
        "group_id": "EUMETNET_USER",
        "plugins": {"key-auth": {"key": "$secret://vault/1/00000000000000000004d/auth_key"}},
        "update_time": "1234567893",
        "key": "",
        "modifiedIndex": "005",
        "createdIndex": "005",
    },
]
