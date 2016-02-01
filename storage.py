from pymongo import MongoClient

client = MongoClient('localhost', 27017)


def fetch_databases():
    return client.database_names()
