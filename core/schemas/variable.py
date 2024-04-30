from core.utils.schema import MisModel


class UpdateVariable(MisModel):
    setting_id: int
    new_value: str | bool | int | None = None


class VariableResponse(MisModel):
    id: int
    key: str
    default_value: str
    is_global: bool
    type: str


class VariableValueResponse(MisModel):
    id: int
    value: str
    setting_id: int
    # team_id: int
    # user_id: int
