# vim: set fileencoding=utf-8 :

# Copyright (C) 2007-2008 Joao Paulo de Souza Medeiros
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
import pango
import gobject

import bestwidgets as bw

from core.I18n import _


PORTS_HEADER = [_("Port"),
                _("Protocol"),
                _("State"),
                _("Service"),
                _("Method")]
EXTRAPORTS_HEADER = [_("Count"), _("State"), _("Reasons")]

SERVICE_COLORS = {'open'            : '#ffd5d5',
                  'closed'          : '#d5ffd5',
                  'filtered'        : '#ffffd5',
                  'unfiltered'      : '#ffd5d5',
                  'open|filtered'   : '#ffd5d5',
                  'closed|filtered' : '#d5ffd5'}

TRACE_HEADER = [_("TTL"), _("RTT"), _("IP"), _("Hostname")]

TRACE_TEXT = _("""\
Traceroute on port <b>%s</b> totalized <b>%d</b> known hops.\
""")

NO_TRACE_TEXT = _("No traceroute information available.")

HOP_COLOR = {'known'   : '#ffffff',
             'unknown' : '#cccccc'}

SYSTEM_ADDRESS_TEXT = "[%s] %s"

OSMATCH_HEADER = [_("%"), _("Name"), _("DB Line")]
OSCLASS_HEADER = [_("%"), _("Vendor"), _("Type"), _("Family"), _("Version")]

USED_PORTS_TEXT = "%d/%s %s"

TCP_SEQ_NOTE = _("""\
<b>*</b> TCP sequence <i>index</i> equal to %d and <i>difficulty</i> is "%s".\
""")



class NodeNotebook(gtk.Notebook):
    """
    """
    def __init__(self, node):
        """
        """
        gtk.Notebook.__init__(self)
        self.set_tab_pos(gtk.POS_TOP)

        self.__node = node

        self.__create_widgets()


    def __create_widgets(self):
        """
        """
        # create body elements
        self.__services_page = ServicesPage(self.__node)
        self.__system_page = SystemPage(self.__node)
        self.__trace_page = TraceroutePage(self.__node)

        # packing notebook elements
        self.append_page(self.__system_page, bw.BWLabel(_("General")))
        self.append_page(self.__services_page, bw.BWLabel(_("Services")))
        self.append_page(self.__trace_page, bw.BWLabel(_("Traceroute")))



