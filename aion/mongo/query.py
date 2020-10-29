# coding: utf-8

# Copyright (c) 2019-2020 Latona. All rights reserved.

import os
import traceback

from pymongo import MongoClient
from aion.logger import lprint


class BaseMongoAccess():
    def __init__(self, db_name):
        self._db_name = db_name

    def __enter__(self):
        self.client = MongoClient(
            port=int(os.environ.get('MONGO_SERVICE_PORT')),
            host=os.environ.get('MONGO_SERVICE_HOST'))
        self._db = self.client[self._db_name]
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            for message in traceback.format_exception(exc_type, exc_value, tb):
                lprint(message.rstrip('\n'))
        if self.client:
            self.client.close()
        return True

    def create_index(self, collection, key, index_type):
        collect = self._db.get_collection(collection)
        if collect is None:
            return False
        index = [(key, index_type)]
        collect.create_index(index)
        return True

    def find(self, collection, projection=None, filter=None, sort=None):
        collect = self._db.get_collection(collection)
        if collect is None:
            return False
        return collect.find(projection=projection, filter=filter, sort=sort)

    def insert_many(self, collection, data):
        if not isinstance(data, list):
            return False
        collect = self._db.get_collection(collection)
        if collect is None:
            return False
        collect.insert_many(data)
        return True

    def insert_one(self, collection, data):
        if not isinstance(data, dict):
            return False
        collect = self._db.get_collection(collection)
        if collect is None:
            return False
        collect.insert_one(data)
        return True

    def delete_one(self, collection, filter):
        collect = self._db.get_collection(collection)
        if collect is None:
            return False
        result = collect.delete_one(filter)
        deleted_count = result.deleted_count
        return deleted_count

    def delete_many(self, collection, filter):
        collect = self._db.get_collection(collection)
        if collect is None:
            return False
        result = collect.delete_many(filter)
        deleted_count = result.deleted_count
        return deleted_count

    def drop(self, collection):
        collect = self._db.get_collection(collection)
        if collect is None:
            return False
        collect.drop()
        return

    def is_connect(self):
        return bool(self.cursor)
