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
        it; otherwise, we let them know we could not find the server.

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
        Add a server.
        """
        # channel_id = ctx.channel.id

    @commands.hybrid_command()
    async def remove(self, ctx):
        """
        Remove a server.
        """
        await ctx.send("test")

    async def cog_load(self):
        self.logger.info("Servers extension loaded.")


async def setup(bot):
    await bot.add_cog(Servers(bot))
