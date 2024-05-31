#### What for?

Guardian реалізовано для керування доступом користувачів до конкретних записів в таблицях БД.
Назва guardian запозичено із бібліотеки [django-guardian](https://github.com/django-guardian/django-guardian), як і саму логіку роботи.

#### How it works?

Модель `GuardianContentType (mis_guardian_content_type)` зберігає всі моделі, які використовують клас `GuardianMixin`.

Модель `GuardianPermission (mis_guardian_permission)` зберігає коди доступу наприклад: `read`, `edit`, `delete`.

Модель `GuardianUserPermission (mis_guardian_user_permission)` зберігає доступ юзера до конкретного `object_pk` конкретної моделі `content_type`.

Моделі `GuardianAccessGroup (mis_guardian_access_group)` і `GuardianGroupPermission (mis_guardian_group_permission)` реалізовані для доступу одразу групі користувачів.

![[guardian-db-diagram.png]]

Дефолтні доступи такі як: `read`, `edit`, `delete` створюються одразу і їх можна використовувати. Можна додавати будь-які нові доступи. 

#### How to use?

Видача доступу до об'єкта моделі
```python
guardian_service = get_guardian_service()

user = await user_service.create(username="User123")
dummy_object = await dummy_service.create(dummy_string="Dummy123")

# видаєм для user доступ 'read' та 'edit' до dummy_object
await guardian_service.assign_perm('read', user, dummy_object)
await guardian_service.assign_perm('edit', user, dummy_object)


g_access_group_service = get_g_access_group_service()
group = await g_access_group_service.create_with_users(  
     name="Dummy group",  
     users_ids=[user.pk],  
)

# видаєм для group доступ 'read' та 'delete' до dummy_object
await guardian_service.assign_perm('read', group, dummy_object_1)
await guardian_service.assign_perm('delete', group, dummy_object_1)
```

Перевірка доступу до об'єкта
```python
# перевіряєм доступи user
is_read_perm = await guardian_service.has_perm('read', user, dummy_object)
is_edit_perm = await guardian_service.has_perm('edit', user, dummy_object)
is_delete_perm = await guardian_service.has_perm('delete', user, dummy_object)

print(is_read_perm, is_edit_perm, is_delete_perm)
>> True, True, False
...

# перевіряєм доступи group
is_read_perm = await guardian_service.has_perm('read', group, dummy_object)
is_edit_perm = await guardian_service.has_perm('edit', group, dummy_object)
is_delete_perm = await guardian_service.has_perm('delete', group, dummy_object)

print(is_read_perm, is_edit_perm, is_delete_perm)
>> True, False, True