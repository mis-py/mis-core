from core.services.base.base_service import BaseService
from core.services.base.unit_of_work import IUnitOfWork


class PermissionService(BaseService):
    def __init__(self, uow: IUnitOfWork):
        super().__init__(repo=uow.permission_repo)
        self.uow = uow
