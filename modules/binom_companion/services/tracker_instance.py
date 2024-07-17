from core.services.base.base_service import BaseService
from modules.binom_companion.repository import TrackerInstanceRepository


class TrackerInstanceService(BaseService):
    def __init__(self, tracker_instance_repo: TrackerInstanceRepository):
        self.tracker_instance_repo = tracker_instance_repo
        super().__init__(repo=tracker_instance_repo)
