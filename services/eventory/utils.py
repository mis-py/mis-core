from aio_pika.abc import AbstractIncomingMessage
from abc import ABC
from dataclasses import dataclass
from typing import Callable


class CustomIncomingMessage(AbstractIncomingMessage, ABC):
    json: dict


@dataclass
class EventTemplate:
    func: Callable
    route_key: str


class RoutingKeysSet:
    def __init__(self, routing_keys):
        for routing_key in routing_keys:
            self.__setattr__(routing_key.key, routing_key.name)
