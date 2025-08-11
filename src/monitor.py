#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: Pippim
License: GNU GPLv3
Source: This repository
Description: mserve - Music Server - Multiple Monitor Management
"""

from __future__ import print_function  # Must be first import
from __future__ import with_statement  # Error handling for file opens

# ==============================================================================
#
#       monitor.py - Functions for screen(desktop), monitors and windows
#
#       Check out: https://www.pythoncheatsheet.org/
#             and: https://python-future.org/compatible_idioms.html
#
#       June 14 2023 - Build list of all windows. To find those off-screen
#       July 12 2023 - Interface to/from mserve_config.py
#       July 29 2023 - Fix Monitor.get_active_monitor()
#       May. 11 2024 - mon.get_home_monitor(window) exact or closest monitor
#       Oct. 09 2024 - check_window_geom(...) to force windows visibility
#       Dec. 08 2024 - Suppress GObject future warnings originating from sql.py
#       Jun. 08 2025 - Deprecate center(), get_monitors() & get_tk_window_mon...
#
# ==============================================================================

"""
        Requires:

            Gnome Desktop Toolkit (Gdk)
            python-xlib
            xdotool - For .get_mouse_location()
"""

try:                        # Python 3
    import tkinter as tk
    PYTHON_VER = "3"

except ImportError:         # Python 2
    import Tkinter as tk
    PYTHON_VER = "2"

import os                   # For get_xrandr_monitors()
import sys
import time                 # To use time.time()

from collections import OrderedDict, namedtuple

''' mserve modules (some shared by bserve via symlink) including this one! '''
#import location as lc       # To get USER id
import global_variables as g
import image as img         # Routines for tk & photo images
import sql                  # SQLite3 functions
import external as ext

''' Imported below in functions 
    import wnck
    import gi
        gi.require_version('Gdk', '3.0')
        gi.require_version('Gtk', '3.0')
        gi.require_version('Wnck', '3.0')
        from gi.repository import Gdk, Gtk, Wnck
    import win32gui
    from AppKit import NSWorkspace
'''
''' Logging is duplicated in monitor.py module. Not sure how to apply yet? '''
# https://stackoverflow.com/a/36419702/6929343
# import logging

# https://stackoverflow.com/a/67352300/6929343
# logging.getLogger('PIL').setLevel(logging.WARNING)
# noinspection SpellCheckingInspection
#logging.basicConfig(format='%(asctime)s %(level name)s %(message)s',
#                    level=logging.DEBUG,
#                    stream=sys.stdout)
# inspection SpellCheckingInspection

''' Future code '''


def get_active_window2():
    """ NOT USED

    From: https://stackoverflow.com/a/36419702/6929343
    Get the currently active window.

    Returns
    -------
    string :
        Name of the currently active window.
    """
    active_window_name = None
    logging.info('sys.platform: ' + sys.platform)
    print('sys.platform:', sys.platform)
    if sys.platform in ['linux', 'linux2']:
        # Alternatives: http://unix.stackexchange.com/q/38867/4784
        try:
            import wnck
        except ImportError:
            logging.info("wnck not installed")
            wnck = None
        if wnck is not None:
            screen = wnck.screen_get_default()
            screen.force_update()
            window = screen.get_active_window()
            if window is not None:
                pid = window.get_pid()
                with open("/proc/{pid}/cmdline".format(pid=pid)) as f:
                    active_window_name = f.read()
        else:
            try:
                # Next 3 limes from: https://stackoverflow.com/a/43349245/6929343
                import gi
                gi.require_version('Gtk', '3.0')
                gi.require_version('Wnck', '3.0')
                # Continue with original code:
                from gi.repository import Gtk, Wnck
                gi = "Installed"
            except ImportError:
                logging.info("gi.repository not installed")
                gi = None
            if gi is not None:
                Gtk.init([])  # necessary if not using a Gtk.main() loop
                screen = Wnck.Screen.get_default()
                screen.force_update()  # recommended per Wnck documentation
                active_window = screen.get_active_window()
                pid = active_window.get_pid()
                with open("/proc/{pid}/cmdline".format(pid=pid)) as f:
                    active_window_name = f.read()
    elif sys.platform in ['Windows', 'win32', 'cygwin']:
        # http://stackoverflow.com/a/608814/562769
        import win32gui
        window = win32gui.GetForegroundWindow()
        active_window_name = win32gui.GetWindowText(window)
    elif sys.platform in ['Mac', 'darwin', 'os2', 'os2emx']:
        # http://stackoverflow.com/a/373310/562769
        from AppKit import NSWorkspace
        active_window_name = (
            NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationName'])
    else:
        print("sys.platform={platform} is unknown. Please report."
              .format(platform=sys.platform))
        print(sys.version)
    print("Active window: %s" % str(active_window_name))
    return active_window_name


def get_gtk_window():
    """ Not used """
    # From: https://askubuntu.com/a/303754/307523
    import gi
    gi.require_version('Gdk', '3.0')
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gdk, Gtk

    # Replace w with the GtkWindow of your application
    #w = Gtk.Window()
    # Get the screen from the GtkWindow
    #s = w.get_screen()
    # Using the screen of the Window, the monitor it's on can be identified
    #m = s.get_monitor_at_window(s.get_active_window())
    # Then get the geometry of that monitor
    #monitor = s.get_monitor_geometry(m)
    # This is an example output
    #print("Height: %s, Width: %s, X: %s, Y: %s" %
    #      (monitor.height, monitor.width, monitor.x, monitor.y))


''' Deprecated code '''


def center(window):
    """ 2025-06-08 deprecated

    July 28, 2023... centers on monitor 0, not monitor 2?
    Similar to Monitor.tk_center()

    This is the only function that calls:
        get_tk_window_monitor_dict(window) - Which is only one calling:
        monitors = get_monitors()
        get_monitors() - This function slated for removal


    From: https://stackoverflow.com/a/10018670/6929343
    centers a tkinter window on monitor in multi-monitor setup
    :param window: the main window or Toplevel window to center
    """

    window.update_idletasks()  # Refresh window's current position
    mon_dict = get_tk_window_monitor_dict(window)  # Monitor geometry window is on

    if mon_dict is None:
        # logging.error("No monitors found!")
        print("No monitors found!")
        return None

    # Calculate X, Y of window to center within monitors X, Y, width and height
    x = mon_dict['width'] // 2 - window.winfo_width() // 2 + mon_dict['x']
    y = mon_dict['height'] // 2 - window.winfo_height() // 2 + mon_dict['y']
    x = 30 if x < 0 else x  # Window top left may be off screen!
    y = 30 if y < 0 else y
    window.geometry('+{}+{}'.format(x, y))

    return mon_dict


def get_tk_window_monitor_dict(window):
    """ DEPRECATED 2025-06-08

    Returns the mserve monitor dictionary a tkinter window is on.
    If window is off screen force it into Monitor 1 (index 0).

    Cannot use Gdk_Monitor_At_Window(gdk_window) because it only works on
    Gdk windows.

    :param window: Tkinter root or Toplevel
    """

    monitors = get_monitors()                   # List of monitor dictionaries

    x, y, w, h = get_window_geom_raw(window)    # Tkinter style window geometry

    if x < 0 or x > SCREEN.width():
        x = 30  # Window top left may be off screen!
    if y < 0 or y > SCREEN.height():
        y = 30

    first_monitor = None
    ''' Assumes another function has already set NUMBER_OF_MONITORS '''
    for index in range(NUMBER_OF_MONITORS):
        # Save first monitor if needed later
        monitor = monitors[index]
        if first_monitor is None:
            first_monitor = monitor

        # Most of window must be on monitor to qualify
        if x < monitor['x']:
            continue
        if x >= monitor['x'] + monitor['width'] // 2:
            continue
        if y < monitor['y']:
            continue
        if y >= monitor['y'] + monitor['height'] // 2:
            continue

        # Window is mostly on this monitor.
        return monitor

    # If window off of screen use first monitor
    return first_monitor


def get_monitors():
    """
        # OLDER CODE: Eventually yanked out.

        Get list of monitors in Gnome Desktop

        TODO: Flush displays / pending events first?

        :returns List of dictionaries

    """

    import gi
    gi.require_version('Gdk', '3.0')
    from gi.repository import Gdk

    global DISPLAY, SCREEN, NUMBER_OF_MONITORS, GNOME_VER

    if DISPLAY is None:
        DISPLAY = Gdk.Display.get_default()
        SCREEN = DISPLAY.get_default_screen()

    # Gnome version 3.22 developed new monitor object
    try:
        # Gnome 3.22
        NUMBER_OF_MONITORS = DISPLAY.get_n_monitors()
        primary = False
        GNOME_VER = 3.22
    except AttributeError:
        # Gnome 3.18
        NUMBER_OF_MONITORS = SCREEN.get_n_monitors()
        primary = SCREEN.get_primary_monitor()
        GNOME_VER = 3.18

    # collect data about monitors
    monitors = []
    for index in range(NUMBER_OF_MONITORS):
        mon = {}
        if GNOME_VER == 3.22:
            monitor = DISPLAY.get_monitor(index)
            primary = monitor.is_primary()
            geometry = monitor.get_geometry()
            name = monitor.get_monitor_plug_name()
        else:
            geometry = SCREEN.get_monitor_geometry(index)
            name = SCREEN.get_monitor_plug_name(index)

        #print("Monitor {} = {}x{}+{}+{}".format(
        #    index, geometry.width, geometry.height, geometry.x, geometry.y),
        #    name)

        mon['number'] = index
        mon['name'] = name
        mon['x'] = geometry.x
        mon['y'] = geometry.y
        mon['width'] = geometry.width
        mon['height'] = geometry.height
        if index == primary:
            mon['primary'] = True       # Usually static but user could change
        else:
            mon['primary'] = False

        monitors.append(mon)

    return monitors


"""  REAL REAL REAL REAL REAL REAL REAL REAL REAL REAL REAL REAL REAL REAL """

''' Start of REAL code used today (July 2, 2021) '''

DISPLAY = None  # GDK interface to X11 display server
SCREEN = None  # GDL screen interface for placing windows
NUMBER_OF_MONITORS = 0  # pycharm doesn't like to see 'None'
GNOME_VER = None  # GNOME versions supported are 3.18 and 3.22


class CommonWindow:
    """ Variables common to Monitors().__init__() and Monitors().get_window()
        Prefix wn_ short for Wnck.
    """
    def __init__(self):

        self.wn_dict = {}  # Dict of keys (without wn_ prefix) / values below

        self.wn_xid_long = None  # X11 window ID long integer (ends in L)
        self.wn_xid_str = None  # X11 window ID str(wn_xid_long)
        self.wn_xid_int = None  # X11 window ID int(wn_xid_str)
        self.wn_xid_hex = None  # X11 window ID hex(wn_xid_int)
        # str_wn = str(window.number)  # should remove L in python 2.7.5+
        # int_wn = int(str_wn)  # https://stackoverflow.com/questions
        # hex_wn = hex(int_wn)  # /5917203/python-trailing-l-problem

        self.wn_pid = None  # Linux PID shared by PulseAudio for match 1
        self.wn_name = None  # Full Window Name shared by PulseAudio match 2
        self.wn_app = None  # Window Name's suffix = Application
        self.wn_video = None  # Window Name's prefix = Media name (song / video)
        self.wn_geom = None  # geom.xp, geom.yp, geom.widthp, geom.heightp
        self.wn_x = self.wn_y = self.wn_width = self.wn_height = None
        self.wn_is_active = None  # active window for keystrokes
        self.wn_is_maximized = None  # maximized horizontally and vertically
        self.wn_is_fullscreen = None  # Full screen required for PimTube ad skip


class Monitors(CommonWindow):
    """ Build list of all monitors connected to computer

        Monitor SQL Configuration: 15-char ShortName, Manufacturer, Model,
        Serial Number, Purchase Date, warranty, 60-char LongName, physical size,
        LAN MAC, LAN IP, WiFi MAC, WiFi IP, Backlight MAC, Backlight IP,
        resolution, refresh, adaptive brightness, communication language, power
        on command, power off command, screen off command, screen on command,
        volume up command, volume down command, mute command, un-mute command,
        disable eyesome command, enable eyesome command, xrandr name, monitor 0-#,
        screen width, height, x-offset, y-offset, image (300x300 or so)

    """
    def __init__(self):
        """ Build list of monitors forming desktop (aka X11 screen) """

        """ Duplicate get_window() """
        CommonWindow.__init__(self)  # Recycled class like Toolkit.py CommonTip()

        self.who = "monitors.py Monitors()."
        self.desk_width = 0
        self.desk_height = 0

        import gi
        gi.require_version('Gdk', '3.0')
        from gi.repository import Gdk

        global DISPLAY, SCREEN, NUMBER_OF_MONITORS, GNOME_VER

        if DISPLAY is None:
            DISPLAY = Gdk.Display.get_default()
            SCREEN = DISPLAY.get_default_screen()

        self.gdk_display = DISPLAY          # Traditional for outside
        self.gdk_screen = SCREEN            # Traditional for outside
        primary = None
        # Gnome version 3.22 developed new monitor object
        try:
            # Gnome 3.22
            NUMBER_OF_MONITORS = DISPLAY.get_n_monitors()
            GNOME_VER = 3.22
        except AttributeError:
            # Gnome 3.18
            NUMBER_OF_MONITORS = SCREEN.get_n_monitors()
            primary = SCREEN.get_primary_monitor()
            GNOME_VER = 3.18

        self.screen_width = SCREEN.width()  # Screen width (all monitors)
        self.screen_height = SCREEN.height()  # 3240 not equal to desk_height: 5760
        self.gdk_gnome_version = GNOME_VER  # Traditional for outside attribute

        self.monitors_list = []  # List of dictionaries w/monitor
        self.long_string_list = []  # For combobox
        self.string_list = []  # For combobox
        self.monitor_count = NUMBER_OF_MONITORS
        self.found_monitor = None
        self.found_window = None  # Not really necessary but simpler
        self.primary_monitor = None

        # collect data about monitors
        for index in range(NUMBER_OF_MONITORS):
            mon = OrderedDict()
            if GNOME_VER == 3.22:
                monitor = DISPLAY.get_monitor(index)
                primary = monitor.is_primary()
                geometry = monitor.get_geometry()
                name = monitor.get_monitor_plug_name()
                # 2024-06-28 - Read SQL for monitor attributes like ShortName
            else:
                geometry = SCREEN.get_monitor_geometry(index)
                name = SCREEN.get_monitor_plug_name(index)

            #print("Monitor {} = {}x{}+{}+{}".format(
            #    index, geometry.width, geometry.height, geometry.x, geometry.y),
            #    name)

            # IMPORTANT - Assign in same order as namedtuple!
            mon['number'] = index
            mon['name'] = name
            mon['x'] = geometry.x
            mon['y'] = geometry.y
            mon['width'] = geometry.width
            mon['height'] = geometry.height
            if index == primary:
                mon['primary'] = True  # Usually static but user could change
                # noinspection PyArgumentList
                #self.primary_monitor = Monitor(mon.keys())(*mon.values())
                self.primary_monitor = namedtuple('Monitor', mon.keys())(*mon.values())
            else:
                mon['primary'] = False

            self.found_monitor = namedtuple('Monitor', mon.keys())(*mon.values())
            self.monitors_list.append(self.found_monitor)
            self.long_string_list.append(
                "Screen " + str(index + 1) + ", " + name + ", " + str(geometry.width) +
                "x" + str(geometry.height) + ", +" + str(geometry.x) + "+" +
                str(geometry.y))   
            self.string_list.append(
                name + ": " + str(geometry.width) +
                "x" + str(geometry.height) + "+" + str(geometry.x) + "+" +
                str(geometry.y))

            # Running calculation of desktop width x height
            x2 = geometry.x + geometry.width
            if x2 > self.desk_width:
                self.desk_width = x2
            y2 = geometry.y + geometry.height
            if y2 > self.desk_height:
                self.desk_height = y2

        ''' list of named tuples: Window(xid_long, name, x, y, wid, hgt) '''
        self.windows_list = []  # List populated by self.get_all_windows()
        self.wn_list = []  # 2025-06-12 List populated by self.make_wn_list()

        # Wrap up
        if self.screen_width != self.desk_width:
            print('ERROR monitor.py: SCREEN.width:,', self.screen_width,
                  'not equal to desk_width:', self.desk_width)
        if self.screen_height != self.desk_height:
            print('ERROR monitor.py: SCREEN.height:,', self.screen_height,
                  'not equal to desk_height:', self.desk_height)
        if len(self.monitors_list) < 1:
            print('ERROR monitor.py: No monitors found!')
        if primary is None:
            print('ERROR monitor.py: Primary monitor not found!')

    def deprecated_get_n_monitors(self):
        """ For external call to get number of monitors connected to computer
            2024-06-27 - Deprecated because caller can use self.monitor_count
        """
        return self.monitor_count

    # noinspection PyUnusedLocal
    def get_active_window(self):
        """ From: https://stackoverflow.com/a/41046548/6929343 """
        import gi
        gi.require_version('Wnck', '3.0')
        from gi.repository import Wnck
        screen = Wnck.Screen.get_default()
        screen.force_update()  # recommended per Wnck documentation

        # loop all windows
        geom = None
        window_name = None
        x_id = None
        for window in screen.get_windows():
            if window.is_active() is True:
                geom = window.get_geometry()  # Includes decorations
                if geom is None:
                    print("monitor.py - get_active_window(): 'geom' is 'NoneType'.")
                    continue  # 2024-12-18 Added today when geom is None
                window_name = window.get_name()
                x_id = window.get_xid()
                # A lot more attributes are available see:
                # https://lazka.github.io/pgi-docs/Wnck-3.0/classes/Window.html#Wnck.Window.get_screen
                break
                
        # clean up Wnck (saves resources, see the documentation)
        window = None  # Although pycharm flags as error,
        screen = None  # these are important else crash!!
        Wnck.shutdown()
        Window = namedtuple('Window', 'number, name, x, y, width, height')
        # noinspection PyArgumentList
        self.found_window = Window(x_id, window_name, geom.xp, geom.yp,
                                   geom.widthp, geom.heightp)
        return self.found_window

    # noinspection PyUnusedLocal
    def get_all_windows(self):
        """ Jun. 14, 2023 - Build list of all windows in self.windows_list[].
            Initially designed to find windows off-monitors
            View results with mserve.py - Dropdown Menu - Tools, Debug information
        """
        import gi
        gi.require_version('Wnck', '3.0')
        from gi.repository import Wnck
        screen = Wnck.Screen.get_default()
        # Different than __init__():
        #       DISPLAY = Gdk.Display.get_default()
        #       SCREEN = DISPLAY.get_default_screen()
        screen.force_update()  # recommended per Wnck documentation
        self.windows_list = []  # empty existing list
        # loop all windows
        for window in screen.get_windows():
            geom = window.get_geometry()  # Includes decorations
            window_name = window.get_name()
            x_id = window.get_xid()  # Long integer. E.G. 111149063L
            Window = namedtuple('Window', 'number, name, x, y, width, height')
            # noinspection PyArgumentList
            self.found_window = Window(x_id, window_name, geom.xp, geom.yp,
                                       geom.widthp, geom.heightp)
            self.windows_list.append(self.found_window)
            # A lot more attributes are available see:
            # https://lazka.github.io/pgi-docs/Wnck-3.0/classes/Window.html#Wnck.Window.get_screen


        # clean up Wnck (saves resources, see the documentation)
        window = None  # Although pycharm flags as error,
        screen = None  # these are important else crash!!
        Wnck.shutdown()
        return self.windows_list
    
    def get_active_monitor(self):
        """ First find the active window. Then find what monitor it is on and
            then return that monitor. """

        win = self.get_active_window()      # Results in self.found_window too

        x, y, w, h = win.x, win.y, win.width, win.height
        #print("win.name:", win.name, "win.x:", win.x, "win.y:", win.y, 
        #      "win.width:", win.width, "win.height:", win.height)

        x_center = win.x + win.width // 2
        y_center = win.y + win.height // 2
        #print("x_center:", x_center, "y_center:", y_center)

        if x < 0 or x > self.screen_width:  # same as self.desk_width
            x = 0  # Window top left may be off screen!
            #print('ERROR monitor.py: Window:,', win.number,
            #      'x-offset:', win.x, 'was off screen.\n', win.name)
        if y < 0 or y > self.screen_height:  # same as self.desk_height
            y = 0
            #print('ERROR monitor.py: Window:,', win.number,
            #      'y-offset:', win.y, 'was off screen.\n', win.name)

        primary_monitor = None

        for mon in self.monitors_list:
            #print("mon.name:", mon.name, "mon.x:", mon.x, "mon.y:", mon.y,
            #      "mon.width:", mon.width, "mon.height:", mon.height)
            # Save primary monitor if needed later
            if mon.primary is True:
                primary_monitor = mon

            ''' July 29, 2023 - Test window center inside monitor bbox '''
            if mon.x <= x_center <= (mon.x + mon.width):
                if mon.y <= y_center <= (mon.y + mon.height):
                    #print("FOUND:", mon.name)
                    return mon

            # Most of window must be on monitor to qualify
            if x < mon.x:
                # A) This is flawed test.
                # win.x could be 10 pixels before mon.x but
                # win.width could be 1000 and most of window
                # does sit inside mon
                #print("x < mon.x:", x, mon.x)
                continue
            if x >= mon.x + mon.width // 2:
                # B) This is flawed test.
                # win.x could be 10 pixels past mon.x middle
                # win.width might only be 400 pixels and all of window
                # sits inside mon
                #print("x >= mon.x + mon.width // 2:", x, mon.x, mon.width // 2)
                continue
            if y > mon.y:
                # C) This is flawed test similar to A).
                # July 29, 2023 used to be "y < mon.y"
                #print("y > mon.y:", y, mon.y)
                continue
            if y >= mon.y + mon.height // 2:
                # D) This is flawed test similar to B).
                #print("y >= mon.y + mon.height // 2:", y, mon.y, mon.height // 2)
                continue

            # Window is mostly on this monitor.
            return mon

        # If window off of screen use first monitor
        return primary_monitor

    def get_mouse_monitor(self):
        """ First find the mouse position. Then find what monitor it is on and
            then return that monitor. """

        x, y = get_mouse_location()  # Uses xdotool
        x = int(x)
        y = int(y)
        x_center = x + 1  # Width of mouse pointer is insignificant
        y_center = y + 1  # Height of mouse pointer is insignificant
        # print("x_center:", x_center, "y_center:", y_center)

        if x < 0 or x > self.screen_width:  # same as self.desk_width
            x = 0  # Mouse top left was off screen!
        if y < 0 or y > self.screen_height:  # same as self.desk_height
            y = 0

        primary_monitor = None

        for mon in self.monitors_list:
            # print("mon.name:", mon.name, "mon.x:", mon.x, "mon.y:", mon.y,
            #      "mon.width:", mon.width, "mon.height:", mon.height)
            # Save primary monitor if needed later
            if mon.primary is True:
                primary_monitor = mon

            ''' Test mouse center inside monitor bbox '''
            if mon.x <= x_center <= (mon.x + mon.width):
                if mon.y <= y_center <= (mon.y + mon.height):
                    return mon

            # Most of mouse must be on monitor to qualify
            if x < mon.x:
                continue
            if x >= mon.x + mon.width // 2:
                continue
            if y > mon.y:
                continue
            if y >= mon.y + mon.height // 2:
                continue

            # Mouse is mostly on this monitor.
            return mon

        # If mouse off of screen use first monitor
        return primary_monitor

    def get_mouse_pointer(self):
        """ Uses Gdk to get mouse location using old gnome 3.18 standards.
            Similar to get_mouse_location() which uses xdotool
            Returns (x, y). If x is None, y contains error message
        """
        _who = self.who + "get_mouse_pointer():"
        import gi
        gi.require_version('Gdk', '3.0')
        from gi.repository import Gdk

        _screen = _x = _y = None

        display = Gdk.Display.get_default()
        if display:
            device_manager = display.get_device_manager()
            if device_manager:
                device = device_manager.get_client_pointer()
                if device:
                    # Get the position relative to the root window
                    _screen, _x, _y = device.get_position()
                    #print(_who, "Device position (x, y): ({}, {}) on screen: {}"
                    #      .format(x, y, screen))
                else:
                    _y = "Could not get client pointer device."
            else:
                _y = "Could not get device manager."
        else:
            _y = "Could not get default display."

        if _x is None:
            print(_who, _y)
        return _x, _y  # If _x is None, _y contains error message

    def get_colors_at_geom(self, geom):
        """ Screenshot using old gnome 3.18 standards
            Based on toolkit.py -> gnome_screenshot()
            geom = namedtuple('Geom', ['x', 'y', 'w', 'h'])
        """
        _who = self.who + "get_color_at_mouse():"
        import gi
        # When replacing 3.0 with 4.0 below
        gi.require_version('Gdk', '3.0')  # Namespace Gdk is already loaded with version 3.0
        gi.require_version('Gtk', '3.0')  # Namespace Gtk not available for version 4.0
        gi.require_version('Wnck', '3.0')  # Namespace Wnck not available for version 4.0
        # gi.require_versions({"Gtk": "3.0", "Gdk": "3.0", "Wnck": "3.0"})  # Python 3

        from gi.repository import Gdk, GdkPixbuf, Gtk, Wnck

        # gi.require_version('GObject', '4.0')  # Namespace GObject is already loaded with version 2.0
        # from gi.repository import Gdk, Gdk Pix buf, Gtk, Wnck, GObject
        # 2024-03-19 add GObject to imports because Gdk.threads_init() is deprecated
        # (https://gnome.pages.gitlab.gnome.org/pygobject/guide/threading.html)
        # When above Gobject is imported:
        # toolkit.py/motion() self.canvas_original_x is none
        # Exception in Tkinter callback
        # Traceback (most recent call last):
        #   File "/usr/lib/python2.7/lib-tk/Tkinter.py", line 1540, in __call__
        #     return self.func(*args)
        #   File "/home/rick/python/toolkit.py", line 1806, in motion
        #     new_x = int(self.canvas_original_x + change)  # Sometimes we get float?
        # TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'

        Gdk.threads_init()  # From: https://stackoverflow.com/questions/15728170/
        while Gtk.events_pending():
            Gtk.main_iteration()

        screen = Wnck.Screen.get_default()
        screen.force_update()
        window = Gdk.get_default_root_window()
        pb = Gdk.pixbuf_get_from_window(window, *geom)
        desk_pixels = pb.read_pixel_bytes().get_data()
        _row_stride = pb.get_rowstride()
        # https://docs.gtk.org/gdk-pixbuf/method.Pixbuf.get_rowstride.html
        #raw_img = Image.from bytes('RGB', (geom.w, geom.h), desk_pixels,
        #                          'raw', 'RGB', _row_stride, 1)
        return desk_pixels, _row_stride

    def tk_center(self, window):
        """
        Based on .center() which was deprecated 2025-06-08

        From: https://stackoverflow.com/a/10018670/6929343
        centers a tkinter window on monitor in multi-monitor setup
        :param window: the main window or Toplevel window to center
        """

        window.update_idletasks()           # Refresh window's current position
        mon = self.get_active_monitor()

        if mon is None:
            # logging.error("No monitors found!")
            print("No monitors found!")
            return None

        # Calculate X, Y of window to center within monitors X, Y, width and height
        x = mon.width // 2 - window.winfo_width() // 2 + mon.x
        y = mon.height // 2 - window.winfo_height() // 2 + mon.y
        if x < 0:
            x = 30  # Window top left may be off screen!
        if y < 0:
            y = 30

        window.geometry('+{}+{}'.format(x, y))
        #print("mon:", mon)
        # Monitor(number=1, name='DP-1-1', x=1920, y=0, width=3840, height=2160, primary=False)
        #print("x, y:", x, y)
        # x, y: 3740 980
        
        return mon  # Should win namedtuple be returned instead?

    def get_home_monitor(self, window, force_visible=False):
        """ Return the monitor passed window is mostly on, or closest to.
            window = namedtuple('Window', 'number, name, x, y, width, height')
            screen = all monitors' width & height combined together
            monitor = namedtuple('Monitor', mon.keys())(*mon.values())
            monitor = (mon.name, mon.x, mon.y, mon.width, mon.height)

            2024-05-12 Use xdotool to move window into dead-zone for testing:
                str_win = str(window.number)  # should remove L in python 2.7.5+
                int_win = int(str_win)  # https://stackoverflow.com/questions
                hex_win = hex(int_win)  # /5917203/python-trailing-l-problem
                # Move window into closest monitor viewable area
                if ext.check_command('xdotool'):
                    os.popen('xdotool windowmove ' + hex_win + ' ' +
                             str(new_x) + ' ' + str(new_y))

            command line:

                xdotool windowmove 0x580000a 2261 2740

        """
        _who = self.who + "get_home_monitor():"

        x = window.x  # All GUI windows geometry - not just tkinter windows
        y = window.y  # x = horizontal / x-offset - y = vertical / y-offset
        w = window.width
        h = window.height

        # If window offset(s) negative force to +100
        x = 100 if x < 0 else x  # Override corrupt horizontal / x-offset
        y = 100 if y < 0 else y  # Override corrupt vertical / y-offset

        first_monitor = last_x = last_y = None  # local vars

        # easy-peasy test first. Window is mostly on a known monitor
        for index in range(self.monitor_count):
            # Get monitor dictionary from monitors list
            monitor = self.monitors_list[index]
            if first_monitor is None:
                first_monitor = monitor  # Save first monitor if needed later
                last_x = monitor
                last_y = monitor

            # find the right most and bottom most monitor
            last_x = monitor if monitor.x > last_x.x else last_x
            last_y = monitor if monitor.y > last_y.y else last_y

            # Most of window must be on monitor to qualify
            if x < monitor.x:
                continue
            if x >= monitor.x + monitor.width // 2 and \
                    x + w > monitor.x + monitor.width:
                continue  # window 50% into monitor x and window end past monitor end
            if y < monitor.y:
                continue
            if y >= monitor.y + monitor.height // 2 and \
                    y + h > monitor.y + monitor.height:
                continue  # window 50% into monitor y and window end past monitor end

            # Window is mostly on this monitor.
            return monitor

        # Window top left or bottom right may be off screen
        bad_x = True if x > self.screen_width else False
        bad_y = True if y > self.screen_height else False

        # Window outside of screen region? - return last_y first and last_x second
        if bad_y:
            return last_y
        elif bad_x:
            return last_x

        print("\n" + _who, "x:", x, "y:", y, "w:", w, "h:", h,
              "x2:", x + w, "y2:", y + h, "\n\tname:", window.name)

        # Window is inside screen region "dead-zone". Return closest monitor.
        closest_x = closest_y = None  # local vars
        for index in range(self.monitor_count):
            # Get monitor dictionary from monitors list
            monitor = self.monitors_list[index]
            print("monitor.name:", monitor.name, "monitor.x:", monitor.x,
                  "+y:", monitor.y, " height:", monitor.height, " width:",
                  monitor.width, "x2:", monitor.x + monitor.width,
                  "y2:", monitor.y + monitor.height)
            if closest_x is None:
                closest_x = monitor
                closest_y = monitor

            # find the closest horizontal and vertical monitors
            closest_x2 = closest_x.x + closest_x.width
            closest_y2 = closest_y.y + closest_y.height
            closest_x = monitor if closest_x.x < x < closest_x2 else closest_x
            closest_y = monitor if closest_y.y < y < closest_y2 else closest_y

        if force_visible:
            # 2024-05-11 TODO port code from mserve.py lines 5000-5030
            print("Code not completed. Port code from mserve.py lines 5000-5030:")
            print("home_mon = mon.get_home_monitor(window, force_visible=True)")

        print("closest_x:", closest_x.name, "closest_y:", closest_y.name)
        if closest_x == closest_y:
            return closest_x  # closest x & y same monitor

        # Which is better match the closest x or the closest y?
        dist_x = x - closest_x.x
        dist_y = y - closest_y.y
        if dist_x < dist_y:
            return closest_x
        else:
            return closest_y

    # noinspection PyUnusedLocal
    def make_wn_list(self):
        """ Use Wnck to read all windows and build self.wn_list comprised of
            self.wn_dict dictionaries.

            Created 2025-06-12 based on self.get_all_windows()

https://stackoverflow.com/questions/63660821/detect-when-a-window-opens-in-wnck-python

import gi

gi.require_version('Wnck', '3.0')
gi.require_version('Gtk', '3.0')

from gi.repository import Wnck
from gi.repository import Gtk


def test_do_when_window_opened_simple():
    Gtk.init([])
    screen: Wnck.Screen = Wnck.Screen.get_default()
    screen.force_update()

    def do_window_opened(this_screen: Wnck.Screen, opened_window: Wnck.Window):
        print('hello')
        app: Wnck.Application = opened_window.get_application()
        app_name = app.get_name()
        print('app name -> ' + app_name)
        print('window name -> ' + opened_window.get_name())

    screen.connect('window-opened', do_window_opened)

    Gtk.main()


if __name__ == '__main__':
    test_do_when_window_opened_simple()
        """
        _who = self.who + "make_wn_list():"
        ext.t_init(_who)
        import gi
        gi.require_version('Wnck', '3.0')
        from gi.repository import Wnck
        screen = Wnck.Screen.get_default()
        # Different than __init__():
        #       DISPLAY = Gdk.Display.get_default()
        #       SCREEN = DISPLAY.get_default_screen()
        ext.t_init(_who + "W/O import")
        screen.force_update()  # recommended per Wnck documentation

        self.wn_list = []  # empty existing list
        # loop all windows
        for window in screen.get_windows():
            """ Duplicate get_window() """
            CommonWindow.__init__(self)  # Set wn_dict = {} and vars to None

            self.wn_xid_long = window.get_xid()  # Long integer. E.G. 111149063L
            self.wn_xid_str = str(self.wn_xid_long)
            self.wn_xid_int = int(self.wn_xid_str)
            self.wn_xid_hex = hex(self.wn_xid_int)

            self.wn_pid = window.get_pid()  # Process ID or 0 if none
            self.wn_name = window.get_name()  # Full window name from title bar
            if " - YouTube" in self.wn_name:
                # Granular matching of " - YouTube \xe2\x80\x94 Mozilla Firefox"
                self.wn_app = self.wn_name.split()[-1]  # 'Firefox'
                self.wn_video = self.wn_name.split(" - YouTube")[0]  # Video name
            self.wn_geom = window.get_geometry()  # Includes decorations
            self.wn_x = self.wn_geom.xp
            self.wn_y = self.wn_geom.yp
            self.wn_width = self.wn_geom.widthp
            self.wn_height = self.wn_geom.heightp
            self.wn_is_active = window.is_active()
            self.wn_is_maximized = window.is_maximized()
            self.wn_is_fullscreen = window.is_fullscreen()

            self.make_wn_dict()  # Builds wn_xid_str, _int and _hex
            self.wn_list.append(self.wn_dict)

        ext.t_end('no_print')  # Time for 24 windows: 0.03 to 0.06

        # clean up Wnck (saves resources, see the documentation)
        window = None  # Although pycharm flags as error,
        screen = None  # these are important else crash!!
        Wnck.shutdown()
        #print("len(self.wn_list):", len(self.wn_list))
        ext.t_end('no_print')  # Time for 24 windows: 0.03 to 0.06
        # For comparison, `wmctrl -lG` takes 0.132s

    def get_wn_by_name(self, wn_name, pid=None):
        """ Search window list for matching name.
            Destroys current self.wn_dict contents !
            Parent must call self.make_wn_list() first !
        """
        _who = self.who + "get_wn_by_name():"

        # loop all windows
        #print(self.wn_list)
        for self.wn_dict in self.wn_list:
            if pid and pid != self.wn_dict['pid']:
                continue
            #print(self.wn_dict)
            self.unmake_wn_dict()
            if self.wn_name.startswith(wn_name):
                return True

        """ Duplicate get_window() """
        CommonWindow.__init__(self)  # Set wn_dict = {} and vars to None
        return False

    def set_fullscreen(self, xid_long):
        """ Search wnck.screen.list for matching windows xid long.
            Preserves self.wn_list and self.wn_dict contents.
            DOES NOT WORK IN GNOME 3.18 test in 3.22
        """
        _who = self.who + "set_fullscreen():"
        import gi
        gi.require_version('Wnck', '3.0')
        from gi.repository import Wnck
        _screen = Wnck.Screen.get_default()
        # Different than __init__():
        #       DISPLAY = Gdk.Display.get_default()
        #       SCREEN = DISPLAY.get_default_screen()
        _screen.force_update()  # recommended per Wnck documentation

        window_found = False
        forced_fullscreen = False
        for _window in _screen.get_windows():
            if not xid_long == _window.get_xid():  # Long integer. E.G. 111149063L
                continue  # Not our window

            window_found = True
            if _window.is_fullscreen():
                break  # Already fullscreen

            _window.fullscreen()  # force fullscreen
            forced_fullscreen = True
            break

        ext.t_end('no_print')  # Time for 24 windows: 0.03 to 0.06

        # clean up Wnck (saves resources, see the documentation)
        _window = None  # Although pycharm flags as error,
        _screen = None  # these are important else crash!!
        Wnck.shutdown()
        return window_found and forced_fullscreen

    def make_wn_dict(self):
        """ Build self.wn_dict using self.variable names """

        _who = self.who + "make_wn_dict():"
        if self.wn_xid_long is None:
            print(_who, "self.wn_xid_long is None")
            self.wn_dict = {}
            return

        self.wn_xid_str = str(self.wn_xid_long)
        self.wn_xid_int = int(self.wn_xid_str)
        self.wn_xid_hex = hex(self.wn_xid_int)

        self.wn_dict = {
            "xid_long": self.wn_xid_long,
            "xid_hex": self.wn_xid_hex,
            "xid_int": self.wn_xid_int,
            "xid_str": self.wn_xid_str,
            "pid": self.wn_pid,
            "name": self.wn_name,
            "app": self.wn_app,
            "video": self.wn_video,
            "geom": self.wn_geom,
            "x": self.wn_x,
            "y": self.wn_y,
            "width": self.wn_width,
            "height": self.wn_height,
            "is_active": self.wn_is_active,
            "is_maximized": self.wn_is_maximized,
            "is_fullscreen": self.wn_is_fullscreen
        }

    def unmake_wn_dict(self, wn_dict=None):
        """ Deconstruct self.wn_dict into self.variable names.
            If wn_dict isn't passed, use self.wn_dict. When passed it is a working
            dictionary named old_dict, hold_dict, new_dict, etc.
        """

        _who = self.who + "unmake_wn_dict():"
        wn_dict = self.wn_dict if wn_dict is None else wn_dict  # old_, hold_, new_dict, etc.

        try:
            self.wn_xid_long = wn_dict["xid_long"]  # X11 window ID with L integer type
        except TypeError:
            print(_who, 'ERROR: self.wn_xid_long = wn_dict["xid_long"]')
            print(wn_dict)
            return

        self.wn_xid_str = wn_dict["xid_str"]
        self.wn_xid_int = wn_dict["xid_int"]
        self.wn_xid_hex = wn_dict["xid_hex"]
        self.wn_pid = wn_dict["pid"]
        self.wn_name = wn_dict["name"] 
        self.wn_app = wn_dict["app"] 
        self.wn_video = wn_dict["video"]
        self.wn_geom = wn_dict["geom"] 
        self.wn_x = wn_dict["x"] 
        self.wn_y = wn_dict["y"] 
        self.wn_width = wn_dict["width"] 
        self.wn_height = wn_dict["height"] 
        self.wn_is_active = wn_dict["is_active"] 
        self.wn_is_maximized = wn_dict["is_maximized"] 
        self.wn_is_fullscreen = wn_dict["is_fullscreen"] 

        """

====================================================================================
https://lazka.github.io/pgi-docs/Wnck-3.0/classes/Window.html#Wnck.Window.get_screen
====================================================================================

get_geometry()¶
get_window_type()¶
is_above()¶
is_below()¶
is_fullscreen()¶
is_maximized()¶
is_maximized_horizontally()¶
is_maximized_vertically()¶
is_minimized()¶
make_above()¶
make_below()¶
maximize()¶
maximize_horizontally()¶
maximize_vertically()¶
minimize()¶
set_fullscreen(fullscreen)¶
set_geometry(gravity, geometry_mask, x, y, width, height)¶
set_icon_geometry(x, y, width, height)¶

get_geometry()¶

    Returns:

        xp:

            return location for X coordinate in pixels of self.
        yp:

            return location for Y coordinate in pixels of self.
        widthp:

            return location for width in pixels of self.
        heightp:

            return location for height in pixels of self.

    Return type:

        (xp: int, yp: int, widthp: int, heightp: int)

    Gets the size and position of self, including decorations. This function 
    uses the information last received in a ConfigureNotify event and adjusts 
    it according to the size of the frame that is added by the window manager 
    (this call does not round-trip to the server, it just gets the last sizes 
    that were notified). The X and Y coordinates are relative to the root 
    window.

    If you need to know the actual size of self ignoring the frame added by 
    the window manager, use Wnck.Window.get_client_window_geometry().


get_window_type()¶

    Returns:

        the semantic type of self.
    Return type:

        Wnck.WindowType

    Gets the semantic type of self.


is_above()¶

    Returns:

        True if self is above other windows, False otherwise.
    Return type:

        bool

    Gets whether self is above other windows. This state may change anytime a 
    Wnck.Window ::state-changed signal gets emitted.

    See Wnck.Window.make_above() for more details on this state.

    New in version 2.14.


is_below()¶

    Returns:

        True if self is below other windows, False otherwise.
    Return type:

        bool

    Gets whether self is below other windows. This state may change anytime a 
    Wnck.Window ::state-changed signal gets emitted.

    See Wnck.Window.make_below() for more details on this state.

    New in version 2.20.

is_fullscreen()¶

    Returns:

        True if self is fullscreen, False otherwise.
    Return type:

        bool

    Gets whether self is fullscreen. Fullscreen state may change anytime a 
    Wnck.Window ::state-changed signal gets emitted.

    New in version 2.8.


is_maximized()¶

    Returns:

        True if self is maximized in both directions, False otherwise.
    Return type:

        bool

    Gets whether self is maximized. Maximization state may change anytime a 
    Wnck.Window ::state-changed signal gets emitted.

    As for GDK, “maximized” means both vertically and horizontally. If self 
    is maximized in only one direction, then self is not considered maximized.

is_maximized_horizontally()¶

    Returns:

        True if self is maximized horizontally, False otherwise.
    Return type:

        bool

    Gets whether self is maximized horizontally. Horizontal maximization state 
    may change anytime a Wnck.Window ::state-changed signal gets emitted.

is_maximized_vertically()¶

    Returns:

        True if self is maximized vertically, False otherwise.
    Return type:

        bool

    Gets whether self is maximized vertically. vertical maximization state 
    may change anytime a Wnck.Window ::state-changed signal gets emitted.

is_minimized()¶

    Returns:

        True if self is minimized, False otherwise.
    Return type:

        bool

    Gets whether self is minimized. Minimization state may change anytime a 
    Wnck.Window ::state-changed signal gets emitted.


make_above()¶

    Asks the window manager to put self on top of most windows (self will not 
    be on top of focused fullscreen windows, of other windows with this setting
    and of dock windows).

    New in version 2.14.

make_below()¶

    Asks the window manager to put self below most windows.

    New in version 2.20.

maximize()¶

    Asks the window manager to maximize self.

maximize_horizontally()¶

    Asks the window manager to maximize horizontally self.

maximize_vertically()¶

    Asks the window manager to maximize vertically self.

minimize()¶

    Minimizes self.


set_fullscreen(fullscreen)¶

    Parameters:

        fullscreen (bool) – whether to make self fullscreen.

    Asks the window manager to set the fullscreen state of self according 
    to fullscreen.

    New in version 2.8.

set_geometry(gravity, geometry_mask, x, y, width, height)¶

    Parameters:

            gravity (Wnck.WindowGravity) – the gravity point to use as a 
            reference for the new position.

            geometry_mask (Wnck.WindowMoveResizeMask) – a bitmask containing 
            flags for what should be set.

            x (int) – new X coordinate in pixels of self.

            y (int) – new Y coordinate in pixels of self.

            width (int) – new width in pixels of self.

            height (int) – new height in pixels of self.

    Sets the size and position of self. The X and Y coordinates should be 
    relative to the root window.

    Note that the new size and position apply to self with its frame added by 
    the window manager. Therefore, using Wnck.Window.set_geometry() with the 
    values returned by Wnck.Window.get_geometry() should be a no-op, while 
    using Wnck.Window.set_geometry() with the values returned by 
    Wnck.Window.get_client_window_geometry() should reduce the size of self 
    and move it.

    New in version 2.16.

set_icon_geometry(x, y, width, height)¶

    Parameters:

            x (int) – X coordinate in pixels.

            y (int) – Y coordinate in pixels.

            width (int) – width in pixels.

            height (int) – height in pixels.

    Sets the icon geometry for self. A typical use case for this is the 
    destination of the minimization animation of self.


        """


