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
RoRServerBot
~~~~~~~~~~~~

The Rigs of Rods Server Bot for Discord.

:license: GNU GPLv3, see LICENSE for more details.

"""

__title__ = "rorserverbot"
__license__ = "GNU GPLv3"
__version__ = "2.0.0"

from .client import Client
from .config import Config
from .datamanager import DataManager

__all__ = ["Client", "Config", "DataManager"]
