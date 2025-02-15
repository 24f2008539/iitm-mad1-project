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

@app.route('/admin/delete_subject/<int:subject_id>')
def delete_subject(subject_id):
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        conn.commit()
        flash('Subject deleted successfully!', 'danger')
    
    return redirect(url_for('manage_subjects'))

@app.route('/admin/delete_chapter/<int:chapter_id>')
def delete_chapter(chapter_id):
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT subject_id FROM chapters WHERE id = ?", (chapter_id,))
        subject_id = cursor.fetchone()
        if subject_id:
            subject_id = subject_id[0]  # Extract value from tuple
        cursor.execute("DELETE FROM chapters WHERE id = ?", (chapter_id,))
        conn.commit()
        flash('Chapter deleted successfully!', 'danger')
    
    return redirect(url_for('manage_chapters', subject_id=subject_id))

@app.route('/admin/delete_question/<int:question_id>')
def delete_question(question_id):
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM quiz WHERE id = ?", (question_id,))
        conn.commit()
        flash('Question deleted successfully!', 'danger')
    
    return redirect(url_for('manage_quiz', chapter_id=request.args.get('chapter_id')))

@app.route('/admin/subjects', methods=['GET', 'POST'])
def manage_subjects():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        if request.method == 'POST':
            subject_name = request.form['subject_name']
            cursor.execute("INSERT INTO subjects (name) VALUES (?)", (subject_name,))
            conn.commit()
            flash('Subject added successfully!', 'success')
        cursor.execute("SELECT * FROM subjects")
        subjects = cursor.fetchall()
    
    return render_template('manage_subjects.html', subjects=subjects)

@app.route('/admin/users')
def manage_users():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, full_name, qualification, dob FROM users")
        users = cursor.fetchall()
    
    return render_template('manage_users.html', users=users)

@app.route('/admin/delete_user/<int:user_id>')
def delete_user(user_id):
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        flash('User deleted successfully!', 'danger')
    
    return redirect(url_for('manage_users'))

@app.route('/admin/chapters/<int:subject_id>', methods=['GET', 'POST'])
def manage_chapters(subject_id):
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        if request.method == 'POST':
            chapter_name = request.form['chapter_name']
            cursor.execute("INSERT INTO chapters (subject_id, name) VALUES (?, ?)", (subject_id, chapter_name))
            conn.commit()
            flash('Chapter added successfully!', 'success')
        cursor.execute("SELECT * FROM chapters WHERE subject_id = ?", (subject_id,))
        chapters = cursor.fetchall()
    
    return render_template('manage_chapters.html', chapters=chapters, subject_id=subject_id)

@app.route('/admin/quiz/<int:chapter_id>', methods=['GET', 'POST'])
def manage_quiz(chapter_id):
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        if request.method == 'POST':
            question = request.form['question']
            option1 = request.form['option1']
            option2 = request.form['option2']
            option3 = request.form['option3']
            option4 = request.form['option4']
            answer = request.form['answer']
            cursor.execute("INSERT INTO quiz (chapter_id, question, option1, option2, option3, option4, answer) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (chapter_id, question, option1, option2, option3, option4, answer))
            conn.commit()
            flash('Quiz question added successfully!', 'success')
        cursor.execute("SELECT * FROM quiz WHERE chapter_id = ?", (chapter_id,))
        questions = cursor.fetchall()
    
    return render_template('manage_quiz.html', questions=questions, chapter_id=chapter_id)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'admin' and password == 'admin':
            session['user'] = 'admin'
            return redirect(url_for('admin'))
        
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            
        if user:
            session['user'] = username
            return redirect(url_for('user_console'))
        else:
            flash('Invalid credentials. Try again or register.', 'danger')
    
    return render_template('login.html')

@app.route('/user_console', methods=['GET', 'POST'])
def user_console():
    if 'user' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))
    
    username = session['user']
    
    return render_template('user.html', username=username)

def get_quiz_performance():
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, AVG(score) FROM scores GROUP BY username")
        data = cursor.fetchall()

        user_names = [row[0] for row in data]
        user_scores = [row[1] for row in data]
    
    return user_names, user_scores

