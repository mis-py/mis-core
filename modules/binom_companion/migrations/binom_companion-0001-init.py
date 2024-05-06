from yoyo import step

steps = [
    step(
        """
        CREATE TABLE IF NOT EXISTS "binom_companion_changed_domains" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "from_domains" VARCHAR(255),
            "to_domain" VARCHAR(255) NOT NULL,
            "geo" VARCHAR(10),
            "offers" JSONB NOT NULL,
            "date_changed" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS "binom_companion_geo" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "name" VARCHAR(10) NOT NULL,
            "is_check" BOOL NOT NULL  DEFAULT False,
            "diff_percent" INT NOT NULL  DEFAULT 30,
            "domain_change_cooldown" INT NOT NULL  DEFAULT 1500,
            "last_period_duration" INT NOT NULL  DEFAULT 300,
            "previous_period_duration" INT NOT NULL  DEFAULT 300,
            "page" VARCHAR(255),
            "registrator" INT,
            "status" INT,
            "ban" INT,
            "domain" INT,
            "curr_geo" INT,
            "another_bans" VARCHAR(255),
            "task_check_statuses" JSONB
        );
        CREATE TABLE IF NOT EXISTS "binom_companion_domain" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "domain" VARCHAR(150) NOT NULL,
            "ip" VARCHAR(150),
            "registrator" VARCHAR(255),
            "vds_service" VARCHAR(255),
            "additional_info" TEXT,
            "status" VARCHAR(16) NOT NULL  DEFAULT 'Готово',
            "updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
            "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
            "current_geo_id" INT REFERENCES "binom_companion_geo" ("id") ON DELETE SET NULL
        );
        COMMENT ON COLUMN "binom_companion_domain"."status" IS 'DONE: Готово\nACTIVE: Активно\nUSED: Заменить домен\nREUSE: Переиспользовать\nNOT_WORK: Не работает';
        CREATE TABLE IF NOT EXISTS "binom_companion_lead_record" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "domain" VARCHAR(255) NOT NULL,
            "geo" VARCHAR(2) NOT NULL,
            "tag" VARCHAR(10) NOT NULL,
            "time" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS "binom_companion_proxy" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "address" VARCHAR(255) NOT NULL,
            "change_url" VARCHAR(255) NOT NULL,
            "name" VARCHAR(255) NOT NULL DEFAULT 'New Proxy',
            "geo_id" INT NOT NULL REFERENCES "binom_companion_geo" ("id") ON DELETE CASCADE
        );
        COMMENT ON TABLE "binom_companion_proxy" IS 'Proxy for check domains';
        CREATE TABLE IF NOT EXISTS "binom_companion_allowed_domain_geo" (
            "binom_companion_domain_id" INT NOT NULL REFERENCES "binom_companion_domain" ("id") ON DELETE CASCADE,
            "geo_id" INT NOT NULL REFERENCES "binom_companion_geo" ("id") ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS "binom_companion_banned_domain_geo" (
            "binom_companion_domain_id" INT NOT NULL REFERENCES "binom_companion_domain" ("id") ON DELETE CASCADE,
            "geo_id" INT NOT NULL REFERENCES "binom_companion_geo" ("id") ON DELETE CASCADE
        );
        """,
        """
        DROP TABLE IF EXISTS "binom_companion_changed_domains";
        DROP TABLE IF EXISTS "binom_companion_geo";
        DROP TABLE IF EXISTS "binom_companion_domain";
        DROP TABLE IF EXISTS "binom_companion_lead_record";
        DROP TABLE IF EXISTS "binom_companion_proxy";
        DROP TABLE IF EXISTS "binom_companion_allowed_domain_geo";
        DROP TABLE IF EXISTS "binom_companion_banned_domain_geo";
        """
    )
]
