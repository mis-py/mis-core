from dataclasses import dataclass
from typing import Any, Optional

from core.db.models import User, Team

from .variable_set import VariableSet


@dataclass
class AppContext:
    """Context data for modules"""
    app_name: str

    # TODO try to pass type reference of actual module variable set
    variables: VariableSet
    routing_keys: Any
    user: Optional[User] = None
    team: Optional[Team] = None

    # async def publish_event(self, obj: Message, routing_key: str):
    #     # import it here due to partial initialized import error
    #
    #     message = obj.to_dict()
    #     await Eventory.publish(message, routing_key, self.name)

    # def __getattr__(self, item):
    #     if item.startswith('_'):
    #         raise AttributeError(f"ModuleProxy doesnt allow access to private attributes")
    #     return getattr(self.__module, item)
