from pydantic import BaseModel


class DomainCheckFailed(BaseModel):
    replacement_group_id: int
    checked_domain: str
    message: str
