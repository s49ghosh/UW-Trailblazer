import requests
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import logging
import json
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

def separate_reqs(requirements):
    if requirements is None or not requirements.startswith('Prereq'):
        return []
    requirements = requirements.split('.')[0]
    requirements = requirements.split(';')[0]
    prereqs = re.split(r', \s*(?![^()]*\))|(?<!\()\s* and \s*(?![^()]*\))', requirements)
    pattern = re.compile(r'[A-Z]+ \d+')
    
    res = []
    subject = ''
    prereqs[0] = prereqs[0].strip()[len('prereq:'):].strip()
    if prereqs[0].strip().lower().startswith('one of'):
        res.append([])
        for prereq in prereqs:
            if prereq.strip().lower().startswith('one of'):
                prereq = prereq.strip()[len('one of'):].strip()

            match = re.search(pattern, prereq)
            if match:
                subject = re.match(r'[A-Z]+', match[0]).group()
                res[0].append(match[0])
            elif subject == '':
                break
            else:
                res[0].append(subject + ' ' + prereq)
        return res

    prereqs_or = re.split(r' or ', requirements)
    ret = True
    if len(prereqs_or) > 1:
        res.append([])
        prereqs_or[0] = prereqs_or[0].strip()[len('prereq:'):].strip()
        for prereq in prereqs_or:
            if ',' in prereq:
                ret = False
                break
            match = re.search(pattern, prereq)
            if match:
                subject = re.match(r'[A-Z]+', match[0]).group()
                res[0].append(match[0])
            elif prereq.isdigit():
                res[0].append(subject + ' ' + prereq)
        if ret:
            return res
        else:
            res = []

    for prereq in prereqs:
        if re.match(r'^\(.+\)$', prereq):
            prereq = prereq[1:-1]
        if 'one of' in prereq or 'One of' in prereq:
            cur_subject = ''
            prereq = re.split(r', ', prereq)
            res.append([])
            for pre in prereq:
                if pre.strip().lower().startswith('one of'):
                    pre = pre.strip()[len('one of'):].strip()
                match = re.search(pattern, pre)
                if match:
                    cur_subject = re.match(r'[A-Z]+', match[0]).group()
                    res[-1].append(match[0])
                elif pre.isdigit():
                    res[-1].append(cur_subject + ' ' + pre)
            continue
        if 'or' in prereq:
            prereq = re.split(r' or ', prereq)
            res.append([])
            cur_subject = ''
            for pre in prereq:
                match = re.search(pattern, pre)
                if match:
                    cur_subject = re.match(r'[A-Z]+', match[0]).group()
                    res[-1].append(match[0])
                elif pre.isdigit():
                    res[-1].append(cur_subject + ' ' + pre)
            continue
        match = re.search(pattern, prereq)
        if match:
            subject = re.match(r'[A-Z]+', match[0]).group()
            res.append(match[0])
            continue
        elif prereq.isdigit():
            res.append(subject + ' ' + prereq)
            continue

    return res




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
            course_code = course['subjectCode'] + ' ' + course['catalogNumber']
            course_name = course['title'].replace("'", "''")
            subject_code = course['subjectCode']
            level = course['catalogNumber'][0]
            if not level.isdigit():
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

                insert_enrollment = f"INSERT INTO EnrollCapacity(course_code, term_id, enroll_cap) VALUES ('{course_code}', '{term_id}', {enroll_cap}) ON DUPLICATE KEY UPDATE course_code = '{course_code}'"
                cursor.execute(insert_enrollment)
                mysql.connection.commit()

            # requirements
            requirement = course['requirementsDescription']
            #print(requirement)
            prereq = separate_reqs(requirement)
            #print(prereq)
            json_string = json.dumps(prereq)
            insert_requirement = f"INSERT INTO Requirements(course_code, prereq) VALUES ('{course_code}', '{json_string}') ON DUPLICATE KEY UPDATE course_code = '{course_code}'"
            cursor.execute(insert_requirement)
            mysql.connection.commit()

    cursor.close()
    

@app.route('/')
def API_calls():
    terms = Term_table()
    Course_table(terms)
    return 'Tables created'

if __name__ == '__main__':
    app.run()