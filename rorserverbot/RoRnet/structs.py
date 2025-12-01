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


class BaseStructure(Structure):
    """Base structure with helper methods 
    for RoRnet structures.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize structure fields.

        :param args: Positional arguments for fields.
        :param kwargs: Keyword arguments for fields.

        :return: None
        :rtype: None

        :raises AttributeError: If a field name is invalid.
        """
        super().__init__()

        field_names = [name for name, _ in self._fields_]

        for i, key in enumerate(args):
            self._set_field(field_names[i], key)
        
        for key, value in kwargs.items():
            if key not in field_names:
                raise AttributeError(f"{self.__class__.__name__} has no field "
                                     f"'{key}'")
            self._set_field(key, value)

    def _set_field(self, field_name, value):
        """
        Set field value, handling string/bytes conversion.
        :param field_name: Name of the field.
        :param value: Value to set.

        :return: None
        :rtype: None
        """
        ctype = dict(self._fields_)[field_name]
        if hasattr(ctype, "_length_") and ctype._type_ is c_char:
            if isinstance(value, str):
                value = value.encode("utf-8", errors="replace")

            if isinstance(value, (bytes, bytearray)):
                length = ctype._length_
                value = value.ljust(length, b"\x00")[:length]

            setattr(self, field_name, value)
            return

        setattr(self, field_name, value)

    def as_bytes(self, field_name):
        """
        Get field value as bytes, stripping null terminators.
        :param field_name: Name of the field.
        :return: Field value as bytes.
        :rtype: bytes
        """
        return getattr(self, field_name).rstrip(b"\x00")
    
    def as_str(self, field_name):
        """
        Get field value as string, decoding from bytes.
        :param field_name: Name of the field.
        :return: Field value as string.
        :rtype: str
        """
        return self.as_bytes(field_name).decode("utf-8", errors="replace")

    def to_dict(self):
        """
        Convert structure fields to a dictionary.
        :return: Dictionary of field names and values.
        :rtype: dict
        """
        out = {}
        for name, ctype in self._fields_:
            if hasattr(ctype, "_length_") and ctype._type_ is c_char:
                out[name] = self.as_str(name)
            else:
                out[name] = getattr(self, name)
        return out


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


class UserInfo(BaseStructure):
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


class ServerInfo(BaseStructure):
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
