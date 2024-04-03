from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator
from core.db.models import Variable, VariableValue
from core.utils.schema import MisModel


class VariableCreate(BaseModel):
    setting_id: int
    new_value: str | bool


class VariableUpdate(BaseModel):
    setting_id: int
    new_value: str | bool | None = None


class VariableResponse(BaseModel):
    id: int
    key: str
    default_value: str
    is_global: bool
    type: str


VariableModel = pydantic_model_creator(
    Variable,
    name='SettingModel',
    exclude=('app.jobs', 'app.routing_keys'),
)

VariableValueModel = pydantic_model_creator(
    VariableValue,
    name='SettingValueModel',
    exclude=('setting.app.jobs', 'setting.app.routing_keys'),
)


class UpdateVariableModel(MisModel):
    setting_id: int
    new_value: str | bool | None = None
