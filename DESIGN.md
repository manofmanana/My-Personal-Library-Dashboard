## Purpose

This project is a personal library tracker, a system that manages books I have read, their authors, genres, and ratings.

On the academic side it is meant to demonstrate competency in relational modeling, normalization, and SQL. It uses CREATE TABLE, INSERT, UPDATE, DELETE, and SELECT queries in ways that reflect a properly structured database.

On the personal side it is much more sentimental. I grew up in public libraries, shepherded by my mother who understood that shelves of books were cheaper than babysitters and infinitely more generous. Those afternoons gave me memories worth more than any grade. They gave me a lifelong habit of reading.

This project is also a placeholder for something larger. Someday I want a home with a dedicated library room, one that doubles as an office and hobby space, filled entirely with books I have read. The model comes from Beauty and the Beast’s impossibly grand library. But in the real world, home ownership is throttled by investors who see houses as revenue streams instead of roofs, so the dream has to wait. For now, this project is the digital version of that future room. A library in code until it can be a library in wood.

Knowledge should not be gatekept. It should be free for those who have curiosity gnawing at them. This project is one attempt to honor that idea.

---

## Scope

This project tracks books and metadata about them. It provides:

Adding books with title, author, genre, year read, ISBN, subjects, and cover image

Editing existing entries, refreshing cover and subject data automatically if ISBN/title/author change

Deleting books and associated ratings

Recording and updating ratings (0.0–5.0)

Viewing library data in a Streamlit dashboard with KPIs and visual charts

Searching, filtering, and exporting the collection to CSV


Out of Scope

The project does not track lending or borrowing. It does not track progress or notes. It does not support multiple users. It is one database for one person.

---

## Entities and Attributes

The database schema contains four normalized tables.

Authors
CREATE TABLE authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);


Each author is stored once, avoiding duplicates like “J.K. Rowling” and “JK Rowling.”

Genres
CREATE TABLE genres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);


Each genre is stored once, ensuring consistency and enabling queries like “how many books in Psychology?”

Books
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author_id INTEGER,
    genre_id INTEGER,
    year INTEGER,
    isbn TEXT,
    subjects TEXT,
    cover_url TEXT,
    FOREIGN KEY (author_id) REFERENCES authors(id),
    FOREIGN KEY (genre_id) REFERENCES genres(id)
);


The books table is the core of the schema, holding metadata about each entry.

Ratings
CREATE TABLE ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    rating REAL NOT NULL,
    FOREIGN KEY (book_id) REFERENCES books(id)
);


Ratings are stored separately, making it possible to allow multiple ratings per book if the design expands later.

---

## Relationships

One author can write many books (1:N)

One genre can classify many books (1:N)

One book can have many ratings (1:N)

This structure eliminates redundancy.

---

## Entity Relationship Diagram
erDiagram
    AUTHORS ||--o{ BOOKS : writes
    GENRES  ||--o{ BOOKS : classifies
    BOOKS   ||--o{ RATINGS : has
    AUTHORS {
        int id PK
        text name
    }
    GENRES {
        int id PK
        text name
    }
    BOOKS {
        int id PK
        text title
        int author_id FK
        int genre_id FK
        int year
        text isbn
        text subjects
        text cover_url
    }
    RATINGS {
        int id PK
        int book_id FK
        real rating
    }

---

## Optimizations

Indexes:

CREATE INDEX idx_books_author_id ON books(author_id);
CREATE INDEX idx_books_genre_id ON books(genre_id);
CREATE INDEX idx_ratings_book_id ON ratings(book_id);


These indexes speed up joins and filtering by foreign keys.

Normalization:

Authors and genres are stored in separate tables

Ratings are separated so multiple can exist per book

Data enrichment:

Book covers, ISBNs, and subjects are fetched from APIs like Open Library and Google Books, reducing manual entry


---

## Limitations

Each book can only have one author and one genre

API cover data is sometimes wrong or missing, tiered system of fetching covers was implemented. ISBN 10 or 13 numbers work best for accurate covers or for placing specific covers since books have a lot of variant covers.

Authentication is minimal: the admin password is hardcoded, which would never survive real-world scrutiny

---

## Queries

The database supports a range of analytical queries that go beyond basic CRUD operations. Some examples:

Select all books with author and genre info
SELECT b.id, b.title, a.name AS author, g.name AS genre, b.year, b.isbn
FROM books b
LEFT JOIN authors a ON b.author_id = a.id
LEFT JOIN genres g ON b.genre_id = g.id;

Average rating per book
SELECT b.title, ROUND(AVG(r.rating), 2) AS avg_rating
FROM books b
JOIN ratings r ON b.id = r.book_id
GROUP BY b.id
ORDER BY avg_rating DESC;

Books with average rating above 4
SELECT b.title, a.name AS author, g.name AS genre, ROUND(AVG(r.rating),2) AS avg_rating
FROM books b
JOIN authors a ON b.author_id = a.id
JOIN genres g ON b.genre_id = g.id
JOIN ratings r ON b.id = r.book_id
GROUP BY b.id
HAVING avg_rating > 4;

Count books per genre
SELECT g.name AS genre, COUNT(*) AS num_books
FROM books b
JOIN genres g ON b.genre_id = g.id
GROUP BY g.id
ORDER BY num_books DESC;

Top-rated authors
SELECT a.name AS author, ROUND(AVG(r.rating), 2) AS avg_rating
FROM books b
JOIN authors a ON b.author_id = a.id
JOIN ratings r ON b.id = r.book_id
GROUP BY a.id
ORDER BY avg_rating DESC;

Most recent books read
SELECT b.title, a.name AS author, b.year
FROM books b
JOIN authors a ON b.author_id = a.id
ORDER BY b.year DESC
LIMIT 10;


These queries demonstrate practical use of joins, grouping, aggregation, filtering, and ordering. They turn the schema from a static design into something that generates insights.

---

## Conclusion

This project demonstrates a normalized relational schema, full CRUD support, query optimization through indexing, and API integration. It includes not just the schema and queries but also a working dashboard for visualization and interaction.

It meets the requirements for CS50 SQL’s final project: a substantial problem, a normalized schema, multiple related tables, complete queries, and a design document explaining it all.

It is also more than a course assignment. It is a fragment of a personal myth: a library waiting for a house to live in. For now it is digital, but it may someday become a room with real shelves.

Maya Angelou once wrote, “Any book that helps a child to form a habit of reading, to make reading one of his deep and continuing needs, is good for him.”