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


def system_message(title: str | None = None,
                   description: str | None = None,
                   color: discord.Colour | None = None):
    """
    Create a standard embed for system messages.

    :param title: The title of the embed
    :type title: str
    :param description: The description of the embed
    :type description: str
    :param color: The color of the embed
    :type color: discord.Color
    :return: The embed
    :rtype: discord.Embed
    """
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    return embed


def danger_message(title: str | None = None,
                   description: str | None = None):
    """
    Create a standard embed for danger messages.
    :param title: The title of the embed
    :type title: str
    :param description: The description of the embed
    :type description: str
    :return: The embed
    :rtype: discord.Embed
    """
    return system_message(title, description, discord.Color.red())


def sucess_message(title: str | None = None,
                   description: str | None = None):
    """
    Create a standard embed for sucess messages.
    :param title: The title of the embed
    :type title: str
    :param description: The description of the embed
    :type description: str
    :return: The embed
    :rtype: discord.Embed
    """
    return system_message(title, description, discord.Color.green())
