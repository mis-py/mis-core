from yoyo import step

steps = [
    step(
        """
CREATE TABLE IF NOT EXISTS "dummy_dummy" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "dummy_string" VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS "dummy_restricted_dummy" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "dummy_int" INT NOT NULL
);
        """,
        """
DROP TABLE IF EXISTS "dummy_dummy";	
DROP TABLE IF EXISTS "dummy_restricted_dummy";	
        """
    )
]