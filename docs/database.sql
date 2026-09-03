-- Users Tabelle
CREATE TABLE users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  username TEXT NOT NULL UNIQUE,
  email TEXT NOT NULL UNIQUE,
  created_at TIMESTAMP DEFAULT now()
);

-- Matchdays Tabelle
CREATE TABLE matchdays (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  season TEXT NOT NULL,
  matchday_number INT NOT NULL,
  deadline TIMESTAMP NOT NULL
);

-- Teams Tabelle
CREATE TABLE teams (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  short_name TEXT NOT NULL,
  openliga_id INT NOT NULL UNIQUE
);

-- Players Tabelle
CREATE TABLE players (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  team_id UUID REFERENCES teams(id),
  position TEXT NOT NULL
);

-- Real Lineups Tabelle
CREATE TABLE real_lineups (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  matchday_id UUID REFERENCES matchdays(id),
  team_id UUID REFERENCES teams(id),
  player_id UUID REFERENCES players(id),
  confirmed_at TIMESTAMP DEFAULT now()
);

-- Predictions Tabelle
CREATE TABLE predictions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  matchday_id UUID REFERENCES matchdays(id),
  team_id UUID REFERENCES teams(id),
  player_id UUID REFERENCES players(id),
  created_at TIMESTAMP DEFAULT now()
);

-- Scores Tabelle
CREATE TABLE scores (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  matchday_id UUID REFERENCES matchdays(id),
  team_id UUID REFERENCES teams(id),
  points INT DEFAULT 0
);