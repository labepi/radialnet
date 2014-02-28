# vim: set fileencoding=utf-8 :

# Copyright (C) 2008 Joao Paulo de Souza Medeiros
#
# Author(s): Joao Paulo de Souza Medeiros <ignotus21@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import os
import ConfigParser

from core.Path import path


class Config:
    """
    """
    def __init__(self, file="config.cfg"):
        """
        """
        self.__file = os.path.join(path.get_dirbase(), file)

        self.__handle = ConfigParser.ConfigParser()
        self.__handle.read(self.__file)


    def get_value(self, section, field):
        """
        """
        try:
            return self.__handle.get(section, field)

        except:
            return None


config = Config()
