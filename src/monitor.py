#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
#
#       monitor.py - Functions for divining screen, monitor and window
#
#       Check out: https://www.pythoncheatsheet.org/
#             and: https://python-future.org/compatible_idioms.html
#
# ==============================================================================

"""
        Requires:

            Gnome Desktop Toolkit (Gdk)
            python-xlib
"""

from __future__ import print_function

try:                        # Python 3
    import tkinter as tk
    PYTHON_VER = "3"

except ImportError:         # Python 2
    import Tkinter as tk
    PYTHON_VER = "2"

import os                   # For get_xrandr_monitors()
import time                 # To use time.time()

from collections import OrderedDict, namedtuple

''' mserve modules (some shared by bserve via symlink) including this one! '''
#import location as lc       # To get USER id
import global_variables as g
import image as img         # Routines for tk & photo images
import sql                  # SQLite3 functions

''' Logging is duplicated in monitor.py module. Not sure how to apply yet? '''
# https://stackoverflow.com/a/36419702/6929343
# import logging

# https://stackoverflow.com/a/67352300/6929343
# logging.getLogger('PIL').setLevel(logging.WARNING)
import sys
# noinspection SpellCheckingInspection
#logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
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
    import sys
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


''' Future code '''


def get_gtk_window():
    """ Not used """
    # From: https://askubuntu.com/a/303754/307523
    import gi
    gi.require_version('Gdk', '3.0')
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gdk, Gtk

    # Replace w with the GtkWindow of your application
    w = Gtk.Window()
    # Get the screen from the GtkWindow
    s = w.get_screen()
    # Using the screen of the Window, the monitor it's on can be identified
    m = s.get_monitor_at_window(s.get_active_window())
    # Then get the geometry of that monitor
    monitor = s.get_monitor_geometry(m)
    # This is an example output
    print("Height: %s, Width: %s, X: %s, Y: %s" %
          (monitor.height, monitor.width, monitor.x, monitor.y))


def e_print(test):
    pass


def ipr(test):
    pass


def apr(test):
    pass


def ipr(test):
    pass


"""  REAL REAL REAL REAL REAL REAL REAL REAL REAL REAL REAL REAL REAL REAL """

''' Start of REAL code used today (July 2, 2021) '''

DISPLAY = None
SCREEN = None
NUMBER_OF_MONITORS = None
GNOME = None


