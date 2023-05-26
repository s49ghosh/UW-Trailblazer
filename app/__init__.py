import os
from flask import Flask

from peewee import *
from dotenv import load_dotenv

from flask import Flask
from flaskext.mysql import MySQL


load_dotenv()
app = Flask(__name__)

if os.getenv("TESTING") == "true":
    print("Running in test mode")
    mydb = SqliteDatabase("file:memory?mode=memory&cache=shared", uri=True)
else:
    mydb = MySQLDatabase(
        os.getenv("MYSQL_DATABASE"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        host=os.getenv("MYSQL_HOST"),
        port=3306
    )


host = os.getenv("MYSQL_HOST")
user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
db = os.getenv("MYSQL_DATABASE")

print(host,user,password,db)
app.config['MYSQL_DATABASE_HOST'] = host
app.config['MYSQL_DATABASE_USER'] = user
app.config['MYSQL_DATABASE_PASSWORD'] = password
app.config['MYSQL_DATABASE_DB'] = db

mysql = MySQL(app)


@app.route('/')
def home():
    conn = mysql.connect()
    cursor = conn.cursor()
    # with open ('backend/database/sql/createtables.sql', 'r') as query:
    #     cursor.execute(query)
    
    # with open ('backend/database/sql/sampledataset.sql', 'r') as query:
    #     cursor.execute(query)

    cursor.execute("SELECT * FROM testDB")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return str(data)



if __name__ == "__main__":
    mydb.connect()
    app.run()

