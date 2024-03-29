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

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GObject

import math

import bestwidgets as bw
import util.geometry as geometry

from core.I18n import _
from core.Coordinate import PolarCoordinate
from gui.RadialNet import *


OPTIONS = ['address',
           'hostname',
           'icon',
           'latency',
           'ring',
           'region',
           'slow in/out']

REFRESH_RATE = 500



class ControlWidget(bw.BWVBox):
    """
    """
    def __init__(self, radialnet):
        """
        """
        bw.BWVBox.__init__(self)
        self.set_border_width(6)

        self.radialnet = radialnet

        self.__create_widgets()


    def __create_widgets(self):
        """
        """
        self.__action = ControlAction(self.radialnet)
        self.__interpolation = ControlInterpolation(self.radialnet)
        self.__layout = ControlLayout(self.radialnet)
        self.__view = ControlView(self.radialnet)

        self.bw_pack_start_noexpand_nofill(self.__action)
        self.bw_pack_start_noexpand_nofill(self.__interpolation)
        self.bw_pack_start_noexpand_nofill(self.__layout)
        self.bw_pack_start_noexpand_nofill(self.__view)



class ControlAction(bw.BWExpander):
    """
    """
    def __init__(self, radialnet):
        """
        """
        bw.BWExpander.__init__(self, _("Action"))
        self.set_expanded(True)

        self.radialnet = radialnet

        self.__create_widgets()


    def __create_widgets(self):
        """
        """
        self.__tbox = bw.BWTable(1, 4)
        self.__tbox.bw_set_spacing(0)
        self.__vbox = bw.BWVBox()

        self.__jump_to = Gtk.RadioToolButton(stock_id=Gtk.STOCK_JUMP_TO)
        self.__jump_to.set_tooltip_text(_("Change focus"))
        self.__jump_to.connect('toggled',
                               self.__change_pointer,
                               POINTER_JUMP_TO)

        self.__info = Gtk.RadioToolButton(group=self.__jump_to,
                                          stock_id=Gtk.STOCK_INFO)
        self.__info.set_tooltip_text(_("Show information"))
        self.__info.connect('toggled',
                            self.__change_pointer,
                            POINTER_INFO)

        self.__group = Gtk.RadioToolButton(group=self.__jump_to,
                                           stock_id=Gtk.STOCK_ADD)
        self.__group.set_tooltip_text(_("Group children"))
        self.__group.connect('toggled',
                             self.__change_pointer,
                             POINTER_GROUP)

        self.__region = Gtk.RadioToolButton(group=self.__jump_to,
                                            stock_id=Gtk.STOCK_SELECT_COLOR)
        self.__region.set_tooltip_text(_("Fill region"))
        self.__region.connect('toggled',
                              self.__change_pointer,
                              POINTER_FILL)

        self.__region_color = Gtk.ComboBoxText()
        self.__region_color.append_text(_("Red"))
        self.__region_color.append_text(_("Yellow"))
        self.__region_color.append_text(_("Green"))
        self.__region_color.connect('changed', self.__change_region)
        self.__region_color.set_active(self.radialnet.get_region_color())

        self.__tbox.bw_attach_next(self.__jump_to)
        self.__tbox.bw_attach_next(self.__info)
        self.__tbox.bw_attach_next(self.__group)
        self.__tbox.bw_attach_next(self.__region)

        self.__vbox.bw_pack_start_noexpand_nofill(self.__tbox)
        self.__vbox.bw_pack_start_noexpand_nofill(self.__region_color)

        self.bw_add(self.__vbox)

        self.__jump_to.set_active(True)
        self.__region_color.set_no_show_all(True)
        self.__region_color.hide()


    def __change_pointer(self, widget, pointer):
        """
        """
        if pointer != self.radialnet.get_pointer_status():
            self.radialnet.set_pointer_status(pointer)

        if pointer == POINTER_FILL:
            self.__region_color.show()
        else:
            self.__region_color.hide()


    def __change_region(self, widget):
        """
        """
        self.radialnet.set_region_color(self.__region_color.get_active())