class Monitors:
    def __init__(self):
        """ Build list of monitors forming desktop (aka X11 screen) """
        self.desk_width = 0
        self.desk_height = 0

        import gi
        gi.require_version('Gdk', '3.0')
        from gi.repository import Gdk

        global DISPLAY, SCREEN, NUMBER_OF_MONITORS, GNOME

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
            GNOME = 3.22
        except AttributeError:
            # Gnome 3.18
            NUMBER_OF_MONITORS = SCREEN.get_n_monitors()
            primary = SCREEN.get_primary_monitor()
            GNOME = 3.18

        self.screen_width = SCREEN.width    # Should equal self.desk_width
                                            # But contains 'gi.FunctionInfo(width)'
        self.screen_height = SCREEN.height  # Should equal self.desk_height
                                            # But contains 'gi.FunctionInfo(height)'
        self.gdk_gnome_version = GNOME      # Traditional for outside

        self.monitors_list = []             # List of dictionaries w/monitor
        self.monitor_count = NUMBER_OF_MONITORS
        self.found_monitor = None
        self.found_window = None            # Not really necessary but simpler
        self.primary_monitor = None

        # collect data about monitors
        for index in range(NUMBER_OF_MONITORS):
            mon = OrderedDict()
            if GNOME == 3.22:
                monitor = DISPLAY.get_monitor(index)
                primary = monitor.is_primary()
                geometry = monitor.get_geometry()
                name = monitor.get_monitor_plug_name()
            else:
                geometry = SCREEN.get_monitor_geometry(index)
                name = SCREEN.get_monitor_plug_name(index)

            # print("Monitor {} = {}x{}+{}+{}".format(
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
                mon['primary'] = True       # Usually static but user could change
                # noinspection PyArgumentList
                #self.primary_monitor = Monitor(mon.keys())(*mon.values())
                self.primary_monitor = namedtuple('Monitor', mon.keys())(*mon.values())
            else:
                mon['primary'] = False

            self.found_monitor = namedtuple('Monitor', mon.keys())(*mon.values())
            self.monitors_list.append(self.found_monitor)

            # Running calculation of desktop width x height
            x2 = geometry.x + geometry.width
            if x2 > self.desk_width:
                self.desk_width = x2
            y2 = geometry.y + geometry.height
            if y2 > self.desk_height:
                self.desk_height = x2

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

        # TODO: Calculate dead zones in desk top (no monitor)

    def get_focus(self):
        """ Set monitor dictionary to monitor with focus

            First get window that has focus. Then use coordinates to devise
            which monitor it is on.
        """
        pass

    def get_n_monitors(self):
        return self.monitor_count

    # noinspection PyUnusedLocal
    def get_active_window(self):
        """
            From: https://stackoverflow.com/a/41046548/6929343

        """
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
                geom = window.get_geometry()        # Includes decorations
                window_name = window.get_name()
                x_id = window.get_xid()
                # A lot more attributes are available see:
                # https://lazka.github.io/pgi-docs/Wnck-3.0/classes/Window.html#Wnck.Window.get_screen
                break
                
        # clean up Wnck (saves resources, check documentation)
        window = None                       # Although pycharm flags as error,
        screen = None                       # these are important else crash!!
        Wnck.shutdown()
        Window = namedtuple('Window', 'number, name, x, y, width, height')
        # noinspection PyArgumentList
        self.found_window = Window(x_id, window_name, geom.xp, geom.yp,
                                   geom.widthp, geom.heightp)
        return self.found_window 

    def get_active_monitor(self):
        """
            First find the active window. Then find what monitor it is on and
            then return that monitor.
        """

        win = self.get_active_window()      # Results in self.found_window too

        x, y, w, h = win.x, win.y, win.width, win.height

        if x < 0 or x > self.screen_width:  # same as self.desk_width
            x = 0  # Window top left may be off screen!
            print('ERROR monitor.py: Window:,', win.number,
                  'x-offset:', win.x, 'was off screen.\n', win.name)
        if y < 0 or y > self.screen_height:  # same as self.desk_height
            y = 0
            print('ERROR monitor.py: Window:,', win.number,
                  'y-offset:', win.y, 'was off screen.\n', win.name)

        primary_monitor = None

        for mon in self.monitors_list:
            # Save primary monitor if needed later
            if mon.primary is True:
                primary_monitor = mon

            # Most of window must be on monitor to qualify
            if x < mon.x:
                # A) This is flawed test.
                # win.x could be 10 pixels before mon.x but
                # win.width could be 1000 and most of window
                # does sit inside mon
                continue
            if x >= mon.x + mon.width // 2:
                # B) This is flawed test.
                # win.x could be 10 pixels past mon.x middle
                # win.width might only be 400 pixels and all of window
                # sits inside mon
                continue
            if y < mon.y:
                # C) This is flawed test similar to A).
                continue
            if y >= mon.y + mon.height // 2:
                # D) This is flawed test similar to B).
                continue

            # Window is mostly on this monitor.
            return mon

        # If window off of screen use first monitor
        return primary_monitor

    def tk_center(self, window):
        """
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

        return mon  # Should win namedtuple be returned instead?


# OLDER CODE: Eventually yanked out.


def get_monitors():
    """
        Get list of monitors in Gnome Desktop

        TODO: Flush displays / pending events first?

        :returns List of dictionaries

    """

    import gi
    gi.require_version('Gdk', '3.0')
    from gi.repository import Gdk

    global DISPLAY, SCREEN, NUMBER_OF_MONITORS, GNOME

    if DISPLAY is None:
        DISPLAY = Gdk.Display.get_default()
        SCREEN = DISPLAY.get_default_screen()

    # Gnome version 3.22 developed new monitor object
    try:
        # Gnome 3.22
        NUMBER_OF_MONITORS = DISPLAY.get_n_monitors()
        primary = False
        GNOME = 3.22
    except AttributeError:
        # Gnome 3.18
        NUMBER_OF_MONITORS = SCREEN.get_n_monitors()
        primary = SCREEN.get_primary_monitor()
        GNOME = 3.18

    # collect data about monitors
    monitors = []
    for index in range(NUMBER_OF_MONITORS):
        mon = {}
        if GNOME == 3.22:
            monitor = DISPLAY.get_monitor(index)
            primary = monitor.is_primary()
            geometry = monitor.get_geometry()
            name = monitor.get_monitor_plug_name()
        else:
            geometry = SCREEN.get_monitor_geometry(index)
            name = SCREEN.get_monitor_plug_name(index)

        # print("Monitor {} = {}x{}+{}+{}".format(
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



def center(window):
    """
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
    if x < 0:
        x = 0  # Window top left may be off screen!
    if y < 0:
        y = 0

    window.geometry('+{}+{}'.format(x, y))

    return mon_dict


