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
from gi.repository import Gtk, Gdk, Pango, GObject

import re
import sys
import tempfile

from subprocess import Popen, PIPE

import bestwidgets as bw

from core.I18n import _
from core.Config import config


REFRESH_RATE = 500

INPUT  = 0
OUTPUT = 1

RE_DEVICE  = "device [\w]+"
RE_BRAZIL  = "BRT$"
RE_IP      = "[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}"
RE_MAC     = "[A-F0-9]{2}(:[A-F0-9]{2}){5}"
RE_URL     = " (localhost|((https?|ftp)://)?[\w-]+(\.[\w-]+)+(\/(\.?[\w-])*)*)"
RE_URI     = " (\/[\w\-\.]+)+"
RE_VAL     = "[\d]+[-:][\d]+([-:][\d]*)?|([\d]+\.)?[\d]+(KB|B|s|\%)"
RE_NUM     = "[\d]+(.[\d]+)?"
RE_HEADER  = "^(TRACE|HOP|PORT |Initiating|Starting|Completed|Retrying|Nmap).*"
RE_PORT    = "([0-9]+/)(tcp|udp)|^\|_?([\s]*\|_?)*"
RE_MARK    = "(Aggressive OS|Running|OS details:|OS:|SF:|TCP|\||[A-Z]{2,4}\()"
RE_CLEAN   = "^(%s|%s).*" % (RE_MARK, RE_PORT)
RE_SIDE    = "[^\w-]%s([^\w]|\.[\s]|$)"
RE_FREE    = "(,|\.[\s]|\)|\]|\(|\[)"

RE_MATCH = [(1, "uri",     RE_URI),
            (0, "url",     RE_URL),
            (1, "number",  RE_SIDE % RE_NUM),
            (1, "value",   RE_SIDE % RE_VAL),
            (1, "ip",      RE_IP),
            (1, "mac",     RE_MAC),
            (1, "port",    RE_PORT),
            (1, "clean",   RE_CLEAN),
            (1, "clean",   RE_FREE),
            (1, "device",  RE_DEVICE),
            (1, "port",    "^" + RE_PORT),
            (0, "brazil",  RE_BRAZIL),
            (0, "header",  RE_HEADER)]



