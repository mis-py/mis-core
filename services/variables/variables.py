from .variables_proxy import SettingsProxy
from core.db import User, App, Team


class SettingsManager:
    """Need for update all SettingsProxy objects when settings changed"""
    _settings: list[SettingsProxy] = []

    @classmethod
    def add_settings(cls, settings: SettingsProxy):
        cls._settings.append(settings)

    @classmethod
    async def update_settings(cls, user=None, team=None, app=None):
        for settings in cls._settings:
            if user and user != settings._user:
                continue
            elif team and (team != settings._team and settings._user not in team.users):
                continue
            elif app and app != settings._app:
                continue
            await settings.load()

    @classmethod
    async def make_settings_proxy(cls, user: User = None, app: App = None, team: Team = None) -> SettingsProxy:
        settings = SettingsProxy(user=user, team=team, app=app)
        await settings.load()
        cls.add_settings(settings)
        return settings
