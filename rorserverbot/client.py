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
import hashlib
from dataclasses import dataclass
from .RoRnet import UserInfo, ServerInfo, MessageType, __version__


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
    :type data: bytes
    :type time: int
    """
    source: int
    command: int
    streamid: int
    size: int
    data: bytes
    time: int


class Client():
    """Client class to handle the connection to the server.
    """

    VERSION = __version__

    def __init__(self,
                 unique_id: int = 0,
                 logger=None,
                 host: str = None,
                 port: int = None,
                 username: str = "RoRBot",
                 password: str = "",
                 language: str = "en-US"):
        """
        :param unique_id: Unique ID of the client.
        :type unique_id: int

        :param logger: Logger object to log messages.
        :type logger: logging.Logger

        :param host: Hostname or IP address of the server.
        :type host: str

        :param port: Port number of the server.
        :type port: int

        :param username: Username of the client.
        :type username: str

        :param password: Password of the client.
        :type password: str

        :param language: Language of the client.
        :type language: str

        :return: None
        :rtype: None
        """
        self.unique_id = unique_id
        self.logger = logger
        self.connected = False
        self.reader = None
        self.writer = None
        self.run_task = None
        self.host = host
        self.port = port
        self.user_info = UserInfo()
        self.server_info = None
        self.event_handlers = {
            'on_message': [],
            'on_event': [],
            'on_error': [],
            'on_close': [],
            'on_connect': [],
            'on_disconnect': [],
            'on_timeout': [],
        }
        self.user_info.username = username.encode('utf-8').ljust(40, b'\x00')
        self.user_info.serverpassword = password.encode('utf-8').ljust(40, b'\x00')
        self.user_info.language = language.encode('utf-8').ljust(10, b'\x00')
        self.user_info.clientname = b'RoRBot'.ljust(10, b'\x00')
        self.user_info.clientversion = b'1.0'.ljust(25, b'\x00')
        self.user_info.usertoken = b''.ljust(40, b'\x00')

    async def connect(self):
        """
        Connect to the server.
        :return: None
        :rtype: None
        :raises Exception: If connection fails.
        """
        try:
            self.reader, self.writer = await asyncio.open_connection(self.host,
                                                                     self.port)
            self.connected = True
            self.logger.info(f"Connection established to "
                             f"{self.host}:{self.port}")
            # TODO: Send HELLO in a _send_hello() method
            #user_info_bytes = bytes(user_info)
            version = b'RoRnet_2.44'
            hello_packet = DataPacket(
                source=0,  # Client source ID
                command=MessageType.MSG2_HELLO,
                streamid=0,
                size=len(version),
                data=bytes(version),  # Store as string in DataPacket
                time=0
            )
            await self.send(hello_packet)

            # TODO: Read HELLO response in big loop
            raw_header = await self.recv()  # Await server response to HELLO
            packet = await self.read(raw_packet=raw_header)  # Process server response
            if packet.command != MessageType.MSG2_HELLO:
                raise Exception("Invalid response from server during HELLO")
            data = struct.pack('Iiii40s40s40s10s10s25s40s10s128s',
                    int(self.user_info.uniqueid),
                    int(self.user_info.authstatus),
                    int(self.user_info.slotnum),
                    int(self.user_info.colournum),
                    self.user_info.username,
                    hashlib.sha1(self.user_info.usertoken).digest().upper(),
                    hashlib.sha1(self.user_info.serverpassword).digest().upper(),
                    self.user_info.language,
                    self.user_info.clientname,
                    self.user_info.clientversion,
                    self.user_info.clientGUID,
                    self.user_info.sessiontype,
                    self.user_info.sessionoptions
            )
            await self.send(DataPacket(
                source=0,
                command=MessageType.MSG2_USER_INFO,
                streamid=0,
                size=len(data),
                data=data,  # Store as string in DataPacket
                time=0
            ))

            self.run_task = asyncio.create_task(self.run())
            await self.dispatch_event('on_connect')
        except Exception as e:
            await self.dispatch_event('on_error', str(e))
            self.logger.error(f"Connection error: {e}")
            raise e

    async def disconnect(self):
        """
        Disconnect from the server.

        :return: None
        :rtype: None
        """
        self.connected = False

        if self.run_task and not self.run_task.done():
            self.run_task.cancel()
            try:
                await self.run_task
            except asyncio.CancelledError:
                pass

        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

        await self.dispatch_event('on_disconnect')
        # Reset the writer and reader
        self.writer = None
        self.reader = None

        self.logger.info("Disconnected from server.")

    async def recv(self):
        """
        Receive the header of a packet from the server.

        :return: Data received from the server (16 bytes header).
        :rtype: bytes
        """
        if not self.connected:
            return None

        try:
            header = await self.reader.readexactly(16)
            return header
        except asyncio.IncompleteReadError as e:
            self.logger.warning(f"Incomplete read: {e}")
            await self.dispatch_event('on_error', str(e))
            await self.disconnect()
            return None
        except Exception as e:
            self.logger.error(f"Error receiving data: {e}")
            await self.dispatch_event('on_error', str(e))
            await self.disconnect()
            return None

    async def read(self, raw_packet) -> DataPacket:
        """
        Read a raw packet from the server.
        :param raw_packet: Raw packet data.
        :return: DataPacket object.
        """
        # Unpack header: command, source, streamid, size
        (command, source, streamid, size) = struct.unpack('IIII',
                                                          raw_packet)

        # Handle signed source ID
        if source & 0x80000000:
            source = -0x100000000 + source

        # Read payload data if size > 0
        raw_data = await self.reader.read(size) if size > 0 else b""
        data = raw_data.decode('utf-8', errors='replace') if raw_data \
            else ""

        # Create packet object
        packet = DataPacket(
            source=source,
            command=command,
            streamid=streamid,
            size=size,
            data=data,
            time=0  # Could add timestamp if needed
        )

        self.logger.debug(f"Reading packet: "
                          f"command={packet.command}, "
                          f"source={packet.source}, "
                          f"streamid={packet.streamid}, "
                          f"size={packet.size}"
                          f"data={packet.data}")
        return packet

    async def send(self, packet: DataPacket):
        """
        Send a DataPacket to the server.

        :param packet: DataPacket object to send.
        :type packet: DataPacket
        :return: None
        :rtype: None
        """
        if not self.connected:
            self.logger.warning("Cannot send: not connected")
            return

        try:
            data = self._pack_packet(packet)
            self.writer.write(data)
            await self.writer.drain()
            self.logger.debug(f"Sent packet: command={packet.command}, "
                              f"size={packet.size}")
        except Exception as e:
            self.logger.error(f"Error sending packet: {e}")
            await self.disconnect()

    async def run(self):
        """
        Run the main receive loop.
        """
        self.logger.debug("Starting the main receive loop.")

        while self.connected:
            try:
                raw_header = await self.recv()
                if not raw_header:
                    break

                # Create packet object
                packet = await self.read(raw_packet=raw_header)

                # Process the packet based on command type
                await self._process_packet(packet)

            except asyncio.CancelledError:
                self.logger.info("Receive loop cancelled")
                await self.disconnect()
                break
            except Exception as e:
                self.logger.error(f"Error in receive loop: {e}")
                await self.dispatch_event('on_error', str(e))
                await self.disconnect()
                break

        self.logger.info("Receive loop ended")

    async def _process_packet(self, packet: DataPacket):
        """
        Process a received packet based on its command type.

        :param packet: The received DataPacket
        """
        command = packet.command

        # Check if command is valid
        if command not in [mt.value for mt in MessageType]:
            self.logger.warning(f"Unknown command type: {command}")
            return

        # Handle different message types
        if command == MessageType.MSG2_STREAM_DATA.value:
            # Stream data - currently ignored
            pass
        elif command == MessageType.MSG2_NETQUALITY.value:
            # Network quality - currently ignored
            pass
        elif command == MessageType.MSG2_USER_JOIN.value:
            self.logger.info(f"User joined: source={packet.source}")
            await self.dispatch_event('on_event', 'user_join',
                                      packet.data)
        elif command == MessageType.MSG2_USER_LEAVE.value:
            self.logger.info(f"User left: source={packet.source}")
            await self.dispatch_event('on_event', 'user_leave',
                                      packet.data)
        elif command == MessageType.MSG2_STREAM_REGISTER_RESULT.value:
            # Stream registration result
            pass
        elif command == MessageType.MSG2_STREAM_REGISTER.value:
            # Stream registration
            pass
        elif command == MessageType.MSG2_STREAM_UNREGISTER.value:
            # Stream unregistration
            pass
        elif command == MessageType.MSG2_UTF_CHAT.value:
            # Handle special system messages (source > 100000 means system)
            if packet.source > 100000:
                packet.source = -1

            chat_message = packet.data
            self.logger.debug(f"Chat message from {packet.source}: "
                              f"{chat_message}")
            await self.dispatch_event('on_message', chat_message)
        elif command == MessageType.MSG2_UTF_PRIVCHAT.value:
            # Private chat - currently ignored
            pass

    def _pack_packet(self, packet: DataPacket):
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
                           packet.data)

    def is_connected(self) -> bool:
        """
        Check if the client is connected to the server.

        :return: True if connected, False otherwise.
        :rtype: bool
        """
        return self.connected

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
            try:
                await handler(*args)
            except Exception as e:
                self.logger.error(f"Error in event handler for {event_name}: "
                                  f"{e}")