def get_window_geom_raw(window, leave_visible=True):
    """
    Get Tkinter window's geometry tuple: x-offset, y-offset, width, height
    Fix: https://stackoverflow.com/a/10018670/6929343
    Above fix doesn't work.
    TODO: get geometry, turn off alpha,
          move to geometry, get geometry second time
          adjusted = second time - first get
          real = first get - adjusted
          move to real, get geometry a third time
          now third time = second time
    """
    try:
        window.attributes('-alpha', 0.0)  # Make window invisible
    except AttributeError:
        return  # 2024-12-07 Window no longer exists, destroyed by Ubuntu Dock.
    window.update_idletasks()
    x = window.winfo_x()                # Tkinter Window's left coordinate
    y = window.winfo_y()                # Tkinter Window's top coordinate
    # Move window to the reported fake geometry
    window.geometry('+{}+{}'.format(x, y))
    window.update_idletasks()
    x2 = window.winfo_x()               # Get the x coordinate again
    y2 = window.winfo_y()               # Get the y coordinate again
    x_diff = x2 - x                     # X difference between get and fake
    y_diff = y2 - y                     # y difference between get and fake
    x = x - x_diff                      # Calculate real x
    y = y - y_diff                      # Calculate real y
    w = window.winfo_width()            # Tkinter Window's width
    h = window.winfo_height()           # Tkinter Window's height
    # Moving window to fake geometry adjusts position to real position
    # Pass 'leave-visible=False' to prevent "blink" if closing program
    if leave_visible:
        window.geometry('+{}+{}'.format(x, y))
        window.attributes('-alpha', 1.0)    # Make window visible again
        window.update_idletasks()

    return x, y, w, h


