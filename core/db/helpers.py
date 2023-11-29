from enum import Enum


class StatusTask(str, Enum):
    PAUSED = 'paused'
    RUNNING = 'running'