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
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class ServerModel:
    """
    The Server dataclass represents the metadata for a Rigs of Rods server
    that interacts with Discord.

    :param name: Server name
    :param guild_id: Discord guild ID
    :param channel_id: Discord channel ID
    :param language: Language

    :param host: Server host
    :param port: Server port
    :param password: Optional server password
    :param created_at: Timestamp when the server entry was created
    """
    name: str
    guild_id: int
    channel_id: int
    host: str
    port: int
    password: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
