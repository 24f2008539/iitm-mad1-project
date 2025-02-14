@app.route('/user_console', methods=['GET', 'POST'])
def user_console():
    if 'user' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))
    
    username = session['user']
    
    return render_template('user.html', username=username)


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
