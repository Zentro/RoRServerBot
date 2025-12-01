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
from rorserverbot import __clt_version__
from .RoRnet import UserInfo, ServerInfo, MessageType, __version__
from .RoRnet.utils import unpack_to_struct, pack_from_struct


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

    def __init__(self,
                 logger=None,
                 host: str = None,
                 port: int = None,
                 username: str = "RoRBot",
                 password: str = "",
                 language: str = "en-US"):
        """
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
        self.unique_id = 0
        self.logger = logger
        self.connected = False
        self.reader = None
        self.writer = None
        self.run_task = None
        self.host = host
        self.port = port
        self.user_info = UserInfo(
            username=username,
            serverpassword=password,
            language=language,
            clientname="RoRBot",
            clientversion=__clt_version__,
            usertoken="",
        )
        self.server_info = ServerInfo(
            protocolversion = __version__
        )
        self.event_handlers = {
            'on_message': [],
            'on_event': [],
            'on_error': [],
            'on_close': [],
            'on_connect': [],
            'on_disconnect': [],
            'on_timeout': [],
        }

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

            await self._send_hello(bytes(__version__, 'utf-8'))
            # Send the MSG2_HELLO packet, and the server should
            # send back a MSG2_HELLO response with server info.
            # Copy that info into our ServerInfo object.
            raw_header = await self.recv()
            packet = await self.read(raw_packet=raw_header)
            if packet.command != MessageType.MSG2_HELLO:
                if packet.command == MessageType.MSG2_WRONG_VER:
                    self.logger.error("Failed to connect: Wrong version.")
                else:
                    self.logger.error("Failed to connect: Unknown error.")
                await self.disconnect()
                raise Exception("Invalid response from server during HELLO")
            # Unpack the server info from the packet data.
            # (self.server_info.protocolversion,
            #  self.server_info.terrain,
            #  self.server_info.servername,
            #  self.server_info.info) = struct.unpack(
            #     '20s128s128s?4096s', packet.data)
            self.server_info = unpack_to_struct(ServerInfo, packet.data)

            # The server now wants our USER_INFO. Send it.
            await self._send_user_info(pack_from_struct(self.user_info))
            raw_header = await self.recv()
            packet = await self.read(raw_packet=raw_header)

            # Now, we should recieve the server's MSG2_WELCOME packet.
            # If we do, we're fully connected. If not, we may get
            # MSG2_FULL, MSG2_BANNED, MSG2_WRONG_VER, or MSG2_WRONG_PW.
            if packet.command != MessageType.MSG2_WELCOME:
                if packet.command == MessageType.MSG2_FULL:
                    self.logger.error('Failed to connect: Server is full.')
                elif packet.command == MessageType.MSG2_BANNED:
                    self.logger.error('Failed to connect: Banned from the '
                                      'server.')
                elif packet.command == MessageType.MSG2_WRONG_PW:
                    self.logger.error('Failed to connect: Wrong password.')
                else:
                    self.logger.error('Failed to connect: Unknown error.')
                self.logger.error('Failed to connect: Unexpected response '
                                  'from server.')
                await self.disconnect()
                raise Exception('Unexpected response from server.')
            # Unpack our user info from the welcome packet.
            self.user_info = unpack_to_struct(UserInfo, packet.data)
            self.unique_id = self.user_info.uniqueid
            self.run_task = asyncio.create_task(self.run())
            await self.dispatch_event('on_connect')
        except asyncio.TimeoutError as e:
            await self.dispatch_event('on_timeout', str(e))
            self.logger.error(f"Connection timeout: {e}")
            raise e
        except ConnectionRefusedError as e:
            await self.dispatch_event('on_error', str(e))
            self.logger.error(f"Connection refused: {e}")
            raise e
        except OSError as e:
            await self.dispatch_event('on_error', str(e))
            self.logger.error(f"OS Error during connection: {e}")
            raise e
        except Exception as e:
            await self.dispatch_event('on_error', str(e))
            self.logger.error(f"Connection error: {e}")
            raise e

    async def _send_user_leave(self):
        """
        Send USER_LEAVE packet to the server.
        :return: None
        :rtype: None
        """
        await self.send(DataPacket(
            source=self.unique_id,
            command=MessageType.MSG2_USER_LEAVE,
            streamid=0,
            size=0,
            data=b'',
            time=0
        ))

    async def _send_hello(self, version_data):
        """
        Send HELLO packet to the server.

        :return: None
        :rtype: None
        """
        await self.send(DataPacket(
            source=0,
            command=MessageType.MSG2_HELLO,
            streamid=0,
            size=len(version_data),
            data=bytes(version_data),
            time=0
        ))

    async def _send_user_info(self, user_info_data):
        """
        Send USER_INFO packet to the server.

        :return: None
        :rtype: None
        """
        await self.send(DataPacket(
            source=0,
            command=MessageType.MSG2_USER_INFO,
            streamid=0,
            size=len(user_info_data),
            data=user_info_data,
            time=0
        ))

    async def disconnect(self):
        """
        Disconnect from the server.

        :return: None
        :rtype: None
        """
        # Send USER_LEAVE packet
        await self._send_user_leave()
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

        # Now tell any listeners we're disconnected
        await self.dispatch_event('on_disconnect')
        # Reset the writer and reader
        self.writer = None
        self.reader = None
        # At this point, we're fully disconnected and
        # we can safely be destroyed at this point.
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
            header = await self.read_exactly(self.reader, 16)
            return header
        except asyncio.IncompleteReadError as e:
            if e.partial == b'':  # Clean disconnect
                self.logger.info("Connection closed by peer")
            else:  # Partial data received
                self.logger.warning(f"Incomplete read: received "
                                    f"{len(e.partial)} bytes, expected 16")
            await self.dispatch_event('on_error', str(e))
            return None
        except Exception as e:
            self.logger.error(f"Error receiving data: {e}")
            await self.dispatch_event('on_error', str(e))
            await self.disconnect()
            return None

    async def read_exactly(self, reader, n: int) -> bytes:
        """
        Read exactly n bytes from the reader.

        :param reader: The StreamReader to read from.
        :param n: Number of bytes to read.
        :return: Bytes read from the reader.
        :rtype: bytes
        """
        data = b""
        while len(data) < n:
            chunk = await reader.read(n - len(data))
            if not chunk:
                raise Exception(f"Expected {n} bytes, got {len(data)} bytes "
                                f"before EOF")
            data += chunk
        return data

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
        raw_data = await self.read_exactly(self.reader, size) \
                    if size > 0 else b""
        data = raw_data if raw_data else b""

        # Create packet object
        packet = DataPacket(
            source=source,
            command=command,
            streamid=streamid,
            size=size,
            data=data,
            time=0
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
