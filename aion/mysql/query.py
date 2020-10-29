# coding: utf-8

# Copyright (c) 2019-2020 Latona. All rights reserved.

import os
import traceback

import MySQLdb
from aion.logger import lprint, lprint_exception


class BaseMysqlAccess():
    cursor = None
    default_mysql_host = "mysql"
    default_mysql_port = "3306"
    default_mysql_user = "latona"

    def __init__(self, db_name):
        self._db_name = db_name

    def __enter__(self):
        try:
            self.connection = MySQLdb.connect(
                host=os.environ.get('MY_MYSQL_HOST', self.default_mysql_host),
                port=int(os.environ.get('MY_MYSQL_PORT', self.default_mysql_port)),
                user=os.environ.get('MYSQL_USER', self.default_mysql_user),
                passwd=os.environ.get('MYSQL_PASSWORD'),
                db=self._db_name,
                charset='utf8')
            self.cursor = self.connection.cursor(MySQLdb.cursors.DictCursor)
        except MySQLdb.Error as e:
            lprint("cant connect mysql")
            lprint_exception(e)
            self.cursor = None
            raise e
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            for message in traceback.format_exception(exc_type, exc_value, tb):
                lprint(message.rstrip('\n'))
        if self.cursor:
            self.cursor.close()
            self.connection.close()
        return True

    def get_query(self, sql, args=None):
        if not self.cursor:
            return None
        self.cursor.execute(sql, args)
        return self.cursor.fetchone()

    def get_query_list(self, size, sql, args=None):
        if not self.cursor:
            return None
        self.cursor.execute(sql, args)
        return self.cursor.fetchmany(size)

    def set_query(self, sql, args=None):
        if not self.cursor:
            return False
        self.cursor.execute(sql, args)
        return True

    def commit_query(self):
        self.connection.commit()

    def is_connect(self):
        return bool(self.cursor)
