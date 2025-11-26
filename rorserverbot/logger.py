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


def set_up_logger(logger_name, log_level, log_file, format_string):
    """
    Set up a logger with the specified name and log level.

    :param logger_name: The name of the logger.
    :type logger_name: str

    :param log_level: The logging level (e.g., logging.DEBUG, logging.INFO).
    :type log_level: int

    :param log_file: The file path for the log file.
    :type log_file: str

    :param format_string: Optional format string for log messages.
    :type format_string: str

    :return: None
    :raisses: None
    """

    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    formatter = logging.Formatter(format_string)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
