# Alejandro's Library

## Overview
Alejandro's Library is a personal digital library and dashboard. It allows books to be added, edited, rated, visualized, and filtered. Built with **SQLite, Python, Streamlit, and Plotly**, the app feels like having your own public library on the web. 

When I was a young child, my mom would take me often to public libraries around town. She nurtured my love of reading at a young age. I will forever be grateful for that, so this is an ode to her. Thanks madre. 

The project began as a CS50 SQL final project and grew into a full interactive application. It serves both as a demonstration of relational database design and as a personal portfolio project.

---

## Features
- Add books with title, author, genre, year read, ISBN, subjects, and cover image
- Edit existing entries with automatic cover and subject lookups
- Delete books and associated ratings
- Track ratings on a 0.0–5.0 scale
- Visualize data in a Streamlit dashboard with diverse chart types
- Filter and search books by title, author, genre, or year
- Export filtered collections to CSV

---

## Tech Stack
- **Backend**: SQLite, SQL queries
- **Frontend**: Streamlit with custom CSS
- **Visualization**: Plotly Express charts
- **Data Enrichment**: Open Library API
- **Languages**: Python, SQL, HTML/CSS

---

## Installation
Clone or download the repository, then install dependencies:

```bash
pip install -r requirements.txt
Run the app:

bash
Copy code
streamlit run main.py
File Structure
main.py: Streamlit entry point, navigation, and layout

app/ui.py: Custom CSS and UI components

app/db_utils.py: Database utilities for CRUD operations

app/analytics.py: Data visualization functions

schema.sql: SQL schema defining tables

queries.sql: Common SQL queries

DESIGN.md: Design document

README.md: This file

Example Queries
Average rating per book

Count of books per genre

Top-rated authors

Most recent books read

See queries.sql for examples.

Purpose
This project is both a course assignment and a personal archive. It is inspired by afternoons in public libraries and the dream of one day having a personal library room. Until then, this project serves as a library in code.

License
This project is for educational purposes under the CS50 SQL final project requirements.