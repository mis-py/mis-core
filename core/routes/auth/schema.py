from pydantic import BaseModel


class AccessToken(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str


class ChangePasswordData(BaseModel):
    old_password: str
    new_password: str
