from dataclasses import dataclass


# from libs.notifications.utils import Message
# from libs.eventory import Eventory

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from services.modules.utils import GenericModule
    from services.variables.variable_set import VariableSet
    from core.db.models import User, Team


@dataclass
class AppContext:
    """Context data for modules"""
    module: 'GenericModule'
    # TODO try to pass type reference of actual module variable set
    variables: 'VariableSet'
    routing_keys: 'object'
    user: 'User'
    team: 'Team'

    @property
    def app_name(self):
        return self.module.name

    # async def publish_event(self, obj: Message, routing_key: str):
    #     # import it here due to partial initialized import error
    #
    #     message = obj.to_dict()
    #     await Eventory.publish(message, routing_key, self.name)

    # def __getattr__(self, item):
    #     if item.startswith('_'):
    #         raise AttributeError(f"ModuleProxy doesnt allow access to private attributes")
    #     return getattr(self.__module, item)