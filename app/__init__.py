from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configure MySQL
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'CS348USER'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'betterDB'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialize MySQL
mysql = MySQL(app)


@app.route('/')
def index():
    # Retrieve data from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Users")
    users = cur.fetchall()
    cur.execute("SELECT * FROM Subjects")
    subject = cur.fetchall()
    cur.execute("SELECT * FROM Terms")
    termdropdown = cur.fetchall()
    cur.close()

    return render_template('index.html', users=users, subjectDropdown=subject, termDropdown=termdropdown )


@app.route('/add', methods=['POST'])
def add_user():
    # Get user data from the form
    uid = request.form['uid']
    fname = request.form['fname']
    lname = request.form['lname']
    startyear = request.form['startyear']

    # Insert data into the database
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO Users (uid, first_name, last_name, start_year) VALUES (%s, %s,%s, %s)", (uid, fname, lname, startyear))
    mysql.connection.commit()
    cur.close()

    return 'User added successfully'

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    subject = request.form.get('subjectfilter')
    #print(query)
    print(subject)
    if query:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Courses WHERE course_name LIKE %s", ('%' + query + '%',))
        courses = cur.fetchall()
        cur.execute("SELECT * FROM Subjects")
        subjectdropdown = cur.fetchall()
        cur.execute("SELECT * FROM Terms")
        termdropdown = cur.fetchall()
        cur.close()
        return render_template('search.html', courses=courses, query=query, subjectDropdown = subjectdropdown, termDropdown = termdropdown)
    else:
        return render_template('search.html', message='Please enter a search query.')


@app.route('/add_course', methods=['POST'])
def add_course():
    course_code = request.form.get('course_code')
    userid = '123'
    if course_code:
        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO UserTakenCourses (uid, course_id) VALUES (%s, %s)", (userid, course_code)) #replace test with user login!            
            mysql.connection.commit()
            cur.close()
            return 'Course added to selectedCourses!'
        except:
            return f'Course already added for user {userid}'
    else:
        return 'No course code submitted'

if __name__ == '__main__':
    app.run()
