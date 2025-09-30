# Design Document

## Purpose

This project is a personal library tracker, a system that manages books I have read, their authors, genres, and ratings. It is designed both as a technical artifact to demonstrate database design and as a personal archive that reflects my lifelong connection to books.

On the academic side, it demonstrates competency in relational modeling, normalization, and SQL. It uses `CREATE TABLE`, `INSERT`, `UPDATE`, `DELETE`, and `SELECT` queries in ways that reflect a properly structured database. The project implements foreign keys, indexes, and entity relationships to enforce consistency and support analytical queries.

On the personal side, it recreates the feeling of having a public library of my own. I grew up in public libraries, shepherded by my mother who understood that shelves of books were cheaper than babysitters and infinitely more generous. This project is the digital version of the library room I hope to build one day — a space where reading is tracked, celebrated, and visualized.

Knowledge should not be gatekept. It should be free for anyone with curiosity. This library is one attempt to honor that idea. Also reading is just cool and fun. Thank you mom for taking me to libraries as a kid. 

---

## Scope

This project tracks books and metadata about them. It provides:

- Adding books with title, author, genre, year read, ISBN, subjects, and cover image
- Editing existing entries, refreshing cover and subject data automatically if ISBN/title/author change
- Deleting books and associated ratings
- Recording and updating ratings (0.0–5.0)
- Viewing library data in a Streamlit dashboard with KPIs and diverse charts (bar, sunburst, violin, lollipop, line)
- Searching, filtering, and exporting the collection to CSV

### Out of Scope
- Tracking lending or borrowing - not supposed to be a public library fully, it's more like owning your own library. 
- Tracking reading progress or notes
- Supporting multiple users
- Acting as a publishing platform

---

## Entities and Attributes

The database schema contains four normalized tables.

Authors
```sql
CREATE TABLE authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);
Genres
sql
Copy code
CREATE TABLE genres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);
Books
sql
Copy code
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
Ratings
sql
Copy code
CREATE TABLE ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    rating REAL NOT NULL,
    FOREIGN KEY (book_id) REFERENCES books(id)
);

---

## Relationships
One author can write many books (1:N)

One genre can classify many books (1:N)

One book can have many ratings (1:N)

This eliminates redundancy and supports normalized queries.

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

sql
Copy code
CREATE INDEX idx_books_author_id ON books(author_id);
CREATE INDEX idx_books_genre_id ON books(genre_id);
CREATE INDEX idx_ratings_book_id ON ratings(book_id);
Separate tables for authors and genres prevent duplicates

Ratings stored separately, allowing future support for multiple ratings per book

Book covers and subjects are enriched via APIs like Open Library

---

## Limitations
Each book currently supports only one author and one genre

API cover data is sometimes wrong or missing

Admin password is minimal and hardcoded (not secure)

Not multi-user

---

## Queries
Examples of supported queries:

sql
Copy code
-- Select all books with author and genre
SELECT b.id, b.title, a.name AS author, g.name AS genre, b.year, b.isbn
FROM books b
LEFT JOIN authors a ON b.author_id = a.id
LEFT JOIN genres g ON b.genre_id = g.id;

-- Average rating per book
SELECT b.title, ROUND(AVG(r.rating), 2) AS avg_rating
FROM books b
JOIN ratings r ON b.id = r.book_id
GROUP BY b.id
ORDER BY avg_rating DESC;
Additional queries include top authors, books above a rating threshold, and counts per genre.

---

## Conclusion
This project demonstrates a normalized relational schema, full CRUD support, indexing, API enrichment, and a working visualization dashboard. It meets CS50 SQL’s requirements for a final project and serves as a personal showcase of both technical skill and creative design.

Maya Angelou once wrote: “Any book that helps a child to form a habit of reading, to make reading one of his deep and continuing needs, is good for him.” This project is a step toward building that lifelong habit into code.