class ServicesPage(gtk.Notebook):
    """
    """
    def __init__(self, node):
        """
        """
        gtk.Notebook.__init__(self)
        self.set_border_width(6)
        self.set_tab_pos(gtk.POS_TOP)

        self.__node = node
        self.__font = pango.FontDescription('Monospace')

        self.__create_widgets()


    def __create_widgets(self):
        """
        """
        self.__cell = gtk.CellRendererText()

        # texteditor widgets
        self.__texteditor = bw.BWTextEditor()
        self.__texteditor.bw_modify_font(self.__font)
        self.__texteditor.bw_set_editable(False)
        self.__texteditor.set_border_width(0)

        self.__select_combobox = gtk.combo_box_new_text()
        self.__select_combobox.connect('changed', self.__change_text_value)

        self.__viewer = bw.BWVBox(spacing=6)
        self.__viewer.set_border_width(6)

        self.__viewer.bw_pack_start_noexpand_nofill(self.__select_combobox)
        self.__viewer.bw_pack_start_expand_fill(self.__texteditor)

        self.__text = list()

        # ports information
        number_of_ports = len(self.__node.get_info('ports'))
        self.__ports_label = bw.BWLabel(_("Ports (%s)") % number_of_ports)

        self.__ports_scroll = bw.BWScrolledWindow()

        self.__ports_store = gtk.TreeStore(gobject.TYPE_INT,
                                           gobject.TYPE_STRING,
                                           gobject.TYPE_STRING,
                                           gobject.TYPE_STRING,
                                           gobject.TYPE_STRING,
                                           gobject.TYPE_STRING,
                                           gobject.TYPE_BOOLEAN)

        self.__ports_treeview = gtk.TreeView(self.__ports_store)

        for port in self.__node.get_info('ports'):

            color = SERVICE_COLORS[port['state']['state']]

            if port['service'].has_key('name'):
                service_name = port['service']['name']

            else:
                service_name = _("<unknown>")

            if port['service'].has_key('method'):
                service_method = port['service']['method']

            else:
                service_method = _("<none>")

            reference = self.__ports_store.append(None,
                                                  [port['id'],
                                                   port['protocol'],
                                                   port['state']['state'],
                                                   service_name,
                                                   service_method,
                                                   color,
                                                   True])

            for key in port['state']:
                self.__ports_store.append(reference,
                                          [port['id'],
                                           'state',
                                           key,
                                           port['state'][key],
                                           '',
                                           'white',
                                           True])

            for key in port['service']:

                if key in ['servicefp', 'extrainfo']:

                    text = _("[%d] service: %s") % (port['id'], key)

                    self.__select_combobox.append_text(text)
                    self.__text.append(port['service'][key])

                    value = _("<special field>")

                else:
                    value = port['service'][key]

                self.__ports_store.append(reference,
                                          [port['id'],
                                           'service',
                                           key,
                                           value,
                                           '',
                                           'white',
                                           True])

            for script in port['scripts']:

                text = _("[%d] script: %s") % (port['id'], script['id'])

                self.__select_combobox.append_text(text)
                self.__text.append(script['output'])

                self.__ports_store.append(reference,
                                          [port['id'],
                                           'script',
                                           'id',
                                           script['id'],
                                           _("<special field>"),
                                           'white',
                                           True])

        self.__ports_column = list()

        for i in range(len(PORTS_HEADER)):

            column = gtk.TreeViewColumn(PORTS_HEADER[i],
                                        self.__cell,
                                        text = i)

            self.__ports_column.append(column)

            self.__ports_column[i].set_reorderable(True)
            self.__ports_column[i].set_resizable(True)
            self.__ports_column[i].set_sort_column_id(i)
            self.__ports_column[i].set_attributes(self.__cell,
                                                  text = i,
                                                  background = 5,
                                                  editable = 6)

            self.__ports_treeview.append_column(self.__ports_column[i])

        self.__ports_scroll.add_with_viewport(self.__ports_treeview)

        # extraports information
        number_of_xports = 0

        self.__xports_scroll = bw.BWScrolledWindow()

        self.__xports_store = gtk.TreeStore(gobject.TYPE_INT,
                                            gobject.TYPE_STRING,
                                            gobject.TYPE_STRING,
                                            gobject.TYPE_STRING,
                                            gobject.TYPE_BOOLEAN)

        self.__xports_treeview = gtk.TreeView(self.__xports_store)

        for xports in self.__node.get_info('extraports'):

            color = SERVICE_COLORS[xports['state']]
            number_of_xports += xports['count']

            reference = self.__xports_store.append(None,
                                                   [xports['count'],
                                                    xports['state'],
                                                    ", ".join(xports['reason']),
                                                    color,
                                                    True])

            for xreason in xports['all_reason']:
                self.__xports_store.append(reference,
                                           [xreason['count'],
                                            xports['state'],
                                            xreason['reason'],
                                            'white',
                                            True])

        self.__xports_column = list()

        for i in range(len(EXTRAPORTS_HEADER)):

            column = gtk.TreeViewColumn(EXTRAPORTS_HEADER[i],
                                        self.__cell,
                                        text = i)

            self.__xports_column.append(column)

            self.__xports_column[i].set_reorderable(True)
            self.__xports_column[i].set_resizable(True)
            self.__xports_column[i].set_sort_column_id(i)
            self.__xports_column[i].set_attributes(self.__cell,
                                                   text = i,
                                                   background = 3,
                                                   editable = 4)

            self.__xports_treeview.append_column(self.__xports_column[i])

        xports_label_text = _("Extraports (%s)") % number_of_xports
        self.__xports_label = bw.BWLabel(xports_label_text)

        self.__xports_scroll.add_with_viewport(self.__xports_treeview)

        self.append_page(self.__ports_scroll, self.__ports_label)
        self.append_page(self.__xports_scroll, self.__xports_label)
        self.append_page(self.__viewer, bw.BWLabel(_("Special fields")))

        if len(self.__text) > 0:
            self.__select_combobox.set_active(0)


    def __change_text_value(self, widget):
        """
        """
        id = self.__select_combobox.get_active()

        self.__texteditor.bw_set_text(self.__text[id])



