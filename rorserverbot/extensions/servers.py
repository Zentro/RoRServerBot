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
import logging

from typing import Dict
from dataclasses import dataclass

from rorserverbot import Client, Config, DataManager
from ..RoRnet import UserInfo, ServerInfo

# import discord
from discord.ext import commands


LOG = logging.getLogger('rorserverbot.ext.servers')


@dataclass
class Server:
    """
    Data class to hold server information.

    :ivar name: The name of the server.
    :ivar host: The hostname or IP address of the server.
    :ivar port: The port number of the server.
    :ivar channel_id: The Discord channel ID associated with the server.
    :ivar client: The Client instance managing the connection to the server.
    """
    name: str
    host: str
    port: int
    channel_id: int
    client: Client


class Servers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config: Config = bot.config
        self.dbm: DataManager = bot.dbm
        self.servers: Dict[str, Server] = {}

    async def _create_connection(
        self,
        name: str,
        host: str,
        port: int,
        channel_id: int
    ) -> Server:
        """
        Create a connection to a server and return a Server instance.

        :param name: The name of the server.
        :type name: str

        :param host: The hostname or IP address of the server.
        :type host: str

        :param port: The port number of the server.
        :type port: int

        :param channel_id: The Discord channel ID associated with the server.
        :type channel_id: int

        :return: A Server instance representing the connected server.
        """
        logger = logging.getLogger(f'rorserverbot.server.{name}')
        client = Client(logger=logger, host=host, port=port)

        client.register_event_handler('on_connect',
                                      lambda *args: self._on_connect(name,
                                                                     *args))
        client.register_event_handler('on_disconnect',
                                      lambda *args: self._on_disconnect(name,
                                                                        *args))
        client.register_event_handler('on_message',
                                      lambda *args: self._on_message(name,
                                                                     *args))

        server = Server(
            name=name,
            host=host,
            port=port,
            channel_id=channel_id,
            client=client
        )

        return server

    async def _connect_server(
        self,
        name: str,
        host: str,
        port: int,
        channel_id: int,
        user_info: UserInfo,
        server_info: ServerInfo
    ):
        """
        Create and connect to a server.

        :param name: The name of the server.
        :type name: str

        :param host: The hostname or IP address of the server.
        :type host: str

        :param port: The port number of the server.
        :type port: int

        :param user_info: User information for the connection.
        :type user_info: UserInfo

        :param server_info: Server information for the connection.
        :type server_info: ServerInfo

        :param channel_id: The Discord channel ID associated with the server.
        :type channel_id: int
        """
        server = await self._create_connection(
            name=name,
            host=host,
            port=port,
            channel_id=channel_id
        )

        try:
            await server.client.connect(
                user_info=user_info,
                server_info=server_info
            )
            self.servers[name] = server
        except Exception as e:
            raise e

    async def _on_connect(self, name: str, user_info, server_info):
        """
        Handle the event when the server connects.

        :param name: The name of the server that connected.
        :type name: str

        :return: None
        :rtype: None
        """
        server = self.servers.get(name)
        if server:
            channel = self.bot.get_channel(server.channel_id)
            if channel:
                await channel.send(f"Connected to server {name} at "
                                   f"{server.host}:{server.port}")

    async def _on_disconnect(self, name: str):
        """
        Handle the event when the server disconnects.

        :param name: The name of the server that disconnected.
        :type name: str

        :return: None
        :rtype: None
        """
        server = self.servers.get(name)
        if server:
            channel = self.bot.get_channel(server.channel_id)
            if channel:
                await channel.send(f"Disconnected from {name} at "
                                   f"{server.host}:{server.port}")

    async def _on_message(self, name: str, message: str):
        """
        Handle the event when a messgage is sent on the server.

        :param name: The name of the server that sent the message.
        :type name: str

        :param message: The message sent.
        :type message: str

        :return: None
        :rtype: None
        """
        server = self.servers.get(name)
        if server:
            channel = self.bot.get_channel(server.channel_id)
            if channel:
                await channel.send(f"💬 {message}")

    @commands.hybrid_command()
    async def connect(self, ctx):
        """
        Connect to a server based on the current channel.

        The command checks against the daabase for a server associated with the
        current Discord channel. If a server is found, let them know we found
        it; otherwise, we let them know we could not find the server and add it
        to the connection pool.

        Args:
            ctx (commands.Context): The context of the command invocation.

        Database:
            - Table: servers
            - Columns channel, ip

        Behavior:
            - Queries the database for a matching `channel`.

        Example Usage:
            ```
            /connect
            ```

        Note:
            - Nothing to note.
        """
        name = "RoR_Server"
        host = "rorservers.com"
        port = 12000
        username = "DiscordUser"
        password = ""

        user_info = UserInfo()
        user_info.username = username.encode('utf-8').ljust(40, b'\x00')
        user_info.serverpassword = password.encode('utf-8').ljust(40, b'\x00')
        user_info.uniqueid = 0
        user_info.language = b'en-US'.ljust(10, b'\x00')
        user_info.clientname = b'DiscordBot'.ljust(10, b'\x00')
        user_info.clientversion = b'1.0'.ljust(25, b'\x00')
        user_info.clientGUID = b'discord-bot'.ljust(40, b'\x00')
        user_info.sessiontype = b'normal'.ljust(10, b'\x00')
        user_info.sessionoptions = b''.ljust(128, b'\x00')
        user_info.authstatus = 0
        user_info.slotnum = 0
        user_info.colournum = 0
        user_info.usertoken = b''.ljust(40, b'\x00')

        # Create ServerInfo
        server_info = ServerInfo()
        server_info.host = host.encode('utf-8')
        server_info.port = port

        success = await self._connect_server(
            name=name,
            host=host,
            port=port,
            channel_id=ctx.channel.id,
            user_info=user_info,
            server_info=server_info
        )
        await ctx.send("Connected to server!" if success else "Failed to connect to server.")

    @commands.hybrid_command()
    async def add(self, ctx, ip: str, password: str):
        """
        Add a server to the database associated with the current Discord
        channel.

        This command allows users to register a server by providing an IP and
        a password. The channel where the command is used will be linked to
        the server.

        This command does't assume the server is already alive, but it will
        attempt to connect and add it to the connection pool.

        Args:
            ctx (commands.Context): The context of the command invocation.
            ip (str): The IP address of the server to add.
            password (str): The password for the server.

        Database:
            - Table: servers
            - Columns: channel (int), ip (str), password (str)

        Behavior:
            - Inserts a new server entry into the database, associating it
              with the channel.

        Example Usage:
            ```
            /add 192.168.1.100:12000 mypassword
            ```

        Note:
            - If a server is already registered for the channel, consider
              updating it instead.
        """
        # channel_id = ctx.channel.id

    @commands.hybrid_command()
    async def remove(self, ctx):
        """
        Remove the server associated with the current Discord channel.

        This command deletes the entry in the database that links the current
        channel to a server.

        If the server is still connected, the connection will be stopped
        first.

        Args:
            ctx (commands.Context): The context of the command invocation.

        Database:
            - Table: servers
            - Columns: channel, ip, password

        Behavior:
            - Deletes the server entry associated with the channel from the
              database.

        Example Usage:
            ```
            /remove
            ```

        Note:
            - If no server is registered for the channel, an error message
              will be displayed.
        """
        await ctx.send("test")

    async def cog_load(self):
        LOG.info("Servers extension loaded.")


async def setup(bot):
    await bot.add_cog(Servers(bot))
