from tortoise import Model
import inspect

from const import MODULES_DIR
from core.exceptions import AlreadyExists
from modules.proxy_registry.dependencies.services import get_proxy_service
from modules.proxy_registry.exceptions import InstanceInvalid
from modules.proxy_registry.schemas.proxy import ProxyCreate


def make_proxy_object_id(instance: Model):
    if not isinstance(instance, Model):
        raise InstanceInvalid("Only 'tortoise.Model' instance allowed")

    class_file_path = inspect.getfile(instance.__class__)
    if str(MODULES_DIR) not in class_file_path:
        raise InstanceInvalid("instance model class not in module")

    app_name = class_file_path.split('/')[3]
    model_name = instance.__class__.__name__
    instance_id = instance.pk

    return f"{app_name}:{model_name}:{instance_id}"


async def create_proxy(address: str, change_url, name: str, instance: Model, is_multi=False):
    """
    Create proxy for "instance" from other models
    is_multi=False - can be created only one proxy for one "instance"
    is_multi=True - can be created many proxies for one "instance"
    """

    object_id = make_proxy_object_id(instance)
    proxy_service = get_proxy_service()

    if not is_multi:
        proxy = await proxy_service.get(object_id=object_id)
        if proxy:
            raise AlreadyExists("Proxy already exists for this instance")

    return await proxy_service.create(
        ProxyCreate(
            address=address,
            change_url=change_url,
            name=name,
            object_id=make_proxy_object_id(instance),
        )
    )


async def get_proxy(instance: Model, is_multi=False):
    """Get proxy one or multi"""
    proxy_service = get_proxy_service()
    object_id = make_proxy_object_id(instance)
    if is_multi:
        return await proxy_service.filter(object_id=object_id)
    return await proxy_service.get(object_id=object_id)


async def remove_proxy(instance: Model, id: int):
    proxy_service = get_proxy_service()
    object_id = make_proxy_object_id(instance)
    return await proxy_service.delete(object_id=object_id, id=id)
