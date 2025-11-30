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
import sys
import argparse
from argparse import RawTextHelpFormatter
from typing import List
from pathlib import Path
import logging

from rorserverbot import Config, DataManager, __version__
from .logger import set_up_logger
from .models import ServerModel
from .const import (
    CONFIG_FILE_PATH,
    LOG_FILE_PATH,
    DATABASE_FILE_PATH
)

import discord
from discord.ext import commands
from aiohttp import ClientSession


LOG = logging.getLogger('RoRBot.bot')
LOG_FORMAT = (
    '%(asctime)s - %(name)s - %(levelname)s - (%(thread)d) - %(message)s'
)


class Main(commands.Bot):
    def __init__(
            self,
            *args,
            initial_extensions: List[str],
            logger: logging.Logger,
            config: Config,
            dbm: DataManager,
            web_client: ClientSession,
            **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_extensions = initial_extensions
        self.logger = logger
        self.config = config
        self.dbm = dbm
        self.web_client = web_client

    def get_config_variable(self, name: str):
        """Get a config variable by name.

        :param name: Name of the config variable to get.
        :type name: str
        :return: The config variable value.
        :rtype: Any
        """
        return getattr(self.config, name, None)

    async def setup_hook(self) -> None:
        # await self.tree.sync(guild=None)
        # Load the extenions prior to sync to ensure we are syncing
        # interactions defined in the extensions...
        for extension in self.initial_extensions:
            try:
                await self.load_extension(extension)
            except Exception as e:
                self.logger.error(f"Error loading extension {extension}: {e}")

    async def close(self):
        await super().close()
        await self.dbm.close()
        await self.web_client.close()


def print_version():
    """
    Print the version and quit.

    :return: None
    :rtype: None
    """
    sys.stderr.write(f"RoRBot version: {__version__}\n")
    sys.stderr.write("\n")


async def main():
    parser = argparse.ArgumentParser(
        description="",
        formatter_class=RawTextHelpFormatter)
    parser.add_argument("--config",
                        help="Path to the config file",
                        default=CONFIG_FILE_PATH)
    parser.add_argument("--db-file",
                        help="Path to the database file",
                        default=DATABASE_FILE_PATH)
    parser.add_argument("--log-file",
                        help="Path to the log file",
                        default=LOG_FILE_PATH)
    parser.add_argument("--version",
                        help="Print the version and quit")
    parser.add_argument("--verbose", action="store_true",
                        help="Enable verbose logging output")
    args = parser.parse_args()
    # Handle the version flag and exit early.
    if args.version:
        print_version()
        return
    # We explictly don't want a global config object given the
    # async nature of the program. So, each class will inherit
    # an in-memory copy of the config object.
    try:
        config = Config(Path(args.config))
    except FileNotFoundError as e:
        sys.stderr.write("An unexpected error occurred:\n")
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)
    # The various libraries can have their own loggers, and we want
    # to take control of all of them to ensure consistent logging.
    loggers_list = ['RoRBot', 'discord', 'discord.http',
                    'aiohttp', 'asyncio']
    # Handle the verbose flag for logging.
    if args.verbose:
        # If the verbose flag is set, enable debug logging.
        # The 'discord.py' library can be very verbose, so we may
        # want to set that to 'INFO' instead of 'DEBUG' in the far
        # future. otherwise we expect the user wants to see the
        # verbose output for all loggers.
        for logger_name in loggers_list:
            set_up_logger(
                logger_name=logger_name,
                log_level=logging.DEBUG,
                log_file=args.log_file,
                format_string=LOG_FORMAT)
            LOG.debug('Verbose logging enabled')
            LOG.debug('RoRServerBot version: %s', __version__)
            LOG.debug('Arguments entered: %s', args)
    else:
        # Default to 'INFO' logging.
        for logger_name in loggers_list:
            set_up_logger(
                logger_name=logger_name,
                log_level=logging.INFO,
                log_file=args.log_file,
                format_string=LOG_FORMAT)
    # The user override what the config said, so apply that.
    if args.db_file:
        config.db_file_path = args.db_file
    # Create the DataManager instance, and creat the tables if
    # they do not already exist.
    dbm = DataManager(config.db_file_path)
    await dbm.connect()
    await dbm.create_table(ServerModel)
    exts = ['rorserverbot.extensions.servers']
    intents = discord.Intents.default()
    intents.message_content = True
    async with ClientSession() as our_client:
        async with Main(
            commands.when_mentioned,
            initial_extensions=exts,
            logger=LOG,
            config=config,
            dbm=dbm,
            web_client=our_client,
            intents=intents,
        ) as our_bot:
            try:
                await our_bot.start(config.discord_token)
            except (asyncio.CancelledError, KeyboardInterrupt):
                LOG.info("Received exit signal, shutdown started.")
            finally:
                try:
                    await our_bot.close()
                except KeyboardInterrupt:
                    pass
                LOG.info("Shutdown complete.")
