
positive_get_modules = [
    (
        {},
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "total": 2,
                "current": 1,
                "size": 50,
                "pages": 1,
                "items": [
                    {
                        "id": 1,
                        "name": "core",
                        "enabled": True,
                        "manifest": None,
                        "state": "running",
                    },
                    {
                        "id": 2,
                        "name": "dummy",
                        "enabled": True,
                        "state": "running",
                        "manifest": {
                            "name": "dummy",
                            "display_name": "Dummy",
                            "description": "Module with examples of core functions and libs extensions",
                            "version": "1.0",
                            "author": "Jake Jameson",
                            "category": "example",
                            "permissions": {
                                "dummy": "Just for demonstration"
                            },
                            "dependencies": [],
                            "extra": {},
                            "auth_disabled": False
                        }
                    }
                ]
            },
            "status": True
        }
    ),
    (
        {
            "module_id": 2
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "total": 1,
                "current": 1,
                "size": 50,
                "pages": 1,
                "items": [
                    {
                        "id": 2,
                        "name": "dummy",
                        "enabled": True,
                        "state": "running",
                        "manifest": {
                            "name": "dummy",
                            "display_name": "Dummy",
                            "description": "Module with examples of core functions and libs extensions",
                            "version": "1.0",
                            "author": "Jake Jameson",
                            "category": "example",
                            "permissions": {
                                "dummy": "Just for demonstration"
                            },
                            "dependencies": [],
                            "extra": {},
                            "auth_disabled": False
                        }
                    }
                ]
            },
            "status": True
        }
    ),
]

negative_get_modules = [
    (
        {
            "module_id": 999
        },
        {
            "status_code": 404,
            "msg": "NotFound",
            "result": "Module not found",
            "status": False
        }
    ),
]


positive_init_modules = [
    (
        {
            "module_id": 2
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "id": 2,
                "name": "dummy",
                "enabled": False,
                "state": "initialized",
                "manifest": {
                    "name": "dummy",
                    "display_name": "Dummy",
                    "description": "Module with examples of core functions and libs extensions",
                    "version": "1.0",
                    "author": "Jake Jameson",
                    "category": "example",
                    "permissions": {
                        "dummy": "Just for demonstration"
                    },
                    "dependencies": [],
                    "extra": {},
                    "auth_disabled": False
                }
            },
            "status": True
        }
    )
]

negative_init_modules = [
    (
        {
            "module_id": 1
        },
        {
            "status_code": 400,
            "msg": "MISError",
            "result": "Operations on 'core' module not allowed from 'module_service'",
            "status": False
        }
    ),
    (
        {
            "module_id": 999
        },
        {
            "status_code": 404,
            "msg": "NotFound",
            "result": "Module not found",
            "status": False
        }
    )
]


positive_start_module = [
    (
        {
            "module_id": 2
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "id": 2,
                "name": "dummy",
                "enabled": True,
                "state": "running",
                "manifest": {
                    "name": "dummy",
                    "display_name": "Dummy",
                    "description": "Module with examples of core functions and libs extensions",
                    "version": "1.0",
                    "author": "Jake Jameson",
                    "category": "example",
                    "permissions": {
                        "dummy": "Just for demonstration"
                    },
                    "dependencies": [],
                    "auth_disabled": False,
                    "extra": {}
                }
            },
            "status": True
        }
    )
]

negative_start_module = [
    (
        {
            "module_id": 1
        },
        {
            "status_code": 400,
            "msg": "MISError",
            "result": "Operations on 'core' module not allowed from 'module_service'",
            "status": False
        }
    ),
    (
        {
            "module_id": 999
        },
        {
            "status_code": 404,
            "msg": "NotFound",
            "result": "Module not found",
            "status": False
        }
    )
]

positive_stop_module = [
    (
        {
            "module_id": 2
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {
                "id": 2,
                "name": "dummy",
                "enabled": False,
                "state": "stopped",
                "manifest": {
                    "name": "dummy",
                    "display_name": "Dummy",
                    "description": "Module with examples of core functions and libs extensions",
                    "version": "1.0",
                    "author": "Jake Jameson",
                    "category": "example",
                    "permissions": {
                        "dummy": "Just for demonstration"
                    },
                    "dependencies": [],
                    "auth_disabled": False,
                    "extra": {}
                }
            },
            "status": True
        }
    )
]

negative_stop_module = [
    (
        {
            "module_id": 1
        },
        {
            "status_code": 400,
            "msg": "MISError",
            "result": "Operations on 'core' module not allowed from 'module_service'",
            "status": False
        }
    ),
    (
        {
            "module_id": 999
        },
        {
            "status_code": 404,
            "msg": "NotFound",
            "result": "Module not found",
            "status": False
        }
    )
]

positive_shutdown_modules = [
    (
        {
            "module_id": 2
        },
        {
            "status_code": 200,
            "msg": "Success",
            "result": {},
            "status": True
        }
    )
]

negative_shutdown_modules = [
    (
        {
            "module_id": 1
        },
        {
            "status_code": 400,
            "msg": "MISError",
            "result": "Operations on 'core' module not allowed from 'module_service'",
            "status": False
        }
    ),
    (
        {
            "module_id": 999
        },
        {
            "status_code": 404,
            "msg": "NotFound",
            "result": "Module not found",
            "status": False
        }
    )
]

get_modules_dataset = positive_get_modules + negative_get_modules
init_module_dataset = positive_init_modules + negative_init_modules
shutdown_module_dataset = positive_shutdown_modules + negative_shutdown_modules
start_module_dataset = positive_start_module + negative_start_module
stop_module_dataset = positive_stop_module + negative_stop_module
