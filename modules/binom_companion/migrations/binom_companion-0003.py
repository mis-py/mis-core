from yoyo import step

steps = [
    step(
        """
ALTER TABLE IF EXISTS "binom_companion_proxy_domains" ADD COLUMN is_ready boolean DEFAULT false;
ALTER TABLE IF EXISTS "binom_companion_proxy_domains" ADD COLUMN server_name character varying(2048);
        """,
        """
ALTER TABLE IF EXISTS "binom_companion_proxy_domains" DROP COLUMN IF EXISTS is_ready;
ALTER TABLE IF EXISTS "binom_companion_proxy_domains" DROP COLUMN IF EXISTS server_name;
        """
    )
]