class ControlVariableWidget(Gtk.DrawingArea):
    """
    """
    def __init__(self, name, value, update, increment=1):
        """
        """
        Gtk.DrawingArea.__init__(self)

        self.__variable_name = name
        self.__value = value
        self.__update = update
        self.__increment_pass = increment

        self.__radius = 6
        self.__increment_time = 100

        self.__pointer_position = 0
        self.__active_increment = False

        self.__last_value = self.__value()

        self.connect('draw', self.expose)
        self.connect('button_press_event', self.button_press)
        self.connect('button_release_event', self.button_release)
        self.connect('motion_notify_event', self.motion_notify)

        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK |
                        #Gtk.gdk.MOTION_NOTIFY |
                        Gdk.EventMask.POINTER_MOTION_HINT_MASK |
                        Gdk.EventMask.POINTER_MOTION_MASK)

        GObject.timeout_add(REFRESH_RATE, self.verify_value)


    def verify_value(self):
        """
        """
        if self.__value() != self.__last_value:
            self.__last_value = self.__value()

        self.queue_draw()

        return True


    def button_press(self, widget, event):
        """
        """
        self.__active_increment = False
        pointer = self.get_pointer()

        if self.__button_is_clicked(pointer) and event.button == 1:

            event.window.set_cursor(Gdk.Cursor(Gdk.CursorType.HAND2))
            self.__active_increment = True
            self.__increment_value()


    def button_release(self, widget, event):
        """
        """
        event.window.set_cursor(Gdk.Cursor(Gdk.CursorType.LEFT_PTR))

        self.__active_increment = False
        self.__pointer_position = 0

        self.queue_draw()


    def motion_notify(self, widget, event):
        """
        Drawing callback
        @type  widget: GtkWidget
        @param widget: Gtk widget superclass
        @type  event: GtkEvent
        @param event: Gtk event of widget
        @rtype: boolean
        @return: Indicator of the event propagation
        """
        if self.__active_increment == True:

            xc, yc = self.__center_of_widget
            x, _ = self.get_pointer()

            if x - self.__radius > 0 and x + self.__radius < 2 * xc:
                self.__pointer_position = x - xc

        self.queue_draw()


    def expose(self, widget, context):
        """
        Drawing callback
        @type  widget: GtkWidget
        @param widget: Gtk widget superclass
        @type  context: GtkEvent
        @param context: cairo_t context
        @rtype: boolean
        @return: Indicator of the event propagation
        """
        self.set_size_request(100, 30)

        self.context = context
        self.__draw()

        return True


    def __draw(self):
        """
        """
        allocation = self.get_allocation()

        self.__center_of_widget = (allocation.width / 2,
                                   allocation.height / 2)

        xc, yc = self.__center_of_widget

        # draw line
        self.context.set_line_width(1)
        self.context.set_dash([1,2])
        self.context.move_to(self.__radius,
                             yc + self.__radius)
        self.context.line_to(2 * xc - 5,
                             yc + self.__radius)
        self.context.stroke()

        # draw text
        self.context.set_dash([1,0])
        self.context.set_font_size(10)

        width = self.context.text_extents(self.__variable_name)[2]
        self.context.move_to(5, yc - self.__radius)
        self.context.show_text(self.__variable_name)

        width = self.context.text_extents(str(self.__value()))[2]
        self.context.move_to(2 * xc - width - 5, yc - self.__radius)
        self.context.show_text(str(self.__value()))

        self.context.set_line_width(1)
        self.context.stroke()

        # draw node
        self.context.arc(xc + self.__pointer_position,
                         yc + self.__radius,
                         self.__radius, 0, 2 * math.pi)
        if self.__active_increment == True:
            self.context.set_source_rgb(0.0, 0.0, 0.0)
        else:
            self.context.set_source_rgb(1.0, 1.0, 1.0)
        self.context.fill_preserve()
        self.context.set_source_rgb(0.0, 0.0, 0.0)
        self.context.stroke()


    def __button_is_clicked(self, pointer):
        """
        """
        xc, yc = self.__center_of_widget
        center = (xc, yc + self.__radius)

        if geometry.is_in_circle(pointer, 6, center) == True:
            return True

        return False


    def __increment_value(self):
        """
        """
        self.__update(self.__value() + self.__pointer_position / 4)

        self.queue_draw()

        if self.__active_increment == True:

            GObject.timeout_add(self.__increment_time,
                                self.__increment_value)


    def set_value_function(self, value):
        """
        """
        self.__value = value


    def set_update_function(self, update):
        """
        """
        self.__update = update



