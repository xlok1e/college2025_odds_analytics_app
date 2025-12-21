CREATE TABLE countries (
    country_id SERIAL PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL,
    country_code VARCHAR(3) NOT NULL UNIQUE
);

CREATE TABLE sports (
    sport_id SERIAL PRIMARY KEY,
    sport_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE teams (
    team_id SERIAL PRIMARY KEY,
    team_name VARCHAR(200) NOT NULL,
    sport_id INT NOT NULL REFERENCES sports(sport_id) ON DELETE CASCADE,
    country_id INT REFERENCES countries(country_id) ON DELETE SET NULL
);

CREATE TABLE tournaments (
    tournament_id SERIAL PRIMARY KEY,
    tournament_name VARCHAR(200) NOT NULL,
    sport_id INT NOT NULL REFERENCES sports(sport_id) ON DELETE CASCADE,
    country_id INT REFERENCES countries(country_id) ON DELETE SET NULL
);

CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    team1_id INT NOT NULL REFERENCES teams(team_id) ON DELETE CASCADE,
    team2_id INT NOT NULL REFERENCES teams(team_id) ON DELETE CASCADE,
    tournament_id INT NOT NULL REFERENCES tournaments(tournament_id) ON DELETE CASCADE,
    event_datetime TIMESTAMP NOT NULL,

    -- Результаты матча (NULL если матч ещё не сыгран)
    is_finished BOOLEAN DEFAULT FALSE,
    winner_team_id INT REFERENCES teams(team_id) ON DELETE SET NULL,
    team1_score INT CHECK (team1_score >= 0),
    team2_score INT CHECK (team2_score >= 0),
    finished_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bookmakers (
    bookmaker_id SERIAL PRIMARY KEY,
    bookmaker_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE bet_types (
    bet_type_id SERIAL PRIMARY KEY,
    bet_type_code VARCHAR(50) NOT NULL UNIQUE,
    bet_type_name VARCHAR(100) NOT NULL,
    has_parameter BOOLEAN DEFAULT FALSE
);

CREATE TABLE odds_records (
    odds_record_id SERIAL PRIMARY KEY,
    event_id INT NOT NULL REFERENCES events(event_id) ON DELETE CASCADE,
    bookmaker_id INT NOT NULL REFERENCES bookmakers(bookmaker_id) ON DELETE CASCADE,
    bet_type_id INT NOT NULL REFERENCES bet_types(bet_type_id) ON DELETE CASCADE,

    bet_parameter DECIMAL(10,2),

    odds_value DECIMAL(10,2) NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_odds_record UNIQUE (event_id, bookmaker_id, bet_type_id, bet_parameter, recorded_at)
);

CREATE INDEX idx_events_datetime ON events(event_datetime);
CREATE INDEX idx_events_tournament ON events(tournament_id);
CREATE INDEX idx_odds_records_event ON odds_records(event_id);
CREATE INDEX idx_odds_records_recorded_at ON odds_records(recorded_at);
CREATE INDEX idx_teams_sport ON teams(sport_id);
