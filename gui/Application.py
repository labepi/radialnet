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

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import bestwidgets as bw

from util.integration import make_graph_from_nmap_parser
from core.Info import INFO
from core.I18n import _
from core.XMLHandler import XMLReader
from gui.ControlWidget import ControlWidget, ControlFisheye
from gui.Toolbar import Toolbar
from gui.Image import Pixmaps
from gui.RadialNet import *


DIMENSION = (640, 480)



class Application(bw.BWMainWindow):
    """
    """
    def __init__(self):
        """
        """
        bw.BWMainWindow.__init__(self)
        self.set_default_size(DIMENSION[0], DIMENSION[1])

        self.set_icon(Pixmaps().get_pixbuf('logo'))

        self.__create_widgets()


    def __create_widgets(self):
        """
        """
        self.__hbox = bw.BWHBox(spacing=0)
        self.__vbox = bw.BWVBox(spacing=0)

        self.__radialnet = RadialNet(LAYOUT_WEIGHTED)
        self.__control = ControlWidget(self.__radialnet)

        self.__control_sw = bw.BWScrolledWindow()
        self.__control_sw.add_with_viewport(self.__control)
        self.__control_sw.set_policy(Gtk.PolicyType.NEVER,
                                     Gtk.PolicyType.AUTOMATIC)

        self.__fisheye = ControlFisheye(self.__radialnet)
        self.__toolbar = Toolbar(self.__radialnet,
                                 self,
                                 self.__control_sw,
                                 self.__fisheye)
        self.__statusbar = bw.BWStatusbar()

        self.__hbox.bw_pack_start_expand_fill(self.__radialnet)
        self.__hbox.bw_pack_start_noexpand_nofill(self.__control_sw)

        self.__vbox.bw_pack_start_noexpand_nofill(self.__toolbar)
        self.__vbox.bw_pack_start_expand_fill(self.__hbox)
        self.__vbox.bw_pack_start_noexpand_nofill(self.__fisheye)
        self.__vbox.bw_pack_start_noexpand_nofill(self.__statusbar)

        self.add(self.__vbox)
        self.set_title(" ".join([INFO['name'], INFO['version']]))
        self.set_position(Gtk.WindowPosition.CENTER)
        self.show_all()
        self.connect('destroy', Gtk.main_quit)

        self.__radialnet.set_no_show_all(True)
        self.__control.set_no_show_all(True)
        self.__fisheye.set_no_show_all(True)

        self.__radialnet.hide()
        self.__control_sw.hide()
        self.__fisheye.hide()
        self.__toolbar.disable_controls()


    def set_fullscreen_state(self, state):
        """
        """
        if state:
            #self.__statusbar.set_has_resize_grip(False)
            self.fullscreen()

        else:
            #self.__statusbar.set_has_resize_grip(True)
            self.unfullscreen()


    def parse_nmap_xml_file(self, file):
        """
        """
        try:

            self.__parser = XMLReader(file)
            self.__parser.parse()

        except:

            text = _("It is not possible open file: %s.") % file

            alert = bw.BWAlertDialog(self,
                                     primary_text=_("Error opening file."),
                                     secondary_text=text)

            alert.show_all()

            return False

        self.__radialnet.set_empty()
        self.__radialnet.set_graph(make_graph_from_nmap_parser(self.__parser))
        self.__radialnet.show()

        self.__toolbar.enable_controls()

        return True


    def start(self):
        """
        """
        Gtk.main()