class ControlVariable(bw.BWHBox):
    """
    """
    def __init__(self, name, get_function, set_function, increment=1):
        """
        """
        bw.BWHBox.__init__(self, spacing=0)

        self.__increment_pass = increment
        self.__increment_time = 200
        self.__increment = False

        self.__name = name
        self.__get_function = get_function
        self.__set_function = set_function

        self.__create_widgets()


    def __create_widgets(self):
        """
        """
        self.__control = ControlVariableWidget(self.__name,
                                               self.__get_function,
                                               self.__set_function,
                                               self.__increment_pass)

        self.__left_button = Gtk.Button()
        self.__left_button.set_size_request(20, 20)
        self.__left_arrow = Gtk.Arrow(Gtk.ArrowType.LEFT, Gtk.ShadowType.NONE)
        self.__left_button.add(self.__left_arrow)
        self.__left_button.connect('pressed',
                                   self.__pressed,
                                   -self.__increment_pass)
        self.__left_button.connect('released', self.__released)

        self.__right_button = Gtk.Button()
        self.__right_button.set_size_request(20, 20)
        self.__right_arrow = Gtk.Arrow(Gtk.ArrowType.RIGHT,
                                       Gtk.ShadowType.NONE)
        self.__right_button.add(self.__right_arrow)
        self.__right_button.connect('pressed',
                                    self.__pressed,
                                    self.__increment_pass)
        self.__right_button.connect('released', self.__released)

        self.bw_pack_start_noexpand_nofill(self.__left_button)
        self.bw_pack_start_expand_fill(self.__control)
        self.bw_pack_start_noexpand_nofill(self.__right_button)


    def __pressed(self, widget, increment):
        """
        """
        self.__increment = True
        self.__increment_function(increment)


    def __increment_function(self, increment):
        """
        """
        if self.__increment:

            self.__set_function(self.__get_function() + increment)
            self.__control.verify_value()

            GObject.timeout_add(self.__increment_time,
                                self.__increment_function,
                                increment)


    def __released(self, widget):
        """
        """
        self.__increment = False




class ControlFisheye(bw.BWVBox):
    """
    """
    def __init__(self, radialnet):
        """
        """
        bw.BWVBox.__init__(self)
        self.set_border_width(6)

        self.radialnet = radialnet
        self.__ring_max_value = self.radialnet.get_number_of_rings()

        self.__create_widgets()


    def __create_widgets(self):
        """
        """
        self.__params = bw.BWHBox()

        self.__fisheye_label = Gtk.Label(_("<b>Fisheye</b> on ring"))
        self.__fisheye_label.set_use_markup(True)

        self.__ring = Gtk.Adjustment(0, 0, self.__ring_max_value, 0.01, 0.01)

        self.__ring_spin = Gtk.SpinButton(adjustment=self.__ring)
        self.__ring_spin.set_digits(2)

        self.__ring_scale = Gtk.HScale(adjustment=self.__ring)
        self.__ring_scale.set_size_request(100, -1)
        self.__ring_scale.set_digits(2)
        self.__ring_scale.set_value_pos(Gtk.PositionType.LEFT)
        self.__ring_scale.set_draw_value(False)
        #self.__ring_scale.set_update_policy(Gtk.UPDATE_CONTINUOUS)

        self.__interest_label = Gtk.Label(_("with interest factor"))
        self.__interest = Gtk.Adjustment(0, 0, 10, 0.01)
        self.__interest_spin = Gtk.SpinButton(adjustment=self.__interest)
        self.__interest_spin.set_digits(2)

        self.__spread_label = Gtk.Label(_("and spread factor"))
        self.__spread = Gtk.Adjustment(0, -1.0, 1.0, 0.01, 0.01)
        self.__spread_spin = Gtk.SpinButton(adjustment=self.__spread)
        self.__spread_spin.set_digits(2)

        self.__params.bw_pack_start_noexpand_nofill(self.__fisheye_label)
        self.__params.bw_pack_start_noexpand_nofill(self.__ring_spin)
        self.__params.bw_pack_start_expand_fill(self.__ring_scale)
        self.__params.bw_pack_start_noexpand_nofill(self.__interest_label)
        self.__params.bw_pack_start_noexpand_nofill(self.__interest_spin)
        self.__params.bw_pack_start_noexpand_nofill(self.__spread_label)
        self.__params.bw_pack_start_noexpand_nofill(self.__spread_spin)

        self.bw_pack_start_noexpand_nofill(self.__params)

        self.__ring.connect('value_changed', self.__change_ring)
        self.__interest.connect('value_changed', self.__change_interest)
        self.__spread.connect('value_changed', self.__change_spread)

        GObject.timeout_add(REFRESH_RATE, self.__update_fisheye)


    def __update_fisheye(self):
        """
        """
        # adjust ring scale to radialnet number of nodes
        ring_max_value = self.radialnet.get_number_of_rings() - 1

        if ring_max_value != self.__ring_max_value:

            value = self.__ring.get_value()

            if value == 0 and ring_max_value != 0:
                value = 1

            elif value > ring_max_value:
                value = ring_max_value

            self.__ring.configure(value, 1, ring_max_value, 0.01, 0.01, 0)
            self.__ring_max_value = ring_max_value

            self.__ring_scale.queue_draw()

        # check ring value
        ring_value = self.radialnet.get_fisheye_ring()

        if self.__ring.get_value() != ring_value:
            self.__ring.set_value(ring_value)

        # check interest value
        interest_value = self.radialnet.get_fisheye_interest()

        if self.__interest.get_value() != interest_value:
            self.__interest.set_value(interest_value)

        # check spread value
        spread_value = self.radialnet.get_fisheye_spread()

        if self.__spread.get_value() != spread_value:
            self.__spread.set_value(spread_value)

        return True


    def active_fisheye(self):
        """
        """
        self.radialnet.set_fisheye(True)
        self.__change_ring()
        self.__change_interest()


    def deactive_fisheye(self):
        """
        """
        self.radialnet.set_fisheye(False)


    def __change_ring(self, widget=None):
        """
        """
        if not self.radialnet.is_in_animation():
            self.radialnet.set_fisheye_ring(self.__ring.get_value())
        else:
            self.__ring.set_value(self.radialnet.get_fisheye_ring())


    def __change_interest(self, widget=None):
        """
        """
        if not self.radialnet.is_in_animation():
            self.radialnet.set_fisheye_interest(self.__interest.get_value())
        else:
            self.__interest.set_value(self.radialnet.get_fisheye_interest())


    def __change_spread(self, widget=None):
        """
        """
        if not self.radialnet.is_in_animation():
            self.radialnet.set_fisheye_spread(self.__spread.get_value())
        else:
            self.__spread.set_value(self.radialnet.get_fisheye_spread())



