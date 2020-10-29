# coding: utf-8

# Copyright (c) 2019-2020 Latona. All rights reserved.

import pytest
import grpc
from concurrent import futures
from queue import Queue
from datetime import datetime

from aion.kanban import KanbanConnection, unpack_any_message, pack_any_message
from aion.kanban.api import status_pb2_grpc as rpc
from aion.kanban.api import status_pb2 as msg
from aion.logger import initialize_logger, function_log, lprint
from google.protobuf.struct_pb2 import Struct


initialize_logger("kanban-test")


class GrpcServer(rpc.KanbanServicer):
    def __init__(self, queue):
        self.queue = queue

    @function_log
    def MicroserviceConn(self, request_iterator, context):
        """最新のCカンバンを取得する
        """
        for new_msg in request_iterator:
            self.queue.put(new_msg)
            if new_msg.messageType == msg.START_SERVICE:
                res = self.start_service(new_msg.message)
            elif new_msg.messageType == msg.OUTPUT_AFTER_KANBAN:
                res = self.output_kanban(new_msg.message)
            else:
                res = msg.Response(
                    messageType=msg.RES_REQUEST_RESULT,
                    error="this message is invalid",
                )
            yield res

    @function_log
    def start_service(self, recv_any_message):
        recv_msg = unpack_any_message(recv_any_message, msg.InitializeService)

        m = msg.StatusKanban()
        metadata = {"test": "test"}
        services = [recv_msg.microserviceName, "test2"]
        s = Struct()
        s.update(metadata)

        m.startAt = datetime.now().isoformat()
        m.finishAt = datetime.now().isoformat()
        m.priorSuccess = True
        m.connectionKey = "key"
        m.processNumber = 1
        m.dataPath = "/var/lib/aion"
        m.metadata.CopyFrom(s)

        m.services.extend(services)

        res = msg.Response(messageType=msg.RES_CACHE_KANBAN)
        res.message.CopyFrom(pack_any_message(m))
        res.error = ""
        return res

    @function_log
    def output_kanban(self, recv_any_message):
        res = msg.Response(messageType=msg.RES_REQUEST_RESULT, error="")
        return res


@function_log
def start_mock_server(get_queue):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rpc.add_KanbanServicer_to_server(GrpcServer(get_queue), server)
    server.add_insecure_port("[::]:11010")
    server.start()
    lprint("starting gRPC server...")


@pytest.fixture()
def setup_grpc():
    # start server
    get_queue = Queue()
    start_mock_server(get_queue)

    # start client
    k = KanbanConnection()
    yield k, get_queue
    k.close()


def test_normal_001_get_kanban(setup_grpc):
    client, server_queue = setup_grpc
    current_service_name = "service1"

    k = client.get_one_kanban(current_service_name, 0)
    assert k
    assert k.get_start_at()
    assert k.get_finish_at()
    assert k.get_services()
    assert k.get_services()[0] == current_service_name
    assert k.get_connection_key() == "key"
    assert 1 == k.get_process_number()
    assert k.get_result()
    assert k.get_data_path() == "/var/lib/aion"
    assert k.get_metadata()
    for k, v in k.get_metadata().items():
        assert k == v


def test_normal_001_output_kanban(setup_grpc):
    client, server_queue = setup_grpc
    current_service_name = "service1"

    connection_key = "key"
    data_path = "/var/lib/aion"
    metadata = {"test": "test"}

    k = client.output_kanban(True, connection_key, data_path, metadata)
    m = server_queue.get(timeout=1)
    assert m.messageType == msg.OUTPUT_AFTER_KANBAN
    raw_m = unpack_any_message(m.message, msg.OutputRequest)

    assert raw_m.connectionKey == connection_key
    assert raw_m.priorSuccess
    assert raw_m.dataPath == data_path

    a = {}
    a.update(raw_m.metadata)
    for k, v in a.items():
        assert k == v
