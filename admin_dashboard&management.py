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
        cursor.execute("DELETE FROM chapters WHERE id = ?", (chapter_id,))
        conn.commit()
        flash('Chapter deleted successfully!', 'danger')
    
    return redirect(url_for('manage_chapters', subject_id=request.args.get('subject_id')))

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
