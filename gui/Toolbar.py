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
from gi.repository import Gtk, GObject

import bestwidgets as bw

from core.I18n import _
from gui.Dialogs import AboutDialog
from gui.HostsViewer import HostsViewer
from gui.ScanDialog import ScanDialog


SHOW = True
HIDE = False

FILE_CHOOSER_OPEN_BUTTONS = (Gtk.STOCK_CANCEL,
                             Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OPEN,
                             Gtk.ResponseType.OK)

FILE_CHOOSER_SAVE_BUTTONS = (Gtk.STOCK_CANCEL,
                             Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_SAVE,
                             Gtk.ResponseType.OK)

REFRESH_RATE = 500



class ToolsMenu(Gtk.Menu):
    """
    """
    def __init__(self, radialnet):
        """
        """
        Gtk.Menu.__init__(self)

        self.radialnet = radialnet

        self.__create_items()


    def __create_items(self):
        """
        """
        self.__hosts = Gtk.ImageMenuItem(_("Hosts Viewer"))
        self.__hosts.connect("activate", self.__hosts_viewer_callback)
        self.__hosts_image = Gtk.Image.new_from_icon_name("x-office-address-book",
                                                          Gtk.IconSize.MENU)
        self.__hosts.set_image(self.__hosts_image)
        self.append(self.__hosts)

        self.__export = Gtk.ImageMenuItem(_("Save Image"))
        self.__export.connect("activate", self.__export_callback)
        self.__export_image = Gtk.Image.new_from_icon_name("document-save",
                                                           Gtk.IconSize.MENU)
        self.__export.set_image(self.__export_image)
        self.append(self.__export)

        self.__hosts.show_all()
        self.__export.show_all()


    def __hosts_viewer_callback(self, widget):
        """
        """
        window = HostsViewer(self.radialnet.get_scanned_nodes())
        window.show_all()
        window.set_keep_above(True)


    def __export_callback(self, widget):
        """
        """
        self.__chooser = Gtk.FileChooserDialog(_("Save PNG Image"),
                                               None,
                                               Gtk.FileChooserAction.SAVE,
                                               FILE_CHOOSER_SAVE_BUTTONS)
        self.__chooser.set_keep_above(True)

        if self.__chooser.run() == Gtk.ResponseType.OK:
            self.radialnet.save_drawing_to_file(self.__chooser.get_filename())

        self.__chooser.destroy()


    def enable_dependents(self):
        """
        """
        self.__hosts.set_sensitive(True)
        self.__export.set_sensitive(True)


    def disable_dependents(self):
        """
        """
        self.__hosts.set_sensitive(False)
        self.__export.set_sensitive(False)



class Toolbar(Gtk.Toolbar):
    """
    """
    def __init__(self, radialnet, window, control, fisheye):
        """
        """
        Gtk.Toolbar.__init__(self)
        self.set_style(Gtk.ToolbarStyle.BOTH_HORIZ)
        #self.set_tooltips(True)

        self.radialnet = radialnet

        self.__window = window
        self.__control_widget = control
        self.__fisheye_widget = fisheye

        self.__state = {'fisheye':SHOW, 'control':SHOW}

        self.__create_widgets()


    def __create_widgets(self):
        """
        """
        self.__scan = Gtk.ToolButton(Gtk.STOCK_FIND)
        self.__scan.set_label(_("Scan"))
        self.__scan.set_tooltip_text(_("Open scan window"))
        self.__scan.set_is_important(True)
        self.__scan.connect('clicked', self.__scan_callback)

        self.__open = Gtk.ToolButton(Gtk.STOCK_OPEN)
        self.__open.set_label(_("Open"))
        self.__open.set_tooltip_text(_("Open a file"))
        self.__open.set_is_important(True)
        self.__open.connect('clicked', self.__open_callback)

        self.__tools_menu = ToolsMenu(self.radialnet)

        self.__tools_button = Gtk.MenuToolButton(Gtk.STOCK_PREFERENCES)
        self.__tools_button.set_label(_("Tools"))
        self.__tools_button.set_tooltip_text(_("Show tools menu"))
        self.__tools_button.set_is_important(True)
        self.__tools_button.set_menu(self.__tools_menu)
        self.__tools_button.connect('clicked', self.__tools_callback)

        self.__control = Gtk.ToggleToolButton(Gtk.STOCK_PROPERTIES)
        self.__control.set_label(_("Controls"))
        self.__control.set_is_important(True)
        self.__control.connect('clicked', self.__control_callback)
        self.__control.set_tooltip_text(_("Show control panel"))
        self.__control.set_active(False)

        self.__fisheye = Gtk.ToggleToolButton(Gtk.STOCK_ZOOM_FIT)
        self.__fisheye.set_label(_("Fisheye"))
        self.__fisheye.set_is_important(True)
        self.__fisheye.connect('clicked', self.__fisheye_callback)
        self.__fisheye.set_tooltip_text(_("Enable fisheye"))
        self.__fisheye.set_active(False)

        self.__fullscreen = Gtk.ToggleToolButton(Gtk.STOCK_FULLSCREEN)
        self.__fullscreen.set_label(_("Fullscreen"))
        self.__fullscreen.set_is_important(True)
        self.__fullscreen.connect('clicked', self.__fullscreen_callback)
        self.__fullscreen.set_tooltip_text(_("Toggle fullscreen"))

        self.__about = Gtk.ToolButton(Gtk.STOCK_ABOUT)
        self.__about.set_label(_("About"))
        self.__about.set_is_important(True)
        self.__about.connect('clicked', self.__about_callback)
        self.__about.set_tooltip_text(_("About RadialNet"))

        self.__separator = Gtk.SeparatorToolItem()
        self.__expander = Gtk.SeparatorToolItem()
        self.__expander.set_expand(True)
        self.__expander.set_draw(False)

        self.insert(self.__scan,         0)
        self.insert(self.__open,         1)
        self.insert(self.__separator,    2)
        self.insert(self.__tools_button, 3)
        self.insert(self.__expander,     4)
        self.insert(self.__control,      5)
        self.insert(self.__fisheye,      6)
        self.insert(self.__fullscreen,   7)
        self.insert(self.__about,        8)

        GObject.timeout_add(REFRESH_RATE, self.__update)


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


    def __scan_callback(self, widget=None):
        """
        """
        scan = ScanDialog(self.__window)

        scan.show_all()
        scan.set_keep_above(True)


    def __open_callback(self, widget=None):
        """
        """
        self.__chooser = Gtk.FileChooserDialog(_("Open a Nmap XML file"),
                                               None,
                                               Gtk.FileChooserAction.OPEN,
                                               FILE_CHOOSER_OPEN_BUTTONS)
        self.__chooser.set_keep_above(True)

        if self.__chooser.run() == Gtk.ResponseType.OK:
            self.__window.parse_nmap_xml_file(self.__chooser.get_filename())

        self.__chooser.destroy()


    def __tools_callback(self, widget):
        """
        """
        self.__tools_menu.popup(None,
                                None,
                                None,
                                1,
                                0,
                                Gtk.get_current_event_time())


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
            self.__window.set_fullscreen_state(True)

        else:
            self.__window.set_fullscreen_state(False)

