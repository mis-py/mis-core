from ..service import LeadRecordService

from datetime import datetime, timedelta
from loguru import logger

from core.utils.notification.message import Message
from services.eventory import Eventory
from services.modules.context import AppContext
from services.modules.components import ScheduledTasks


from ..db.models import BinomGeo
# from ..util.domains import change_proxy
from ..util.redis_utils import (
    increase_task_value,
    decrease_task_value,
    clear_task_value,
    get_available_geos,
    get_task_values
)
from ..util.leads import (
    check_lead_rate,
    is_change_domain_cooldown_pass,
    check_last_lead_time_by_geo,
    check_last_lead_time_by_user_tag
)


scheduled_tasks = ScheduledTasks()


# Идея чекеров в том что каждый тип проверки может отдавать значение коэффициента от 0 до 1,
# где 0 это все в порядке а 1 означает что проверка провалена и требуется внимание оператора или автоматическое решение
# Все таски работают в режиме: проверка каждого ГЕО раздельно
# 1 Таска: Показатель лиды/период времени (check_lead_rate_for_geos)
#          Берем 2 одинаковых прошлых периода времени
#          Eсли количество лидов уменьшилось то увеличиваем коэффициент на 0.n значение (но не более 1)
#          Если количество лидов увеличилось то уменьшаем на то же значение (но не менее 0)
#          Соответственно состояние прошлых проверок хранится между выполнениями тасок
#          Состояние этой таски обнуляется при смене домена
# 2 Таска: Время с последнего лида
#          Если по определенному гео нет лидов за последнее N количество секунд
#          То коеффициент устанавливается в 1
#          Если появился хотябы один лид то устанавливаем в 0
# 3 Таска: Тест на бан по прокси
#          Чекер автоматически выгрузит из трекера текущие домены, с офферов и прелендов
#          Затем он проверит эти домены через сконфигурированный список мобильных прокси
#          Идея в том что за каждую прокси через которую идет проверка насчитывается коэффициент если через неё
#          не получен корректный ответ
#          Если количество активных проксей менее двух то коэффициент домножается на 2
#          Статус таски обнуляется при смене домена
# 4 Таска: Проверяет статусы трех предыдущих
#          Если по N тасок коэфициент больше 1 то происходит смена домена
#          Либо если сумма коэфициентов превышает пороговое значение


@scheduled_tasks.schedule_task(
    seconds=300, start_date=datetime.now() + timedelta(seconds=5)
)
async def check_lead_rate_for_geos(ctx: AppContext):
    """
    Check all groups that have geo specified for lead rate.
    Compare two previous periods with diff_percent.
    Save check result as coefficient for later processing.
    Required leads that is incoming into database.
    :param ctx:
    :return:
    """
    for geo in await get_available_geos(user_id=ctx.user.pk):
        if geo.name.upper() not in ctx.variables.GEOS.upper():
            logger.info(
                f'[{geo.name}] check rate skipped. Geo not set to scan.'
            )
            continue

        if not await is_change_domain_cooldown_pass(geo.name, geo.domain_change_cooldown):
            logger.debug(
                f'[{geo.name}] check skipped. Cooldown is: {geo.domain_change_cooldown}sec.'
            )
            continue

        lead_rate_decreased = await LeadRecordService().check_lead_rate(
            geo=geo.name,
            last_period=geo.last_period_duration,
            previous_period=geo.previous_period_duration,
            diff_percent=geo.diff_percent,
        )

        if lead_rate_decreased:
            await Eventory.publish(
                Message(body={'geo_name': geo.name}),
                routing_keys.LEAD_RATE_CHECK_PASSED,
                ctx.app_name
            )

        #     # increase if lead rate decreased
        #     await increase_task_value(geo, 'check_lead_rate_for_geos', ctx.variables.LEAD_DECREASE_CHECK_COEFFICIENT)
        # else:
        #     # decrease if lead rate same or more
        #     await decrease_task_value(geo, 'check_lead_rate_for_geos', ctx.variables.LEAD_DECREASE_CHECK_COEFFICIENT)


# send notifications if in specific geo is no leads for amount of time
@scheduled_tasks.schedule_task(
    seconds=60,
    start_date=datetime.now() + timedelta(seconds=10)
)
async def check_time_since_last_lead(ctx: AppContext):
    """
    Task that monitoring time passed since last lead received.
    :param ctx:
    :return:
    """
    # 1. gather time when was last lead of buyer
    # 2. gather info when was last lead by geo
    # 3. if time high then IDLE time - send notify to byer
    setting = await Setting.get_or_none(key="TAG",app_id=12)
    users_tag_to_check = await SettingValue.filter(setting=setting)

    for geo in await get_available_geos(ctx.user.pk):
        last_lead_time_by_geo_passed = False
        last_lead_time_by_user_tag_passed = False

        if geo.name.upper() not in ctx.variables.GEOS.upper():
            logger.info(
                f'[{geo.name}] check time skipped. Geo not set to scan.'
            )
            continue

        last_lead_time_by_geo = await LeadRecordService().check_last_lead_time_by_geo(geo, int(geo.time_since_last_lead))
        last_lead_time_by_geo_passed = last_lead_time_by_geo > geo.time_since_last_lead

    message = {
        'geo_name': geo.name,
        'idle_check_geo_passed': last_lead_time_by_geo_passed,
        'idle_geo_time': last_lead_time_by_geo
    }

    # if context.settings.TAG:
    for user in users_tag_to_check:
        last_lead_time_by_user_tag = await LeadRecordService().check_last_lead_time_by_user_tag(user.value, int(geo.time_since_last_lead))
        last_lead_time_by_user_tag_passed = last_lead_time_by_user_tag > geo.time_since_last_lead

        if last_lead_time_by_user_tag_passed:
            message['tag_name'] = user.value
            message['idle_check_tag_passed'] = last_lead_time_by_user_tag_passed
            message['idle_tag_time'] = last_lead_time_by_user_tag

        if last_lead_time_by_geo_passed or last_lead_time_by_user_tag_passed:
            # context.logger.info(message)
            await Eventory.publish(
                Message(body=message,recipient=Recipient(user_id=user.user_id)),
                routing_keys.IDLE_GEO_CHECK_PASSED,
                ctx.app_name
            )

    #    await increase_task_value(geo, 'check_time_since_last_lead', 1.0, context.module_proxy)
    # else:
    #    await decrease_task_value(geo, 'check_time_since_last_lead', 1.0, context.module_proxy)

