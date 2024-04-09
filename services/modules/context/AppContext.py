from dataclasses import dataclass


# from libs.notifications.utils import Message
# from libs.eventory import Eventory

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from services.modules.utils import ModuleTemplate
    from services.variables.variable_set import VariableSet


@dataclass
class AppContext:
    """Context data for modules"""
    # module: 'ModuleTemplate'
    app_name: str
    settings: 'VariableSet'

    # @property
    # def app_name(self):
    #     return "test" #self.module.name

    # async def publish_event(self, obj: Message, routing_key: str):
    #     # import it here due to partial initialized import error
    #
    #     message = obj.to_dict()
    #     await Eventory.publish(message, routing_key, self.name)

    # def __getattr__(self, item):
    #     if item.startswith('_'):
    #         raise AttributeError(f"ModuleProxy doesnt allow access to private attributes")
    #     return getattr(self.__module, item)