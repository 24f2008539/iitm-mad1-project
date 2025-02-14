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

