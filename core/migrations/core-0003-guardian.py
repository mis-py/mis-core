from yoyo import step

steps = [
    step(
        """
        CREATE TABLE IF NOT EXISTS "mis_guardian_access_group" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "name" VARCHAR(150) NOT NULL,
            "module_id" INT REFERENCES "mis_apps" ("id") ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS "mis_guardian_content_type" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "model" VARCHAR(100) NOT NULL,
            "module_id" INT NOT NULL REFERENCES "mis_apps" ("id") ON DELETE CASCADE,
            CONSTRAINT "uid_mis_guardia_module__a620a6" UNIQUE ("module_id", "model")
        );
        CREATE TABLE IF NOT EXISTS "mis_guardian_permission" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "code_name" VARCHAR(100) NOT NULL,
            "name" VARCHAR(255) NOT NULL,
            "content_type_id" INT NOT NULL REFERENCES "mis_guardian_content_type" ("id") ON DELETE CASCADE,
            CONSTRAINT "uid_mis_guardia_content_e3a7c3" UNIQUE ("content_type_id", "code_name")
        );
        CREATE TABLE IF NOT EXISTS "mis_guardian_group_permission" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "object_pk" VARCHAR(255) NOT NULL,
            "content_type_id" INT NOT NULL REFERENCES "mis_guardian_content_type" ("id") ON DELETE CASCADE,
            "group_id" INT NOT NULL REFERENCES "mis_guardian_access_group" ("id") ON DELETE CASCADE,
            "permission_id" INT NOT NULL REFERENCES "mis_guardian_permission" ("id") ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS "mis_guardian_user_permission" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "object_pk" VARCHAR(255) NOT NULL,
            "content_type_id" INT NOT NULL REFERENCES "mis_guardian_content_type" ("id") ON DELETE CASCADE,
            "permission_id" INT NOT NULL REFERENCES "mis_guardian_permission" ("id") ON DELETE CASCADE,
            "user_id" INT NOT NULL REFERENCES "mis_users" ("id") ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS "mis_guardian_user_group_relation" (
            "mis_guardian_access_group_id" INT NOT NULL REFERENCES "mis_guardian_access_group" ("id") ON DELETE CASCADE,
            "user_id" INT NOT NULL REFERENCES "mis_users" ("id") ON DELETE CASCADE
        );
        """,
        """
        DROP TABLE IF EXISTS "mis_guardian_access_group";
        DROP TABLE IF EXISTS "mis_guardian_content_type";
        DROP TABLE IF EXISTS "mis_guardian_permission";
        DROP TABLE IF EXISTS "mis_guardian_group_permission";
        DROP TABLE IF EXISTS "mis_guardian_user_permission";
        DROP TABLE IF EXISTS "mis_guardian_user_group_relation";
        """
    )
]