class ControlInterpolation(bw.BWExpander):
    """
    """
    def __init__(self, radialnet):
        """
        """
        bw.BWExpander.__init__(self, _("Interpolation"))

        self.radialnet = radialnet

        self.__create_widgets()


    def __create_widgets(self):
        """
        """
        self.__vbox = bw.BWVBox()

        self.__cartesian_radio = Gtk.RadioButton(label=_("Cartesian"))
        self.__polar_radio = Gtk.RadioButton(group=self.__cartesian_radio,
                                             label=_("Polar"))
        self.__cartesian_radio.connect('toggled',
                                       self.__change_system,
                                       INTERPOLATION_CARTESIAN)
        self.__polar_radio.connect('toggled',
                                   self.__change_system,
                                   INTERPOLATION_POLAR)

        self.__system_box = bw.BWHBox()
        self.__system_box.bw_pack_start_noexpand_nofill(self.__polar_radio)
        self.__system_box.bw_pack_start_noexpand_nofill(self.__cartesian_radio)

        self.__frames_box = bw.BWHBox()
        self.__frames_label = Gtk.Label(_("Frames"))
        self.__frames_label.set_alignment(0.0, 0.5)
        self.__frames = Gtk.Adjustment(self.radialnet.get_number_of_frames(),
                                       1,
                                       1000,
                                       1)
        self.__frames.connect('value_changed', self.__change_frames)
        self.__frames_spin = Gtk.SpinButton(adjustment=self.__frames)
        self.__frames_box.bw_pack_start_expand_fill(self.__frames_label)
        self.__frames_box.bw_pack_start_noexpand_nofill(self.__frames_spin)

        self.__vbox.bw_pack_start_noexpand_nofill(self.__frames_box)
        self.__vbox.bw_pack_start_noexpand_nofill(self.__system_box)

        self.bw_add(self.__vbox)

        GObject.timeout_add(REFRESH_RATE, self.__update_animation)


    def __update_animation(self):
        """
        """
        active = self.radialnet.get_interpolation()

        if active == INTERPOLATION_CARTESIAN:
            self.__cartesian_radio.set_active(True)

        else:
            self.__polar_radio.set_active(True)

        return True


    def __change_system(self, widget, value):
        """
        """
        if not self.radialnet.set_interpolation(value):

            active = self.radialnet.get_interpolation()

            if active == INTERPOLATION_CARTESIAN:
                self.__cartesian_radio.set_active(True)

            else:
                self.__polar_radio.set_active(True)


    def __change_frames(self, widget):
        """
        """
        if not self.radialnet.set_number_of_frames(self.__frames.get_value()):
            self.__frames.set_value(self.radialnet.get_number_of_frames())



