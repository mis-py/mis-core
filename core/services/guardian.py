import asyncio
import time
from loguru import logger

from core.db.guardian import GuardianPermission, GuardianContentType, GuardianUserPermission, GuardianGroupPermission
from core.db.models import User
from core.db.restricted import AccessGroup
from modules.dummy.db import DummyModel, DummyRestrictedModel


async def assign_perm(perm: str, user_or_group: User | AccessGroup, obj):
    """Assign object permission to user or group"""

    permission = await GuardianPermission.get_or_none(code_name=perm)
    if not permission:
        raise Exception('Permission not found')

    class_name = obj.__class__.__name__
    content_type = await GuardianContentType.get_or_none(model=class_name)
    if not content_type:
        raise Exception('Content type not found')

    if isinstance(user_or_group, User):
        user = user_or_group
        return await GuardianUserPermission.get_or_create(
            user=user,
            permission=permission,
            content_type=content_type,
            object_pk=obj.id,
        )
    elif isinstance(user_or_group, AccessGroup):
        group = user_or_group
        return await GuardianGroupPermission.get_or_create(
            group=group,
            permission=perm,
            content_type=content_type,
            object_pk=obj.id,
        )
    else:
        raise Exception("user_or_group is not User or AccessGroup")


async def get_user_assigned_objects(perm: str, queryset, user: User):
    """Return filtered queryset by permission"""
    all_objects_pks = []

    # collect user permission objects
    user_perm_objects_pks = await GuardianUserPermission.filter(
        user=user,
        permission__code_name=perm,
        content_type__model=queryset.model.__name__,
    ).values_list("id", flat=True)
    all_objects_pks.extend(user_perm_objects_pks)

    # collect groups permission objects
    groups = await user.groups.all()
    if groups:
        groups_ids = [group.id for group in groups]
        groups_perm_objects_pks = await GuardianGroupPermission.filter(
            group__id__in=groups_ids, permission__code_name=perm, content_type__model=queryset.model.__name__
        ).values_list("id", flat=True)
        all_objects_pks.extend(groups_perm_objects_pks)

    return await queryset.filter(id__in=all_objects_pks)


async def get_group_assigned_objects(perm: str, queryset, group: AccessGroup):
    """Return filtered queryset by permission"""
    objects_pks = await GuardianGroupPermission.filter(
        group=group, permission__code_name=perm, content_type__model=queryset.model.__name__
    ).values_list("id", flat=True)
    return await queryset.filter(id__in=objects_pks)


async def has_perm(perm: str, user_or_group: User | AccessGroup, obj) -> bool:
    """User or Group permission checker"""

    model = obj.__class__.__name__
    object_pk = obj.id
    if isinstance(user_or_group, User):
        user = user_or_group
        perms = await _get_user_perms(user=user, model=model, object_pk=object_pk)
    elif isinstance(user_or_group, AccessGroup):
        group = user_or_group
        perms = await _get_group_perm(group=group, model=model, object_pk=object_pk)
    else:
        raise Exception("user_or_group is not User or AccessGroup")

    return perm in perms


async def _get_user_perms(user: User, model: str, object_pk: str):
    """Get user permission code names. Compared with groups permission code names"""

    groups = await user.groups.all()
    groups_ids = [group.id for group in groups]
    user_perms = await GuardianPermission.filter(
        user_permissions__user_id=user.id,
        content_type__model=model,
        user_permissions__object_pk=object_pk,
    ).distinct().values_list("code_name", flat=True)
    if groups:
        groups_perms = await GuardianPermission.filter(
            content_type__model=model,
            group_permissions__group_id__in=groups_ids,
            group_permissions__object_pk=object_pk,
        ).distinct().values_list("code_name", flat=True)
        user_perms.extend(groups_perms)
    return user_perms


async def _get_group_perm(group: AccessGroup, model: str, object_pk: str):
    """Get group permission code names"""

    group_perms = await GuardianPermission.filter(
        content_type__model=model,
        group_permissions__group_id=group.id,
        group_permissions__object_pk=object_pk,
    ).values_list("code_name", flat=True)
    return group_perms


async def test_guardian():
    user = await User.get(id=1).prefetch_related("group")
    group = await user.groups.all().first()
    dummy = await DummyRestrictedModel.get(id=1)

    # Guardian
    logger.info(f"Guardian")
    await assign_perm('edit', user, dummy)
    await assign_perm('view', group, dummy)

    is_user_has_view_perm = await has_perm('view', user, dummy)
    is_user_has_edit_perm = await has_perm('edit', user, dummy)

    is_group_has_view_perm = await has_perm('view', group, dummy)
    is_group_has_edit_perm = await has_perm('edit', group, dummy)

    logger.warning(f"User: view={is_user_has_view_perm} edit={is_user_has_edit_perm}")
    logger.warning(f"Group: view={is_group_has_view_perm} edit={is_group_has_edit_perm}")

    time_executions = []
    times = 20
    for i in range(times):
        st = time.time()
        is_user_has_view_perm = await has_perm('view', user, dummy)
        end = time.time() - st
        logger.info(f"has_perm={is_user_has_view_perm} | {end} seconds elapsed")
        time_executions.append(end)
    logger.info(f"Check has_perm avg {times} times: {sum(time_executions) / len(time_executions)} seconds elapsed")

    time_executions = []
    for i in range(times):
        st = time.time()
        await get_user_assigned_objects('view', queryset=DummyModel.all(), user=user)
        end = time.time() - st
        time_executions.append(end)
    logger.info(
        f"Check get_user_assigned_objects avg {times} times: "
        f"{sum(time_executions) / len(time_executions)} seconds elapsed"
    )

    ######################################################################3
    # RO
    logger.info(f"Ro")
    await dummy.allow(group)
    is_allowed_for = await dummy.is_allowed_for(user)
    logger.warning(f"User: is_allowed_for={is_allowed_for}")

    time_executions = []
    for i in range(times):
        st = time.time()
        is_allowed_for = await dummy.is_allowed_for(user)
        end = time.time() - st
        logger.info(f"is_allowed_for={is_allowed_for} | {end} seconds elapsed")
        time_executions.append(end)

    logger.info(
        f"Check is_allowed_for avg {times} times: {sum(time_executions) / len(time_executions)} seconds elapsed")
