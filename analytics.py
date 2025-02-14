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
