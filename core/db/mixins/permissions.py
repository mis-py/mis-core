from tortoise import Model, fields
from tortoise.expressions import Q
from tortoise.queryset import QuerySet


class Permission(Model):
    name = fields.CharField(max_length=50)
    scope = fields.CharField(max_length=30, unique=True)
    app = fields.ForeignKeyField('models.App', related_name='permissions')

    @classmethod
    def create(cls, using_db=None, **kwargs):
        scope, app = kwargs.get('scope'), kwargs.get('app')
        app_scope = cls.make_app_scope(app_name=app.name, scope=scope)
        return super().create(using_db, name=kwargs.get('name'), scope=app_scope, app=app)

    @staticmethod
    def make_app_scope(app_name: str, scope: str):
        return f"{app_name}:{scope}"

    class Meta:
        table = 'mis_permissions'

    def __repr__(self):
        return self.scope


class GrantedPermission(Model):
    permission = fields.ForeignKeyField('models.Permission', related_name='granted_permissions')
    user = fields.ForeignKeyField('models.User', null=True, related_name='granted_permissions')
    team = fields.ForeignKeyField('models.Team', null=True, related_name='granted_permissions')

    class Meta:
        table = 'mis_grantedpermissions'
        unique_together = (('permission', 'user'), ('permission', 'team'))


class PermissionsMixin:
    async def set_permissions(self, scopes_list: list):
        """
        Set list of permissions

        :param scopes_list: list of scopes to grant
        :return: True. Exactly, only True right now. Nothing else cant be returned :)
        """
        relation_arg = {self.__class__.__name__.lower(): self}
        if not ('user' in relation_arg or 'team' in relation_arg):
            raise TypeError(f"Can't use PermissionsMixin with type {self.__class__.__name__}")

        await GrantedPermission.filter(**relation_arg).delete()  # clearing all previous permits
        to_create = [
            GrantedPermission(permission=permission, **relation_arg)  # creating new permits
            for permission in await Permission.filter(scope__in=scopes_list)
        ]
        await GrantedPermission.bulk_create(to_create)
        return True

    async def granted_permissions(self, scopes_list=False) -> QuerySet['GrantedPermission'] | list[str]:
        """
        Get list of granted permissions

        :param scopes_list: If True, then list of scopes will be returned.
        :return: list[GrantedPermission] | list[str]
        """

        if self.__class__.__name__ == 'User':
            query = GrantedPermission.filter(
                Q(user_id=self.id) | Q(user_id=self.id, team_id=self.team_id)
            )
        elif self.__class__.__name__ == 'Team':
            query = GrantedPermission.filter(
                team_id=self.id
            )
        else:
            raise TypeError(f"Can't use PermissionsMixin with type {self.__class__.__name__}")

        if scopes_list:
            query = query.select_related('permission')
            return [p.permission.scope for p in await query]
        return query
