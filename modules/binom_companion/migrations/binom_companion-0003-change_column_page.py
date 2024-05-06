from yoyo import step

steps = [
    step(
        """
        UPDATE public.binom_companion_geo SET "page" = NULL;
        
        ALTER TABLE IF EXISTS public.binom_companion_geo RENAME "page" TO "tracker";

        ALTER TABLE public.binom_companion_geo 
            ALTER COLUMN "tracker" TYPE integer USING tracker::integer;
        """,
        """
        UPDATE public.binom_companion_geo SET "tracker" = NULL;
        
        ALTER TABLE IF EXISTS public.binom_companion_geo RENAME "tracker" TO "page";
        
        ALTER TABLE public.binom_companion_geo 
            ALTER COLUMN "tracker" TYPE character varying(255) COLLATE pg_catalog."default";
        """
    )
]
