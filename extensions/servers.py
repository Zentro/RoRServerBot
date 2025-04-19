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
import logging

# import discord
from config import Config
from discord.ext import commands
import aiosqlite

from util import system_message


class Servers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('RoRBot.servers_extension')
        self.config = Config.get_config()
        self.clients = {}

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
        channel_id = ctx.channel.id
        async with aiosqlite.connect("rorserverbot.db") as db:
            async with db.execute("SELECT ip FROM servers WHERE channel = ?",
                                  (channel_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    # ip = row[0]
                    embed = system_message()
                    await ctx.send(embed)
                else:
                    await ctx.send("server not found")

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
        self.logger.info("Servers extension loaded.")


async def setup(bot):
    await bot.add_cog(Servers(bot))
