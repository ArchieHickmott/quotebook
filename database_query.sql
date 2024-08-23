CREATE TABLE `users` (
`id` int PRIMARY KEY,
`name` TEXT NOT NULL,
`email` TEXT UNIQUE NOT NULL,
`password_hash` TEXT NOT NULL,
`created_at` int NOT NULL,
`plevel` int NOT NULL
);

CREATE TABLE `quotes` (
`id` int PRIMARY,
`author` TEXT DEFAULT 'Unknown',
`year` TEXT NOT NULL,
`quote` TEXT NOT NULL,
`likes` int DEFAULT 0
);

CREATE TABLE `reports` (
`id` int PRIMARY KEY,
`user_id` int,
`quote_id` int,
`reason` TEXT NOT NULL,
`details` TEXT,
`status` int
);

CREATE TABLE `logs` (
`id` int PRIMARY KEY,
`user_id` int,
`action` TEXT,
`message` TEXT
);

CREATE TABLE `likes` (
`user_id` int,
`quote_id` int
);

ALTER TABLE `reports` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
ALTER TABLE `reports` ADD FOREIGN KEY (`quote_id`) REFERENCES `quotes` (`id`);
ALTER TABLE `logs` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
ALTER TABLE `likes` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
ALTER TABLE `likes` ADD FOREIGN KEY (`quote_id`) REFERENCES `quotes` (`id`);
