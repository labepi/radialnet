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

import gtk
import bestwidgets as bw
import gui.BackendForm as Backend

from core.I18n import _


DIMENSION = (640, 400)

BACKEND_NMAP = 0


class ScanToolbar(gtk.Toolbar):
    """
    """
    def __init__(self, window):
        """
        """
        gtk.Toolbar.__init__(self)
        self.set_style(gtk.TOOLBAR_BOTH_HORIZ)
        self.set_tooltips(True)

        self.__window = window

        self.__create_widgets()


    def __create_widgets(self):
        """
        """
        self.__tooltips = gtk.Tooltips()

        self.__nmap = gtk.RadioToolButton(None, gtk.STOCK_FIND)
        self.__nmap.set_label('Nmap')
        self.__nmap.set_is_important(True)
        self.__nmap.connect('toggled', self.__backend_callback, BACKEND_NMAP)
        self.__nmap.set_tooltip(self.__tooltips, _("Nmap as backend"))
        self.__nmap.set_active(True)

        self.__backend_callback(self.__nmap, BACKEND_NMAP)

        self.insert(self.__nmap,    0)


    def __backend_callback(self, widget, backend):
        """
        """
        self.__window.set_backend(backend)



class ScanDialog(bw.BWMainWindow):
    """
    """
    def __init__(self, window):
        """
        """
        bw.BWMainWindow.__init__(self)
        self.set_title(_("Scan"))
        self.set_default_size(DIMENSION[0], DIMENSION[1])

        self.__backend = None
        self.__window = window

        self.set_position(gtk.WIN_POS_CENTER)

        self.__create_widgets()


    def __create_widgets(self):
        """
        """
        self.__vbox = bw.BWVBox()
        self.__frame = bw.BWFrame(_("Scan form:"))
        self.__toolbar = ScanToolbar(self)

        self.__vbox.bw_pack_start_noexpand_nofill(self.__toolbar)
        self.__vbox.bw_pack_start_expand_fill(self.__frame)

        self.add(self.__vbox)


    def set_backend(self, backend):
        """
        """
        if backend == BACKEND_NMAP:

            if self.__backend:
                self.__frame.bw_remove(self.__backend)

            self.__backend = Backend.Nmap(self.__window)
            self.__frame.bw_add(self.__backend)

            self.__frame.show_all()



if __name__ == "__main__":

    d = ScanDialog(None)
    d.show_all()

    d.connect('destroy', gtk.main_quit)

    gtk.main()
