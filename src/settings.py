import locale
import multiprocessing
import os
import signal
import sys
import time
from locale import gettext as _
from subprocess import PIPE, Popen

import gi
import pulsectl
from pydbus import SessionBus

from .rec import *
from .recapp_constants import recapp_constants as constants

gi.require_version('Gtk', '3.0')
gi.require_version('Gst', '1.0')
gi.require_version('Notify', '0.7')
gi.require_version('GstPbutils', '1.0')
from gi.repository import Gdk, Gio, GLib, Gst, GstPbutils, Gtk, Notify

Gtk.init(sys.argv)
# initialize GStreamer
Gst.init(sys.argv)

@Gtk.Template(resource_path='/com/github/amikha1lov/RecApp/settings.ui')
class SettingsWindow(Gtk.Window):
    __gtype_name__ = 'SettingsWindow'
    recordFormat = ""
    encoders = ["vp8enc", "x264enc"]
    formats = []

    _formats_combobox = Gtk.Template.Child()
    _frames_combobox = Gtk.Template.Child()
    _video_folder_button = Gtk.Template.Child()
    _quality_video_box = Gtk.Template.Child()
    _quality_video_switcher = Gtk.Template.Child()

    def __init__(self, parent):
        Gtk.Window.__init__(self, transient_for=parent)

        self.settings = Gio.Settings.new(constants["APPID"])
        self.videoFrames = self.settings.get_int('frames')
        self.recordFormat = self.settings.get_string('format-video')
        self._quality_video_switcher.set_active(self.settings.get_boolean("high-quality-switch"))
        self.currentFolder = self.settings.get_string('path-to-save-video-folder')
        self.cpus = multiprocessing.cpu_count() - 1

        if self.currentFolder == "Default":
            if GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_VIDEOS) == None:

                directory = "/RecAppVideo"
                parent_dir = Popen("xdg-user-dir", shell=True, stdout=PIPE).communicate()
                parent_dir = list(parent_dir)
                parent_dir = parent_dir[0].decode().split()[0]
                path = parent_dir + directory

                if not os.path.exists(path):
                    os.makedirs(path)
                self.settings.set_string('path-to-save-video-folder', path)
            else:
                self.settings.set_string('path-to-save-video-folder', GLib.get_user_special_dir(
                    GLib.UserDirectory.DIRECTORY_VIDEOS))
            self._video_folder_button.set_current_folder_uri(
                self.settings.get_string('path-to-save-video-folder'))
        else:
            self._video_folder_button.set_current_folder_uri(self.currentFolder)

        if self.videoFrames == 15:
            self._frames_combobox.set_active(0)
        elif self.videoFrames == 30:
            self._frames_combobox.set_active(1)
        else:
            self._frames_combobox.set_active(2)

        for encoder in self.encoders:
            plugin = Gst.ElementFactory.find(encoder)
            if plugin:
                if (encoder == "vp8enc"):
                    self.formats.append("webm")
                    self.formats.append("mkv")
                elif (encoder == "x264enc"):
                    self.formats.append("mp4")
            else:
                pass
        formats_store = Gtk.ListStore(str)
        for format in self.formats:
            formats_store.append([format])
        self._formats_combobox.set_model(formats_store)
        self._formats_combobox.set_active(
            self.formats.index(self.settings.get_string('format-video')))
        self.recordFormat = self._formats_combobox.get_active_text()

    @Gtk.Template.Callback()
    def on__frames_combobox_changed(self, box):
        frames_combobox_changed(self, box)

    @Gtk.Template.Callback()
    def on__formats_combobox_changed(self, box):
        formats_combobox_changed(self, box)

    @Gtk.Template.Callback()
    def on__quality_video_switcher_state_set(self, switch, gparam):
        quality_video_switcher(self, switch, gparam)

    @Gtk.Template.Callback()
    def on__video_folder_button_file_set(self, button):
        video_folder_button(self, button)