''' Start of REAL code used today (May 2, 2021) '''


def get_tk_window_monitor_dict(window):
    """
    Returns the mserve monitor dictionary a tkinter window is on.
    If window is off screen force it into Monitor 1 (index 0).

    Cannot use Gdk_Monitor_At_Window(gdk_window) because it only works on
    Gdk windows.

    :param window: Tkinter root or Toplevel
    """

    monitors = get_monitors()                   # List of monitor dictionaries

    x, y, w, h = get_window_geom_raw(window)    # Tkinter style window geometry

    if x < 0 or x > SCREEN.width():
        x = 0  # Window top left may be off screen!
    if y < 0 or y > SCREEN.height():
        y = 0

    first_monitor = None

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
    window.attributes('-alpha', 0.0)    # Make window invisible
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
    # Move window to the reported fake geometry adjust to reality
    # TODO: Make this optional to reduce "blink" when closing program
    if leave_visible:
        window.geometry('+{}+{}'.format(x, y))
        window.attributes('-alpha', 1.0)    # Make window visible again
        window.update_idletasks()

    return x, y, w, h


def get_window_geom_rect(window, leave_visible=True):
    """ Get Tkinter window's x0, y0, x1, y1 tuple """
    x, y, w, h = get_window_geom_raw(window, leave_visible)
    return x, y, (x + w), (y + h)


def get_window_geom_string(window, leave_visible=True):
    """ Get Tkinter window's width x height + x-offset + y-offset """
    x, y, w, h = get_window_geom_raw(window, leave_visible)
    return str(w) + 'x' + str(h) + '+' + str(x) + '+' + str(y)


def get_xrandr_monitors():
    """ Return list of monitors by parsing output from:

        $ xrandr --list monitors

             Monitors: 3
             0: +*eDP-1-1 1920/382x1080/215+3840+2160  eDP-1-1
             1: +HDMI-0 1920/1107x1080/623+0+0  HDMI-0
             2: +DP-1-1 3840/1600x2160/900+1920+0  DP-1-1

    """
    # noinspection SpellCheckingInspection
    result = os.popen('xrandr --listmonitors').read().splitlines()
    # inspection SpellCheckingInspection

    # print('get_xrandr_monitors() result:')
    # print(result)

    monitors = []
    for line in result:
        # Compress multiple whitespace into single space
        line = ' '.join(line.split())

        if "Monitors" in line:
            continue              # First line needs to be skipped

        monitor = {'number': int(line.split(':')[0])}
        # print('line:', line)
        # print('field 0:', line.split(':')[0])
        if "*" in line:
            monitor['primary'] = True
        else:
            monitor['primary'] = False
        full_geom_list = line.split()[2:3]
        full_geom = full_geom_list[0]
        # print('full_geom:', full_geom)
        monitor['x'] = int(full_geom.split('+')[1:2][0])
        monitor['y'] = int(full_geom.split('+')[2:][0])
        width_height = full_geom.split('+')[0]
        width = width_height.split('x')[0]
        height = width_height.split('x')[1]
        monitor['width'] = int(width.split('/')[0])
        monitor['height'] = int(height.split('/')[0])
        monitor['name'] = line.split()[-1]
        monitors.append(monitor)

    # print('get_xrandr_monitors() monitors:')
    # print(monitors)

    return monitors     # List of mon_dict


