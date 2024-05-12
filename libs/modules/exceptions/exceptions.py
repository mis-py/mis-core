from typing import Optional
from fastapi import status


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


class LoadModuleError(ModuleError):
    pass


class StartModuleError(ModuleError):
    pass
