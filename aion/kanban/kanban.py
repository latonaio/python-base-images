# coding: utf-8

# Copyright (c) 2019-2020 Latona. All rights reserved.

from aion.proto import status_pb2_grpc as rpc
from aion.proto import status_pb2 as message
import grpc
from google.protobuf.any_pb2 import Any
from google.protobuf.struct_pb2 import Struct
from google.protobuf.json_format import MessageToDict

from threading import Thread, Condition
from queue import Queue, Empty
from dateutil import parser
from typing import Iterator

from aion.logger import lprint


def unpack_any_message(any_message, recv_message):
    if not any_message.Is(recv_message.DESCRIPTOR):
        lprint("cant unmarshal any message")
        return None
    m = recv_message()
    any_message.Unpack(m)
    return m


def pack_any_message(normal_message):
    any_m = Any()
    any_m.Pack(normal_message)
    return any_m


class Kanban:
    def __init__(self, kanban):
        self.kanban = kanban

    def get_start_at(self):
        if self.kanban.startAt:
            return parser.parse(self.kanban.startAt)
        return None

    def get_finish_at(self):
        if self.kanban.startAt:
            return parser.parse(self.kanban.finishAt)
        return None

    def get_services(self):
        return self.kanban.services

    def get_connection_key(self):
        return self.kanban.connectionKey

    def get_process_number(self):
        return self.kanban.processNumber

    def get_result(self):
        return self.kanban.priorSuccess

    def get_data_path(self):
        return self.kanban.dataPath

    def get_file_list(self):
        return self.kanban.fileList

    def get_metadata(self):
        return MessageToDict(self.kanban.metadata)


class KanbanServerNotFoundError(Exception):
    def __init__(self, addr):
        self.addr = addr

    def __str__(self):
        return f"cant connect to kanban server: {self.addr}"


