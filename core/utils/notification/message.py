from dataclasses import dataclass
from enum import Enum
from typing import Optional
from dataclasses_json import dataclass_json

from .recipient import Recipient


@dataclass_json
@dataclass
class EventMessage:
    class Source(str, Enum):
        """Events by source type"""
        EXTRA = 'extra'  # type of route that come from outside
        INTRA = 'intra'  # type of route that results from the operation of modules

    class Data(str, Enum):
        """Events by data type"""
        INFO = 'info'  # users can subscribe and receive messages
        INTERNAL = 'internal'  # users cannot subscribe; for internal project use only

    body: dict
    source_type: Source = Source.INTRA
    data_type: Data = Data.INFO
    recipient: Optional[Recipient] = None
    is_force_send: bool = False


@dataclass_json
@dataclass
class IncomingProcessedMessage:
    message: EventMessage

    app_name: str
    key: str

    key_verbose: Optional[str] = None
    body_verbose: Optional[str] = None
