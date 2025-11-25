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

from RoRnet.structs import UserInfo, ServerInfo
from .stream import Stream
import asyncio


class Client():
    """Client class is a high-level interface to manage a single connection.
    """

    def __init__(self, logger, host, port, password, channel_id):
        """
        Client class to handle the connection to the server.

        :param logger: Logger object to log messages.
        :type logger: logging.Logger
        :param host: Hostname or IP address of the server.
        :type host: str
        :param port: Port number of the server.
        :type port: int
        :param password: Password for authentication (Optional).
        :type password: str
        :param channel_id: Channel ID to connect to.
        :type channel_id: int
        """
        self.logger = logger
        self.host = host
        self.port = port
        self.password = password
        self.channel_id = channel_id
        self.stream = Stream(logger, host, port)
        self.running = False

        self.user_info = None
        self.server_info = None

        # Register event handlers
        self._setup_event_handlers()

    def _setup_event_handlers(self):
        """
        Setup internal event handlers for the stream.
        :return: None
        :rtype: None
        """
        self.stream.register_event_handler('on_connect',
                                           self._on_connect)
        self.stream.register_event_handler('on_disconnect',
                                           self._on_disconnect)
        self.stream.register_event_handler('on_message',
                                           self._on_message)

    async def _on_connect(self, user_info, server_info):
        self.user_info = user_info
        self.server_info = server_info
        self.logger.info(f"Connected to {self.host}:{self.port} for channel "
                         f"{self.channel_id}")

    async def _on_disconnect(self):
        self.logger.info(f"Disconnected from {self.host}:{self.port}")
        self.running = False

    async def _on_message(self, chat_message):
        self.logger.debug(f"Message from RoR server: {chat_message}")

    async def run(self,
                      username="DiscordBot",
                      user_token="",
                      language="en-US",
                      client_name="discord",
                      client_version="1.0"):
        """
        Connect to the RoR server.

        :param username: Username to use for connection
        :param user_token: Authentication token (if required)
        :param language: Language code
        :return: True if connected successfully, False otherwise
        """
        try:
            # Create user info structure
            # Make sure to encode strings to bytes and truncate to max length
            user_info = UserInfo()
            user_info.uniqueid = 0  # Will be assigned by server
            user_info.authstatus = 0  # Not authenticated
            user_info.slotnum = -1  # Not assigned yet
            user_info.colournum = 0  # Default color
            user_info.username = username[:39].encode('utf-8')  # Max 40 chars (null-terminated)
            user_info.usertoken = user_token[:39].encode('utf-8')
            user_info.serverpassword = self.password[:39].encode('utf-8')
            user_info.language = language[:9].encode('utf-8')
            user_info.clientname = client_name[:9].encode('utf-8')
            user_info.clientversion = client_version[:24].encode('utf-8')
            user_info.clientGUID = b""  # Empty GUID
            user_info.sessiontype = b"normal"
            user_info.sessionoptions = b""

            # Create server info (will be populated by server response)
            server_info = ServerInfo()

            # Connect to server
            await self.stream.connect(
                user_info,
                server_info
            )

            self.running = True
            self.logger.info(f"Client connected to {self.host}:{self.port}")
            while self.running:
                await asyncio.sleep(1)

        except Exception as e:
            self.logger.error(f"Failed to connect to {self.host}:{self.port}: "
                              f"{e}")
            return False

    def is_connected(self):
        return self.stream.connected

    def register_message_handler(self, handler):
        """
        Register a custom handler for incoming messages.

        :param handler: Async function that takes (chat_message) as parameter
        """
        self.stream.register_event_handler('on_message', handler)
