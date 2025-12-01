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
import ctypes
import struct
from ctypes import c_char, _SimpleCData


STRUCT_FORMAT = {
    # 1 byte
    ctypes.c_uint8: "B",
    ctypes.c_int8:  "b",

    # 2 bytes
    ctypes.c_uint16: "H",
    ctypes.c_int16:  "h",

    # 4 bytes
    ctypes.c_uint32: "I",
    ctypes.c_int32:  "i",
    ctypes.c_float:  "f",
    
    # booleans
    ctypes.c_bool: "?",
}


def get_struct_format(struct_cls):
    """
    Get the struct format string for the given structure class.
    :param struct_cls: The structure class.
    :return: The struct format string.
    :rtype: str
    """
    fmt = ""
    for name, ctype in struct_cls._fields_:

        # c_char * N
        if hasattr(ctype, "_length_") and ctype._type_ is c_char:
            fmt += f"{ctype._length_}s"
            continue

        # Simple numeric types (c_uint8, c_int32, c_float, etc.)
        if issubclass(ctype, _SimpleCData):
            # mapping: c_uint8 -> B, c_int32 -> i, c_uint32 -> I, etc.
            fmt += STRUCT_FORMAT[ctype]
            continue

        raise TypeError(f"Unsupported field type: {ctype}")

    return fmt


def unpack_to_struct(struct_cls, data):
    """
    Unpack binary data into an instance of the given structure class.
    :param struct_cls: The structure class to unpack into.
    :param data: The binary data to unpack.

    :return: An instance of struct_cls populated with unpacked data.
    :rtype: struct_cls
    """
    fmt = get_struct_format(struct_cls)
    fields = struct.unpack(fmt, data)

    return struct_cls(*fields)


def pack_from_struct(instance):
    """
    Pack an instance of a structure class into binary data.
    :param instance: The structure instance to pack.

    :return: The packed binary data.
    :rtype: bytes
    """
    fmt = get_struct_format(instance.__class__)
    values = []

    for name, ctype in instance._fields_:

        field_value = getattr(instance, name)

        # c_char arrays
        if hasattr(ctype, "_length_") and ctype._type_ is c_char:
            # ensure bytes
            if isinstance(field_value, str):
                field_value = field_value.encode("utf-8", errors="replace")
            field_value = field_value.ljust(ctype._length_,
                                            b"\x00")[:ctype._length_]
            values.append(field_value)
            continue

        # numeric fields
        values.append(field_value)

    return struct.pack(fmt, *values)
