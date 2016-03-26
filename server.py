from bson import ObjectId
from flask import Flask, request
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
# TODO: This needs to be a dictionary for quick removal of grabbers
grabbers = []

# a mapping from a specific grabber to its corresponding job
grabber_to_job = {}


@app.route('/', methods=['GET'])
def index():
    return "Welcome to the RSS Grabber ..."


@app.route('/grabber', methods=['GET'])
def get_all_grabbers():
    return json.dumps([grabber.to_json() for grabber in grabbers])


@app.route('/grabber', methods=['POST'])
def add_grabber():
    # TODO: Validate the incoming data
    jsn = request.get_json()
    database_id = _add_grabber(jsn['name'], jsn['feed'], jsn['interval'])
    return '{}'.format(database_id), 201


@app.route('/grabber/<_id>', methods=['PUT'])
def update_grabber(_id):
    jsn = request.get_json()
    connection = SmplConnPool.get_instance().get_connection()
    grabber_collection = connection[
        Grabber.cfg['database']['db']]['grabbers']
    grabber = Grabber(jsn['name'], jsn['feed'], jsn['interval'], _id)
    _update_job(grabber)
    grabber_collection.find_one_and_replace(
        {"_id": ObjectId(_id)},
        jsn
    )
    return 'Succesfully updated grabber', 201


def _add_grabber(name, feed, interval):
    new_grabber = Grabber(name, feed, interval)
    database_id = new_grabber.save()
    _add_job_for_grabber(new_grabber)
    grabbers.append(new_grabber)
    return database_id


def _add_job_for_grabber(grabber):
    job = scheduler.add_job(grabber.run, 'interval', seconds=10)
    grabber_to_job[grabber._id] = job


def _update_job(grabber):
    object_id = ObjectId(grabber._id)
    assert object_id in grabber_to_job
    if object_id in grabber_to_job:
        job = grabber_to_job[object_id]
        job.remove()
    _add_job_for_grabber(grabber)


@app.route('/grabber/<_id>/start', methods=['POST'])
def start_grabber(_id):
    object_id = ObjectId(_id)
    if object_id in grabber_to_job:
        job = grabber_to_job[object_id]
        job.resume()
        return 'Succesfully started grabber', 200
    else:
        return 'Invalid grabber id', 404


@app.route('/grabber/<_id>/stop', methods=['POST'])
def stop_grabber(_id):
    """
    Stop the grabber with the specified id
    :param _id: the id of the grabber that should be stopped
    :return: http code 200 if grabber could be deleted, else 404
    """
    object_id = ObjectId(_id)
    if object_id in grabber_to_job:
        job = grabber_to_job[object_id]
        job.pause()
        return 'Succesfully stopped grabber', 200
    else:
        return 'Invalid grabber id', 404


@app.route('/grabber/<id>', methods=['DELETE'])
def delete_grabber(id):
    """
    Delete grabber from system
    :param id: the id of the grabber that should be deleted
    :return: http code 200 if grabber could be deleted, else 404
    """
    object_id = ObjectId(id)
    if object_id in grabber_to_job:

        # delete associated job
        job = grabber_to_job[object_id]
        job.remove()
        del grabber_to_job[object_id]

        # FIXME: stupid an inefficient but using the grabbers collection the only way
        # delete grabber from grabbers collection
        for idx, grabber in enumerate(grabbers):
            if str(grabber._id) == id:
                del grabbers[idx]

        # delete grabber from database
        connection = SmplConnPool.get_instance().get_connection()
        grabber_collection = connection[Grabber.cfg['database']['db']]['grabbers']
        grabber_collection.remove({'_id': ObjectId(id)})

        return 'Succesfully stopped grabber', 200
    else:
        return 'Invalid grabber id', 404


def main():
    scheduler.start()
    fetch_grabbers_from_db()
    app.run()


def fetch_grabbers_from_db():
    connection = SmplConnPool.get_instance().get_connection()
    grabber_collection = connection[Grabber.cfg['database']['db']]['grabbers']
    for grabber in grabber_collection.find():
        recreated = Grabber(grabber['name'], grabber['feed'], grabber['interval'],
                            grabber['_id'])
        grabbers.append(recreated)
        job = scheduler.add_job(recreated.run, 'interval',
                                seconds=grabber['interval'])
        grabber_to_job[grabber['_id']] = job


if __name__ == '__main__':
    main()
