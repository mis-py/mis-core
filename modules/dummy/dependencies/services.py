from modules.dummy.repositories.dummy_category import DummyCategoryRepository
from modules.dummy.repositories.dummy_element import DummyElementRepository
from modules.dummy.repositories.dummy_group import DummyGroupRepository
from modules.dummy.repositories.dummy_item import DummyItemRepository
from modules.dummy.repositories.dummy import DummyRepository
from modules.dummy.repositories.dummy_restricted import DummyRestrictedRepository
from modules.dummy.services.dummy import DummyService
from modules.dummy.services.dummy_restricted import DummyRestrictedService
from modules.dummy.services.dummy_category import DummyCategoryService
from modules.dummy.services.dummy_element import DummyElementService
from modules.dummy.services.dummy_group import DummyGroupService
from modules.dummy.services.dummy_item import DummyItemService


def get_dummy_model_service() -> DummyService:
    dummy_repo = DummyRepository()

    dummy_service = DummyService(dummy_repo)
    return dummy_service

def get_dummy_restricted_model_service() -> DummyRestrictedService:
    dummy_restricted_repo = DummyRestrictedRepository()

    dummy_restricted_service = DummyRestrictedService(dummy_restricted_repo)
    return dummy_restricted_service

def get_dummy_item_service() -> DummyItemService:
    dummy_item_repo = DummyItemRepository()

    dummy_item_repository = DummyItemService(dummy_item_repo=dummy_item_repo)
    return dummy_item_repository


def get_group_service() -> DummyGroupService:
    dummy_group_repo = DummyGroupRepository()

    dummy_group_service = DummyGroupService(dummy_group_repo=dummy_group_repo)
    return dummy_group_service


def get_category_service() -> DummyCategoryService:
    dummy_category_repo = DummyCategoryRepository()

    dummy_category_service = DummyCategoryService(dummy_category_repo=dummy_category_repo)
    return dummy_category_service


def get_element_service() -> DummyElementService:
    dummy_element_repo = DummyElementRepository()

    dummy_element_service = DummyElementService(dummy_element_repo=dummy_element_repo)
    return dummy_element_service
