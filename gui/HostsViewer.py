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

import re

import bestwidgets as bw

from core.I18n import _
from gui.NodeNotebook import NodeNotebook
from util.misc import ipv4_compare


HOSTS_COLORS = ['#d5ffd5', '#ffffd5', '#ffd5d5']
HOSTS_HEADER = [_("ID"), _("#"), _("Hosts")]
DIMENSION = (700, 400)
IP_RE = '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$'



class HostsViewer(bw.BWMainWindow):
    """
    """
    def __init__(self, nodes):
        """
        """
        bw.BWMainWindow.__init__(self)
        self.set_title(_("Hosts Viewer"))
        self.set_default_size(DIMENSION[0], DIMENSION[1])

        self.set_position(Gtk.WindowPosition.CENTER)

        self.__nodes = nodes

        self.__create_widgets()


    def __create_widgets(self):
        """
        """
        self.__panel = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        self.__panel.set_border_width(6)

        self.__list = HostsList(self, self.__nodes)
        self.__view = bw.BWLabel()

        self.__panel.add1(self.__list)
        self.__panel.add2(self.__view)
        self.__panel.set_position(int(DIMENSION[0] / 5))

        self.add(self.__panel)



    def change_notebook(self, node):
        """
        """
        self.__view.destroy()
        self.__view = NodeNotebook(node)
        self.__panel.add2(self.__view)
        self.__panel.get_child2().show_all()



class HostsList(Gtk.ScrolledWindow):
    """
    """
    def __init__(self, parent, nodes):
        """
        """
        super(HostsList, self).__init__()
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.set_shadow_type(Gtk.ShadowType.NONE)

        self.__parent = parent
        self.__nodes = nodes

        self.__create_widgets()


    def __create_widgets(self):
        """
        """
        self.__cell = Gtk.CellRendererText()

        self.__hosts_store = Gtk.ListStore(GObject.TYPE_INT,
                                           GObject.TYPE_INT,
                                           GObject.TYPE_STRING,
                                           GObject.TYPE_STRING,
                                           GObject.TYPE_BOOLEAN)

        self.__hosts_treeview = Gtk.TreeView(self.__hosts_store)

        for i in range(len(self.__nodes)):

            node = self.__nodes[i]

            ports = node.get_info('number_of_scanned_ports')
            color = HOSTS_COLORS[node.get_info('vulnerability_score')]

            host = node.get_info('ip')

            if node.get_info('hostname') != None:
                host = node.get_info('hostname')

            self.__hosts_store.append([i,
                                       ports,
                                       host,
                                       color,
                                       True])

        self.__hosts_column = list()

        for i in range(0, len(HOSTS_HEADER)):

            column = Gtk.TreeViewColumn(HOSTS_HEADER[i],
                                        self.__cell,
                                        text = i)

            self.__hosts_column.append(column)

            self.__hosts_column[i].set_reorderable(True)
            self.__hosts_column[i].set_resizable(True)
            self.__hosts_column[i].set_attributes(self.__cell,
                                                  text = i,
                                                  background = 3,
                                                  editable = 4)

        self.__hosts_treeview.append_column(self.__hosts_column[2])

        self.__hosts_store.set_sort_func(2, self.__host_sort)

        self.__hosts_column[2].set_sort_column_id(2)

        self.add_with_viewport(self.__hosts_treeview)

        self.__hosts_treeview.set_cursor((0,))
        self.__hosts_treeview.connect('cursor-changed', self.__cursor_callback)


    def __cursor_callback(self, widget):
        """
        """
        path = widget.get_cursor()[0]
        iter = self.__hosts_store.get_iter(path)

        node = self.__nodes[self.__hosts_store.get_value(iter, 0)]

        self.__parent.change_notebook(node)


    def __host_sort(self, treemodel, iter1, iter2):
        """
        """
        value1 = treemodel.get_value(iter1, 2)
        value2 = treemodel.get_value(iter2, 2)

        value1_is_ip = re.search(IP_RE, value1)
        value2_is_ip = re.search(IP_RE, value2)

        if value1_is_ip and value2_is_ip:
            return ipv4_compare(value1, value2)

        if value1_is_ip:
            return -1

        if value2_is_ip:
            return 1

        if value1 < value2:
            return -1

        if value1 > value2:
            return 1

        return 0
