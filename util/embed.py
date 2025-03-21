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
import discord


def system_message(title: str, description: str, color=discord.Color.blue()):
    """
    """
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    return embed


def error_message(title: str, description: str):
    """
    """
    return system_message(title, description, discord.Color.red())
