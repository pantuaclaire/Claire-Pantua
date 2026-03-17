from flask import Flask, request, redirect, url_for, render_template_string, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
 app = Flask(__name__)
 app.secret_key = 'supersecretkey'  # Required for session and flash messages
# Configure SQLite database
 app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
 app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
 db = SQLAlchemy(app)
# --- LOGIN MANAGER ---
 login_manager = LoginManager()
 login_manager.init_app(app)
 login_manager.login_view = 'login'  # Redirect unauthorized users to login page
# --- DATABASE MODELS ---
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    year_level = db.Column(db.String(50), nullable=False)
    contact_number = db.Column(db.String(50), nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)  # Store hashed password in production!

# Initialize the database
with app.app_context():
    db.create_all()
    # Create a default user if none exist
    if not User.query.first():
        default_user = User(username='admin', password='password')
        db.session.add(default_user)
        db.session.commit()

# --- USER LOADER ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- HTML TEMPLATES ---
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container mt-5" style="max-width: 400px;">
    <div class="card shadow-sm">
        <div class="card-header bg-primary text-white"><strong>Login</strong></div>
        <div class="card-body">
            {% with messages = get_flashed_messages() %}
            {% if messages %}
                <div class="alert alert-danger">{{ messages[0] }}</div>
            {% endif %}
            {% endwith %}
            <form action="{{ url_for('login') }}" method="POST">
                <div class="mb-3">
                    <input type="text" name="username" class="form-control" placeholder="Username" required>
                </div>
                <div class="mb-3">
                    <input type="password" name="password" class="form-control" placeholder="Password" required>
                </div>
                <button type="submit" class="btn btn-primary w-100">Login</button>
            </form>
        </div>
    </div>
</div>
</body>
</html>
"""

# Add a logout button on the main page
INDEX_TEMPLATE_WITH_LOGIN = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Student Information System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container mt-3">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2>Student Information System</h2>
        <div>
            Logged in as <strong>{{ current_user.username }}</strong>
            <a href="{{ url_for('logout') }}" class="btn btn-sm btn-danger">Logout</a>
        </div>
    </div>
    <div class="card mb-4 shadow-sm">
        <div class="card-header bg-primary text-white">Add New Student</div>
        <div class="card-body">
            <form action="{{ url_for('add_student') }}" method="POST" class="row g-3">
                <div class="col-md-2"><input type="text" name="student_id" class="form-control" placeholder="Student ID" required></div>
                <div class="col-md-3"><input type="text" name="name" class="form-control" placeholder="Full Name" required></div>
                <div class="col-md-2"><input type="text" name="course" class="form-control" placeholder="Course" required></div>
                <div class="col-md-2"><input type="text" name="year_level" class="form-control" placeholder="Year Level" required></div>
                <div class="col-md-2"><input type="text" name="contact_number" class="form-control" placeholder="Contact Number" required></div>
                <div class="col-md-1"><button type="submit" class="btn btn-primary w-100">Add</button></div>
            </form>
        </div>
    </div>
    <div class="card shadow-sm">
        <div class="card-header bg-dark text-white">Student List</div>
        <div class="card-body p-0">
            <table class="table table-striped table-hover mb-0">
                <thead class="table-dark">
                    <tr>
                        <th>Student ID</th><th>Name</th><th>Course</th><th>Year Level</th><th>Contact</th><th class="text-center">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for student in students %}
                    <tr>
                        <td>{{ student.student_id }}</td>
                        <td>{{ student.name }}</td>
                        <td>{{ student.course }}</td>
                        <td>{{ student.year_level }}</td>
                        <td>{{ student.contact_number }}</td>
                        <td class="text-center">
                            <a href="{{ url_for('edit_student', id=student.id) }}" class="btn btn-sm btn-warning">Edit</a>
                            <a href="{{ url_for('delete_student', id=student.id) }}" class="btn btn-sm btn-danger" onclick="return confirm('Are you sure?')">Delete</a>
                        </td>
                    </tr>
                    {% else %}
                    <tr><td colspan="6" class="text-center py-4">No students enrolled yet.</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
</body>
</html>
"""

# --- ROUTES ---

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template_string(LOGIN_TEMPLATE)

# LOGOUT
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# READ: Display all students
@app.route('/')
@login_required
def index():
    students = Student.query.all()
    return render_template_string(INDEX_TEMPLATE_WITH_LOGIN, students=students, current_user=current_user)

# CREATE: Add a new student
@app.route('/add', methods=['POST'])
@login_required
def add_student():
    new_student = Student(
        student_id=request.form['student_id'],
        name=request.form['name'],
        course=request.form['course'],
        year_level=request.form['year_level'],
        contact_number=request.form['contact_number']
    )
    try:
        db.session.add(new_student)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error adding student: {e}") 
    return redirect(url_for('index'))

# UPDATE
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        student.student_id = request.form['student_id']
        student.name = request.form['name']
        student.course = request.form['course']
        student.year_level = request.form['year_level']
        student.contact_number = request.form['contact_number']
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error updating student: {e}")
        return redirect(url_for('index'))
    return render_template_string(EDIT_TEMPLATE, student=student)

# DELETE
@app.route('/delete/<int:id>')
@login_required
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
