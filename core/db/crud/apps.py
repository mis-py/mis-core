from core.db import App
from core.db.crud.base import CRUDBase


class CRUDApp(CRUDBase):
    async def get_or_create(self, name: str):
        return await self.model.get_or_create(
            name=name,
            defaults={"enabled": False},
        )

    async def get_enabled_app_names(self):
        return await self.model.filter(enabled=True).values_list('name', flat=True)


crud_app = CRUDApp(App)