class KanbanNotFoundError(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return f"cant get kanban from server"


class _Callback(object):
    def __init__(self):
        self._condition = Condition()
        self._connectivity = None

    def update(self, connectivity):
        with self._condition:
            self._connectivity = connectivity
            self._condition.notify()

    def connectivity(self):
        with self._condition:
            return self._connectivity

    def block_until_connectivities_satisfy(self, predicate):
        with self._condition:
            while True:
                connectivity = self._connectivity
                if predicate(connectivity):
                    return connectivity
                else:
                    self._condition.wait()


class KanbanConnection:
    channel = None
    conn = None
    response_thread = None

    def __init__(self, addr="localhost:11010"):
        self.addr = addr
        self.run()

    def __del__(self):
        self.send_queue.put(None)
        self.close()
        if self.response_thread is not None:
            self.response_thread.join()

    def run(self):
        callback = _Callback()
        self.channel = grpc.insecure_channel(self.addr, options=[('grpc.keepalive_time_ms', 5000), ('grpc.keepalive_timeout_ms', 10000), ('grpc.min_time_between_pings_ms', 15000), ('grpc.max_pings_without_data', 0)])
        self.channel.subscribe(callback.update, try_to_connect=True)
        self.connectivity = callback.block_until_connectivities_satisfy(
            lambda c:
            c == grpc.ChannelConnectivity.READY or
            c == grpc.ChannelConnectivity.TRANSIENT_FAILURE)

        self.conn = rpc.KanbanStub(self.channel)
        self.send_queue = Queue()
        self.kanban_queue = Queue()
        self.response_queue = Queue()
        self.responses = self.conn.MicroserviceConn(self.message_generator())

    def reconnect(self):
        self.run()
        self.check_connectivity()
        if self.current_message_type == message.START_SERVICE_WITHOUT_KANBAN:
            self.set_kanban(self.current_service_name, self.current_number)
        elif self.current_message_type == message.START_SERVICE:
            self.get_one_kanban(self.current_service_name, self.current_number)

    def set_current_service_name(self, service_name):
        self.current_service_name = service_name

    def set_current_number(self, number):
        self.current_number = number

    def set_current_message_type(self, messate_type):
        self.current_message_type = messate_type

    def check_connectivity(self):
        lprint(self.connectivity)
        if grpc.ChannelConnectivity.READY != self.connectivity:
            raise KanbanServerNotFoundError(self.addr)

        self.response_thread = Thread(target=self.receive_function, args=())
        self.response_thread.start()

    def close(self):
        self.channel.close()

    def message_generator(self):
        while True:
            try:
                r = self.send_queue.get()
                if r is None:
                    break
                yield r
            except Empty:
                lprint("send queue is closed")
                break

    def receive_function(self):
        try:
            for res in self.responses:
                if res.messageType == message.RES_CACHE_KANBAN:
                    if res.error != "":
                        lprint(f"[gRPC] get cache kanban is failed :{res.error}")
                        self.kanban_queue.put(None)
                    else:
                        m = unpack_any_message(res.message, message.StatusKanban)
                        if m is None:
                            continue
                        self.kanban_queue.put(m)
                elif res.messageType == message.RES_REQUEST_RESULT:
                    if res.error != "":
                        lprint(f"[gRPC] request is failed :{res.error}")
                        self.response_queue.put(res.error)
                    else:
                        lprint(f"[gRPC] success to send request :{res.messageType}")
                        self.response_queue.put(None)
                else:
                    lprint(f"[gRPC] invalid message type: {res.messageType}")
                    self.response_queue.put(res.error)
        except grpc.RpcError as e:
            self.kanban_queue.put(None)

            lprint(f'[gRPC] failed with code {e.code()}')
            if e.code() == grpc.StatusCode.CANCELLED:
                lprint("[gRPC] closed connection is successful")
            elif e.code() == grpc.StatusCode.INTERNAL:
                # when stream idle time is more than 5 minutes, grpc connection is disconnected by envoy.
                # while that action is not wrong(long live connection is evil), it is bother by application.
                # so we attempt to reconnect on library.
                self.reconnect()

    def send_message(self, message_type, body):
        m = message.Request()

        m.messageType = message_type
        m.message.CopyFrom(pack_any_message(body))
        self.send_queue.put(m)

    def send_kanban_request(self, message_type, service_name, number):
        m = message.InitializeService()
        m.microserviceName = service_name
        m.processNumber = int(number)
        self.send_message(message_type, m)

    def get_one_kanban(self, service_name, number) -> Kanban:
        self.send_kanban_request(message.START_SERVICE, service_name, number)

        self.set_current_service_name(service_name)
        self.set_current_number(number)
        self.set_current_message_type(message.START_SERVICE)
        # get kanban when
        k = None
        try:
            k = self.kanban_queue.get(timeout=0.1)
        except Empty:
            lprint("[gRPC] cant connect to status kanban server, exit service")
        if k is None:
            raise KanbanNotFoundError

        return Kanban(k)

    def get_kanban_itr(self, service_name: str, number: int) -> Iterator[Kanban]:
        self.send_kanban_request(message.START_SERVICE, service_name, number)

        self.set_current_service_name(service_name)
        self.set_current_number(number)
        self.set_current_message_type(message.START_SERVICE)
        # get kanban when
        k = None
        try:
            while True:
                k = self.kanban_queue.get()
                if k is None:
                    break
                yield Kanban(k)
        except Empty:
            lprint("[gRPC] kanban queue is empty")

    def set_kanban(self, service_name, number) -> Kanban:
        self.send_kanban_request(message.START_SERVICE_WITHOUT_KANBAN, service_name, number)

        self.set_current_service_name(service_name)
        self.set_current_number(number)
        self.set_current_message_type(message.START_SERVICE_WITHOUT_KANBAN)
        # get kanban when
        k = None
        try:
            k = self.kanban_queue.get(timeout=0.1)
        except Empty:
            lprint("[gRPC] cant connect to status kanban server, exit service")
        if k is None:
            raise KanbanNotFoundError

        return Kanban(k)

    def output_kanban(
            self, result=True, connection_key="default", output_data_path="",
            process_number=1, file_list=None, metadata=None, device_name="") -> None:
        m = message.OutputRequest()

        if metadata is None:
            metadata = {}

        if not file_list:
            file_list = []
        elif not isinstance(file_list, list):
            file_list = [file_list]

        s = Struct()
        s.update(metadata)

        m.priorSuccess = result
        m.dataPath = output_data_path
        m.connectionKey = connection_key
        m.processNumber = int(process_number)
        m.fileList.extend(file_list)
        m.metadata.CopyFrom(s)
        m.deviceName = device_name
        self.send_message(message.OUTPUT_AFTER_KANBAN, m)
        try:
            self.response_queue.get(timeout=0.1)
        except Empty:
            pass