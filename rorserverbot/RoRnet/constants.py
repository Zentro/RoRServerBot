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
from enum import IntEnum, IntFlag


class MessageType(IntEnum):
    MSG2_HELLO = 1025
    MSG2_FULL = 1026
    MSG2_WRONG_PW = 1027
    MSG2_WRONG_VER = 1028
    MSG2_BANNED = 1029
    MSG2_WELCOME = 1030
    MSG2_VERSION = 1031
    MSG2_SERVER_SETTINGS = 1032
    MSG2_USER_INFO = 1033
    MSG2_MASTERINFO = 1034
    MSG2_NETQUALITY = 1035
    MSG2_GAME_CMD = 1036
    MSG2_USER_JOIN = 1037
    MSG2_USER_LEAVE = 1038
    MSG2_UTF_CHAT = 1039
    MSG2_UTF_PRIVCHAT = 1040
    MSG2_STREAM_REGISTER = 1041
    MSG2_STREAM_REGISTER_RESULT = 1042
    MSG2_STREAM_UNREGISTER = 1043
    MSG2_STREAM_DATA = 1044
    MSG2_STREAM_DATA_DISCARDABLE = 1045
    MSG2_WRONG_VER_LEGACY = 1003
    MSG2_INVALID = 0


class UserAuth(IntFlag):
    AUTH_NONE = 0
    AUTH_ADMIN = 1 << (1 - 1)
    AUTH_RANKED = 1 << (2 - 1)
    AUTH_MOD = 1 << (3 - 1)
    AUTH_BOT = 1 << (4 - 1)
    AUTH_BANNED = 1 << (5 - 1)


class Netmask(IntFlag):
    NETMASK_HORN = 1 << (1 - 1)
    NETMASK_LIGHTS = 1 << (2 - 1)
    NETMASK_BRAKES = 1 << (3 - 1)
    NETMASK_REVERSE = 1 << (4 - 1)
    NETMASK_BEACONS = 1 << (5 - 1)
    NETMASK_BLINK_LEFT = 1 << (6 - 1)
    NETMASK_BLINK_RIGHT = 1 << (7 - 1)
    NETMASK_BLINK_WARN = 1 << (8 - 1)
    NETMASK_CLIGHT1 = 1 << (9 - 1)
    NETMASK_CLIGHT2 = 1 << (10 - 1)
    NETMASK_CLIGHT3 = 1 << (11 - 1)
    NETMASK_CLIGHT4 = 1 << (12 - 1)
    NETMASK_CLIGHT5 = 1 << (13 - 1)
    NETMASK_CLIGHT6 = 1 << (14 - 1)
    NETMASK_CLIGHT7 = 1 << (15 - 1)
    NETMASK_CLIGHT8 = 1 << (16 - 1)
    NETMASK_CLIGHT9 = 1 << (17 - 1)
    NETMASK_CLIGHT10 = 1 << (18 - 1)
    NETMASK_POLICEAUDIO = 1 << (19 - 1)
    NETMASK_PARTICLE = 1 << (20 - 1)
    NETMASK_PBRAKE = 1 << (21 - 1)
    NETMASK_TC_ACTIVE = 1 << (22 - 1)
    NETMASK_ALB_ACTIVE = 1 << (23 - 1)
    NETMASK_ENGINE_CONT = 1 << (24 - 1)
    NETMASK_ENGINE_RUN = 1 << (25 - 1)
    NETMASK_ENGINE_MODE_AUTOMATIC = 1 << (26 - 1)
    NETMASK_ENGINE_MODE_SEMIAUTO = 1 << (27 - 1)
    NETMASK_ENGINE_MODE_MANUAL = 1 << (28 - 1)
    NETMASK_ENGINE_MODE_MANUAL_STICK = 1 << (29 - 1)
    NETMASK_ENGINE_MODE_MANUAL_RANGES = 1 << (30 - 1)
