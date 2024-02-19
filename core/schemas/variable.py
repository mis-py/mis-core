from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator
from core.db.models import Variable, VariableValue

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


class UpdateVariableModel(BaseModel):
    setting_id: int
    new_value: str | bool | None = None