def get_window_bbox(window, leave_visible=True):
    """ NOT USED.
     Get Tkinter window's x0, y0, x1, y1 tuple """
    x, y, w, h = get_window_geom_raw(window, leave_visible)
    return x, y, (x + w), (y + h)


def get_window_geom_string(window, leave_visible=True):
    """ Get Tkinter window's: Width x Height + X-offset + Y-offset
    Primarily used to for writing window geometry to disk for next restart.
    Used in encoding.py(1), location.py(1), mserve.py(6) and webscrape.py(1)
    :returns "WxH+X+Y" string.
    """
    try:
        x, y, w, h = get_window_geom_raw(window, leave_visible)
        return str(w) + 'x' + str(h) + '+' + str(x) + '+' + str(y)
    except TypeError:
        return None  # Window has disappeared


def get_xrandr_monitors():
    """ NOT USED. 
    Return list of monitors by parsing output from:

        $ xrandr --list monitors

             Monitors: 3
             0: +*eDP-1-1 1920/382x1080/215+3840+2160  eDP-1-1
             1: +HDMI-0 1920/1107x1080/623+0+0  HDMI-0
             2: +DP-1-1 3840/1600x2160/900+1920+0  DP-1-1

    """
    # noinspection SpellCheckingInspection
    result = os.popen('xrandr --listmonitors').read().splitlines()
    # inspection SpellCheckingInspection

    #print('get_xrandr_monitors() result:')
    #print(result)

    monitors = []
    for line in result:
        # Compress multiple whitespace into single space
        line = ' '.join(line.split())

        if "Monitors" in line:
            continue              # First line needs to be skipped

        monitor = {'number': int(line.split(':')[0])}
        #print('line:', line)
        #print('field 0:', line.split(':')[0])
        if "*" in line:
            monitor['primary'] = True
        else:
            monitor['primary'] = False
        full_geom_list = line.split()[2:3]
        full_geom = full_geom_list[0]
        #print('full_geom:', full_geom)
        monitor['x'] = int(full_geom.split('+')[1:2][0])
        monitor['y'] = int(full_geom.split('+')[2:][0])
        width_height = full_geom.split('+')[0]
        width = width_height.split('x')[0]
        height = width_height.split('x')[1]
        monitor['width'] = int(width.split('/')[0])
        monitor['height'] = int(height.split('/')[0])
        monitor['name'] = line.split()[-1]
        monitors.append(monitor)

    #print('get_xrandr_monitors() monitors:')
    #print(monitors)

    return monitors     # List of mon_dict


