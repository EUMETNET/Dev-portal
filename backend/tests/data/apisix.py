"""
APISix test data
"""

ROUTES = [
    {
        "id": "foo",
        "uri": "/foo",
        "plugins": {
            "key-auth": {},
            "limit-req": {
                "rate": 5,
                "burst": 10,
                "key": "consumer_name",
                "rejected_code": 429
            },
            "limit-count": {
                "count": 5,
                "time_window": 60,
                "key": "consumer_name",
                "rejected_code": 429
            },
            "proxy-rewrite": {"uri": "/"}
        },
        "upstream": {"type": "roundrobin", "nodes": {"httpbin.org:80": 1}, "scheme": "http"},
    },
    {
        "id": "bar",
        "uri": "/bar",
        "plugins": {
            "key-auth": {},
            "limit-req": {
                "rate": 10,
                "burst": 20,
                "key": "consumer_name",
                "rejected_code": 429
            },
            "limit-count": {
                "count": 10,
                "time_window": 60,
                "key": "consumer_name",
                "rejected_code": 429
            },
            "proxy-rewrite": {"uri": "/"}
        },
        "upstream": {"type": "roundrobin", "nodes": {"httpbin.org:80": 1}, "scheme": "http"},
    },
    {
        "id": "baz",
        "uri": "/baz",
        "plugins": {},
        "upstream": {"type": "roundrobin", "nodes": {"httpbin.org:80": 1}, "scheme": "http"},
    },
    {
        "id": "qux",
        "uri": "/qux",
        "plugins": {
            "key-auth": {},
            "proxy-rewrite": {"uri": "/"}
        },
        "upstream": {"type": "roundrobin", "nodes": {"httpbin.org:80": 1}, "scheme": "http"},
    },
]
