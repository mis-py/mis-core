from tortoise import Model, fields


class Proxy(Model):
    object_id = fields.CharField(max_length=255, null=True)  # relation identifier for other module model
    address = fields.CharField(max_length=255)
    change_url = fields.CharField(max_length=255, null=True)  # static proxy doesn't have change url
    name = fields.CharField(max_length=255, default="New Proxy")
    proxy_type = fields.CharField(max_length=255)  # proxy type http / socks5. unused currently
    is_online = fields.BooleanField(default=True)  # for marking that proxy actually work. used in proxy task
    is_enabled = fields.BooleanField(default=True)  # for manual enable/disable that proxy

    class Meta:
        table = 'proxy_registry_proxy'
