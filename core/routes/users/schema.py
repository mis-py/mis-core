from pydantic import BaseModel, Field
from typing import Optional
from core.routes.variables.settings import UpdateSettingModel


class EditUserInput(BaseModel):
    username: Optional[str] = Field(max_length=20, min_length=3)
    team_id: int = None
    new_password: str = ''
    disabled: bool = None
    position: Optional[str] = Field(max_length=100)


class EditUserMe(BaseModel):
    username: Optional[str] = Field(max_length=20, min_length=3)


class CreateUserInput(BaseModel):
    username: str = Field(max_length=20, min_length=3)
    password: str
    team_id: int = None
    settings: Optional[list[UpdateSettingModel]] = []
    position: Optional[str] = Field(max_length=100)
    permissions: Optional[list[str]] = []