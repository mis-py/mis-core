from modules.binom_companion.repository import TrackerInstanceRepository
from modules.binom_companion.services.tracker_instance import TrackerInstanceService


def get_tracker_instance_service() -> TrackerInstanceService:
    tracker_instance_repo = TrackerInstanceRepository()

    tracker_instance_service = TrackerInstanceService(tracker_instance_repo)
    return tracker_instance_service

