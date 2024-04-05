from pydantic import BaseModel
from core.utils.schema import MisModel


class AccessToken(MisModel):
    access_token: str
    token_type: str
    user_id: int
    username: str


class ChangePasswordData(BaseModel):
    old_password: str
    new_password: str
