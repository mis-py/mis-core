from yoyo import step

steps = [
    step(
        """
ALTER TABLE IF EXISTS "binom_companion_tracker_instances" ADD COLUMN IF NOT EXISTS tracker_type VARCHAR(15) NOT NULL DEFAULT 'binom';
        """,
        """
ALTER TABLE IF EXISTS "binom_companion_tracker_instances" DROP COLUMN IF EXISTS tracker_type;
        """
    )
]