CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_users_username ON users(username);

CREATE TABLE IF NOT EXISTS detection_requests (
    id VARCHAR(36) PRIMARY KEY,
    media_type VARCHAR(20) NOT NULL,
    sha256_hash VARCHAR(64) NOT NULL UNIQUE,
    verdict VARCHAR(10) NOT NULL,
    confidence FLOAT NOT NULL,
    ensemble_method VARCHAR(20) NOT NULL,
    inference_time FLOAT NOT NULL,
    full_response_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_detection_requests_sha256_hash ON detection_requests(sha256_hash);
