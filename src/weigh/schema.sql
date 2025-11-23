-- schema.sql

CREATE TABLE IF NOT EXISTS sources (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS types (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT UNIQUE NOT NULL,
    sort_order INTEGER DEFAULT 999,
    requires_temp INTEGER DEFAULT 0  -- NEW: 1 if this type requires temperature logging
);

CREATE TABLE IF NOT EXISTS logs (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp  TEXT NOT NULL,
    weight_lb  REAL NOT NULL,
    source_id  INTEGER NOT NULL,
    type_id    INTEGER NOT NULL,
    deleted    INTEGER DEFAULT 0,
    temp_pickup_f REAL,     -- NEW: Temperature at pickup in Fahrenheit
    temp_dropoff_f  REAL,   -- NEW: Temperature at dropoff in Fahrenheit
    FOREIGN KEY (source_id) REFERENCES sources(id),
    FOREIGN KEY (type_id)   REFERENCES types(id)
);

-- Default sources
INSERT OR IGNORE INTO sources (name) VALUES ('Food for Neighbors');
INSERT OR IGNORE INTO sources (name) VALUES ('Trader Joe''s');
INSERT OR IGNORE INTO sources (name) VALUES ('Whole Foods');
INSERT OR IGNORE INTO sources (name) VALUES ('Wegmans');
INSERT OR IGNORE INTO sources (name) VALUES ('Safeway');
INSERT OR IGNORE INTO sources (name) VALUES ('Good Shepherd donations');
INSERT OR IGNORE INTO sources (name) VALUES ('FreshFarm St John Neumann');

INSERT OR IGNORE INTO types (name, sort_order) VALUES ('Produce', 0);
INSERT OR IGNORE INTO types (name, sort_order) VALUES ('Dry', 1);
INSERT OR IGNORE INTO types (name, sort_order) VALUES ('Dairy', 2);
INSERT OR IGNORE INTO types (name, sort_order) VALUES ('Meat', 3);
INSERT OR IGNORE INTO types (name, sort_order) VALUES ('Prepared', 4);
INSERT OR IGNORE INTO types (name, sort_order) VALUES ('Bread', 5);
INSERT OR IGNORE INTO types (name, sort_order) VALUES ('Non-food', 6);
UPDATE types SET requires_temp=1 WHERE name IN ('Dairy', 'Meat', 'Prepared');
