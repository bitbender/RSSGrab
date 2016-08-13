import logging
import feedparser
from flask import Flask, request
from config import Config
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
logger = logging.getLogger('server')

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
    return dumps([grabber.encode() for grabber in engine.get_all()], default=json_util.default)


@app.route('/grabber', methods=['POST'])
@login_required
def add_grabber():
    jsn = loads(request.data.decode('utf-8'), object_hook=json_util.object_hook)
    # TODO: Validate the incoming json data
    engine.add_grabber(Grabber.new(jsn))
    return 'Success', 201


@app.route('/grabber', methods=['PUT'])
@login_required
def update_grabber():
    jsn = loads(request.data.decode('utf-8'), object_hook=json_util.object_hook)

    engine.update_grabber(Grabber.new(jsn))
    return 'Succesfully updated grabber', 201


@app.route('/grabber/start', methods=['POST'])
@login_required
def start__all_grabbers():
    engine.start_grabbers()
    return 'Succesfully started all grabbers', 200


@app.route('/grabber/stop', methods=['POST'])
@login_required
def suspend__all_grabbers():
    engine.suspend_grabbers()
    return 'Succesfully suspended all grabbers', 200


@app.route('/grabber/<_id>/start', methods=['POST'])
@login_required
def start_grabber(_id):
    engine.start_grabber(engine.get_grabber(_id))
    return 'Succesfully started the grabber', 200


@app.route('/grabber/<_id>/stop', methods=['POST'])
@login_required
def suspend_grabber(_id):
    """
    Stop the grabber with the specified id
    :param _id: the id of the grabber that should be stopped
    :return: http code 200 if grabber could be deleted, else 404
    """
    engine.pause_grabber(engine.get_grabber(_id))
    return 'Succesfully stopped the grabber', 200


@app.route('/grabber', methods=['DELETE'])
@login_required
def delete_grabber():
    """
    Delete grabber from system
    :param id: the id of the grabber that should be deleted
    :return: http code 200 if grabber could be deleted, else 404
    """
    jsn = loads(request.data.decode('utf-8'), object_hook=json_util.object_hook)

    engine.delete_grabber(Grabber.new(jsn))
    return 'Grabber deleted', 200


def main():
    engine.start()
    #restart_grabbers_from_db()

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


if __name__ == '__main__':
    main()
