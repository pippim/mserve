#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: Pippim
License: GNU GPLv3
Source: This repository
Description: mserve - Music Server - Tkinter Tools and Tooltips()
"""

from __future__ import print_function       # Must be first import
from __future__ import with_statement       # Error handling for file opens

#==============================================================================
#
#       toolkit.py - tkinter functions
#
#       Jan. 18 2022 - Set tooltip location SW, SE, NW or NE of parent widget.
#       Feb. 26 2022 - Add border to tooltip, don't vary y-axis mouse movement.
#       Jul. 17 2022 - Error in bserve when bup_view close button clicked.
#       Jul. 25 2022 - Begin systray development - GNOME cross platform.
#       Jul. 30 2022 - Expand find_column() with:  elif self.find_op == '>=':
#       Apr. 15 2023 - Move in normalize_tcl() from bserve.py for mserve.py.
#       Jun. 15 2023 - New Tooltip anchor "sc" South Centered for banner_btn
#       July 11 2023 - Delete unused methods to simplify mserve_config.py
#       Aug. 15 2023 - Fix 'menu' tooltips on left monitor with self.menu_tuple
#       Jan. 01 2024 - computer_bytes(size_str) converts '4.0K blah' to 4000
#       Mar. 23 2024 - Save custom views in DictTreeview() class
#       Apr. 30 2024 - New tool_type="splash" manually invoked
#       May. 15 2024 - User configurable Tooltip colors and timings
#       Sep. 03 2024 - Tooltips - Remove old splash window before new splash
#       Dec. 29 2024 - Tooltips - ttk.Label, ttk.Frame & ttk.Entry fg/bg colors
#
#==============================================================================

# identical imports in mserve

# Must be before tkinter and released from interactive. Required to insert
# from clipboard.
#import gtk                     # Doesn't work. Use xclip instead
#gtk.set_interactive(False)

'''

References:
    https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/ttk-Treeview.html

'''


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

from PIL import Image, ImageTk  # For MoveTreeviewColumn
from ttkwidgets import CheckboxTreeview

# python standard library modules
import os
import time
import datetime
from collections import OrderedDict, namedtuple
import re                   # w, h, old_x, old_y = re.split(r'\D+', geom)
import copy
import traceback            # To display call stack (functions that got us here)
import locale               # Use decimals or commas for float remainder?
try:
    import subprocess32 as sp
    SUBPROCESS_VER = '32'
except ImportError:  # No module named subprocess32
    import subprocess as sp
    SUBPROCESS_VER = 'native'
# mserve modules
import global_variables as g
if g.USER is None:
    print('toolkit.py was forced to run g.init()')
    g.init()
import message              # Rename column heading (AskString)
import external as ext      # External program calls
import timefmt as tmf       # Time formatting routines
import image as img         # Pippim image.py module
import sql                  # Pippim sqlite3 methods

# noinspection SpellCheckingInspection
'''
    Optional gnome_screenshot() for MoveTreeviewColumn function imports:
        import gi
        gi.require_version('Gdk', '3.0')
        gi.require_version('Gtk', '3.0')
        gi.require_version('Wnck', '3.0')
        # gi.require_versions({"Gtk": "3.0", "Gdk": "3.0", "Wnck": "3.0"})
        from gi.repository import Gdk, GdkPixbuf, Gtk, Wnck
'''


def print_trace():
    """ Mimic trace """
    for line in traceback.format_stack():
        print(line.strip())


def get_trace():
    """ Mimic trace """
    return traceback.format_stack()


'''
List all objects in play next song
https://stackoverflow.com/questions/60978666/get-list-of-toplevels-on-tkinter
'''
LAST_TIME = 0.0             # So headings only appear once during recursion
WIDGET_COUNT = 0            # Last call's subtotal


def list_widgets(level, scan="All"):
    """
    List all widgets of a certain type (or "All") for object.

    Scan options are: "All", "Toplevel", "Frame", "Label",  
    "Button", "Treeview", "Scrollbar", "Menu", "Canvas" & "Other" 

    widget_list: [<Tkinter.Label instance at 0x7f16387b63f8>]
                               instance_hex: 0x7f16387b63f8

    TODO: Make into a class so global variable name space is reduced

    """
    global LAST_TIME, WIDGET_COUNT
    now = time.time()
    if not int(now) == int(LAST_TIME):
        if WIDGET_COUNT > 0:
            # Print total from last run
            print('Number of widgets:', WIDGET_COUNT)
            WIDGET_COUNT = 0
        print('\n============= list_widgets() called at:', ext.t(now),
              "'scan=" + scan + "' =============")
        print("Parent Widget:", level)
        LAST_TIME = now

    for k, v in level.children.items():

        error_found = False
        print_it = False

        if isinstance(v, tk.Toplevel) and (scan == "All" or scan == "Toplevel"):
            print('Toplevel :', 'key;', k, 'value:', v)
            print_it = True

        elif isinstance(v, tk.Frame) and (scan == "All" or scan == "Frame"):
            print('Frame    :', k, v)
            print_it = True
            if not isinstance(v, tk.Frame):
                print("toolkit.py list_widgets(): Not a tkinter Frame!")

        elif (isinstance(v, tk.Label)) and (scan == "All" or scan == "Label"):
            # elif isinstance(v, tk.Label) and (scan=="Label" or scan=="All"):
            # elif isinstance(v, tk.Label) and (scan=="Label"):
            # elif isinstance(v, tk.Label):  all were BROKEN but now work???
            print('Label    :', k, v)
            print_it = True
            instance_hex = hex(int(k))
            tkinter_label = '<Tkinter.Label instance at ' + \
                            instance_hex + '>'
            print('\t Instance :', k, tkinter_label)
            if not isinstance(v, tk.Label):
                print("toolkit.py list_widgets(): Not a tkinter Label!",
                      scan)
            
        elif isinstance(v, tk.Button) and (scan == "All" or scan == "Button"):
            print('Button   :', k, v)
            print_it = True

        elif isinstance(v, ttk.Treeview) and (scan == "All" or scan == "Treeview"):
            print('Treeview :', k, v)
            print_it = True

        elif isinstance(v, tk.Scrollbar) and (scan == "All" or scan == "Scrollbar"):
            print('Scrollbar:', k, v)
            print_it = True

        elif isinstance(v, tk.Menu) and (scan == "All" or scan == "Menu"):
            print('Menu     :', k, v)
            print_it = True

        elif isinstance(v, tk.Canvas) and (scan == "All" or scan == "Canvas"):
            print('Canvas   :', k, v)
            print_it = True

        elif scan == "All" or scan == "Other":
            print('Other    :', k, v)
            print_it = True

        else:
            # This instance doesn't match but drill down and return
            print("\t No match scanning for:", scan, k, v)
            # top levels(v, scan=scan)
            list_widgets(v, scan=scan)
            WIDGET_COUNT += 1
            error_found = True

        if print_it is False:
            continue

        if error_found is True:
            pass
        
        print('\t Geometry  :', v.winfo_geometry(),
              "x-offset:", v.winfo_x(), "y-offset:", v.winfo_y())

        try:
            # pprint.pprint(v.config())
            print('\t Text      :', v.cget('text'))
        except tk.TclError:
            pass

        try:
            # pprint.pprint(v.config())
            print('\t Font      :', v.cget('font'))
            try:
                tt_font = font.Font(font=label['font'])
                print(tt_font.actual())
            except NameError:
                # Maybe try something like this instead:
                #         # Creating a Font object of "TkDefaultFont"
                #         self.defaultFont = font.nametofont("TkDefaultFont")
                print("\t tt_font = font.Font(font=label['font']): 'label' is undefined???")
        except tk.TclError:
            pass

        try:
            print('\t Foreground:', v.cget('fg'), 'Background:', v.cget('bg'))
        except tk.TclError:
            pass

        keys = v.keys()
        for key in keys:
            print("\t Attribute : {:<20}".format(key), end=' ')
            value = v[key]
            value_type = type(value)
            try:
                print('Type: {:<25} Value: {}'.format(str(value_type), value))
            except TypeError:
                # <_tkinter_TCL_Obj> doesn't format properly...
                print('Type:', value_type, 'value:', value)

        list_widgets(v, scan=scan)
        WIDGET_COUNT += 1


def config_all_labels(level, **kwargs):
    """ Configure all tk labels within a frame (doesn't work for toplevel?).

        level = frame name, eg self.play_frm

        **kwargs = tkinter_button.configure(keywords and values). For example:
            fg="#000000", bg="#ffffff", pad x=5

    """

    global LAST_TIME, WIDGET_COUNT
    now = time.time()
    if not int(now) == int(LAST_TIME):
        if WIDGET_COUNT > 0:
            # print('Number of widgets:', WIDGET_COUNT)
            WIDGET_COUNT = 0
        # print('\n========= config_all_labels() called at:', ext.t(now),'=========')
        LAST_TIME = now

    for k, v in level.children.items():

        if isinstance(v, tk.Label):
            '''
            print('Label    :', k, v)
            wrapper = kwargs
            print('\t **kwargs :', wrapper)
            instance_hex = hex(int(k))
            tkinter_label = ('<Tkinter.Label instance at ' + \
                             instance_hex + '>')
            print('\t Instance :', k, tkinter_label)
            #tkinter_label.configure(**kwargs)      # THIS IS STRING!
            '''
            if v["image"] == "":
                # We can't configure image labels that have a value
                v.configure(**kwargs)

        config_all_labels(v, **kwargs)
        WIDGET_COUNT += 1


def config_all_buttons(level, **kwargs):
    """ Configure all tk buttons within a frame (doesn't work for toplevel?).

        level = frame name, eg self.play_btn

        **kwargs = tkinter_button.configure(keywords and values). For example:
            fg="#000000", bg="#ffffff", pad x=5
    """
    for k, v in level.children.items():

        if isinstance(v, tk.Button):
            if v["image"] == "":
                # We can't configure image labels that have a value
                v.configure(**kwargs)

        config_all_buttons(v, **kwargs)


def config_all_canvas(level, **kwargs):
    """ Configure all tk canvass within a frame

        level = frame name, eg self.play_F3_panel

        **kwargs = tkinter_button.configure(keywords and values). For example:
            fg="#000000", bg="#ffffff", pad x=5
    """
    for k, v in level.children.items():

        if isinstance(v, tk.Canvas):
            v.configure(**kwargs)

        config_all_canvas(v, **kwargs)


def uni_str(s):
    """ After much headbanging a bullet proof single call for all strings  """

    # noinspection SpellCheckingInspection
    '''
        Previously used: good_str = bad_str.encode('utf-8')
        Bullet-proof is: good_str = unicode(bad_str, 'utf-8')

        Test data song by "Filter" titled "I’m Not the Only One"
        Notice the apostrophe ’ is not '

        grephere .encode | wc
            198    1026   15219  # 198 uses of ".encode('utf-8') to upgrade
    '''

    try:
        if PYTHON_VER == 3:
            return s
    except NameError:  # global name 'PYTHON_VER' is not defined
        print("toolkit.py uni_str() exception: " +
              "global name 'PYTHON_VER' is not defined")
        return s

    if s is None:
        #print_trace()
        #print("toolkit.py uni_str() string is None:", s, type(s))
        return s

    if isinstance(s, unicode):
        #print("toolkit.py uni_str() already unicode:", s, type(s))
        return s  # Already unicode, cannot do twice or get error message:
        # TypeError: decoding Unicode is not supported

    if isinstance(s, str):
        return unicode(s, 'utf-8')

    print("toolkit.py uni_str(): Unknown data type:", s, type(s))
    return s


def normalize_tcl(s):
    """
        Fixes error:
          File "/usr/lib/python2.7/lib-tk/ttk.py", line 1339, in insert
            res = self.tk.call(self._w, "insert", parent, index, *opts)
        _tkinter.TclError: character U+1f3d2 is above the 
            range (U+0000-U+FF FF) allowed by Tcl
        From: https://bugs.python.org/issue21084
    """
    astral = re.compile(r'([^\x00-\uffff])')
    new_s = ""
    for i, ss in enumerate(re.split(astral, s)):
        if not i % 2:
            new_s += ss
        # Patch June 17, 2023 for test results published below
        elif ss == "v":
            new_s += u"v"
        elif ss == "w":
            new_s += u"w"
        elif ss == "x":
            new_s += u"x"
        elif ss == "y":
            new_s += u"y"
        elif ss == "z":
            new_s += u"z"
        # end of June 17, 2023 patch
        else:
            new_s += '?'

    return new_s


# noinspection SpellCheckingInspection
'''
TclError: character U+1f3b5 is above the range (U+0000-U+FFFF) allowed by Tcl
Results prior to patch made June 17, 2023. Note sometimes you can avoid using
noramlize_tcl() function by using .encode('utf-8') See "Rainy Days" playlist
name handling in 'mserve.py build_lib_top_playlist_name()' function.

test = "abcdefghijklmnopqrstuvwxyz"
result = normalize_tcl(test)
print("test  :", test)      # test  : abcdefghijklmnopqrstuvwxyz
print("result:", result)    # result: abcdefghijklmnopqrstu?????
test2 = test.encode("utf-8")
result = normalize_tcl(test2)
print("test2 :", test2)     # test2 : abcdefghijklmnopqrstuvwxyz
print("result:", result)    # result: abcdefghijklmnopqrstu?????
test3 = test.decode("utf-8")
result = normalize_tcl(test3)
print("test3 :", test3)     # test3 : abcdefghijklmnopqrstuvwxyz
print("result:", result)    # result: abcdefghijklmnopqrstu?????
test = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
result = normalize_tcl(test)
print("test  :", test)      # test  : ABCDEFGHIJKLMNOPQRSTUVWXYZ
print("result:", result)    # result: ABCDEFGHIJKLMNOPQRSTUVWXYZ
test = "0123456789`~!@#$%^&*()_+-=[]{};:',.<>/?"
result = normalize_tcl(test)
print("test  :", test)      # test  : 0123456789`~!@#$%^&*()_+-=[]{};:',.<>/?
print("result:", result)    # result: 0123456789`~!@#$%^&*()_+-=[]{};:',.<>/?
'''

''' Time saving scheme not used yet.

    ext.t_init("grab all parents")
    all_artists = self.lib_tree.get_children()
    last_albums = self.lib_tree.get_children(all_artists[-1])
    ext.t_end('print')

    hex_str_start = '0x' + all_artists[0][1:]
    hex_str_end = '0x' + last_albums[-1][1:]
    int_start = int(hex_str_start, 16)
    int_end = int(hex_str_end, 16)
    hex_start = hex(int_start)
    hex_end = hex(int_end)
    print("\nfrom:", hex_start, "to:", hex_end)

    ext.t_init("loop through generated parents")
    awkward_fnd_cnt = 0
    for int_base in range(int_start, int_end + 1):
        hex_base = hex(int_base)
        str_base = str(hex_base)[2:].zfill(3)  # Drop '0x' prefix, prepend zeros
        parent = "I" + str_base.upper()
        try:
            stuff = self.lib_tree.item(parent)
            awkward_fnd_cnt += 1
            if awkward_fnd_cnt == 1:
                print("\nFirst Artist:", parent)
                print(stuff)
        except tk.TclError:
            print("parent not found:", parent)

    print("\n# parents:", awkward_fnd_cnt, "Last Album:", parent)
    print(stuff, "\n")
    ext.t_end('print')
    # Returns all the artists but can read sequentially from first to last
    # with hex increment to get all Artists and Albums
'''


def unique_key(key, dictionary):
    """ Create unique key(1) (2), etc. up to (99) """
    new_key = key
    i = 0  # To make PyCharm happy :)
    for i in range(1, 100):
        existing = dictionary.get(new_key)
        if existing is None:
            return new_key
        new_key = key + "(" + str(i) + ")"

    print_trace()
    print("toolkit.py - unique_key() has > " + str(i) + " duplicate keys.")
    print("new_key:", new_key)
    
    return "toolkit.py unique_key(): Two many keys"


def tv_tag_add(tv, iid, new, strict=False):
    """ Treeview tag function """
    tags = tv.item(iid)['tags']
    # BUG tags is <type 'str'>
    if isinstance(tags, str):
        #print("tv_tag_add got tags type:", type(tags))
        # This will happen for you_tree (YouTube Playlist) first time call.
        tags = []
    if new not in tags:
        tags.append(new)
        tv.item(iid, tags=tags)
        return True
    else:
        if strict:
            print_trace()
            print("'new' tag: '" + new + "' already in treeview 'tags' list:", tags)
        return False


def tv_tag_insert_first(tv, iid, new, strict=False):
    """ Treeview tag function """
    tags = tv.item(iid)['tags']
    # BUG tags is <type 'str'>
    if isinstance(tags, str):
        print("tv_tag_insert_first got tags type:", type(tags))
        tags = []
    try:
        if new not in tags:
            tags.insert(0, new)
            tv.item(iid, tags=tags)
            return True
        else:
            if strict:
                print_trace()
                print("'insert_first' tag: '" + new +
                      "' already in treeview 'tags' list:", tags)
            return False
    except AttributeError:  # 'str' object has no attribute 'insert'
        print("toolkit.py tv_tag_insert_first() tags not a list:", tags, type(tags))


def tv_tag_replace(tv, iid, old, new, strict=False):
    """ Treeview tag function """
    tags = tv.item(iid)['tags']
    if old in tags:
        if new in tags:
            if strict:
                print_trace()
                print("'new' tag: '" + new + "' already in treeview 'tags' list:", tags)
            return False
        else:
            tags.remove(old)
            tags.append(new)
            tv.item(iid, tags=tags)
            return True
    else:
        if strict:
            print_trace()
            print("'old' tag: '" + old + "' NOT in treeview 'tags' list:", tags)
        return False


def tv_tag_remove(tv, iid, old, strict=False):
    """ Treeview tag function """
    try:
        tags = tv.item(iid)['tags']
    except tk.TclError:
        # Aug 31/23 - error when synchronize locations finishes up:
        #   File "/home/rick/python/location.py", line 3981, in cmp_update_files
        #     toolkit.tv_tag_remove(self.cmp_tree, last_sel_iid, 'cmp_sel')
        #   File "/home/rick/python/toolkit.py", line 530, in tv_tag_remove
        #     tags = tv.item(iid)['tags']
        #   File "/usr/lib/python2.7/lib-tk/ttk.py", line 1353, in item
        #     return _val_or_dict(self.tk, kw, self._w, "item", item)
        #   File "/usr/lib/python2.7/lib-tk/ttk.py", line 299, in _val_or_dict
        #     res = tk.call(*(args + options))
        # TclError: wrong # args: should be ".139900134771528.139900142151368.
        # 139900142151584.139900142150936 item item ?option ?value??..."
        return False
    if old in tags:
        tags.remove(old)
        tv.item(iid, tags=tags)
        return True
    else:
        if strict:
            print_trace()
            print("'old' tag: '" + old + "' NOT in treeview 'tags' list:", tags)
        return False


def tv_tag_remove_all(tv, old):
    """ Remove tag from all items """
    items = tv.tag_has(old)
    for item in items:
        tv_tag_remove(tv, item, old, strict=True)
    return items


def custom_paste(event):
    """ Clipboard paste replaces current text selection.
        Macro level doesn't work at all. Also Ctrl-Z (undo) works with error msgs.
        Works at micro level. E.G.:
            self.lyrics_score_box.bind("<<Paste>>", toolkit.custom_paste)

        From: https://stackoverflow.com/a/46636970/6929343
        July 23, 2023 - Fix and move to toolkit.py
        2024-06-18 - Moved to toolkit.py as planned last year.
    """
    # noinspection PyBroadException
    try:
        event.widget.delete("sel.first", "sel.last")
    except:
        pass
    event.widget.insert("insert", event.widget.clipboard_get())
    return "break"


def X_is_running():
    """ Determine if xserver is running.
        https://stackoverflow.com/a/1027942/6929343 """
    p = sp.Popen(["xset", "-q"], stdout=sp.PIPE, stderr=sp.PIPE)
    p.communicate()
    return p.returncode == 0


# ==============================================================================
#
#       ProgressBars class - Managed Frame with ACCURATE progress bar(s).
#
# ==============================================================================
class CommonBar:
    """ UNDER DEVELOPMENT
        Variables common to ProgressBars__init__() and new_bar()
        Must appear before first reference (otherwise message.ShowInfo crashes)
    """
    def __init__(self, size=None):

        self.dict = {}

        self.widget = None
        self.current_state = None

        # Bar number 1 totals
        self.b1_size = size  # Total bytes / characters
        self.b1_it = None  # initial start time
        self.b1_pst = None  # Pause start time
        self.b1_tpt = None  # Total pause time


class ProgressBars(CommonBar):
    """ UNDER DEVELOPMENT
        Called from 'Tools' / 'Volume' / 'Analyze Xxx' where 'Analyze Xxx' is
        inside locations.py which is imported into mserve.py as instance 'lcs'.
    """
    def __init__(self, toplevel, item_count, item_size):

        """ Duplicate entry_init() """
        CommonBar.__init__(self)  # Recycled class like CommonTip

        self.toplevel = toplevel  # Parent window
        self.item_count = item_count
        self.item_size = item_size
        self.window = {}  # Child Window {key, widget, x, y, w, h
        self.window_list = []  # list of window dictionaries

        self.who = "toolkit.py ProgressBars()."  # For debug messages

        # All bars totals
        self.ab_count = item_count  # Total item count. Backup when size is 'None'
        self.ab_size = item_size  # Total bytes / characters. Preferred progress
        self.ab_it = None  # initial start time
        self.ab_pst = None  # Pause start time
        self.ab_tpt = None  # Total pause time

        ''' Controls to drag child window of toplevel '''
        # list of [width, height, x, y] returned by self.geometry(window)
        self.curr_geom = [0, 0, 0, 0]  # Geometry when drag_window called
        self.last_geom = [0, 0, 0, 0]  # Geometry when drag_window last called
        self.move_geom = [0, 0, 0, 0]  # Difference between curr and last
        self.toplevel.bind("<Configure>", self.drag_window)
        self.toplevel.bind("<FocusIn>", self.raise_children)

        ''' Event log '''
        self.init_time = time.time()
        self.mec = 0  # move children event count
        self.rec = 0  # raise children event count
        # times from init_time. Printed to three decimal places
        self.mit_st = 0.0  # MOVE start time.time() - self.init_time
        self.mit_en = 0.0
        self.mit_el = 0.0  # elapsed milliseconds
        self.rit_st = 0.0  # RAISE start time.time() - self.init_time
        self.rit_en = 0.0  # Raise end time
        self.rit_el = 0.0  # Raise elapsed time

        self.last_mit_st = 0.0
        self.last_rit_st = 0.0

        ''' Event log - one record for start, one record for end. '''
        self.event_log = []
        # Tuple (Event type, Event Count, Start IT, End IT, Elapsed MS)
        #   Event type = "M" or "R"

        ''' YouTube video progress and player controls '''
        self.durationYouTube = 0.0  # Length of song (Duration)
        self.progressYouTube = 0.0  # Progress (Duration) within playing song
        self.progressLastYouTube = 0.0  # Last progress, if same then stuck
        self.timeLastYouTube = 0.0  # Last System time playing video (33ms)
        self.timeForwardYouTube = 0.0  # System time self.driver.forward()
        self.isSongRepeating = None  # Fall out from .back() and .forward()
        self.youProVar = None  # YouTube Video progress TK variable, percent float
        self.youProBar = None  # YouTube Video TK Progress Bar element / instance
        self.youPlayerButton = None  # Tkinter element mounted with .grid
        self.youPlayerCurrText = None  # "None" / "Pause" / "Play" button
        self.youPlayerNoneText = "?  None"  # Music Player Text options
        self.youPlayerPlayText = "▶  Play"  # used when music player status
        self.youPlayerPauseText = "❚❚ Pause"  # changes between 1 & 2
        self.youPlayerSink = None  # Audio Sink (sink_no_str)
        """ Shared by: displayYouTubePlaylist and displayMusicIds 
            Column 1 has progress bar hidden until music playing.
            Column 3 has None / Pause / Play button player button.
            Column 4 has Close button. 
        """

        ''' button frame '''
        self.you_btn_frm = tk.Frame(self.frame)
        self.you_btn_frm.grid(row=4, columnspan=4, sticky=tk.NSEW)

        ''' Player Button - NOTE: Starts as "None" '''
        if player_button:
            # self.youPlayerButton = None  # Tkinter element mounted with .grid
            # self.youPlayerCurrText = None  # "None" / "Pause" / "Play" button
            # self.youPlayerNoneText = "?  None"  # Music Player Text options
            # self.youPlayerPlayText = "▶  Play"  # used when music player status
            # self.youPlayerPauseText = "❚❚ Pause"  # changes between 1 & 2
            self.youPlayerButton = tk.Button(self.you_btn_frm, text="None",
                                             width=g.BTN_WID2 - 4,
                                             command=self.youTogglePlayer)
            self.youPlayerButton.grid(row=0, column=3, padx=(10, 5),
                                      pady=5, sticky=tk.E)
            self.tt.add_tip(self.youPlayerButton,
                            "Music not playing", anchor="ne")

        ''' Close Button - NOTE: This calls reset() function !!! '''
        self.close_button = tk.Button(self.you_btn_frm, text="✘ Close",
                                      width=g.BTN_WID2 - 4,
                                      command=self.youClosePlayLrc)
        self.close_button.grid(row=0, column=4, padx=(10, 5), pady=5,
                               sticky=tk.E)
        self.tt.add_tip(self.close_button, "Close YouTube Playlist", anchor="ne")

        self.top.bind("<Escape>", self.youClosePlayLrc)
        self.top.protocol("WM_DELETE_WINDOW", self.youClosePlayLrc)

    def buildYouTubeDuration(self):
        """ Build progress bar under self.you_tree  """
        s = ttk.Style()
        s.theme_use("default")
        # https://stackoverflow.com/a/18140195/6929343
        s.configure("TProgressbar", thickness=6)  # Thinner bar
        self.youProVar = tk.DoubleVar()  # Close"
        self.youProBar = ttk.Progressbar(
            self.you_btn_frm, style="TProgressbar", variable=self.youProVar,
            length=1000)
        # https://stackoverflow.com/a/4027297/6929343
        self.youProBar.grid(row=0, column=1, padx=20, pady=30, sticky=tk.NSEW)
        self.you_btn_frm.pack_slaves()

    def resetYouTubeDuration(self):
        """ Set duration fields for a new song.
            The variable self.durationYouTube is set by youCurrentIndex()
        """

        now = time.time()  # DRY - Four lines repeated
        self.timeForwardYouTube = now
        self.timeLastYouTube = now
        self.progressYouTube = 0.0
        self.youPlayerSink = None  # Force Audio Sink read
        self.youPlayerCurrText = "?"  # Force button text & tooltip setup

    def updateYouTubeDuration(self):
        """ Query YouTube duration and update progress bar.
            If self.isViewCountBoost active then click next video.

            If errors occur, first step rebuild mserve playlists with:
              cd ~/.local/share/mserve/YoutubePlaylists
              rm <PLAYLIST NAME>.csv
              rm <PLAYLIST NAME>.private
              Start mserve, view <PLAYLIST NAME> and select "Smart Play All".
              If playlist doesn't rebuild then also use:
                  rm <PLAYLIST NAME>.pickle

        """
        '''
            "How often does YouTube update view count?
            Though YouTube doesn't publish this information,
            we know that it updates views approximately every
            24 to 48 hours. It does not update views instantly.
            Apr 13, 2021"

2024-01-23-05:01 - START Bombs 6:00-109, 17:29-219, 18:28-329, 19:26-439
2024-01-23-19:19 - Chill 6,050+323 Rock 25,585+462 Bombs 160+0 Gangs 3,480+17
2024-01-23-19:27 - START Gangs 6:00-339, 2024-01-24-19:37-681, 06:05-1,023
2024-01-24-05:59 - self.you_tree.see(str(you_tree_iid_int)) tcl error: 355

2024-01-25-05:00 - Chill 6,050+0 Rock 25,585+0 Bombs 601+441 Gangs 3,762+282
2024-01-25-19:35 - Gangster Skipped: 1364 (The day the music died)
2024-01-30-18:39 - Chill 5,849-201 Rock 25,594+9 Bombs 672+71 Gangs 3,641-121
            Currently only subscriber to channel but just now told another.

===============================================================================

        '''
        if self.durationYouTube == 0.0:
            self.youPrint("updateYouTubeDuration() video duration is ZERO!")
            return  # Can't divide by zero

        try:
            # CPU load = 0.00641703605652
            time_video = self.driver.execute_script(
                "return document.getElementsByTagName('video')[0].currentTime;")
        except Exception as err:
            print("updateYouTubeDuration() 'video[0].currentTime' not found!")
            print(err)
            time_video = 0.0

        # Over 45 seconds and view count speed boost active?
        if time_video >= 31.0 and self.isViewCountBoost:
            self.youPlayNext()
            # if not self.youPlayNext():
            #    print("self.isViewCountBoost TURNED OFF!")
            #    self.isViewCountBoost = None

        if time_video > 0.0:
            self.progressYouTube = time_video
        percent = float(100.0 * self.progressYouTube / self.durationYouTube)
        self.youProVar.set(percent)
        self.youProBar.update_idletasks()

    def get_it(self):
        """ Get Initial Time Offset: time.time() - self.init_time """
        return time.time() - self.init_time

    def get_el(self, start):
        """ Get End Time and Calculated Elapsed time """
        end = self.get_it()
        return end, end - start

    def log_it(self, et, ec, start):
        """ Log start time """
        tup = (et, ec, start, 0.0, 0.0)
        self.event_log.append(tup)

    def log_el(self, et, ec, es, ee, el):
        """ Log ee time & sanity check """
        _who = self.who + "log_el():"
        tup = (et, ec, es, ee, el)
        self.event_log.append(tup)

        # Sanity check
        for lt, lc, ls, le, lel in reversed(self.event_log):
            if et != lt or ec != lc:
                continue
            if es != ls:
                print("\n" + _who, "et:", et, "ec:", ec,
                      "es times differ:", self.fit(es), self.fit(ls))
            return

        print("\n" + _who, "et:", et, "ec:", ec,
              "Log start not found! es:", self.fit(es), "ee", self.fit(ee),
              "el:", self.fel(el))

    def prt_log(self):
        """ Print Log """
        _who = self.who + "prt_log():"
        cit = time.time() - self.init_time
        print("\n" + _who, "Log closed after:", self.fit(cit), "seconds.")
        print("Event (R=Raise Window, M=Move Window), Event Count, Start sec")
        print(" "*5, "Start sec  End sec  Elapsed ms")

        last_start = 0.0
        for lt, lc, ls, le, lel in self.event_log:
            if ls == last_start:  # suppress duplicated start time
                print(" "*15, self.fit(le).rjust(7), self.fel(lel).rjust(6))
            else:
                print(lt, str(lc).rjust(3), self.fit(ls).rjust(7),
                      self.fit(le).rjust(7), self.fel(lel).rjust(6))  #
            last_start = ls

    @staticmethod
    def fit(it):
        """ Format Initial Time Offset to 3 decimals """
        if it:
            return "%.3f" % round(it, 3)
        else:
            return "     "

    @staticmethod
    def fel(it):
        """ Format Elapsed Initial Time Offset in milliseconds to 2 decimal """
        if it:
            it = it * 1000.
            return "%.2f" % round(it, 2)
        else:
            return "    "

    # DOWN TO BUSINESS
    def raise_children(self, *_args):
        """ Focus in on parent. Focus in and lift the children up in the
            order they were registered.
        """
        if not len(self.window_list):
            return
        _who = self.who + "raise_children():"
        self.rec += 1  # raise event count
        self.rit_st = self.get_it()
        self.log_it("R", self.rec, self.rit_st)
        for win_dict in self.window_list:
            if self.check_candidacy(win_dict):
                win_dict['widget'].lift()
                win_dict['widget'].focus_force()
        self.rit_en, self.rit_el = self.get_el(self.rit_st)
        self.log_el("R", self.rec, self.rit_st, self.rit_en, self.rit_el)

    def move_children(self, x_off, y_off):
        """ Focus in on parent. Focus in and lift the children up in the
            order they were registered.

            2024-04-02 - As window dragged down to left, child raises up to left.
        """
        if not len(self.window_list):
            return
        _who = self.who + "move_children():"
        self.mec += 1  # raise event count
        self.mit_st = self.get_it()
        self.log_it("M", self.mec, self.mit_st)
        if True is False:
            print("\n" + _who, " | x_off:", x_off, " | y_off:", y_off)

        for win_dict in self.window_list:
            if self.check_candidacy(win_dict):
                _w, _h, x, y = self.geometry(win_dict['widget'])
                new_x = x + x_off
                new_y = y + y_off
                geom = "+" + str(new_x) + "+" + str(new_y)
                win_dict['widget'].geometry(geom)

        self.mit_en, self.mit_el = self.get_el(self.mit_st)
        self.log_el("M", self.mec, self.mit_st, self.mit_en, self.mit_el)

    def check_candidacy(self, win_dict):
        """ Test if 50% of a window lays inside parent toplevel

            :param win_dict: dictionary
        """
        _who = self.who + "check_candidacy():"
        w, h, x, y = self.geometry(win_dict['widget'])
        if True is False:  # Too much noise with spam prints
            print("\n" + _who, " | key:", win_dict['key'],
                  " | widget:", win_dict['widget'],
                  "\n\t\t | x:", x, " | y:", y, " | w:", w, " | h:", h)
        return True

    def drag_window(self, _event):
        """ Defined in __init__ with:
                self.key.bind("<Configure>", drag_window)
        """
        _who = self.who + "drag_window():"
        self.curr_geom = self.geometry(self.toplevel)  # window's [wid, hgt, x, y]
        if not self.last_geom[3]:  # Is last window height impossibly zero?
            self.last_geom = copy.deepcopy(self.curr_geom)  # last time not init

        # Leave now if geometry unchanged from last time
        if self.curr_geom == self.last_geom:
            return  # drag_window called with window.update() & no changes

        # How much has window moved or resized?
        self.move_geom = [c - l for c, l in zip(self.curr_geom, self.last_geom)]

        # Move and raise children if 50% inside parent window
        self.move_children(self.move_geom[2], self.move_geom[3])
        self.raise_children()  # NOTE: move before 50% test of raising children

        # Save for comparison next time
        self.last_geom = copy.deepcopy(self.curr_geom)

        # Uncomment print commands for debugging
        _w, _h, _x, _y = self.curr_geom  # shorthand for printing current
        _wm, _hm, _xm, _ym = self.move_geom  # shorthand for moved amounts
        #print(_who, "| x:", _x, " | y:", _y, " | w:", _w, " | h:", _h)
        #print("\t| x moved:", _xm, "\t| y moved:", _ym,
        #      "\t| width change:", _wm, "\t| height change:", _hm)

        # NOTE _event.x, _event.x_root refer to mouse position not window position

    def register_child(self, key, widget):
        """ Called from mserve.py for delayed textbox (dtb) or
            here for displaying mini-windows E.G. column details.

            Set focus in for self.key to lift the child window
            When self.key is dragged, so is the child window.
            Whilst child window is "None" do nothing.

            window.winfo_xxx see: https://wiki.tcl-lang.org/page/winfo%28%29

            :param key: 'dtb', 'column details', 'rename heading', etc.
            :param widget: msg_top, or create_window toplevel, etc.
        """
        _who = self.who + "register_child():"
        has_key = self.key_for_widget(widget)
        has_widget = self.widget_for_key(key)
        if has_key or has_widget:
            print("\n" + _who, "Window already registered.")
            print("\tkey:", key, "window:", widget)
            print("\t", self.window_list)

        w, h, x, y = self.geometry(widget)
        #print("\n" + _who, " | key:", key, " | widget:", widget,
        #      "\n\t\t | x:", x, " | y:", y, " | w:", w, " | h:", h)
        # Unordered dict so geometry order irrelevant
        win = {'key': key, 'widget': widget, 'x': x, 'y': y, 'w': w, 'h': h}
        self.window_list.append(win)  # order children born
        #print("self.window_list:", self.window_list)

    def unregister_child(self, widget):
        """ Called from mserve.py for delayed textbox (dtb) or
            here for displaying mini-windows E.G. column details.

            :param widget: dtb.msg_top, or self.key
        """
        if not len(self.window_list):
            return
        _who = self.who + "unregister_child():"
        #print("\n" + _who, "Searching for:", widget)
        #print(_who, "BEFORE self.window_list:", self.window_list)

        i = found = False
        for i, win in enumerate(self.window_list):
            if win['widget'] == widget:
                found = True
                break  # deleting index inside loop doesn't work

        if found:
            _deleted = self.window_list.pop(i)
            # Parent responsible for destroying child window.
        else:
            print("\n" + _who, " - Widget not found:", widget)

        #print(_who, "AFTER self.window_list:", self.window_list)
        #self.prt_log()

    def destroy_all(self, tt=None):
        """ When caller doesn't know the window widgets at close time """
        if not len(self.window_list):
            return

        _who = self.who + "destroy_all():"
        #print(_who, "self.window_list:", self.window_list)
        safe_list = []  # Can't iterate window_list and remove from it
        for win_dict in self.window_list:
            safe_list.append(win_dict['key'])
        for key in safe_list:
            self.destroy_by_key(key, tt)

        self.window_list = []  # Should be empty now

    def destroy_by_key(self, key, tt=None):
        """ When caller doesn't know the window widgets at close time """
        _who = self.who + "destroy_by_key():"

        window = self.widget_for_key(key)
        if window is None:
            print("\n" + _who, " - Key not found:", key)
            return False

        if tt:  # Close all tooltips under the window
            if tt.check(window):  # window may not have any tooltips
                tt.close(window)

        window.destroy()
        self.unregister_child(window)
        return True

    def key_for_widget(self, widget):
        """ When caller doesn't know the 'key' get it with window widget 

            ONLY USED FOR A FEW MINUTES THEN OBSOLETE. Leave for now.

            :param widget: Window's TK widget identifier
        """
        if not len(self.window_list):
            return
        _who = self.who + "key_for_widget():"
        for win_dict in self.window_list:
            if win_dict['widget'] == widget:
                return win_dict['key']

        #print("No key for widget:", widget)

    def widget_for_key(self, key):
        """ When caller doesn't know the 'key' get it with window widget

            :param key: Child Window's key. E.G. "move column"
        """
        if not len(self.window_list):
            return
        _who = self.who + "widget_for_key():"
        for win_dict in self.window_list:
            if win_dict['key'] == key:
                return win_dict['widget']

        #print("No key for widget:", widget)

    @staticmethod
    def geometry(widget):
        """ Return list of widget's [width, height, x, y]
            Called for both parent window and child windows

        stackoverflow: https://stackoverflow.com/a/77503326/6929343 """
        widget.update_idletasks()  # 2024-03-29 tested & confirm needed
        geometry_info = widget.geometry()
        # re search in "<WIDTH> x <HEIGHT> + <X> + <Y>" string (no spaces or <>)
        position_info = re.split('[x+]', geometry_info)
        # https://stackoverflow.com/a/50716478/6929343
        return map(int, position_info)


# ==============================================================================
#
#       ChildWindows class - Keep children on top of parent and move as group.
#
# ==============================================================================
class ChildWindows:
    """ Called from mserve.py for delayed textbox (dtb) or DictTreeview class
        below.

        Set focus in for self.toplevel to lift the child window(s)
        When self.toplevel is dragged, so are the child window.

        window.winfo_xxx see: https://wiki.tcl-lang.org/page/winfo%28%29

    """
    def __init__(self, toplevel, auto_raise=True):

        self.toplevel = toplevel  # Parent window
        self.window = {}  # Child Window {key, widget, x, y, w, h
        self.window_list = []  # list of window dictionaries

        self.who = "toolkit.py ChildWindows()."  # For debug messages

        ''' Controls to drag child window of toplevel '''
        # list of [width, height, x, y] returned by self.geometry(window)
        self.curr_geom = [0, 0, 0, 0]  # Geometry when drag_window called
        self.last_geom = [0, 0, 0, 0]  # Geometry when drag_window last called
        self.move_geom = [0, 0, 0, 0]  # Difference between curr and last
        self.toplevel.bind("<Configure>", self.drag_window)
        if auto_raise:
            self.toplevel.bind("<FocusIn>", self.raise_children)

        ''' Event log '''
        self.init_time = time.time()
        self.mec = 0  # move children event count
        self.rec = 0  # raise children event count
        # times from init_time. Printed to three decimal places
        self.mit_st = 0.0  # MOVE start time.time() - self.init_time
        self.mit_en = 0.0
        self.mit_el = 0.0  # elapsed milliseconds
        self.rit_st = 0.0  # RAISE start time.time() - self.init_time
        self.rit_en = 0.0  # Raise end time
        self.rit_el = 0.0  # Raise elapsed time

        self.last_mit_st = 0.0
        self.last_rit_st = 0.0



        ''' Event log - one record for start, one record for end. '''
        self.event_log = []
        # Tuple (Event type, Event Count, Start IT, End IT, Elapsed MS)
        #   Event type = "M" or "R"

    def get_it(self):
        """ Get Initial Time Offset: time.time() - self.init_time """
        return time.time() - self.init_time

    def get_el(self, start):
        """ Get End Time and Calculated Elapsed time """
        end = self.get_it()
        return end, end - start

    def log_it(self, et, ec, start):
        """ Log start time """
        tup = (et, ec, start, 0.0, 0.0)
        self.event_log.append(tup)

    def log_el(self, et, ec, es, ee, el):
        """ Log ee time & sanity check """
        _who = self.who + "log_el():"
        tup = (et, ec, es, ee, el)
        self.event_log.append(tup)

        # Sanity check
        for lt, lc, ls, le, lel in reversed(self.event_log):
            if et != lt or ec != lc:
                continue
            if es != ls:
                print("\n" + _who, "et:", et, "ec:", ec,
                      "es times differ:", self.fit(es), self.fit(ls))
            return

        print("\n" + _who, "et:", et, "ec:", ec,
              "Log start not found! es:", self.fit(es), "ee", self.fit(ee),
              "el:", self.fel(el))

    def prt_log(self):
        """ Print Log """
        _who = self.who + "prt_log():"
        cit = time.time() - self.init_time
        print("\n" + _who, "Log closed after:", self.fit(cit), "seconds.")
        print("Event (R=Raise Window, M=Move Window), Event Count, Start sec")
        print(" "*5, "Start sec  End sec  Elapsed ms")

        last_start = 0.0
        for lt, lc, ls, le, lel in self.event_log:
            if ls == last_start:  # suppress duplicated start time
                print(" "*15, self.fit(le).rjust(7), self.fel(lel).rjust(6))
            else:
                print(lt, str(lc).rjust(3), self.fit(ls).rjust(7),
                      self.fit(le).rjust(7), self.fel(lel).rjust(6))  #
            last_start = ls

    @staticmethod
    def fit(it):
        """ Format Initial Time Offset to 3 decimals """
        if it:
            return "%.3f" % round(it, 3)
        else:
            return "     "

    @staticmethod
    def fel(it):
        """ Format Elapsed Initial Time Offset in milliseconds to 2 decimal """
        if it:
            it = it * 1000.
            return "%.2f" % round(it, 2)
        else:
            return "    "

    # DOWN TO BUSINESS
    def raise_children(self, *_args):
        """ Focus in on parent. Focus in and lift the children up in the
            order they were registered.
        """
        if not len(self.window_list):
            return
        _who = self.who + "raise_children():"
        self.rec += 1  # raise event count
        self.rit_st = self.get_it()
        self.log_it("R", self.rec, self.rit_st)
        for win_dict in self.window_list:
            if self.check_candidacy(win_dict):
                win_dict['widget'].lift()
                win_dict['widget'].focus_force()
        self.rit_en, self.rit_el = self.get_el(self.rit_st)
        self.log_el("R", self.rec, self.rit_st, self.rit_en, self.rit_el)

    def move_children(self, x_off, y_off):
        """ Focus in on parent. Focus in and lift the children up in the
            order they were registered.

            2024-04-02 - As window dragged down to left, child raises up to left.
        """
        if not len(self.window_list):
            return
        _who = self.who + "move_children():"
        self.mec += 1  # raise event count
        self.mit_st = self.get_it()
        self.log_it("M", self.mec, self.mit_st)
        if True is False:
            print("\n" + _who, " | x_off:", x_off, " | y_off:", y_off)

        for win_dict in self.window_list:
            if self.check_candidacy(win_dict):
                _w, _h, x, y = self.geometry(win_dict['widget'])
                new_x = x + x_off
                new_y = y + y_off
                geom = "+" + str(new_x) + "+" + str(new_y)
                win_dict['widget'].geometry(geom)

        self.mit_en, self.mit_el = self.get_el(self.mit_st)
        self.log_el("M", self.mec, self.mit_st, self.mit_en, self.mit_el)

    def check_candidacy(self, win_dict):
        """ Test if 50% of a window lays inside parent toplevel

            :param win_dict: dictionary
        """
        _who = self.who + "check_candidacy():"
        w, h, x, y = self.geometry(win_dict['widget'])
        if True is False:  # Too much noise with spam prints
            print("\n" + _who, " | key:", win_dict['key'],
                  " | widget:", win_dict['widget'],
                  "\n\t\t | x:", x, " | y:", y, " | w:", w, " | h:", h)
        return True

    def drag_window(self, _event):
        """ Defined in __init__ with:
                self.key.bind("<Configure>", drag_window)
        """
        _who = self.who + "drag_window():"
        self.curr_geom = self.geometry(self.toplevel)  # window's [wid, hgt, x, y]
        if not self.last_geom[3]:  # Is last window height impossibly zero?
            self.last_geom = copy.deepcopy(self.curr_geom)  # last time not init

        # Leave now if geometry unchanged from last time
        if self.curr_geom == self.last_geom:
            return  # drag_window called with window.update() & no changes

        # How much has window moved or resized?
        self.move_geom = [c - l for c, l in zip(self.curr_geom, self.last_geom)]

        # Move and raise children if 50% inside parent window
        self.move_children(self.move_geom[2], self.move_geom[3])
        self.raise_children()  # NOTE: move before 50% test of raising children

        # Save for comparison next time
        self.last_geom = copy.deepcopy(self.curr_geom)

        # Uncomment print commands for debugging
        _w, _h, _x, _y = self.curr_geom  # shorthand for printing current
        _wm, _hm, _xm, _ym = self.move_geom  # shorthand for moved amounts
        #print(_who, "| x:", _x, " | y:", _y, " | w:", _w, " | h:", _h)
        #print("\t| x moved:", _xm, "\t| y moved:", _ym,
        #      "\t| width change:", _wm, "\t| height change:", _hm)

        # NOTE _event.x, _event.x_root refer to mouse position not window position

    def register_child(self, key, widget):
        """ Called from mserve.py for delayed textbox (dtb) or
            toolkit.py for displaying mini-windows E.G. column details.

            Set focus in for self.key to lift the child window
            When self.key is dragged, so is the child window.
            Whilst child window is "None" do nothing.

            window.winfo_xxx see: https://wiki.tcl-lang.org/page/winfo%28%29

            :param key: 'dtb', 'column details', 'rename heading', etc.
            :param widget: msg_top, or create_window toplevel, etc.
        """
        _who = self.who + "register_child():"
        has_key = self.key_for_widget(widget)
        has_widget = self.widget_for_key(key)
        if has_key or has_widget:
            print("\n" + _who, "Window already registered.")
            print("\tkey:", key, "window:", widget)
            print("\t", self.window_list)

        w, h, x, y = self.geometry(widget)
        #print("\n" + _who, " | key:", key, " | widget:", widget,
        #      "\n\t\t | x:", x, " | y:", y, " | w:", w, " | h:", h)
        # Unordered dict so geometry order irrelevant
        win = {'key': key, 'widget': widget, 'x': x, 'y': y, 'w': w, 'h': h}
        self.window_list.append(win)  # order children born
        #print("self.window_list:", self.window_list)

    def unregister_child(self, widget):
        """ Called from mserve.py for delayed textbox (dtb) or
            here for displaying mini-windows E.G. column details.

            :param widget: dtb.msg_top, or self.key
        """
        if not len(self.window_list):
            return
        _who = self.who + "unregister_child():"
        #print("\n" + _who, "Searching for:", widget)
        #print(_who, "BEFORE self.window_list:", self.window_list)

        i = found = False
        for i, win in enumerate(self.window_list):
            if win['widget'] == widget:
                found = True
                break  # deleting index inside loop doesn't work

        if found:
            _deleted = self.window_list.pop(i)
            # Parent responsible for destroying child window.
        else:
            print("\n" + _who, " - Widget not found:", widget)

        #print(_who, "AFTER self.window_list:", self.window_list)
        #self.prt_log()

    def destroy_all(self, tt=None):
        """ When caller doesn't know the window widgets at close time """
        if not len(self.window_list):
            return

        _who = self.who + "destroy_all():"
        #print(_who, "self.window_list:", self.window_list)
        safe_list = []  # Can't iterate window_list and remove from it
        for win_dict in self.window_list:
            safe_list.append(win_dict['key'])
        for key in safe_list:
            self.destroy_by_key(key, tt)

        self.window_list = []  # Should be empty now

    def destroy_by_key(self, key, tt=None):
        """ When caller doesn't know the window widgets at close time """
        _who = self.who + "destroy_by_key():"

        window = self.widget_for_key(key)
        if window is None:
            print("\n" + _who, " - Key not found:", key)
            return False

        if tt:  # Close all tooltips under the window
            if tt.check(window):  # window may not have any tooltips
                tt.close(window)

        window.destroy()
        self.unregister_child(window)
        return True

    def key_for_widget(self, widget):
        """ When caller doesn't know the 'key' get it with window widget

            ONLY USED FOR A FEW MINUTES THEN OBSOLETE. Leave for now.

            :param widget: Window's TK widget identifier
        """
        if not len(self.window_list):
            return
        _who = self.who + "key_for_widget():"
        for win_dict in self.window_list:
            if win_dict['widget'] == widget:
                return win_dict['key']

        #print("No key for widget:", widget)

    def widget_for_key(self, key):
        """ When caller doesn't know the 'key' get it with window widget

            :param key: Child Window's key. E.G. "move column"
        """
        if not len(self.window_list):
            return
        _who = self.who + "widget_for_key():"
        for win_dict in self.window_list:
            if win_dict['key'] == key:
                return win_dict['widget']

        #print("No key for widget:", widget)

    @staticmethod
    def geometry(widget):
        """ Return list of widget's [width, height, x, y]
            Called for both parent window and child windows

        stackoverflow: https://stackoverflow.com/a/77503326/6929343 """
        widget.update_idletasks()  # 2024-03-29 tested & confirm needed
        geometry_info = widget.geometry()
        # re search in "<WIDTH> x <HEIGHT> + <X> + <Y>" string (no spaces or <>)
        position_info = re.split('[x+]', geometry_info)
        # https://stackoverflow.com/a/50716478/6929343
        return map(int, position_info)


# ==============================================================================
#
#       CustomScrolledText class - scrollable text with tag highlighting
#
# ==============================================================================
class CustomScrolledText(scrolledtext.ScrolledText):
    """ A text widget with a new method, highlight_pattern()

        REQUIRES:

            import tkinter.scrolledtext as scrolledtext  # Python 3
            import ScrolledText as scrolledtext  # Python 2


        EXAMPLE:
    
            text = CustomScrolledText()
            text.tag_config("red", foreground="#ff0000")
            text.highlight_pattern("this should be red", "red")
        
            The highlight_pattern method is a simplified python
            version of the tcl code at http://wiki.tcl.tk/3246
    """

    def __init__(self, *args, **kwargs):
        scrolledtext.ScrolledText.__init__(self, *args, **kwargs)

    def highlight_pattern(self, pattern, tag, start="1.0", end="end",
                          regexp=False, upper_and_lower=True):
        """ Apply the given tag to all text that matches the given pattern

        If 'regexp' is set to True, pattern will be treated as a regular
        expression according to Tcl regular expression syntax.
        """

        start = self.index(start)
        end = self.index(end)
        last_index = None
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)

        count = tk.IntVar()
        while True:
            index = self.search(pattern, "matchEnd", "searchLimit", count=count,
                                regexp=regexp, nocase=upper_and_lower)
            if index == "":
                break
            last_index = index
            # degenerate pattern which matches zero-length strings
            if count.get() == 0:
                break
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
            self.tag_add(tag, "matchStart", "matchEnd")

        return last_index

    def unhighlight_pattern(self, pattern, tag, start="1.0", end="end",
                            regexp=False):
        """ Remove the given tag to all text that matches the given pattern
        """

        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)

        count = tk.IntVar()
        while True:
            index = self.search(pattern, "matchEnd", "searchLimit",
                                count=count, regexp=regexp, nocase=True)
            if index == "":
                break
            # degenerate pattern which matches zero-length strings
            if count.get() == 0:
                break
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
            self.tag_remove(tag, "matchStart", "matchEnd")


