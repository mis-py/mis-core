from yoyo import step

steps = [
    step(
        """
ALTER TABLE IF EXISTS "binom_companion_proxy_domains" ALTER COLUMN tracker_instance_id DROP NOT NULL;;
        """,
        """
ALTER TABLE IF EXISTS "binom_companion_proxy_domains" ALTER COLUMN tracker_instance_id SET NOT NULL;;
        """
    )
]