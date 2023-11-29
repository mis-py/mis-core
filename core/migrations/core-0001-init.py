from yoyo import step

steps = [
    step(
        """
        CREATE TABLE IF NOT EXISTS "mis_apps" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "name" VARCHAR(50) NOT NULL UNIQUE,
            "enabled" BOOL NOT NULL  DEFAULT True
        );
        CREATE TABLE IF NOT EXISTS "mis_permissions" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "name" VARCHAR(50) NOT NULL,
            "scope" VARCHAR(30) NOT NULL UNIQUE,
            "app_id" INT NOT NULL REFERENCES "mis_apps" ("id") ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS "mis_restricted_objects" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "object_id" VARCHAR(150) NOT NULL,
            "object_app_id" INT REFERENCES "mis_apps" ("id") ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS "mis_routing_key" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "key" VARCHAR(100) NOT NULL UNIQUE,
            "name" VARCHAR(100) NOT NULL UNIQUE,
            "key_verbose" VARCHAR(255),
            "template" TEXT,
            "app_id" INT NOT NULL REFERENCES "mis_apps" ("id") ON DELETE CASCADE
        );
        COMMENT ON TABLE "mis_routing_key" IS 'RabbitMQ routing key from config.py in modules';
        CREATE TABLE IF NOT EXISTS "mis_settings" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "key" VARCHAR(50) NOT NULL,
            "default_value" VARCHAR(500),
            "is_global" BOOL NOT NULL  DEFAULT True,
            "type" VARCHAR(100) NOT NULL  DEFAULT 'text',
            "app_id" INT NOT NULL REFERENCES "mis_apps" ("id") ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS "mis_teams" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "name" VARCHAR(50) NOT NULL
        );
        CREATE TABLE IF NOT EXISTS "mis_users" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "username" VARCHAR(20) NOT NULL UNIQUE,
            "position" VARCHAR(100),
            "hashed_password" VARCHAR(200) NOT NULL,
            "disabled" BOOL NOT NULL  DEFAULT False,
            "signed_in" BOOL NOT NULL  DEFAULT False,
            "team_id" INT REFERENCES "mis_teams" ("id") ON DELETE SET NULL
        );
        CREATE TABLE IF NOT EXISTS "mis_grantedpermissions" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "permission_id" INT NOT NULL REFERENCES "mis_permissions" ("id") ON DELETE CASCADE,
            "team_id" INT REFERENCES "mis_teams" ("id") ON DELETE CASCADE,
            "user_id" INT REFERENCES "mis_users" ("id") ON DELETE CASCADE,
            CONSTRAINT "uid_mis_granted_permiss_2aebab" UNIQUE ("permission_id", "user_id"),
            CONSTRAINT "uid_mis_granted_permiss_e83094" UNIQUE ("permission_id", "team_id")
        );
        CREATE TABLE IF NOT EXISTS "mis_routing_key_subscription" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "routing_key_id" INT NOT NULL REFERENCES "mis_routing_key" ("id") ON DELETE CASCADE,
            "user_id" INT NOT NULL REFERENCES "mis_users" ("id") ON DELETE CASCADE
        );
        COMMENT ON TABLE "mis_routing_key_subscription" IS 'User subscriptions to routing_keys';
        CREATE TABLE IF NOT EXISTS "mis_scheduled_job" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "job_id" VARCHAR(255) NOT NULL UNIQUE,
            "name" VARCHAR(255) NOT NULL,
            "status" VARCHAR(7) NOT NULL,
            "interval" INT,
            "cron" VARCHAR(100),
            "or_cron_list" JSONB,
            "extra_data" JSONB,
            "app_id" INT NOT NULL REFERENCES "mis_apps" ("id") ON DELETE CASCADE,
            "team_id" INT REFERENCES "mis_teams" ("id") ON DELETE CASCADE,
            "user_id" INT NOT NULL REFERENCES "mis_users" ("id") ON DELETE CASCADE
        );
        COMMENT ON COLUMN "mis_scheduled_job"."status" IS 'PAUSED: paused\nRUNNING: running';
        COMMENT ON TABLE "mis_scheduled_job" IS 'Needed for manage when to start scheduled tasks';
        CREATE TABLE IF NOT EXISTS "mis_setting_values" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "value" VARCHAR(500) NOT NULL,
            "setting_id" INT NOT NULL REFERENCES "mis_settings" ("id") ON DELETE CASCADE,
            "team_id" INT REFERENCES "mis_teams" ("id") ON DELETE CASCADE,
            "user_id" INT REFERENCES "mis_users" ("id") ON DELETE CASCADE,
            CONSTRAINT "uid_mis_setting_setting_904166" UNIQUE ("setting_id", "user_id"),
            CONSTRAINT "uid_mis_setting_setting_fe119e" UNIQUE ("setting_id", "team_id")
        );
        CREATE TABLE IF NOT EXISTS "mis_usergroup" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "name" VARCHAR(150) NOT NULL,
            "app_id" INT REFERENCES "mis_apps" ("id") ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS "mis_group_permission_flags" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "model_name" VARCHAR(150) NOT NULL,
            "update" BOOL NOT NULL  DEFAULT False,
            "delete" BOOL NOT NULL  DEFAULT False,
            "group_id" INT NOT NULL REFERENCES "mis_usergroup" ("id") ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS "mis_object_group_relation" (
            "mis_usergroup_id" INT NOT NULL REFERENCES "mis_usergroup" ("id") ON DELETE CASCADE,
            "restrictedobject_id" INT NOT NULL REFERENCES "mis_restricted_objects" ("id") ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS "mis_user_group_relation" (
            "mis_usergroup_id" INT NOT NULL REFERENCES "mis_usergroup" ("id") ON DELETE CASCADE,
            "user_id" INT NOT NULL REFERENCES "mis_users" ("id") ON DELETE CASCADE
        );
        """,
        """
        DROP TABLE IF EXISTS "mis_apps";
        DROP TABLE IF EXISTS "mis_permissions";
        DROP TABLE IF EXISTS "mis_restricted_objects";
        DROP TABLE IF EXISTS "mis_routing_key";
        DROP TABLE IF EXISTS "mis_settings";
        DROP TABLE IF EXISTS "mis_teams";
        DROP TABLE IF EXISTS "mis_users";
        DROP TABLE IF EXISTS "mis_grantedpermissions";
        DROP TABLE IF EXISTS "mis_routing_key_subscription";
        DROP TABLE IF EXISTS "mis_scheduled_job";
        DROP TABLE IF EXISTS "mis_usergroup";
        DROP TABLE IF EXISTS "mis_group_permission_flags";
        DROP TABLE IF EXISTS "mis_object_group_relation";
        DROP TABLE IF EXISTS "mis_user_group_relation";
        """
    )
]
