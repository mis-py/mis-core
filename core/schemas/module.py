from pydantic import BaseModel
from core.schemas.common import AppModel


class DownloadAppInput(BaseModel):
    url: str
    branch: str = 'main'


class BundleAppModel(AppModel):
    front_bundle_path: str = None
    is_editable: bool = True
