from typing import Optional, Any

from fastapi import status
from pydantic import BaseModel
from starlette import status


class ErrorSchema(BaseModel):
    status: int
    type: str
    message: str
    data: Optional[Any]


class MISError(Exception):
    status_code: int = status.HTTP_400_BAD_REQUEST

    def __init__(
            self,
            message: str,
            status_code: Optional[int] = None,
            data: Optional[dict] = None
    ):
        self.message = message
        self.data = data

        if status_code:
            self.status_code = status_code


class AuthError(MISError):
    status_code: int = status.HTTP_401_UNAUTHORIZED


class TokenError(MISError):
    status_code: int = status.HTTP_401_UNAUTHORIZED


class AccessError(MISError):
    status_code: int = status.HTTP_403_FORBIDDEN


class NotFound(MISError):
    status_code: int = status.HTTP_404_NOT_FOUND


class AlreadyExists(MISError):
    status_code: int = status.HTTP_409_CONFLICT


class ValidationFailed(MISError):
    status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY


class ModuleError(Exception):
    status_code: int = status.HTTP_400_BAD_REQUEST

    def __init__(
            self,
            message: str,
            status_code: Optional[int] = None,
            data: Optional[dict] = None
    ):
        self.message = message
        self.data = data

        if status_code:
            self.status_code = status_code


class InstallModuleError(ModuleError):
    pass


class StartModuleError(ModuleError):
    pass


class LoadModuleError(ModuleError):
    pass
