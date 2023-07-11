from fnmatch import fnmatchcase
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import logging
import bcrypt
import traceback

app = Flask(__name__)

# Configure MySQL
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'CS348USER'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'jasminefeature'
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

    takenCourses = ''
    if 'username' in session:
        takenCourses = ratings() 
    
    return render_template('index.html', users=users, takenCourses=takenCourses, subjectDropdown=subject, termDropdown=termdropdown)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        first_name = request.form['fname']
        last_name = request.form['lname']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM LoginDetails WHERE uid = %s", (username,))
        user = cur.fetchone()

        if user:
            error = 'UID already exists.'
            return render_template('signup.html', error=error)

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cur.execute("INSERT INTO Users (uid, first_name, last_name) VALUES (%s, %s, %s)", (username, first_name, last_name))
        mysql.connection.commit()

        cur.execute("INSERT INTO LoginDetails (uid, password) VALUES (%s, %s)", (username, hashed_password))
        mysql.connection.commit()
        cur.close()

        session['username'] = username
        session['fname'] = first_name
        session['lname'] = last_name
        return redirect('/')

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM LoginDetails WHERE uid = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['username'] = username
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM Users WHERE uid = %s", (username,))
            userDetails = cur.fetchone()
            cur.close()
            session['fname'] = userDetails['first_name']
            session['lname'] = userDetails['last_name']
            return redirect('/')
        else:
            error = 'Invalid username or password.'
            return render_template('login.html', error=error)

    return render_template('login.html')   


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


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

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Subjects")
    subjectdropdown = cur.fetchall()
    courses ={}

    if query:
        if subject == 'All': # There is a query and no subject filter
            cur.execute("SELECT * FROM Courses WHERE course_code LIKE %s", ('%' + query + '%',))
            courses = cur.fetchall()

        else: # There is a query and subject filter
            cur.execute("SELECT * FROM Courses WHERE course_code LIKE %s AND subject_code LIKE %s", ('%' + query + '%', '%' + subject + '%',))
            courses = cur.fetchall()
        cur.close()
        return render_template('search.html', courses=courses, subject=subject, query=query, subjectDropdown = subjectdropdown)
    else:

        if subject != 'All': # There is no query and a subject filer
            cur.execute("SELECT * FROM Courses WHERE subject_code LIKE %s", ('%' + subject + '%',))
            courses = cur.fetchall()
            cur.close()

        elif subject == 'All': # There is no query and no subject filter
            return render_template('search.html', message = 'Please specifiy search more.' , subject = subject, query=query, subjectDropdown = subjectdropdown)
        return render_template('search.html', courses=courses, subject=subject, query=query, subjectDropdown = subjectdropdown)


@app.route('/add_course', methods=['POST'])
def add_course():
    course_code = request.form.get('course_code')
    
    #userid = request.form.get('uid')
    userid = 0
    if 'username' in session:
        userid = session['username']
    else:
        html_code = '<!DOCTYPE html><html><head><title>Sign In</title></head><body><h3>Please sign in to add courses</h3><button onclick="location.href=\'/login\'">Sign In</button></body></html>'
        return html_code
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
    user_id = session['username']
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT UserTakenCourses.course_code, Ratings.rating
        FROM Users
        INNER JOIN UserTakenCourses ON Users.uid = UserTakenCourses.uid
        LEFT JOIN Ratings ON UserTakenCourses.course_code = Ratings.course_code and Users.uid = Ratings.uid
        WHERE Users.uid = %s
    """, (user_id,))
    courses = [{'course_code': row['course_code'], 'rating': row['rating'] if row['rating'] is not None else ""} for row in cur.fetchall()]
    
    cur.execute("""
        SELECT friend_id 
        FROM UserFriends
        WHERE uid = %s
    """, (user_id,))
    friends = [{'friend_id': row['friend_id']} for row in cur.fetchall()]

    cur.close()
    return render_template('index.html', courses=courses, friends=friends)

@app.route('/submit-ratings', methods=['POST'])
def submit_ratings():
    user_id = session['username']
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
    friend_id = request.form.get('friend_id')  # friend id taken from form
    user_id = session['username']
    
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT DISTINCT uf.friend_id, c.course_code, c.course_name, s.subject_name, s.avg_rating
        FROM userfriends uf
        JOIN users u ON uf.friend_id = u.uid
        JOIN usertakencourses ut ON u.uid = ut.uid
        JOIN courses c ON ut.course_code = c.course_code
        JOIN subjects s ON c.subject_code = s.subject_code
        WHERE uf.uid = %s
        AND c.course_code IN (
            SELECT course_code
            FROM usertakencourses
            WHERE uid = %s
        )
    """, (user_id, friend_id,))

    courses = cur.fetchall()
    cur.close()
    return render_template('friend_courses.html', courses=courses)


@app.route('/course-friends', methods=['GET'])
def get_friends_same_course():
    course_code = request.form.get('course_code')
    cur = mysql.connection.cursor()
    
    user_id = session['username']
    
    cur.execute("""
        SELECT DISTINCT uf.friend_id, u.name
        FROM UserFriends uf
        INNER JOIN Users u ON uf.friend_id = u.uid
        INNER JOIN UserTakenCourses utc ON uf.friend_id = utc.uid
        WHERE uf.uid = %s AND utc.course_code = %s
    """, (user_id, course_code))
    
    friends = [{'friend_id': row['friend_id'], 'name': row['name']} for row in cur.fetchall()]

    cur.close()
    return render_template('friends_courses.html', items=friends)


@app.route('/charts', methods=['GET']) 
def viewTopRated():
    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT course_name, rating FROM courses ORDER BY rating DESC")
        result = cur.fetchall()
        courses = [row['course_name'] for row in result]
        ratings = [row['rating'] for row in result]
        if len(courses) > 100:
            courses = courses[0:101]
            ratings = ratings[0:101]
        return render_template('charts.html', courses=courses, ratings=ratings)
    except Exception as e:
        traceback.print_exc()
        return f'Error: {str(e)}'
    


if __name__ == '__main__':
    app.run()