# ==============================================================================
#
#       DictNotebook class - Data Dictionary Driven ttk.Notebook()
#
# ==============================================================================
class makeNotebook:
    """ Data Dictionary controlled notebook. """
    def __init__(self, notebook, listTabs, listFields, dictData,
                 tStyle=None, fStyle=None, bStyle=None, close=None, tt=None):

        self.notebook = notebook
        self.listTabs = listTabs  # Tuples List: (Tab Name, Tool Tip)
        self.listFields = listFields
        self.dictData = dictData
        self.tStyle = tStyle  # Notebook Tab style "TNotebook.Tab
        self.fStyle = fStyle  # Frame style "N.TFrame"
        self.bStyle = bStyle  # Button style "C.TButton"
        self.close = close  # Close callback
        self.tt = tt

        self.who = "toolkit.py DictNotebook()."  # For debug messages

        ''' Deep copy dictData to oldData and newData '''
        self.oldData = copy.deepcopy(self.dictData)
        self.newData = copy.deepcopy(self.dictData)

        self.original_value = None  # before anything was input into field
        self.value_error = False

        self.add_tabs()

    def add_tabs(self):
        """ Populate Notebook. """

        tab_no = 1  # 1's based tab number matching dictionary
        for name, tip in self.listTabs:

            ''' frame for Notebook tab '''
            frame = ttk.Frame(self.notebook, width=200, height=200, padding=[20, 20])
            # 2024-12-29 - tooltip spams screen moving between fields
            #self.tt_add(frame, tip, "ne")

            self.add_rows(frame, tab_no)  # Add label: Entry fields to frame

            close_btn = ttk.Button(frame, width=7, text="✘ Close",
                                   style=self.bStyle, command=self.close)
            close_btn.grid(row=100, column=1, columnspan=2, padx=10, pady=5,
                           sticky=tk.E)
            tt_text = "Close Preferences.\nAny changes made will be lost."
            self.tt_add(close_btn, tt_text, "ne", tool_type='button')

            self.notebook.add(frame, text=name, compound=tk.TOP)
            #     notebook.add(frame, style=tStyle, text=name, compound=tk.TOP)
            # TclError: unknown option "-style"
            tab_no += 1

        self.notebook.grid(row=0, column=0, padx=3, pady=3, sticky=tk.NSEW)
        self.notebook.update()
        self.notebook.enable_traversal()

    def add_rows(self, frm, tab):
        """ Add rows to Notebook frame """
        '''
        # (name, tab#, hide/ro/rw, input as, stored as, width, decimals, 
                 min, max, edit callback, tooltip text)
        '''
        _who = self.who + "add_rows():"
        row = 0
        for atts in self.listFields:
            if atts[1] != tab:
                continue  # tab number doesn't match search

            data = self.oldData.get(atts[0], None)
            if data is None:
                # If data dictionary doesn't exist for key, can't process
                # NOTE: GLO['SUDO_PASSWORD'] can also have value of None
                continue

            label = ttk.Label(frm, text=atts[0], font=g.FONT)
            label.grid(row=row, column=0, sticky=tk.W, padx=15, pady=10)
            self.tt_add(label, atts[10])

            if len(atts) != 11:
                print(_who, "Invalid number of atts[] list variables:", len(atts))
                print("atts[0] value:", atts[0])
                exit(0)

            self.add_var(tab, frm, row, atts, data)

            row += 1

    def add_var(self, tab_id, frm, row, atts, value):
        """ Add tk Variable to Notebook Tab's frame.
            Called from add_rows().
            Define 'entry' (tkk.Entry) an important widget in the Notebook.
        """
        _who = self.who + "add_rows(): add_var():"
        '''
        # (name, tab#, hide/ro/rw, input as, stored as, width, decimals, 
                 min, max, edit callback, tooltip text)
        # name: value
        '''

        entry_type = atts[2]  # 'hidden', 'read-only', 'read-write'
        input_type = atts[3]  # "string", "integer", "float", "time", "list"
        _store_type = atts[4]  # "string", "integer", "float", "time", "list"
        width = atts[5]
        _decimal = atts[6]
        _minimum = atts[7]
        _maximum = atts[8]
        _edit_cb = atts[9]
        tip_text = atts[10]

        sticky = tk.W
        if input_type == "string":
            var = tk.StringVar(value=value)
        elif input_type == "integer":
            var = tk.IntVar(value=value)
            #sticky = tk.E
        elif input_type == "float" or input_type == "time":
            var = tk.DoubleVar(value=value)
            #sticky = tk.E
        elif input_type == "boolean":
            str_value = "1" if value is True else "0"
            var = tk.BooleanVar(value=str_value)
        else:
            var = None  # for pycharm error
            print(_who, "invalid input_type:", input_type)
            exit()

        def validate():
            """ Validate var - Called when receiving focus and after changes """
            _who2 = _who + " validate():"
            _what = "'validate command' for: " + atts[0]
            #message.ShowInfo(frm, _who2, _what)
            #print(_what)

        def check_value():
            """ e is entry widget. Check within bounds and data type.
                Called from focusOut() inner function.
            """
            _who2 = _who + " check_value():"
            self.value_error = False
            try:
                new_value = var.get()
            except ValueError as e:
                title = \
                    "Edit Preferences Error - HomA"
                text = "Invalid value for: " + atts[0] + "\n\n" +\
                    str(e) + "\n"
                message.ShowInfo(frm, title, text, icon="error")
                return None

            if new_value == self.original_value:
                return new_value

            if input_type == "float":
                test = float(new_value)

            return None  # Error. Get variable again

        def focusIn(event):
            """ variable received focus """
            _who2 = _who + " focusIn():"
            _what = "<FocusIn> for: " + atts[0]
            #e = event.widget  # entry widget
            # Prevent entire text turning blue when painted and with tab key
            entry.selection_range(0, 0)
            entry.configure(font="-weight bold")
            try:
                self.original_value = var.get()
            except ValueError:
                pass  # Redoing after check_value

        def focusOut(event):
            """ variable lost focus """
            _who2 = _who + " focusOut():"
            _what = "<FocusOut> for: " + atts[0]
            #e = event.widget  # entry widget
            # Remove blue selection when leaving field
            entry.selection_range(0, 0)

            # 2024-12-30 - Getting double message
            if self.value_error:
                self.value_error = False
                # This fixes double message but after field is fixed,
                # an extra enter is required to leave the field.
                return

            # Check value within min, max and correct data type
            stored_value = check_value()
            if stored_value is None:
                self.notebook.select(tab_id - 1)  # if focus out by tab click
                entry.focus_set()  # If error, None is returned
                self.value_error = True
                return  # Don't repeat focusOut
            entry.configure(font="-weight normal")

        def trace_cb(*_args):
            """ variable received focus - Called with each keystroke ('w')"""
            _who2 = _who + " trace_cb():"
            _what = "'var.trace()' for: " + atts[0]

        state = tk.NORMAL if entry_type == "read-write" else tk.DISABLED
        entry = ttk.Entry(frm, textvariable=var, width=width, font=g.FONT,
                          #state=state, validate='all', validate command=validate)
                          state=state)
        entry.grid(row=row, column=1, sticky=sticky, padx=15, pady=10)
        self.tt_add(entry, tip_text, "nw")
        if row == 0:
            entry.focus_set()  # Required for first time load

        # Enter key goes to next field like the tab key would.
        entry.bind('<Return>', lambda x: self.notebook.event_generate('<Tab>'))
        # Number Keypad Enter key goes to next field like the tab key would.
        entry.bind('<KP_Enter>', lambda x: self.notebook.event_generate('<Tab>'))
        entry.bind("<FocusIn>", focusIn)  # set input field bold text
        entry.bind("<FocusOut>", focusOut)  # sanity check data entered

        if True is False:  # useless experimental functions kept around
            var.trace('w', trace_cb)  # Fake call to make pyCharm happy
            validate()  # Fake call to make pyCharm happy

    def tt_add(self, widget, tt_text, tt_anchor="nw", tool_type="label"):
        """ Add tooltip. Parent responsible for closing all tooltips
            before destroying Notebook widget.
        """
        if self.tt is None:
            return
        if tt_text is not None and tt_anchor is not None:
            self.tt.add_tip(widget, tt_text, tool_type=tool_type, anchor=tt_anchor)


