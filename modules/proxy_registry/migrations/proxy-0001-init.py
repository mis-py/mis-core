from yoyo import step

steps = [
    step(
        """
        CREATE TABLE IF NOT EXISTS "proxy_registry_proxy" (
        "id" SERIAL NOT NULL PRIMARY KEY,
        "address" VARCHAR(255) NOT NULL,
        "change_url" VARCHAR(255),
        "name" VARCHAR(255) NOT NULL DEFAULT 'New proxy',
        "object_id" VARCHAR(255) NOT NULL,
        "proxy_type" VARCHAR(255) NOT NULL,
        "is_online" BOOLEAN NOT NULL DEFAULT TRUE,
        "is_enabled" BOOLEAN NOT NULL DEFAULT TRUE
        );;
        """,
        """
        DROP TABLE IF EXISTS "proxy_registry_proxy";
        """
    )
]
