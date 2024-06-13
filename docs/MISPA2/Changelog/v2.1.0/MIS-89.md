## Core
* Додано `LogManager` через який виконується `setup` логів
* Додавання logger хендлерів тепер відбувається лише через `LogManager`, він зберігає id хендлерів, завдяки чому виконується динамічне редагування логів.
* Додано `VariableCallbackManager` в який додаються функції, які будуть запускатись при редагування певних змінних.
* У компонент `Variables` додано атрибут `observers`, який приймає функції, що будуть реєструватись у `VariableCallbackManager`

## Dummy
* У компонент `Variables` додано функцію `change_module_logs` до `observers` на змінну `LOG_LEVEL`

## Binom companion
* У компонент `Variables` додано функцію `change_module_logs` до `observers` на змінну `LOG_LEVEL`

## Proxy registry
* У компонент `Variables` додано функцію `change_module_logs` до `observers` на змінну `LOG_LEVEL`