# ==============================================================================
#
#       DictTreeview class - Define Data Dictionary Driven treeview
#
# ==============================================================================
class DictTreeview:
    """ Use list of column dictionaries to create treeview. List names passed
        are music_treeview, history_treeview, etc. Class instance is often
        called 'dd_view' (data dictionary driven view) by parent.

        2024-03-12 - Upgrade to use SQL configuration. Manage TK widget colors
        using history 'Type' of: cfg_play_top, cfg_sql_music, etc.

        2024-03-28 - ChildWindows() class to keep children on top and move when
        parent window dragged.
        
        Interim version:
            When 'columns=()' the displaycolumns will be autogenerated based on
            'tree_dict' parameter
    """
    def __init__(self, tree_dict, toplevel, master_frame, show='headings', 
                 columns=(), sbar_width=12, highlight_callback=None, colors=None,
                 sql_type="", name="", use_h_scroll=False, force_close=None,
                 tt=None, sql_config=True):

        self.tree_dict = tree_dict          # Data dictionary
        self.toplevel = toplevel
        self.show = show                    # 'tree' or 'headings'
        self.attached = OrderedDict()       # Rows attached, detached, skipped
        self.highlight_callback = highlight_callback
        self.colors = colors                # Dictionary colors, edges, etc.
        self.sql_type = sql_type            # E.G. "sql_music"
        self.cfg_name = "cfg_" + sql_type
        self.name = name                    # E.G. "SQL Music Table"
        self.force_close = force_close
        self.tt = tt                        # Tool tips

        self.cfg = sql.Config()             # SQL user configurations

        self.tree = None                    # tk.Treeview created here in master

        # ChildWindows() moves children with toplevel and keeps children on top.
        self.win_grp = ChildWindows(self.toplevel)
        self.who = "toolkit.py DictTreeview()."
        self.photo = None                   # To prevent garbage collection

        # Child Windows - xxx_is_active vars are in .close() and __init__
        self.rsd_top_is_active = None       # Row SQL details
        self.rmd_top_is_active = None       # Row Metadata Details
        self.hcd_top_is_active = None       # Header Column details
        self.hic_top_is_active = None       # Header insert column
        self.hdc_top_is_active = None       # Header delete column
        self.hmc_top_is_active = None       # Header change column order
        self.hrc_top_is_active = None       # Header rename column

        # 2024-03-27 last_row will be phased out. use tree.has_tag() instead.
        self.last_row = None                # Used for removing highlight bar
        # 2024-03-27 col_count will be phased out
        self.col_count = 20                 # Set<20 for debug printing

        # TEST font families - Move out of sql.py to new toolkit Fonts() class
        #self.cfg.show_fonts(self.toplevel)

        color_key = [self.cfg_name, 'sql_treeview', 'style', 'color']
        sbar_key = [self.cfg_name, 'sql_treeview', 'style', 'scroll']
        order_key = [self.cfg_name, 'sql_treeview', 'column', 'order']
        custom_key = [self.cfg_name, 'sql_treeview', 'dict_treeview', 'custom']

        if sql_config:  # bserve doesn't have TypeAction Index needed for Config()
            colors = self.cfg.get_cfg(color_key)
            sbar_width = self.cfg.get_cfg(sbar_key)['width']
            # Get SQl stored treeview 'displaycolumns' (order of columns)
            if len(columns) == 0:
                columns = self.cfg.get_cfg(order_key)
                select_dict_columns(columns, self.tree_dict)
                #print("AFTER column order:", get_dict_displaycolumns(self.tree_dict))
            # User custom column order, width and heading
            if self.cfg.has_disk_cfg(custom_key):
                self.tree_dict = self.cfg.get_cfg(custom_key)  # on disk, no default
                columns = get_dict_displaycolumns(self.tree_dict)

            self.columns = columns
            #print("AFTER sql_config:", self.columns)

        ''' Get displaycolumns if not passed & not in SQL config '''
        if len(columns) == 0:
            self.columns = self.get_dict_displaycolumns(self.tree_dict)
        else:
            self.columns = list(columns)
        displaycolumns = tuple(self.columns)
        #print("final displaycolumns:", displaycolumns)

        ''' Key fields may be hidden. Add as extra column for callback. '''
        for d in self.tree_dict:
            if d['select_order'] == 0 and d['key'] is True:
                # SQL Table Ids (Keys) are required for optional retrieving rows
                self.columns.append(d['column'])

        # 2024-03-12 - colors from sql configuration (sql.Config) need defaults
        # for colors not enhanced in bserve.py, encoding.py, etc.
        fg = "Black"  # "systemTextColor" https://stackoverflow.com/a/67213569/6929343
        bg = fbg = "WhiteSmoke"  # "systemTextBackgroundColor" HORRIBLY broken
        style_name = "Treeview"
        edge_color = None
        edge_px = None

        if colors:  # Were colors passed as a dictionary?
            fg = colors['foreground']
            bg = colors['background']
            style_name = colors['name']
            fbg = colors['fieldbackground']
            edge_color = colors['edge_color']
            edge_px = colors['edge_px']

        # Create a frame for the treeview and scrollbar(s).
        if edge_color and edge_px:
            # Treeview with edge (not to be confused with frame border)
            self.frame = tk.Frame(master_frame, relief='solid',
                                  highlightcolor=colors['edge_color'],
                                  highlightbackground=colors['edge_color'],
                                  highlightthickness=colors['edge_px'], bd=0)
        else:
            self.frame = tk.Frame(master_frame)  # No around treeview edge

        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.grid(sticky=tk.NSEW)


        ''' CheckboxTreeview List Box, Columns and Headings '''
        #self.tree = CheckboxTreeview(  # NOT USED - SAVE MEMORY AND LAG
        #    self.frame, select mode='none', columns=self.columns)
        self.tree = ttk.Treeview(
            self.frame, selectmode='none', columns=self.columns)
        self.tree['displaycolumns'] = displaycolumns

        # Set selected displaycolumns widths and headings text
        for d in self.tree_dict:
            if d['select_order'] > 0:
                self.tree.column(d['column'], anchor=d['anchor'], width=d['width'],
                                 minwidth=d['minwidth'], stretch=d['stretch'])
                self.tree.heading(d['column'], text=d['heading'])

        # Move show below column config as per:
        #   https://stackoverflow.com/a/67839537/6929343
        self.tree['show'] = self.show

        style = ttk.Style()
        # print('style.theme_names():', style.theme_names())
        # OUTPUT: style.theme_names(): ('clam', 'alt', 'default', 'classic')
        # Each window requires unique name for treeview style
        style.configure(style_name + ".Heading", font=(None, g.MED_FONT),
                        rowheight=int(g.MED_FONT * 2.2))
        self.tree.configure(style=style_name + ".Heading")

        row_height = int(g.MON_FONTSIZE * 2.2)
        style.configure(style_name, font=(None, g.MON_FONTSIZE),
                        rowheight=row_height, foreground=fg, background=bg,
                        fieldbackground=fbg)
        self.tree.configure(style=style_name)

        """ NOT USED - SAVE MEMORY AND LAG
        ''' Create images for checked, unchecked and tristate '''
        self.checkboxes = img.make_checkboxes(
            row_height - 8, 'black', 'white', 'DodgerBlue')  # SkyBlue3 not in Pillow
        self.tree.tag_configure("unchecked", image=self.checkboxes[0])
        self.tree.tag_configure("tristate", image=self.checkboxes[1])
        self.tree.tag_configure("checked", image=self.checkboxes[2])

        ''' Create images for open, close and empty '''
        width = row_height - 9
        self.triangles = []  # list to prevent Garbage Collection
        # TODO: If triangles created already, they are not remade so lost here!
        img.make_triangles(self.triangles, width, 'black', 'grey')
        """
        
        ''' Configure tag for row highlight '''
        self.tree.tag_configure('highlight', background='lightblue')
        self.tree.bind('<Motion>', self.highlight_row)
        self.tree.bind("<Leave>", self.leave)

        ''' Put on grid '''
        self.tree.grid(row=0, column=0, sticky=tk.NSEW)

        ''' Treeview Scrollbars '''
        # Create a vertical scrollbar linked to the frame.
        v_scroll = tk.Scrollbar(self.frame, orient=tk.VERTICAL,
                                width=sbar_width, command=self.tree.yview)
        v_scroll.grid(row=0, column=1, sticky=tk.NS)
        self.tree.configure(yscrollcommand=v_scroll.set)

        # Create a horizontal scrollbar linked to the frame.
        if use_h_scroll:
            h_scroll = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL,
                                    width=sbar_width, command=self.tree.xview)
            h_scroll.grid(row=1, column=0, sticky=tk.EW)
            self.tree.configure(xscrollcommand=h_scroll.set)

    def insert(self, parent_iid="", row=None, iid="", tags="unchecked"):
        """ Insert new row or update existing row in treeview.
            Formatting convention: integers "{:,}" and floats "{0:,.0f}"

            2024-04-03 - Review tags "unchecked" if they were gone that would
                imply the row item was not checked anyway.
        """
        who = self.who + 'insert():'  
        
        if row is None:
            print(who, "- SQL Dictionary row is required parameter")
            return

        if len(self.columns) == 0:
            print(who, "- len(self.columns) == 0")
            return

        values = []

        for col in self.columns:
            data_dict = get_dict_column(col, self.tree_dict)
            unmasked_value = row[data_dict['var_name']]

            # DEBUGGING - Print first 20 columns and first Table row
            self.col_count += 1
            if self.col_count < 20:
                if self.col_count == 1:
                    print('============ row ============')
                    print(row)
                print(self.col_count, '========= data_dict =========')
                print(data_dict)
            elif self.col_count == 20:
                print('column count reached:', self.col_count)

            # TODO: New format "MB" for Megabytes
            if unmasked_value is None:
                values.append("")
            elif data_dict['format'] == "MB":
                values.append(human_mb(unmasked_value))
            elif data_dict['format'] == "days":
                values.append(tmf.days(unmasked_value))
            elif data_dict['format'] == "date":
                # times are stored in epoch (seconds since January 1, 1970)
                # Tue Jun 25 10:09:52 2019
                #values.append(time.asctime(time.localtime(unmasked_value)))

                # s = strftime("%a, %d %b %Y %H:%M:%S + 1010", gmtime())
                # Tue, 25 Jun 2019 10:09:52 + 1010
                values.append(time.strftime("%a, %b %d %Y - %H:%M:%S",
                                            time.localtime(unmasked_value)))
            elif data_dict['format'] is not None:
                mask = data_dict['format']
                try:
                    values.append(mask.format(unmasked_value))
                except ValueError:
                    print('Invalid format:', data_dict['format'],
                          'var_name:', data_dict['var_name'],
                          'row_id:', row['Id'],)
                    values.append("ValueError:" + str(unmasked_value))
                except KeyError:
                    #values.append(unmasked_value)
                    # April 14, 2023 - All values are already string???
                    values.append("KeyError:" + str(unmasked_value))
                    # DEBUGGING - Print first 20 encounters
                    if self.col_count < 20:
                        print('========= KEY ERROR =========')
                        print('mask:', mask, 'unmasked_value:', unmasked_value)
            else:
                values.append(unmasked_value)  # String with no formatting

        try:
            # insert new row into treeview
            self.tree.insert(parent_iid, tk.END, iid=iid, values=values, tags=tags)
        except tk.TclError as _err:  # Item L001 already exists
            # update existing row into treeview
            print("err:", _err)  # 2024-04-03 print error msg but nothing so far
            self.tree.item(iid, values=values, tags=tags)

        ''' highlight row as mouse traverses across treeview '''
        self.tree.tag_bind(iid, '<Motion>', self.highlight_row)

    def close(self, *_args):
        """ Parent is closing toplevel containing the treeview.

            Compare self.tree_dict (list of column dictionaries) to
            Tk Treeview Column Values: displaycolumns & each column
            width.

            Common close for sql_music, sql_history and sql_location.
            Also for maintenance of locations and playlists.

            Compare default dictionary to current treeview columns to see
            if any changes to:
                'displaycolumns' column order
                'width' column width
                'heading' column heading text

        :return: 1 new custom view created, 2 existing custom view updated
        """
        self.win_grp.destroy_all()  # Unregister & destroy all child windows

        # Child Windows - xxx_is_active vars are in .close() and __init__
        self.rsd_top_is_active = None       # Row SQL Details
        self.rmd_top_is_active = None       # Row Metadata Details (SQL Music only)
        self.hcd_top_is_active = None       # Header Column details
        self.hic_top_is_active = None       # Header insert column
        self.hdc_top_is_active = None       # Header delete column
        self.hmc_top_is_active = None       # Header change column order
        self.hrc_top_is_active = None       # Header rename column

        # Deep copy starting list of column dictionaries
        dict_list = copy.deepcopy(self.tree_dict)

        # Apply new Tk displaycolumns (columns in order of appearance)
        displaycolumns = self.tree['displaycolumns']
        select_dict_columns(displaycolumns, dict_list)

        # Apply column widths and headings to new dict_list
        for column in displaycolumns:
            #attributes = self.tree.column(column)  # Original not current
            d = get_dict_column(column, dict_list)  # Pippim column attributes
            try:
                d['width'] = self.tree.column(column)['width']
                d['heading'] = self.tree.heading(column)['text']
            except tk.TclError:
                pass  # newly inserted column
            save_dict_column(column, dict_list, d)

        # Has list of dictionaries changed?
        ret = None
        for i, new_d in enumerate(dict_list):
            old_d = self.tree_dict[i]
            for j, k in zip(old_d.items(), new_d.items()):
                if j != k:
                    ret = True  # Column changes made
                    #print(j, k)

        if ret is None:
            return None  # No column or heading changes were made

        ''' Use SQL configuration for column order, widths and headings '''
        sql_key = [self.cfg_name, 'sql_treeview', 'dict_treeview', 'custom']
        ret = self.cfg.insert_update_cfg(sql_key, self.name, dict_list)
        return ret

    def pretty_column(self, title, column_name, x=None, y=None):
        """ Display pretty column details using Data Dictionary of clicked column.

        """

        top = None
        scrollbox = None  # custom scrolled text box w/pattern highlighting

        def close(*_args):
            """ Close window painted by this pretty_column() method """
            if not self.hcd_top_is_active:
                return
            scrollbox.unbind("<Button-1>")
            self.win_grp.unregister_child(top)
            self.hcd_top_is_active = False  # heading column details
            top.destroy()
            #top = None  # Cannot update variable from outer space

        if self.hcd_top_is_active:
            close()  # Close the last instance opened

        if x is None or y is None:
            # Should always be passed x,y coordinates but just in case
            print(self.who + "pretty_column(): coordinates not passed.")
            x = self.toplevel.winfo_x() + g.PANEL_HGT  # Use parent's top left position
            y = self.toplevel.winfo_y() + g.PANEL_HGT

        self.hcd_top_is_active = True  # heading column details
        top = self.make_common_top('column details', title, 640, 500, x, y)

        ''' Bind <Escape> to close window '''
        top.bind("<Escape>", close)
        top.protocol("WM_DELETE_WINDOW", close)

        ''' frame - Holds scrollable text entry '''
        frame = ttk.Frame(top, borderwidth=g.FRM_BRD_WID,
                          padding=(2, 2, 2, 2), relief=tk.RIDGE)
        frame.grid(column=0, row=0, sticky=tk.NSEW)
        ms_font = (None, g.MON_FONT)  # bs_font = bserve, ms_font = mserve

        close_btn = tk.Button(
            frame, width=g.BTN_WID, text="✘ Close", command=close)
        close_btn.grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)

        scrollbox = CustomScrolledText(
            frame, state="normal", font=ms_font, borderwidth=15, relief=tk.FLAT)
        scroll_defaults(scrollbox)  # Default tab stops are too wide
        scrollbox.config(tabs=("2m", "60m", "80m"))  # "Nicer" tab stops
        scrollbox.grid(row=0, column=0, padx=3, pady=3, sticky=tk.NSEW)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)  # 2024-07-13 - Was column 1

        column_dict = get_dict_column(column_name, self.tree_dict)
        pretty_column = sql.PrettyTreeHeading(column_dict)
        #pretty_column.scrollbox = scrollbox
        #sql.tkinter_display(pretty_column)  # Populate scrollbox
        sql.pretty_display(pretty_column, scrollbox)  # Populate scrollbox

    def pretty_sql_row(self, search, pretty_row, x=None, y=None):
        """ Display pretty SQL Row details using Data Dictionary of clicked row.

            Before calling:
                Create pretty = sql.PrettyMusic(), sql.PrettyHistory(), etc.

        """

        top = None
        scrollbox = None  # custom scrolled text box w/pattern highlighting

        def close(*_args):
            """ Close window painted by this pretty_sql_row() method """
            if not self.rsd_top_is_active:
                return
            scrollbox.unbind("<Button-1>")
            self.win_grp.unregister_child(top)
            self.rsd_top_is_active = False  # heading column details
            top.destroy()
            #top = None  # Cannot update variable from outer space

        if self.rsd_top_is_active:
            close()  # Close the last instance opened

        if not x or not y:
            # Should always be passed x,y coordinates but just in case
            print(self.who + "pretty_sql_row(): coordinates not passed.",
                  "x:", x, "y:", y)
            x = self.toplevel.winfo_x() + g.PANEL_HGT  # Use parent's top left position
            y = self.toplevel.winfo_y() + g.PANEL_HGT

        self.rsd_top_is_active = True  # Row SQL Details
        title = None
        try:
            title = pretty_row.dict['Title']  # Get song title
        except KeyError:
            try:
                title = pretty_row.dict['Master Source Code']  # Get History column
            except KeyError:
                try:
                    title = pretty_row.dict['Name']  # Get Location Name
                except KeyError:
                    print("unable to locate key 'Title', 'Source Master' or",
                          "'Name' in SQL TABLE Music/History/Location")
                    print(pretty_row.dict)

        if title is None:
            title = "Unknown Row Title"  # Metadata hasn't been initialized

        top = self.make_common_top('sql row details', title, 1000, 750, x, y)

        ''' Bind <Escape> to close window '''
        top.bind("<Escape>", close)
        top.protocol("WM_DELETE_WINDOW", close)

        ''' frame - Holds scrollable text entry and close button '''
        frame = ttk.Frame(top, borderwidth=g.FRM_BRD_WID,
                          padding=(2, 2, 2, 2), relief=tk.RIDGE)
        frame.grid(column=0, row=0, sticky=tk.NSEW)
        ms_font = (None, g.MON_FONT)  # bs_font = bserve, ms_font = mserve

        close_btn = tk.Button(
            frame, width=g.BTN_WID, text="✘ Close", command=close)
        close_btn.grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)
        
        ''' custom scrolled text box with pattern highlighting '''
        scrollbox = CustomScrolledText(
            frame, state="normal", font=ms_font, borderwidth=15, relief=tk.FLAT)
        scroll_defaults(scrollbox)
        scrollbox.grid(row=0, column=0, padx=3, pady=3, sticky=tk.NSEW)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        #pretty_row.scrollbox = scrollbox  # Needed for old version only
        pretty_row.search = search  # To highlight Search Words
        #sql.tkinter_display(pretty_row)  # Populate scrollbox old version

        sql.pretty_display(pretty_row, scrollbox)  # 2024-06-09 - NEW version
        # 2024-06-29 - sql.pretty_display is upgrade to sql.tkinter_display

    def pretty_meta_row(self, FileControl, os_filename, info, x=None, y=None):
        """ Display pretty file metadata details using Data Dictionary of clicked row.
        """

        top = None
        scrollbox = None  # custom scrolled text box w/pattern highlighting

        def close(*_args):
            """ Close window painted by this pretty_meta_row() method """
            if not self.rmd_top_is_active:
                return
            scrollbox.unbind("<Button-1>")
            self.win_grp.unregister_child(top)
            self.rmd_top_is_active = False  # heading column details
            top.destroy()
            #top = None  # Cannot update variable from outer space

        if self.rmd_top_is_active:
            close()  # Close the last instance opened

        if not x or not y:
            # Should always be passed x,y coordinates but just in case
            print(self.who + "pretty_meta_row(): coordinates not passed.",
                  "x:", x, "y:", y)
            x = self.toplevel.winfo_x() + g.PANEL_HGT  # Use parent's top left position
            y = self.toplevel.winfo_y() + g.PANEL_HGT

        self.rmd_top_is_active = True  # Row SQL Details

        ''' File Control to get metadata loaded. '''
        view_ctl = FileControl(top, info)
        view_ctl.new(os_filename)  # Declaring new file populates metadata
        pretty_row = sql.PrettyMeta(view_ctl.metadata)

        title = pretty_row.dict.get('TITLE', "Unknown Song Title")  # Get song title
        top = self.make_common_top('row metadata details', title, 1350, 750, x, y)

        ''' Bind <Escape> to close window '''
        top.bind("<Escape>", close)
        top.protocol("WM_DELETE_WINDOW", close)

        ''' frame - Holds scrollable text entry '''
        frame = ttk.Frame(top, borderwidth=g.FRM_BRD_WID,
                          padding=(2, 2, 2, 2), relief=tk.RIDGE)
        frame.grid(column=0, row=0, sticky=tk.NSEW)
        ms_font = (None, g.MON_FONT)  # bs_font = bserve, ms_font = mserve

        ''' Artwork '''
        sample_art = img.make_image("No Artwork")
        sample_resized_art = sample_art.resize(
            (200, 200), Image.ANTIALIAS)
        self.photo = ImageTk.PhotoImage(sample_resized_art)
        sample_art_label = tk.Label(frame, image=self.photo,
                                    font=g.FONT)
        sample_art_label.grid(row=0, column=0, sticky=tk.EW)

        artwork, resized_art, original_art = \
            view_ctl.get_artwork(200, 200)
        view_ctl.close()

        if artwork is not None:
            self.photo = artwork
            sample_art_label.configure(image=self.photo)
            pass

        ''' custom scrolled text box with pattern highlighting '''
        scrollbox = CustomScrolledText(
            frame, state="normal", font=ms_font, borderwidth=15, relief=tk.FLAT)
        scroll_defaults(scrollbox)
        scrollbox.grid(row=1, column=0, padx=3, pady=3, sticky=tk.NSEW)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        #pretty_row.scrollbox = scrollbox
        #sql.tkinter_display(pretty_row)  # Populate scrollbox
        sql.pretty_display(pretty_row, scrollbox)  # Populate scrollbox


    def rename_column(self, column_name, x, y):
        """ Called from mserve.py view_sql_button_3() -> view_sql_heading_menu()

            Prompt for column to rename (defaults to current column) from view.
            Prompt for new name.
            
            After apply, close all child windows of dd_view.

            :param column_name: tkinter column name from displaycolumns.
            :param x: x position 24 pixels left of mouse pointer.
            :param y: y position 24 pixels below mouse pointer.
        """
        if self.hrc_top_is_active:
            return

        self.hrc_top_is_active = True
        top = self.make_common_top(
            'rename column', 'Rename column heading', 680, 390, x, y)

        last_heading = []  # pycharm likes definition higher up
        column_dict, combo_list, column_list, heading_list, ndx = \
            self.make_common_data(column_name)
        last_heading.append(column_dict['heading'])  # Pipe to/from combo_update

        def combo_update(*_args):
            """ New column selected.
                Remove previous highlight and apply new highlight.
            """
            # Must rebuild heading_list
            new_heading = heading_list[combo_list.index(combo_col_var.get())]
            self.update_common_bottom(
                scrollbox, heading_list, last_heading[0], new_heading)
            last_heading[0] = new_heading
            entry_text.set(new_heading)

        def entry_update(*_args):
            """ New column selected.
                Remove previous highlight and apply new highlight.
            """
            new_heading = entry_text.get()
            heading_list[combo_list.index(combo_col_var.get())] = new_heading
            self.update_common_bottom(
                scrollbox, heading_list, last_heading[0], new_heading)
            last_heading[0] = new_heading

        def close(*_args):
            """ close the window """
            if not self.hrc_top_is_active:
                return

            self.win_grp.unregister_child(top)
            # self.tt.close(hrc_top)  # Close tooltips (There aren't any yet)
            self.hrc_top_is_active = False
            top.destroy()

        def apply_rename(*_args):
            """ Delete current column from treeview. """
            if not self.hrc_top_is_active:
                return

            position = combo_list.index(combo_col_var.get())
            column = self.tree['displaycolumns'][position]
            new_heading = heading_list[position]
            self.tree.heading(column, text=new_heading)

            close()  # Close our window & save changes to self.dict_tree
            self.close_common_windows()  # Other common windows must close

        ''' frame - Holds combox, spinbox, custom scrolledtext and buttons '''
        # Rows: 10 Combobox, 20 Spinbox, 30/50 separators, 40 displaycolumns
        # Row 60 Buttons - Apply & Cancel (plus callback for combobox update)

        # Combobox selects which column to move/insert/delete/rename
        frame, combo_col, combo_col_var = self.make_common_frame(
            top, 'rename', combo_list, ndx)

        text = "New heading:"
        tk.Label(frame, text=text, bg="WhiteSmoke", pady=20).\
            grid(column=0, row=20, sticky=tk.W)

        entry_text = tk.StringVar()
        entry = tk.Entry(frame, textvariable=entry_text)  # self.search_text
        entry.grid(column=1, row=20, sticky=tk.W)
        entry_text.set(heading_list[ndx])
        entry.focus_set()
        entry_text.trace('w', entry_update)  # realtime changes to text
        entry.bind('<Return>', apply_rename)

        scrollbox = self.make_common_bottom(
            top, frame, combo_col, combo_update, apply_rename, 'Rename', close)

        combo_update()  # Set initial values displaycolumns scrolled textbox
        top.update_idletasks()

    def insert_column(self, column_name, x, y):
        """ Called from mserve.py view_sql_button_3() -> view_sql_heading_menu()

            Display combobox of unselected columns to pick from.

            Show current column and prompt where to insert.

            Call self.force_close(restart=True) to close all windows
            and restart parent.
            
            :param column_name: tkinter column name from displaycolumns.
            :param x: x position 24 pixels left of mouse pointer.
            :param y: y position 24 pixels below mouse pointer.
        """
        if self.hic_top_is_active:
            return
        self.hic_top_is_active = True
        top = self.make_common_top(
            'insert column', 'Insert column into view', 665, 390, x, y)

        _who = self.who + "insert_column(): "

        column_dict, combo_list, column_list, heading_list, ndx = \
            self.make_common_data(column_name)
        # Throw away combo_list because it has selected (displaycolumns)
        unselected_list = []  # d['column'] list
        full_list = []  # Full dictionary list
        combo_list = []
        last_heading = []  # Need mutable list to pass between spin_update()

        # Find all unselected columns
        for d in self.tree_dict:
            if d['select_order'] == 0:
                unselected_list.append(d['column'])  # the keys
                combo_list.append(d['heading'] + " - (" + d['column'] + ")")
                full_list.append(d)

        if len(combo_list) == 0:
            print("\n" + _who + "Need message for empty unselected_list")
            self.close_common_windows()
            return

        last_heading.append(full_list[0]['heading'])  # mutable variable

        def spin_update(*_args):
            """ Spin buttons clicked or new column selected.
                Remove previous highlight and apply new highlight.
            """
            unselected_ndx = combo_list.index(combo_col_var.get())
            new_name = full_list[unselected_ndx]['heading']
            new_ndx = spin_pos_var.get() - 1

            disp_list = list(self.tree['displaycolumns'])  # Build from scratch
            disp_list.insert(new_ndx, new_name)

            # Rebuild Columns display custom scrolledtext w/patterns
            self.update_common_bottom(
                scrollbox, disp_list, last_heading[0], new_name, 'Green')
            # Mutable variable in local space
            last_heading[0] = new_name

        def close(*_args):
            """ close the window """
            if not self.hic_top_is_active:
                return
            self.win_grp.unregister_child(top)
            # self.tt.close(top)  # Close tooltips (There aren't any yet)
            self.hic_top_is_active = False
            top.destroy()

        def apply_insert():
            """ Apply combox boxes. """
            if not self.hic_top_is_active:
                return

            combo_col_new = combo_col.get()
            pos_new = spin_pos_var.get()

            new_ndx = combo_list.index(combo_col_new)
            new_column = unselected_list[new_ndx]  # No longer dictionaries

            save_cols = self.save_before_update()
            # New displaycolumns with inserted column
            displaycolumns = list(self.tree['displaycolumns'])
            displaycolumns.insert(pos_new-1, str(new_column))  # convert from unicode

            # Update treeview with new columns. These are reread by force_close()
            self.tree['columns'] = displaycolumns  # Destroys headings & sizes
            self.tree['displaycolumns'] = displaycolumns
            self.reapply_after_update(save_cols, 'add')

            close()  # Close our window
            self.force_close(restart=True)  # Close toplevel window

        ''' frame - Holds combox, spinbox, custom scrolledtext and buttons '''
        # Rows: 10 Combobox, 20 Spinbox, 30/50 separators, 40 displaycolumns
        # Row 60 Buttons - Apply & Cancel (plus callback for combobox update)

        # Combobox selects which column to move/insert/delete/rename
        frame, combo_col, combo_col_var = self.make_common_frame(
            top, 'insert', combo_list, 0)  # Select first entry to insert new

        # Spinbox to bump up/bump down selected column's order in treeview
        spin_pos, spin_pos_var = self.make_common_spinbox_pos(
            frame, len(heading_list)+1, spin_update, ndx+1)

        scrollbox = self.make_common_bottom(
            top, frame, combo_col, spin_update, apply_insert, 'Insert', close)

        spin_update()  # Set initial values displaycolumns scrolled textbox
        top.update_idletasks()
        combo_col.focus_set()
        combo_col.event_generate('<Down>')

    def delete_column(self, column_name, x, y):
        """ Called from mserve.py view_sql_button_3() -> view_sql_heading_menu()

            Right click (button-3) performed on tkinter column heading.

            Prompt for column to delete (default is the current column from view).

            Call self.force_close(restart=True) to close all windows
            and restart parent.

            :param column_name: tkinter column name from displaycolumns.
            :param x: x position 24 pixels left of mouse pointer.
            :param y: y position 24 pixels below mouse pointer.
        """
        if self.hdc_top_is_active:
            return

        if len(self.tree['displaycolumns']) < 2:
            print(self.who + "delete_column():",
                  "len(self.tree['displaycolumns']) < 2:")
            return

        self.hdc_top_is_active = True
        top = self.make_common_top(
            'delete column', 'Remove column from view', 680, 390, x, y)

        last_heading = []  # pycharm likes definition higher up
        column_dict, combo_list, column_list, heading_list, ndx = \
            self.make_common_data(column_name)
        last_heading.append(column_dict['heading'])  # Pipe to/from combo_update

        def combo_update(*_args):
            """ New column selected.
                Remove previous highlight and apply new highlight.
            """
            new_heading = heading_list[combo_list.index(combo_col_var.get())]
            self.update_common_bottom(
                scrollbox, heading_list, last_heading[0], new_heading, 'Red')
            last_heading[0] = new_heading

        def close(*_args):
            """ close the window """
            if not self.hdc_top_is_active:
                return

            self.win_grp.unregister_child(top)
            # self.tt.close(hdc_top)  # Close tooltips (There aren't any yet)
            self.hdc_top_is_active = False
            top.destroy()

        def apply_delete():
            """ Delete current column from treeview. """
            if not self.hdc_top_is_active:
                return

            # New displaycolumns after column removed
            displaycolumns = list(self.tree['displaycolumns'])
            position = combo_list.index(combo_col_var.get())
            displaycolumns.pop(position)

            # "self.tree['columns'] = " destroys attributes; save & reapply
            save_cols = self.save_before_update()
            self.tree['displaycolumns'] = displaycolumns
            self.tree['columns'] = displaycolumns
            self.reapply_after_update(save_cols, 'delete')

            close()  # Close our window
            self.force_close(restart=True)  # Close toplevel window

        ''' frame - Holds combox, spinbox, custom scrolledtext and buttons '''
        # Rows: 10 Combobox, 20 Spinbox, 30/50 separators, 40 displaycolumns
        # Row 60 Buttons - Apply & Cancel (plus callback for combobox update)

        # Combobox selects which column to move/insert/delete/rename
        frame, combo_col, combo_col_var = self.make_common_frame(
            top, 'remove', combo_list, ndx)

        text = "Some columns like 'Lyrics' are needed for search buttons."
        tk.Label(frame, text=text, bg="WhiteSmoke", pady=20).\
            grid(column=0, columnspan=2, row=20, sticky=tk.W)

        scrollbox = self.make_common_bottom(
            top, frame, combo_col, combo_update, apply_delete, 'Remove', close)

        combo_update()  # Set initial values displaycolumns scrolled textbox
        top.update_idletasks()

    def move_column(self, column_name, x, y):
        """ Called from mserve.py view_sql_button_3() -> view_sql_heading_menu()

            Right click (button-3) performed on tkinter column heading.

            Display combobox of columns to pick from.
            Display spinbox to change order
            Dynamically show column order with each spinbox action.

            Apply changes to self.tree['displaycolumns'] and set tree_dict
            
            After apply, close all child windows of dd_view.

            :param column_name: tkinter column name from displaycolumns.
            :param x: x position 24 pixels left of mouse pointer.
            :param y: y position 24 pixels below mouse pointer.
        """
        if self.hmc_top_is_active:
            return
        self.hmc_top_is_active = True
        top = self.make_common_top(
            'move column', 'Shift column position', 650, 390, x, y)
        column_dict, combo_list, column_list, heading_list, ndx = \
            self.make_common_data(column_name)

        def spin_update(*_args):
            """ Spin buttons clicked or new column selected.
                Remove previous highlight and apply new highlight.
            """
            # Get old column index
            #combo_col_new = combo_col.get()  # establish index in list
            old_ndx = combo_list.index(combo_col.get())
            heading = heading_list[old_ndx]  # pattern to unhighlight

            # get new column order (position) and set new index
            #spin_new = spin_pos_var.get()
            new_ndx = spin_pos_var.get() - 1

            # For Insert Column / Move Column
            # Rearrange lists with new displaycolumns order
            # credit: https://stackoverflow.com/a/33933500/6929343
            combo_list.insert(new_ndx, combo_list.pop(old_ndx))
            column_list.insert(new_ndx, column_list.pop(old_ndx))
            heading_list.insert(new_ndx, heading_list.pop(old_ndx))
            combo_col['values'] = combo_list

            # Rebuild Columns display custom scrolledtext with standard colors
            self.update_common_bottom(
                scrollbox, heading_list, heading, heading_list[new_ndx])

        def combo_update(*_args):
            """ New column to move selected from combo box. Set spin position. """
            combo_col_new = combo_col_var.get()  # establish index in list
            new_ndx = combo_list.index(combo_col_new)
            spin_pos_var.set(new_ndx+1)
            spin_update()  # Highlight new column selected in columns display

        def close(*_args):
            """ close the window """
            if not self.hmc_top_is_active:
                return
            combo_col.unbind('<<ComboboxSelected>>')
            self.win_grp.unregister_child(top)
            self.hmc_top_is_active = False
            top.destroy()

        def apply_move():
            """ Apply changes and close child window (but not toplevel). """
            if not self.hmc_top_is_active:
                return

            # Update treeview with displaycolumns.
            self.tree['displaycolumns'] = column_list
            close()  # Close our window
            self.close_common_windows()  # Other common windows must close

        ''' frame - Holds combox, spinbox, custom scrolledtext and buttons '''
        # Rows: 10 Combobox, 20 Spinbox, 30/50 separators, 40 displaycolumns
        # Row 60 Buttons - Apply & Cancel (plus callback for combobox update)

        # Combobox selects which column to move/insert/delete/rename
        frame, combo_col, combo_col_var = self.make_common_frame(
            top, 'move', combo_list, ndx)

        # Spinbox to bump up/bump down selected column's order in treeview
        spin_pos, spin_pos_var = self.make_common_spinbox_pos(
            frame, len(heading_list), spin_update, ndx+1)

        scrollbox = self.make_common_bottom(
            top, frame, combo_col, combo_update, apply_move, 'Move', close)

        spin_update()  # Set initial values displaycolumns scrolled textbox
        top.update_idletasks()

    def make_common_top(self, key, method, w, h, x, y):
        """ Make toplevel for insert/remove/move/rename columns """

        top = tk.Toplevel()
        top.geometry('%dx%d+%d+%d' % (w, h, x, y))
        top.minsize(width=g.BTN_WID * 10, height=g.PANEL_HGT * 4)
        title = self.name + " - " + method + " - mserve"
        top.title(title)

        top.columnconfigure(0, weight=1)
        top.rowconfigure(0, weight=1)
        top.configure(background="WhiteSmoke")  # Future user configuration
        self.win_grp.register_child(key, top)  # Lifting & moving with parent

        return top

    def make_common_data(self, column_name):
        """ Make data lists for insert/remove/move/rename columns """

        # column_dict with d['column'], d['heading'], d['width'], etc.
        column_dict = get_dict_column(column_name, self.tree_dict)

        # Three synchronized lists
        combo_list = []  # list of "'Heading' - (column name)"
        column_list = []  # list of column names dictionary['column']
        heading_list = []  # list of dictionary['Heading']

        # Build lists in displaycolumns order
        for i, column in enumerate(self.tree['displaycolumns']):
            d = get_dict_column(column, self.tree_dict)
            combo_list.append(d['heading'] + " - (" + column + ")")
            column_list.append(d['column'])  # the keys (column_name)
            heading_list.append(d['heading'])  # the display names ('Heading')

        ndx = column_list.index(column_name)
        if ndx is None:
            print("Could not find column_name:", column_name, "in column_list below:")
            print(column_list)
            ndx = 0

        return column_dict, combo_list, column_list, heading_list, ndx

    @staticmethod
    def make_common_frame(top, action, combo_list, ndx):
        """ Make toplevel for insert/remove/move/rename columns """

        # Rows: 10 Combobox, 20 Spinbox, 30/50 separators, 40 displaycolumns
        # Row 60 Buttons - Apply & Cancel (plus callback for combobox update)

        # FUTURE: User configuration for colors
        frame = tk.Frame(top, borderwidth=18,
                         relief=tk.FLAT, bg="WhiteSmoke")
        frame.grid(column=0, row=0, sticky=tk.NSEW)

        # Combobox selects which column to move/insert/delete/rename
        tk.Label(frame, text="Column to " + action + ":", bg="WhiteSmoke",
                 padx=10, pady=10).grid(column=0, row=10, sticky=tk.W)
        combo_col_var = tk.StringVar()
        combo_col = ttk.Combobox(frame, textvariable=combo_col_var,
                                 state='readonly', width=30)
        combo_col.grid(column=1, row=10)
        combo_col['values'] = combo_list  # 'Heading' - (column name) ...
        combo_col.current(ndx)  # Current treeview column default entry

        return frame, combo_col, combo_col_var

    @staticmethod
    def make_common_spinbox_pos(frame, to, callback, initial_value):
        """ Make toplevel for insert/remove/move/rename columns """
        # spin_pos, spin_pos_var = make_common_spinbox_pos(
        #    frame1, to, callback, initial_value)

        # Rows: 10 Combobox, 20 Spinbox, 30/50 separators, 40 displaycolumns
        # Row 60 Buttons - Apply & Cancel (plus callback for combobox update)

        # Spinbox to bump up/bump down selected column's order in treeview
        # Spinbox for Move Column and Insert Column only.

        # Delete and Rename have NO Spinbox. In that place instead:
        #   - Delete has warning about removing lyrics.
        #   - Rename prompts for the new 'Heading'

        tk.Label(frame, text="Column position:", bg="WhiteSmoke", padx=10, pady=10). \
            grid(column=0, row=20, sticky=tk.W)
        spin_pos_var = tk.IntVar(value=initial_value)
        spin_pos = tk.Spinbox(
            frame, from_=1, to=to, increment=-1, width=3,
            state='readonly', textvariable=spin_pos_var, command=callback)
        spin_pos.grid(column=1, row=20, sticky=tk.W)

        return spin_pos, spin_pos_var

    @staticmethod
    def make_common_bottom(top, frame, combo_col, combo_func,
                           apply_func, apply_text, close_func):
        """ Make bottom for insert/remove/move/rename columns """
        # scrollbox = make_common_bottom(
        #    top, frame, combo_col, combo_func, apply_func, close_func)
        
        # Rows: 10 Combobox, 20 Spinbox, 30/50 separators, 40 displaycolumns
        # Row 60 Buttons - Apply & Cancel (plus callback for combobox update)

        # Separator around Columns display custom scrolled textbox
        ttk.Separator(frame, orient='horizontal').\
            grid(column=0, row=30, columnspan=2, sticky=tk.EW)
        frame.grid_rowconfigure(30, minsize=30)

        # Columns displayed in order with current column highlighted
        # Highlight in yellow Move, Insert, Delete and Rename
        tk.Label(frame, text="Columns displayed:", bg="WhiteSmoke", padx=10,
                 pady=10, anchor=tk.W).grid(column=0, row=40, sticky=tk.W)
        scrollbox = CustomScrolledText(
            frame, state="normal", font=(None, g.MON_FONT), borderwidth=10,
            pady=2, relief=tk.FLAT, wrap=tk.WORD)
        scrollbox.grid(row=40, column=1, padx=3, pady=3, sticky=tk.NSEW)
        tk.Grid.rowconfigure(frame, 40, weight=1)  # spinbox row expands
        tk.Grid.columnconfigure(frame, 1, weight=1)  # column 2 expands

        scrollbox.tag_config('Red', foreground='White', background='Red')
        scrollbox.tag_config('Gray', foreground='White', background='Gray')
        scrollbox.tag_config('Green', foreground='White', background='Green')
        scrollbox.tag_config('Yellow', background='Yellow')

        # Separator around Columns display custom scrolled textbox
        ttk.Separator(frame, orient='horizontal').\
            grid(column=0, row=50, columnspan=2, sticky=tk.EW)
        frame.grid_rowconfigure(50, minsize=30)

        # Buttons to apply or close
        # make_common_buttons(order_apply, close)
        button1 = tk.Button(frame, text=apply_text, pady=2, command=apply_func)
        button1.grid(column=0, row=60)
        button2 = tk.Button(frame, text="Cancel", pady=2, command=close_func)
        button2.grid(column=1, row=60)

        combo_col.bind('<<ComboboxSelected>>', combo_func)
        #spin_update()  # Set initial values in combobox and scrolled textbox

        ''' Bind <Escape> to close window '''
        top.bind("<Escape>", close_func)
        top.protocol("WM_DELETE_WINDOW", close_func)

        return scrollbox

    @staticmethod
    def update_common_bottom(scrollbox, names, old, new, high_tag=None, sep_tag=None):
        """ Update text for displaycolumns & highlight pattern """

        if high_tag is None:
            high_tag = 'Yellow'
        if sep_tag is None:
            sep_tag = 'Gray'

        scrollbox.configure(state="normal")
        scrollbox.unhighlight_pattern(old, high_tag)  # Remove old word highlighting
        scrollbox.unhighlight_pattern('|', sep_tag)  # not really necessary
        text = '| ' + ' | '.join(names) + ' |'
        scrollbox.delete("1.0", "end")
        scrollbox.insert("end", text)
        scrollbox.highlight_pattern(new, high_tag)
        scrollbox.highlight_pattern('|', sep_tag)
        scrollbox.configure(state="disabled")

    def save_before_update(self):
        """ Save column attributes and headings to restore later.
            Used for Insert Column and Remove Column """
        ls = []
        for column in self.tree['displaycolumns']:
            # 'minwidth': 99, 'width': 99, 'id': column, 'anchor': 'w', 'stretch': 1
            ds = self.tree.column(column)  # grab all. 'column' is labelled 'id'
            ds['heading'] = self.tree.heading(column)['text']
            ls.append(ds)
        return ls

    def reapply_after_update(self, ls, mode):
        """ Restore column headings and width saved earlier.
                ls['minwidth': 99, 'width': 99, 'id': COLUMN_NAME, 'anchor': 'w',
                   'stretch': 1 'heading': HEADING]
            Used for Insert Column and Remove Column.
            Tally tot_stretch and tot_width for massaging after insert.
        """
        # Apply saved column attributes and headings to new treeview
        tot_stretch = cnt_stretch = tot_all = add_ndx = add_width = 0
        for i, column in enumerate(self.tree['displaycolumns']):
            # https://stackoverflow.com/a/9980160/6929343
            lm = [ds for ds in ls if ds['id'] == column]
            if lm:  # Saved self.tree attributes before add/delete column
                ds = lm[0]  # List of matching dicts has one dict
                self.tree.column(column, width=ds['width'], anchor=ds['anchor'],
                                 stretch=ds['stretch'], minwidth=ds['minwidth'])
                self.tree.heading(column, text=ds['heading'])
                if ds['stretch'] == 1:  # stretchable columns get allocation
                    tot_stretch += ds['width']
                    cnt_stretch += 1
                tot_all += ds['width']  # Used when no columns stretchable
            elif mode == 'add':
                # Get new column attributes from Data Dictionary
                di = get_dict_column(column, self.tree_dict)
                self.tree.column(column, width=di['width'], anchor=di['anchor'],
                                 stretch=di['stretch'], minwidth=di['minwidth'])
                self.tree.heading(column, text=di['heading'])
                add_ndx = i
                add_width += di['width']
            else:
                print(self.who + "reapply_after_update(): mode != 'add'", mode)
                continue

        if mode == 'add':
            pass  # Proceed with column width reductions
        elif mode == 'delete':
            self.tree.update_idletasks()
            return  # Tkinter automatically widens columns to fill frame
        else:
            print(self.who + "reapply_after_update(): Bad 'mode' !!!", mode)
            return

        ''' reduce columns by inserted column width '''
        cnt_all = len(self.tree['displaycolumns']) - 1
        COL_SEP_WIDTH = 20  # Treeview column separator width (best guess)
        if cnt_stretch:
            adj_amt = add_width / cnt_stretch
            adj_rounding = add_width - (adj_amt * cnt_stretch) + COL_SEP_WIDTH
        else:
            adj_amt = tot_all / cnt_all
            adj_rounding = add_width - (adj_amt * cnt_all) + COL_SEP_WIDTH

        #print(self.who + "reapply_after_update(): tot_stretch:", tot_stretch,
        #       "cnt_stretch:", cnt_stretch, "tot_all:", tot_all, "cnt_all:", cnt_all)
        #print(" "*30, "add_ndx:", add_ndx, "add_width:", add_width,
        #      "adj_amt:", adj_amt, "adj_rounding:", adj_rounding)

        for i, column in enumerate(self.tree['displaycolumns']):
            if i == add_ndx:
                continue  # Added column isn't adjusted
            c = self.tree.column(column)
            if cnt_stretch and c['stretch'] == 0:
                continue  # Stretchable columns but not this one

            width = c['width'] - adj_amt - adj_rounding
            adj_rounding = 0  # Only the first column receives rounding amount
            self.tree.column(column, width=width)

        # After update, close is called to save tree to tree_dict disk image
        # Then restart SQL Table viewer with force_close(restart=True)
        self.tree.update_idletasks()

    def close_common_windows(self):
        """ Either Move or Rename column applied changes. Close all children """
        if self.hmc_top_is_active:
            self.win_grp.destroy_by_key('move column')
            self.hmc_top_is_active = False
        if self.hic_top_is_active:
            self.win_grp.destroy_by_key('insert column')
            self.hic_top_is_active = False
        if self.hdc_top_is_active:
            self.win_grp.destroy_by_key('delete column')
            self.hdc_top_is_active = False
        if self.hrc_top_is_active:
            self.win_grp.destroy_by_key('rename column')
            self.hrc_top_is_active = False

    def edit_column_dict(self, column_name):
        """ Called from mserve.py view_sql_button_3() -> view_sql_heading_menu()

            Right click (button-3) performed on tkinter column heading.

            Popup menu at mouse position with options:
                - 'Xxx' column details
                - Edit column (width, heading)
                - Change column order (you can drag in GNOME)
                - Remove column from view
                - Add new column to view
                - Change window colors

            :param column_name: tkinter column name from displaycolumns.
        """
        column_dict = get_dict_column(column_name, self.tree_dict)
        # Get real column width, heading, etc. from self.tree.column / .heading
        print("\ntoolkit.py DictTreeview.edit_column_dict() column_dict:")
        print(column_dict)

    def update_column(self, iid, search, value):
        """ Update Tkinter item's specific column with a new value
            Only used in bserve.py with self.bup_view instance.
        """

        # Get all column values
        values = self.tree.item(iid, "values")
        i = self.columns.index(search)
        values_l = list(values)
        values_l[i] = value
        self.tree.item(iid, values=values_l)
        if True is True:
            return True  # Delete code below after bserve.py tested

        # Loop through all columns in treeview
        for col in self.columns:
            # June 18, 2023 - No need to Loop through all columns in treeview, just go direct.
            # Get data dictionary for current column
            data_dict = get_dict_column(col, self.tree_dict)
            # Does data dictionary column name match search name?
            if data_dict['column'] != search:
                continue  # Try next element

            #print('values:', values)
            view_order = data_dict['select_order']
            if view_order < 1 or view_order > len(values):
                print('toolkit.py DictTree().update_column() search column error:',
                      search)
                print('    invalid view_order retrieved:', view_order,
                      'max:', len(values))
                print_dict_columns(self.tree_dict)
                return None

            values_l = list(values)
            values_l[view_order - 1] = value
            self.tree.item(iid, values=values_l)
            return True

        print('toolkit.py DictTreeview.update_column() search column not found:',
              search)
        print_dict_columns(self.tree_dict)
        print('values:', values)
        return None

    def highlight_row(self, event):
        """ Cursor moving over row highlights row in light blue """
        tree = event.widget
        item = tree.identify_row(event.y)
        tree.tk.call(tree, "tag", "remove", "highlight")
        tree.tk.call(tree, "tag", "add", "highlight", item)
        self.last_row = item

        if self.highlight_callback:
            self.highlight_callback(item)

    def leave(self, event):
        """ Cursor leaving row Un-highlight's the row """
        if self.last_row is not None:
            tree = event.widget
            tree.tk.call(self.tree, "tag", "remove", "highlight")
            self.last_row = None

    def column_value(self, values, search):
        """
            Gets value matching treeview column name from treeview row.
            Used in bserve.py to get message_id which may be hidden column.
            As of July 15, 2021 message_id is a key field in every view.

            :param values is treeview row of values
            :param search is string for data dictionary field name
            :returns matching value from passed values list

        """

        # Directly get index. Change other methods to do same way.
        i = self.columns.index(search)
        # Weird bug in LyricsScore for 10cc song The Things We Do For Love.
        # Appears after 'row_id' column dragged after 'lyrics' column
        if i > len(values) - 1:
            i = len(values) - 1
        return values[i]

    def change_column_format(self, new_format, search):
        """ For example history size is usually regular integer. Playlists
            repurposes for MB's.
            
            :param new_format: New format. E.G. "MB"
            :param search: column name, E.G. "size"
            :returns None
        """

        # No need to Loop through all columns in treeview, just go direct.
        data_dict = get_dict_column(search, self.tree_dict)
        if data_dict is None:
            print_trace()
            print("Bad search column:", search)
            return
        if data_dict['column'] == search:
            data_dict['format'] = new_format
            save_dict_column(search, self.tree_dict, data_dict)

    def print_tk_columns(self):
        """
            Print user modified column widths plus any column defaults.
            .column(cid, option=None, **kw)

            This method configures the appearance of the logical column
            specified by cid, which may be either a column index or a
            column identifier. To configure the icon column, use a cid
            value of '#0'.

            Each column in a Treeview widget has its own set of options
            from this table:
                anchor 	    The anchor that specifies where to position
                            the content of the column. The default value
                            is 'w'.
                id 	        The column name. This option is read-only and
                            set when the constructor is called.
                min width 	Minimum width of the column in pixels; the
                            default value is 20.
                stretch 	If this option is True, the column's width
                            will be adjusted when the widget is resized.
                            The default setting is 1.
                width 	    Initial width of the column in pixels; the
                            default is 200.

            If no option value or any other keyword argument is supplied,
            the method returns a dictionary of the column options for the
            specified column.

            To interrogate the current value of an option named X , use an
            argument option=X.

            To set one or more column options, you may pass keyword
            arguments using the option names shown above,
            e.g., anchor=tk.CENTER to center the column contents.
        """

        print("\ntoolkit.py - print_tk_columns()")
        # self.columns are in mserve, tk_columns are in Tkinter
        for col in self.columns:
            tk_columns = self.tree.column(col)
            print("tk_columns:", tk_columns)


