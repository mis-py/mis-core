from tortoise import fields
from tortoise.models import Model


class GrantedPermission(Model):
    permission = fields.ForeignKeyField('core.Permission', related_name='granted_permissions')
    user = fields.ForeignKeyField('core.User', null=True, related_name='granted_permissions')
    team = fields.ForeignKeyField('core.Team', null=True, related_name='granted_permissions')

    class Meta:
        table = 'mis_granted_permissions'
        unique_together = (('permission', 'user'), ('permission', 'team'))


class Permission(Model):
    name = fields.CharField(max_length=50)
    scope = fields.CharField(max_length=30, unique=True)
    app = fields.ForeignKeyField('core.Module', related_name='permissions')

    class Meta:
        table = 'mis_permissions'

    def __repr__(self):
        return self.scope