class Nmap(bw.BWVBox):
    """
    """
    def __init__(self, window):
        """
        """
        bw.BWVBox.__init__(self)

        self.__path = config.get_value("backend", "nmap")
        self.__window = window
        self.__output = ""
        self.__cmd = "-d -v -A "
        self.__handle = None

        self.__fnxml = None
        self.__fnout = None
        self.__fnerr = None

        self.__fdout = None
        self.__fderr = None

        self.__create_widgets()

        self.__entry.grab_focus()


    def get_command(self):
        """
        """
        return self.__cmd


    def set_command(self, widget):
        """
        """
        self.__cmd = self.__entry.get_text()


    def run(self, widget):
        """
        """
        self.__view.bw_set_text("")

        self.__fnxml = tempfile.mktemp(prefix="rnxml-")
        self.__fnout = tempfile.mktemp(prefix="rnout-")
        self.__fnerr = tempfile.mktemp(prefix="rnerr-")

        self.__fdout = open(self.__fnout, "w+")
        self.__fderr = open(self.__fnerr, "w+")

        args = ["-oX", self.__fnxml] + self.__cmd.split()

        self.__handle = Popen([self.__path] + args,
                              bufsize=0,
                              stdin=PIPE,
                              stdout=self.__fdout.fileno(),
                              stderr=self.__fderr.fileno(),
                              shell=False)

        self.__load.set_sensitive(False)
        GObject.timeout_add(REFRESH_RATE, self.__check_output)


    def __check_output(self):
        """
        """
        fdout = open(self.__fnout, "r")
        otext = fdout.read().strip()

        if self.__output != otext:

            self.__output = otext
            self.__view.bw_set_text(self.__output, self.apply_text_tags)

            if self.__colors.get_active() and not self.__scroll.get_active():
                self.apply_text_tags()

        state = self.__handle.poll()

        if state != None and state != 0:

            fderr = open(self.__fnerr, "r")
            self.__view.bw_set_text(fderr.read().strip())

            return False

        if state == 0:

            self.__load.set_sensitive(True)
            return False

        return True


    def apply_text_tags(self):
        """
        """
        buff = self.__view.bw_get_textbuffer()
        text = self.__view.bw_get_text().split("\n")

        for n in range(len(text)):

            for pair in RE_MATCH:

                f, k, w = pair

                r = re.compile(w)
                i = r.finditer(text[n])

                for m in i:

                    s = buff.get_iter_at_line_offset(n, m.start())
                    e = buff.get_iter_at_line_offset(n, m.end())

                    if f == 1:
                        buff.remove_all_tags(s, e)

                    buff.apply_tag_by_name(k, s, e)


    def create_text_tags(self):
        """
        """
        buff = self.__view.bw_get_textbuffer()

        buff.create_tag("ip",
                        foreground="#0000ff")

        buff.create_tag("mac",
                        foreground="#0000ff")

        buff.create_tag("number",
                        foreground="#000000",
                        style=Pango.Style.ITALIC)

        buff.create_tag("value",
                        foreground="#888800")

        buff.create_tag("clean")

        buff.create_tag("header",
                        weight=Pango.Weight.BOLD)

        buff.create_tag("port",
                        foreground="#00aa00")

        buff.create_tag("uri",
                        foreground="#006666")

        buff.create_tag("url",
                        foreground="#ff0000")

        buff.create_tag("device",
                        foreground="#bc5029")

        buff.create_tag("brazil",
                        foreground="#005500",
                        background="#ffff00",
                        weight=Pango.Weight.BOLD)


    def load(self, widget):
        """
        """
        self.__window.parse_nmap_xml_file(self.__fnxml)


    def __toggle_colors(self, widget):
        """
        """
        if widget.get_active():
            self.apply_text_tags()

        else:
            self.__view.bw_remove_all_tags()


    def __toggle_scroll(self, widget):
        """
        """
        self.__view.bw_set_scroll(widget.get_active())


    def __toggle_wrap(self, widget):
        """
        """
        if widget.get_active():
            self.__view.bw_set_wrap_mode(Gtk.WrapMode.WORD)

        else:
            self.__view.bw_set_wrap_mode(Gtk.WrapMode.NONE)


    def entry_check(self, widget, event):
        """
        """
        key = Gdk.keyval_name(event.keyval)

        if key == "KP_Enter" or key == "Return":
            self.__button.clicked()


    def __create_widgets(self):
        """
        """
        self.__font = Pango.FontDescription('Monospace')

        self.__command = bw.BWHBox()
        self.__actions = bw.BWHBox()

        self.__label = bw.BWSectionLabel("Nmap")
        self.__entry = Gtk.Entry()
        self.__entry.modify_font(self.__font)
        self.__entry.set_text(self.__cmd)
        self.__entry.connect("changed", self.set_command)
        self.__entry.connect("key-press-event", self.entry_check)

        self.__button = bw.BWStockButton(Gtk.STOCK_EXECUTE,
                                         _("Scan"),
                                         Gtk.IconSize.MENU)
        self.__button.connect("clicked", self.run)

        self.__load = bw.BWStockButton(Gtk.STOCK_JUMP_TO,
                                       _("Load"),
                                       Gtk.IconSize.MENU)
        self.__load.connect("clicked", self.load)
        self.__load.set_sensitive(False)

        self.__view = bw.BWTextView()
        self.__view.set_border_width(0)
        self.__view.bw_set_scroll(True)
        self.__view.bw_set_editable(False)
        self.__view.bw_modify_font(self.__font)
        self.__view.bw_set_wrap_mode(Gtk.WrapMode.WORD)

        self.__scroll = Gtk.CheckButton(_("Auto-scroll"))
        self.__scroll.connect("toggled", self.__toggle_scroll)
        self.__scroll.set_active(True)

        self.create_text_tags()

        self.__colors = Gtk.CheckButton(_("Highlight"))
        self.__colors.connect("toggled", self.__toggle_colors)
        self.__colors.set_active(True)

        self.__wrap = Gtk.CheckButton(_("Wrap"))
        self.__wrap.connect("toggled", self.__toggle_wrap)
        self.__wrap.set_active(True)

        self.__actions.bw_pack_start_noexpand_nofill(self.__scroll)
        self.__actions.bw_pack_start_noexpand_nofill(self.__colors)
        self.__actions.bw_pack_start_noexpand_nofill(self.__wrap)
        self.__actions.bw_pack_start_expand_fill(self.__load)

        self.__statusbar = bw.BWStatusbar()

        self.__command.bw_pack_start_noexpand_nofill(self.__label)
        self.__command.bw_pack_start_expand_fill(self.__entry)
        self.__command.bw_pack_start_noexpand_nofill(self.__button)

        self.bw_pack_start_noexpand_nofill(self.__command)
        self.bw_pack_start_expand_fill(self.__view)
        self.bw_pack_start_noexpand_nofill(self.__actions)
        self.bw_pack_start_noexpand_nofill(self.__statusbar)

        self.show_all()
