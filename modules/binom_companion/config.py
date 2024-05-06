from pydantic import BaseModel


class UserSettings(BaseModel):
    TRACKER_URL_GET: str = ""
    TRACKER_URL_EDIT: str = ""
    TRACKER_API_KEY: str = ""
    SPREADSHEET_ID: str = ""
    SHEET_NAME: str = ""
    AFFILIATE_NETWORKS: str = ""
    GEOS: str = ""
    LEAD_RECORD_TTL: int = 60 * 30  # 30 minutes
    PROXY_FAIL_CHECK_COEFFICIENT: float = 0.5
    LEAD_DECREASE_CHECK_COEFFICIENT: float = 0.2
    MINIMUM_REQUIRED_COEFFICIENT: float = 1.0
    DOMAIN_CHANGE_ENABLED: bool = False


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


GEO_TO_LANG: dict[str, str] = {
    "RU": "RU",
    "KZ": "KZ",
    "TR": "TR",
    "AZ": "AZ"
}
