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
import logging
import logging.handlers

from rorserverbot.config import Config
from rorserverbot import __version__
from rorserverbot.const import (
    CONFIG_FILE_PATH,
    LOG_FILE_PATH,
    DATABASE_FILE_PATH
)

import discord
from discord.ext import commands
from aiohttp import ClientSession
from config import Config


LOG = logging.getLogger('rorserverbot.bot')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'



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


def set_logger()


def print_version():
    """
    Print the version and quit.

    :return: None
    :rtype: None
    """
    sys.stderr.write("RoRServerBot version\n")
    sys.stderr.write("\n")


async def main():
    parser = argparse.ArgumentParser(
        description="",
        formatter_class=RawTextHelpFormatter)
    parser.add_argument("--config",
                        help="Path to the configuration file",
                        default=CONFIG_FILE_PATH)
    parser.add_argument("--version",
                        help="Print the version and quit")
    parser.add_argument("--verbose", action="store_true",
                        help="Enable verbose logging output")
    args = parser.parse_args()

    if args.version:
        print_version()
        return

    config = Config(args.config)

    loggers_list = ['rorserverbot', 'discord', 'aiohttp', 'asyncio']
    if args.verbose:
        for logger_name in loggers_list:


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