def get_window_geom(name):
    """
    Every time you get the window geometry it is panel height lower than it
    really is. Subsequently when painting it it is lower. Subtract PANEL_HGT
    from the values.

    CURRENT:
        Get geometry for window which was saved on last exit. If no record
        use 130,130 and predefined default width & height. Returns string
        of "width x height + x + y" with no spaces in between variables.

    FUTURE:
    From SQL history we get 1 screen, multiple monitors per screen,
    library window, playlist window, etc. positioned on a monitor.

    Watch for black holes that can appear if screen configuration
    changes.

    Only saved when different than last time

    SQL ROWS and COLUMNS in TABLE HISTORY
    =====================================
    Type:           'screen'
    Action:         '(monitor plug names)'          # xrandr | grep " connected" # split()[0]
    SourceMaster:   'width x height'                # xrandr | grep "Screen " # split(',')[1]
    SourceDetail:   'xrandr text: left-of, right-of, etc.'
    Comments:       'Active (or Last Active on: yyyy-mm-dd hh:mm:ss)'

    Type:           'monitor'
    Action:         'monitor plug name'
    SourceMaster:   'width x height + x_offset + y_offset'  # xrandr | grep PLG_NAME # split('x')[3]
    SourceDetail:   'xrandr text: left-of, right-of, etc.'  # xrandr how???
    Comments:       "Used in conjunction with 'screen' History Record Id #"

    Type:           'window'
    Action:         'library' / 'playlist' / 'music_sql' / 'hist_sql', etc.
    SourceMaster:   'width x height + x_offset + y_offset'  # Only saved when different than last time
    SourceDetail:   'saved on exit, loaded on starting
    Comments:       "Used in conjunction with 'screen' History Record Id #"


    """

    xy = (130, 130)  # Default coordinates for first encounter windows.
    # When changing (130, 130), revise location.py Locations.display_test_window()
    # Could also use active monitor but that requires compiz?
    # Alternatively could use mouse location?

    if name == 'library':  # mserve.py & bserve.py
        _w = int(1920 * .75)
        _h = int(1080 * .75)
        _root_xy = (100, 100)  # Temporary hard-coded coordinates
        default_geom = '%dx%d+%d+%d' % (_w, _h, _root_xy[0], _root_xy[1])
    elif name == 'playlist':  # mserve.py - Playing selected songs
        default_geom = '+%d+%d' % (xy[0], xy[1])
    elif name == 'backups':  # bserve.py
        default_geom = '+%d+%d' % (xy[0], xy[1])
    elif name == 'history':  # scrape.py (OBSOLETE) & webscrape.py
        default_geom = '+%d+%d' % (xy[0], xy[1])
    elif name == 'encoding':  # encoding.py
        default_geom = '+%d+%d' % (xy[0], xy[1])
    elif name == 'results':  # scrape.py (OBSOLETE) - s/b deleted in SQL history
        default_geom = '+%d+%d' % (xy[0], xy[1])
    elif name == 'sql_music':  # mserve.py
        default_geom = '+%d+%d' % (xy[0], xy[1])
        # 2024-03-10 Use Library +30 +30
    elif name == 'sql_history':  # mserve.py
        default_geom = '+%d+%d' % (xy[0], xy[1])
        # 2024-03-10 Use Library +60 +60
    elif name == 'sql_location':  # mserve.py
        default_geom = '+%d+%d' % (xy[0], xy[1])
        # 2024-03-10 Use Library +90 +90
    elif name == 'playlists':  # mserve.py - Playlists maintenance toplevel window
        default_geom = '+%d+%d' % (xy[0], xy[1])
    elif name == 'lcs_top':  # location.py - Locations - SQL deleted with pls_top
        default_geom = '+%d+%d' % (xy[0], xy[1])
    elif name == 'locations':  # location.py - Locations
        default_geom = '+%d+%d' % (xy[0], xy[1])
    elif name == 'calculator':  # calc.py - Calculator() class
        default_geom = '+%d+%d' % (xy[0], xy[1])
    else:
        print('monitor.get_window_geom(): Bad window name:', name)
        xy = (130, 130)
        default_geom = '+%d+%d' % (xy[0], xy[1])

    ''' Override defaults when window was previously saved. '''
    if sql.hist_check(0, 'window', name):
        sql.hist_cursor.execute("SELECT * FROM History WHERE Id = ?",
                                [sql.HISTORY_ID])
        d = dict(sql.hist_cursor.fetchone())
        if d is None:
            # If we get here there is programmer error
            print('monitor.get_window_geom(): No History ID:', sql.HISTORY_ID)
            return default_geom
        else:
            # new_geom intention for windows off desktop but gnome seems to fix?
            #new_geom = check_window_geom(d['SourceMaster'])
            return d['SourceMaster']  # Geometry (Coordinates, width & height)
    else:
        # First time.
        return default_geom


