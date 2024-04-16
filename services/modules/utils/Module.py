import dataclasses


from .BaseModule import BaseModule
from .manifest import ModuleManifest

from services.modules.context import AppContext
from services.variables.variables import VariablesManager


class GenericModule(BaseModule):
    # TODO does it really need here??? move it to manifest?
    # app_settings: BaseSettings = None
    # user_settings: BaseSettings = None

    # def __init__(
    #     self,
    #     components: list[Component],
    #     model: App,
    #     permissions: dict = None,
    #     app_settings: BaseSettings = None,
    #     user_settings: BaseSettings = None,
    # notification_sender: Callable = None,
    # ):
    # self.sender: Optional[Callable] = notification_sender

    # if user or team is defined then they will be available in context
    async def get_context(self, user=None, team=None):
        return AppContext(
            # module=self, # Module is not serializing for apscheduler
            app_name=self.name,
            settings=await VariablesManager.make_variable_set(user=user, team=team, app=self._model)
        )

    def set_manifest(self, manifest: ModuleManifest):
        self.name = manifest.name
        self.display_name = manifest.display_name
        self.description = manifest.description
        self.version = manifest.version
        self.author = manifest.author
        self.category = manifest.category
        self.permissions = manifest.permissions
        self.dependencies = manifest.dependencies
        self.auth_disabled = manifest.auth_disabled
        # TODO add global_settings, local_settings
