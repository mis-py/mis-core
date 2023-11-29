from core.db import RestrictedObject
from core.db.crud.base import CRUDBase


class CRUDRestrictedObject(CRUDBase):
    pass


restricted_object = CRUDRestrictedObject(RestrictedObject)
