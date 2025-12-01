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
"""
RoRnet
~~~~~~

Rigs of Rods Network Protocol Structures and Constants.

:license: GNU GPLv3, see LICENSE for more details.
"""

__version__ = "RoRnet_2.44"

from .structs import (
    Header, StreamRegister, StreamUnRegister, UserInfo,
    VehicleState, ServerInfo
)
from .constants import MessageType, UserAuth, Netmask

__all__ = [
    "Header",
    "StreamRegister",
    "StreamUnRegister",
    "UserInfo",
    "VehicleState",
    "ServerInfo",
    "MessageType",
    "UserAuth",
    "Netmask",
]
