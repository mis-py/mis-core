from yoyo import step

steps = [
    step(
        """
        ALTER TABLE "binom_companion_geo" ADD "user_id" INT REFERENCES "binom_companion_geo" ("id") ON DELETE CASCADE DEFAULT 1;
        """,
        """
        ALTER TABLE "binom_companion_geo" DROP COLUMN "user_id";
        """
    )
]