def get_window_geom(name):
    """
    Every time you get the window geometry it is panel height lower than it
    really is. Subsequently when painting it it is lower. Subtract PANEL_HGT
    from the values.

    CURRENT:
        Get geometry for window which was saved on last exit. If no record
        use 100,100 and predefined default width & height. Returns string
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
    Action:         'library'
    SourceMaster:   'width x height + x_offset + y_offset'  # Only saved when different than last time
    SourceDetail:   'saved on exit, loaded on starting
    Comments:       "Used in conjunction with 'screen' History Record Id #"

    Type:           'window'
    Action:         'playlist'
    SourceMaster:   'width x height + x_offset + y_offset'
    SourceDetail:   'saved on exit, loaded on starting
    Comments:       "Used in conjunction with 'screen' History Record Id #"

    NOTE:       xrandr is the easy approach but requires os.open() calls
                that are rather messy. Instead try gtk commands which *should*
                support Wayland and offer more symmetry with Windows, Mac
                ChromeOS and Android. See: https://stackoverflow.com/a/21213145/6929343
    """

    if name == 'library':  # mserve.py & bserve.py
        _w = int(1920 * .75)
        _h = int(1080 * .75)
        _root_xy = (100, 100)  # Temporary hard-coded coordinates
        default_geom = '%dx%d+%d+%d' % (_w, _h, _root_xy[0], _root_xy[1])
    elif name == 'playlist':  # mserve.py
        xy = (130, 130)
        default_geom = '+%d+%d' % (xy[0], xy[1])
    elif name == 'backups':  # bserve.py
        xy = (130, 130)
        default_geom = '+%d+%d' % (xy[0], xy[1])
    elif name == 'history':  # webscrape.py
        xy = (130, 130)
        default_geom = '+%d+%d' % (xy[0], xy[1])
    elif name == 'encoding':  # encoding.py
        xy = (130, 130)
        default_geom = '+%d+%d' % (xy[0], xy[1])
    elif name == 'results':  # webscrape.py
        xy = (130, 130)
        default_geom = '+%d+%d' % (xy[0], xy[1])
    elif name == 'sql_music':  # mserve.py
        xy = (130, 130)
        default_geom = '+%d+%d' % (xy[0], xy[1])
    elif name == 'sql_history':  # mserve.py
        xy = (130, 130)
        default_geom = '+%d+%d' % (xy[0], xy[1])
    else:
        print('monitor.get_window_geom(): Bad window name:', name)
        xy = (130, 130)
        default_geom = '+%d+%d' % (xy[0], xy[1])

    if sql.hist_check(0, 'window', name):
        sql.hist_cursor.execute("SELECT * FROM History WHERE Id = ?",
                                [sql.HISTORY_ID])
        d = dict(sql.hist_cursor.fetchone())
        if d is None:
            # If we get here there is programmer error
            print('monitor.get_window_geom(): No History ID:', sql.HISTORY_ID)
            return default_geom
        return d['SourceMaster']
    else:
        # First time add the record
        return default_geom


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
        # sql.hist_add(time.time(), 0, lc.USER, 'window', name, geom,
        sql.hist_add(time.time(), 0, g.USER, 'window', name, geom,
                     'saved on exit, loaded on starting', None, 0, 0, 0.0,
                     "Used in conjunction with 'screen' History Record Id #")
        sql.con.commit()
        return True

    ''' We have the existing history record, simply replace the geometry field '''
    sql_cmd = "UPDATE History SET Time=?, SourceMaster=? WHERE Id = ?"

    sql.hist_cursor.execute(sql_cmd, (time.time(), geom, sql.HISTORY_ID))
    sql.con.commit()

# End of monitor.py
