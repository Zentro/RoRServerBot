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


from pathlib import Path
from typing import OrderedDict

from rorserverbot.const import (
    DEFAULT_CONFIG_FILE,
    DEFAULT_LOG_FILE,
    DEFAULT_DB_FILE,
    DEFAULT_DISCORD_COMMAND_PREFIX,
)

import yaml


class Config:
    """Config manager.
    """

    OPTION_DEFAULTS = OrderedDict(
        ('name', None),
        ('verbose', False),
        ('discord.token', None),
        ('discord.command_prefix', DEFAULT_DISCORD_COMMAND_PREFIX),
        ('db_file', DEFAULT_DB_FILE),
        ('log_file', DEFAULT_LOG_FILE),
    )

    name: str = "RoRBot"
    verbose: bool = False
    discord_token: str = None
    discord_command_prefix: str = "!"
    language: str = "en"
    db_file_path: str = "/var/lib/rorserverbot/rorserverbot.db"
    log_file_path: str = "/var/log/rorserverbot/rorserverbot.log"

    def __init__(self, path: Path):
        self.path: Path = path
        # if self.path.exists():
        #     raise FileNotFoundError(
        #         f'Config file not found: {self.path}'
        #     )

        with self.path.open('r') as f:
            data = yaml.safe_load(f)

        annotations = self.__class__.__annotations__
        for key, value in data.items():
            # Check for unexpected keys
            if key not in annotations:
                raise ValueError(f"Unexpected key: {key}")

            # Type checking, if annotation exists
            expected_type = annotations[key]
            if expected_type is not None and not isinstance(value,
                                                            expected_type):
                raise ValueError(
                    f"Invalid type for '{key}': expected "
                    f"{expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )

            setattr(self, key, value)

    def __repr__(self):
        return f"<Config path={self.path}>"
