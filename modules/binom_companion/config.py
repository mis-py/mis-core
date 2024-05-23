from pydantic import BaseModel


class UserSettings(BaseModel):
    YANDEX_API_KEY: str = ""


class ModuleSettings(BaseModel):
    LOG_LEVEL: str = "DEBUG"


class RoutingKeys(BaseModel):
    NEW_LEAD: str = 'new_lead'
    CHECK_CURRENT_DOMAINS_PASSED: str = 'check_current_domains_passed'
    CHECK_TASK_STATUSES: str = 'check_task_statuses'
    IDLE_GEO_CHECK_PASSED: str = 'idle_geo_check_passed'
    LEAD_RATE_CHECK_PASSED: str = 'lead_rate_check_passed'
    PROXY_IP_CHANGED: str = 'proxy_ip_changed'
    DOMAIN_CHANGED: str = 'domain_changed'
    PROXY_DOMAIN_FAILED: str = 'proxy_domain_failed'
