from abc import abstractmethod, ABC

from typing import Callable
from tortoise.models import Model

from typing import TYPE_CHECKING

# if TYPE_CHECKING:
from .BaseComponent import BaseComponent
from core.schemas.module import ModuleManifest, ModuleDependency


class BaseModule(ABC):
    """
    Basic module data container
    """
    # System name of module
    name: str
    # Verbose name of module
    display_name: str
    # Description of module
    description: str
    # Module version
    version: str
    # Module author
    author: str
    # Module category
    category: str
    # Permissions that module is required to use
    permissions: dict

    # List of module components
    pre_init_components: list['BaseComponent']
    components: list['BaseComponent']

    # Other modules as dependencies
    dependencies: list['ModuleDependency']

    # If auth disabled routes will not have access to current user
    auth_disabled: bool

    # DB reference to app model
    _model: Model

    # will be True on very first model init
    _is_created: bool

    pre_init_event: Callable
    init_event: Callable
    shutdown_event: Callable
    start_event: Callable
    stop_event: Callable

    def __init__(
            self,
            pre_init_event: Callable = None,
            init_event: Callable = None,
            shutdown_event: Callable = None,
            start_event: Callable = None,
            stop_event: Callable = None,
            pre_init_components: list['BaseComponent'] = None,
            components: list['BaseComponent'] = None
    ):
        self.pre_init_event = pre_init_event
        self.init_event = init_event
        self.shutdown_event = shutdown_event
        self.start_event = start_event
        self.stop_event = stop_event
        self.pre_init_components = pre_init_components
        self.components = components

    @abstractmethod
    async def pre_init(self, application) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def bind_model(self, model, is_created) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def init(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def start(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def stop(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def shutdown(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def set_manifest(self, manifest: ModuleManifest) -> None:
        raise NotImplementedError

    @abstractmethod
    async def refresh_from_db(self) -> bool:
        raise NotImplementedError