class ControlLayout(bw.BWExpander):
    """
    """
    def __init__(self, radialnet):
        """
        """
        bw.BWExpander.__init__(self, _("Layout"))

        self.radialnet = radialnet

        self.__create_widgets()


    def __create_widgets(self):
        """
        """
        self.__hbox = bw.BWHBox()

        self.__layout = Gtk.ComboBoxText()
        self.__layout.append_text(_("Symmetric"))
        self.__layout.append_text(_("Weighted"))
        self.__layout.set_active(self.radialnet.get_layout())
        self.__layout.connect('changed', self.__change_layout)
        self.__force = Gtk.ToolButton(Gtk.STOCK_REFRESH)
        self.__force.connect('clicked', self.__force_update)

        self.__hbox.bw_pack_start_expand_fill(self.__layout)
        self.__hbox.bw_pack_start_noexpand_nofill(self.__force)

        self.bw_add(self.__hbox)

        self.__check_layout()


    def __check_layout(self):
        """
        """
        if self.__layout.get_active() == LAYOUT_WEIGHTED:
            self.__force.set_sensitive(True)

        else:
            self.__force.set_sensitive(False)

        return True


    def __force_update(self, widget):
        """
        """
        self.__fisheye_ring = self.radialnet.get_fisheye_ring()
        self.radialnet.update_layout()


    def __change_layout(self, widget):
        """
        """
        if not self.radialnet.set_layout(self.__layout.get_active()):
            self.__layout.set_active(self.radialnet.get_layout())

        else:
            self.__check_layout()



class ControlRingGap(bw.BWVBox):
    """
    """
    def __init__(self, radialnet):
        """
        """
        bw.BWVBox.__init__(self)

        self.radialnet = radialnet

        self.__create_widgets()


    def __create_widgets(self):
        """
        """
        self.__radius = ControlVariable(_("Ring gap"),
                                        self.radialnet.get_ring_gap,
                                        self.radialnet.set_ring_gap)

        self.__label = Gtk.Label(_("Lower ring gap"))
        self.__label.set_alignment(0.0, 0.5)
        self.__adjustment = Gtk.Adjustment(self.radialnet.get_min_ring_gap(),
                                           0,
                                           50,
                                           1)
        self.__spin = Gtk.SpinButton(adjustment=self.__adjustment)
        self.__spin.connect('value_changed', self.__change_lower)

        self.__lower_hbox = bw.BWHBox()
        self.__lower_hbox.bw_pack_start_expand_fill(self.__label)
        self.__lower_hbox.bw_pack_start_noexpand_nofill(self.__spin)

        self.bw_pack_start_noexpand_nofill(self.__radius)
        self.bw_pack_start_noexpand_nofill(self.__lower_hbox)


    def __change_lower(self, widget):
        """
        """
        if not self.radialnet.set_min_ring_gap(self.__adjustment.get_value()):
            self.__adjustment.set_value(self.radialnet.get_min_ring_gap())



