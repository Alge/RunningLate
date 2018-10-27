import datetime

from flask import Flask
from flask import g
from flask import redirect
from flask import request
from flask import session
from flask import url_for, abort, render_template, flash
from functools import wraps
from hashlib import md5
import peewee  # Let's be explicit
from peewee import *
import json
from playhouse.shortcuts import model_to_dict, dict_to_model
from flask_cors import CORS
import dateutil.parser
from sl import travel_planner, location_lookup, travel_planner_recon
import time
from flask import abort


# config - aside from our database, the rest is for use by Flask
DATABASE = 'runningLate.db'
DEBUG = True
SECRET_KEY = 'hin6bab8gasde25*r=x&amp;+5$0kn=-#log$pt^#@vrqjld!^2ci@g*b'
PENALTY_CONSTANT = 1


def myconverter(o):
  if isinstance(o, datetime.datetime):
    return time.mktime(o.timetuple()) + 7200


# create a flask application - this ``app`` object will be used to handle
# inbound requests, routing them to the proper 'view' functions, etc
app = Flask(__name__)
CORS(app)
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
    username = peewee.CharField(unique=True)

    def get_json(self):
        return {
            "username": self.username,
            "sprints": [sprint.get_json() for sprint in self.sprints],
        }

class Sprint(BaseModel):
  user = ForeignKeyField(User, backref='sprints')
  start = DateTimeField()
  end = DateTimeField(null = True)
  startLat = FloatField()
  startLong = FloatField()
  endLat = FloatField()
  endLong = FloatField()
  score = FloatField(null = True)
  distance = FloatField()
  reconId = CharField()
  departure = DateTimeField()
  goal_name = DateTimeField()

  def get_score(self):
    duration = self.end-self.start
    margin = (self.departure + datetime.timedelta(minutes=1) - self.end).total_seconds()
    score = 0
    if margin >= 0:
      score += margin * PENALTY_CONSTANT
    else:

      score -= 1000
      return score
    score = (self.distance ** 1.2) / duration.total_seconds()
    return score

  def get_json(self):
    j = {}
    j["id"] = self.id
    j["startTime"] = time.mktime(self.start.timetuple()) + 7200
    if self.end:
      j["endTime"] = time.mktime(self.end.timetuple()) + 7200
    j["startLat"] = self.startLat
    j["startLong"] = self.startLong
    j["endLat"] = self.endLat
    j["endLong"] = self.endLong
    if self.score:
      j["score"] = self.score
    j["distance"] = self.distance
    j["reconId"] = self.reconId
    if isinstance(self.departure, str):
      self.departure = dateutil.parser.parse(self.departure)
    j["departure"] = time.mktime(self.departure.timetuple()) + 7200
    j["goalName"] = self.goal_name
    return j

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

@app.route('/register', methods=['POST'])
def register():
  if request.method == 'POST' and request.form['username']:
    try:
      with database.atomic():
       # Attempt to create the user. If the username is taken, due to the
       # unique constraint, the database will raise an IntegrityError.
        user = User.create(username=request.form['username'])

    except IntegrityError:
      return json.dumps({"error":"Username already taken"})

  return json.dumps(user.get_json())


@app.route('/user')
def get_users():
    return json.dumps([user.get_json() for user in User.select()])

@app.route('/user/<username>')
def get_user(username):
  user = User.get(User.username == username)

  return json.dumps(user.get_json(), sort_keys=True, indent=4)

@app.route('/sprint/<id>')
def get_sprint(id):
  sprint = Sprint.get(Sprint.id == id)

  return json.dumps(sprint.get_json(), sort_keys=True, indent=4)


@app.route('/start_sprint', methods = ['POST'])
def start_sprint():

  print(request.form)
  if request.method == 'POST' and request.form['startPosLat'] and request.form['endPosLat'] and request.form['startPosLong'] and request.form['endPosLat'] and request.form['username'] and request.form['distance'] and request.form['reconId']:
    print(request.form)
    sprint = Sprint()

    user = User.get(User.username==request.form['username'])
    if not user:
      return "{'error':'no user with that username found'}"

    sprint.user = user
    sprint.start = datetime.datetime.utcnow()
    sprint.startLat = request.form['startPosLat']
    sprint.startLong = request.form['startPosLong']
    sprint.endLat = request.form['endPosLat']
    sprint.endLong = request.form['endPosLong']
    sprint.distance = request.form['distance']
    sprint.reconId = request.form['reconId']

    routes = travel_planner_recon(sprint.reconId)

    if routes and "error" not in routes:
        sprint.departure = routes['sprint_deadline_timetable']
        if isinstance(sprint.departure, str):
          sprint.departure = dateutil.parser.parse(sprint.departure)
        print(type(routes['sprint_deadline_timetable']))
        print(routes['sprint_deadline_timetable'])
        sprint.goal_name = routes['sprint_goal_name']
    sprint.save()

    return json.dumps(sprint.get_json(), sort_keys=True, indent=4)

  return "failed"

@app.route('/end_sprint', methods=["POST"])
def end_sprint():
  if request.form['sprint']:
    sprint = Sprint.get(Sprint.id == int(request.form['sprint']))
    if sprint:
      #if sprint.end:
      #  return json.dumps({"error":"Sprint already ended"})
      sprint.end = datetime.datetime.utcnow()
      sprint.score = sprint.get_score()
      sprint.save()
      return json.dumps(sprint.get_json())
  return json.dumps({"error":"No such sprint"})


@app.route('/get_route', methods=["POST"])
def get_route():
  if request.form['startLat'] and request.form['startLong'] and request.form['endLat'] and request.form['endLong']:
    route = travel_planner((request.form['startLat'], request.form['startLong']), (request.form['endLat'], request.form['endLong']))
    if not route:
      return "{'error':'SL failed'}"
    if "error" in route:
      return  route
    if not route:
      abort(404)
    print(route)
    print(json.dumps(route, default = myconverter))
    return json.dumps(route, default = myconverter)
  return "{'error':'wrong parameters supplied'}"


@app.route('/get_location/<q>', methods=["GET"])
def get_location(q):
  res = location_lookup(q)
  return json.dumps(res, default = myconverter)


@app.route('/get_path')
def get_distance():
  return render_template("index.html")


# allow running from the command line
if __name__ == '__main__':
  create_tables()
  app.run()
