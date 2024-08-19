
## Tests

* Додано autouse фікстуру `initialize_tests` для ініціалізації Tortoise (initializer, finalizer)
* Переписано tortoise функцію `getDBConfig` яка використовується у `initializer`, щоб встановити `connection_label='models'`, тому що у tortoise `TestCase`, встановлений хардкод на `models`
* Переписано ще одну функцію `_init_db`, щоб прибрати generate_schema і додати yoyo міграції
* Написано тести для AuthService, UserService, TeamService