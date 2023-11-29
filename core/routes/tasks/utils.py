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
            type_trigger = "interval"
            value = trigger.interval
        case CronTrigger():
            type_trigger = "cron"
            value = make_string_cron(trigger)
        case OrTrigger():
            type_trigger = "or_cron"
            value = [make_string_cron(cron_trigger) for cron_trigger in trigger.triggers]
        case _:
            return None
    return {
        'type': type_trigger,
        'value': value,
    }


def make_trigger(input_trigger):
    try:
        if input_trigger.interval:
            return IntervalTrigger(seconds=input_trigger.interval)
        elif isinstance(input_trigger.cron, str):
            return CronTrigger.from_crontab(input_trigger.cron)
        elif isinstance(input_trigger.cron, list):
            return OrTrigger([CronTrigger.from_crontab(c) for c in input_trigger.cron])
        else:
            raise ValidationFailed("Trigger not added")
    except ValueError as e:
        raise ValidationFailed(f"Invalid schedule value. {e}")
