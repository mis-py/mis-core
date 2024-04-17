from yoyo import step

steps = [
    step(
        """
        CREATE TYPE AppState AS ENUM ('pre_initialized', 'initialized', 'running', 'stopped', 'shutdown', 'error');
        ALTER TABLE IF EXISTS public.mis_apps ADD COLUMN state AppState NOT NULL DEFAULT 'pre_initialized';
        """,
        """
        DROP TYPE IF EXISTS AppState;
        ALTER TABLE IF EXISTS public.mis_apps DROP COLUMN IF EXISTS state;
        """
    )
]
