# vim: set fileencoding=utf-8 :

# Copyright (C) 2008 Insecure.Com LLC.
#
# Author: João Paulo de Souza Medeiros <ignotus21@gmail.com>
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
import gobject

import bestwidgets as bw
from gui.Dialogs import AboutDialog
from gui.HostsViewer import HostsViewer


SHOW = True
HIDE = False

FILE_CHOOSER_BUTTONS = (gtk.STOCK_CANCEL,
                        gtk.RESPONSE_CANCEL,
                        gtk.STOCK_OPEN,
                        gtk.RESPONSE_OK)

REFRESH_RATE = 500



class ToolsMenu(gtk.Menu):
    """
    """
    def __init__(self, radialnet):
        """
        """
        gtk.Menu.__init__(self)

        self.radialnet = radialnet

        self.__create_items()


    def __create_items(self):
        """
        """
        self.__hosts = gtk.ImageMenuItem('Hosts viewer')
        self.__hosts.connect("activate", self.__hosts_viewer_callback)
        self.__hosts_image = gtk.Image()
        self.__hosts_image.set_from_stock(gtk.STOCK_INDEX, gtk.ICON_SIZE_MENU)
        self.__hosts.set_image(self.__hosts_image)

        self.append(self.__hosts)

        self.__hosts.show_all()


    def __hosts_viewer_callback(self, widget):
        """
        """
        window = HostsViewer(self.radialnet.get_scanned_nodes())
        window.show_all()
        window.set_keep_above(True)


    def enable_dependents(self):
        """
        """
        self.__hosts.set_sensitive(True)


    def disable_dependents(self):
        """
        """
        self.__hosts.set_sensitive(False)



class Toolbar(gtk.Toolbar):
    """
    """
    def __init__(self, radialnet, window, control, fisheye):
        """
        """
        gtk.Toolbar.__init__(self)
        self.set_style(gtk.TOOLBAR_BOTH_HORIZ)
        self.set_tooltips(True)

        self.radialnet = radialnet

        self.__window = window
        self.__control_widget = control
        self.__fisheye_widget = fisheye

        self.__state = {'fisheye':SHOW, 'control':SHOW}

        self.__create_widgets()


    def __create_widgets(self):
        """
        """
        self.__tooltips = gtk.Tooltips()

        self.__open = gtk.ToolButton(gtk.STOCK_OPEN)
        self.__open.set_label('Open')
        self.__open.set_is_important(True)
        self.__open.connect('clicked', self.__open_callback)

        self.__tools_menu = ToolsMenu(self.radialnet)

        self.__tools_button = gtk.MenuToolButton(gtk.STOCK_PREFERENCES)
        self.__tools_button.set_label('Tools')
        self.__tools_button.set_is_important(True)
        self.__tools_button.set_menu(self.__tools_menu)
        self.__tools_button.connect('clicked', self.__tools_callback)

        self.__control = gtk.ToggleToolButton(gtk.STOCK_PROPERTIES)
        self.__control.set_label('Controls')
        self.__control.set_is_important(True)
        self.__control.connect('clicked', self.__control_callback)
        self.__control.set_tooltip(self.__tooltips, 'Show control panel')
        self.__control.set_active(False)

        self.__fisheye = gtk.ToggleToolButton(gtk.STOCK_ZOOM_FIT)
        self.__fisheye.set_label('Fisheye')
        self.__fisheye.set_is_important(True)
        self.__fisheye.connect('clicked', self.__fisheye_callback)
        self.__fisheye.set_tooltip(self.__tooltips, 'Enable fisheye')
        self.__fisheye.set_active(False)

        self.__fullscreen = gtk.ToggleToolButton(gtk.STOCK_FULLSCREEN)
        self.__fullscreen.set_label('Fullscreen')
        self.__fullscreen.set_is_important(True)
        self.__fullscreen.connect('clicked', self.__fullscreen_callback)
        self.__fullscreen.set_tooltip(self.__tooltips, 'Toggle fullscreen')

        self.__about = gtk.ToolButton(gtk.STOCK_ABOUT)
        self.__about.set_label('About')
        self.__about.set_is_important(True)
        self.__about.connect('clicked', self.__about_callback)
        self.__about.set_tooltip(self.__tooltips, 'About RadialNet')

        self.__separator = gtk.SeparatorToolItem()
        self.__expander = gtk.SeparatorToolItem()
        self.__expander.set_expand(True)
        self.__expander.set_draw(False)

        self.insert(self.__open,         0)
        self.insert(self.__separator,    1)
        self.insert(self.__tools_button, 2)
        self.insert(self.__expander,     3)
        self.insert(self.__control,      4)
        self.insert(self.__fisheye,      5)
        self.insert(self.__fullscreen,   6)
        self.insert(self.__about,        7)

        gobject.timeout_add(REFRESH_RATE, self.__update)


    def disable_controls(self):
        """
        """
        self.__control.set_sensitive(False)
        self.__fisheye.set_sensitive(False)
        self.__tools_menu.disable_dependents()


    def enable_controls(self):
        """
        """
        self.__control.set_sensitive(True)
        self.__fisheye.set_sensitive(True)
        self.__tools_menu.enable_dependents()


    def __update(self):
        """
        """
        self.__fisheye.set_active(self.radialnet.get_fisheye())

        self.__fisheye_callback()
        self.__control_callback()

        return True


    def __open_callback(self, widget=None):
        """
        """
        self.__chooser = gtk.FileChooserDialog('Open a Nmap XML file',
                                               None,
                                               gtk.FILE_CHOOSER_ACTION_OPEN,
                                               FILE_CHOOSER_BUTTONS)
        self.__chooser.set_keep_above(True)

        if self.__chooser.run() == gtk.RESPONSE_OK:
            self.__window.parse_nmap_xml_file(self.__chooser.get_filename())

        self.__chooser.destroy()


    def __tools_callback(self, widget):
        """
        """
        self.__tools_menu.popup(None, None, None, 1, 0)


    def __control_callback(self, widget=None):
        """
        """
        if self.__control.get_active() != self.__state['control']:

            if self.__control.get_active():
                self.__control_widget.show()

            else:
                self.__control_widget.hide()

            self.__state['control'] = self.__control.get_active()


    def __fisheye_callback(self, widget=None):
        """
        """
        if self.__fisheye.get_active() != self.__state['fisheye']:

            if not self.radialnet.is_in_animation():

                if self.__fisheye.get_active():

                    self.__fisheye_widget.active_fisheye()
                    self.__fisheye_widget.show()

                else:

                    self.__fisheye_widget.deactive_fisheye()
                    self.__fisheye_widget.hide()

                self.__state['fisheye'] = self.__fisheye.get_active()


    def __about_callback(self, widget):
        """
        """
        self.__about_dialog = AboutDialog()
        self.__about_dialog.show_all()


    def __fullscreen_callback(self, widget=None):
        """
        """
        if self.__fullscreen.get_active():
            self.__window.fullscreen()

        else:
            self.__window.unfullscreen()

