# preferences.py
#
# Copyright 2020 Alexey Mikhailov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Handy', '1')
from gi.repository import Gtk, Handy, Gio
from .recapp_constants import recapp_constants as constants


@Gtk.Template(resource_path=constants['RESOURCEID'] + '/preferences.ui')
class PreferencesWindow(Handy.PreferencesWindow):
    __gtype_name__ = "hdy_preferences_dialog"

    formats_combobox = Gtk.Template.Child()
    fps_combobox = Gtk.Template.Child()
    high_quality_switcher = Gtk.Template.Child()
    startup_sound_switcher = Gtk.Template.Child()

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.settings = Gio.Settings.new(constants["APPID"])
        self.formats_combobox.set_active(self.settings.get_enum('video-format'))
        self.fps_combobox.set_active(self.settings.get_enum('frames-per-second'))
        self.high_quality_switcher.set_active(self.settings.get_boolean('high-video-quality'))
        self.startup_sound_switcher.set_active(self.settings.get_boolean('sound-on-startup'))

    @Gtk.Template.Callback()
    def on_formats_combobox_changed(self, combobox):
        self.settings.set_enum('video-format', combobox.get_active())


    @Gtk.Template.Callback()
    def on_fps_combobox_changed(self, combobox):
        self.settings.set_enum('frames-per-second', combobox.get_active())

    @Gtk.Template.Callback()
    def on_high_quality_switcher_state_set(self, switcher, state):
        self.settings.set_boolean('high-video-quality', state)

    @Gtk.Template.Callback()
    def on_startup_sound_switcher_state_set(self, switcher, state):
        self.settings.set_boolean('sound-on-startup', state)

