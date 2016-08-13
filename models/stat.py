import json
import logging
from bson import json_util, ObjectId
from config import Config
from smpl_conn_pool import SmplConnPool

logger = logging.getLogger('statistics')


class Statistic:
    cfg = Config.get_instance()

    def __init__(self, grb_id, _id=None):

        if type(_id) == str:
            self._id = ObjectId(_id)

        elif type(_id) == ObjectId:
            self._id = _id

        else:
            self._id = ObjectId()

        self.grb_id = grb_id
        # newly discovered urls
        self.new = []
        # urls that got updated
        self.updated = []
        # urls to payed pages
        self.payed = []
        self.total_pages = 0
        self.start_time = None
        self.end_time = None

    def save(self):
        """
        Save the grabber to a mongodb database.

        :return: the document id of the grabber in the database.
        """
        connection = SmplConnPool.get_instance().get_connection()
        stats_collection = connection[Statistic.cfg['database']['db']]['stats']

        result = stats_collection.update_one(
            {'_id': self._id},
            {'$set': self.__dict__},
            True
        )
        logger.info('{}: Saved stats for current grabber run'.format(self.grb_id))

        return result.upserted_id

    def toDoc(self):
        return json.dumps(self.__dict__, default=json_util.default)
