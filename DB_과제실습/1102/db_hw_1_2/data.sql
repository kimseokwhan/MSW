-- Active: 1793587524769@@127.0.0.1@3306
SELECT *
FROM tracks;

SELECT Name, Milliseconds, UnitPrice
FROM tracks;

SELECT *
FROM tracks
WHERE GenreId = 1;

SELECT *
FROM tracks
ORDER BY name ASC;

SELECT *
FROM tracks
LIMIT 10;