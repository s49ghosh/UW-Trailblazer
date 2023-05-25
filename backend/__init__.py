import os
from flask import Flask, render_template, make_response, request
from peewee import *
from dotenv import *

load_dotenv()
app = Flask(__name__)


if os.getenv("TESTING") == "true":
    print("Running in test mode")
    mydb = SqliteDatabase("file:memory?mode=memory&cache=shared",uri=True)
else:
    # db
    mydb = MySQLDatabase(os.getenv("MYSQL_DATABASE"),
           user=os.getenv("MYSQL_USER"),
           password=os.getenv("MYSQL_PASSWORD"),
           host=os.getenv("MYSQL_HOST"),
           port=3306
          )

print(mydb)

class TimelinePost(Model):
       name = CharField()
       email = CharField()
       content = TextField()
       created_at = DateTimeField(default=datetime.datetime.now)

       class Meta:
              database = mydb

mydb.connect()
mydb.create_tables([TimelinePost], safe=True)
if os.getenv("TESTING") != "true":
    mydb.close()