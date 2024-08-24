-- Drop the tables that exist in the database
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS quotes;
DROP TABLE IF EXISTS reports;
DROP TABLE IF EXISTS logs;
DROP TABLE IF EXISTS likes;
DROP TABLE IF EXISTS comments;


-- Create the tables in the database
CREATE TABLE `users` (
`id` INTEGER PRIMARY KEY AUTOINCREMENT,
`name` TEXT NOT NULL,
`email` TEXT UNIQUE NOT NULL,
`password_hash` TEXT NOT NULL,
`created_at` INTEGER NOT NULL,
`plevel` INTEGER NOT NULL
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
`user_id` INTEGER,
`quote_id` INTEGER,
`reason` TEXT NOT NULL,
`details` TEXT,
`status` INTEGER
);

CREATE TABLE `logs` (
`id` INTEGER PRIMARY KEY AUTOINCREMENT,
`user_id` INTEGER,
`action` TEXT,
`message` TEXT
);

CREATE TABLE `likes` (
`user_id` INTEGER,
`quote_id` INTEGER
);

CREATE TABLE `comments` (
`user_id` INTEGER,
`quote_id` INTEGER,
`comment` TEXT
);
/*
ALTER TABLE `reports` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
ALTER TABLE `reports` ADD FOREIGN KEY (`quote_id`) REFERENCES `quotes` (`id`);
ALTER TABLE `logs` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
ALTER TABLE `likes` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
ALTER TABLE `likes` ADD FOREIGN KEY (`quote_id`) REFERENCES `quotes` (`id`);
ALTER TABLE `comments` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
ALTER TABLE `comments` ADD FOREIGN KEY (`quote_id`) REFERENCES `quotes` (`id`);