from typing import Optional, Any, Dict
from pydantic import BaseModel, ConfigDict
from loguru import logger
from core.db.models import User, Module, Team


class VariableSet(BaseModel):
    app: Module
    user: Optional[User] = None
    team: Optional[Team] = None

    def is_bind(self, user: User, team: Team, app: Module):
        if user and user != self.user:
            return False
        elif team and (team != self.team and self.user not in team.users):
            return False
        elif app and app != self.app:
            return False

        return True

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True
    )
