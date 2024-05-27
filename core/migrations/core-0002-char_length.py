from yoyo import step

steps = [
    step(
        """
            ALTER TABLE public.mis_permissions ALTER COLUMN name TYPE character varying(1024);
            
            ALTER TABLE public.mis_permissions ALTER COLUMN scope TYPE character varying(1024);
        """,
        """
            ALTER TABLE public.mis_permissions ALTER COLUMN name TYPE character varying(50);
            
            ALTER TABLE public.mis_permissions ALTER COLUMN scope TYPE character varying(30);
        """
    )
]