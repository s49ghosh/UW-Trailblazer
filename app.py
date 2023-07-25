from fnmatch import fnmatchcase
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import logging
import bcrypt
from call_api import API_calls
import traceback
import ast
from flask_mail import Mail, Message
import secrets
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)

# Configure MySQL
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = ''
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = ''
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


# Initialize MySQL
mysql = MySQL(app)


app.config['MAIL_SERVER']='smtp-mail.outlook.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'cs348ProjectGroup28@outlook.com'
app.config['MAIL_PASSWORD'] = 'cs348cs348'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['SECURITY_PASSWORD_SALT'] = secrets.token_hex(16)


mail = Mail(app)


with app.app_context():
    print("importing data")
    # comment the following line if don't want to use production data
    #API_calls(app, mysql)



def genToken(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    cur.execute("UPDATE Users SET confirmed = %s WHERE email = %s", (True, email))
    mysql.connection.commit()
    flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('login'))


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email


def sendEmail(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_USERNAME']
    )
    mail.send(msg)


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

    friends = []
    plannedCourses = []
    if 'username' in session:
        user_id = session['username']
        cur.execute("SELECT * FROM userfriends JOIN users ON userfriends.friend_id = users.uid WHERE userfriends.uid = %s", (user_id,))
        friends = cur.fetchall()

        cur.execute("SELECT * FROM UserPlannedCourses WHERE uid = %s", (user_id,))
        plannedCourses = cur.fetchall()

    cur.close()

    takenCourses = ''
    if 'username' in session:
        takenCourses = ratings() 

    return render_template('index.html', users=users, takenCourses=takenCourses, subjectDropdown=subject, termDropdown=termdropdown, friends=friends, plannedCourses=plannedCourses)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
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

        cur.execute("INSERT INTO Users (uid, first_name, last_name, email, confirmed) VALUES (%s, %s, %s, %s, %s)", (username, first_name, last_name, email, False))
        mysql.connection.commit()

        cur.execute("INSERT INTO LoginDetails (uid, password) VALUES (%s, %s)", (username, hashed_password))
        mysql.connection.commit()
        cur.close()

        token = genToken(email)
        confirm_url = url_for('confirm_email', token=token, _external=True)
        html = render_template('activate.html', confirm_url=confirm_url)
        subject = "Please confirm your email"
        sendEmail(email, subject, html)

        return redirect('/')

    return render_template('signup.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM LoginDetails JOIN Users ON LoginDetails.uid = Users.uid WHERE LoginDetails.uid = %s AND Users.confirmed = 1", (username,))
        user = cur.fetchone()
        cur.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['username'] = username
            session['fname'] = user['first_name']
            session['lname'] = user['last_name']
            return redirect('/')
        else:
            error = 'Invalid username or password or email not confirmed.'
            return render_template('login.html', error=error)

    return render_template('login.html')   


@app.route('/confirmed', methods=['GET', 'POST'])
def confirmed_email():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM LoginDetails WHERE uid = %s", (username,))
        user = cur.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            cur.execute("UPDATE Users SET confirmed = 1 WHERE uid = %s", (username,))
            mysql.connection.commit()

            cur.execute("SELECT * FROM LoginDetails JOIN Users ON LoginDetails.uid = Users.uid WHERE LoginDetails.uid = %s", (username,))
            user = cur.fetchone()
            cur.close()

            session['username'] = username
            session['fname'] = user['first_name']
            session['lname'] = user['last_name']
            return redirect('/')
        else:
            error = 'Invalid username or password or email not confirmed.'
            return render_template('confirmed.html', error=error)

    return render_template('confirmed.html')   



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

    # Insert data into the database
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO Users (uid, first_name, last_name) VALUES (%s, %s, %s)", (uid, fname, lname))
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
                requirements = requirements[0]
                requirements = requirements.strip('"')
                requirements = ast.literal_eval(requirements)
                for courses in requirements:
                    if type(courses) == list:
                        flag = 0
                        for item in courses:
                            if item in taken:
                                flag = 1
                                break
                        if not flag:
                            return f'Missing Prerequisite!: One of {courses}'
                    else: 
                        if courses not in taken:
                            return f'Missing Prerequisite!: {courses}'
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
    cur.close()
    return courses

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

@app.route('/friend-courses', methods=['GET', 'POST'])
def get_friend_courses():
    friend_id = request.args.get('friend_id')  # friend id taken from form
    user_id = session['username']
    
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT DISTINCT uf.friend_id, c.course_code, c.course_name, s.subject_name, s.avg_rating
        FROM userfriends uf
        JOIN users u ON uf.friend_id = u.uid
        JOIN userplannedcourses ut ON u.uid = ut.uid
        JOIN courses c ON ut.course_code = c.course_code
        JOIN subjects s ON c.subject_code = s.subject_code
        WHERE uf.uid = %s
        AND c.course_code IN (
            SELECT course_code
            FROM userplannedcourses
            WHERE uid = %s
        )
    """, (user_id, friend_id))

    courses = cur.fetchall()
    cur.close()
    return render_template('friend_courses.html', courses=courses)


@app.route('/course-friends', methods=['GET', 'POST'])
def get_friends_same_course():
    course_code = request.args.get('course_code')
    cur = mysql.connection.cursor()
    
    user_id = session['username']
    
    cur.execute("""
        SELECT DISTINCT uf.friend_id, u.first_name
        FROM UserFriends uf
        INNER JOIN Users u ON uf.friend_id = u.uid
        INNER JOIN UserPlannedCourses utc ON uf.friend_id = utc.uid
        WHERE uf.uid = %s AND utc.course_code = %s
    """, (user_id, course_code))
    
    friends = [{'friend_id': row['friend_id'], 'first_name': row['first_name']} for row in cur.fetchall()]

    cur.close()
    return render_template('course_friends.html', friends=friends)


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
