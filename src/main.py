# main.py
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
import sys

from .recapp_constants import recapp_constants as constants
from .window import RecappWindow

gi.require_version('Gtk', '3.0')
gi.require_version('Handy', '1')
from gi.repository import Gio, Gtk, Handy, Gst, Gdk  # noqa: E402


class Application(Gtk.Application):
    def __init__(self):
        super().__init__(application_id=constants["APPID"],
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.init_style()

    def do_startup(self):
        Gtk.Application.do_startup(self)
        Gtk.init(sys.argv)
        Gst.init(sys.argv)
        Handy.init()

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = RecappWindow(application=self)
        win.present()

    def init_style(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_resource(constants['RESOURCEID'] + '/style.css')
        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


def main(version):
    app = Application()
    return app.run(sys.argv)
