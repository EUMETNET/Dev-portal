"""
APISix test data
"""

ROUTES = [
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
                "count": 20,
                "time_window": 60,
                "key": "consumer_name",
                "rejected_code": 429
            },
            "proxy-rewrite": {
                "regex_uri": ["^/bar(.*)", "/$1"]
            }
        },
        "upstream": {"type": "roundrobin", "nodes": {"httpbin.org:80": 1}, "scheme": "http"},
    },
    {
        "id": "foo",
        "uri": "/foo",
        "plugins": {
            "key-auth": {},
            "limit-req": {
                "rate": 20,
                "burst": 40,
                "key": "consumer_name",
                "rejected_code": 429
            },
            "limit-count": {
                "count": 200,
                "time_window": 60,
                "key": "consumer_name",
                "rejected_code": 429
            },
            "proxy-rewrite": {
                "regex_uri": ["^/foo(.*)", "/$1"]
            }
        },
        "upstream": {"type": "roundrobin", "nodes": {"httpbin.org:80": 1}, "scheme": "http"},
    },
    {
        "id": "baz",
        "uri": "/baz",
        "plugins": {
            "proxy-rewrite": {
                "regex_uri": ["^/baz(.*)", "/$1"]
            }
        },
        "upstream": {"type": "roundrobin", "nodes": {"httpbin.org:80": 1}, "scheme": "http"},
    },
    {
        "id": "qux",
        "uri": "/qux",
        "plugins": {
            "key-auth": {},
            "proxy-rewrite": {
                "regex_uri": ["^/qux(.*)", "/$1"]
            }
        },
        "upstream": {"type": "roundrobin", "nodes": {"httpbin.org:80": 1}, "scheme": "http"},
    },
]
