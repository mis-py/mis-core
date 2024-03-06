from tortoise import fields, Model


class GuardianContentType(Model):
    """Stores all models names in project"""

    module = fields.ForeignKeyField('models.Module', related_name='content_types')
    model = fields.CharField(max_length=100)

    class Meta:
        table = 'mis_guardian_content_type'
        unique_together = ('module', 'model')


class GuardianPermission(Model):
    """Stores available permissions for models objects"""

    content_type = fields.ForeignKeyField('models.GuardianContentType', related_name='permissions')
    code_name = fields.CharField(max_length=100)
    name = fields.CharField(max_length=255)

    class Meta:
        table = 'mis_guardian_permission'
        unique_together = ('content_type', 'code_name')


class GuardianUserPermission(Model):
    """Stores user permissions on objects"""

    object_pk = fields.CharField(max_length=255)
    content_type = fields.ForeignKeyField('models.GuardianContentType', related_name='user_permissions')
    permission = fields.ForeignKeyField('models.GuardianPermission', related_name='user_permissions')
    user = fields.ForeignKeyField('models.User', related_name='user_permissions')

    class Meta:
        table = 'mis_guardian_user_permission'


class GuardianAccessGroup(Model):
    """Stores users groups for grouping permissions"""

    name = fields.CharField(max_length=150)
    module = fields.ForeignKeyField('models.Module', related_name='access_groups', null=True)
    users = fields.ManyToManyField(
        "models.User",
        related_name="access_groups",
        through="mis_user_group_relation"
    )

    class Meta:
        table = 'mis_guardian_access_group'


class GuardianGroupPermission(Model):
    """Stores group permissions on objects"""

    object_pk = fields.CharField(max_length=255)
    content_type = fields.ForeignKeyField('models.GuardianContentType', related_name='group_permissions')
    permission = fields.ForeignKeyField('models.GuardianPermission', related_name='group_permissions')
    group = fields.ForeignKeyField('models.AccessGroup', related_name='group_permissions')

    class Meta:
        table = 'mis_guardian_group_permission'
