from pydantic import BaseModel

# from core.schemas.common import UserModelShort


class DummyResponse(BaseModel):
    id: int
    dummy_string: str


class DummyCreate(BaseModel):
    dummy_string: str


class DummyEdit(BaseModel):
    dummy_string: str


class DummyRestrictedResponse(BaseModel):
    dummy_int: int


# class DummyResponse(BaseModel):
#     current_user: UserModelShort
#     test_data: list
#     setting: str
