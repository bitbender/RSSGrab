import logging
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config
from smpl_conn_pool import SmplConnPool
from models.grabber import Grabber
"""
This class represents the execution engine of the RSS Grabber.
It is responsible for creating, managing and running the
created grabbers.
"""

logger = logging.getLogger('engine')


class Engine:

    def __init__(self, max_threads=20, max_processes=5):
        self.scheduler = BackgroundScheduler({
            'apscheduler.executors.default': {
                'class': 'apscheduler.executors.pool:ThreadPoolExecutor',
                'max_workers': max_threads
            },
            'apscheduler.executors.processpool': {
                'type': 'processpool',
                'max_workers': max_processes
            },
            'apscheduler.job_defaults.max_instances': '1',
            'apscheduler.timezone': 'UTC',
        })
        # load configuration
        self.cfg = Config.get_instance()

        # get grabber collection
        connection = SmplConnPool.get_instance().get_connection()
        self.grb_coll = connection[self.cfg['database']['db']]['grabbers']

        # get stats collection
        connection = SmplConnPool.get_instance().get_connection()
        self.stats_coll = connection[self.cfg['database']['db']]['stats']

        self.grabbers = {str(doc['_id']): Grabber.new(doc) for doc in self.grb_coll.find()}

    def add_grabber(self, grabber):
        self.grabbers[str(grabber._id)] = grabber
        grabber.save()
        logger.info('Registered grabber {} with the engine.'.format(grabber))

    def update_grabber(self, grabber):
        # update in memory
        self.grabbers[str(grabber._id)] = grabber

        # save to db
        grabber.save()

        # update scheduled job
        if self._exists_job(str(grabber._id)):
            self._reschedule_job(grabber)

        logger.info('Updated grabber to {}'.format(grabber))
        return grabber

    def get_grabber(self, grb_id):
        try:
            return self.grabbers[grb_id]
        except KeyError as e:
            return None

    def get_all(self):
        return self.grabbers.values()

    def get_stats(self, grabber):
        result = list(self.stats_coll.find({'grb_id': grabber._id}))
        logger.info('Retrieved stats for grabber {}'.format(grabber))

        return result


    def delete_grabber(self, grabber):
        if self.grabbers[str(grabber._id)]:
            grabber = self.grabbers[str(grabber._id)]

            # delete job
            if self._exists_job(str(grabber._id)):
                self._delete_job(grabber)

            # delete from db
            grabber.delete()

            # delete from memory
            del self.grabbers[str(grabber._id)]

            logger.info('Deleted grabber {}'.format(grabber))

    def start_grabbers(self):
        """
        Start all registered grabbers.
        """
        for grabber in self.grabbers.values():
            self.start_grabber(grabber)
        return self.grabbers.values()

    def suspend_grabbers(self):
        """
        Stop all registered grabbers.
        """
        for grabber in self.grabbers.values():
            self.pause_grabber(grabber)
        return self.grabbers.values()

    def start_grabber(self, grabber):
        if self.grabbers[str(grabber._id)]:
            if self._exists_job(str(grabber._id)):
                self._resume_job_by_id(str(grabber._id))
            else:
                self._create_job(grabber)
            logger.info('Scheduled grabber {} for execution.'.format(grabber))
        return grabber

    def pause_grabber(self, grabber):
        if self.grabbers[str(grabber._id)]:
            self._pause_job_by_id(str(grabber._id))
            logger.info('Paused grabber {}'.format(grabber))
        return grabber

    def _create_job(self, grabber):
        """
        Schedule a job that executes the passed in grabber
        in certain intervals.
        :param grabber: the grabber that should be scheduled for execution
        """
        self.scheduler.add_job(grabber.run, 'interval', seconds=grabber.interval, id=str(grabber._id))
        grabber.status = 'scheduled'

    def _reschedule_job(self, grabber):
        if self.scheduler.get_job(str(grabber._id)):
            # remove the old job
            self._delete_job(grabber)
            # add the new one
            self.scheduler.add_job(grabber.run, 'interval', seconds=grabber.interval,  id=str(grabber._id))
            grabber.status = 'scheduled'

    def _pause_job_by_id(self, grb_id):
        """
        Pause the job that executes the passed in grabber.
        :param grabber: the grabber that should be paused
        """
        if self.scheduler.get_job(grb_id):
            self.scheduler.pause_job(grb_id)
            self.grabbers[grb_id].status = 'suspended'

    def _resume_job_by_id(self, grb_id):
        """
        Resume the job that executes the passed in grabber.
        :param grb_id: the id of the grabber (string) that should be resumed
        """
        if self.scheduler.get_job(grb_id):
            self.scheduler.resume_job(grb_id)
            self.grabbers[grb_id].status = 'scheduled'

    def _delete_job(self, grabber):
        """
        Remove the scheduled job for a grabber
        :param grabber: the grabber for which the associated job should be removed
        """
        if self.scheduler.get_job(str(grabber._id)):
            self.scheduler.remove_job(str(grabber._id))

    def _exists_job(self, grb_id):
        if self.scheduler.get_job(grb_id):
            return True
        else:
            return False

    def start(self):
        """
        Start the scheduler
        """
        self.scheduler.start()

    def pause(self):
        """
        Pause the scheduler from processing jobs
        """
        self.scheduler.pause()

    def resume(self):
        """
        Resume the scheduler the scheduler for processing jobs
        """
        self.scheduler.resume()

    def shutdown(self):
        """
        Shutdown the scheduler
        """
        self.scheduler.shutdown()
