CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    language_code VARCHAR(10) DEFAULT 'en',
    current_subscription_status BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sessions (
    session_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Session start time
    shutdown_time TIMESTAMP,                         -- Session end time
    ram_usage_mb DECIMAL(10, 2),                     -- RAM usage in MB
    errors TEXT,                                     -- Any errors during the session
    session_duration_sec INT                         -- Session duration in seconds
);

CREATE TABLE IF NOT EXISTS summaries (
    summary_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,  -- Foreign key to users
    session_id INT REFERENCES sessions(session_id) ON DELETE CASCADE,  -- Foreign key to sessions
    video_id VARCHAR(50),  -- YouTube video ID
    video_url VARCHAR(100) NOT NULL,  -- YouTube video URL
    language_code VARCHAR(10),  -- Language code for the summary
    text_summary TEXT,  -- Text summary of the video
    input_tokens INT,  -- Number of input tokens
    output_tokens INT,  -- Number of output tokens
    summary_model VARCHAR(100),  -- GPT model used
    requested_audio BOOLEAN DEFAULT FALSE,  -- Whether audio summary was requested
    got_audio BOOLEAN DEFAULT FALSE,  -- Whether audio summary was generated
    tts_model VARCHAR(100),  -- TTS model used for audio summary
    tts_tokens INT,  -- Number of tokens used by TTS
    created_at TIMESTAMP,  -- set creation timestamp
    UNIQUE (video_id, language_code)  -- Ensure each video summary is unique for a language
);

