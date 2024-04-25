from tortoise import fields
from tortoise.models import Model


class GrantedPermission(Model):
    permission = fields.ForeignKeyField('models.Permission', related_name='granted_permissions')
    user = fields.ForeignKeyField('models.User', null=True, related_name='granted_permissions')
    team = fields.ForeignKeyField('models.Team', null=True, related_name='granted_permissions')

    class Meta:
        table = 'mis_grantedpermissions'
        unique_together = (('permission', 'user'), ('permission', 'team'))


class Permission(Model):
    name = fields.CharField(max_length=50)
    scope = fields.CharField(max_length=30, unique=True)
    app = fields.ForeignKeyField('models.Module', related_name='permissions')

    class Meta:
        table = 'mis_permissions'

    def __repr__(self):
        return self.scope
