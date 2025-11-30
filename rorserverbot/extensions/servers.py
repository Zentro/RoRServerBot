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

from rorserverbot import Client, DataManager
from rorserverbot.models import ServerModel
from rorserverbot.util import danger_message, sucess_message

# import discord
from discord.ext import commands


LOG = logging.getLogger('RoRBot.ext.servers')


class Servers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dbm: DataManager = bot.dbm
        self.servers: Dict[int, Client] = {}

    async def _load_servers_from_db(self):
        """
        Load servers from the database and populate the servers dictionary.

        :return: None
        :rtype: None
        """
        servers = await self.dbm.select_all(ServerModel)
        for server in servers:
            LOG.info(f"Found {server.name} from database.")
            await self._connect_client(
                name=server.name,
                host=server.host,
                port=server.port,
                channel_id=server.channel_id
            )

    async def _create_client(
        self,
        name: str,
        host: str,
        port: int,
        channel_id: int
    ) -> Client:
        """
        Create a connection to a server and return a Server instance.

        :param name: The name of the server.
        :type name: str

        :param host: The hostname or IP address of the server.
        :type host: str

        :param port: The port number of the server.
        :type port: int

        :param channel_id: The channel ID associated with the server.
        :type channel_id: int

        :return: A Server instance representing the connected server.
        """
        logger = logging.getLogger(f'RoRBot.server.{channel_id}')
        client = Client(logger=logger, host=host, port=port)

        client.register_event_handler('on_connect',
                                      lambda *args: 
                                      self._on_connect(channel_id, *args))
        client.register_event_handler('on_disconnect',
                                      lambda *args:
                                      self._on_disconnect(channel_id, *args))
        client.register_event_handler('on_message',
                                      lambda *args:
                                      self._on_message(channel_id, *args))
        client.register_event_handler('on_event',
                                      lambda *args:
                                      self._on_event(channel_id, *args))
        return client

    async def _connect_client(
        self,
        name: str,
        host: str,
        port: int,
        channel_id: int,
    ):
        """
        Create and connect to a server.

        :param name: The name of the server.
        :type name: str

        :param host: The hostname or IP address of the server.
        :type host: str

        :param port: The port number of the server.
        :type port: int

        :param channel_id: The Discord channel ID associated with the server.
        :type channel_id: int
        """
        client = await self._create_client(
            name=name,
            host=host,
            port=port,
            channel_id=channel_id
        )
        try:
            await client.connect()
            self.servers[channel_id] = client
        except Exception as e:
            raise e

    async def _on_connect(self, channel_id: int):
        """
        Handle the event when the server connects.

        :param channel_id: The channel ID of the client that connected.
        :type channel_id: int

        :return: None
        :rtype: None
        """
        server = self.servers.get(channel_id)
        if server:
            channel = self.bot.get_channel(channel_id)
            if channel:
                await channel.send(f"Connected to {server.host}:{server.port}")

    async def _on_disconnect(self, channel_id: int):
        """
        Handle the event when the server disconnects.

        :param channel_id: The channel ID of the server that disconnected.
        :type channel_id: int

        :return: None
        :rtype: None
        """
        server = self.servers.get(channel_id)
        if server:
            channel = self.bot.get_channel(channel_id)
            server.client = None
            if channel:
                await channel.send(f"Disconnected from "
                                   f"{server.host}:{server.port}")

    async def _on_message(self, channel_id: int, message: str):
        """
        Handle the event when a messgage is sent on the server.

        :param name: The name of the server that sent the message.
        :type name: str

        :param message: The message sent.
        :type message: str

        :return: None
        :rtype: None
        """
        server = self.servers.get(channel_id)
        if server:
            channel = self.bot.get_channel(channel_id)
            if channel:
                await channel.send(f"💬 {message}")

    async def _on_event(self):
        """
        """
        pass

    @commands.hybrid_command()
    @commands.has_permissions(administrator=True)
    async def create_server(self, ctx, name: str, host: str, port: int):
        """
        Create a server based on the current channel.

        This command creates a new server based on the the provided name, host,
        and port, and associates it with the current Discord channel.

        Args:
            ctx (commands.Context): The context of the command invocation.
            name (str): The name of the server.
            host (str): The hostname or IP address of the server.
            port (int): The port number of the server.

        Behavior:
            - Creates a new server connection and adds it to the connection
              pool.

        Example Usage:
            ```
            /create_server MyServer rorservers.com 12000
            ```

        Note:
            - Ensure that the provided host and port are correct and that
              the server is reachable.
        """
        channel_id = ctx.channel.id
        guild_id = ctx.guild.id

        # Check if a server already exists for this channel
        servers = await self.dbm.select(
            ServerModel,
            where_field='channel_id',
            value=channel_id
        )

        if len(servers) > 0:
            ctx.reply('A server is already registered for this channel.')
            return

        # Create the server entry in the database
        server = ServerModel(
            name=name,
            guild_id=guild_id,
            channel_id=channel_id,
            host=host,
            port=port
        )

        try:
            await self.dbm.insert(server)
            await ctx.reply('Server was created and is now registered with '
                            'this channel. You can now use the '
                            '**connect** command to connect to it.')
        except Exception as e:
            LOG.error(f"Failed to create server: {e}")
            await ctx.reply('An unexpected error occurred while creating the '
                            'server. Please try again later.')

    @commands.hybrid_command()
    @commands.has_permissions(administrator=True)
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
            - Columns: name, channel, ip

        Behavior:
            - Queries the database for a matching `channel`.

        Example Usage:
            ```
            /connect
            ```

        Note:
            - Nothing to note.
        """
        channel_id = ctx.chnnel.id

        servers = await self.dbm.select(
            ServerModel,
            where_field='channel_id',
            value=channel_id
        )

        if not servers:
            await ctx.reply('I couldn\'t find a server registered with this '
                            'channel. '
                            'Please run the **create_server** command first.')
            return

        if len(servers) > 1:
            await ctx.reply('I found more than once server registered with '
                            'this channel.')
            return

        server = servers[0]



        await ctx.reply(f'Trying to connect to **{server.name}** at '
                        f'***{server.host}:{server.port}*** ...')
    

        await self._connect_server(

        )

    @commands.hybrid_command()
    @commands.has_permissions(administrator=True)
    async def disconnect(self, ctx):
        """
        Disconnect from the server associated with the current Discord channel.

        This command looks up the server associated with the current channel
        and disconnects from it if connected.

        Args:
            ctx (commands.Context): The context of the command invocation.

        Behavior:
            - Disconnects from the server associated with the channel.

        Example Usage:
            ```
            /disconnect
            ```

        Note:
            - Nothing to note.
        """
        pass

    @commands.hybrid_command()
    @commands.has_permissions(administrator=True)
    async def delete_server(self, ctx):
        """
        Delete the server associated with the current Discord channel.

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
        channel_id = ctx.channel.id

        # Check if a server exists for this channel
        servers = await self.dbm.select(
            ServerModel,
            where_field='channel_id',
            value=channel_id
        )

        if not servers:
            await ctx.reply(
                danger_message(
                    'No server found for this channel. '
                    'Use **/create_server** to create one first.'
                )
            )
            return

        server = servers[0]

        # If server is connected, disconnect it first
        if server.name in self.servers and self.servers[server.name].client:
            try:
                await self.servers[server.name].client.disconnect()
                del self.servers[server.name]
            except Exception as e:
                LOG.warning(f"Error disconnecting server during deletion: {e}")

        # Delete from database
        try:
            await self.dbm.delete(
                ServerModel,
                where_field='channel_id',
                value=channel_id
            )
            await ctx.reply(
                sucess_message(
                    f'Server **{server.name}** has been deleted from this channel.'
                )
            )
        except Exception as e:
            LOG.error(f"Failed to delete server: {e}")
            await ctx.reply(
                danger_message(
                    f'Failed to delete server: {str(e)}'
                )
            )

    @commands.hybrid_command()
    @commands.has_permissions(administrator=True)
    async def list_servers(self, ctx):
        """
        List all servers associated with the current Discord channel.

        This command displays information about servers registered for this
        channel, including their connection status.

        Args:
            ctx (commands.Context): The context of the command invocation.

        Behavior:
            - Lists all servers registered for the current channel.
            - Shows server name, host, port, and connection status.

        Example Usage:
            ```
            /list_servers
            ```

        Note:
            - Only one server per channel is allowed, so this will typically
              show zero or one server.
        """
        channel_id = ctx.channel.id

        # Get all servers for this channel
        servers = await self.dbm.select(
            ServerModel,
            where_field='channel_id',
            value=channel_id
        )

        if not servers:
            await ctx.reply(
                danger_message(
                    'No servers found for this channel. '
                    'Use **/create_server** to create one.'
                )
            )
            return

        # Build response message
        message_parts = ['**Servers for this channel:**\n']

        for server in servers:
            # Check connection status
            is_connected = (server.name in self.servers and
                          self.servers[server.name].client is not None)
            status = '🟢 Connected' if is_connected else '🔴 Disconnected'

            message_parts.append(
                f'\n**{server.name}**\n'
                f'  • Host: `{server.host}:{server.port}`\n'
                f'  • Status: {status}\n'
            )

        await ctx.reply('\n'.join(message_parts))

    async def cog_load(self):
        LOG.info("Servers extension loaded.")
        # Look for servers in the database and load them...
        await self._load_servers_from_db()


async def setup(bot):
    await bot.add_cog(Servers(bot))
