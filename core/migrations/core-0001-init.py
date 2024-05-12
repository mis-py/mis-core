from yoyo import step

steps = [
    step(
        """
CREATE TABLE IF NOT EXISTS "mis_modules" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL UNIQUE,
    "enabled" BOOL NOT NULL  DEFAULT False,
    "state" VARCHAR(15) NOT NULL  DEFAULT 'pre_initialized'
);
COMMENT ON COLUMN "mis_modules"."state" IS 'PRE_INITIALIZED: pre_initialized\nINITIALIZED: initialized\nRUNNING: running\nSTOPPED: stopped\nSHUTDOWN: shutdown';
CREATE TABLE IF NOT EXISTS "mis_permissions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL,
    "scope" VARCHAR(30) NOT NULL UNIQUE,
    "app_id" INT NOT NULL REFERENCES "mis_modules" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "mis_routing_key" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "key" VARCHAR(100) NOT NULL UNIQUE,
    "name" VARCHAR(100) NOT NULL UNIQUE,
    "key_verbose" VARCHAR(255),
    "template" TEXT,
    "app_id" INT NOT NULL REFERENCES "mis_modules" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "mis_routing_key" IS 'RabbitMQ routing key from config.py in modules';
CREATE TABLE IF NOT EXISTS "mis_teams" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS "mis_users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(20) NOT NULL UNIQUE,
    "position" VARCHAR(100),
    "hashed_password" VARCHAR(200) NOT NULL,
    "disabled" BOOL NOT NULL  DEFAULT False,
    "team_id" INT REFERENCES "mis_teams" ("id") ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS "mis_routing_key_subscription" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "routing_key_id" INT NOT NULL REFERENCES "mis_routing_key" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "mis_users" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "mis_routing_key_subscription" IS 'User subscriptions to routing_keys';
CREATE TABLE IF NOT EXISTS "mis_scheduled_job" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "job_id" VARCHAR(255),
    "task_name" VARCHAR(255) NOT NULL,
    "status" VARCHAR(7) NOT NULL,
    "interval" INT,
    "cron" VARCHAR(100),
    "or_cron_list" JSONB,
    "extra_data" JSONB,
    "trigger" JSONB,
    "app_id" INT NOT NULL REFERENCES "mis_modules" ("id") ON DELETE CASCADE,
    "team_id" INT REFERENCES "mis_teams" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "mis_users" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "mis_scheduled_job"."status" IS 'PAUSED: paused\nRUNNING: running';
COMMENT ON TABLE "mis_scheduled_job" IS 'Needed for manage when to start scheduled tasks';
CREATE TABLE IF NOT EXISTS "mis_variables" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "key" VARCHAR(50) NOT NULL,
    "default_value" VARCHAR(500),
    "is_global" BOOL NOT NULL  DEFAULT True,
    "type" VARCHAR(100) NOT NULL  DEFAULT 'text',
    "app_id" INT NOT NULL REFERENCES "mis_modules" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "mis_variable_values" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "value" VARCHAR(2048) NOT NULL,
    "team_id" INT REFERENCES "mis_teams" ("id") ON DELETE CASCADE,
    "user_id" INT REFERENCES "mis_users" ("id") ON DELETE CASCADE,
    "variable_id" INT NOT NULL REFERENCES "mis_variables" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_mis_variabl_variabl_9a6f84" UNIQUE ("variable_id", "user_id"),
    CONSTRAINT "uid_mis_variabl_variabl_362069" UNIQUE ("variable_id", "team_id")
);
CREATE TABLE IF NOT EXISTS "mis_granted_permissions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "permission_id" INT NOT NULL REFERENCES "mis_permissions" ("id") ON DELETE CASCADE,
    "team_id" INT REFERENCES "mis_teams" ("id") ON DELETE CASCADE,
    "user_id" INT REFERENCES "mis_users" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_mis_granted_permiss_0db451" UNIQUE ("permission_id", "user_id"),
    CONSTRAINT "uid_mis_granted_permiss_49213d" UNIQUE ("permission_id", "team_id")
);
CREATE TABLE IF NOT EXISTS "mis_guardian_access_group" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(150) NOT NULL,
    "module_id" INT REFERENCES "mis_modules" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "mis_guardian_access_group" IS 'Stores users groups for grouping permissions';
CREATE TABLE IF NOT EXISTS "mis_guardian_content_type" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "model" VARCHAR(100) NOT NULL,
    "module_id" INT NOT NULL REFERENCES "mis_modules" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_mis_guardia_module__a620a6" UNIQUE ("module_id", "model")
);
COMMENT ON TABLE "mis_guardian_content_type" IS 'Stores all models names in project';
CREATE TABLE IF NOT EXISTS "mis_guardian_permission" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "code_name" VARCHAR(100) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "content_type_id" INT NOT NULL REFERENCES "mis_guardian_content_type" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_mis_guardia_content_e3a7c3" UNIQUE ("content_type_id", "code_name")
);
COMMENT ON TABLE "mis_guardian_permission" IS 'Stores available permissions for models objects';
CREATE TABLE IF NOT EXISTS "mis_guardian_group_permission" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "object_pk" VARCHAR(255) NOT NULL,
    "content_type_id" INT NOT NULL REFERENCES "mis_guardian_content_type" ("id") ON DELETE CASCADE,
    "group_id" INT NOT NULL REFERENCES "mis_guardian_access_group" ("id") ON DELETE CASCADE,
    "permission_id" INT NOT NULL REFERENCES "mis_guardian_permission" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "mis_guardian_group_permission" IS 'Stores group permissions on objects';
CREATE TABLE IF NOT EXISTS "mis_guardian_user_permission" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "object_pk" VARCHAR(255) NOT NULL,
    "content_type_id" INT NOT NULL REFERENCES "mis_guardian_content_type" ("id") ON DELETE CASCADE,
    "permission_id" INT NOT NULL REFERENCES "mis_guardian_permission" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "mis_users" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "mis_guardian_user_permission" IS 'Stores user permissions on objects';
CREATE TABLE IF NOT EXISTS "mis_guardian_user_group_relation" (
    "mis_guardian_access_group_id" INT NOT NULL REFERENCES "mis_guardian_access_group" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "mis_users" ("id") ON DELETE CASCADE
);
        """,
        """
DROP TABLE IF EXISTS "mis_modules";		
DROP TABLE IF EXISTS "mis_permissions";
DROP TABLE IF EXISTS "mis_routing_key";		
DROP TABLE IF EXISTS "mis_teams";		
DROP TABLE IF EXISTS "mis_users";		
DROP TABLE IF EXISTS "mis_routing_key_subscription";		
DROP TABLE IF EXISTS "mis_scheduled_job";		
DROP TABLE IF EXISTS "mis_variables";		
DROP TABLE IF EXISTS "mis_variable_values";		
DROP TABLE IF EXISTS "mis_granted_permissions";	
DROP TABLE IF EXISTS "mis_guardian_access_group";		
DROP TABLE IF EXISTS "mis_guardian_content_type";		
DROP TABLE IF EXISTS "mis_guardian_permission";		
DROP TABLE IF EXISTS "mis_guardian_group_permission";		
DROP TABLE IF EXISTS "mis_guardian_user_permission";
        """
    )
]