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
INSERT OR IGNORE INTO sources (name) VALUES 
    ('Trader Joe''s'),
    ('Safeway'),
    ('Wegmans'),
    ('Whole Foods'),
    ('Costco'),
    ('Giant'),
    ('Harris Teeter');

-- Default types (with temperature requirements)
INSERT OR IGNORE INTO types (name, sort_order, requires_temp) VALUES 
    ('Produce', 1, 0),
    ('Bread', 2, 0),
    ('Dry', 3, 0),
    ('Dairy', 4, 1),      -- Requires temperature
    ('Meat', 5, 1),       -- Requires temperature
    ('Prepared', 6, 1),   -- Requires temperature
    ('Frozen', 7, 0),
    ('Other', 8, 0);
