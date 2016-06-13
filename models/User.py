from smpl_conn_pool import SmplConnPool
from bson import ObjectId
from config import Config
from copy import copy
import logging
import bcrypt


class User(object):

    def __init__(self, email, password=None, name=None, _id=None):

        if _id:
            self._id = _id
        else:
            self._id = ObjectId()

        self.name = name
        self.email = email.lower()
        self.password = password

    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    def validate_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), self.password) == self.password

    def save(self):
        """
        Save the grabber to a mongodb database.

        :return: the document id of the grabber in the database.
        """
        connection = SmplConnPool.get_instance().get_connection()
        cfg = Config.get_instance()

        users_collection = connection[cfg['database']['db']]['users']

        user = users_collection.find_one({'email': self.email})
        if user:
            temp = copy(self.__dict__)
            del temp['_id']
            users_collection.replace_one(user, temp)
            logging.info('Updated user: {0}'.format(self.__repr__()))
        else:
            user_id = users_collection.insert_one(self.__dict__).inserted_id
            logging.info('Inserted new user: {0}'.format(self.__repr__()))

    @classmethod
    def load(cls, email):
        connection = SmplConnPool.get_instance().get_connection()
        cfg = Config.get_instance()

        users_collection = connection[cfg['database']['db']]['users']
        user = users_collection.find_one({'email': email})

        if user:
            return User(name=user['name'], email=user['email'], password=user['password'], _id=user['_id'])
        else:
            return None

    def __repr__(self):
        return '{0}:[{1}, {2}]'.format(self._id, self.name, self.email)

