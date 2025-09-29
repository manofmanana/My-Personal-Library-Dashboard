-- =====================
-- QUERIES.SQL
-- Common SQL statements for the Library Database
-- =====================

-- === INSERTS ===

-- Insert a new author
INSERT INTO authors (name) VALUES ('Haruki Murakami');

-- Insert a new genre
INSERT INTO genres (name) VALUES ('Psychology');

-- Insert a new book (example: The Body Keeps the Score)
INSERT INTO books (title, author_id, genre_id, year, isbn, subjects, cover_url)
VALUES (
    'The Body Keeps the Score',
    1,  -- assumes author_id = 1
    1,  -- assumes genre_id = 1
    2014,
    '9780143127741',
    'Trauma, Psychology, Healing',
    'https://covers.openlibrary.org/b/id/123456-L.jpg'
);

-- Insert a rating for a book
INSERT INTO ratings (book_id, rating) VALUES (1, 4.5);


-- === UPDATES ===

-- Update a book's title
UPDATE books SET title = 'The Body Keeps the Score: Brain, Mind, and Body in the Healing of Trauma'
WHERE id = 1;

-- Update an author’s name
UPDATE authors SET name = 'Bessel A. van der Kolk'
WHERE id = 1;

-- Update a book's year
UPDATE books SET year = 2015 WHERE id = 1;

-- Replace a rating for a book
UPDATE ratings SET rating = 5.0 WHERE book_id = 1;


-- === DELETES ===

-- Delete all ratings for a book (before deleting the book itself)
DELETE FROM ratings WHERE book_id = 1;

-- Delete a book
DELETE FROM books WHERE id = 1;

-- Delete an author (will fail if books still reference it)
DELETE FROM authors WHERE id = 1;

-- Delete a genre (will fail if books still reference it)
DELETE FROM genres WHERE id = 1;


-- === SELECTS (Analytical) ===

-- Select all books with author and genre info
SELECT b.id, b.title, a.name AS author, g.name AS genre, b.year, b.isbn
FROM books b
LEFT JOIN authors a ON b.author_id = a.id
LEFT JOIN genres g ON b.genre_id = g.id;

-- Get average rating per book
SELECT b.title, ROUND(AVG(r.rating), 2) AS avg_rating
FROM books b
JOIN ratings r ON b.id = r.book_id
GROUP BY b.id
ORDER BY avg_rating DESC;

-- Get all books with average rating above 4
SELECT b.title, a.name AS author, g.name AS genre, ROUND(AVG(r.rating),2) AS avg_rating
FROM books b
JOIN authors a ON b.author_id = a.id
JOIN genres g ON b.genre_id = g.id
JOIN ratings r ON b.id = r.book_id
GROUP BY b.id
HAVING avg_rating > 4;

-- Count books per genre
SELECT g.name AS genre, COUNT(*) AS num_books
FROM books b
JOIN genres g ON b.genre_id = g.id
GROUP BY g.id
ORDER BY num_books DESC;

-- Find the most recent books read
SELECT b.title, a.name AS author, b.year
FROM books b
JOIN authors a ON b.author_id = a.id
ORDER BY b.year DESC
LIMIT 10;

-- Find top-rated authors (average rating across their books)
SELECT a.name AS author, ROUND(AVG(r.rating), 2) AS avg_rating
FROM books b
JOIN authors a ON b.author_id = a.id
JOIN ratings r ON b.id = r.book_id
GROUP BY a.id
ORDER BY avg_rating DESC;

-- Find books without a cover image
SELECT id, title FROM books WHERE cover_url IS NULL OR cover_url = '';
