from flask import Flask, render_template, url_for, request, session, redirect
from flask_pymongo import PyMongo
from binascii import hexlify
import bcrypt
import os

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'heroku_k0kdm9jl'
app.config['MONGO_URI'] = 'mongodb://test_user:test_pass@ds157380.mlab.com:57380/heroku_k0kdm9jl'
app.secret_key = 'mysecret'

mongo = PyMongo(app)


@app.route('/')
def index():
    if 'username' in session:
        projects = mongo.db.projects
        u_projects = projects.find({'username': session['username']})

        return render_template('dashboard.html', u_name=session['username'], projects=u_projects)

    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name': request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
            session['username'] = request.form['username']
            return redirect(url_for('index'))

    return 'Invalid username/password combination'


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name': request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name': request.form['username'], 'password': hashpass, 'apikey': generate_key(40)})
            session['username'] = request.form['username']
            return redirect(url_for('index'))

        return 'That username already exists!'

    return render_template('register.html')


@app.route('/newproject', methods=['POST', 'GET'])
def new_project():
    if request.method == 'POST':
        projects = mongo.db.projects
        existing_project = projects.find_one({'name': request.form['p_name'], 'username': session['username']})

        if existing_project is None:
            projects.insert({'name': request.form['p_name'], 'username': session['username']})
            return redirect(url_for('index'))

        return 'You already have a project with that name!'

    return render_template('new_project.html')


@app.route('/api', methods=['GET'])
def api():
    users = mongo.db.users
    existing_user = users.find_one({'name': session['username']})

    return render_template('api.html', u_name=session['username'], apikey=existing_user['apikey'])


@app.route('/database/<project>')
def database(project):
    projects = mongo.db.projects
    existing_project = projects.find_one({'name': project, 'username': session['username']})

    if existing_project is None:
        return 'That project does not exist!'

    students = mongo.db.students
    existing_students = students.find({'teacheruser': session['username']})

    courses = mongo.db.courses
    existing_courses = courses.find({'teacheruser': session['username']})

    student_courses = mongo.db.student_courses
    existing_student_courses = student_courses.find({'teacheruser': session['username']})

    lessons = mongo.db.lessons
    existing_lessons = lessons.find({'teacheruser': session['username']})

    assignments = mongo.db.assignments
    existing_assignments = assignments.find({'teacheruser': session['username']})

    student_assignments = mongo.db.student_assignments
    existing_student_assignments = student_assignments.find({'teacheruser': session['username']})

    questions = mongo.db.questions
    existing_questions = questions.find({'teacheruser': session['username']})

    return render_template('project.html', p_name=project, u_name=session['username'],
                           students=existing_students,
                           courses=existing_courses,
                           student_courses=existing_student_courses,
                           lessons=existing_lessons,
                           assignments=existing_assignments,
                           student_assignments=existing_student_assignments,
                           questions=existing_questions)


def generate_key(length):
    return hexlify(os.urandom(length))


if __name__ == '__main__':
    app.run(debug=True)
