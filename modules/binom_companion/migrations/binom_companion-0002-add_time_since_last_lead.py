from yoyo import step

steps = [
    step(
        """
        ALTER TABLE "binom_companion_geo" ADD "time_since_last_lead" INT DEFAULT 300;
        """,
        """
        ALTER TABLE "binom_companion_geo" DROP COLUMN "time_since_last_lead";
        """
    )
]
