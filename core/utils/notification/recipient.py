from dataclasses import dataclass
from enum import Enum
from typing import Optional
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Recipient:
    class Type(str, Enum):
        """Events by recipient type"""
        USER = 'user'  # message will be able only to a specific user
        TEAM = 'team'  # message will be able only to a specific team
        MODULE = 'module'  # message will be able only to a specific module

    user_id: Optional[int] = None
    team_id: Optional[int] = None
    module_name: Optional[str] = None

    # post init
    type: Type = None

    def __post_init__(self):
        if not self.user_id and self.team_id and self.module_name:
            raise Exception('One of this fields required: user_id,team_id,module_name')

        # change recipient_type if setting user_id, team_id or module_name
        if self.user_id:
            self.type = self.Type.USER
        elif self.team_id:
            self.type = self.Type.TEAM
        elif self.module_name:
            self.type = self.Type.MODULE