# TODO: June 18, 2023 review moving these functions into class.
def select_dict_all(dict_list):
    """ Select all dictionary columns """
    for curr in range(1, len(dict_list)):
        for d in dict_list:
            d['select_order'] = curr


def unselect_dict_all(dict_list):
    """ Unselect all dictionary columns """
    for d in dict_list:
        d['select_order'] = 0


def select_dict_columns(columns, dict_list):
    """ Select columns in order.
        Returns nothing because dict_list is changed in place.

        :param  columns list in order of display. 
                It may be a tuple of column names for gmail message header.
        :param  dict_list is mutable list of dictionary fields. The
                "("select_order", 0)" field is changed from 0 to number 1 to last.

    """
    unselect_dict_all(dict_list)
    curr = 1

    for column in columns:
        for i, d in enumerate(dict_list):
            if d['column'] == column:
                d['select_order'] = curr
                dict_list[i] = d
                curr += 1
                break


def unselect_dict_columns(columns, dict_list):
    """ Unselect columns.
        Returns nothing because dict_list is changed in place.

        :param  columns list or tuple of column names to unselect
        :param  dict_list is list of dictionaries

    """
    unselect_dict_all(dict_list)

    # TODO: after removing a column rest must be renumbered !!!
    for column in columns:
        for i, d in enumerate(dict_list):
            if d['column'] == column:
                ''' June 15, 2023 - appears this never ever worked
                d['select_order'] = curr
                dict_list[i] = d
                curr += 1
                '''
                d['select_order'] = 0
                break


