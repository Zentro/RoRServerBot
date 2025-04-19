#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
import asyncio
import struct
from dataclasses import dataclass
from RoRnet import UserInfo, ServerInfo, MessageType


@dataclass
class DataPacket:
    """
    DataPacket class to represent a packet of data to be sent or received.

    :param source: Source of the packet.
    :param command: Command of the packet.
    :param streamid: Stream ID of the packet.
    :param size: Size of the packet.
    :param data: Data of the packet.
    :param time: Time of the packet.
    :type source: int
    :type command: int
    :type streamid: int
    :type size: int
    :type data: str
    :type time: int
    """
    source: int
    command: int
    streamid: int
    size: int
    data: str
    time: int


class Connection():
    def __init__(self, stream, logger):
        """
        Connection class to handle the connection to the server.
        :param stream: Stream object to handle the connection.
        :param
        logger: Logger object to handle logging.
        :type stream: Stream
        :type logger: Logger

        """
        self.logger = logger
        self.connected = False
        self.reader = None
        self.writer = None
        self.event_handlers = {
            'on_message': [],
            'on_event': [],
            'on_error': [],
            'on_close': [],
            'on_connect': [],
            'on_disconnect': [],
            'on_timeout': [],
        }

    async def connect(self,
                      host: str,
                      port: int,
                      user_info: UserInfo,
                      server_info: ServerInfo):
        """
        Connect to the server.

        :param host: Hostname or IP address of the server.
        :param port: Port number of the server.
        :param user_info: UserInfo object containing user information.
        :param server_info: ServerInfo object containing server information.
        :type host: str
        :type port: int
        :type user_info: UserInfo
        :type server_info: ServerInfo
        :return: None
        :rtype: None
        """
        self.reader, self.writer = await asyncio.open_connection(host, port)
        self.connected = True
        # Dispatch the on_connect event to all registered handlers.
        await self.dispatch_event('on_connect', user_info, server_info)
        asyncio.create_task(self.run())

    async def disconnect(self):
        """
        Disconnect from the server.

        :return: None
        :rtype: None
        """
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        self.connected = False
        await self.dispatch_event('on_disconnect')
        # Reset the writer and reader to None to allow for garbage collection
        # and prevent memory leaks.
        self.writer = None
        self.reader = None

    async def recv(self):
        """
        Receive data from the server.

        :return: Data received from the server.
        :rtype: bytes
        """
        if not self.connected:
            return

        try:
            await self.reader.readexactly(16)
        except asyncio.IncompleteReadError:
            await self.disconnect()
            return

    async def send(self, packet: DataPacket):
        """
        Send a DataPacket to the server.

        :param packet: DataPacket object to send.
        :type packet: DataPacket
        :return: None
        :rtype: None"""
        if not self.connected:
            return

        data = self.__pack_packet(packet)
        self.writer.write(data)
        await self.writer.drain()

    async def run(self):
        while self.connected:
            raw_data = await self.recv()
            if raw_data:
                (command, source, streamid, size) = struct.unpack('IIII',
                                                                  raw_data)
                if source & 0x80000000:
                    source = -0x100000000 + source
                raw_data = await self.reader.read(size) if size > 0 else b""
                data = struct.unpack(str(size) + 's', raw_data)[0]
                packet = DataPacket(
                    source,
                    command,
                    streamid,
                    size,
                    data.decode()
                )

                if command not in MessageType:
                    continue

                if command == MessageType.MSG2_STREAM_DATA:
                    # We're not interested in this message currently.
                    continue
                elif command == MessageType.MSG2_NETQUALITY:
                    # We're not interested in this message currently.
                    continue
                elif command == MessageType.MSG2_USER_JOIN:
                    # We're not interested in this message currently.
                    continue
                elif command == MessageType.MSG2_USER_LEAVE:
                    # We're not interested in this message currently.
                    continue
                elif command == MessageType.MSG2_STREAM_REGISTER_RESULT:
                    # We're not interested in this message currently.
                    continue
                elif command == MessageType.MSG2_STREAM_REGISTER:
                    # We're not interested in this message currently.
                    continue
                elif command == MessageType.MSG2_STREAM_UNREGISTER:
                    # We're not interested in this message currently.
                    continue
                elif command == MessageType.MSG2_UTF_CHAT:
                    if packet.source > 100000:
                        packet.source = -1
                    chat_message = packet.data.decode('utf-8')

                    await self.dispatch_event('on_message', chat_message)
                    continue
                elif command == MessageType.MSG2_UTF_PRIVCHAT:
                    # We're not interested in this message currently.
                    continue

    def __pack_packet(self, packet: DataPacket):
        """
        Pack a DataPacket into bytes.

        :param packet: DataPacket object to pack.
        :type packet: DataPacket
        :return: Packed bytes.
        :rtype: bytes
        """
        if packet.size == 0:
            return struct.pack('IIII',
                               packet.command,
                               packet.source,
                               packet.streamid,
                               packet.size)
        return struct.pack('IIII'+str(packet.size)+'s',
                           packet.command,
                           packet.source,
                           packet.streamid,
                           packet.size,
                           packet.data.encode())

    def register_event_handler(self, event_name, handler):
        """
        Register an event handler for a specific event.

        :param event_name: Name of the event to register the handler for.
        :param handler: Function to handle the event.
        :type event_name: str
        :type handler: function
        :return: None
        :rtype: None
        """
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(handler)
        self.logger.debug(f"Registered event handler for {event_name}")

    async def dispatch_event(self, event_name, *args):
        """
        Dispatch an event to all registered handlers.

        :param event_name: Name of the event to dispatch.
        :param args: Arguments to pass to the event handlers.
        :type event_name: str
        :type args: tuple
        :return: None
        :rtype: None
        """
        for handler in self.event_handlers.get(event_name, []):
            await handler(*args)
