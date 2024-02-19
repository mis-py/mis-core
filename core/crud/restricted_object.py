from core.db.restricted import RestrictedObject
from core.crud.base import CRUDBase


class CRUDRestrictedObject(CRUDBase):
    pass


restricted_object = CRUDRestrictedObject(RestrictedObject)