def get_dict_column(column, dict_list):
    """ Return data dictionary for column name """
    for d in dict_list:
        if d['column'] == column:
            return d
    return None


def get_dict_displaycolumns(dict_list):
    """ Return list of selected columns in order.
        :param  dict_list is mutable list of dictionary fields. The
                "("select_order", 0)" field is changed from 0 to number 1 to last.

    """
    columns = []
    for d in dict_list:
        if d['select_order'] == 0:
            continue  # Not selected
        name_off = d['select_order'] - 1
        while len(columns) - 1 < name_off:
            # Fill holes and new ending name with "Reserved" string
            columns.append("Reserved")
        columns[name_off] = d['column']  # Tk Column Name

    return columns


def save_dict_column(column, dict_list, new_dict):
    """ Update data dictionary for specific column name """
    for i, d in enumerate(dict_list):
        if d['column'] == column:
            dict_list[i] = new_dict
            return True

    return False


def print_dict_columns(dict_list):
    """ For debugging purposes.
         {"column": "snippet", "heading": "Snippet", "sql_table": "Header",
          "var_name": "snippet", "select_order": 0, "unselect_order": 9,
          "anchor": "wrap", "instance": str, "format": None, "width": 60,
          "minwidth": 10, "stretch": 1}

      OrderedDict([
        ("column", "row_id"), ("heading", "Row ID"), ("sql_table", "Music"),
        ("var_name", "Id"), ("select_order", 0), ("unselect_order", 1),
        ("key", False), ("anchor", "e"), ("instance", int), ("format", "{,,}"),
        ("width", 150), ("minwidth", 80), ("stretch", 0)]),  # 0=NO, 1=YES

    """
    print('\nDATA DICTIONARY\n==============================')
    ''' TODO: Print in selected order first, then unselected order '''
    for d in dict_list:
        print('\ncolumn    :', d['column'].ljust(15), ' | heading     :',
              d['heading'].ljust(17), ' | sql_table     :', d['sql_table'])
        print('  var_name:', d['var_name'].ljust(15), ' | select_order:',
              str(d['select_order']).ljust(17), ' | unselect_order:', d['unselect_order'])
        print('  anchor  :', d['anchor'].ljust(15), ' | instance    :',
              str(d['instance']).ljust(17), ' | format        :', d['format'])
        print('  width   :', str(d['width']).ljust(15), ' | minwidth    :',
              d['minwidth'], '  | stretch', d['stretch'],
              '\t| key           :', d['key'])


def human_mb(size, decimals=1, uom=" MB"):
    """ Change '99,999,999' bytes to '99.9 MB', etc.
        Called by mserve.py MusicTree() class and Playlists() class """
    divisor = float(1000 * 1000)
    converted = float(size) / divisor
    rounded = round(converted, decimals)
    rounded = '{:n}'.format(rounded)  # Test will locale work for float?
    return rounded + uom


def human_bytes(size, decimals=1, space=True):
    """ Return 127.38 MB, 3.12 GB, 876 KB, etc.
        Called by location.py Locations()

    Credit:
    https://unix.stackexchange.com/questions/44040/
    a-standard-tool-to-convert-a-byte-count-into-human-kib-mib-etc-like-du-ls1/
    259254#259254 """
    size = float(size)
    off = 0
    uom = ("Bytes", "KB", "MB", "GB", "TB", "EB", "PB", "YB", "ZB")
    while size > 999:
        off += 1
        size = size / 1000.0
        
    rounded = round(size, decimals)
    rounded = '{:n}'.format(rounded)
    rounded = rounded.rstrip("0")  # Remove trailing 0's
    rounded = rounded.rstrip(".")  # Remove trailing '.' if there
    pad = " " if space is True else ""
    return rounded + pad + uom[off]


def computer_bytes(size, decimals=False):
    """ Passed 127.38 MB, 12K, 15.1GB, 876 KB, etc.
        Returns float

        Credit: https://stackoverflow.com/a/5917250/6929343
    """
    _match = re.match(r'^\D*\.?\D+$', size, re.I)
    # Credit: https://stackoverflow.com/a/430102/6929343
    _match = re.match(r"([a-z]+)([0-9]+)", size, re.I)
    # https: // stackoverflow.com / a / 430296 / 6929343
    size = size.strip()  # attempt to get rid of leading null, no luck :(

    # 2024-01-02: Doesn't work
    results = re.split(r'^\D*\.?\D+$', size)
    print("Experimental results:", results)
    # Experimental results: ['4.0K\t2023-12-25 12:21\t total']

    if decimals:
        # 2024-01-01 '4.0K' returns '4 bytes'
        decimal_point = locale.localeconv()["decimal_point"]
        parts = size.split(decimal_point)
        whole = parts[0]
        results = re.split(r'(\d+)', parts[1])
        if int(results[1]) == 0:
            size = float(whole)
        else:
            size = float(whole) + float(1 / int(results[1]))
        print("whole:", whole, " | results:", results, " | size:", size)
    else:
        results = re.split(r'(\d+)', size)  # 2024-01-01 '4.0K' returns '4 bytes'
        size = float(results[1])
    #results = re.split(r'^\D*\.?\D+$', size)  # 2024-01-01 Catch 4.0K
    #   File "/home/rick/python/mserve.py", line 8329, in check_chrome_tmp_files
    #     size = toolkit.computer_bytes(results[-1])
    #   File "/home/rick/python/toolkit.py", line 1198, in computer_bytes
    #     size = float(results[1])
    # IndexError: list index out of range

    # Passed: 16K	2023-12-24 23:21	total
    # results: ['', '16', 'K\t', '2023', '-', '12', '-', '24', ' ', '23', ':', '21', '\t total']
    #print("results:", results)
    #if match:
    #    results = match.groups()
    #else:
    #    print("computer_bytes(size) NO match", match, "size:", size)
    #    return 0
    #print("computer_bytes(size) results:", results)
    if size == 0:
        return 0
    uom = results[2].lstrip()  # Grab Unit of Measure
    uom = uom[0].upper()  # First non-blank character
    uom_dict = {
        "K": 1000.0,
        "M": 1000000.0,
        "G": 1000000000.0,
        "T": 1000000000000.0,
        "E": 1000000000000000.0,
        "P": 1000000000000000000.0,
        "Y": 1000000000000000000000.0,
        "Z": 1000000000000000000000000.0
    }
    multiplier = uom_dict.get(uom, 1.0)  # If not found multiply by 1.0
    converted = size * multiplier
    return int(converted)


def scroll_defaults(scrollbox, tabs=None):
    """ Assign tag colors to custom text scroll boxes
        Also set tab stops, margins and button fix for Ctrl+C
    """

    # Foreground colors
    scrollbox.tag_config('red', foreground='red')
    scrollbox.tag_config('blue', foreground='blue')
    scrollbox.tag_config('green', foreground='green')
    scrollbox.tag_config('black', foreground='black')
    scrollbox.tag_config('gray', foreground='gray')

    # Highlighting background colors
    scrollbox.tag_config('yellow', background='yellow')
    scrollbox.tag_config('cyan', background='cyan')
    scrollbox.tag_config('magenta', background='magenta')

    scrollbox.configure(background="WhiteSmoke")
    if not tabs:
        # 2024-09-12 - TODO: https://stackoverflow.com/a/78976310/6929343
        tabs = ("10", "240", "300")  # 2024-09-11 Use stable pixel units
    scrollbox.config(tabs=tabs)  # tab stops
    scrollbox.tag_configure("margin", lmargin1="10", lmargin2="20")
    # Fix Control+C  https://stackoverflow.com/a/64938516/6929343
    scrollbox.bind("<Button-1>", lambda event: scrollbox.focus_set())


