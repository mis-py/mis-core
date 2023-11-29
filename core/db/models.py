
from tortoise import fields
from tortoise.expressions import Q
from tortoise.models import Model
from tortoise.queryset import QuerySet

from core.db.helpers import StatusTask
from core.db.mixins.permissions import GrantedPermission, Permission
from core.security.utils import verify_password, get_password_hash


class PermissionsMixin:
    _granted_permissions: fields.ReverseRelation['GrantedPermission']

    async def get_relation_arg(self):
        if isinstance(self, User):
            relation_arg = {'user': self}
        elif isinstance(self, Team):
            relation_arg = {'team': self}
        else:
            raise TypeError(f"Can't use PermissionsMixin with type {self.__class__.__name__}")
        return relation_arg

    async def set_permissions(self, scopes_list: list):
        """
        Set list of permissions

        :param scopes_list: list of scopes to grant
        :return: True. Exactly, only True right now. Nothing else cant be returned :)
        """
        relation_arg = await self.get_relation_arg()

        await GrantedPermission.filter(**relation_arg).delete()  # clearing all previous permits
        to_create = [
            GrantedPermission(permission=permission, **relation_arg)  # creating new permits
            for permission in await Permission.filter(scope__in=scopes_list)
        ]
        await GrantedPermission.bulk_create(to_create)
        return True

    async def add_permission(self, scope: str):
        """
        Grant new permission for relation
        return: True if success added
        """
        relation_arg = await self.get_relation_arg()
        permission = await Permission.get_or_none(scope=scope)
        if not permission:
            return False
        await GrantedPermission.get_or_create(permission=permission, **relation_arg)
        return True

    async def remove_permission(self, scope: str):
        """
        Remove permission for relation
        return: True if success removed
        """
        relation_arg = await self.get_relation_arg()
        permission = await Permission.get_or_none(scope=scope)
        if not permission:
            return False
        await GrantedPermission.filter(permission=permission, **relation_arg).delete()
        return True

    async def granted_permissions(self, scopes_list=False) -> QuerySet['GrantedPermission'] | list[str]:
        """
        Get list of granted permissions

        :param scopes_list: If True, then list of scopes will be returned.
        :return: list[GrantedPermission] | list[str]
        """

        if isinstance(self, User):
            query = GrantedPermission.filter(
                Q(user_id=self.id) | Q(user_id=self.id, team_id=self.team_id)
            )
        elif isinstance(self, Team):
            query = GrantedPermission.filter(
                team_id=self.id
            )
        else:
            raise TypeError(f"Can't use PermissionsMixin with type {self.__class__.__name__}")

        if scopes_list:
            query = query.select_related('permission')
            return [p.permission.scope for p in await query]
        return query


class User(Model, PermissionsMixin):
    username = fields.CharField(max_length=20, unique=True)
    position = fields.CharField(max_length=100, null=True)
    hashed_password = fields.CharField(max_length=200)

    disabled = fields.BooleanField(default=False)
    signed_in = fields.BooleanField(default=False)

    team = fields.ForeignKeyField('models.Team', related_name='users', on_delete=fields.SET_NULL, null=True)
    settings: fields.ReverseRelation['SettingValue']
    groups: fields.ManyToManyRelation

    @classmethod
    async def authenticate(cls, username, plain_password):
        """
        Get user by its username and password. If there is no match, None is returned.

        :param username:
        :param plain_password:
        :return: User | None
        """

        user = await cls.get_or_none(username=username)
        if user and verify_password(plain_password, user.hashed_password):
            return user

    async def change_password(self, old_password, new_password) -> bool:
        """
        Set new password for user only if old_password matches

        :param old_password: old plain password
        :param new_password: new plain password
        :return:
        """
        if verify_password(old_password, self.hashed_password):
            self.set_password(new_password)
            await self.save()
            return True
        return False

    def set_password(self, value):
        """
        Just set new password for user without verification

        :param value:
        :return:
        """

        self.hashed_password = get_password_hash(value)

    class PydanticMeta:
        exclude = ("hashed_password",)

    class Meta:
        table = 'mis_users'

    def __str__(self):
        return f'<User: {self.username}>'


class Team(Model, PermissionsMixin):
    name = fields.CharField(max_length=50, )  # unique=True)
    users: fields.ReverseRelation[User]

    class Meta:
        table = 'mis_teams'


# class SettingType(str, Enum):
#     str = "str"
#     int = "int"
#     float = "float"
#     bool = "bool"


class Setting(Model):
    key = fields.CharField(max_length=50)
    default_value = fields.CharField(max_length=500, null=True)

    is_global = fields.BooleanField(default=True)
    type = fields.CharField(max_length=100, default="text")

    app = fields.ForeignKeyField('models.App', related_name='settings')

    class PydanticMeta:
        exclude = ('values',)

    class Meta:
        table = 'mis_settings'


class SettingValue(Model):
    setting = fields.ForeignKeyField('models.Setting', related_name='values')

    user = fields.ForeignKeyField('models.User', null=True, related_name='settings')
    team = fields.ForeignKeyField('models.Team', null=True, related_name='settings')

    value = fields.CharField(max_length=500)

    class PydanticMeta:
        exclude = ('user', 'team', 'user_id', 'team_id')

    class Meta:
        table = 'mis_setting_values'
        unique_together = (('setting', 'user'), ('setting', 'team'))


class App(Model):
    name = fields.CharField(max_length=50, unique=True)
    enabled = fields.BooleanField(default=True)
    permissions: fields.ReverseRelation[Permission]

    class PydanticMeta:
        exclude = ('permissions', 'settings')

    class Meta:
        table = 'mis_apps'

    def __str__(self):
        return f'<App: {self.name}>'


class ScheduledJob(Model):
    """Needed for manage when to start scheduled tasks"""

    app = fields.ForeignKeyField('models.App', related_name='jobs')
    user = fields.ForeignKeyField('models.User', related_name='jobs')
    team = fields.ForeignKeyField('models.Team', related_name='jobs', null=True)
    job_id = fields.CharField(max_length=255, unique=True)
    task_name = fields.CharField(max_length=255)
    status = fields.CharEnumField(enum_type=StatusTask)
    interval = fields.IntField(null=True)
    cron = fields.CharField(max_length=100, null=True)
    or_cron_list = fields.JSONField(null=True)
    extra_data = fields.JSONField(null=True)

    class Meta:
        table = 'mis_scheduled_job'

    def __str__(self):
        return self.name


class RoutingKey(Model):
    """
    RabbitMQ routing key from config.py in modules
    """

    key = fields.CharField(max_length=100, unique=True)
    name = fields.CharField(max_length=100, unique=True)
    app = fields.ForeignKeyField('models.App', related_name='routing_keys')
    key_verbose = fields.CharField(max_length=255, null=True)
    template = fields.TextField(null=True)

    class Meta:
        table = 'mis_routing_key'


class RoutingKeySubscription(Model):
    """User subscriptions to routing_keys"""

    user = fields.ForeignKeyField(
        'models.User', related_name='subscriptions', on_delete=fields.CASCADE)
    routing_key = fields.ForeignKeyField(
        'models.RoutingKey', related_name='key_subscriptions', on_delete=fields.CASCADE)

    class Meta:
        table = "mis_routing_key_subscription"
