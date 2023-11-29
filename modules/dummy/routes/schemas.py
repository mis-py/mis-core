from pydantic import BaseModel

from core.db.schemas import UserModelShort


class DummyResponse(BaseModel):
    current_user: UserModelShort
    test_data: list
    setting: str
