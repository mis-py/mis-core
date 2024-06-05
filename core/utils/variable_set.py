from typing import Optional, Any, Dict
from pydantic import BaseModel, ConfigDict
from loguru import logger
from core.db.models import User, Module, Team


class VariableSet(BaseModel):
    _app: Module
    _user: Optional[User] = None
    _team: Optional[Team] = None

    def is_bind(self, user: User, team: Team, app: Module):
        if user and user != self._user:
            return False
        elif team and (team != self._team and self._user not in team.users):
            return False
        elif app and app != self._app:
            return False

        return True

    model_config = ConfigDict(
        validate_assignment=True
    )
