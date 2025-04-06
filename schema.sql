CREATE TABLE eeg_data (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT timezone('UTC', NOW()),
    event_time DOUBLE PRECISION NOT NULL,   
    unix_timestamp DOUBLE PRECISION NOT NULL,  
    lsl_timestamp DOUBLE PRECISION NOT NULL,
    round_id TEXT NOT NULL,
    player_id TEXT NOT NULL,
    labels TEXT[] NOT NULL,
    eeg_data FLOAT[] NOT NULL,
    CONSTRAINT fk_round_eeg FOREIGN KEY (round_id) REFERENCES rounds (round_id)
);

-- Indexes for EEG data
CREATE INDEX idx_eeg_round_id ON eeg_data (round_id);
CREATE INDEX idx_eeg_event_time ON eeg_data (event_time);


CREATE TABLE metrics_data (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT timezone('UTC', NOW()),
    event_time DOUBLE PRECISION NOT NULL,   
    unix_timestamp DOUBLE PRECISION NOT NULL,  
    lsl_timestamp DOUBLE PRECISION NOT NULL,
    round_id TEXT NOT NULL,
    player_id TEXT NOT NULL,
    labels TEXT[] NOT NULL,
    metrics_data FLOAT[] NOT NULL,
    CONSTRAINT fk_round_metrics FOREIGN KEY (round_id) REFERENCES rounds (round_id)
);

-- Indexes for EEG Metrics data
CREATE INDEX idx_metrics_round_id ON metrics_data (round_id);
CREATE INDEX idx_metrics_event_time ON metrics_data (event_time);


