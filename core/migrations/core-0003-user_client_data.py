from yoyo import step

steps = [
    step(
        """
        ALTER TABLE IF EXISTS "mis_users" ADD COLUMN IF NOT EXISTS client_data JSONB NOT NULL DEFAULT '{}'::jsonb;
        """,
        """
        ALTER TABLE IF EXISTS "mis_users" DROP COLUMN IF EXISTS client_data;
        """
    )
]