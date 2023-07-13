#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: Pippim
License: GNU GPLv3
Source: This repository
Description: mserve - Music Server - X11 window client
"""

from __future__ import print_function  # Must be first import
from __future__ import with_statement  # Error handling for file opens

# ==============================================================================
#
#       x11 - Module for Python X lib (X11) functions
#
#       July 05 2023 - Make display optional when bserve indirectly imports.
#       July 12 2023 - Interface to/from mserve_config.py
#
# ==============================================================================

# noinspection SpellCheckingInspection
"""
    To solve this error:
  File "/usr/lib/python2.7/dist-packages/Xlib/protocol/rq.py", line 510, in parse_binary_value
    v = struct.unpack(scode, data[pos: pos + slen])
error: unpack requires a string argument of length 4

    It is necessary to move Ubuntu 16.04 from Xlib version 0.14 to Ubuntu 20.04 version with:

        python-xlib_0.23-2build1_all.deb for 20.04 LTS Focal Fossa
        python-xlib_0.29-1.debian.tar.xz for 21.04 Hirsute Hippo

"""
# inspection SpellCheckingInspection

''' July 12, 2023 - Doesn't look like these belong. 
try:
    import tkinter as tk
    import tkinter.ttk as ttk
    import tkinter.font as font
    import tkinter.filedialog as filedialog
    import tkinter.messagebox as messagebox
    import tkinter.scrolledtext as scrolledtext
    PYTHON_VER = "3"
except ImportError:  # Python 2
    import Tkinter as tk
    import ttk
    import tkFont as font
    import tkFileDialog as filedialog
    import tkMessageBox as messagebox
    import ScrolledText as scrolledtext
    PYTHON_VER = "2"
# print ("Python version: ", PYTHON_VER)

from PIL import Image, ImageTk
'''

# Print the name and bounding box (x1, y1, x2, y2) for the active window in
# a loop.

# Credit: active_window_xlib_demo.py
# link:   https://gist.github.com/mgalgs/8c1dd50fe3c19a1719fb2ecd012c4edd
import time
from collections import namedtuple

# /usr/lib/python2.7/dist-packages/Xlib/X.py
import Xlib.X
# /usr/lib/python2.7/dist-packages/Xlib/__init__.py
import Xlib
# /usr/lib/python2.7/dist-packages/Xlib/display.py
import Xlib.display
# /usr/lib/python2.7/dist-packages/Xlib/ext/randr.py
from Xlib.ext import randr

#d = Xlib.display.Display(':0')              # d is for X11 Display object
# noinspection SpellCheckingInspection
"""
System crash in ~/bserve June 19, 2023, noticed July 5, 2023. Cause was change:
Jun 17 23 - toolkit.normalize_tcl() changed to support "vwxyz" which were "?"

Xlib.xauth: warning, no xauthority details available
Traceback (most recent call last):
  File "/home/rick/bserve/gmail-send-msg.py", line 28, in <module>
    import gmail_api
  File "/home/rick/bserve/gmail_api.py", line 74, in <module>
    import external as ext          # Timing
  File "/home/rick/bserve/external.py", line 24, in <module>
    import toolkit
  File "/home/rick/bserve/toolkit.py", line 58, in <module>
    import image as img         # Pippim image.py module
  File "/home/rick/bserve/image.py", line 45, in <module>
    import x11                  # Home-brewed x11 wrapper functions
  File "/home/rick/bserve/x11.py", line 62, in <module>
    d = Xlib.display.Display(':0')              # d is for X11 Display object
  File "/usr/lib/python2.7/dist-packages/Xlib/display.py", line 80, in __init__
    self.display = _BaseDisplay(display)
  File "/usr/lib/python2.7/dist-packages/Xlib/display.py", line 62, in __init__
    display.Display.__init__(*(self, ) + args, **keys)
  File "/usr/lib/python2.7/dist-packages/Xlib/protocol/display.py", line 129, in __init__
    raise error.DisplayConnectionError(self.display_name, r.reason)
