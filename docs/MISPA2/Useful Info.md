https://tortoise.github.io/setup.html?h=refres#tortoise.Model.refresh_from_db - обновить модель из базы данных. может быть полезно для того чтобы обновить state модуля без rebind модели.
### Permissions & Auth
https://github.com/zhanymkanov/fastapi-best-practices/issues/4

Для реализации FSM - смены состояний каких либо объектов.
https://github.com/pytransitions/transitions

Dependency Injections
https://python-dependency-injector.ets-labs.org/examples/fastapi.html

FastApi plugins interesting implementation
https://github.com/madkote/fastapi-plugins

MIGRATIONS
https://ollycope.com/software/yoyo/latest/#postgresql-connections

IMPORTS
1. Standard library imports.
2. Related third party imports.
3. Local application/library specific imports.

TYPE CHECKING
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prog.ui.menus import MainMenu

def funct(self, master: 'MainMenu', **kwargs):
    pass