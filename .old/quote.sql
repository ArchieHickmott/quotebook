CREATE TABLE users (
    userid       INTEGER PRIMARY KEY,
    first_name   TEXT    NOT NULL,
    last_name    TEXT,
    email        TEXT    NOT NULL
                         UNIQUE,
    date_created TEXT,
    PLEVEL       INTEGER DEFAULT (0) 
);
CREATE TABLE reports (
    reportid INTEGER        PRIMARY KEY,
    reporter                REFERENCES users (userid),
    quoteid  INTEGER        REFERENCES quotes (quoteid),
    reason   TEXT,
    details  TEXT,
    status   INTEGER (0, 2) DEFAULT (0) 
);
CREATE TABLE log_failed_logins (
    userid        INTEGER REFERENCES users (userid),
    ip            TEXT,
    time          TEXT,
    error_message TEXT
);
CREATE TABLE log_logins (
    userid INTEGER REFERENCES users (userid),
    ip     TEXT,
    time   TEXT
);
CREATE TABLE passwords (
    userid INTEGER REFERENCES users (userid) 
                   NOT NULL
                   UNIQUE,
    hash   BLOB
);
CREATE TABLE likes (
    quoteid INTEGER REFERENCES quotes (quoteid),
    userid  INTEGER REFERENCES users (userid) 
);
CREATE TABLE quotes (
    quoteid  INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT,
    year     TEXT,
    quote    TEXT,
    numlikes INTEGER DEFAULT (0) 
);
INSERT INTO quotes VALUES (1, "name", "2024", "example quote 1", 0);
INSERT INTO quotes VALUES (2, "name", "2024", "example quote 2", 0);
INSERT INTO quotes VALUES (3, "name", "2024", "example quote 3", 0);
INSERT INTO quotes VALUES (4, "name", "2024", "example quote 4", 0);
INSERT INTO quotes VALUES (5, "name", "2024", "example quote 5", 0);
INSERT INTO quotes VALUES (6, "name", "2024", "example quote 6", 0);
INSERT INTO quotes VALUES (7, "name", "2024", "example quote 7", 0);
INSERT INTO quotes VALUES (8, "name", "2024", "example quote 8", 0);
INSERT INTO quotes VALUES (9, "name", "2024", "example quote 9", 0);