from fastapi import APIRouter
from fastapi.routing import APIRoute
from loguru import logger

from ..Base.BaseComponent import BaseComponent


class APIRoutes(BaseComponent):
    def __init__(self, router: APIRouter):
        self.router: APIRouter = router
        self.application = None

    async def pre_init(self, application):
        self.application = application

    async def init(self, app_db_model, is_created: bool):
        pass

    async def start(self):
        # dependencies = [Depends(inject_context)]
        dependencies = []
        # TODO remove it if it is not used
        if not self.module.auth_disabled:
            pass
            # dependencies.append(Depends(inject_user))

        for route in self.router.routes:
            if hasattr(route, 'tags') and route.tags:
                tags = [f'{self.module.name} | {route.tags[0]}']
            else:
                tags = [self.module.name]
            route.tags = tags

        self.application.include_router(
            self.router,
            prefix=f"/{self.module.name}",
            dependencies=dependencies,
        )

        await self.regen_openapi()

    async def stop(self):
        for route in filter(lambda r: isinstance(r, APIRoute), self.application.router.routes):
            if self.module.name in route.tags:
                self.application.router.routes.remove(route)
        await self.regen_openapi()

    async def shutdown(self):
        pass

    async def regen_openapi(self):
        self.application.openapi_schema = None
        self.application.setup()
