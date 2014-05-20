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


from gi.repository import Gtk

from GTG import _, ngettext
from GTG.gtk.editor import GnomeConfig


class NotifyCloseUI():

    def __init__(self):
        # Load window tree
        self.builder = Gtk.Builder()
        self.builder.add_from_file(GnomeConfig.NOTIFY_UI_FILE)
        signals = {"on_confirm_activate": self.on_confirm_pressed,
                   "on_delete_cancel": lambda x: x.hide, }
        self.builder.connect_signals(signals)

    def on_confirm_pressed(self, widget):
        self.builder.get_object("notify_dialog").hide()

    def notifyclose(self):
        cdlabel2 = self.builder.get_object("cd-label2")
        cdlabel2.set_label(ngettext(
            "You need to set Due date before closing the task.",
            "You need to set Due date before closing the task.",
            0))

        notifyclose_dialog = self.builder.get_object("notify_dialog")
        notifyclose_dialog.resize(1, 1)
        confirm_button = self.builder.get_object("confirm")
        confirm_button.grab_focus()

        if notifyclose_dialog.run() != 1:
            pass
        notifyclose_dialog.hide()
