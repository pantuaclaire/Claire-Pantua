from flask import Flask, request, redirect, url_for, render_template_string
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- DATABASE MODEL ---
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Internal DB ID
    student_id = db.Column(db.String(50), nullable=False, unique=True) # School Student ID
    name = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    year_level = db.Column(db.String(50), nullable=False)
    contact_number = db.Column(db.String(50), nullable=False)

# Initialize the database
with app.app_context():
    db.create_all()


# --- HTML TEMPLATES ---

# Main page for Reading and Creating students
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Student Information System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container mt-5">
    <h2 class="mb-4">Student Information System</h2>
    
    <div class="card mb-4 shadow-sm">
        <div class="card-header bg-primary text-white">Add New Student</div>
        <div class="card-body">
            <form action="{{ url_for('add_student') }}" method="POST" class="row g-3">
                <div class="col-md-2">
                    <input type="text" name="student_id" class="form-control" placeholder="Student ID" required>
                </div>
                <div class="col-md-3">
                    <input type="text" name="name" class="form-control" placeholder="Full Name" required>
                </div>
                <div class="col-md-2">
                    <input type="text" name="course" class="form-control" placeholder="Course" required>
                </div>
                <div class="col-md-2">
                    <input type="text" name="year_level" class="form-control" placeholder="Year Level" required>
                </div>
                <div class="col-md-2">
                    <input type="text" name="contact_number" class="form-control" placeholder="Contact Number" required>
                </div>
                <div class="col-md-1">
                    <button type="submit" class="btn btn-primary w-100">Add</button>
                </div>
            </form>
        </div>
    </div>

    <div class="card shadow-sm">
        <div class="card-header bg-dark text-white">Student List</div>
        <div class="card-body p-0">
            <table class="table table-striped table-hover mb-0">
                <thead class="table-dark">
                    <tr>
                        <th>Student ID</th>
                        <th>Name</th>
                        <th>Course</th>
                        <th>Year Level</th>
                        <th>Contact Number</th>
                        <th class="text-center">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for student in students %}
                    <tr>
                        <td class="align-middle">{{ student.student_id }}</td>
                        <td class="align-middle">{{ student.name }}</td>
                        <td class="align-middle">{{ student.course }}</td>
                        <td class="align-middle">{{ student.year_level }}</td>
                        <td class="align-middle">{{ student.contact_number }}</td>
                        <td class="text-center align-middle">
                            <a href="{{ url_for('edit_student', id=student.id) }}" class="btn btn-sm btn-warning">Edit</a>
                            <a href="{{ url_for('delete_student', id=student.id) }}" class="btn btn-sm btn-danger" onclick="return confirm('Are you sure you want to remove this student?')">Delete</a>
                        </td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="6" class="text-center py-4">No students enrolled yet.</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
</body>
</html>
"""

# Page for Updating existing student information
EDIT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Edit Student</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container mt-5">
    <div class="card mx-auto shadow-sm" style="max-width: 600px;">
        <div class="card-header bg-warning"><strong>Edit Student Information</strong></div>
        <div class="card-body">
            <form action="{{ url_for('edit_student', id=student.id) }}" method="POST">
                <div class="mb-3">
                    <label class="form-label">Student ID</label>
                    <input type="text" name="student_id" class="form-control" value="{{ student.student_id }}" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Full Name</label>
                    <input type="text" name="name" class="form-control" value="{{ student.name }}" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Course</label>
                    <input type="text" name="course" class="form-control" value="{{ student.course }}" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Year Level</label>
                    <input type="text" name="year_level" class="form-control" value="{{ student.year_level }}" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Contact Number</label>
                    <input type="text" name="contact_number" class="form-control" value="{{ student.contact_number }}" required>
                </div>
                <div class="d-flex justify-content-between">
                    <a href="{{ url_for('index') }}" class="btn btn-secondary">Cancel</a>
                    <button type="submit" class="btn btn-success">Update Student</button>
                </div>
            </form>
        </div>
    </div>
</div>
</body>
</html>
"""

# --- ROUTES ---

# READ: Display all students
@app.route('/')
def index():
    students = Student.query.all()
    return render_template_string(INDEX_TEMPLATE, students=students)

# CREATE: Add a new student
@app.route('/add', methods=['POST'])
def add_student():
    new_student = Student(
        student_id=request.form['student_id'],
        name=request.form['name'],
        course=request.form['course'],
        year_level=request.form['year_level'],
        contact_number=request.form['contact_number']
    )
    # Basic error handling in case of duplicate student IDs
    try:
        db.session.add(new_student)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # In a production app, you'd flash an error message here
        print(f"Error adding student: {e}") 
    return redirect(url_for('index'))

# UPDATE: Edit an existing student
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
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

# DELETE: Remove a student
@app.route('/delete/<int:id>')
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
