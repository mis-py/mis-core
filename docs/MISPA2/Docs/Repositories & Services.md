#### What for?

Цей патерн використано на заміну звичайним CRUD класам, які були більше ніж CRUD і змішували логіку доступу до даних та бізнес логіку. 
За цим патерном логіка доступу до даних `repositories`, та бізнес логіка `services` рознесена на 2 різних шари логіки.

#### How it works?

В `/core/repositories/base/repository.py` реалізовано інтерфейс `IRepository`, та базовий клас `TortoiseORMRepository`, який реалізовує методи інтерфейсу.

У директорії `/repositories` (у core і кожного модуля своя) створюються класи репозиторії для кожної моделі.
Приклад із /`core/repositories/module.py`:
```python
from abc import ABC, abstractmethod  
  
from core.db.models import Module  
from core.repositories.base.repository import TortoiseORMRepository, IRepository  
  
  
class IModuleRepository(IRepository, ABC):  
    @abstractmethod  
    async def get_or_create_by_name(self, name: str):  
        raise NotImplementedError  
  
  
class ModuleRepository(TortoiseORMRepository, IModuleRepository):  
    model = Module  
  
    async def get_or_create_by_name(self, name: str) -> (Module, bool):  
        return await self.model.get_or_create(name=name)
```
Тут створюється інтерфейс `IModuleRepository` і сам репо `ModuleRepository`, який успадковується від базового класу `TortoiseORMRepository` (якщо потрібна логіка з нього) і `IModuleRepository`.

Використовувати репозиторій напряму не рекомендується, тому репозиторії використовуються лише в сервісах.
В `/core/services/base/base_service.py` реалізовано базовий клас, в якому реалізовані методи, які використовують методи з інтерфейсу `IRepository`.
Самі сервіси знаходяться в `core/services`. 
Приклад із `/core/services/module.py`:
```python
from core.repositories.module import IModuleRepository
from core.services.base.base_service import BaseService

class ModuleService(BaseService):  
    def __init__(self, module_repo: IModuleRepository):  
        self.module_repo = module_repo  
        super().__init__(repo=module_repo)
	
	async def get_or_create(self, name: str):  
	    return await self.module_repo.get_or_create_by_name(name=name)
```

`super().__init__(repo=module_repo)` - необхідний щоб визначити, який з репозиторіїв буде використовувати базовий сервіс `BaseService`, тому що сервіс може використовувати безліч репозиторіїв. Успадковуватись від `BaseService` не обов'язково для роботи з репо.

Створення об'єктів сервісів відбувається у `dependecies`
Приклад `/core/dependencies/services.py`:
```python
from core.repositories.module import ModuleRepository
from core.services.module import ModuleService

...

def get_module_service() -> ModuleService:  
    module_repo = ModuleRepository()  
  
    module_service = ModuleService(module_repo=module_repo)  
    return module_service

...

```

#### How to use?

Сервіси використовуються в ендпоінтах через [dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/#dependencies) 
`module_service: Annotated[module.ModuleService, Depends(get_module_service)]`
Приклад  із `/core/routes/module.py`
```python
@router.get(  
    '',  
    dependencies=[Security(get_current_user)],  
    response_model=PageResponse[ModuleManifestResponse]  
)  
async def get_modules(  
        module_service: Annotated[module.ModuleService, Depends(get_module_service)],  
        paginate_params: PaginateParamsDep, module_id: int = None, module_name: str = None,  
):  
    if module_id:  
        module_instance = await module_service.get_or_raise(id=module_id)  
    elif module_name:  
        module_instance = await module_service.get_or_raise(name=module_name)  
    else:  
        module_instance = None  
  
    paginated_modules = await module_service.filter_and_paginate(  
        id=module_instance.pk if module_instance else None,  
        params=paginate_params  
    )  
    modules_with_manifest = await module_service.set_manifest_in_response(paginated_modules)  
    return modules_with_manifest
```

Якщо потрібно використати сервіс поза ендпоінтами, його можна отримати просто:
```python
from core.dependencies.services import get_module_service

module_service = get_module_service()
