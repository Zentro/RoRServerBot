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
import aiosqlite
import argparse
from argparse import RawTextHelpFormatter

from typing import List

import logging
import logging.handlers
import discord
from discord.ext import commands
from aiohttp import ClientSession
from config import Config


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
__version__ = "2.0.0"


class Main(commands.Bot):
    def __init__(
            self,
            *args,
            initial_extensions: List[str],
            logger: logging.Logger,
            web_client: ClientSession,
            **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_extensions = initial_extensions
        self.logger = logger
        self.web_client = web_client
        self.db = None

    async def setup_hook(self) -> None:

        # Load the extenions prior to sync to ensure we are syncing
        # interactions defined in the extensions...
        for extension in self.initial_extensions:
            try:
                await self.load_extension(extension)
            except Exception as e:
                self.logger.error(f"Error loading extension {extension}: {e}")

        # Connect to the sqlite database and establish our connection pool
        # including loading anything into memory prior to handling events...
        await self.connect_db()

    async def connect_db(self):
        """
        Establish a connection to the sqlite database.

        Raises:
            ValueError: If the database connection could not be established.
        """
        try:
            self.db = await aiosqlite.connect('rorserverbot.db')
            self.logger.info("Database connection established.")
            await self.setup_db()
        except Exception as e:
            self.logger.error(
                f"Error trying to establish connection to database: {e}")

    async def setup_db(self):
        """
        Setup the database tables if they don't already exist.

        Raises:
            Exception: If there is an issue writing to the database, such as a
                       connection issue.
        """
        async with self.db.cursor() as cursor:
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS servers (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    ip TEXT UNIQUE,
                    password TEXT NULL,
                    channel INTEGER UNIQUE,
                    active INTEGER NOT NULL CHECK (active IN (0, 1))
                );
            ''')
            await self.db.commit()
            self.logger.info("Database setup completed.")

    async def close_db(self):
        """
        Close the database connection pool.

        Raises:
            Exception: If there is an issue of safely closing the coonnection
                       pool.
        """
        if self.db:
            try:
                await self.db.close()
                self.logger.info("Database connection closed.")
            except Exception as e:
                self.logger.error(
                    f"Error closing the database connection: {e}")
            finally:
                self.db = None


def print_version_and_quit():
    """
    """


async def main():
    # ------------------------------------------------------------------------
    # Setup the command line arguments
    # ------------------------------------------------------------------------
    parser = argparse.ArgumentParser(
        description="",
        formatter_class=RawTextHelpFormatter)
    parser.add_argument("--config",
                        required=True,
                        help="Path to the configuration file")
    parser.add_argument("--version",
                        help="Print the version and quit")
    args = parser.parse_args()
    # ------------------------------------------------------------------------
    # Load the configuration file
    # ------------------------------------------------------------------------
    Config.load_config(args.config)
    config = Config.get_config()
    # ------------------------------------------------------------------------
    # Setup the logger
    # ------------------------------------------------------------------------
    # logger = logging.getLogger(config["application"]["name"])
    logger = logging.getLogger('RoRBot')
    logger.setLevel(Config.get_logging_level())
    handler = logging.handlers.RotatingFileHandler(
        filename="rorserverbot.log",
        encoding="utf-8",
        maxBytes=32 * 1024 * 1024,
        backupCount=5,
    )
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(
        '[{asctime}] [{threadName:21s}] [{levelname:<8}] {name}: {message}',
        dt_fmt, style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    # ------------------------------------------------------------------------
    # Setup the Discord bot
    # ------------------------------------------------------------------------
    exts = ['extensions.servers']
    intents = discord.Intents.default()
    intents.message_content = True
    async with ClientSession() as our_client:
        async with Main(
            commands.when_mentioned,
            initial_extensions=exts,
            logger=logger,
            web_client=our_client,
            intents=intents,
        ) as our_bot:
            await our_bot.start(config['discord']['token'])


asyncio.run(main())
