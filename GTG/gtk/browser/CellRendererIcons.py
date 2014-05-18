# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Getting Things GNOME! - a personal organizer for the GNOME desktop
# Copyright (c) 2008-2013 - Lionel Dricot & Bertrand Rousseau
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------

#=== IMPORT ===================================================================

# system imports
from gi.repository import GObject, GLib, Gtk, Gdk
import cairo
from GTG.tools.logger import Log

#=== MAIN CLASS ===============================================================


class CellRendererIcons(Gtk.CellRendererPixbuf):
    __gproperties__ = {
        'icon': (GObject.TYPE_PYOBJECT, "Icon",
                "Icon", GObject.PARAM_READWRITE),
    }
    # Class methods
    def __init__(self):
        Gtk.CellRendererPixbuf.__init__(self)
        self.tasks = None

    def do_set_property(self, pspec, value):
        if pspec.name == 'icon':
            self.tasks = value
            setattr(self, pspec.name, value)

    def do_get_property(self, pspec):
        return getattr(self, pspec.name)

    def do_render(self, cr, widget, background_area, cell_area, flags):
        count = 0
        if self.tasks is not None:
            tasks = [self.tasks]
        else:
            return

        gdkcontext = cr
        gdkcontext.set_antialias(cairo.ANTIALIAS_NONE)

        # Coordinates of the origin point
        x_align = self.get_property("xalign")
        y_align = self.get_property("yalign")
        orig_x = cell_area.x + int(cell_area.width - 16 *  x_align)
        orig_y = cell_area.y + int((cell_area.height - 16) * y_align)

        for my_task in tasks:

            rect_x = orig_x  * count + 16 * count
            rect_y = orig_y

            try:
                pixbuf = Gtk.IconTheme.get_default().load_icon(
                    'gtk-refresh', 16, 0)
                Gdk.cairo_set_source_pixbuf(gdkcontext, pixbuf,
                                            rect_x, rect_y)
                gdkcontext.paint()
                count = count + 1
            except GLib.GError:
                # In some rare cases an icon could not be found
                # (e.g. wrong set icon path, missing icon)
                # Raising an exception breaks UI and signal catcher badly
                Log.error("Can't load icon ")

GObject.type_register(CellRendererIcons)