class SystemPage(bw.BWScrolledWindow):
    """
    """
    def __init__(self, node):
        """
        """
        bw.BWScrolledWindow.__init__(self)

        self.__node = node
        self.__font = pango.FontDescription('Monospace')

        self.__create_widgets()


    def __create_widgets(self):
        """
        """
        self.__vbox = bw.BWVBox()
        self.__vbox.set_border_width(6)

        self.__cell = gtk.CellRendererText()

        self.__general_frame = bw.BWExpander(_("General information"))
        self.__sequences_frame = bw.BWExpander(_("Sequences"))
        self.__os_frame = bw.BWExpander(_("Operating System"))

        self.__sequences_frame.bw_add(gtk.Label(_("No sequence information.")))
        self.__os_frame.bw_add(gtk.Label(_("No OS information.")))

        # general information widgets
        self.__general = bw.BWTable(3, 2)

        self.__address_label = bw.BWSectionLabel(_("Address:"))
        self.__address_list = gtk.combo_box_entry_new_text()
        self.__address_list.child.set_editable(False)

        for address in self.__node.get_info('addresses'):

            params = address['type'], address['addr']
            address_text = SYSTEM_ADDRESS_TEXT % params

            if address['vendor'] != None:
                address_text += " (%s)" % address['vendor']

            self.__address_list.append_text(address_text)

        self.__address_list.set_active(0)

        self.__general.bw_attach_next(self.__address_label,
                                      yoptions=gtk.FILL,
                                      xoptions=gtk.FILL)
        self.__general.bw_attach_next(self.__address_list, yoptions=gtk.FILL)

        if self.__node.get_info('hostnames') != None:

            self.__hostname_label = bw.BWSectionLabel(_("Hostname:"))
            self.__hostname_list = gtk.combo_box_entry_new_text()
            self.__hostname_list.child.set_editable(False)

            for hostname in self.__node.get_info('hostnames'):

                params = hostname['type'], hostname['name']
                self.__hostname_list.append_text(SYSTEM_ADDRESS_TEXT % params)

            self.__hostname_list.set_active(0)

            self.__general.bw_attach_next(self.__hostname_label,
                                          yoptions=gtk.FILL,
                                          xoptions=gtk.FILL)
            self.__general.bw_attach_next(self.__hostname_list,
                                          yoptions=gtk.FILL)

        if self.__node.get_info('uptime') != None:

            self.__uptime_label = bw.BWSectionLabel(_("Last boot:"))

            seconds = self.__node.get_info('uptime')['seconds']
            lastboot = self.__node.get_info('uptime')['lastboot']

            text = _("%s (%s seconds).") % (lastboot, seconds)

            self.__uptime_value = bw.BWLabel(text)
            self.__uptime_value.set_selectable(True)
            self.__uptime_value.set_line_wrap(False)

            self.__general.bw_attach_next(self.__uptime_label,
                                          yoptions=gtk.FILL,
                                          xoptions=gtk.FILL)
            self.__general.bw_attach_next(self.__uptime_value,
                                          yoptions=gtk.FILL)

        self.__general_frame.bw_add(self.__general)
        self.__general_frame.set_expanded(True)

        # sequences information widgets
        self.__sequences = bw.BWTable(5, 3)

        sequences = self.__node.get_info('sequences')

        if len(sequences) > 0:

            self.__sequences.attach(bw.BWSectionLabel(_("Class")), 1, 2, 0, 1)
            self.__sequences.attach(bw.BWSectionLabel(_("Values")), 2, 3, 0, 1)

            self.__sequences.attach(bw.BWSectionLabel(_("TCP *")), 0, 1, 1, 2)
            self.__sequences.attach(bw.BWSectionLabel(_("IP ID")), 0, 1, 2, 3)
            self.__sequences.attach(bw.BWSectionLabel(_("TCP Timestamp")),
                                    0,
                                    1,
                                    3,
                                    4)

            # tcp sequence values
            tcp = sequences['tcp']

            tcp_class = bw.BWLabel(tcp['class'])
            tcp_class.set_selectable(True)

            self.__sequences.attach(tcp_class, 1, 2, 1, 2)

            tcp_values = gtk.combo_box_entry_new_text()

            for value in tcp['values']:
                tcp_values.append_text(value)

            tcp_values.set_active(0)

            self.__sequences.attach(tcp_values, 2, 3, 1, 2)

            tcp_note = bw.BWLabel()
            tcp_note.set_selectable(True)
            tcp_note.set_line_wrap(False)
            tcp_note.set_alignment(1.0, 0.5)
            tcp_note.set_markup(TCP_SEQ_NOTE % (tcp['index'], tcp['difficulty']))

            self.__sequences.attach(tcp_note, 0, 3, 4, 5)

            # ip id sequence values
            ip_id = sequences['ip_id']

            ip_id_class = bw.BWLabel(ip_id['class'])
            ip_id_class.set_selectable(True)

            self.__sequences.attach(ip_id_class, 1, 2, 2, 3)

            ip_id_values = gtk.combo_box_entry_new_text()

            for value in ip_id['values']:
                ip_id_values.append_text(value)

            ip_id_values.set_active(0)

            self.__sequences.attach(ip_id_values, 2, 3, 2, 3)

            # tcp sequence values
            tcp_ts = sequences['tcp_ts']

            tcp_ts_class = bw.BWLabel(tcp_ts['class'])
            tcp_ts_class.set_selectable(True)

            self.__sequences.attach(tcp_ts_class, 1, 2, 3, 4)

            if tcp_ts['values'] != None:

                tcp_ts_values = gtk.combo_box_entry_new_text()

                for value in tcp_ts['values']:
                    tcp_ts_values.append_text(value)

                tcp_ts_values.set_active(0)

                self.__sequences.attach(tcp_ts_values, 2, 3, 3, 4)

            self.__sequences_frame.bw_add(self.__sequences)

        # operating system information widgets
        self.__os = gtk.Notebook()
        self.__os.set_tab_pos(gtk.POS_LEFT)

        os = self.__node.get_info('os')

        if os != None:

            if os.has_key('matches'):

                self.__match_scroll = bw.BWScrolledWindow()

                self.__match_store = gtk.ListStore(gobject.TYPE_INT,
                                                   gobject.TYPE_STRING,
                                                   gobject.TYPE_INT,
                                                   gobject.TYPE_BOOLEAN)

                self.__match_treeview = gtk.TreeView(self.__match_store)

                for os_match in os['matches']:

                    self.__match_store.append([os_match['accuracy'],
                                               os_match['name'],
                                               os_match['db_line'],
                                               True])

                self.__match_column = list()

                for i in range(len(OSMATCH_HEADER)):

                    column = gtk.TreeViewColumn(OSMATCH_HEADER[i],
                                                self.__cell,
                                                text = i)

                    self.__match_column.append(column)

                    self.__match_column[i].set_reorderable(True)
                    self.__match_column[i].set_resizable(True)
                    self.__match_column[i].set_attributes(self.__cell,
                                                          text = i,
                                                          editable = 3)

                    self.__match_column[i].set_sort_column_id(i)
                    self.__match_treeview.append_column(self.__match_column[i])

                self.__match_scroll.add_with_viewport(self.__match_treeview)

                self.__os.append_page(self.__match_scroll,
                                      bw.BWLabel(_("Match")))

            if os.has_key('classes'):

                self.__class_scroll = bw.BWScrolledWindow()

                self.__class_store = gtk.ListStore(gobject.TYPE_INT,
                                                   gobject.TYPE_STRING,
                                                   gobject.TYPE_STRING,
                                                   gobject.TYPE_STRING,
                                                   gobject.TYPE_STRING,
                                                   gobject.TYPE_BOOLEAN)

                self.__class_treeview = gtk.TreeView(self.__class_store)

                for os_class in os['classes']:

                    os_gen = ''

                    if os_class.has_key('os_gen'):
                        os_gen = os_class['os_gen']

                    self.__class_store.append([os_class['accuracy'],
                                               os_class['vendor'],
                                               os_class['type'],
                                               os_class['os_family'],
                                               os_gen,
                                               True])

                self.__class_column = list()

                for i in range(len(OSCLASS_HEADER)):

                    column = gtk.TreeViewColumn(OSCLASS_HEADER[i],
                                                self.__cell,
                                                text = i)

                    self.__class_column.append(column)

                    self.__class_column[i].set_reorderable(True)
                    self.__class_column[i].set_resizable(True)
                    self.__class_column[i].set_attributes(self.__cell,
                                                          text = i,
                                                          editable = 5)

                    self.__class_column[i].set_sort_column_id(i)
                    self.__class_treeview.append_column(self.__class_column[i])

                self.__class_scroll.add_with_viewport(self.__class_treeview)

                self.__os.append_page(self.__class_scroll,
                                      bw.BWLabel(_("Class")))

            self.__fp_viewer = bw.BWTextEditor()
            self.__fp_viewer.bw_modify_font(self.__font)
            self.__fp_viewer.bw_set_editable(False)
            self.__fp_viewer.bw_set_text(os['fingerprint'])

            self.__fp_ports = bw.BWHBox()
            self.__fp_label = bw.BWSectionLabel(_("Used ports:"))

            self.__fp_ports_list = gtk.combo_box_entry_new_text()
            self.__fp_ports_list.child.set_editable(False)

            self.__fp_vbox = bw.BWVBox()

            if os.has_key('used_ports'):

                used_ports = os['used_ports']

                for port in used_ports:

                    params = port['id'], port['protocol'], port['state']
                    self.__fp_ports_list.append_text(USED_PORTS_TEXT % params)

                self.__fp_ports_list.set_active(0)

                self.__fp_ports.bw_pack_start_noexpand_nofill(self.__fp_label)
                self.__fp_ports.bw_pack_start_expand_fill(self.__fp_ports_list)

                self.__fp_vbox.bw_pack_start_noexpand_nofill(self.__fp_ports)

            self.__os.append_page(self.__fp_viewer,
                                  bw.BWLabel(_("Fingerprint")))
            self.__fp_vbox.bw_pack_start_expand_fill(self.__os)

            self.__os_frame.bw_add(self.__fp_vbox)
            self.__os_frame.set_expanded(True)

        self.__vbox.bw_pack_start_noexpand_nofill(self.__general_frame)
        self.__vbox.bw_pack_start_expand_fill(self.__os_frame)
        self.__vbox.bw_pack_start_noexpand_nofill(self.__sequences_frame)

        self.add_with_viewport(self.__vbox)



