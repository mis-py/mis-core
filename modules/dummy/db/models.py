from tortoise import Model, fields

from core.db.mixin import GuardianMixin


class DummyModel(Model):
    dummy_string = fields.CharField(255)

    class Meta:
        table = 'dummy_dummy'


class DummyRestrictedModel(Model, GuardianMixin):
    dummy_int = fields.IntField()

    class Meta:
        table = 'dummy_restricted_dummy'

