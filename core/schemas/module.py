from typing import Optional

from pydantic import BaseModel

from core.db.models import Module
from core.schemas.common import AppModel
from services.modules.utils.manifest import ModuleManifest


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
    state: Module.AppState
    manifest: Optional[ModuleManifest] = None


class ModuleShortResponse(BaseModel):
    id: int
    name: str
    enabled: bool


class ModuleResponse(BaseModel):
    id: int
    name: str
    enabled: bool
    state: Module.AppState
