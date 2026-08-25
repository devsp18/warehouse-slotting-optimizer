CREATE TABLE IF NOT EXISTS slots (
    slot_id          VARCHAR NOT NULL,
    aisle            INTEGER NOT NULL,
    bay              INTEGER NOT NULL,
    level            INTEGER NOT NULL,
    distance_ft      DOUBLE  NOT NULL,
    travel_time_sec  DOUBLE  NOT NULL,
    pick_penalty_sec DOUBLE  NOT NULL,
    total_time_sec   DOUBLE  NOT NULL
);

CREATE TABLE IF NOT EXISTS sku_velocity (
    sku            VARCHAR NOT NULL,
    annual_picks   DOUBLE  NOT NULL,
    velocity_rank  VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS optimal_assignment (
    sku             VARCHAR NOT NULL,
    annual_picks    DOUBLE  NOT NULL,
    velocity_rank   VARCHAR NOT NULL,
    slot_id         VARCHAR NOT NULL,
    total_time_sec  DOUBLE  NOT NULL,
    annual_time_sec DOUBLE  NOT NULL
);

CREATE TABLE IF NOT EXISTS baseline_assignment (
    sku             VARCHAR NOT NULL,
    annual_picks    DOUBLE  NOT NULL,
    velocity_rank   VARCHAR NOT NULL,
    slot_id         VARCHAR NOT NULL,
    total_time_sec  DOUBLE  NOT NULL,
    annual_time_sec DOUBLE  NOT NULL
);
