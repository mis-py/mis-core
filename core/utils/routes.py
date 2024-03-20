from pydantic import BaseModel, Field, computed_field
from typing import Generic, TypeVar, Type, Optional

T = TypeVar('T')

class GenericResponse(BaseModel, Generic[T]):
    # Code table
    # 0 - success
    code: int = Field(default=0)
    msg: str = Field(default="success")
    data: Optional[T]

    @computed_field
    @property
    def status(self) -> bool:
        return self.code == 0
