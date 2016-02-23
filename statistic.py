from config import Config
from smpl_conn_pool import SmplConnPool


class Statistic:
    cfg = Config.get_instance()

    def __init__(self, grabber_id):
        self.grabber_id = grabber_id
        if self._exists_statistic(grabber_id):
            print("Created statistic from existing database statistic")
            saved_statistic = self._get_statistic_for_grabber_id(grabber_id)
            self.downloaded_articles = saved_statistic['downloaded_articles']
            self.runs_since_startup = saved_statistic['runs_since_startup']
        else:
            print("Create new statistic")
            self.downloaded_articles = 0
            self.runs_since_startup = 0

    def _get_statistic_for_grabber_id(self, grabber_id):
        connection = SmplConnPool.get_instance().get_connection()
        statistics = connection[Statistic.cfg['database']['db']]['statistics']
        return statistics.find_one({"grabber_id": self.grabber_id})

    def _exists_statistic(self, grabber_id):
        connection = SmplConnPool.get_instance().get_connection()
        statistics = connection[Statistic.cfg['database']['db']]['statistics']
        return statistics.count() == 1

    def save(self):
        connection = SmplConnPool.get_instance().get_connection()
        statistics = connection[Statistic.cfg['database']['db']]['statistics']
        saved_statistic = statistics.find({"grabber_id": self.grabber_id})
        # Insert only if there is no statistic for this grabber
        if saved_statistic.count() == 0:
            print("Inserted new statistic")
            self.grabber_id = statistics.insert_one(self.__dict__).inserted_id
        else:
            self.grabber_id = saved_statistic[0]['grabber_id']
        return self._id

    def increase_runs(self):
        connection = SmplConnPool.get_instance().get_connection()
        statistics = connection[Statistic.cfg['database']['db']]['statistics']
        statistics.update_one({
            'grabber_id': self.grabber_id
        }, {
            '$inc': {
                'runs_since_startup': 1
            }
        }, upsert=False)

    def reset_run(self):
        print("Reset run to 0")
        connection = SmplConnPool.get_instance().get_connection()
        statistics = connection[Statistic.cfg['database']['db']]['statistics']
        statistics.update_one({
            'grabber_id': self.grabber_id
        }, {
            '$set': {
                'downloaded_articles': 0
            }
        }, upsert=False)

    def increase_downloaded_articles(self):
        connection = SmplConnPool.get_instance().get_connection()
        statistics = connection[Statistic.cfg['database']['db']]['statistics']
        statistics.update_one({
            'grabber_id': self.grabber_id
        }, {
            '$inc': {
                'downloaded_articles': 1
            }
        }, upsert=False)