def check_window_geom(window, mon=None, print_panel_error=True):
    """ When switching from multi-head system to laptop ony windows may be
        off visible desktop. Also if xrandr resets same problem.

        Get real estate of all monitors and when window isn't 50% inside a
        monitor, force it inside

        2024-10-09 - Code taken from mserve.py in self.debug() line 6025.

    :param window: namedtuple('Window', 'number, name, x, y, width, height').
    :param mon: Monitors class instance. If not passed new instance generated.
    :param print_panel_error: Print error message if system or panel window.
    :return: True geometry valid. False geometry invalid and window moved.
    """

    x = window.x
    y = window.y
    if mon is None:
        mon = Monitors()

    # The monitor the window is mostly on or closest too
    home_mon = mon.get_home_monitor(window, force_visible=False)

    # At least 50 pixels should be visible else nothing for mouse grab
    x_cutoff = home_mon.x + home_mon.width - 50
    y_cutoff = home_mon.y + home_mon.height - 50
    if x < 0 or y < 0:
        # system windows / panels are hidden with negative x and y:
        if print_panel_error:
            print("System window / panel passed. Ignoring:", window.name,
                  "at x:", x, "y:", y)
        return True  # Never move system or panel window
    elif x < home_mon.x or y < home_mon.y or x > x_cutoff or y > y_cutoff:
        ''' When monitor loses power, windows can move off screen '''
        print("\nhome_mon:", home_mon, "\nwindow:", window)
        print("ERROR: Window is off screen at x + y:", x, "+",
              y, "x_cutoff:", x_cutoff, "y_cutoff:", y_cutoff)
        print("  ", window)

        new_x = x_cutoff - 500 if x > x_cutoff else x
        new_y = y_cutoff - 500 if y > y_cutoff else y
        new_x = home_mon.x + 50 if x < home_mon.x else new_x
        new_y = home_mon.y + 50 if y < home_mon.y else new_y

        print("     Adjust to coordinates:", new_x, "+", new_y, "\n")
        str_win = str(window.number)  # should remove L in python 2.7.5+
        int_win = int(str_win)  # https://stackoverflow.com/questions
        hex_win = hex(int_win)  # /5917203/python-trailing-l-problem
        # Move window into closest monitor viewable area
        if ext.check_command('xdotool'):
            os.popen('xdotool windowmove ' + hex_win + ' ' +
                     str(new_x) + ' ' + str(new_y))
        else:
            print("ext.check_command('xdotool') is not installed!")
            print("Above window must be moved with another method.")
        return False
    else:
        return True


