from tortoise import Model, fields
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

from core.db.mixin import GuardianMixin


class DummyModel(Model, GuardianMixin):
    dummy_string = fields.CharField(255)

    class Meta:
        table = 'dummy_dummy'



DummyModelSchema = pydantic_model_creator(DummyModel, name='DummyModel')
DummyListModelSchema = pydantic_queryset_creator(DummyModel, name='DummyModel')

