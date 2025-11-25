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
from dataclasses import dataclass
from ctypes import Structure, c_uint32, c_int32, c_float, c_char, c_uint8


@dataclass
class Header(Structure):
    _fields_ = [
        ("command", c_uint32),
        ("source", c_int32),
        ("streamid", c_uint32),
        ("size", c_uint32)
    ]


@dataclass
class StreamRegister(Structure):
    _fields_ = [
        ("type", c_int32),
        ("status", c_int32),
        ("origin_sourceid", c_int32),
        ("origin_streamid", c_int32),
        ("name", c_char * 128),
        ("data", c_char * 128)
    ]


@dataclass
class ActorStreamRegister(Structure):
    _fields_ = [
        ("type", c_int32),
        ("status", c_int32),
        ("origin_sourceid", c_int32),
        ("origin_streamid", c_int32),
        ("name", c_char * 128),
        ("bufferSize", c_int32),
        ("time", c_int32),
        ("skin", c_char * 60),
        ("sectionconfig", c_char * 60)
    ]


@dataclass
class StreamUnRegister(Structure):
    _fields_ = [
        ("streamid", c_uint32)
    ]


@dataclass
class UserInfo(Structure):
    _fields_ = [
        ("uniqueid", c_uint32),
        ("authstatus", c_int32),
        ("slotnum", c_int32),
        ("colournum", c_int32),
        ("username", c_char * 40),
        ("usertoken", c_char * 40),
        ("serverpassword", c_char * 40),
        ("language", c_char * 10),
        ("clientname", c_char * 10),
        ("clientversion", c_char * 25),
        ("clientGUID", c_char * 40),
        ("sessiontype", c_char * 10),
        ("sessionoptions", c_char * 128)
    ]


@dataclass
class VehicleState(Structure):
    _fields_ = [
        ("time", c_int32),
        ("engine_speed", c_float),
        ("engine_force", c_float),
        ("engine_clutch", c_float),
        ("engine_gear", c_int32),
        ("hydrodirstate", c_float),
        ("brake", c_float),
        ("wheelspeed", c_float),
        ("flagmask", c_uint32)
    ]


@dataclass
class ServerInfo(Structure):
    _fields_ = [
        ("protocolversion", c_char * 20),
        ("terrain", c_char * 128),
        ("servername", c_char * 128),
        ("has_password", c_uint8),
        ("info", c_char * 4096)
    ]


@dataclass
class LegacyServerInfo(Structure):
    _fields_ = [
        ("protocolversion", c_char * 20)
    ]