def save_window_geom(name, geom):
    """
    CURRENT:
        Get geometry for window which was saved on last exit. If no record
        use 100,100 and predefined default width & height. Returns string
        of "width x height + x + y" with no spaces in between variables.
    """

    if sql.hist_check(0, 'window', name):
        sql.hist_cursor.execute("SELECT * FROM History WHERE Id = ?",
                                [sql.HISTORY_ID])
        d = dict(sql.hist_cursor.fetchone())
        if d is None:
            print('monitor.save_window_geom error no History ID:', sql.HISTORY_ID)
            return False
    else:
        # First time add the record
        sql.hist_add(time.time(), 0, g.USER, 'window', name, geom,
                     'saved on exit, loaded on starting', None, 0, 0, 0.0,
                     "Used in conjunction with 'screen' History Record Id #")
        sql.con.commit()
        return True

    ''' We have the existing history record, simply replace the geometry field 
        Time is from creation, Timestamp is from update
    '''
    # 2024-03-24 sql.py in bserve doesn't have Timestamp column
    if "bserve" in sql.FNAME_LIBRARY:
        sql_cmd = "UPDATE History SET SourceMaster=? WHERE Id = ?"
        sql.hist_cursor.execute(sql_cmd, (geom, sql.HISTORY_ID))
    else:
        sql_cmd = "UPDATE History SET Timestamp=?, SourceMaster=? WHERE Id = ?"
        sql.hist_cursor.execute(sql_cmd, (time.time(), geom, sql.HISTORY_ID))
    sql.con.commit()


