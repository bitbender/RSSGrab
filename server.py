import logging
import feedparser
from flask import Flask, request
from config import Config
from smpl_conn_pool import SmplConnPool
from models.grabber import Grabber
from engine import Engine
from flask.ext.cors import CORS
from auth import auth_endpoints
from annotations import login_required
from bson import json_util
from json import dumps, loads


# load configuration
conf = Config.get_instance()

# configure logger
logging.basicConfig(level=logging.DEBUG)

# init connection pool
conn = SmplConnPool.get_instance()

# create the engine
engine = Engine()

app = Flask(__name__)
# Add standard CORS headers in order to access the app
CORS(app)

# register flask blueprints
app.register_blueprint(auth_endpoints)


@app.route('/', methods=['GET'])
def index():
    return "Running ..."


@app.route('/feed', methods=['POST'])
@login_required
def preview_feed():
    """
    This endpoint is responsible for fetching the feed url
    and sending the content for display purposes back to the
    client.
    """
    jsn = request.get_json()
    data = feedparser.parse(jsn['url'])

    return dumps([(entry['title'], entry['guid']) for entry in data['entries']], default=json_util.default)


@app.route('/grabber', methods=['GET'])
@login_required
def get_all_grabbers():
    connection = SmplConnPool.get_instance().get_connection()
    grabber_collection = connection[
        Grabber.cfg['database']['db']]['grabbers']

    return dumps([grabber.encode() for grabber in [Grabber.new(doc) for doc in grabber_collection.find()]], default=json_util.default)


@app.route('/grabber', methods=['POST'])
@login_required
def add_grabber():
    jsn = loads(request.data.decode('utf-8'), object_hook=json_util.object_hook)
    # TODO: Validate the incoming json data

    grabber = Grabber.new(jsn)
    grabber.save()
    engine.create_job(grabber)

    print('{}'.format(grabber.encode()))
    return 'Success', 201


@app.route('/grabber', methods=['PUT'])
@login_required
def update_grabber():
    jsn = loads(request.data.decode('utf-8'), object_hook=json_util.object_hook)

    connection = SmplConnPool.get_instance().get_connection()
    grabber_collection = connection[
        Grabber.cfg['database']['db']]['grabbers']

    grabber = Grabber.new(jsn)
    grabber.save()
    engine.reschedule_job(grabber)

    return 'Succesfully updated grabber', 201


@app.route('/grabber/<_id>/start', methods=['POST'])
@login_required
def start_grabber(_id):
    if engine.exists_job(_id):
        engine.start_job_by_id(_id)
        return 'Succesfully started the grabber', 200
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
    if engine.exists_job(_id):
        engine.pause_job_by_id(_id)
        return 'Succesfully stopped the grabber', 200
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
    jsn = loads(request.data.decode('utf-8'), object_hook=json_util.object_hook)
    grabber = Grabber.new(jsn)

    # delete associated job
    engine.delete_job(grabber)

    # delete grabber from database
    connection = SmplConnPool.get_instance().get_connection()
    grabber_collection = connection[Grabber.cfg['database']['db']]['grabbers']

    grabber_collection.remove({'_id': grabber._id})

    return 'Grabber deleted', 200



def main():
    engine.start()
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
        engine.create_job(Grabber.new(doc))


if __name__ == '__main__':
    main()