class SearchText:
    """ Search for string in text and highlight it. Based on:
    https://www.geeksforgeeks.org/search-string-in-text-using-python-tkinter/
    """
    def __init__(self, view, column=None, find_str=None, find_op='in',
                 callback=None, tt=None, thread=None, keypress=False):
        # root window is the parent window
        self.view = view  # Treeview frame with scrollbars
        ''' How view was created: 
        self.mus_view = toolkit.DictTreeview(
            music_dict, self.mus_top, master_frame, columns=columns,
            sbar_width=sbar_width)
        '''
        self.toplevel = view.toplevel
        self.tree = view.tree
        self.dict = view.tree_dict
        self.attached = view.attached

        self.column = column  # Specific column to search, else all of treeview
        self.find_str = find_str  # Passed search string when searching one column
        self.find_op = find_op  # comparison operator '==', '<', '>', etc.
        self.callback = callback  # E.G. missing_artwork_callback
        self.tt = tt  # ToolTIps
        self.get_thread_func = thread  # mserve.py self.get_refresh_thread
        self.use_keypress = keypress  # Launch search with each key press?
        # print('column:', column, 'find_str:', find_str)
        self.who = "toolkit.SearchText()."

        self.frame = None  # frame for input
        # Search text entry box
        self.entry = None  # input field for search string

        ''' Cannot conduct search when Row SQL Details (RSD) are viewed. '''
        if self.view.rsd_top_is_active:
            title = 'Text search disabled.'
            text = 'Row SQL Details window must be closed before Text Search.'
            #print(self.who + '__init__(): Text search disabled.')
            #print('self.view.rsd_top_is_active - Close details window.')
            # .Show
            message.ShowInfo(self.toplevel, title, text, thread=self.get_thread_func)
            self.toplevel = None  # Signal inactive
            return

        ''' keypress search variables '''
        self.keypress_waiting = None  # A keypress is waiting
        self.search_text = tk.StringVar()

        self.search_or = False  # Later make a choice box. Find word OR word...
        self.search_and = True  # Find word AND word AND word

        self.new_str = ""  # New search string. Cannot be none for comparison.
        self.old_str = ""  # Last search string
        self.sip = False  # Search in progress?
        self.rip = False  # Reattach in progress?
        self.last_refresh = time.time()

        if self.find_str is not None:
            return  # search string passed, no need for frame

        self.frame = tk.Frame(self.toplevel)
        self.frame.grid()

        # adding label to search box
        tk.Label(self.frame, text='Text to find:').pack(side=tk.LEFT)

        # adding of single line text box
        self.entry = tk.Entry(self.frame, textvariable=self.search_text)

        # positioning of text box
        self.entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        # setting focus
        self.entry.focus_set()

        # trace on Tk String variable changing
        if self.use_keypress:
            #print("self.search_text.trace('w', self.search_changed)")
            self.search_text.trace('w', self.search_changed)

        # adding of search button  TODO: Expand with tooltips self.tt not visible
        butt = tk.Button(self.frame, text='🔍  Find')
        butt.pack(side=tk.LEFT)
        butt.config(command=self.find)
        self.entry.bind("<Return>", self.find)
        if self.tt is not None:
            self.tt.add_tip(butt, "Type in text then click this button.", anchor="ne")

        but2 = tk.Button(self.frame, text='✘  Close')
        but2.pack(side=tk.RIGHT)
        but2.config(command=self.close)
        if self.tt is not None:
            self.tt.add_tip(but2, "Close search bar.", anchor="nw")

    def search_changed(self, *_args):
        """ Callback as string variable changes in TK entry """
        #if self.keypress_waiting:
        #    print("if self.keypress_waiting:")
        #    # Never executed because can't type faster than search 0.0055580139
        #    return  # Already have another keypress waiting to be processed
        self.keypress_waiting = True  # Tell previous find() call to end now
        #print("self.keypress_waiting = True")

        # Wait for last find() to shutdown (self.sip is False)
        start = time.time()
        while self.sip is True:
            if time.time() - start > 3.0:
                print("toolkit.py - SearchText.search_changed() Waited 3 seconds!")
                self.sip = False
                break
            if not self.check_refresh():
                self.toplevel.after(100)  # Maybe refresh thread instead?
            #if self.sip:
            #    print("toolkit.py - SearchText.search_changed() Waiting another 100 ms")

        self.keypress_waiting = False  # Start a fresh find() with no key waiting
        wait_cursor(self.toplevel)
        self.find()
        self.toplevel.config(cursor="")
        #self.toplevel.update_idletasks()

    def reattach(self):
        """ Reattach treeview items detached by search method """
        i_r = -1  # https://stackoverflow.com/a/47055786/6929343
        words = self.new_str.split() if self.new_str else None
        self.rip = True  # Reattach in progress
        self.last_refresh = time.time()  # skip .1 second first time penalty
        for iid in self.attached.keys():
            # 2024-04-23 Leave screen stale to service waiting keypress
            self.check_refresh()  # spamming backspace getting .1 sec delay.
            #self.check_refresh()  # spamming backspace getting .11 sec delay.
            if self.keypress_waiting:
                return

            # Does it qualify for attaching?

            if words:
                ret = self.search_matches(iid, words)
                if ret is None:
                    return  # Window is closing down
                elif ret is True:
                    pass  # drop down and reattach treeview row
                elif ret is False:
                    continue  # doesn't contain search words, remains detached
                else:
                    print(self.who + "find(): ret is not 'None', 'True' or 'False'")
                    exit()

            # If not attached then reattach it
            i_r += 1  # Get back attached in same position!
            if self.attached[iid] is False:
                #i_r += 1  # Causing attached to go near bottom!
                self.tree.reattach(iid, '', i_r)
                self.attached[iid] = True

        self.rip = False  # Reattach completed

    def check_refresh(self):
        """ check if refresh function used and call it periodically. """
        if not self.get_thread_func:
            return False  # Caller will have to do toplevel.after(999)

        elapsed = time.time() - self.last_refresh
        if elapsed > 0.033:  # Call refresh 30 times a second
            thread = self.get_thread_func()
            thread()
            self.last_refresh = time.time()

        return True  # There is a refresh function

    def search_matches(self, iid, words):
        """ Does the treeview row contain the search string? """
        # searches for desired string
        try:
            values = self.tree.item(iid)['values']
        except TclError:  # Window was closed
            return None

        found_one = False  # Assume worst case
        found_all = True  # Assume best case
        for w in words:
            if any(w.lower() in t.lower()
                   for t in values if isinstance(t, basestring)):
                # Searching all columns of basestring type
                found_one = True
            else:
                found_all = False

        if self.search_or and found_one:
            return True

        if self.search_and and found_one and found_all:
            return True

        return False

    def find(self, *_args):
        """ Search treeview for string in all string columns

            if self.keypress_waiting is True, check if self.new_str starts with
            self.old_str. If so, no need to reattach. Simply keep detaching.
            If self.new_str doesn't start with self.old_str (delete or backspace),
            then reattach all rows.

            if self.keypress waiting is False then reattach from last search.

        """
        ''' Cannot conduct search when Row SQL Details (RSD) are viewed. '''
        if self.view.rsd_top_is_active:
            #print(self.who + 'find(): Text search disabled.')
            #print('self.view.rsd_top_is_active - Close details window.')
            # message already displayed in init
            return

        if self.find_str is not None:
            print(self.who + '.find(): find_column() should have been called.')
            self.find_column()
            return

        s = self.search_text.get()
        stripped = s.strip()
        self.new_str = stripped
        #print("self.new_str: '" + self.new_str + \
        #      "'  | self.old_str: '" + self.old_str + "'.")
        if self.new_str == self.old_str:
            # self.keypress_waiting = False
            # 2024-04-24 keypress_waiting already False on startup.
            self.sip = False
            return

        ext.t_init('reattach')
        #if not self.keypress_waiting:  # None or false
        #    self.reattach()         # Put back items excluded on last search
        # 2024-04-24 new design where self.reattach() will quit on keypress
        if not self.new_str.startswith(self.old_str) or self.rip:
            # 1. Backspace erased character or text inserted/deleted before end
            # 2. Previously reattaching and got interrupted by keypress so
            #    need to continue last reattaching
            self.reattach()  # Put back items excluded on last search

        # 2024-04-23 Leave screen stale to service waiting keypress
        #self.check_refresh()
        #if self.keypress_waiting:
        #    self.sip = False
        #    return

        ext.t_end('no_print')   # For 4000 songs 0.0000178814 seconds
        # For 28k history records 0.038 seconds
        # For 28k history records with whole bunch of typing 11.26 seconds
        self.old_str = self.new_str
        self.keypress_waiting = False

        if len(self.new_str) == 0:
            return  # Nothing to search for

        self.sip = True  # Search in progress
        self.search_or = False  # Later make a choice box
        self.search_and = True

        # Breakdown string into set of words
        #words = s.split()
        words = self.new_str.split()
        #ext.t_init('Loop over every treeview row')
        # Loop over every treeview row
        for iid in self.tree.get_children():
            # self.toplevel.update_idletasks()  # Causes crazy lag
            # Was keyboard character entered/erased?
            #self.check_refresh()
            if self.keypress_waiting:
                self.sip = False
                #print("if self.keypress_waiting: early exit")
                #ext.t_end('print')  # Never executed loop is: 0.02236
                return  # Will be called again from self.search_changed()

            ret = self.search_matches(iid, words)
            if ret is None:
                self.sip = False
                return
            elif ret is True:
                continue
            elif ret is False:
                pass  # drop down and detach from treeview row
            else:
                print(self.who + "find(): ret is not 'None', 'True' or 'False'")
                exit()
                ""
            ''' 2024-04-24 old code
            # searches for desired string
            try:
                values = self.tree.item(iid)['values']
            except TclError:  # Window wsa closed
                self.sip = False
                return

            found_one = False  # Assume worst case
            found_all = True  # Assume best case
            for w in words:
                if any(w.lower() in t.lower()
                       for t in values if isinstance(t, basestring)):
                    # Searching all columns of basestring type
                    found_one = True
                else:
                    found_all = False

            if self.search_or and found_one:
                continue

            if self.search_and and found_one and found_all:
                continue
            '''
            self.tree.detach(iid)
            self.attached[iid] = False

        #ext.t_end('print')  #  Loop over every treeview row: 0.0026471615
        self.sip = False  # Search is over.
        self.entry.focus_set()

    def find_callback(self):
        """ Search treeview and use callback function to test """
        if not self.toplevel:
            #self.dump_vars()
            return  # Closed window
        self.reattach()         # Put back items excluded on last search
        for iid in self.tree.get_children():
            # Comment out below which takes History Configuration Rows from
            # 1 second to 2 minutes.
            #if self.get_thread_func:
            #    thread = self.get_thread_func()
            #    thread()  # crashes when next song starts up
            #if self.toplevel:
            #    self.toplevel.update_idletasks()  # Allow X to close window
            #else:
            #    return  # Closed window - Slows down processing considerably
            # Next line still generates error when window closes. never exited
            # Get all treeview values for testing via callback function
            try:
                values = self.tree.item(iid)['values']
            except tk.TclError:
                # Window closed
                # TclError: invalid command name ".140238088693448.140238088494256.140238088601680.140238088601752"
                return  # No need to dump values anymore. Learned enough

            ret = self.callback(iid, values)
            if ret is None:
                return  # Signal that 'X' closed window of long running process
            elif ret is True:
                continue  # callback says to keep this row

            try:
                self.tree.detach(iid)
                self.attached[iid] = False  # callback says to drop row
            except tk.TclError:
                # invalid command name ".140654660774080.140654660879640.140654660880576.140654660880648"
                #print("toolkit.py SearchText.find_callback() self.tree.detach(iid)",
                #      iid)
                #print("Next song selected causing Update Metadata to fail.")
                #self.dump_vars()
                return

    def dump_vars(self):
        """ debugging when view.tree is corrupted when playing next song.
            Also delayed text box gets corrupted:
            self.missing_artwork_dtb.close()  # Close delayed text box
            AttributeError: 'NoneType' object has no attribute 'close' 
        """
        print("\nself.view:", self.view,
              "\nself.toplevel:", self.toplevel,
              "\nself.tree:", self.tree,
              #"\n len(self.tree.get_children()):", len(self.tree.get_children()),
              #   File "/home/rick/python/toolkit.py", line 1296, in dump_vars
              #     "\n len(self.tree.get_children()):", len(self.tree.get_children()),
              #   File "/usr/lib/python2.7/lib-tk/ttk.py", line 1195, in get_children
              #     self.tk.call(self._w, "children", item or '') or ())
              # TclError: invalid command name ".140320456140848.140320057982560.140320064991816.140320064991888"
              "\nself.dict[0]:", self.dict[0],
              "\nself.dict[-1]:", self.dict[-1],
              "\nself.attached['1']:", self.attached['1'],
              "\nself.attached['2']:", self.attached['2'],
              "\nself.column:", self.column,
              "\nself.find_str:", self.find_str,
              "\nself.find_op:", self.find_op,
              "\nself.callback:", self.callback,
              "\nself.tt:", self.tt,
              "\nself.frame:", self.frame,
              "\nself.entry:", self.entry)

    def find_column(self):
        """ Search treeview for single column of any type (not just strings)
            There is no GUI input for search text.
        """
        if not self.toplevel:
            return  # Closed window
        self.reattach()         # Put back items excluded on last search

        s = self.find_str
        for iid in self.tree.get_children():
            # searches for desired string
            values = self.tree.item(iid)['values']
            if len(values) > 3:
                one_value = self.view.column_value(values, self.column)
            else:
                print("toolkit.py - SearchText.find_column() len(values)",
                      len(values), "iid:", iid)
                one_value = ""
            #if iid == "1":
            #    print('iid:', iid, 'values:', values)
            #    print('one_value:', one_value)

            if self.find_op == 'in':
                if s.lower() in one_value.lower():
                    #print('iid:', iid, 'values:', values)
                    continue
            elif self.find_op == '<=':
                if s > one_value:
                    #print('iid:', iid, 'values:', values)
                    continue
            elif self.find_op == '>=':
                if s < one_value:
                    # print('iid:', iid, 'values:', values)
                    continue
            elif self.find_op == '==':
                if s == '':
                    # When find_str is '' it means we are looking for None
                    if one_value == u'None':
                        continue
                if s == one_value:
                    # print('iid:', iid, 'values:', values)
                    continue
            else:
                # Limited number of operations supported on Aug 2, 2021.
                print('toolkit.py.SearchText.find_column() invalid find_op:',
                      self.find_op)


            try:
                self.tree.detach(iid)
                self.attached[iid] = False  # callback says to drop row
            except tk.TclError:
                # invalid command name ".140654660774080.140654660879640.140654660880576.140654660880648"
                print("toolkit.py SearchText.find_callback() self.tree.detach(iid)",
                      iid)
                print("Rare event known to happen when song ends. Reason unknown")
                return

    def close(self):
        """ Remove find search bar
            TODO: No way of stopping find loop when window closed by parent
        """
        if not self.toplevel:
            return  # Closed window
        self.search_text.set("")  # Prevent future text highlighting of old search
        self.new_str = ""  # New and old are compared to see if find() should
        self.old_str = ""  # begin execution. Ensure they are both blank.
        self.reattach()  # 2024-04-24 was higher up but do with empty self.new_str
        if self.find_str is None:
            self.frame.grid_remove()  # Next pack is faster this way?


""" MoveTreeviewColumn class

Published to: https://stackoverflow.com/a/51425272/6929343

May. 05 2023 - 'BUTTON_HEIGHT = 63' global constant is no longer used.
Mar. 19 2024 - Fix uninitialized variables in .start() not published to
               stackoverflow.com 

UNCOMMENT BELOW when publishing to stackoverflow.com:

try:  # Python 3
    import tkinter as tk
except ImportError:  # Python 2
    import Tkinter as tk
from PIL import Image, ImageTk
from collections import namedtuple
from os import popen
"""


class MoveTreeviewColumn:
    """ Shift treeview column to preferred order """

    def __init__(self, toplevel, treeview, row_release=None, apply_callback=None):

        self.toplevel = toplevel
        self.treeview = treeview
        self.apply_callback = apply_callback

        self.row_release = row_release      # Button-Release not on heading
        self.eligible_for_callback = False  # If button-release in cell region
        # 2024-03-26 button-1 release in cell no longer supported in mserve.py.
        # It has become too complicated so button-3 (right click) is used.

        self.region = None                  # Region of treeview clicked

        self.xdotool_installed = ext.check_command('xdotool')
        self.col_cover_top = None           # toplevel move columns
        self.col_top_is_active = False      # column move in progress?
        self.canvas = None                  # tk Canvas with column photos
        self.col_being_moved = None         # Column being moved in '#?' form
        self.col_swapped = False            # Did we swap a column?

        self.images = []                    # GIC protected image list
        self.canvas_names = []              # treeview column names
        self.canvas_widths = []             # matching widths
        self.canvas_objects = []            # List of canvas objects
        self.canvas_x_offsets = []          # matching x-offsets within canvas

        self.canvas_index = None            # Canvas index being moved
        self.canvas_name = None             # Treeview column name
        self.canvas_object = None           # Canvas item object being moved
        self.canvas_original_x = None       # Canvas item starting offset
        self.start_mouse_pos = None         # Starting position to calc delta

        self.treeview.bind("<ButtonPress-1>", self.start)
        self.treeview.bind("<ButtonRelease-1>", self.stop)
        self.treeview.bind("<B1-Motion>", self.motion)

    def close(self):
        """ Close Treeview - unbinding bad idea? See bug reports. """
        self.treeview.unbind("<ButtonPress-1>")
        self.treeview.unbind("<ButtonRelease-1>")
        self.treeview.unbind("<B1-Motion>")

    def start(self, event):
        """
            Button 1 was just pressed for library treeview or backups treeview in 
                bserve.py (gmail API backup server). Or button 1 pressed for
                mserve.py (Music Server) SQL Music treeview or SQL History Treeview

            :param event: tkinter event
            :return: None
        """

        #print('<ButtonPress-1>', event.x, event.y)
        self.region = self.treeview.identify("region", event.x, event.y)

        if self.region != 'heading':
            self.eligible_for_callback = True  # If button-release in cell region
            return

        self.eligible_for_callback = False     # If button-release in cell ignore

        Mouse = namedtuple('Mouse', 'x y')
        # noinspection PyArgumentList
        self.start_mouse_pos = Mouse(event.x, event.y)

        if self.col_cover_top is not None:
            print('toolkit.py MoveTreeviewColumn attempting to create self.col_cover_top a second time.')
            return

        self.create_move_column()
        if self.col_top_is_active is False:
            return  # Released button quickly or error creating top level

        # The column being moved - Recalculated after snap to grid
        self.col_being_moved = self.treeview.identify_column(event.x)
        #print('self.col_being_moved:', self.col_being_moved)
        self.get_source(self.col_being_moved)
        self.treeview.config(cursor='boat red red')  # boat cursor supports red
        self.col_swapped = False
        #print('\n columns BEFORE:', self.canvas_names)

    def stop(self, event):
        """ Determine if we were in motion before we lifted mouse button
        """
        if self.region != 'heading':
            # If button release not on heading call optional row_release
            if self.row_release is not None and self.eligible_for_callback:
                self.row_release(event)
            return

        ''' Destroy toplevel used for moving columns on canvas '''
        if self.col_top_is_active:
            # Destroy top level window covering up old music player position
            if self.col_cover_top is not None:
                if self.col_swapped:
                    #print('columns AFTER :', self.canvas_names)
                    self.treeview["displaycolumns"] = self.canvas_names
                    # 2024-04-01 - dd_view.close_common_windows()
                    if self.apply_callback:
                        self.apply_callback()
                    self.toplevel.update_idletasks()  # just in case
                self.col_cover_top.destroy()
                self.col_cover_top = None
            self.col_top_is_active = False
            self.treeview.config(cursor='')

    def motion(self, event):
        """
        TODO: What if treeview only has 1 column?

        What if horizontal scroll and non-displayed columns to left or right
        of displayed treeview columns? Need to compare 'displaycolumns' to
        current treeview.

        :param event: Tkinter event with x, y, widget
        :return:
        """
        if self.region != 'heading':
            return

        # xdotool required to move mouse position
        # During initialization define self.xdotool_installed
        # Calculate delta - distance travelled since startup or snap to grid
        change = event.x - self.start_mouse_pos.x
        # Aug 1/22 - self.start_mouse_pos.x or self.canvas_original_x is None Type?
        if self.start_mouse_pos.x is None:
            print("toolkit.py/motion() self.start_mouse_pos.x is none")
        if self.canvas_original_x is None:
            print("toolkit.py/motion() self.canvas_original_x is none")

        # Calculate new start, middle and ending x offsets for source object
        new_x = int(self.canvas_original_x + change)  # Sometimes we get float?

        new_x = 0 if new_x < 0 else new_x  # 2024-03-19 limit x to zero offset

        new_middle_x = new_x + self.canvas_widths[self.canvas_index] // 2
        new_x2 = new_x + self.canvas_widths[self.canvas_index]
        try:
            self.canvas.coords(self.canvas_object, (new_x, 0))  # Move on screen
        except tk.TclError as _err:
            # 2024-03-24 Suppress printing lots of these errors
            #print("toolkit.py/motion() 1st err:", _err)
            #print("new_x:", new_x, "new_x2:", new_x2)
            # toolkit.py/motion() 1st err: wrong # args: should be
            #   ".140483232493720.140483232493936.140483232494080
            #   co ords tagOrId ?x y x y ...?"
            # new_x: 49 new_x2: 291
            pass  # Get lots of these errors all the time?

        ''' Make column snap to next (jump) when over half way -
            Either half of target is covered or half of source
            has moved into target 
        '''
        if change < 0:  # Mouse is moving column to the left
            if self.canvas_index == 0:
                return  # We are already first column on left
            target_index = self.canvas_index - 1
            target_start_x, target_middle_x, target_end_x = self.get_target(
                target_index)
            if new_x > target_middle_x and new_middle_x > target_end_x:
                return  # Not eligible for snap to grid

        elif change > 0:  # Mouse is moving column to the right
            if self.canvas_index == len(self.canvas_x_offsets) - 1:
                return  # We are already last column on right
            target_index = self.canvas_index + 1
            target_start_x, target_middle_x, target_end_x = self.get_target(
                target_index)
            if new_x2 < target_middle_x and new_middle_x < target_start_x:
                return  # Not eligible for snap to grid
        else:
            #print('toolkit.py MoveTreeviewColumn motion() called with no motion.')
            # Common occurrence when mouse moves fraction back and forth
            return  # Mouse didn't change position

        ''' Swap our column and the target column beside us (snap to grid).
            Calculate jump factor and then make mouse jump by same amount
        '''

        ''' Diagnostic section
        print('\n<B1-Motion>', event.x, event.y)
        print('\tcanvas_index   :', self.canvas_index,
              '\ttarget_index:  :', target_index,
              '\toriginal_x     :', self.canvas_original_x)
        print('\tnew_x          :', new_x,
              '\tnew_middle_x   :', new_middle_x,
              '\tnew_x2         :', new_x2)
        print('\ttarget_start_x :', target_start_x,
              '\ttarget_middle_x:', target_middle_x,
              '\ttarget_end_x   :', target_end_x)
        '''

        if target_index < self.canvas_index:
            # snapping to grid on left
            if self.canvas_index == 0:
                return  # Can't go before first column
            new_target_x = self.canvas_x_offsets[target_index] + \
                self.canvas_widths[self.canvas_index]
            new_source_x = self.canvas_x_offsets[target_index]
        else:
            # snapping to grid on right
            if self.canvas_index == len(self.canvas_widths) - 1:
                return  # Can't go past last column
            new_source_x = self.canvas_x_offsets[self.canvas_index] + \
                self.canvas_widths[target_index]
            new_target_x = self.canvas_x_offsets[self.canvas_index]

        # Swap lists at target index and self.canvas_index
        source_old_x = source_x_jump = 0
        try:
            source_old_x = self.canvas.coords(self.canvas_object)[0]
            self.source_to_target(target_index, new_target_x, new_source_x)
        except tk.TclError as err:
            print("toolkit.py/motion() 2nd err:", err)

        try:
            source_new_x = self.canvas.coords(self.canvas_object)[0]
            source_x_jump = source_new_x - source_old_x
        except tk.TclError as err:
            print("toolkit.py/motion() 3rd err:", err)

        # Move mouse on screen to reflect snapping to grid
        self.treeview.unbind("<B1-Motion>")            # Don't call ourself
        ''' If you don't have xdotool installed, activate following code
         current_mouse_xy = self.toplevel.winfo_x() + event.x + source_x_jump
         window_mouse_xy = self.toplevel.winfo_y() + event.y
        # mouse_move_to takes .1 to .14 seconds and flickers new window
        move_mouse_to( current_mouse_xy,  window_mouse_xy)
        # xdotool takes .006 to .012 seconds and no flickering window
        '''
        os.popen("xdotool mousemove_relative -- " + str(int(source_x_jump)) + " 0")
        self.treeview.bind("<B1-Motion>", self.motion)

        # Recalibrate mouse starting position within toplevel
        Mouse = namedtuple('Mouse', 'x y')
        # noinspection PyArgumentList
        self.start_mouse_pos = Mouse(event.x + source_x_jump, event.y)

        self.col_swapped = True  # We swapped a column so update treeview

    def get_source(self, col_being_moved):
        """ Set self.canvas_xxx instances """
        # Strip treeview '#' from '#?' column number
        self.canvas_index = int(col_being_moved.replace('#', '')) - 1
        self.canvas_name = self.canvas_names[self.canvas_index]
        self.canvas_object = self.canvas_objects[self.canvas_index]
        self.canvas_original_x = self.canvas_x_offsets[self.canvas_index]
        self.canvas.tag_raise(self.canvas_object)  # Top stacking order

    def get_target(self, target_index):
        """ Get target """
        target_start_x = self.canvas_x_offsets[target_index]
        target_middle_x = target_start_x + \
            self.canvas_widths[target_index] // 2
        if target_index == len(self.canvas_x_offsets) - 1:
            # This is the last column on right so use canvas width
            target_end_x = self.canvas.winfo_width()
        else:
            # This is the last column on right so use canvas width
            target_end_x = self.canvas_x_offsets[target_index + 1]

        return target_start_x, target_middle_x, target_end_x

    @staticmethod
    def swap(lst, x1, x2):
        """ Swap two elements in a list """
        lst[x1], lst[x2] = lst[x2], lst[x1]  # Swap two elements in list

    def source_to_target(self, target_index, new_target_x, new_source_x):
        """ Swap source and target columns """
        self.swap(self.canvas_names, self.canvas_index, target_index)
        self.swap(self.canvas_objects, self.canvas_index, target_index)
        self.swap(self.canvas_widths, self.canvas_index, target_index)
        self.canvas_x_offsets[self.canvas_index] = new_target_x
        self.canvas_x_offsets[target_index] = new_source_x

        # Swap the two images on canvas
        self.canvas.coords(self.canvas_objects[self.canvas_index],
                           (self.canvas_x_offsets[self.canvas_index], 0))
        self.canvas.coords(self.canvas_objects[target_index],
                           (self.canvas_x_offsets[target_index], 0))

        # Now that columns swapped on canvas, get new variables
        self.col_being_moved = "#" + str(target_index + 1)
        self.get_source(self.col_being_moved)

    def create_move_column(self):
        """
            Create canvas toplevel covering up treeview.
            Canvas divided into rectangles for each column.
            Track <B1-Motion> horizontally to swap with next column.
        """

        if self.col_cover_top is not None:
            print('trying to create self.col_cover_top again!!!')
            return

        self.toplevel.update()              # Refresh current coordinates
        self.col_top_is_active = True
        self.canvas_original_x = 0          # 2024-03-19 Canvas item start offset
        self.canvas_index = 0               # Canvas index being moved

        # create named tuple class with names x, y, w, h
        Geom = namedtuple('Geom', ['x', 'y', 'w', 'h'])

        # noinspection PyArgumentList
        top_geom = Geom(self.toplevel.winfo_x(),
                        self.toplevel.winfo_y(),
                        self.toplevel.winfo_width(),
                        self.toplevel.winfo_height())

        #print('\n tkinter top_geom:', top_geom)

        ''' Take screenshot of treeview region (x, y, w, h)
        '''
        # X11 takes 4.5 seconds first time and .67 seconds subsequent times
        #top_image = x11.screenshot(top_geom.x, top_geom.y,
        #                           top_geom.w, top_geom.h)

        # gnome screenshot entire desktop takes .25 seconds
        # noinspection PyTypeChecker
        top_image = gnome_screenshot(top_geom)

        # Did button get released while we were capturing screen?
        if self.col_top_is_active is False:
            return

        # Mount our column moving window over original treeview
        self.col_cover_top = tk.Toplevel()
        self.col_cover_top.overrideredirect(True)   # No window decorations
        self.col_cover_top.withdraw()
        # No title when undecorated (override direct = true)
        #self.col_cover_top.title("Shift column - bserve")
        self.col_cover_top.grid_columnconfigure(0, weight=1)
        self.col_cover_top.grid_rowconfigure(0, weight=1)

        can_frame = tk.Frame(self.col_cover_top, bg="grey",
                             width=top_geom.w, height=top_geom.h)
        can_frame.grid(column=0, row=0, sticky=tk.NSEW)
        can_frame.grid_columnconfigure(0, weight=1)
        can_frame.grid_rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(can_frame, width=top_geom.w,
                                height=top_geom.h, bg="grey")
        self.canvas.grid(row=0, column=0, sticky='nsew')

        total_width = 0
        self.images = []                    # Reset GIC protected image list
        self.canvas_names = []              # treeview column ids (names)
        self.canvas_widths = []             # matching widths
        self.canvas_objects = []            # List of canvas objects
        self.canvas_x_offsets = []          # matching x-offsets within canvas

        for i, column in enumerate(self.treeview['displaycolumns']):

            col_width = self.treeview.column(column)['width']
            # Create cropped image for column out of screenshot using 1 px
            # border width.  Extra crop from bottom to exclude buttons.
            # noinspection PyTypeChecker
            image = top_image.crop([total_width + 1, 1,
                                    total_width + col_width - 2,
                                    top_geom.h - 63])

            # Make a black background image at original column size
            new_im = Image.new("RGB", (col_width, top_geom.h))

            # Paste cropped column image inside black image making a border
            new_im.paste(image, (2, 2))
            photo = ImageTk.PhotoImage(new_im)
            self.images.append(photo)       # Prevent GIC (garbage collection)
            item = self.canvas.create_image(total_width, 0,
                                            image=photo, anchor=tk.NW)
            self.canvas_names.append(column)
            self.canvas_objects.append(item)
            self.canvas_widths.append(col_width)
            self.canvas_x_offsets.append(total_width)
            total_width += col_width

            # Did button get released while we were formatting canvas?
            if self.col_top_is_active is False:
                return

        # Move the column cover window with canvas over original treeview
        self.col_cover_top.geometry('{}x{}+{}+{}'.format(
            top_geom.w, top_geom.h, top_geom.x, top_geom.y))
        self.col_cover_top.deiconify()  # Forces window to appear
        self.col_cover_top.update()  # This is required for visibility


def wait_cursor(toplevel):
    """ Turn mouse pointer (cursor) into hour glass 
        Caller reverses with toplevel.config(cursor="")
    """
    try:
        toplevel.config(cursor="watch")  # Ubuntu 16.04
        #print('toplevel.config(cursor="watch")')
    except tk.TclError:
        toplevel.config(cursor="clock")  # Ubuntu 18.04
        #print('toplevel.config(cursor="clock")')

    toplevel.update_idletasks()


def move_mouse_to(x, y):
    """ Moves the mouse to an absolute location on the screen.
        Rather slow at .1 second and causes brief screen flicker.
        From: https://stackoverflow.com/a/66808226/6929343
        Visit link for other options under Windows and Mac.
        For Linux use xdotool for .007 response time and no flicker.
    """
    # Create a new temporary root
    temp_root = tk.Tk()
    # Move it to +0+0 and remove the title bar
    temp_root.overrideredirect(True)
    # Make sure the window appears on the screen and handles the `overrideredirect`
    temp_root.update()
    # Generate the event as @a bar nert did
    temp_root.event_generate("<Motion>", warp=True, x=x, y=y)
    # Make sure that tcl handles the event
    temp_root.update()
    # Destroy the root
    temp_root.destroy()


