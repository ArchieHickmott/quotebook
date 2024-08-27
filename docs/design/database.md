# Database Structure

## Requirements
The new database structuer needs the following capabiitys:
1. To store quotes with id, author, year, quote, and number of likes.
2. To store users with id, name, email, created_at, password, and permission level.
3. To store quote reports with user_id, quote_id, reason, details, and status
4. To log actions made by users, including failed logins, logins, and reports.
5. To store likes with user_id and quote_id.

## DB Diagram
![DB Diagram](./assets/dbdiagram.png)

## New database sql
```sql
CREATE TABLE users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL,
email TEXT UNIQUE NOT NULL,
password_hash TEXT NOT NULL,
created_at INTEGER NOT NULL,
style TEXT DEFAULT 'light',
plevel INTEGER NOT NULL
);

CREATE TABLE `quotes` (
`id` INTEGER PRIMARY KEY AUTOINCREMENT,
`author` TEXT DEFAULT 'Unknown',
`year` TEXT NOT NULL,
`quote` TEXT NOT NULL,
`likes` INTEGER DEFAULT 0
);

CREATE TABLE `reports` (
`id` INTEGER PRIMARY KEY AUTOINCREMENT,
`user_id` INTEGER REFERENCES users (id),
`quote_id` INTEGER REFERENCES quotes (id),
`reason` TEXT NOT NULL,
`details` TEXT,
`status` INTEGER
);

CREATE TABLE `logs` (
`id` INTEGER PRIMARY KEY AUTOINCREMENT,
`user_id` INTEGER REFERENCES users (id),
`action` TEXT,
`message` TEXT,
`time` TEXT,
`ip` TEXT,
`agent` TEXT
);

CREATE TABLE `likes` (
`user_id` INTEGER REFERENCES users (id),
`quote_id` INTEGER REFERENCES quotes (id)
);

CREATE TABLE `comments` (
`user_id` INTEGE REFERENCES users(id),
`quote_id` INTEGER REFERENCES quotes (id),
`comment` TEXT
);
```