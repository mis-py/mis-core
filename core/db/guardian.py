from tortoise import fields, Model


class GuardianContentType(Model):
    module = fields.ForeignKeyField('models.Module', related_name='content_types')
    model = fields.CharField(max_length=100)

    class Meta:
        table = 'mis_guardian_content_type'
        unique_together = ('module', 'model')


class GuardianPermission(Model):
    content_type = fields.ForeignKeyField('models.GuardianContentType', related_name='permissions')
    code_name = fields.CharField(max_length=100)
    name = fields.CharField(max_length=255)

    class Meta:
        table = 'mis_guardian_permission'


class GuardianUserPermission(Model):
    object_pk = fields.CharField(max_length=255)
    content_type = fields.ForeignKeyField('models.GuardianContentType', related_name='user_permissions')
    permission = fields.ForeignKeyField('models.GuardianPermission', related_name='user_permissions')
    user = fields.ForeignKeyField('models.User', related_name='user_permissions')

    class Meta:
        table = 'mis_guardian_user_permission'


class GuardianGroupPermission(Model):
    object_pk = fields.CharField(max_length=255)
    content_type = fields.ForeignKeyField('models.GuardianContentType', related_name='group_permissions')
    permission = fields.ForeignKeyField('models.GuardianPermission', related_name='group_permissions')
    group = fields.ForeignKeyField('models.AccessGroup', related_name='group_permissions')

    class Meta:
        table = 'mis_guardian_group_permission'