def gnome_screenshot(geom):
    """ Screenshot using old gnome 3.18 standards
        Required to move column in tk.Treeview
    """

    import gi
    # When replacing 3.0 with 4.0 below
    gi.require_version('Gdk', '3.0')  # Namespace Gdk is already loaded with version 3.0
    gi.require_version('Gtk', '3.0')  # Namespace Gtk not available for version 4.0
    gi.require_version('Wnck', '3.0')  # Namespace Wnck not available for version 4.0
    # gi.require_versions({"Gtk": "3.0", "Gdk": "3.0", "Wnck": "3.0"})  # Python 3

    from gi.repository import Gdk, GdkPixbuf, Gtk, Wnck

    #gi.require_version('GObject', '4.0')  # Namespace GObject is already loaded with version 2.0
    #from gi.repository import Gdk, Gdk Pix buf, Gtk, Wnck, GObject
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
    w = Gdk.get_default_root_window()
    pb = Gdk.pixbuf_get_from_window(w, *geom)
    desk_pixels = pb.read_pixel_bytes().get_data()
    # June 19, 2023 - Error 'Image' was never imported. Add above.
    raw_img = Image.frombytes('RGB', (geom.w, geom.h), desk_pixels,
                              'raw', 'RGB', pb.get_rowstride(), 1)
    return raw_img


# ==============================================================================
#
#   toolkit.py - ToolTips(), .add_tip(), .set_text(), .toggle_position(),
#                .close(), .reset_widget_colors() and .poll_tips()
#
#   Aug 16/2021 - Copied from message.py which will be kept intact for
#                 tool tips that do not fade in/out.
#
# ==============================================================================

""" TODO:
    Border around tooltip using foreground color to contrast background color:
    https://www.geeksforgeeks.org/how-to-change-border-color-in-tkinter-widget/
"""

D_PRINT = False         # Print debug events

#VISIBLE_DELAY = 750     # ms pause before balloon tip appears (3/4 sec)
#VISIBLE_SPAN = 5000     # ms balloon tip remains on screen (5 sec/line)
#EXTRA_WORD_SPAN = 500   # 1/2 second per word if > VISIBLE_SPAN
#FADE_IN_SPAN = 500      # 1/4 second to fade in
#FADE_OUT_SPAN = 400     # 1/5 second to fade out

# Five timing variables are user configurable and stored in SQL History Table
# Type, Action, Master, Detail = ['cfg_tooltips', 'default', 'time', 'ms']
VISIBLE_DELAY = None    # ms pause before balloon tip appears (3/4 sec)
VISIBLE_SPAN = None     # ms balloon tip remains on screen (5 sec/line)
EXTRA_WORD_SPAN = None  # 1/2 second per word if > VISIBLE_SPAN
FADE_IN_SPAN = None     # 1/4 second to fade in
FADE_OUT_SPAN = None    # 1/5 second to fade out


class CommonTip:
    """ Variables common to ToolTips__init__() and add_tip()
        Must appear before first reference (E.G. message.ShowInfo crashes)
    """
    def __init__(self):

        self.dict = {}                  # add_tip() dictionary

        self.widget = None              # "999.999.999" = top.frame.button  1
        self.current_state = None       # enter, press, release or leave    2
        self.current_mouse_xy = 0       # Mouse position within widget      3
        self.window_mouse_xy = 0        # Position when tip window created  4
        self.enter_time = 0.0           # time button was entered           5
        self.leave_time = 0.0           # time button was left              6
        self.motion_time = 0.0          # time button was released          7
        self.press_time = 0.0           # time button was pressed           8
        self.release_time = 0.0         # time button was released          9
        # User configurable timings ('cfg_tooltips', 'default', 'time', 'ms')
        self.visible_delay = 0          # milliseconds before visible       10
        self.visible_span = 0           # milliseconds to keep visible      11
        self.extra_word_span = 0        # milliseconds for extra lines      12
        self.fade_in_span = 0           # milliseconds for fading in        13
        self.fade_out_span = 0          # milliseconds for fading out       14

        # Too much window_ prefix usage??
        #  'tip_window' used to be 'window_object'
        #  'text' used to be 'window_text'
        #  'window_fading_in' could be 'fading_in'
        #  'window_fading_out' could be 'fading_out'
        self.tip_window = None          # The tooltip window we created     15
        self.text = None                # Text can be changed by caller     16
        Geometry = namedtuple('Geometry', 'x, y, width, height')
        # noinspection PyArgumentList
        self.window_geom = Geometry(0, 0, 0, 0)                           # 17
        self.window_visible = False     # False when alpha = 0.0          # 18
        # Window is never alpha 0 anymore...
        self.current_alpha = 0.0        # current window alpha            # 19
        self.window_fading_in = False                                     # 20
        self.window_fading_out = False                                    # 21

        self.tool_type = None           # "button", "label", etc.         # 22
        self.name = None                # Widget name for debugging       # 23
        self.fg = None                  # Foreground color (buttons)      # 24
        self.bg = None                  # Background color (buttons)      # 25
        self.normal_text_color = None   # self.widget.itemcget(...)       # 26
        self.normal_button_color = None  # .itemcget("button_color"...)   # 27
        self.anchor = None              # tooltip anchor point on widget  # 28
        self.menu_tuple = None          # tool_type 'menu' controls       # 29

                                        # 'piggy_back' below with # 30 to # 33
        self.pb_alpha = None            # Update 'piggy_back' with alpha percent
        self.pb_leave = None            # Tell 'piggy_back' mouse left widget
        self.pb_ready = None            # Tell 'piggy_back' it can display msg
        self.pb_close = None            # Tell 'piggy_back' tip_window closed


