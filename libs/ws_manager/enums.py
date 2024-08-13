from enum import Enum


class ResponseStatus(str, Enum):
    SUCCESS = 'success'
    ERROR = 'error'


class Action(str, Enum):
    SUBSCRIBE = 'subscribe'
    UNSUBSCRIBE = 'unsubscribe'
    UNKNOWN = 'unknown'


class WebsocketEvent(str, Enum):
    NOTIFICATION = 'notification'
    LOG = 'log'
