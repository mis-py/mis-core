from yoyo import step

steps = [
    step(
        """
        ALTER TABLE IF EXISTS public.mis_scheduled_job ALTER COLUMN job_id DROP NOT NULL;
        ALTER TABLE IF EXISTS public.mis_scheduled_job ADD COLUMN trigger jsonb;
        CREATE TYPE AppState AS ENUM ('pre_initialized', 'initialized', 'running', 'stopped', 'shutdown', 'error');
        ALTER TABLE IF EXISTS public.mis_apps ADD COLUMN state AppState NOT NULL DEFAULT 'pre_initialized';
        """,
        """
        ALTER TABLE IF EXISTS public.mis_scheduled_job ALTER COLUMN job_id SET NOT NULL;
        ALTER TABLE IF EXISTS public.mis_scheduled_job DROP COLUMN IF EXISTS trigger;
        DROP TYPE IF EXISTS AppState;
        ALTER TABLE IF EXISTS public.mis_apps DROP COLUMN IF EXISTS state;
        """
    )
]
