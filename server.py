from flask import Flask, request, jsonify
from config import Config
from smpl_conn_pool import SmplConnPool
from models.grabber import Grabber
from flask.ext.cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
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
    # TODO: Validate the incoming date
    jsn = request.get_json()

    _add_grabber(jsn['name'], jsn['feed'], json['interval'])
    return '', 201


def _add_grabber(name, feed, interval):
    new_grabber = Grabber(name, feed, interval)
    database_id = new_grabber.save()
    scheduler.add_job(new_grabber.run, 'interval', seconds=10)
    return database_id

@app.route('/grabber/<id>', methods=['DELETE'])
def delete_grabber():
    raise NotImplemented('Delete the specified grabber from the database')


def main():
    scheduler.start()

    _add_grabber('Handelsblatt', 'http://newsfeed.zeit.de/index', 10)
    # TODO: During startup load all grabbers from the database and place them into mem (grabbers)
    # and schedule them for execution

    app.run()


def fetch_grabbers_from_db():
    connection = SmplConnPool.get_instance().get_connection()
    grabber_collection = connection[Grabber.cfg['database']['db']]['grabbers']

if __name__ == '__main__':
    main()
