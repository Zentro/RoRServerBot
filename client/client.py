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

from connection import Connection


class Client():
    """
    """

    def __init__(self, logger, host, port, channel_id):
        self.logger = logger
        self.server = Connection(logger, host, port)
        self.channel_id = channel_id
        self.running = True

    async def send_message(self, content):
        """
        """

    async def send_event(self, content):
        """
        """

    def run(self):
        """
        """
