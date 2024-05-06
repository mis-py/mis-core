from enum import Enum


class DomainStatus(str, Enum):
    DONE = 'Готово'
    ACTIVE = 'Активно'
    USED = 'Заменить домен'
    REUSE = 'Переиспользовать'
    NOT_WORK = 'Не работает'