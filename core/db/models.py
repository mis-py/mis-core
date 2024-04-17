from enum import Enum

from tortoise import fields
from tortoise.models import Model
from .mixin import UserPermissionsMixin, TeamPermissionsMixin, Permission


class User(Model, UserPermissionsMixin):
    username = fields.CharField(max_length=20, unique=True)
    position = fields.CharField(max_length=100, null=True)
    hashed_password = fields.CharField(max_length=200)

    disabled = fields.BooleanField(default=False)
    signed_in = fields.BooleanField(default=False)

    team = fields.ForeignKeyField('models.Team', related_name='users', on_delete=fields.SET_NULL, null=True)
    settings: fields.ReverseRelation['VariableValue']
    groups: fields.ManyToManyRelation
    access_groups: fields.ManyToManyRelation['GuardianAccessGroup']

    class PydanticMeta:
        exclude = ("hashed_password",)

    class Meta:
        table = 'mis_users'

    def __str__(self):
        return f'<User: {self.username}>'


class Team(Model, TeamPermissionsMixin):
    name = fields.CharField(max_length=50, )  # unique=True)
    users: fields.ReverseRelation[User]

    class Meta:
        table = 'mis_teams'


class Variable(Model):
    key = fields.CharField(max_length=50)
    default_value = fields.CharField(max_length=500, null=True)

    is_global = fields.BooleanField(default=True)
    type = fields.CharField(max_length=100, default="text")

    app = fields.ForeignKeyField('models.Module', related_name='settings')

    class PydanticMeta:
        exclude = ('values',)

    class Meta:
        table = 'mis_settings'


class VariableValue(Model):
    setting = fields.ForeignKeyField('models.Variable', related_name='values')

    user = fields.ForeignKeyField('models.User', null=True, related_name='settings')
    team = fields.ForeignKeyField('models.Team', null=True, related_name='settings')

    value = fields.CharField(max_length=500)

    class PydanticMeta:
        exclude = ('user', 'team', 'user_id', 'team_id')

    class Meta:
        table = 'mis_setting_values'
        unique_together = (('setting', 'user'), ('setting', 'team'))


class Module(Model):
    class AppState(str, Enum):
        PRE_INITIALIZED = 'pre_initialized'  # initial state
        INITIALIZED = 'initialized'  # after init
        RUNNING = 'running'  # after start
        STOPPED = 'stopped'  # after stop
        SHUTDOWN = 'shutdown'  # after shutdown
        ERROR = 'error'  # if any error in module occurred

    name = fields.CharField(max_length=50, unique=True)
    enabled = fields.BooleanField(default=False)
    permissions: fields.ReverseRelation[Permission]
    state = fields.CharEnumField(enum_type=AppState, default=AppState.PRE_INITIALIZED)

    class PydanticMeta:
        exclude = ('permissions', 'settings')

    class Meta:
        table = 'mis_apps'

    def __str__(self):
        return f'<Module: {self.name}>'


class ScheduledJob(Model):
    """Needed for manage when to start scheduled tasks"""

    class StatusTask(str, Enum):
        PAUSED = 'paused'
        RUNNING = 'running'

    app = fields.ForeignKeyField('models.Module', related_name='jobs')
    user = fields.ForeignKeyField('models.User', related_name='jobs')
    team = fields.ForeignKeyField('models.Team', related_name='jobs', null=True)
    job_id = fields.CharField(max_length=255, null=True)
    task_name = fields.CharField(max_length=255)
    status = fields.CharEnumField(enum_type=StatusTask)
    interval = fields.IntField(null=True)
    cron = fields.CharField(max_length=100, null=True)
    or_cron_list = fields.JSONField(null=True)
    extra_data = fields.JSONField(null=True)
    trigger = fields.JSONField(null=True)

    class Meta:
        table = 'mis_scheduled_job'


class RoutingKey(Model):
    """
    RabbitMQ routing key from config.py in modules
    """

    key = fields.CharField(max_length=100, unique=True)
    name = fields.CharField(max_length=100, unique=True)
    app = fields.ForeignKeyField('models.Module', related_name='routing_keys')
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
