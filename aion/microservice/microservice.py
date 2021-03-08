# coding: utf-8

# Copyright (c) 2019-2020 Latona. All rights reserved.

from aion.logger import initialize_logger, lprint_exception, lprint
from aion.kanban import KanbanConnection, KanbanConnectionAsync, KanbanServerNotFoundError
from logging import DEBUG
import os
from retry import retry

NORMAL_CONNECTION_MODE = "normal"
DIRECT_CONNECTION_MODE = "direct"


class Options:
    conn: KanbanConnection
    ms_number: int
    docker: bool

    def __init__(self, conn: KanbanConnection, ms_number: int, is_docker: bool):
        self.conn = conn
        self.ms_number = ms_number
        self.docker = is_docker

    def get_conn(self) -> KanbanConnection:
        return self.conn

    def get_number(self) -> int:
        return self.ms_number

    def is_docker(self) -> bool:
        return self.docker


def main_decorator(component, level=DEBUG, async_kanban=False):
    initialize_logger(component, level)
  
    def _main_decorator(func):
        
        @retry(exceptions=Exception, tries=5, delay=1, backoff=2, max_delay=4)  
        def _wrapper(*args, **kwargs):
            conn = None
            try:
                addr = os.environ.get("KANBAN_ADDR")

                connection_mode = os.environ.get("CONNECTION_MODE", NORMAL_CONNECTION_MODE)
                if connection_mode == DIRECT_CONNECTION_MODE:
                    addr = "aion-statuskanban:10000"

                if async_kanban:
                    conn = KanbanConnectionAsync(addr) if addr else KanbanConnectionAsync()
                else:
                    conn = KanbanConnection(addr) if addr else KanbanConnection()

                n = os.environ.get("MS_NUMBER")
                n = int(n) if n else 1

                docker = os.environ.get("IS_DOCKER")
                is_docker = True if docker else False

                options = Options(
                    conn=conn,
                    ms_number=n,
                    is_docker=is_docker,
                )
                func(*args, **kwargs, opt=options)
            except Exception as e:
                lprint_exception(e)
                raise
            finally:
                if conn is not None:
                    conn.close()
            return
        return _wrapper
    return _main_decorator
