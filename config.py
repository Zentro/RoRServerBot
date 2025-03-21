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

import yaml
import logging


class Config:
    _config = None

    @staticmethod
    def load_config(file_path="config.yaml"):
        """
        Load the YAML configuration file into memory.

        Args:
            file_path(str): The path to the YAML configuration file.
                            Defaults to 'config.yaml'.

        Raises:
            FileNotFoundError: If the configuration file is not found at the
                               given path.
            yaml.YAMLError: If there is an error in parsing the YAML file.

        """
        with open(file_path, "r") as f:
            Config._config = yaml.safe_load(f)

    @staticmethod
    def get_config():
        """
        Retrieve the loaded configuration data.

        Returns:
            dict: The loaded configuration as a dictionary.

        Raises:
            RuntimeError: If the configuration has not been loaded yet.
        """
        if Config._config is None:
            raise RuntimeError("")
        return Config._config

    @staticmethod
    def get_logging_level():
        """
        Convert the logging level from the configuration file to a `logging`
        module constant.

        Returns:
            int: Corresponding logging level
                 (ex., `logging.INFO`, `logging.ERROR`).

        Raises:
            KeyError: If the logging level is not defined in the configuration.
            ValueError: If the logging level in the configuration is invalid.
        """
        if Config._config is None:
            raise RuntimeError(
                "Configuration not loaded. Call `load_config` first.")
        log_level_str = Config._config.get("logging", {}).get("level", "info")
        log_levels = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL
        }

        if log_level_str not in log_levels:
            raise ValueError(f"Invalid logging level: {log_level_str}")
        return log_levels[log_level_str]
