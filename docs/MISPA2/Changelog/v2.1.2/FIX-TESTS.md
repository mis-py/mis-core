## Tests

* Виправлено шлях до `test.env`
* Змінено дані, які очікуються при negative test (із за зміни result у `validation_exception_handler`)
* В `test_core_modules.py` в `ignore_keys` додано `version`
* В тестах `tasks` і `jobs` змінено тестові дані під актуальні назви полів та `extra` аргументів
* Внесено зміни в Core і Proxy Registry для виправлення тестів

## Core

* Повернуто помилку Operations on 'core' module not allowed from 'module_service' у `get_module_by_id`
* У `TeamService` прибрано `uow`, який був пропущений раніше при випилюванні `UnitOfWork`
* У `VariableService` додано `raise ValidationFailed` замість `ValidationError`, щоб корректно відобразити помилку
* Schedulery `get_job` змінено `ValueError` на `NotFound`, щоб також корректно відображати помилку
* `validation_exception_handler` - до error msg додано loc, щоб виводилась інформація з якими параметрами помилка.

## Proxy Registry

* Додано міграцію із прибиранням `NOT NULL` у `object_id`, що помилково було зроблено у init міграції