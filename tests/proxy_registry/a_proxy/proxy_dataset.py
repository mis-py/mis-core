from fastapi import status

positive_add_proxy_dataset = [
    (
        {
            "name": "test",
            "proxy_type": "http",
            "is_online": True,
            "is_enabled": True,
            "address": "http://HyZsLosLGDFIbKsO:mobile;ua;kyivstar;kyiv+city;kyiv@proxy.froxy.com:9191",
            "change_url": "http://test.test"
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "id": 1,
                "last_known_ip": None
            },
            "status": True
        }
    ),
]

negative_add_proxy_dataset = [
    (
        {},
        {
            "status_code": 422,
            "msg": "RequestValidationError",
            "result": [
                "Field required ('body', 'name')",
                "Field required ('body', 'address')",
                "Field required ('body', 'change_url')"
            ],
            "status": False
        }
    )
]

positive_get_proxy_dataset = [
    (
        {'proxy_id': 1},
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "address": "http://HyZsLosLGDFIbKsO:mobile;ua;kyivstar;kyiv+city;kyiv@proxy.froxy.com:9191",
                "change_url": "http://test.test",
            },
            "status": True
        }
    ),
]

negative_get_proxy_dataset = [
    (
        {'proxy_id': 0},
        {
            "status_code": 404,
            "msg": "NotFound",
            "result": "Proxy not found",
            "status": False,
        }
    )
]

positive_edit_proxy_dataset = [
    (
        {
            "proxy_id": 1,
        },
        {
            "name": "test",
            "proxy_type": "http",
            "is_online": True,
            "is_enabled": True,
            "address": "http://HyZsLosLGDFIbKsO:mobile;ua;kyivstar;kyiv+city;kyiv@proxy.froxy.com:9191",
            "change_url": "http://test.updated"
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "id": 1,
                "last_known_ip": None
            },
            "status": True
        }
    ),
]

negative_edit_proxy_dataset = [
    (
        {
            "proxy_id": 0,
        },
        {
            "name": "test",
            "proxy_type": "http",
            "is_online": True,
            "is_enabled": True,
            "address": "http://HyZsLosLGDFIbKsO:mobile;ua;kyivstar;kyiv+city;kyiv@proxy.froxy.com:9191",
            "change_url": "http://test.updated"
        },
        {
            "status_code": 404,
            "msg": "NotFound",
            "result": "Proxy not found",
            "status": False
        },
    )
]

positive_del_proxy_dataset = [
    (
        {
            "proxy_id": 1,
        },
        {
            "status_code": 204,
            "msg": "Success",
            "result": {},
            "status": False
        }
    ),
]

negative_del_proxy_dataset = [
    (
        {
            "proxy_id": 0,
        },
        {
            "status_code": 404,
            "msg": "NotFound",
            "result": "Proxy not found",
            "status": False
        },
    )
]

positive_check_proxy_dataset = [
    (
        {
            'id': 1,
            'proxy_address': None,
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "status": 200,
                "text": "46.211.66.180",
                "exceptions": []
            },
            "status": True
        },
    ),
]

negative_check_proxy_check = [
    (
        {'id': None, 'proxy_address': 'http://invalid.proxy'},
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "status": 0,
                "text": "",
                "exceptions": [...]  # ignored
            },
            "status": True
        }
    ),
]

positive_change_status_proxy_dataset = [
    (
        {'proxy_id': 1},
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "address": "http://HyZsLosLGDFIbKsO:mobile;ua;kyivstar;kyiv+city;kyiv@proxy.froxy.com:9191",
                "change_url": "http://test.updated"
            },
            "status": True,
        }
    ),
]

negative_change_status_proxy_check = [
    (
        {'proxy_id': 0},
        {
            "status_code": 404,
            "msg": "NotFound",
            "result": "Proxy not found",
            "status": False
        }
    ),

]

add_proxy_dataset = positive_add_proxy_dataset + negative_add_proxy_dataset
get_proxy_dataset = positive_get_proxy_dataset + negative_get_proxy_dataset
change_status_proxy_dataset = positive_change_status_proxy_dataset + negative_change_status_proxy_check
edit_proxy_dataset = positive_edit_proxy_dataset + negative_edit_proxy_dataset
del_proxy_dataset = positive_del_proxy_dataset + negative_del_proxy_dataset
