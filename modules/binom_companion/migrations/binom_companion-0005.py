import asyncio

from loguru import logger
from yoyo import step

from modules.binom_companion.db.models import TrackerInstance


async def transfer_data_to_new_table():
    logger.info("Start transferring data to new table")

    tracker_instance = await TrackerInstance.first()
    proxy_domains_deprecated = await tracker_instance.proxy_domains_deprecated.all()
    proxy_domains_new = await tracker_instance.proxy_domains.all()

    for proxy_domain in proxy_domains_deprecated:
        if proxy_domain in proxy_domains_new:
            continue

        await proxy_domain.tracker_instances.add(tracker_instance)
        logger.debug(f"[M2M] TrackerInstance '{tracker_instance.name}' - ProxyDomain '{proxy_domain.name}'")

    logger.info("Transferring finished")


def apply_step(conn):
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS "binom_companion_proxy_domain_tracker_instance_relation" (
            "binom_companion_proxy_domains_id" INT NOT NULL REFERENCES "binom_companion_proxy_domains" ("id") ON DELETE CASCADE,
            "trackerinstance_id" INT NOT NULL REFERENCES "binom_companion_tracker_instances" ("id") ON DELETE CASCADE
        );
        """
    )

    asyncio.create_task(transfer_data_to_new_table())


def rollback_step(conn):
    cursor = conn.cursor()
    cursor.execute(
        """
        DROP TABLE IF EXISTS "binom_companion_proxy_domain_tracker_instance_relation";    
        """
    )


steps = [
    step(apply_step, rollback_step)
]
