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
