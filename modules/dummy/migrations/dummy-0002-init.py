from yoyo import step

steps = [
    step(
        """
CREATE TABLE IF NOT EXISTS "dummy_group_dummy"
(
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
);
CREATE TABLE IF NOT EXISTS "dummy_category_dummy"
(
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "group_id" INT REFERENCES "dummy_group_dummy" ("id") ON DELETE CASCADE,
);
CREATE TABLE IF NOT EXISTS "dummy_element_dummy"
(
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "is_visible" BOOL NOT NULL  DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "category_id" INT REFERENCES "dummy_category_dummy" ("id") ON DELETE CASCADE,
)
        """,
        """
DROP TABLE IF EXISTS "dummy_group_dummy";
DROP TABLE IF EXISTS "dummy_category_dummy";
DROP TABLE IF EXISTS "dummy_elements_dummy";
        """
    )
]