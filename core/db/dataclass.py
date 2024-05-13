from enum import Enum


class AppState(str, Enum):
    PRE_INITIALIZED = 'pre_initialized'  # initial state
    INITIALIZED = 'initialized'  # after init
    RUNNING = 'running'  # after start
    STOPPED = 'stopped'  # after stop
    SHUTDOWN = 'shutdown'  # after shutdown


class StatusTask(str, Enum):
    PAUSED = 'paused'
    RUNNING = 'running'
