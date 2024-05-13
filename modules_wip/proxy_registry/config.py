from pydantic import BaseModel


class ModuleSettings(BaseModel):
    LOG_LEVEL: str = "DEBUG"


class UserSettings(BaseModel):
    pass


class RoutingKeys(BaseModel):
    PROXY_IP_CHANGED:  str = 'proxy_ip_change_done'
    PROXY_IP_FAILED:   str = 'proxy_ip_change_fail'
    PROXY_STATUS_UP:   str = 'proxy_status_up'
    PROXY_STATUS_DOWN: str = 'proxy_status_down'

