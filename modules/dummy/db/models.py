from tortoise import Model, fields
from core.db.restricted import RestrictedObjectMixin
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator


class DummyModel(Model):
    dummy_string = fields.CharField(255)

    class Meta:
        table = 'dummy_dummy'


class DummyRestrictedModel(Model, RestrictedObjectMixin):
    dummy_restricted_string = fields.CharField(100)

    class Meta:
        table = 'dummy_restricted_model'


DummyModelSchema = pydantic_model_creator(DummyModel, name='DummyModel')
DummyListModelSchema = pydantic_queryset_creator(DummyModel, name='DummyModel')

