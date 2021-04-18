# window.py
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

import os
from locale import gettext as _

from gi.repository import Gdk, Gio, GLib, Gtk, Handy

from .recording import Recording
from .recapp_constants import recapp_constants as constants
from .preferences import PreferencesWindow
from .about import AboutWindow
from .shortcuts import RecAppShortcuts

# TODO Not working yet: record computer sounds (keyboard shortcut already working)


@Gtk.Template(resource_path=constants['RESOURCEID'] + '/window.ui')
class RecappWindow(Handy.ApplicationWindow):
    __gtype_name__ = 'RecAppWindow'

    is_full_screen_mode = True
    _record_button = Gtk.Template.Child()
    _stop_record_button = Gtk.Template.Child()
    _delay_button = Gtk.Template.Child()
    _sound_on_computer = Gtk.Template.Child()
    _record_mouse_switcher = Gtk.Template.Child()
    _fullscreen_mode_button = Gtk.Template.Child()
    _window_mode_button = Gtk.Template.Child()
    _selection_mode_button = Gtk.Template.Child()
    _pause_record_button = Gtk.Template.Child()
    _continue_record_button = Gtk.Template.Child()
    _sound_rowbox = Gtk.Template.Child()
    _menu_button = Gtk.Template.Child()
    _paused_start_stack = Gtk.Template.Child()
    _menu_stack = Gtk.Template.Child()
    _cancel_button = Gtk.Template.Child()
    _time_recording_label = Gtk.Template.Child()
    _recording_label = Gtk.Template.Child()
    _paused_label = Gtk.Template.Child()
    _sound_on_microphone = Gtk.Template.Child()
    _main_stack = Gtk.Template.Child()
    _delay_box = Gtk.Template.Child()
    _record_stop_record_button_stack = Gtk.Template.Child()
    _menu_stack_revealer = Gtk.Template.Child()
    _delay_label = Gtk.Template.Child()
    _paused_start_stack_box = Gtk.Template.Child()
    _main_screen_box = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.application = kwargs["application"]

        accel = Gtk.AccelGroup()
        accel.connect(Gdk.keyval_from_name('q'), Gdk.ModifierType.CONTROL_MASK, 0, self.on_quit)
        self.add_accel_group(accel)
        self.connect("delete-event", self.on_delete_event)

        self.settings = Gio.Settings.new(constants["APPID"])
        self.delay_before_recording = self.settings.get_int('delay')
        self.record_mouse = self.settings.get_boolean('record-mouse-cursor-switch')
        self._sound_on_computer.set_active(self.settings.get_boolean('sound-on-computer'))
        self._sound_on_microphone.set_active(self.settings.get_boolean('sound-on-microphone'))
        self._record_mouse_switcher.set_active(self.record_mouse)
        self._delay_button.set_value(self.delay_before_recording)

        self.recording = Recording(self)

        # Notification actions
        action = Gio.SimpleAction.new("open-folder", None)
        action.connect("activate", self.open_folder)
        self.application.add_action(action)

        action = Gio.SimpleAction.new("open-file", None)
        action.connect("activate", self.open_video_file)
        self.application.add_action(action)

        self.currentFolder = self.get_output_folder()
        if self.recording.is_wayland:
            self.prepare_to_wayland()
        self.recording.find_encoders()

        self.label_context = self._time_recording_label.get_style_context()

    def open_folder(self, notification, action, user_data=None):
        try:
            video_folder_for_open = self.settings.get_string('path-to-save-video-folder')
            Gio.AppInfo.launch_default_for_uri("file:///" + video_folder_for_open.lstrip("/"))

        except Exception as error:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text=_("Unable to open folder")
            )
            dialog.format_secondary_text(str(error))
            dialog.run()
            dialog.destroy()

    def open_video_file(self, notification, action, user_data=None):
        try:
            Gio.AppInfo.launch_default_for_uri(
                "file:///" + self.recording.filename.lstrip("/") + self.recording.extension
            )

        except Exception as error:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text=_("Unable to open file")
            )
            dialog.format_secondary_text(str(error))
            dialog.run()
            dialog.destroy()

    def to_default(self):
        self._main_stack.set_visible_child(self._main_screen_box)
        self._record_stop_record_button_stack.set_visible_child(self._record_button)
        self._menu_stack.set_visible_child(self._menu_button)

    def prepare_for_record(self):
        self._record_stop_record_button_stack.set_visible_child(self._stop_record_button)
        self._main_stack.set_visible_child(self._paused_start_stack_box)
        self._menu_stack.set_visible_child(self._pause_record_button)
        self.label_context.add_class("recording")

    def after_stop_record(self):
        self._record_stop_record_button_stack.set_visible_child(self._record_button)
        self._paused_start_stack.set_visible_child(self._recording_label)
        self._main_stack.set_visible_child(self._main_screen_box)
        self._menu_stack.set_visible_child(self._menu_button)
        self.label_context.remove_class("recording")

    def show_delay_view(self):
        self._main_stack.set_visible_child(self._delay_box)
        self._record_stop_record_button_stack.set_visible_child(self._cancel_button)
        self._menu_stack_revealer.set_reveal_child(False)

    def prepare_to_wayland(self):
        self._sound_rowbox.set_visible(False)
        self._sound_on_computer.set_active(False)
        if GLib.getenv('XDG_CURRENT_DESKTOP') != 'GNOME':
            self._record_button.set_sensitive(False)
            notification = Gio.Notification.new(constants["APPNAME"])
            notification.set_body(_("Sorry, Wayland session is not supported yet."))
            self.application.send_notification(None, notification)

    def get_output_folder(self):
        path = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_VIDEOS)  # XDG-VIDEOS
        if self.settings.get_string('path-to-save-video-folder') == "Default":
            if path is None:  # there is no XDG-VIDEOS folder
                directory = "/RecAppVideo"
                parent_dir = GLib.get_home_dir()
                path = parent_dir + directory  # set up a new path
                if not os.path.exists(path):
                    os.makedirs(path)
                self.settings.set_string('path-to-save-video-folder', path)
            else:
                self.settings.set_string('path-to-save-video-folder', path)  # XDG-VIDEOS
        else:
            path = self.settings.get_string('path-to-save-video-folder')
        return path

    @Gtk.Template.Callback()
    def on_about_button_clicked(self, widget):
        about = AboutWindow(self)
        about.set_program_name(_(constants["APPNAME"]))
        about.set_logo_icon_name(constants["APPID"])
        about.set_version(constants["APPVERSION"])
        about.set_transient_for(self)
        about.run()
        about.destroy()

    @Gtk.Template.Callback()
    def on_shortcuts_button_clicked(self, button):
        shortcuts = RecAppShortcuts(self)
        shortcuts.set_transient_for(self)
        shortcuts.present()

    def on_delete_event(self, w, h):
        if self.recording.is_recording:
            self.recording.stop_recording()

    @Gtk.Template.Callback()
    def on__record_mouse_switcher_state_set(self, switch, state):
        self.record_mouse = state
        self.settings.set_boolean('record-mouse-cursor-switch', state)

    @Gtk.Template.Callback()
    def on__delay_button_change_value(self, spin):
        self.delay_before_recording = spin.get_value_as_int()
        self.settings.set_int('delay', spin.props.value)

    @Gtk.Template.Callback()
    def on__sound_on_computer_state_set(self, switcher, state):
        self.settings.set_boolean('sound-on-computer', state)

    @Gtk.Template.Callback()
    def on__sound_on_microphone_state_set(self, switcher, state):
        self.settings.set_boolean('sound-on-microphone', state)

    @Gtk.Template.Callback()
    def on__record_button_clicked(self, widget):
        self.recording.start_recording()

    @Gtk.Template.Callback()
    def on__stop_record_button_clicked(self, widget):
        self.recording.stop_recording()

    def on_quit(self, window, *args):
        if self.recording.is_recording:
            self.recording.stop_recording()
        self.destroy()

    @Gtk.Template.Callback()
    def on_preferences_button_clicked(self, button):
        preferences = PreferencesWindow(self)
        preferences.set_transient_for(self)
        preferences.show()

    # TODO
    # Connect pause and continue to something

    @Gtk.Template.Callback()
    def on__pause_record_button_clicked(self, widget):
        self._menu_stack.set_visible_child(self._continue_record_button)
        self._paused_start_stack.set_visible_child(self._paused_label)
        self.label_context.remove_class("recording")
        self.recording.is_timer_running = False

    @Gtk.Template.Callback()
    def on__continue_record_button_clicked(self, widget):
        self._menu_stack.set_visible_child(self._pause_record_button)
        self._paused_start_stack.set_visible_child(self._recording_label)
        self.label_context.add_class("recording")
        self.recording.is_timer_running = True

    @Gtk.Template.Callback()
    def on__cancel_button_clicked(self, widget):
        self.recording.cancel_delay()

    # TODO
    # Connect window mode to something

    @Gtk.Template.Callback()
    def on__fullscreen_mode_pressed(self, widget):
        if self._fullscreen_mode_button.get_active():
            self.is_full_screen_mode = True
            self.is_window_mode = False
            self.is_selection_mode = False

    @Gtk.Template.Callback()
    def on__window_mode_pressed(self, widget):
        if self._window_mode_button.get_active():
            self.is_window_mode = True
            self.is_full_screen_mode = False
            self.is_selection_mode = False

    @Gtk.Template.Callback()
    def on__selection_mode_pressed(self, widget):
        if self._selection_mode_button.get_active():
            self.is_selection_mode = True
            self.is_full_screen_mode = False
            self.is_window_mode = False
