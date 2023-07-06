import requests
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import logging
import re

app = Flask(__name__)

# Configure MySQL
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = ''
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = ''
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialize MySQL
mysql = MySQL(app)

# Set Open API key
openapi_key = '1E5B68EB071D404F8D68C2571CDBA921'

def Term_table():
    # Call API endpoint: /v3/terms
    url = "https://openapi.data.uwaterloo.ca/v3/terms"
    headers = {'x-api-key': openapi_key}
    response = requests.get(url, headers=headers)
    data = response.json()

    cursor = mysql.connection.cursor()

    terms = []
    for term in data:
        term_id = term['termCode']
        terms.append(term_id)
        start_date = term['termBeginDate']
        end_date = term['termEndDate']

        term_season = ''
        if term_id.endswith('9'):
            term_season = 'Fall'
        elif term_id.endswith('1'):
            term_season = 'Winter'
        elif term_id.endswith('5'):
            term_season = 'Spring'

        if term_season:
            insert_command = f"INSERT INTO Terms(term_id, start_date, end_date, term_season) VALUES ('{term_id}', '{start_date}', '{end_date}', '{term_season}')"
            cursor.execute(insert_command)
            mysql.connection.commit()

    cursor.close()
    return terms

def Course_table(terms):
    cursor = mysql.connection.cursor()

    for term_id in terms:
        # Call API endpoint: /v3/Courses/{termCode}
        url = f"https://openapi.data.uwaterloo.ca/v3/Courses/{term_id}"
        headers = {'x-api-key': openapi_key}
        response = requests.get(url, headers=headers)
        data = response.json()

        if response.status_code == 404:
            continue
        for course in data:
            #print(course)
            course_code = course['subjectCode'] + ' ' + course['catalogNumber']
            course_name = course['title'].replace("'", "''")
            subject_code = course['subjectCode']
            level = course['catalogNumber'][0]
            if not level.isdigit():
                print(course['catalogNumber'])
                continue
            course_level = int(course['catalogNumber'][0]) * 100
            course_id = course['courseId']

            insert_course = f"INSERT INTO Courses(course_code, course_name, subject_code, course_level, rating) VALUES ('{course_code}', '{course_name}', '{subject_code}', {course_level}, 0) ON DUPLICATE KEY UPDATE course_code = '{course_code}'"
            cursor.execute(insert_course)
            mysql.connection.commit()

            # Call the API endpoint: /v3/ClassSchedule/{termCode}/{courseId}
            url_schedule = f"https://openapi.data.uwaterloo.ca/v3/ClassSchedules/{term_id}/{course_id}"
            response_schedule = requests.get(url_schedule, headers=headers)
            if response_schedule.status_code == 404:
                continue
            data_schedule = response_schedule.json()
            if data_schedule:
                enroll_cap = data_schedule[0]['maxEnrollmentCapacity']

                insert_enrollment = f"INSERT INTO EnrollCapacity(course_code, term_id, enroll_cap) VALUES ('{course_code}', '{term_id}', {enroll_cap})"
                cursor.execute(insert_enrollment)
                mysql.connection.commit()
    cursor.close()
    

@app.route('/')
def API_calls():
    terms = Term_table()
    Course_table(terms)
    return 'Tables created'

if __name__ == '__main__':
    app.run()