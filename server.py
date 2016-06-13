import logging
from bson import ObjectId
from flask import Flask, request
from config import Config
from smpl_conn_pool import SmplConnPool
from models.grabber import Grabber
from flask.ext.cors import CORS
from auth import auth_endpoints
from annotations import login_required
from apscheduler.schedulers.background import BackgroundScheduler
from json import dumps

# load configuration
conf = Config.get_instance()

# configure logger
logging.basicConfig(level=logging.DEBUG)

# init connection pool
conn = SmplConnPool.get_instance()

# instantiate the scheduler
scheduler = BackgroundScheduler()

app = Flask(__name__)
# Add standard CORS headers in order to access the app
CORS(app)

# a mapping from a specific grabber to its corresponding job
grabber_to_job = {}

# register blueprints
app.register_blueprint(auth_endpoints)


@app.route('/', methods=['GET'])
def index():
    return "Welcome to the RSS Grabber ..."


@app.route('/grabber', methods=['GET'])
@login_required
def get_all_grabbers():
    connection = SmplConnPool.get_instance().get_connection()
    grabber_collection = connection[
        Grabber.cfg['database']['db']]['grabbers']

    return dumps([grabber.encode() for grabber in [Grabber.decode(doc) for doc in grabber_collection.find()]])


@app.route('/grabber', methods=['POST'])
@login_required
def add_grabber():
    jsn = request.get_json()
    # TODO: Validate the incoming json data
    grabber = _add_grabber(jsn)
    print('{}'.format(grabber.encode()))
    return 'Hallali!', 201


@app.route('/grabber', methods=['PUT'])
@login_required
def update_grabber():
    jsn = request.get_json()
    connection = SmplConnPool.get_instance().get_connection()
    grabber_collection = connection[
        Grabber.cfg['database']['db']]['grabbers']

    grabber = Grabber.decode(jsn)
    _update_job(grabber)

    update = grabber.encode()
    del update['_id']

    grabber_collection.find_one_and_replace(
        {"_id": grabber._id},
        update
    )
    return 'Succesfully updated grabber', 201


def _add_grabber(doc):
    """
    Create and save grabber from a json document / dict

    :param doc: the document which should be used to create the grabber
    :return: the newly created grabber
    """
    grabber = Grabber.decode(doc)
    grabber.save()
    _add_job_for_grabber(grabber)
    return grabber


def _add_job_for_grabber(grabber):
    job = scheduler.add_job(grabber.run, 'interval', seconds=grabber.interval)
    grabber_to_job[grabber._id] = job


def _update_job(grabber):
    assert grabber._id in grabber_to_job
    if grabber._id in grabber_to_job:
        job = grabber_to_job[grabber._id]
        job.remove()
    _add_job_for_grabber(grabber)


@app.route('/grabber/<_id>/start', methods=['POST'])
@login_required
def start_grabber(_id):
    object_id = ObjectId(_id)
    if object_id in grabber_to_job:
        job = grabber_to_job[object_id]
        job.resume()
        return 'Succesfully started grabber', 200
    else:
        return 'Invalid grabber id', 404


@app.route('/grabber/<_id>/stop', methods=['POST'])
@login_required
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


@app.route('/grabber', methods=['DELETE'])
@login_required
def delete_grabber():
    """
    Delete grabber from system
    :param id: the id of the grabber that should be deleted
    :return: http code 200 if grabber could be deleted, else 404
    """
    grabber = Grabber.decode(request.get_json())
    if grabber._id in grabber_to_job:
        # delete associated job
        job = grabber_to_job[grabber._id]
        job.remove()
        del grabber_to_job[grabber._id]

        # delete grabber from database
        connection = SmplConnPool.get_instance().get_connection()
        grabber_collection = connection[Grabber.cfg['database']['db']]['grabbers']
        grabber_collection.remove({'_id': grabber._id})

        return 'Grabber deleted', 200
    else:
        return 'Invalid grabber id', 404


def main():
    scheduler.start()
    restart_grabbers_from_db()

    # Only for testing purposes (if not used any longer ... remove)
    # grabber = Grabber.decode({
    #     'id': ObjectId("56ca2e9399b19050bf6d6fc5"),
    #     'feed': 'http://www.handelsblatt.com/contentexport/feed/wirtschaft',
    #     'interval': 10,
    #     'css_selector': 'div.vhb-article-pagination-list a',
    #     'name': 'Handelsblatt Wirtschafts-Schlagzeilen'
    # })
    #
    # job = scheduler.add_job(grabber.run, 'interval',
    #                         seconds=grabber.interval)
    #
    # grabber_to_job[grabber._id] = job

    app.run()


def restart_grabbers_from_db():
    connection = SmplConnPool.get_instance().get_connection()
    grabber_collection = connection[Grabber.cfg['database']['db']]['grabbers']
    for doc in grabber_collection.find():
        grabber = Grabber.decode(doc)
        job = scheduler.add_job(grabber.run, 'interval',
                                seconds=grabber.interval)
        grabber_to_job[grabber._id] = job


if __name__ == '__main__':
    main()
