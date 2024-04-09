from yoyo import step

steps = [
    step(
        """
        ALTER TABLE IF EXISTS public.mis_scheduled_job
            ALTER COLUMN job_id DROP NOT NULL;
        """,
        """
        ALTER TABLE IF EXISTS public.mis_scheduled_job
            ALTER COLUMN job_id SET NOT NULL;
        """
    )
]
