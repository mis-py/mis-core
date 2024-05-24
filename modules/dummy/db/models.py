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


class DummyGroupModel(Model):
    name = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)

    categories: fields.ForeignKeyRelation['DummyCategoryModel']

    class Meta:
        table = 'dummy_group_dummy'


class DummyCategoryModel(Model):
    name = fields.CharField(max_length=255)
    group = fields.ForeignKeyField('dummy.DummyGroupModel',
                                   on_delete=fields.CASCADE, related_name='categories')
    created_at = fields.DatetimeField(auto_now_add=True)

    elements: fields.ForeignKeyRelation['DummyElementModel']

    class Meta:
        table = 'dummy_category_dummy'


class DummyElementModel(Model):
    name = fields.CharField(max_length=255)
    category = fields.ForeignKeyField('dummy.DummyCategoryModel',
                                      on_delete=fields.CASCADE, related_name='elements')
    is_visible = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'dummy_element_dummy'
