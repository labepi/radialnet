# vim: set fileencoding=utf-8 :

# Copyright (C) 2012-2014 Joao Paulo de Souza Medeiros
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
import locale
import gettext

from core.Path import path


LOCALE_DIR = os.path.join(path.get_dirbase(), "share/locale")


try:
    LC_ALL = locale.setlocale(locale.LC_ALL, "")

except locale.Error:
    LC_ALL = locale.setlocale(locale.LC_ALL, None)


LANGUAGE, ENCODING = locale.getdefaultlocale()

if LANGUAGE == None:
    LANGUAGE = "en_US"

if ENCODING == None:
    ENCODING = "utf8"


translation = gettext.translation("radialnet",
                                  LOCALE_DIR,
                                  [LANGUAGE],
                                  fallback=True)

_ = translation.gettext



if __name__ == "__main__":


    print _("RadialNet supports i18n.")
