from tortoise import Model, fields


class TrackerInstance(Model):
    name = fields.CharField(max_length=255)
    description = fields.CharField(max_length=1024)
    api_key = fields.CharField(max_length=1024)
    base_url = fields.CharField(max_length=2048)
    get_route = fields.CharField(max_length=1024)
    edit_route = fields.CharField(max_length=1024)

    replacement_groups: fields.ReverseRelation["ReplacementGroup"]

    def __str__(self):
        return f'<TrackerInstance: {self.pk}, {self.name} {self.base_url}>'

    class Meta:
        table = 'binom_companion_tracker_instances'


class ReplacementGroup(Model):
    name = fields.CharField(max_length=255)
    description = fields.CharField(max_length=1024)

    offer_group_id = fields.IntField()
    # represents country code or "1" if global
    offer_geo = fields.CharField(max_length=1024)
    offer_name_regexp_pattern = fields.CharField(max_length=8192)

    land_group_id = fields.IntField()
    # represents country code or "all" if all langs
    land_language = fields.CharField(max_length=1024)
    land_name_regexp_pattern = fields.CharField(max_length=8192)

    tracker_instance: fields.ForeignKeyRelation["TrackerInstance"] = fields.ForeignKeyField(
        model_name="binom_companion.TrackerInstance",
        related_name="replacement_groups"
    )

    is_active = fields.BooleanField(default=False)

    replacement_history: fields.ReverseRelation["ReplacementHistory"]

    def __str__(self):
        return f'<ReplacementGroup: {self.pk}, {self.name} active:{self.is_active}>'

    class Meta:
        table = 'binom_companion_replacement_groups'


class ProxyDomain(Model):
    name = fields.CharField(max_length=2048, unique=True)
    date_added = fields.DatetimeField(auto_now_add=True)

    # in case we need to track domain is broken or not working
    is_invalid = fields.BooleanField(default=False)

    # for tracking what server is binded to domain and ready state after setup
    is_ready = fields.BooleanField(default=False)
    server_name = fields.CharField(max_length=2048)

    # currently some domains can be used only with some trackers
    tracker_instance: fields.ForeignKeyRelation["TrackerInstance"] = fields.ForeignKeyField(
        model_name="binom_companion.TrackerInstance",
        related_name="proxy_domains",
    )

    def __str__(self):
        return f'<ProxyDomain: {self.pk}, {self.name} {self.date_added.strftime("%d.%m.%Y %H:%M:%S")}>'

    class Meta:
        table = 'binom_companion_proxy_domains'


class ReplacementHistory(Model):
    from_domains: fields.ManyToManyRelation["ProxyDomain"] = fields.ManyToManyField(
        model_name="binom_companion.ProxyDomain",
        related_name="from_domains",
        through="binom_companion_replacement_history_from_domain_relation"
    )

    to_domain: fields.ForeignKeyRelation["ProxyDomain"] = fields.ForeignKeyField(
        model_name="binom_companion.ProxyDomain",
        related_name="to_domain"
    )
    replacement_group: fields.ForeignKeyRelation["ReplacementGroup"] = fields.ForeignKeyField(
        model_name="binom_companion.ReplacementGroup",
        related_name="replacement_history",
    )
    replaced_by = fields.ForeignKeyField(
        model_name="core.User"
    )

    offers = fields.JSONField()
    lands = fields.JSONField()

    date_changed = fields.DatetimeField(auto_now_add=True)

    reason = fields.CharField(max_length=2048)

    def __str__(self):
        return f'<ReplacementHistory: {self.pk}, {self.to_domain} {self.replaced_by} {self.replacement_group} {self.date_changed.strftime("%d.%m.%Y %H:%M:%S")}>'

    class Meta:
        table = 'binom_companion_replacement_history'


class LeadRecord(Model):
    origin = fields.CharField(max_length=255)
    tag = fields.CharField(max_length=255)

    date_created = fields.DatetimeField(auto_now_add=True)

    ip = fields.CharField(max_length=255)
    ua = fields.CharField(max_length=8192)
    country = fields.CharField(max_length=255)
    us = fields.CharField(max_length=255)
    uc = fields.CharField(max_length=255)
    un = fields.CharField(max_length=255)
    ut = fields.CharField(max_length=255)
    um = fields.CharField(max_length=255)
    clickid = fields.CharField(max_length=1024)
    item_id = fields.CharField(max_length=255)

    def __str__(self):
        return f'<LeadRecord: {self.origin} {self.country} {self.tag} {self.date_created.strftime("%d.%m.%Y %H:%M:%S")}>'

    class Meta:
        table = 'binom_companion_lead_record'