class TraceroutePage(bw.BWVBox):
    """
    """
    def __init__(self, node):
        """
        """
        bw.BWVBox.__init__(self)
        self.set_border_width(6)

        self.__node = node

        self.__create_widgets()


    def __create_widgets(self):
        """
        """
        if self.__node.get_info('trace') == None:

            self.__trace_label = gtk.Label(NO_TRACE_TEXT)
            self.pack_start(self.__trace_label, True, True)

        else:

            # add hops
            hops = self.__node.get_info('trace')['hops']
            ttls = [int(i['ttl']) for i in hops]

            self.__cell = gtk.CellRendererText()

            self.__trace_scroll = bw.BWScrolledWindow()
            self.__trace_scroll.set_border_width(0)

            self.__trace_store = gtk.ListStore(gobject.TYPE_INT,
                                               gobject.TYPE_STRING,
                                               gobject.TYPE_STRING,
                                               gobject.TYPE_STRING,
                                               gobject.TYPE_STRING,
                                               gobject.TYPE_BOOLEAN)

            self.__trace_treeview = gtk.TreeView(self.__trace_store)

            count = 0

            for i in range(1, max(ttls) + 1):

                if i in ttls:

                    hop = hops[count]
                    count += 1

                    self.__trace_store.append([hop['ttl'],
                                               hop['rtt'],
                                               hop['ip'],
                                               hop['hostname'],
                                               HOP_COLOR['known'],
                                               True])

                else:
                    self.__trace_store.append([i,
                                               '',
                                               _("<unknown>"),
                                               '',
                                               HOP_COLOR['unknown'],
                                               True])


            self.__trace_column = list()

            for i in range(len(TRACE_HEADER)):

                column = gtk.TreeViewColumn(TRACE_HEADER[i],
                                            self.__cell,
                                            text = i)

                self.__trace_column.append(column)

                self.__trace_column[i].set_reorderable(True)
                self.__trace_column[i].set_resizable(True)
                self.__trace_column[i].set_attributes(self.__cell,
                                                      text = i,
                                                      background = 4,
                                                      editable = 5)

                self.__trace_treeview.append_column(self.__trace_column[i])

            self.__trace_column[0].set_sort_column_id(0)

            self.__trace_scroll.add_with_viewport(self.__trace_treeview)

            self.__trace_info = (self.__node.get_info('trace')['port'],
                                 len(self.__node.get_info('trace')['hops']))

            self.__trace_label = bw.BWLabel(TRACE_TEXT % self.__trace_info)
            self.__trace_label.set_use_markup(True)

            self.bw_pack_start_expand_fill(self.__trace_scroll)
            self.bw_pack_start_noexpand_nofill(self.__trace_label)
