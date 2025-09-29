-- =====================================
-- SEED.SQL (Optional)
-- =====================================
-- This file is provided as an example to quickly populate the database
-- with a few books for testing or demonstration purposes.
-- ⚠️ Running this will DELETE all existing data in the database.
-- Only use if you want to reset the library to this starter set.

-- Reset existing data
DELETE FROM ratings;
DELETE FROM books;
DELETE FROM authors;
DELETE FROM genres;

-- =====================================
-- Authors
-- =====================================
INSERT INTO authors (name) VALUES
('Haruki Murakami'),
('Bessel van der Kolk'),
('John Steinbeck');

-- =====================================
-- Genres
-- =====================================
INSERT INTO genres (name) VALUES
('Fiction'),
('Psychology'),
('Classic');

-- =====================================
-- Books & Ratings
-- =====================================
INSERT INTO books (title, author_id, genre_id, year)
SELECT 'Kafka on the Shore', a.id, g.id, 2020
FROM authors a, genres g
WHERE a.name='Haruki Murakami' AND g.name='Fiction';
INSERT INTO ratings (book_id, rating) VALUES ((SELECT id FROM books WHERE title='Kafka on the Shore'), 4.5);

INSERT INTO books (title, author_id, genre_id, year)
SELECT 'The Body Keeps the Score', a.id, g.id, 2021
FROM authors a, genres g
WHERE a.name='Bessel van der Kolk' AND g.name='Psychology';
INSERT INTO ratings (book_id, rating) VALUES ((SELECT id FROM books WHERE title='The Body Keeps the Score'), 4.7);

INSERT INTO books (title, author_id, genre_id, year)
SELECT 'East of Eden', a.id, g.id, 2019
FROM authors a, genres g
WHERE a.name='John Steinbeck' AND g.name='Classic';
INSERT INTO ratings (book_id, rating) VALUES ((SELECT id FROM books WHERE title='East of Eden'), 4.8);
