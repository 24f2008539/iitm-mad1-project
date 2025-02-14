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