from pydantic import BaseModel


class DomainCheckFailed(BaseModel):
    checked_domain: str
    message: str
