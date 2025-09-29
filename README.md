# Personal Library Tracker

A Streamlit-powered dashboard and SQLite database for tracking my personal library.  
Think of it as the first draft of the floor-to-ceiling library I hope to build one day, but in SQL form.  

---

## Purpose

This project keeps track of the books I’ve read, their authors, genres, and ratings. It’s built as my final project for **CS50’s Introduction to Databases with SQL**.  

It is both academic and personal. On the academic side, it demonstrates a normalized relational schema, CRUD operations, indexing, and visualization. On the personal side, it is the database version of a lifelong love affair with books — one that began in public libraries my mom took me to as a kid, continued through countless late nights reading, and is now represented in this project.  

One day I’d like to build a home library like the one in Disney’s *Beauty and the Beast*. Since home ownership has been priced into absurdity by late-stage capitalism and BlackRock’s shopping spree, this will have to do for now.  

---

## Features

- **Relational Database** with four tables: `authors`, `genres`, `books`, and `ratings`.  
- **Streamlit Dashboard** with:  
  - Add, edit, and delete book entries (password-protected).  
  - Automatic fetching of book covers, ISBNs, and subjects from Open Library and Google Books.  
  - KPI cards summarizing total books, average ratings, most popular genre, and years covered.  
  - Interactive charts showing reading trends.  
  - Search and filters for genre and year.  
  - Export filtered data to CSV.  
- **Design Touches**: Gold-framed book covers, hover effects with ratings and genre, decorative corners, and a banner to set the mood.  

---

## Installation

### Requirements
- Python 3.9+  
- SQLite  
- Dependencies: `streamlit`, `pandas`, `plotly`, `requests`

### Setup
Clone this repository and install dependencies:

```bash
pip install -r requirements.txt
Run the App
From the project directory, run:

bash
Copy code
streamlit run app/main.py
Open the URL Streamlit provides (usually http://localhost:8501) in your browser.

Usage
Use the dashboard to browse your library, filter by genre or year, and view analytics.

To manage books (add, edit, delete), enter the password:

nginx
Copy code
JulietA
Add new books through the form. Covers and ISBNs will be fetched automatically if possible.

Hover over book covers to see rating and genre details.

Export your filtered library to CSV for safekeeping or analysis.

File Structure
schema.sql — Creates the database schema.

queries.sql — Example queries (insert, update, delete, select).

design.md — Technical write-up of the database design and scope.

main.py — Main Streamlit app logic and UI.

ui.py — Components for KPIs, book grid, and forms.

analytics.py — Visualization code (charts with Plotly).

db_utils.py — Utility functions for interacting with the database and APIs.

---

Acknowledgments
My mom: for endless trips to public libraries that made me fall in love with reading.

Harvard's CS50: for providing the structure to turn that love into code.

Open Library & Google Books: for the book covers and metadata.

Disney’s Beauty and the Beast: for setting unrealistic expectations for what a library can look like.

Final Note
This project is a personal library tracker, but more than that it is a placeholder for a dream. Someday I’d like to walk into a room filled with all the books I’ve read, walls lined with shelves, the air thick with memory and curiosity. Until then, it lives here in SQL tables and Streamlit code.

“A room without books is like a body without a soul.” — Cicero