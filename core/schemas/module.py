from typing import Optional

from pydantic import BaseModel
from tortoise.contrib.pydantic import PydanticModel
from core.db.dataclass import AppState
from core.schemas.common import AppModel
from libs.modules.utils.ModuleManifest import ModuleManifest


class DownloadAppInput(BaseModel):
    url: str
    branch: str = 'main'


class BundleAppModel(AppModel):
    front_bundle_path: str = None
    is_editable: bool = True


class ModuleManifestResponse(BaseModel):
    id: int
    name: str
    enabled: bool
    state: AppState
    manifest: Optional[ModuleManifest] = None


class ModuleShortResponse(PydanticModel):
    id: int
    name: str
    enabled: bool


class ModuleResponse(BaseModel):
    id: int
    name: str
    enabled: bool
    state: AppState
