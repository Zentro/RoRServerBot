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
import socket
import struct


class Connection():
    def __init__(self, stream, logger):
        self.logger = logger
        self.socket = None
        self.reader = None
        self.writer = None

    def connected(self) -> bool:
        """
        """
        return self.socket is not None

    def knock(self, host, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as error_message:
            print(error_message)
            sock = None
            return None

        sock.settimeout(2)

        try:
            sock.connect((u"%s", host, port))
        except socket.error as error_message:
            print(error_message)
            sock.close()
            sock = None
            return None

        data = "MasterServer"
        try:
            sock.send(struct.pack('IIII'+str(len(data))+'s', MSG2_HELLO, 5000, 0, len(data), str(data)))
        except Exception as e:
            print(e)
            return None
