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
#       Jan. 01 2024 - computer_bytes(size) converts '4.0K blah' to 4000, etc.
#       Mar. 23 2024 - Save custom views in DictTreeview() class
#
#==============================================================================

# identical imports in mserve

# Must be before tkinter and released from interactive. Required to insert
# from clipboard.
#import gtk                     # Doesn't work. Use xclip instead
#gtk.set_interactive(False)
import copy

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
import traceback            # To display call stack (functions that got us here)
import locale               # Use decimals or commas for float remainder?

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
                print("toolkit.py ToolTips.list_widgets(): Not a tkinter Frame!")

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
                print("toolkit.py ToolTips.list_widgets(): Not a tkinter Label!",
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
    return "toolkit.py ToolTips.list_widgets(): Unknown error?"


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
    def __init__(self, toplevel):

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
        self.toplevel.bind("<FocusIn>", self.raise_children)

    def raise_children(self, *_args):
        """ Focus in on parent. Focus in and lift the children up in the
            order they were registered.
        """
        if not len(self.window_list):
            return
        _who = self.who + "raise_children():"
        for win_dict in self.window_list:
            if self.check_candidacy(win_dict):
                win_dict['widget'].lift()
                win_dict['widget'].focus_force()

    def move_children(self, x_off, y_off):
        """ Focus in on parent. Focus in and lift the children up in the
            order they were registered.
        """
        if not len(self.window_list):
            return
        _who = self.who + "move_children():"
        if True is False:
            print("\n" + _who, " | x_off:", x_off, " | y_off:", y_off)
        for win_dict in self.window_list:
            if self.check_candidacy(win_dict):
                _w, _h, x, y = self.geometry(win_dict['widget'])
                new_x = x + x_off
                new_y = y + y_off
                geom = "+" + str(new_x) + "+" + str(new_y)
                win_dict['widget'].geometry(geom)

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
        _who = self.who + "drag_window"
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
        _who = self.who + "register_child"
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
        _who = self.who + "unregister_child"
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

    def destroy_all(self, tt=None):
        """ When caller doesn't know the window widgets at close time """
        if not len(self.window_list):
            return

        _who = self.who + "destroy_all():"
        #print(_who, "self.window_list:", self.window_list)
        for win_dict in self.window_list:
            window = win_dict['widget']
            if tt:
                if tt.check(window):
                    tt.close(window)
            window.destroy()

        self.window_list = []

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

        print("No key for widget:", widget)

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
            text.tag_configure("red", foreground="#ff0000")
            text.highlight_pattern("this should be red", "red")
        
            The highlight_pattern method is a simplified python
            version of the tcl code at http://wiki.tcl.tk/3246
    """

    def __init__(self, *args, **kwargs):
        scrolledtext.ScrolledText.__init__(self, *args, **kwargs)

    def highlight_pattern(self, pattern, tag, start="1.0", end="end",
                          regexp=False):
        """ Apply the given tag to all text that matches the given pattern

        If 'regexp' is set to True, pattern will be treated as a regular
        expression according to Tcl regular expression syntax.
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
            self.tag_add(tag, "matchStart", "matchEnd")

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
                 tt=None):

        self.tree_dict = tree_dict          # Data dictionary
        self.toplevel = toplevel
        self.master_frame = master_frame    # Master frame for treeview frame
        self.show = show                    # 'tree' or 'headings'
        self.attached = OrderedDict()       # Rows attached, detached, skipped
        self.highlight_callback = highlight_callback
        self.sql_type = sql_type            # E.G. "sql_music"
        self.cfg_name = "cfg_" + sql_type
        self.name = name                    # E.G. "SQL Music Table"
        self.force_close = force_close
        self.tt = tt                        # Tool tips

        self.cfg = sql.Config()             # SQL user configurations

        self.tree = None                    # tk.Treeview created here in master

        # ChildWindows() moves children with toplevel and keeps children on top.
        self.win_grp = ChildWindows(self.toplevel)
        self.hdr_top = None                 # To display column details
        self.hdr_top_is_active = None       # hdr also used to display sql row
        self.scrollbox = None               # CustomScrolltext w/patterns
        self.hic_top = None                 # Heading insert column

        # xxx_is_active in .close() and __init__
        self.rsd_top_is_active = None       # Row SQL details
        self.hcd_top_is_active = None       # Header Column details
        self.hic_top_is_active = None       # Header insert column
        self.hdc_top_is_active = None       # Header delete column
        self.hco_top_is_active = None       # Header change column order
        self.hrc_top_is_active = None       # Header rename column

        # 2024-03-27 last_row will be phased out. use tree.has_tag() instead.
        self.last_row = None                # Used for removing highlight bar
        # 2024-03-27 col_count will be phased out
        self.col_count = 20                 # Set<20 for debug printing

        # TEST font families - Have to move out of sql.py to here Fonts() class
        #self.cfg.show_fonts(self.toplevel)

        ''' Use SQL configuration for column order, width and heading '''
        #sql_key = [self.cfg_name, 'sql_treeview', 'column', 'custom']
        sql_key = [self.cfg_name, 'sql_treeview', 'dict_treeview', 'custom']
        self.use_custom = self.cfg.check_cfg(sql_key)
        if self.use_custom:
            self.tree_dict = self.cfg.get_cfg(sql_key)
            #print_dict_columns(self.tree_dict)
            '''
            parts_list = self.cfg.get_cfg(sql_key)
            columns = []  # displaycolumns
            for part in parts_list:
                column, width, heading = part
                columns.append(column)
                #print("part:", part)
                d = get_dict_column(column, self.tree_dict)
                d['width'] = width
                d['heading'] = heading
                save_dict_column(column, self.tree_dict, d)
            select_dict_columns(columns, self.tree_dict)  # Set 'select_order'
            '''
        ''' Auto-generate columns if not passed as parameter '''
        if len(columns) == 0:
            self.columns = []
            for d in self.tree_dict:
                if d['select_order'] == 0:
                    continue  # Not selected
                name_off = d['select_order'] - 1
                while len(self.columns) - 1 < name_off:
                    # Fill holes and new ending name with "Reserved" string
                    self.columns.append("Reserved")
                self.columns[name_off] = d['column']  # Tk Column Name
            #print("columns_list:", columns_list)
        else:
            self.columns = list(columns)

        ''' Passed tuple or autogenerated display columns list'''
        displaycolumns = tuple(self.columns)

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

        tk.Grid.rowconfigure(self.frame, 0, weight=1)
        tk.Grid.columnconfigure(self.frame, 0, weight=1)
        self.frame.grid(row=0, column=0, sticky=tk.NSEW)

        ''' CheckboxTreeview List Box, Columns and Headings '''
        self.tree = CheckboxTreeview(
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

        # DEBUGGING -  Dump out column values
        #for col in columns:
        #    print(self.tree.column(col))
        #    print(self.tree.heading(col))

        style = ttk.Style()
        # print('style.theme_names():', style.theme_names())
        # OUTPUT: style.theme_names(): ('clam', 'alt', 'default', 'classic')
        # Each color requires unique name for treeview style
        style.configure(style_name + ".Heading", font=(None, g.MED_FONT),
                        rowheight=int(g.MED_FONT * 2.2))
        self.tree.configure(style=style_name + ".Heading")

        row_height = int(g.MON_FONTSIZE * 2.2)
        style.configure(style_name, font=(None, g.MON_FONTSIZE),
                        rowheight=row_height, foreground=fg, background=bg,
                        fieldbackground=fbg)
        self.tree.configure(style=style_name)

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
            NOTE: Formatting integers "{:,}" and floats "{0:,.0f}"
        """
        if row is None:
            print('toolkit.py - dict_tree.insert() - row is required parameter')
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
        except tk.TclError:  # Item L001 already exists
            # update existing row into treeview
            self.tree.item(iid, values=values, tags=tags)

        ''' highlight row as mouse traverses across treeview '''
        self.tree.tag_bind(iid, '<Motion>', self.highlight_row)

    def close(self, *_args):
        """ Parent is closing toplevel containing the treeview.

            Compare self.tree_dict (list of column dictionaries) to
            Tk Treeview Column Values: displaycolumns & each column
            width.

            Common close for sql_music, sql_history and sql_location.
            Compare default dictionary to current treeview columns to see
            if any changes to:
                'displaycolumns' column order
                'width' column width
                'heading' column heading text

        :return: 1 new custom view created, 2 existing custom view updated
        """

        # Close Pretty column details or Pretty SQL Row details
        if self.hdr_top:  # Need to get a better name!
            self.pretty_close()  # This unregisters child as well

        self.win_grp.destroy_all()  # Unregister & destroy all child windows

        # xxx_is_active in .close() and __init__
        self.rsd_top_is_active = None       # Row SQL details
        self.hcd_top_is_active = None       # Header Column details
        self.hic_top_is_active = None       # Header insert column
        self.hdc_top_is_active = None       # Header delete column
        self.hco_top_is_active = None       # Header change column order
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

    def pretty_display(self, title, width, height, x=None, y=None):
        """ Create new window top-left of parent window with g.PANEL_HGT padding or
            at passed x,y coordinates.

            Before calling:
                Create pretty data dictionary using tree column data dictionary
                Or entire treeview data dictionary (E.G. sql.music_treeview)
            After calling / usage:
                create_window(title, width, height, top=None)
                pretty.scrollbox = self.scrollbox
                # If text search, highlight word(s) in yellow
                if self.mus_search is not None:
                    # history doesn't have support. Music & history might both be open
                    if self.mus_search.entry is not None:
                        pretty.search = self.mus_search.entry.get()
                sql.tkinter_display(pretty)

            When Music Location Tree calls from show_raw_metadata it passes
            top=self.lib_top. In this case not called from SQL Music Table
            viewer.

            TODO: Instead of parent guessing width, height it would be nice
                  to pass a maximum and reduce size when text box has extra
                  white space.
        """
        if self.hdr_top_is_active:
            self.hdr_top.lift()
            return

        self.hdr_top = tk.Toplevel()  # New window for data dictionary display.
        self.hdr_top_is_active = True
        self.win_grp.register_child(title, self.hdr_top)

        if x and y:
            xy = (x, y)  # passed as parameters
        else:
            # Should always be passed x,y coordinates but just in case
            print("coordinates not passed.")
            xy = (self.toplevel.winfo_x() + g.PANEL_HGT,  # Use parent's top left position
                  self.toplevel.winfo_y() + g.PANEL_HGT)

        self.hdr_top.minsize(width=g.BTN_WID * 10, height=g.PANEL_HGT * 4)
        self.hdr_top.geometry('%dx%d+%d+%d' % (width, height, xy[0], xy[1]))
        self.hdr_top.title(title)
        self.hdr_top.configure(background="Gray")
        self.hdr_top.columnconfigure(0, weight=1)
        self.hdr_top.rowconfigure(0, weight=1)

        ''' Set program icon in taskbar '''
        #Piggy back onto parent window as this window is raised overtop oo parent
        #img.taskbar_icon(self.hdr_top, 64, 'white', 'lightskyblue', 'black', char="S")

        ''' Bind <Escape> to close window '''
        self.hdr_top.bind("<Escape>", self.pretty_close)
        self.hdr_top.protocol("WM_DELETE_WINDOW", self.pretty_close)

        ''' frame1 - Holds scrollable text entry '''
        frame1 = ttk.Frame(self.hdr_top, borderwidth=g.FRM_BRD_WID,
                           padding=(2, 2, 2, 2), relief=tk.RIDGE)
        frame1.grid(column=0, row=0, sticky=tk.NSEW)
        bs_font = (None, g.MON_FONTSIZE)  # bs = bserve, ms = mserve

        ''' Scrollable textbox to show selections / ripping status '''
        text = ("Retrieving SQL data.\n" +
                "If this screen can be read, there is a problem.\n\n" +
                "TIPS:\n\n" +
                "\tRun in Terminal: 'm' and check for errors.\n\n" +
                "\twww.pippim.com\n\n")

        # Text padding not working: https://stackoverflow.com/a/51823093/6929343
        self.scrollbox = CustomScrolledText(
            frame1, state="normal", font=bs_font, borderwidth=15, relief=tk.FLAT)
        self.scrollbox.configure(background="#eeeeee")  # Replace "LightGrey"
        self.scrollbox.insert("end", text)
        self.scrollbox.grid(row=0, column=1, padx=3, pady=3, sticky=tk.NSEW)
        tk.Grid.rowconfigure(frame1, 0, weight=1)
        tk.Grid.columnconfigure(frame1, 1, weight=1)

        self.scrollbox.tag_config('red', foreground='Red')
        self.scrollbox.tag_config('blue', foreground='Blue')
        self.scrollbox.tag_config('green', foreground='Green')
        self.scrollbox.tag_config('black', foreground='Black')
        self.scrollbox.tag_config('yellow', background='Yellow')
        self.scrollbox.tag_config('cyan', background='Cyan')
        self.scrollbox.tag_config('magenta', background='Magenta')

        self.scrollbox.highlight_pattern(u'TIPS:', 'red')

        #self.scrollbox.config(tabs=("2m", "40m", "50m"))  # Apr 9, 2023
        self.scrollbox.config(tabs=("2m", "65m", "80m"))  # Apr 27, 2023
        self.scrollbox.tag_configure("margin", lmargin1="2m", lmargin2="65m")
        # Fix Control+C  https://stackoverflow.com/a/64938516/6929343
        self.scrollbox.bind("<Button-1>", lambda event: self.scrollbox.focus_set())

    def pretty_close(self, *_args):
        """ Close window painted by the create_window() function """
        if self.hdr_top is None:
            return
        self.win_grp.unregister_child(self.hdr_top)
        #self.tt.close(self.hdr_top)  # Close tooltips (There aren't any yet)
        self.scrollbox.unbind("<Button-1>")
        self.hdr_top_is_active = False
        self.hdr_top.destroy()
        self.hdr_top = None
        iid_list = self.tree.tag_has("menu_sel")
        for iid in iid_list:
            tv_tag_remove(self.tree, iid, "menu_sel")

    def rename_column_heading(self, column_name, new):
        """ Called from show_sql_common_click() -> view_sql_heading_menu()

            Display current column heading and prompt for new name.

            :param column_name: tkinter column name from displaycolumns.
            :param new: New tkinter column heading.
        """

        # Update treeview with new column heading
        self.tree.heading(column_name, text=new)
        self.tree.update_idletasks()

        # Update treeview dictionary and save custom configuration for next time
        column_dict = get_dict_column(column_name, self.tree_dict)
        column_dict['heading'] = new  # unicode testing needed?
        save_dict_column(column_name, self.tree_dict, column_dict)
        sql_key = [self.cfg_name, 'sql_treeview', 'dict_treeview', 'custom']
        self.cfg.insert_update_cfg(sql_key, self.name, self.tree_dict)

    def insert_column(self, column_name, x, y):
        """ Called from mserve.py view_sql_button_3() -> view_sql_heading_menu()

            Right click (button-3) performed on tkinter column heading.

            Display combobox of unselected columns to pick from.

            Show current column and prompt whether to insert before/after.

            :param column_name: tkinter column name from displaycolumns.
            :param x: x position 24 pixels left of mouse pointer.
            :param y: y position 24 pixels below mouse pointer.
        """
        if self.hic_top_is_active:
            return

        title = self.name + " - Add new column to view - mserve"
        hic_top = tk.Toplevel()  # New window for data dictionary display.
        self.hic_top_is_active = True

        hic_top.minsize(width=g.BTN_WID * 10, height=g.PANEL_HGT * 4)
        hic_top.geometry('%dx%d+%d+%d' % (665, 200, x, y))
        hic_top.title(title)
        hic_top.configure(background="WhiteSmoke")
        hic_top.columnconfigure(0, weight=1)
        hic_top.rowconfigure(0, weight=1)

        ''' Register child window for raising & moving with parent '''
        self.win_grp.register_child('insert column', hic_top)

        column_dict = get_dict_column(column_name, self.tree_dict)
        highlight_column = column_dict['heading']
        # Get real column width, heading, etc. from self.tree.column / .heading
        unselected_list = []
        combo_list = []
        before_after = ["Before '" + highlight_column + "' column",
                        "After '" + highlight_column + "' column"]

        # Find all unselected columns
        for d in self.tree_dict:
            if d['select_order'] == 0:
                unselected_list.append(d)  # the keys
                # Because 'heading' can be renamed, user can create duplicates
                combo_list.append(d['heading'] + " - (" + d['column'] + ")")

        ''' frame1 - Holds combox text entry subclasses '''
        # ttk.Frame doesn't allow bg color, only style = 
        frame1 = tk.Frame(hic_top, borderwidth=18,
                          relief=tk.FLAT, bg="WhiteSmoke")
        frame1.grid(column=0, row=0, sticky=tk.NSEW)

        # Credit: https://stackoverflow.com/a/72195664/6929343
        tk.Label(frame1, text="Column to add:", bg="WhiteSmoke", padx=10, pady=10).\
            grid(column=0, row=0)
        combo_col_var = tk.StringVar()
        # https://stackoverflow.com/a/46507359/6929343
        combo_col_keep = combo_col_var.get()  # Keep from garbage collector
        combo_col = ttk.Combobox(frame1, textvariable=combo_col_keep, 
                                 state='readonly', width=30)
        combo_col['values'] = combo_list
        combo_col.current(0)
        combo_col.grid(column=1, row=0, padx=20)

        tk.Label(frame1, text="Insert position:", bg="WhiteSmoke", padx=10, pady=10).\
            grid(column=0, row=1)
        combo_pos_var = tk.StringVar()
        combo_pos_keep = combo_pos_var.get()
        combo_pos = ttk.Combobox(frame1, textvariable=combo_pos_keep, 
                                 state='readonly', width=30)
        combo_pos['values'] = before_after
        combo_pos.current(0)
        combo_pos.grid(column=1, row=1, padx=20)

        def close(*_args):
            """ close the window """
            if not self.hic_top_is_active:
                return
            self.win_grp.unregister_child(hic_top)
            # self.tt.close(hic_top)  # Close tooltips (There aren't any yet)
            self.hic_top_is_active = False
            hic_top.destroy()

        def insert_apply():
            """ Apply combox boxes. """
            if not self.hic_top_is_active:
                return

            combo_col_new = combo_col.get()
            combo_pos_new = combo_pos.get()

            new_ndx = combo_list.index(combo_col_new)
            new_column = unselected_list[new_ndx]['column']

            # New displaycolumns with inserted column
            displaycolumns = list(self.tree['displaycolumns'])
            position = displaycolumns.index(column_name)  # parameter passed
            if "After" in combo_pos_new:
                position += 1
            displaycolumns.insert(position, str(new_column))  # convert from unicode

            # Update treeview with new columns. These are reread by force_close()
            select_dict_columns(displaycolumns, self.tree_dict)
            self.tree['columns'] = displaycolumns
            self.tree['displaycolumns'] = displaycolumns
            self.columns = displaycolumns  # extra insurance

            # Set selected column headings text
            for d2 in self.tree_dict:
                if d2['select_order'] > 0:
                    self.tree.heading(d2['column'], text=d2['heading'])

            close()  # Close our window
            self.force_close()  # Close toplevel window

        ttk.Separator(frame1, orient='horizontal').\
            grid(column=0, row=2, columnspan=2, sticky=tk.EW)
        frame1.grid_rowconfigure(2, minsize=30)

        button1 = tk.Button(frame1, text="Apply", pady=5, command=insert_apply)
        button1.grid(column=0, row=3)
        button2 = tk.Button(frame1, text="Cancel", pady=5, command=close)
        button2.grid(column=1, row=3)

        ''' Bind <Escape> to close window '''
        hic_top.bind("<Escape>", close)
        hic_top.protocol("WM_DELETE_WINDOW", close)

    def delete_column(self, column_name, x, y):
        """ Called from mserve.py view_sql_button_3() -> view_sql_heading_menu()

            Right click (button-3) performed on tkinter column heading.

            Prompt to delete the current column from view.

            :param column_name: tkinter column name from displaycolumns.
            :param x: x position 24 pixels left of mouse pointer.
            :param y: y position 24 pixels below mouse pointer.
        """
        if self.hdc_top_is_active:
            return

        title = self.name + " - Remove column from view - mserve"
        hdc_top = tk.Toplevel()
        self.hdc_top_is_active = True

        hdc_top.minsize(width=g.BTN_WID * 10, height=g.PANEL_HGT * 4)
        hdc_top.geometry('%dx%d+%d+%d' % (680, 290, x, y))
        hdc_top.title(title)
        hdc_top.configure(background="WhiteSmoke")
        hdc_top.columnconfigure(0, weight=1)
        hdc_top.rowconfigure(0, weight=1)

        ''' Register child window for raising & moving with parent '''
        self.win_grp.register_child('delete column', hdc_top)

        column_dict = get_dict_column(column_name, self.tree_dict)
        highlight_column = column_dict['heading']

        ''' frame1 - Holds text '''
        frame1 = tk.Frame(hdc_top, borderwidth=18,
                          relief=tk.FLAT, bg="WhiteSmoke")
        frame1.grid(column=0, row=0, sticky=tk.NSEW)

        text = "Removing some columns like 'Lyrics' will "
        text += "disable some buttons.\n\n"
        text += "After clicking 'Apply' the View SQL window "
        text += "will close.\n\n"
        text += "Click 'Apply' to remove the column '" + highlight_column + "'.\n"
        tk.Label(frame1, text=text, bg="WhiteSmoke", pady=20).\
            grid(column=0, row=0)

        def close(*_args):
            """ close the window """
            if not self.hdc_top_is_active:
                return

            self.win_grp.unregister_child(hdc_top)
            # self.tt.close(hdc_top)  # Close tooltips (There aren't any yet)
            self.hdc_top_is_active = False
            hdc_top.destroy()

        def delete_apply():
            """ Delete current column from treeview. """
            if not self.hdc_top_is_active:
                return

            # New displaycolumns with inserted column
            displaycolumns = list(self.tree['displaycolumns'])
            position = displaycolumns.index(column_name)  # parameter passed
            displaycolumns.remove(position)

            # Update treeview with new columns. These are reread by force_close()
            select_dict_columns(displaycolumns, self.tree_dict)
            self.tree['columns'] = displaycolumns
            self.tree['displaycolumns'] = displaycolumns
            self.columns = displaycolumns  # extra insurance

            # Set selected column headings text
            for d2 in self.tree_dict:
                if d2['select_order'] > 0:
                    self.tree.heading(d2['column'], text=d2['heading'])

            close()  # Close our window
            self.force_close()  # Close toplevel window

        ttk.Separator(frame1, orient='horizontal').\
            grid(column=0, row=2, sticky=tk.EW)
        frame1.grid_rowconfigure(2, minsize=30)

        button1 = tk.Button(frame1, text="Apply", padx=25, command=delete_apply)
        button1.grid(column=0, row=3, ipadx=20, sticky=tk.W)
        button2 = tk.Button(frame1, text="Cancel", padx=25, command=close)
        button2.grid(column=0, row=3, ipadx=20, sticky=tk.E)

        ''' Bind <Escape> to close window '''
        hdc_top.bind("<Escape>", close)
        hdc_top.protocol("WM_DELETE_WINDOW", close)

    def column_order(self, column_name, x, y):
        """ Called from mserve.py view_sql_button_3() -> view_sql_heading_menu()

            Right click (button-3) performed on tkinter column heading.

            Display combobox of columns to pick from.
            Display spinbox to change order
            Dynamically show column order with each spinbox action.

            Apply changes to self.tree['displaycolumns'] and set tree_dict

            :param column_name: tkinter column name from displaycolumns.
            :param x: x position 24 pixels left of mouse pointer.
            :param y: y position 24 pixels below mouse pointer.
        """
        if self.hco_top_is_active:
            return

        title = self.name + " - Change column order - mserve"
        hco_top = tk.Toplevel()  # New window for data dictionary display.
        self.hco_top_is_active = True

        hco_top.minsize(width=g.BTN_WID * 10, height=g.PANEL_HGT * 4)
        hco_top.geometry('%dx%d+%d+%d' % (650, 390, x, y))
        hco_top.title(title)
        hco_top.configure(background="WhiteSmoke")
        hco_top.columnconfigure(0, weight=1)
        hco_top.rowconfigure(0, weight=1)

        ''' Register child window for raising & moving with parent '''
        self.win_grp.register_child('column order', hco_top)

        column_dict = get_dict_column(column_name, self.tree_dict)

        # Three synchronized lists
        combo_list = []  # list of "'Heading' - (column name)"
        column_list = []  # list of column names dictionary['column']
        heading_list = []  # list of dictionary['Heading']

        # Build lists in displaycolumns order
        for column in self.tree['displaycolumns']:  # don't use self.columns!
            d = get_dict_column(column, self.tree_dict)
            combo_list.append(d['heading'] + " - (" + column + ")")
            column_list.append(d['column'])  # the keys
            heading_list.append(d['heading'])  # the display names

        def spin_update(*_args):
            """ Spin buttons clicked or new column selected.
                Remove previous highlight and apply new highlight.
            """
            # Get old column index
            combo_col_new = combo_col.get()  # establish index in list
            old_ndx = combo_list.index(combo_col_new)
            heading = heading_list[old_ndx]  # pattern to unhighlight

            spin_new = spin_pos_var.get()
            new_ndx = spin_new - 1

            # credit: https://stackoverflow.com/a/33933500/6929343
            combo_list.insert(new_ndx, combo_list.pop(old_ndx))
            column_list.insert(new_ndx, column_list.pop(old_ndx))
            heading_list.insert(new_ndx, heading_list.pop(old_ndx))
            combo_col['values'] = combo_list

            scrollbox.unhighlight_pattern(heading, 'yellow')
            scrollbox.unhighlight_pattern('|', 'red')  # deleting but un- anyway
            text = '| ' + ' | '.join(heading_list) + ' |'
            scrollbox.delete("1.0", "end")
            scrollbox.insert("end", text)
            scrollbox.highlight_pattern(heading_list[new_ndx], 'yellow')
            scrollbox.highlight_pattern('|', 'red')  # Not really red

        def combo_update(*_args):
            """ New column selected from combo box. Set spin position. """
            combo_col_new = combo_col_var.get()  # establish index in list
            new_ndx = combo_list.index(combo_col_new)
            spin_pos_var.set(new_ndx+1)
            spin_update()  # Highlight new column selected in columns display

        def close(*_args):
            """ close the window """
            if not self.hco_top_is_active:
                return
            combo_col.unbind('<<ComboboxSelected>>')
            self.win_grp.unregister_child(hco_top)
            # self.tt.close(hco_top)  # Close tooltips (There aren't any yet)
            self.hco_top_is_active = False
            hco_top.destroy()

        def order_apply():
            """ Apply changes and close child window (but not toplevel). """
            if not self.hco_top_is_active:
                return

            # Update treeview with displaycolumns.
            self.tree['displaycolumns'] = column_list
            select_dict_columns(column_list, self.tree_dict)

            # Set selected column headings text
            #for d2 in self.tree_dict:
            #    if d2['select_order'] > 0:
            #        self.tree.heading(d2['column'], text=d2['heading'])

            close()  # Close our window
            # No need to close toplevel. Simply change displaycolumns
            #self.force_close()  # Close toplevel window


        ''' frame1 - Holds combox, spinbox, custom scrolledtext and buttons '''
        # ttk.Frame doesn't allow bg color, only style = 
        frame1 = tk.Frame(hco_top, borderwidth=18,
                          relief=tk.FLAT, bg="WhiteSmoke")
        frame1.grid(column=0, row=0, sticky=tk.NSEW)

        # Combobox selects which column to move
        tk.Label(frame1, text="Column to move:", bg="WhiteSmoke",
                 padx=10, pady=10).grid(column=0, row=0)
        combo_col_var = tk.StringVar()
        combo_col = ttk.Combobox(frame1, textvariable=combo_col_var,
                                 state='readonly', width=30)
        combo_col.grid(column=1, row=0)
        combo_col['values'] = combo_list  # 'Heading' - (column name) ...
        ndx = column_list.index(column_dict['column'])  # column_dict set in init
        combo_col.current(ndx)  # Current treeview column default entry

        # Spinbox to bump up/bump down selected column's order in treeview
        tk.Label(frame1, text="Column position:", bg="WhiteSmoke", padx=10, pady=10). \
            grid(column=0, row=1, sticky=tk.W)
        spin_pos_var = tk.IntVar()
        spin_pos_var.set(ndx+1)
        spin_pos = tk.Spinbox(
            frame1, from_=1, to=len(heading_list), increment=-1, width=3,
            state='readonly', textvariable=spin_pos_var, command=spin_update)
        spin_pos.grid(column=1, row=1, sticky=tk.W)

        # Separator around Columns display custom scrolled textbox
        ttk.Separator(frame1, orient='horizontal').\
            grid(column=0, row=2, columnspan=2, sticky=tk.EW)
        frame1.grid_rowconfigure(2, minsize=30)

        # Columns displayed in order with current column highlighted
        tk.Label(frame1, text="Columns display:", bg="WhiteSmoke",
                 padx=10, pady=10, anchor=tk.W).grid(column=0, row=3)
        scrollbox = CustomScrolledText(
            frame1, state="normal", font=(None, g.MON_FONT), borderwidth=10,
            pady=2, relief=tk.FLAT, wrap=tk.WORD)
        scrollbox.grid(row=3, column=1, padx=3, pady=3, sticky=tk.NSEW)
        tk.Grid.rowconfigure(frame1, 3, weight=1)  # spinbox row expands
        tk.Grid.columnconfigure(frame1, 1, weight=1)  # column 2 expands
        scrollbox.tag_config('yellow', background='Yellow')
        scrollbox.tag_config('red', foreground='White', background="gray")

        # Separator around Columns display custom scrolled textbox
        ttk.Separator(frame1, orient='horizontal').\
            grid(column=0, row=4, columnspan=2, sticky=tk.EW)
        frame1.grid_rowconfigure(4, minsize=30)

        # Buttons to apply or close
        button1 = tk.Button(frame1, text="Apply", pady=2, command=order_apply)
        button1.grid(column=0, row=5)
        button2 = tk.Button(frame1, text="Cancel", pady=2, command=close)
        button2.grid(column=1, row=5)

        combo_col.bind('<<ComboboxSelected>>', combo_update)
        spin_update()  # Set initial values in combobox and scrolled textbox

        ''' Bind <Escape> to close window '''
        hco_top.bind("<Escape>", close)
        hco_top.protocol("WM_DELETE_WINDOW", close)

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
                print('toolkit.py ToolTips.update_column() search column error:',
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

    def is_attached(self, msgId):
        """ Is it attached? """
        return self.attached[msgId] is True

    def is_detached(self, msgId):
        """ Is it detached? """
        return self.attached[msgId] is False

    def is_skipped(self, msgId):
        """ Is it skipped? """
        return self.attached[msgId] is None

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


class SearchText:
    """ Search for string in text and highlight it from:
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

        self.frame = None  # frame for input
        # Search text entry box
        self.entry = None  # input field for search string

        ''' keypress search variables '''
        self.keypress_waiting = None  # A keypress is waiting
        self.search_text = tk.StringVar()
        self.new_str = None  # New search string
        self.old_str = None  # Last search string
        self.sip = False  # Search in progress?

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
        if self.keypress_waiting:
            #print("if self.keypress_waiting:")
            # Never executed because can't type faster than search 0.0055580139
            return  # Already have another keypress waiting to be processed
        self.keypress_waiting = True  # Tell previous find() call to end now
        #print("self.keypress_waiting = True")

        # Wait for find() to shutdown
        while self.sip is True:
            self.toplevel.after(100)  # Maybe refresh thread instead?
            if self.sip:
                print("toolkit.py - SearchText.search_changed() Waiting another 100 ms")
        self.find()

    def find(self, *_args):
        """ Search treeview for string in all string columns

            if self.keypress_waiting is True, check if self.new_str starts with
            self.old_str. If so, no need to reattach. Simply keep detaching.
            If self.new_str doesn't start with self.old_str (delete or backspace),
            then reattach all rows.

            if self.keypress waiting is False then reattach from last search.

        """
        if self.find_str is not None:
            print('toolkit.py.SearchText.find_column() should have been called.')
            self.find_column()
            return

        s = self.search_text.get()
        stripped = s.strip()
        self.new_str = stripped

        #ext.t_init('reattach')
        if not self.keypress_waiting:  # None or false
            self.reattach()         # Put back items excluded on last search
        elif self.new_str.startswith(self.old_str):
            # print("self.new_str.startswith(self.old_str):")
            pass  # What was detached before would remain detached
        else:
            # backspace erased character or text inserted/deleted before end
            self.reattach()  # Put back items excluded on last search
        #ext.t_end('print')   # For 1200 messages 0.00529 seconds
        self.old_str = self.new_str
        self.keypress_waiting = False

        if len(stripped) == 0:
            return  # Nothing to search for

        search_or = False  # Later make a choice box
        search_and = True
        self.sip = True  # Search in progress

        # Breakdown string into set of words
        words = s.split()
        #ext.t_init('Loop over every treeview row')
        # Loop over every treeview row
        for iid in self.tree.get_children():
            # self.toplevel.update_idletasks()  # Causes crazy lag
            # Was keyboard character entered/erased?
            if self.keypress_waiting:
                self.sip = False
                #print("if self.keypress_waiting: early exit")
                #ext.t_end('print')  # Never executed loop is: 0.02236
                return  # Will be called again from search_changed()

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

            if search_or and found_one:
                continue

            if search_and and found_one and found_all:
                continue

            self.tree.detach(iid)
            self.attached[iid] = False

        #ext.t_end('print')  #  Loop over every treeview row: 0.0026471615

        self.sip = False  # Search ended
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

    def reattach(self):
        """ Reattach items detached """
        i_r = -1  # https://stackoverflow.com/a/47055786/6929343
        for msgId in self.attached.keys():
            # If not attached then reattach it
            i_r += 1  # Get back attached in same position!
            if self.attached[msgId] is False:
                #i_r += 1  # Causing attached to go near bottom!
                self.tree.reattach(msgId, '', i_r)
                self.attached[msgId] = True

    def close(self):
        """ Remove find search bar
            TODO: No way of stopping find loop when window closed by parent
        """
        if not self.toplevel:
            return  # Closed window
        self.reattach()
        self.search_text.set("")  # Prevent future text highlighting of old search
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

    def __init__(self, toplevel, treeview, row_release=None):

        self.toplevel = toplevel
        self.treeview = treeview

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

VISIBLE_DELAY = 750     # ms pause before balloon tip appears (3/4 sec)
VISIBLE_SPAN = 5000     # ms balloon tip remains on screen (5 sec/line)
EXTRA_WORD_SPAN = 500   # 1/2 second per word if > VISIBLE_SPAN
FADE_IN_SPAN = 500      # 1/4 second to fade in
FADE_OUT_SPAN = 400     # 1/5 second to fade out

''' NOTE: Because a new tip fades in after 3/4 second we have time to
          make old tool tip fade out assuming VISIBLE_DELAY > FADE_TIME '''
if VISIBLE_DELAY < FADE_OUT_SPAN:
    print('VISIBLE_DELAY < FADE_OUT_SPAN')
    exit()


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
        self.visible_delay = 0          # milliseconds before visible       10
        self.visible_span = 0           # milliseconds to keep visible      11
        self.extra_word_span = 0        # milliseconds for extra lines      12
        self.fade_in_span = 0           # milliseconds for fading in        13
        self.fade_out_span = 0          # milliseconds for fading out       14

        # Too much window_ ??
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
                WHERE: the class_name has methods inside.

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

    def __init__(self):

        """ Duplicate entry_init() """
        CommonTip.__init__(self)        # Recycled class to set self. instances

        self.log_nt = None              # namedtuple time, action, widget, x, y
        self.log_list = []              # list of log dictionaries
        self.deleted_str = "0.0.0"      # flag log entry as deleted (zero time)
        self.now = time.time()          # Current time

        self.dict = {}                  # Tip dictionary
        self.tips_list = []             # List of Tip dictionaries
        self.tips_index = 0             # Current working Tip dictionary in list


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
                print('toolkit.py delete_older_for_widget():', self.log_nt)
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
            print('Tooltips.set_tip_plan() self.log_nt widget NOT FOUND!:',
                  self.log_nt)
            print('search_widget for above:', search_widget)
            try:
                print("search_widget['text']:", search_widget['text'])
            except tk.TclError:
                print("Probably shutting down...")
            return
            # Could exit now and save second test
        
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

        else:
            print('toolkit.py ToolTips.process_tip(): Invalid action:',
                  self.log_nt.action)

        self.fields_to_dict()
        self.tips_list[self.tips_index] = self.dict

    def force_fade_out(self):
        """ Override enter time to begin fading out now
        """
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
                visible_delay=VISIBLE_DELAY, visible_span=VISIBLE_SPAN,
                extra_word_span=EXTRA_WORD_SPAN, fade_in_span=FADE_IN_SPAN,
                fade_out_span=FADE_OUT_SPAN, anchor="sw", menu_tuple=None,
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

        self.visible_delay = visible_delay
        self.visible_span = visible_span
        self.extra_word_span = extra_word_span
        self.fade_in_span = fade_in_span
        self.fade_out_span = fade_out_span
        self.anchor = anchor

        # All widgets except "piggy_back" are bound to three common functions
        if self.tool_type is not 'piggy_back':
            # 'piggy_back' functions will send fake <Enter> and <Leave> events
            self.widget.bind('<Enter>', self.enter)
            self.widget.bind('<Leave>', self.leave)
            self.widget.bind('<Motion>', self.motion)
        if self.tool_type is 'button':
            self.widget.bind("<ButtonPress-1>", self.on_press)
            self.widget.bind("<ButtonRelease-1>", self.on_release)
            self.name = self.widget['text']  # Button text
        if self.name is None or self.name.strip() == "":
            self.name = self.tool_type  # Not a Button or no text in button

        # Add tip dictionary to tips list
        self.fields_to_dict()
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
                #print('CreateToolTip.leave(): reset button state to tk.NORMAL')
                self.widget['state'] = tk.NORMAL

        if self.tool_type is 'canvas_button' and self.widget.state is 'active':
            #print('CreateToolTip.leave(): reset canvas button state to normal')
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
                #print("toolkit.py Tooltips.poll_tips() - " +
                #      "Tip disappeared in loop!")
                now_len = len(self.tips_list)
                #print("len(self.tips_list) change 4. size at start:", start_len,
                #      "now:", now_len)
                break

    def process_tip(self):
        """ Check if window should be created or destroyed.
            Check if we are fading in or fading out and set alpha.

            TODO: Leave event is not passed to InfoCentre() unless fading in/out
        """
        #if not self.widget.winfo_exists():  # Oct 18/23 - enhancement
        if not self.widget.winfo_exists() and self.tool_type is not 'piggy_back':
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
                print("toolkit.py ToolTips.process_tip():",
                      "self.tip.window doesn't exist")
                return

        ''' Pending event to start displaying tooltip balloon?
        '''
        if self.enter_time == 0.0:
            if self.tip_window:
                self.tip_window.destroy()
                # Happens when leaving widget while tip window displayed
                print('TEMPORARY: forced tip window close')
                self.tip_window = None
                self.window_visible = False
                self.window_fading_in = False
                self.window_fading_out = False
            return  # Widget doesn't have focus

        fade_in_time, fade_out_time = self.calc_fade_in_out()
        if fade_in_time > self.now + 8:
            print("fade_in_time starts in:", fade_in_time - self.now)

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
                if self.pb_close:
                    self.reset_tip()  # pb_close will probably destroy tip next...
                    self.pb_close()  # Tell "piggy_back" to destroy it's frame
                    return

                if self.tip_window is None:
                    print('toolkit.py ToolTips.process_tip(): ' +
                          'self.tip_window does not exist')
                    print('self.now:', self.now, 'zero_alpha_time:', zero_alpha_time)
                    diff = self.now - zero_alpha_time
                    print('diff:', diff)
                else:
                    self.tip_window.destroy()

                self.reset_tip()
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
        """ Create tooltip window with helpful text / usage instructions """
        # Screen coordinates of parent widget
        widget_nw = (self.widget.winfo_rootx(), self.widget.winfo_rooty())
        widget_ne = (self.widget.winfo_rootx() + self.widget.winfo_width(),
                     widget_nw[1])
        widget_sw = (widget_nw[0], widget_nw[1] + self.widget.winfo_height())
        widget_se = (widget_ne[0], widget_sw[1])

        ''' June 15, 2023 - mserve fake ruler can be 7000 px wide on 1000 frame 
            Patch code to support new anchor "sc" (South Centered)
        '''
        parent_name = self.widget.winfo_parent()
        # noinspection PyProtectedMember
        parent = self.widget._nametowidget(parent_name)
        parent_nw = (parent.winfo_rootx(), parent.winfo_rooty())
        parent_ne = (parent.winfo_rootx() + parent.winfo_width(),
                     parent_nw[1])
        if widget_ne[0] > parent_ne[0]:
            d_print("toolkit.py Tooltips() create_tip_window() Override fake:")
            d_print("     widget_ne:", widget_ne, "with parent_ne:", parent_ne)
            # Above: widget_ne: (9442, 169) parent_ne: (4043, 169)
            widget_ne = parent_ne

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10

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
        if self.tool_type is 'button' or self.tool_type is 'menu':
            self.fg = self.widget["background"]
            self.bg = self.widget["foreground"]
        else:
            self.fg = None  # 'canvas_button' has no coloring.  'label' and
            self.bg = None  # 'piggy-back' will also come here

        #self.tip_window = tw = tk.Toplevel(self.widget)  # Original weird code...
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
            x = nw[0]
            y = nw[1] - h - 20  # 20 px gives distance from edge
        elif self.anchor == "ne":
            x = ne[0] - w
            y = nw[1] - h - 20  # 20 px gives distance from edge
        elif self.anchor == "se":
            x = se[0] - w
            y = se[1] + 20   # 20 px gives distance from edge
        elif self.anchor == "sw":
            x = sw[0]
            y = sw[1] + 20   # 20 px gives distance from edge 20
        elif self.anchor == "sc":  # South Centered
            off = (wid_w - w) / 2
            off = off if off > 0 else 0
            x = sw[0] + off
            y = sw[1] + 20  # 20 px gives distance from edge 20
        else:
            print_trace()
            print('Bad self.anchor value:', self.anchor)
            exit()
        self.tip_window.wm_geometry("+%d+%d" % (x, y))
        self.window_geom = self.tip_window.wm_geometry()

    def set_text(self, widget, text, visible_delay=VISIBLE_DELAY,
                 visible_span=VISIBLE_SPAN, extra_word_span=EXTRA_WORD_SPAN,
                 fade_in_span=FADE_IN_SPAN, fade_out_span=FADE_OUT_SPAN):
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
  
        print_trace()          
        print('toolkit.py ToolTips.set_text(): tip not found')

    def get_dict(self, widget):
        """ Debugging tool for external caller to get a widget's dictionary """
        for s in self.tips_list:
            if s['widget'] == widget:
                return s
        print('toolkit.py ToolTips.get_dict(): self.dict for "widget" not found',
              widget)


    def toggle_position(self, widget):
        """ Flip anchor from North->South or from South->North
            If tip window's position is below widget, set above. 
            If above, then set below. Used when button bar moves to middle
            of window to bottom and vice versa. E.G. mserve chronology.
        """
        for i, s in enumerate(self.tips_list):
            if s['widget'] == widget:
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

        print_trace()
        print('toolkit.py ToolTips.toggle_position(): widget not found', widget)
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
        """ Mouse is panning over widget.
            Keep windows steady traveling along x-axis.
            This generates a lot of noise when printing debug information...
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

    def close(self, widget):
        """ When window closes all tooltips in it must be removed.
        :param widget either button or parent(s) of button. """
        new_list = []
        start = len(self.tips_list)
        for self.dict in self.tips_list:
            if not str(self.dict['widget']).startswith(str(widget)):
                new_list.append(self.dict)
                continue
            d_print("Closing widget:", str(widget)[-4:])

        #diff = len(self.tips_list) - len(new_list)
        #print(diff, 'Tooltips removed on close')
        self.tips_list = []
        self.tips_list = new_list
        end = len(self.tips_list)
        if start == end:
            print("\ntoolkit.py ToolTips.close() called with no effect: ", start)
            print_trace()
            print("Widget(s):", widget)
        self.log_list = []      # Flush out log list for new events

    def check(self, widget, prefix_only=True):
        """ Check if widget in ToolTips()
        :param widget: Parent button or parent frame and prefix check.
        :param prefix_only: Check for members of window group
        :returns: Tooltip dictionary if found, else type 'None' """
        for s in self.tips_list:
            if str(s['widget']) == str(widget):
                return s  # Full match passes
            elif prefix_only and str(s['widget']).startswith(str(widget)):
                return s  # Test prefix and it matches
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

        for i, tips_dict in enumerate(self.tips_list):
            line  = "#" + '{:3d}'.format(i + 1)
            line += "  " + str(tips_dict['widget'])[-4:]  # Short name suffix
            line += "  " + tips_dict['name']
            line += "  -  " + tips_dict['text'].splitlines()[0]  # First line only
            lines.append(line)
            line = "            " + str(tips_dict['widget'])
            lines.append(line)
            # Following stuff is all Null so check before including
            if tips_dict['tip_window'] is not None:
                line  = "  tip_window: " + str(tips_dict['tip_window'])[-4:]
                line += "  window_geom: " + str(tips_dict['window_geom'])[-4:]
                line += "  current_state: " + str(tips_dict['current_state'])
                lines.append(line)  # almost always null

        return lines


def d_print(*args):
    """ Only print debugging lines when D_PRINT is true
        Prepend current time with four decimal places (chop 2 places off)
    """
    if D_PRINT is True:
        prt_time = datetime.datetime.now().strftime("%M:%S.%f")[:-2]
        print(prt_time, *args)


# End of: toolkit.py
