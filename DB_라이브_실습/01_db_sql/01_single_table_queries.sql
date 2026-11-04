-- Active: 1793582545459@@127.0.0.1@3306
-- 01. Querying data
SELECT
  LastName
FROM
  employees;
  

SELECT
  LastName, FirstName
FROM
  employees;


SELECT
  *
FROM
  employees;


SELECT
  FirstName AS '이름', LastName AS '성'
FROM
  employees;


SELECT
  Name,
  Milliseconds / 60000 AS '재생 시간(분)'
FROM
  tracks;



-- 02. Sorting data
SELECT
  FirstName
FROM
  employees
ORDER BY
  FirstName;


SELECT
  FirstName
FROM
  employees
ORDER BY
  FirstName DESC;


SELECT
  Country, City
FROM
  customers
ORDER BY
  Country DESC,
  City;



SELECT
  Name,
  Milliseconds / 60000 AS '재생 시간(분)'
FROM
  tracks
ORDER BY
  Milliseconds DESC;


SELECT
  ReportsTo
FROM
  employees
ORDER BY
  ReportsTo;


-- 03. Filtering data
SELECT DISTINCT
  Country
FROM
  customers
ORDER BY
  Country;


SELECT
  LastName,
  FirstName,
  City
FROM
  customers
WHERE
  -- City = 'Prague';
  City != 'Prague';


SELECT
  *
FROM
  customers
WHERE
  Company IS NULL
  AND Country = 'USA';


SELECT
  Company, Country
FROM
  customers
WHERE
  Company IS NULL
  OR Country = 'USA';


SELECT
  Name, Bytes
FROM
  tracks
WHERE
  Bytes BETWEEN 100000 AND 500000;
  -- Bytes >= 100000 AND Bytes < 500000;


SELECT
  Name, Bytes
FROM
  tracks
WHERE
  Bytes BETWEEN 100000 AND 500000
ORDER BY
  Bytes;


SELECT
  Company, Country
FROM
  customers
WHERE
  -- Country = 'USA'  OR Country = 'Canada';
  Country IN ('Canada', 'Germany', 'France');
  -- Country NOT IN ('Canada', 'Germany', 'France');


SELECT
  LastName, FirstName
FROM
  customers
WHERE
  Lastname LIKE '_____son';
  -- LastName LIKE '%son';
  -- LastName LIKE 'Peter%';


SELECT
  *
FROM
  tracks
ORDER BY
  Bytes DESC
LIMIT 7 OFFSET 4;


SELECT
  Country, COUNT(*)
FROM
  customers
GROUP BY
  Country;


SELECT
  Composer,
  AVG(Milliseconds / 60000) AS avgOfminute
FROM
  tracks
GROUP BY
  Composer
HAVING
  AVG(Milliseconds / 60000) < 10;