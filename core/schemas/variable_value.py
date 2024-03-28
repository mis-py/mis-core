from pydantic import BaseModel

from core.schemas.variable import VariableResponse


class VariableValueResponse(BaseModel):
    id: int
    setting: VariableResponse
    value: str
