from flask import Flask, render_template, request
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'CS348USER'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'TestDB'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialize MySQL
mysql = MySQL(app)


@app.route('/')
def index():
    # Retrieve data from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user")
    users = cur.fetchall()
    cur.close()

    return render_template('index.html', users=users)


@app.route('/add', methods=['POST'])
def add_user():
    # Get user data from the form
    uid = request.form['uid']
    fname = request.form['fname']
    lname = request.form['lname']
    startyear = request.form['startyear']

    # Insert data into the database
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO user (uid, first_name, last_name, start_year) VALUES (%s, %s,%s, %s)", (uid, fname, lname, startyear))
    mysql.connection.commit()
    cur.close()

    return 'User added successfully'

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    if query:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM courses WHERE course_name LIKE %s", ('%' + query + '%',))
        courses = cur.fetchall()
        cur.close()
        return render_template('index.html', courses=courses, query=query)
    else:
        return render_template('index.html', message='Please enter a search query.')

@app.route('/add_course', methods=['POST'])
def add_course():
    course_code = request.form.get('course_code')
    if course_code:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO UserTakenCourses (uid, course_id) VALUES (%s, %s)", ('1234', course_code)) #replace test with user login!
        mysql.connection.commit()
        cur.close()
        return 'Course added to selectedCourses!'
    else:
        return 'Invalid request.'

if __name__ == '__main__':
    app.run()
