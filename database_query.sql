-- Drop the tables that exist in the database
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS quotes;
DROP TABLE IF EXISTS reports;
DROP TABLE IF EXISTS logs;
DROP TABLE IF EXISTS likes;
DROP TABLE IF EXISTS comments;


-- Create the tables in the database
CREATE TABLE `users` (
`id` int UNIQUE PRIMARY KEY NOT NULL DEFAULT (last_insert_rowid() + 1),
`name` TEXT NOT NULL,
`email` TEXT UNIQUE NOT NULL,
`password_hash` TEXT NOT NULL,
`created_at` int NOT NULL,
`plevel` int NOT NULL
);

CREATE TABLE `quotes` (
`id` int UNIQUE PRIMARY KEY NOT NULL DEFAULT (last_insert_rowid() + 1),
`author` TEXT DEFAULT 'Unknown',
`year` TEXT NOT NULL,
`quote` TEXT NOT NULL,
`likes` int DEFAULT 0
);

CREATE TABLE `reports` (
`id` int UNIQUE PRIMARY KEY NOT NULL DEFAULT (last_insert_rowid() + 1),
`user_id` int,
`quote_id` int,
`reason` TEXT NOT NULL,
`details` TEXT,
`status` int
);

CREATE TABLE `logs` (
`id` int UNIQUE PRIMARY KEY NOT NULL DEFAULT (last_insert_rowid() + 1),
`user_id` int,
`action` TEXT,
`message` TEXT
);

CREATE TABLE `likes` (
`user_id` int,
`quote_id` int
);

CREATE TABLE `comments` (
`user_id` int,
`quote_id` int,
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