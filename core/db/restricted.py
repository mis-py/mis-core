from tortoise import fields, Model
from tortoise.queryset import QuerySet


class GroupPermissionFlags(Model):
    group = fields.ForeignKeyField(
        'models.AccessGroup',
        related_name='flags'
    )
    model_name = fields.CharField(max_length=150)

    update = fields.BooleanField(default=False)
    delete = fields.BooleanField(default=False)

    class Meta:
        table = 'mis_group_permission_flags'


class AccessGroup(Model):
    name = fields.CharField(max_length=150)
    app = fields.ForeignKeyField('models.Module', related_name='groups', null=True)
    users = fields.ManyToManyField(
        "models.User",
        related_name="groups",
        through="mis_user_group_relation"
    )
    allowed_objects = fields.ManyToManyField(
        "models.RestrictedObject",
        related_name='allowed_groups',
        through='mis_object_group_relation'
    )
    flags: fields.ForeignKeyRelation[GroupPermissionFlags]

    async def set_flags_for(self, model: type, update=None, delete=None):
        flags, is_created = await GroupPermissionFlags.get_or_create(group=self, model_name=model.__name__)
        flags.update = update if (update is not None) else flags.update
        flags.delete = delete if (delete is not None) else flags.delete
        await flags.save()

    def __str__(self):
        return f'<AccessGroup: {self.name}>'

    class Meta:
        table = 'mis_usergroup'


class RestrictedObject(Model):
    object_id = fields.CharField(max_length=150)
    object_app = fields.ForeignKeyField('models.Module', related_name='restricted_objects', null=True)

    allowed_groups: fields.ManyToManyRelation[AccessGroup]

    class Meta:
        table = 'mis_restricted_objects'


class RestrictedObjectMixin:
    _restricted_object_model = fields.ForeignKeyField(
        'models.RestrictedObject',
        null=True
    )


    def resolve_relation(func):  # noqa
        async def _wrapper(self, *args, **kwargs):
            if not self._restricted_object_model:
                _obj, is_created = await RestrictedObject.get_or_create(
                    object_id=f'{self.__class__.__name__}:{self.get_id()}'
                )

                self._restricted_object_model = _obj
                await self.save()

            if isinstance(self._restricted_object_model, QuerySet):
                await self.fetch_related('_restricted_object_model')

            if not self._restricted_object_model:
                await self.delete()
                return

            return await func(self, *args, **kwargs)  # noqa

        return _wrapper

    def get_id(self):
        return self.id

    @classmethod
    async def get_allowed_for(cls: Model, user: 'db.User', to_update=False, to_delete=False):
        res = []
        async for obj in cls.all():
            if await obj.is_allowed_for(user, to_update, to_delete):  # noqa
                res.append(obj)
        return res

    @resolve_relation  # noqa
    async def is_allowed_for(self, user: 'db.User', to_update=False, to_delete=False):
        groups = await user.groups.filter(
            allowed_objects__object_id=self._restricted_object_model.object_id
        )
        for group in groups:
            flags = await group.flags.filter(model_name=self.__class__.__name__).first()
            if to_update and (not flags.update):
                continue

            if to_delete and (not flags.delete):
                continue

            return True
        return False

    @resolve_relation  # noqa
    async def allow(self, group: AccessGroup):
        await group.allowed_objects.add(await self._restricted_object_model)
        await GroupPermissionFlags.create(group=group, model_name=self.__class__.__name__)

    @classmethod
    async def get_safe(cls: Model, *args, **kwargs):
        return (await cls.get_or_create(*args, **kwargs))[0]


class RestrictedBox:
    def __init__(self, *objects):
        self.objects = objects
        self.res = []

    async def resolve(self, user: 'db.User', allow_empty=True, serialize_with=None):
        for obj in self.objects:
            if isinstance(obj, RestrictedBox):
                obj_res = await obj.resolve(user, allow_empty, serialize_with)
                if obj_res or allow_empty:
                    self.res.append(obj_res)

            elif isinstance(obj, RestrictedObjectMixin):
                if await obj.is_allowed_for(user):
                    self.res.append(serialize_with(obj) if serialize_with else obj)
        return self.res

