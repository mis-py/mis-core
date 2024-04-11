from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from core.exceptions import ValidationFailed


def make_string_cron(trigger: CronTrigger):
    minute_index = trigger.FIELD_NAMES.index('minute')
    hour_index = trigger.FIELD_NAMES.index('hour')
    day_index = trigger.FIELD_NAMES.index('day')
    month_index = trigger.FIELD_NAMES.index('month')
    day_of_week_index = trigger.FIELD_NAMES.index('day_of_week')

    minute = str(trigger.fields[minute_index])
    hour = str(trigger.fields[hour_index])
    day = str(trigger.fields[day_index])
    month = str(trigger.fields[month_index])
    day_of_week = str(trigger.fields[day_of_week_index])

    return f"{minute} {hour} {day} {month} {day_of_week}"


def format_trigger(trigger: IntervalTrigger | CronTrigger | OrTrigger | None):
    match trigger:
        case IntervalTrigger():
            return trigger.interval.seconds
        case CronTrigger():
            return make_string_cron(trigger)
        case OrTrigger():
            return [make_string_cron(cron_trigger) for cron_trigger in trigger.triggers]
        case _:
            return None


def get_trigger(input_trigger: int | str | list[str]):
    if isinstance(input_trigger, int):
        return IntervalTrigger(seconds=input_trigger)
    elif isinstance(input_trigger, str):
        return CronTrigger.from_crontab(input_trigger)
    elif isinstance(input_trigger, list):
        return OrTrigger([CronTrigger.from_crontab(c) for c in input_trigger])
    else:
        return None

