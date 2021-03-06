#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
#
#       mserve.py - Manage Music in multiple locations
#
#       Sept 20 2020 - Start taking out or replacing 63 root.update()
#       Sept 23 2020 - Make compare button disappear (entire grid 4 remove)
#       Oct. 24 2020 - CheckboxTreeview() replace "songsel" tag with "checked"
#       Nov. 02 2020 - Remove old selection processing for new CheckboxTreeview 
#       Dec. 12 2020 - Chrome os doesn't support .grid_remove(). Comment out 15
#            self.loc_F4.grid_remove()
#       Dec. 28 2020 - Selected MB is now Song Number Sequence
#       Jan. 15 2021 - Add vu_meter.py as separate program
#       Feb. 07 2021 - Add webscrape.py as separate program
#       Mar. 05 2021 - Fine-tune time index (Lyrics Synchronization)
#       Mar. 13 2021 - Use ffplay output for current seconds
#       May. 02 2021 - Now called by m wrapper splash screen
#       May. 18 2021 - createToolTip() - Hover balloon
#       Jun. 14 2021 - Rounded Rectangle Canvas widget
#       Aug. 08 2021 - New webscrape.py parameters/results via SQL History
#       Aug. 21 2021 - Revamp tooltips with toolkit.ToolTips
#       Jan. 18 2022 - Set tooltip location SW, SE, NW or NE of parent widget.
#
# ==============================================================================

# noinspection SpellCheckingInspection
"""
TODO:   When inserting song collapse parent list of currently playing song if
        not our parent.
      
        .see() needs to be optional if song already displayed being
        checked/unchecked
      
        When editing lyrics, set scroll box to where cursor used to be. Add tip
        for copy & paste using CTRL+C and CTRL+V

        Save last selections after each song.

        Create self.message_waiting() called by every function to lift
            message window to top of window stack and return true so
            caller can do it's own return. If lifting window it is
            shaken around to give attention to user. The lifted window
            in turn calls tool.thread() to keep music player graphics
            running.

        Create self.tool_check() which examines every registered widget
            to see if enter time is 500 ms > leave time and paint balloon.
            When leave time is > enter time and balloon mounted then
            destroy it. Provide widget fade after time and fade period
            parameters with system wide defaults, eg 5 second time with
            3 second fade to invisible.

TODO:   Save last known monitor configuration. If different this time then
        reset startup window coordinates centered. If monitor configuration
        the same then use saved window coordinates when program last used.
        
        As each window is closed, save it's coordinates (including width and
        height). When opening windows if saved coordinates still valid mount
        where it was previously.

        If parent window moved from it's previous coordinates and child
        window had saved coordinates remap by parent's changed offsets.

        Rounded rectangle on canvas for modern buttons and tool tips
CALL:
   mserve "/mnt/music/Users/Person/Music/iTunes/iTunes Media/Music/"

REQUIRES:
   sudo apt install python-tk
   sudo apt install python-pil
   sudo apt install python-pil.imagetk
   sudo apt install python-subprocess32             # To compare locations
   sudo apt install ffmpeg                          # To get artwork
   sudo apt install xdotool                         # To move Kid3 into our
   sudo apt install wmctrl                          #  lib_top parent window
   sudo apt install python-libdiscid                # Get CD's disc ID
   sudo apt install python-musicbrainzngs           # Get metadata for CD
   sudo apt install python-requests                 # Get Cover Art
   sudo apt install python-notify2                  # Popup bubble messages
   sudo apt install python-magic                    # Get file type information
   sudo apt install python-mutagen                  # Encode and ID3 tags
   sudo apt install x11-apps                        # xwd window dump (screen shot)
   sudo apt install xclip                           # Insert clipboard
   sudo apt install python-beautifulsoup            # Scrape Song lyrics

   sudo add-apt-repository ppa:j-4321-i/ttkwidgets  # CheckboxTreeview
   # NOTE: on Chromebook crostini you need to patch Debian to use Ubuntu key
   To add Ubuntu PPA to Debian for Crostini:
    https://linuxconfig.org/install-packages-from-an-ubuntu-ppa-on-debian-linux

   This is necessary for ttkwidgets and ttkcaldenar
   sudo apt-get update
   sudo apt-get install python-ttkwidgets           # CheckboxTreeview
   sudo add-apt-repository ppa:j-4321-i/ppa
   sudo apt-get update
   sudo apt-get install python-tkcalendar

   FOR Python 2.7 ttkthemes (Python 3 can use current version of ttkthemes):
    pip install -U setuptools
    python2 -m pip install ttkthemes==2.4.0

   ERROR OVERRIDES:
   File "/usr/lib/python2.7/dist-packages/mutagen/flac.py", line 597, in write
    desc = self.desc.encode('UTF-8')
    UnicodeDecodeError: 'ascii' codec can't decode byte 0xe2 in position 4: 
    ordinal not in range(128)

    CHANGE line 597 from:

        desc = self.desc.encode('UTF-8')

    to:

        try:                                # 2020-10-18 UnidcodeDecodeError
            desc = self.desc.encode('UTF-8')
        except UnicodeDecodeError:          # Filename: 06 Surf???s Up.oga
            desc = self.desc                # self.desc already in UTF-8

    $ sudo apt-mark hold python-mutagen

    - https://github.com/quodlibet/mutagen/issues/499


NOTES:

    File server needs to mount music directory if on idle partition:
    
        sudo mount -t auto -v /dev/sdb1 /mnt/music

TODO: verify external commands are in path:
    command -v ffplay, ffprobe, ffmpeg, kill, pactl, diff, touch,
                wmctrl, xdotool

    Sometimes pausing music doesn't restore other sound sources which were
        chopped to 50% when we started playing.
    
    Sometimes when pausing our own volume is only 50% which makes volume
        jump then diminish back.

    When starting fresh session old ffplay profile of muted might be remembered.
    
    Compare Location - Make background process so music player keeps spinning

    encoding.py - After song is ripped, we will still come back from time to
        time and update metatags from Musicbrainz or CoverArtArchive.

    Playing selected song: Allow click on item and play it.
    
"""
# inspection SpellCheckingInspection

# identical imports in message.py and similar in location.py

from __future__ import print_function  # Must be first import
from __future__ import with_statement  # Error handling for file opens

# from __future__ import unicode_literals     # Unicode errors fix

try:
    import tkinter as tk
    import tkinter.ttk as ttk
    import tkinter.font as font
    import tkinter.filedialog as filedialog
    import tkinter.messagebox as messagebox
    import tkinter.simpledialog as simpledialog
    PYTHON_VER = "3"

except ImportError:  # Python 2
    import Tkinter as tk
    import ttk
    import tkFont as font
    import tkFileDialog as filedialog
    import tkMessageBox as messagebox
    import tkSimpleDialog as simpledialog
    PYTHON_VER = "2"

# print ("Python version: ", PYTHON_VER)
# print ('TK Version:', tk.TkVersion)   # https://tkdocs.com/ Nov 2019 ver 8.6
#

import signal                               # Shutdown signals
import subprocess32 as sp
import threading
import sys
import os
import shutil
import time
import datetime
from PIL import Image, ImageTk, ImageDraw, ImageFont
from ttkwidgets import CheckboxTreeview
import pickle
from random import shuffle
import getpass              # Get username for file storage
import notify2              # send inotify over python-dbus

import locale               # To set thousands separator as , or .

locale.setlocale(locale.LC_ALL, '')  # Use '' for auto locale selecting
import numpy as np          # For image processing speed boost

# mserve modules
import global_variables as g
g.init()
import location as lc       # manage device music locations
import message              # manage dialog messages
import encoding             # CD ripping + Musicbrainz + cover art
import external as ext      # launch external programs
import image as img         # make_image()
import sql                  # SQLite3 functions
import monitor              # Display, Screen, Monitor and Window functions
import toolkit              # Functions for tkinter-tool kit interface
import timefmt as tmf       # Format date and time
import webscrape            # Get song lyrics via web scrape

# Subdirectory in ~/python
from pulsectl import pulsectl

# sql.sample()

CFG_THOUSAND_SEP = ","      # English "," to for thousands separator
CFG_DECIMAL_SEP = "."       # English "." for fractional amount
CFG_DECIMAL_PLACES = 1      # 1 decimal place, eg "38.5 MB"
CFG_DIVISOR_AMT = 1000000   # Divide by million
CFG_DIVISOR_UOM = "MB"      # Unit of Measure becomes Megabyte

# Global variables
RESTART_SLEEP = .3          # Delay for mserve close down
KEEP_AWAKE_MS = 250         # Milliseconds between time checks
MON_FONTSIZE = 12           # Font size for monitor name
WIN_FONTSIZE = 11           # Font size for Window name
BIG_FONT = 18               # Font size not used
LARGE_FONT = 14             # Font size not used
MED_FONT = 10               # Medium Font size
BTN_WID = 17                # Width for buttons on main window
BTN_WID2 = 15               # Width for buttons on play window
BTN_BRD_WID = 3             # Width for button border
FRM_BRD_WID = 2             # Width for frame border
PANEL_HGT = 24              # Height of Unity panel
MAX_DEPTH = 3               # Sanity check if starting at c:\ or /
# If MAX_DEPTH changes you must update 'depth_count = [ 0, 0, 0 ]' below.

# Temporary directory currently_playing filename
TMP_CURR_SONG = "/run/user/" + g.USER_ID + "/mserve.currently_playing"
TMP_CURR_SAMPLE = "/run/user/" + g.USER_ID + "/mserve.current_sample"
TMP_FFPROBE = "/run/user/" + g.USER_ID + "/mserve.ffprobe"
TMP_FFMPEG = "/run/user/" + g.USER_ID + "/mserve.ffmpeg.jpg"

# vu_meter.py (Volume Meter) IPC file names
VU_METER_FNAME = "/run/user/" + g.USER_ID + "/mserve.vu-meter-mono.txt"
VU_METER_LEFT_FNAME = "/run/user/" + g.USER_ID + "/mserve.vu-meter-left.txt"
VU_METER_RIGHT_FNAME = "/run/user/" + g.USER_ID + "/mserve.vu-meter-right.txt"

# Firefox name which is really the sound source for big screen TV
FIREFOX = "Firefox"

# Values from gnome-terminal to prevent window shrinking too small
#WIN_MIN_WIDTH = 142
#WIN_MIN_HEIGHT = 63

KID3_INSTALLED = True
KID3_PROGRAM = "kid3 "
# TODO: Command before running kid3: 'xrandr --dpi 144'
FM_INSTALLED = True
FM_PROGRAM = "nautilus"

# Chrome os Linux Beta doesn't support .grid_remove() properly
GRID_REMOVE_SUPPORTED = True
# When unselecting song in library, end song (if playing) and remove in list
# TODO: clicking in library to remove song from playlist leaves music player
# silent. Must click song in chron tree to start new song.
LIBRARY_UNSELECT_REMOVE_PLAYING = True
# When selecting song in library, how does it go into currently playing list?
LIBRARY_SELECT_INSERT_PLAY_HERE = True
LIBRARY_SELECT_INSERT_PLAY_NEXT = False
LIBRARY_SELECT_INSERT_PLAY_RANDOM = False
LIBRARY_SELECT_INSERT_PLAY_ORDER = False
'''
If an entire album or artist is inserted as anything but RANDOM
then a new function to randomize those songs just inserted should
be created.

When inserting "HERE" and then playing we need a way to start with
first song inserted when the default would be the last song inserted.

'''

# Below reveals ALBUM_ art work which might be useful
# FILE_TYPES = [".gif", ".png",".jpg", ".jpeg"]
# Select music files only, no artwork
# TODO: Make user definable and much larger list
#       Deep scan with python-magic to read each file for song type
FILE_TYPES = [".mp3", ".m4a", ".mp4", ".wma", ".oga", ".ogg", ".flac", ".wav", ".PCM"]
NO_ARTIST_STR = "(No Artist)"   # global User defined labels
NO_ALBUM_STR = "(No Album)"
NO_ART_STR = "No Artwork"
PAUSED_STR = "|| Paused"
NUMBER_PREFIX = "??? "            # UTF-8 (2116) + normal space
DIGIT_SPACE = "???"             # UTF-8 (2007)

''' Music Library's top directory '''
START_DIR = ""

# noinspection SpellCheckingInspection
''' TODO: Start up announcement at 75% volume
    Setting should be for once a day. We don't want this dozens of times when
    we are developing and testing code. Need ~/.config/mserve/last_start_time
$ pico2wave -w=/tmp/test.wav "m serve version 1.0"
$ aplay /tmp/test.wav
$ rm /tmp/test.wav
'''
# inspection SpellCheckingInspection


# TV commercial and intermission breaks
TV_BREAK1 = 90
TV_BREAK2 = 1080
PRUNED_SUBDIRS = 0  # sys arg topdir = 0, artist = 1, album = 2


def make_sorted_list(start_dir, toplevel=None, idle=None):
    """ Build list of songs
        Called at startup and by refresh_lib_tree()
        Use DelayedTextBox for status updates on long-running processes
        which doesn't appear if process shorter than a second.
    """

    ''' If system argument 1 is for random directory, we have no last location.
        It may not point to a music topdir, rather an Artist or Album. A single
        song cannot be passed because os.walk() returns nothing.

        TODO: Error message if song is passed as start_dir.

        In os.walk() we process 100 ms at a time and call lib_top.after() 
        for 100 ms so album artwork keeps spinning.

        Before calling make_sorted_list() must ensure network is up. After a
        resume from suspend network may be down.

    '''

    global PRUNED_SUBDIRS  # When no topdir and artist or album used.

    if NEW_LOCATION:
        # print('WIP:',start_dir,"may point to topdir, Artist or Album")
        pass

    # print('make_sorted_list() toplevel:',toplevel,'idle:',idle)
    work_list = []
    dtb = message.DelayedTextBox(title="Scanning music directories",
                                 toplevel=toplevel, width=1000)

    depth_count = [0, 0, 0]  # Count of songs at each level
    last_check = time.time()  # Time we last checked to enter idle loop
    next_check = last_check  # For PyCharm warning message
    if idle is not None:
        next_check = last_check + float(idle) / 1000
        print('last_check:', last_check, 'next_check:', next_check)
    idle_loops = 0  # How many times we idled while building list

    start_dir = unicode(start_dir)  # Get results in unicode
    # What's the difference between unicode() and .encode('utf-8')?
    for subdir, dirs, files in os.walk(start_dir, topdown=True):

        ''' Limit search to files in 3 levels (/Artist/Album/Songs) '''
        curr_depth = subdir.count(os.sep) - start_dir.count(os.sep)
        """
        """
        if curr_depth == MAX_DEPTH - 1:
            # Sanity check - delete directories below maximum depth
            del dirs[:]
            continue

        for f in files:
            # Check to sleep
            if idle is not None:
                last_check = time.time()
                if last_check > next_check:
                    # Time we last checked to enter idle loop
                    print('make_sorted_list() last_check:', last_check,
                          'work_list count:', len(work_list))
                    # toplevel.update_idletasks()
                    # toplevel.after(idle)
                    root.update_idletasks()
                    root.after(idle)
                    next_check = time.time() + float(idle) / 1000
                    # print('make_sorted_list() next sleeping at:', next_check)
                    idle_loops += 1

            # Take sub-path /Artist/Album/Song.xxx and build full path for tests
            full_path = os.path.join(subdir, f)
            # There are depths with no files so must recalculate current depth
            curr_depth = full_path.count(os.sep) - start_dir.count(os.sep)
            dtb.update(full_path)
            # Valid songs are regular files with known extensions
            if os.path.isfile(full_path) and \
                    os.path.splitext(f)[1] in FILE_TYPES:
                # Count song occurrences at this level
                depth_count[curr_depth] += 1
                # Insert missing Artists and Albums directories into work_f
                work_f = f
                work_level = full_path.count(os.sep) - start_dir.count(os.sep)
                if NEW_LOCATION:
                    # print('WIP work_f, work_level:', work_f, work_level)
                    pass
                if work_level is 0:
                    # Note leading / break os.path.join
                    work_f = NO_ARTIST_STR + os.sep + NO_ALBUM_STR \
                             + os.sep + work_f
                if work_level is 1:
                    work_f = NO_ALBUM_STR + os.sep + work_f

                # Build full path name from root directory
                work_path = os.path.join(subdir, work_f)

                # Insert space in front of every / for proper sorting                   
                work_path = work_path.replace(os.sep, " " + os.sep)
                work_list.append(work_path)

    # Sort work list with ` /` then normalize to '/' and return it
    work_list.sort()
    work_list = [w.replace(" " + os.sep, os.sep) for w in work_list]
    dtb.close()
    # print('make_sorted_list idle loop count:', idle_loops)

    # print(depth_count)
    # print(work_list)

    ''' NOT pointing at Topdir, eg An Artist or an Album.

        If all three levels are zero, bail out

        If level 2 and 3 is zero, No Artist/No Album become dir_name-2/dir_name-1

        If 3 is zero, /No Album becomes Artist Name
                      Artist Name becomes dir_name - 1
    '''
    if depth_count[0] == 0 and depth_count[1] == 0 and depth_count[2] == 0:
        return work_list  # No songs, or started pointing at single song

    if depth_count[1] == 0 and depth_count[2] == 0:
        # print('BEFORE:', work_list)
        # print('replacing: '+NO_ALBUM_STR+' with: '+back_dir1)
        work_list = [w.replace(os.sep + NO_ALBUM_STR + os.sep, os.sep)
                     for w in work_list]
        # print('replacing: '+NO_ARTIST_STR+' with: '+back_dir2)
        work_list = [w.replace(os.sep + NO_ARTIST_STR + os.sep, os.sep)
                     for w in work_list]
        # print('AFTER:', work_list)
        PRUNED_SUBDIRS = 2
        return work_list  # No songs, or started pointing at single song

    if depth_count[1] > 0 and depth_count[2] == 0:
        # More complex shifting Artist name to album name requires looping
        # print('BEFORE:', work_list)
        # print('replacing: '+NO_ALBUM_STR+' with: '+back_dir1)
        work_list = [w.replace(os.sep + NO_ALBUM_STR + os.sep, os.sep)
                     for w in work_list]
        # print('AFTER:', work_list)
        PRUNED_SUBDIRS = 1
        return work_list  # No songs, or started pointing at single song

    PRUNED_SUBDIRS = 0
    return work_list


# ==============================================================================
#
#       MusicTree class - Define lib (library of music)
#
# ==============================================================================

class PlayCommonSelf:
    """ Variables in play_items() for self.play_frm frame defined here because
        pycharm syntax highlighting errors.

        Plus provides a useful overview of all variables.

        Must appear before first reference (MusicTree)
    """
    def __init__(self):
        #def __init__(self, toplevel, song_list, sbar_width=12, **kwargs):

        self.killer = ext.GracefulKiller()  # Class to shut down

        self.play_on_top = None             # Is play frame overtop library?
        self.pause_t_start = None           # Time current song was paused
        self.play_t_start = None            # Time current song was playing
        self.play_song_count = None         # playlist (selected) song count
        self.secs_before_pause = None       # get_curr_ffplay_secs(
        self.current_song_t_start = None    # time.time() started playing
        self.saved_DurationSecs = None      # self.DurationSecs
        self.saved_DurationMin = None       # Duration in Min:Sec.Deci
        self.current_song_secs = None       # How much time played
        self.current_song_mm_ss_d = None    # time in mm:ss.d (decisecond)
        self.secs_before_pause = None       # How much before paused NEEDED??
        self.last_started = None            # self.ndx catch fast clicking Next
        self.play_opened_artist = None      # Play expanded artist in Library?
        self.play_opened_album = None       # Play expanded album in Library?

        # Below called with "python vu_meter.py stereo 2>/dev/null"
        self.vu_meter_pid = None            # Linux Process ID for vu_meter.py
        self.play_top_title = None          # Playing Selected Songs - mserve
        self.play_frm = None                # play_top master frame
        self.play_frm_bg = None             # "self.play_resized_art.get pixel((3,"
        self.background = None              # hex_background color
        self.foreground = None              # hex_foreground color

        # Play Frame column 0
        self.art_width = 200                # Spinning art work initial size
        self.art_height = 200
        self.art_label = None               # Spinning art tkinter label widget
        self.start_w = 0                    # self.play_frm.winfo_reqheight()
        self.start_h = 0                    # self.play_frm.winfo_reqwidth()
        self.play_resized_art = None        # self.play_resized_art.resize(
        self.play_current_song_art = None   # ImageTk.PhotoImage(..resized_art
        ''' play_no_art(self): '''
        self.play_original_art = None       # img.make_image(NO_ART_STR
        self.play_rotated_art = None        # Image.new(
        self.play_rotated_value = None      # Rotate art up to -365
        self.play_shifted_art = None        # Shift art with play_art_fade2()
        self.play_art_slide_count = None    # = 0 and 
        self.play_art_fade_count = None     # = 0:
        self.step = None                    # Number fade/slide steps taken
        self.current_chunk = None           # fade/slide in chunks
        self.chunk_size = None              # int(len(self.xy_list) / 100)
        # Weird stuff below from: play_art_fade_numpy(self):
        self.im = None                      # np.array(rgb_image)
        self.fade = None                    # np.zeros_like(self.im)
        self.co_ords = None                 # np.column_stack((X, Y))
        self.xy_list = None                 # list(map(tuple, self.co_ords.
        self.breakpoint = None              # int(self.im.size * self.play/100

        self.current_song_number = None     # Playing song number in playlist
        self.current_song_artist = None     # Metadata Artist name (ellipses)
        self.current_song_album = None      # Metadata Album name (ellipses)
        self.current_song_path = None       # Not sure yet!!!!
        self.current_song_name = None       # Metadata song (Title) name
        self.current_progress = None        # Seconds (1 decimal) song played

        # Play frame VU meters - columns 2 & 3
        self.play_vu_meter_style = None     # 'led' = Use LED rectangles
        self.vu_width = None                # VU Meters (Left & Right channel
        self.vu_height = None               # width and height in pixels
        self.vu_meter_left = None           # tk.Canvas(self.play_frm...
        self.vu_meter_left_rectangle = None  # vu_meter_left.create_rectangle(
        self.vu_meter_right = None          # tk.Canvas(self.play_frm...
        self.vu_meter_right_rectangle = None  # vu_meter_right.create_r
        self.VU_HIST_SIZE = None            # History of six db levels
        self.vu_meter_left_hist = None      # Left & Right channel histories
        self.vu_meter_right_hist = None     # can be zero on race condition

        # Play frame # 3 (misleading frame number) - column 4
        self.play_F3 = None                 # tk.Frame(self.play_frm)
        self.play_F3_panel = None           # tk.Frame(self.play_F3)
        # The panel dynamically changes depending on Basic Time Index,
        # edit lyrics, webscrape lyrics, fine-tune time index, manual scroll
        self.lyrics_panel_label = None      # tk.Label(self.play_F3_panel,
        self.lyrics_panel_last_line = None  # Rebuild panel_text when changing
        self.lyrics_panel_scroll = None     # Auto / Time / Manual Scroll
        self.lyrics_panel_text = None       # 0%, Line: 99 of 99  ??????
        self.lyrics_panel_burger = None     # Hamburger menu
        # title_F3 is old stuff being removed this weekend (May 29-30, 2021)
        self.lyrics_pid = None              # Process ID for web scrape
        self.lyrics_edit_is_active = False  # song lyrics being edited?
        self.lyrics_train_is_active = False  # Basic time index training
        self.lyrics_train_start_time = None  # When basic training started
        self.lyrics_score_box = None        # tk.Text(self.play_F3

        # Four rounded rectangle buttons: Auto to Manual, Time to Manual,
        # Manual to Auto and Manual to Time:
        self.lyrics_panel_scroll_a_m_grid = None
        self.lyrics_panel_scroll_t_m_grid = None
        self.lyrics_panel_scroll_m_a_grid = None
        self.lyrics_panel_scroll_m_t_grid = None
        # rounded rectangle button widgets
        self.lyrics_panel_scroll_a_m = None
        self.lyrics_panel_scroll_t_m = None
        self.lyrics_panel_scroll_m_a = None
        self.lyrics_panel_scroll_m_t = None
        # Associated tooltips to rounded rectangle buttons
        #self.lyrics_panel_scroll_a_m_tt = None
        #self.lyrics_panel_scroll_t_m_tt = None
        #self.lyrics_panel_scroll_m_a_tt = None
        #self.lyrics_panel_scroll_m_t_tt = None
        self.lyrics_panel_scroll_widest = 0
        self.lyrics_panel_scroll_highest = 0
        self.lyrics_panel_hamburger = None
        self.lyrics_panel_hamburger_tt = None
        self.lyrics_score_scroll_y = None   # y-axis scroll bar for lyrics score
        self.lyrics_time_list = None        # [] Seconds time index
        self.lyrics_score = None            # Loaded from sql or web scrape
        self.lyrics_prev_line = None        # Line clicked previously
        self.lyrics_curr_line = None        # Line just clicked
        self.lyrics_line_count = None       # int(end.split('.')[0]) - 1
        self.work_sql_key = None            # self.play_make_sql_key()
        self.work_lyrics_score = None       # self.lyrics_score
        self.work_time_list = None          # self.lyrics_time_list
        self.work_song_path = None          # self.current_song_path
        self.work_song_secs = None          # self.current_song_secs
        self.work_DurationSecs = None       # self.DurationSecs
        self.work_Title = None              # self.Title (song name)
        self.work_line_count = None         # self.lyrics_line_count  # FUDGE FOR Time being...
        self.lyrics_scroll_rate = None      # 1.5 = Default auto scroll rate
        self.lyrics_time_scroll = None      # Use lyrics time index scrolling
        self.lyrics_auto_scroll = None      # Use auto scrolling
        self.lyrics_old_scroll = None       # Last scroll setting
        self.lyrics_scrape_done = None      # Signal we are done scrape
        self.lyrics_edit_start_time = None  # time.time()
        # Set cursor position in text box
        self.edit_current_cursor = None     # self.lyrics_score_box.index(INSERT)

        # Fine-tune time index (synchronize) variables
        self.syn_top = None                 # Toplevel window over play_top
        self.syn_tree = None                # CheckboxTreeview(frame2,
        self.check2 = None                  # Duplicated treeview checkboxes
        self.syn_top_buttons = None         # tk.Frame(self.syn_top, tk.GROOVE,
        self.sync_begin_buttons = None      # tk.Frame(self.syn_top, tk.GROOVE,
        self.sync_sample_buttons = None     # tk.Frame(self.syn_top, tk.GROOVE,
        self.sync_sample_pp_state = None    # 'Playing'
        self.sync_sample_pp_button = None   # text=self.pp_pause_text
        self.sync_ffplay_is_running = None  # Already playing and syncing?
        self.sync_paused_music = None       # Did sync force play to pause?
        self.sync_changed_score = None      # Was lyrics score changed?
        self.sync_changed_lyrics = None     # Lyrics score has changed DUPLICATE!
        self.sync_ffplay_pid = None         # ffplay linux process ID
        self.sync_ffplay_sink = None        # pulseaudio sink number
        self.label_line_count = None        # Display # of lines in lyrics
        self.sync_default_set = None        # Have tree line going into sync?
        self.new_time_list = None           # [] time list is edited these
        self.new_durations_list = None      # [] lists override synchronizing
        #self.sync_first, self.sync_last = self.sync_fill_checkboxes()
        self.sync_first = None              # First check box to synchronize
        self.sync_last = None               # Last check box to synchronize
        self.sync_curr_highlight = None     # When changes move bar
        self.sync_start = None              # Offset to start syncing at
        self.sync_duration = None           # Duration to sync. 0 = quit
        self.sync_music_start_time = None   # time() Music is playing now
        self.sync_elapsed = None            # time()-sync_music_start_time
        self.old_sinks = None               # sink_master() - list of tuples

        # Play frame Buttons frame
        self.play_btn = None                # tk.Frame(self.play_top, bg="Blue"
        self.close_button = None            # tk.Button(play_btn, text="??? Close
        self.shuffle_button = None          # tk.Button(...text="??????? Shuffle",

        # Pause/Play Button changes dynamically when pp_toggle() called
        self.pp_state = "Playing"
        self.pp_play_text = "???  Play"
        self.pp_pause_text = "?????? Pause"
        self.pp_button = None               # tk.Button(self.play_btn,
        self.pp_toggle_time = None          # Not sure!!!

        self.prev_button = None             # tk.Button(...text="????  Previous"
        self.next_button = None             # tk.Button(...text="???Next ???? "
        self.com_button = None              # tk.Button(.text="????  Commercial"
        self.int_button = None              # tk.Button(text="????  Intermission"

        self.play_hockey_active = None      # TV turned down and music play?
        self.play_firefox_indices = None    # sink_list("Firefox") FIREFOX
        self.play_hockey_secs = None        # Commercial = TV_BREAK1 seconds
        self.play_hockey_remaining = None   # init to self.play_hockey_secs
        self.play_hockey_t_start = None     # time.time()
        self.gone_fishing = None            # Class: Shark eating man

        ''' Show/Hide Playlist Chronology button (Frame 4) '''
        self.play_list_hide = None          # Frame can .remove()/.grid()
        self.chron_button = None           # tk.Button(..."???? Hide Chronology"

        ''' Frame for Playlist Chronology '''
        self.F4 = None                      # tk.Frame(self.play_top, bg="Black

        self.play_top_pid = None            # Integer for ffplay PID
        self.play_top_sink = ""             # String for ffplay Pulse Audio
        self.metadata = None                # {}
        self.Artist = None                  # metadata.get('ARTIST', "None")
        self.Album = None                   # metadata.get('ALBUM', "None")
        self.Title = None                   # metadata.get('TITLE', "None")
        self.Genre = None                   # metadata.get('GENRE', "None")
        self.Track = None                   # metadata.get('TRACK', "None")
        self.Date = None                    # metadata.get('DATE', "None")
        self.Duration = None                # self.metadata.get('DURATION',
        self.DurationSecs = None            # NOTE: Must save in parent

        # Popup menu
        self.mouse_x = None
        self.mouse_y = None
        self.kid3_window = None

        self.parm = None                    # sys arg parameters called with
        
        # Location common variables
        self.loc_top = None                 # Location toplevel
        self.loc_tree = None                # Treeview
        self.loc_tree_btn1 = None           # ??? Close
        self.loc_tree_btn2 = None           # ???  Test
        self.loc_tree_btn3 = None           # ????  Show location
        self.loc_tree_btn4 = None           # ????   Add location
        self.loc_tree_btn5 = None           # ????   Edit location
        self.loc_tree_btn6 = None           # ????   Forget location
        self.loc_tree_btn7 = None           # ????  Compare
        self.loc_F4 = None                  # Frame for Location Data Entry
        self.awake_last_time_check = None
        self.next_active_cmd_time = None
        ''' Define tk variables used with .set() and .get() '''
        self.iid_var = None
        self.name_var = None
        self.topdir_var = None
        self.host_var = None
        self.wakecmd_var = None
        self.testcmd_var = None
        self.testrep_var = None
        self.mountcmd_var = None
        self.activecmd_var = None
        self.activemin_var = None

        self.state = None                   # Editing 'normal' or 'readonly'
        self.name_fld = None                # Location name entry field
        self.topdir_fld = None              # Music top directory entry field
        self.host_fld = None                # Optional host name for location
        self.wakecmd_fld = None             # Command to wake up sleeping host
        self.testcmd_fld = None             # Command to test if host is awake
        self.testrep_fld = None             # Repeat test x times .1 seconds
        self.mountcmd_fld = None            # command to mount host music
        self.activecmd_fld = None           # SSH command to keep host awake
        self.activemin_fld = None           # Minutes between keep awake cmd
        self.sub_btn = None                 # Submit changes button


        # Compare common variables
        self.cmp_target_dir = None          # OS directory comparing to
        self.cmp_tree = None                # Treeview
        self.cmp_close_btn = None           # Doesn't need to be instanced
        self.update_differences_btn = None
        self.src_mt = None                  # Source modification time
        self.trg_mt = None                  # Target modification time
        self.cmp_msg_box = None             # message.Open()

        ''' Refresh items - inotify '''
        self.last_inotify_time = None       # now
        self.next_message_time = None       # now + (60 * 20)


        self.loc_mode = None                # Used by loc_submit()
        self.loc_iid = None                 # location internal ID
        self.location_text = None           # Mode: show, add, etc.

        ''' Rip CD class (separate module) '''
        self.rip_cd_class = None

        ''' Sample middle of song '''
        self.sam_top = None                 # tk.Toplevel()
        self.sam_paused_music = None        # We will resume play later
        self.sam_top_pid = None             # Process ID
        self.sam_top_sink = None            # Pulse Audio sink

        ''' Play Chronology '''
        self.chron_tree = None               # ttk.Treeview


class MusicTree(PlayCommonSelf):
    """ Create self.lib_tree = tk.Treeview() via CheckboxTreeview()

        Resizeable, Scroll Bars, select songs, play songs.

        If toplevel is not None then it is the splash screen to destroy.

    """

    def __init__(self, toplevel, song_list, sbar_width=12):

        # Define self. variables in play_items() where play_top frame is used.
        #PlayCommonSelf.__init__(self, toplevel, song_list, sbar_width=12, **kwargs)
        PlayCommonSelf.__init__(self)

        # If we are started by splash screen get object, else it will be None
        self.splash_toplevel = toplevel
        self.splash_removed = False  # Did we remove splash screen?

        # Create our tooltips pool (hover balloons)
        #self.tooltips = message.ToolTipsPool()
        self.tt = toolkit.ToolTips()

        dtb = message.DelayedTextBox(title="Building music view",
                                     toplevel=None, width=1000)
        self.ndx = 0  # Start song index
        self.play_from_start = True  # We start as normal
        self.song_list = song_list
        self.lib_top = tk.Toplevel()
        self.lib_top.minsize(g.WIN_MIN_WIDTH, g.WIN_MIN_HEIGHT)

        ''' Set program icon in taskbar '''
        img.taskbar_icon(self.lib_top, 64, 'white', 'lightskyblue', 'black')

        ''' Initial size of Window 75% of HD monitor size '''
        _w = int(1920 * .75)
        _h = int(1080 * .75)
        _root_xy = (3800, 200)  # Temporary hard-coded coordinates

        ''' Mount window at popup location '''
        self.lib_top.minsize(width=BTN_WID * 10, height=PANEL_HGT * 4)
        #self.lib_top.geometry('%dx%d+%d+%d' % (_w, _h, _root_xy[0], _root_xy[1]))
        geom = monitor.get_window_geom('library')
        self.lib_top.geometry(geom)

        self.lib_top.configure(background="Gray")
        self.lib_top.columnconfigure(0, weight=1)
        self.lib_top.rowconfigure(0, weight=1)

        ''' Set program icon in taskbar '''
        # Move to main()
        # img.taskbar_icon(self.lib_top, 64, 'white', 'lightskyblue', 'black')

        ''' Window Title bar.
        '''
        self.lib_top.title("Music Server")
        #                       Loc     Songs   Time    Count sSize sSeconds
        #                       0       2       4       6     8     10
        self.lib_top_totals = ["", "", "", "", "", 0, 0, 0, 0, 0, 0]
        #                           1       3        5     7     9
        #                           Play    Space    Size  Secs  sCount
        self.lib_top_totals[0] = LODICT['name']
        self.lib_top_totals[1] = ""  # Playlist name makes title too long

        ''' Create frames '''
        master_frame = tk.Frame(self.lib_top, bg="olive", relief=tk.RIDGE)
        master_frame.grid(sticky=tk.NSEW)
        master_frame.columnconfigure(0, weight=1)
        master_frame.rowconfigure(0, weight=1)

        # Create a frame for the treeview and scrollbar(s).
        frame2 = tk.Frame(master_frame)
        tk.Grid.rowconfigure(frame2, 0, weight=1)
        tk.Grid.columnconfigure(frame2, 0, weight=1)
        frame2.grid(row=0, column=0, sticky=tk.NSEW)

        ''' CheckboxTreeview List Box, Columns and Headings '''
        self.lib_tree = CheckboxTreeview(frame2, show=('tree', 'headings'),
                                         columns=("Access", "Size", "Selected", "StatTime",
                                                  "StatSize", "Count", "Seconds",
                                                  "SelSize", "SelCount", "SelSeconds"))
        # 'values' 0=Access, 1=Size, 2=Selected, 3=StatTime, 4=StatSize,
        #          5=Count, 6=Seconds, 7=SelSize, 8=SelCount, 9=SelSeconds
        # indices 3 to 9 are hidden. In treeview 10 columns appear with tree.
        self.lib_tree.column("#0", width=630, stretch=tk.YES)
        self.lib_tree.heading(
            "#0", text="Click ??? (collapse) ??? (expand) an Artist or Album")
        self.lib_tree.column("Access", width=200, stretch=tk.YES)
        self.lib_tree.heading("Access", text="Count / Last Played")
        self.lib_tree.column("Size", width=80, anchor=tk.E, stretch=tk.YES)
        self.lib_tree.heading("Size", text="Size " + CFG_DIVISOR_UOM, anchor=tk.E)
        self.lib_tree.column("Selected", width=80, anchor=tk.E, stretch=tk.YES)
        self.lib_tree.heading("Selected", text="Play ??? / Sel. MB", anchor=tk.E)

        # Debugging columns display extra fields
        # In order to use .set method on columns they must be displayed. To
        # make "invisible", set width to 0 and stretch to tk.NO.

        # Comment next two lines to show hidden columns
        w = 0
        s = tk.NO
        # Comment next two lines to hide the hidden columns
        # w=80
        # s=tk.YES

        self.lib_tree.column("StatTime", width=w, anchor=tk.E, stretch=s)
        self.lib_tree.heading("StatTime", text="StatTime", anchor=tk.E)
        self.lib_tree.column("StatSize", width=w, anchor=tk.E, stretch=s)
        self.lib_tree.heading("StatSize", text="StatSize", anchor=tk.E)
        self.lib_tree.column("Count", width=w, anchor=tk.E, stretch=s)
        self.lib_tree.heading("Count", text="Count", anchor=tk.E)
        self.lib_tree.column("Seconds", width=w, anchor=tk.E, stretch=s)
        self.lib_tree.heading("Seconds", text="Seconds", anchor=tk.E)
        self.lib_tree.column("SelSize", width=w, anchor=tk.E, stretch=s)
        self.lib_tree.heading("SelSize", text="SelSize", anchor=tk.E)
        self.lib_tree.column("SelCount", width=w, anchor=tk.E, stretch=s)
        self.lib_tree.heading("SelCount", text="SelCount", anchor=tk.E)
        self.lib_tree.column("SelSeconds", width=w, anchor=tk.E, stretch=s)
        self.lib_tree.heading("SelSeconds", text="SelSeconds", anchor=tk.E)

        self.lib_tree["displaycolumns"] = ("Access", "Size", "Selected",
                                           # columns below set to 0 width to hide in treeview
                                           "StatTime", "StatSize", "Count", "Seconds",
                                           "SelSize", "SelCount", "SelSeconds")

        ''' Treeview select item - custom select processing '''
        self.lib_tree.bind('<Button-1>', self.button_1_click)
        self.lib_tree.bind("<Button-3>", self.popup)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=(None, MED_FONT),
                        rowheight=int(MED_FONT * 2.2))
        row_height = int(MON_FONTSIZE * 2.2)
        style.configure("Treeview", font=(None, MON_FONTSIZE),
                        rowheight=row_height)
        style.configure('Treeview', indent=row_height + 6)

        ''' Create images for checked, unchecked and tristate '''
        self.checkboxes = img.make_checkboxes(row_height - 8, 'black',
                                              'white', 'deepskyblue')
        self.lib_tree.tag_configure("unchecked", image=self.checkboxes[0])
        self.lib_tree.tag_configure("tristate", image=self.checkboxes[1])
        self.lib_tree.tag_configure("checked", image=self.checkboxes[2])

        ''' Create images for open, close and empty '''
        width = row_height - 9
        self.triangles = []  # list to prevent Garbage Collection
        img.make_triangles(self.triangles, width, 'black', 'grey')

        self.lib_tree.grid(row=0, column=0, sticky=tk.NSEW)

        '''
                    B I G   T I C K E T   E V E N T
         
        Create Treeview item list with NO songs selected YET. '''
        self.manually_checked = False  # Used for self.reverse/self.toggle
        self.populate_lib_tree(dtb)

        ''' Treeview Scrollbars '''
        # Create a vertical scrollbar linked to the frame.
        v_scroll = tk.Scrollbar(frame2, orient=tk.VERTICAL, width=sbar_width,
                                command=self.lib_tree.yview)
        v_scroll.grid(row=0, column=1, sticky=tk.NS)
        self.lib_tree.configure(yscrollcommand=v_scroll.set)

        # Create a horizontal scrollbar linked to the frame.
        h_scroll = tk.Scrollbar(frame2, orient=tk.HORIZONTAL, width=sbar_width,
                                command=self.lib_tree.xview)
        h_scroll.grid(row=1, column=0, sticky=tk.EW)
        self.lib_tree.configure(xscrollcommand=h_scroll.set)

        ''' Treeview Buttons '''
        frame3 = tk.Frame(master_frame, bg="Blue", bd=2, relief=tk.GROOVE,
                          borderwidth=BTN_BRD_WID)
        frame3.grid_rowconfigure(0, weight=1)
        frame3.grid_columnconfigure(0, weight=0)
        frame3.grid(row=1, column=0, sticky=tk.NW)

        ''' Global variables of active children '''
        self.play_top = None                    # Music player selected songs
        self.play_top_is_active = False         # Playing songs window open?
        self.sam_top_is_active = False          # sample middle of song open?
        self.loc_top_is_active = False          # locations treeview open?
        self.cmp_top_is_active = False          # compare locations open?
        self.dia_top_is_active = False          # Is blocking dialog box open?
        self.syn_top_is_active = False          # Sync Time Index window open?
        self.sync_paused_music = False          # Important this is False now
        self.sync_changed_score = False         # For warning messages
        self.sync_ffplay_is_running = False     # Music playing for Syncing?
        self.loc_keep_awake_is_active = False   # Prevent remote host sleeping?

        ''' ??? Close Button ??? ??? '''
        self.lib_top.bind("<Escape>", self.close)
        self.lib_top.protocol("WM_DELETE_WINDOW", self.close)
        self.close_text = "??? Close"  # Variable button text
        self.lib_tree_btn1 = tk.Button(frame3, text=self.close_text,
                                       width=BTN_WID - 2, command=self.close)
        self.lib_tree_btn1.grid(row=0, column=0, padx=2)
        #if self.refresh_play_top:
        #    thread = self.refresh_play_top
        #else:
        #    thread = None
        self.tt.add_tip(self.lib_tree_btn1,
                        "Close mserve and any windows mserve opened.", anchor="nw")

        ''' ???  Play Button '''
        self.play_text = "???  Play"  # play songs window is opened.
        self.lib_tree_btn2 = tk.Button(frame3, text=self.play_text,
                                       width=BTN_WID, command=self.play_items)
        self.lib_tree_btn2.grid(row=0, column=1, padx=2)
        self.tt.add_tip(self.lib_tree_btn2, "Play selected songs.", anchor="nw")

        ''' Save button '''
        # Floppy Disk U+1F4BE ????  Hard Disk U+1F5B4 ????
        self.save_text = "????  Save playlist"  # save songs window is opened.
        self.lib_tree_btn3 = tk.Button(frame3, text=self.save_text,
                                       width=BTN_WID - 1, command=self.save_items)
        self.lib_tree_btn3.grid(row=0, column=2, padx=2)
        self.tt.add_tip(self.lib_tree_btn3,
                        "Save playlist (selected songs in sorted order).",
                        anchor="nw")
        ''' Load button '''
        self.load_text = "????  Load playlist"  # Load songs window is opened.
        self.lib_tree_btn4 = tk.Button(frame3, text=self.load_text,
                                       width=BTN_WID - 1, command=self.load_items)
        self.lib_tree_btn4.grid(row=0, column=3, padx=2)
        self.tt.add_tip(self.lib_tree_btn4,
                        "Load new playlist (changes selections and sort order).",
                        anchor="nw")
        ''' Refresh Treeview Button u  1f5c0 ???? '''
        ''' ????  Update differences Button u1f5d8 ????'''
        self.rebuild_text = "???? Refresh library"  # Rebuild MusicTree
        self.lib_tree_btn5 = tk.Button(frame3, text=self.rebuild_text,
                                       width=BTN_WID - 1, command=self.rebuild_lib_tree)
        self.lib_tree_btn5.grid(row=0, column=4, padx=2)
        self.tt.add_tip(self.lib_tree_btn5, "Scan disk for songs added and removed.",
                        anchor="ne")

        ''' Rip CD Button ???? (1f5b8) '''
        self.import_text = "????  Rip CD"
        self.lib_tree_btn6 = tk.Button(frame3, text=self.import_text,
                                       width=BTN_WID - 2, command=self.rip_cd)
        self.lib_tree_btn6.grid(row=0, column=5, padx=2)
        self.tt.add_tip(self.lib_tree_btn6,
                        "Convert songs from Audio CD to music files.", anchor="ne")

        ''' Colors for tags '''
        self.ignore_item = None
        self.lib_tree.tag_configure('popup_sel', foreground='ForestGreen')
        self.lib_tree.tag_configure('play_sel', foreground='Red')

        ''' Refresh last played 999 ago, every minute '''
        self.lib_top_is_active = True  # Tell refresh_items() to run
        self.last_inotify_time = None  # Last time bubble message sent
        self.refresh_items()  # Update elapsed play time

        ''' Menu bars: File, Edit, View, Search, About '''
        mb = tk.Menu(self.lib_top)
        file_bar = tk.Menu(mb, tearoff=0)
        file_bar.add_command(label="New Location", font=(None, MED_FONT),
                             command=lambda: self.loc_add_new(caller='Drop', mode='Add'))
        file_bar.add_command(label="New Playlist", font=(None, MED_FONT),
                             command=self.new_items)
        file_bar.add_command(label="Open Location & Play",
                             font=(None, MED_FONT),
                             command=lambda: self.loc_open_play(caller='Drop', mode='Open'))
        file_bar.add_command(label="Open Playlist", font=(None, MED_FONT),
                             command=self.load_items)
        file_bar.add_command(label="Save Playlist", font=(None, MED_FONT),
                             command=self.save_items)
        # UTF-8 3 dots U+2026 ???
        file_bar.add_command(label="Save Playlist as???", font=(None, MED_FONT),
                             command=self.save_items)
        file_bar.add_command(label="Append Playlist", font=(None, MED_FONT),
                             command=self.append_items)

        file_bar.add_separator()
        file_bar.add_command(label="Restart", font=(None, MED_FONT),
                             command=self.restart)
        file_bar.add_command(label="Exit", font=(None, MED_FONT),
                             command=self.close)

        mb.add_cascade(label="File", menu=file_bar, font=(None, MED_FONT))

        # Edit Menu - Edit Location
        edit_bar = tk.Menu(mb, tearoff=0)
        edit_bar.add_command(label="Edit Location", font=(None, MED_FONT),
                             command=lambda: self.loc_edit(caller='Drop', mode='Edit'))
        edit_bar.add_command(label="Compare Location", font=(None, MED_FONT),
                             command=lambda: self.loc_compare(caller='Drop', mode='Compare'))
        edit_bar.add_command(label="Forget Location", font=(None, MED_FONT),
                             command=lambda: self.loc_forget(caller='Drop', mode='Forget'))

        mb.add_cascade(label="Edit", menu=edit_bar, font=(None, MED_FONT))

        # View menu - Song order (strip track and extension)
        view_bar = tk.Menu(mb, tearoff=0)
        view_bar.add_command(label="Show Location", font=(None, MED_FONT),
                             command=lambda: self.show_location(caller='Drop', mode='Show'))
        view_bar.add_command(label="Debug", font=(None, MED_FONT),
                             command=self.show_monitors)

        mb.add_cascade(label="View", menu=view_bar, font=(None, MED_FONT))

        # Search menu - search by words in any order
        # About Menu - Need author name?

        self.lib_top.config(menu=mb)
        dtb.close()  # Close our startup messages dtb

        ''' Load last selections and begin playing with last song '''
        self.saved_selections = []
        self.load_last_selections()

        ''' When load_last_selections() ends we need to enter idle loop
            until self.close() is called.
        '''

        while self.lib_top:
            # self.lib_top.update_idletasks()  # doesn't allow tree to scroll
            if self.killer.kill_now:
                # SIGTERM to shut down / reboot was received
                self.close()
            self.lib_top.update()  # process events in queue
            # What happens when Play is clicked and play_items() starts?
            if not self.lib_top:
                # self.close() has set to None
                break
            self.lib_top.after(50)

    def populate_lib_tree(self, delayed_textbox):

        """ Add Artist, Album and Song to treeview listbox.
            Set tags "Artist", "Album" or "Song".
            Initialize artists expanded and albums collapsed.
            All songs are NOT selected. They will be selected LATER.

            NOTE: With cell phone, dtb() may be mounted and every 30 frames
                  the current artist/album is displayed.
        """

        LastArtist = ""
        LastAlbum = ""
        CurrAlbumId = ""  # When there are no albums?
        CurrArtistId = ""  # When there are no albums?

        start_dir_sep = START_DIR.count(os.sep) - 1  # Number of / separators
        global PRUNED_SUBDIRS
        # print('PRUNED_SUBDIRS:', PRUNED_SUBDIRS)
        start_dir_sep = start_dir_sep - PRUNED_SUBDIRS

        for i, os_name in enumerate(self.song_list):

            # split /mnt/music/Artist/Album/Song.m4a into list
            '''
                Our sorted list may have removed subdirectory levels using:
                
                work_list = [w.replace(os.sep + NO_ALBUM_STR + os.sep, os.sep) \
                     for w in work_list]

            '''
            groups = os_name.split(os.sep)
            #            Artist = str(groups [start_dir_sep+1])
            #            Album = str(groups [start_dir_sep+2])
            #            Song = str(groups [start_dir_sep+3])
            Artist = groups[start_dir_sep + 1]
            Album = groups[start_dir_sep + 2]
            Song = groups[start_dir_sep + 3]

            if Artist != LastArtist:
                #  0=Access, 1=Size, 2=Selected Size, 3=StatTime, 4=StatSize,
                #  5=Count, 6=Seconds, 7=SelSize, 8=SelCount, 9=SelSeconds
                # Dec 28 2020 - Selected Size is now Song Sequence Number
                CurrArtistId = self.lib_tree.insert("", "end", text=Artist,
                                                    tags=("Artist",
                                                          "unchecked"), open=True,
                                                    values=("", "", '',
                                                            0.0, 0, 0, 0, 0, 0, 0))
                #              Access    Selected   StatSize  sSize  sSeconds
                #              0         2          4         6       8
                # 'values' = [ "",  "",  "",  0.0,  0,  0,    0,  0,  0 ]
                #                   1         3         5         7
                #                   Size      StatTime  Count     sCount

                # Treeview bug inserts integer 0 as string 0, must overwrite
                self.tree_col_range_replace(CurrArtistId, 5,
                                            [0, 0, 0, 0, 0, 0])

                LastArtist = Artist
                LastAlbum = ""  # Force subtotal break for Album

            if Album != LastAlbum:
                CurrAlbumId = self.lib_tree.insert(CurrArtistId, "end",
                                                   text=Album, tags=("Album",
                                                                     "unchecked"),
                                                   values=("", "", "",
                                                           0.0, 0, 0, 0, 0, 0, 0))

                # Treeview bug inserts integer 0 as string 0, must overwrite
                self.tree_col_range_replace(CurrAlbumId, 5,
                                            [0, 0, 0, 0, 0, 0])

                LastAlbum = Album

            ''' Build full song path from song_list[] '''
            full_path = os_name
            full_path = full_path.replace(os.sep + NO_ARTIST_STR, '')
            full_path = full_path.replace(os.sep + NO_ALBUM_STR, '')

            if delayed_textbox.update(full_path):
                # delayed_textbox returns true only when visible otherwise
                # we are in quiet mode because not enough time has passed.
                self.lib_tree.see(CurrArtistId)
                self.lib_tree.update()

            # os.stat gives us all of file's attributes
            stat = os.stat(full_path)
            size = stat.st_size
            self.tree_col_range_add(CurrAlbumId, 5, [size, 1])
            self.tree_col_range_add(CurrArtistId, 5, [size, 1])
            self.tree_title_range_add(5, [size, 1])  # update title bar
            converted = float(size) / float(CFG_DIVISOR_AMT)
            fsize = str(round(converted, CFG_DECIMAL_PLACES))

            # Format date as "Abbreviation - 99 Xxx Ago"
            ftime = tmf.ago(float(stat.st_atime))

            ''' Add the song '''
            self.lib_tree.insert(CurrAlbumId, "end", iid=str(i), text=Song,
                                 tags=("Song", "unchecked"), values=(ftime,
                                                                     fsize, '', float(stat.st_atime),
                                                                     stat.st_size, 1, 0, 0, 0, 0))
            self.tree_col_range_replace(str(i), 6,
                                        [1, 0, 0, 0, 0])

            # TODO: Add Music and History tables. Take out of sql.py
            #       Analyze performance hit for updating Music Table
            #       with most recent access time (ie last played time)

        ''' Calculate columns for Artists and Albums with no songs '''
        # ext.t_init('Calculate all Artists and Albums')
        for artist in self.lib_tree.get_children():
            self.tree_col_parent_format(artist, "artist_sel")
            for album in self.lib_tree.get_children(artist):
                self.tree_col_parent_format(album, "album_sel")
        # ext.t_end('print')

    def toggle_select(self, song, album, artist):
        """ Toggle song selection off and on. Update selected values and
            roll up totals into parents.
        """
        # 'values' 0=Access, 1=Size, 2=Selected Size, 3=StatTime, 4=StatSize,
        #          5=Count, 6=Seconds, 7=SelSize, 8=SelCount, 9=SelSeconds
        # Set slice to StatSize, Count, Seconds
        total_values = slice(4, 7)  # start at index, stop before index
        #select_values = slice(7, 10)  # start at index, stop before index

        tags = self.lib_tree.item(song)['tags']
        # Can't Replace "songsel" with "checked" because artist is checked too
        if "songsel" in tags:
            # We will toggle off and subtract from selected parent totals
            tags.remove("songsel")
            self.lib_tree.set(song, "Selected", "")  # Blank selected size
            self.lib_tree.item(song, tags=tags)
            # noinspection PyProtectedMember
            self.lib_tree._uncheck_ancestor(song)  # in CheckboxTreeview()
            self.play_remove(song)  # Remove from playlist
            # Get StatSize, Count and Seconds multiplying by negative 1
            adj_list = [element * -1 for element in
                        self.lib_tree.item(song)['values'][total_values]]
        else:
            # We will toggle on and add to selected parent totals
            tags.append("songsel")
            #       Dec. 28 2020 - Selected MB is now Song Number Sequence
            # noinspection PyBroadException
            try:
                song_number = self.saved_selections.index(song) + 1
            except:
                # print('toggle_select(): song not found iid:',song)
                song_number = 0
            number_digits = len(self.saved_selections)
            number_str = self.play_padded_number(song_number, number_digits)
            # self.lib_tree.set(song, "Selected", self.lib_tree.set(song, "Size"))
            self.lib_tree.set(song, "Selected", number_str)
            self.lib_tree.item(song, tags=tags)
            # noinspection PyProtectedMember
            self.lib_tree._check_ancestor(song)  # in CheckboxTreeview()
            self.play_insert(song)  # Insert into playlist
            # Get StatSize, Count and Seconds
            adj_list = self.lib_tree.item(song)['values'][total_values]  # 1 past

        self.tree_col_range_add(song, 8, adj_list)  # Column number passed
        self.tree_col_range_add(album, 8, adj_list, tagsel='album_sel')
        self.tree_col_range_add(artist, 8, adj_list, tagsel='artist_sel')
        self.tree_title_range_add(8, adj_list)  # Pass start index

    def tree_col_range_replace(self, iid, numb, init_list):
        """ Initialize treeview columns to list of values
        """
        for i, new_val in enumerate(init_list):
            col_str = "#" + str(numb + i)  # eg '#3'
            self.lib_tree.set(iid, col_str, new_val)

    def tree_col_range_add(self, iid, numb, add_list, tagsel=""):
        """ Add list of values to contiguous treeview columns
            To subtract just add negative numbers.
        """
        for i, add_val in enumerate(add_list):
            col_str = "#" + str(numb + i)  # eg '#3'
            curr_val = self.lib_tree.set(iid, col_str)
            add_val += curr_val
            self.lib_tree.set(iid, col_str, add_val)

        if tagsel:
            self.tree_col_parent_format(iid, tagsel)

    def tree_col_parent_format(self, iid, tagsel):
        """ Artist or Album format selected totals into columns """

        tags = self.lib_tree.item(iid)['tags']

        # Update last played column with number of songs selected
        # set with no argument performs a get
        song_count = self.lib_tree.set(iid, "Count")
        selected_count = self.lib_tree.set(iid, "SelCount")

        # Human readable size. eg 12345678 becomes 12.3 MB
        size = self.lib_tree.set(iid, "StatSize")
        converted = float(size) / float(CFG_DIVISOR_AMT)
        all_sizes = round(converted, CFG_DECIMAL_PLACES)
        size = self.lib_tree.set(iid, "SelSize")
        converted = float(size) / float(CFG_DIVISOR_AMT)
        all_selected = round(converted, CFG_DECIMAL_PLACES)

        if selected_count > 0:
            # At least one song selected so add tag and update text
            if tagsel not in tags:
                tags.append(tagsel)

            self.lib_tree.set(iid, "Access", str(song_count) + ' songs, '
                              + str(selected_count) + ' selected')
            self.lib_tree.set(iid, "Size", str(all_sizes))
            self.lib_tree.set(iid, "Selected", str(all_selected))
        else:
            # No songs selected so clear tag
            if tagsel in tags:
                tags.remove(tagsel)

            self.lib_tree.set(iid, "Access", str(song_count) + ' songs')
            self.lib_tree.set(iid, "Size", str(all_sizes))
            self.lib_tree.set(iid, "Selected", "")  # Do we need to clear?

        self.lib_tree.item(iid, tags=tags)

    def tree_title_range_add(self, start_ndx, add_list):
        """ list of values to add to title bar
            Treeview column numbers align to our totals list indices.
                 0 = location name
                 1 = playlist name - may be empty, '.pkl' extension stripped
                 2 = # + " songs" (Access)
                   + , #+"selected" (string concatenated may be entirely blank)
                 3 = Size of files + " MB Used" (fSize)
                   + , #+"selected" (string concatenated may be entirely blank)
                 4 = Music Duration DDDd:HHh:MMm:SSs, DDDd:HHh:MMm:SSs (fSelect)
                 5 = Total Sizes (Size)
                 6 = Total Songs (Count)
                 7 = Total Seconds (Seconds)
                 8 = (SelSize)
                 9 = (SelCount)
                10 = (SelSeconds)
        """
        # Copy and paste legend into code for guidance
        #                       Loc     Songs   Time    Count sSize sSeconds
        #                       0       2       4       6     8     10
        # elf.lib_top_totals = [ "", "", "", "", "",  0, 0, 0, 0, 0, 0 ]
        #                           1       3        5     7     9
        #                           Play    Space    Size  Secs  sCount

        for i, add_val in enumerate(add_list):
            ndx = start_ndx + i
            # After working check if += add_list inserts rather than adds
            # self.lib_top_totals[ndx] = self.lib_top_totals[ndx] + add_list[i]
            self.lib_top_totals[ndx] += add_list[i]

        # Put counts into title bar
        song_count = self.lib_top_totals[6]
        selected_count = self.lib_top_totals[9]

        # Human-readable size 12345678 becomes 12.3 MB
        size = self.lib_top_totals[5]
        converted = float(size) / float(CFG_DIVISOR_AMT)
        all_sizes = round(converted, CFG_DECIMAL_PLACES)
        size = self.lib_top_totals[8]
        converted = float(size) / float(CFG_DIVISOR_AMT)
        all_selected = round(converted, CFG_DECIMAL_PLACES)
        """
            "??????? "    # big space + UTF-8 (1f3b5) + normal space
            "??????? "  # big space + UTF-8 (1f5b8) + normal space
            "??????? "   # big space + UTF-8 (1f4c5) + normal space
            "??????? "  # big space + UTF-8 (1f551) + normal space
        """
        if selected_count > 0:
            # Format for at least one song selected
            self.lib_top_totals[2] = "?????????????" + str(song_count) + '  songs, ' + \
                                     str(selected_count) + ' selected  '
            self.lib_top_totals[3] = "?????????????" + str(all_sizes) + " " + \
                                     CFG_DIVISOR_UOM + " used, " + str(all_selected) + \
                                     " " + CFG_DIVISOR_UOM + ' selected'
        else:
            # Format for NO songs selected
            self.lib_top_totals[2] = "?????????????" + str(song_count) + '???songs  '
            self.lib_top_totals[3] = "?????????? ???" + str(all_sizes) + " " + \
                                     CFG_DIVISOR_UOM + " used"

        self.lib_top.title(self.lib_top_totals[0] + self.lib_top_totals[1] +
                           self.lib_top_totals[2] + self.lib_top_totals[3] +
                           " - mserve")

    '''
    def tree_title__add(self, ndx, val):
        """ Add a value to single index.
            Not efficient but created for conformity with other add functions.
        """
        self.lib_top_totals[ndx] = self.lib_top_totals[ndx] + add_list[i]
    '''

    # ==============================================================================
    #
    #       MusicTree Processing - Location and Dropdown Menu options
    #
    # ==============================================================================

    def loc_close(self):
        #def loc_close(self, *args):
        """ Close location treeview """
        if self.loc_top_is_active is False:
            return  # We are already closed
        self.loc_top_is_active = False
        if self.cmp_top_is_active:
            self.cmp_close()  # Close Compare location treeview
        root.update()
        root.after(50)  # Give time for treeview to close
        self.loc_top.destroy()  # Close the treeview window

    def loc_keep_awake(self):
        """ Every x minutes issue keep awake command for server. For example:
            'ssh dell "touch /tmp/mserve"' works for ssh-activity bash script.

        """

        if self.loc_keep_awake_is_active is False:
            return  # We are shutting down

        self.awake_last_time_check = time.time()
        if self.awake_last_time_check > self.next_active_cmd_time:
            # Test if still awake before sending active command
            # NOTE: Use LODICT[] because user can change lc.DICT[] values
            test_passed = lc.test_host_up(LODICT['host'])
            if self.loc_keep_awake_is_active is False:
                return
            if test_passed is False:
                print('Host:', LODICT['host'], 'is off-line. Restarting...')
                self.restart()              # Temporary - only start device
                if test_passed is False:    # Dummy test always true
                    return                  # Code below is not developed

                # TODO:
                '''
                  When resuming after long system suspend:

                    Host: dell is off-line. Quiting...
                    Checking to save: /home/rick/.config/mserve/last_location
                    No 'iid' found in 'LODICT' for: /mnt/music/
                    ssh: connect to host dell port 22: No route to host
                    
                    FIXED NOW I THINK because this function was broken:
                                lc.save_mserve_location(iid)

                    FIXED AGAIN (Nov 12) because 'return' added above.

                    Nov 12 - About 10 to 15 minutes after resuming got bubble
                    message: Library has changed and files need refreshing. Then
                    on command line:

                        last message time: 1605229131.81 next message time: 1605230331.81
                        refresh_items(): 931.62436986
                        Host: dell is off-line. Quiting...

                    Did not issue kill -9. Did not see Disk Wait+ status. FTR
                    931 seconds = 15.5 minutes. Bottom line refresh_items()
                    must poll connection before issuing os.walk(). Also why
                    does it wake up before loc_keep_awake? Can it test
                    loc_keep_awake()'s last time?

                    
                '''

            result = os.popen(LODICT['activecmd']).read().strip()
            if len(result) > 4:
                print('loc_keep_awake() result:', result)
            self.awake_last_time_check = time.time()
            self.next_active_cmd_time = self.awake_last_time_check + (60 * LODICT['activemin'])

            # noinspection SpellCheckingInspection
            '''
            now2 = datetime.datetime.now()
            print(now2.strftime("%H:%M:%S"),'Wake command:',LODICT['activecmd'])
            ftime = datetime.datetime.fromtimestamp(self.next_active_cmd_time)
            print('Next keep awake time:', ftime.strftime("%H:%M:%S"))
            '''
            # inspection SpellCheckingInspection

            if self.loc_keep_awake_is_active is False:
                return

        # root.after(250, self.loc_keep_awake)
        ''' ERROR when click X to close lib_top treeview:

                invalid command name "139661461069488loc_keep_awake"
                    while executing
                "139661461069488loc_keep_awake"
                    ("after" script)

            Final solution was changing global variable:
                RESTART_SLEEP = .1              # Delay for mserve close down
            to:
                RESTART_SLEEP = .3              # Delay for mserve close down
                
            Note if program just opened, this delay is too short...
        '''

        # noinspection PyBroadException
        try:
            # Was running root.after every 1/4 second, change every minute and
            # got lock up in refresh_items() running first.  On file server
            # this was causing 'ps' status 'D+' (Disk Sleep foreground) and
            # program could not be killed for 15 min when resuming from suspend.
            self.lib_top.after(KEEP_AWAKE_MS, self.loc_keep_awake)
        except:
            # pass
            return

    def loc_create_tree(self, sbar_width=12, caller="", mode=""):
        """ Create location treeview listbox
            'caller' are dynamic based on caller:
                'Drop' called from top bar dropdown menu
                'Tree' called from within our own Treeview buttons
            'mode' tells us which buttons to paint:
                'Open', 'Add', 'Edit', 'Show', 'Forget', 'Compare'

            The 'Close' and 'Test' buttons are always shown
        """
        if caller != "":
            pass    # Pycharm error, should probably get rid of parameter...

        if self.loc_top_is_active:  # Already processing locations?
            self.loc_top.focus_force()  # Get focus
            self.loc_top.lift()  # Raise in stacking order
            messagebox.showinfo(title="Location processing active",
                                message="An instance of location processing is " +
                                        "already active.", parent=self.loc_top)
            root.update()
            return  # Don't want two windows opened

        self.loc_top = tk.Toplevel()
        self.loc_top.minsize(g.WIN_MIN_WIDTH, g.WIN_MIN_HEIGHT)
        self.loc_top_is_active = True

        ''' Place Window top-left of parent window with PANEL_HGT padding '''
        xy = (self.lib_top.winfo_x() + PANEL_HGT,
              self.lib_top.winfo_y() + PANEL_HGT)
        self.loc_top.minsize(width=BTN_WID * 10, height=PANEL_HGT * 4)
        self.loc_top.geometry('+%d+%d' % (xy[0], xy[1]))

        title = "Music Locations - Select location to " + mode
        self.loc_top.title(title)
        self.loc_top.columnconfigure(0, weight=1)
        self.loc_top.rowconfigure(0, weight=1)

        ''' Set program icon in taskbar '''
        img.taskbar_icon(self.loc_top, 64, 'white', 'lightskyblue', 'black')

        ''' Create master frame '''
        master_frame = tk.Frame(self.loc_top, borderwidth=BTN_BRD_WID,
                                relief=tk.RIDGE)
        master_frame.grid(sticky=tk.NSEW)

        # Create a frame for the treeview and scrollbar(s).
        frame2 = tk.Frame(master_frame)
        tk.Grid.rowconfigure(frame2, 0, weight=1)
        tk.Grid.columnconfigure(frame2, 0, weight=1)
        frame2.grid(row=0, column=0, sticky=tk.NSEW)

        ''' Treeview List Box, Columns and Headings '''
        self.loc_tree = ttk.Treeview(frame2, columns=("ID", "Path"), height=7,
                                     selectmode="browse", show=('tree', 'headings'))
        self.loc_tree.column("#0", width=500, stretch=tk.YES)
        self.loc_tree.heading("#0", text="Location Name")
        self.loc_tree.column("ID", width=100, stretch=tk.NO)
        self.loc_tree.heading("ID", text="ID (Dir)")
        self.loc_tree.column("Path", width=800, stretch=tk.YES)
        self.loc_tree.heading("Path", text="Top Directory for Music " +
                                           "(Any device, drive or path)")

        ''' This moves focus to window but doesn't lift it '''
        # self.loc_tree.tk_focusFollowsMouse()
        self.loc_tree.grid(row=0, column=0, sticky=tk.NSEW)

        ''' Create Treeview item listbox '''
        self.loc_tree.delete(*self.loc_tree.get_children())
        for iid in lc.get_children():
            # NOTE: Never use LODICT which is our starting dictionary
            loc_item = lc.item(iid)
            self.loc_tree.insert('', "end", iid=iid, text=loc_item["name"],
                                 values=(loc_item["iid"], loc_item["topdir"]))

        ''' Treeview Scrollbars '''
        # Create a vertical scrollbar linked to the frame.
        v_scroll = tk.Scrollbar(frame2, orient=tk.VERTICAL, width=sbar_width,
                                command=self.loc_tree.yview)
        v_scroll.grid(row=0, column=1, sticky=tk.NS)
        self.loc_tree.configure(yscrollcommand=v_scroll.set)

        # Create a horizontal scrollbar linked to the frame.
        h_scroll = tk.Scrollbar(frame2, orient=tk.HORIZONTAL, width=sbar_width,
                                command=self.loc_tree.xview)
        h_scroll.grid(row=1, column=0, sticky=tk.EW)
        self.loc_tree.configure(xscrollcommand=h_scroll.set)

        ''' Treeview Buttons '''
        frame3 = tk.Frame(master_frame, bg="Blue", bd=2, relief=tk.GROOVE,
                          borderwidth=BTN_BRD_WID)
        frame3.grid_rowconfigure(0, weight=1)
        frame3.grid_columnconfigure(0, weight=0)
        frame3.grid(row=1, column=0, sticky=tk.NW)
        self.location_text = "Show Location"  # Default

        ''' ??? Close Button - Always visible '''
        self.loc_top.bind("<Escape>", self.loc_close)
        self.loc_top.protocol("WM_DELETE_WINDOW", self.loc_close)
        self.loc_tree_btn1 = tk.Button(frame3, text="??? Close",
                                       width=BTN_WID, command=self.loc_close)
        self.loc_tree_btn1.grid(row=0, column=0, padx=2)

        ''' ???  Test Button  - Always visible '''
        self.loc_tree_btn2 = tk.Button(
            frame3, text="???  Test", width=BTN_WID,
            command=lambda: self.loc_test(caller='Tree', mode='Test'))
        self.loc_tree_btn2.grid(row=0, column=1, padx=2)

        ''' ???  Open Location Button '''
        if mode == 'Open':
            self.location_text = "Open Location"
            self.loc_tree_btn2 = tk.Button(
                frame3, text="???  Open & play", width=BTN_WID,
                command=lambda: self.loc_open_play(caller='Tree', mode='Open'))
            self.loc_tree_btn2.grid(row=0, column=2, padx=2)
            # NOTE: If column 2 is missing, the other buttons shift left OK

        ''' Show button - Always visible '''
        # Magnifying glass ?????????? U+1F50D
        self.loc_tree_btn3 = tk.Button(
            frame3, text="????  Show location", width=BTN_WID,
            command=lambda: self.show_location(caller='Tree', mode='Show'))
        self.loc_tree_btn3.grid(row=0, column=3, padx=2)

        # Following buttons will only appear when those functions are callers
        ''' Add button '''
        if mode == 'Add':
            # Magnifying glass ?????????? U+1F50D
            self.loc_tree_btn4 = tk.Button(
                frame3, text="????   Add location", width=BTN_WID,
                command=lambda: self.loc_add_new(caller='Tree', mode='Add'))
            self.location_text = "Add Location"
            self.loc_tree_btn4.grid(row=0, column=4, padx=2)

        ''' Edit button u  1f5c0 ???? '''
        if mode == 'Edit':
            # Magnifying glass ?????????? U+1F50D
            self.loc_tree_btn5 = tk.Button(
                frame3, text="????   Edit location", width=BTN_WID,
                command=lambda: self.loc_edit(caller='Tree', mode='Edit'))
            self.location_text = "Edit Location"
            self.loc_tree_btn5.grid(row=0, column=5, padx=2)

        ''' Forget Button u  1f5c0 ???? '''
        if mode == 'Forget':
            # Magnifying glass ?????????? U+1F50D
            self.loc_tree_btn6 = tk.Button(
                frame3, text="????   Forget location", width=BTN_WID,
                command=lambda: self.loc_forget(caller='Tree', mode='Forget'))
            self.location_text = "Forget Location"
            self.loc_tree_btn6.grid(row=0, column=6, padx=2)

        ''' Compare Button  ?????????? U+1F50D '''
        if mode == 'Compare':
            # Magnifying glass ?????????? U+1F50D
            self.loc_tree_btn7 = tk.Button(
                frame3, text="????  Compare", width=BTN_WID,
                command=lambda: self.loc_compare(caller='Tree', mode='Compare'))
            self.location_text = "Compare Location"
            self.loc_tree_btn7.grid(row=0, column=7, padx=2)

        ''' Frame for Location Data Entry '''
        self.loc_F4 = tk.LabelFrame(self.loc_top, borderwidth=BTN_BRD_WID,
                                    text=self.location_text, padx=10, pady=10,
                                    relief=tk.GROOVE, font=('calibre', 13, 'bold'))
        self.loc_F4.grid(row=3, column=0, sticky=tk.NSEW)
        self.loc_F4.grid_rowconfigure(0, weight=1)
        self.loc_F4.grid_columnconfigure(1, weight=2)  # Note weight to stretch

        ''' Define tk variables used with .set() and .get() '''
        self.iid_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.topdir_var = tk.StringVar()
        self.host_var = tk.StringVar()
        self.wakecmd_var = tk.StringVar()
        self.testcmd_var = tk.StringVar()
        # self.testrep_var=tk.IntVar()           # int() crash if ./letter/space
        self.testrep_var = tk.StringVar()
        self.testrep_var.set("0")
        self.mountcmd_var = tk.StringVar()
        self.activecmd_var = tk.StringVar()
        self.activemin_var = tk.StringVar()
        self.activemin_var.set("0")

        #fontB = ('calibre', 13, 'bold')  # Old Field name font BOLD
        #font1 = ('calibre', 13, 'normal')  # Field name font
        #font2 = ('calibre', 12, 'normal')  # Date entry font
        self.state = 'normal'  # data entry is not 'readonly'
        ms_font1 = (None, MON_FONTSIZE)  # Temporary for error message
        ms_font2 = (None, MON_FONTSIZE)  # Temporary for error message
        tk.Label(self.loc_F4, text='Name:',
                 font=ms_font1).grid(row=0, column=0, sticky=tk.E, padx=10)
        self.name_fld = tk.Entry(self.loc_F4, font=ms_font2,
                                 state=self.state, textvariable=self.name_var)
        self.name_fld.grid(row=0, column=1, sticky=tk.EW)
        self.name_fld.focus_force()  # First data entry field

        tk.Label(self.loc_F4, text='Top Directory for Music:',
                 font=ms_font1).grid(row=1, column=0, sticky=tk.E, padx=10)
        self.topdir_fld = tk.Entry(self.loc_F4, font=ms_font2,
                                   state=self.state, textvariable=self.topdir_var)
        self.topdir_fld.grid(row=1, column=1, sticky=tk.EW)

        tk.Label(self.loc_F4, text='Optional Host Name:',
                 font=ms_font1).grid(row=2, column=0, sticky=tk.E, padx=10)
        self.host_fld = tk.Entry(self.loc_F4, font=ms_font2,
                                 state=self.state, textvariable=self.host_var)
        self.host_fld.grid(row=2, column=1, sticky=tk.EW)

        tk.Label(self.loc_F4, text='Local command to wakeup sleeping host:',
                 font=ms_font1).grid(row=3, column=0, sticky=tk.E, padx=10)
        self.wakecmd_fld = tk.Entry(self.loc_F4, font=ms_font2,
                                    state=self.state, textvariable=self.wakecmd_var)
        self.wakecmd_fld.grid(row=3, column=1, sticky=tk.EW)

        tk.Label(self.loc_F4, text='SSH command to test if host awake:',
                 font=ms_font1).grid(row=4, column=0, sticky=tk.E, padx=10)
        self.testcmd_fld = tk.Entry(self.loc_F4, font=ms_font2,
                                    state=self.state, textvariable=self.testcmd_var)
        self.testcmd_fld.grid(row=4, column=1, sticky=tk.EW)

        tk.Label(self.loc_F4, text='Maximum test commands every .1 second:',
                 font=ms_font1).grid(row=5, column=0, sticky=tk.E, padx=10)
        self.testrep_fld = tk.Entry(self.loc_F4, font=ms_font2,
                                    state=self.state, textvariable=self.testrep_var)
        self.testrep_fld.grid(row=5, column=1, sticky=tk.EW)

        tk.Label(self.loc_F4, text='SSHFS locally mount music from host:',
                 font=ms_font1).grid(row=6, column=0, sticky=tk.E, padx=10)
        self.mountcmd_fld = tk.Entry(self.loc_F4, font=ms_font2,
                                     state=self.state, textvariable=self.mountcmd_var)
        self.mountcmd_fld.grid(row=6, column=1, sticky=tk.EW)

        tk.Label(self.loc_F4, text='SSH command to keep host awake:',
                 font=ms_font1).grid(row=7, column=0, sticky=tk.E, padx=10)
        self.activecmd_fld = tk.Entry(self.loc_F4, font=ms_font2,
                                      state=self.state, textvariable=self.activecmd_var)
        self.activecmd_fld.grid(row=7, column=1, sticky=tk.EW)

        tk.Label(self.loc_F4, text='Minutes between keeping host awake:',
                 font=ms_font1).grid(row=8, column=0, sticky=tk.E, padx=10)
        self.activemin_fld = tk.Entry(self.loc_F4, font=ms_font2,
                                      state=self.state, textvariable=self.activemin_var)
        self.activemin_fld.grid(row=8, column=1, sticky=tk.EW)

        # Button that will call the submit function
        self.sub_btn = tk.Button(self.loc_F4, text='Nothing Yet',
                                 command=self.loc_submit, font=ms_font1)
        self.sub_btn.grid(row=9, column=1, sticky=tk.W)

        # Button that will abandon changes, or close entry fields
        tk.Button(self.loc_F4, text='Close', command=self.loc_abandon,
                  font=ms_font1).grid(row=9, column=1, sticky=tk.E)

        # Make location input fields invisible until appropriate time
        # self.loc_F4.grid_remove()  # Makes window too small on chrome os
        self.loc_hide_fields()
        self.loc_top.update_idletasks()

    def loc_hide_fields(self):
        if GRID_REMOVE_SUPPORTED:
            self.loc_F4.grid_remove()

    def loc_show_fields(self):
        if GRID_REMOVE_SUPPORTED:
            self.loc_F4.grid()

    def loc_open_play(self, caller="", mode=""):
        """ Open location by calling loc_test() first to check success
            Called from File menu and from within self.loc_create_tree()
            Buttons are dynamic based on caller:
                'Drop' called from top bar dropdown menu
                'Tree' called from treeview button
        """
        global LODICT

        if mode != "":
            pass    # Pycharm error, should probably get rid of parameter...

        if caller == 'Drop':  # Called from dropdown Edit menu?
            self.loc_create_tree(caller='Tree', mode='Open')
            # Make location input fields invisible until appropriate time
            #            self.loc_F4.grid_remove()      # Dec. 12 2020
            self.loc_hide_fields()
            root.update()
            return

        if not caller == 'Tree':
            print("ERROR: 'caller' is neither 'Drop' nor 'Tree'.")
            return

        # We must save current selections before LODICT changes
        self.save_last_selections()
        item = self.loc_tree.selection()[0]
        if lc.test(item, self.loc_top):
            pass  # We are good to go
        else:
            # Location doesn't exist
            messagebox.showinfo(title="Location Error",
                                message="Top directory doesn't exist or is off-line.",
                                parent=self.loc_top)
            return False

        next_iid = lc.item(item)['iid']
        # print('next_iid:',next_iid)

        ''' Save last opened location iid with next iid to load '''
        lc.save_mserve_location(next_iid)

        ''' Next top directory to startup '''
        next_topdir = lc.item(item)['topdir']
        # print('next_topdir:',next_topdir)
        self.parm = next_topdir
        # print ('topdir:', self.parm)        # Forces in manual call
        self.restart_new_parameters(self)

    def loc_test(self, caller="", mode=""):
        """ Test location - host name, on-line and directory exists
            Called from File menu and from within self.loc_create_tree()
            Buttons are dynamic based on caller:
                'Drop' called from top bar dropdown menu
                'Tree' called from treeview button
        """

        if mode != "":
            pass    # Pycharm error, should probably get rid of parameter...

        if caller == 'Drop':  # Called from dropdown Edit menu?
            self.loc_create_tree(caller='Tree', mode='Test')
            # Make location input fields invisible until appropriate time
            #            self.loc_F4.grid_remove()      # Dec. 12 2020
            self.loc_hide_fields()
            self.loc_top.update_idletasks()
            return

        if not caller == 'Tree':
            print("ERROR: 'caller' is neither 'Drop' nor 'Tree'.")
            return

        if len(self.loc_tree.selection()) == 0:
            messagebox.showinfo(title="Location Error",
                                message="You must select a location to test.",
                                parent=self.loc_top)
            return False

        # 'browse' option is used so only one item will be selected all times.
        item = self.loc_tree.selection()[0]
        if lc.test(item, self.loc_top):
            messagebox.showinfo(title="Location valid",
                                message="Top directory exists. Good to go!",
                                parent=self.loc_top)
            return True
        else:
            # Location doesn't exist
            messagebox.showinfo(title="Location Error",
                                message="Top directory doesn't exist or is off-line.",
                                parent=self.loc_top)
            return False

    def loc_add_new(self, caller="", mode=""):
        """ Get new location name, directory and ssh flags / options
            Called from File menu and from within self.loc_create_tree()
            Buttons are dynamic based on caller:
                'File' called from top bar dropdown menu
        """

        if mode != "":
            pass    # Pycharm error, should probably get rid of parameter...

        if caller == 'Drop':  # Called from dropdown File menu?
            self.loc_create_tree(caller='Tree', mode='Add')
            self.loc_top.update_idletasks()

        elif not caller == 'Tree':
            print("ERROR: 'caller' is neither 'Drop' nor 'Tree'.")
            return

        self.loc_entry_state('Add', 'New')  # Create a mew entry
        #        self.loc_F4.grid()                  # Make entry grid visible
        self.loc_show_fields()
        self.loc_top.update_idletasks()

    def loc_edit(self, caller="", mode=""):
        """ Edit location name, directory and ssh flags / options
            Called from File menu and from within self.loc_create_tree()
            Buttons are dynamic based on caller:
                'Drop' called from top bar dropdown menu
                'Tree' called from treeview button
        """

        if mode != "":
            pass    # Pycharm error, should probably get rid of parameter...

        if caller == 'Drop':  # Called from dropdown Edit menu?
            self.loc_create_tree(caller='Tree', mode='Edit')
            # Make location input fields invisible until appropriate time
            #            self.loc_F4.grid_remove()      # Dec. 12 2020
            self.loc_hide_fields()
            self.loc_top.update_idletasks()
            return

        elif not caller == 'Tree':
            print("ERROR: 'caller' is neither 'Drop' nor 'Tree'.")
            return
        #        self.loc_create_tree(caller='Edit', mode='Edit')

        if len(self.loc_tree.selection()) == 0:
            messagebox.showinfo(title="Location Error",
                                message="You must select a location to edit.",
                                parent=self.loc_top)
            return False

        item = self.loc_tree.selection()[0]
        #        loc_dict = lc.item(item)

        self.loc_entry_state('Edit', item)  # Edit existing entry
        #        self.loc_F4.grid()                  # Make entry grid visible
        self.loc_show_fields()
        self.loc_top.update_idletasks()

        self.loc_populate_screen(item)  # Paint screen with lc.DICT{}

    def loc_populate_screen(self, item):
        """ Called by 'Edit', 'Show' and 'Forget' """
        loc_dict = lc.item(item)
        self.iid_var.set(loc_dict['iid'])
        self.name_var.set(loc_dict['name'])
        self.topdir_var.set(loc_dict['topdir'])
        self.host_var.set(loc_dict['host'])
        self.wakecmd_var.set(loc_dict['wakecmd'])
        self.testcmd_var.set(loc_dict['testcmd'])
        self.testrep_var.set(loc_dict['testrep'])
        self.mountcmd_var.set(loc_dict['mountcmd'])
        self.activecmd_var.set(loc_dict['activecmd'])
        self.activemin_var.set(loc_dict['activemin'])
        self.loc_top.update_idletasks()

    def show_location(self, caller="", mode=""):
        """ Show location name, directory and ssh flags / options
            Called from File menu and from within self.loc_create_tree()
            Buttons are dynamic based on caller:
                'Drop' called from top bar dropdown menu
                'Tree' called from treeview button
        """

        if mode != "":
            pass    # Pycharm error, should probably get rid of parameter...

        if caller == 'Drop':  # Called from dropdown Edit menu?
            self.loc_create_tree(caller='Show', mode='Show')
            # Make location input fields invisible until appropriate time
            #            self.loc_F4.grid_remove()      # Dec. 12 2020
            self.loc_hide_fields()
            self.loc_top.update_idletasks()
            return

        elif not caller == 'Tree':
            print("ERROR: 'caller' is neither 'Drop' nor 'Tree'.")
            return
        #        self.loc_create_tree(caller='Show', mode='Show')

        if len(self.loc_tree.selection()) == 0:
            messagebox.showinfo(title="Location Error",
                                message="You must select a location to show.",
                                parent=self.loc_top)
            return False

        item = self.loc_tree.selection()[0]
        self.loc_entry_state('Show', item)  # Show existing entry
        #        self.loc_F4.grid()                  # Make entry grid visible
        self.loc_show_fields()
        self.loc_top.update_idletasks()

        self.loc_populate_screen(item)  # Paint screen with lc.DICT{}

    def loc_forget(self, caller="", mode=""):
        """ Forget location and remove ~/.config/$USER/mserve/L999/* directory
            Called from Edit menu and from within self.loc_create_tree()
            Buttons are dynamic based on caller:
                'Drop' called from top bar dropdown menu
                'Tree' called from treeview button
        """

        if mode != "":
            pass    # Pycharm error, should probably get rid of parameter...

        if caller == 'Drop':  # Called from dropdown Edit menu?
            self.loc_create_tree(caller='Forget', mode='Forget')
            # Make location input fields invisible until appropriate time
            #            self.loc_F4.grid_remove()      # Dec. 12 2020
            self.loc_hide_fields()
            self.loc_top.update_idletasks()
            return  # Why was this removed in other spots???

        elif not caller == 'Tree':
            print("ERROR: 'caller' is neither 'Drop' nor 'Tree'.")
            return
        #        self.loc_create_tree(caller='Forget', mode='Forget')

        if len(self.loc_tree.selection()) == 0:
            messagebox.showinfo(title="Location Error",
                                message="You must select a location to forget.",
                                parent=self.loc_top)
            return False

        item = self.loc_tree.selection()[0]
        self.loc_entry_state('Forget', item)
        #        self.loc_F4.grid()                  # Make entry grid visible
        self.loc_show_fields()
        self.loc_top.update_idletasks()
        self.loc_populate_screen(item)  # Paint screen with lc.DICT{}

    def confirm_forget(self, iid):
        """ Confirm forgetting location. Cannot be current open location.
            Remove '/home/$USER/.config/mserve/L999' directory
            Rename higher '~/.config/mserve/L999' directories 1 less
            Update higher iid in locations master file 1 less
            If our opened location iid is changing call:
                lc.set_location_filenames(iid)
                Rename LODICT('iid') with new number
        """
        global LODICT
        our_current_iid = LODICT['iid']
        if iid == our_current_id:
            messagebox.showinfo(title="Location Error",
                                message="You cannot forget the location currently running.",
                                parent=self.loc_top)
            return

        result = tkMessageBox.askquestion("Forget Location Confirmation",
                                          message="This cannot be undone. Are You Sure?",
                                          parent=self.loc_top, icon='warning')
        if result == 'no':
            return

        print('WIP: existing locations must be renumbered sequentially')
        our_new_iid = lc.remove(iid)  # Do the heavy lifting

        if not our_current_iid == our_new_iid:
            LODICT = lc.item(our_new_iid)  # Reload Local Copy

    def loc_entry_state(self, mode, iid):
        """ Set location data entry field states
        """

        self.loc_mode = mode  # Used by loc_submit()
        self.loc_iid = iid
        self.location_text = mode + " Location"
        self.loc_F4['text'] = self.location_text

        if mode is 'Show' or mode is 'Forget' or mode is 'Compare':
            self.state = 'readonly'  # Data entry NOT allowed (can copy)
        else:
            # TODO: Separate state for Name, don't change on Edit as location
            #       directory in ~/.config/mserve will have to be renamed.
            self.state = 'normal'  # Allow data entry

        # The button text for the submit button
        if self.loc_mode is 'Edit':
            sub_text = 'Save'
        elif self.loc_mode is 'Show':
            sub_text = 'Done'
        else:
            sub_text = self.loc_mode  # 'Add', 'Forget' or 'Compare'

        self.name_fld['state'] = self.state
        self.topdir_fld['state'] = self.state
        self.host_fld['state'] = self.state
        self.wakecmd_fld['state'] = self.state
        self.testcmd_fld['state'] = self.state
        self.testrep_fld['state'] = self.state
        self.mountcmd_fld['state'] = self.state
        self.activecmd_fld['state'] = self.state
        self.activemin_fld['state'] = self.state
        self.sub_btn['text'] = sub_text
        self.loc_top.update_idletasks()

    def loc_abandon(self):
        """ Abandoned changes to location, or simply close view
        """
        #        self.loc_F4.grid_remove()      # Dec. 12 2020
        self.loc_hide_fields()
        self.loc_top.update_idletasks()

    def loc_submit(self):
        """ Add, Update or Forget location on disk
            self.loc_mode is set to 'Add', 'Edit', 'Show' or 'Forget'
            self.loc_iid is set to string index within location LIST[]
        """
        if self.loc_mode is 'Show':
            # Submit button text is "Done".
            #            self.loc_F4.grid_remove()       # Make entry grid invisible
            self.loc_hide_fields()
            return

        name = self.name_var.get()
        topdir = self.topdir_var.get()
        host = self.host_var.get()
        wakecmd = self.wakecmd_var.get()
        testcmd = self.testcmd_var.get()
        testrep = self.testrep_var.get()
        mountcmd = self.mountcmd_var.get()
        activecmd = self.activecmd_var.get()
        activemin = self.activemin_var.get()

        # if name == "" or name.isspace():
        # More efficient way: if not name.strip()
        if not name.strip():  # If .strip() returns None it's blank
            # Empty or all blank names not allowed
            messagebox.showinfo(title="Location Error",
                                message="Name cannot be blank.",
                                parent=self.loc_top)
            self.name_fld.focus_force()
            return False

        if topdir == "" or topdir.isspace():
            # Empty or all blank top directory not allowed
            messagebox.showinfo(title="Location Error",
                                message="Top Directory for Music cannot be blank.",
                                parent=self.loc_top)
            self.topdir_fld.focus_force()
            return False

        if not testrep.isdigit():
            # Empty or all blank top directory not allowed
            messagebox.showinfo(title="Location Error",
                                message="Number of times to repeat test command must be an integer.",
                                parent=self.loc_top)
            self.testrep_fld.focus_force()
            return False
        else:
            testrep = int(self.testrep_var.get())

        if not activemin.isdigit():
            # Empty or all blank top directory not allowed
            messagebox.showinfo(title="Location Error",
                                message="Minutes between keeping host awake must be an integer.",
                                parent=self.loc_top)
            self.activemin_fld.focus_force()
            return False
        else:
            activemin = int(self.activemin_var.get())

        iid = self.loc_iid  # Abbreviate for shorter code lines
        #        self.loc_F4.grid_remove()          # Dec. 12 2020
        self.loc_hide_fields()
        self.loc_top.update_idletasks()  # Sept 23 2020
        if self.loc_mode is 'Add':
            # Dec 5 2020 iid was "New".  Causing base10 errors for integers.
            lc.insert(iid="", name=name, topdir=topdir, host=host,
                      wakecmd=wakecmd, testcmd=testcmd, testrep=int(testrep),
                      mountcmd=mountcmd, activecmd=activecmd, activemin=int(activemin))
        elif self.loc_mode is 'Edit':
            lc.item(iid=iid, name=name, topdir=topdir, host=host,
                    wakecmd=wakecmd, testcmd=testcmd, testrep=int(testrep),
                    mountcmd=mountcmd, activecmd=activecmd, activemin=int(activemin))
        elif self.loc_mode is 'Forget':
            self.confirm_forget(iid)
        elif self.loc_mode is 'Compare':
            self.cmp_build_treeview(iid)
        else:
            print('submit() Bad self.loc_mode:', self.loc_mode)
            return

        ''' Close loc_tree when cmp_add_items() running gets error: 
             File "./mserve", line 1031, in loc_submit
                self.loc_tree.delete(*self.loc_tree.get_children()) '''
        if self.loc_top_is_active is False:
            return  # We are closing down

        # Update treeview with new entry / revised / forgotten entry
        self.loc_tree.delete(*self.loc_tree.get_children())
        for iid in lc.get_children():
            loc_item = lc.item(iid)
            self.loc_tree.insert('', "end", iid=iid, text=loc_item["name"],
                                 values=(loc_item["iid"], loc_item["topdir"]))

        lc.write()  # Save location changes to disk
        # Blank out entry fields, but not necessary here
        self.name_var.set("")
        self.topdir_var.set("")
        self.host_var.set("")
        self.wakecmd_var.set("")
        self.testcmd_var.set("")
        self.testrep_var.set("0")
        self.mountcmd_var.set("")
        self.activecmd_var.set("")
        self.activemin_var.set("0")
        self.loc_top.update_idletasks()

    def loc_compare(self, caller="", mode=""):
        """ Compare songs to other location
            Called from File menu and from within self.loc_create_tree()
            Caller:
                'Drop' called from top bar dropdown menu
                    We create treeview and return
                'Tree' called from treeview button
                    We do the pre-processing for Submit button to take over
        """

        if mode != "":
            pass    # Pycharm error, should probably get rid of parameter...

        if self.cmp_top_is_active:
            self.cmp_top.focus_force()  # Get focus
            self.cmp_top.lift()  # Raise in stacking order
            root.update_idletasks()  # Sept 20 2020
            return  # We are closing down

        if caller == 'Drop':  # Called from dropdown Edit menu?
            # TODO: Redesign as we can call New Location from dropdown when
            #       Compare location is already active in cmp_tree
            self.loc_create_tree(caller='Tree', mode='Compare')
            # Make location input fields invisible until appropriate time
            #            self.loc_F4.grid_remove()      # Dec. 12 2020
            self.loc_hide_fields()
            root.update()
            return

        elif not caller == 'Tree':
            print("ERROR: 'caller' is neither 'Drop' nor 'Tree'.")
            return

        # If we are here caller is 'Tree'
        if len(self.loc_tree.selection()) == 0:
            messagebox.showinfo(title="Location Error",
                                message="You must select a location to compare.",
                                parent=self.loc_top)
            return False

        iid = self.loc_tree.selection()[0]  # iid of selected item
        #loc_dict = lc.item(iid)  # get dictionary for iid

        # Test target location to make sure it's online
        if not lc.test(iid, self.loc_top):
            # Location doesn't exist or is off-line
            messagebox.showinfo(title="Location Error",
                                message="Top directory doesn't exist or is off-line.",
                                parent=self.loc_top)
            return False

        self.loc_entry_state('Compare', iid)  # Show target entry
        #        self.loc_F4.grid()                     # Make entry grid visible
        self.loc_show_fields()
        self.loc_top.update_idletasks()

        # TODO: Test what happens if user changes selection and picks 'Show'
        self.loc_populate_screen(iid)  # Paint screen with lc.DICT{}
        return True

    # ==============================================================================
    #
    #       MusicTree Processing - Compare locations and update file differences
    #
    # ==============================================================================

    def cmp_build_treeview(self, trg_dict_iid, sbar_width=12):
        """ Compare target location songs to build treeview of differences.

            Source is current LODICT, Target it selected by user here

            After comparison, we can:
                - Set modification time (mtime) of target to match source
                - Set modification time (mtime) of source to match target
                - Copy files from source to target maintaining mtime
                - Copy files from target to source maintaining mtime

            NOTE: We don't export or import songs
                  Android doesn't allow setting mod time so track in mserve

            TODO:



            Compare locations can be setup like RipCD () class where generating
            list is done in background, and it generates a pickle while ps_active
            is polled. Button to cancel is active with status message in
            ScrolledText stating work in progress.

            When ps_active is done, text updated with filenames and actions.
            Button appears to update.


        """

        # print('cmp_build_treeview() get trg_dict',t(time.time()))
        trg_dict = lc.item(trg_dict_iid)  # get dictionary for iid
        self.cmp_target_dir = trg_dict['topdir']

        # If no optional `/` at end, add it for equal comparisons
        if not self.cmp_target_dir.endswith(os.sep):
            self.cmp_target_dir = self.cmp_target_dir + os.sep
        self.cmp_top_is_active = True

        ''' Set program icon in taskbar '''
        img.taskbar_icon(self.cmp_top, 64, 'white', 'lightskyblue', 'black')

        xy = (self.loc_top.winfo_x() + PANEL_HGT,
              self.loc_top.winfo_y() + PANEL_HGT)
        self.cmp_top.minsize(width=BTN_WID * 10, height=PANEL_HGT * 4)
        self.cmp_top.geometry('%dx%d+%d+%d' % (1800, 500, xy[0], xy[1]))  # 500 pix high
        title = "Compare Locations - SOURCE: " + START_DIR + \
                " - TARGET: " + self.cmp_target_dir
        self.cmp_top.title(title)
        self.cmp_top.columnconfigure(0, weight=1)
        self.cmp_top.rowconfigure(0, weight=1)

        ''' Set program icon in taskbar '''
        img.taskbar_icon(self.cmp_top, 64, 'white', 'lightskyblue', 'black')

        ''' Create frames '''
        master_frame = tk.Frame(self.cmp_top, bg="olive", relief=tk.RIDGE)
        master_frame.grid(sticky=tk.NSEW)
        master_frame.columnconfigure(0, weight=1)
        master_frame.rowconfigure(0, weight=1)

        ''' Create a frame for the treeview and scrollbar(s). '''
        frame2 = tk.Frame(master_frame)
        tk.Grid.rowconfigure(frame2, 0, weight=1)
        tk.Grid.columnconfigure(frame2, 0, weight=1)
        frame2.grid(row=0, column=0, sticky=tk.NSEW)

        ''' Treeview List Box, Columns and Headings '''
        self.cmp_tree = ttk.Treeview(frame2, show=('tree', 'headings'),
                                     columns=("SrcModified", "TrgModified", "SrcSize",
                                              "TrgSize", "Action", "src_mtime", "trg_mtime"),
                                     selectmode="none")
        self.cmp_tree.column("#0", width=630, stretch=tk.YES)
        # self.cmp_tree.heading("#0", text = "??? / ???   Artist/Album/Song")
        self.cmp_tree.heading(
            "#0", text="Click ??? (collapse) ??? (expand) an Artist or Album")
        self.cmp_tree.column("SrcModified", width=300, stretch=tk.YES)
        self.cmp_tree.heading("SrcModified", text="Source Modified")
        self.cmp_tree.column("TrgModified", width=300, stretch=tk.YES)
        self.cmp_tree.heading("TrgModified", text="Target Modified")
        self.cmp_tree.column("SrcSize", width=140, anchor=tk.E,
                             stretch=tk.YES)
        self.cmp_tree.heading("SrcSize", text="Source " + CFG_DIVISOR_UOM)
        self.cmp_tree.column("TrgSize", width=140, anchor=tk.E,
                             stretch=tk.YES)
        self.cmp_tree.heading("TrgSize", text="Target " + CFG_DIVISOR_UOM)
        self.cmp_tree.column("Action", width=280, stretch=tk.YES)
        self.cmp_tree.heading("Action", text="Action")
        self.cmp_tree.column("src_mtime")  # Hidden modification time
        self.cmp_tree.column("trg_mtime")  # Hidden modification time
        self.cmp_tree.grid(row=0, column=0, sticky=tk.NSEW)
        self.cmp_tree["displaycolumns"] = ("SrcModified", "TrgModified",
                                           "SrcSize", "TrgSize", "Action")
        ''' Treeview Scrollbars '''
        # Create a vertical scrollbar linked to the frame.
        v_scroll = tk.Scrollbar(frame2, orient=tk.VERTICAL, width=sbar_width,
                                command=self.cmp_tree.yview)
        v_scroll.grid(row=0, column=1, sticky=tk.NS)
        self.cmp_tree.configure(yscrollcommand=v_scroll.set)

        # Create a horizontal scrollbar linked to the frame.
        h_scroll = tk.Scrollbar(frame2, orient=tk.HORIZONTAL, width=sbar_width,
                                command=self.cmp_tree.xview)
        h_scroll.grid(row=1, column=0, sticky=tk.EW)
        self.cmp_tree.configure(xscrollcommand=h_scroll.set)

        ''' Treeview Buttons '''
        frame3 = tk.Frame(master_frame, bg="Blue", bd=2, relief=tk.GROOVE,
                          borderwidth=BTN_BRD_WID)
        frame3.grid_rowconfigure(0, weight=1)
        frame3.grid_columnconfigure(0, weight=0)
        frame3.grid(row=1, column=0, sticky=tk.NW)

        ''' ??? Close Button '''
        # TODO: we aren't keeping remote location awake only home location!
        self.cmp_top.bind("<Escape>", self.cmp_close)
        self.cmp_top.protocol("WM_DELETE_WINDOW", self.cmp_close)
        self.cmp_close_btn = tk.Button(frame3, text="??? Close",
                                       width=BTN_WID - 4, command=self.cmp_close)
        self.cmp_close_btn.grid(row=0, column=0, padx=2)

        ''' Create Treeview using source (START_DIR) as driver '''
        if not self.cmp_add_items(trg_dict_iid):
            self.cmp_close()  # Files are identical
            return

        ''' ????  Update differences Button u1f5d8 ????'''
        self.update_differences_btn = tk.Button(frame3, width=BTN_WID + 4,
                                                text="????  Update differences",
                                                command=self.cmp_update_files)
        self.update_differences_btn.grid(row=0, column=1, padx=2)

        if self.cmp_top_is_active is False:
            return  # We are already closed
        self.cmp_tree.update_idletasks()

    # noinspection PyUnusedLocal
    def cmp_close(self, *args):
        """ Close Compare location treeview """
        if self.cmp_top_is_active is False:
            return  # We are already closed
        self.cmp_top_is_active = False
        root.update()
        root.after(50)  # Give time for treeview to close
        self.cmp_top.destroy()  # Close the treeview window

        return True

    def cmp_add_items(self, trg_dict_iid):

        """ Add Artist, Album and Song to treeview self.cmp_tree.
            Similar to add_items() in MusicTree

            TODO: Rest of mserve is unresponsive while this is running.
                  Take all compare location code and make new python module
                  called compare.py imported as cmp

            It takes 1.5 hour to stat 4,000 songs on phone mounted on sshfs
            over Wi-Fi. Speed up with: https://superuser.com/questions/344255/
            faster-way-to-mount-a-remote-file-system-than-sshfs

            -o auto_cache,reconnect,defer_permissions
            -o Ciphers=aes128-ctr -o Compression=no


        """
        # How many path separators '/' are there in source and target?
        start_dir_sep = START_DIR.count(os.sep) - 1
        #target_dir_sep = self.cmp_target_dir.count(os.sep) - 1
        self.src_mt = lc.ModTime(LODICT['iid'])
        self.trg_mt = lc.ModTime(trg_dict_iid)

        #first_artist = True
        LastArtist = ""
        LastAlbum = ""
        #first_album = True
        CurrAlbumId = ""  # When there are no albums?
        CurrArtistId = ""
        # do_debug_steps = 0 # DEBUGGING
        last_i = 0

        for i, os_name in enumerate(self.song_list):
            self.cmp_top.update()  # Allow close button to abort right away

            # Experimental doesn't work! Solution is to make this function
            # a new python module launched in background. Or use new
            # tool.thread called every 1000 reads for SSD, less for phone.
            if self.play_top_is_active:  # Play window open?
                root.update_idletasks()
                self.play_top.update()  # Update spinner & text

            # split song /mnt/music/Artist/Album/Song.m4a into variable names
            groups = os_name.split(os.sep)
            Artist = str(groups[start_dir_sep + 1])
            Album = str(groups[start_dir_sep + 2])
            Song = str(groups[start_dir_sep + 3])

            if Artist != LastArtist:
                CurrArtistId = self.cmp_tree.insert("", "end", text=Artist,
                                                    tags=("Artist",), open=True)
                LastArtist = Artist
                LastAlbum = ""  # Force subtotal break for Album

            if Album != LastAlbum:
                CurrAlbumId = self.cmp_tree.insert(CurrArtistId, "end",
                                                   text=Album, tags=("Album",))
                LastAlbum = Album

            if self.cmp_top_is_active is False:
                return  # We are closing down

            ''' Build full song path from song_list[] '''
            src_path = os_name
            src_path = src_path.replace(os.sep + NO_ARTIST_STR, '')
            src_path = src_path.replace(os.sep + NO_ALBUM_STR, '')

            # os.stat gives us all of file's attributes
            src_stat = os.stat(src_path)
            src_size = src_stat.st_size
            src_mtime = float(src_stat.st_mtime)

            # Get target list's size and mtime
            trg_path = src_path.replace(START_DIR, self.cmp_target_dir)
            if not os.path.isfile(trg_path):
                self.cmp_tree.see(CurrAlbumId)
                continue  # Source song doesn't exist on target

            trg_stat = os.stat(trg_path)
            trg_size = trg_stat.st_size
            trg_mtime = float(trg_stat.st_mtime)
            # Android not updating modification time, keep track ourselves
            # print('mserve before src:',t(src_mtime),' trg:',t(trg_mtime))
            src_mtime = self.src_mt.get(src_path, src_mtime)
            trg_mtime = self.trg_mt.get(trg_path, trg_mtime)
            # print('mserve AFTER  src:',t(src_mtime),' trg:',t(trg_mtime))

            # FUDGE because cp --preserve=timestamps doesn't do nanoseconds
            src_mtime = int(src_mtime)
            trg_mtime = int(trg_mtime)
            # FUDGE if time difference is 1 second. Caused by copy to SD Card
            if src_mtime > trg_mtime:
                diff = src_mtime - trg_mtime
            else:
                diff = trg_mtime - src_mtime
            if diff == 1:
                src_mtime = trg_mtime  # override 1-second difference
            # End of patch FUDGE

            if src_size == trg_size and src_mtime == trg_mtime:
                self.cmp_tree.see(CurrAlbumId)
                continue

            if not src_size == trg_size:
                # Copy newer file to older
                if src_mtime < trg_mtime:
                    action = "Copy Trg -> Src (Size)"
                elif src_mtime > trg_mtime:
                    action = "Copy Src -> Trg (Size)"
                else:
                    action = "Size diff but same time!"

            elif os.system('diff ' + '"' + src_path + '"' + ' ' +
                           '"' + trg_path + '" 1>/dev/null'):

                if self.cmp_top_is_active is False:
                    return  # We are closing down
                # Files have different contents even though size the same
                # Copy newer file to older
                if src_mtime < trg_mtime:
                    action = "Copy Trg -> Src (Diff)"
                else:
                    action = "Copy Src -> Trg (Diff)"

            else:
                # File contents same so modification times must be synced
                if src_mtime > trg_mtime:
                    action = "Timestamp Trg -> Src"
                elif src_mtime < trg_mtime:
                    action = "Timestamp Src -> Trg"
                else:
                    # Impossible situation
                    action = "OOPS same time?"

            # fsize = '{:n}'.format(size)     # Format size with locale separators
            converted = float(src_size) / float(CFG_DIVISOR_AMT)
            src_fsize = str(round(converted, CFG_DECIMAL_PLACES + 2))
            converted = float(trg_size) / float(CFG_DIVISOR_AMT)
            trg_fsize = str(round(converted, CFG_DECIMAL_PLACES + 2))
            #                 '{:n}'.format(Size))) # 9,999,999 format
            # Format date as "Abbreviation - 99 Xxx Ago"
            src_ftime = tmf.ago(float(src_stat.st_mtime))
            trg_ftime = tmf.ago(float(trg_stat.st_mtime))

            # Catch programmer's bug
            if i == last_i:
                print('same song ID twice in a row:', i)
                continue
            last_i = i

            ''' Add the song '''
            # NOTE: Numeric 0 allowed for index except for 0 which is converted
            #       to a parent ID, EG I003. Convert to string to fix bug.
            self.cmp_tree.insert(CurrAlbumId, "end", iid=str(i), text=Song,
                                 values=(src_ftime, trg_ftime, src_fsize, trg_fsize, action,
                                         float(src_stat.st_mtime), float(trg_stat.st_mtime)),
                                 tags=("Song",))
            self.cmp_tree.see(str(i))

            # Sept 23 2020 - Treeview doesn't scroll after update button added?
            # After clicking update differences can you click it again?
            if self.cmp_top_is_active is False:
                return  # We are already closed
            self.cmp_tree.update_idletasks()

            # do_debug_steps += 1
            # if do_debug_steps == 10000: break     # Set to short for testing

        ''' Prune tree - Albums with no songs, then artists with no albums '''
        for artist in self.cmp_tree.get_children():
            album_count = 0
            for album in self.cmp_tree.get_children(artist):
                if self.cmp_top_is_active is False:
                    return  # We are closing down
                #song_count = 0
                #for song in self.cmp_tree.get_children(album):
                #    song_count += 1  # Signal not to delete album
                #    break
                song_count = len(self.cmp_tree.get_children(album))
                if song_count == 0:
                    self.cmp_tree.delete(album)
                else:
                    album_count += 1  # Signal not to delete artist
            if album_count == 0:
                self.cmp_tree.delete(artist)

        ''' Message if files are same (no treeview children) '''
        if self.cmp_tree.get_children():
            return True
        else:
            messagebox.showinfo(title="Files identical",
                                message="Files common to both locations are identical.",
                                parent=self.cmp_top)
            return False

    def cmp_update_files(self):
        """ Build list of commands to run with subprocess
            Called via "Update" button on cmp_top treeview
        """
        return_code = 0
        title = "Updating files"
        self.update_differences_btn.grid_forget()  # Can't click again
        # Display status messages in window 800 wide x 260 high
        self.cmp_msg_box = message.Open(title, self.cmp_top, 800, 260)
        for artist in self.cmp_tree.get_children():
            for album in self.cmp_tree.get_children(artist):
                for song in self.cmp_tree.get_children(album):
                    # Update file and display in message box.
                    return_code = self.cmp_run_command(song)
                    root.update_idletasks()
                    if self.cmp_top_is_active is False:
                        # TODO: Move duplicated code into common ...close()
                        self.src_mt.close()  # Save modification_time to disk
                        self.trg_mt.close()  # If no changes then simply exit
                        self.cmp_msg_box.close()
                        return  # Closing down
                    if not return_code == 0:
                        break
                if not return_code == 0:
                    break
            if not return_code == 0:
                break

        self.src_mt.close()  # Save modification_time to disk
        self.trg_mt.close()  # If no changes then simply exit
        self.cmp_msg_box.close()

        if not return_code == 0:
            print('cmp_update_files() received non-zero return_code:', return_code)
        # All done, close treeview as it's no longer relevant
        self.cmp_close()

    def cmp_run_command(self, iid):
        """ Build single commands to run with subprocess
                cp -p source_path target_path
                touch -m -r source_path target_path

            NOTE: START_DIR may become target_path and target_dir may become
                  source_path after deciphering arrow
        """

        # action = 'Copy Trg -> Src (Size)', 'Timestamp Src -> Trg', etc.
        action = self.cmp_tree.item(iid)['values'][4]  # 6th treeview column
        src_mtime = self.cmp_tree.item(iid)['values'][5]
        trg_mtime = self.cmp_tree.item(iid)['values'][6]
        # Extract real source path from treeview display e.g. strip (No Album)
        src_path = self.real_path(int(iid))
        # replace source topdir with target topdir for target full path
        trg_path = src_path.replace(START_DIR, self.cmp_target_dir)

        # Build command line list for subprocess
        command_line_list = []
        src, trg = self.cmp_decipher_arrow(action, src_path, trg_path)
        if src is None:
            return False  # Programmer made error

        if action.startswith("Copy "):  # Is it a copy?
            command_line_list.append("cp")
            command_line_list.append("--preserve=timestamps")

        elif action.startswith("Timestamp "):  # Is it a timestamp?
            command_line_list.append("touch")
            command_line_list.append("-m")
            command_line_list.append("-r")

        else:  # None of above? - ERROR!
            print("cmp_run_command(): action is not 'Copy ' or 'Timestamp '")
            return False

        # Add common arguments for source and target to end
        command_line_list.append(src)
        command_line_list.append(trg)

        command_str = " ".join(command_line_list)  # list to printable string
        self.cmp_msg_box.update(command_str)  # Display status line
        pipe = sp.Popen(command_line_list, stdout=sp.PIPE, stderr=sp.PIPE)
        text, err = pipe.communicate()  # This performs .wait() too

        # print('subprocess:', command_line_list)
        # print("return_code of subprocess:",pipe.return_code)
        if text:
            print("standard output of subprocess:")
            print(text)
            self.cmp_msg_box.update(text)
        if err:
            print("standard error of subprocess:")
            print(err)
            self.cmp_msg_box.update(err)

        if pipe.return_code == 0:
            if src == src_path:  # Action is from Src -> Trg
                self.src_mt.update(src_path, trg_mtime, src_mtime)
                self.trg_mt.update(trg_path, trg_mtime, src_mtime)
            elif src == trg_path:  # Action is from Trg -> Src
                self.src_mt.update(src_path, src_mtime, trg_mtime)
                self.trg_mt.update(trg_path, src_mtime, trg_mtime)
            else:
                print('ERROR: paths do not work')

        return pipe.return_code

    @staticmethod
    def cmp_decipher_arrow(action, src_path, trg_path):
        """ Flip src_path (full_path) and trg_path (full_path2) around """
        if "Trg -> Src" in action:
            return trg_path, src_path
        elif "Src -> Trg" in action:
            return src_path, trg_path
        else:
            print('cmp_decipher_arrow(): was passed invalid arrow')
            return None, None

    # ==============================================================================
    #
    #       MusicTree Processing - Select items, Popup Menus
    #
    # ==============================================================================

    """
        Single button 1 click is processed by CheckboxTreeview().
    """

    def button_1_click(self, event):
        """ Call CheckboxTreeview to manage "checked" and "unchecked" tags.
            Before calling issue warning if it will change tri-state.
            When it finishes call set_all_parents() to update selection column
            for Artist or Album. Call reverse() to update just one song.
            Both will roll up the totals into parents.
        """

        # Mimic CheckboxTreeview self._box_click() code
        x, y, widget = event.x, event.y, event.widget
        elem = widget.identify("element", x, y)
        if "image" not in elem:
            return  # Image was not clicked

        # get item id (iid) matching checkbox that was just clicked
        item = self.lib_tree.identify_row(y)

        """ Warning if status is tri-state, all will be selected. """
        # Call CheckboxTreeview function first to let it flag item(s).
        if self.lib_tree.tag_has("tristate", item):
            dialog = message.AskQuestion(
                self.lib_top, thread=self.refresh_play_top,
                title="Discard unique selections.",
                text="All items will be selected and unique selections lost.")
            if dialog.result != 'yes':
                return

        """ Warning if unchecking parent all children will be unchecked. """
        # Call CheckboxTreeview function first to let it flag item(s).
        if self.lib_tree.tag_has("checked", item):
            if self.lib_tree.tag_has("Artist", item) or \
                    self.lib_tree.tag_has("Album", item):
                dialog = message.AskQuestion(
                    parent=self.lib_top, thread=self.refresh_play_top,
                    title="Discard child selections.",
                    text="All child items will be unchecked.")
                if dialog.result != 'yes':
                    return

        # Call CheckboxTreeview function check (select/unselect) item.
        # noinspection PyProtectedMember
        self.lib_tree._box_click(event)

        if self.lib_tree.tag_has("unchecked", item):
            self.process_unchecked(item)

        elif self.lib_tree.tag_has("checked", item):
            self.process_checked(item)

        else:
            # No need to test tristate, item must be checked or unchecked.
            print("button_1_click() ERROR: No 'checked' or 'unchecked' tag.",
                  self.lib_tree.item(item, 'tags'))
            return

    def process_unchecked(self, item):
        """ We just unchecked the item, update totals

            TODO: Removing from playlist artwork keeps spinning but playing
                  stops. Instead, next song should start playing.
        """
        tags = self.lib_tree.item(item)['tags']
        if 'Artist' in tags or 'Album' in tags:
            self.set_all_parent(item, 'Del')
        elif 'Song' in tags:
            self.reverse(item)
        else:
            print('process_unchecked() bad tag:', tags)

    def process_checked(self, item):
        """ We just checked the item, update totals

            TODO: Adding to playlist an album or artist then all get same
                  song number in chron tree until restart.
        """

        self.manually_checked = True  # Used for self.reverse/self.toggle
        tags = self.lib_tree.item(item)['tags']
        if 'Artist' in tags or 'Album' in tags:
            self.set_all_parent(item, 'Add')
        elif 'Song' in tags:
            self.reverse(item)
        else:
            print('process_checked() bad tag:', tags)
        self.manually_checked = False

    def set_all_parent(self, Id, action):
        """ ID can be an Artist or Album. action can be "Add" or "Del"
                Are we processing an albums for artist or single album?
                Are we turning selection on or off? (action passed)
        """
        tags = self.lib_tree.item(Id)['tags']
        if "Artist" in tags:
            for album in self.lib_tree.get_children(Id):
                self.set_all_songs(album, action)

        elif "Album" in tags:
            self.set_all_songs(Id, action)

        else:
            print("set_all_parent() error: 'Id' is neither 'Album' nor 'Artist'")

    def set_all_songs(self, Id, action):
        """ set single song selected or unselected """
        # count = 0
        for child in self.lib_tree.get_children(Id):
            # Check selected column being non-blank
            selected = self.lib_tree.item(child)['values'][2]
            if (selected == "" and action == "Add") \
                    or (not selected == "" in tags and action == "Del"):
                self.reverse(child)
                # count += 1
        # print(self.lib_tree.item(Id,'text'),'action:',action,'count:',count)

    def ensure_visible(self, Id):
        """ WARNING: Called from multiple places """
        opened = self.lib_tree.item(Id, 'open')
        if opened is not True:
            self.lib_tree.item(Id, open=True)
        # Get children and ensure last child is visible
        last_child = Id  # Should always have children but got error
        for child in self.lib_tree.get_children(Id):
            last_child = child
        self.lib_tree.see(last_child)

    def popup(self, event):
        """ Action in event of button 3 on treeview
        """
        # select row under mouse
        Id = self.lib_tree.identify_row(event.y)
        if Id is None or Id is "":
            return  # clicked on whitespace (no row)

        # print ('popup Id:', Id)
        self.mouse_x, self.mouse_y = event.x_root, event.y_root
        self.kid3_window = ""
        # print ('self.mouse; x, y:', self.mouse_x, self.mouse_y)
        ''' Apply 'popup_sel' tag for visual feedback '''
        tags = self.lib_tree.item(Id)['tags']
        tags.append("popup_sel")
        #self.lib_tree.item(Id, tags=tags)
        self.lib_tree.item(Id, tags=tags)   # PyCharm redundant paren warning

        ''' If Parent collapsed, expand it. '''
        if Id.startswith("I"):
            # If it is collapsed then expand it for viewing
            self.ensure_visible(Id)
            # Make it more obvious which parent is being processed with popup
            self.parent_popup(event, Id)
        else:
            # We are a song, different menu options:
            self.song_popup(event, Id)

    def parent_popup(self, event, Id):
        """ Popup parent menu
            Need to filter out Artist
            Need to apply 'popup_sel' tag to get visual feedback
        """

        ''' Parent already done now apply 'popup_sel' tag to children '''
        for child in self.lib_tree.get_children(Id):
            tags = self.lib_tree.item(child)['tags']
            tags.append("popup_sel")
            self.lib_tree.item(child, tags=tags)

        menu = tk.Menu(root, tearoff=0)
        menu.post(event.x_root, event.y_root)

        # If lambda isn't used the command is executed as soon as popup
        # menu is displayed, not when option is chosen.
        menu.add_command(label="Collapse list", font=(None, MED_FONT),
                         command=lambda: self.collapse_all(Id))
        ''' TODO: Call Nautilus with directory name '''
        if FM_INSTALLED:
            menu.add_command(label=FM_PROGRAM, font=(None, MED_FONT),
                             command=lambda: self.file_manager_parent(Id))
        menu.add_command(label="Ignore click", font=(None, MED_FONT),
                         command=lambda: self.remove_popup_sel())

        menu.tk_popup(event.x_root, event.y_root)
        # Without lambda executes immediately, without _: invalid # parameters
        menu.bind("<FocusOut>", lambda _: self.close_popup(menu))

    def song_popup(self, event, Id):
        """ Popup menu for a song
            LONG TERM TODO: Display large 500x500 image and all metadata
        """

        menu = tk.Menu(root, tearoff=0)
        menu.post(event.x_root, event.y_root)

        # If lambda isn't used the command is executed as soon as popup
        # menu is displayed, not when option is chosen.
        menu.add_command(label="Sample middle 10 seconds", font=(None, MED_FONT),
                         command=lambda: self.sample_middle(Id))
        if KID3_INSTALLED:
            menu.add_command(label="kid3", font=(None, MED_FONT),
                             command=lambda: self.kid3_song(Id))
        menu.add_command(label="Ignore click", font=(None, MED_FONT),
                         command=lambda: self.remove_popup_sel())

        menu.tk_popup(event.x_root, event.y_root)
        # Without lambda executes immediately, without _: invalid # parameters
        menu.bind("<FocusOut>", lambda _: self.close_popup(menu))

    def close_popup(self, menu):
        self.remove_popup_sel()  # Remove 'popup_sel' tags
        menu.unpost()  # Remove popup menu

    def wrap_up_popup(self):
        self.remove_popup_sel()  # Remove 'popup_sel' tags

    def remove_popup_sel(self):
        # Remove special view popup selection tags to restore normal view
        tags_selections = self.lib_tree.tag_has("popup_sel")
        for child in tags_selections:
            tags = self.lib_tree.item(child)['tags']
            tags.remove("popup_sel")
            self.lib_tree.item(child, tags=tags)

    def collapse_all(self, Id):
        opened = self.lib_tree.item(Id, 'open')
        if opened is True or opened == 1:
            self.lib_tree.item(Id, open=False)
        self.wrap_up_popup()  # Set color tags and counts

    def reverse(self, Id):
        """ WARNING: Called from multiple places """
        # Toggle song tag on/off. Only used for song, not parent
        if Id.startswith("I"):
            return  # Parents are a no-go

        # New code October 1, 2020
        album = self.lib_tree.parent(Id)
        artist = self.lib_tree.parent(album)
        self.toggle_select(Id, album, artist)
        return

    def file_manager_parent(self, Id):
        """ Open path with file manager. FUTURE FUNCTION
        """
        #        self.remove_popup_sel()              # Return normal highlighting
        # TODO: Get first song to serve as Artist/Album subdirectory
        #       Append subdirectory to topdir
        if Id.startswith("I"):
            return  # Parents are a no-go
        full_path = self.real_path(int(Id))
        print("full_path:", full_path)
        os.popen(FM_PROGRAM + ' "' + full_path + '"')

    def kid3_song(self, Id):
        #        self.remove_popup_sel()              # Return normal highlighting
        full_path = self.real_path(int(Id))
        our_window = os.popen("xdotool getactivewindow").read().strip()
        # print('Our active window:',our_window)
        os.popen(KID3_PROGRAM + ' "' + full_path + '" 2>/dev/null &')
        self.kid3_window = os.popen("xdotool getactivewindow").read().strip()
        sleep_count = 0

        # Wait until Kid3 active then move it into popup menu mouse position
        while self.kid3_window == our_window:
            sleep_count += 1
            root.after(100)  # Fine tune for sleep count of 3
            self.kid3_window = os.popen("xdotool getactivewindow"). \
                read().strip()

        # print('Kid3 window:',self.kid3_window,'sleep_count:',sleep_count)

        # Move window to mouse position within popup menu event
        os.popen('xdotool windowmove ' + self.kid3_window + ' ' +
                 str(self.mouse_x) + ' ' + str(self.mouse_y))

        ''' Wait until Kid3 window is closed
            WHO CARES?!? So what if user keeps Kid3 open
            TODO: Force close (with dialog prompt!) if focus out of Kid3 '''
        if our_window != "impossible value":    # Dummy test always true
            return                              # Code below not finished

        # active_window = self.kid3_window  # Decimal Window ID
        # print('active_window:',active_window)
        warning_issued = False  # Warning dialog displayed?

        # Loop until Kid3 ends
        while self.kid3_window is not "":

            root.update()
            root.after(100)
            # Get list of all open X-Windows
            # TODO: Check if active window is a child of kid3
            all_windows = os.popen("wmctrl -l -p").read().strip().splitlines()
            if "Kid3" not in all_windows:
                self.kid3_window = ""
                break

            # noinspection SpellCheckingInspection
            '''

$ wmctrl -l -p
0x07800007  0 12234  alien Software Updater
0x0400000a  0 3128   alien Python 2
0x02c00002  0 2670   alien XdndCollectionWindowImp
0x02c00009  0 2670   alien unity-launcher
0x02c0001e  0 2670   alien unity-panel
0x02c00025  0 2670   alien unity-panel
0x02c0002c  0 2670   alien unity-panel
0x02c00033  0 2670   alien unity-dash
0x02c00034  0 2670   alien Hud
0x0340000a  0 2951   alien Desktop
0x040000f8  0 3128   alien rick@alien: ~
0x00a00010  0 7490   alien *mserve (~/python) - gedit
0x04600002  0 0      alien conky (alien)
0x04018cf0  0 3128   alien rick@alien: ~
0x01e00003  0 13008  alien wmctrl(1) - Linux man page - Mozilla Firefox
0x01e00038  0 13008  alien Watch Zombieland (2009) Full Movie - Putlocker - Mozilla Firefox
0x01e00020  0 13008  alien SSHelper - Mozilla Firefox
0x01e0002d  0 13008  alien Display Control Sample - Mozilla Firefox
0x08600036  0 0        N/A mmm - Multiple Monitors Manager
0x0480001d  0 0        N/A mserve - Music Server            729 songs total of:        6,326,239,452 bytes
0x0480043a  0 0        N/A Playing Selected Songs
0x05200004  0 6683     N/A A Momentary Lapse Of Reason [Remaster]  ??? Kid3
0x05200037  0 6683     N/A Add Frame ??? Kid3
0x04832219  0 0        N/A Kid3 is running
            
            '''
            # inspection SpellCheckingInspection

            active_window = os.popen("xdotool getactivewindow").read().strip()
            #if self.kid3_active(active_window, self.kid3_window, all_windows):
            # June 2, 2021 bug fix wrong parameter list
            if self.kid3_active(active_window, all_windows):
                warning_issued = False  # active window is kid3
                continue
            else:
                if warning_issued is False:
                    # print('active_window changed:',active_window)
                    # set_font_style()
                    messagebox.showinfo("Kid3 is running",
                                        "mserve won't respond until Kid3 is closed.",
                                        parent=self.lib_top)
                    root.update()
                    # noinspection SpellCheckingInspection
                    os.popen("xdotool windowactivate "
                             + self.kid3_window + " 2> /dev/null"). \
                        read().strip()
                    # inspection SpellCheckingInspection
                    # Make Kid3 active after OK pressed
                    warning_issued = True

        self.kid3_window = ""  # Let others know kid3 is closed
        root.update()

    @staticmethod
    def kid3_active(dec_window, all_windows):
        # Kid3 or one of his children must be active to return True

        # 0x0480043a  0 0        N/A Playing Selected Songs
        # 0x05200004  0 6683     N/A Momentary Lapse Of Reason ??? Kid3
        # 0x05200037  0 6683     N/A Add Frame ??? Kid3
        for line in all_windows:
            if "Kid3" in line:
                # MAJOR BUG May 30, 2021, hex_window defined below instead of
                # hex_windows. TODO: Bug fix not tested yet.
                #hex_window = line.split(" ")[0]
                hex_windows = line.split(" ")[0]
                decimal = int(hex_windows, 16)
                if decimal == dec_window:
                    return True

        return False

    # ==============================================================================
    #
    #       MusicTree Processing section - Top level functions
    #
    # ==============================================================================

    # noinspection PyUnusedLocal
    def close(self, *args):
        self.close_sleepers()  # Shut down running functions
        self.save_last_selections()  # Last selections for next open
        root.destroy()
        self.lib_top = None

    # noinspection PyUnusedLocal
    def restart(self, *args):
        self.close()
        os.execl(sys.executable, sys.executable, *sys.argv)

    # noinspection PyUnusedLocal
    def restart_new_parameters(self, *args):
        # NOTE: We've already saved selections and don't want to overwrite
        #       with new location iid
        self.close_sleepers()  # Shut down running functions
        root.destroy()

        print('Restarting with new music library:', self.parm)
        if len(sys.argv) > 1:
            sys.argv[1] = self.parm
        else:
            sys.argv.append(self.parm)
        os.execl(sys.executable, sys.executable, *sys.argv)

    def close_sleepers(self):
        # Close loc_keep_awake() first as it has .25-second sleep cycle
        # COMMON CODE for restart and quit
        self.loc_keep_awake_is_active = False
        self.lib_top_is_active = False      # Tell refresh_items() to bail out

        if self.gone_fishing is not None:
            self.gone_fishing.close()       # Shark eating man animation
            self.gone_fishing = None


        if self.cmp_top_is_active:          # Editing Locations?
            self.cmp_close()                # Extreme lags when running 'diff'
        if self.play_top_is_active:         # Is music playing?
            self.play_close()
        if self.syn_top_is_active:          # Synchronizing lyrics time indices
            self.sync_close()
        if self.sam_top_is_active:          # Sampling middle 10 seconds?
            self.sample_close()
        if self.loc_top_is_active:          # Editing Locations?
            self.loc_close()
        if encoding.RIP_CD_IS_ACTIVE:       # Ripping CD currently active?
            encoding.RIP_CD_IS_ACTIVE = False

        # Last known window position for music library, saved to SQL
        last_library_geom = monitor.get_window_geom_string(
            self.lib_top, leave_visible=False)
        monitor.save_window_geom('library', last_library_geom)

        time.sleep(RESTART_SLEEP)           # Extra insurance sleepers close

    def clear_buttons(self):
        """ When new windows open, disable TreeView buttons """
        # self.lib_tree_btn1 ["text"] = ""     # Close button
        # Unicode Character ?????????? (U+1F3B5)
        self.lib_tree_btn2["text"] = "????  Show library"  # Play button
        self.play_on_top = True
        # self.lib_tree_btn3 ["text"] = ""     # Save button
        # self.lib_tree_btn4 ["text"] = ""     # Load button
        # self.lib_tree_btn5 ["text"] = ""     # Export button
        # self.lib_tree_btn6 ["text"] = ""     # Import button

    def restore_buttons(self):
        """ When playing window closes, restore TreeView buttons """
        self.lib_tree_btn1["text"] = self.close_text
        self.lib_tree_btn2["text"] = self.play_text
        self.lib_tree_btn3["text"] = self.save_text
        self.lib_tree_btn4["text"] = self.load_text
        self.lib_tree_btn5["text"] = self.rebuild_text
        self.lib_tree_btn6["text"] = self.import_text

    def refresh_items(self):
        """ Refresh items in treeview listbox.
            Updates last play time
            TODO: Don't run unless loc_keep_awake() is run first otherwise we
                  go into 'Disk Wait+' status in 'ps aux'
        """
        # ext.t_init('refresh_items()')

        for artist in self.lib_tree.get_children():
            for album in self.lib_tree.get_children(artist):
                for song in self.lib_tree.get_children(album):
                    # Are we closing down?
                    if self.lib_top_is_active is False:
                        return
                    # Update last played time "xxx ago" in column #1
                    self.update_song_last_play_time(song)

        # job_time = ext.t_end('print')
        ''' NOTE: DO NOT CALL if make_sorted_list takes longer than 0.1 second.
                  This could happen on some Wifi connections using SSHFS.

                  On file server it is taking 1.67 second causing lag...
        #ext.t_init('refresh_items(): Compare SORTED_LIST')
        if self.loc_keep_awake_is_active:
            # loc_keep_awake() is processing FileServer over ethernet
            # TODO: A special test for phone SSHFS over WiFi
            last_time_check = self.awake_last_time_check
            while last_time_check == self.awake_last_time_check:
                # update idletasks if resuming from sleep until connection
                # drops and program quits.
                #print('refresh_items() idling milliseconds:',KEEP_AWAKE_MS)
                #print('curr time:',time.time(),self.awake_last_time_check)
                #self.lib_top.after(KEEP_AWAKE_MS, self.refresh_items)
                #self.lib_top.after(KEEP_AWAKE_MS)
                #self.lib_top.update_idletasks()
                #self.lib_top.after(10000)
                #root.after(10000)
                break               # self.awake_last_time_check not updating?
            # If we get here self.loc_keep_awake() is running normally

        # Build list of songs, pausing 100 ms to update idletasks
        SortedList2 = make_sorted_list(START_DIR, self.lib_top, 100)
        #SortedList2 = make_sorted_list(START_DIR, self.lib_top, None)
        if not SORTED_LIST == SortedList2:
            # NOTE: SORTED_LIST is inherited globally from __main___
            self.inotify()
        else:
            # disk image hasn't changed, reset time last message sent
            self.last_inotify_time = None
        #job_time = ext.t_end('print')
        '''
        self.lib_top.after(60000, self.refresh_items)  # Update every minute

    def inotify(self):

        # Send bubble message when first encountered, then wait 20 minutes
        # before sending again which allows time to rip CD.
        now = time.time()
        if self.last_inotify_time:
            # Has enough time passed to send another inotify message?
            if now < self.next_message_time:
                return

        notify2.init("SortedList")
        title = "Songs in Music Directory changed"
        notice = notify2.Notification(
            title, 'Click "Refresh library" button to update songs')
        notice.show()
        self.last_inotify_time = now
        self.next_message_time = now + (60 * 20)
        print('last message time:', self.last_inotify_time,
              'next message time:', self.next_message_time)

    # ==============================================================================
    #
    #       MusicTree Processing - Buttons: Save, Load, Refresh, Rip
    #
    # ==============================================================================

    def rebuild_lib_tree(self):
        """ If directories/songs have changed rebuild cd tree and position
            cursor (so to speak) to first changed song (open parents).
            Called from lib_tree button.
        """

        global SORTED_LIST
        # Build list of songs
        SortedList2 = make_sorted_list(START_DIR, toplevel=self.lib_top)

        # Assign background animation thread for message boxes
        if self.play_top_is_active:
            thread = self.refresh_play_top
        else:
            thread = None

        if SORTED_LIST == SortedList2:
            # print('self.play_top_is_active:', self.play_top_is_active)
            message.ShowInfo(
                self.lib_top, thread=thread,
                title="Refresh music library",
                text="The same " + str(len(SORTED_LIST)) +
                     " songs are in the library.\n\n" +
                     "No updates have been made to the view.")
            return
        else:
            additions = list(set(SortedList2).difference(SORTED_LIST))
            deletions = list(set(SORTED_LIST).difference(SortedList2))
            answer = message.AskQuestion(
                self.lib_top, thread=thread, align='left', icon='warning',
                title="Refresh music library - EXPERIMENTAL !!!",
                text="Songs have changed in storage:\n" +
                     "\tAdditions:\t" + str(len(additions)) + "\n" +
                     "\tDeletions:\t" + str(len(deletions)) + "\n\n" +
                     "This experimental feature will backup these files:\n" +
                     "\t " + lc.FNAME_LAST_OPN_STATES + "\n" +
                     "\t " + lc.FNAME_LAST_SONG_NDX + "\n" +
                     "\t " + lc.FNAME_LAST_SELECTIONS + "\n" +
                     "\t " + lc.FNAME_LAST_PLAYLIST + "\n\n" +
                     "...to the same location with the extension '.bak'\n\n"
                     "TIP:\tHighlight this text and use Control+C to copy\n"
                     "\tto clipboard. You may need to manually restore files.\n")

            if answer.result != "yes":
                return

        ''' Debug information
            TODO: put this into logging and/or SQL history
        for added in additions:
            print('added song:', added)
        for deleted in deletions:
            print('deleted song:', deleted)
        '''
        # Backup files
        shutil.copy(lc.FNAME_LAST_OPN_STATES, lc.FNAME_LAST_OPN_STATES + ".bak")
        shutil.copy(lc.FNAME_LAST_SONG_NDX, lc.FNAME_LAST_SONG_NDX + ".bak")
        shutil.copy(lc.FNAME_LAST_SELECTIONS, lc.FNAME_LAST_SELECTIONS + ".bak")
        shutil.copy(lc.FNAME_LAST_PLAYLIST, lc.FNAME_LAST_PLAYLIST + ".bak")

        SORTED_LIST = SortedList2
        self.song_list = SORTED_LIST
        self.lib_tree.delete(*self.lib_tree.get_children())
        # Copied from __init__
        dtb = message.DelayedTextBox(title="Building music view",
                                     toplevel=None, width=1000)

        '''
                    B I G   T I C K E T   E V E N T
         
        Create Treeview item list. '''
        self.populate_lib_tree(dtb)

        ''' Load last selections and begin playing with last song '''
        # If below is commented out all open states and checkboxes are lost
        self.saved_selections = []
        self.load_last_selections()

    @staticmethod
    def show_monitors():
        """ Debugging - show monitors
        """
        mon = monitor.Monitors()            # Monitors class list of dicts
        for m in mon.monitors_list:
            print(m)
            
        print('Primary:', mon.primary_monitor)
        print('Active:', mon.get_active_window())

    def rip_cd(self):
        """ Rip CD using libdiscid, MusicBrainzNGS, CoverArtArchive.org,
            images copied from clipboard and mutagen.
        """

        if encoding.RIP_CD_IS_ACTIVE:
            messagebox.showinfo(title="Rip CD Error",
                                message="Rip CD function is already running!",
                                parent=self.lib_top)
            ''' lift toplevel '''
            self.rip_cd_class.cd_top.focus_force()  # Get focus
            self.rip_cd_class.cd_top.lift()  # Raise in stacking order
            return

        self.rip_cd_class = encoding.RipCD(self.lib_top, self.tt, LODICT)
        return

    def save_items(self):
        """ Save Playlist to disk
            TODO: Separate functions for save_items_as and save_items
                  What about open/close states of parents?
        """
        self.saved_selections = self.lib_tree.tag_has("songsel")
        # Can't Replace "songsel" with "checked" because artist is checked too
        self.play_song_count = len(self.saved_selections)

        ''' At least one song must be selected '''
        if self.play_song_count == 0:
            # Same message in multiple places. Move to own function. Perhaps at top
            # making language changes easier.
            messagebox.showinfo(title="No songs selected.",
                                message="You must select at least one song.",
                                icon='error', parent=self.lib_top)
            return

        # set_font_style()
        save_songs = []
        ext.t_init('save_items()')
        for s_ndx in self.saved_selections:
            if s_ndx.startswith("I"):
                print('Invalid saved_sections:', s_ndx,
                      self.lib_tree.item(s_ndx, 'text'))
                continue
            ndx = int(s_ndx)
            save_songs.append(self.song_list[ndx])

        f = filedialog.asksaveasfile(mode='wb', initialdir=START_DIR,
                                     defaultextension=".pkl", parent=self.lib_top)
        ext.t_end('no_print')

        if f:
            # store the data as binary data stream
            pickle.dump(save_songs, f)
            f.close()

    def new_items(self):
        """ Clear previously selected play list entries
        """

        self.play_close()  # Close playing selections
        self.ndx = 0  # Getting errors out of range
        self.saved_selections = []  # Empty our sorted playlist
        for artist in self.lib_tree.get_children():
            for album in self.lib_tree.get_children(artist):
                for song in self.lib_tree.get_children(album):
                    tags = self.lib_tree.item(song)['tags']
                    #                    if "songsel" in tags:
                    if "checked" in tags:
                        # Turn off all songs
                        self.toggle_select(song, album, artist)

        self.lib_top.update_idletasks()

    def load_items(self):
        """ Load Playlist from disk and erase what's selected already
        """
        self.lib_top_totals.append(LODICT['name'])
        self.lib_top_totals.append("")  # Playlist name makes title bar too long
        self.append_items(erase=True)

    def append_items(self, erase=False):
        # noinspection SpellCheckingInspection
        """ Load Playlist from disk and add to what's selected already

TODO: Convert playlist from one location to another (Import Playlist?)
    $ head Big_List.pkl
    (lp0
    S'/mnt/music/Compilations/Atomic Blonde Soundtrack/01 Cat People (Putting Out The Fire).m4a'
    p1)

    $ head last_playlist
    (lp0
    S'/home/rick/Music/Compilations/White Heat_ 30 Hits [Disc 1]/1-04 Icehouse.m4a'
    p1)

BUG: After Append Items, Open Playlist, New Playlist, Save Playlist As...

    Traceback (most recent call last):
      File "./mserve", line 4565, in <module>
        MusicTree(SORTED_LIST)                           # Build library treeview
      File "./mserve", line 481, in __init__
        self.load_last_selections()
      File "./mserve", line 3009, in load_last_selections
        self.play_from_last_point() # Continue playing where we left off
      File "./mserve", line 3022, in play_from_last_point
        self.play_items()
      File "./mserve", line 3203, in play_items
        self.play_start()
      File "./mserve", line 3475, in play_start
        self.song_set_ndx('next')
      File "./mserve", line 3272, in song_set_ndx
        self.wrap_up_song()                          # Close currently playing
      File "./mserve", line 3297, in wrap_up_song
        ID = self.saved_selections[self.ndx]        # Get treeview song ID
    IndexError: tuple index out of range

        """
        # inspection SpellCheckingInspection
        # set_font_style()

        # f = Playlist of songs selected for playing in artist/album/song order
        f = filedialog.askopenfilename(initialdir=START_DIR,
                                       title="Select playlist to open",
                                       filetypes=[("Pickle file", "*.pkl")],
                                       parent=self.lib_top)

        if not f:
            return  # No file selected

        ''' Add song selections (doesn't turn any off) '''
        selected, newly_selected = \
            self.select_songs_from_filename(f, erase)

        messagebox.showinfo(title="Playlist loaded",
                            message=str(selected) + " songs in playlist.  " +
                            str(newly_selected) + " new songs selected",
                            parent=self.lib_top)

        self.lib_tree.update_idletasks()
        # root.update()
        return

    def select_songs_from_filename(self, filename, erase=False):
        """ Song selections used to flag our playlist """
        # filename = songs selected for playing in shuffled artist/album/song
        # print('pickle.STOP code:', pickle.STOP)

        # save_songs = []
        # save_songs = lc.unpickle_list(filename)   # generic open with errors

        with open(filename, 'rb') as f:
            # read the data as binary data stream
            save_songs = pickle.load(f)
            # print('len(save_songs):', len(save_songs))

        if erase is True:
            self.new_items()  # Erase all previous selections

        newly_selected = 0
        for song in save_songs:
            try:
                ndx = self.song_list.index(song)
            except ValueError:
                continue
            iid = str(ndx)
            tags = self.lib_tree.item(iid)['tags']
            if "checked" not in tags:
                album = self.lib_tree.parent(iid)
                artist = self.lib_tree.parent(album)
                self.toggle_select(iid, album, artist)
                newly_selected += 1

        return len(save_songs), newly_selected

    def save_last_selections(self):

        """ Save to ~/.config/mserve:
                last_location    = 'iid' in location master

            Save settings to disk to ~/.config/mserve/L999/xxx_xxx
                last_selections  = selected songs
                last_open_states = Artist/Album expanded/collapsed states
                last_playlist    = songs selected for playing in user order
                last_song_ndx    = pointer into playlist to continue playing

                # FUTURE ENHANCEMENTS:
                last_variables   = last song index, last playlist name, etc.
        """

        global LODICT, START_DIR

        # Aug 15/2021 - Not sure why sql was being closed but debug database locked
        # sql.con.close()  # If we close now it's lost forever

        # Is self.saved_selections already populated by music player?
        if len(self.saved_selections) == 0:
            # Use selections from toplevel (main treeview)
            self.saved_selections = self.lib_tree.tag_has("songsel")
            # Can't Replace "songsel" with "checked" because artist is checked too

        self.play_song_count = len(self.saved_selections)
        if self.play_song_count == 0:
            # User has cleared all selections, next startup uses previous save
            return ''' No songs selected '''

        ''' Save full path of selected songs in Artist/Album/Track order '''
        save_songs = []
        song_count = 0
        ext.t_init('save_last_selections()')
        # NOTE: Can't drive on using 'checked' because artists are checked too
        for s_ndx in self.lib_tree.tag_has("songsel"):
            ndx = int(s_ndx)  # string to integer
            save_songs.append(self.song_list[ndx])  # Get full path
            song_count += 1  # What if zero?

        with open(lc.FNAME_LAST_SELECTIONS, "wb") as f:
            # store the data as binary data stream
            pickle.dump(save_songs, f)  # Save song list

        ''' Save expanded/collapsed state of Artists & Albums '''
        save_parents = []
        for Artist in self.lib_tree.get_children():  # Process artists
            self.append_open_state(Artist, save_parents)  # Artist text
            for Album in self.lib_tree.get_children(Artist):  # Process albums
                self.append_open_state(Album, save_parents)  # Album text

        with open(lc.FNAME_LAST_OPN_STATES, "wb") as f:
            pickle.dump(save_parents, f)  # Save open states

        ''' Save last opened location iid '''
        # noinspection PyBroadException
        try:
            iid = LODICT['iid']
            lc.save_mserve_location(iid)
        except:
            # Occurs when manually started with directory not in locations
            # Occurs when there are no locations defined whatsoever
            print('Checking to save:', lc.FNAME_LAST_LOCATION)
            print("No 'iid' found in 'LODICT' for:", START_DIR)

        ''' Save full path of selected songs in current play order
            play_shuffle() should be honored '''
        save_songs = []
        song_count = 0
        for s_ndx in self.saved_selections:
            if s_ndx.startswith("I"):
                print('Invalid saved_sections:', s_ndx,
                      self.lib_tree.item(s_ndx, 'text'))
                continue
            ndx = int(s_ndx)  # string to integer
            save_songs.append(self.song_list[ndx])  # Get full path
            song_count += 1  # What if zero?

        with open(lc.FNAME_LAST_PLAYLIST, "wb") as f:
            # store the data as binary data stream
            pickle.dump(save_songs, f)  # Save song list

        ''' Save last playing song  '''
        if self.ndx > (song_count - 1):
            self.ndx = 0
        with open(lc.FNAME_LAST_SONG_NDX, "wb") as f:
            # store the data as binary data stream
            pickle.dump(self.ndx, f)  # Save song index

        ext.t_end('no_print')  # Calculate processing time.

    def get_open_state(self, Id):
        if not Id.startswith("I"):
            print("get_open_state() Id must start with 'I':", Id)
            return  # Skip songs (irrelevant)
        opened = self.lib_tree.item(Id, 'open')
        text = self.lib_tree.item(Id)['text']
        tags = self.lib_tree.item(Id)['tags'][0]  # Only Artist or Album tag
        return opened, text, tags

    def append_open_state(self, Id, opn_states_list):
        if not Id.startswith("I"):
            print("append_open_state() Id must start with 'I':", Id)
            return  # Skip songs (irrelevant)
        opened, text, tags = self.get_open_state(Id)
        # We only want to save "Artist" or "Album" tag, no selections otherwise
        # lookups will fail.
        if "Artist" in tags:
            tags = u"Artist"
        elif "Album" in tags:
            tags = u"Album"
        else:
            print("append_open_state(): Missing 'Artist' or 'Album' tag:", tags)
        opn_states_list.append(tuple((opened, text, tags)))

    def apply_open_state(self, Id, opn_states_list):
        """ Set the expanded/collapsed indicators (triangles) for
            artists and albums. The treeview iid all start with "I"
        """
        if not Id.startswith("I"):
            print("apply_open_state() Id must start with 'I':", Id)
            return  # Skip songs (irrelevant)
        opened, text, tags = self.get_open_state(Id)

        look_closed = tuple((0, text, tags))
        look_open = tuple((1, text, tags))

        if look_closed in opn_states_list:
            if opened is True or opened == 1:
                self.lib_tree.item(Id, open=False)
                # print ("Parent forced to collapsed:", opened, Id, text, tags)
        elif look_open in opn_states_list:
            if opened is False or opened == 0:
                self.lib_tree.item(Id, open=True)
                # print ("Parent forced to expanded:", opened, Id, text, tags)
        else:
            if "Artist" in tags:
                entity = "Artist"
            elif "Album" in tags:
                entity = "Album"
            else:
                entity = "Unknown Entity"
            print("New " + entity + " added to library:", opened, Id, text, tags)
            print("look_closed:", look_closed)

    def load_last_selections(self):

        """ Load last playlist from ~/.config/mserve/L999/xxx_xxx
            Load last location and open ~/.config/mserve/I999/
            Playlist sorted by last order shuffled.
            Begin playing with song we left off at.
            Mark selected playing songs in lib_tree.

            Finally, remove splash screen if mserve.py was called by it.

        """

        global LODICT  # Never change LODICT after startup!

        print(r'  ######################################################')
        print(r' //////////////                            \\\\\\\\\\\\\\')
        print(r'<<<<<<<<<<<<<<    mserve - Music Server     >>>>>>>>>>>>>>')
        print(r' \\\\\\\\\\\\\\                            //////////////')
        print(r'  ######################################################')

        self.saved_selections = []  # Songs selected for playing

        ''' If parameter 1 is for random directory, we have no last location
            So set variables to null and return early.
        '''
        if NEW_LOCATION:
            return

        ''' Check for Last selections file on disk '''
        if not os.path.isfile(lc.FNAME_LAST_SELECTIONS):
            return
        if not os.path.isfile(lc.FNAME_LAST_OPN_STATES):
            return
        if not os.path.isfile(lc.FNAME_LAST_SONG_NDX):
            return

        ''' Load selected songs and parent opened states from disk '''
        ext.t_init('load_last_selections()')

        #save_parents = []  # List of expanded/collapsed flags
        with open(lc.FNAME_LAST_OPN_STATES, 'rb') as f:
            save_parents = pickle.load(f)
            #print('len(save_parents):', len(save_parents))
            #print('save_parents:', save_parents[:10])  # DEBUG
            # save_parents: [(0, u'10cc', u'Artist'), (0, u'The Best of 10cc', u'Album'), (0, u'3 Doors Down',

        #save_playlist = []  # Songs checked in lib_tree
        with open(lc.FNAME_LAST_PLAYLIST, 'rb') as f:
            save_playlist = pickle.load(f)
            #print('len(save_playlist):', len(save_playlist))
            #print(save_playlist[:10])  # DEBUG
            # [u'/media/rick/SANDISK128/Music/April\ Wine/Greatest Hits Live 2003/Just between you and me.mp3',

        song_count = len(save_playlist)
        number_digits = len(str(song_count))

        self.ndx = 0  # Already playing song
        with open(lc.FNAME_LAST_SONG_NDX, 'rb') as f:
            self.ndx = pickle.load(f)
            #print('current index:', self.ndx)

        ''' Set opened states for Artists and Albums '''
        for Artist in self.lib_tree.get_children():  # Read all artists
            self.apply_open_state(Artist, save_parents)
            for Album in self.lib_tree.get_children(Artist):  # Read all albums
                self.apply_open_state(Album, save_parents)

        ''' Set song checkbox tags in library order '''
        ''' TODO: When clicking refresh_lib_tree() this got corrupted
                  so write program to rebuild it from last_open_states
                  and last_playlist which are intact.
        '''
        self.select_songs_from_filename(lc.FNAME_LAST_SELECTIONS)

        ''' Set selections in playlist order self.song_list = '''
        spam_count = 0  # Turn off debugging by setting to 10
        for song in save_playlist:
            try:
                ndx = self.song_list.index(song)
            except ValueError:
                if spam_count < 10:
                    print('Not found:', song)
                    # print(self.song_list[spam_count])
                    spam_count += 1
                continue  # New song added to library
            iid = str(ndx)
            self.saved_selections.append(iid)

            # Update Selected MB/Sequence column with Song number
            song_number = len(self.saved_selections)
            number_str = self.play_padded_number(song_number, number_digits)
            self.lib_tree.set(iid, "Selected", number_str)

        # root.update()
        # print('saved_selections:', self.saved_selections[:10])  # DEBUG
        # saved_selections: ['215', '3694', '1432', '2924', '1627', '2329', '1886', '3623', '1178', '1616']
        self.lib_tree.update_idletasks()
        ext.t_end('no_print')  # Calculate processing time.

        # Keep host awake if necessary
        if LODICT.get('activecmd', "") is not "":
            self.loc_keep_awake_is_active = True

            # May be restarting music player so keep awake immediately
            self.next_active_cmd_time = time.time()
            self.loc_keep_awake()

        # IF self.ndx is greater than number in playlist, reset to 0
        if self.ndx > (len(self.saved_selections) - 1):
            # print('len(self.saved_selections):', len(self.saved_selections))
            # print('last saved song index too large:', self.ndx, 'reset to zero')
            self.ndx = 0

        #if M_START_TIME:
        #    print('load time:', time.time() - M_START_TIME)
        #NameError: global name 'M_START_TIME' is not defined

        if len(self.saved_selections) > 0:
            self.play_from_last_point()  # Continue playing where we left off

    # ==============================================================================
    #
    #       MusicTree Processing - Play All Songs forever
    #
    # ==============================================================================

    def play_from_last_point(self):
        # Continue playing where we left off
        self.play_from_start = False
        # print('Continue playing with song#:',self.ndx)
        self.play_items()

    def play_items(self):
        """ Play 1 or more songs in saved_selections. Define buttons:
                Close, Pause, Prev, Next, Commercial and Intermission
            If Initialize is False then playlist loaded with current song
        """

        if self.play_top_is_active:  # Are we already playing songs?
            if self.play_on_top:
                # If we had the focus, give it up
                self.play_on_top = False
                self.lib_tree_btn2["text"] = "????  Show playing"
                self.lib_top.focus_force()  # Get focus
                self.lib_top.lift()  # Raise in stacking order
            else:
                # If we didn't have focus, take it
                self.play_on_top = True
                self.lib_tree_btn2["text"] = "????  Show library"
                self.play_top.focus_force()  # Get focus
                self.play_top.lift()  # Raise in stacking order
            # root.update()
            self.lib_tree.update_idletasks()
            return  # Don't start playing again

        ''' Count number of songs selected. '''
        self.play_song_count = 0    # How many songs selected for playing
        self.pause_t_start = 0      # How much time was spent paused
        self.play_t_start = 0       # Hom much time was spent playing
        self.play_top_sink = ""     # Fix error if self.play_top_sink is not ""

        if self.play_from_start:
            ''' Get list of items tagged for playing in Artist order '''
            # If not true, we are using playlist in user defined order

            new_selections = self.lib_tree.tag_has("songsel")  # 1484 count
            if len(new_selections) != len(self.saved_selections):
                # Play new selections because old save out of date.
                self.saved_selections = new_selections
            else:
                # We will be keeping current sorted selections and index.
                self.play_from_start = False

        self.play_song_count = len(self.saved_selections)

        ''' At least one song must be selected '''
        if self.play_song_count == 0:
            messagebox.showinfo(title="No Songs Selected",
                                message="You must select at least one song!",
                                parent=self.lib_top)
            return

        ''' Make parent buttons invisible so user doesn't try to click '''
        self.clear_buttons()
        # Option 2 instead of self.clear_buttons()
        # self.lib_top.withdraw()               # Make invisible but still active
        self.play_top = tk.Toplevel()
        self.play_top.minsize(g.WIN_MIN_WIDTH, g.WIN_MIN_HEIGHT)
        self.play_top_is_active = True

        # Set flags for child processes running
        self.sam_top_is_active = False          # Sample middle 10 seconds
        self.syn_top_is_active = False          # Fine-tune time index running?
        self.sync_ffplay_is_running = False     # Playing and syncing?
        self.sync_paused_music = False          # Important this is False now
        self.sync_changed_score = False         # For warning messages

        ''' Gather data to paint VU Meter
            TODO: When pausing vu_meter fill black space with background color. 
        '''
        # /dev/hull prevents ALSA errors from clearing screen with errors:
        #   ALSA lib pcm.c: (snd_pcm_open_no update) Unknown PCM cards.pcm.rear
        #   ALSA lib pcm_route.c: Found no matching channel map
        # If this isn't done real error messages from mserve could be wiped out
        ext_name = "python vu_meter.py stereo 2>/dev/null"
        self.vu_meter_pid = \
            ext.launch_command(ext_name, toplevel=self.play_top)

        ''' Place Window top-left of parent window with PANEL_HGT padding '''
        # TODO: "Using Playlist: Big List"
        #xy = (self.lib_top.winfo_x() + PANEL_HGT,
        #      self.lib_top.winfo_y() + PANEL_HGT)
        self.play_top.minsize(width=BTN_WID * 10, height=PANEL_HGT * 10)
        #self.play_top.geometry('+%d+%d' % (xy[0], xy[1]))
        # June 1, 2021 new sql history
        geom = monitor.get_window_geom('playlist')
        self.play_top.geometry(geom)
        self.play_top_title = "Playing Selected Songs - mserve"
        self.play_top.title(self.play_top_title)
        self.play_top.configure(background="Gray")
        self.play_top.columnconfigure(0, weight=1)
        self.play_top.rowconfigure(0, weight=1)

        ''' Set program icon in taskbar '''
        img.taskbar_icon(self.play_top, 64, 'white', 'lightskyblue', 'black')

        ''' Create master frame '''
        self.play_frm = tk.Frame(self.play_top, borderwidth=BTN_BRD_WID,
                                 relief=tk.RIDGE)
        #        self.play_frm.grid(sticky=tk.NSEW)
        #        tk.Grid.rowconfigure(self.play_frm, 0, weight=1)
        #        tk.Grid.columnconfigure(self.play_frm, 0, weight=0)
        #        tk.Grid.columnconfigure(self.play_frm, 0, weight=1)
        self.play_frm.grid(column=0, row=0, sticky=tk.NSEW)
        # 5 rows of text labels and string variables auto adjust with weight 1
        for i in range(5):
            self.play_frm.grid_rowconfigure(i, weight=1)

        ms_font = (None, MON_FONTSIZE)

        ''' Artwork image spanning 5 rows '''
        self.art_width = 200
        self.art_height = 200
        self.play_no_art()  # Temporary starting image
        self.art_label = tk.Label(self.play_frm, borderwidth=0,
                                  image=self.play_current_song_art, font=ms_font)
        self.art_label.grid(row=0, rowspan=5, column=0, sticky=tk.W)

        ''' Controls to resize image to fit frame '''
        self.play_frm.bind("<Configure>", self.on_resize)
        self.start_w = self.play_frm.winfo_reqheight()
        self.start_h = self.play_frm.winfo_reqwidth()

        ''' Current song number '''
        PAD_X = 5
        self.current_song_number = tk.StringVar()
        # New Short form with 'config_all_labels()' doesn't need variables
        # Apply color codes to buttons - See play_ffmpeg_artwork()
        tk.Label(self.play_frm, text="Current Song:", font=ms_font) \
            .grid(row=0, column=1, sticky=tk.W, padx=PAD_X)
        tk.Label(self.play_frm, text="", textvariable=self.current_song_number,
                 font=ms_font).grid(row=0, column=2, sticky=tk.W)

        ''' Current artist '''
        self.current_song_artist = tk.StringVar()
        tk.Label(self.play_frm, text="Current Artist:", font=ms_font) \
            .grid(row=1, column=1, sticky=tk.W, padx=PAD_X)
        tk.Label(self.play_frm, text="", textvariable=self.current_song_artist,
                 font=ms_font).grid(row=1, column=2, sticky=tk.W)

        ''' Current album '''
        self.current_song_album = tk.StringVar()
        tk.Label(self.play_frm, text="Current Album:", font=ms_font) \
            .grid(row=2, column=1, sticky=tk.W, padx=PAD_X)
        tk.Label(self.play_frm, text="", font=ms_font,
                 textvariable=self.current_song_album) \
            .grid(row=2, column=2, sticky=tk.W)

        ''' Current title '''
        self.current_song_path = ""
        self.current_song_name = tk.StringVar()
        tk.Label(self.play_frm, text="Current Title:", font=ms_font) \
            .grid(row=3, column=1, sticky=tk.W, padx=PAD_X)
        tk.Label(self.play_frm, text="", textvariable=self.current_song_name,
                 font=ms_font).grid(row=3, column=2, sticky=tk.W)

        ''' Progress of play '''
        self.current_progress = tk.StringVar()
        tk.Label(self.play_frm, text="Play Progress:", font=ms_font) \
            .grid(row=4, column=1, sticky=tk.W, padx=PAD_X)
        tk.Label(self.play_frm, text="", textvariable=self.current_progress,
                 font=ms_font).grid(row=4, column=2, sticky=tk.W)

        ''' VU Meter canvas object spanning 5 rows '''
        self.vu_width = 30
        self.vu_height = 200

        self.vu_meter_left = tk.Canvas(self.play_frm, width=self.vu_width,
                                       relief=tk.FLAT,  # Trying to override tk.RIDGE :(
                                       height=self.vu_height, bg='black')
        self.vu_meter_left.grid(row=0, rowspan=5, column=3, padx=PAD_X * 3)
        self.vu_meter_left_rectangle = self.vu_meter_left.create_rectangle(
            0, self.vu_height, 0, self.vu_height)

        self.vu_meter_right = tk.Canvas(self.play_frm, width=self.vu_width,
                                        relief=tk.FLAT,  # Trying to override tk.RIDGE :(
                                        height=self.vu_height, bg='black')
        self.vu_meter_right.grid(row=0, rowspan=5, column=4, padx=PAD_X * 3)
        self.vu_meter_right_rectangle = self.vu_meter_right.create_rectangle(
            0, self.vu_height, 0, self.vu_height)

        self.VU_HIST_SIZE = 6
        self.vu_meter_left_hist = [0.0] * self.VU_HIST_SIZE
        self.vu_meter_right_hist = [0.0] * self.VU_HIST_SIZE

        ''' self.play_F3: Lyrics Frame - Title & Textbox with scrollbar
            Further divided into self.play_F3_panel and lyrics_score_box
        '''

        self.play_frm.grid_columnconfigure(5, weight=1)
        self.play_F3 = tk.Frame(self.play_frm)
        self.play_F3.grid(row=0, rowspan=5, column=5, sticky=tk.NSEW)
        self.play_F3.grid_rowconfigure(1, weight=1)
        self.play_F3.grid_columnconfigure(0, weight=1)

        # Define title frame top of play_F3
        self.play_F3_panel = tk.Frame(self.play_F3)
        self.play_F3_panel.grid(row=0, rowspan=1, column=0, sticky=tk.NSEW)
        self.play_F3_panel.grid_rowconfigure(0, weight=0)
        self.play_F3_panel.grid_columnconfigure(0, weight=1)

        # Rounded rectangle buttons mapped to same .grid using .remove

        # New Short form with 'config_all_labels()' doesn't need variables
        # Apply color codes to buttons - See play_ffmpeg_artwork()
        # There are four different combinations of rounded buttons with
        # tooltips:

        #   FROM     TO     WIDGET NAME                     Button Text
        #  Auto -> Manual   self.lyrics_panel_scroll_a_m    Auto Scrolling
        #  Time -> Manual   self.lyrics_panel_scroll_t_m    Time Scrolling
        #  Manual -> Auto   self.lyrics_panel_scroll_m_a    Manual Scroll
        #  Manual -> Time   self.lyrics_panel_scroll_m_t    Manual Scroll

        rounded_text = "Auto Scrolling"
        tt_text = "Auto Scrolling lyrics is active.\n" + \
                  "Click to scroll lyrics score manually."
        #self.lyrics_panel_scroll_a_m, self.lyrics_panel_scroll_a_m_tt =\
        #    self.create_scroll_button_and_tooltip(
        #        rounded_text, tt_text, ms_font=ms_font)
        self.lyrics_panel_scroll_a_m =\
            self.create_scroll_button_and_tooltip(
                rounded_text, tt_text, ms_font=ms_font)

        rounded_text = "Time Scrolling"
        tt_text = "Lyrics line is highlighted using time index.\n" + \
                  "Click to scroll lyrics score manually."
        #self.lyrics_panel_scroll_t_m, self.lyrics_panel_scroll_t_m_tt =\
        #    self.create_scroll_button_and_tooltip(
        #        rounded_text, tt_text, ms_font=ms_font)
        self.lyrics_panel_scroll_t_m =\
            self.create_scroll_button_and_tooltip(
                rounded_text, tt_text, ms_font=ms_font)

        rounded_text = "Manual Scroll"
        tt_text = "Manual lyrics score scrolling is active.\n" + \
                  "Click to auto scroll lyrics at 1.5x speed."
        #self.lyrics_panel_scroll_m_a, self.lyrics_panel_scroll_m_a_tt =\
        #    self.create_scroll_button_and_tooltip(
        #        rounded_text, tt_text, ms_font=ms_font)
        self.lyrics_panel_scroll_m_a =\
            self.create_scroll_button_and_tooltip(
                rounded_text, tt_text, ms_font=ms_font)

        rounded_text = "Manual Scroll"
        tt_text = "Manual lyrics score scrolling is active.\n" + \
                  "Click to highlight lyrics using time index."
        #self.lyrics_panel_scroll_m_t, self.lyrics_panel_scroll_m_t_tt =\
        #    self.create_scroll_button_and_tooltip(
        #        rounded_text, tt_text, ms_font=ms_font)
        self.lyrics_panel_scroll_m_t =\
            self.create_scroll_button_and_tooltip(
                rounded_text, tt_text, ms_font=ms_font)

        # Set four rounded rectangles to width of the longest rectangle to
        # prevent the longest rectangle right side showing under shorter ones
        self.set_max_dimensions()

        # U+2630 in unicode and then U+22EE
        self.lyrics_panel_text = "0%, Blah blah, Line: 99 of: 99"

        # We give extra padding around label so RoundedRectangle hsa enough
        # space
        self.lyrics_panel_label = tk.Label(
            self.play_F3_panel, borderwidth=BTN_BRD_WID, padx=7, pady=7,
            #text=self.lyrics_panel_text, relief=tk.GROOVE,
            text=self.lyrics_panel_text, font=ms_font)
        #self.lyrics_panel_label.grid(row=0, column=2, sticky=tk.NSEW)
        #self.lyrics_panel_label.grid_rowconfigure(0, weight=0)
        #self.lyrics_panel_label.grid_columnconfigure(0, weight=1)  # Note weight to stretch
        # Center labels in panel
        self.play_F3_panel.update()
        self.lyrics_panel_label.place(relx=.6, rely=.5, anchor="center")

        self.lyrics_panel_last_line = 1                 # Appears in title string

        self.tt.add_tip(self.lyrics_panel_label, tool_type='label',
                        text="Replace me!", anchor="se")

        # Hamburger menu. Do we want to use: ??? or ??? ?
        rounded_text = u"???"
        tt_text = "Left-clicking this hamburger icon brings up a\n" + \
                  "context sensitive menu for web scraping,\n" + \
                  "editing lyrics score and time indexes.\n\n" + \
                  "You can also right-click on the lyrics score\n" + \
                  "and the same context sensitive menu appears."

        """ Define Hamburger rounded rectangle button and it's tooltip """
        self.lyrics_panel_hamburger = img.RoundedRectangle(
            self.play_F3_panel, rounded_text, 'black', 'white',
            ms_font=ms_font, stretch=False,
            command=self.play_lyrics_fake_right_click)

        # Colors reassigned for each song in play_ffmpeg_artwork()
        self.lyrics_panel_hamburger.grid(row=0, column=1, sticky=tk.E)

        self.tt.add_tip(self.lyrics_panel_hamburger, text=tt_text,
                        tool_type='canvas_button', anchor="se")

        # We give extra padding around label so RoundedRectangle hsa enough
        # space. dummy is required because panel_label uses place to center
        # and doesn't permit padding with .place() command
        dummy = tk.Label(
            self.play_F3_panel, borderwidth=BTN_BRD_WID, padx=7, pady=7,
            text=" ", font=ms_font)
        dummy.grid(row=0, column=2, sticky=tk.E)

        # Lyrics current state variables
        self.lyrics_pid = 0  # Process ID for web scrape
        self.lyrics_edit_is_active = False  # song lyrics being edited?
        self.lyrics_train_is_active = False  # basic training time index

        # Default width and height prevent supersized play_top frame
        # undo=True provides support for Ctrl+Z and Ctrl+Shift+Z (Redo)
        self.lyrics_score_box = tk.Text(
            self.play_F3, width=30, height=10, padx=3, pady=3, wrap=tk.WORD,
            insertbackground='white', font=ms_font, undo=True)
        self.lyrics_score_box.grid(row=1, column=0, sticky=tk.NSEW)
        self.lyrics_score_box.bind("<1>", self.play_lyrics_left_click)
        self.lyrics_score_box.bind("<3>", self.play_lyrics_right_click)
        self.lyrics_score_box.tag_config('highlight', background='black',
                                         foreground='white')

        self.lyrics_score_scroll_y = ttk.Scrollbar(
            self.play_F3, command=self.lyrics_score_box.yview)
        self.lyrics_score_scroll_y.grid(row=0, column=1, rowspan=2, sticky='ns')
        self.lyrics_score_box['yscrollcommand'] = self.lyrics_score_scroll_y.set

        ''' Frame for Buttons '''
        self.play_btn = tk.Frame(self.play_top, bg="Blue",
                                 borderwidth=BTN_BRD_WID, relief=tk.GROOVE)
        self.play_btn.grid(row=2, column=0, sticky=tk.NSEW)
        self.play_btn.grid_rowconfigure(0, weight=1)
        self.play_btn.grid_columnconfigure(0, weight=0)

        ''' Close Button ??? '''
        self.close_button = tk.Button(self.play_btn, text="??? Close",
                                      width=BTN_WID2 - 6,
                                      command=self.play_close)
        self.close_button.grid(row=0, column=0, padx=2, sticky=tk.W)
        self.play_top.bind("<Escape>", self.play_close)
        self.play_top.protocol("WM_DELETE_WINDOW", self.play_close)
        self.tt.add_tip(self.close_button, "Close playlist but mserve stays open.",
                        anchor="sw")

        ''' Shuffle Button Em space + u 1f500 = ???? '''
        # BIG_SPACE = "???"         # UTF-8 (2003) aka Em Space
        self.shuffle_button = tk.Button(self.play_btn, text="??????? Shuffle",
                                        width=BTN_WID2 - 6, command=self.play_shuffle)
        self.shuffle_button.grid(row=0, column=1, padx=2, sticky=tk.W)
        self.tt.add_tip(self.shuffle_button, "Shuffle songs into random order.",
                        anchor="sw")

        ''' Pause/Play Button '''
        self.pp_state = "Playing"           # This and next two lines in init
        self.pp_play_text = "???  Play"
        self.pp_pause_text = "?????? Pause"
        self.pp_button = tk.Button(self.play_btn, text=self.pp_pause_text,
                                   width=BTN_WID2 - 5, command=self.pp_toggle)
        self.pp_button.grid(row=0, column=2, padx=2)
        text = "Pause music, pause artwork and\nallow manual lyrics scrolling."
        self.tt.add_tip(self.pp_button, text, anchor="sw")
        self.pp_toggle_time = 0.0

        ''' Prev and Next Buttons '''
        # U+1f844 ????         U+1f846 ????         U_1f808 ????         I+1f80a ????
        self.prev_button = \
            tk.Button(self.play_btn, text="????  Previous", width=BTN_WID2 - 4,
                      command=lambda s=self: s.song_set_ndx('prev'))
        self.prev_button.grid(row=0, column=3, padx=2, sticky=tk.W)
        self.tt.add_tip(self.prev_button, "Play previous song in playlist.",
                        anchor="sw")
        # BIG_SPACE = "???"         # UTF-8 (2003) aka Em Space
        self.next_button = \
            tk.Button(self.play_btn, text="???Next ???? ", width=BTN_WID2 - 6,
                      command=lambda s=self: s.song_set_ndx('next'))
        self.next_button.grid(row=0, column=4, padx=2, sticky=tk.W)
        self.tt.add_tip(self.next_button, "Play next song in playlist.",
                        anchor="sw")

        ''' Hockey Commercial and Intermission Buttons '''
        # ???? | television (U+1F4FA) @ Graphic
        self.play_hockey_active = False  # U+1f3d2 ????
        self.com_button = tk.Button(self.play_btn, text="????  Commercial",
                                    width=BTN_WID2 - 3, command=lambda
                                    s=self: s.start_hockey(TV_BREAK1))
        self.com_button.grid(row=0, column=5, padx=2, sticky=tk.W)
        self.tt.add_tip(self.com_button, "Play music for 90 seconds.\n" +
                        "Turn down TV volume whilst playing.", anchor="sw")
        self.int_button = tk.Button(self.play_btn, text="????  Intermission",
                                    width=BTN_WID2 - 3, command=lambda
                                    s=self: s.start_hockey(TV_BREAK2))
        self.int_button.grid(row=0, column=6, padx=2, sticky=tk.W)
        self.tt.add_tip(self.int_button, "Play music for 18 minutes.\n" +
                        "Turn down TV volume whilst playing.", anchor="se")
        ''' Show/Hide Playlist Chronology button (Frame 4) '''
        self.play_list_hide = False
        self.chron_button = tk.Button(
            self.play_btn, text="???? Hide Chronology",
            width=BTN_WID2 + 1, command=lambda s=self: s.play_show_hide())
        self.chron_button.grid(row=0, column=7, padx=2, sticky=tk.W)

        # TODO: This text is duplicated in show/hide function
        text = "Hide the scrollable playlist below and\n" + \
               "double the size of spinning artwork."
        self.tt.add_tip(self.chron_button, text, anchor="se")

        ''' Frame for Playlist Chronology '''
        self.F4 = tk.Frame(self.play_top, bg="Black", borderwidth=BTN_BRD_WID,
                           relief=tk.GROOVE)
        self.F4.configure(background="Gray")
        self.F4.grid(row=7, column=0, sticky=tk.NSEW)
        self.play_frm.grid_rowconfigure(7, weight=1)
        self.F4.grid_rowconfigure(0, weight=1)
        self.F4.grid_columnconfigure(0, weight=1)  # Note weight to stretch
        self.play_chron_tree()  # Treeview in play order
        # self.F4.grid_remove()                      # Defaults to show

        ''' Start at first listbox entry selected '''
        self.play_top_pid = 0  # Can only be one
        self.play_top_sink = ""
        if self.play_from_start:  # Caller can set starting index
            self.ndx = 0  # Control for current song 0 = 1st

        ''' Remove splash screen if we were called with it. '''
        if self.splash_toplevel:
            self.splash_toplevel.withdraw()  # Remove splash screen
            self.splash_removed = True  # No more splash screen!

        root.update()
        root.after(1000)

        ''' Start a song until signal to close '''
        while self.play_top_is_active:  # Play window closed?
            self.play_start()

            # noinspection SpellCheckingInspection
            """
        Line # 3264 was above when this error occurred. Was selecting images in
        encoding.py to rip on Jim Steinem CD when music clunked to stop but
        spinning and counter continued. Awhile after song should have ended
        (based on counter over) clicked the "Next" button in player to generate
        following error:
        
Next keep awake time: 12:00:06
last message time: 1605034452.73 next message time: 1605035652.73
Looped 20 times, aborting start_fplay() get sink
Traceback (most recent call last):
  File "./mserve", line 4620, in <module>
    MusicTree(SORTED_LIST)                           # Build treeview of songs
  File "./mserve", line 599, in __init__
    self.load_last_selections()
  File "./mserve", line 3056, in load_last_selections
    self.play_from_last_point() # Continue playing where we left off
  File "./mserve", line 3070, in play_from_last_point
    self.play_items()
  File "./mserve", line 3264, in play_items
    self.play_start()
  File "./mserve", line 3550, in play_start
    start_ffplay(self.current_song_path, TMP_CURR_SONG, " ")
TypeError: 'NoneType' object is not iterable

            """
            # inspection SpellCheckingInspection

            self.play_from_start = True  # Reset any low volume override

        self.play_top_pid = 0  # Can only be one
        self.play_top_sink = ""

    def on_resize(self, event):
        """ Resize image when frame size changes """
        # images use ratio of original width/height to new width/height
        # OLD WAY: w_scale = float(event.width) / self.start_w
        h_scale = float(event.height) / self.start_h
        w_scale = h_scale  # It's a square!
        self.art_width = int(w_scale) - 6  # Border width, this is awkward
        self.art_height = int(h_scale) - 6  # play_spin_art
        self.vu_height = self.art_height - 4

        # Quick fix for error:
        #   return Image()._new(core.fill(mode, size, color))
        #   ValueError: bad image size

        if self.art_width < 1:
            self.art_width = 1
        if self.art_height < 1:
            self.art_height = 1
        if self.vu_height < 1:
            self.vu_height = 1

        self.vu_meter_left.config(height=self.vu_height)
        self.vu_meter_right.config(height=self.vu_height)
        if self.art_width > 0 and self.art_height > 0:
            self.play_resized_art = self.play_resized_art.resize(
                (self.art_width, self.art_height), Image.ANTIALIAS)
        self.play_current_song_art = ImageTk.PhotoImage(self.play_resized_art)

        # Sometimes attribute isn't defined yet, e.g. during init
        if hasattr(self, 'pp_state'):
            if self.pp_state is "Paused":
                # Recreate image to new size (doesn't resize in above line).
                self.show_paused_art()

    def create_scroll_button_and_tooltip(self, rounded_text, tt_text, ms_font):
        """ Define rounded rectangle button and it's tooltip """

        rectangle = img.RoundedRectangle(
            self.play_F3_panel, rounded_text, 'black', 'white', ms_font=ms_font,
            command=self.play_lyrics_toggle_scroll)

        # Colors reassigned for each song in play_ffmpeg_artwork()
        rectangle.grid(row=0, column=0, sticky=tk.W)
        rectangle.grid_rowconfigure(0, weight=0)
        rectangle.grid_columnconfigure(0, weight=1)

        #print(tt_text, '\n width', rectangle.width, 'height:', rectangle.height)

        self.get_max_dimensions(rectangle)      # maximum width to reset all

        self.tt.add_tip(rectangle, tool_type='canvas_button', text=tt_text)
        return rectangle

    def get_max_dimensions(self, widget):
        """ Get width and height of widget compare to and set maximums """
        if widget.width > self.lyrics_panel_scroll_widest:
            self.lyrics_panel_scroll_widest = widget.width
        if widget.height > self.lyrics_panel_scroll_highest:
            self.lyrics_panel_scroll_highest = widget.height

    def set_max_dimensions(self):
        """ Set width and height of rounded rectangles to logged maximums """
        self.lyrics_panel_scroll_a_m.config(width=self.lyrics_panel_scroll_widest,
                                            height=self.lyrics_panel_scroll_highest)
        self.lyrics_panel_scroll_t_m.config(width=self.lyrics_panel_scroll_widest,
                                            height=self.lyrics_panel_scroll_highest)
        self.lyrics_panel_scroll_m_a.config(width=self.lyrics_panel_scroll_widest,
                                            height=self.lyrics_panel_scroll_highest)
        self.lyrics_panel_scroll_m_t.config(width=self.lyrics_panel_scroll_widest,
                                            height=self.lyrics_panel_scroll_highest)

    def set_min_dimensions(self):
        """ Set width and height of rounded rectangles to logged maximums """
        self.lyrics_panel_scroll_a_m.config(width=1, height=1)
        self.lyrics_panel_scroll_t_m.config(width=1, height=1)
        self.lyrics_panel_scroll_m_a.config(width=1, height=1)
        self.lyrics_panel_scroll_m_t.config(width=1, height=1)


    def play_no_art(self):
        self.play_original_art = img.make_image(NO_ART_STR,
                                                image_w=self.art_width, image_h=self.art_height)
        self.play_resized_art = self.play_original_art.resize(
            (self.art_width, self.art_height), Image.ANTIALIAS)
        self.play_current_song_art = ImageTk.PhotoImage(self.play_resized_art)

    def show_paused_art(self):
        paused_art = img.make_image(PAUSED_STR, image_w=self.art_width,
                                    image_h=self.art_height)
        paused_resized_art = paused_art.resize(
            (self.art_width, self.art_height), Image.ANTIALIAS)
        self.play_current_song_art = ImageTk.PhotoImage(paused_resized_art)
        self.art_label.configure(image=self.play_current_song_art)

    def pp_toggle(self):
        """ Pause/Play button pressed. Signal ffplay and set button text """
        # print('pp_toggle() has been called:', ext.h(time.time()))
        if not self.play_top_is_active:
            return  # Play window closed?

        ''' Synchronizing lyrics to time index controls music '''
        if self.syn_top_is_active:
            self.sync_time_index_lift()  # Raise window focus to top
            return

        if self.pp_state is "Playing":
            # We were playing so now we will pause
            self.pp_toggle_button()  # Set button text
            # Volume down in 10 steps of 5% with .025 sec in-between, end @ 50%
            # TODO: Put vu meter 'stop' here.
            step_volume(self.play_top_sink, 100, 50, 10, .025,
                        thread=self.play_vu_meter)
            ext.stop_pid_running(self.play_top_pid)  # Pause the music
            self.secs_before_pause = get_curr_ffplay_secs(TMP_CURR_SONG)
            ext.stop_pid_running(self.vu_meter_pid)  # Pause the VU Meters
            self.show_paused_art()  # Mount "Paused" artwork

            for _ in range(self.VU_HIST_SIZE):  # Remove VU_meter rectangles
                self.play_vu_meter(stop='yes')  # Gradually declines as
                self.play_top.after(10)         # history list has more 0 levels
            self.play_vu_meter_blank()          # Fill with self.background
        else:
            # We were paused so now we resume playing
            self.pp_toggle_button()  # Set button text
            ext.continue_pid_running(self.play_top_pid)
            # self.current_song_secs = get_curr_ffplay_secs(TMP_CURR_SONG)
            self.current_song_t_start = time.time()
            ext.continue_pid_running(self.vu_meter_pid)
            # Volume up in 10 steps of 5% with .063 sec in-between, end @ 100%
            step_volume(self.play_top_sink, 50, 100, 10, .063518,
                        thread=self.play_vu_meter)

    def pp_toggle_button(self):
        """ Flip button text. Called from song_set_ndx() and pp_toggle() """
        self.pp_toggle_time = time.time()
        if self.pp_state is "Playing":
            self.pp_state = "Paused"  # Was Playing now is Paused
            self.pp_button['text'] = self.pp_play_text
            text = "Pause music, pause artwork and\nallow manual lyrics scrolling."
            self.tt.set_text(self.pp_button, text)
            if self.play_hockey_active:
                self.play_restore_firefox()  # Restore TV sound

        else:
            self.pp_state = "Playing"  # Was Paused now is Playing
            self.pp_button['text'] = self.pp_pause_text
            text = "Play music, spin artwork and\nautomatically scroll lyrics."
            self.tt.set_text(self.pp_button, text)
            if self.play_hockey_active:
                self.play_soften_firefox()  # Soften volume for commercials

    def song_set_ndx(self, seq):
        """ Set index to previous or next song
            When fast clicking next/previous button tests in other functions
            will trap by testing:
                if not self.last_started == self.ndx:
                    return

            TODO: We aren't saving time indices on next click!

        """
        if not self.play_top_is_active:
            return  # Play window closed?

        ''' Synchronizing lyrics to time index controls music '''
        if self.syn_top_is_active:
            self.sync_time_index_lift()  # Raise window focus to top
            return

        self.wrap_up_song()  # Close currently playing
        if seq == 'prev':
            if self.ndx == 0:  # If on first go to last
                self.ndx = len(self.saved_selections) - 1
            else:
                self.ndx -= 1  # Previous song
        elif seq == 'next':
            if self.ndx == len(self.saved_selections) - 1:
                self.ndx = 0  # On last so go to first
            else:
                self.ndx += 1  # Next song
        else:
            self.ndx = int(seq)  # Jump to index passed

        self.current_song_path = ""  # signal not increment song
        if self.pp_state is "Paused":  # Button reflects paused?
            self.pp_toggle_button()  # Button reflects playing
            # No song loaded so, we don't need to actually unpause. New plays.

    def wrap_up_song(self):
        if len(self.saved_selections) == 0:
            return  # Empty list
        self.kill_song()  # Kill if song is playing

        iid = self.saved_selections[self.ndx]  # Get treeview song ID
        album = self.lib_tree.parent(iid)
        artist = self.lib_tree.parent(album)
        if self.play_opened_album:  # Did we open album?
            opened = self.lib_tree.item(album, 'open')
            # User may have closed parent, but if not we close what we opened
            if opened is True or opened == 1:
                self.lib_tree.item(album, open=False)

        if self.play_opened_artist:  # Did we open artist?
            opened = self.lib_tree.item(artist, 'open')
            # User may have closed parent, but if not we close what we opened
            if opened is True or opened == 1:
                self.lib_tree.item(artist, open=False)

        tags = self.lib_tree.item(iid)['tags']  # Remove 'play_sel' tag
        if "play_sel" in tags:
            tags.remove("play_sel")
            self.lib_tree.item(iid, tags=tags)

    def start_hockey(self, secs):
        """
        Commercial button plays music for 90 seconds then pauses
        Intermission button plays for 1080 seconds (18 minutes)
        """

        ''' Synchronizing lyrics to time index controls music '''
        if self.syn_top_is_active:
            self.sync_time_index_lift()  # Raise window focus to top
            return

        if self.play_hockey_active:
            # Are we already counting down commercial or intermission?
            seconds = ""            # For PyCharm syntax checking
            minutes = ""            # For PyCharm syntax checking
            if self.play_hockey_remaining:
                seconds = '%.1f' % self.play_hockey_remaining
                minutes = '%.2f' % float(self.play_hockey_remaining / 60.0)
            answer = message.AskQuestion(
                self.play_top, thread=self.refresh_play_top,
                title="TV break in progress - mserve", confirm='no',
                text="There are " + seconds + " seconds (" +
                     minutes + ") minutes remaining\n" +
                     "in commercial/intermission.\n\n" +
                     "Do you want to resume TV?")
            if answer.result != 'yes':
                # Keep hockey countdown going
                return

            # End hockey countdown
            self.play_hockey_t_start = 0
            #self.hockey_countdown(999999)
            return

        self.play_hockey_active = True
        self.play_hockey_secs = secs  # Commercial = 90 seconds
        self.play_hockey_remaining = self.play_hockey_secs
        self.play_soften_firefox()  # Soften volume
        self.play_hockey_t_start = time.time()

        ''' GoneFishing gobbles up big screen with shark '''
        ext.t_init('Gone Fishing')
        self.gone_fishing = img.GoneFishing(self.play_top)
        ext.t_end('print')

        # How many iterations? = about seconds at 30 frames per second (33ms)
        self.gone_fishing.plot_move(100)  # More steps = greater compiz success

        if self.pp_state is "Paused":
            self.pp_toggle()  # Play music

    def play_soften_firefox(self):
        """
            Set Firefox volume to 25%
        """
        # Firefox may have multiple entries
        self.play_firefox_indices = sink_list(FIREFOX)
        for index in self.play_firefox_indices:
            os.popen('pactl set-sink-input-volume ' + index + ' 25%') \
                     .read().strip().splitlines()

    def play_restore_firefox(self):
        """
            Restore Firefox volume to 100%
            Note Input Sinks may have changed since volume decreased.
        """
        # rebuild to prevent 17 errors if paused when countdown ends:
        #   Failed to get sink input information: No such entity
        self.play_firefox_indices = sink_list(FIREFOX)

        for index in self.play_firefox_indices:
            os.popen('pactl set-sink-input-volume ' + index + ' 100%') \
                     .read().strip().splitlines()

    def hockey_countdown(self, elapsed):
        """
            Update time remaining for commercials or intermission
        """
        if not self.play_top_is_active:
            return  # Play window closed?
        if not self.play_hockey_active:
            return  # Play hockey not active?

        if self.gone_fishing is not None:
            self.gone_fishing.shark_move()                 # Move shark closer to man

        if elapsed < self.play_hockey_secs:
            remaining = int(self.play_hockey_secs - elapsed)
            if remaining == self.play_hockey_remaining:
                # We don't want to update every 1/10th seconds
                return
            self.play_hockey_remaining = remaining
            com_str = "????  Remaining: " + str(remaining)
            int_str = com_str
        else:
            # repaint buttons
            com_str = "????  Commercial"
            int_str = "????  Intermission"
            if self.gone_fishing is not None:
                self.gone_fishing.close()
            self.gone_fishing = None        # So global close doesn't try
            self.play_restore_firefox()     # Restore volume after commercials

        self.com_button['text'] = com_str
        self.int_button['text'] = int_str
        root.update()  # Process other events TODO: Test less power

    # ==============================================================================
    #
    #       Play one song
    #
    # ==============================================================================

    def play_start(self):
        """ Play song from start.
            If self.play_start is False we are continuing with last song played
            We need to slowly ramp up volume because user may have closed in
            evening and restarted music player in morning (quiet time).

        """

        ''' Get our song_list index number from user treeview selections '''
        if self.ndx > len(self.saved_selections) - 1:
            self.ndx = 0  # Restarted smaller list
        iid = self.saved_selections[self.ndx]
        self.last_started = self.ndx  # Catch fast clicking Next

        ''' TODO: Bitter Sweet Symphony Song.
  File "/home/rick/python/mserve.py", line  3885, in play_start
    list_index = int(iid)
ValueError: invalid literal for int() with base 10: 'I191'

        NEXT TIME PUT IN CIRCUMSTANCE THAT CAUSED ABOVE !!!

        '''

        list_index = int(iid)
        album = self.lib_tree.parent(iid)
        artist = self.lib_tree.parent(album)

        opened = self.lib_tree.item(artist, 'open')
        if opened is not True:
            # Don't want to open artist, it opens all albums. The album
            # will be opened below and open artist at same time.
            self.play_opened_artist = True  # We opened artist
        else:
            self.play_opened_artist = False  # artist was already open

        opened = self.lib_tree.item(album, 'open')
        if opened is not True:
            self.lib_tree.item(album, open=True)
            self.play_opened_album = True  # We opened album
        else:
            self.play_opened_album = False  # Album was already open

        tags = self.lib_tree.item(iid)['tags']  # Append 'play_sel' tag
        if "play_sel" not in tags:
            tags.append("play_sel")
            self.lib_tree.item(iid, tags=tags)
        self.lib_tree.see(iid)  # Ensure song visible

        ''' Set current song # of: total song count '''
        self.current_song_number.set(str(self.ndx + 1) + " of: " +
                                     str(self.play_song_count))

        ''' Build full song path from song_list[] '''
        # TODO: Get SQLite3 row which may have originally been recorded with
        #       different OS directory name or song name which was later
        #       changed.
        self.current_song_path = self.real_path(list_index)

        ''' Populate display with metadata using ffprobe '''
        ext.t_init("self.play_metadata()")
        self.play_metadata(self.current_song_path)
        #global E_WIDTH
        E_WIDTH = 28
        self.current_song_artist.set(self.ellipsis(self.Artist, E_WIDTH))
        self.current_song_album.set(self.ellipsis(self.Album, E_WIDTH))
        self.current_song_name.set(self.ellipsis(self.Title, E_WIDTH))
        self.saved_DurationSecs = self.DurationSecs
        self.saved_DurationMin = tmf.mm_ss(self.saved_DurationSecs)
        ext.t_end('no_print')
        if not self.last_started == self.ndx:  # Fast clicking Next button?
            return

        ''' Get artwork from metadata with ffmpeg '''
        ext.t_init("play_ffmpeg_artwork()")
        self.play_ffmpeg_artwork(self.current_song_path)
        if not self.play_top_is_active:
            return  # Play window closed?
        if not self.last_started == self.ndx:  # Catch if clicking Next
            return
        ext.t_end('no_print')

        ''' Gather song lyrics to fill text box '''
        self.play_init_lyrics()

        ''' Update playlist chronology (Frame 4) with short line = False '''
        self.play_chron_update(self.ndx, False)
        if not self.play_top_is_active:
            return  # Play window closed?
        if not self.last_started == self.ndx:  # Catch if clicking Next
            return

        self.current_song_secs = 0  # How much time played
        self.secs_before_pause = 0  # How much before paused

        ''' Start song with ffplay & Update tree view's last played time 

            TODO: Replace " " with extra options:
                  -ss Start Time
                  -t  Duration
                extra_opt = ' -ss ' + str(self.sync_start) + ' -t 10'
        '''
        extra_opt = " "
        self.play_top_pid, self.play_top_sink = \
            start_ffplay(self.current_song_path, TMP_CURR_SONG, extra_opt)
        self.current_song_t_start = time.time()

        # update treeview display and position treeview to current song
        self.update_lib_tree_song(self.current_song_path, list_index)

        self.play_to_end()  # play song until end

        if self.current_song_path is not "":  # next/prev set new name?
            # Song ended naturally so select next in list
            # TODO: Save should be done in children processes not here
            self.play_save_time_index()  # Save lyrics & time index

            # TODO: Set OsAccessTime in Music Table

            self.song_set_ndx('next')

    @staticmethod
    def ellipsis(string, cutoff):
        """ Format "Very long string" as
                   "long string..."
        """
        if len(string) > cutoff:
            return string[:cutoff - 3] + "..."
        return string

    def update_lib_tree_song(self, full_path, iid):
        """ Update file's last played time in tkinter treeview.
            Linux only updates last access time once per day so use
            touch command to update last access. For example:
            https://opensource.com/article/20/6/linux-noatime
        """
        os.popen('touch -a -c ' + '"' + full_path + '"')  # -a = access time
        stat = os.stat(full_path)  # Get all stat attributes of file
        self.lib_tree.set(iid, 'StatTime', float(stat.st_atime))
        self.update_song_last_play_time(iid)  # Update treeview
        self.lib_tree.see(iid)  # Position listbox

    def update_song_last_play_time(self, iid):
        """ Called by self.update_lib_tree_song() and self.refresh_items()
        """
        a_time = self.lib_tree.set(iid, 'StatTime')
        f_time = tmf.ago(float(a_time))  # Pretty time format
        self.lib_tree.set(iid, 'Access', f_time)

    def play_to_end(self):
        """
        Play single song, checking status 30 fps
        Called from:
            self.play_start() to start a new song
            self.pp_toggle() to resume song after pausing

        """

        while True:
            if not self.play_top_is_active:
                return  # Play window closing

            if not self.last_started == self.ndx:
                return  # Fast clicking Next/Prev buttons

            # If self.play_top_pid active song is playing
            try:
                os.kill(self.play_top_pid, 0)
            except OSError:
                # Do not blank out current song! It controls song_set_ndx('next')
                self.play_top_pid = 0
                self.play_top_sink = ""
                return  # Song has ended

            self.refresh_play_top()  # Rotate art, refresh vu meter

    def refresh_play_top(self):
        """
        Common code for updating graphics that can be called from anywhere
        Use this when stealing processing cycles from self.play_to_end()
        """

        # TODO: tool.thread() needs update to check if called from
        #       multiple places there is no need to repeat what was
        #       just done < 20 ms ago (or whatever the shortest run
        #       time happens to be).

        # DEBUG LOST TIME of .25 seconds or so

        ''' Is system shutting down? '''
        if self.killer.kill_now:
            self.close()

        ''' Always give time slice to tooltips '''
        now = time.time()
        root.update_idletasks()
        self.tt.poll_tips()

        ''' May be called from Library with no music playing (tooltip)  '''
        if not self.play_top_is_active:
            return  # Used to be a "continue" statement

        if self.pp_toggle_time != 0.0:
            # prev_song_sec
            self.pp_toggle_time = 0.0

        ''' Synchronizing lyrics to time index controls music '''
        if self.syn_top_is_active:
            self.syn_top.update()               # Is this needed? YES!
            sleep = 50 - (int(time.time() - now))
            sleep = 1 if sleep < 1 else sleep
            self.syn_top.after(sleep)              # Wait until lyric sync
            return  # Used to be a "continue" statement

        if self.play_hockey_active:  # Is hockey active?
            elapsed = int(time.time() -
                          self.play_hockey_t_start)  # Elapsed time Hockey
            self.hockey_countdown(elapsed)      # Remaining in buttons
            if elapsed > self.play_hockey_secs:  # Has countdown ended?
                self.play_hockey_active = False  # Turn off timer
                if self.pp_state is "Playing":  # Is music playing?
                    self.pp_toggle()            # Pause & watch TV

        if self.pp_state is "Paused":
            self.play_top.update()  # Sept 20 2020
            sleep = 33 - (int(time.time() - now))
            sleep = 1 if sleep < 1 else sleep
            self.play_top.after(sleep)  # Wait until playing
            return

        ''' Following is updated only when music playing '''

        # Update screen with song progress seconds: 999.9
        self.current_song_secs = \
            time.time() - self.current_song_t_start + self.secs_before_pause
        self.current_song_mm_ss_d = tmf.mm_ss(self.current_song_secs, 
                                              trim=False, rem='d')
        # TODO: Explain the rationale for below. Intent is probably future
        #       option for user to select minutes:seconds or just seconds.
        if True is True:
            self.current_progress.set(self.current_song_mm_ss_d +
                                      " of: " + self.saved_DurationMin)
        else:
            self.current_progress.set(str('%.1f' % self.current_song_secs) +
                                      " seconds of: " + str(self.saved_DurationSecs))

        self.play_spin_art()                    # Rotate artwork 1??
        self.play_vu_meter()                    # Left & Right VU Meters
        self.play_paint_lyrics()                # Uses the lyrics time index
        if not self.play_top_is_active:
            return  # Play window closed?
        self.play_top.update()  # Update spinner & text
        sleep = 33 - (int(time.time() - now))   # Strict 30 frames per second
        sleep = 1 if sleep < 1 else sleep
        self.play_top.after(sleep)  # Wait until playing


    def play_metadata(self, path):
        """ WARNING: Called from multiple places
            Get metadata for current song
            NOTE: .wav files have no metadata so when Artist, Album or Track
                  is None use OS filename segments.
        """
        # Called by self.sam_top when self.play_top may NOT be active!
        # if not self.play_top_is_active: return             # Play window closed?
        self.metadata = {}
        # ffplay already output /tmp/mserve.currently has control chars YUK
        ext.t_init("ffprobe")
        result = os.popen('ffprobe ' + '"' + path + '"' +
                          ' 2>' + TMP_FFPROBE).read().strip()
        ext.t_end('no_print')
        if len(result) > 1:
            print('ffprobe result:', result)

        ext.t_init("parse " + TMP_FFPROBE)
        ''' Create self.metadata{} dictionary '''
        with open(TMP_FFPROBE) as f:
            for line in f:
                line = line.rstrip()  # remove \r and \n
                # noinspection PyBroadException
                try:
                    (key, val) = line.split(':', 1)  # Split first ':' only
                except:
                    continue  # No ':' on line
                key = key.strip()  # strip leading amd
                val = val.strip()  # trailing whitespace
                if key is not "" and val is not "":
                    # print ('self.metadata {} key ### val:', key, '###', val)
                    self.metadata[key.upper()] = val
        ext.t_end('no_print')
        #        os.remove(TMP_FFPROBE)

        # Get OS path as Artist, Album, Title.
        # NOTE: If we ripped this song then real info can be retrieved
        #       from SQL Music Table.  EG pretty song name.
        list_index = int(self.saved_selections[self.ndx])
        rpath = self.song_list[list_index].split(os.sep)
        # print('rpath:', rpath[-3], rpath[-2], rpath[-1])

        self.Artist = self.metadata.get('ARTIST', "None")
        if self.Artist == "None":
            self.Artist = rpath[-3].encode('utf-8')  # .wav files have no metadata
        self.Album = self.metadata.get('ALBUM', "None")
        if self.Album == "None":
            self.Album = rpath[-2].encode('utf-8')
        self.Title = self.metadata.get('TITLE', "None")
        if self.Title == "None":
            self.Title = rpath[-1].encode('utf-8')
        self.Genre = self.metadata.get('GENRE', "None")
        self.Track = self.metadata.get('TRACK', "None")
        self.Date = self.metadata.get('DATE', "None")
        self.Duration = self.metadata.get('DURATION', "0,0").split(',')[0]
        self.Duration = self.Duration.split('.')[0]
        self.DurationSecs = self.convert_seconds(self.Duration)  # Note must save in parent

        # Update sql library Music Table with metadata tags
        # Important we use self.Artist instead of self.current_song_artist
        # which can have ellipsis in truncated name.
        sql.update_metadata(self.play_make_sql_key(), self.Artist,
                            self.Album, self.Title, self.Genre, self.Track,
                            self.Date, self.DurationSecs, self.Duration)

    @staticmethod
    def convert_seconds(s):
        """ Convert duration d:hh:mm:ss to seconds
            Make definition static because self isn't changed anywhere
        """
        # Grab segments between : in hh:mm:ss
        if PYTHON_VER == "2":
            seg = map(int, s.split(':'))  # Python 2.x
        else:
            seg = list(map(int, s.split(':')))  # Python 3.x +
        return sum(n * sec for n, sec in zip(seg[::-1], (1, 60, 3600)))

    def play_spin_art(self):
        """
            Spin artwork clockwise, rotate artwork -1?? each decisecond
            at 0?? slide up and pixelate, -90?? slide right, -180?? slide down,
            and at -270?? slide left.
        """
        if not self.play_top_is_active:
            return  # Play window closed?

        # Are we overriding spin art mode?
        if self.play_rotated_value == -360:
            self.play_shifted_art = self.play_art_slide('up')
        elif self.play_rotated_value == -90:
            self.play_shifted_art = self.play_art_slide('right')
        elif self.play_rotated_value == -180:
            self.play_shifted_art = self.play_art_slide('down')
        elif self.play_rotated_value == -270:
            self.play_shifted_art = self.play_art_slide('left')

        if self.play_rotated_value == -365:
            self.play_shifted_art = self.play_art_fade2()

        if self.play_art_slide_count == 0 and self.play_art_fade_count == 0:
            # When count is zero we aren't sliding or fading, so spin again
            if self.play_rotated_value < -360:
                self.play_rotated_value = 0  # At 1 image wobbles-Interesting?
            self.play_rotated_value -= .5  # Rotate 1/2 degree

            ''' If Pillow < 5 background fill for corners more complicated '''
            im = self.play_resized_art.convert('RGBA')
            # Instead of 200,200 use height and width
            self.play_rotated_art = Image.new(
                "RGBA", (self.art_width, self.art_height), self.play_frm_bg)
            rot = im.rotate(self.play_rotated_value)
            self.play_rotated_art.paste(rot, (0, 0), rot)

            ''' ??????If Pillow version >= 5 solution is simple
            self.play_rotated_art = self.play_resized_art. \
                                    rotate(self.play_rotated_value, \
                                    fillcolor=self.play_frm_bg)
            '''

            self.play_current_song_art = \
                ImageTk.PhotoImage(self.play_rotated_art)
        else:
            self.play_current_song_art = \
                ImageTk.PhotoImage(self.play_shifted_art)

        self.art_label.configure(image=self.play_current_song_art)

    def play_art_slide(self, direction):
        """
            Slide artwork in 100 steps.
            at 0?? slide up, -90?? slide right, -180?? slide down, -270?? slide left
        """
        if self.play_art_slide_count == 100 or self.art_width < 10:
            # We have completed a loop + 1 idle loop using 100 %
            self.play_art_slide_count = 0  # Reset art slide count
            # If direction is 'up' we invoke art_fade next
            if direction == 'up':
                self.play_rotated_value = -365  # Start art fade in
            return None

        self.play_art_slide_count += 1  # Increment slide count
        percent = float(self.play_art_slide_count) / 100.0
        return img.shift_image(self.play_rotated_art, direction,
                               self.art_width, self.art_height, percent)

    def play_art_fade_numpy(self):
        """ NUMPY VERSION (not used):
            Fade in artwork in 100 steps leaving for loop after each step and
            reentering after tkinter updates screen and pauses.

            If the RGBA values are (255,255,255,0), then you will see black.
            This is because the transparency is set to 0.
            If the RGBA values are (255,255,255,255), then you will see white.

        """
        if self.play_art_fade_count == 100 or self.art_width < 10:
            # We have completed a full cycle - At 100% it breaks so do 99%:
            # /PIL/ImageTk.py:107: FutureWarning: element wise comparison failed;
            # returning scalar instead, but in the future will perform
            # element wise comparison

            self.play_art_fade_count = 0  # Reset art fade count
            self.play_rotated_value = -361  # Force Spin Art
            return None

        # Initialize numpy arrays
        if self.play_art_fade_count == 0:
            rgb_image = self.play_rotated_art.convert('RGB')
            self.im = np.array(rgb_image)
            self.fade = np.zeros_like(self.im)
            print(self.play_rotated_art.__dict__)
            print('self..play_rotated_ar - format, size, mode:',
                  self.play_rotated_art.format,
                  self.play_rotated_art.size,
                  self.play_rotated_art.mode)
            print('self.im - shape, size, n dim:',
                  self.im.shape, self.im.size, self.im.ndim)
            print('self.fade - shape, size, n dim:',
                  self.fade.shape, self.fade.size, self.fade.ndim)

            # Generate a randomly shuffled array of the coordinates
            X, Y = np.where(self.im[..., 0] >= 0)
            self.co_ords = np.column_stack((X, Y))
            np.random.shuffle(self.co_ords)
            print('self.co_ords - shape, size, n dim:',
                  self.co_ords.shape, self.co_ords.size, self.co_ords.ndim)
            self.xy_list = list(map(tuple, self.co_ords.reshape((2, 2))))
            print('xy_list - len, first element:',
                  len(self.xy_list), self.xy_list[0])

        self.breakpoint = int(self.im.size * self.play_art_fade_count / 100)
        if self.breakpoint == 0:
            self.breakpoint = self.im.size

        count = 0
        for self.n, self.c in enumerate(list(self.co_ords)):
            # Copy one original pixel across to image we are fading in
            x, y = self.c
            if count == 0 and self.play_art_fade_count == 1:
                print('1st element self.co_ords x,y,value:', x, y, self.im[x, y])
            self.fade[x, y] = self.im[x, y]
            # breakpoint reached?
            count += 1
            if self.n % self.breakpoint == 0:
                break

        self.play_art_fade_count += 1
        if self.play_art_fade_count == 100:
            print(self.fade.size, self.play_art_fade_count, self.breakpoint, Count)

        return Image.fromarray(np.uint8(self.fade)).convert('RGB')

    def play_art_fade2(self):
        """ PILLOW VERSION:
            Fade in artwork in 100 chunks leaving loop after 1% chunk and
            reentering after tkinter updates screen and pauses.
        """
        if self.play_art_fade_count == 100:
            # We have completed a full cycle. Force graphical effects exit
            self.play_art_fade_count = 0  # Reset art fade count
            self.play_rotated_value = -361  # Force Spin Art
            return None

        # Initialize numpy arrays first time through
        if self.play_art_fade_count == 0:

            # Create contrasting black or white image to fade into (foreground)
            self.fade = Image.new('RGBA', self.play_rotated_art.size,
                                  color=self.background)

            self.step = self.play_rotated_art.size[0] / 100
            if self.step < 1:
                self.step = 1
            size = self.play_rotated_art.size[0] - self.step

            self.xy_list = [
                (x, y)
                for x in range(0, size, self.step)
                for y in range(0, size, self.step)
            ]

            shuffle(self.xy_list)
            # Convert numpy array into python list & calculate chunk size
            self.current_chunk = 0
            self.chunk_size = int(len(self.xy_list) / 100)

        # Where we stop copying pixels for current 1% chunk
        end = self.current_chunk + self.chunk_size
        if end > len(self.xy_list) - 1:
            end = len(self.xy_list) - 1

        while self.current_chunk < end:
            x0, y0 = self.xy_list[self.current_chunk]
            x1 = x0 + self.step
            y1 = y0 + self.step
            box = (x0, y0, x1, y1)
            region = self.play_rotated_art.crop(box)
            self.fade.paste(region, box)
            self.current_chunk += 1

        self.play_art_fade_count += 1
        return self.fade

    # ==============================================================================
    #
    #       MusicTree Processing - VU Meter
    #
    # ==============================================================================

    def play_vu_meter_blank(self):
        """
            Display blank VU Meter, when music paused.
            Previous dynamic display rectangles have already been removed.
        """
        self.play_vu_meter_blank_side(self.vu_meter_left,
                                      self.vu_meter_left_rectangle)

        self.play_vu_meter_blank_side(self.vu_meter_right,
                                      self.vu_meter_right_rectangle)

    def play_vu_meter_blank_side(self, canvas, rectangle):
        """
            Display blank VU Meter, when music paused.
            Previous dynamic display rectangles have already been removed.
        """
        # Function to display single large rectangle
        x0, y0, x1, y1 = 0, 0, self.vu_width, self.vu_height
        canvas.coords(rectangle, x0, y0, x1, y1)
        canvas.create_rectangle(x0, y0, self.vu_width, y1,
                                fill=self.background,
                                width=1, outline='black', tag="rect")

    def play_vu_meter(self, stop='no'):
        """
            Update VU Meter display, either 'mono' or 'left' and 'right'
        """
        # print('vu_meter_play')
        # return
        if stop == 'yes':
            # Stop display
            self.play_vu_meter_side(
                'stop', self.vu_meter_left,
                self.vu_meter_left_rectangle, self.vu_meter_left_hist)

            self.play_vu_meter_side(
                'stop', self.vu_meter_right,
                self.vu_meter_right_rectangle, self.vu_meter_right_hist)
            return

        # Regular display
        self.play_vu_meter_side(
            VU_METER_LEFT_FNAME, self.vu_meter_left,
            self.vu_meter_left_rectangle, self.vu_meter_left_hist)

        self.play_vu_meter_side(
            VU_METER_RIGHT_FNAME, self.vu_meter_right,
            self.vu_meter_right_rectangle, self.vu_meter_right_hist)

    def play_vu_meter_side(self, fname, canvas, rectangle, history):
        """
            Update one VU Meter display
        """

        if fname == 'stop':
            # We are pausing music but vu_meter.py will wait for sounds and
            # not update the files with zero values. So manually do it here.
            vu_max, vu_amp = 0.0, 0.0
        else:
            with open(fname, "r") as f:
                line = f.readline()
                if len(line) > 2:
                    # noinspection PyBroadException
                    try:
                        s_max, s_amp = line.split()
                    except:
                        # Error on Feb 6, 2021 @ 5:35 pm - Not sure what causes.
                        # Not repeated when adding except & replaying same song.
                        print("play_vu_meter_side(): too many values \
                              to unpack:", line)
                        return False
                    vu_max, vu_amp = float(s_max), float(s_amp)
                else:
                    # Every 30 seconds getting a null line. So skip over it
                    return False

        # Calculate average_amp for last n samples stored in list
        average_amp = sum(history) / self.VU_HIST_SIZE
        max_amp = max(history)
        average_amp = (average_amp + max_amp * 1.5) / 2.5

        # Use smoothed_amp to slowly paint volume decay
        smoothed_amp = vu_amp
        if smoothed_amp < average_amp:
            smoothed_amp = average_amp

        if vu_max == 0.0:
            # No sound (can't divide by zero) set y0 for no rectangle displayed
            percent_height = self.vu_height
        else:
            # We have vu_max. set y0 to percentage of volume, 0 = 100% volume
            percent_height = self.vu_height - \
                             (self.vu_height * smoothed_amp / vu_max)

        self.play_vu_meter_style = 'led'  # Use LED rectangles
        # What style of bar?
        if self.play_vu_meter_style == 'one':
            # Function to display single large rectangle
            x0, y0, x1, y1 = 0, int(percent_height), self.vu_width, self.vu_height
            canvas.coords(rectangle, x0, y0, x1, y1)
            # print("canvas.co ords(self.vu_meter_rectangle", x0, y0, x1, y1)
        else:
            # Function to display multiple smaller rectangles simulating LEDs
            bar_hgt = self.vu_height - int(percent_height)
            self.play_vu_meter_paint(canvas, bar_hgt, self.vu_height)

        # Save current amplitude in sample history list
        history.pop(0)
        history.append(int(vu_amp))
        # print(t(time.time()),history)
        return True

    def play_vu_meter_paint(self, canvas, bar_height, height):
        """
            Number of rectangles depends on height:
                A rectangle must be at least 2 pixels high
                Space between rectangles must be at least 1 pixel

            We have 100 possible steps but there can be scaling down. Reserve
            space for bars based on weight:

                Lower part of bar (10%) is blue
                Major part of bar (60%) is green
                Upper part of bar (15%) is orange
                Top part of bar (15%) is red

            Assuming 30 rectangles and height = 400:

                400/30 = 13 pixels per rectangle and padding
                10 pixels for rectangle, 3 pixels for padding
                3 blue rectangles
                5 orange rectangles
                5 red rectangles
                17 green rectangles (the remainder of 30 - others)
        """

        num_rect = height / 13  # How many rectangles will fit in height?
        if num_rect < 1:
            num_rect = 1  # Not enough height for rectangles

        # r_hgt_pad = rectangle height + padding and sits on y-axis
        #        r_hgt_pad = int(height / num_rect * 1.1)     # Use 10% padding
        r_hgt_pad = int(height / num_rect)

        #r_hgt = int(r_hgt_pad * .9)  # Rectangle height
        r_hgt = r_hgt_pad - 2  # Experimental overrides
        if r_hgt < 1:
            r_hgt = 1  # Not enough height for rectangles

        #pad = r_hgt_pad - r_hgt  # Padding height
        #if pad < 0:
        #    pad = 0

        canvas.delete("rect")  # Remove rectangles from last time

        '''
            Create list of rectangle coordinate tuples (y0, y1). x0 and
            x1 will be constant for left side and right side to form a box
            of (x0, y0, x1, y1). The padding for x0 and x1 defaults to 2 from
            canvas border line.

            Future modification will be to have peek hold 1 second.
            
            Version after peek hold will have opaque colors between peek hold
            and current color.
        '''

        ''' Generate list of all possible rectangles '''
        y_list = []
        negative_r_hgt_pad = r_hgt_pad * -1
        for y0 in range(height - 2, 0, negative_r_hgt_pad):
            y1 = y0 - r_hgt
            if y1 < 0:
                y1 = 0
            y_list.append((y0, y1))

        num_rect = len(y_list)  # We may end up with fewer rectangles

        # print('height:', height, 'number:', num_rect, 'r_hgt_pad:', r_hgt_pad, \
        #       'r_hgt:', r_hgt, 'pad:', pad, 'y_list', y_list)

        # TODO: Analyze why there is rect_count and num_rect
        rect_count = int(round(float(bar_height) / height * num_rect))
        if rect_count > num_rect:
            rect_count = num_rect  # Fix rounding errors
        # print('bar_height:', bar_height, 'rect_count:', rect_count)

        ''' Paint the rectangles '''
        for rect_no in range(1, rect_count):

            y0, y1 = y_list[rect_no - 1]
            percent = rect_no * 100 / num_rect
            if percent < 10:
                color = 'Purple'
            elif percent < 20:
                color = 'RoyalBlue'
            elif percent < 80:
                color = 'SpringGreen3'
            elif percent < 90:
                color = 'Orange'
            else:
                color = 'Red'
            canvas.create_rectangle(3, y0, self.vu_width - 2, y1, fill=color,
                                    width=1, outline='black', tag="rect")

    # ==============================================================================
    #
    #       MusicTree Processing - Song Lyrics
    #
    # ==============================================================================

    def play_init_lyrics(self):
        """ A new song has started playing. Initialize lyrics textbox """
        if self.lyrics_edit_is_active:
            return  # Is user editing lyrics?
        self.play_clear_lyrics()  # Reset all fields

        self.lyrics_score, self.lyrics_time_list = \
            sql.get_lyrics(self.play_make_sql_key())
        if not self.play_top_is_active:
            return

        #print('BEGIN:', self.Artist, self.Album, self.Title)

        if self.lyrics_time_list is None:
            # print('overriding lyrics time index from None to empty list.')
            self.lyrics_time_list = []  # Seconds time index

        if self.lyrics_score is not None:
            if len(self.lyrics_score) < 10:
                # print('overriding lyrics to None: "' + self.lyrics_score +'"')
                self.lyrics_score = None

        if self.lyrics_score is None:
            print('web scraping lyrics from internet')
            self.play_lyrics_from_web()  # scrape lyrics from web
        else:
            # print('getting lyrics from library, count:', len(self.lyrics_score))
            self.play_lyrics_from_library()  # lyrics in Music Table

        self.play_lyrics_rebuild_title()

    def play_lyrics_rebuild_title(self):
        """ Query status of widgets and make title over lyrics body """
        if not self.play_top_is_active:
            return  # Play window is closed

        '''
        # Redefine frame
        if self.play_F3_panel:
            for widget in self.play_F3_panel.winfo_children():
                widget.destroy()
                # _tkinter.TclError: bad window path name ".140066774294968..."
        WE MIGHT RESURRECT THIS CODE: 
        # Remove all widgets in top panel
        if self.play_F3_panel:
            self.play_F3_panel.destroy()
        self.play_F3_panel = tk.Frame(self.play_F3)
        self.play_F3_panel.grid(row=0, row span=1, column=0, sticky=tk.NSEW)
        self.play_F3_panel.grid_rowconfigure(0, weight=0)
        self.play_F3_panel.grid_columnconfigure(0, weight=1)
        '''

        line_count = str(self.work_line_count)
        special = True  # Default to reverse highlight title

        ''' Web scraping mode '''
        if not self.lyrics_pid == 0:
            # NOT TESTED
            self.lyrics_panel_text = \
                'Clicking previous/next too fast for web scraping'

        elif not self.lyrics_scrape_done:
            # NOT TESTED
            self.lyrics_panel_text = "Web scrape in progress..."
            text = \
                "Web scraping takes a couple of seconds.\n" +\
                "If no internet connection BAD THINGS HAPPEN\n" +\
                "NOTE: You can copy lyrics from any website and paste."
            self.tt.set_text(self.lyrics_panel_label, text=text)

        elif self.lyrics_train_is_active:
            # NOT TESTED new flag self.lyrics_train_is_active
            ''' Basic Training mode '''
            self.lyrics_panel_text = "0%, BASIC time index, Line: 1 of: " +\
                                     line_count
            text =\
                "Left-click = Highlights the line being sung\n" + \
                "Right click = Save time index or cancel changes\n" + \
                "NOTE: When song ends time index is automatically saved."

            self.tt.set_text(self.lyrics_panel_label, text=text)

        elif self.lyrics_edit_is_active:
            ''' Edit mode '''
            self.lyrics_panel_text = "EDIT MODE"
            text = \
                "Ctrl + C = Copy highlighted text to clipboard\n" + \
                "Ctrl + V = Paste clipboard text at current cursor position\n" + \
                "Ctrl + Z = Undo\n" + \
                "Ctrl + Shift + Z = Redo\n" +\
                "Backspace = Erase character before cursor\n" +\
                "Delete key = Erase highlighted text\n" +\
                "Enter key = Insert new line after cursor\n" +\
                "Left-click = Move cursor to click point\n" +\
                "Right click = Save lyrics or cancel changes"

            self.tt.set_text(self.lyrics_panel_label, text=text)

        elif self.syn_top_is_active:
            ''' Fine-tune mode '''
            self.lyrics_panel_text = "Disabled during Fine-tune"

        else:
            ''' Normal mode has nothing special going on '''
            self.grid_lyrics_panel_scroll()  # Bring back hidden frames
            # Restore y scroll bar for lyrics score
            # lift relevant rounded rectangle button to top of stacking order
            # There is a bug in lift() for canvas windows. For fix use:
            #     https://stackoverflow.com/a/55559387/6929343
            if self.lyrics_auto_scroll:
                self.lyrics_panel_scroll_a_m.lift()
            elif self.lyrics_time_scroll:
                self.lyrics_panel_scroll_t_m.lift()
            elif self.lyrics_old_scroll == 'auto':
                self.lyrics_panel_scroll_m_a.lift()
            elif self.lyrics_old_scroll == 'time':
                self.lyrics_panel_scroll_m_t.lift()
            else:
                print('unknown lyrics old scroll type:', self.lyrics_old_scroll)

            line_no = self.lyrics_curr_line

            # panel text label tooltip for normal circumstances
            text = \
                "x % time:\n" + \
                "  - x is percentage of lyric lines indexed.\n\n" + \
                "Line: y of z:\n" +\
                "  - y is current line number highlighted (visible).\n" + \
                "  - z is number of lines in song lyrics score."

            self.tt.set_text(self.lyrics_panel_label, text=text)

            self.lyrics_panel_text = "0% time, Line: " + \
                                     str(line_no) + " of: " + line_count
            # Set real percentage complete in lyrics title bar
            self.lyrics_update_title_line_number(1)  # TODO: This doesn't make sense
            special = False  # Do not reverse highlight title or remove buttons

        # Lifted from play_ffmpeg_artwork()
        if special:
            # Reverse title to highlight special mode
            self.play_F3_panel.configure(bg=self.foreground)
            toolkit.config_all_labels(self.play_F3_panel, fg=self.background,
                                      bg=self.foreground)
            # Unfortunately can't change canvas color or text color, just the
            # outline background color. So tags are set up for rounded rectangle
            # and text within it. Below sets background around rounded corners.
            toolkit.config_all_canvas(self.play_F3_panel,
                                      bg=self.foreground)
            # hamburger colors are inverted during special
            self.lyrics_panel_hamburger.update_colors(
                self.background, self.foreground)
            # Restore y scroll bar for lyrics score
            self.lyrics_score_scroll_y.grid()

            # Hide four rounded rectangle buttons for auto/time/manual mode
            self.grid_remove_lyrics_panel_scroll()
            # Shrink size of four rounded rectangles
            self.set_min_dimensions()
            # place label text further to left
            self.lyrics_panel_label.place(relx=0, rely=.5, anchor="w")

        else:
            # Restore title to normal display
            self.play_F3_panel.configure(bg=self.background)
            toolkit.config_all_labels(self.play_F3_panel, fg=self.foreground,
                                      bg=self.background)
            toolkit.config_all_canvas(self.play_F3_panel,
                                      bg=self.background)
            # Hide y scroll bar for lyrics score
            if self.lyrics_auto_scroll or self.lyrics_time_scroll:
                self.lyrics_score_scroll_y.grid_remove()
            else:
                # Manual scrolling needs scrollbar
                self.lyrics_score_scroll_y.grid()

            # Restore four rounded rectangle buttons for auto/time/manual mode
            self.set_max_dimensions()

            # hamburger colors were inverted during special so restore them
            self.lyrics_panel_hamburger.update_colors(
                self.foreground, self.background)

            # place label text back to center
            self.lyrics_panel_label.place(relx=.6, rely=.5, anchor="center")

        # Refresh panel label from new special or normal setup
        self.lyrics_panel_label['text'] = self.lyrics_panel_text

    def grid_remove_lyrics_panel_scroll(self):
        self.lyrics_panel_scroll_a_m.grid_remove()
        self.lyrics_panel_scroll_t_m.grid_remove()
        self.lyrics_panel_scroll_m_a.grid_remove()
        self.lyrics_panel_scroll_m_t.grid_remove()

    def grid_lyrics_panel_scroll(self):
        self.lyrics_panel_scroll_a_m.grid()
        self.lyrics_panel_scroll_t_m.grid()
        self.lyrics_panel_scroll_m_a.grid()
        self.lyrics_panel_scroll_m_t.grid()

    def play_clear_lyrics(self):  # Reset all fields
        self.lyrics_score_box.configure(state="normal")
        self.lyrics_score_box.delete("1.0", "end")  # Delete last lyrics
        self.lyrics_score_box.update()  # Refresh immediately
        self.lyrics_score_box.configure(state="disabled")
        if not self.lyrics_pid == 0:
            print('clicking previous/next too fast for web scraping')
        self.lyrics_prev_line = 0  # Line clicked previously
        self.lyrics_curr_line = 0  # Line just clicked
        self.lyrics_score = None  # Text lines with \n
        self.lyrics_edit_is_active = False  # Is user editing lyrics?
        self.lyrics_train_is_active = False  # basic time index training?
        self.lyrics_time_list = []  # Seconds time index list
        self.lyrics_scroll_rate = 1.5  # Default auto scroll rate
        self.lyrics_old_scroll = None  # Normal scrolling

    def play_lyrics_from_library(self):
        """ turn on auto scrolling, it can be overridden from saved steps or
            if left-clicking on lyrics to set lyrics line to time index.
            self.lyrics_score, self.lyrics_time_list = sql.get_lyrics(key)
        """
        self.play_lyrics_populate_score_box()

        self.lyrics_scrape_done = True  # Signal we are done scrape
        # print('last line:', self.lyrics_line_count, 'end:', end)

        self.lyrics_scroll_rate = 1.5  # TODO: Set rate for song
        if len(self.lyrics_time_list) == 0:
            self.lyrics_time_scroll = False
            self.lyrics_auto_scroll = True
        else:
            self.lyrics_time_scroll = True
            self.lyrics_auto_scroll = False  # Use lyrics time index

    def play_lyrics_populate_score_box(self):
        """ Called from self.play_lyrics_from_library() and
                        self.sync_save_changes()
        """
        self.lyrics_score_box.configure(state="normal")
        for line in self.lyrics_score:
            self.lyrics_score_box.insert(tk.END, line)
        self.lyrics_score_box.update()  # Is this necessary? CONFIRMED YES
        self.lyrics_score_box.configure(state="disabled")

        end = self.lyrics_score_box.index('end')  # returns line.column
        self.lyrics_line_count = int(end.split('.')[0]) - 1
        self.work_line_count = self.lyrics_line_count  # FUDGE FOR Time being...
        # After changing lyrics in self.sync_save_changes() they aren't updating
        self.lyrics_score_box.update()

    def play_lyrics_from_web(self):
        """ turn on auto scrolling, it can be overridden from saved steps or
            if left-clicking on lyrics to set lyrics line to time index.
        """
        webscrape.delete_files()  # Cleanup last run
        self.lyrics_line_count = 1  # Average about 45 lines

        artist = ext.shell_quote(self.Artist)  # backslash in from of '
        song = ext.shell_quote(self.Title)     # and " in variables
        # 'Bob Seeger & The Silver Bullet Band' finds nothing, while just
        # 'Bob Seeger' finds 'Shakedown' song.
        artist = artist.split('&', 1)[0]

        if self.lyrics_pid == 0:
            # Only start new search if last one is finished.
            # Implausible test since we aren't called until true.
            MusicId = sql.hist_get_music_id(self.work_sql_key)
            # Aug 12/2021 change 'USER' to 'g.USER' didn't test
            sql.hist_add(time.time(), MusicId, g.USER, 'scrape',
                         'parm', artist, song, "", 0, 0, 0.0,
                         time.asctime(time.gmtime(time.time())))
            sql.con.commit()
            # Aug 25 fudge parameter list to skip no_parameters()
            parm = '"' + artist + ' ' + song + '" ' + str(MusicId)
            ext_name = 'python webscrape.py ' + parm
            self.lyrics_pid = ext.launch_command(ext_name,
                                                 toplevel=self.play_top)
        else:
            print('Last instance of webscrape is still running.')
            return

        self.lyrics_scrape_done = False  # Signal not done yet
        self.lyrics_auto_scroll = True
        self.lyrics_time_scroll = False
        # print('initial self.lyrics_pid:', self.lyrics_pid, \
        #      'type:', type(self.lyrics_pid))

    def play_paint_lyrics(self, caller=""):
        """ Scroll lyrics in text box """
        if not self.lyrics_scrape_done:
            ''' It takes a few seconds to get lyrics from internet '''
            self.lyrics_pid = ext.check_pid_running(self.lyrics_pid)
            if self.lyrics_pid == 0:
                self.play_process_scraped_lyrics()
                # We have to save the lyrics we just scraped from the web
                self.play_save_score_erase_time()
                self.lyrics_scrape_done = True
                self.play_lyrics_rebuild_title()
            else:
                return  # We are still fetching lyrics

        # Update percentage complete in lyrics title bar
        self.lyrics_update_title_percentage()

        # If scrape lyrics function called us we don't want to scroll text
        if caller == "get_new":
            self.play_lyrics_rebuild_title()    # NOT TESTED!
            return

        ''' Scroll automatically or by interactive / recorded steps '''
        if self.lyrics_edit_is_active:
            return  # Is user editing lyrics?

        if self.lyrics_auto_scroll:
            self.play_lyrics_auto_scroll()
        else:
            self.play_lyrics_time_scroll()

    def play_process_scraped_lyrics(self):
        """ Read lyrics and populate text box """
        if self.lyrics_edit_is_active:
            return  # Is user editing lyrics?

        self.lyrics_score_box.configure(state="normal")
        # TODO: Grab lyrics from SQL web scrape result instead of
        #       pickle file.
        with open(webscrape.SCRAPE_LYRICS_FNAME, "r") as ws_file:
            lines = ws_file.readlines()
            for line in lines:
                # Skip lines with all whitespace
                if not line.isspace():
                    self.lyrics_score_box.insert(tk.END, line)

        self.lyrics_score_box.update()  # Is this necessary? CONFIRMED YES
        self.lyrics_score_box.configure(state="disabled")
        webscrape.delete_files()

        end = self.lyrics_score_box.index('end')  # returns line.column
        self.lyrics_line_count = int(end.split('.')[0]) - 1

    def play_make_sql_key(self):
        """ Create key to read Music index by OsFileName which is
            /path/to/topdir/album/artist/song.ext
        """
        list_index = int(self.saved_selections[self.ndx])
        return sql.make_key(self.song_list[list_index])

    def play_save_score_erase_time(self):
        """ Preliminary lyrics save that WIPES OUT the lyrics time index """
        if not self.play_top_is_active or self.lyrics_edit_is_active:
            return  # Play closed or user editing lyrics?

        self.lyrics_score = self.lyrics_score_box.get("1.0", 'end-1c')
        save = self.play_override_score()
        sql.update_lyrics(self.play_make_sql_key(), save, None)

    def play_override_score(self):
        """ If lyrics not found return None, else return them """
        if self.lyrics_score.startswith("No lyrics found for "):
            return None
        else:
            return self.lyrics_score

    def play_save_time_index(self):
        """ Final lyrics save that saves the lyrics time index """
        if not self.play_top_is_active or self.lyrics_edit_is_active:
            return  # Play closed or user editing lyrics?

        save = self.play_override_score()

        if self.lyrics_time_list is not None:
            if len(self.lyrics_time_list) == 0:
                self.lyrics_time_list = None

        sql.update_lyrics(self.play_make_sql_key(), save,
                          self.lyrics_time_list)

    def play_lyrics_auto_scroll(self):
        """ Automatically update cursor position in text box.
            Based on percentage of time, not synchronized to the lyrics.
            NO highlight bar
        """
        if not self.play_top_is_active or self.lyrics_edit_is_active:
            return  # Play closed or user editing lyrics?

        # Calculate play progress percentage
        percent = self.current_song_secs / self.saved_DurationSecs
        line_no = int(self.lyrics_line_count * percent * self.lyrics_scroll_rate)
        if line_no > self.lyrics_line_count:
            line_no = self.lyrics_line_count
        self.lyrics_score_box.see(str(line_no) + ".0")

        # Update 'Line: 99 of 99' in lyrics title bar (aka panel)
        self.lyrics_update_title_line_number(line_no)

    def play_lyrics_time_scroll(self):
        """ Synchronize cursor position in text box using lyrics time index
            and a highlight bar to indicate current lyrics line.
            Can be called when all indices set from previous training.
            Can be called when last index was just set during training in
                which case we don't want to override to previous line.
        """
        # if not self.play_top_is_active or len(self.lyrics_time_list) == 0:
        #      File "/home/rick/python/mserve.py", line 5274, in play_lyrics_time_scroll
        #        if not self.play_top_is_active or len(self.lyrics_time_list) == 0:
        #    TypeError: object of type 'NoneType' has no len()
        if not self.play_top_is_active or not self.lyrics_time_list:
            return  # Play has stopped or no lyrics time index

        # Look up current time in list
        old_lyrics_curr_line = self.lyrics_curr_line
        self.lyrics_curr_line = 0
        # print('Searching for current seconds:', self.current_song_secs)
        line_found = False
        for i, seconds in enumerate(self.lyrics_time_list):
            # Search current seconds to first greatest lyrics time index
            # Note if we just added line, it could be exactly same seconds
            if seconds > self.current_song_secs:
                # print('Found greater seconds:', seconds, 'at index i:', i)
                self.lyrics_curr_line = i  # Previous line number is the current index
                line_found = True
                break

        if not line_found:
            # We are the last line
            # print('USING END OF LOOP seconds:', seconds, 'at index i:', i)
            self.lyrics_curr_line = len(self.lyrics_time_list)
        elif self.lyrics_curr_line < old_lyrics_curr_line:
            # We have just overridden self.lyrics_curr_line but did it
            # backwards from where we just were.
            self.lyrics_curr_line = old_lyrics_curr_line

        ''' Update screen when current line changes based on time index '''
        if self.lyrics_curr_line != self.lyrics_prev_line:
            self.play_lyrics_remove_highlights()
            self.play_highlight(self.lyrics_curr_line)
            if self.lyrics_time_scroll:  # May 15/21: manual
                self.play_lyrics_see_ahead()

        self.lyrics_prev_line = self.lyrics_curr_line

        # Update 'Line: 99 of 99' in lyrics title bar (aka panel)
        self.lyrics_update_title_line_number(self.lyrics_curr_line)

    # ==============================================================================
    #
    #       MusicTree Processing - Basic time index
    #
    # ==============================================================================

    def play_train_lyrics(self):
        """ Train Lyrics was right-clicked. Right click again to Save/Cancel.

            WARNING: work_time_list, new_time_list and lyrics_time_list are
                    used differently.
        """
        if not self.lyrics_pid == 0:
            print('lyrics are being web scraped. Please wait a second.')
            return

        if not self.play_top_is_active or self.syn_top_is_active:
            return

        print('TRAIN LYRICS:', self.Artist, self.Album, self.Title)

        ''' turn off auto scrolling and use synchronized time indices '''
        self.lyrics_auto_scroll = False
        # print('previous line:', self.lyrics_prev_line, 'clicked line:', line, \
        #      'at lyrics time index:', self.current_song_secs)

        self.play_lyrics_remove_highlights()

        self.lyrics_train_is_active = True
        self.lyrics_train_start_time = time.time()
        self.play_create_lyrics_work_fields()  # sql key, score & time list
        # Refresh title to reflect edit mode is in progress
        self.play_lyrics_rebuild_title()

    def play_train_lyrics_done(self, action):
        """ Train Lyrics done. action='save' or 'cancel' or 'quit'
        """
        self.lyrics_train_is_active = False  # Allow normal read/save ops

        # If cancel bail out now and spare indenting after an "else:"
        if action == 'cancel':
            # Restore old time list from work field
            self.lyrics_time_list = self.work_time_list
            self.play_init_lyrics()  # We may be on a new song at this point.
            return

        # Save current text box and revised time list to library
        sql.update_lyrics(self.work_sql_key,
                          self.work_lyrics_score,
                          self.lyrics_time_list)

        # Hold variables reset by self.play_init_lyrics()
        hold_work_sql_key = self.work_sql_key
        hold_lyrics_old_scroll = self.lyrics_old_scroll
        hold_lyrics_auto_scroll = self.lyrics_auto_scroll
        hold_lyrics_time_scroll = self.lyrics_time_scroll
        self.play_init_lyrics()  # We may be on a new song at this point.

        # If we are still on same song reset variables to hold values
        if hold_work_sql_key == self.work_sql_key:
            # Honor previous scrolling setting: auto/time/manual
            self.lyrics_old_scroll = hold_lyrics_old_scroll
            self.lyrics_auto_scroll = hold_lyrics_auto_scroll
            self.lyrics_time_scroll = hold_lyrics_time_scroll

            # Position cursor to where it was when editing finished
            self.lyrics_score_box.configure(state="normal")
            self.lyrics_score_box.mark_set("insert",
                                           self.edit_current_cursor)
            self.lyrics_score_box.update()  # Refresh immediately
            self.lyrics_score_box.configure(state="disabled")

        # Refresh title to reflect edit mode is in progress
        self.play_lyrics_rebuild_title()

    def play_lyrics_left_click(self, event):
        """ Left-clicked lyric line. Scroll as needed to see next two lines.
            Highlight line with reversed colors. Record time index (the 
            cross-reference between seconds and line number). Remove
            highlight from previous line (unless zero). If you click the next
            line too soon simply re-click the current line again and the false
            click will be discarded. rename list_data to os_filenames

            WARNING: work_time_list, new_time_list and lyrics_time_list are
                    used differently.

            Lyrics were either retrieved from the internet (takes 2 seconds) or
            from SQL row in table Music indexed by OsFileName. There may be
            duplicates so read until Music.OsArtist and Music.OsAlbum match as
            well. Use SORTED_LIST or self.song_list

        """
        if self.lyrics_edit_is_active:
            # When editing lyrics, any left click is to position cursor and
            # not for changing highlighted line for synchronizing time index
            return

        if not self.lyrics_train_is_active:
            # If not in basic training, treat left-click as right-click
            self.play_lyrics_right_click(event)
            return

        if self.pp_state is 'Paused':
            # If Pause/Play State is currently paused we can not synchronize
            # June 5/2021: change top level from self.play_top
            answer = message.AskQuestion(
                self.lyrics_score_box, thread=self.refresh_play_top,
                title="Music is paused - mserve", confirm='no',
                text="Left clicking synchronizes lyrics\n" +
                     "but only works when music is playing.\n" +
                     "Do you want to resume playing?")
            if answer.result is 'yes':
                # Resume playing
                self.pp_toggle()
            # Don't want click that resume play to be interpreted as syncing
            return

        # If not a new line and Lyrics > 80% synchronized use Fine-Tune.
        # It can delete all if needed.
        ''' PROBLEM with this method is when they are synchronizing the first
            time on way up to 100%
        percent = self.lyrics_update_title_percentage()
        if percent >= 81:
            # If Pause/Play State is currently paused we can not synchronize
            message.ShowInfo(self.play_top, \
                     title="Time is >= 80% synchronized", \
                     text="Use right-click followed by Fine-Tune time index")
            return
        '''

        # TODO: What if accidentally clicked left instead of right?

        ''' PROBLEM When seeding ahead multiple lines and going back to
            sync properly. It's not allowing to click earlier. It automatically
            resets forwards.
            Must "Delete All" in Fine-tune followed by Next followed by Prev.
            
            When restarting Avenged Sevenfold - Afterlife cannot click back one
            line? Also percentage stuck at 46% when it is 100%. Also cannot
            save fine-tune???
        '''

        self.play_lyrics_remove_highlights()
        index = self.lyrics_score_box.index("@%s,%s" % (event.x, event.y))
        line, char = index.split(".")
        self.lyrics_curr_line = int(line)  # Line # just clicked
        self.play_highlight(self.lyrics_curr_line)  # Position highlight bar
        # We probably don't need a separate function anymore
        # if self.lyrics_time_scroll == True:
        #     self.play_lyrics_replace_time()
        #     return

        ''' Scroll as needed to see next two lines '''
        self.play_lyrics_see_ahead()

        ''' Compare current line # to list line count and previous line # '''
        if self.lyrics_time_list:
            line_cnt = len(self.lyrics_time_list)
        else:
            line_cnt = 0
        if self.lyrics_curr_line > line_cnt + 1:
            # clicked many lines down to make up for lost clicking
            # Create dummy time indices between line count and current line #
            self.play_lyrics_create_skipped(line_cnt + 1, self.lyrics_curr_line)
        elif self.lyrics_prev_line + 1 == self.lyrics_curr_line:
            # Clicking next line. But if it exists we are replacing time
            if line_cnt > self.lyrics_curr_line:
                self.play_lyrics_replace_time()
            else:
                # line_cnt is <= current line #
                self.lyrics_time_list.append(self.current_song_secs)
        elif self.lyrics_prev_line == self.lyrics_curr_line:
            # Clicked previous line indicating they clicked ahead too soon
            self.play_lyrics_replace_time()
        elif self.lyrics_prev_line > self.lyrics_curr_line:
            # Clicked many lines earlier so everything in between needs time
            # bumped down by time difference / # of lines difference.
            for i in range(self.lyrics_curr_line, self.lyrics_prev_line):
                # Delete last entry for loop # of times
                # TODO: We are deleting last entry, may not be in range.
                del self.lyrics_time_list[-1]
        else:
            print('left click lyrics line not handled.',
                  'line_cnt:', line_cnt,
                  'prev_line:', self.lyrics_prev_line,
                  'curr_line:', self.lyrics_curr_line)
            self.lyrics_curr_line = self.lyrics_prev_line
            print('curr_line has been reset to prev_line')

        self.lyrics_prev_line = self.lyrics_curr_line

        # Update percentage complete in lyrics title bar
        self.lyrics_update_title_percentage()

        # Update 'line: 99 of 99' in lyrics title bar (aka panel)
        self.lyrics_update_title_line_number(self.lyrics_curr_line)

    def lyrics_update_title_percentage(self):
        """ Called from many places.
        """
        if self.lyrics_time_list:
            sync_cnt = len(self.lyrics_time_list)
        else:
            sync_cnt = 0
        percent = sync_cnt * 100 / self.lyrics_line_count

        try:
            # Title is dynamic based on methodology, may not have percentage
            suffix = self.lyrics_panel_text[self.lyrics_panel_text.index('%'):]
            self.lyrics_panel_text = str(percent) + suffix
        except ValueError:
            pass

        # Override title when editing lyrics
        ''' REPLACE in rebuild_title() 
        '''
        if not self.lyrics_edit_is_active:
            self.lyrics_panel_label['text'] = self.lyrics_panel_text

        self.play_F3_panel.update()
        return percent

    def lyrics_update_title_line_number(self, line_no):
        """ Unlike lyrics_update_title_percentage this function is only
            called when line number is in title. No need to test if
            title bar should be formatted with line number.
        """
        # Update 'line: 99 of 99' in lyrics title bar (aka panel)
        # Overrides rebuild_title()
        if line_no == self.lyrics_panel_last_line:
            return  # Line number hasn't changed, not need to update title

        try:
            prefix = self.lyrics_panel_text[:self.lyrics_panel_text.index('Line: ')]
            suffix = self.lyrics_panel_text[self.lyrics_panel_text.index('Line: '):]
        except ValueError:
            print('lyrics_update_title_line_number() string not found')
            return

        suffix2 = suffix.split()[2:]
        self.lyrics_panel_text = prefix + "Line: " + str(line_no) + " " + ' '.join(suffix2)
        self.play_F3_panel.update()
        self.lyrics_panel_last_line = line_no

    def play_lyrics_see_ahead(self):
        line_no = self.lyrics_curr_line + 2  # Reveal up-coming
        if line_no > self.lyrics_line_count:
            line_no = self.lyrics_line_count
        self.lyrics_score_box.see(str(line_no) + ".0")

    def play_lyrics_replace_time(self):
        """ Clicking same line again to reset start time.

            Called when:

            if self.lyrics_prev_line + 1 == self.lyrics_curr_line:
                if line_cnt > self.lyrics_curr_line:
                    play_lyrics_replace_time(self):
            elif self.lyrics_prev_line == self.lyrics_curr_line:
                    play_lyrics_replace_time(self):

        """
        print('play_lyrics_replace_time() BEGIN')
        this_ndx = self.lyrics_curr_line - 1
        if self.lyrics_time_list[this_ndx] < self.current_song_secs:
            # Clicked ahead too quickly now going back. Keep time
            print('Clicked ahead too quickly now going back. Keep time')
            return

        # old time was greater than current time so replace it current.
        print('Old time:', self.lyrics_time_list[this_ndx],
              'New time:', self.current_song_secs)
        self.lyrics_time_list[this_ndx] = self.current_song_secs

        line_cnt = len(self.lyrics_time_list)
        last_ndx = line_cnt - 1
        next_ndx = self.lyrics_curr_line
        ndx_after_next = self.lyrics_curr_line + 1

        if ndx_after_next <= last_ndx:
            # Give 2 seconds to click next line
            # TODO: We have to keep doing this forever!
            two_second_rule = self.current_song_secs + 2
            if self.lyrics_time_list[next_ndx] < two_second_rule:
                print('Two second rule. Next line (not last) was:',
                      self.lyrics_time_list[next_ndx],
                      'Changing to :', two_second_rule)
                self.lyrics_time_list[next_ndx] = two_second_rule
        elif next_ndx == last_ndx:
            # next index is the last one so simply delete it.
            print('next index is the last one so simply delete it.')
            del self.lyrics_time_list[next_ndx]
        else:
            print('play_lyrics_replace_time() ERROR:')
            print('this_ndx:', this_ndx, 'next_ndx:', next_ndx,
                  'ndx_after_next:', ndx_after_next)

    def play_lyrics_create_skipped(self, first, last):
        """

            TODO: Pause music and display what will happen in Yes/No Message

            Clicking many lines ahead to make up for missed lines.
            To compensate add dummy lines from last know index (or zero if none)
            divided by the elapsed time divided by the number of inserted lines.

        if self.lyrics_curr_line > line_cnt + 1:
            self.play_lyrics_create_skipped(line_cnt+1, self.lyrics_curr_line)

        """
        # Catch logic errors. Plethora of checks yielding nothing....
        plus_one = len(self.lyrics_time_list) + 1
        if first > plus_one:
            print('play_lyrics_create_skipped(first:', first, ', last):', last)
            print('ERROR: First line # is > last line # recorded plus 1.')
            return

        if first <= len(self.lyrics_time_list):
            print('play_lyrics_create_skipped(first:', first, ', last):', last)
            print('ERROR: First line # <= last line # recorded.')
            return

        if first < 1:
            # First line must be at least 1
            print('play_lyrics_create_skipped(first:', first, ', last):', last)
            print('ERROR: first line # can never be less than 1.')
            return

        if last <= first:
            # Last line must be > first line
            print('play_lyrics_create_skipped(first:', first, ', last):', last)
            print('ERROR: Last line # must be > first line #.')
            return

        if last - first < 1:
            # Only one entry to append
            self.lyrics_time_list.append(self.current_song_secs)
            print('play_lyrics_create_skipped(first:', first, ', last):', last)
            print('WARNING: Only one line was appended, function not needed.')
            return

        if first == 1:
            start_time = 0.0
        else:
            # Get previous entry's start time. first = line_count + 1
            # Last entry on record index = first - 2
            start_time = self.lyrics_time_list[first - 2]

        elapsed_time = self.current_song_secs - start_time
        step_time = elapsed_time / (last - first)

        print('play_lyrics_create_skipped() first:', first, 'last:', last)
        print('self.current_song_secs:', self.current_song_secs,
              'start_time:', start_time)
        print('elapsed_time:', elapsed_time, 'step_time:', step_time)
        for i in range(first, last + 1):  # Was creating 1 too many
            #        for i in range(first, last):       # Was creating 1 too few
            start_time += step_time
            self.lyrics_time_list.append(start_time)
            print('added:', i, 'with seconds:', start_time)

    def play_highlight(self, n):
        self.lyrics_score_box.tag_add("highlight", "{}.0".format(n),
                                      "{}.0+1lines".format(n))

    def play_lyrics_remove_highlights(self):
        self.lyrics_score_box.tag_remove("highlight", "1.0", tk.END)

    def play_lyrics_toggle_scroll(self):
        """ Check if auto scrolling or timed scrolling, if so set to manual.
            If manual reverse to previous setting.

            TODO: This is broken May 13, 2021. Doesn't turn off time scroll
                  Create button in lyrics title bar showing scrolling state
                    left-clicking button will toggle the state, right-clicking
                    will bring up menu to select states - timed, auto, manual
        """

        if self.lyrics_old_scroll is not None:  # Override scroll in effect?
            if self.lyrics_old_scroll is 'auto':
                self.lyrics_auto_scroll = True  # Restore auto scrolling
            elif self.lyrics_old_scroll is 'time':
                self.lyrics_time_scroll = True  # Restore time scrolling
            else:
                print("self.lyrics_old_scroll isn't 'auto' or 'time'",
                      self.lyrics_old_scroll)
            self.lyrics_old_scroll = None  # Back to normal scrolling

        elif self.lyrics_auto_scroll:
            self.lyrics_old_scroll = 'auto'  # Save auto scrolling state
            self.lyrics_auto_scroll = False  # Turn off auto scrolling

        elif self.lyrics_time_scroll:
            self.lyrics_old_scroll = 'time'  # Save time scrolling state
            self.lyrics_time_scroll = False  # Turn off time scrolling

        else:
            print("self.lyrics_time_scroll:", self.lyrics_time_scroll,
                  "self.lyrics_auto_scroll:", self.lyrics_auto_scroll)
            print("self.lyrics_old_scroll isn't 'auto' or 'time'",
                  self.lyrics_old_scroll)

        self.play_lyrics_rebuild_title()

    # ==============================================================================
    #
    #       MusicTree class - Lyrics Right click menu - Edit, Scrape options
    #
    # ==============================================================================

    def play_lyrics_fake_right_click(self):
        """ Callback from RoundedRectangle click on hamburger menu
        """
        fake_event = message.FakeEvent(self.play_F3_panel)
        self.play_lyrics_right_click(fake_event)


    def play_lyrics_right_click(self, event):
        """ Right-clicked lyric line. Popup menu with options:

            - Webscrape lyrics (from genius.com. FUTURE option pick website)
            - Clipboard paste lyrics (erases current lyrics first)
            - Edit lyrics (Control+C and Control+V supported)
            - Toggle lyrics scroll (Switch between auto/time scroll and manual)
            - Fine-tune time index (Precisely set time index for any line)

            If currently editing lyrics right click offers override options:
            - Save
            - Cancel

        """

        # If we are synchronizing lyrics activate that window instead
        if self.syn_top_is_active:
            self.sync_time_index_lift()
            return

        menu = tk.Menu(root, tearoff=0)
        menu.post(event.x_root, event.y_root)

        # Add the binding for Select All with Control+A
        # TODO: These aren't working???
        # Tkinter doesn't remove highlighted text when pasting over:
        #  https://stackoverflow.com/a/46636970/6929343
        self.lyrics_score_box.bind("<Control-Key-a>",
                                   self.play_edit_lyrics_select_all)
        self.lyrics_score_box.bind("<Control-Key-A>",
                                   self.play_edit_lyrics_select_all)

        # If lambda isn't used the command is executed as soon as popup
        # menu is displayed, not when option is chosen.
        if self.lyrics_edit_is_active:  # Is user editing lyrics?
            # Cut, Copy, Paste, Delete, Select All can be greyed out and skipped
            self.lyrics_edit_right_click(menu, self.lyrics_score_box)
        elif self.lyrics_train_is_active:  # basic time index training?
            # Cut, Copy, Paste, Delete, Select All can be greyed out and skipped
            self.lyrics_train_right_click(menu)
        else:
            # Normal menus
            menu.add_command(label="Webscrape lyrics", font=(None, MED_FONT),
                             command=lambda: self.play_scrape_new_lyrics())
            menu.add_command(label="Clipboard replace", font=(None, MED_FONT),
                             command=lambda: self.play_clip_paste_lyrics())
            menu.add_command(label="Edit lyrics", font=(None, MED_FONT),
                             command=lambda: self.play_edit_lyrics())
            menu.add_separator()
            menu.add_command(label="Toggle lyrics scroll", font=(None, MED_FONT),
                             command=lambda: self.play_lyrics_toggle_scroll())
            menu.add_command(label="Basic time index", font=(None, MED_FONT),
                             command=lambda: self.play_train_lyrics())
            menu.add_command(label="Fine-tune time index", font=(None, MED_FONT),
                             command=lambda: self.play_sync_time_index())
            menu.add_separator()
            menu.add_command(label="Ignore click", font=(None, MED_FONT),
                             command=lambda: menu.unpost())

        menu.tk_popup(event.x_root, event.y_root)
        # Without lambda executes immediately, without _: invalid # parameters
        menu.bind("<FocusOut>", lambda _: menu.unpost())

    def lyrics_edit_right_click(self, menu, txt):
        """
            Popup menu whilst editing text

            Get selected text: https://tkdocs.com/tutorial/text.html#more
            Copy to clipboard: https://stackoverflow.com/questions/
                               20611523/tkinter-text-widget-unselect-text
            Deactivate item:   https://bytes.com/topic/python/answers/
                               27013-tkinter-disable-menu-items-while-running

            param menu: Menu widget passed from parent
            param txt: Convenient shorthand for self.lyrics_score_box
        """

        # Has text been edited?
        if txt.edit_modified():
            edit_state = tk.NORMAL
            no_edit_state = tk.DISABLED
        else:
            edit_state = tk.DISABLED
            no_edit_state = tk.NORMAL

        # Is text selected? (Allows copy, cut and delete options
        if txt.tag_ranges("sel"):
            sel_state = tk.NORMAL
        else:
            sel_state = tk.DISABLED

        # Is there anything in the clipboard? (almost always)
        try:
            clip_text = txt.clipboard_get()
            if len(clip_text) > 0:
                clip_state = tk.NORMAL
            else:
                clip_state = tk.DISABLED
        except tk.TclError:
            clip_state = tk.DISABLED

        # edited = txt.edit_modified()                    # text modified?
        # select = txt.tag_ranges("sel")                  # something selected?
        # print('edited?:', edited, 'select:', select, "clip:", clip_text)

        menu.add_command(label="Find", command=lambda:
                         self.play_edit_lyrics_done('save'),
                         state=tk.NORMAL, font=(None, MED_FONT))
        # Find needs to link to search field
        menu.add_command(label="Undo", command=lambda:
                         txt.edit_undo(),
                         state=edit_state, font=(None, MED_FONT))
        menu.add_command(label="Redo", command=lambda:
                         txt.edit_redo(),
                         state=edit_state, font=(None, MED_FONT))
        menu.add_separator()
        menu.add_command(label="Cut", command=lambda:
                         txt.event_generate('<Control-x>'),
                         state=sel_state, font=(None, MED_FONT))
        menu.add_command(label="Copy", command=lambda:
                         txt.event_generate('<Control-c>'),
                         state=sel_state, font=(None, MED_FONT))
        menu.add_command(label="Paste", command=lambda:
                         txt.event_generate('<Control-v>'),
                         state=clip_state, font=(None, MED_FONT))
        menu.add_command(label="Delete", command=lambda:
                         txt.event_generate('<Delete>'),
                         state=sel_state, font=(None, MED_FONT))
        menu.add_command(label="Select All", command=lambda:
                         self.play_edit_lyrics_select_all(),  # Only thing that works
                         #self.play_edit_lyrics_select_all(),  # Only thing that works
                         #txt.event_generate('<Control-a>'),  # Doesn't work
                         state=tk.NORMAL, font=(None, MED_FONT))
        menu.add_separator()
        menu.add_command(label="Save lyrics", command=lambda:
                         self.play_edit_lyrics_done('save'),
                         state=edit_state, font=(None, MED_FONT))
        menu.add_command(label="Cancel changes", command=lambda:
                         self.play_edit_lyrics_done('cancel'),
                         state=edit_state, font=(None, MED_FONT))
        # TODO: Create 'quit' option below
        menu.add_command(label="Done", command=lambda:
                         self.play_edit_lyrics_done('cancel'),
                         state=no_edit_state, font=(None, MED_FONT))
        menu.add_separator()
        menu.add_command(label="Ignore click", command=lambda:
                         menu.unpost(), font=(None, MED_FONT))


    def lyrics_train_right_click(self, menu):
        """
            Popup menu whilst basic time index training
            :param menu: Menu widget passed from parent
        """

        # Has time index been modified?
        if self.lyrics_time_list == self.work_time_list:
            edit_state = tk.NORMAL
            no_edit_state = tk.DISABLED
        else:
            edit_state = tk.DISABLED
            no_edit_state = tk.NORMAL

        # Is text selected? (Allows copy, cut and delete options)
        # August 2, 2021 comment out below - it's not used???
        #if txt.tag_ranges("sel"):
        #    sel_state = tk.NORMAL
        #else:
        #    sel_state = tk.DISABLED

        # edited = txt.edit_modified()                    # text modified?
        # select = txt.tag_ranges("sel")                  # something selected?
        # print('edited?:', edited, 'select:', select, "clip:", clip_text)

        menu.add_command(label="Save time index", command=lambda:
                         self.play_train_lyrics_done('save'),
                         state=edit_state, font=(None, MED_FONT))
        menu.add_command(label="Cancel changes", command=lambda:
                         self.play_train_lyrics_done('cancel'),
                         state=edit_state, font=(None, MED_FONT))
        # TODO: Create 'quit' option below
        menu.add_command(label="Done", command=lambda:
                         self.play_train_lyrics_done('cancel'),
                         state=no_edit_state, font=(None, MED_FONT))
        menu.add_separator()
        menu.add_command(label="Ignore click", command=lambda:
                         menu.unpost(), font=(None, MED_FONT))

    def play_scrape_new_lyrics(self):
        """ Trash existing lyrics and get new ones.
            TODO: prompt with one of 8 websites to focus on getting:
                1. Metrolyrics
                2. AZ Lyrics
                3. Lyrics.com
                4. LyricsMode
                5. LetSingIt
                6. Genius
                7. MusixMatch
                8. LyricsPlanet

            TODO: Scrape mega lo biz for LRC files.
                  Modify play_lyrics_from_web()
        """
        if not self.lyrics_pid == 0:
            print('lyrics are already being web scraped. Please wait a second')
            return

        # Give warning box when lyrics exist all will be lost!
        if len(self.lyrics_score) > 10:
            answer = message.AskQuestion(
                self.play_top, thread=self.refresh_play_top,
                title="Lyrics will scraped from web and replaced",
                text="If you have edited these lyrics all changes will be lost!" +
                "\n\nTIP: You can edit lyrics to copy and paste groups of lines.")
            if answer.result != 'yes':
                return

        self.play_clear_lyrics()  # Reset all fields
        if not self.play_top_is_active:
            return

        # print('GET NEW:',self.Artist,self.Album,self.Title)
        # print('web scraping lyrics from internet')
        self.play_lyrics_from_web()  # scrape lyrics from web

        # When music is paused the lyrics never appear on their own
        while self.pp_state is 'Paused' and self.lyrics_scrape_done is False:
            ''' It takes a few seconds to get lyrics from internet '''
            self.play_paint_lyrics("get_new")
            root.after(50)


    def play_clip_paste_lyrics(self):
        """ Delete current song lyrics and insert text from clipboard.
        """
        # Give warning box when lyrics exist all will be lost!
        if len(self.lyrics_score) > 10:
            answer = message.AskQuestion(
                self.play_top, thread=self.refresh_play_top,
                title="Lyrics will pasted from clipboard",
                text="If you edited these lyrics changes will be lost!\n\n" +
                     "TIP: Edit lyrics can copy and paste groups of lines.")
            if answer.result != 'yes':
                return

        command_line_list = ["xclip", "-selection", "clipboard", "-out"]
        pipe = sp.Popen(command_line_list, stdout=sp.PIPE, stderr=sp.PIPE)
        text, err = pipe.communicate()  # This performs .wait() too

        if not pipe.return_code == 0:
            messagebox.showinfo("Copy from clipboard error.",
                                "An error occurred trying to grab text from clipboard.",
                                icon='error', parent=self.play_top)
            return

        if text:
            # Delete existing text box lines
            self.lyrics_score_box.configure(state="normal")
            self.lyrics_score_box.delete("1.0", "end")  # Delete last lyrics
            # Insert lyrics grabbed from clipboard
            for line in text:
                self.lyrics_score_box.insert(tk.END, line)
            self.lyrics_score_box.update()  # Refresh immediately
            self.lyrics_score_box.configure(state="disabled")
            # Save lyrics
            sql.update_lyrics(self.play_make_sql_key(),
                              text, self.lyrics_time_list)
        else:
            # Image is going direct to stdout instead of filename passed?
            # Note `messagebox` is from Tkinter, `message` is from mserve
            messagebox.showinfo("Copy from clipboard error.",
                                "Text should have been in clipboard but not found?",
                                icon='error', parent=self.play_top)
            return

        ''' Insert text into lyrics text box and sql '''
        # size = str(len(text))
        # print('size of text found: '+size)
        # print(text)

    # ==============================================================================
    #
    #       MusicTree Processing - Edit lyrics
    #
    # ==============================================================================

    def play_edit_lyrics(self):
        """ Edit Lyrics was right-clicked. Right click again to Save/Cancel.
            Typical usage:
                A. Copy [chorus] block and paste at next [chorus] tag.
                B. Correct works like "have" to "got" and vice versa.
                C. Remove line break before single comma on its own line.
        """
        if not self.lyrics_pid == 0:
            print('lyrics are being web scraped. Please wait a second.')
            return

        if not self.play_top_is_active or self.syn_top_is_active:
            return

        print('EDIT LYRICS:', self.Artist, self.Album, self.Title)

        self.play_lyrics_remove_highlights()

        # Save current time index because by time editing is finished may be
        # on a different song.
        #self.play_save_time_index()

        # Turn on text editing make insert cursor visible by setting background
        # If too narrow set insert width=4 or more.
        self.lyrics_score_box.configure(state="normal",
                                        insertbackground=self.foreground)
        # Don't reposition to top, keep cursor where it was.
        # self.lyrics_score_box.see("1.0")

        # reset the flag to false. If the user modifies the widget the flag
        # will become True again
        self.lyrics_score_box.edit_modified(False)
        #self.lyrics_score_box.bind("<Control-Key-a>",
        # No difference for Control-Key-a and Control-a See:
        # https://stackoverflow.com/a/66746994/6929343
        self.lyrics_score_box.bind("<Control-a>",
                                   self.play_edit_lyrics_select_all)
        # self.lyrics_score_box.bind("<Control-Key-A>",
        self.lyrics_score_box.bind("<Control-A>",
                                   self.play_edit_lyrics_select_all)
        self.lyrics_score_box.bind("<Control-Key-z>",
                                   self.lyrics_score_box.edit_undo)
        self.lyrics_score_box.bind("<Control-Key-Z>",
                                   self.lyrics_score_box.edit_undo)
        self.lyrics_score_box.bind("<Control-Shift-Key-z>",
                                   self.lyrics_score_box.edit_redo)
        self.lyrics_score_box.bind("<Control-Shift-Key-Z>",
                                   self.lyrics_score_box.edit_redo)

        # Fix Control+C  https://stackoverflow.com/a/64938516/6929343
        self.lyrics_score_box.bind(
            "<Button>", lambda event: self.lyrics_score_box.focus_set())

        self.lyrics_score_box.update()  # Is this necessary? YES
        self.lyrics_edit_is_active = True
        self.lyrics_edit_start_time = time.time()
        self.play_create_lyrics_work_fields()  # sql key, score & time list
        # Refresh title to reflect edit mode is in progress
        self.play_lyrics_rebuild_title()

    def play_create_lyrics_work_fields(self):
        """ Save the sql key, lyrics & time list when entering edit mode.
            Just in case next or previous song is clicked or new playlist.
        """
        self.work_sql_key = self.play_make_sql_key()
        self.work_lyrics_score = self.lyrics_score
        self.work_time_list = self.lyrics_time_list
        self.work_song_path = self.current_song_path
        self.work_song_secs = self.current_song_secs
        self.work_DurationSecs = self.DurationSecs
        self.work_Title = self.Title
        self.work_line_count = self.lyrics_line_count


    def play_edit_lyrics_select_all(self):
        """ Select all text """
        self.lyrics_score_box.tag_add(tk.SEL, "1.0", tk.END)
        self.lyrics_score_box.mark_set(tk.INSERT, "1.0")
        self.lyrics_score_box.see(tk.INSERT)
        # break prevents others from repeating action:
        # https://stackoverflow.com/a/13808423/6929343
        return 'break'


    def play_edit_lyrics_done(self, action):
        """ Edit Lyrics done. action='save' or 'cancel' or 'quit'
            TODO: Bug displays original lyrics when getting confirmation
                  to replace > 80% change in size.
        """
        # Set cursor position in text box
        self.edit_current_cursor = self.lyrics_score_box.index(tk.INSERT)
        print('current_cursor:', self.edit_current_cursor)
        # text.mark_set("insert", "%d.%d" % (line + 1, column + 1))
        self.lyrics_score_box.unbind("<Control-Key-a>")
        self.lyrics_score_box.unbind("<Control-Key-A>")
        self.lyrics_score_box.unbind("<Control-Key-z>")
        self.lyrics_score_box.unbind("<Control-Key-Z>")
        self.lyrics_score_box.unbind("<Control-Key-Shift-Key-z>")
        self.lyrics_score_box.unbind("<Control-Key-Shift-Key-Z>")

        self.lyrics_score_box.configure(state="disabled")
        self.lyrics_edit_is_active = False  # Allow normal read/save ops

        # If cancel bail out now and spare indenting after an "else:"
        if action == 'cancel':
            self.play_init_lyrics()  # We may be on a new song at this point.
            return

        # Rebuild lyrics from textbox
        self.work_lyrics_score = \
            self.lyrics_score_box.get('1.0', tk.END)

        while self.work_lyrics_score.endswith('\n\n'):
            # Drop last blank line which textbox automatically inserts.
            # User may have manually deleted during edit so don't always assume
            self.work_lyrics_score = self.work_lyrics_score[:-1]

        # Convert empty text to None = NULL in SQL
        if len(self.work_lyrics_score) == 0:
            self.work_lyrics_score = None
        # Convert empty time list to None = NULL in SQL
        if self.work_time_list is not None:
            if len(self.work_time_list) == 0:
                self.work_time_list = None

        # Confirm if > 20% of text has been deleted
        percent = float(len(self.work_lyrics_score)) / \
            float(len(self.lyrics_score))

        # Confirm if > 20% of text has been deleted
        if percent < 0.8:
            answer = message.AskQuestion(
                self.play_top, thread=self.refresh_play_top,
                title="More than 20% of text deleted",
                text="A large amount of text has been deleted!\n\n" +
                     "TIP: Deleting all text will web scrape lyrics again.")
            if answer.result != 'yes':
                print('Did not answer yes:', answer.result)
                self.play_init_lyrics()
                # Refresh title to reflect edit mode is in progress
                self.play_lyrics_rebuild_title()
                return

        # Save current text box to library
        sql.update_lyrics(self.work_sql_key,
                          self.work_lyrics_score,
                          self.work_time_list)

        # Hold variables reset by self.play_init_lyrics()
        hold_work_sql_key = self.work_sql_key
        hold_lyrics_old_scroll = self.lyrics_old_scroll
        hold_lyrics_auto_scroll = self.lyrics_auto_scroll
        hold_lyrics_time_scroll = self.lyrics_time_scroll
        self.play_init_lyrics()  # We may be on a new song at this point.

        # If we are still on same song reset variables to hold values
        if hold_work_sql_key == self.work_sql_key:
            # Honor previous scrolling setting: auto/time/manual
            self.lyrics_old_scroll = hold_lyrics_old_scroll
            self.lyrics_auto_scroll = hold_lyrics_auto_scroll
            self.lyrics_time_scroll = hold_lyrics_time_scroll

            # Position cursor to where it was when editing finished
            self.lyrics_score_box.configure(state="normal")
            self.lyrics_score_box.mark_set("insert",
                                           self.edit_current_cursor)
            self.lyrics_score_box.update()  # Refresh immediately
            self.lyrics_score_box.configure(state="disabled")

        # Refresh title to reflect edit mode is in progress
        self.play_lyrics_rebuild_title()

    # ==============================================================================
    #
    #       MusicTree class - Fine-tune time index ("sync_")
    #
    # ==============================================================================

    def play_sync_time_index(self, sbar_width=12):
        """ Fine-tune time index (Synchronize Time Index to Lyrics)

            WARNING: work_time_list, new_time_list and lyrics_time_list are
                     used differently.

            Startup check to ensure at least 80% of lines already synchronized.
            If not display splash screen with basic sync instructions.

            Create master_frame covering play_top frame. master_frame contains:
                frame1: information labels, non-stretchable
                frame2: time index treeview, stretchable
                frame3: control buttons, non-stretchable

            Pause music if playing
            Set default checkbox for the lyrics line currently playing           

            TODO:

            FIX BROKEN TOOLTIPS !!!
            When clicking "Sample All" the new tooltips do not display on hover and
                the old tooltip remains with focus forever it needs to be closed at
                same time as grid forget command.
            tt.close(widget) when closing window

            Buttons Tag group, Copy
            When clicking Tag, prompt for first line and last line to index
            When clicking Begin, prompt for pre-tag lead in and mount:
                play button, prev line, next line, pause button
        """

        if not self.lyrics_pid == 0:
            print('lyrics are being web scraped. Please wait a second.')
            return

        # If already active, move window to foreground.
        if self.syn_top_is_active:
            self.sync_time_index_lift()  # Raise window focus to top
            print('play_sync_time_index(): Should not be here a second time.')
            return  # Don't want to start again

        # 80% threshold required. Instructions window mounted if not reached.
        self.play_create_lyrics_work_fields()  # sql key, lyrics & time list
        if not self.play_sync_startup_check():
            return

        # Set flags for child processes running
        self.syn_top_is_active = False          # Synchronizing Time Indices?
        self.sync_ffplay_is_running = False     # Currently, playing and syncing?
        self.sync_paused_music = False          # Important this is False now
        self.sync_changed_score = False         # For warning messages
        self.sync_changed_lyrics = True         # Lyrics score has been changed

        self.sync_ffplay_pid = 0                # ffplay linux process ID
        self.sync_ffplay_sink = ""              # pulseaudio sink number
        if self.pp_state is "Playing":          # Is music playing?
            self.pp_toggle()                    # Pause to synchronize lyrics
            self.sync_paused_music = True       # So we can resume play later

        ''' Create window '''
        self.syn_top = tk.Toplevel()
        self.syn_top.minsize(g.WIN_MIN_WIDTH, g.WIN_MIN_HEIGHT)
        self.syn_top_is_active = True
        # Refresh title to reflect edit mode is in progress
        self.play_lyrics_rebuild_title()

        ''' Set program icon in taskbar '''
        # Not sure why other windows don't need below?
        img.taskbar_icon(self.syn_top, 64, 'white', 'lightskyblue', 'black')

        # self.sync_start = time.time()
        '''
            Traceback (most recent call last):
              File "/usr/lib/python2.7/lib-tk/Tkinter.py", line 1540, in __call__
                return self.func(*args)
              File "./mserve", line 5058, in <lambda>
                self.play_sync_time_index(), font=(None, MED_FONT))
              File "./mserve", line 5300, in play_sync_time_index
                self.sync_start = time.time()
            UnboundLocalError: local variable 'time' referenced before assignment
        '''

        ''' Place Window top-left of play list window '''
        geometry = self.play_top.winfo_geometry()
        self.syn_top.geometry(geometry)
        self.syn_top.title("Fine-tune time index - mserve")
        self.syn_top.configure(background=self.background)
        self.syn_top.columnconfigure(0, weight=1)
        self.syn_top.rowconfigure(1, weight=1)

        ''' frame1 - Song information '''
        frame1 = tk.Frame(self.syn_top, background=self.background,
                          borderwidth=0)
        frame1.grid(row=0, column=0, sticky=tk.EW)
        frame1.grid_columnconfigure(0, weight=1)
        frame1.grid_columnconfigure(1, weight=1)
        frame1.grid_columnconfigure(2, weight=1)

        ''' Song name and Duration Seconds '''
        # foreground=self.foreground, \
        tk.Label(frame1, text="Title: " + self.work_Title,
                 font=(None, MON_FONTSIZE), padx=10) \
            .grid(row=0, column=0, sticky=tk.W)
        tk.Label(frame1, text="Total seconds: " + str(self.work_DurationSecs),
                 font=(None, MON_FONTSIZE), padx=10) \
            .grid(row=0, column=1, sticky=tk.W)

        self.label_line_count = tk.StringVar()
        self.label_line_count.set("Line count: " + str(self.work_line_count))
        tk.Label(frame1, textvariable=self.label_line_count,
                 font=(None, MON_FONTSIZE), padx=10) \
            .grid(row=0, column=2, sticky=tk.W)

        ''' frame2 - Treeview Listbox'''
        frame2 = tk.Frame(self.syn_top, background=self.background,
                          borderwidth=BTN_BRD_WID, relief=tk.RIDGE)
        tk.Grid.rowconfigure(frame2, 1, weight=1)
        tk.Grid.columnconfigure(frame2, 0, weight=1)
        frame2.grid_columnconfigure(0, weight=1)
        frame2.grid_rowconfigure(1, weight=1)
        frame2.grid(row=1, column=0, sticky=tk.NSEW)

        ''' Treeview List Box, Columns and Headings 
            color tips from chron_tree
            TODO: We have to manually specify width and height???
        '''
        width = int(geometry.split('x')[0])
        width = width - 680
        if width < 200:
            width = 200
        #height = geometry.split('x')[1]
        #height = int(height.split('+')[0])
        row_height = int(MON_FONTSIZE * 2.2)
        # rows = (height - 120) / row_height

        # From: https://stackoverflow.com/a/43834987/6929343
        style = ttk.Style(frame2)
        style.configure("syn.Treeview", background=self.background,
                        fieldbackground=self.background, foreground=self.foreground)

        self.syn_tree = CheckboxTreeview(frame2,
                                         columns=("new", "lyrics", "old_dur", "new_dur"),
                                         selectmode="none", show=('tree', 'headings',))
        self.syn_tree.configure(style="syn.Treeview")

        self.syn_tree.column("#0", width=200, anchor='w', stretch=tk.NO)
        self.syn_tree.heading("#0", text="Time index")
        self.syn_tree.column("new", width=150, stretch=tk.NO)
        self.syn_tree.heading("new", text="New Time")
        self.syn_tree.column("lyrics", width=width, stretch=tk.YES)
        self.syn_tree.heading("lyrics", text="Lyrics")
        self.syn_tree.column("old_dur", width=150, stretch=tk.NO)
        self.syn_tree.heading("old_dur", text="Duration")
        self.syn_tree.column("new_dur", width=150, stretch=tk.NO)
        self.syn_tree.heading("new_dur", text="New Dur.")

        self.syn_tree.grid(row=1, column=0, sticky=tk.NSEW)

        ''' Treeview select item - custom select processing '''
        # self.syn_tree.bind('<ButtonRelease-1>', self.sync_select)

        ''' Create images for checked, unchecked and tristate '''
        # Don't use self.checkboxes list as GC destroys others with that name
        self.check2 = img.make_checkboxes(row_height - 6, self.foreground,
                                          self.background, 'deepskyblue')
        self.syn_tree.tag_configure("unchecked", image=self.check2[0])
        self.syn_tree.tag_configure("tristate", image=self.check2[1])
        self.syn_tree.tag_configure("checked", image=self.check2[2])

        ''' Create Treeview item list '''
        self.sync_create_treeview_list()

        ''' sync lyrics Treeview Scrollbars '''
        # Create a vertical scrollbar linked to the frame.
        v_scroll = tk.Scrollbar(frame2, orient=tk.VERTICAL, width=sbar_width,
                                command=self.syn_tree.yview)
        v_scroll.grid(row=1, column=1, sticky=tk.NS)
        self.syn_tree.configure(yscrollcommand=v_scroll.set)

        ''' sync lyrics treeview Colors '''
        self.syn_tree.tag_configure('normal', background=self.background,
                                    foreground=self.foreground)
        self.syn_tree.tag_configure('sync_sel', background=self.foreground,
                                    foreground=self.background)

        ''' Synchronize lyrics / Treeview Buttons 
            To hide use:    self.syn_top_buttons.grid_remove()
            To restore use: self.syn_top_buttons.grid()
        '''
        self.syn_top_buttons = tk.Frame(self.syn_top, relief=tk.GROOVE,
                                        background=self.background, borderwidth=BTN_BRD_WID)
        self.syn_top_buttons.grid(row=2, column=0, padx=2, pady=2, sticky=tk.W)

        ''' ??? Close Button - Cancels changes '''
        close = tk.Button(self.syn_top_buttons, text="??? Close",
                          width=BTN_WID2 - 6, command=self.sync_close)
        close.grid(row=0, column=0, padx=2, sticky=tk.W)
        self.tt.add_tip(close, "Close this fine-tune index window.", anchor="nw")
        # Disable for now because Child process like "self.sync_begin()" should
        # be trapping ESCAPE
        # self.syn_top.bind("<Escape>", self.sync_close)
        self.syn_top.protocol("WM_DELETE_WINDOW", self.sync_close)

        ''' ???  Begin Button - Synchronize selected lines '''
        begin = tk.Button(self.syn_top_buttons, text="???  Begin sync",
                          width=BTN_WID2 - 4, command=self.sync_begin)
        begin.grid(row=0, column=1, padx=2)
        self.tt.add_tip(
            begin, "First check boxes for first and last line.\n" +
            "Then click this button to synchronize.",
            anchor="nw")

        ''' ???? Delete - ???? (u+1f612) - Delete all '''
        delete = tk.Button(self.syn_top_buttons, text="???? Delete all",
                           width=BTN_WID2 - 4, command=self.sync_delete_all)
        delete.grid(row=0, column=2, padx=2)
        self.tt.add_tip(
            delete, "When time indices are hopelessly wrong,\n" +
            "click this button to delete them all.", anchor="nw")

        ''' ????  Sample all - Sample all show library '''
        sample = tk.Button(self.syn_top_buttons, text="????  Sample all",
                           width=BTN_WID2 - 4, command=self.sync_sample_all)
        sample.grid(row=0, column=3, padx=2)
        self.tt.add_tip(
            sample, "Click to sample the first second of every line.",
            anchor="nw")

        ''' - Merge lines - Merge two lines together '''
        merge = tk.Button(self.syn_top_buttons, text="- Merge lines",
                          width=BTN_WID2 - 4, command=self.sync_merge_lines)
        merge.grid(row=0, column=4, padx=2)
        self.tt.add_tip(
            merge, "First check two or more lines. Then\n" +
            "click this button to merge together.", anchor="nw")

        ''' + Insert line - Insert line line eg [chorus] or [bridge] '''
        insert = tk.Button(self.syn_top_buttons, text="+ Insert line",
                           width=BTN_WID - 4, command=self.sync_insert_line)
        insert.grid(row=0, column=5, padx=2)
        self.tt.add_tip(
            insert, "First check line to insert before. Then\n" +
            "click this button to insert a new line.", anchor="ne")

        ''' ????  Save - Save lyrics (may be merged) and time indices '''
        save = tk.Button(self.syn_top_buttons, text="????  Save",
                         width=BTN_WID2 - 4, command=self.sync_save_changes)
        save.grid(row=0, column=6, padx=2)
        self.tt.add_tip(
            save, "Save time indices and close\n" +
            "this fine-tune index window.", anchor="ne")

        ''' Create & remove child buttons for sync_begin '''
        self.syn_top_buttons.grid_remove()  # Remove syn_top buttons grid
        self.sync_begin_buttons = tk.Frame(self.syn_top, relief=tk.GROOVE,
                                           background=self.background, borderwidth=BTN_BRD_WID)
        # pad x & pad y below have no effect???
        self.sync_begin_buttons.grid(row=2, column=0, padx=2, pady=2,
                                     sticky=tk.SW)

        ''' "Sync in progress" label '''
        tk.Label(self.sync_begin_buttons, text="Sync in progress...",
                 font=(None, MON_FONTSIZE), padx=10) \
            .grid(row=0, column=0, sticky=tk.W)
        ''' Done Button - Saves work and returns to parent '''
        begin_done = tk.Button(self.sync_begin_buttons, text="Done",
                               width=BTN_WID2 - 6, command=self.sync_begin_done)
        begin_done.grid(row=0, column=1, padx=2, sticky=tk.W)
        self.tt.add_tip(
            begin_done, "Click this button to skip\n" +
            "synchronizing remaining lines.", anchor="nw")

        ''' "Rewind 5 seconds" Button - Synchronize selected lines '''
        begin_rewind = tk.Button(self.sync_begin_buttons, text="Rewind 5 seconds",
                                 width=BTN_WID2 + 2, command=self.sync_begin_rewind)
        begin_rewind.grid(row=0, column=2, padx=2)
        self.tt.add_tip(
            begin_rewind, "Click this button to stop play,\n" +
            "go back 5 seconds and resume play.", anchor="nw")

        ''' Restore main button grid '''
        self.sync_begin_buttons.grid_remove()   # Remove sync_begin buttons grid
        self.syn_top_buttons.grid()             # Restore syn_top buttons grid

        ''' Create & remove child buttons for sync_sample '''
        self.syn_top_buttons.grid_remove()      # Remove syn_top buttons grid
        self.sync_sample_buttons = tk.Frame(self.syn_top, relief=tk.GROOVE,
                                            background=self.background,
                                            borderwidth=BTN_BRD_WID)
        # pad x & pad y below have no effect???
        self.sync_sample_buttons.grid(row=2, column=0, padx=2, pady=2,
                                      sticky=tk.SW)

        ''' "Sample in progress" label '''
        tk.Label(self.sync_sample_buttons, text="Sample all in progress...",
                 font=(None, MON_FONTSIZE), padx=10) \
            .grid(row=0, column=0, sticky=tk.W)
        ''' Done Button - Saves work and returns to parent '''
        sample_done = tk.Button(self.sync_sample_buttons, text="Done",
                                width=BTN_WID2 - 6, command=self.sync_sample_done)
        sample_done.grid(row=0, column=1, padx=2, sticky=tk.W)
        self.tt.add_tip(
            sample_done, "Click this button to skip\n" +
            "sampling remaining lines.", anchor="nw")
        ''' Pause/Play Button - Toggles state '''
        self.sync_sample_pp_state = 'Playing'
        self.sync_sample_pp_button = \
            tk.Button(self.sync_sample_buttons, text=self.pp_pause_text,
                      width=BTN_WID2 - 4, command=self.sync_sample_toggle_play)
        self.sync_sample_pp_button.grid(row=0, column=2, padx=2, sticky=tk.W)
        ''' TODO: Tooltip remains ghosted when moving off button focus '''
        self.tt.add_tip(
            self.sync_sample_pp_button, "Click this button to toggle\n" +
            "pause / playing of music.", anchor="nw")

        ''' "Rewind 5 seconds" Button '''
        sample_rewind = tk.Button(self.sync_sample_buttons, text="Rewind 5 seconds",
                                  width=BTN_WID2 + 2, command=self.sync_sample_rewind)
        sample_rewind.grid(row=0, column=3, padx=2)
        self.tt.add_tip(
            sample_rewind, "Click this button to stop play,\n" +
            "go back 5 seconds and resume play.", anchor="nw")

        ''' Restore main button grid '''
        self.sync_sample_buttons.grid_remove()  # Remove sync_sample buttons
        self.syn_top_buttons.grid()             # Restore syn_top buttons grid

        ''' Setup label & buttons sizes and styles '''
        # Apply color codes to buttons - See play_ffmpeg_artwork()
        self.syn_top.configure(bg=self.background)

        toolkit.config_all_labels(self.syn_top, fg=self.foreground,
                                  bg=self.background)
        self.syn_top_buttons.configure(bg=self.background)
        self.sync_begin_buttons.configure(bg=self.background)
        self.sync_sample_buttons.configure(bg=self.background)
        toolkit.config_all_buttons(self.syn_top, fg=self.background,
                                   bg=self.foreground)
        self.syn_top.update_idletasks()

        ''' Set default checkbox for currently playing line '''
        self.sync_default_set = 0
        found = 0
        for i, start_time in enumerate(self.work_time_list):
            if start_time > self.work_song_secs:
                # We found greater entry so target is line before
                found = i
                break

        # print('i:', i, 'found:', found, 'time:', time,
        #      'self.work_song_secs:', self.work_song_secs)
        if found > 1:
            # Mark the checkbox of currently playing line
            tags = self.syn_tree.item(str(found))['tags']
            if "unchecked" in tags:
                tags.remove("unchecked")
                tags.append("checked")
                self.syn_tree.item(str(found), tags=tags)
                self.syn_tree.see(str(found))
                self.sync_default_set = found

        self.syn_top.update()

    def sync_create_treeview_list(self):
        """ Called from two places """
        start_time = 0.0
        duration = 0.0
        last_time = 0.0
        time_override_count = 0  # >= 1 negative durations?
        self.new_time_list = []  # As time list is edited these
        self.new_durations_list = []  # lists override synchronizing
        last_ndx = len(self.work_time_list) - 1
        for line_ndx, line in enumerate(self.work_lyrics_score.split('\n')):
            line = line.strip('\r')  # Microsoft Windows
            # time_override = False  # Adjusted negative durations?

            ''' Calculate line start time index and duration '''
            if line_ndx <= last_ndx:
                start_time = self.work_time_list[line_ndx]
                duration = self.DurationSecs - self.work_time_list[line_ndx]
            if line_ndx + 1 <= last_ndx:
                duration = self.work_time_list[line_ndx + 1] - \
                           self.work_time_list[line_ndx]

            # Override if this line number > total lines indexed
            if line_ndx > last_ndx:
                # print('lyrics score line_ndx:', line_ndx, \
                #       '> tine index last_ndx:', last_ndx)
                start_time = float(self.DurationSecs)
                duration = 0.0
            else:
                # New values default to original
                self.new_time_list.append(start_time)
                self.new_durations_list.append(duration)

            if last_time > start_time:
                time_override_count += 1
                # time_override = True
            last_time = start_time

            ''' Pad digit spaces to line up time index and duration evenly '''
            # time = '%9s' % time    # Regular space doesn't line up evenly
            ftime = '%.1f' % start_time
            fduration = '%.1f' % duration
            ftime = self.play_padded_number(ftime, 8)
            fduration = self.play_padded_number(fduration, 7, prefix="")
            # FUTURE if time_override: insert with new duration else:
            self.syn_tree.insert('', 'end', iid=str(line_ndx + 1), text=ftime,
                                 values=("", line, fduration, ""),
                                 tags=("normal",))

        if len(self.work_time_list) != len(self.new_time_list):
            print('PROGRAM ERROR. len(self.work_time_list):',
                  len(self.work_time_list), 'len(self.new_time_list):',
                  len(self.new_time_list))

        if time_override_count > 0:
            messagebox.showinfo(
                title="Time indices are NOT sequential!", icon="error",
                message="Negative time durations need to be fixed.",
                parent=self.syn_top)

    def sync_begin(self):
        """ Play music and synchronize time for checked treeview lines.
        
            Fill in all blank check boxes between first and last checked.
            If nothing was checked error is displayed, and we return.
            Set start time 4 seconds before first checked.
            Set end time to start of line following last checked.

            Hide syn_top buttons using:    self.syn_top_buttons.grid_remove()
            Restore syn_top buttons using: self.syn_top_buttons.grid()

            Buttons and functions for self.sync_begin_buttons.grid():
                Done - allows early exit - self.sync_begin_done()
                Rewind 5 - rewinds 5 seconds - self.sync_begin_rewind()

            TODO: We are still getting message syncing Janine by Trooper:

count: 31 first: 18 last: 19
Failed to get sink input information: No such entity
Failed to get sink input information: No such entity
Failed to get sink input information: No such entity
Failed to get sink input information: No such entity

            May have to append " 2>/dev/null" but that will also hide bad
            programming using "pactl" external command
        """
        if self.sync_ffplay_is_running:
            print('self.sync_ffplay_is_running:')
            return  # Already playing

        # Fill first and last checked boxes. At least one line must be checked.
        self.sync_first, self.sync_last = self.sync_fill_checkboxes()
        if self.sync_first is None:  # Error message already
            return  # displayed so return.

        if self.sync_last + 1 - self.sync_first > 3:
            text = "It could take a while to play more than three lines."
            if self.sync_three_abort(text):
                return  # Warn > 3 checkboxes

        self.syn_top_buttons.grid_remove()  # Hide syn_top buttons
        self.sync_begin_buttons.grid()  # Display our buttons
        self.sync_curr_highlight = 0  # When changes move bar
        self.sync_ffplay_is_running = True  # We are now playing
        self.sync_start_ffplay()  # Sets variables;
        # QUESTION? Is below calling poll_tips?
        self.sync_watch_ffplay()  # self.old_sinks
        self.sync_clean_ffplay()  # self.active_sink
        self.sync_ffplay_is_running = False  # No longer playing
        if not self.syn_top_is_active:
            return  # syn_top is destroyed
        self.sync_begin_buttons.grid_remove()  # Remove our buttons
        self.syn_top_buttons.grid()  # Restore syn_top buttons
        return

    def sync_begin_done(self):
        """ End the sync_begin() function
        """
        self.sync_duration = 0  # Force exit

    def sync_begin_rewind(self):
        """ Rewind 5 seconds.
            Temporarily hide buttons so, they can't be clicked for 2 seconds
            Ramp down our currently playing volume only (don't ramp up others)
            Kill currently playing
            Rewind 4 seconds from current spot, calculate new duration
            Restart play and ramp up only our volume
        """
        self.sync_begin_buttons.grid_remove()  # Remove our buttons
        self.sync_clean_ffplay(others=False)  # Turn down our volume

        if not self.syn_top_is_active or \
                not ext.check_pid_running(self.sync_ffplay_pid):
            # Window closed or song finished playing already
            return

        # Pause the music so, it can't end while we ramp up next ffplay sink
        ext.stop_pid_running(self.sync_ffplay_pid)  # Pause the music

        # Calculate new start index and duration
        old_pid = self.sync_ffplay_pid  # The PID to kill later
        curr_start = self.sync_start + self.sync_elapsed - 5
        if curr_start > self.sync_start:
            # New start time later than previous start time, good to override
            start_diff = curr_start - self.sync_start
            self.sync_start = curr_start
            self.sync_duration -= start_diff

        # curr_duration = self.sync_duration - 

        # Start playing: others=Don't turn down other applications,
        #                calculate=use existing self.sync_xxx values
        self.sync_start_ffplay(others=False, calculate=False)
        ext.kill_pid_running(old_pid)  # Kill the last ffplay
        self.sync_begin_buttons.grid()  # Display our buttons

    def sync_start_ffplay(self, others=True, calculate=True):
        """ Start ffplay and get our Linux PID and Pulseaudio Input Sink #
            others = Turn down volume of other applications
            calculate = calculate self.sync_start & self.sync_duration


            TODO: self.sync_start, self.sync_first and self.sync_last may be
                  greater that len(self.new_time_list)

Traceback (most recent call last):
  File "/usr/lib/python2.7/lib-tk/Tkinter.py", line 1540, in __call__
    return self.func(*args)
  File "/home/rick/python/mserve.py", line 5835, in sync_begin
    self.sync_start_ffplay()                        # Sets variables;
  File "/home/rick/python/mserve.py", line 5908, in sync_start_ffplay
    self.sync_start + 2.0
IndexError: list index out of range
        """

        # Give 2.5-second playing countdown before line to sync
        if calculate:
            self.sync_start = self.new_time_list[self.sync_first - 1] - 2.5
            if self.sync_start < 0.0:
                self.sync_start = 0.0

        # Duration after last checkbox line + 2 seconds.
        # TODO: work_line_count (based on lyrics) can be greater than time_list
        #sync_start = time.time()
        #print('\n sync_start_ffplay() count:', self.work_line_count,
        #      'first:', self.sync_first, 'last:', self.sync_last)
        if calculate:
            if self.sync_last + 1 < self.work_line_count:
                # Grab start time of line after last line to set duration+2 secs
                self.sync_duration = self.new_time_list[self.sync_last] - \
                                     self.sync_start + 2.0
            else:
                self.sync_duration = self.work_DurationSecs - self.sync_start

        # Launch ffplay at start second for duration seconds
        extra_opt = ' -ss ' + str(self.sync_start) + \
                    ' -t ' + str(int(self.sync_duration))
        self.sync_ffplay_pid, self.sync_ffplay_sink = \
            start_ffplay(self.work_song_path, TMP_CURR_SAMPLE, extra_opt)
        self.sync_music_start_time = time.time()  # Music is playing now
        set_volume(self.sync_ffplay_sink, 0)  # Turn off volume
        ext.stop_pid_running(self.sync_ffplay_pid)  # Pause the music

        ''' During 1st second reduce other sound applications '''
        # What if sink is for something like phone ringing or timer?
        # Note if music paused play_top_sink will also be processed.
        self.old_sinks = sink_master()  # build list of tuples
        ext.continue_pid_running(self.sync_ffplay_pid)  # Resume the music

        # To get 1-10 you need 1,11 range!  Our volume turns up 10% each step
        for i in range(1, 11):  # 10 steps
            if not self.syn_top_is_active:
                return
            s_time = set_volume(self.sync_ffplay_sink, int(i * 10))
            for app_sink, app_vol, app_name in self.old_sinks:
                if not others:
                    break  # Only doing ourselves
                if app_sink == self.sync_ffplay_sink:
                    continue  # Skip our sink!
                percent = int(app_vol - int(app_vol * i / 10))  # Reduce by 10%
                app_time = set_volume(app_sink, percent)  # Volume down 10%
                s_time += app_time  # Total all job times
            if s_time < .07:
                root.after(int((.07 - s_time) * 1000))  # Sleep .07 per step

        #sync_end = time.time()
        #print('sync_start_ffplay() start: %.2f' % sync_start,
        #      'end: %.2f' % sync_end,
        #      'diff: %.2f' % (sync_end - sync_start))
        #print('self.sync_music_start_time: %.2f' % self.sync_music_start_time,
        #      'start diff: %.2f' % (self.sync_music_start_time - sync_start),
        #      'end diff: %.2f' % (sync_end - self.sync_music_start_time))
        # Final verdict: We are burning up .75 seconds before watch starts

    def sync_watch_ffplay(self):
        """
            Synchronize each line as it is played
            Allow left click to select line and set new time index
            With no overrides, lines are auto highlighted based on time index
            Exit loop when there is 1 second left to play
        """
        self.sync_elapsed = 0.0
        self.sync_curr_highlight = ""
        self.syn_tree.bind("<ButtonRelease-1>", self.sync_select)
        # self.printed=False                    # DEBUGGING stuff
        # Run until ffplay ends prematurely, or 1 second before it ends.
        while ext.check_pid_running(self.sync_ffplay_pid):
            if not self.syn_top_is_active:
                return                          # Window closed?
            self.sync_elapsed = time.time() - self.sync_music_start_time
            #            if self.sync_elapsed + 2.6 > self.sync_duration:
            if self.sync_elapsed + 1.0 > self.sync_duration:
                # Leave 1 second early so there is time to ramp down/up volume
                break
            self.sync_check_highlight()         # Check highlight pos.
            self.refresh_play_top()

        # Restore treeview button settings
        if not self.syn_top_is_active:
            return  # Window closed?
        self.syn_tree.unbind("<ButtonRelease-1>")  # Mouse left-click

        # Clear highlights and checkboxes
        self.sync_remove_all_highlights()
        # TODO: We want to keep checkboxes if adjust button added
        self.sync_remove_all_checkboxes()
        self.syn_top.update_idletasks()

    def sync_clean_ffplay(self, others=True):
        """ Over last second restore volume on other sound applications

            Following lines need global variables devised from speed tests:
                for i in range(1,11):                       # 10 steps
                if app_time > .025:
            sleep = int((.07 - s_time)*1000)             # .07 between steps
            if sleep < 20:
        """
        # Only restore active_sinks, using self.old_sinks volume
        # self.syn_top_active maybe False but, we still have to restore volume
        active_sinks = sink_master()  # list of sinks now

        #print('\n sync_clean_ffplay() sink:', self.sync_ffplay_sink,
        #      'duration: %.2f' % self.sync_duration,
        #      'elapsed: %.2f' % self.sync_elapsed,
        #      'diff: %.2f' % (self.sync_duration - self.sync_elapsed), '\n')
        #loop_start = time.time()
        # time_used = time.time() - loop_start
        err = False
        err_count = 0
        lost_ms = 0  # sleep ms lost

        for i in range(1, 11):  # 10 steps of 10%
            s_time = 0.0  # s_time = system time to turn our sink's volume down
            for app_sink, app_vol, app_name in active_sinks:
                # Is this our currently playing sink?
                if app_sink == self.sync_ffplay_sink:  # This is our sink
                    percent = 100 - (i * 10)    # Turn down volume 10%
                    if err_count < 1:           # If no errors yet
                        app_time, err = set_volume(self.sync_ffplay_sink,
                                                   percent, return_err=True)
                    else:
                        err_count += 1          # Would be another error
                        app_time = 0
                    s_time += app_time          # Total all system times
                    if app_time > .025:
                        print('sync_clean_ffplay(self): app_time too large:',
                              app_time, 'our sink:', app_sink, 'i', i)
                    if err:
                        err_count += 1

                # Turn up sink for old applications if still active
                for old_sink, old_vol, old_name in self.old_sinks:
                    if others is False:
                        break                   # Only doing ourselves
                    if old_sink == self.sync_ffplay_sink:
                        continue                # We are on our own sink already adjusted
                    if old_sink == app_sink:
                        percent = int(old_vol * i / 10)  # Old volume up 10%
                        app_time = set_volume(old_sink, percent)
                        s_time += app_time      # Total all system times
                        if app_time > .025:
                            print('sync_clean_ffplay(self): app_time too large:',
                                  app_time, 'sink:', app_sink, 'i', i)
                    # Grab next o sink (old sink) for comparison
                # Grab next a sink (active sink)

            #time_used = time.time() - loop_start
            sleep = int((.06 - s_time) * 1000)  # .06 between steps
            if sleep < 1:
                #print('%.2f' % time_used, 'step number: %2d' % i,
                #      's time: %.2f' % s_time, 'cannot sleep < 1 ms:', sleep,
                #      'lost_ms:', lost_ms)
                # Lag if commands is like sleeping anyway.
                lost_ms += sleep  # negative total
            else:
                # Positive sleep value: either sleep or apply to lost sleep
                #print('%.2f' % time_used, 'step number: %2d' % i,
                #      's time: %.2f' % s_time, 'sleep milliseconds :', sleep,
                #      'lost_ms:', lost_ms)
                ext.t_init('root.after using: ' + str(sleep) + ' milliseconds')
                # Do we have lost ms to make up for?
                if lost_ms < 0:
                    new_sleep = sleep + lost_ms  # Recalculate sleep
                    # print('new_sleep:', new_sleep, 'lost_ms:', lost_ms)
                    if new_sleep > 0:  # Sleep still positive?
                        root.after(new_sleep)  # Sleep recalculated
                        lost_ms = 0  # Reset lost sleep to 0
                    else:
                        lost_ms += sleep  # Regain some lost sleep
                    # print('new_sleep:', new_sleep, 'new lost_ms:', lost_ms)
                else:
                    root.after(sleep)  # Sleep original
                ext.t_end('no_print')

        self.sync_ffplay_sink = ""  # Forget our sink

    def sync_remove_all_highlights(self):
        """ Remove everything highlighted """
        for item in self.syn_tree.get_children():  # For all items
            self.syn_tree.selection_remove(item)  # Remove selection
            tags = self.syn_tree.item(item)['tags']  # Remove line highlight
            if "sync_sel" in tags:
                tags.remove("sync_sel")
                tags.append("normal")
                self.syn_tree.item(item, tags=tags)

    def sync_remove_all_checkboxes(self):
        """ Remove all checkboxes """
        for line in self.syn_tree.tag_has("checked"):
            tags = self.syn_tree.item(line)['tags']
            tags.remove("checked")
            tags.append("unchecked")
            self.syn_tree.item(line, tags=tags)

    # noinspection PyUnusedLocal
    def sync_select(self, event=None):
        """ Process line clicked in treeview while music playing
            Set new start time and recalculate duration of previous line and
            this line. 
        """
        clicked_line = int(self.syn_tree.focus())  # Line that was clicked
        if clicked_line < self.sync_first or \
                clicked_line > self.sync_last:  # Between first and last
            print('You can only click line between first and last checkbox.')
            return  # Ignore everything else

        if clicked_line < self.sync_curr_highlight:
            # Clicking previous line? Reset last changes back to original
            values = self.syn_tree.item(str(clicked_line))['values']
            # values[0] = new_time, values[1]=line text, values[2]=old duration
            # values[3] = new_duration
            if values[3] != "":
                # A non-blank time was formatted so, we overrode previously
                # TODO: Recall create treeview routine
                self.syn_tree.delete(*self.syn_tree.get_children())
                self.sync_create_treeview_list()
                print('Start time changes (edits) removed.')
            else:
                print('You can only click previous line to cancel time edits.')
            return

        elif clicked_line == self.sync_curr_highlight:
            # Clicking same line? We start later and extend previous time
            print('Start time reduced.')
            pass

        elif clicked_line != self.sync_curr_highlight + 1:
            # Clicking next line? Quicken line start time and extend duration
            print('You can only click one line ahead to make it start sooner.')
            return

        ''' Remove everything highlighted '''
        self.sync_remove_all_highlights()

        ''' Highlight current line clicked '''
        tags = self.syn_tree.item(self.syn_tree.focus())['tags']
        if "normal" in tags:
            tags.remove("normal")
            tags.append("sync_sel")  # Apply line highlight
            self.syn_tree.item(self.syn_tree.focus(), tags=tags)

        ''' Update time and duration for line clicked. See merge_lines()'''
        # Calculate new time
        new_time = self.sync_start + self.sync_elapsed
        values = self.syn_tree.item(str(clicked_line))['values']
        # values[0] = new_time, values[1]=line text, values[2]=old duration
        # values[3] = new_duration
        if clicked_line + 1 <= len(self.new_time_list):
            new_duration = self.new_time_list[clicked_line] - new_time
        else:
            new_duration = self.work_DurationSecs - new_time
        values[0] = self.sync_formatted_secs(new_time, 7)
        values[3] = self.sync_formatted_secs(new_duration, 7)
        # Here's the kicker, clicked line maybe beyond len(time_list[])
        # Insert additional indices as necessary.
        # TODO:
        self.new_time_list[clicked_line - 1] = new_time
        self.new_durations_list[clicked_line - 1] = new_duration
        self.syn_tree.item(str(clicked_line), values=values)

        ''' Update duration for previous line clicked '''
        previous_line = clicked_line - 1
        if previous_line > 0:
            values = self.syn_tree.item(str(previous_line))['values']
            new_duration = self.new_time_list[clicked_line - 1] - \
                self.new_time_list[previous_line - 1]
            values[3] = self.sync_formatted_secs(new_duration, 7)
            self.new_durations_list[previous_line - 1] = new_duration
            self.syn_tree.item(str(previous_line), values=values)

        ''' Wrap up '''
        # print('tree values:',values)
        # print('new_time:', new_time)
        # Apply current selection
        self.syn_tree.selection_toggle(self.syn_tree.focus())
        # print('Selected:', self.syn_tree.selection())

        # Apply current selection
        self.syn_tree.selection_toggle(self.syn_tree.focus())
        # print('Selected:', self.syn_tree.selection())
        self.sync_curr_highlight = clicked_line

    def sync_formatted_secs(self, secs, length, prefix=""):
        f_secs = '%.1f' % secs
        return self.play_padded_number(f_secs, length, prefix)

    def sync_check_highlight(self):
        """ As music plays, check if we need to reposition highlight bar.
            Called every .05 second.
        """

        """ calculate line that should be highlighted """
        new_time = self.sync_start + self.sync_elapsed  # Where are we in song?
        # if self.printed == False:
        #    print('new_time:', new_time, 'self.sync_start:', self.sync_start, \
        #          'self.sync_elapsed:', self.sync_elapsed)

        calculated_highlight = self.work_line_count  # Default last line
        # TODO: Eliminate loop to save resources. Use self.next_time variable
        for i, entry in enumerate(self.new_time_list):
            # if self.printed == False:
            #    last_ndx = len(self.new_time_list) - 1
            #    print('for loop @ i:', i, 'entry:', entry, 'last_ndx', last_ndx)
            if entry > new_time:  # Find next highest time
                calculated_highlight = i  # Current line is before
                break
            # If no times found, we are on the last line.
        if calculated_highlight == 0:
            calculated_highlight = 1
        # self.printed=True                              # DEBUGGING stuff

        ''' If correct line already highlighted, return now '''
        if self.sync_curr_highlight == calculated_highlight:
            return
        self.syn_tree.see(str(calculated_highlight))

        # print('new_time:', new_time, 'self.sync_start:', self.sync_start,
        #      'self.sync_elapsed:', self.sync_elapsed)

        ''' Update tags to highlight current line '''
        self.sync_remove_all_highlights()

        self.sync_curr_highlight = calculated_highlight  # Set new current line
        tags = self.syn_tree.item(str(self.sync_curr_highlight))['tags']
        tags.remove("normal")  # Remove line normal
        tags.append("sync_sel")  # Apply line highlight
        self.syn_tree.item(str(self.sync_curr_highlight), tags=tags)

    def sync_fill_checkboxes(self):
        """ Fill in all blank check boxes between first and last checked.
            At least one must be checked or return False.
        """
        # Find the first and last checked boxes.
        first_checked = self.work_line_count
        last_checked = 0
        for line in self.syn_tree.tag_has("checked"):
            i_line = int(line)
            if i_line < first_checked:
                first_checked = i_line
            if i_line > last_checked:
                last_checked = i_line

        # At least one line must be checked
        if last_checked == 0:
            messagebox.showinfo(title="Checkbox error", icon="error",
                                message="Check at least one box.",
                                parent=self.syn_top)
            return None, None

        # Mark all lines between first checked and last checked.
        for line in range(first_checked, last_checked):
            tags = self.syn_tree.item(line)['tags']
            if "unchecked" in tags:
                tags.remove("unchecked")
                tags.append("checked")
                self.syn_tree.item(line, tags=tags)

        self.syn_top.update_idletasks()  # Process pending events
        self.syn_top.update()  # Update checkboxes on screen
        return first_checked, last_checked

    def sync_delete_all(self):
        """ Time Indices hopelessly out of sync so Delete them.
        """
        if self.sync_ffplay_is_running:
            return  # Already playing?

        answer = message.AskQuestion(
            self.syn_top, thread=self.refresh_play_top,
            title="Delete all time indices",
            text="All times will be permanently erased!!!\n\n" +
                 'To cancel time changes, click "Close" button instead.' +
                 "\n\nAfter deleting, Time Index window will be closed.")
        # print('answer.result:', answer.result)
        if answer.result != 'yes':
            return

        self.work_time_list = []
        self.new_time_list = []
        # Reset variables to reflect no time indices
        self.play_lyrics_remove_highlights()
        # This is awkward because we aren't using work fields but, it's not
        # possible for next song to be playing anyway.
        self.lyrics_prev_line = 0
        self.lyrics_curr_line = 0
        self.lyrics_time_scroll = False
        self.lyrics_auto_scroll = True
        self.lyrics_old_scroll = None  # Normal scrolling
        print('no lyrics time index')
        # Save SQL row
        if len(self.work_lyrics_score) == 0:
            self.work_lyrics_score = None
        sql.update_lyrics(self.work_sql_key, self.work_lyrics_score,
                          self.work_time_list)
        sql.hist_delete_time_index(self.work_sql_key)
        self.sync_close()

    def sync_sample_all(self):
        """ Play music 1 second for each line.
            Mount new buttons like sync_begin has sync_begin_done,
                 sync_begin_rewind
            TODO: button to instantly adjust last line just played. Tagging
                  and coming back after entire song finishes takes too much
                  time and effort.
        
        """
        if self.sync_ffplay_is_running:
            return                              # Already playing

        # Check all boxes
        for line in range(1, self.work_line_count):
            tags = self.syn_tree.item(str(line))['tags']
            if "unchecked" in tags:
                tags.remove("unchecked")
                tags.append("checked")
                self.syn_tree.item(str(line), tags=tags)

        # Setup first and last checked boxes. At least one line must be checked.
        self.sync_first, self.sync_last = self.sync_fill_checkboxes()
        if not self.sync_first:  # Error message already
            return  # displayed so return.

        self.sync_ffplay_is_running = True      # We are now playing
        # TODO: May be paused from last sample all that was cancelled
        self.sync_sample_pp_state = 'Playing'   # Initial pause/play
        self.syn_top_buttons.grid_remove()      # Hide syn_top buttons
        self.sync_sample_buttons.grid()         # Display our buttons
        self.sync_start_ffplay()                # Sets variables;
        self.sync_watch_ffplay2()               # self.old_sinks
        self.sync_clean_ffplay()                # self.active_sink
        self.sync_ffplay_is_running = False     # No longer playing
        self.sync_sample_buttons.grid_remove()  # Hide our buttons
        self.syn_top_buttons.grid()             # Restore main buttons

    def sync_sample_done(self):
        """ Save changes and quit sync_sample_all() function
        """
        self.sync_ffplay_pid = 0                # Force exit
        self.sync_remove_all_checkboxes()       # Remove highlight done
        self.sync_ffplay_is_running = False     # No longer playing "Playing"
        # If clicked "Done" while music was paused, reset for next time
        if self.sync_sample_pp_state is 'Paused':
            self.sync_sample_pp_state = 'Playing'
            self.sync_sample_pp_button['text'] = self.pp_pause_text

    def sync_sample_toggle_play(self):
        """ Toggle pause/play during Fine-Tune Sample All
        """
        if self.sync_sample_pp_state is 'Playing':
            self.sync_sample_pp_state = 'Paused'
            self.sync_sample_pp_button['text'] = self.pp_play_text
            ext.stop_pid_running(self.sync_ffplay_pid)  # Pause the music
        else:
            self.sync_sample_pp_state = 'Playing'
            self.sync_sample_pp_button['text'] = self.pp_pause_text
            # Resume(unpause) the music
            ext.continue_pid_running(self.sync_ffplay_pid)
        self.syn_top.update_idletasks()  # Process pending events
        self.syn_top.update()

    def sync_sample_adjust(self):
        """ Pause and manually adjust time index
        """
        self.sync_duration = 0  # Force exit

    def sync_sample_rewind(self):
        """ Rewind 5 seconds.
            Temporarily hide buttons so, they can't be clicked for 2 seconds
            Ramp down our currently playing volume only (don't ramp up others)
            Kill currently playing
            Rewind 4 seconds from current spot, calculate new duration
            Restart play and ramp up only our volume
        """
        self.sync_begin_buttons.grid_remove()   # Remove our buttons
        self.sync_clean_ffplay(others=False)    # Turn down our volume

        if not self.syn_top_is_active or \
                not ext.check_pid_running(self.sync_ffplay_pid):
            # Window closed or song finished playing already
            return

        # Pause the music so, it can't end while we ramp up next ffplay sink
        ext.stop_pid_running(self.sync_ffplay_pid)  # Pause the music

        # Calculate new start index and duration
        old_pid = self.sync_ffplay_pid          # The PID to kill later
        curr_start = self.sync_start + self.sync_elapsed - 5
        if curr_start > self.sync_start:
            # New star time later than previous start time, good to override
            start_diff = curr_start - self.sync_start
            self.sync_start = curr_start
            self.sync_duration -= start_diff

        # curr_duration = self.sync_duration - 

        # Start playing: others=Don't turn down other applications,
        #                calculate=use existing self.sync_xxx values
        self.sync_start_ffplay(others=False, calculate=False)
        ext.kill_pid_running(old_pid)           # Kill the last ffplay
        self.sync_begin_buttons.grid()          # Display our buttons

    def sync_watch_ffplay2(self):
        """
            Play line for 1 second then skip to next.
            When we first start up music already playing for length of song.
            Allow two seconds first time before killing.
            After that, kill each line after 1 second of play
        """
        self.sync_elapsed = 0.0
        self.sync_curr_highlight = ""

        # self.printed=False                             # DEBUGGING stuff
        # First time ffplay with 2-second delay for ramping up.
        play_seconds = 2.0
        line_no = 1
        while ext.check_pid_running(self.sync_ffplay_pid):
            if not self.syn_top_is_active:
                return  # Window closed?
            if self.sync_sample_pp_state is 'Paused':
                # TODO: Sounds choppy with no ramp up/ramp down pp_toggle
                self.sync_music_start_time = time.time()
            else:
                self.sync_elapsed = time.time() - self.sync_music_start_time
                if self.sync_elapsed > play_seconds:
                    ext.kill_pid_running(self.sync_ffplay_pid)
                    # self.sync_ffplay_pid = 0            # Insurance policy
                    # Uncheck line just played via CheckboxTreeview()
                    # noinspection PyProtectedMember
                    self.syn_tree._uncheck_ancestor(str(line_no))
                    line_no += 1
                    if line_no > len(self.new_time_list):
                        break
                    self.syn_tree.see(str(line_no))
                    self.sync_restart_ffplay(line_no)

            self.sync_check_highlight()         # Check highlight pos.
            self.refresh_play_top()

            # Remaining loops ffplay with 1-second delay.
            play_seconds = 1.0

        # Clear highlights
        if not self.syn_top_is_active:
            return  # Window closed?
        self.sync_remove_all_highlights()
        # Make first manually checked box visible (if any)
        for item in self.syn_tree.get_children():
            tags = self.syn_tree.item(str(item))['tags']
            if "checked" in tags:
                self.syn_tree.see(item)
                break

    def sync_restart_ffplay(self, line_no):
        """ Restart playing at line. Previous line already stopped.  """
        self.sync_start = self.new_time_list[line_no - 1]
        if self.sync_start < 0.0:
            self.sync_start = 0.0

        # Launch ffplay at start second for 2 seconds but, it is killed after 1
        # print('Relaunch ffplay at:', self.sync_start, 'line:', line_no, \
        #       'time_list:', self.new_time_list[line_no -1])
        extra_opt = ' -ss ' + str(self.sync_start) + ' -t 2'
        self.sync_ffplay_pid, self.sync_ffplay_sink = \
            start_ffplay(self.work_song_path, TMP_CURR_SAMPLE, extra_opt)
        set_volume(self.sync_ffplay_sink, 100)  # TODO: Why is volume
        # at 0% after first line so, we have to force 100% volume now?

        self.sync_music_start_time = time.time()  # Music is playing now
        # print('playing: ffplay "' + self.work_song_path +'"', extra_opt)
        # print('starting line:', line_no, 'time:', str(self.sync_start), \
        #      'PID:', self.sync_ffplay_pid, 'Sink:', self.sync_ffplay_sink)

    def sync_merge_lines(self):
        """ Merge two or more lines together.
            Error if no lines checked.
            Warning if one line checked it will be merged with next.
            Warning if more than 3 lines checked.

            TODO: After merging lines and clicking 'Save' the
                  lyrics weren't saved to text box or to file.

        """
        # Get first and last line numbers being processed.
        # Take care to subtract 1 when referencing corresponding list index.
        first, last = self.sync_fill_checkboxes()  # Verify checkbox(es)
        if first is None:
            return  # Error message already
        if first == last:
            answer = message.AskQuestion(
                self.syn_top, thread=self.refresh_play_top,
                title="Merge lines together",
                text="At least two lines must be selected to merge together." +
                     "\n\nThis will merge checked line and the line after it.")
            if answer.result == 'yes':
                last = first + 1
            else:
                return
        if last + 1 - first > 3:
            text = "Merging more than three lines can make new line too long."
            if self.sync_three_abort(text):
                return  # Warn > 3 checkboxes

        ''' Make first line duration longer Similar to sync_select() '''
        values = self.syn_tree.item(str(first))['values']
        # values[0] = new_time, values[1]=line text, values[2]=old duration
        # values[3] = new_duration
        if last + 1 <= len(self.new_time_list):
            # last as index is 1 past last line.
            new_duration = self.new_time_list[last] - self.new_time_list[first - 1]
        elif last <= len(self.new_time_list):
            new_duration = self.work_DurationSecs - self.new_time_list[last - 1]
        else:
            new_duration = 0.0
        values[3] = self.sync_formatted_secs(new_duration, 7)
        # print('first-1:', first-1, 'durations:', len(self.new_durations_list))
        self.new_durations_list[first - 1] = new_duration
        self.syn_tree.item(str(first), values=values)

        ''' Merge checked lyrics line(s) into first checked line's lyrics. 

            Building new treeview when finished changing lyrics will lose all
            our work in progress new time and new duration columns. This will
            give illusion work has been saved when it really hasn't been. So
            we will manually massage treeview line by line instead.
        '''
        tree_count = len(self.syn_tree.get_children())  # IMPORTANT it is here!
        for i in range(first, last):
            # print('Merging line:', i+1, 'to line:', i)
            # item = self.syn_tree.item(str(i))
            # print('treeview item:', item)
            # trg_item = self.syn_tree.item(str(i+1))
            # print('target item:', trg_item)
            ''' Update treeview lyrics line '''
            trg_values = self.syn_tree.item(
                str(i + 1))['values']  # Get line values to delete
            self.syn_tree.delete(str(i + 1))  # Delete from treeview
            self.sync_delete_lyric_line(i + 1)  # Delete from lyrics score
            values[1] = values[1] + trg_values[1]  # Merge lyrics to line
            self.syn_tree.item(str(first),
                               values=values)  # Update lyrics line

            ''' Remove index in new_time_list[] and new_durations_list[] '''
            # Deleting index shifts others down so always deleting index after
            # first which in zero's based index is 'first' variable.
            if first < len(self.new_time_list):
                # del self.work_time_list[first]    # Need original before edit
                del self.new_time_list[first]
                del self.new_durations_list[first]
            else:
                print('i:', i, '>= len(self.new_time_list:',
                      len(self.new_time_list))
                print('i:', i, '>= len(self.new_durations_list:',
                      len(self.new_durations_list))
            # print('new values:',values)

        ''' Renumber treeview items' Ids to fill in holes of deleted Ids
            We already have holes made from deleted treeview rows during merge
        '''
        renumber_count = last - first
        ''' Attempt to fix blank line inserted after merged line '''
        for i in range(first + 1, tree_count):
            # for i in range(first, tree_count + 1):
            trg_item = i + renumber_count
            # Don't go past end of tree
            if trg_item > tree_count:
                print('reached end of tree with trg_item:', trg_item)
                continue
            # print('renumbering iid:', trg_item, 'to:', i)
            item = self.syn_tree.item(str(trg_item))  # Save item to move
            self.syn_tree.delete(str(trg_item))  # Delete item to move
            self.syn_tree.insert('', 'end', iid=str(i), text=item['text'],
                                 values=item['values'], tags=item['tags'])
            # Red rider Neruda - Power song has "Image:" dictionary key empty
            # print('renumbered from:', trg_item, 'to:', i, 'item:', item)

        ''' Remove all checkboxes as they won't repeat this '''
        self.sync_remove_all_checkboxes()

        ''' Update new line count in label field '''
        # Line count =

        ''' Update lyrics textbox '''
        self.sync_changed_score = True  # Lyrics score has been changed
        # This tells the Save button to perform:
        # self.lyrics_score_box = self.work_lyrics_score

    def sync_delete_lyric_line(self, line_no):
        """ Delete one line from lyrics score.

            Examples 1 & 2 return a table, 3 returns a string:
                >>> my_string="Line 1\nLine 2\nLine 3\nLine4\n"
                >>> my_string.split('\n')[0:2]
                ['Line 1', 'Line 2']
                >>> my_string.split('\n')[3:4]
                ['Line4']
                >>> my_string.split('\n')[3]
                'Line4'

        """
        # Extract chunks 1 & 2 before and after line
        if line_no > 1:
            chunk1 = self.work_lyrics_score.split('\n')[0:line_no - 1]
        else:
            chunk1 = self.work_lyrics_score.split('\n')[0:]
        if line_no < self.work_line_count:
            chunk2 = self.work_lyrics_score.split('\n')[line_no:
                                                        self.work_line_count]
        else:
            chunk2 = self.work_lyrics_score.split('\n')[-1]
        # Merge chunks 1 & 2 for new lyrics score
        self.work_lyrics_score = ""
        for line in chunk1:
            self.work_lyrics_score += line + '\n'
        for line in chunk2:
            self.work_lyrics_score += line + '\n'
        self.work_line_count -= 1  # Decrement line count
        self.label_line_count.set("Line count: " + str(self.work_line_count))
        self.sync_changed_score = True  # For warning messages

    def sync_three_abort(self, msg):
        """ Give chance to abort - allows one-liner in caller. """
        answer = message.AskQuestion(self.syn_top,
                                     thread=self.refresh_play_top,
                                     title="More than three lines checked",
                                     text=msg)
        return answer.result != 'yes'

    def sync_insert_line(self):
        """ Insert line like [chorus], [bridge], [solo], "song lyrics line"
            Option to insert "Line(s) just copied" has added advantage of
            increasing time indices for all following lyric lines automatically.
        """
        first, last = self.sync_fill_checkboxes()  # Verify checkbox(es)
        if first is None:
            return  # Error message already

        if first != last:
            messagebox.showinfo(
                title="Check only one box", icon="error",
                message="Check the line to insert before.",
                parent=self.syn_top)
            return

        self.sync_remove_all_checkboxes()

    def sync_save_changes(self):
        """ Save changes to time indices and possibly lyrics score too.
            Lyrics score changes by 'Merge lines' or 'Insert Tag' buttons.
        """
        if self.sync_changed_score is False and \
                self.work_time_list == self.new_time_list:
            answer = message.AskQuestion(
                self.syn_top, thread=self.refresh_play_top,
                title="Lyrics have NOT been fine-tuned",
                text="Saving time indices makes no sense.")
            if answer.result != 'yes':
                return

        if len(self.work_lyrics_score) == 0:
            print('PROGRAM ERROR: There are no lyrics score to save!')
            self.work_lyrics_score = None  # Don't want to save ""
            return

        ''' write synchronized lyrics changes to SQL database '''
        sql.update_lyrics(self.work_sql_key, self.work_lyrics_score,
                          self.new_time_list)
        # TODO: Future save lyrics in memory after support for editing is added
        if self.sync_changed_score:
            # Update lyrics score textbox score_box
            self.play_lyrics_populate_score_box()
            self.sync_changed_score = False  # To avoid close warning
            self.lyrics_score = self.work_lyrics_score
            """
    def play_lyrics_from_library(self):
        ''' turn on auto scrolling, it can be overridden from saved steps or
            if left-clicking on lyrics to set lyrics line to seconds link.
            self.lyrics_score, self.lyrics_time_list = sql.get_lyrics(key)
        '''
        self.lyrics_score_box.configure(state="normal")
        for line in self.lyrics_score:
            self.lyrics_score_box.insert(tk.END, line)
        self.lyrics_score_box.update()       # Is this necessary? CONFIRMED YES
        self.lyrics_score_box.configure(state="disabled")

        end = self.lyrics_score_box.index('end')  # returns line.column
        self.lyrics_line_count = int(end.split('.')[0]) - 1
        self.work_line_count = self.lyrics_line_count # FUDGE FOR Time being...
            """
        # self.work_time_list = self.new_time_list        # To avoid close warning
        self.new_time_list = self.work_time_list  # To avoid close warning
        self.sync_close()  # Close window & exit
        self.lyrics_time_list = self.work_time_list  # Update list in memory

    def sync_time_index_lift(self):
        self.syn_top.focus_force()  # Grab back window focus
        self.syn_top.lift()  # Raise stacking order

    def play_sync_startup_check(self):
        """ Check if fine-tuning time indices is appropriate.
            Use 80% threshold. Give advice on how to manually click each
            lyrics score line in song as it is being sung by the singer.
        """
        time_count = len(self.work_time_list)
        if float(self.work_line_count) > 0.0:
            percent = float(time_count) / float(self.work_line_count)
        else:
            percent = 0.0

        # Problem, with Afterlife by Avenged Sevenfold
        # return True

        if percent > .8:
            return True

        ''' Instructions to obtain 80% synchronization with basic steps '''
        quote = ("\n" +

                 "Fine-tuning lyrics time indices can only be done after basic\n" +
                 "synchronization is completed for at least 80% of lines.\n\n\t" +

                 "Number of lines in lyrics score: " + str(self.work_line_count) + "\n\t" +
                 "Number of lines with time index: " + str(time_count) + "\n\n" +

                 "To perform basic lyrics synchronization:\n\n\t" +

                 "1. Play song.\n\t" +
                 "2. If no lyrics exist they are scraped from the internet.\n\t" +
                 "3. As singing starts for each line in song, left click on it.\n\t" +
                 "4. If you click ahead too quickly, click the playing line.\n\t" +
                 "5. If you fall behind on clicking, click the correct line.\n\t" +
                 "6. When song ends, click 'Previous' button to replay it.\n\t" +
                 "7. Now as song plays, lines will highlight automatically.\n\t" +
                 "8. Mistakes can be fixed by left-clicking at correct time.\n\t" +
                 "9. If lines still need fine-tuning then use this function.\n\n" +

                 'NOTE: If lyrics contain errors, fix them before using this function.')

        message.ShowInfo(self.play_top, text=quote, align='left',
                         title="Fine-tune time index instructions - mserve")
        return False

    # noinspection PyUnusedLocal
    def sync_close(self, *args):  # *args required for lambda
        """ Close Synchronize Time Index to Lyrics window
            Modeled after sample_close() but with confirmation if changes made.
        """
        if self.sync_changed_score or \
                self.work_time_list != self.new_time_list:
            # What if they merge two lines and insert 1 Tag? then count same!
            # TODO: Ensure merge & insert set self.sync_changed_score flag
            print('self.sync_changed_score:', self.sync_changed_score)
            print('len(self.work_time_list):', len(self.work_time_list))
            print('len(self.new_time_list):', len(self.new_time_list))
            print('differences:', list(set(self.work_time_list) -
                                       set(self.new_time_list)))
            answer = message.AskQuestion(self.syn_top,
                                         thread=self.refresh_play_top,
                                         title="Times have been fine-tuned",
                                         text="Changes will be lost!")
            if answer.result != 'yes':
                return
            # When you answer 'no' during restart from lib_top_close program
            # still ends and changes are lost. So we need to find if 'Restart'
            # is calling us and provide "Last chance to save" option.

        self.sync_ffplay_is_running = False     # Playing and syncing?
        self.syn_top_is_active = False          # Lyrics Time Index window open?
        self.tt.close(self.syn_top_buttons)     # Delete tooltips
        self.tt.close(self.sync_begin_buttons)
        self.tt.close(self.sync_sample_buttons)
        if not self.sync_ffplay_sink == "":
            # Restore volume to other applications
            self.sync_clean_ffplay()            # Note this takes a second!
        self.sync_ffplay_pid = 0                # ffplay linux process ID
        self.sync_ffplay_sink = ""              # pulseaudio sink number
        self.syn_top.destroy()                  # Close the window
        if self.sync_paused_music:              # Did we pause music player?
            self.pp_toggle()                    # Resume playing
        if os.path.isfile(TMP_CURR_SAMPLE):
            os.remove(TMP_CURR_SAMPLE)          # Clean up /tmp directory

        # Refresh title to reflect edit mode is in progress
        self.play_lyrics_rebuild_title()

    # ==============================================================================
    #
    #       MusicTree class - Smaller functions and buttons
    #
    # ==============================================================================

    def play_ffmpeg_artwork(self, path):
        """
            Get artwork for currently playing song.
        """

        self.play_current_song_art, self.play_resized_art = ffmpeg_artwork(
            path, self.art_width, self.art_height)
        if self.play_current_song_art is None:
            self.play_no_art()  # Use "No Artwork" image

        # Get background color of x=3, y=3 for filling corners when rotating
        # which "squares the circle".
        self.play_frm_bg = self.play_resized_art.getpixel((3, 3))
        hex_background = img.rgb_to_hex(self.play_frm_bg)
        dec_foreground = img.contrasting_rgb_color(self.play_frm_bg)
        hex_foreground = img.rgb_to_hex(dec_foreground)
        self.background = hex_background  # Globalization for
        self.foreground = hex_foreground  # vu_meter functions

        # Apply color codes to all play_top labels and buttons - See syn_top.
        self.play_frm.configure(bg=self.background)
        toolkit.config_all_labels(self.play_top, fg=self.foreground,
                                  bg=self.background)
        self.play_btn.configure(bg=self.background)
        toolkit.config_all_buttons(self.play_top, fg=self.background,
                                   bg=self.foreground)

        # Apply color code to canvas rounded button and text
        #self.lyrics_panel_scroll.update_colors(hex_foreground, hex_background)
        self.lyrics_panel_scroll_a_m.update_colors(hex_foreground, hex_background)
        self.lyrics_panel_scroll_t_m.update_colors(hex_foreground, hex_background)
        self.lyrics_panel_scroll_m_a.update_colors(hex_foreground, hex_background)
        self.lyrics_panel_scroll_m_t.update_colors(hex_foreground, hex_background)
        self.lyrics_panel_hamburger.update_colors(hex_foreground, hex_background)

        # Apply color code to Lyrics
        self.play_F3.config(bg=hex_background,
                            highlightbackground=hex_foreground)
        self.lyrics_score_box.config(bg=hex_background, fg=hex_foreground,
                                     highlightbackground=hex_foreground)
        self.lyrics_score_box.tag_config('highlight', background=hex_foreground,
                                         foreground=hex_background)

        # List all widgets in lyrics panel
        #toolkit.list_widgets(self.play_F3_panel)

        self.play_top.update_idletasks()

        self.play_rotated_value = 0  # Set art rotation (spinning) degrees
        self.play_art_slide_count = 0  # Set art slide count
        self.play_art_fade_count = 0  # Set art fade in count

    def real_path(self, ndx):
        """ WARNING: Called from multiple places
            Convert /(NoArtist)/(No Album)/song.m4a to:
                    /song.m4a
            /Artist/Album/song.m4a stays the same
        """
        rpath = self.song_list[ndx]
        # Strip out /(No Artist) and /(No Album) strings added earlier
        rpath = rpath.replace(os.sep + NO_ARTIST_STR, '', 1)
        rpath = rpath.replace(os.sep + NO_ALBUM_STR, '', 1)
        return rpath

    def play_shuffle(self):
        """ Convert selections to list, shuffle, convert back to tuple
            Get confirmation because this cannot be undone. 'yes'
        """
        dialog = message.AskQuestion(
            self.play_top, thread=self.refresh_play_top,
            title="Shuffle song order confirmation",
            text="This will permanently change playlist song order!")
        if dialog.result != 'yes':
            return

        sql.hist_add_shuffle('remove', 'shuffle', self.saved_selections)
        Id = self.saved_selections[self.ndx]  # Save current song name
        L = list(self.saved_selections)  # convert tkinter tuple to list
        shuffle(L)  # randomize list
        self.ndx = L.index(Id)  # restore old index
        self.saved_selections = tuple(L)  # convert list back into tuple
        self.play_chron_create()  # Rebuild with new sort order
        sql.hist_add_shuffle('edit', 'shuffle', self.saved_selections)

    def play_remove(self, iid):
        """ Song has been unchecked. Remove from sorted playlist.
            Convert selections to list, remove index, convert back to tuple
        """
        # Is option to remove from currently playing list turned on?
        if not LIBRARY_UNSELECT_REMOVE_PLAYING:
            return
        if len(self.saved_selections) == 0:
            return

        # Possible if nothing is playing and new library was loaded?
        if self.ndx > len(self.saved_selections) - 1:
            self.ndx = 0
            print('play_remove(): Unplanned resetting self.ndx = 0')

        curr_play_id = self.saved_selections[self.ndx]  # Get current song ID
        L = list(self.saved_selections)  # convert tkinter tuple to list
        # noinspection PyBroadException
        try:
            remove_ndx = L.index(iid)  # Is it in self.saved_selections?
        except:
            print('play_remove(): Trying to remove song not in playlist yet')
            print('Report this condition. Further programming may be required')
            return  # A song not inserted yet!

        curr_play_ndx = L.index(curr_play_id)  # should be equal to self.ndx
        if curr_play_ndx != self.ndx:
            print('play_remove(): curr_play_ndx != self.ndx')
            print('               curr_play_ndx:', curr_play_ndx)
            print('                                self.ndx:', self.ndx)
            curr_play_ndx = self.ndx

        # If tagged as currently playing, remove it.
        tags = self.lib_tree.item(iid)['tags']
        if "play_sel" in tags:
            tags.remove("play_sel")
            self.lib_tree.item(iid, tags=tags)

        # Blank out Play No. in treeview selected column
        self.lib_tree.set(iid, "Selected", "")

        if remove_ndx == curr_play_ndx:
            # TODO: If song currently playing start playing next song instead.
            #       May 15, 2021 - This is broken, song stays in music player
            #       but ffplay is killed.
            if self.play_top_is_active:  # Play window open?
                self.song_set_ndx('next')  # Start playing next song, ndx + 1
                self.ndx = L.index(iid)  # restore old index

        elif remove_ndx < curr_play_ndx:
            self.ndx -= 1  # As it is greater safe to sub 1.
            self.last_started = self.ndx  # For fast clicking 'Next'

        L.remove(iid)
        self.saved_selections = tuple(L)  # convert list back into tuple
        self.play_song_count = len(self.saved_selections)
        if self.play_top_is_active:  # Play window open?
            self.play_chron_create()  # Rebuild without removed song

    def play_insert(self, iid):
        """ Song has been checked. Insert it into sorted playlist.

            Convert selections to list, insert index, convert back to tuple
                LIBRARY_SELECT_INSERT_PLAY_HERE = True
                LIBRARY_SELECT_INSERT_PLAY_NEXT = False
                LIBRARY_SELECT_INSERT_PLAY_RANDOM = False
                LIBRARY_SELECT_INSERT_PLAY_ORDER = False

            If an entire album or artist is inserted as anything but RANDOM
            then a new function to randomize those songs just inserted should
            be created.

            Only ??? is appearing in select column for newly inserted item
            Existing items do not have their ??? updated (incremented)
        """

        if not self.manually_checked:
            return  # Used for self.reverse/self.toggle

        if not LIBRARY_SELECT_INSERT_PLAY_HERE:
            print("LIBRARY_SELECT_INSERT_PLAY_HERE must be true")
            return

        # Possible if nothing is playing and new library was loaded?
        if self.ndx > len(self.saved_selections) - 1:
            self.ndx = 0
            print('play_insert(): Unplanned resetting self.ndx = 0')

        # print ('Inserting song iid:',iid, 'at:',self.ndx)
        curr_play_id = self.saved_selections[self.ndx]  # Get current song ID
        L = list(self.saved_selections)  # convert tkinter tuple to list
        L[self.ndx:self.ndx] = [iid]  # Insert song new ID here
        self.saved_selections = tuple(L)  # convert list back into tuple
        self.play_song_count = len(self.saved_selections)

        # Remove currently playing red tag
        tags = self.lib_tree.item(curr_play_id)['tags']
        if "play_sel" in tags:
            tags.remove("play_sel")
            self.lib_tree.item(curr_play_id, tags=tags)

        # Set treeview selection number
        number_digits = len(str(self.play_song_count))
        number_str = self.play_padded_number(self.ndx + 1, number_digits)
        self.lib_tree.set(iid, "Selected", number_str)

        if self.play_top_is_active:  # Play window open?
            self.last_started = self.ndx  # For fast clicking 'Next'
            self.song_set_ndx(self.ndx)  # Start playing next song, ndx + 1
            # Remove red highlighting 'play_sel' of old song 'red'
            # If tagged as currently playing, remove it.
            self.play_chron_create()  # Rebuild with new song

    def kill_song(self):
        """ WARNING: Called from multiple places """
        # When paused music at 50%, even though ffplay closes need to
        # set volume to 100% because next load of ffplay inherits setting.
        self.play_100()
        self.play_top_sink = ""

        # If no internet web scraping process could be running for entire song
        if self.lyrics_pid is not 0:
            ext.kill_pid_running(self.lyrics_pid)
            self.lyrics_pid = 0
        self.lyrics_pid = 0

        if not self.play_top_pid == 0:
            # If music playing then kill the process ID
            ext.kill_pid_running(self.play_top_pid)
            self.play_top_pid = 0

    def play_100(self):

        #        print("self.play_top_sink:", self.play_top_sink)
        if self.play_top_sink is not "":
            os.popen('pactl set-sink-input-volume ' +
                     self.play_top_sink + ' 100%') \
                .read().strip().splitlines()

    # noinspection PyUnusedLocal
    def play_close(self, *args):
        # TODO: last_selections aren't being saved. When clicking play again
        #       shuffle order and last song index are lost.

        if self.play_hockey_active:
            self.play_restore_firefox()

        self.play_top_is_active = False
        ext.kill_pid_running(self.vu_meter_pid)

        # Last known window position for playlist, saved to SQL
        last_playlist_geom = monitor.get_window_geom_string(
            self.play_top, leave_visible=False)
        monitor.save_window_geom('playlist', last_playlist_geom)

        root.update()
        root.after(50)  # Give events time to close down
        self.wrap_up_song()  # kill song and collapse parent(s) if necessary
        #        os.remove(TMP_CURR_SONG)           # Clean up /tmp directory
        self.restore_buttons()  # Restore Library buttons to default

        self.play_top.destroy()
        #self.play_top = None  #Nonetype error, try reassigning and destroy first

    # ==============================================================================
    #
    #       Sample middle 10 seconds (of highlighted song in popup menu)
    #
    # ==============================================================================

    def sample_middle(self, Id):
        """
            Sample middle 10 seconds of a song. Turn down other applications
            when starting and restore other application when ending.
        """

        ''' Are we already playing middle clip? '''
        if self.sam_top_is_active:
            self.sam_top.focus_force()  # Get focus
            self.sam_top.lift()  # Raise in stacking order
            root.update()
            return  # Don't want to start playing again

        ''' Are we synchronizing lyrics? It has control of music player '''
        if self.syn_top_is_active:
            self.sync_time_index_lift()
            return

        ''' Build full song path from song_list[] '''
        list_index = int(Id)
        path = self.real_path(list_index)
        self.sam_top_pid = 0  # ffplay Process ID
        self.sam_top_sink = ""  # Pulse audio sink number

        ''' Get metadata using ffprobe '''
        self.play_metadata(path)
        middle_secs = str(int(self.DurationSecs / 2))

        ''' Create window '''
        self.sam_top = tk.Toplevel()
        self.sam_top.minsize(g.WIN_MIN_WIDTH, g.WIN_MIN_HEIGHT)
        self.sam_top_is_active = True
        self.sam_paused_music = False

        if self.pp_state is "Playing":  # Is music playing?
            self.pp_toggle()  # Pause to play sample
            self.sam_paused_music = True  # We will resume play later

        ''' Place Window top-left of parent window with PANEL_HGT padding '''
        xy = (self.lib_top.winfo_x() + PANEL_HGT,
              self.lib_top.winfo_y() + PANEL_HGT)
        self.sam_top.minsize(width=BTN_WID * 10, height=PANEL_HGT * 4)
        self.sam_top.geometry('+%d+%d' % (xy[0], xy[1]))
        self.sam_top.title("Playing middle 10 seconds - mserve")
        self.sam_top.configure(background="Gray")
        self.sam_top.columnconfigure(0, weight=1)
        self.sam_top.rowconfigure(0, weight=1)

        ''' Create master frame '''
        sam_frm = tk.Frame(self.sam_top, borderwidth=BTN_BRD_WID, relief=tk.RIDGE)
        sam_frm.grid(sticky=tk.NSEW)

        ''' Artwork image spanning 7 rows '''
        sample_art = img.make_image("Sample")
        sample_resized_art = sample_art.resize(
            (self.art_width, self.art_height), Image.ANTIALIAS)
        sample_display_art = ImageTk.PhotoImage(sample_resized_art)
        sample_art_label = tk.Label(sam_frm, image=sample_display_art,
                                    font=(None, MON_FONTSIZE))
        sample_art_label.grid(row=0, rowspan=7, column=0, sticky=tk.W)

        ''' Artist, Album, Song '''
        #        self.current_song_artist = tk.StringVar()
        tk.Label(sam_frm, text="Artist: " + self.Artist,
                 font=(None, MON_FONTSIZE)).grid(row=0, column=1, sticky=tk.W)
        # Truncate self.Album to 25 characters plus ...
        tk.Label(sam_frm, text="Album: " + self.Album,
                 font=(None, MON_FONTSIZE)).grid(row=1, column=1, sticky=tk.W)
        tk.Label(sam_frm, text="Title: " + self.Title,
                 font=(None, MON_FONTSIZE)).grid(row=2, column=1, sticky=tk.W)
        tk.Label(sam_frm, text="Genre: " + self.Genre,
                 font=(None, MON_FONTSIZE)).grid(row=3, column=1, sticky=tk.W)
        tk.Label(sam_frm, text="Track: " + self.Track,
                 font=(None, MON_FONTSIZE)).grid(row=4, column=1, sticky=tk.W)
        tk.Label(sam_frm, text="Date: " + self.Date,
                 font=(None, MON_FONTSIZE)).grid(row=5, column=1, sticky=tk.W)
        tk.Label(sam_frm, text="Duration: " + self.Duration,
                 font=(None, MON_FONTSIZE)).grid(row=6, column=1, sticky=tk.W)

        ''' Close Button ??? '''
        tk.Button(sam_frm, text="??? Close", width=BTN_WID2,
                  command=self.sample_close) \
            .grid(row=8, column=0, padx=2, sticky=tk.W)
        self.sam_top.bind("<Escape>", self.sample_close)
        self.sam_top.protocol("WM_DELETE_WINDOW", self.sample_close)

        ''' Start ffplay and get our Linux PID and Pulseaudio Input Sink # '''
        extra_opt = ' -ss ' + middle_secs + ' -t 10'  # Start sec + duration
        self.sam_top_pid, self.sam_top_sink = \
            start_ffplay(path, TMP_CURR_SAMPLE, extra_opt)

        ext.t_init("sample_middle()")  # Start 10 seconds now
        set_volume(self.sam_top_sink, 0)  # Turn off volume
        ext.stop_pid_running(self.sam_top_pid)  # Pause the music

        ''' During first second reduce other sound applications 
            NOTE: at same time we increase our volume which was set at 0.
            
            TODO: Port code from self.sync_begin() with refined volume steps
        '''
        old_sinks = sink_master()  # build list of tuples
        ext.continue_pid_running(self.sam_top_pid)  # Resume playing music

        for i in range(1, 21):  # 20 steps
            if self.sam_top_is_active is False:
                break
            our_time = set_volume(self.sam_top_sink, int(i * 5))  # Volume up 5%
            # To get 1-20 you need 1,21 range!
            # print('i',i,'i*5',int(i*5)) 
            for active_sink in old_sinks:
                app_sink, app_vol, app_name = active_sink
                if app_sink == self.sam_top_sink:
                    continue  # Skip our sink!
                if app_sink == self.play_top_sink:
                    continue
                percent = int(app_vol - int(app_vol * i / 20))  # Reduce by 5%
                app_time = set_volume(app_sink, percent)  # Volume down 5%
                our_time += app_time  # Total all job times
                self.sam_top.update()  # Poll for close button
            if our_time < .05:
                root.after(int((.05 - our_time) * 1000))  # Sleep .05 per step

        ''' Now mount real artwork '''
        artwork, resized_art = ffmpeg_artwork(path,
                                              self.art_width, self.art_height)
        if artwork is not None:
            sample_art_label.configure(image=artwork)

        elapsed = ext.t_end('no_print')  # Setup time in elapsed

        ''' Continue playing sample until 1 second left '''
        while True:
            if self.sam_top_is_active is False:
                break
            if elapsed >= 8.8:
                break  # Need fade out time
            try:
                ext.kill_pid_rnning(self.sam_top_pid)  # Kill the music
                # self.sam_top.update_idletasks()        # These don't work. You
                # root.update_idletasks()                #  can google it.
                self.sam_top.update()  # Only way that works!
                self.sam_top.after(100)
                elapsed += .105
            except OSError:
                print("Should not be here! Increase elapsed time")
                self.sam_top_pid = 0  # Leave sink open
                break

        ''' Over last second restore volume on other sound applications
            NOTE: We cannot abort this step and leave volume turned down
        '''
        active_sinks = sink_master()  # list of sinks now
        # Only restore sinks active now, using old_sinks volume
        for i in range(1, 21):  # 20 steps
            # May be closed but still need to restore others' volumes
            percent = 100 - i * 5
            if self.sam_top_sink is not "":
                # Set our playing sample's volume down by 5%
                our_time = set_volume(self.sam_top_sink, percent)
            else:
                our_time = 0.0  # Time used so far
            # Turn volume back up for sinks we turned down earlier
            for active_sink in active_sinks:
                app_sink, app_vol, app_name = active_sink
                for old_sink in old_sinks:
                    old_sink, old_vol, old_name = old_sink
                    if old_sink == app_sink and not old_sink == self.sam_top_sink:
                        if old_sink == self.play_top_sink:
                            continue
                        # Sink is still active after sample 10 secs
                        percent = int(old_vol * i / 20)  # Volume up 5%
                        app_time = set_volume(old_sink, percent)
                        our_time += app_time  # Total all job times
            if our_time < .04:
                root.after(int((.04 - our_time) * 1000))  # Sleep .04 between

        ''' Wrap up '''
        if self.sam_top_is_active is False: 
            return  # We are already closed
        self.sample_close()

    # noinspection PyUnusedLocal
    def sample_close(self, *args):  # *args required when lambda used
        """ Close self.sam_top - Play middle 10 seconds sample """
        if self.sam_top_is_active is False:
            return  # We are already closed
        self.sam_top_is_active = False
        root.update()
        root.after(350)  # Give some volume ramp-down time

        if not self.sam_top_pid == 0:
            # If music still playing kill it
            ext.kill_pid_running(self.sam_top_pid)
        if os.path.isfile(TMP_CURR_SAMPLE):
            os.remove(TMP_CURR_SAMPLE)  # Clean up /tmp directory

        self.sam_top_pid = 0  # Can only be one
        self.sam_top_sink = ""  # This and above line Mar 1, 2021.
        self.sam_top.destroy()  # Close the window
        self.wrap_up_popup()  # Set color tags and counts
        if self.sam_paused_music:  # Did we pause music player?
            self.pp_toggle()  # Resume playing

    # ==============================================================================
    #
    #       Playlist chronology
    #
    # ==============================================================================

    def play_chron_tree(self, sbar_width=12):
        """ Chronology treeview List Box, Columns and Headings

            TODO:   Right click on Chrono Tree and Library brings up same
                    song options:
                        - View History
                        - Kid 3
                        - Sample middle 10 seconds (change function?)
        """
        self.chron_tree = ttk.Treeview(self.F4, show=('tree',),
                                       selectmode="none")
        self.chron_tree.column("#0",
                               minwidth=900, stretch=tk.YES)
        self.chron_tree.grid(row=0, column=0, sticky=tk.NSEW)

        ''' Chrono Treeview Scrollbars '''
        # Create a vertical scrollbar linked to the frame.
        v_scroll = tk.Scrollbar(self.F4, orient=tk.VERTICAL, width=sbar_width,
                                command=self.chron_tree.yview)
        v_scroll.grid(row=0, column=1, sticky=tk.NS)
        self.chron_tree.configure(yscrollcommand=v_scroll.set)

        ''' Chrono treeview Colors '''
        self.chron_tree.tag_configure('normal', background='Black',
                                      foreground='Gold')
        self.chron_tree.tag_configure('chron_sel', background='grey18',
                                      foreground='LightYellow')

        ''' Trap left mouse click to select song for playing '''
        # self.chron_tree.bind('<Button-1>', self.chron_tree_click)
        # Aug 17/2021 this is too quirky. Use drop down menu instead

        ''' Create chronology item list '''
        self.play_chron_create()

    def chron_tree_click(self, event):
        """ Play song clicked in chronology treeview.
            # Aug 17/2021 this is too quirky. Use drop down menu instead

        """

        item = self.chron_tree.identify_row(event.y)
        self.song_set_ndx(int(item) - 1)  # Start playing next song, ndx + 1
        # Note above is broken for replaying current song.

    def play_chron_create(self):
        """ Populate playlist chronology treeview listbox
        """

        ''' Delete all entries in old scrollbox '''
        self.chron_tree.delete(*self.chron_tree.get_children())

        # Build chron box treeview listbox
        song_number = 0
        song_count = len(self.saved_selections)
        number_digits = len(str(song_count))

        for song in self.saved_selections:
            if not self.play_top_is_active:
                return  # Play window closed?
            song_number += 1
            ''' Add the #-song-artist line to chron listbox '''
            line = self.play_chron_line(song_number, number_digits, song, True)
            self.chron_tree.insert('', 'end', iid=song_number, text=line,
                                   tags=("normal",))

        ''' Highlight current song
        
            Ensure that self.Album is initialized by play_metadata function.
            If play_metadata has not been called, then a simple highlight is
            all that can be done.
        '''
        self.play_chron_update(self.ndx, True)  # Calls root.update

    def play_chron_line(self, song_number, number_digits, song, short_line):
        """ ??? (U+2116)  ????  (1f3b5)  ????  (1f3a8)  ????  (1f58c)  ???? (1f5b8)
            Big space  (2003) ??? ???Tabular width???, the width of digits (2007)
        """
        # BIG_SPACE = "???"  # UTF-8 (2003) aka Em Space
        # DIGIT_SPACE = "???"       # UTF-8 (2007)
        # NUMBER_PREFIX = "??? "    # UTF-8 (2116) + normal space
        TITLE_PREFIX = "??????? "  # big space + UTF-8 (1f3b5) + normal space
        ARTIST_PREFIX = "??????? "  # big space + UTF-8 (1f3a8) + normal space
        ALBUM_PREFIX = "??????? "  # big space + UTF-8 (1f5b8) + normal space
        # FUTURE SUPPORT:
        DATE_PREFIX = "??????? "  # big space + UTF-8 (1f4c5) + normal space
        # CLOCK_PREFIX = "??????? "  # big space + UTF-8 (1f550) + normal space
        CLOCK_PREFIX = "??????? "  # big space + UTF-8 (1f551) + normal space

        ''' Pad song number with spaces to line up song name evenly '''
        number_str = self.play_padded_number(song_number, number_digits)

        ''' Song title - remove track number and filename extension '''
        song_name = self.lib_tree.item(song)['text']
        song_name = song_name.lstrip('0123456789.- ')  # Trim leading digit
        song_name = os.path.splitext(song_name)[0]  # Trim trailing ext
        line = number_str
        line = cat3(line, TITLE_PREFIX, song_name)

        ''' Extract Artist name from treeview parents '''
        album = self.lib_tree.parent(song)
        artist = self.lib_tree.parent(album)
        line = cat3(line, ARTIST_PREFIX, self.lib_tree.item(artist)['text'])
        line = cat3(line, ALBUM_PREFIX, self.lib_tree.item(album)['text'])
        # print (line)
        if short_line:
            return line

        ''' Build extended line using metadata granular information '''
        #        self.Genre=self.metadata.get('genre', "None")
        #        self.Track=self.metadata.get('track', "None")

        line = number_str + TITLE_PREFIX + self.Title
        line = line + ARTIST_PREFIX + self.Artist
        line = line + ALBUM_PREFIX + self.Album
        line = line + DATE_PREFIX + self.Date
        line = line + CLOCK_PREFIX + self.Duration
        # Replace "00:09:99" duration with "9:99" duration
        line = line.replace("00:0", "")
        line = line.replace("00:", "")  # Catch pink floyd Shine On 11 min song
        line = line.replace(CLOCK_PREFIX + "0", CLOCK_PREFIX)  # Catch 1-9 hour
        return line

    @staticmethod
    def play_padded_number(song_number, number_digits,
                           prefix=NUMBER_PREFIX):
        """ Pad song number with spaces to line up song name evenly
            Called from refresh_items() and play_chron_line()

            Parent(s) can calculate number_digits using:
                song_count = len(self.saved_selections)
                number_digits = len(str(song_count))

        """
        padded_number = ""
        this_digits = len(str(song_number))
        pad_digits = number_digits - this_digits
        for _ in range(pad_digits):
            padded_number = padded_number + DIGIT_SPACE
        return prefix + padded_number + str(song_number)

    def play_chron_update(self, ndx, short_line):

        """ Remove 'chron_sel' tag applied to last song and apply 'normal' tag
            Append 'chron_sel' tag and remove 'normal' tag from selected.
            Format extended line information to 'chron_sel' if
            self.play_metadata() has been called for song.

        """
        old = self.chron_tree.tag_has("chron_sel")
        for child in old:
            tags = self.chron_tree.item(child)['tags']
            tags.remove("chron_sel")
            tags.append("normal")
            self.chron_tree.item(child, tags=tags)

        ''' Set 'chron_sel' tag and remove 'normal' tag '''
        Id = str(ndx + 1)
        tags = self.chron_tree.item(Id)['tags']  # Append 'chron_sel' tag
        tags.remove("normal")
        tags.append("chron_sel")
        self.chron_tree.item(Id, tags=tags)
        # Add self.Album, self.Duration
        if short_line is False:
            song = self.saved_selections[ndx]
            song_number = int(Id)
            song_count = len(self.saved_selections)
            number_digits = len(str(song_count))
            ''' Add the #-song-artist line to chron listbox '''
            line = self.play_chron_line(song_number, number_digits, song, False)
            self.chron_tree.item(Id, text=line)

        ''' Position row to show previous 3, current and next 7 songs '''
        if ndx > 3:
            ThreeBefore = ndx - 3
        else:
            ThreeBefore = 0

        Position = float(ThreeBefore) / len(self.saved_selections)
        # print('Position:',Position)
        self.chron_tree.yview_moveto(Position)  # Initially not open?
        root.update()

    def play_show_hide(self):
        """ Toggles "now playing" list below playing buttons """
        if self.play_list_hide:
            self.F4.grid()  # Restore hidden grid
            self.play_list_hide = False
            text = "???? Hide Chronology"
            text2 = "Hide the scrollable playlist below\n" +\
                    "double the size of spinning artwork."

        else:
            self.F4.grid_remove()  # Hide grid but remember options
            self.play_list_hide = True
            text = "???? Show Chronology"
            text2 = "Show last three songs played,\n" +\
                    "current song, and next six\n" +\
                    "songs in playlist."

        self.chron_button['text'] = text
        self.tt.set_text(self.chron_button, text2)
        ''' Toggle position from above to below, or below to above '''
        self.tt.toggle_position(self.close_button)
        self.tt.toggle_position(self.shuffle_button)
        self.tt.toggle_position(self.pp_button)
        self.tt.toggle_position(self.prev_button)
        self.tt.toggle_position(self.next_button)
        self.tt.toggle_position(self.com_button)
        self.tt.toggle_position(self.int_button)
        self.tt.toggle_position(self.chron_button)

        self.play_chron_update(self.ndx, True)  # Required after shuffle songs
        #root.update()
        self.F4.update_idletasks()


# ==============================================================================
#
#       MusicTree Functions that can be independent
#
# ==============================================================================


def start_ffplay(song, tmp_name, extra_opt):
    """ start_ffplay parameters:
            song = unquoted song name, we'll add the quotes
            tmp_name = /tmp/filename to send output of song name EG:
                TMP_CURR_SONG="/tmp/mserve.currently_playing"
                TMP_CURR_SAMPLE="/tmp/mserve.current_sample"
            extra_opt can be blank or, they can be:
                -ss = start seconds offset within song, normal is 0
                -t = how long to play song (duration in seconds)

    """

    ''' Get old Input Sinks before ffplay starts '''
    old_sink = sink_list("ffplay")

    ''' ffplay start options to redirect output to temporary file '''
    # noinspection SpellCheckingInspection
    ext_name = 'ffplay -autoexit ' + '"' + song + '" ' + extra_opt + \
               ' -nodisp 2>' + tmp_name
    # inspection SpellCheckingInspection
    ''' launch ffplay external command in background '''
    found_pid = ext.launch_command(ext_name, toplevel=None)
    if found_pid == 0:
        print('Waited 10 seconds, aborting start_ffplay() get PID')
        return

    ''' Get New PID and Input Sinks for ffplay '''
    found_sink = None
    loop_cnt = 0
    while True:
        # Give time for `ffplay` to create pulseaudio sink.
        loop_cnt += 1
        if loop_cnt == 20:
            print('Looped 20 times, aborting start_ffplay() get sink')
            return

        root.after(5)

        new_sink = sink_list("ffplay")
        if new_sink == old_sink:
            continue
        found_sink = list_diff(new_sink, old_sink, "start_ffplay()")
        print('found sink:', found_sink)
        break

    return found_pid, found_sink


def get_curr_ffplay_secs(tmp_name):
    """ Get elapsed play time from ffplay output file in RAM
        If resuming play, first time is unreliable so return second time.
        If we've just paused then first time is reliable.
    """
    last_time = 0
    second_last = 0
    time_count = 0
    with open(tmp_name, "rb") as f:
        f.seek(-256, os.SEEK_END)  # 256 from end. Note minus sign
        x = f.read()
        fields = x.split()
        for i, val in enumerate(fields):
            if val == "M-A:" and i > 0:
                time_count += 1
                second_last = last_time
                last_time = fields[i - 1]  # time proceeds "M-A:" tag

        # print('times found:', i, '.  Last:', last_time, \
        #      'Second last:', second_last)

    return float(second_last)


def list_diff(new_lst, old_lst, name):
    """ Return string variable added to new list not in old list
        Must be exactly one new item
    """
    count_diff = len(new_lst) - len(old_lst)
    diff_lst = list(set(new_lst) - set(old_lst))
    if not count_diff == 1 or not len(diff_lst) == 1:
        print("new_list_var() for " + name + " difference is not 1.")
        print("new_lst:", new_lst)
        print("old_lst:", old_lst)
        return diff_lst
    return str(diff_lst[0])


def pid_list(program):
    """ Return list of PIDs for program name """
    PID = os.popen("pgrep " + program).read().strip().splitlines()
    return PID


def sink_list(program):
    """ Return list of Firefox or ffplay input sinks indices
        Used for both old_lst and new_lst lists. old_lst may be empty.
    """
    indices = []
    all_sinks = sink_master()
    for entry in all_sinks:
        sink, vol, name = entry
        if program == name:
            indices.append(sink)
            print('MATCHING sink entry found:', entry)
    return indices


# After calling 11 times crashes so call outside of sink_master()
pulse_working = True
try:
    pulse = pulsectl.Pulse()

except Exception as p_err:  # CallError, socket.error, IOError (pidfile), OSError (os.kill)
    pulse_working = False
    raise PulseError('Failed to connect to pulse {} {}'.format(type(p_err), p_err))


def sink_master():
    """ Get PulseAudio list of all sinks
        Return list of tuples with sink #, flat volume and application name
    """

    all_sinks = []                              # List of tuples

    if pulse_working:
        # WIP: Use existing tuple structure but convert to pulsectl volume
        #      structure down the road.
        for sink in pulse.sink_input_list():
            #print("\n=======  ", sink.index, sink.volume, sink.name)
            #print(sink.proplist['application.name'])
            # sink.volume = channels = 2, volumes = [100 % 100 %]
            this_volume = str(sink.volume)
            this_volume = this_volume.split('[')[1]
            this_volume = this_volume.split(' ')[0]
            this_volume = this_volume.replace('%', '')
            all_sinks.append(tuple((str(sink.index), this_volume,
                                    str(sink.proplist['application.name']))))
            #print(sink.proplist)
            #pulse_dict = sink.proplist
            #for i in pulse_dict:
            #    print("key:", i, "value:", pulse_dict[i])
        return all_sinks


    all_lines = os.popen('pactl list sink-inputs').read().splitlines()

    this_sink = ""
    in_sink = False
    this_volume = ""
    in_volume = False
    for line in all_lines:
        if in_sink is False and "Sink Input #" in line:
            # Sink Input #725
            this_sink = line.split('#')[1]
            in_sink = True
            continue
        if in_sink is True and in_volume is False and "Volume:" in line:
            # Volume: front-left: 32768 /  50% / -18.06 dB,   front-right ...
            this_volume = line.split('/')[1]  # Grab 50% or 100%, etc
            this_volume = this_volume.replace(' ', '')
            this_volume = int(this_volume.replace('%', ''))
            in_volume = True
            continue

        # noinspection SpellCheckingInspection
        if in_sink is True and in_volume is True and "tion.name =" in line:
            # inspection SpellCheckingInspection
            # application.name = "ffplay"
            this_name = line.split('=')[1]
            this_name = this_name.replace(' ', '')
            this_name = this_name.replace('"', '')
            # Add tuple to the list
            all_sinks.append(tuple((this_sink, this_volume, this_name)))
            # Reset searching for first and second targets again
            in_sink = False
            in_volume = False
            continue

    ''' return list of tuples (sink#, volume percent, application name) '''
    return all_sinks


def step_volume(sink, p_start, p_stop, steps, interval, thread=None):
    """
        Step volume up or down for Pulseaudio Input Sink #
        if p_stop > p_start we are going up, else we are going down
        interval defines interval between steps and time to call pa adjusted
    """
    if sink is "":
        print("step_volume(): Input Sink # is blank")
        return
    adjust = int((p_stop - p_start) / steps)
    for _ in range(steps):
        p_start += adjust  # positive (up) or negative (down)
        t_start = time.time()
        job_time = set_volume(sink, p_start)
        # Sleep in milliseconds to interval time and allow screen updates
        if thread:
            thread()
        sleep = interval * 1000 - (time.time() - t_start) * 1000
        if sleep < 1:
            sleep = 1
        if job_time < interval:
            root.update_idletasks()
            root.after(int(sleep))


def set_volume(sink, percent, return_err=False):
    """ Set volume and return time required to do it
        Trap error messages with 2>&1
        subprocess

        Long Term TODO: Use: https://github.com/mk-fg/python-pulse-control
            this will be faster than call to `pactl`
    """
    # Build command line list for subprocess
    # noinspection PyListCreation
    command_line_list = []
    command_line_list.append("pactl")
    command_line_list.append("set-sink-input-volume")
    command_line_list.append(sink)
    command_line_list.append(str(percent) + '%')
    #command_str = " ".join(command_line_list)  # list to printable string

    ext.t_init('set_volume() -- pactl set-sink-input-volume')
    pipe = sp.Popen(command_line_list, stdout=sp.PIPE, stderr=sp.PIPE)
    text, err = pipe.communicate()  # This performs .wait() too
    job_time = ext.t_end('no_print')
    if text:
        print("standard output of set_volume() subprocess:")
    if err:
        print("standard error of set_volume() subprocess:")
        print('set_volume() ERROR. sink:', sink, 'percent:', percent,
              'job_time:', job_time)
        print('error:', err)
    # if pipe.return_code == 0:                  # Future use

    if return_err:
        return job_time, err
    else:
        return job_time


def ffmpeg_artwork(path, width, height):
    """
        Use ffmpeg to get artwork for song into TMP_FFMPEG filename.
        Messages go to TMP_FFPROBE filename which is ignored for now.
    """

    # Don't reuse last artwork
    if os.path.isfile(TMP_FFMPEG):
        os.remove(TMP_FFMPEG)

    # noinspection SpellCheckingInspection
    result = os.popen('ffmpeg -nostdin -y -vn -an -r 1 -i ' +
                      '"' + path + '" '
                      + TMP_FFMPEG + ' 2>' + TMP_FFPROBE). \
        read().strip()

    # noinspection SpellCheckingInspection
    ''' ffmpeg options
    -nostdin to suppress: Press [q] to stop, [?] for help
    -y to supppress error when file exists
    -vn = skip video
    -vn = skip audio
    -r 1 = frame rate 1
    -i = input filename
    2> = redirect stderr (where stdout is written) to filename
    '''
    # inspection SpellCheckingInspection

    if len(result) > 1:
        # OS returned an error message of some sort.
        return None, None

    if not os.path.isfile(TMP_FFMPEG):
        # Song has no artwork that ffmpeg can identify.
        return None, None

    original_art = Image.open(TMP_FFMPEG)
    resized_art = original_art.resize(
        (width, height), Image.ANTIALIAS)
    return ImageTk.PhotoImage(resized_art), resized_art


# ==============================================================================
#
#       Miscellaneous Functions section + "__main__"
#
# ==============================================================================


def cat3(line, prefix, string):
    """ Concatenating strings with latin characters has error:

            UnicodeEncodeError: 'ascii' codec can't encode character
            u'\xc6' in position 0: ordinal not in range(128)
    """
    # noinspection PyBroadException
    try:
        # return (line + prefix + string)
        return line + prefix + string.encode("utf8")
    except:
        # noinspection PyProtectedMember
        print('cat3() called from:', sys._getframe(1).f_code.co_name,
              '() Latin character error in:', prefix, string)
        # noinspection SpellCheckingInspection
        ''' cat3() ... Latin character error in: ???????  ??nema '''
        return line + prefix + "????????"
        # inspection SpellCheckingInspection


def get_dir(parent, title, start):
    """ Get directory name
    """

    root.directory = filedialog.askdirectory(initialdir=start,
                                             parent=parent,
                                             title=title)
    # print (root.directory)
    return root.directory


def load_last_location():
    """ Open last location used.
    """

    global START_DIR, LODICT  # Never change LODICT after startup!

    ''' Check for Last known location iid '''
    if not os.path.isfile(lc.FNAME_LAST_LOCATION):
        return False
    try:
        with open(lc.FNAME_LAST_LOCATION, 'rb') as f:
            # read the data as binary data stream
            iid = pickle.load(f)

    except IOError as error:
        # New installation would not have last location...
        # User may never create locations... 
        print('Error opening:', lc.FNAME_LAST_LOCATION)
        print(error)
        return False

    # Set protected LODICT
    LODICT = lc.item(iid)  # local SAVE loc dictionary
    lc.set_location_filenames(LODICT['iid'])  # insert /L999/ into paths
    START_DIR = LODICT['topdir']  # Music Top directory
    # Display keep awake values
    if LODICT['activecmd'] is not "":
        print('Keep awake command:', LODICT['activecmd'],
              'every', LODICT['activemin'], 'minutes.')

    # Check if host name not blank and then wake it up and validate topdir
    if lc.validate_host(LODICT['iid']):  # No toplevel for parm 2
        # returns true only when host and host is online
        return True

    ''' See if last location path and see if it is mounted '''
    if not os.path.isdir(START_DIR):
        print('Location contains invalid or off-line directory:', START_DIR)
        return False

    return True


class ToolTip(object):
    """ Now obsolete. Leave here to compare to message.ToolTip() """

    def __init__(self, widget, text, thread=None, pool=None, tool_type='button'):
        """ Background defaults to yellow """
        self.widget = widget
        # Invert tooltip colors from widget colors
        if type is 'button':
            self.fg = self.widget["background"]
            self.bg = self.widget["foreground"]
        else:
            self.fg = None
            self.bg = None

        self.tip_window = None
        self.id = None
        self.x = self.y = 0
        self.text = text
        self.thread = thread
        self.pool = pool
        self.tool_type = tool_type
        self.left_already = False
        self.enter_time = time.time()
        self.leave_time = time.time()
        self.enter_count = 0
        self.leave_count = 0

    #def showtip(self, text):
    def showtip(self):
        """ Display text in tooltip window """
        #self.text = text

        if self.left_already or self.tip_window or not self.text:
            return

        # Text doesn't have a bbox
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 37
        y = y + cy + self.widget.winfo_rooty() + 37

        # Invert tooltip colors from current widget album art colors.
        if type is 'button':
            self.fg = self.widget["background"]
            self.bg = self.widget["foreground"]
        else:
            self.fg = None
            self.bg = None

        self.tip_window = tw = tk.Toplevel(self.widget)
        self.tip_window.withdraw()  # Remain invisible while we figure out the geometry
        # Default background color must be same as widget foreground
        self.tip_window['background'] = self.bg
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))

        try:
            # For macOS
            # noinspection PyProtectedMember
            tw.tk.call("::tk::unsupported::MacWindowStyle",
                       "style", tw._w,
                       "help", "noActivates")
        except tk.TclError:
            pass

        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background=self.bg, foreground=self.fg, relief=tk.SOLID,
                         borderwidth=2, pady=10, padx=10, font=(None, MED_FONT))
        label.pack(ipadx=2)
        self.tip_window.deiconify()  # Become visible at the desired location

    def hidetip(self):
        """ Indirect removal via 'tw' var is necessary to prevent artifacts
        """
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

        self.left_already = True  # In case delayed balloon tries to mount
        # Reset button colors


def custom_paste(event):
    """ Allow paste to wipe out current selection. Doesn't work yet!
        From: https://stackoverflow.com/a/46636970/6929343
    """
    # noinspection PyBroadException
    try:
        event.widget.delete("sel.first", "sel.last")
    except:
        pass
    event.widget.insert("insert", event.widget.clipboard_get())
    return "break"


LODICT = {}  # Never change LODICT after startup!
NEW_LOCATION = False  # Is directory not saved in location master file?
SORTED_LIST = []
root = None


# if __name__ == "__main__":
def main(toplevel=None, mon_geom=None):
    """
    Establish our file locations from sys.argv or last used location
    :param mon_geom: Monitor geometry
    :type toplevel: Object
    :param toplevel: Splash screen mounted for startup
    """

    global root  # named main()
    global SORTED_LIST  # os.walk() results: artist/album/songs
    global START_DIR  # Required to define after creating function
    global NEW_LOCATION  # When new hasn't been saved in location master

    g.init()            # Initialize global variables.

    if mon_geom is not None:
        print('monitor geometry passed but not supported yet.')

    # create Top Level
    if toplevel is None:
        root = tk.Tk()  # Create "very top" toplevel for all top levels
    else:
        root = tk.Toplevel()

    root.withdraw()  # Remove default window because we have treeview
    """ From: https://stackoverflow.com/a/46636970/6929343
        Should deleted highlighted text when paste is used.
        Only applies to X11 because other systems do it automatically. 
    """
    root.bind_class("Entry", "<<Paste>>", custom_paste)  # X11 only test

    ''' Set font style for all fonts including tkSimpleDialog.py '''
    img.set_font_style()  # Make messagebox text larger for HDPI monitors
    ''' Set program icon in taskbar '''
    img.taskbar_icon(root, 64, 'white', 'lightskyblue', 'black')

    # Find location dictionary matching top directory passed as argument
    try:
        ''' mserve called with parameter to Top Directory '''
        START_DIR = sys.argv[1]

        # Massage parm1 of ".", "..", "../Sibling", etc.
        START_DIR = os.path.realpath(START_DIR)

        ''' Is passed Top Directory in our known locations? '''
        if lc.get_dict_by_dirname(START_DIR):
            # print('mserve manually started with lc.DICT:',lc.DICT)
            # Make passed Top Directory our last known location then load it
            lc.save_mserve_location(lc.DICT['iid'])
            load_last_location()
        else:
            # print('START_DIR not in location master file:', START_DIR)
            LODICT['name'] = START_DIR  # Name required for title bar
            NEW_LOCATION = True  # Don't use location master

    except IndexError:
        ''' No Parameter passed. Check for Last location file on disk '''
        if load_last_location():
            # We successfully loaded last used location
            pass
        else:
            # First time or no saved locations matching current directory
            cwd = os.getcwd()
            dir_path = os.path.dirname(os.path.realpath(__file__))
            print('current directory:', cwd)
            print('working path:', dir_path)
            # Our user ID got initialized in location.py imported as lc.
            # music_dir = os.sep + "home" + os.sep + lc.USER + os.sep + "Music"
            music_dir = os.sep + "home" + os.sep + g.USER + os.sep + "Music"
            # Prompt to get startup directory using /home/USER/Music as default
            START_DIR = get_dir(root, "Select Music Directory", music_dir)
            if START_DIR is None:
                START_DIR = cwd
            LODICT['name'] = START_DIR  # Name required for title bar
            NEW_LOCATION = True

    # If no optional `/` at end, add it for equal comparisons
    if not START_DIR.endswith(os.sep):
        START_DIR = START_DIR + os.sep

    # TODO: Review SORTED_LIST duplicated with self.song_list
    # Build list of songs
    SORTED_LIST = make_sorted_list(START_DIR, toplevel=toplevel)

    if len(SORTED_LIST) == 0:
        print('ERROR: Music Library appears empty !!!\n')
        print('       If this is a remote host check connection by listing')
        print('       files on mount point.\n')
        print('       If you run command below and get the error below:')
        print('         $ sshfs "host:/mnt/music/" /mnt/music')
        print('         fuse: bad mount point `/mnt/music`: ' +
              'Transport endpoint is not connected')
        print('       Then unmount the point with:')
        print('         $ sudo umount -l /mnt/music')

    # Temporarily create SQL music tables until search button created.
    # TODO: How to create music tables when location hasn't been defined yet?
    ext.t_init('sql.create_tables()')
    sql.create_tables(SORTED_LIST, START_DIR, PRUNED_SUBDIRS, g.USER, LODICT)
    #sql.hist_delete_type_action('encode', 'discid')  # One time Aug 23/2021
    #sql.hist_delete_type_action('encode', 'album')  # One time Aug 23/2021
    ext.t_end('print')  # sql.create_tables(): 0.1092669964

    MusicTree(toplevel, SORTED_LIST)  # Build treeview of songs

    # https://stackoverflow.com/questions/12800007/why-photoimages-dont-exist
    if toplevel is None:
        root.mainloop()         # When splash screen calls us there is mainloop


if __name__ == "__main__":
    main()

# End of mserve.py
