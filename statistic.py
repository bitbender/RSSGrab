from config import Config
from smpl_conn_pool import SmplConnPool


class Statistic:
    cfg = Config.get_instance()

    def __init__(self, grabber_id):
        self.runs_since_startup = 0
        self.grabber_id = grabber_id
        self.downloaded_articels = 0

    def save(self):
        connection = SmplConnPool.get_instance().get_connection()
        statistics = connection[Statistic.cfg['database']['db']]['statistics']
        self._id = statistics.insert_one(self.__dict__).inserted_id
        return self._id

    def increase_runs(self):
        connection = SmplConnPool.get_instance().get_connection()
        statistics = connection[Statistic.cfg['database']['db']]['statistics']
        grabber_statistic = statistics.find({'id': self._id})
        grabber_statistic['runs_since_startup'] += 1
        statistics.replace_one({'id': self['_id']}, grabber_statistic)

    def reset_run(self):
        connection = SmplConnPool.get_instance().get_connection()
        statistics = connection[Statistic.cfg['database']['db']]['statistics']
        grabber_statistic = statistics.find({'id': self._id})
        grabber_statistic['runs_since_startup'] = 0
        statistics.replace_one({'id': self['_id']}, grabber_statistic)

    def increase_downloaded_articles(self):
        connection = SmplConnPool.get_instance().get_connection()
        statistics = connection[Statistic.cfg['database']['db']]['statistics']
        grabber_statistic = statistics.find({'id': self._id})
        grabber_statistic['downloaded_articles'] += 1
        statistics.replace_one({'id': self._id}, grabber_statistic)