class ToolTips(CommonTip):
    """ Manage fading in and fading out of tooltips (balloons).
        Canvas button (rounded rectangles) highlighting upon button focus.
        Tooltips can be buttons, canvas buttons or labels.
        Tooltips are internally tracked by their widget object:
            Toplevel.Frame.Widget.Window
                Where .Window is created here.

        USAGE:

            From Master Toplevel initialize:

                self.tt = ToolTips()

            During screen creation Add tooltip (defaults to type='button'):

                self.tt.add_tip(widget_name, type='canvas_button',
                                text="This button\nDoes that.")

            When screen is closed:

                self.tt.close(widget_toplevel)

            Parent must poll the tooltips every 33 ms or so with:

                self.tt.poll_tips()

            June 15, 2023 - Allow piggy backing on Tooltips() technology:

                self.tt.add_tip(widget_name, type='piggy_back',
                                class=class_name)
                WHERE: the class_name has methods inside. E.G. InfoCentre()

            April 30, 2024 - Support tool_type='splash'

                self.tt.add_tip(widget_name, type='splash', visible_delay=0)

        When polling is impractical, fade in and fade out can be disabled by:

            VISIBLE_DELAY = 0
            VISIBLE_SPAN = 0
            FADE_TIME = 0
            FADE_STEPS = 0

        TODO: When long pressing button (previous/next song testing) sometimes
              it is ignored while tooltip is fading in. Button press and release
              events are not being tracked in our poll_tips() function. Press
              and hold button then after tooltip fully fades in a pseudo button
              release event occurs and active state returns to normal.
              The error message is usually displayed: "ToolTipsPool.showtip():
              Previous tooltip should not be waiting to be visible".

              If window doesn't have focus, don't display tips.
              If window loses focus, close balloons.
    """

    def __init__(self, print_error=True):

        """ Duplicate entry_init() """
        CommonTip.__init__(self)        # Recycled class to set self. instances

        self.print_error = print_error  # Print errors? Not possible with no stdout

        self.log_nt = None              # namedtuple time, action, widget, x, y
        self.log_list = []              # list of log dictionaries
        self.deleted_str = "0.0.0"      # flag log entry as deleted (zero time)
        self.now = time.time()          # Current time
        self.who = "toolkit.py ToolTips()."

        self.dict = {}                  # Tip dictionary
        self.tips_list = []             # List of Tip dictionaries
        self.tips_index = 0             # Current working Tip dictionary in list

        self.cfg = sql.Config()
        sql_key = ['cfg_tooltips', 'default', 'style', 'color']
        dft = self.cfg.get_cfg(sql_key)
        self.dft_fg = dft['foreground']
        self.dft_bg = dft['background']

        sql_key = ['cfg_tooltips', 'default', 'time', 'ms']
        dft = self.cfg.get_cfg(sql_key)
        #print("dft:", dft)
        global VISIBLE_DELAY, VISIBLE_SPAN, EXTRA_WORD_SPAN
        global FADE_IN_SPAN, FADE_OUT_SPAN
        VISIBLE_DELAY = dft['VISIBLE_DELAY']
        VISIBLE_SPAN = dft['VISIBLE_SPAN']
        EXTRA_WORD_SPAN = dft['EXTRA_WORD_SPAN']
        FADE_IN_SPAN = dft['FADE_IN_SPAN']
        FADE_OUT_SPAN = dft['FADE_OUT_SPAN']

        ''' NOTE: Because a new tip fades in after 3/4 second we have time to
                  make old tool tip fade out assuming VISIBLE_DELAY > FADE_TIME '''
        if VISIBLE_DELAY < FADE_OUT_SPAN:
            print(self.who + '__init__(): VISIBLE_DELAY < FADE_OUT_SPAN')
            exit()

    def dict_to_fields(self):
        """ Cryptic dictionary fields to easy names """
        self.widget = self.dict['widget']                           # 01
        self.current_state = self.dict['current_state']             # 02
        self.current_mouse_xy = self.dict[' current_mouse_xy']      # 03
        self.window_mouse_xy = self.dict[' window_mouse_xy']        # 04
        self.enter_time = self.dict['enter_time']                   # 05
        self.leave_time = self.dict['leave_time']                   # 06
        self.motion_time = self.dict['motion_time']                 # 07
        self.press_time = self.dict['press_time']                   # 08
        self.release_time = self.dict['release_time']               # 09
        self.visible_delay = self.dict['visible_delay']             # 10
        self.visible_span = self.dict['visible_span']               # 11
        self.extra_word_span = self.dict['extra_word_span']         # 12
        self.fade_in_span = self.dict['fade_in_span']               # 13
        self.fade_out_span = self.dict['fade_out_span']             # 14
        self.tip_window = self.dict['tip_window']                   # 15
        self.text = self.dict['text']                               # 16
        self.window_geom = self.dict['window_geom']                 # 17
        self.window_visible = self.dict['window_visible']           # 18
        self.current_alpha = self.dict['current_alpha']             # 19
        self.window_fading_in = self.dict['window_fading_in']       # 20
        self.window_fading_out = self.dict['window_fading_out']     # 21
        self.tool_type = self.dict['tool_type']                     # 22
        self.name = self.dict['name']                               # 23
        self.fg = self.dict['fg']                                   # 24
        self.bg = self.dict['bg']                                   # 25
        self.normal_text_color = self.dict['normal_text_color']     # 26
        self.normal_button_color = self.dict['normal_button_color']  # 27
        self.anchor = self.dict['anchor']                           # 28
        self.menu_tuple = self.dict['menu_tuple']                   # 29
        self.pb_alpha = self.dict['pb_alpha']                       # 30
        self.pb_leave = self.dict['pb_leave']                       # 31
        self.pb_ready = self.dict['pb_ready']                       # 32
        self.pb_close = self.dict['pb_close']                       # 33

    def fields_to_dict(self):
        """ Easy names to cryptic dictionary fields """
        self.dict['widget'] = self.widget                           # 01
        self.dict['current_state'] = self.current_state             # 02
        self.dict[' current_mouse_xy'] = self.current_mouse_xy      # 03
        self.dict[' window_mouse_xy'] = self.window_mouse_xy        # 04
        self.dict['enter_time'] = self.enter_time                   # 05
        self.dict['leave_time'] = self.leave_time                   # 06
        self.dict['motion_time'] = self.motion_time                 # 07
        self.dict['press_time'] = self.press_time                   # 08
        self.dict['release_time'] = self.release_time               # 09
        self.dict['visible_delay'] = self.visible_delay             # 10
        self.dict['visible_span'] = self.visible_span               # 11
        self.dict['extra_word_span'] = self.extra_word_span         # 12
        self.dict['fade_in_span'] = self.fade_in_span               # 13
        self.dict['fade_out_span'] = self.fade_out_span             # 14
        self.dict['tip_window'] = self.tip_window                   # 15
        self.dict['text'] = self.text                               # 16
        self.dict['window_geom'] = self.window_geom                 # 17
        self.dict['window_visible'] = self.window_visible           # 18
        self.dict['current_alpha'] = self.current_alpha             # 19
        self.dict['window_fading_in'] = self.window_fading_in       # 20
        self.dict['window_fading_out'] = self.window_fading_out     # 21
        self.dict['tool_type'] = self.tool_type                     # 22
        self.dict['name'] = self.name                               # 23
        self.dict['fg'] = self.fg                                   # 24
        self.dict['bg'] = self.bg                                   # 25
        self.dict['normal_text_color'] = self.normal_text_color     # 26
        self.dict['normal_button_color'] = self.normal_button_color  # 27
        self.dict['anchor'] = self.anchor                           # 28
        self.dict['menu_tuple'] = self.menu_tuple                   # 29
        self.dict['pb_alpha'] = self.pb_alpha                       # 30
        self.dict['pb_leave'] = self.pb_leave                       # 31
        self.dict['pb_ready'] = self.pb_ready                       # 32
        self.dict['pb_close'] = self.pb_close                       # 33

    def log_event(self, action, widget, x, y):
        """ action is 'enter', 'leave', 'press' or 'release'.
            If release coordinates outside of bounding box, it doesn't count.
            Just log events to array. Do not process them at this point.
            Called from bind

            Events are logged instantly, however processed every 33 ms
            There is no perceptible lag as 30 fps is faster than human eye.
        """
        Event = namedtuple('Event', 'time, action, widget, x, y')
        # noinspection PyArgumentList
        self.log_nt = Event(time.time(), action, widget, x, y)
        #if action == 'enter' or action == 'leave' or action == 'press':  # debug self.info
        #    print("log_event(self, action, widget)", action, str(widget)[-4:])
        self.log_list.append(self.log_nt)
        # print('EVENT:', self.log_nt)

    def process_log_list(self):
        """ Process log list backwards deleting earlier matching widget events """
        # https://stackoverflow.com/a/529427/6929343

        for i, self.log_nt in reversed(list(enumerate(self.log_list))):
            # print('log_dict in log_list', self.log_nt)
            if self.log_nt.widget == self.deleted_str:
                continue                        # We deleted this one, grab next
            # Delete matching widget events prior to this event (i) which is kept
            # self.delete_older_for_widget(i)
            self.set_tip_plan()

        self.log_list = []      # Flush out log list for new events

    def delete_older_for_widget(self, stop_index):
        """ Process log list forwards from 0 deleting matching widget
            Requires specialized testing using manual calls to 
            log_event(action, widget, x, y) followed by process_log_list()

            Intention is to delete <enter> event if there is a <leave> event
            in the queue. Problem is the <leave> event is getting deleted
            instead. Disable for now...

        """
        # Find event log's widget in list of tooltips
        search_widget = self.renumber_widget(self.log_nt.widget)

        for i, nt in enumerate(self.log_list):
            if i >= stop_index:
                return  # Don't want to delete the last one
            if nt.widget == search_widget:
                # Widget matches so flag as deleted
                if self.print_error:
                    print(self.who + 'delete_older_for_widget():', self.log_nt)
                # TODO: What if entering canvas is deleted and colors not changed?
                Event = namedtuple('Event', 'time, action, widget, x, y')
                # noinspection PyArgumentList
                self.log_list[i] = Event(self.log_nt.time, self.log_nt.action,
                                         self.deleted_str,
                                         self.log_nt.x, self.log_nt.y)

    def set_tip_plan(self):
        """ Called to process event from self.log_nt """
        # Find event log's widget in list of tooltips
        search_widget = self.renumber_widget(self.log_nt.widget)
        for self.tips_index, self.dict in enumerate(self.tips_list):
            if self.dict['widget'] == search_widget:
                break
        else:
            if self.print_error:
                print(self.who + 'set_tip_plan() self.log_nt widget NOT FOUND!:',
                      self.log_nt)
                print('search_widget for above:', search_widget)
            try:
                if self.print_error:
                    print("search_widget['text']:", search_widget['text'])
            except tk.TclError:
                if self.print_error:
                    print("Probably shutting down...")
                pass  # Weirdly needed to make pycharm happy
            return

        self.dict_to_fields()  # Dictionary to easy names
        self.current_mouse_xy = (self.log_nt.x, self.log_nt.y)  # pos in widget

        ''' OVERVIEW:
            Enter, wait, create, fade in, wait, fade out, close (destroy).  
            self.window_fading_in and self.window_fading_out already 
            setup so just need self.wait_time.
            
            BUG October 18/23:
            Tip created (with info.cast) gets 'enter' event then play top
            steals 2 seconds of processing time. poll_tips is called and
            the 'close' event is called. All steps inbetween are skipped.
        '''
        if self.log_nt.action == 'leave' or self.log_nt.action == 'press':
            # Leaving widget - June 20, 2023 treat button press as leave
            self.leave_time = self.log_nt.time
            if self.log_nt.action == 'leave':
                d_print('Leaving widget: ', str(self.widget)[-4:])
            else:
                d_print('Clicked widget: ', str(self.widget)[-4:])

            if self.window_fading_out:
                pass  # If already fading out, continue the process
            elif self.window_fading_in:
                self.force_fade_out()  # Fudge start time to begin fade out
            elif self.window_visible:
                self.reset_widget_colors()  # Return widget colors to 'normal'.
                self.force_fade_out()  # Begin fade out process now
            else:
                self.enter_time = 0.0  # Force window to never mount

        elif self.log_nt.action == 'enter':
            d_print('Entering widget:', str(self.widget)[-4:])

            #print("self.log_nt.action:", self.log_nt.action, str(self.widget)[-4:],
            #      self.text.split("\n")[0])  # debug self.info

            self.enter_time = self.log_nt.time
            if self.window_visible is True:
                # Same widget was entered again before fade out completed.
                pass

            if self.tool_type is 'canvas_button' and self.widget.state is 'normal':
                self.set_widget_colors()

        elif self.log_nt.action == 'motion':
            # Mouse motion in widget
            self.motion_time = self.log_nt.time
            if self.window_visible:
                self.move_window()

        elif self.log_nt.action == 'press':
            # Button pressed in widget
            # June 20, 2023 - Was not used. Now treat like 'leave' in code above
            self.press_time = self.log_nt.time

        elif self.log_nt.action == 'release':
            # Button released after press in widget
            self.release_time = self.log_nt.time

        elif self.print_error:
            print(self.who + 'set_tip_plan(): Invalid action:',
                  self.log_nt.action)

        self.fields_to_dict()
        self.tips_list[self.tips_index] = self.dict

    def force_fade_out(self):
        """ Override enter time to begin fading out now. """
        _fade_in, _fade_out = self.calc_fade_in_out()
        diff = _fade_out - self.enter_time
        self.enter_time = self.now - diff
        #print('diff:', diff)

    def move_window(self):
        """ Move window as mouse moves"""
        if self.menu_tuple:
            return  # Dropdown Menus don't have normal widget width or height
        # s = start, g = self.geometry, m = mouse, x = x-axis, y = y-axis
        sgx, sgy = self.window_geom.split('+')[1:3]
        smx, smy = self.window_mouse_xy[0:2]
        cmx, cmy = self.current_mouse_xy[0:2]
        smx_diff = int(cmx) - int(smx)  # How has mouse changed since start?
        # smy_diff = int(cmy) - int(smy)
        # Override y so it stays on same access
        smy_diff = 0
        # New geometry = start geometry + mouse change since start
        x = int(sgx) + smx_diff
        y = int(sgy) + smy_diff
        self.tip_window.wm_geometry("+%d+%d" % (x, y))

    def renumber_widget(self, event_widget):
        """ Some widget such as menus have unusual naming. For example:

            Widget:  .140408240130024.140408237557160.140408237557952

            becomes: .140408240130024.#140408240130024#140408237557160.
                      #140408240130024#140408237557160#140408237557952

            Suf. W: .0024                       .7160 .57952
            Suf. M: .0024 .#30024 #7160 .#30024 #7160 #57952
        """
        if '#' not in str(event_widget):
            return event_widget  # Normal widget formatting

        new_widget = str(event_widget).split('.')[-1]
        new_widget = new_widget.replace('#', '.')
        for self.dict in self.tips_list:
            if str(self.dict['widget']) == new_widget:
                d_print('event widget substituted. tool_type:', self.dict['tool_type'])
                return self.dict['widget']

        # Widget wasn't found
        if self.print_error:
            print('renumber_widget(): widget not found:\n', event_widget)

    def calc_fade_in_out(self):
        """ Calculate fade in and fade out time.
        :return: fade_in_time, fade_out_time:
        """
        fade_in_time = self.enter_time + float(self.visible_delay) / 1000
        # Calculate visible duration based on word count. Empty line
        # or new line count as one word.
        words = self.text.replace('\n', ' ')
        word_count = len(words.split())
        extra_time = float(word_count) * self.extra_word_span
        # If minimal visible time is larger use that
        if extra_time < self.visible_span:
            extra_time = self.visible_span 
        fade_out_time = fade_in_time + float(extra_time) / 1000
        return fade_in_time, fade_out_time

    def add_tip(self, widget, text='Pass text here', tool_type='button',
                visible_delay=None, visible_span=None, extra_word_span=None, 
                fade_in_span=None, fade_out_span=None, anchor="sw", menu_tuple=None,
                pb_alpha=None, pb_leave=None, pb_ready=None, pb_close=None):
        """ Declare Tooltip """
        CommonTip.__init__(self)            # Initialize all tip instances

        self.widget = widget                # .140599674917592.140599679077192.140599679077336
        self.text = text                    # "This button \n does that."
        self.tool_type = tool_type          # button/canvas_button/label/menu/piggy_back
        self.menu_tuple = menu_tuple        # E.G. (self.cd_top, 200, 50)
        self.pb_alpha = pb_alpha            # Piggy-back callback when alpha changes
        self.pb_leave = pb_leave            # Piggy-back callback when mouse leaves widget
        self.pb_ready = pb_ready            # Piggy-back callback when tip can be displayed
        self.pb_close = pb_close            # Piggy-back callback when tip destroyed
        # Also used by "splash" tool_type to wrapup

        self.visible_delay = visible_delay if visible_delay else VISIBLE_DELAY
        self.visible_span = visible_span if visible_span else VISIBLE_SPAN
        self.extra_word_span = extra_word_span if extra_word_span else EXTRA_WORD_SPAN
        self.fade_in_span = fade_in_span if fade_in_span else FADE_IN_SPAN
        self.fade_out_span = fade_out_span if fade_out_span else FADE_OUT_SPAN
        self.anchor = anchor

        # Bind all widgets except "piggy_back" and "splash" to common functions
        if self.tool_type is not 'piggy_back' and self.tool_type is not 'splash':
            self.widget.bind('<Enter>', self.enter)
            self.widget.bind('<Leave>', self.leave)
            self.widget.bind('<Motion>', self.motion)
            # 'piggy_back' callers will send fake <Enter> and <Leave> events
            # 'splash' callers will send fake <Enter> only
        if self.tool_type is 'button':
            self.widget.bind("<ButtonPress-1>", self.on_press)
            self.widget.bind("<ButtonRelease-1>", self.on_release)
            self.name = self.widget['text']  # Button text
        if self.name is None or self.name.strip() == "":
            self.name = self.tool_type  # Not a Button or no text in button

        self.fields_to_dict()
        i = self.check(self.widget)

        ''' Normal processing: this is a new widget '''
        if i is None:
            # Add tip dictionary to tips list
            self.tips_list.append(self.dict)
            return

        ''' i is not None: previous widget already exists so remove before new '''
        # Probably splash message being recycled. Clean up ghost windows
        old_dict = self.tips_list[i]  # Get previous widget dictionary
        self.tips_list[i] = self.dict  # Needed to prevent recursion
        # 2024-09-02 - Old splash message staying on screen
        d_print("\n" + self.who + "add_tip(): i is not None:", i)

        # 2024-09-02 - def pb_close(
        callback_function = old_dict['pb_close']
        if callback_function is not None:
            # Loudness toggle splash
            d_print("  running callback_function:", callback_function)
            callback_function()  # Tell "piggy_back" to destroy it's frame
            self.poll_tips()
        else:
            # Information splash window not linked to callback
            self.close(self.widget, flush_log=False)

        # Regular splash (not linked to callback) tip window still exists
        tip_window = old_dict['tip_window']
        if tip_window is not None:
            d_print("  destroying window:", tip_window)
            tip_window.destroy()

        # 2024-09-02 - Above fix breaks Old/New song toggle button text
        #if old_dict['pb_close'] is not None:
        #    self.reset_tip()  # pb_close will probably destroy tip next...
        #    self.pb_close()  # Tell "piggy_back" to destroy it's frame

        self.tips_list.append(self.dict)

    def reset_tip(self):
        """ After cycle is finished reset selected widget values """
        self.enter_time = self.leave_time = self.press_time = \
            self.release_time = self.current_alpha = 0.0

        self.tip_window = self.window_geom = None
        self.window_visible = self.window_fading_in = False
        self.window_fading_out = False

    def set_widget_colors(self):
        """ Set the colors for canvas object focus """

        # For canvas buttons do heavy lifting of reflecting button active state
        self.widget.state = 'active'
        self.normal_text_color = self.widget.itemcget("text_color", "fill")
        self.normal_button_color = self.widget.itemcget("button_color", "fill")

        # We know the button is always black #000000 or white #ffffff
        if self.normal_button_color == "#000000":
            # Button color is black so lighten all 25%
            new_text_color_hex = img.rgb_to_hex(img.lighten_rgb(
                img.hex_to_rgb(self.normal_text_color)))
            new_button_color_hex = img.rgb_to_hex(img.lighten_rgb(
                img.hex_to_rgb(self.normal_button_color)))
        else:
            # Button color is white so darken all 25%
            new_text_color_hex = img.rgb_to_hex(img.darken_rgb(
                img.hex_to_rgb(self.normal_text_color)))
            new_button_color_hex = img.rgb_to_hex(img.darken_rgb(
                img.hex_to_rgb(self.normal_button_color)))

        self.widget.itemconfig("button_color", fill=new_button_color_hex,
                               outline=new_button_color_hex)
        self.widget.itemconfig("text_color", fill=new_text_color_hex)

    def reset_widget_colors(self):
        """ Reset colors for canvas object losing focus """
        if self.tool_type is 'button':
            if self.widget['state'] != tk.NORMAL:
                #print(self.who + 'reset_widget_colors(): reset button state to tk.NORMAL')
                self.widget['state'] = tk.NORMAL

        if self.tool_type is 'canvas_button' and self.widget.state is 'active':
            #print('reset_widget_colors(): reset canvas button state to normal')
            self.widget.state = 'normal'
            self.widget.itemconfig("button_color", fill=self.normal_button_color,
                                   outline=self.normal_button_color)
            self.widget.itemconfig("text_color", fill=self.normal_text_color)

    # noinspection PyUnusedLocal
    def poll_tips(self):
        """ Check for fading in new tooltip and/or fading out current tooltip """
        self.now = time.time()          # Current time

        # Read event log list backwards to avoid unnecessary steps, eg leave after enter
        # means we don't have to do enter step. Empty log list when done.
        self.process_log_list()

        start_len = len(self.tips_list)
        for self.tips_index, self.dict in enumerate(self.tips_list):
            self.dict_to_fields()
            self.process_tip()
            self.fields_to_dict()
            try:
                self.tips_list[self.tips_index] = self.dict
                # Should verify it's same as old dictionary since they disappear
            except IndexError:  # list assignment index out of range
                ''' Aug 18/23 - Normal behavior for InfoCentre() tt.close() '''
                # Caused by fast clicking 'Next' song. likely tt.close() run
                #print(self.who + "poll_tips() - " +
                #      "Tip disappeared in loop!")
                now_len = len(self.tips_list)
                #print("len(self.tips_list) change 4. size at start:", start_len,
                #      "now:", now_len)
                break

    def process_tip(self):
        """ Check if window should be created or destroyed.
            Check if window is fading in or fading out and set alpha.

            TODO: Leave event is not passed to InfoCentre() unless fading in/out.

            TODO: If existing splash window exists destroy it. Otherwise it will
                  remain painted forever. Noticed on 2024-06-07 when playlist splash
                  for chron filter didn't come up and lib_top splash for playlist
                  information stays up forever.

        """
        #if not self.widget.winfo_exists():  # Oct 18/23 - enhancement
        if not self.widget.winfo_exists() and self.tool_type is not 'piggy_back' \
                and self.tool_type is not 'splash':
            # If parent closed, tool tip is irrelevant. bserve bup_view close
            d_print("Parent closed, tool tip irrelevant. bserve bup_view close",
                    str(self.widget)[-4:])
            self.reset_tip()
            return

        # Was window destroyed? E.G. by toplevel closing.
        if self.tip_window:  # 'piggy_back' doesn't use self.tip_window
            if not self.tip_window.winfo_exists():
                self.tip_window = None
                self.window_visible = False
                self.window_fading_in = False
                self.window_fading_out = False
                if self.print_error:
                    print(self.who + ".process_tip():",
                          "self.tip.window doesn't exist")
                return

        ''' Pending event to start displaying tooltip balloon? '''
        if self.enter_time == 0.0:
            if self.tip_window:
                self.tip_window.destroy()
                # Happens when leaving widget while tip window displayed
                if self.print_error:
                    print(self.who + 'process_tip(): TEMPORARY forced tip window close')
                self.tip_window = None
                self.window_visible = False
                self.window_fading_in = False
                self.window_fading_out = False
            return  # Widget doesn't have focus

        fade_in_time, fade_out_time = self.calc_fade_in_out()
        if fade_in_time > self.now + 8:
            # 2024-06-02 - Not sure why here. Perhaps testing delayed fade_in?
            if self.print_error:
                print(self.who + ".process_tip(): fade_in_time starts in:", fade_in_time - self.now)

        # Tooltip fading out?
        if self.now > fade_out_time:
            d_print("self.now > fade_out_time:", str(self.widget)[-4:],
                    "self.now:", self.now, "fade_out_time:", fade_out_time)
            # 10 occurrences - self.now: 1697681387.38   First
            #             fade_out_time: 1697681387.37
            #                  self.now: 1697681387.58
            #             fade_out_time: 1697681387.37   Tenth
            if self.window_fading_out is False:
                self.window_fading_out = True
                self.window_fading_in = False

            # What time will we hit zero alpha? (fully faded out)
            zero_alpha_time = fade_out_time + float(self.fade_out_span) / 1000

            if self.now > zero_alpha_time:
                d_print("self.now > zero_alpha_time:", str(self.widget)[-4:],
                        "self.now:", self.now, "zero_alpha_time:", zero_alpha_time)
                # d_print self.now: 1697681040.39
                #  zero_alpha_time: 1697681040.39
                # We've finished fading out
                if self.pb_close and self.tool_type == "piggy_back":
                    # "splash" tool_type will be reset further down
                    self.reset_tip()  # pb_close will probably destroy tip next...
                    self.pb_close()  # Tell "piggy_back" to destroy it's frame
                    return

                if self.tip_window is None:
                    if self.print_error:
                        print(self.who + 'process_tip(): ' +
                              'self.tip_window does not exist')
                        print('self.now:', self.now, 'zero_alpha_time:', zero_alpha_time)
                    diff = self.now - zero_alpha_time
                    if self.print_error:
                        print('diff:', diff)
                else:
                    self.tip_window.destroy()

                self.reset_tip()

                if self.pb_close:  # self.pb_close callback not using "piggy_back"
                    self.pb_close()  # "splash" tool_type callback

                return

            # Calculate fade out alpha 1.00 to 0.01
            delta = (zero_alpha_time - self.now) * 1000
            alpha = delta / self.fade_out_span
            self.update_alpha(alpha)
            return

        # Tooltip fading in?
        if self.now > fade_in_time:

            # If we've already left the button, forego the creation
            #if self.leave_time > self.enter_time:
            #    self.enter_time = 0.0  # Prevent tip window creation
            #    #print('prevent tip window creation when leave > enter')
            #    return

            # for those quirky timing situations
            diff = abs(self.leave_time - self.enter_time)
            if diff < 0.1:
                # To Correct:
                # 45:13.059 Log 'enter': 8216 x: 59 y: 6
                # 45:13.061 Log 'leave': 8216 x: 59 y: 52
                # 45:13.1039 leaving widget:  8216
                # 45:13.1041 entering widget: 8216
                self.enter_time = 0.0  # Prevent tip window creation
                d_print('prevent tip window creation when enter ~.1 of leave')
                return

            if self.window_visible is False:
                if self.tool_type is not 'piggy_back':
                    ''' 'piggy_back' has own tk.Frame and tk.Text scrollbox '''
                    self.create_tip_window()
                self.window_visible = True
                self.window_fading_in = True

            full_alpha_time = fade_in_time + float(self.fade_in_span) / 1000
            if self.now > full_alpha_time:
                # We've finished fading in
                if self.tool_type is 'piggy_back' and self.window_fading_in:
                    self.pb_ready()  # Tell "piggy_back" to display (optional)
                self.window_fading_in = False
                if self.current_alpha != 1.0:
                    self.update_alpha(1.0)
                return

            # Calculate fade in alpha 0.01 to 1.00
            delta = (full_alpha_time - self.now) * 1000
            alpha = 1.0 - (delta / self.fade_in_span)
            self.update_alpha(alpha)
            return

        # At this point we are simply waiting to fade in or fade out

    def update_alpha(self, alpha):
        """
        When tool_type is 'piggy_back', use callback. Else set window alpha.
        :param alpha: Fractional value between 0 and 100% complete
        :return: None
        """

        if alpha != self.current_alpha:
            if callable(self.pb_alpha):
                ''' There is no tip window to transition. Inform 'piggy_back' '''
                self.pb_alpha(alpha)
            else:
                ''' Adjust tip window alpha (transparency) during fade-in/out '''
                self.tip_window.attributes("-alpha", alpha)
            self.current_alpha = alpha  # Save to prevent spamming same alpha

    def create_tip_window(self):
        """ Create tooltip window at anchor position. """
        # Screen coordinates of widget  NW -- NE
        #                               |      |
        #                               SW -- SE
        widget_nw = (self.widget.winfo_rootx(), self.widget.winfo_rooty())
        widget_ne = (self.widget.winfo_rootx() + self.widget.winfo_width(),
                     widget_nw[1])
        widget_sw = (widget_nw[0], widget_nw[1] + self.widget.winfo_height())
        widget_se = (widget_ne[0], widget_sw[1])

        ''' June 15, 2023 - mserve fake ruler can be 7000 px wide on 1000 frame 
            Patch code to support new anchor "sc" (South Center) '''
        parent_name = self.widget.winfo_parent()
        # noinspection PyProtectedMember
        parent = self.widget._nametowidget(parent_name)
        parent_nw = (parent.winfo_rootx(), parent.winfo_rooty())
        parent_ne = (parent.winfo_rootx() + parent.winfo_width(),
                     parent_nw[1])
        if widget_ne[0] > parent_ne[0]:
            # Override widgets NE with parents NE
            d_print("toolkit.py Tooltips() create_tip_window() Override fake:")
            d_print("     widget_ne:", widget_ne, "with parent_ne:", parent_ne)
            # Above: widget_ne: (9442, 169) parent_ne: (4043, 169)
            widget_ne = parent_ne

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10

        #print("parent.__dict__:", parent.__dict__)
        # parent.__dict__: {
        # 'widgetName': 'ttk::frame',
        # '_w': '.140537754704352.140537752171152.140537751992440',
        # '_tclCommands': [], '_name': '140537751992440',
        # 'master': <ttk.Notebook instance at 0x7fd17ec bb290>,
        # 'tk': <tkapp object at 0x7fd17ef0a130>,
        # 'children': {
        #    '140537752005304': <ttk.Entry instance at 0x7fd17ec92ab8>,
        #    '140537751991216': <ttk.Label instance at 0x7fd17ec8f3b0>,
        #    '140537752003144': <ttk.Label instance at 0x7fd17ec92248>,
        #    '140537752052728': <ttk.Entry instance at 0x7fd17ec9e3f8>,
        #    '140537751710680': <ttk.Label instance at 0x7fd17ec4abd8>,
        #    '140537751708232': <ttk.Entry instance at 0x7fd17ec4a248>,
        #    '140537752170648': <ttk.Button instance at 0x7fd17ec bb098>}
        # }
        #print("self.widget.__dict__:", self.widget.__dict__)
        # self.widget.__dict__: {
        # 'widgetName': 'ttk::entry',
        # '_w': '.140537754704352.140537752171152.140537751992440.140537752052728',
        # '_tclCommands': ['140537752219312validate', '140537752219072enter',
        # '140537752219392leave', '140537752216992motion'], '_name': '140537752052728',
        # 'master': <ttk.Frame instance at 0x7fd17ec8f878>,
        # 'tk': <tkapp object at 0x7fd17ef0a130>,
        # 'children': {}
        # }
        #print("self.widget.widgetName:", self.widget.widgetName)  # ttk::entry
        if self.tool_type == 'menu':
            ''' Menu objects have no parent and no widget _winfo(). '''
            parent, menu_x, menu_y = self.menu_tuple
            x = parent.winfo_rootx() + menu_x
            y = parent.winfo_rooty() + menu_y
            mouse_x = x + self.widget.winfo_reqwidth()
            self.current_mouse_xy = (mouse_x, y)  # Reassign out of widget co-ords

        # Invert tooltip colors from current widget album art colors.
        #if self.tool_type is not 'canvas_button':  # comment June 15/23
        # What about 'label'?
        # 2024-09-07 ttk.Button() has no color attributes like tk.Button()
        try:
            self.fg = self.widget["background"]  # self.tool_type 'button' or
            self.bg = self.widget["foreground"]  # 'menu' using tk. NOT ttk.
        except tk.TclError:
            self.fg = self.dft_fg  # 'canvas_button', 'label', 'splash',
            self.bg = self.dft_bg  # 'piggy-back' have no fg/bg colors.
        ''' 2024-09-07 - Original code broken by ttk.Button() 
        if self.tool_type is 'button' or self.tool_type is 'menu':
            self.fg = self.widget["background"]
            self.bg = self.widget["foreground"]
        else:
            self.fg = self.dft_fg  # 'canvas_button', 'label', 'splash',
            self.bg = self.dft_bg  # and 'piggy-back' have no fg/bg colors.
        '''
        if self.fg is None or self.fg == "":  # 2024-12-29
            # When ttk.Label, ttk.Frame and ttk.Entry is used the colors are "".
            self.fg = self.dft_fg
            #print("self.tool_type:", self.tool_type, "self.fg:", self.fg, "self.bg:",
            #      self.bg,
            #      "self.dft_fg:", self.dft_fg, "self.dft_bg:", self.dft_bg)
        if self.bg is None or self.bg == "":
            self.bg = self.dft_bg

        #self.tip_window = tw = tk.Toplevel(self.widget)  # Original sample code...
        if self.menu_tuple:
            # For 'menu' the self.widget is believed to be top-left monitor
            self.tip_window = tk.Toplevel(parent)
            self.tip_window.wm_overrideredirect(1)  # Undecorated
            self.tip_window.wm_geometry("+%d+%d" % (x, y))
            parent.update()
        else:
            self.tip_window = tk.Toplevel(self.widget)
            self.tip_window.wm_overrideredirect(1)   # Undecorated
            self.tip_window.wm_geometry("+%d+%d" % (x, y))

        # Track mouse movements to change window geometry
        self.window_mouse_xy = self.current_mouse_xy

        # https://www.tcl.tk/man/tcl8.6/TkCmd/wm.htm#M9
        # self.tip_window['background'] = self.bg  # Aug 20/23 already commented!
        ''' Aug 20/23 - Add if check for 'NoneType' error '''
        if self.tip_window and self.bg:
            self.tip_window['background'] = self.bg  # original below commented
            #   File "/home/rick/python/toolkit.py", line 2599, in create_tip_window
            #     self.tip_window['background'] = self.bg
            # TypeError: 'NoneType' object does not support item assignment
        # https://stackoverflow.com/a/52123172/6929343

        self.tip_window.wm_attributes('-type', 'tooltip')  # only works X11 and not all distros

        d_print('created self.tip_window:', self.tip_window)
        d_print('w.wm_geometry("+%d+%d" % (x, y)):', "+%d+%d" % (x, y))

        ''' Below MAC code Throws py charm error: access to protected 'tw._w' '''
        try:
            # For Mac OS
            # noinspection PyProtectedMember
            tw.tk.call("::tk::unsupported::MacWindowStyle",
                       "style", tw._w,
                       "help", "noActivates")
        except NameError:  # global name 'tw' is not defined
            pass

        # TODO: Create Frame for border color. Then place label into frame. See:
        #       https://www.geeksforgeeks.org/how-to-change-border-color-in-tkinter-widget/
        border_color = tk.Frame(self.tip_window, background=self.fg)
        #label = tk.Label(tw, text=self.text, justify=tk.LEFT,
        label = tk.Label(border_color, text=self.text, justify=tk.LEFT,
                         background=self.bg, foreground=self.fg, relief=tk.SOLID,
                         borderwidth=2, pady=10, padx=10, font=(None, g.MON_FONTSIZE))
        label.pack(padx=2, pady=2)
        border_color.pack(padx=10, pady=10)

        self.tip_window.attributes("-alpha", 0)  # Start at 0%
        self.tip_window.update_idletasks()
        if not self.menu_tuple:
            self.window_geom = self.tip_window.wm_geometry()
            self.override_window_geom(widget_nw, widget_ne, widget_se, widget_sw)
        d_print('tip_window created at:', "+%d+%d" % (x, y), 'for:', self.widget)

    def override_window_geom(self, nw, ne, se, sw):
        """ Change self.window_geom wxh+x+y depending on anchor point to widget.
            Requires that tooltip window has already been created such that
            width and height are known.

            Pass the widget's (parent's) nw, ne, se and sw coordinates

            DISTANCE_FROM_WIDGET_X = 20 how far left when ne or se, else right
            DISTANCE_FROM_WIDGET_Y = 10 how far down when sw or se, else up
        """
        w, h, old_x, old_y = re.split(r'\D+', self.window_geom)
        # print('tip_window started at:', self.window_geom, 'w:', w, 'h:', h)
        w = int(w)
        h = int(h)
        # June 15/23 - Widget's width to calculate center
        wid_w = ne[0] - nw[0]
        #print("wid_w:", wid_w)  # 7000 for mserve.py fake self.banner_btn
        x = y = 0  # Bogus defaults to make pycharm error checker happy.

        if self.anchor == "nw":
            x = nw[0]  # Northwest of parent x, y
            y = nw[1] - h - 20  # 20 px above parent's top
        elif self.anchor == "ne": 
            x = ne[0] - w  # Northeast of parent x2, y
            y = nw[1] - h - 20  # 20 px below parent's top
        elif self.anchor == "se":
            x = se[0] - w  # Southeast of x2, y2
            y = se[1] + 20   # 20 px below parent's bottom
        elif self.anchor == "sw":
            x = sw[0]  # Southwest of parent x, y2
            y = sw[1] + 20   # 20 px below parent's bottom
        elif self.anchor == "sc":
            off = (wid_w - w) / 2  # calculate center
            off = off if off > 0 else 0
            x = sw[0] + off  # South Centered below parent
            y = sw[1] + 20  # 20 px below parent's bottom
        elif self.anchor == "top":
            off = (wid_w - w) / 2  # calculate center
            off = off if off > 0 else 0
            x = nw[0] + off  # bottom centered inside parent
            y = nw[1] + 20  # 20 px below parent's top
        elif self.anchor == "bottom":
            off = (wid_w - w) / 2  # calculate center
            off = off if off > 0 else 0
            x = sw[0] + off  # bottom centered inside parent
            y = sw[1] - h - 20  # 20 px above parent's bottom
        elif self.print_error:
            print_trace()
            print(self.who + 'override_window_geom(): ')
            print('Bad self.anchor value:', self.anchor)
            exit()
        self.tip_window.wm_geometry("+%d+%d" % (x, y))
        self.window_geom = self.tip_window.wm_geometry()

    def set_text(self, widget, text, visible_delay=None, visible_span=None, 
                 extra_word_span=None, fade_in_span=None, fade_out_span=None):
        """ Change Tooltip text and duration timings """

        visible_delay = visible_delay if visible_delay else VISIBLE_DELAY
        visible_span = visible_span if visible_span else VISIBLE_SPAN
        extra_word_span = extra_word_span if extra_word_span else EXTRA_WORD_SPAN
        fade_in_span = fade_in_span if fade_in_span else FADE_IN_SPAN
        fade_out_span = fade_out_span if fade_out_span else FADE_OUT_SPAN

        """ Text and fade variables changed by caller """
        for i, s in enumerate(self.tips_list):
            if s['widget'] == widget:
                s['text'] = text
                s['visible_delay'] = visible_delay
                s['visible_span'] = visible_span
                s['extra_word_span'] = extra_word_span
                s['fade_in_span'] = fade_in_span
                s['fade_out_span'] = fade_out_span
                s[i] = s
                # TODO: When text expands/shrinks line count
                #       we need to
                return
  
        if self.print_error:
            print_trace()          
            print(self.who + 'set_text(): tip not found')

    def get_dict(self, widget):
        """ Debugging tool for external caller to get a widget's dictionary """
        for s in self.tips_list:
            if s['widget'] == widget:
                return s
        if self.print_error:
            print(self.who + 'get_dict(): self.dict for "widget" not found',
                  widget)

    def toggle_position(self, widget):
        """ Flip anchor from North->South or from South->North
            If tip window's position is below widget, set above. 
            If above, then set below. Used when button bar moves to middle
            of window to bottom and vice versa. E.G. mserve chronology.
        """
        for i, s in enumerate(self.tips_list):
            #if s['widget'] == widget:  # process single widget
            if str(s['widget']).startswith(str(widget)):  # process all inside frame
                if s['anchor'] == "nw":
                    s['anchor'] = "sw"
                elif s['anchor'] == "ne":
                    s['anchor'] = "se"
                elif s['anchor'] == "se":
                    s['anchor'] = "ne"
                elif s['anchor'] == "sw":
                    s['anchor'] = "nw"
                self.tips_list[i] = s
                return

        if self.print_error:
            print_trace()
            print(self.who + 'toggle_position(): widget not found', widget)
        exit()

    def enter(self, event):
        """ Mouse has entered widget bounding box. """
        d_print("Log 'enter':", str(event.widget)[-4:], "x:", event.x, "y:", event.y)
        # print("scope of event:", event)  # scope of event: <Tkinter.Event instance at 0x7ffb7aec6dd0>
        self.log_event('enter', event.widget, event.x, event.y)

    def leave(self, event):
        """
        Enter has 500 ms delay so leave may come before tooltip displayed.

        TEST: When leaving early button remains "active" so force to "normal".
        """
        d_print("Log 'leave':", str(event.widget)[-4:], "x:", event.x, "y:", event.y)
        self.log_event('leave', event.widget, event.x, event.y)
        if self.pb_leave:
            # print("Calling pb_leave():", str(event.widget)[-4:])  # debug self.info
            self.pb_leave()  # Let "piggy_back" know mouse left parent widget

    def motion(self, event):
        """ Mouse is moving over widget.
            Tip window follows mouse along x-axis with y-axis fixed.
            This generates a lot of output when printing debug information...
        """
        #d_print('MOVES:', str(event.widget)[-4:], event.x, event.y)
        self.log_event('motion', event.widget, event.x, event.y)
        return

    def on_press(self, event):
        """ Widget type is button and it was just pressed """
        d_print('PRESS:', str(event.widget)[-4:], event.x, event.y)
        self.log_event('press', event.widget, event.x, event.y)

    def on_release(self, event):
        """ Widget type is button and mouse click was just released.
            A leave event is automatically generated but we may no longer
            be in the same widget.
        """
        d_print('REL_S:', str(event.widget)[-4:], event.x, event.y)
        self.log_event('release', event.widget, event.x, event.y)

    def close(self, widget, flush_log=True):
        """ When a window closes, all tooltips in it must be removed.
            Can be called externally.  Extra steps required to ensure
            window isn't visible.  Caller needs top.update() afterwards.

        :param widget: either button or parent / grandparent of button. 
        :param flush_log: empty self.log_list for all events.
        """
        new_list = []
        start = len(self.tips_list)  # Compare length at end to ensure found

        # Losing last dictionary?
        old_last = self.tips_list[-1]

        for old_dict in self.tips_list:
            if not str(old_dict['widget']).startswith(str(widget)):
                new_list.append(old_dict)
                continue
            d_print("Closing widget:", str(widget)[-4:])
            #print("Closing widget:", widget)
            tip_window = old_dict['tip_window']
            if tip_window is not None:
                tip_window.destroy()
            # 2024-05-06 was getting left over window self.play_top.update() fixes

        #diff = len(self.tips_list) - len(new_list)
        #print(diff, 'Tooltips removed on close')
        self.tips_list = []
        self.tips_list = new_list

        # Losing last dictionary?
        new_last = self.tips_list[-1]
        if old_last != new_last:
            #print("last dictionary changed:")
            #print(old_last)
            #print(new_last)
            pass
        end = len(self.tips_list)
        if start == end:
            if self.print_error:
                print("\n" + self.who + "close() called with no effect:", start)
                print_trace()
                print("Widget:", widget)
        if flush_log:
            self.log_list = []  # Flush out log list for new events

    def check(self, widget, prefix_only=True):
        """ Check if widget in ToolTips()
        :param widget: Button (or another widget type) to check.
        :param prefix_only: Check for members of window or button frame group.
        :returns: Tooltip dictionary if found, else type 'None' """
        for i, s in enumerate(self.tips_list):
            if str(s['widget']) == str(widget):
                return i  # Full match passes
            elif prefix_only and str(s['widget']).startswith(str(widget)):
                return i  # Test prefix and it matches
        return None

    def line_dump(self):
        """ Dump out selected data from tooltips list in printed format.
            self.dict['widget'] = self.widget                           # 01
            self.dict['current_state'] = self.current_state             # 02
            self.dict['tip_window'] = self.tip_window                   # 15
            self.dict['text'] = self.text                               # 16
            self.dict['window_geom'] = self.window_geom                 # 17
        """

        lines = list()  # PyCharm error when using 'lines = []'
        lines.append('Tooltips Line Dump - ' +
                     str(len(self.tips_list)) + ' Tip Dictionaries')
        lines.append('Tip#  Suf.  Name - Text')
        lines.append('====  ====  ' + '=' * 78)
        s = "            "

        for i, tips_dict in enumerate(self.tips_list):
            line  = "#" + '{:3d}'.format(i + 1)
            line += "  " + str(tips_dict['widget'])[-4:]  # Short name suffix
            line += "  " + tips_dict['name']
            line += "  -  " + tips_dict['text'].splitlines()[0]  # First line only
            lines.append(line)
            line = s + str(tips_dict['widget'])
            lines.append(line)
            # Following stuff is all Null so check before including
            if tips_dict['tip_window'] is not None:
                line  = s + "tip_window: " + str(tips_dict['tip_window'])[-4:]
                line += "  window_geom: " + str(tips_dict['window_geom'])
                line += "  current_state: " + str(tips_dict['current_state'])
                lines.append(line)  # almost always null

        return lines


def d_print(*args):
    """ Print debugging lines when D_PRINT is true
        Prepend current time with four decimal places (chop 2 places off)
    """
    if D_PRINT is True:
        prt_time = datetime.datetime.now().strftime("%M:%S.%f")[:-2]
        print(prt_time, *args)


# End of: toolkit.py
