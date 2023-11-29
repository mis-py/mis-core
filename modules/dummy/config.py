from pydantic import BaseModel


class ModuleSettings(BaseModel):
    """
    Global module settings
    """
    TICK_5_SEC: int = 5
    LOG_LEVEL: str = "DEBUG"


class UserSettings(BaseModel):
    """
    Settings that configured and used by specific user
    """
    PRIVATE_SETTING: str = "very private"


class RoutingKeys(BaseModel):
    """
    Events that module can publish and other listeners can read
    """
    DUMMY_EVENT: str = "dummy_event"
