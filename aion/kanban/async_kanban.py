# coding: utf-8

# Copyright (c) 2019-2020 Latona. All rights reserved.

from aion.proto import status_pb2_grpc as rpc
from aion.proto import status_pb2 as message
import grpc
from grpc.experimental import aio
from google.protobuf.any_pb2 import Any
from google.protobuf.struct_pb2 import Struct
from google.protobuf.json_format import MessageToDict

from threading import Thread, Condition
from asyncio import Queue, wait_for, TimeoutError, get_event_loop, ensure_future
from dateutil import parser
from typing import Iterator

from aion.logger import lprint
from .kanban import KanbanConnection

async def _grpc_message_generator(message_queue):
    while True:
        try:
            r = await message_queue.get()
            if r is None:
                break
            yield r
        except TimeoutError:
            lprint("send queue is closed")
            break


def _unpack_any_message(any_message, recv_message):
    if not any_message.Is(recv_message.DESCRIPTOR):
        lprint("cant unmarshal any message")
        return None
    m = recv_message()
    any_message.Unpack(m)
    return m


def _pack_any_message(normal_message):
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


class KanbanConnectionAsync(KanbanConnection):
    channel = None
    conn = None
    response_thread = None

    def __init__(self, addr="localhost:11010"):
        self.addr = addr
        loop = get_event_loop()
        loop.run_until_complete(self.run())

    async def __del__(self):
        await self.close()

    async def run(self):
        aio.init_grpc_aio()
        self.channel = aio.insecure_channel(self.addr)
        await self.channel.channel_ready()
        self.connectivity = self.channel.get_state(try_to_connect=True)

        self.conn = rpc.KanbanStub(self.channel)

        self.send_kanban_queue = Queue()
        self.recv_kanban_queue = Queue()

        self.responses = self.conn.MicroserviceConn(_grpc_message_generator(self.send_kanban_queue))

        self.check_connectivity()
        self.is_thread_stop = False
        self.response_thread = ensure_future(self._receive_function())

    def reconnect(self):
        loop = get_event_loop()
        loop.run_until_complete(self.run())
        self.check_connectivity()
        if self.current_message_type == message.START_SERVICE_WITHOUT_KANBAN:
            self.set_kanban(self.current_service_name, self.current_number)

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

    async def close(self):
        self.is_thread_stop = True
        await self.send_kanban_queue.put(None)
        await self.channel.close()
        if self.response_thread is not None:
            self.response_thread.cancel()

    async def _receive_function(self):
        try:
            async for res in self.responses:
                if res.messageType == message.RES_CACHE_KANBAN:
                    if res.error != "":
                        lprint(f"[gRPC] get cache kanban is failed :{res.error}")
                        await self.recv_kanban_queue.put(None)
                    else:
                        m = _unpack_any_message(res.message, message.StatusKanban)
                        if m is None:
                            continue
                        await self.recv_kanban_queue.put(m)
                elif res.messageType == message.RES_REQUEST_RESULT:
                    if res.error != "":
                        lprint(f"[gRPC] request is failed :{res.error}")
                    else:
                        lprint(f"[gRPC] success to send request :{res.messageType}")
                else:
                    lprint(f"[gRPC] invalid message type: {res.messageType}")
        except grpc.RpcError as e:
            await self.recv_kanban_queue.put(None)

            lprint(f'[gRPC] failed with code {e.code()}')
            if e.code() == grpc.StatusCode.CANCELLED:
                if self.is_thread_stop:
                    lprint("[gRPC] closed connection is successful")
                else:
                    self.reconnect()
            elif e.code() == grpc.StatusCode.INTERNAL:
                # when stream idle time is more than 5 minutes, grpc connection is disconnected by envoy.
                # while that action is not wrong(long live connection is evil), it is bother by application.
                # so we attempt to reconnect on library.
                self.reconnect()

    async def _send_message_to_grpc(self, message_type, body):
        m = message.Request()

        m.messageType = message_type
        m.message.CopyFrom(_pack_any_message(body))
        await self.send_kanban_queue.put(m)

    async def _send_initial_kanban(self, message_type, service_name, number):
        m = message.InitializeService()
        m.microserviceName = service_name
        m.processNumber = int(number)
        await self._send_message_to_grpc(message_type, m)

    async def get_one_kanban(self, service_name, number) -> Kanban:
        self._send_initial_kanban(message.START_SERVICE, service_name, number)

        self.set_current_service_name(service_name)
        self.set_current_number(number)
        self.set_current_message_type(message.START_SERVICE)
        # get kanban when
        k = None
        try:
            k = await wait_for(self.recv_kanban_queue.get(), timeout=0.1)
        except TimeoutError:
            lprint("[gRPC] cant connect to status kanban server, exit service")
        if k is None:
            raise KanbanNotFoundError

        return Kanban(k)

    async def get_kanban_itr(self, service_name: str, number: int) -> Iterator[Kanban]:
        await self._send_initial_kanban(message.START_SERVICE, service_name, number)

        self.set_current_service_name(service_name)
        self.set_current_number(number)
        self.set_current_message_type(message.START_SERVICE)
        # get kanban when
        k = None
        try:
            while True:
                k = await self.recv_kanban_queue.get()
                if k is None:
                    break
                yield Kanban(k)
        except TimeoutError:
            lprint("[gRPC] kanban queue is empty")

    async def set_kanban(self, service_name, number) -> Kanban:
        self._send_initial_kanban(message.START_SERVICE_WITHOUT_KANBAN, service_name, number)

        self.set_current_service_name(service_name)
        self.set_current_number(number)
        self.set_current_message_type(message.START_SERVICE_WITHOUT_KANBAN)
        # get kanban when
        k = None
        try:
            k = await wait_for(self.recv_kanban_queue.get(), timeout=0.1)
        except TimeoutError:
            lprint("[gRPC] cant connect to status kanban server, exit service")
        if k is None:
            raise KanbanNotFoundError

        return Kanban(k)

    async def output_kanban(
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
        self._send_message_to_grpc(message.OUTPUT_AFTER_KANBAN, m)
