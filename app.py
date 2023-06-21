from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import logging

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

    takenCourses = ratings()

    return render_template('index.html', users=users, takenCourses=takenCourses)


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

@app.route('/', methods=['GET'])
def ratings():
    user_id = "1"
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT takenCourses.course_code, ratings.rating
        FROM user
        INNER JOIN takenCourses ON user.uid = takenCourses.uid
        LEFT JOIN ratings ON takenCourses.course_code = ratings.course_code and user.uid = ratings.uid
        WHERE user.uid = %s
    """, (user_id))

    courses = [{'course_code': row['course_code'], 'rating': row['rating'] if row['rating'] is not None else ""} for row in cur.fetchall()]

    cur.close()
    return courses

@app.route('/submit-ratings', methods=['POST'])
def submit_ratings():
    user_id = '1' 
    cur = mysql.connection.cursor()

    for course_code, rating in request.form.items():
        cur.execute("""
            INSERT INTO ratings (course_code, uid, rating)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE rating = %s
        """, (course_code, user_id, rating, rating))

    mysql.connection.commit()

    cur.close()

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
