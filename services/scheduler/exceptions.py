from fastapi import status


class SchedulerException(Exception):
    pass


class NotFound(SchedulerException):
    status_code: int = status.HTTP_404_NOT_FOUND


class AlreadyExists(SchedulerException):
    status_code: int = status.HTTP_409_CONFLICT


class ValidationFailed(SchedulerException):
    status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY