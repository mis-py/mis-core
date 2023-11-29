from pydantic import BaseModel


class UpdateSettingModel(BaseModel):
    setting_id: int
    new_value: str | bool | None = None