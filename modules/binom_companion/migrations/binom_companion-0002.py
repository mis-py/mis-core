from yoyo import step

steps = [
    step(
        """
ALTER TABLE IF EXISTS "binom_companion_proxy_domains" ADD COLUMN is_invalid boolean DEFAULT true;
ALTER TABLE IF EXISTS "binom_companion_replacement_history" ADD COLUMN reason character varying(2048);
        """,
        """
ALTER TABLE IF EXISTS "binom_companion_proxy_domains" DROP COLUMN IF EXISTS is_invalid;
ALTER TABLE IF EXISTS "binom_companion_replacement_history" DROP COLUMN IF EXISTS reason;
        """
    )
]