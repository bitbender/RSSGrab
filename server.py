from flask import Flask, request, jsonify
from config import Config
from smpl_conn_pool import SmplConnPool
import logging
from models.grabber import Grabber
from flask.ext.cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from bson.objectid import ObjectId
from storage import fetch_databases
import json

# load configuration
conf = Config.get_instance()

# init connection pool
conn = SmplConnPool.get_instance()

# instantiate the scheduler
scheduler = BackgroundScheduler()

app = Flask(__name__)
# Add standard CORS headers in order to access the app
CORS(app)

# stores all grabbers currently in the system
grabbers = []


@app.route('/', methods=['GET'])
def index():
    return "Welcome to the RSS Grabber ..."


@app.route('/grabber', methods=['GET'])
def get_all_grabbers():
    return json.dumps([grabber.to_json() for grabber in grabbers])


@app.route('/grabber', methods=['POST'])
def add_grabber():
    jsn = request.get_json()

    # TODO: Validate the incoming data
    grabbers.append(Grabber(jsn['name'], jsn['feed']))
    # TODO: Save the grabber to the database

    return '', 201


@app.route('/grabber/<id>', methods=['DELETE'])
def delete_grabber():
    raise NotImplemented('Delete the specified grabber from the database')


def main():
    scheduler.start()

    grabber1 = Grabber('Handelsblatt', 'http://newsfeed.zeit.de/index')

    # TODO: During startup load all grabbers from the database and place them into mem (grabbers)
    # and schedule them for execution

    # schedule grabber1 to be executed every 10 seconds
    # job = scheduler.add_job(grabber1.run, 'interval', seconds=10)

    app.run()


if __name__ == '__main__':
    main()
