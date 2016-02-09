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

tasks = []


def test():
    print("Boom")


@app.route('/', methods=['GET'])
def index():
    return "Welcome the RSS Grabber ..."


def get_grabbers():
    return "Get all the grabbers currently in the system"


if __name__ == '__main__':
    scheduler.start()

    grabber1 = Grabber('Handelsblatt', 'http://newsfeed.zeit.de/index')
    # schedule grabber1 to be executed every 10 seconds
    job = scheduler.add_job(grabber1.run, 'interval', seconds=10)
    app.run()
