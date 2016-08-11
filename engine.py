from apscheduler.schedulers.background import BackgroundScheduler

"""
This class represents the execution engine of the RSS Grabber.
It is responsible for creating, managing and running the
created grabbers.
"""


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

    def create_job(self, grabber):
        """
        Schedule a job that executes the passed in grabber
        in certain intervals.
        :param grabber: the grabber that should be scheduled for execution
        """
        self.scheduler.add_job(grabber.run, 'interval', seconds=grabber.interval, id=str(grabber._id)).pause()

    def reschedule_job(self, grabber):
        if self.scheduler.get_job(str(grabber._id)):
            # remove the old job
            self.delete_job(grabber)
            # add the new one
            self.scheduler.add_job(grabber.run, 'interval', seconds=grabber.interval,  id=str(grabber._id))

    def start_job_by_id(self, grb_id):
        """
        Start the job that executes the passed in grabber.
        :param grabber: the grabber that should be resumed
        """
        if self.scheduler.get_job(str(grb_id)):
            self.scheduler.resume_job(str(grb_id))

    def pause_job_by_id(self, grb_id):
        """
        Pause the job that executes the passed in grabber.
        :param grabber: the grabber that should be paused
        """
        if self.scheduler.get_job(grb_id):
            self.scheduler.pause_job(str(grb_id))

    def resume_job_by_id(self, grb_id):
        """
        Resume the job that executes the passed in grabber.
        :param grabber: the grabber that should be resumed
        """
        if self.scheduler.get_job(grb_id):
            self.scheduler.resume_job(grb_id)

    def delete_job(self, grabber):
        """
        Remove the scheduled job for a grabber
        :param grabber: the grabber for which the associated job should be removed
        """
        if self.scheduler.get_job(str(grabber._id)):
            self.scheduler.remove_job(str(grabber._id))

    def exists_job(self, grb_id):
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
