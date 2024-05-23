from modules.dummy.repositories.dummy_item import DummyItemRepository
from modules.dummy.repository import DummyRepository
from modules.dummy.services.dummy import DummyService
from modules.dummy.services.dummy_item import DummyItemService


def get_dummy_model_service():
    dummy_repo = DummyRepository()

    dummy_service = DummyService(dummy_repo)
    return dummy_service


def get_dummy_item_service():
    dummy_item_repo = DummyItemRepository()

    dummy_item_repository = DummyItemService(dummy_item_repo=dummy_item_repo)
    return dummy_item_repository
