from pymongo import MongoClient
from config import Config
import random

"""
This class implements a very simple MongoDB connection pool
which should be used to get a connection to the MongoDB throughout
the entire application

Usage:
    pool = SmplConnPool.get_instance()
    connection = pool.get_connection()

    collection = connection.database.collection

The get_connection() method of SmplConnPool returns a normal
connection instance from pymongo.
"""


class SmplConnPool():
    _instance = None
    _pool = list()
    _cfg = Config.get_instance()

    def __init__(self):
        """
        This is the constructor of the SmplConnPool

        :param address: the address where the MongoDB is running
        :param port: the port the MongoDB is listening on
        :param size: the pool size
        """
        if SmplConnPool._instance is not None:
            raise NotImplemented(
                "This is a singleton class. Use the get_instance() method")

        self.address = SmplConnPool._cfg['database']['host']
        self.port = SmplConnPool._cfg['database']['port']

        for i in range(SmplConnPool._cfg['database']['poolsize']):
            SmplConnPool._pool.append(MongoClient(self.address, self.port))

    @staticmethod
    def get_instance():
        """
        This method returns an instance of the SmplConnPool class.
        :return: an instance of the SmplConnPool class.
        """
        if SmplConnPool._instance is None:
            SmplConnPool._instance = SmplConnPool()

        return SmplConnPool._instance

    def get_connection(self):
        """
        This method returns a random connection drawn
        from the available connections pool.
        :return: a random connection.
        """
        if SmplConnPool._pool:
            return random.choice(SmplConnPool._pool)