class ControlOptions(bw.BWScrolledWindow):
    """
    """
    def __init__(self, radialnet):
        """
        """
        bw.BWScrolledWindow.__init__(self)

        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.set_shadow_type(Gtk.ShadowType.NONE)
        self.set_min_content_height(100)

        self.radialnet = radialnet

        self.__create_widgets()


    def __create_widgets(self):
        """
        """
        self.__liststore = Gtk.ListStore(GObject.TYPE_BOOLEAN,
                                         GObject.TYPE_STRING)

        self.__liststore.append([None, _("address")])     # address
        self.__liststore.append([None, _("hostname")])    # hostname
        self.__liststore.append([None, _("icon")])        # icon
        self.__liststore.append([None, _("latency")])     # latency
        self.__liststore.append([None, _("ring")])        # ring
        self.__liststore.append([None, _("region")])      # region
        self.__liststore.append([None, _("slow in/out")]) # slow in/out

        self.__cell_toggle = Gtk.CellRendererToggle()
        self.__cell_toggle.set_property('activatable', True)
        self.__cell_toggle.connect('toggled',
                                   self.__change_option,
                                   self.__liststore)

        self.__column_toggle = Gtk.TreeViewColumn('', self.__cell_toggle)
        self.__column_toggle.add_attribute(self.__cell_toggle, 'active', 0)

        self.__cell_text = Gtk.CellRendererText()

        self.__column_text = Gtk.TreeViewColumn(_("Enable"),
                                                self.__cell_text,
                                                text=1)

        self.__treeview = Gtk.TreeView(self.__liststore)
        self.__treeview.set_enable_search(True)
        self.__treeview.set_search_column(1)
        self.__treeview.append_column(self.__column_toggle)
        self.__treeview.append_column(self.__column_text)

        self.add_with_viewport(self.__treeview)

        GObject.timeout_add(REFRESH_RATE, self.__update_options)


    def __update_options(self):
        """
        """
        model = self.__liststore

        model[OPTIONS.index('address')][0] = self.radialnet.get_show_address()
        model[OPTIONS.index('hostname')][0] = self.radialnet.get_show_hostname()
        model[OPTIONS.index('icon')][0] = self.radialnet.get_show_icon()
        model[OPTIONS.index('latency')][0] = self.radialnet.get_show_latency()
        model[OPTIONS.index('ring')][0] = self.radialnet.get_show_ring()
        model[OPTIONS.index('region')][0] = self.radialnet.get_show_region()
        model[OPTIONS.index('slow in/out')][0] = self.radialnet.get_slow_inout()

        return True


    def __change_option(self, cell, option, model):
        """
        """
        option = int(option)
        model[option][0] = not model[option][0]

        if OPTIONS[option] == 'address':
            self.radialnet.set_show_address(model[option][0])

        elif OPTIONS[option] == 'hostname':
            self.radialnet.set_show_hostname(model[option][0])

        elif OPTIONS[option] == 'icon':
            self.radialnet.set_show_icon(model[option][0])

        elif OPTIONS[option] == 'latency':
            self.radialnet.set_show_latency(model[option][0])

        elif OPTIONS[option] == 'ring':
            self.radialnet.set_show_ring(model[option][0])

        elif OPTIONS[option] == 'region':
            self.radialnet.set_show_region(model[option][0])

        elif OPTIONS[option] == 'slow in/out':
            self.radialnet.set_slow_inout(model[option][0])



class ControlView(bw.BWExpander):
    """
    """
    def __init__(self, radialnet):
        """
        """
        bw.BWExpander.__init__(self, _("View"))
        self.set_expanded(True)

        self.radialnet = radialnet

        self.__create_widgets()


    def __create_widgets(self):
        """
        """
        self.__vbox = bw.BWVBox(spacing=0)

        self.__zoom = ControlVariable(_("Zoom"),
                                      self.radialnet.get_zoom,
                                      self.radialnet.set_zoom)

        self.__ring_gap = ControlRingGap(self.radialnet)
        self.__navigation = ControlNavigation(self.radialnet)

        self.__options = ControlOptions(self.radialnet)
        self.__options.set_border_width(0)

        self.__vbox.bw_pack_start_expand_nofill(self.__options)
        self.__vbox.bw_pack_start_noexpand_nofill(self.__navigation)
        self.__vbox.bw_pack_start_noexpand_nofill(self.__zoom)
        self.__vbox.bw_pack_start_noexpand_nofill(self.__ring_gap)

        self.bw_add(self.__vbox)