Xlib.error.DisplayConnectionError: Can't connect to display ":0": No protocol specified
"""

try:
    d = Xlib.display.Display(':0')              # d is for X11 Display object
    r = d.screen().root                         # r is for X11 Root object

    _NET_ACTIVE_WINDOW = d.intern_atom('_NET_ACTIVE_WINDOW')
    _NET_CLIENT_LIST = d.get_atom('_NET_CLIENT_LIST')
    _NET_WM_NAME = d.get_atom('_NET_WM_NAME')

    # Note x11 uses 'height' then 'width'. Tkinter uses 'width' then 'height'.
    # Change below from author's original "height width" format.
    Geometry = namedtuple('Geometry', 'x y width height')
except Xlib.error.DisplayConnectionError:
    # Can't connect to display ":0": No protocol specified
    print('Can\'t connect to display ":0": No protocol specified')


def find_mode(iid, modes):
    """ Called by get_display_info() below """
    for mode in modes:
        if iid == mode.id:
            return "{}x{}".format(mode.width, mode.height)


def get_display_info():
    """ Not working """
    #d = display.Display(':0')
    #screen_count = d.screen_count()
    #default_screen = d.get_default_screen()
    result = []
    screen = 0
    info = d.screen(screen)

    window = info.root
    #window = r.root

    res = randr.get_screen_resources(window)
    for output in res.outputs:
        params = d.xrandr_get_output_info(output, res.config_timestamp)
        #try:
        #    params = d.xrandr_get_output_info(output, res.config_timestamp)
        #except Exception as e:  # work on python 3.x
        #    print('Failed to get params: ' + str(e))
        #    print('unpack requires a string argument of length 4',
        #          'res.config_timestamp:', res.config_timestamp)
        #    return None

        if not params.crtc:
            continue

        print('res.config_timestamp:', res.config_timestamp)  # Debugging
        #print('Xlib.X.CurrentTime:', Xlib.X.CurrentTime)
        crtc = d.xrandr_get_crtc_info(params.crtc, res.config_timestamp)
        #try:
        #    crtc = d.xrandr_get_crtc_info(params.crtc, res.config_timestamp)
        #except Exception as e:  # work on python 3.x
        #    print('Failed to unpack: ' + str(e))
        #    print('unpack requires a string argument of length 4',
        #          'res.config_timestamp:', res.config_timestamp)
        #    return None

        #x = crtc.x
        #y = crtc.y

        modes = set()
        for mode in params.modes:
            modes.add(find_mode(mode, res.modes))
        result.append({
            'name': params.name,
            'resolution': "{}x{}+{}+{}".
            format(crtc.width, crtc.height, crtc.x, crtc.y),
            'available_resolutions': list(modes)
        })

    return result


#print(get_display_info())           # Test xrandr extension


def get_window_name(win):
    """ Get the window state above, below, full screen, etc. """
    return win.get_wm


def get_window_state(win):
    """ Get the window state above, below, full screen, etc. """
    return win.get_wm_state()


def wait_visible_name(string, toplevel, ms, times):
    """ Get window name matching substring and return hex ID
        Call toplevel.after(ms) for number of times.
    """
    # print('search string:', string)
    for i in range(times):
        win_list = build_windows_list()
        for win_dict in win_list:
            if string in win_dict['name']:
                # print('found after', i, 'times')  # Found after 3 times = 99 ms
                return win_dict['id']
        toplevel.after(ms)
    return None


def get_absolute_geometry(win):
    """
    Returns the (x, y, height, width) of a window relative to the top-left
    of the screen.
    """
    geom = win.get_geometry()
    (x, y) = (geom.x, geom.y)
    while True:
        parent = win.query_tree().parent
        p_geom = parent.get_geometry()
        x += p_geom.x
        y += p_geom.y
        if parent.id == r.id:           # Are we at Root?
            break
        win = parent

    # noinspection PyArgumentList
    return Geometry(x, y, geom.width, geom.height)


def get_window_bbox(win):
    """
    Returns (x1, y1, x2, y2) relative to the top-left of the screen.
    """
    geom = get_absolute_geometry(win)
    x1 = geom.x
    y1 = geom.y
    x2 = x1 + geom.width
    y2 = y1 + geom.height
    return x1, y1, x2, y2


def get_active_window():
    win_id = r.get_full_property(_NET_ACTIVE_WINDOW,
                                 Xlib.X.AnyPropertyType).value[0]
    try:
        return d.create_resource_object('window', win_id)
    except Xlib.error.XError:
        pass


def set_window_above(win_id):
    win_id.configure(stack_mode=Xlib.X.Above)
    d.sync()


def move_window(window, x, y, width, height):
    """ Use x11 library to move window From:
        https://gist.github.com/chipolux/13963019c6ca4a2fed348a36c17e1277
    """
    window.configure(x=x, y=y, width=width, height=height, border_width=0,
                     stack_mode=Xlib.X.Above)
    d.sync()


def build_windows_list():
    """ Use x11 library to build windows list

        TODO: Turn this into a class
    """

    win_list = []

    window_ids = r.get_full_property(
        d.intern_atom('_NET_CLIENT_LIST'), Xlib.X.AnyPropertyType).value

    for window_id in window_ids:
        # Note window_id is integer followed by L
        window_obj = d.create_resource_object('window', window_id)
        name = window_obj.get_wm_name()
        win_dict = {'id': window_obj.id, 'name': name}
        win_list.append(win_dict)

    return win_list


def screenshot(x, y, width, height):
    """ Take screenshot """
    raw = r.get_image(x, y, width, height, Xlib.X.ZPixmap, 0xffffffff)
    image = Image.frombytes("RGB", (width, height), raw.data, "raw", "BGRX")
    return image


def main():
    while True:
        # Protect against races when the window gets destroyed before we
        # have a chance to use it.  Guessing there's a way to lock access
        # to the resource, but for this demo we're just punting.  Good
        # enough for who it's for.
        try:
            win = get_active_window()
            print(win.get_wm_name(), get_window_bbox(win))
        except Xlib.error.BadWindow:
            print("Window vanished")
        time.sleep(1)


if __name__ == "__main__":
    main()

# End of x11.py
