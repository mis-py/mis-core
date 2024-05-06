from tortoise import Model, fields
from tortoise.contrib.postgres.fields import ArrayField

from modules.binom_companion.db.dataclass import DomainStatus


class TrackerInstance(Model):
    name = fields.CharField(max_length=10)
    description = fields.CharField(max_length=1024)
    api_key = fields.CharField(max_length=1024)
    base_url = fields.CharField(max_length=2048)
    get_route = fields.CharField(max_length=1024)
    edit_route = fields.CharField(max_length=1024)

    replacement_groups: fields.ReverseRelation["ReplacementGroup"]

    class Meta:
        table = 'binom_companion_tracker_instances'


class ReplacementGroup(Model):
    name = fields.CharField(max_length=10)
    description = fields.CharField(max_length=1024)
    aff_networks_ids = ArrayField(element_type="integer")

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

    # by default 30 minutes ttl
    lead_record_ttl = fields.IntField(default=60*30)
    proxy_fail_check_coefficient = fields.FloatField(default=0.5)
    lead_decrease_check_coefficient = fields.FloatField(default=0.2)
    minimum_required_coefficient = fields.FloatField(default=1.0)

    replacement_history: fields.ReverseRelation["ReplacementHistory"]

    class Meta:
        table = 'binom_companion_replacement_groups'


class ProxyDomain(Model):
    name = fields.CharField(max_length=2048)
    date_added = fields.DatetimeField(auto_now_add=True)

    # currently some domains can be used only with some trackers
    tracker_instance: fields.ForeignKeyRelation["TrackerInstance"] = fields.ForeignKeyField(
        model_name="binom_companion.TrackerInstance",
        related_name="proxy_domains",
    )

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
        related_name="replacement_history"
    )
    replaced_by = fields.ForeignKeyField(
        model_name="core.User"
    )

    offers = fields.JSONField()
    lands = fields.JSONField()

    date_changed = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'binom_companion_replacement_history'


class LeadRecord(Model):
    domain = fields.CharField(max_length=255)
    geo = fields.CharField(max_length=2)
    tag = fields.CharField(max_length=10)
    time = fields.DatetimeField(auto_now_add=True)

    def __init__(self, domain, geo, tag, **kwargs):
        super().__init__(**kwargs)
        self.domain = domain
        self.geo = geo.upper()
        self.tag = tag

    def to_dict(self):
        return {'domain': self.domain, 'geo': self.geo, 'tag': self.tag, 'time': int(self.time.timestamp())}

    def __str__(self):
        return f'<LeadRecord: {self.domain} {self.geo} {self.tag} {self.time.strftime("%d.%m.%Y %H:%M:%S")}>'

    class Meta:
        table = 'binom_companion_lead_record'
