from yoyo import step

steps = [
    step(
        """
        ALTER TABLE IF EXISTS public.mis_scheduled_job RENAME "name" TO "task_name";
        """,
        """
        ALTER TABLE IF EXISTS public.mis_scheduled_job RENAME "task_name" TO "name";
        """
    )
]
