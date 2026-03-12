from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for session management

# Dummy student credentials
STUDENT_CREDENTIALS = {
    "username": "student1",
    "password": "password123",
    "name": "Juan Dela Cruz",
    "grade": 10,
    "section": "Zechariah"
}

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == STUDENT_CREDENTIALS['username'] and password == STUDENT_CREDENTIALS['password']:
            session['logged_in'] = True
            session['student_name'] = STUDENT_CREDENTIALS['name']
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials. Try again.", "danger")
    return render_template('login.html')

# Dashboard route (protected)
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        flash("You need to login first!", "warning")
        return redirect(url_for('login'))
    student = {
        "name": STUDENT_CREDENTIALS['name'],
        "grade": STUDENT_CREDENTIALS['grade'],
        "section": STUDENT_CREDENTIALS['section']
    }
    return render_template('dashboard.html', student=student)

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for('home'))

# API endpoint
@app.route('/student')
def get_student():
    return jsonify({
        "name": STUDENT_CREDENTIALS['name'],
        "grade": STUDENT_CREDENTIALS['grade'],
        "section": STUDENT_CREDENTIALS['section']
    })

if __name__ == "__main__":
    app.run(debug=True)
