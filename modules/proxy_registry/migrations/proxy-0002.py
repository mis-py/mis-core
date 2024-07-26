from yoyo import step

steps = [
    step(
        """
        ALTER TABLE proxy_registry_proxy ALTER COLUMN object_id DROP NOT NULL;
        """,
        """
        ALTER TABLE proxy_registry_proxy ALTER COLUMN object_id SET NOT NULL;
        """
    )
]
