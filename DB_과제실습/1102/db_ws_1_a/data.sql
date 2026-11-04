-- Active: 1793594706003@@127.0.0.1@3306
CREATE TABLE songs(
  id INTEGER PRIMARY KEY,
  title TEXT,
  artist TEXT,
  album TEXT,
  genre TEXT,
  duration INTEGER
);

INSERT INTO songs (title, duration) VALUES ('Song 1', 200);

UPDATE songs SET title = 'New Title' WHERE id = 1;

INSERT INTO songs (title, artist, album, genre, duration) VALUES ('Song 2', 'Artist 2', 'Album 2', 'Rock', 300);
INSERT INTO songs (title, artist, album, genre, duration) VALUES ('Song 3', 'Artist 3', 'Album 3', 'Hip Hop', 250);
INSERT INTO songs (title, artist, album, genre, duration) VALUES ('Song 4', 'Artist 4', 'Album 4', 'Electronic', 180);
INSERT INTO songs (title, artist, album, genre, duration) VALUES ('Song 5', 'Artist 5', 'Album 5', 'R&B', 320);

UPDATE songs SET artist = 'Artist 1' WHERE id = 1;
UPDATE songs SET album = 'Album 1' WHERE id = 1;
UPDATE songs SET genre = 'Pop' WHERE id = 1;

SELECT *
FROM songs