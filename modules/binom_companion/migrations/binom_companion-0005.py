from yoyo import step

steps = [
    step(
        """
CREATE TABLE IF NOT EXISTS "binom_companion_proxy_domain_tracker_instance_relation" (
    "binom_companion_proxy_domains_id" INT NOT NULL REFERENCES "binom_companion_proxy_domains" ("id") ON DELETE CASCADE,
    "trackerinstance_id" INT NOT NULL REFERENCES "binom_companion_tracker_instances" ("id") ON DELETE CASCADE
);
        """,
        """
DROP TABLE IF EXISTS "binom_companion_proxy_domain_tracker_instance_relation";    
        """
    )
]