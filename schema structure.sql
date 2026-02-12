


CREATE TABLE websites (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    url VARCHAR(500) NOT NULL,
    monitoring_interval INTEGER NOT NULL,       -- in minutes
    response_threshold INTEGER NOT NULL,        -- in ms
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



CREATE TABLE incidents (
    id SERIAL PRIMARY KEY,
    website_id INTEGER NOT NULL,
    incident_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20),
    description TEXT,
    probable_cause TEXT,
    suggestion TEXT,
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP,
    duration_seconds INTEGER,
    is_resolved BOOLEAN DEFAULT FALSE,

    CONSTRAINT fk_incidents_website
        FOREIGN KEY (website_id)
        REFERENCES websites(id)
        ON DELETE CASCADE
);


CREATE TABLE monitoring_checks (
    id SERIAL PRIMARY KEY,
    website_id INTEGER NOT NULL,
    status_code INTEGER,
    response_time DOUBLE PRECISION,
    is_up BOOLEAN NOT NULL,
    error_message TEXT,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_checks_website
        FOREIGN KEY (website_id)
        REFERENCES websites(id)
        ON DELETE CASCADE
);

CREATE TABLE subpages (
    id SERIAL PRIMARY KEY,
    website_id INTEGER NOT NULL,
    url VARCHAR(500) NOT NULL,
    name VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,

    CONSTRAINT fk_subpages_website
        FOREIGN KEY (website_id)
        REFERENCES websites(id)
        ON DELETE CASCADE
);