def get_mouse_location(coord_only=True):
    """ Get Mouse Location using xdotool. Called by Monitors().get_mouse_monitor().
        Also used by homa.py and homa-indicator.py. Ported from homa-common.py.
    """

    f = os.popen("xdotool getmouselocation")  # 0.012 seconds
    text = f.read().strip()
    _returncode = f.close()  # https://stackoverflow.com/a/70693068/6929343

    # print("text:", text, "returncode:", _returncode)
    # text: ['x:5375 y:2229 screen:0 window:56623114'] returncode: None

    def get_value(offset):
        """ Get value from key: value pair """
        try:
            # text: ['x:5375 y:2229 screen:0 window:56623114'] returncode: None
            key_value = text.split()[offset]
        except IndexError:
            return "30"

        try:
            # key_value[0]: 'x:5375' -OR- key_value[1]: 'y:2229'
            value = key_value.split(":")[1]
        except IndexError:
            value = 30
        return value

    xPos = get_value(0)
    yPos = get_value(1)

    if coord_only:
        return xPos, yPos

    # noinspection SpellCheckingInspection
    """
time xwd -root -silent | convert xwd:- -depth 8 -crop "1x1+20+20" txt:- | grep -om1 '#\w\+'
    
    
#!/usr/bin/python -W ignore::DeprecationWarning
import sys
import gtk

def get_pixel_rgb(x, y):
    pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 1, 1)
    pixbuf.get_from_drawable(gtk.gdk.get_default_root_window(),
                             gtk.gdk.colormap_get_system(), 
                             x, y, 0, 0, 1, 1)
    return pixbuf.get_pixels_array()[0][0]
    """

    Screen = get_value(2)
    Window = get_value(3)
    return xPos, yPos, Screen, Window


# End of monitor.py
