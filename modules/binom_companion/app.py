from services.modules.utils import GenericModule
from services.modules.components import Variables, ModuleLogs, TortoiseModels, EventRoutingKeys, APIRoutes

from .config import UserSettings, RoutingKeys, ModuleSettings
from .routes import router
from .tasks import scheduled_tasks
# from .consumers import event_consumers


app_settings = ModuleSettings()
user_settings = UserSettings()
routing_keys = RoutingKeys()


async def init(module_instance: GenericModule):
    pass
    # ru_geo, is_created = await Geo.get_or_create(name='RU')
    # if is_created:
    #     ru_geo.page = 'Прокси сервера (кроме TR)'
    #     ru_geo.registrator = 2
    #     ru_geo.status = 3
    #     ru_geo.ban = 5
    #     ru_geo.domain = 10
    #     ru_geo.curr_geo = 14
    #     ru_geo.another_bans = '6,7'
    #
    #     ru_geo.diff_percent = 25
    #     ru_geo.domain_change_cooldown = 600
    #     ru_geo.last_period_duration = 600
    #     ru_geo.previous_period_duration = 600
    #
    #     ru_geo_proxy_1, is_created = await Proxy.get_or_create(
    #         name="RU Dynamic Мегафон",
    #         geo=ru_geo,
    #         address="http://Uc1eg2:GeHHUymyXAgt@mproxy.site:13345",
    #         change_url="https://mobileproxy.space/reload.html?proxy_key=a5bcc728de5d22c1be146dc5d9b5c547"
    #     )
    #
    #     await ru_geo.save()
    #     logger.info('Created RU geo with default settings')

    # kz_geo, is_created = await Geo.get_or_create(name='KZ')
    # if is_created:
    #     kz_geo.page = 'Прокси сервера (кроме TR)'
    #     kz_geo.registrator = 2
    #     kz_geo.status = 3
    #     kz_geo.ban = 7
    #     kz_geo.domain = 10
    #     kz_geo.curr_geo = 14
    #     kz_geo.another_bans = '5,6'
    #
    #     kz_geo_proxy_1, is_created = await Proxy.get_or_create(
    #         name="KZ Dynamic",
    #         geo=kz_geo,
    #         address="http://Av3VUn:YfYp2tAdYGhE@fproxy.site:13239",
    #         change_url="https://mobileproxy.space/reload.html?proxy_key=a7acfbd23ca73fbd7cb39612ef84b836"
    #     )
    #
    #     await kz_geo.save()
    #     logger.info('Created KZ geo with default settings')
    #
    # tr_geo, is_created = await Geo.get_or_create(name='TR')
    # if is_created:
    #     tr_geo.page = 'Прокси сервера (кроме TR)'
    #     tr_geo.registrator = 2
    #     tr_geo.status = 3
    #     tr_geo.ban = 6
    #     tr_geo.domain = 10
    #     tr_geo.curr_geo = 14
    #     tr_geo.another_bans = '7,5'
    #     await tr_geo.save()
    #     logger.info('Created TR geo with default settings')


# //  "dependencies": [
# //    {"module": "proxy_registry", "version": "<=0.1,>=0.1"}
# //  ],

module = GenericModule(
    pre_init_components=[
        TortoiseModels(),
    ],
    components=[
        scheduled_tasks,
        # event_consumers,
        APIRoutes(router),
        Variables(app_settings, user_settings),
        ModuleLogs(),
        EventRoutingKeys(routing_keys),
    ],
    init_event=init
)
