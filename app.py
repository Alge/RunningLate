import datetime

from flask import Flask
from flask import g
from flask import redirect
from flask import request
from flask import session
from flask import url_for, abort, render_template, flash
from functools import wraps
from hashlib import md5
from peewee import *

# config - aside from our database, the rest is for use by Flask
DATABASE = 'runningLate.db'
DEBUG = True
SECRET_KEY = 'hin6bab8gasde25*r=x&amp;+5$0kn=-#log$pt^#@vrqjld!^2ci@g*b'

# create a flask application - this ``app`` object will be used to handle
# inbound requests, routing them to the proper 'view' functions, etc
app = Flask(__name__)
app.config.from_object(__name__)

# create a peewee database instance -- our models will use this database to
# persist information
database = SqliteDatabase(DATABASE)

# model definitions -- the standard "pattern" is to define a base model class
# that specifies which database to use.  then, any subclasses will automatically
# use the correct storage. for more information, see:
# http://charlesleifer.com/docs/peewee/peewee/models.html#model-api-smells-like-django
class BaseModel(Model):
    class Meta:
        database = database

class User(BaseModel):
    username = CharField(unique=True)

class Sprint(BaseModel):
    user = ForeignKeyField(User, backref='sprints')
    start = DateTimeField()
    end = DateTimeField()
    startLat = DecimalField()
    startLong = DecimalField()
    endLat = DecimalField()
    endLong = DecimalField()
    score = DecimalField()

# simple utility function to create tables
def create_tables():
    with database:
        database.create_tables([User, Sprint])

# Request handlers -- these two hooks are provided by flask and we will use them
# to create and tear down a database connection on each request.
@app.before_request
def before_request():
    g.db = database
    g.db.connect()

@app.after_request
def after_request(response):
    g.db.close()
    return response

# views -- these are the actual mappings of url to view function
@app.route('/')
def homepage():
  return "hej!"

@app.route('/user')
def get_user():
    return render_template("index.html")

@app.route('/start_sprint')
def start_sprint():
    return render_template("index.html")

@app.route('/end_sprint')
def end_sprint():
    return render_template("index.html")

@app.route('/get_path')
def get_distance():
    return render_template("index.html")


# allow running from the command line
if __name__ == '__main__':
    create_tables()
    app.run()
