CREATE TABLE users (
    userid       TEXT    PRIMARY KEY,
    first_name   TEXT    NOT NULL,
    last_name    TEXT,
    email        TEXT    NOT NULL
                         UNIQUE,
    date_created TEXT,
    PLEVEL       INTEGER DEFAULT (0) 
);
CREATE TABLE log_failed_logins (
    userid        TEXT REFERENCES users (userid),
    ip            TEXT,
    time          TEXT,
    error_message TEXT
);
CREATE TABLE log_logins (
    userid TEXT REFERENCES users (userid),
    ip     TEXT,
    time   TEXT
);
CREATE TABLE passwords (
    userid TEXT REFERENCES users (userid) 
                NOT NULL
                UNIQUE,
    hash   BLOB
);
CREATE TABLE quotes (
    name     TEXT,
    year     TEXT,
    quote    TEXT,
    likes    TEXT    DEFAULT "[]",
    numlikes INTEGER DEFAULT (0) 
);