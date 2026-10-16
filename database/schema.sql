CREATE DATABASE IF NOT EXISTS music_recommender
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;

USE music_recommender;

SELECT DATABASE();

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ratings (
    user_id INT NOT NULL,
    track_id VARCHAR(22)
        CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    rating TINYINT NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id, track_id),

    CONSTRAINT fk_ratings_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_rating_range
        CHECK (rating BETWEEN 1 AND 5)
);