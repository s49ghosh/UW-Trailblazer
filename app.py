from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import logging

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

    takenCourses = ratings()
    
    return render_template('index.html', users=users, takenCourses=takenCourses, subjectDropdown=subject, termDropdown=termdropdown)


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
        cur.execute("SELECT * FROM Courses WHERE course_code LIKE %s", ('%' + query + '%',))
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
    userid = request.form.get('uid')
    value = request.form.get('action')
    if course_code:
        if value == 'Planned':
            cur = mysql.connection.cursor()
            try:
                cur.execute(f'SELECT prereq FROM Requirements WHERE course_code = "{course_code}"')
                requirements = [row['prereq'] for row in cur.fetchall()]
                cur.execute(f'SELECT course_code FROM UserTakenCourses WHERE uid = "{userid}"')
                taken = [row['course_code'] for row in cur.fetchall()]
                for course in requirements:
                    if course not in taken:
                        return 'Missing Prerequisite!'
                cur.execute(f'INSERT INTO UserPlannedCourses (uid, course_code) VALUES ({userid}, "{course_code}")') #replace test with user login!            
                mysql.connection.commit()
                cur.close()
                return 'Course added to Planned Courses!'  
            except:
                return f'{course_code} already added for user {userid}'
        elif value == 'Taken':
            cur = mysql.connection.cursor()
            try:
                cur.execute(f'INSERT INTO UserTakenCourses (uid, course_code) VALUES ({userid}, "{course_code}")') #replace test with user login!            
                mysql.connection.commit()
                cur.close()
                return 'Course added to Taken Courses!'
            except:
                return f'{course_code} already added for user {userid}'
    else:
        return 'No course code submitted'

@app.route('/', methods=['GET'])
def ratings():
    user_id = "1"
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT UserTakenCourses.course_code, Ratings.rating
        FROM Users
        INNER JOIN UserTakenCourses ON Users.uid = UserTakenCourses.uid
        LEFT JOIN Ratings ON UserTakenCourses.course_code = Ratings.course_code and Users.uid = Ratings.uid
        WHERE Users.uid = %s
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
            INSERT INTO Ratings (uid, course_code, rating)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE rating = %s
        """, (user_id, course_code, rating, rating))

    mysql.connection.commit()

    cur.close()

    return redirect(url_for('index'))

@app.route('/friend-courses', methods=['GET'])
def get_friend_courses():
    cur = mysql.connection.cursor()

    # Substitute 1 and 2 with the user ids you're interested in
    cur.execute("""
        SELECT DISTINCT uf.friend_id, c.course_code, c.course_name, s.subject_name, s.avg_rating
        FROM userfriends uf
        JOIN users u ON uf.friend_id = u.uid
        JOIN usertakencourses ut ON u.uid = ut.uid
        JOIN courses c ON ut.course_code = c.course_code
        JOIN subjects s ON c.subject_code = s.subject_code
        WHERE uf.uid = 1
        AND c.course_code IN (
            SELECT course_code
            FROM courses 
            WHERE u.uid = 2
        )
    """)
    courses = cur.fetchall()
    cur.close()
    return render_template('friend_courses.html', courses=courses)



if __name__ == '__main__':
    app.run()
