from pydantic import BaseModel


class UpdatePermissionModel(BaseModel):
    permission_id: int
    granted: bool | None = None