@app.route('/admin/analytics')
def quiz_analytics():
    user_names, user_scores = get_quiz_performance()
    return render_template('analytics.html', user_names=user_names, user_scores=user_scores)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        qualification = request.form['qualification']
        dob = request.form['dob']
        
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password, full_name, qualification, dob) VALUES (?, ?, ?, ?, ?)",
                               (username, password, full_name, qualification, dob))
                conn.commit()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('Username already exists!', 'danger')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quiz")
        questions = cursor.fetchall()
        cursor.execute("SELECT quiz_duration FROM settings ORDER BY id DESC LIMIT 1")
        duration = cursor.fetchone()
        duration = duration[0] if duration else 60
    
    if request.method == 'POST':
        new_duration = int(request.form['quiz_duration'])
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM settings")
            cursor.execute("INSERT INTO settings (quiz_duration) VALUES (?)", (new_duration,))
            conn.commit()
            flash('Quiz duration updated!', 'success')
        return redirect(url_for('admin'))
    
    return render_template('admin.html', questions=questions, duration=duration)

@app.route('/admin')
def admin_panel():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    return render_template('admin.html')

@app.route('/add', methods=['GET', 'POST'])
def add_question():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        question = request.form['question']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        answer = request.form['answer']

        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO quiz (question, option1, option2, option3, option4, answer) VALUES (?, ?, ?, ?, ?, ?)",
                           (question, option1, option2, option3, option4, answer))
            conn.commit()
            flash('Question added successfully!', 'success')

        return redirect(url_for('admin'))
    
    return render_template('add.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'chapter' not in session:
        return redirect(url_for('select_subject'))

    conn = get_db_connection()

    # Get subject ID
    sub_id = conn.execute('SELECT id FROM subjects WHERE name = ?', (session['subject'],)).fetchone()
    if not sub_id:
        return redirect(url_for('select_subject'))  # Handle invalid subjects
    sub_id = sub_id['id']

    # Get quiz duration
    duration_row = conn.execute("SELECT quiz_duration FROM settings ORDER BY id DESC LIMIT 1").fetchone()
    duration = duration_row['quiz_duration'] if duration_row else 60

    # Get chapter IDs
    chap_ids = conn.execute('SELECT id FROM chapters WHERE subject_id = ?', (sub_id,)).fetchall()
    chap_ids = [row['id'] for row in chap_ids]

    # Fetch all questions for the chapters
    questions = []
    for chap_id in chap_ids:
        questions.extend(conn.execute('SELECT * FROM quiz WHERE chapter_id = ?', (chap_id,)).fetchall())

    if request.method == 'POST':
        # Process quiz submission
        # print(request.form)
        total_questions = len(questions)
        score = 0

        
        form_data = request.form.to_dict()
        # print(form_data)


        for question in questions:
            q_id = str(question['id'])
            correct_answer = question[f"option{question['answer']}"]  # Assuming 'correct_option' stores the right answer
            user_answer = form_data[q_id]  # Get user answer from form

            print(f'user {user_answer} correct {correct_answer}')

            if user_answer == correct_answer:
                score += 1
        # Insert score into scores table
        conn.execute('''INSERT INTO scores (username, score, total) VALUES (?, ?, ?)''', 
                     (session['user'], score, total_questions))
        conn.commit()
        conn.close()

        return redirect(url_for('view_scores', score=score, total=total_questions))

    conn.close()
    return render_template('quiz.html', questions=questions, duration=duration)

def get_db_connection():
    conn = sqlite3.connect('quiz.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/select_subject', methods=['GET', 'POST'])
def select_subject():
    conn = get_db_connection()
    subjects = conn.execute('SELECT DISTINCT name FROM subjects').fetchall()
    conn.close()
    if request.method == 'POST':
        session['subject'] = request.form['subject']
        return redirect(url_for('select_chapter'))
    return render_template('select_subject.html', subjects=subjects)

@app.route('/select_chapter', methods=['GET', 'POST'])
def select_chapter():
    if 'subject' not in session:
        return redirect(url_for('select_subject'))
    conn = get_db_connection()
    sub_id=conn.execute('SELECT id FROM subjects WHERE name = ?', (session['subject'],)).fetchone()
    row_dict = dict(sub_id)
    sub_idd=row_dict['id']
    chapters = conn.execute('SELECT name FROM chapters WHERE subject_id = ?', (sub_idd,)).fetchall()
    conn.close()
    if request.method == 'POST':
        session['chapter'] = request.form['chapter']
        return redirect(url_for('quiz'))
    return render_template('select_chapter.html', chapters=chapters)

@app.route('/scores')
def view_scores():
    if 'score' in session:
        score = request.args.get('score', type=int)
        total = request.args.get('total', type=int)
        return render_template('quiz_results.html', score=score, total=total)
    
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT score, total, timestamp FROM scores WHERE username = ? ORDER BY timestamp DESC", (session['user'],))
        scores = cursor.fetchall()
    
    return render_template('scores.html', scores=scores)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
