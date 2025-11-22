DROP TABLE IF EXISTS sources;
DROP TABLE IF EXISTS types;
DROP TABLE IF EXISTS logs;

CREATE TABLE sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    sort_order INTEGER NOT NULL
);

CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    weight_lb REAL NOT NULL,
    source_id INTEGER NOT NULL,
    type_id INTEGER NOT NULL,
    deleted INTEGER NOT NULL DEFAULT 0,
    action TEXT NOT NULL DEFAULT 'record',
    FOREIGN KEY (source_id) REFERENCES sources(id),
    FOREIGN KEY (type_id) REFERENCES types(id)
);

INSERT OR IGNORE INTO sources (name) VALUES
    ('Food for Neighbors'),
    ('Trader Joe''s'),
    ('Whole Foods'),
    ('Wegmans'),
    ('Safeway'),
    ('Good Shepherd donations'),
    ('FreshFarm St John Neumann');

INSERT OR IGNORE INTO types (name, sort_order) VALUES
    ('Produce', 0),
    ('Dry', 1),
    ('Dairy', 2),
    ('Meat', 3),
    ('Prepared', 4),
    ('Bread', 5),
    ('Non-food', 6);
