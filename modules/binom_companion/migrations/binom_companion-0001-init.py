from yoyo import step

steps = [
    step(
        """
CREATE TABLE IF NOT EXISTS "binom_companion_lead_record" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "origin" VARCHAR(255) NOT NULL,
    "tag" VARCHAR(255) NOT NULL,
    "date_created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "ip" VARCHAR(255) NOT NULL,
    "ua" VARCHAR(8192) NOT NULL,
    "country" VARCHAR(255) NOT NULL,
    "us" VARCHAR(255) NOT NULL,
    "uc" VARCHAR(255) NOT NULL,
    "un" VARCHAR(255) NOT NULL,
    "ut" VARCHAR(255) NOT NULL,
    "um" VARCHAR(255) NOT NULL,
    "clickid" VARCHAR(1024) NOT NULL,
    "item_id" VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS "binom_companion_tracker_instances" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "description" VARCHAR(1024) NOT NULL,
    "api_key" VARCHAR(1024) NOT NULL,
    "base_url" VARCHAR(2048) NOT NULL,
    "get_route" VARCHAR(1024) NOT NULL,
    "edit_route" VARCHAR(1024) NOT NULL
);
CREATE TABLE IF NOT EXISTS "binom_companion_proxy_domains" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(2048) NOT NULL UNIQUE,
    "date_added" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "tracker_instance_id" INT NOT NULL REFERENCES "binom_companion_tracker_instances" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "binom_companion_replacement_groups" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "description" VARCHAR(1024) NOT NULL,
    "offer_group_id" INT NOT NULL,
    "offer_geo" VARCHAR(1024) NOT NULL,
    "offer_name_regexp_pattern" VARCHAR(8192) NOT NULL,
    "land_group_id" INT NOT NULL,
    "land_language" VARCHAR(1024) NOT NULL,
    "land_name_regexp_pattern" VARCHAR(8192) NOT NULL,
    "is_active" BOOL NOT NULL  DEFAULT False,
    "tracker_instance_id" INT NOT NULL REFERENCES "binom_companion_tracker_instances" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "binom_companion_replacement_history" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "offers" JSONB NOT NULL,
    "lands" JSONB NOT NULL,
    "date_changed" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "replaced_by_id" INT NOT NULL REFERENCES "mis_users" ("id") ON DELETE CASCADE,
    "replacement_group_id" INT NOT NULL REFERENCES "binom_companion_replacement_groups" ("id") ON DELETE CASCADE,
    "to_domain_id" INT NOT NULL REFERENCES "binom_companion_proxy_domains" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "binom_companion_replacement_history_from_domain_relation" (
    "binom_companion_replacement_history_id" INT NOT NULL REFERENCES "binom_companion_replacement_history" ("id") ON DELETE CASCADE,
    "proxydomain_id" INT NOT NULL REFERENCES "binom_companion_proxy_domains" ("id") ON DELETE CASCADE
);
        """,
        """
DROP TABLE IF EXISTS "binom_companion_lead_record";	
DROP TABLE IF EXISTS "binom_companion_tracker_instances";		
DROP TABLE IF EXISTS "binom_companion_proxy_domains";
DROP TABLE IF EXISTS "binom_companion_replacement_groups";		
DROP TABLE IF EXISTS "binom_companion_replacement_history";		
DROP TABLE IF EXISTS "binom_companion_replacement_history_from_domain_relation";    
        """
    )
]