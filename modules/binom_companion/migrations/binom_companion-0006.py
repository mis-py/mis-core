import asyncio

from loguru import logger
from yoyo import step

from modules.binom_companion.db.models import TrackerInstance, ProxyDomain


async def transfer_data_to_new_table():
    logger.info("Start transferring all ProxyDomain to all TrackerInstance")

    tracker_instances = await TrackerInstance.all()
    proxy_domains = await ProxyDomain.all()

    for proxy_domain in proxy_domains:
        await proxy_domain.tracker_instances.clear()
        await proxy_domain.tracker_instances.add(*tracker_instances)
        logger.debug(f"[M2M] [{proxy_domain.name}] Added to trackers {[tracker.name for tracker in tracker_instances]}")

    logger.info("Transferring finished")


def apply_step(conn):
    asyncio.create_task(transfer_data_to_new_table())


def rollback_step(conn):
    pass


steps = [
    step(apply_step, rollback_step)
]
