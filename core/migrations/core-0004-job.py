from yoyo import step

steps = [
    step(
        """
        ALTER TABLE IF EXISTS public.mis_scheduled_job ALTER COLUMN job_id DROP NOT NULL;
        ALTER TABLE IF EXISTS public.mis_scheduled_job ADD COLUMN trigger jsonb;
        """,
        """
        ALTER TABLE IF EXISTS public.mis_scheduled_job ALTER COLUMN job_id SET NOT NULL;
        ALTER TABLE IF EXISTS public.mis_scheduled_job DROP COLUMN IF EXISTS trigger;
        """
    )
]