# tasks below is active checks for current domains in Binom by proxy
@scheduled_tasks.schedule_task(
    seconds=60,
    start_date=datetime.now() + timedelta(seconds=10)
)
async def check_current_domains(ctx: AppContext):
    pass
    # for geo in await get_available_geos(ctx.user.pk):
    #     if geo.name.upper() not in ctx.variables.GEOS.upper():
    #         logger.info(
    #             f'[{geo.name}] check current skipped. Geo not set to scan.'
    #         )
    #         continue
    #
    #     # TODO make in configurable to check one of them or both
    #     _, offers_domains = await get_offers(geo_name=geo.name, settings=ctx.variables)
    #     _, land_domains = await get_landings(geo_name=geo.name, settings=ctx.variables)
    #
    #     domains = set(offers_domains + land_domains)
    #     proxies = await get_proxy(geo, is_multi=True)
    #     proxy_count = len(proxies)
    #
    #     if not domains:
    #         logger.debug(f"[{geo.name}] No domains to check with proxy, skip geo!")
    #         continue
    #     elif not proxy_count:
    #         logger.error(f"[{geo.name}] No proxy configured, skip geo!")
    #         continue
    #     else:
    #         logger.debug(f"[{geo.name}] Check domains {', '.join(domains)} with proxy!")
    #
    #     # here can be multiple domains with different proxy check result
    #     domains_check_result = await check_current_domains_with_proxy(
    #         module_proxy=ctx.module_proxy,
    #         domains_to_check=domains,
    #         geo=geo,
    #         proxies=proxies,
    #     )
    #
    #     # calculate total False checks and increase by coefficient if any
    #     false_checks = 0
    #     for domain, proxy_check_result in domains_check_result.items():
    #         for proxy_name, check_result in proxy_check_result.items():
    #             if check_result is False:
    #                 false_checks += 1
    #
    #     # use coefficient from settings if proxy_count more than one, else coefficient equal 1.0
    #     decrease_coefficient = float(ctx.variables.PROXY_FAIL_CHECK_COEFFICIENT) if proxy_count > 1 else 1.0
    #
    #     final_coefficient = float(false_checks * decrease_coefficient)
    #
    #     task_name = f"{ctx.user.pk}:check_current_domains"
    #
    #     if final_coefficient > 0:
    #         await Eventory.publish(
    #             Message(body={
    #                 'geo_name': geo.name,
    #                 'final_coefficient': final_coefficient,
    #                 'false_checks': false_checks,
    #                 'proxy_count': proxy_count,
    #                 'domains_check_result': domains_check_result
    #             }),
    #             routing_keys.CHECK_CURRENT_DOMAINS_PASSED,
    #             ctx.app_name
    #         )
    #         await increase_task_value(geo, task_name, final_coefficient, ctx.module_proxy)
    #     else:
    #         await decrease_task_value(geo, task_name, 1.0, ctx.module_proxy)

#
# @scheduled_tasks.schedule_task(minutes=10, start_date=datetime.now() + timedelta(seconds=30))
# async def check_task_statuses(ctx: AppContext):
#     minimum_required_coefficient = ctx.variables.MINIMUM_REQUIRED_COEFFICIENT
#
#     for geo in await get_available_geos(user_id=ctx.user.pk):
#         # scan for task_values on geo
#
#         cursor, keys = await RedisService.scan(match=f'task_value:{geo.name}:{ctx.user.pk}:*')
#
#         task_check_values = await get_task_values(geo)
#
#         if not task_check_values:
#             logger.debug(f"[{geo.name}] No task values.")
#             continue
#
#         sum_values = sum(float(task_value) for task_value in task_check_values)
#
#         for i, key in enumerate(keys):
#             logger.debug(f"[{geo.name}] Task {key.replace(f'task_value:{geo.name}:', '')} -> <cyan>{task_check_values[i]}</>")
#
#         if sum_values < float(minimum_required_coefficient):
#             logger.debug(f"[{geo.name}] Tasks sum: <cyan>{sum_values}</>, minimum: <cyan>{minimum_required_coefficient}</>. No need to change domain")
#             continue
#
#         logger.info(f"[{geo.name}] Tasks sum: <cyan>{sum_values}</>, minimum: <cyan>{minimum_required_coefficient}</>. Need change domain!")
#
#         await Eventory.publish(
#             Message(body={
#                 'geo_name': geo.name,
#                 'sum_values': sum_values,
#                 'minimum_required_coefficient': minimum_required_coefficient
#             }),
#             routing_keys.CHECK_TASK_STATUSES,
#             ctx.app_name
#         )

        # new_domain, old_domains = await change_proxy(geos=[geo], variables=ctx.variables, geo_names=[])

        # if new_domain:
        #     await Eventory.publish(
        #         Message(body={
        #             'geo_name': geo.name,
        #             'new_domain': new_domain,
        #             'old_domains': old_domains
        #         }),
        #         routing_keys.DOMAIN_CHANGED,
        #         ctx.app_name
        #     )

        # await clear_task_value(geo)