class ControlNavigation(Gtk.DrawingArea):
    """
    """
    def __init__(self, radialnet):
        """
        """
        Gtk.DrawingArea.__init__(self)

        self.radialnet = radialnet

        self.__rotate_node = PolarCoordinate()
        self.__rotate_node.set_coordinate(40, 90)
        self.__center_of_widget = (50, 50)
        self.__moving = None
        self.__centering = False
        self.__rotating = False
        self.__move_pass = 100

        self.__move_position = (0, 0)
        self.__move_addition = [(-1, 0),
                                (-1,-1),
                                ( 0,-1),
                                ( 1,-1),
                                ( 1, 0),
                                ( 1, 1),
                                ( 0, 1),
                                (-1, 1)]

        self.__move_factor = 1
        self.__move_factor_limit = 20

        self.__rotate_radius = 6
        self.__move_radius = 6

        self.__rotate_clicked = False
        self.__move_clicked = None

        self.connect('draw', self.expose)
        self.connect('button_press_event', self.button_press)
        self.connect('button_release_event', self.button_release)
        self.connect('motion_notify_event', self.motion_notify)
        self.connect('enter_notify_event', self.enter_notify)
        self.connect('leave_notify_event', self.leave_notify)
        self.connect('key_press_event', self.key_press)
        self.connect('key_release_event', self.key_release)

        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK |
                        Gdk.EventMask.ENTER_NOTIFY_MASK |
                        Gdk.EventMask.LEAVE_NOTIFY_MASK |
                        #Gdk.EventMask.MOTION_NOTIFY |
                        #Gdk.EventMask.NOTHING |
                        Gdk.EventMask.KEY_PRESS_MASK |
                        Gdk.EventMask.KEY_RELEASE_MASK |
                        Gdk.EventMask.POINTER_MOTION_HINT_MASK |
                        Gdk.EventMask.POINTER_MOTION_MASK)

        self.__rotate_node.set_coordinate(40, self.radialnet.get_rotation())


    def key_press(self, widget, event):
        """
        """
        key = Gtk.gdk.keyval_name(event.keyval)

        self.queue_draw()

        return True


    def key_release(self, widget, event):
        """
        """
        key = Gtk.gdk.keyval_name(event.keyval)

        self.queue_draw()

        return True


    def enter_notify(self, widget, event):
        """
        """
        return False


    def leave_notify(self, widget, event):
        """
        """
        self.queue_draw()

        return False


    def button_press(self, widget, event):
        """
        Drawing callback
        @type  widget: GtkWidget
        @param widget: Gtk widget superclass
        @type  event: GtkEvent
        @param event: Gtk event of widget
        @rtype: boolean
        @return: Indicator of the event propagation
        """
        pointer = self.get_pointer()

        direction = False

        if self.__rotate_is_clicked(pointer) == True:

            event.window.set_cursor(Gdk.Cursor(Gdk.CursorType.HAND2))
            self.__rotating = True

        direction = self.__move_is_clicked(pointer)

        if direction != None and self.__moving == None:

            event.window.set_cursor(Gdk.Cursor(Gdk.CursorType.HAND2))
            self.__moving = direction
            self.__move_in_direction(direction)

        if self.__center_is_clicked(pointer) == True:

            event.window.set_cursor(Gdk.Cursor(Gdk.CursorType.HAND2))
            self.__centering = True
            self.__move_position = (0, 0)
            self.radialnet.set_translation(self.__move_position)

        self.queue_draw()

        return False


    def button_release(self, widget, event):
        """
        Drawing callback
        @type  widget: GtkWidget
        @param widget: Gtk widget superclass
        @type  event: GtkEvent
        @param event: Gtk event of widget
        @rtype: boolean
        @return: Indicator of the event propagation
        """
        self.__moving = None        # stop moving
        self.__centering = False
        self.__rotating = False     # stop rotate
        self.__move_factor = 1

        event.window.set_cursor(Gdk.Cursor(Gdk.CursorType.LEFT_PTR))

        self.queue_draw()

        return False


    def motion_notify(self, widget, event):
        """
        Drawing callback
        @type  widget: GtkWidget
        @param widget: Gtk widget superclass
        @type  event: GtkEvent
        @param event: Gtk event of widget
        @rtype: boolean
        @return: Indicator of the event propagation
        """
        xc, yc = self.__center_of_widget
        x, y = self.get_pointer()

        status = not self.radialnet.is_in_animation()
        status = status and not self.radialnet.is_empty()

        if self.__rotating == True and status:

            r, t = self.__rotate_node.get_coordinate()
            t = math.degrees(math.atan2(yc - y, x - xc))

            if t < 0:
                t = 360 + t

            self.radialnet.set_rotation(t)
            self.__rotate_node.set_coordinate(r, t)

            self.queue_draw()
        
        return False


    def expose(self, widget, context):
        """
        Drawing callback
        @type  widget: GtkWidget
        @param widget: Gtk widget superclass
        @type  context: cairo_t
        @param event: cairo.Context pf the widget
        @rtype: boolean
        @return: Indicator of the event propagation
        """
        self.set_size_request(120, 130)

        self.context = context
        self.__draw()

        return False


    def __draw_rotate_control(self):
        """
        """
        xc, yc = self.__center_of_widget
        r, t = self.__rotate_node.get_coordinate()
        x, y = self.__rotate_node.to_cartesian()

        # draw text
        self.context.set_font_size(10)
        self.context.move_to(xc - 49, yc - 48)
        self.context.show_text(_("Navigation"))

        width = self.context.text_extents(str(int(t)))[2]
        self.context.move_to(xc + 49 - width - 2, yc - 48)
        self.context.show_text(str(round(t, 1)))
        self.context.set_line_width(1)
        self.context.stroke()

        # draw arc
        self.context.set_dash([1,2])
        self.context.arc(xc, yc, 40, 0, 2 * math.pi)
        self.context.set_source_rgb(0.0, 0.0, 0.0)
        self.context.set_line_width(1)
        self.context.stroke()

        # draw node
        self.context.set_dash([1,0])
        self.context.arc(xc + x, yc - y, self.__rotate_radius, 0, 2 * math.pi)

        if self.__rotating == True:
            self.context.set_source_rgb(0.0, 0.0, 0.0)

        else:
            self.context.set_source_rgb(1.0, 1.0, 1.0)

        self.context.fill_preserve()
        self.context.set_source_rgb(0.0, 0.0, 0.0)
        self.context.set_line_width(1)
        self.context.stroke()

        return False


    def __draw_move_control(self):
        """
        """
        xc, yc = self.__center_of_widget
        pc = PolarCoordinate()

        self.context.set_dash([1,1])
        self.context.arc(xc, yc, 23, 0, 2 * math.pi)
        self.context.set_source_rgb(0.0, 0.0, 0.0)
        self.context.set_line_width(1)
        self.context.stroke()

        for i in range(8):

            pc.set_coordinate(23, 45 * i)
            x, y = pc.to_cartesian()
        
            self.context.set_dash([1,1])
            self.context.move_to(xc, yc)
            self.context.line_to(xc + x, yc - y)
            self.context.stroke()

            self.context.set_dash([1,0])
            self.context.arc(xc + x, yc - y, self.__move_radius, 0, 2 * math.pi)

            if i == self.__moving:
                self.context.set_source_rgb(0.0, 0.0, 0.0)
            else:
                self.context.set_source_rgb(1.0, 1.0, 1.0)
            self.context.fill_preserve()
            self.context.set_source_rgb(0.0, 0.0, 0.0)
            self.context.set_line_width(1)
            self.context.stroke()

        self.context.arc(xc, yc, 6, 0, 2 * math.pi)

        if self.__centering == True:
            self.context.set_source_rgb(0.0, 0.0, 0.0)
        else:
            self.context.set_source_rgb(1.0, 1.0, 1.0)
        self.context.fill_preserve()
        self.context.set_source_rgb(0.0, 0.0, 0.0)
        self.context.set_line_width(1)
        self.context.stroke()

        return False


    def __draw(self):
        """
        Drawing method
        """
        # Getting allocation reference
        allocation = self.get_allocation()

        self.__center_of_widget = (allocation.width / 2,
                                   allocation.height / 2)

        self.__draw_rotate_control()
        self.__draw_move_control()

        return False


    def __move_in_direction(self, direction):
        """
        """
        if self.__moving != None:

            bx, by = self.__move_position
            ax, ay = self.__move_addition[direction]

            self.__move_position = (bx + self.__move_factor * ax,
                                    by + self.__move_factor * ay)
            self.radialnet.set_translation(self.__move_position)

            if self.__move_factor < self.__move_factor_limit:
                self.__move_factor += 1

            GObject.timeout_add(self.__move_pass,
                                self.__move_in_direction,
                                direction)

        return False


    def __rotate_is_clicked(self, pointer):
        """
        """
        xn, yn = self.__rotate_node.to_cartesian()
        xc, yc = self.__center_of_widget

        center = (xc + xn, yc - yn)
        result = geometry.is_in_circle(pointer, self.__rotate_radius, center)

        if result == True:
            return True

        return False


    def __center_is_clicked(self, pointer):
        """
        """
        result = geometry.is_in_circle(pointer,
                                       self.__move_radius,
                                       self.__center_of_widget)

        if result == True:
            return True

        return False


    def __move_is_clicked(self, pointer):
        """
        """
        xc, yc = self.__center_of_widget
        pc = PolarCoordinate()

        for i in range(8):

            pc.set_coordinate(23, 45 * i)
            x, y = pc.to_cartesian()
        
            center = (xc + x, yc - y)
            result = geometry.is_in_circle(pointer,
                                           self.__move_radius,
                                           center)

            if result == True:
                return i

        return None


