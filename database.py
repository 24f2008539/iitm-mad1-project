from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'quizmaster_secret'

db_file = 'quiz.db'

# Initialize the database
def init_db():
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL,
                            full_name TEXT NOT NULL,
                            qualification TEXT NOT NULL,
                            dob TEXT NOT NULL)
                        ''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS subjects (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT UNIQUE NOT NULL)
                        ''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS chapters (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            subject_id INTEGER NOT NULL,
                            name TEXT NOT NULL,
                            FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE)
                        ''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS quiz (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            chapter_id INTEGER NOT NULL,
                            question TEXT NOT NULL,
                            option1 TEXT NOT NULL,
                            option2 TEXT NOT NULL,
                            option3 TEXT NOT NULL,
                            option4 TEXT NOT NULL,
                            answer TEXT NOT NULL,
                            FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE)
                        ''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            quiz_duration INTEGER NOT NULL)
                        ''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS scores (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL,
                            score INTEGER NOT NULL,
                            total INTEGER NOT NULL,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)
                        ''')
        conn.commit()

init_db()