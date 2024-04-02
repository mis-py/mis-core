from typing import Optional

from pydantic import BaseModel
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
    manifest: Optional[ModuleManifest] = None


class ModuleResponse(BaseModel):
    id: int
    name: str
    enabled: bool
