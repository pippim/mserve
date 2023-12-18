#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: pippim.com
License: GNU GPLv3. (c) 2020 - 2023
Source: This repository
Description: mserve - Music Server - Main **mserve** Python Module
"""

from __future__ import print_function  # Must be first import
from __future__ import with_statement  # Error handling for file opens
# from __future__ import unicode_literals  # Not needed.
import warnings  # 'warnings' advises which commands aren't supported
warnings.simplefilter('default')  # in future Python versions.

# /usr/lib/python3/dist-packages/apport/report.py:13: PendingDeprecationWarning:
# the imp module is deprecated in favour of importlib; see the module's
# documentation for alternative uses

# ==============================================================================
#
#       mserve.py (Music Server) - Manage Music in multiple locations
#
#       July 26 2020 - Copy from mserve-tmplt. Add thousands of code lines.
#       Sept 20 2020 - Start taking out or replacing 63 root.update().
#       Sept 23 2020 - Make compare button disappear (entire grid 4 remove).
#       Nov. 02 2020 - Remove old selection processing for new CheckboxTreeview.
#       Dec. 12 2020 - Chrome os doesn't support .grid_remove(). Comment out 15
#            self.loc_F4.grid_remove().
#       Dec. 28 2020 - Expand Selected MB to include Playlist Song Number.
#       Jan. 15 2021 - Add vu_meter.py as separate program.
#       Feb. 07 2021 - Add webscrape.py as separate program.
#       Mar. 05 2021 - Add fine-tune time index function (Lyrics Synchronization).
#       Mar. 13 2021 - Read ffplay output for current seconds instead of calc.
#       May. 02 2021 - mserve.py is now called by 'm' wrapper splash screen.
#       May. 18 2021 - createToolTip() - Hover balloon (Deprecated 8/8/21).
#       Jun. 14 2021 - Rounded Rectangle Canvas widget.
#       Aug. 08 2021 - New webscrape.py parameters/results via SQL History.
#       Aug. 21 2021 - Revamp tooltips with toolkit.ToolTips().
#       Jan. 18 2022 - Set tooltip location SW, SE, NW or NE of parent widget.
#       Jan. 03 2023 - Shuffle broken when song with no lyrics is playing.
#       May. 07 2023 - sql.FixData to fix times and remove duplicate records.
#                      View SQL Music and History Tables using filters.
#       May. 20 2023 - Move Lyrics frame when hiding chronology. Resume song on
#                      startup and saved pause/play & show/hide chronology states
#       May. 22 2023 - Replace Hockey buttons with FF/Rewind buttons. Toggle
#                      with variable dropdown menu text.
#       May. 23 2023 - Support user defined image file when no artwork. Fix long
#                      running function causing refresh_play_top() to stop. Now
#                      next song automatically starts when current song ends.
#                      Update: https://www.pippim.com/programs/mserve.html#
#       May. 25 2023 - Extensive performance enhancements over two days.
#       May. 26 2023 - Set volume to 66% when CBC hockey game on air.
#       June 01 2023 - Music Location checkboxes batch update to Playlist.
#       June 03 2023 - Handle <No Album> in lib_tree paths used in SQL tables.
#       June 05 2023 - No location when passing music directory parameter.
#       June 07 2023 - Many changes. E.G. step_volume() takes list of sinks.
#       June 09 2023 - tvVolume() class for Hockey. Stanley=Vegas 2, Florida 1.
#       June 11 2023 - Add TV_BREAK and SOUND. Stanley Cup=Vegas 3, Panthers 1.
#       June 13 2023 - Develop Playlists() class. Vegas won Stanley Cup! (4-1)
#       June 18 2023 - Expanding/Collapsing Information Centre. InfoCentre().
#       June 21 2023 - 'M' splash screen disappears as late as possible.
#       June 23 2023 - Antonia's request to highlight hovered chron_tree row.
#       June 25 2023 - Check corrupt music files and device off-line.
#       June 26 2023 - New classes Refresh() and FileControl().
#       June 29 2023 - Restore last access when < 80% of song was played.
#       July 02 2023 - Temporary filenames Windows/Mac. Enhance artwork.
#       July 04 2023 - Create FineTune() class. Major bugs worked out.
#       July 05 2023 - Create Help buttons that open pippim website pages.
#       July 07 2023 - Begin vu_pulse_audio.py for pulsectl.Pulse interface.
#       July 09 2023 - New PA fading - faster, easier, smaller & more robust.
#       July 12 2023 - New 'mserve_config.py' checks required modules/commands.
#       July 13 2023 - sqlite3 overhaul with new field 'MostlyPlayedTime'
#       July 15 2023 - Rename Artist or Album. Rename files in OS & SQL.
#       July 16 2023 - Click Artist, Album or Title to open kid3 or nautilus
#       July 21 2023 - check_missing_artwork() report files missing audio stream.
#       Aug. 18 2023 - InfoCentre() Banner tooltip erase and rebuild not necessary.
#       Aug. 19 2023 - Dynamic display_metadata(), fix VU Meter Height on startup.
#       Aug. 20 2023 - View SQL + Metadata dictionaries built on ffprobe.
#       Aug. 24 2023 - Redirect show_debug() from console to InformationCentre().
#       Aug. 31 2023 - refresh_play_top() queuing next song was replaying song.
#       Sep. 02 2023 - Begin libftp substitute to curlftpfs.
#       Sep. 03 2023 - Make LRC (synchronized lyrics) for other music players.
#       Sep. 06 2023 - Use walk_list and size_dict from FTP test host at start.
#       Sep. 09 2023 - Tools - checked files - Make LRC files and copy to loc.
#       Sep. 21 2023 - Slide Show Carousel (beta < 1 hour coding)
#       Sep. 23 2023 - Playlists class save_act() for Rename Playlist function.
#       Sep. 24 2023 - YouTube Playlists - View in mserve and Open in browser.
#       Oct. 29 2023 - YouTube Playlists - Condense youTreeSmartPlayAll().

# noinspection SpellCheckingInspection
"""

References:
    https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/ttk-Treeview.html


-----------------------------------------------------------------------------

BUGS:

    Sep. 11 2023 - All Bugs have been fixed.

TODO:

    "Playing Music" window start up splash tooltip centered with:
        "Playing Music from: "  Favorites, Playlist: "xxx", Artist: "xxx",
                                Album: "xxx", Genre "xxx", Year "9999".
        "Duration: ", "Position: ", "Current Song: "
        Repeat splash tooltip on Pause/Play
        Similar splash tooltip for "Music Location Tree" window.

    Update Metadata over WiFi takes hours. Mutagen check should be skipped
        because the results aren't used. When `curlftpfs` gives error:
        "1) Not a music file", use FTP transfer because `#` in filename.

    Remove all lc.LIST, lc.DICT, lc.read(), lc.write(), etc.  Delete old
        location pickle files no longer referenced:
            .../mserve/locations
            .../mserve/last_location

    Top Directory picker needs to recall dir_name() checker to get location. 

    Display invalid music files (<100K) with ShowInfo() instead of print().
        At same time advise to delete walk_list and paths_and_sizes to have
        rebuilt.

    High priority to crawl FTP server with fast_refresh per file to find new
        songs and delete old songs. With every filename refresh can be
        called every 10 ms or so. When complete, rebuild lib_tree and save
        walk_list and paths_and_sizes. Do this at start of every session. It
        may not finish if session less than ten minutes?

    Setup variables when file_ctl.new(path) method called:
        ''' Variables for FTP / SSH '''
        # For FTP check if music file in cache. If not, retrieve to cache
        self.file_cached = None     # music file retrieved locally for playing?
        self.cache_name = None      # cached filename replaces self.path 
        self.cache_size = None      # music file size
        self.cache_mtime = None     # music file lc.ModTime()
    
    After 'Make LRC For Checked Songs' and 'Copy Checked To New Location'
        'add' new history or add/update last 'edit' history record. Not
        for every song, simply for that location or playlist.

    Chronology filter "this artist" is pulling all compilations
        Evaluate feasibility of "this album" filter

    FileControl.zoom() _alpha_cb() that covers instead of pushing tree down
        FineTune.sync() divide last duration time to zero duration lines


LONGER TERM TODO'S:

    Calculate total duration in Music Location Tree and seleccted duration.

    When playing .wav and there is a matching .mp3, mp4, etc. with artwork
        and lyrics, why not use that SQL Music Table metadata?
    
    After lyrics training, make .lrc file?

    Track mserve suspend / resume times. Similar to play_ctl start / stop.
        This is needed for knowing that host may be auto disconnected.

    Artist and Album popup in Music Location Tree new option to create
        temporary playlist and play all. Current favorites or playlist
        swapped out while temporary playlist plays in play_top. Same new
        technology could replace "sample middle" and sample full"?

    Too many history records. Purge function from 20k records and reuild
        row IDs. Since only genius is webscraped for lyrics, it's pointless
        having history records for now. Only if a website other than
        genius is scraped should there be a history record. 'file'-'init'
        history might be irrelevant except for new songs added to location.

    VU Meter peak line indicator that drops down to current level and changes
        color as it passes through zone. How long to hold peak and how fast
        to drop? Peak is instantly pushed up on db increase. Peak would be
        visible betwen rectangles and inside retangles which requires new
        rectangle box that is no longer simply invisible or all one color.

    Synchronize Android host is 1,000 times faster with ModTime() class
        but can be even faster using earlier and with paths_and_sizes
        file. Probalby another 100 times faster. 

    rebuild_lib_tree() doesn't show the song just ripped. Since going
        through the trouble, might as well reuse SORTED_LIST2 with new last
        access time if it doesn't refresh automatically for old song ripped
        again like it should.

    Instead of ellipsis for long labels, try: wraplength=250

    In mserve_config.py, verify external commands are in path:
        command -v cp, diff, ffplay, ffprobe, ffmpeg, fusermount, 
            gsettings, gst-launch-1.0, kid3, kill, nautilus, nc, nmap,
            pactl, pgrep, pqiv, ps, ssh, sshfs, stat, touch, 
            wakeonlan, wmctrl, xclip, xdotool, xprop

    In InfoCentre():
        
        Define future button (collapsed=True) such that only title is
            displayed and click on button to expand section (text).

    When watching lyrics time scrolling and you notice time is out of sync,
        need quick click action button to pause and fix 2 seconds ago...

RENAME VARIABLES:
    'self.saved_selections' -> 'self.play_order_iid'
    'self.saved_selections' -> 'self.play_iid_seqs'
    'self.saved_selections' -> 'self.playlist_iids'  # Depends on next section
    'self.saved_selections' -> 'self.play_lib_iid'
    'self.saved_selections' -> 'self.sel_lib_iids'
    'self.saved_selections' -> 'self.sel_lib_tree_iids'
    'self.saved_selections' -> 'self.play_iids'
    'self.saved_selections' -> 'self.select_iids'
    'self.saved_selections' -> 'self.sel_iids'
    'self.saved_selections' -> 'self.fav_iid_list'
    'self.saved_selections' -> 'self.play_iid_list'

    'self.saved_playlist'   -> 'self.playlist_paths'  # Already DONE
    'self.playlist_paths'   -> 'self.sel_lib_paths'
    'self.playlist_paths'   -> 'self.sel_lib_tree_paths'
    'self.playlist_paths'   -> 'self.select_paths'
    'self.playlist_paths'   -> 'self.play_paths'
    'self.playlist_paths'   -> 'self.fav_paths'  # Misleading when Playlists()
    'self.playlist_paths'   -> 'self.select_paths'
    'self.playlist_paths'   -> 'self.fav_path_list'  # Misleading when Playlists()
    'self.playlist_paths'   -> 'self.play_path_list'

    'self.song_list'        -> 'self.lib_tree_paths'
    'self.song_list'        -> 'self.lib_song_paths'
    'self.song_list'        -> 'self.fake_paths'  # Already DONE

    'self.ndx'              -> 'self.curr_iid_ndx'
    'self.ndx'              -> 'self.play_curr_ndx'
    'self.ndx'              -> 'self.play_ndx'  # June 29, 2023 11 AM - Flavor De Jure
    'self.ndx'              -> 'self.seq_ndx'
    'self.ndx'              -> 'self.select_ndx'
    'self.ndx'              -> 'self.sel_ndx'
    'self.ndx'              -> 'self.sel_curr_ndx'
    'self.ndx'              -> 'self.iid_ndx'
    'self.ndx'              -> 'self.fav_ndx'  # Misleading when Playlists()

    New brothers for '_ndx' -> 'self.---_iid"   # self.saved_selections[self.ndx]
                            -> 'self.---_path"  # self.playlist_paths[self.ndx]

RENAME FUNCTIONS:
    'self.song_set_ndx()'   -> 'self.set_sel_ndx()'
    'self.song_set_ndx()'   -> 'self.set_select_ndx()'
    'self.song_set_ndx()'   -> 'self.change_select_ndx()'
    'self.song_set_ndx()'   -> 'self.play_new_song()'
    'self.song_set_ndx()'   -> 'self.play_set_ndx()'
    'self.song_set_ndx()'   -> 'self.set_play_ndx()'    # July 1, 2023 5:28pm
    Advantage of changing "self.song_" to "self.play_" is below too:
        self.song_artist_var.set(make_ellipsis(self.play_ctl.Artist, E_WIDTH))
        self.song_album_var.set(make_ellipsis(self.play_ctl.Album, E_WIDTH))
        self.song_title_var.set(make_ellipsis(self.play_ctl.Title, E_WIDTH))

    'self.play_insert()'    -> 'self.add_selected()'
    'self.play_insert()'    -> 'self.insert_selection()'
    
RENAME WINDOWS:
    'Playing Playlist'      -> 'Playing Music' window
                            -> 'Music Playing' window           # 1
                            -> 'Play Selections' window
                            -> 'Playing Checked' window
                            -> 'Music Checked' window
                            -> 'Checked Music' window
                            -> 'Playlist Music' window
                            -> 'Playlist Songs' window

    'Music Location Tree'   -> doesn't have a name, just location name

    'Information Centre'    -> 'Session History' window
#
# =============================================================================

CALL:
    m "/mnt/music/Users/Person/Music/iTunes/iTunes Media/Music/"

REQUIRES:
    sudo apt install compiz                  # for Hockey (smooth shark move)
    sudo apt install dconf-editor            # for Hockey (gsettings)
    sudo apt install ffmpeg                  # for artwork, ffprobe and ffplay
    sudo apt install gstreamer1.0-tools      # For encoding CDs gst-launch-1.0
    sudo apt install kid3                    # Optional for editing metadata
    sudo apt install pauvcontrol             # For VU Meters (sound redirect)
    sudo apt install pqiv                    # Make transparent Shark (Hockey)
    sudo apt install python-appdirs          # Application directory names
    sudo apt install python-beautifulsoup    # Scrape Song lyrics
    sudo apt install python-gi               # Gnome window functions (newer)
    sudo apt install gir1.2-wnck-3.0         # Gnome window functions (older?)
    # NOTE: python-wnck not tested but may work instead of gi + gir1.2-wnck-3.0
    sudo apt install python-libdiscid        # Get CD's disc ID
    sudo apt install python-notify2          # Popup bubble messages
    sudo apt install python-numpy            # Installed by default in Ubuntu
    sudo apt install python-magic            # Get file type "magic" information
    sudo apt install python-musicbrainzngs   # Get metadata for CD
    sudo apt install python-mutagen          # Encode and ID3 tags
    sudo apt install python-pil              # PIL graphics routines
    sudo apt install python-pil.imagetk      # PIL image processing
    sudo apt install python-pyaudio          # For background job vu_meter.py
    sudo apt install python-requests         # Get Cover Art
    sudo apt install python-selenium         # Automated YouTube Playlist play
    sudo apt install python-subprocess32     # To compare locations
    sudo apt install python-simplejson       # automatically installed Ubuntu
    sudo apt install python-tk               # Tkinter (default in Windows & Mac)
    sudo apt install wmctrl                  # To move Kid3 or Fishing window
    sudo apt install x11-apps                # xwd window dump (screen shot)
    sudo apt install xclip                   # Insert clipboard
    sudo apt install xdotool                 # To move Kid3 or Fishing window

    sudo add-apt-repository ppa:j-4321-i/ttkwidgets  # CheckboxTreeview
    # NOTE: on Chromebook crostini you need to patch Debian to use Ubuntu key
    To add Ubuntu PPA to Debian for Crostini:
    https://linuxconfig.org/install-packages-from-an-ubuntu-ppa-on-debian-linux

    This is necessary for ttkwidgets and ttkcalendar
    sudo apt-get update
    sudo apt-get install python-ttkwidgets           # CheckboxTreeview
    sudo add-apt-repository ppa:j-4321-i/ppa
    sudo apt-get update
    sudo apt-get install python-tkcalendar

    Python 2.7 copy of ttkwidgets is stored directly in .../mserve/ttkwidgets
    Python 2.7 copy of pyaudio is stored directly in .../mserve/pulsectl

ERROR OVERRIDE - https://github.com/quodlibet/mutagen/issues/499:
    File "/usr/lib/python2.7/dist-packages/mutagen/flac.py", line 597, in write
      desc = self.desc.encode('UTF-8')
  UnicodeDecodeError: 'ascii' codec can't decode byte 0xe2 in position 4: 
    ordinal not in range(128)
    CHANGE line 597 from:
        desc = self.desc.encode('UTF-8')
    to:
        try:                                # 2020-10-18 UnidcodeDecodeError
            desc = self.desc.encode('UTF-8')
        except UnicodeDecodeError:          # Filename: 06 Surf’s Up.oga
            desc = self.desc                # self.desc already in UTF-8
    $ sudo apt-mark hold python-mutagen

    ERROR # 2

    File "/usr/lib/python2.7/dist-packages/mutagen/id3/__init__.py", line 600, in __save_frame
      framedata = frame._writeData()
  AttributeError: 'unicode' object has no attribute '_writeData'

File Server NOTES:
    File server needs to mount music directory if not mounted already. e.g.:
        sudo mount -t auto -v /dev/sdb1 /mnt/music

"""

''' If called by 'm', configuration is OK. Otherwise, check configuration. '''
import inspect
import os
try:
    filename = inspect.stack()[1][1]  # If there is a parent, it must be 'm'
    parent = os.path.basename(filename)
    if parent != "m":
        print("mserve.py must be called by 'm' but is called by:", parent)
        exit()
except IndexError:  # list index out of range
    ''' 'm' hasn't been run to get global variables or verify configuration '''
    import mserve_config as cfg
    caller = "mserve.py"  # don't call if 'm' called 'mserve.py' splash
    if not cfg.main(caller):
        print("mserve not fully installed. Aborting...")
        exit()
    import global_variables as g  # Added Aug 3/23 as shortcut to below.
    g.init()

try:  # Python 3
    import tkinter as tk
    import tkinter.ttk as ttk
    import tkinter.font as font
    import tkinter.filedialog as filedialog
    import tkinter.messagebox as messagebox
    import tkinter.simpledialog as simpledialog
    import tkinter.scrolledtext as scrolledtext
    PYTHON_VER = "3"
except ImportError:  # Python 2
    import Tkinter as tk
    import ttk
    import tkFont as font
    import tkFileDialog as filedialog
    import tkMessageBox as messagebox
    import tkSimpleDialog as simpledialog
    import ScrolledText as scrolledtext
    PYTHON_VER = "2"

from PIL import Image, ImageTk, ImageDraw, ImageFont
from ttkwidgets import CheckboxTreeview

import signal  # Shutdown signals
import sqlite3  # Was only used for error messages but needed sql. in front

try:
    import subprocess32 as sp
    SUBPROCESS_VER = '32'
except ImportError:  # No module named subprocess32
    import subprocess as sp
    SUBPROCESS_VER = 'native'
import threading

import sys
try:
    reload(sys)  # June 25, 2023 - Without these commands, os.popen() fails on OS
    sys.setdefaultencoding('utf8')  # filenames that contain unicode characters
except NameError:  # name 'reload' is not defined
    pass  # Python 3 already in unicode by default

import shutil
import json  # List and Dictionary storage to SQL column, Pickle or text file
import glob  # For globbing files in /tmp/mserve_ffprobe*
import time
import datetime
import re
import traceback  # To display call stack (functions that got us here)
import webbrowser
import requests  # retrieve YouTube thumbnail images
from io import BytesIO  # convert YouTube thumbnail images to TK image format
import random  # For FileControl() make_temp
import string  # For FileControl() make_temp
from collections import OrderedDict

from threading import Lock
critical_function_lock = Lock()

import pickle
from random import shuffle
import locale               # To set thousands separator as , or .
locale.setlocale(locale.LC_ALL, '')  # Use '' for auto locale selecting

# Dist-packages
import notify2              # send inotify over python-dbus
import numpy as np          # For image processing speed boost
from selenium import webdriver  # For YouTube Playlists
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException

# Dist-packages copied underneath .../mserve/ directory
import mutagen              # Get easy tags instead of ffprobe - testing stage

# mserve modules
import global_variables as g
if g.USER is None:
    print('mserve.py was forced to run g.init()')
    g.init()

import location as lc       # manage device music locations
import message              # manage dialog messages
import encoding             # CD ripping + Musicbrainz + cover art
import external as ext      # launch external programs
import image as img         # make_image()
import sql                  # SQLite3 functions DIFFERENT than bserve sql.py module
import monitor              # Display, Screen, Monitor and Window functions
import toolkit              # Functions for tkinter-tool kit interface
import timefmt as tmf       # Format date and time
import webscrape            # Get song lyrics via web scrape
import vu_pulse_audio       # Volume Pulse Audio class pulsectl.Pulse()
from calc import Calculator  # Big Number Calculator on Tools Dropdown Menu


# Poor man's locale circa 2020 stuff that needs to be upgraded
"""
https://stackoverflow.com/a/956084/6929343
    locale.setlocale(locale.LC_ALL, 'de_DE') # use German locale; 
name might vary with platform
On Windows, I think it would be something like:
    locale.setlocale(locale.LC_ALL, 'deu_deu')
MSDN has a list of language strings and of country/region strings

Aug 4/23 move to global_variables.py for locations.py to share.

CFG_DECIMAL_PLACES = 0      # 0 decimal place, eg "38 MB"
CFG_DIVISOR_AMT = 1000000   # Divide by million
CFG_DIVISOR_UOM = "MB"      # Unit of Measure becomes Megabyte
"""

# Global variables
RESTART_SLEEP = .3          # Delay for mserve close down - No longer used
KEEP_AWAKE_MS = 250         # Milliseconds between time checks loc_keep_awake()
META_DISPLAY_ROWS = 15      # Number of Metadata Rows displayed in frame
SCROLL_WIDTH = 14           # Scroll bar width, July 3, 2023 used to be 12
MON_FONTSIZE = 12           # Font size for monitor name
WIN_FONTSIZE = 11           # Font size for Window name
BIG_FONT = 18               # Font size not used
LARGE_FONT = 14             # Font size not used
MED_FONT = 10               # Medium Font size
#BTN_WID = 12               # Now from g. Width for buttons on main window
#BTN_WID2 = 12              # Now from g. Width for buttons on play window
#BTN_BRD_WID = 3            # Now from g. Width for button border
FRM_BRD_WID = 2             # Width for frame border
# TODO: Calculate g.PANEL_HGT (height)
#PANEL_HGT = 24             # Now from g. Height of Unity panel
SONG_LABEL_STR = "song"     # For bolding metadata variable in play_top

# Temporary directory work filenames
TMP_CURR_SONG = g.TEMP_DIR + "mserve_song_playing"
TMP_CURR_SAMPLE = g.TEMP_DIR  + "mserve_song_sampling"
TMP_CURR_SYNC = g.TEMP_DIR + "mserve_song_syncing"
TMP_FFPROBE = g.TEMP_DIR + "mserve_ffprobe"  # _a3sd24 appended
TMP_FFMPEG = g.TEMP_DIR + "mserve_ffmpeg.jpg"  # _2h7s6s.jpg appended
TMP_MBZ_GET1 = g.TEMP_DIR + "mserve_mbz_get1"
TMP_MBZ_GET2 = g.TEMP_DIR + "mserve_mbz_get2"
TMP_PRINT_FILE = g.TEMP_DIR + "mserve_print_file"  # _a5sd87 appended

''' Volume Meter IPC filenames. Change in vu_meter.py too '''
VU_METER_FNAME = g.TEMP_DIR + "mserve_vu-meter-mono.txt"  # Mono output
VU_METER_LEFT_FNAME = g.TEMP_DIR + "mserve_vu-meter-left.txt"  # Stereo Left
VU_METER_RIGHT_FNAME = g.TEMP_DIR + "mserve_vu-meter-right.txt"  # Stereo Right

''' Webscraping lyrics - three files '''
LYRICS_SCRAPE = g.TEMP_DIR + "mserve_scrape_*"

''' Mostly all the names. TMP_FFPROBE & TMP_FFMPEG have unique suffixes '''
''' VU_METER...FNAME are pipes that can't be removed. '''
TMP_ALL_NAMES = [TMP_CURR_SONG, TMP_CURR_SAMPLE, TMP_CURR_SYNC, TMP_FFPROBE+"*",
                 TMP_FFMPEG + "*", TMP_PRINT_FILE + "*", VU_METER_FNAME,
                 VU_METER_LEFT_FNAME, VU_METER_RIGHT_FNAME, LYRICS_SCRAPE,
                 lc.FNAME_TEST, lc.TMP_STDOUT+"*", lc.TMP_STDERR+"*",
                 lc.TMP_FTP_RETRIEVE+"*"]

# More names added later after lcs is initialized.

ENCODE_DEV = True  # Development encoding.py last disc ID recycled saving 63 secs
# When True also recycles mbz_get1_pickle and mbz_get2_pickle pass-back files
# TMP_MBZ_GET1A = g.TEMP_DIR + "mserve_mbz_get1_releases_json"
# TMP_MBZ_GET1B = g.TEMP_DIR + "mserve_mbz_get1_recordings_json"
# TMP_MBZ_GET1C = g.TEMP_DIR + "mserve_mbz_get1_release_by_id_results_json"
# TMP_MBZ_GET1D = g.TEMP_DIR + "mserve_mbz_get1_releases_with_work_json"
# TMP_MBZ_GET1E = g.TEMP_DIR + "mserve_mbz_get1_releases_with_dates_json"
# TMP_MBZ_GET1F = g.TEMP_DIR + "mserve_mbz_get1_release_by_id_error_json"
# TMP_MBZ_DEBUG = g.TEMP_DIR + "mserve_mbz_get1_dates_list"
# No variable   = g.TEMP_DIR + "mserve_mbz_get1_stdout
#     "               "         mserve_mbz_get1_pickle
#     "               "         mserve_mbz_get2_pickle
#     "               "         mserve_mbz_get2_stdout
# ALSO filenames: mserve_disc_get_stdout, mserve_encoding_artwork.jpg
# mserve_encoding_last_disc, mserve_encoding_pickle, mserve_gst_launch


KID3_INSTALLED = False  # Reset just before popup menu created
KID3_NAME = "Kid3 Audio Tagger"
KID3_COMMAND = "xrandr --dpi 144 && kid3 "  # Kid3 isn't HDPI yet
KID3_WIN_SIZE = "1280x736"  # Window size changed after program starts

FM_INSTALLED = False  # Reset just before popup menu created
FM_NAME = "Nautilus File Manager"  # No HDPI required.  Change to FM_NAME
FM_COMMAND = "nautilus"
FM_WIN_SIZE = "1000x600"  # Window size changed after program starts

LRC_INSTALLED = True  # Sep 3/23 - .lrc (Synchronized LyRiCs) file generation
XDOTOOL_INSTALLED = True  # Sep 26/23 - experimental youTubePlaylist
WMCTRL_INSTALLED = True  # Sep 27/23 - experimental youTubePlaylist

# Kill application.name: speech-dispatcher, application.process.id: 5529
DELETE_SPEECH = True  # Kill speech dispatcher which has four threads each boot.
CHROME_TMP_FILES = True  # Check Chrome temporary disk space with `du` command.

# Chrome os Linux Beta doesn't support .grid_remove() properly
GRID_REMOVE_SUPPORTED = True

# When unselecting song in music location, end song (if playing) and remove
# TODO: Unchecking current song in music location leaves music player silent.
# Must click song in chron tree to start new song.
LIBRARY_UNSELECT_REMOVE_PLAYING = True

# When checking song in music location, how does it go into currently playing list?
#LIBRARY_SELECT_INSERT_PLAY_HERE = False  # Not supported
LIBRARY_SELECT_INSERT_PLAY_NEXT = True
#LIBRARY_SELECT_INSERT_PLAY_RANDOM = False  # Not supported
#LIBRARY_SELECT_INSERT_PLAY_ORDER = False  # Not supported
'''
If an entire album or artist is inserted as anything but RANDOM
then a new function to randomize those songs just inserted should
be created.

When inserting "HERE" and then playing we need a way to start with
first song inserted when the default would be the last song inserted.

'''

# Select music files only, no artwork
# Moved to g.MUSIC_FILE_TYPES
# FILE_TYPES = [".mp3", ".m4a", ".mp4", ".wma", ".oga", ".ogg", ".flac", ".wav", ".PCM"]
NO_ART_STR = "No Artwork"
#PAUSED_STR = "|| Paused"  # < July 4, 2023 paused ImageDraw() text
# Unicode Character 'DOUBLE VERTICAL BAR' (U+23F8):  ⏸  # Too small
# Right half block + Left half block:  ▐ ▌  # Doesn't ImageDraw() properly
PAUSED_STR = "Pippim.\nmserve\nClick to\n!> Play"
NUMBER_PREFIX = "№ "            # UTF-8 (2116) + normal space
DIGIT_SPACE = " "             # UTF-8 (2007)

''' Music Location's top directory. E.G. /mnt/drive/home/user/Music/'''
START_DIR = ""
PRUNED_DIR = ""  # Same as START_DIR unless manually passing Music Artist

# noinspection SpellCheckingInspection
''' TODO: Start up announcement at 75% volume
    Setting should be for once a day. We don't want this dozens of times when
    we are developing and testing code. Need ~/.../mserve/last_start_time
$ pico2wave -w=/tmp/test.wav "m serve version 1.0"
$ aplay /tmp/test.wav
$ rm /tmp/test.wav
'''

TV_BREAK1 = 90          # Hockey TV commercial break is 90 seconds
TV_BREAK2 = 1080        # Hockey TV intermission is 18 minutes
TV_VOLUME = 60          # Hockey TV mserve play music at 60% volume level
TV_SOUND = "Firefox"    # Hockey broadcast is aired on Firefox browser

''' Update last access time after X % of song has been played. '''
ATIME_THRESHOLD = 80    # playing 80% of song updates last access to now.
# NOTE: FF and Rewind buttons reset time played to 0.
#       Simply getting metadata or artwork always resets access time to
#       the original time making it "untouched" by mserve.

# Number of seconds to Rewind or Fast Forward a song. Must be string
REW_FF_SECS = "10"
REW_CUTOFF = 12         # If current less than cutoff, play previous song

PRUNED_COUNT = 0  # sys arg topdir = 0, artist = 1, album = 2
COMPIZ_FISHING_STEPS = 100  # May 18, 2023 when 100 steps windows disappear
# for a few seconds & system freezes once. It was compiz 'place' window bug.

# When no artwork for song use this image file
ARTWORK_SUBSTITUTE = g.PROGRAM_DIR + "Be Creative 2 cropped.jpg"
# "Be Creative 2 cropped.png" is a 4.4 MB image 3120x3120

# NOTE: Slideshow only works when when ~/.local/share/mserve/SlideShow exists
SLIDE_SHOW = False  # Set to true to override album artwork with slideshow
SLIDE_SHOW_DIR = g.USER_DATA_DIR + os.sep + "SlideShow"
# all images in directory are cycled through as album artwork

WEB_PLAY = True  # Does directory ~/.local/share/mserve/YouTubePlaylists/ exist?
WEB_PLAY_DIR = g.USER_DATA_DIR + os.sep + "YouTubePlaylists"  # + playlist.name + ".csv"
# YouTube Resolution: default = 120x90(2.8K), hqdefault = 480x360(35.6K)
# mqdefault = 320x180
YOUTUBE_RESOLUTION = "mqdefault.jpg"  # 63 videos = 176.4 KB

# June 20, 2023 - Losing average of 4ms per sleep loop when play_top paused
#   Created new SLEEP_XXX constants but also create 'self.last_sleep_time'
# Sep. 07, 2023 - Drop SLEEP from 33 to 16 for faster VU meters. Separate
#   sleep cycle for artwork speed can be created. At twice speed artwork
#   rendering goes from 3% CPU to 6% CPU load.
SLEEP_PAUSED = 16       # play_top open but music paused
SLEEP_PLAYING = 16      # play_top is playing music
SLEEP_NO_PLAY = 16      # play_top closed, refresh_lib_top() running


def make_sorted_list(start_dir, toplevel=None, idle=None, check_only=False):
    """ Build list of songs on storage device beginning at 'start_dir'
        Insert '/<No Artist>' and or '/<No Album>' subdirectory names
        Called at startup and by refresh_acc_times()
        Use DelayedTextBox for status updates on long-running processes
        which doesn't appear if process shorter than a second.

        When check_only just ensure /Artist/Album/ levels have at least
        ten songs.

        TODO:
            for lcs.open_host don't walk directory tree, because it takes
            over a minute for 3,800 songs using FTP over Wifi.

            Inside location directory is ".../mserve/L999/last_sorted_list
            Open file and use it to build skeleton sorted list without
            last access times. Last play time still appears and applies for
            all locations.   

            send info.fact() message and begin long running update with
            FTP list files one directory at a time with callback for each
            file/directory instigating play top or lib top refresh.
        
        """

    ''' If system argument 1 is for random directory, we have no last location.
        It may not point to a music topdir, rather an Artist or Album. A single
        song cannot be passed because os.walk() returns nothing.

        TODO: 

        In os.walk() we process 100 ms at a time and call lib_top.after() 
        for 100 ms so album artwork keeps spinning.

    '''

    global PRUNED_COUNT  # No topdir. Started pointing at artist or album.
    global PRUNED_DIR    # The real topdir. E.G. = '../' or '../../'

    who = "mserve.py make_sorted_list() - "
    if NEW_LOCATION:
        # print('WIP:', start_dir, "may point to topdir, Artist or Album")
        pass

    #print(who + 'toplevel:',toplevel,'idle:',idle)
    work_list = []
    dtb = message.DelayedTextBox(title="Scanning music directories",
                                 toplevel=toplevel, width=1000)

    depth_count = [0, 0, 0]  # Count of songs at topdir, artist, album
    last_check = time.time()  # Time we last checked to enter idle loop
    next_check = last_check  # For PyCharm warning message
    if idle is not None:
        next_check = last_check + float(idle) / 1000
        print('last_check:', last_check, 'next_check:', next_check)
    idle_loops = 0  # How many times we idled while building list

    start_dir = unicode(start_dir)  # Get results in unicode
    loop_count = 0
    # What's the difference between unicode() and .encode('utf-8')?
    #   https://stackoverflow.com/questions/643694/
    #   what-is-the-difference-between-utf-8-and-unicode
    #print(who + "lcs.open_ftp:", lcs.open_ftp)
    if lcs.open_ftp:
        #print("mserve.py make_sorted_list() This is an FTP host")
        orig_list = ext.read_from_json(lc.FNAME_WALK_LIST)
        walk_list = []
        for lin in orig_list:
            sfx, subdirs, files = lin
            walk_list.append((os.path.join(lcs.open_topdir, sfx), subdirs, files))
    else:
        # Sep 5/23 - convert os.walk() to list in prep for using fake_paths_sizes
        walk_list = list(os.walk(start_dir, topdown=True))

    for subdir, dirs, files in walk_list:
        ''' subdir + files[i] = full path.  dirs are ignored '''

        curr_depth = subdir.count(os.sep) - start_dir.count(os.sep)
        ''' Limit search to files in 2 levels (/Artist/Album) '''
        if curr_depth == 2:
            # Sanity check - delete directories below TopDir/Artist/Album/
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

            # Take sub-path /Artist/Album + Song.xxx and build full path
            full_path = os.path.join(subdir, f)

            ''' July 13, 2023 - Test code from new sql.update_metadata2() '''
            # File and Directory names with ":", "?", "/" and "." replaced with "_"
            parts = full_path.split(os.sep)
            try:
                artist = parts[-3]
                album = parts[-2]
                title = parts[-1]
                legal_artist = ext.legalize_dir_name(artist)
                legal_album = ext.legalize_dir_name(album)
                legal_title = ext.legalize_song_name(title)
                if legal_artist != artist or \
                        legal_album != album or \
                        legal_title != title:
                    print("illegal names:", legal_artist, legal_album, legal_title)
            except IndexError:
                pass  # Skip legality test of files in root directory

            # There are depths with no files so must recalculate current depth
            #curr_depth = full_path.count(os.sep) - start_dir.count(os.sep)
            dtb.update(full_path)
            if os.path.splitext(f)[1].lower() not in g.MUSIC_FILE_TYPES:
                ''' TODO: .lrc files should be tracked stored in a list '''
                continue  # Not a music file

            # If FTP used don't waste time checking curlftpfs for ".isfile"
            if lcs.open_ftp or os.path.isfile(full_path):
                # Count song occurrences at this level
                work_level = full_path.count(os.sep) - start_dir.count(os.sep)
                depth_count[work_level] += 1

                ''' Were 100 files checked without success? '''
                loop_count += 1
                if check_only and loop_count > 100:
                    return work_list, depth_count  # song paths & file counts

                ''' If checking only for valid topdir success after 10 found '''
                if check_only and depth_count[2] > 10:
                    return work_list, depth_count  # song paths & file counts

                # Insert missing Artists and Albums directories into work_f
                work_f = f
                if NEW_LOCATION:
                    # print('WIP work_f, work_level:', work_f, work_level)
                    pass
                if work_level == 0:
                    # song sitting at Artist directory level
                    work_f = g.NO_ARTIST_STR + os.sep + g.NO_ALBUM_STR \
                             + os.sep + work_f
                if work_level == 1:
                    # song sitting at Album directory level
                    work_f = g.NO_ALBUM_STR + os.sep + work_f

                # Build full path name from root directory
                work_path = os.path.join(subdir, work_f)

                # Insert space in front of every / for proper sorting                   
                work_path = work_path.replace(os.sep, " " + os.sep)
                work_list.append(work_path)

    # Sort work list with fake ' /' inserted. Then normalize back to '/'
    work_list.sort()
    work_list = [w.replace(" " + os.sep, os.sep) for w in work_list]
    dtb.close()
    # print('make_sorted_list idle loop count:', idle_loops)

    if check_only:
        ''' less than 100 files and didn't find 10 music files at Album level '''
        return work_list, depth_count  # song paths & file counts

    ''' Check if NOT pointing at Topdir, eg An Artist or an Album is the target.
        If all three levels are zero, bail out because no music at all.
    '''
    PRUNED_DIR = START_DIR  # Needed to prune off /Artist Name/Album Name
    PRUNED_COUNT = 0

    if depth_count[0] == 0 and depth_count[1] == 0 and depth_count[2] == 0:
        return work_list, depth_count  # No songs, or started pointing at single song

    if depth_count[1] == 0 and depth_count[2] == 0:
        PRUNED_COUNT = 2  # Both "<No Artist>" and "<No Album>" forced inserts
    if depth_count[1] > 0 and depth_count[2] == 0:
        PRUNED_COUNT = 1  # "<No Album>" forced insert

    ''' Create the pseudo start directory - Probably more efficient way... '''
    for i in range(0, PRUNED_COUNT):
        #print("looping through prunes:", i)
        PRUNED_DIR = PRUNED_DIR[:-1]  # Remove os.sep from end
        last_sub_dir = PRUNED_DIR.rfind(os.sep)  # Find last os.sep
        PRUNED_DIR = PRUNED_DIR[:last_sub_dir] + os.sep  # Shorten path

    if PRUNED_COUNT > 0:
        work_list = [w.replace(os.sep + g.NO_ALBUM_STR, '') for w in work_list]
    if PRUNED_COUNT > 1:
        work_list = [w.replace(os.sep + g.NO_ARTIST_STR, '') for w in work_list]

    return work_list, depth_count


# ==============================================================================
#
#       Music Location Tree class - Define lib (library of music)
#
# ==============================================================================
class MusicLocTreeCommonSelf:
    """ Class Variables used by play_selected_list().
        Must appear before Music Location Tree() class
        
        TODO: Move suitable variables to FileControl().FileControlCommonSelf

    """

    def __init__(self):
        #def __init__(self, toplevel, song_list, sbar_width=14, **kwargs):

        self.killer = ext.GracefulKiller()  # Class to shut down
        self.calculator = None              # Big Number calculator object
        self.calc_top = None                # Top level for calculator
        self.debug_file = None              # ~/tmp/mserve_print_file_xxxxxxxx
        self.debug_title = None             # 
        self.debug_text = None              # ~/tmp/mserve_print_file_xxxxxxxx
        self.close_sleepers_in_progress = False  # Prevent multiple calls

        self.play_top = None                # Music player selected songs
        self.play_on_top = None             # Is play frame overtop library?
        self.secs_before_pause = None       # get_curr_ffplay_secs(
        self.current_song_path = None       # Full pathname can have utf-8 chars
        self.current_song_t_start = None    # time.time() started playing
        self.current_song_secs = None       # How much time played
        self.current_song_mm_ss_d = None    # time in mm:ss.d (decisecond)
        self.saved_DurationSecs = None      # self.play_ctl.DurationSecs
        self.saved_DurationMin = None       # Duration in Min:Sec.Deci
        self.song_set_ndx_just_run = None   # Song manually set, don't use 'Next'
        self.last_started = None            # self.ndx catch fast clicking Next
        self.play_opened_artist = None      # Play expanded artist in Library?
        self.play_opened_album = None       # Play expanded album in Library?

        # Below called with "python vu_meter.py stereo 2>/dev/null"
        self.vu_meter_pid = None            # Linux Process ID for vu_meter.py
        self.play_top_title = None          # Playlist: Xxx Xxx - mserve
        self.play_frm = None                # play_top master frame
        self.lyrics_on_right_side = True    # False = lyrics frame on bottom
        self.theme_bg = None                # hex_background color
        self.theme_fg = None                # hex_foreground color

        # Play Frame column 0
        self.art_width = 200                # Spinning art work initial size
        self.art_height = 200
        self.art_label = None               # Spinning art tkinter label widget
        self.start_w = 0                    # self.play_frm.winfo_reqheight()
        self.start_h = 0                    # self.play_frm.winfo_reqwidth()
        self.play_original_art = None       # Original Artwork before resizing
        self.play_resized_art = None        # self.play_resized_art.resize(
        self.play_current_song_art = None   # ImageTk.PhotoImage(..resized_art
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
        # Slide Show vars
        self.runSlideShow = False           # Files in ~/.../mserve/SlideShow?
        self.listSlideNames = []            # List of files in mserve/SlideShow
        self.nextSlideIndex = 0             # Current slide displayed in list
        if SLIDE_SHOW and os.path.isdir(SLIDE_SHOW_DIR):
            self.listSlideNames = os.listdir(SLIDE_SHOW_DIR)
            #print("len(self.listSlideNames):", len(self.listSlideNames))
            ''' TODO: python-magic to ensure only image files included'''
            if len(self.listSlideNames) > 1:
                self.runSlideShow = True
                for image in self.listSlideNames:
                    #print("image:", image)
                    pass


        ''' Volume slider above Metadata Display fields '''
        self.slider_frm = None              # Volume slider frame
        self.ffplay_slider = None           # volume slider above metadata vars
        self.ffplay_mute = None             # LEFT: 🔉 U+F1509
        self.ffplay_full = None             # RIGHT: 🔊 U+1F50A

        self.curr_ffplay_volume = None      # Retrieved from slider adjustments
        self.set_ffplay_sink_WIP = None     # Only one value handled at a time

        ''' Metadata Display fields under volume slider '''
        self.song_title_var = tk.StringVar()  # song title without # or extension
        self.song_first_date_var = tk.StringVar()  # Song's first year of release
        self.song_artist_var = tk.StringVar()  # Artist name (ellipses)
        self.song_album_artist_var = tk.StringVar()  # Album Artist name
        self.song_composer_var = tk.StringVar()  # Composer (ellipses)
        self.song_comment_var = tk.StringVar()  # Optional Comment (ellipses)
        self.song_album_var = tk.StringVar()  # Album name (ellipses)
        self.song_album_date_var = tk.StringVar()  # Album release year (copyright)
        self.song_genre_var = tk.StringVar()  # Genre
        self.song_disc_var = tk.StringVar()  # Disc Number e.g. "1/1", "2/3"
        self.song_track_var = tk.StringVar()  # Track Number e.g. "9/12"
        self.song_number_var = tk.StringVar()   # Playing song number in playlist
        self.song_progress_var = tk.StringVar()  # mm:ss.d of mm:ss song played

        self.song_compilation = tk.StringVar()  # "1" Yes, "0" No
        self.song_play_count = tk.StringVar()  # number of times played
        self.song_last_play_time = tk.StringVar()  # stored as float
        self.song_gapless_playback = tk.StringVar()  # "1" Yes, "0" No
        self.song_creation_time = tk.StringVar()  # YYYY-MM-DD HH:MM:SS
        self.song_access_time = tk.StringVar()  # date ago
        self.song_file_size = tk.StringVar()  # 99.99 MB

        ''' Aug 10/23 version 3 SQL columns:
        OsFileName, OsAccessTime, OsModifyTime, OsChangeTime, OsFileSize,
        ffMajor, ffMinor, ffCompatible, Title, Artist, Album, Compilation, 
        AlbumArtist, AlbumDate, FirstDate, CreationTime, DiscNumber, TrackNumber, 
        Rating, Genre, Composer, Comment, Hyperlink, Duration, Seconds, 
        GaplessPlayback, PlayCount, LastPlayTime, LyricsScore, LyricsTimeIndex 
        + EncodingFormat, DiscId, MusicBrainzDiscId, OsFileSize, OsAccessTime '''

        # Play frame VU meters - columns 2 & 3
        self.play_vu_meter_style = None     # 'led' = Use LED rectangles
        self.vu_width = None                # VU Meters (Left & Right channel
        self.vu_height = None               # width and height in pixels
        self.vu_meter_left = None           # tk.Canvas(self.play_frm...
        self.vu_meter_left_rect = None      # vu_meter_left.create_rectangle(
        self.vu_meter_right = None          # tk.Canvas(self.play_frm...
        self.vu_meter_right_rect = None     # vu_meter_right.create_r
        self.VU_HIST_SIZE = None            # History of six db levels
        self.vu_meter_left_hist = None      # Left & Right channel histories
        self.vu_meter_right_hist = None     # can be zero on race condition

        # Play frame # 3 (misleading frame number) - column 4
        self.lyrics_master_frm = None       # tk.Frame(self.play_frm child)
        self.lyrics_frm = None              # tk.Frame(self.lyrics_master_frm child)
        # The panel dynamically changes depending on Basic Time Index,
        # edit lyrics, webscrape lyrics, fine-tune time index, manual scroll
        self.lyrics_panel_label = None      # tk.Label(self.lyrics_frm,
        self.lyrics_panel_last_line = None  # Rebuild panel_text when changing
        self.lyrics_panel_scroll = None     # Auto / Time / Manual Scroll
        self.lyrics_panel_text = None       # 0% time, Line: 99 of 99
        # title_F3 is old stuff being removed this weekend (May 29-30, 2021)
        self.lyrics_scrape_pid = None       # Process ID for web scrape
        self.lyrics_edit_is_active = False  # song lyrics being edited?
        self.lyrics_train_is_active = False  # Basic time index training
        self.lyrics_train_start_time = None  # When basic training started
        self.lyrics_score_box = None        # tk.Text(self.lyrics_master_frm

        # Four tk.Canvas rounded rectangle buttons: Auto to Manual (a_m), 
        # Time to Manual (t_m), Manual to Auto (m_a) and Manual to Time (M_t):
        self.lyrics_panel_scroll_a_m_grid = None
        self.lyrics_panel_scroll_t_m_grid = None
        self.lyrics_panel_scroll_m_a_grid = None
        self.lyrics_panel_scroll_m_t_grid = None
        # rounded rectangle button widgets
        self.lyrics_panel_scroll_a_m = None  # Automatic to Manual
        self.lyrics_panel_scroll_t_m = None  # Timed (Synced) to Manual
        self.lyrics_panel_scroll_m_a = None  # Manual to Automatic
        self.lyrics_panel_scroll_m_t = None  # Manual to Timed (Synced)
        # Associated tooltips to rounded rectangle buttons
        self.lyrics_panel_scroll_widest = 0
        self.lyrics_panel_scroll_highest = 0
        self.lyrics_panel_hamburger = None
        self.lyrics_panel_hamburger_tt = None  # tooltip for hamburger menu
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
        self.work_DurationSecs = None       # self.play_ctl.DurationSecs
        self.work_Title = None              # self.play_ctl.Title (song name)
        self.work_line_count = None         # self.lyrics_line_count  # FUDGE FOR Time being...
        self.lyrics_scroll_rate = None      # 1.5 = Default auto scroll rate
        self.lyrics_time_scroll = None      # Use lyrics time index scrolling
        self.lyrics_auto_scroll = None      # Use auto scrolling
        self.lyrics_old_scroll = None       # Last scroll setting
        self.lyrics_scrape_done = None      # Signal we are done scrape
        self.lyrics_edit_start_time = None  # time.time()
        # Set cursor position in text box
        self.edit_current_cursor = None     # self.lyrics_score_box.index(INSERT)

        # Fine-tune class replaces dozens of variables and functions
        self.fine_tune = None               # instance of class FineTune()
        self.sync_paused_music = None       # Did sync force play to pause?

        # Pause/Play Button changes dynamically when pp_toggle() called
        self.pp_toggle_fading_out = False   # True = Pause button pressed
        self.pp_toggle_fading_in = False    # True = Play button pressed
        self.pp_state = "Playing"
        self.pp_play_text = "▶  Play"       # Can make global var because
        self.pp_pause_text = "❚❚ Pause"     # same text used other classes

        # Resume from previous state when mserve starts up
        self.resume_state = None            # Can be "Paused" or "Playing"
        self.resume_song_secs = None        # Position to start playing song

        ''' Play Top Button frame (_btn) and Buttons (_button) '''
        self.play_btn_frm = None            # tk.Frame(self.play_top, bg="LightGrey"
        self.long_running_process = None    # True = remove most buttons
        self.close_button = None            # tk.Button(text="✘ Close
        self.shuffle_button = None          # tk.Button(text=" 🔀 Shuffle",
        self.prev_button = None             # tk.Button(text="⏮  Previous"
        self.previous_text = "⏮  Previous"  # Appears when < 12 seconds played
        self.restart_text = "⏮  Restart"    # Appears when > 12 seconds played
        self.prev_button_text = None        # Contains one of above two strings
        self.rew_button = None              # tk.Button(text="⏪  -10 sec"
        self.com_button = None              # tk.Button(text="🏒  Commercial"
        self.pp_button = None               # tk.Button(text="▶  Play"
        self.int_button = None              # tk.Button(text="🏒  Intermission"
        self.ff_button = None               # tk.Button(text="⏩  +10 sec"
        self.next_button = None             # tk.Button(text=" Next ⏭ "
        # June 17, 2023: last track button emoji (u+23ee) ⏮
        # June 17, 2023: next track button 23ED ⏭

        ''' Variables for playing music instead of TV Commercials '''
        self.play_hockey_allowed = False    # False = FF and REW buttons instead
        self.play_hockey_active = None      # TV turned down and music play?
        self.play_hockey_secs = None        # Commercial = TV_BREAK1 seconds
        self.play_hockey_remaining = None   # init to self.play_hockey_secs
        self.play_hockey_t_start = 0.0      # time.time()
        self.gone_fishing = None            # Class: Shark eating man

        ''' Show/Hide Playlist Chronology button (Frame 4) '''
        self.chron_is_hidden = None         # True/False=Frame .grid_remove()/.grid()
        self.chron_button = None            # tk.Button(..."🖸 Hide Chronology"

        ''' Frame for Playlist Chronology '''
        self.chron_frm = None               # tk.Frame(self.play_top, bg="Black

        self.play_ctl = None                # instance of FileControl() class
        self.ltp_ctl = None                 # Location Tree Play sample song
        self.mus_ctl = None                 # SQL Music Table get metadata
        self.rip_ctl = None                 # encoding.py (rip) CD

        # Popup menu
        self.mouse_x = None                 # Mouse position at time popup
        self.mouse_y = None                 # window was opened. Screen(x,y)
        self.kid3_window = None             # Window ID returned by xdotool
        self.fm_window = None               # Window ID returned by xdotool

        self.parm = None                    # sys arg parameters called with
        
        # Keep open host awake variables. Note Locations() can keep awake too.
        self.awake_last_time_check = None  # time.time()
        self.next_active_cmd_time = None  # time.time + touchmin * 60

        ''' Refresh items - inotify '''
        self.last_inotify_time = None       # now
        self.next_message_time = None       # now + (60 * 20)

        ''' Rip CD class (separate module: encoding.py) '''
        self.rip_cd_class = None
        self.rip_last_disc = None           # For development purposes

        ''' Sample middle of song '''
        self.ltp_top = None                 # tk.Toplevel()
        self.ltp_paused_music = None        # We will resume play later

        ''' Play Chronology '''
        self.chron_tree = None              # ttk.Treeview Playlist Chronology
        self.chron_last_row = None          # Last row highlighted with cursor
        self.chron_last_tag_removed = None  # 'normal' or 'chron_sel' was removed for highlight
        self.chron_filter = None            # 'time_index', 'over_5', [ARTIST NAME]
        self.chron_attached = []            # list of attached chronology tree id's
        self.chron_detached = []            # list of detached id's to restore
        self.chron_org_ndx = None           # original song index 'self.ndx'

        ''' SQL Music Table viewer '''
        self.mus_top = None                 # SQL Music Viewer Top Window
        self.mus_view = None                # SQL Music Table Viewer Scrollbox
        self.mus_search = None              # Searching for no lyrics, no sync, etc.
        self.mus_view_btn1 = None           # ✘ Close
        self.mus_view_btn2 = None           # 🗑 Missing Metadata
        self.mus_view_btn3 = None           # 🗑 Missing Lyrics
        self.mus_view_btn4 = None           # 🗑 Lyrics UnSynced
        self.mus_view_btn5 = None           # ? Text Search
        self.mus_view_btn6 = None           # 🖸 Update Metadata
        self.mus_view_btn7 = None           # ∑ Summary

        ''' SQL History Table viewer '''
        self.his_top = None                 # SQL History Viewer Top Window
        self.his_view = None                # SQL History Table Viewer Scrollbox
        self.his_search = None              # 
        self.his_view_btn1 = None           # ✘ Close
        self.his_view_btn2 = None           # ? Configuration rows
        self.his_view_btn3 = None           # ? Encode CD rows
        self.his_view_btn4 = None           # 🗑
        self.his_view_btn5 = None           # ? Text Search
        self.his_view_btn6 = None           # 🖸
        self.his_view_btn7 = None           # ∑ Summary

        ''' SQL Location Table viewer '''
        self.lcs_top = None                 # SQL Location Viewer Top Window
        self.lcs_view = None                # SQL Location Table Viewer Scrollbox
        self.lcs_search = None              # 
        self.lcs_view_btn1 = None           # ✘ Close
        self.lcs_view_btn2 = None           # 🗑 Configuration rows
        self.lcs_view_btn3 = None           # 🗑
        self.lcs_view_btn4 = None           # 🗑
        self.lcs_view_btn5 = None           # ? Text Search
        self.lcs_view_btn6 = None           # 🖸
        self.lcs_view_btn7 = None           # ∑ Summary

        ''' SQL miscellaneous variables '''
        self.meta_scan = None               # Class for song metadata searching
        self.missing_artwork_dtb = None           # metadata searching delayed textbox
        # NOTE: self.view used for both SQL Music and SQL History.
        #       self.view is the left-click and right-click menu for single row
        self.view = None                    # Shared view for SQL Music and SQL History
        self.common_top = None              # Top level clone for SQL Music or History
        # NOTE: self.hdr_top is window opened drilling down into treeview heading too
        self.hdr_top = None                 # hdr, iid & scrollbox for create_window()
        self.view_iid = None                # Treeview IID of row ID clicked on
        self.scrollbox = None               # Used by self.create_window()

        ''' Tools - batch processing - make .lrc / copy files '''
        self.checked_loc_name = None        # Location name copied to
        self.checked_loc_topdir = None      # Top Directory copied to
        self.checked_in_progress = None     # Has batch processing begun?
        self.checked_opened_artist = None   # Did batch process open the artist?
        self.checked_opened_album = None    # Did batch process open the album?
        self.checked_hl_color = 'Orange'    # Highlight color for row processing

        ''' Global variables of active children '''
        self.play_top_is_active = False     # Playing songs window open?
        self.vu_meter_first_time = None     # Aug 3/23 Patch for VU meter height
        self.mus_top_is_active = False      # View SQL Music open?
        self.his_top_is_active = False      # View SQL History open?
        self.lcs_top_is_active = False      # View SQL Location open?
        self.hdr_top_is_active = None       # Did we open SQL drill down window?
        self.sync_paused_music = False      # Important this is False now
        self.loc_keep_awake_is_active = False   # Prevent remote host sleeping?

        self.saved_selections = []          # lib_tree song ids in playlist order
        # May 29, 2023 - sometimes saved_selections is a list and sometimes a tuple
        #   self.saved_selections = tuple(L)  # convert list back into tuple
        #   It should always be a list. No need for tuple conversion
        self.filtered_selections = []       # Filtered songs from Chronology Pane

        ''' Pending Playlist Updates from Checkbox Actions '''
        self.pending_frame = None           # Hidden frame between TV & buttons
        self.pending_grid_visible = False   # Is hidden frame visible now?
        self.pending_additions = []         # List of checkbox additions and
        self.pending_deletions = []         # deletions. Duplicates are removed.
        self.pending_add_cnt = 0            # Count of additions and deletes.
        self.pending_del_cnt = 0            # When both zero, grid removed.
        self.pending_add_cnt_var = None     # Additions count
        self.pending_add_song_var = None    # Last added song name
        self.pending_del_cnt_var = None     # Deletions count
        self.pending_del_song_var = None    # Last deleted song name
        self.pending_tot_add_cnt = 0        # Total changes made without being
        self.pending_tot_del_cnt = 0        # written to disk with "Save Playlist"
        self.pending_update_btn = None      # Update Playlist from checked Button
        self.pending_cancel_btn = None      # Cancel Playlist Update Button

        ''' Set volume slider '''
        self.tv_vol = None  # tvVolume() during Hockey TV commercials

        ''' Playlists stored in SQL database '''
        self.playlists = None  # Playlists() class
        self.title_suffix = None  # title_suffix used in two places below

        ''' Menu bars: File, Edit, View + space + playlist information '''
        self.file_menu = None
        self.edit_menu = None
        self.view_menu = None
        self.tools_menu = None
        self.playlist_bar = None

        ''' last_sleep_time for mor accurate 30 frames per second (fps) '''
        self.last_sleep_time = time.time()


class MusicLocationTree(MusicLocTreeCommonSelf):
    """ Create self.lib_tree = tk.Treeview() via CheckboxTreeview()

        Resizeable, Scroll Bars, select songs, play songs.

        If toplevel is not None then it is the splash screen to destroy.

    """

    def __init__(self, toplevel, song_list, sbar_width=14):

        MusicLocTreeCommonSelf.__init__(self)  # Define self. variables
        ext.t_init('MusicLocationTree() __init__(toplevel, song_list, sbar_width=14)')

        # If we are started by splash screen get object, else it will be None
        self.splash_toplevel = toplevel

        # Create our tooltips pool (hover balloons)
        self.tt = toolkit.ToolTips()
        lcs.register_tt(self.tt)  # Assign in Locations() class
        lcs.register_menu(self.enable_lib_menu)
        lcs.register_pending(self.get_pending_cnt_total)
        lcs.register_oap_cb(self.open_and_play_callback)
        # Register self.start_long_running_process
        # Register self.end_long_running_process
        lcs.register_FileControl(FileControl)  # Not used on Aug 7/23

        dtb = message.DelayedTextBox(title="Building music view",
                                     toplevel=None, width=1000)
        self.ndx = 0  # Start song index
        self.play_from_start = True  # We start as normal
        # self.fake_paths = song_list = SORTED_LIST = make_sorted_list(START_DIR)
        self.fake_paths = song_list  # Contains /<No Artist>/<No Album> fakes
        lcs.register_fake_paths(self.fake_paths)
        self.real_paths = []  # stripped out <No Artist> and <No Album>

        self.size_dict = {}
        if lcs.open_ftp:
            self.size_dict = ext.read_from_json(lc.FNAME_SIZE_DICT)

        self.lib_top = tk.Toplevel()
        self.lib_top_is_active = True
        self.ltp_top_is_active = False  # Sample song NOTICE DIFFERENT SPELLING
        self.lib_top.minsize(g.WIN_MIN_WIDTH, g.WIN_MIN_HEIGHT)

        lcs.register_parent(self.lib_top)  # Assign in Locations() class

        ''' Set program icon in taskbar '''
        img.taskbar_icon(self.lib_top, 64, 'white', 'lightskyblue', 'black')

        ''' Mount window at previously used location '''
        self.lib_top.minsize(width=g.BTN_WID * 10, height=g.PANEL_HGT * 4)
        ext.t_init("monitor.get_window_geom('library')")
        geom = monitor.get_window_geom('library')
        self.lib_top.geometry(geom)
        ext.t_end('no_print')  # June 13, 2023 - 0.0002460480

        self.lib_top.configure(background="Gray")
        self.lib_top.columnconfigure(0, weight=1)
        self.lib_top.rowconfigure(0, weight=1)

        ''' Create frames '''
        # tk.Frame uses small fonts for File/Edit/View menus
        #master_frame = tk.Frame(self.lib_top, bg="LightGrey", relief=tk.RIDGE)
        # ttk.Frame doesn't allow bg="LightGrey"
        master_frame = ttk.Frame(self.lib_top, padding=(5, 5, 5, 0))
        master_frame.grid(sticky=tk.NSEW)
        master_frame.columnconfigure(0, weight=1)
        master_frame.rowconfigure(0, weight=0)  # InfoCentre bar frame
        master_frame.rowconfigure(1, weight=1)  # treeview frame

        ''' Expanding/collapsing information centre Frame - PART I of II '''
        # noinspection SpellCheckingInspection
        self.banner_frm = tk.Frame(master_frame, bg="SkyBlue3", height=7)
        self.banner_frm.grid(row=0, column=0, sticky=tk.NSEW)
        self.build_banner_btn()  # Create thin horizontal ruler w/tooltip

        ''' CheckboxTreeview Frame '''
        frame2 = tk.Frame(master_frame)
        tk.Grid.rowconfigure(frame2, 0, weight=1)
        tk.Grid.columnconfigure(frame2, 0, weight=1)
        frame2.grid(row=1, column=0, sticky=tk.NSEW)  # June 15/23 was row=0

        ''' CheckboxTreeview List Box, Columns and Headings '''
        self.lib_tree = \
            CheckboxTreeview(frame2, show=('tree', 'headings'),
                             columns=("Access", "Size", "Selected", "StatTime",
                                      "StatSize", "Count", "Seconds",
                                      "SelSize", "SelCount", "SelSeconds"))
        # indices 3 (StatTime) to 9 (SelSeconds) are hidden.
        self.lib_tree.column("#0", width=630, stretch=tk.YES)  # 0='text' column
        self.lib_tree.heading(
            "#0", text="Click ▼ (collapse) ▶ (expand) an Artist or Album")
        self.lib_tree.column("Access", width=200, stretch=tk.YES)
        # TODO: When mserve gets metadata, but doesn't play song, keep old Access
        self.lib_tree.heading("Access", text="Count / Last Access or Played")
        self.lib_tree.column("Size", width=100, anchor=tk.E, stretch=tk.NO)
        self.lib_tree.heading("Size", text="Size " + g.CFG_DIVISOR_UOM + " ",
                              anchor=tk.E)
        self.lib_tree.column("Selected", width=50, anchor=tk.E, stretch=tk.YES)
        self.lib_tree.heading("Selected", text="Play № / Sel. MB ", anchor=tk.E)

        # Debug hidden columns by making them visible in Treeview:
        # Uncomment first pair of lines to show REGULAR columns, comment last pair
        # Uncomment last pair of lines to show HIDDEN columns, comment first pair
        w = 0
        s = tk.NO
        #w = 80
        #s = tk.YES

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

        # Give some padding between triangles and border, between tree & scroll bars
        self.lib_tree["padding"] = (10, 0, 10, 10)  # left, top, right, bottom

        ''' Expanding/collapsing information centre Frame - PART II of II '''
        self.info = InfoCentre(self.lib_top, self.lib_tree,
                               self.banner_frm, self.tt)

        pav.registerInfoCentre(self.info)  # Wasn't available earlier
        lcs.register_info(self.info)  # Assign in Locations() class
        lcs.register_get_thread(self.get_refresh_thread)  # Assign in Locations() class

        patterns = [("using directory:", "Green", "Black")]
        self.info.fact("mserve started using directory: " + g.MSERVE_DIR,
                       patterns=patterns)

        if lcs.open_touchcmd:
            text = 'Keeping Host awake with Touch command: ' + lcs.open_touchcmd + \
                   ' every: ' + str(lcs.open_touchmin) + ' minutes.'
            self.info.cast(text)

        ''' Create self.playlists '''
        # thread=self.get_refresh_thread,  # Passing function for each time window opens!
        self.playlists = Playlists(
            self.lib_top, apply_callback=self.apply_playlists, tooltips=self.tt,
            pending=self.get_pending_cnt_total, enable_lib_menu=self.enable_lib_menu,
            thread=self.get_refresh_thread, play_close=self.play_close,
            display_lib_title=self.display_lib_title, info=self.info)

        ''' Last File Access Time overrides. E.G. Look but do not touch. '''
        self.play_ctl = FileControl(self.lib_top, self.info,
                                    close_callback=self.close_lib_tree_song,
                                    get_thread=self.get_refresh_thread)


        #self.build_lib_menu()  # Menu bar with File-Edit-View dropdown submenus
        self.set_title_suffix()  # At this point (June 18, 2023) it will be "Favorites"

        ''' Window Title bar. E.G.
            AW17R3  🎵 757 songs, 279 selected  🖸 6626.3 MB used, 2602.1 MB selected - mserve
        '''
        self.lib_top.title("Music Server")
        #                       Loc     Songs   Time  Count sSize sSeconds
        #                       0       2       4     6     8     10
        self.lib_top_totals = ["", "", "", "", "", 0, 0, 0, 0, 0, 0]
        #                           1       3      5     7     9
        #                           Play    Space  Size  Secs  sCount
        self.lib_top_totals[0] = str(lcs.open_name)
        self.lib_top_totals[1] = ""  # Playlist name makes title too long
        self.lib_top_playlist_name = ""  # appended to lib_top.title after totals

        ''' Music Location Dropdown Menu references Playlists() and InfoCentre() '''
        self.build_lib_menu()  # Menu bar with File-Edit-View dropdown submenus

        ''' Treeview select item - custom select processing '''
        self.lib_tree_open_states = []  # State of collapsed/expanded artists & albums
        self.playlist_paths = []
        self.lib_tree.bind('<Button-1>', self.button_1_click)
        self.lib_tree.bind("<Button-3>", self.popup)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=(None, MED_FONT),
                        rowheight=int(MED_FONT * 2.2))
        row_height = int(MON_FONTSIZE * 2.2)
        style.configure("Treeview", font=g.FONT, rowheight=row_height)

        ''' Create images for checked, unchecked and tristate '''
        self.checkboxes = img.make_checkboxes(
            row_height - 8, 'black', 'white', 'DodgerBlue')  # SkyBlue3 not in Pillow
        self.lib_tree.tag_configure("unchecked", image=self.checkboxes[0])
        self.lib_tree.tag_configure("tristate", image=self.checkboxes[1])
        self.lib_tree.tag_configure("checked", image=self.checkboxes[2])

        ''' Create images for open, close and empty '''
        width = row_height - 9
        self.triangles = []  # list to prevent Garbage Collection
        img.make_triangles(self.triangles, width, 'black', 'grey')

        self.lib_tree.grid(row=0, column=0, sticky=tk.NSEW)

        ''' Configure tag for row highlight '''
        self.lib_tree.tag_configure('highlight', background='lightblue')
        self.lib_tree.bind('<Motion>', self.lib_highlight_row)
        self.lib_tree.bind("<Leave>", self.lib_leave_row)

        '''         B I G   T I C K E T   E V E N T
            Create Album/Artist/ OS Song filename Treeview 
        '''
        self.populate_lib_tree(dtb)

        ''' Treeview Scrollbars '''
        # Create a vertical scrollbar linked to the frame.
        v_scroll = tk.Scrollbar(frame2, orient=tk.VERTICAL, width=sbar_width,
                                command=self.lib_tree.yview)
        v_scroll.grid(row=0, column=1, sticky=tk.NS)
        self.lib_tree.configure(yscrollcommand=v_scroll.set)

        # Create a horizontal scrollbar linked to the frame.
        # noinspection SpellCheckingInspection
        ''' June 19, 2023 - Disable horizontal scroll for lib_top.tree 
            It might be needed for debugging hidden columns though. 
        h_scroll = tk.Scrollbar(frame2, orient=tk.HORIZONTAL, width=sbar_width,
                                command=self.lib_tree.xview)
        h_scroll.grid(row=1, column=0, sticky=tk.EW)
        self.lib_tree.configure(xscrollcommand=h_scroll.set)
        '''

        ''' Pending Playlist Updates from Checkbox Actions '''
        self.create_pending_frame(master_frame)  # Hides after creation

        ''' Treeview Buttons '''
        frame3 = tk.Frame(master_frame)
        frame3.grid_rowconfigure(0, weight=1)
        frame3.grid_columnconfigure(0, weight=0)
        frame3.grid(row=3, column=0, sticky=tk.E)  # May 28, 2023 was row=2

        ''' ▶  Play Button '''
        self.play_text = "▶  Play"  # Appears when play_top is closed
        self.lib_tree_play_btn = tk.Button(
            frame3, text=self.play_text, width=g.BTN_WID2 + 1,
            font=g.FONT, command=self.play_selected_list)
        self.lib_tree_play_btn.grid(row=0, column=0, padx=10, pady=5,
                                    sticky=tk.E)
        self.tt.add_tip(self.lib_tree_play_btn, "Play favorite songs.",
                        anchor="nw")

        ''' Refresh Treeview Button u  1f5c0 🗀 '''
        ''' 🗘  Update differences Button u1f5d8 🗘'''
        lib_refresh_btn = tk.Button(frame3, text="🗘 Refresh library", 
                                    width=g.BTN_WID2 + 2, font=g.FONT, 
                                    command=self.rebuild_lib_tree)
        lib_refresh_btn.grid(row=0, column=1, padx=10, pady=5, sticky=tk.E)
        self.tt.add_tip(lib_refresh_btn, anchor="nw",
                        text="Scan disk for songs added and removed.")

        ''' Rip CD Button 🖸 (1f5b8) '''
        lib_rip_cd_btn = tk.Button(frame3, text="🖸  Rip CD", width=g.BTN_WID2 - 4,
                                   font=g.FONT, command=self.rip_cd)
        lib_rip_cd_btn.grid(row=0, column=2, padx=10, pady=5, sticky=tk.E)
        self.tt.add_tip(lib_rip_cd_btn, anchor="nw",
                        text="Encode songs from Audio CD to music files.")

        ''' Help Button - 
            https://www.pippim.com/programs/mserve.html#HelpMusicLocationTree '''
        ''' ⧉ Help - Videos and explanations on pippim.com '''

        help_text = "Open new window in default web browser for\n"
        help_text += "videos and explanations on using this screen.\n"
        help_text += "https://www.pippim.com/programs/mserve.html#\n"

        lib_help_btn = tk.Button(
            frame3, text="⧉ Help", font=g.FONT, width=g.BTN_WID2 - 4,
            command=lambda: g.web_help("HelpMusicLocationTree"))
        lib_help_btn.grid(row=0, column=3, padx=10, pady=5, sticky=tk.E)
        if self.tt:
            self.tt.add_tip(lib_help_btn, help_text, anchor="ne")
            
        ''' ✘ Close Button '''
        self.lib_top.bind("<Escape>", self.close)
        self.lib_top.protocol("WM_DELETE_WINDOW", self.close)
        lib_close_btn = tk.Button(frame3, text="✘ Close", width=g.BTN_WID2 - 4,
                                  font=g.FONT, command=self.close)
        lib_close_btn.grid(row=0, column=4, padx=(10, 2), pady=5, sticky=tk.E)
        self.tt.add_tip(lib_close_btn, anchor="ne",
                        text="Close mserve and any windows mserve opened.")

        ''' Colors for tags '''
        self.ignore_item = None
        self.lib_tree.tag_configure(
            'play_sel', background='ForestGreen', foreground="White")
        self.lib_tree.tag_configure('popup_sel', background='yellow')
        self.lib_tree.tag_configure(
            'checked_sel', background=self.checked_hl_color)  # 'Orange'

        ''' Refresh last played 999 ago, every minute '''
        self.last_inotify_time = None  # Last time bubble message sent
        self.refresh_acc_times(first_time=True)  # Update last access time every 60 seconds

        dtb.close()  # Close our startup messages delayed text box
        self.lib_top.bind("<FocusIn>", self.handle_lib_top_focus)
        ext.t_end('no_print')  # May 24, 2023 - MusicLocationTree() : 1.0563580990
        # June 13, 2023 -    MusicLocationTree() init__(toplevel...): 1.3379859924

        ''' Check Chrome /tmp/ files - can be 5GB after few days '''
        self.check_chrome_tmp_files()

        ''' Load last selections and resume playing music from last session '''
        self.load_last_selections()  # Play songs in favorites or playlists

        ''' When load_last_selections() ends we need to enter idle loop
            until self.close() is called. '''
        while self.refresh_lib_top():  # Sleeps for 33ms
            if self.lib_top is None:
                break

    def build_banner_btn(self):
        """ Called from init in MusicLocationTree() class """
        # Use lambda because self.info.view() hasn't been defined yet.
        banner_btn = tk.Button(self.banner_frm, height=0, bg="SkyBlue3",
                               fg="black", command=lambda: self.info.view())
        banner_btn.place(height=7, width=7000)  # ...height of 7 override
        text = "▼ ▲ ▼ ▲  Expanding/Collapsing Information Centre  ▲ ▼ ▲ ▼ \n\n" +\
            "Click this ruler line and it expands to a large frame.\n\n" +\
            "Actions are displayed with the most recent at the top.\n\n" +\
            "You can also access using the 'View' Dropdown Menu and\n" +\
            "selecting the 'Information Centre option."
        self.tt.add_tip(banner_btn, text=text, anchor="sc",
                        visible_span=1000, extra_word_span=100,
                        visible_delay=150, fade_out_span=149)

    def build_lib_top_playlist_name(self):
        """ name goes into lib_top.title()
            self.playlists.open_name is inside Playlists() class
        """
        if self.playlists.open_name:
            self.lib_top_playlist_name = self.playlists.open_name.encode("utf-8")
        else:
            self.lib_top_playlist_name = str(lcs.open_code) + \
                ' - Default Favorites'

    def set_title_suffix(self):
        """ Define variable text depending on playlist or favorites opened. """
        if self.playlists.open_name:
            self.title_suffix = "Playlist: " + self.playlists.open_name
        else:
            self.title_suffix = "Favorites"  # title_suffix used in two places below

    def build_lib_menu(self):
        """
        Menu bars: File, Edit, View + space + playlist information
        Designed to be called from self.playlists.build_lib_menu()
        ABANDON second calls because they take 1.0 seconds to run. Only
        call once during self.lib_top window creation. Alternate method for
        status messages must be used. - June 15, 2023.
        """
        ext.t_init('self.lib_top.config(menu="")')
        #self.lib_top.config(menu=None)  # Destroy last version
        ext.t_end('no_print')  # 0.0000929832
        ext.t_init('mb = tk.Menu(self.lib_top)')
        mb = tk.Menu(self.lib_top)
        ext.t_end('no_print')  # 0.0001151562
        ext.t_init('lib_top.config(menu=mb)')
        # .config(menu=) used to be at end of function. Moving to top has no effect
        # Still first run is:  0.0247361660 seconds (Which still seems too long)
        # Subsequent runs are: 0.9895310402 seconds (Which is horribly long!)
        #                      1.0078911781
        #                      0.9450080395
        #                      0.9970889091
        self.lib_top.config(menu=mb)  # Full second to rerun
        #self.lib_top['menu'] = mb  # Also takes a full second to rerun
        ext.t_end('no_print')

        ''' Option names are referenced for enabling and disabling.
            Before changing an "option name", search "option name" occurrences. '''
        # File Dropdown Menu
        ext.t_init('self.file_menu = tk.Menu(mb)')
        self.file_menu = tk.Menu(mb, tearoff=0)
        self.file_menu.add_command(label="Open Location and Play", font=g.FONT,
                                   command=lcs.open, state=tk.DISABLED)
        self.file_menu.add_command(label="New Location", font=g.FONT,
                                   command=lcs.new, state=tk.DISABLED)
        self.file_menu.add_separator()

        self.file_menu.add_command(label="Open Playlist", font=g.FONT,
                                   command=self.playlists.open, state=tk.DISABLED)
        self.file_menu.add_command(label="New Playlist", font=g.FONT,
                                   command=self.playlists.new, state=tk.DISABLED)
        self.file_menu.add_command(label="Save Playlist", font=g.FONT,
                                   command=self.write_playlist_to_disk, state=tk.DISABLED)
        #self.file_menu.add_command(label="Save Playlist As…", font=g.FONT,
        #                           command=self.playlists.save_as, state=tk.DISABLED)
        self.file_menu.add_command(label="Close Playlist and Use Favorites", font=g.FONT,
                                   command=self.close_playlist, state=tk.DISABLED)
        self.file_menu.add_separator()  # NOTE: UTF-8 3 dots U+2026 …

        #self.file_menu.add_command(label="Save Play and Restart", font=g.FONT,
        #                           command=self.restart)
        # Uncomment above if heavy development changes needed for testing, beware:
        # of: SLOWDOWN BUG: https://gitlab.gnome.org/GNOME/gnome-shell/-/issues/2674
        # and: SLOWDOWN BUG: https://gitlab.gnome.org/GNOME/gnome-shell/-/issues/3125
        # The facts are apparent when you restart. To save time, just exit and type 'm'.

        self.file_menu.add_command(label="Save Favorites", font=g.FONT,
                                   command=self.write_playlist_to_disk, state=tk.DISABLED)
        self.file_menu.add_command(label="Exit and CANCEL Pending", font=g.FONT,
                                   command=self.exit_without_save, state=tk.DISABLED)
        self.file_menu.add_separator()

        self.file_menu.add_command(label="Save Play and Exit", font=g.FONT,
                                   command=self.close)

        mb.add_cascade(label="File", font=g.FONT, menu=self.file_menu)
        ext.t_end('no_print')  # 0.0009999275

        # Edit Dropdown Menu
        ext.t_init('self.edit_menu = tk.Menu(mb)')
        self.edit_menu = tk.Menu(mb, tearoff=0)
        self.edit_menu.add_command(
            label="Synchronize Location", font=g.FONT, state=tk.DISABLED,
            command=lambda: lcs.synchronize(self.start_long_running_process,
                                            self.end_long_running_process))
        self.edit_menu.add_command(label="Edit Location", font=g.FONT,
                                   command=lcs.edit, state=tk.DISABLED)
        self.edit_menu.add_command(label="Delete Location", font=g.FONT,
                                   command=lcs.delete, state=tk.DISABLED)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Rename Playlist", font=g.FONT,
                                   command=self.playlists.rename, state=tk.DISABLED)
        self.edit_menu.add_command(label="Delete Playlist", font=g.FONT,
                                   command=self.playlists.delete, state=tk.DISABLED)
        self.edit_menu.add_separator()
        # Volume for Hocker Commercials state will be enabled by get_hockey_state()
        self.edit_menu.add_command(label="Volume During TV Commercials",
                                   font=g.FONT, state=tk.DISABLED,
                                   command=self.set_tv_volume)

        mb.add_cascade(label="Edit", menu=self.edit_menu, font=g.FONT)
        ext.t_end('no_print')  # 0.0004191399

        ext.t_init('self.view_menu = tk.Menu(mb)')

        # View Dropdown Menu
        self.view_menu = tk.Menu(mb, tearoff=0)
        # If adding new view options, bump up variable Enable option from 3 to 4
        self.view_menu.add_command(label="Information Centre", font=g.FONT,
                                   command=self.info.view)
        self.view_menu.add_command(label="View Locations", font=g.FONT,
                                   command=lcs.view, state=tk.DISABLED)
        self.view_menu.add_command(label="View Playlists", font=g.FONT,
                                   command=self.playlists.view, state=tk.DISABLED)
        self.view_menu.add_separator()  # If countdown running, don't show options

        self.view_menu.add_command(label="SQL Music Table", font=g.FONT,
                                   command=self.show_sql_music)
        self.view_menu.add_command(label="SQL History Table", font=g.FONT,
                                   command=self.show_sql_hist)
        self.view_menu.add_command(label="SQL Location Table", font=g.FONT,
                                   command=self.show_sql_location)

        mb.add_cascade(label="View", menu=self.view_menu, font=g.FONT)
        ext.t_end('no_print')  # 0.0006351471

        ext.t_init('self.view_menu = tk.Menu(mb)')

        # Tools Dropdown Menu
        self.tools_menu = tk.Menu(mb, tearoff=0)
        # If new option, before Enable Hockey, go below bump option # from 0 to 1
        self.play_hockey_allowed = self.get_hockey_state()
        if self.play_hockey_allowed:
            text = "Enable FF/Rewind buttons"  # TODO: Make self.variable names
        else:
            text = "Enable TV Commercial buttons"
        self.tools_menu.add_command(label=text, font=g.FONT,
                                    command=self.toggle_hockey)
        self.tools_menu.add_command(label="Big Number Calculator", font=g.FONT,
                                    command=self.calculator_open)
        self.tools_menu.add_separator()  # If countdown running, don't show options

        self.tools_menu.add_command(label="Make LRC For Checked Songs", font=g.FONT,
                                    command=self.checked_make_lrc, state=tk.DISABLED)
        self.tools_menu.add_command(label="Copy Checked To New Location",
                                    font=g.FONT, command=self.checked_copy_files)
        self.tools_menu.add_separator()  # If countdown running, don't show options

        self.tools_menu.add_command(label="Debug Information", font=g.FONT,
                                    command=self.show_debug)

        self.tools_menu.add_command(label="Pulse Audio", font=g.FONT,
                                    command=self.show_pulse_audio)

        mb.add_cascade(label="Tools", menu=self.tools_menu, font=g.FONT)
        ext.t_end('no_print')  # 0.0006351471

        self.enable_lib_menu()

    def enable_lib_menu(self):
        """ Called from build_lib_menu() and passed to self.playlists to call.
            Also passed with lcs.register_menu(self.enable_lib_menu)
        :return: None """

        if not self.lib_top_is_active:
            return  # Shutting down, catch for Playlists() & Locations()

        ''' Quick and dirty solution for Locations Maintenance Window '''
        if lcs.main_top or self.checked_in_progress:
            # Location Maintenance window open or checked songs processing
            self.file_menu.entryconfig("Open Location and Play", state=tk.DISABLED)
            self.file_menu.entryconfig("New Location", state=tk.DISABLED)
            self.edit_menu.entryconfig("Edit Location", state=tk.DISABLED)
            self.edit_menu.entryconfig("Delete Location", state=tk.DISABLED)
            self.edit_menu.entryconfig("Synchronize Location", state=tk.DISABLED)
            self.view_menu.entryconfig("View Locations", state=tk.DISABLED)
            self.tools_menu.entryconfig("Make LRC For Checked Songs",
                                        state=tk.DISABLED)
            self.tools_menu.entryconfig("Copy Checked To New Location",
                                        state=tk.DISABLED)
        else:
            self.file_menu.entryconfig("Open Location and Play", state=tk.NORMAL)
            self.file_menu.entryconfig("New Location", state=tk.NORMAL)
            self.edit_menu.entryconfig("Edit Location", state=tk.NORMAL)
            self.edit_menu.entryconfig("Delete Location", state=tk.NORMAL)
            self.edit_menu.entryconfig("Synchronize Location", state=tk.NORMAL)
            self.view_menu.entryconfig("View Locations", state=tk.NORMAL)
            self.tools_menu.entryconfig("Make LRC For Checked Songs",
                                        state=tk.NORMAL)
            self.tools_menu.entryconfig("Copy Checked To New Location",
                                        state=tk.NORMAL)
        self.disable_playlist_menu()
        if self.playlists.top:  # If top level is open, everything disabled.
            return  # Playlist Maintenance is active

        if self.playlists.open_name:  # Is there a playlist open?
            # Can close even if pending counts but there will be confirmation inside
            #self.file_menu.entry config("Save Playlist As…", state=tk.NORMAL)
            self.file_menu.entryconfig("Close Playlist and Use Favorites",
                                       state=tk.NORMAL)

        if self.get_pending_cnt_total() == 0 and not self.checked_in_progress:
            # If nothing pending can open create new playlist, etc.
            self.file_menu.entryconfig("Open Playlist", state=tk.NORMAL)
            self.file_menu.entryconfig("New Playlist", state=tk.NORMAL)
            self.edit_menu.entryconfig("Rename Playlist", state=tk.NORMAL)
            self.edit_menu.entryconfig("Delete Playlist", state=tk.NORMAL)
            self.view_menu.entryconfig("View Playlists", state=tk.NORMAL)

        ''' Favorites are pending? '''
        if self.pending_add_cnt != 0 or self.pending_del_cnt != 0:
            # Do not want save option until pending is applied or cancelled
            return

        if self.playlists.open_name and self.get_pending_cnt_total() > 0:
            self.file_menu.entryconfig("Save Playlist", state=tk.NORMAL)
            #self.file_menu.entry config("Save Playlist As…", state=tk.NORMAL)

    def disable_playlist_menu(self):
        """ Called above and self.pending_apply() when changes made to Favorites
            Also called as soon as Checkbox processing starts. June 17, 2023 error
            message in self.playlists.new() and .open() are no longer needed now.
        """
        self.file_menu.entryconfig("Open Playlist", state=tk.DISABLED)
        self.file_menu.entryconfig("New Playlist", state=tk.DISABLED)
        self.file_menu.entryconfig("Save Playlist", state=tk.DISABLED)
        #self.file_menu.entry config("Save Playlist As…", state=tk.DISABLED)
        self.file_menu.entryconfig("Close Playlist and Use Favorites",
                                   state=tk.DISABLED)
        self.edit_menu.entryconfig("Rename Playlist", state=tk.DISABLED)
        self.edit_menu.entryconfig("Delete Playlist", state=tk.DISABLED)
        self.view_menu.entryconfig("View Playlists", state=tk.DISABLED)

    def apply_playlists(self, delete_only=False):
        """ Called from Playlists() class after 'new' or 'open' playlist
            with their method self.playlists.apply_callback()
            Also called when deleting playlist currently playing. """
        if delete_only:  # Deleted Playlist that was open
            self.pending_reset(ShowInfo=False)  # Just in case it was open.
            self.enable_lib_menu()
            self.load_last_selections()
            return  # Called by Playlists.delete() function

        self.save_last_selections(new_playlist=True)  # special save situation
        self.ndx = 0  # resume will set to last playing song
        self.saved_selections = []  # lib_tree id's in sorted play order
        self.playlist_paths = []  # full path names that need to be pruned
        self.clear_all_checks_and_opened()  # Clear in lib_tree (music library)
        # Above does lib_top.update_idletasks()
        self.lib_tree.update()  # If not done song_sel tags still visible
        # Above first time 0, second time 17
        self.lib_top.update()  # If not done song_sel tags still visible
        items = self.lib_tree.tag_has("song_sel")
        #print("len(song_sel) items:", len(items))
        items = self.lib_tree.tag_has("checked")
        #print("len(checked) items:", len(items))
        items = self.lib_tree.tag_has("tristate")
        #print("len(tristate) items:", len(items))
        items = self.lib_tree.tag_has("unchecked")
        #print("len(unchecked) items:", len(items))

        # Build playlist_paths using Music Ids
        for music_id in self.playlists.open_id_list:
            d = sql.music_get_row(music_id)
            if d is None:
                toolkit.print_trace()
                print("mserve.py build_lib_with_playlist() ERROR music_id missing:",
                      music_id)
                continue
            full_path = PRUNED_DIR + d['OsFileName']
            self.playlist_paths.append(full_path)
            ndx = self.real_paths.index(full_path)
            iid = str(ndx)
            self.saved_selections.append(iid)

        ''' Restore previous open states when we first opened grid '''
        self.get_open_states_to_list()
        self.set_all_checks_and_opened()

        if len(self.saved_selections) >= 2:
            self.play_from_start = False  # Continue playing where we left off
            self.play_selected_list()

    def close_playlist(self):
        """ Close running playlist and open favorites based on lib_tree. """
        if not self.playlists.close():
            ''' If user confirms, playlists.close() proceeds with:
                    self.play_close()  # close main playing window
                    self.display_lib_title()
            '''
            return  # Playlist changes haven't been saved yet

        # If there were any pending amounts, use chose not to save.
        self.pending_tot_add_cnt = self.pending_tot_del_cnt = 0
        self.pending_reset(ShowInfo=False)  # Just in case it was open.
        self.enable_lib_menu()
        self.load_last_selections()

    def handle_lib_top_focus(self, _event):
        """ When tvVolume() Slider, Playlists(), Locations(),
            FineTune(), or ltp AKA Sample Song windows are active,
            move them above Music Location Tree (lib_top).

            Credit: https://stackoverflow.com/a/44615104/6929343

        :param _event: Ignored
        :return: None """

        ''' Since lib_top took focus, reset play button text '''
        self.play_on_top = False
        self.set_lib_tree_play_btn()

        if self.tv_vol and self.tv_vol.top:
            self.tv_vol.top.focus_force()  # Get focus
            self.tv_vol.top.lift()  # Raise in stacking order

        if self.playlists.top:
            self.playlists.top.focus_force()  # Get focus
            self.playlists.top.lift()  # Raise in stacking order

        elif lcs.main_top:  # Location Maintenance Window
            lcs.main_top.focus_force()  # Get focus
            lcs.main_top.lift()  # Raise in stacking order

        ''' Synchronizing lyrics to time index controls music '''
        if self.fine_tune and self.fine_tune.top_is_active:
            #self.fine_tune.top_lift()  # Need name change....
            # Above steals focus and keyboard from other applications !
            self.fine_tune.top.focus_force()  # Uncomment July 25, 2023
            #self.fine_tune.top.lift()
            self.fine_tune_lift()

        ''' Big Number Calculator - Checks if self.calc_top active '''
        self.calculator_lift()  # Can still highlight row and invoke ltp

        ''' Sampling random song in lib_tree '''
        if self.ltp_top_is_active:
            self.lib_tree_play_lift()  # Focus and raise in stacking order

    def refresh_lib_top(self, tk_after=True):
        """ Wait until clicks to do something in lib_tree (like play music)
            NOTE: this would be a good opportunity for housekeeping
            TODO: Call refresh_acc_times() every 60 seconds
                  Sep 8/23 - higher priority now that FTP needs background
                  processing to retrieve files one at a time with callbacks.
        """

        if not self.lib_top_is_active:
            return False  # self.close() has set to None

        ''' Is system shutting down? '''
        if self.killer.kill_now:
            print('\nmserve.py refresh_lib_top() closed by SIGTERM')
            self.close()
            return False  # Not required because this point never reached.

        ''' Host down? (sshfs-fuse cannot be accessed anymore) '''
        if lcs.host_down:
            print('\nmserve.py refresh_lib_top() closed by host down.')
            self.close()
            return False

        ''' Always give time slice to tooltips '''
        self.tt.poll_tips()  # Tooltips fade in and out. self.info piggy backing
        pav.poll_fades()
        self.lib_top.update()  # process events in queue. E.G. message.ShowInfo()

        if not self.lib_top_is_active:  # Second check needed June 2023
            return False  # self.close() has set to None

        ''' Aug 5/23 - Make speedy version for calling in loops '''
        if not tk_after:
            return self.lib_top_is_active

        ''' sleep remaining time until 33ms expires '''
        now = time.time()  # June 20, 2023 - Use new self.last_sleep_time
        sleep = SLEEP_NO_PLAY - int(now - self.last_sleep_time)
        sleep = sleep if sleep > 0 else 1      # Sleep minimum 1 millisecond
        self.last_sleep_time = now
        self.lib_top.after(sleep)              # Sleep until next 30 fps time

        ''' Wrapup '''
        if not self.lib_top_is_active:  # Second check needed June 2023
            return False  # self.close() has set to None
        else:
            return True  # Go back to caller as success

    def create_pending_frame(self, master_frame):
        """ Define apply pending frame used when lib_tree boxes are checked """
        text = "Pending Playlist Updates from Checkbox Actions"
        self.pending_frame = tk.LabelFrame(
            master_frame, borderwidth=g.FRM_BRD_WID, text=text,
            relief=tk.GROOVE, font=('calibre', 13, 'bold'))
        self.pending_frame.grid(row=2, column=0, sticky=tk.NSEW)
        self.pending_frame.grid_columnconfigure(3, weight=5)  # Song name extra wide

        ms_font1 = g.FONT  # Temporary for error message
        ms_font2 = g.FONT  # Temporary for error message

        tk.Label(self.pending_frame, text='Addition Count:', font=ms_font1) \
            .grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        self.pending_add_cnt_var = tk.Label(self.pending_frame, font=ms_font2,
                                            text="0", padx=2, pady=2, fg="Green")
        self.pending_add_cnt_var.grid(row=0, column=1, sticky=tk.W)

        tk.Label(self.pending_frame, text='Last Added:', font=ms_font1,
                 padx=2, pady=2).grid(row=0, column=2, sticky=tk.W, padx=2)
        self.pending_add_song_var = tk.Label(self.pending_frame, text='', fg="Green",
                                             font=ms_font1, padx=2, pady=2)
        self.pending_add_song_var.grid(row=0, column=3, sticky=tk.W, padx=2, pady=2)

        tk.Label(self.pending_frame, text='Deletion Count:',
                 font=ms_font1).grid(row=1, column=0, sticky=tk.W, padx=2)
        self.pending_del_cnt_var = tk.Label(self.pending_frame, font=ms_font2,
                                            text="0", padx=2, pady=2, fg="Red")
        self.pending_del_cnt_var.grid(row=1, column=1, sticky=tk.W)

        tk.Label(self.pending_frame, text='Last Deleted:',
                 font=ms_font1, padx=2, pady=2).grid(row=1, column=2, sticky=tk.W, padx=2)
        self.pending_del_song_var = tk.Label(self.pending_frame, text='', fg="Red",
                                             font=ms_font1, padx=2, pady=2)
        self.pending_del_song_var.grid(row=1, column=3, sticky=tk.W, padx=2, pady=2)

        # Button that will cancel changes
        self.pending_cancel_btn = tk.Button(self.pending_frame, text='Cancel',
                                            command=self.pending_reset, font=ms_font1)
        self.pending_cancel_btn.grid(row=2, column=0, sticky=tk.W)
        self.tt.add_tip(self.pending_cancel_btn, anchor="nw",
                        text="Cancel changes. Playlist remains unchanged.")

        # Button that will apply changes
        self.pending_update_btn = tk.Button(self.pending_frame, text='Apply',
                                            command=self.pending_apply, font=ms_font1)
        # For some reason when applying deletions to playlist song starts playing???
        # lambda doesn't fix the problem though...
        #                                    command=lambda: self.pending_apply(),
        #                                    font=ms_font1)

        self.pending_update_btn.grid(row=2, column=1, sticky=tk.W)
        self.pending_update_btn.focus_force()  # First data entry field
        self.tt.add_tip(self.pending_update_btn, anchor="nw",
                        text="Temporarily update changes to playlist in memory.")

        ''' Remove grid for tracking playlist changes until lib_tree box checked. '''
        self.pending_grid_visible = True
        self.pending_remove_grid()
        self.lib_top.update_idletasks()

    def pending_remove_grid(self):
        """ After applying pending checkboxes in lib_tree remove popup frame. """
        if not self.pending_grid_visible:
            # July 6, 2023 - happens when closing playlist when changes not saved
            print("mserve.py pending_remove_grid() called but already invisible.")
            return
        self.pending_grid_visible = False
        if GRID_REMOVE_SUPPORTED:
            self.pending_frame.grid_remove()

    def pending_restore_grid(self):
        """ Popup frame to apply pending checkboxes in lib_tree """
        # When applying or canceling updates, restore open_states
        self.lib_tree_open_states = self.make_open_states()
        # NOTE: The very first check that restored the grid will appear
        #       As initially opened. All subsequent albums opened will
        #       be closed.
        if self.pending_grid_visible:
            toolkit.print_trace()
            print("mserve.py pending_restore_grid() called but already visible.")
            return
        if GRID_REMOVE_SUPPORTED:
            self.pending_frame.grid()
            self.pending_grid_visible = True

    def pending_apply(self):
        """
            The "play_sel" tag reveals if deleted iid is current self.ndx. This
            forces music to stop playing.

            TODO: When applying to new playlist, dropdown menu options become disabled
        """
        global DPRINT_ON
        DPRINT_ON = False  # Debug printing: 'dprint(*args)' calls 'print(*args)'

        dprint("\n==================== mserve.py self.pending_apply() ====================")

        ''' Step 1 - Establish current song iid & ndx '''
        dprint("\n''' Step 1 - Establish current song iid & ndx '''")

        if self.play_top_is_active:
            tag_selections = self.lib_tree.tag_has("play_sel")  # Tuple with Id
            current_playing_id = tag_selections[0]
            if len(tag_selections) != 1:
                dprint("mserve.py pending_apply() 'play_sel' tag count is not 1:",
                       len(tag_selections))
            if current_playing_id != self.saved_selections[self.ndx]:
                dprint("mserve.py pending_apply() current_playing_id:",
                       current_playing_id, "!= self.saved_selections[self.ndx]:",
                       self.saved_selections[self.ndx])
            current_playing_ndx = self.ndx
        else:
            ''' This could be fresh playlist with no self.saved_selections '''
            if len(self.saved_selections) > 1:
                current_playing_ndx = self.ndx  # When no play_top, self.ndx correct
                current_playing_id = self.saved_selections[self.ndx]
            else:
                current_playing_ndx = None
                current_playing_id = None

        # Older code would recreate self.saved_selections as tuple
        dprint("Checking type(self.saved_selections):", type(self.saved_selections))
        if not isinstance(self.saved_selections, list):
            dprint("type(self.saved_selections):", type(self.saved_selections),
                   "Forcing to <type 'list'>")
            self.saved_selections = list(self.saved_selections)

        dprint("current_playing_id:", current_playing_id)
        dprint("current_playing_ndx:", current_playing_ndx)
        current_playing_deleted = False

        dprint("current len(self.saved_selections):", len(self.saved_selections),
               " | current len(self.playlist_paths):", len(self.playlist_paths))
        new_song_count = len(self.saved_selections) + self.pending_add_cnt -\
            self.pending_del_cnt
        dprint("len(self.saved_selections) + pending_add_cnt - pending_del_cnt:",
               new_song_count)

        if new_song_count < 2:
            dprint("Playlist needs at least two songs.")
            message.ShowInfo(self.lib_top, thread=self.get_refresh_thread,
                             icon='warning', title="Cannot apply changes.",
                             text="Playlist needs at least two songs.")
            return

        ''' Step 2 - Delete songs from playlist '''
        dprint("\n''' Step 2 - Delete songs from playlist '''")
        prior_to_current_count = 0
        delete_play_ndx_list = []
        delete_ndx_list = []
        delete_music_ndx_list = []  # June 17, 2023 - Music Ids to be deleted

        for delete_iid in self.pending_deletions:

            delete_path = self.real_paths[int(delete_iid)]
            try:
                delete_play_path_ndx = self.playlist_paths.index(delete_path)
                delete_play_ndx_list.append(delete_play_path_ndx)
            except ValueError:
                toolkit.print_trace()
                print("Could not find song in playlist:", delete_path, "\n")
                continue

            try:
                delete_ndx = self.saved_selections.index(delete_iid)
                delete_ndx_list.append(delete_ndx)
                # Note delete_ndx is 1 less than Playlist Play Number
            except ValueError:
                toolkit.print_trace()
                print("Could not find iid in self.saved_selections:",
                      delete_iid, "\n")
                continue

            ''' Build list of music ids indices to be deleted '''
            if self.playlists.open_name:
                music_id = sql.music_id_for_song(delete_path[len(PRUNED_DIR):])
                if music_id == 0:
                    toolkit.print_trace()
                    print("sql.music_id_for_song(delete_path[len(PRUNED_DIR):])\n")
                else:
                    delete_ndx = self.playlists.open_id_list.index(music_id)
                    delete_music_ndx_list.append(delete_ndx)

            dprint("delete_iid:", delete_iid, "delete_ndx:", delete_ndx)
            dprint("delete_path:", delete_path)
            if delete_iid == current_playing_id:
                current_playing_deleted = True
                dprint("current_playing_deleted:", current_playing_deleted)
                self.wrapup_song()  # kill song if playing and collapse parents
            if delete_ndx < self.ndx:
                prior_to_current_count += 1  # self.ndx reduced by count
                dprint("prior_to_current_count:", prior_to_current_count)

        dprint("delete_play_ndx_list:", delete_play_ndx_list)
        dprint("delete_ndx_list     :", delete_ndx_list)
        dprint("delete_music_ndx_list   :", delete_music_ndx_list)

        if len(delete_play_ndx_list) != self.pending_del_cnt:
            dprint("len(delete_play_ndx_list) != self.pending_del_cnt")
            dprint(len(delete_play_ndx_list), "!=", self.pending_del_cnt)

        if len(delete_ndx_list) != self.pending_del_cnt:
            dprint("len(delete_ndx_list) != self.pending_del_cnt")
            dprint(len(delete_ndx_list), "!=", self.pending_del_cnt)

        for index in sorted(delete_play_ndx_list, reverse=True):
            # Code credit: https://stackoverflow.com/a/11303234/6929343
            del self.playlist_paths[index]  # File is: lc.FNAME_LAST_PLAYLIST
            dprint("deleting self.playlist_paths[index] in reverse order:", index)

        for index in sorted(delete_ndx_list, reverse=True):
            del self.saved_selections[index]
            dprint("deleting self.saved_selections[index] in reverse order:", index)

        ''' Delete music ids in reverse order from self.playlists.open_id_list '''
        if self.playlists.open_name:
            for index in sorted(delete_music_ndx_list, reverse=True):
                music_id = self.playlists.open_id_list[index]
                del self.playlists.open_id_list[index]
                d = sql.music_get_row(music_id)
                if d is None:
                    print("ERROR bad song getting deleted (no meta)")
                else:
                    self.playlists.open_size -= d['OsFileSize']
                    self.playlists.open_count -= 1
                    self.playlists.open_seconds -= d['Seconds']
                dprint("deleting self.playlists.open_id_list[index]" +
                       " in reverse order:", index)

        if delete_play_ndx_list != delete_ndx_list:
            dprint("mserve.py pending_apply():" +
                   " delete_play_ndx_list != delete_ndx_list")

        ''' Adjust currently playing song index (self.ndx) if necessary '''
        if prior_to_current_count > 0:
            # This test also solves problem when current_playing_ndx is None
            self.ndx = current_playing_ndx - prior_to_current_count
            self.last_started = self.ndx  # Prevents different song playing

        ''' Step 3 - Add songs to playlist '''
        dprint("\n''' Step 3 - Add songs to playlist '''")
        insert_at = self.ndx + 1  # Insert after current playing song

        insert_play_paths = []
        insert_music_ids = []
        for insert_iid in self.pending_additions:
            insert_path = self.real_paths[int(insert_iid)]
            insert_play_paths.append(insert_path)
            dprint("Building playlist path:", insert_path)

            ''' Build list of Music IDs to insert into self.playlists.open_id_list '''
            if self.playlists.open_name:
                #music_id = sql.music_id_for_song(insert_path[len(PRUNED_DIR):])
                d = sql.ofb.Select(insert_path[len(PRUNED_DIR):])
                if d is None:
                    print("Cannot process song when it hasn't been played (no meta)")
                else:
                    insert_music_ids.append(d['Id'])
                    self.playlists.open_size += d['OsFileSize']
                    self.playlists.open_count += 1
                    self.playlists.open_seconds += d['Seconds']
                    dprint("Building Music ID:", d['Id'],
                           self.playlists.open_loc_id,
                           self.playlists.open_code,
                           self.playlists.open_count,
                           self.playlists.open_seconds)

        if len(insert_play_paths) != self.pending_add_cnt:
            dprint("len(insert_play_paths) != self.pending_add_cnt")
            dprint(len(insert_play_paths), "!=", self.pending_add_cnt)

        if len(self.pending_additions) != self.pending_add_cnt:
            dprint("len(self.pending_additions) != self.pending_add_cnt")
            dprint(len(self.pending_additions), "!=", self.pending_add_cnt)

        if insert_at >= len(self.saved_selections):
            self.saved_selections.extend(self.pending_additions)
            self.playlist_paths.extend(insert_play_paths)
            if self.playlists.open_name:
                self.playlists.open_id_list.extend(insert_music_ids)
            dprint("Appending at end:", len(self.saved_selections),
                   "self.pending_additions:", self.pending_additions)
        else:
            self.saved_selections[insert_at:insert_at] = self.pending_additions
            # NEED to insert insert_music_id_list into act_music_id list in Playlists
            self.playlist_paths[insert_at:insert_at] = insert_play_paths
            if self.playlists.open_name:
                self.playlists.open_id_list[insert_at:insert_at] = insert_music_ids
            dprint("Inserting at insert_at:", insert_at,
                   " | self.pending_additions:", self.pending_additions)

        if self.pending_add_cnt > 0:
            dprint("First addition insert self.playlist_paths.index[insert_play_paths[0]]:")
            first_path = insert_play_paths[0]
            try:
                # NEED to build first_ndx from new field first_music_id
                first_ndx = self.playlist_paths.index(first_path)
                dprint("First addition inserted self.playlist_paths.index:", first_ndx)
                # June 7, 2023 - What's going on here??? first_ndx isn't being used!
                # Design was to devine insertion point into playlist_paths?
                dprint(first_path)
            except ValueError:
                dprint("First addition can't be inserted self.playlist_paths.index:",
                       first_path)

        else:
            dprint("self.pending_add_cnt is zero:", self.pending_add_cnt)

        if self.ndx < 0:
            dprint("mserve.py pending_apply() self.ndx is negative:", self.ndx)
            self.info.cast("mserve.py pending_apply() self.ndx is negative: " +
                           str(self.ndx), 'error')
            self.ndx = 0
            self.last_started = self.ndx  # Prevents different song playing

        if self.ndx >= len(self.saved_selections):
            dprint("mserve.py pending_apply() self.ndx:", self.ndx,
                   "greater than len(self.saved_selections) - 1:",
                   len(self.saved_selections) - 1)
            self.ndx = len(self.saved_selections) - 1
            self.last_started = self.ndx  # Prevents different song playing

        ''' Step 4 - Save total playlist change counts and reset '''
        dprint("\n''' Step 4 - Save total playlist change counts and reset '''")
        if current_playing_deleted:
            dprint("We cannot start up with same song, it's deleted")

        dprint("New len(self.saved_selections):", len(self.saved_selections),
               " | New len(self.playlist_paths):", len(self.playlist_paths))

        self.pending_tot_add_cnt += self.pending_add_cnt
        self.pending_tot_del_cnt += self.pending_del_cnt

        """ Enable dropdown menu options for new playlist in memory are already
            enabled by enable_playlists_menu:
            - Save Playlist
            - Save Playlist As...
            - Close Playlist (use Favorites)
        """
        if self.playlists.open_name:
            self.enable_lib_menu()
            self.file_menu.entryconfig("Save Playlist", state=tk.NORMAL)
            # Save Playlist As hasn't been written yet.
            #self.file_menu.entry config("Save Playlist As…", state=tk.DISABLED)
            self.file_menu.entryconfig("Exit and CANCEL Pending", state=tk.NORMAL)
        else:
            self.file_menu.entryconfig("Save Favorites", state=tk.NORMAL)
            self.file_menu.entryconfig("Exit and CANCEL Pending", state=tk.NORMAL)

        ''' Rebuild chronology treeview '''
        if self.play_top_is_active:  # Play window open?
            self.populate_chron_tree()  # Rebuild with new songs & without removed songs

        ''' Call reset which reads playlist in memory and applies to lib_tree'''
        str_add_cnt = str(self.pending_add_cnt)  # reset() will destroy values
        str_del_cnt = str(self.pending_del_cnt)  # reset() will destroy values
        add_del_str = ""
        if str_add_cnt != "0":
            add_del_str += "\t- " + str_add_cnt + " New song(s) added.\n"
        if str_del_cnt != "0":
            add_del_str += "\t- " + str_del_cnt + " Song(s) removed.\n"

        self.pending_reset(ShowInfo=False)  # Set tree open/close states
        self.lib_tree.update_idletasks()

        current_playing_ndx = self.ndx  # When no play_top, self.ndx is still correct
        current_playing_id = self.saved_selections[self.ndx]
        dprint("current_playing_id:", current_playing_id)
        dprint("current_playing_ndx:", current_playing_ndx)

        # NEED to broadcast with InfoCentre
        text = "Playlist changes applied to memory but not saved to storage yet.\n\n" +\
            add_del_str + "\n"

        self.info.cast(text, action='update')  # it's really 'add' and/or 'delete'

        message.ShowInfo(
            self.lib_top, thread=self.get_refresh_thread,
            align='left', title="Playlist changes applied.",
            text="Changes to checkboxes in Music Location saved in memory.\n\n" +
                 "Playlist in memory has been updated with:\n" +
                 add_del_str +
                 "\nPlaylist in storage has NOT been saved yet.")

        DPRINT_ON = False  # Turn off debug printing

    def get_refresh_thread(self):
        """ Refresh thread is used by functions that are waiting.
            The function is waiting for user input or long running process.
            Loop and call thread to allow other functions to keep running.
        """
        if self.play_top_is_active:
            thread = self.refresh_play_top
        elif self.lib_top_is_active:
            thread = self.refresh_lib_top
        else:
            thread = None  # June 26 2023 - Return None when destroyed
        return thread

    def pending_reset(self, ShowInfo=True):
        """ Pending Music Location Tree checkboxes have been processed. """
        # Rebuild checkboxes, selected totals, song play order numbers
        # Get current open states to reopen after cancel processing
        # Uncheck all artists, albums, songs and "song_sel" tags
        self.clear_all_checks_and_opened()  # Clear in lib_tree music library
        self.set_all_checks_and_opened()  # Rebuild using playlist in memory
        ''' Restore previous open states when we first opened grid '''
        self.apply_all_open_states(self.lib_tree_open_states)

        ''' When called from pending_apply(), no message to display '''
        if ShowInfo:
            message.ShowInfo(
                self.lib_top, thread=self.get_refresh_thread,
                align='left', title="Playlist changes cancelled.",
                text="Changes to checkboxes in Music Location reversed.\n" +
                     "Playlist in memory and storage remains unchanged.")

        # Reset lists and remove grid
        self.pending_additions = []
        self.pending_deletions = []
        self.pending_add_cnt = 0            # June 17, 2023 - needed to make new
        self.pending_del_cnt = 0            # self.playlists.open() happy.
        self.enable_lib_menu()  # Not enabling Open, New, etc. Changes to Default Favorites?
        self.pending_remove_grid()

    def populate_lib_tree(self, delayed_textbox):
        """ Add Artist, Album and Song to treeview listbox.
            Set tags "Artist", "Album" or "Song".
            Initialize artists expanded and albums collapsed.
            All songs are NOT selected. They will be selected LATER. """

        who = "mserve.py populate_lib_tree() - "
        LastArtist = ""
        LastAlbum = ""
        CurrAlbumId = ""  # When there are no albums?
        CurrArtistId = ""  # When there are no albums?
        level_count = [0, 0, 0]  # Count of Artists, Albums, Songs

        start_dir_sep = START_DIR.count(os.sep) - 1  # Number of / separators
        global PRUNED_COUNT
        # print(who + 'PRUNED_COUNT:', PRUNED_COUNT)
        start_dir_sep = start_dir_sep - PRUNED_COUNT

        for i, os_name in enumerate(self.fake_paths):

            ''' Sorted list removed subdirectory levels: self.fake_paths = 
                    [w.replace(os.sep + g.NO_ALBUM_STR + os.sep, os.sep) \
                        for w in work_list] '''
            groups = os_name.split(os.sep)
            Artist = groups[start_dir_sep + 1]
            Album = groups[start_dir_sep + 2]
            Song = groups[start_dir_sep + 3]

            if Artist != LastArtist:
                level_count[0] += 1  # Increment artist count
                opened = False  # New installation would be more concise view for user
                CurrArtistId = self.lib_tree.insert(
                    "", "end", text=Artist, tags=("Artist", "unchecked"), open=opened,
                    values=("", "", "", 0.0, 0, 0, 0, 0, 0, 0))
                #   Index:  0         2      4     6     8
                #   Name:   LastPlay  SelStr Size  Secs  sCount (s=Selected)
                #   Index:      1        3      5     7     9
                #   Name:       SizeStr  Time   Cnt   sSize sSeconds

                # Treeview bug inserts integer 0 as string 0, must overwrite
                self.tree_col_range_replace(CurrArtistId, 5, [0, 0, 0, 0, 0, 0])
                self.lib_tree.tag_bind(CurrArtistId, '<Motion>', self.lib_highlight_row)
                LastArtist = Artist
                LastAlbum = ""  # Force subtotal break for Album

            if Album != LastAlbum:
                level_count[1] += 1  # Increment album count
                opened = False  # New installation would be more concise view for user
                CurrAlbumId = self.lib_tree.insert(
                    CurrArtistId, "end", text=Album, tags=("Album", "unchecked"),
                    open=opened, values=("", "", "", 0.0, 0, 0, 0, 0, 0, 0))
                # 0=PlayTime, 1=Size MB, 2=Selected Str, 3=Time, 4=StatSize,
                # 5=Count, 6=Seconds, 7=SelSize, 8=SelCount, 9=SelSeconds
                # May 24, 2023 - open state wasn't specified before today
                # Treeview bug inserts integer 0 as string 0, must overwrite
                self.tree_col_range_replace(CurrAlbumId, 5, [0, 0, 0, 0, 0, 0])

                # Treeview bug inserts integer 0 as string 0, must overwrite
                self.tree_col_range_replace(CurrAlbumId, 5, [0, 0, 0, 0, 0, 0])

                self.lib_tree.tag_bind(CurrAlbumId, '<Motion>', self.lib_highlight_row)
                LastAlbum = Album

            ''' Build full song path from song_list[] '''
            level_count[2] += 1  # Increment song count
            full_path = os_name
            full_path = full_path.replace(os.sep + g.NO_ARTIST_STR, '')
            full_path = full_path.replace(os.sep + g.NO_ALBUM_STR, '')
            self.real_paths.append(full_path)

            if delayed_textbox.update(full_path):
                # delayed_textbox returns true only when visible otherwise
                # we are in quiet mode because not enough time has passed.
                self.lib_tree.see(CurrArtistId)
                self.lib_tree.update()

            ''' FTP override - cannot stat every file. Take size from list.
                Use sql last play time if it exists.
                If song never played then use lowest of sql creation time, 
                or sql last access time or sql last modified time.
            '''
            # os.stat gives us all of file's attributes

            ''' TODO: Get size from size_dict '''
            play_time = 0.0
            d = sql.ofb.Select(full_path[len(PRUNED_DIR):])
            if d:
                play_time = d['LastPlayTime']
            if lcs.open_ftp:
                size = self.size_dict.get(full_path, 0)
                if not play_time and d:
                    play_time = d['OsAccessTime']
            else:
                try:
                    stat = os.stat(full_path)  # Get file attributes
                    size = stat.st_size
                    if not play_time:
                        play_time = stat.st_atime
                except OSError:
                    print(who + "Could not stat:", full_path)
                    continue

            if size < g.MUSIC_MIN_SIZE:
                str_size = '{:n}'.format(g.MUSIC_MIN_SIZE)
                print(who + "Skipping file less than:", str_size,
                      "bytes. Filename below:")
                print(" " + full_path)
                continue  # Causes error because in sorted_list

            self.tree_col_range_add(CurrAlbumId, 5, [size, 1])
            self.tree_col_range_add(CurrArtistId, 5, [size, 1])
            self.tree_title_range_add(5, [size, 1])  # update title bar
            converted = float(size) / float(g.CFG_DIVISOR_AMT)
            fsize = '{:n}'.format(round(converted, g.CFG_DECIMAL_PLACES))

            # Format date as "Abbreviation - 99 Xxx Ago"
            ftime = tmf.ago(float(play_time), seconds=True)

            ''' Add the song '''
            self.lib_tree.insert(
                CurrAlbumId, "end", iid=str(i), text=Song, tags=("Song", "unchecked"),
                values=(ftime, fsize, '', float(play_time), size, 1, 0, 0, 0, 0))
            # Dec 28 2020 - Selected Size is now Song Sequence Number
            # 0=PlayTime, 1=Size MB, 2=Selected Str, 3=Time, 4=StatSize,
            # 5=Count, 6=Seconds, 7=SelSize, 8=SelCount, 9=SelSeconds
            self.tree_col_range_replace(str(i), 6, [1, 0, 0, 0, 0])
            self.lib_tree.tag_bind(str(i), '<Motion>', self.lib_highlight_row)

        self.display_lib_title()  # Was called thousands of times above.

    @staticmethod
    def lib_highlight_row(event):
        """ Cursor hovering over row highlights it in light blue """
        tree = event.widget
        item = tree.identify_row(event.y)
        tree.tk.call(tree, "tag", "remove", "highlight")
        tree.tk.call(tree, "tag", "add", "highlight", item)

    @staticmethod
    def lib_leave_row(event):
        """ Un-highlight row just left """
        tree = event.widget
        tree.tk.call(tree, "tag", "remove", "highlight")

    def toggle_select(self, song, album, artist):
        """ Toggle song selection off and on. Update selected values and
            roll up totals into parents. Only called when manually checking
            boxes. Never called for batched checkbox processing on load or
            Process Pending functions.
        """
        # 0=PlayTime, 1=Size MB, 2=Selected Str, 3=Time, 4=StatSize,
        # 5=Count, 6=Seconds, 7=SelSize, 8=SelCount, 9=SelSeconds
        # Set slice to StatSize, Count, Seconds
        total_values = slice(4, 7)  # start at index, stop before index
        #select_values = slice(7, 10)  # start at index, stop before index

        tags = self.lib_tree.item(song)['tags']
        if "song_sel" in tags:
            # We will toggle off and subtract from selected parent totals
            old = self.lib_tree.item(song)['values'][2]  # "Selected" column ndx 2
            if old == "Adding":
                self.lib_tree.set(song, "Selected", "")  # Reset to nothing
            else:
                self.lib_tree.set(song, "Selected", "Deleting")  # Will be deleted
            tags.remove("song_sel")
            self.lib_tree.item(song, tags=tags)
            # noinspection PyProtectedMember
            self.lib_tree._uncheck_ancestor(song)  # in CheckboxTreeview()
            # Get StatSize, Count and Seconds multiplying by negative 1
            adj_list = [element * -1 for element in
                        self.lib_tree.item(song)['values'][total_values]]
            # [total_values] = slice(4,7)
        else:
            # Toggle on and add to selected parent totals
            tags.append("song_sel")
            try:
                song_number = self.saved_selections.index(song) + 1
                number_str = play_padded_number(
                    song_number, len(str(len(self.saved_selections))))
            except ValueError:
                # print('mserve.py toggle_select(): song not found iid:', song)
                number_str = "Adding"  # Number will be assigned when inserted

            self.lib_tree.set(song, "Selected", number_str)
            self.lib_tree.item(song, tags=tags)
            # noinspection PyProtectedMember
            self.lib_tree._check_ancestor(song)  # in CheckboxTreeview()
            # Get StatSize, Count and Seconds
            adj_list = self.lib_tree.item(song)['values'][total_values]  # 1 past

        self.tree_col_range_add(song, 8, adj_list)  # Column number passed
        self.tree_col_range_add(album, 8, adj_list, tagsel='album_sel')
        self.tree_col_range_add(artist, 8, adj_list, tagsel='artist_sel')
        self.tree_title_range_add(8, adj_list)  # Pass start index
        self.display_lib_title()  # Format sizes and selected in title bar


    def tree_col_range_replace(self, iid, numb, init_list, tagsel=None):
        """ Initialize treeview columns to list of values
        """
        for i, new_val in enumerate(init_list):
            col_str = "#" + str(numb + i)  # eg '#3'
            self.lib_tree.set(iid, col_str, new_val)

        if tagsel:
            self.tree_col_parent_format(iid, tagsel)

    def tree_col_range_add(self, iid, numb, add_list, tagsel=None):
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

        # Human readable size. eg 12345678 becomes 12 MB
        size = self.lib_tree.set(iid, "StatSize")
        converted = float(size) / float(g.CFG_DIVISOR_AMT)
        all_sizes = '{:n}'.format(round(converted, g.CFG_DECIMAL_PLACES))
        # all_sizes of 1824.5 but should be 1,824.5
        size = self.lib_tree.set(iid, "SelSize")
        converted = float(size) / float(g.CFG_DIVISOR_AMT)
        all_selected = '{:n}'.format(round(converted, g.CFG_DECIMAL_PLACES))

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

    def tree_title_zero_selected(self):
        """ Called before batch update that calculates selected for entire
            playlist.
                 8 = (SelSize)
                 9 = (SelCount)
                10 = (SelSeconds)
        """
        # Copy and paste legend into code for guidance
        #                       Loc     Songs   Time    Count sSize sSeconds
        #                       0       2       4       6     8     10
        # self.lib_top_totals=[ "", "", "", "", "",  0, 0, 0, 0, 0, 0 ]
        #                           1       3        5     7     9
        #                           Play    Space    Size  Secs  sCount

        self.lib_top_totals[8] = 0
        self.lib_top_totals[9] = 0
        self.lib_top_totals[10] = 0

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
        # self.lib_top_totals=[ "", "", "", "", "",  0, 0, 0, 0, 0, 0 ]
        #                           1       3        5     7     9
        #                           Play    Space    Size  Secs  sCount

        for i, add_val in enumerate(add_list):
            ndx = start_ndx + i
            # After working check if += add_list inserts rather than adds
            # self.lib_top_totals[ndx] = self.lib_top_totals[ndx] + add_list[i]
            self.lib_top_totals[ndx] += add_list[i]

    def display_lib_title(self):
        """ Format sizes, selected and playlist name in title bar.
            Called after lib_top_totals are built and when playlist changes
            In case playlist was renamed, update play_top.title
        """
        if not self.lib_top_is_active:
            return  # June 19, 2023 - throw in the towel debugging errors below

        if self.play_top_is_active:  # These three lines repeated when play_top
            self.set_title_suffix()  # is created. Consider shared function.
            self.play_top_title = "Playing " + self.title_suffix + " - mserve"
            self.play_top.title(self.play_top_title)

        if self.lib_top is None:
            toolkit.print_trace()  # Can't figure out - causes error lib_top.title()
            # File "/home/rick/python/mserve.py", line 7830, in refresh_play_top
            #     self.play_top.update()           # Sept 20 2020 - Need for lib_top
            # File "/usr/lib/python2.7/lib-tk/Tkinter.py", line 1022, in update
            #     self.tk.call('update')
            # File "/usr/lib/python2.7/lib-tk/Tkinter.py", line 1540, in __call__
            #     return self.func(*args)
            # File "/home/rick/python/mserve.py", line 13455, in apply
            #     self.display_lib_title()  # Important that self.name is ACCURATE
            # File "/home/rick/python/mserve.py", line 2422, in display_lib_title
            #     toolkit.print_trace()
            # File "/home/rick/python/toolkit.py", line 60, in print_trace
            #     for line in traceback.format_stack():
            # self.lib_top is None
            print("self.lib_top is None")
            return

        # Put counts into title bar
        song_count = self.lib_top_totals[6]
        selected_count = self.lib_top_totals[9]

        # Human-readable size 12345678 becomes 12.3 MB
        human_all_sizes = toolkit.human_bytes(self.lib_top_totals[5])
        human_selected = toolkit.human_bytes(self.lib_top_totals[8])
        # Default format for NO songs selected
        self.lib_top_totals[2] = \
            "   🎵 " + '{:n}'.format(song_count) + ' songs.'
        self.lib_top_totals[3] = "   🖸 " + human_all_sizes + " used."

        if selected_count > 0:
            # Extend format for at least one song selected
            self.lib_top_totals[2] += " "+'{:n}'.format(selected_count) + ' selected.'
            self.lib_top_totals[3] += " " + human_selected + ' selected.'

        self.build_lib_top_playlist_name()  # More verbose than self.title_suffix
        s = "   ☰ " + self.lib_top_playlist_name + " - mserve"
        self.lib_top.title(self.lib_top_totals[0] + self.lib_top_totals[1] +
                           self.lib_top_totals[2] + self.lib_top_totals[3] + s)

    def loc_keep_awake(self):
        """ Every x minutes issue keep awake command for server. For example:
            'ssh dell "touch /tmp/mserve_client.time"'

            Recursive call to self

            For Debugging, run the following commands on the host and client:

            HOST - Open a terminal and enter command which runs forever:
              mserve_client.sh -d

            CLIENT - Open a terminal, and paste below, replacing "<HOST>" with Host name:
              while : ; do ssh <HOST> "cat /tmp/mserve_client.log" ; sleep 60 ; done
        """

        if not self.loc_keep_awake_is_active:
            return  # mserve.py is shutting down

        self.awake_last_time_check = time.time()
        if self.awake_last_time_check > self.next_active_cmd_time:
            ''' Test if Host still connected before sending touch command '''
            test_passed = lcs.test_host_up()  # Quick & dirty nc test
            if not self.loc_keep_awake_is_active:
                return  # Shutting down now
            if test_passed is False:
                mount_point = lcs.open_mountcmd  # Extract '/mnt/music' at end
                mount_point = mount_point.split()[-1]  # last part after space
                title = "Remote Host Disconnected!"
                text = lcs.open_name + " is off-line. Shutting down...\n\n"
                text += "'sshfs' MAY leave drive mounted for 15 minute timeout.\n"
                text += "Try: 'fusermount -u " + mount_point + "\n\n"
                text += "You can also try 'sshfs -o reconnect' option.\n\n"
                text += "OR... reboot, or do 15 minutes of other other work."
                text += "\n15 minute sshfs-fuse bug reportedly fixed Oct 27 2017:"
                text += "\nhttps://bugs.launchpad.net/ubuntu/+source/sshfs-fuse/+bug/912153"

                ''' Cannot show message because other threads keep closing? '''
                print(title + "\n" + text)
                lcs.out_cast_show_print(title, text, 'error')  # CRASHES
                # July 30, 2023, restarting will access /mnt/music and stall
                # If host suspends when mserve running, use 'ssh-activity -d'.
                lcs.host_down = True  # Don't close files on frozen sshfs-fuse
                self.close()  # Shutdown.  Could try to wakeup host one time...

                """  Experiments below 
                USING RECONNECT AFTER DROP MAKES EMPTY MOUNT BELOW:
                https://serverfault.com/a/639735
                
                Use -o reconnect,ServerAliveInterval=15,ServerAliveCountMax=3
                
                https://serverfault.com/a/924787

                Can receive broadcast message when system going down:
                    you can use nc for example in receiving host type:
                    nc -l port_number and in sending host type:
                    nc ip port_number like:
                        nc -l 3106
                    in receiving host and
                        nc 192.168.32.98 3106
                    in sending host
                """

                '''
                  When resuming after long system suspend:

                    Host: dell is off-line. Quiting...
                    Checking to save: /home/rick/.../mserve/last_location
                    No 'iid' found in 'LODICT' for: /mnt/music/
                    ssh: connect to host dell port 22: No route to host
                    
                    FIXED NOW I THINK because this function was broken:
                                lc.save_mserve_location(iid)

                    FIXED AGAIN (Nov 12 2020) because 'return' added above.

                    Nov 12 2020 - About 10 to 15 minutes after resuming got bubble
                    message: Library has changed and files need refreshing. Then
                    on command line:

                        last message time: 1605229131.81 next message time: 1605230331.81
                        refresh_acc_times(): 931.62436986
                        Host: dell is off-line. Quiting...

                    Did not issue kill -9. Did not see Disk Wait+ status. FTR
                    931 seconds = 15.5 minutes. Bottom line refresh_acc_times()
                    must poll connection before issuing os.walk(). Also why
                    does it wake up before loc_keep_awake? Can it test
                    loc_keep_awake()'s last time?
                '''

            # Host is awake. Set next test time.
            result = os.popen(lcs.open_touchcmd).read().strip()
            lcs.save_touch_time()  # SQL history 'location' 'last' w/timestamp
            if len(result) > 4:  # Did nc -z have error results?
                title = "mserve.py .loc_keep_awake()"
                text = "Running command: 'nc -z " + lcs.open_host + " 22'"
                text += "\n\nReceived unexpected results show below:\n\n"
                text += result
                lcs.out_cast_show_print(title, text, 'error')
            self.awake_last_time_check = time.time()
            self.next_active_cmd_time = self.awake_last_time_check + (60 * lcs.open_touchmin)

            title = "Keeping Remote Host awake."
            text = "Running: " + lcs.open_touchcmd + "\n"
            text += "  | This time: " + ext.t(self.awake_last_time_check)
            text += "  | Next time: " + ext.t(self.next_active_cmd_time)
            lcs.out_fact(title, text, 'info')

            if not self.loc_keep_awake_is_active:
                return  # mserve.py is shutting down

        # noinspection PyBroadException
        try:
            # Was running root.after every 1/4 second, change every minute and
            # got lock up in refresh_acc_times() running first.  On file server
            # this was causing 'ps' status 'D+' (Disk Sleep foreground) and
            # program could not be killed for 15 min when resuming from suspend.
            self.lib_top.after(KEEP_AWAKE_MS, self.loc_keep_awake)
        except:
            # pass
            return

    # ==============================================================================
    #
    #       MusicLocationTree Processing - Select items, Popup Menus
    #
    # ==============================================================================

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

        ''' Set object for warning messages below. '''
        if self.lib_tree.tag_has("Artist", item):
            line_type = "Artist"
        elif self.lib_tree.tag_has("Album", item):
            line_type = "Album"
        else:
            line_type = None

        ''' Warning if status is tri-state, all will be selected. '''
        if self.lib_tree.tag_has("tristate", item):  # tristate = artist / album
            dialog = message.AskQuestion(
                self.lib_top, thread=self.get_refresh_thread,
                title="Discard custom unchecked?",
                text="All songs under " + line_type + " will be checked.\n" +
                     "Some Songs are unchecked and will be checked.")
            if dialog.result != 'yes':
                return

        ''' Warning if unchecking line_type all children will be unchecked. '''
        if self.lib_tree.tag_has("checked", item) and line_type:
            dialog = message.AskQuestion(
                self.lib_top, thread=self.get_refresh_thread,
                title="Uncheck all songs below?",
                text="All songs under " + line_type + " will be unchecked.")
            if dialog.result != 'yes':
                return

        ''' Warning if checking line_type all children will be checked. '''
        if self.lib_tree.tag_has("unchecked", item) and line_type:
            dialog = message.AskQuestion(
                self.lib_top, thread=self.get_refresh_thread,
                title="Check all songs below?",
                text="All songs under " + line_type + " will be checked.")
            if dialog.result != 'yes':
                return

        ''' ERROR if checking line_type with <No Artist> or <No Album>  
            Note design allows unchecking because previous to June 7, 2023 some
            may have been checked or tri-state.
            
            WIP: still need to read up to line_types of song, or Artist of Album.
        '''
        if self.lib_tree.tag_has("unchecked", item) and line_type is not None\
                and (g.NO_ARTIST_STR in self.lib_tree.item(item, 'text') or
                     g.NO_ARTIST_STR in self.lib_tree.item(item, 'text')):
            message.ShowInfo(
                self.lib_top, thread=self.get_refresh_thread,
                title="Song(s) invalid for playlist when " + g.NO_ARTIST_STR +
                "\nor " + g.NO_ALBUM_STR + " exists.", icon='error',
                text="Song(s) under " + line_type + " cannot be included in playlist.")
            return  # TODO lookup upwards from Song to line_types for same message.

        # Call CheckboxTreeview function check (select/unselect) item.
        # May 29, 2023 - Review calling _box_click, can it call us instead?
        # noinspection PyProtectedMember
        self.lib_tree._box_click(event)  # Force check or uncheck to appear
        self.lib_tree.update()  # June 10, 2023 - checking isn't showing on screen

        if self.lib_tree.tag_has("unchecked", item):
            self.process_unchecked(item, event)

        elif self.lib_tree.tag_has("checked", item):
            self.process_checked(item, event)

        else:
            # No need to test tristate, item must be checked or unchecked.
            # If item was tri-state, it becomes unchecked when clicked.
            print("button_1_click() ERROR: No 'checked' or 'unchecked' tag.",
                  self.lib_tree.item(item, 'tags'))
            return

    def process_unchecked(self, item, event):
        """ Unchecked the item now update totals """
        tags = self.lib_tree.item(item)['tags']
        if 'Artist' in tags or 'Album' in tags:
            self.set_all_parent(item, 'Del', event)
        elif 'Song' in tags:
            self.pending_append(item, 'Del')
            self.reverse(item)
        else:
            print('process_unchecked() bad line type tag:', tags)

    def process_checked(self, item, event):
        """ Checked the item, update totals """
        tags = self.lib_tree.item(item)['tags']
        if 'Artist' in tags or 'Album' in tags:
            self.set_all_parent(item, 'Add', event)
        elif 'Song' in tags:
            if not self.validate_song_addition(item, event):
                return  # Adding to playlist but no SQL Music Table Row exists
            self.pending_append(item, 'Add')
            self.reverse(item)
        else:
            print('process_checked() bad line type tag:', tags)

    def set_all_parent(self, Id, action, event):
        """ ID can be an Artist or Album. action can be "Add" or "Del"
                Are we processing an albums for artist or single album?
                Are we turning selection on or off? (action passed)
        """
        tags = self.lib_tree.item(Id)['tags']
        if "Artist" in tags:
            for album in self.lib_tree.get_children(Id):
                self.set_all_songs(album, action, event)

        elif "Album" in tags:
            self.set_all_songs(Id, action, event)

        else:
            print("set_all_parent() error: 'Id' is neither 'Album' nor 'Artist'")

    def set_all_songs(self, Id, action, event):
        """ set all songs selected or unselected """
        for child in self.lib_tree.get_children(Id):
            ''' Selected column may be "" or "Adding" or "No. 999" '''
            selected = self.lib_tree.item(child)['values'][2]
            if action == "Add" and not self.validate_song_addition(child, event):
                continue
            if (selected == "" and action == "Add") or \
                    (not selected == "" and action == "Del"):
                self.pending_append(child, action)
                self.reverse(child)

    def validate_song_addition(self, Id, event):
        """ If playlists, can only add songs that exist in the SQL Music Table """
        if self.playlists.open_name:
            music_id = self.get_music_id_for_lib_tree_id(Id)
            if music_id > 0:
                return True  # Song row exists in SQL Music Table
        else:
            return True  # Playing favorites which doesn't need SQL Music Table

        # noinspection PyProtectedMember
        self.lib_tree._box_click(event)  # Force check or uncheck to appear
        self.lib_tree.update()  # June 10, 2023 - checking isn't showing on screen

        item = self.lib_tree.item(Id)
        text  = "The song '" + item['text'] + "' has no Artist or Album.\n\n" + \
                "It can't be added to playlist but can be added to favorites."
        self.info.fact(text, 'error', 'add')
        message.ShowInfo(self.lib_top, thread=self.get_refresh_thread, align='left',
                         icon='error', title="Playlists Error", text=text)
        return False

    def pending_append(self, item, action):
        """ Add song to pending_additions or pending_deletions lists
        """
        if action is 'Add':
            self.pending_additions.append(item)
        elif action is 'Del':
            self.pending_deletions.append(item)
        else:
            print("mserve.py pending_append(" + item + ", action):" +
                  " has invalid action:", action)
            return

        """ If song exists in pending_additions and pending_deletions
            remove the song from both lists. Duplicates occur when a song
            is checked and then unchecked or vice versa.
        """
        duplicates = []
        for song in self.pending_additions:
            if song in self.pending_deletions:  # Addition in Deletions list?
                duplicates.append(song)
        for song in self.pending_deletions:
            if song in self.pending_additions:  # Deletion in Additions list?
                if song not in duplicates:  # Not already in Duplicates list?
                    duplicates.append(song)

        for song in duplicates:  # Remove songs duplicated in both lists
            self.pending_additions.remove(song)
            self.pending_deletions.remove(song)

        self.pending_add_cnt = len(self.pending_additions)  # Additions Count
        if self.pending_add_cnt > 0:
            add_last_text = self.lib_tree.item(
                self.pending_additions[self.pending_add_cnt - 1], "text")
        else:
            add_last_text = "No songs added yet."

        self.pending_del_cnt = len(self.pending_deletions)  # Deletions Count
        if self.pending_del_cnt > 0:
            del_last_text = self.lib_tree.item(
                self.pending_deletions[self.pending_del_cnt - 1], "text")
        else:
            del_last_text = "No songs deleted yet."

        ''' Update tkinter fields on screen '''
        self.pending_add_cnt_var.config(text=str(self.pending_add_cnt))
        self.pending_del_cnt_var.config(text=str(self.pending_del_cnt))
        self.pending_add_song_var.config(text=add_last_text)
        self.pending_del_song_var.config(text=del_last_text)
        if not self.pending_grid_visible:
            self.pending_restore_grid()

        ''' Playlists being used? Then not operating on favorites '''
        if self.playlists.open_name:
            self.disable_playlist_menu()  # Using Favorites, no Playlist permitted.
        else:
            # Not necessary because not activated yet anyway.
            self.file_menu.entryconfig("Save Favorites", state=tk.DISABLED)
            self.file_menu.entryconfig("Exit and CANCEL Pending", state=tk.DISABLED)

    def get_pending_cnt_total(self):
        """
            Used by Playlists to abort if favorites not saved yet.
        :return: sum of add_cnt + del_cnt + tot_add_cnt + tot_del_cnt
        """
        return self.pending_add_cnt  + self.pending_del_cnt + \
            self.pending_tot_add_cnt + self.pending_tot_del_cnt

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
        if Id is None:
            return  # clicked on whitespace (no row)

        # Still relative to screen. Not relative to treeview as expected?
        #test_xy = self.lib_tree.winfo_pointerxy()  # same as event.x_root()
        # print ('popup Id:', Id)
        self.mouse_x, self.mouse_y = event.x_root, event.y_root
        self.kid3_window = ""
        self.fm_window = ""  # Not sure why but mimic kid3 - July 16, 2023
        #print("test_xy:", test_xy,
        #      "self.mouse_x:", self.mouse_x, "self.mouse_y:", self.mouse_y)
        # print ('self.mouse; x, y:', self.mouse_x, self.mouse_y)
        # test_xy: (3362, 598) self.mouse_x: 3362 self.mouse_y: 598
        ''' Apply 'popup_sel' tag for visual feedback '''
        toolkit.tv_tag_add(self.lib_tree, Id, "popup_sel")

        ''' If Parent collapsed, expand it. '''
        if Id.startswith("I"):
            # If it is collapsed then expand it for viewing
            self.ensure_visible(Id)
            # Make it more obvious which parent is being processed with popup
            self.parent_popup(event, Id)
        else:
            # Song has different menu options:
            self.song_popup(event, Id)

    def parent_popup(self, event, Id):
        """ Popup parent menu
            Rename Artist or Album
            Need to apply 'popup_sel' tag to get visual feedback
        """
        ''' Set level for rename. '''
        if self.lib_tree.tag_has("Artist", Id):
            level = "Artist"
        elif self.lib_tree.tag_has("Album", Id):
            level = "Album"
        else:
            print("parent_popup() called with bad Id:", Id)
            return

        ''' Parent already done now apply 'popup_sel' tag to children '''
        for child in self.lib_tree.get_children(Id):
            toolkit.tv_tag_add(self.lib_tree, child, "popup_sel")

        menu = tk.Menu(root, tearoff=0)
        menu.post(event.x_root, event.y_root)

        # If lambda isn't used the command is executed as soon as popup
        # menu is displayed, not when option is chosen.
        menu.add_command(label="Collapse list", font=(None, MED_FONT),
                         command=lambda: self.collapse_all(Id))
        menu.add_command(label="Rename " + level, font=(None, MED_FONT),
                         command=lambda: self.rename_files(Id, level))
        menu.add_separator()

        global KID3_INSTALLED, FM_INSTALLED
        KID3_INSTALLED = ext.check_command('kid3')
        FM_INSTALLED = ext.check_command(FM_COMMAND)
        if KID3_INSTALLED:
            menu.add_command(label="Open " + KID3_NAME, font=(None, MED_FONT),
                             command=lambda: self.kid3_open(Id))
        if FM_INSTALLED:
            menu.add_command(label="Open " + FM_NAME, font=(None, MED_FONT),
                             command=lambda: self.fm_open(Id))
        menu.add_separator()

        menu.add_command(label="Ignore click", font=(None, MED_FONT),
                         command=lambda: self.remove_popup_sel())

        menu.tk_popup(event.x_root, event.y_root)
        # Without lambda executes immediately, without _: invalid # parameters
        menu.bind("<FocusOut>", lambda _: self.close_lib_popup(menu))

    def song_popup(self, event, Id):
        """ Popup menu for a song
            LONG TERM TODO: Display large 500x500 image and all metadata
        """
        os_filename = self.real_paths[int(Id)]
        menu = tk.Menu(root, tearoff=0)
        menu.post(event.x_root, event.y_root)
        menu.add_command(label="Sample middle 10 seconds", font=(None, MED_FONT),
                         command=lambda s=self: s.lib_tree_play(Id))
        menu.add_command(label="Sample whole song", font=(None, MED_FONT),
                         command=lambda s=self: s.lib_tree_play(Id, sample="full"))
        menu.add_separator()

        menu.add_command(label="Rename Song Title", font=(None, MED_FONT),
                         command=lambda: self.rename_files(Id, "Song Title"))

        global KID3_INSTALLED, FM_INSTALLED
        KID3_INSTALLED = ext.check_command('kid3')
        FM_INSTALLED = ext.check_command(FM_COMMAND)

        if KID3_INSTALLED:
            menu.add_command(label="Open " + KID3_NAME, font=(None, MED_FONT),
                             command=lambda: self.kid3_open(Id))
        if FM_INSTALLED:
            menu.add_command(label="Open " + FM_NAME, font=(None, MED_FONT),
                             command=lambda: self.fm_open(Id))
        if LRC_INSTALLED:
            menu.add_command(label="Make LRC file", font=(None, MED_FONT),
                             command=lambda: self.lrc_make(Id))

        menu.add_separator()
        menu.add_command(label="View Raw Metadata", font=(None, MED_FONT),
                         command=lambda: self.view_metadata(
                             Id, os_filename=os_filename, top=self.lib_top))
        menu.add_command(label="View SQL Metadata", font=(None, MED_FONT),
                         command=lambda: 
                         self.view_sql_music_id(Id, self.play_ctl))

        menu.add_separator()
        menu.add_command(label="Ignore click", font=(None, MED_FONT),
                         command=lambda: self.remove_popup_sel())

        menu.tk_popup(event.x_root, event.y_root)
        # Without lambda executes immediately, without _: invalid # parameters
        menu.bind("<FocusOut>", lambda _: self.close_lib_popup(menu))

    def close_lib_popup(self, menu):
        """ Remove popup menu and tags """
        self.remove_popup_sel()  # Remove 'popup_sel' tags
        menu.unpost()  # Remove popup menu

    def wrapup_lib_popup(self):
        """ Remove 'popup_sel' tags """
        self.remove_popup_sel()

    def remove_popup_sel(self):
        """ Remove special view popup selection tags to restore normal view
            TODO: Move cursor back to original treeview row and highlight row.
                  Possibly move cursor of 1/2 second and animate in rotating
                  motion regular - cursor - drag (boat) - menu - regular, etc.
        """
        tags_selections = self.lib_tree.tag_has("popup_sel")
        for child in tags_selections:
            toolkit.tv_tag_remove(self.lib_tree, child, "popup_sel")

    def collapse_all(self, Id):
        """ collapse songs under album or albums under artist """
        opened = self.lib_tree.item(Id, 'open')
        if opened is True or opened == 1:
            self.lib_tree.item(Id, open=False)
        self.wrapup_lib_popup()  # Set color tags and counts

    def view_sql_music_id(self, Id, file_ctl=None, top=None):
        """ View SQL Music Row.
        Called from Music Location Tree popup menu and passes os_filename
        
        file_ctl is NOT modified ! If the song is the same, then data is used.

        :param Id: Music Location Tree Id selected.
        :param file_ctl: self.play_ctl
        :param top: self.lib_top default when none, else self.play_top probably
        :returns None:
        """
        if not top:
            top = self.lib_top
        music_id = self.get_music_id_for_lib_tree_id(Id)
        pretty = sql.PrettyMusic(str(music_id), file_ctl=file_ctl)
        """ Create new window top-left of parent window with g.PANEL_HGT padding

            Before calling:
                Create pretty data dictionary using tree column data dictionary
            After calling / usage:
                create_window(title, width, height, top=None)
                pretty.scrollbox = self.scrollbox
                # If we did text search, highlight word(s) in yellow
                if self.mus_search is not None:
                    # history doesn't have support. Music & history might both be open
                    if self.mus_search.edit is not None:
                        pretty.search = self.mus_search.edit.get()
                sql.tkinter_display(pretty)

            When Music Location Tree calls from view_metadata it passes
            top=self.lib_top. In this case not called from SQL Music Table
            viewer.

            TODO: Instead of parent guessing width, height it would be nice
                  to pass a maximum and reduce size when text box has extra
                  white space.
        """

        # Requires override to def create_window
        self.create_window("SQL Music Row - mserve", 1400, 975, top=top)
        pretty.scrollbox = self.scrollbox
        sql.tkinter_display(pretty)

    # noinspection PyUnusedLocal
    def rename_files(self, Id, level):
        """ Rename Artist or Album on disc and in SQL Music Table
        :param Id: Treeview Id for item. Always starts with I for parents
        :param level: string with 'Artist', 'Album', or "Song Title"
        """

        old_name = self.lib_tree.item(Id)['text']
        default_string = old_name

        if encoding.RIP_CD_IS_ACTIVE:
            title = "CD Ripping is Active"
            text = "Cannot rename when CD Ripping is Active."
            self.info.cast(title + "\n\n" + text, 'error')
            message.ShowInfo(self.lib_top, title, text, icon='error',
                             thread=self.get_refresh_thread)
            self.wrapup_lib_popup()  # Set color tags and counts
            return

        if g.NO_ARTIST_STR in old_name or g.NO_ALBUM_STR in old_name:
            title = "Rename not allowed"
            text = "Cannot rename directories containing: '" + g.NO_ARTIST_STR + \
                "' or '" + g.NO_ALBUM_STR + "'."
            text += "\n\nThese types of directories do not exist."
            text += "\nThe song files should be move to real directories."
            self.info.cast(title + "\n\n" + text, 'error')
            message.ShowInfo(self.lib_top, title, text, icon='error',
                             thread=self.get_refresh_thread)
            self.wrapup_lib_popup()  # Set color tags and counts
            return

        if self.get_pending_cnt_total():
            title = "Pending playlist changes."
            text = "Checkboxes in Music Location Tree have not been updated."
            text += "\n\nIf the pending frame is open click 'Apply' button."
            text += "\n\nThen, open the 'File' dropdown menu and choose from:"
            text += "\n\n1) Select 'Save Playlist' if enabled."
            text += "\n\n2) Select 'Save Favorites' if enabled."
            text += "\n\n3) If you want to cancel changes, choose"
            text += "\nthe option 'Exit and CANCEL Pending'.\n"
            self.info.cast(title + "\n\n" + text, 'error')
            message.ShowInfo(self.lib_top, title, text, icon='error',
                             thread=self.get_refresh_thread)
            self.wrapup_lib_popup()  # Set color tags and counts
            return

        artist_name = None  # Added July 24, 2023 for pycharm syntax check
        album_name = None  # Added July 24, 2023 for pycharm syntax check
        if level == 'Song Title':
            album_id = self.lib_tree.parent(Id)
            album_name = self.lib_tree.item(album_id)['text']
            artist_id = self.lib_tree.parent(album_id)
            artist_name = self.lib_tree.item(artist_id)['text']
            search = artist_name + os.sep + album_name + os.sep + old_name
        elif level == 'Album':
            artist_id = self.lib_tree.parent(Id)
            artist_name = self.lib_tree.item(artist_id)['text']
            search = artist_name + os.sep + old_name + os.sep
        else:
            search = old_name + os.sep  # Renaming artists
        sql.cursor.execute("SELECT OsFileName, Id, Artist, Album, Title FROM Music " +
                           "WHERE OsFileName LIKE ? ", [search + "%"])
        old_rows = sql.cursor.fetchall()

        while True:
            title = "Rename " + level
            text = "Enter a new name for " + level + ":\n\n" + old_name
            string_width = int(len(default_string) * 1.5)
            string_width = 28 if string_width < 28 else string_width
            string_width = 100 if string_width > 100 else string_width
            answer = message.AskString(
                self.lib_top, title, text, thread=self.get_refresh_thread,
                string=default_string, string_width=string_width)

            if answer.result != "yes":
                self.wrapup_lib_popup()  # Set color tags and counts
                return False

            uni_string = toolkit.uni_str(answer.string)
            default_string = uni_string  # If prompting again for string
            """ '/', ':', and '?' are some of the invalid characters for 
                file and directory names that are replaced with "_".
                See: https://stackoverflow.com/a/31976060/6929343
            """
            legal_string = ext.legalize_dir_name(uni_string)
            if legal_string != uni_string:
                title = "New name has been legalized"
                text = "The new name contains invalid characters:\n"
                text += uni_string
                text += "\n\nInvalid characters replaced with '_':\n"
                text += legal_string
                text += "\n\nContinue with legal version?\n"
                answer = message.AskQuestion(
                    self.lib_top, title, text, 'no', icon='warning',
                    thread=self.get_refresh_thread)
                self.info.cast(title + "\n\n" + text + "\n\n\t\t" +
                               "Answer was: " + answer.result, 'warning')
                if answer.result != "yes":
                    continue  # Enter a new name

            ''' Blank names are not allowed. '''
            if len(legal_string) == 0:
                title = "Bad " + level + " name"
                text = "New name cannot be blank"
                self.info.cast(title + "\n\n" + text, 'error')
                message.ShowInfo(self.lib_top, title, text, icon='error',
                                 thread=self.get_refresh_thread)
                continue

            ''' old_name same as new name?'''
            if old_name == legal_string:
                title = "New " + level + " name invalid."
                text = "New name cannot be the same as the existing " + level
                text += ":\n\n" + legal_string
                self.info.cast(title + "\n\n" + text, 'error')
                message.ShowInfo(self.lib_top, title, text, icon='error',
                                 thread=self.get_refresh_thread)
                continue

            ''' If new name exists then files will be merged '''
            if level == 'Song Title':
                search = artist_name + os.sep + album_name + os.sep + legal_string
            elif level == 'Album':
                search = artist_name + os.sep + legal_string + os.sep
            else:
                search = legal_string + os.sep  # Renaming artists
            sql.cursor.execute("SELECT OsFileName, Id FROM Music " +
                               "WHERE OsFileName LIKE ? ", [search + "%"])
            test_rows = sql.cursor.fetchall()

            ''' Trying to rename to another song that exists under /Album '''
            if level == 'Song Title' and len(test_rows) != 0:
                title = "New " + level + " name invalid."
                text = "New " + level
                text += " name:\n\n" + legal_string + "\n\nAlready exists."
                self.info.cast(title + "\n\n" + text, 'error')
                message.ShowInfo(self.lib_top, title, text, icon='error',
                                 thread=self.get_refresh_thread)
                continue

            ''' New Artist or Album already exists so merge files 
            '''
            if len(test_rows) != 0:
                title = "New " + level + " name already exists."
                text = "The Music files from under the old " + level + ": "
                text += old_name + "\nwill be moved under the new " + level
                text += ": " + legal_string
                self.info.cast(title + "\n\n" + text)
                answer = message.AskQuestion(
                    self.lib_top, title, text, icon='warning',
                    thread=self.get_refresh_thread)
                self.info.cast(title + "\n\n" + text + "\n\n\t\t" +
                               "Answer was: " + answer.result, 'warning')
                if answer.result != "yes":
                    continue  # Enter a new name

            ''' Ensure old name isn't playing - Do this last so music
                player can't switch to new song during other dialog boxes. '''
            old_playing = False
            if self.ltp_ctl and old_name in self.ltp_ctl.path:
                old_playing = True  # Library Tree Play sampling same Album
            if self.play_ctl and old_name in self.play_ctl.path:
                old_playing = True  # Music Player playing same Album
            if self.fine_tune and old_name in self.fine_tune.time_ctl.path:
                old_playing = True  # Library Tree Playing same Album

            if old_playing:
                title = level + " is being played."
                text = "The " + level + ":" + old_name
                text += " is in use.\n\n"  # pycharm has problem with this string
                text += "Cannot rename the " + level
                text += " current being played.\n"
                text += "\n\nSwitch music player to a different " + level + "."
                self.info.cast(title + "\n\n" + text, 'error')
                message.ShowInfo(self.lib_top, title, text, icon='error',
                                 thread=self.get_refresh_thread)
                continue
            break

        ''' loop through old music by OsFileName
            old_base = artist/album/01 title.mp3 '''
        change_count = 0
        duplicate_count = 0
        for old_base, music_id, oldArtist, oldAlbum, OldTitle in old_rows:

            new_artist = old_artist = old_base.split(os.sep)[0]
            new_album = old_album = old_base.split(os.sep)[1]
            new_title = old_title = old_base.split(os.sep)[2]
            newArtist = oldArtist  # New metadata. Will change next if needed.
            newAlbum = oldAlbum  # New metadata. Will change next if needed.
            # newTitle = oldTitle  # There is no newTitle saved to SQL
            # newTitle for metadata, new_title for OS Filename
            if level == "Song Title":
                new_title = legal_string  # For OS Filename
                # Can't update metadata Title because "99-", "99 - " prefix
                # and ".m4a" suffix need to be stripped. Assume song title
                # hasn't changed or it will be changed with Kid3.
            elif level == 'Album':
                newAlbum = new_album = legal_string  # For OS Filename
            else:
                newArtist = new_artist = legal_string

            old_path = PRUNED_DIR + old_base
            new_base = new_artist + os.sep + new_album + os.sep + new_title
            new_path = PRUNED_DIR + new_base

            """ July 18, 2023 conversion notes: """
            artist_dir = OsFileName.rsplit(os.sep, 2)[0]
            if artist_dir == "Compilations":
                new_compilation = "1"
            else:
                new_compilation = "0"
            if old_artist == "Compilations" and not new_artist == "Compilations":
                # flip compilation flag using Kid3 warning
                pass
            if new_artist == "Compilations" and not old_artist == "Compilations":
                # flip compilation flag using Kid3 warning
                pass

            ''' Attempt to update Music Table with new OsFileName base_path '''
            sql_cmd = "UPDATE Music SET OsFileName=?, Artist=?, Album=?, \
                       Compilation=? WHERE Id=?"
            try:
                sql.cursor.execute(sql_cmd, (new_base, newArtist, newAlbum, 
                                             new_compilation, music_id))
                """

            ''' Attempt to update Music Table with new OsFileName base_path '''
            sql_cmd = "UPDATE Music SET OsFileName=?, Artist=?, Album=? WHERE Id=?"
            try:
                sql.cursor.execute(sql_cmd,
                                   (new_base, newArtist, newAlbum, music_id))
                """
            except sql.sqlite3.IntegrityError:  # UNIQUE constraint failed: Music.OsFileName
                print("UNIQUE constraint failed: Music.OsFileName")
                title = "Cannot rename to duplicate file name"
                text = "Old name: " + old_path + "\n\n"
                text += "New name: " + new_path + "\n\n"
                text += "Rename from old to new failed due to duplicate name."
                text += "\n\nMoving on to next file."
                self.info.cast(title + "\n\n" + text, 'error')
                message.ShowInfo(self.lib_top, title, text, icon='error',
                                 thread=self.get_refresh_thread)
                duplicate_count += 1
                sql.hist_add(time.time(), music_id, g.USER, 'rename', level,
                             old_name, old_path, "Rename FAILED. Target exists.",
                             duplicate_count, 0, 0.0, legal_string)
                continue

            ''' os.renames(old, new) '''
            os.renames(old_path, new_path)
            change_count += 1
            sql.hist_add(time.time(), music_id, g.USER, 'rename', level,
                         old_name, old_path, new_path, change_count, 0, 0.0,
                         legal_string)

            ''' Update fake_paths, real_paths and playlist_paths '''
            if level == 'Album':
                self.rename_path(-2, old_album, new_album, self.fake_paths)
                self.rename_path(-2, old_album, new_album, self.real_paths)
                self.rename_path(-2, old_album, new_album, self.playlist_paths)
            else:
                self.rename_path(-3, old_artist, new_artist, self.fake_paths)
                self.rename_path(-3, old_artist, new_artist, self.real_paths)
                self.rename_path(-3, old_artist, new_artist, self.playlist_paths)

        sql.con.commit()  # Write changes to disk
        self.lib_tree.item(Id, text=legal_string)  # Update Music Location Tree

        title = "Rename completed"
        if change_count == 0:
            text = "No files were renamed!\n"
        else:
            text = str(change_count) + " file(s) renamed.\n"
        if duplicate_count != 0:
            text += str(duplicate_count) + " duplicate file(s) NOT renamed!\n"
        if change_count != 0:
            text += "\nOld " + level + " name:\n" + old_name
            text += "\n\nNew " + level + " name:\n"  + legal_string
            text += "\n\nStorage device and SQL database in mserve have been updated."
            text += "\n\nUse your file manager (not mserve) to rename in other locations."
            text += "\n\nOtherwise the mserve SQL database will no longer be perfect"
            text += "\nwhen mserve opens the other locations. Duplicate data will"
            text += "\nappear in SQL database under the old " + level +\
                    " and the new " + level + ".\n"
        self.info.cast(title + "\n\n" + text)
        message.ShowInfo(self.lib_top, title, text,
                         thread=self.get_refresh_thread)

        self.wrapup_lib_popup()  # Set color tags and counts

    @staticmethod
    def rename_path(from_end, old, new, paths):
        """ Called from rename_files() to process one filename in paths list

        :param from_end: -1 = song, -2 = album, -3 = artist
        :param old: old name
        :param new: new name
        :param paths: list of paths
        :return: True old string was found and changed. Otherwise, False.
        """
        for i, path in enumerate(paths):
            parts = path.split(os.sep)
            if parts[from_end] == old:
                parts[from_end] = new
                path = os.sep.join(parts)
                paths[i] = path  # Update list element
                return True
        return False

    def reverse(self, Id):
        """ Toggle song tag on/off. Only used for song, not parent """
        if Id.startswith("I"):
            print("mserve.py reverse(" + Id + "): should not be called.")
            return  # Parents are a no-go
        album = self.lib_tree.parent(Id)
        artist = self.lib_tree.parent(album)
        self.toggle_select(Id, album, artist)

    def kid3_open(self, Id):
        """ Open Kidd3 for Artist, Album or Music File """
        trg_path = self.make_variable_path(Id)
        self.run_and_move_window(trg_path, KID3_COMMAND, KID3_WIN_SIZE)

    def make_variable_path(self, Id):
        """
        Called by fm_open() and kid3_open()
        :param Id: Treeview Id
        :return: path matching Treeview Id: /Artist, /Album or Music full path
        """
        trg_path = self.get_first_path(Id)
        if not trg_path:
            print("mserve.py make_variable_path() Unknown Id:", Id,
                  "treeview text:", self.lib_tree.item(Id)['text'])
            return self.real_path(0)

        if self.lib_tree.tag_has("Artist", Id):
            return trg_path.rsplit(os.sep, 2)[0]  # Right split on 2nd '/'
        elif self.lib_tree.tag_has("Album", Id):
            return trg_path.rsplit(os.sep, 1)[0]  # Right split on 1st '/'
        elif self.lib_tree.tag_has("Song", Id):
            return trg_path
        else:
            print("mserve.py make_variable_path() Unknown tags:",
                  self.lib_tree.item(Id)['tags'],
                  "treeview text:", self.lib_tree.item(Id)['text'])
            return trg_path

    def get_first_path(self, Id):
        """ Get first path for Treeview Id. If already a music file, return
        it back unchanged. """

        ''' Treeview iid for Artist or Album start with letter "I" '''
        if not Id.startswith("I"):
            ''' It's a Song Title, return path for Id '''
            return self.real_path(int(Id))

        ''' If an Artist, change pointer to first Album '''
        if self.lib_tree.tag_has("Artist", Id):
            Id = self.lib_tree.get_children(Id)[0]

        ''' Get path from first Title (song filename) in Album '''
        for child in self.lib_tree.get_children(Id):
            if self.lib_tree.tag_has("Song", child):
                return self.real_path(int(child))

    def run_and_move_window(self, trg_path, command, window_size):
        """
            Run command for Kid3 or File Manager.
            Move window to coordinates at self.mouse_x & _y.
            Resize window to specified geometry

        :param trg_path: Path to /Artist, /Album or Title (song filename)
        :param command: External command to run
        :param window_size: Resize window after it is active
        :return new_window: The window ID (in hex) that became active
        """
        our_window = os.popen("xdotool getactivewindow").read().strip()
        os.popen(command + ' "' + trg_path + '" 2>/dev/null &')

        ''' Wait until a new window opens '''
        ext.t_init("new_window = our_window")
        new_window = our_window
        i = 0  # For pycharm syntax checker
        for i in range(100):
            thread = self.get_refresh_thread()
            thread()
            new_window = os.popen("xdotool getactivewindow").read().strip()
            if new_window != our_window:
                break
        ext.t_end('no_print')  # 0.6692051888
        print(i, new_window)

        ''' Looped 100 times at 33ms '''
        if new_window == our_window:
            print("''' run_and_move_window() Looped ", i, "times at 33ms '''")
            print("No change to our_window:", our_window)
            return

        ''' Move window to mouse position within popup menu event '''
        os.popen('xdotool windowmove ' + new_window + ' ' +
                 str(self.mouse_x) + ' ' + str(self.mouse_y))

        ''' Set size of new window '''
        if window_size is not None:
            width = window_size.split('x')[0]
            height = window_size.split('x')[1]
            # noinspection SpellCheckingInspection
            os.popen('xdotool windowsize ' + new_window + ' ' +
                     width + ' ' + height)
        return new_window

    def fm_open(self, Id):
        """ Open File Manager (Nautilus) for Artist, Album or Music File """
        trg_path = self.make_variable_path(Id)
        self.run_and_move_window(trg_path, FM_COMMAND, FM_WIN_SIZE)

    def lrc_make(self, Id, msgs=True):
        """ Make song_name.lrc file with synchronized lyrics
            Called from song file right click popup
            Called from Tools / Make LRC for checked files

            https://en.wikipedia.org/wiki/LRC_(file_format)

            [ar:Lyrics artist]
            [al:Album where the song is from]
            [ti:Lyrics (song) title]
            [au:Creator of the Songtext]
            [length:How long the song is]
            [by:Creator of the LRC file]

            [offset:+/- Overall timestamp adjustment in milliseconds,
                + shifts time up, - shifts down i.e. a positive value
                causes lyrics to appear sooner, a negative value causes
                them to appear later]

            [re:The player or editor that created the LRC file]
            [ve:version of program]

            [00:12.00]Get up each morning
            [00:15.30]Some more lyrics ...
            [03:45.30]Then go to bed
        """
        trg_path = self.make_variable_path(Id)
        trg_base, trg_ext = trg_path.rsplit(u".", 1)
        lrc_path = toolkit.uni_str(trg_base) + u'.lrc'

        music_id = self.get_music_id_for_lib_tree_id(Id)
        pretty = sql.PrettyMusic(str(music_id), file_ctl=self.play_ctl)

        if pretty.synchronized < 0.8:
            if msgs:  # When no messages, called from checked_ batch processing
                title = "Song not synchronized"
                text = "Song must be at least 80% synchronized to make .lrc file\n\n"
                text += "Current synchronized percentage is: "
                text += '{0:.2f}'.format(pretty.synchronized)
                lcs.out_cast_show(title, text, 'error')
            return False

        lrc_list = list()
        lrc_list.append(u"[ar:" + pretty.dict['Artist'] + u"]")
        lrc_list.append(u"[al:" + pretty.dict['Album'] + u"]")
        lrc_list.append(u"[ti:" + pretty.dict['Title'] + u"]")
        lrc_list.append(u"[length:" + tmf.mm_ss(float(pretty.dict['Seconds'])) + u"]")
        lrc_list.append(u"[re:mserve]")
        lrc_list.append(u"[ve:" + g.MSERVE_VERSION + u"]")  # unicode to string

        # For lyrics lines, see def sql.tkinter_display(pretty)
        curr_level = 2  # dictionary part containing indexed lyrics score
        curr_level_name = pretty.part_names[curr_level]
        curr_start = pretty.part_start[curr_level]
        curr_end = 9999999  # Default no next section
        if len(pretty.part_start) > curr_level:
            curr_end = pretty.part_start[curr_level + 1] - 1
        for i, key in enumerate(pretty.dict):  # ordered dict
            if curr_start <= i <= curr_end:
                lrc_list.append(key + pretty.dict[key])

        ext.write_from_list(lrc_path, lrc_list)

        title = u".lrc file created"
        text = u"Synchronized lyrics have been written to the file:\n\n"
        text += lrc_path
        if msgs:
            lcs.out_cast_show(title, text)

        if True is False:
            ''' print audit log "if True is True:" '''
            print(u"Make LRC file for:", trg_path)
            print("Extracting lyrics from dictionary level:", curr_level_name)
            print("curr_start:", curr_start, "curr_end:", curr_end)
            for line in lrc_list:
                print(line)

        return True

    def checked_make_lrc(self):
        """ Make LRC files for Music Location Tree checked files """
        title = "Make LRC Files For Checked Songs"
        text = "For every checked song, e.g. 'Song Name.mp3'\n"
        text += "a matching 'Song Name.lrc' file is created.\n\n"
        text += "LRC files are used by other Music Players \n"
        text += "to display synchronized lyrics.\n\n"
        text += "If no lyrics score, or if lyrics score < 80%\n"
        text += "synchronized, no '.lrc' file will be created."
        answer = message.AskQuestion(self.lib_top, title, text, align='left',
                                     thread=self.get_refresh_thread)
        self.info.cast(title + "\n\n" + text + "\n\n\t\t" +
                       "Answer was: " + answer.result, 'info')
        if answer.result != "yes":
            return

        ''' TODO: Prevent other location & playlist related functions from 
                  starting up and changing lcs.act_topdir or music tree. '''

        ''' Tools - batch processing - make .lrc / copy files '''
        self.checked_process('lrc')

    def checked_copy_files(self):
        """ Copy Music Location Tree checked files + LRC to new location

            Sep 9, 2023 - Only works on new empty locations. Otherwise
            synchronization needs to be used.
        """
        title = "Copy Checked Files To New Location"
        text = "You will be prompted to select a target location.\n\n"
        text += "Then every checked song in the Music Location Tree, and\n"
        text += "it's LRC file, will be copied to the selected location.\n\n"
        human_selected = toolkit.human_bytes(self.lib_top_totals[8])
        text += "Total size of copied files: " + human_selected + "\n\n"

        text += "If the Top Directory is NOT empty, you will need to use the\n"
        text += "'Synchronize Location' function for existing songs.\n\n"

        text += "If the new location is a remote host, make sure it works\n"
        text += "by using the 'Test Host' button, on the next window."
        answer = message.AskQuestion(self.lib_top, title, text, align='left',
                                     thread=self.get_refresh_thread)
        self.info.fact(title + "\n\n" + text + "\n\n\t\t" +
                       "Answer was: " + answer.result, 'info')
        # lcs.main_top messed up if cast used above.
        # The .cast close button disappears.
        # The piggy_back tool_type from .cast gets main_top_window name.  
        if answer.result != "yes":
            return

        lcs.register_target_cb(self.checked_target_cb)
        ''' Select location for target '''
        lcs.target()  # Enters idle loop until button clicked
        while lcs.main_top:  # Is Location Maintenance window still open?
            # Location Maintenance calls refresh
            thread = self.get_refresh_thread()
            thread()

        if self.checked_loc_name is None and self.checked_loc_topdir is None:
            # When both are None, cancel button clicked
            title = "No Location"
            text = "Cancelling target location selection."
            lcs.out_cast_show(title, text, 'warning')
            return

        if self.checked_loc_name is None or self.checked_loc_topdir is None:
            # When one is None, Proceed clicked but with errors
            title = "Invalid Location"
            text = "Location has a blank Name or a blank Music Top Directory"
            lcs.out_cast_show(title, text, 'error')
            return

        if not os.path.isdir(self.checked_loc_topdir):
            title = "Invalid Music Top Directory"
            text = "Location has an invalid Music Top Directory!\n\n"
            text += "Location: " + self.checked_loc_name + "\n\n"
            text += "Directory: " + self.checked_loc_topdir + "\n\n"
            text += "Edit the location and correct error."
            lcs.out_cast_show(title, text, 'error')
            return

        list_dir = os.listdir(self.checked_loc_topdir)
        if len(list_dir) > 0:
            title = "Invalid Location"
            text = "Location's Music Top Directory not empty!\n\n"
            text += "Location: " + self.checked_loc_name + "\n\n"
            text += "Directory: " + self.checked_loc_topdir + "\n\n"
            text += "Edit the location and correct error."
            lcs.out_cast_show(title, text, 'error')
            return

        ''' Tools - batch processing - make .lrc / copy files '''
        self.checked_process('copy')
        self.checked_loc_name = None  # Extra safety
        self.checked_loc_topdir = None

    def checked_target_cb(self, loc_name, loc_topdir):
        """ Location selected - get name and topdir """
        print("loc_name:", loc_name)
        print("loc_topdir:", loc_topdir)
        self.checked_loc_name = loc_name
        self.checked_loc_topdir = loc_topdir

    def checked_copy_one_file(self, Id):
        """ Copy Music Location Tree checked files to another location

            mkdir -p /foo/bar && cp myfile "$_"

        """
        if not self.lib_top_is_active:
            return  # mserve is shutting down
        who = "mserve.py checked_copy_one_file() - "
        src_path = self.make_variable_path(Id)
        src_base, src_ext = src_path.rsplit(u".", 1)
        lrc_src_path = toolkit.uni_str(src_base) + u'.lrc'
        trg_path = src_path.replace(lcs.open_topdir, self.checked_loc_topdir)
        trg_subdir = trg_path.rsplit(os.sep, 1)[0]
        lrc_trg_path = lrc_src_path.replace(lcs.open_topdir, self.checked_loc_topdir)

        src_path = toolkit.uni_str(src_path)
        src_size = os.path.getsize(src_path)

        lrc_src_path = toolkit.uni_str(lrc_src_path)
        trg_path = toolkit.uni_str(trg_path)
        trg_subdir = toolkit.uni_str(trg_subdir)
        lrc_trg_path = toolkit.uni_str(lrc_trg_path)
        #print("trg_path:", trg_path)
        #print("lrc_trg_path:", lrc_trg_path)

        # Make subdirectory if it doesn't exist
        command_str = u'mkdir -p  "' + trg_subdir + u'"  &&  '  # chain to next command
        command_str += u"cp --preserve=timestamps --verbose"

        ''' Complete command line with extra space:  "source"  "target" '''
        command_str += u'  "' + src_path + u'"  "' + trg_path + u'"'

        # Make dir first & copy file next
        lcs.run_one_command(command_str, src_size)  # size = ~8 MB
        if not self.lib_top_is_active:
            return

        if os.path.isfile(lrc_src_path):
            lrc_src_size = os.path.getsize(lrc_src_path)
            command_str = u"cp --preserve=timestamps --verbose"
            command_str += u'  "' + lrc_src_path + u'"  "' + lrc_trg_path + u'"'
            lcs.run_one_command(command_str, lrc_src_size)  # size ~2 KB

    def checked_process(self, action):
        """ Process all checked items 
            Copied from clear_all_checks
        """
        who = "mserve.py checked_process() - "
        ext.t_init('check_process()')

        ''' TODO: Prevent other location & playlist related functions from 
                  starting up and changing lcs.act_topdir or music tree. '''

        if not self.lib_top_is_active:
            return  # mserve is shutting down
        self.checked_in_progress = True  # Options will be set tk.DISABLED
        self.enable_lib_menu()  # Turn off location and playlist options
        self.start_long_running_process()
        self.lib_top.update_idletasks()
        self.lib_tree_open_states = []
        for Artist in self.lib_tree.get_children():  # Read all Artists
            if self.lib_tree.tag_has("unchecked", Artist):
                continue
            self.checked_highlight('Artist', Artist)
            for Album in self.lib_tree.get_children(Artist):  # Read all Albums
                if self.lib_tree.tag_has("unchecked", Album):
                    continue
                self.checked_highlight('Album', Album)
                for Song in self.lib_tree.get_children(Album):  # Read all Albums
                    if not self.lib_top_is_active:
                        return  # mserve is shutting down
                    if self.lib_tree.tag_has("unchecked", Song):
                        continue
                    self.checked_highlight('Song', Song)
                    ''' Process 'copy' or 'lrc' action '''
                    if action == 'lrc':
                        self.lrc_make(Song, msgs=False)
                    elif action == 'copy':
                        self.checked_copy_one_file(Song)
                    else:
                        toolkit.print_trace()
                        print(who + "Bad action:", action)
                        return
                    self.checked_done('Song', Song)
                self.checked_done('Album', Album)
            self.checked_done('Artist', Artist)
        ext.t_end('no_print')  # 0.33 for 1500 selections
        self.checked_in_progress = None  # When None, options set to tk.NORMAL
        if not self.lib_top_is_active:
            return  # mserve is shutting down

        self.lib_top.update_idletasks()
        self.end_long_running_process()
        self.enable_lib_menu()  # Turn On location and playlist options
        # 0.1857478619  for 3 selections out of 3826 songs

    def checked_highlight(self, line_type, iid):
        """ Highlight Music Location Treeview line """
        if not self.lib_top_is_active:
            return
        toolkit.tv_tag_add(self.lib_tree, iid, "checked_sel", strict=True)

        if line_type == 'Song':
            self.lib_tree.see(iid)
            thread = self.get_refresh_thread()
            thread()  # ten times slower due to every 18 ms invocation
            # but visual effect nicer than racing through music location tree
            #self.lib_top.update_idletasks()
            return

        ''' Is it already opened? '''
        opened = self.lib_tree.item(iid, 'open')

        if line_type == 'Artist':
            if opened is True or opened == 1:
                self.checked_opened_artist = False
            else:
                self.checked_opened_artist = True
                self.lib_tree.item(iid, open=True)

        elif line_type == 'Album':
            if opened is True or opened == 1:
                self.checked_opened_album = False
            else:
                self.checked_opened_album = True
                self.lib_tree.item(iid, open=True)

        #self.lib_top.update_idletasks()  # Done by get_refresh_thread

    def checked_done(self, line_type, iid):
        """ Finished one batched item """
        if not self.lib_top_is_active:
            return

        toolkit.tv_tag_remove(self.lib_tree, iid, "checked_sel", strict=True)

        if line_type == 'Song':
            self.lib_top.update_idletasks()
            return

        if line_type == 'Artist':
            if self.checked_opened_artist:  # Did we open album?
                self.lib_tree.item(iid, open=False)

        elif line_type == 'Album':
            if self.checked_opened_album:  # Did we open album?
                self.lib_tree.item(iid, open=False)

        self.lib_top.update_idletasks()

    # ==============================================================================
    #
    #       Music Location Tree Processing section - Top level functions
    #
    # ==============================================================================

    def exit_without_save(self):
        """ save=True is default. False prevents saving data. """
        self.close(save=False)

    # noinspection PyUnusedLocal
    def close(self, save=True, *args):
        """ save=True is default. When <Escape> or X closes window save=tk.Event
            which is boolean True. Only 'Exit and CANCEL Changes' passes False.
        """
        if save:
            if self.playlists.open_name:
                # Saving requires reading stats from lib_tree
                self.write_playlist_to_disk(ShowInfo=False)
            else:
                self.save_last_selections()  # Last selections for next open
        self.close_sleepers()  # Shut down running functions
        root.destroy()
        self.lib_top = None
        exit()  # Doesn't happen because .close_sleepers() keeps running?

    # noinspection PyUnusedLocal
    def restart(self, *args):
        """ July 13 2023 - A couple weeks ago this option was removed from
            dropdown menu because after 100 times it causes lag in TCL/Tk """
        self.close()
        # TODO: Test with `m` passing sys.argv via "parameters" keyword.
        os.execl(sys.executable, sys.executable, *sys.argv)

    def close_sleepers(self):
        """ COMMON CODE for restart and quit
            Close loc_keep_awake() first as it has .25-second sleep cycle 

            TODO: Review to close mount or leave open?
                
                $ fusermount -u /mnt/phone
    
                $ ll /mnt/phone
                total 8
                drwxrwxrwx 2 rick rick 4096 Oct  6  2019 ./
                drwxr-xr-x 9 root root 4096 Jun 11 08:26 ../

        """
        if self.close_sleepers_in_progress:
            print("duplicate call to close_sleepers() !!!")
            return  # Multiple threads can call close() -> close_sleepers()
        self.close_sleepers_in_progress = True

        if self.loc_keep_awake_is_active:  # Keeping remote host awake?
            self.loc_keep_awake_is_active = False  # Has 10 minute wakeup cycle

        self.lib_top_is_active = False      # Tell refresh_acc_times() to bail out

        if self.gone_fishing is not None:
            self.gone_fishing.close()       # Shark eating man animation
            self.gone_fishing = None

        if lcs.cmp_top_is_active:
            lcs.cmp_close()                 # Close Compare Locations window
        if self.fine_tune and self.fine_tune.top_is_active:
            self.fine_tune.close()          # Synchronizing lyrics time indices
        if self.play_top_is_active:         # Is music playing?
            self.play_close()
        if self.ltp_top_is_active:          # Sampling middle 10 seconds?
            self.lib_tree_play_close()
        if self.mus_top_is_active:          # Viewing SQL Music Table?
            self.mus_close()
        if self.his_top_is_active:          # Viewing SQL History Table?
            self.his_close()
        if self.lcs_top_is_active:          # Viewing SQL Location Table
            self.lcs_close()                # Careful: NOT self.lcs.close() !!!
        if self.tv_vol and self.tv_vol.top:
            self.tv_vol.close()             # Adjusting Volume during TV commercials?
        if self.playlists.top:              # Close Playlists window and tell it
            self.playlists.reset(shutdown=True)  # NOT to enable lib_top menu options
        if lcs.test_top:                    # Test Host Window is open
            lcs.test_top.destroy()
            lcs.test_top = None             # Extra insurance
        if lcs.main_top:                    # Locations Maintenance Window open
            lcs.reset(shutdown=True)
        if not lcs.host_down:  # When host down accessing /mnt/music locks 15 min.
            lcs.sshfs_close()  # It will check if mounted and act accordingly
        if encoding.RIP_CD_IS_ACTIVE:       # Ripping CD currently active?
            encoding.RIP_CD_IS_ACTIVE = False  # Force ripping window shutdown.

        ''' Remove temporary files - NOTE: could simply use /tmp/mserve* '''
        for f in TMP_ALL_NAMES:
            if f.endswith("*"):
                ext.remove_group(f)
            elif os.path.isfile(f):
                os.remove(f)

        ''' Encoding (MusicBrainz) development debugging files '''
        if not ENCODE_DEV:
            ext.remove_group(g.TEMP_DIR + "mserve_gst_*")
            ext.remove_group(g.TEMP_DIR + "mserve_mbz_*")
            ext.remove_group(g.TEMP_DIR + "mserve_disc_*")
            ext.remove_group(g.TEMP_DIR + "mserve_encoding_*")

        ''' Last known window position for music location tree, saved to SQL '''
        last_library_geom = monitor.get_window_geom_string(
            self.lib_top, leave_visible=True)  # don't destroy lib_top
        monitor.save_window_geom('library', last_library_geom)

        ''' Close SQL databases '''
        sql.close_db()  # Added July 13, 2023
        self.lib_top.destroy()  # Was left visible to last second
        #time.sleep(RESTART_SLEEP)           # Extra insurance sleepers close

    def open_and_play_callback(self, code, topdir):
        """ Open location by calling lcs.test() first to check success.
            After error checking, call restart with new topdir as parameter 1.
            Called from lcs.apply() self.open_and_play_callback()
            lcs.act_code and lcs.act_topdir are all current because
            lcs.reset() has not been run yet. """
        # Save current selections before restart
        if self.playlists.open_name:
            ''' Not a problem because lcs.open() checks pending counts '''
            pass
        else:
            self.save_last_selections()

        ''' Shouldn't be required. lcs.open should have run test '''
        lcs.read_location(code)  # setup self.act_code, self.act_host, etc.
        lcs.sshfs_close()
        if lcs.test_common(self.lib_top):  # Validate Host can be woken up
            pass  # Host and Top Directory passed tests
        else:
            # Location doesn't exist
            title = "Location Error"
            text = "Top directory doesn't exist or is off-line."
            self.info.cast(title + "\n\n" + text)
            message.ShowInfo(lcs.main_top, title, text,
                             thread=self.get_refresh_thread)
            return False  # Pops back into lcs.apply() which calls lcs.reset()

        ''' Save last opened location code '''
        lcs.save_mserve_location(code)

        ''' Next top directory to startup '''
        #self.parm = topdir  # Can no longer use matching on topdir
        self.parm = code  # Sep 5/23 - topdir appears twice, L001 and L005
        self.restart_new_parameters(self)

    # noinspection PyUnusedLocal
    def restart_new_parameters(self, *args):
        """ Called by open_and_play() function """
        self.close_sleepers()  # Shut down running functions
        root.destroy()

        print('mserve.py restart_new_parameters() - Restarting',
              'with new music library:', self.parm)
        ''' Replace existing, or append first parameter with music directory '''
        if len(sys.argv) > 1:
            sys.argv[1] = self.parm
        else:
            sys.argv.append(self.parm)
        os.execl(sys.executable, sys.executable, *sys.argv)

    def clear_buttons(self):
        """ When new windows open, disable TreeView buttons """
        self.lib_tree_play_btn["text"] = "🎵  Show library"  # Play button
        self.play_on_top = True
        self.lib_top.update_idletasks()

    def restore_lib_buttons(self):
        """ When playing window closes, restore TreeView buttons """
        if not self.lib_top_is_active:
            return
        self.lib_tree_play_btn["text"] = self.play_text
        self.tt.set_text(self.lib_tree_play_btn, "Play favorite songs.")

    def refresh_acc_times(self, first_time=False):
        """ Refresh songs last access time in Music Location treeview (lib_tree).

            Called once when lib_top created then recursively calls itself every
            60 seconds.

            TODO: Don't run unless loc_keep_awake() is run first otherwise we
                  go into 'Disk Wait+' status in 'ps aux'
        """
        # ext.t_init('refresh_acc_times()')

        if not first_time:
            for artist in self.lib_tree.get_children():
                for album in self.lib_tree.get_children(artist):
                    for song in self.lib_tree.get_children(album):
                        # Are we closing down?
                        if self.lib_top_is_active is False:
                            return
                        # Update last played time "xxx ago" in column #1
                        self.update_song_last_play_time(song)

        # job_time = ext.t_end('print')
        """ A simpler method is checking the modification time Top Directory """
        ''' NOTE: DO NOT CALL if make_sorted_list takes longer than 0.1 second.
                  This could happen on some Wifi connections using SSHFS.

                  On file server it is taking 1.67 second causing lag...
        #ext.t_init('refresh_acc_times(): Compare SORTED_LIST')
        if self.loc_keep_awake_is_active:
            # loc_keep_awake() is processing FileServer over ethernet
            # TODO: A special test for phone SSHFS over WiFi
            last_time_check = self.awake_last_time_check
            while last_time_check == self.awake_last_time_check:
                # update idletasks if resuming from sleep until connection
                # drops and program quits.
                #print('refresh_acc_times() idling milliseconds:',KEEP_AWAKE_MS)
                #print('curr time:',time.time(),self.awake_last_time_check)
                #self.lib_top.after(KEEP_AWAKE_MS, self.refresh_lib_tree)
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
            self.refresh_required_notify()
        else:
            # disk image hasn't changed, reset time last message sent
            self.last_inotify_time = None
        #job_time = ext.t_end('print')
        '''
        self.lib_top.after(60000, self.refresh_acc_times)  # Update every minute

    def refresh_required_notify(self):
        """ NOT CALLED - Needs more work. """
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
    #       Music Location Tree Processing - Refresh Library
    #
    # ==============================================================================

    def rebuild_lib_tree(self):
        """ If directories/songs have changed rebuild cd tree and position
            to first changed song.
            Called from lib_tree's "🗘 Refresh library" button.
        """
        if self.playlists.open_name:
            self.info.cast("Rebuild music library - Only works when Favorites playing",
                           'error', 'open')
            message.ShowInfo(
                self.lib_top, thread=self.get_refresh_thread,
                title="Support for Playlists not finished.",
                text="The Refresh Library function cannot be run when a\n" +
                     "Playlist is open. Close playlist and use Favorites.\n\n" +
                     "The Refresh Library function checks for new song files which is\n" +
                     "a process automatically performed during mserve startup anyway.")
            return

        self.info.cast("Rebuild music library - scan for new songs")

        global SORTED_LIST
        # Build list of songs
        ext.t_init("make_sorted_list(START_DIR, toplevel=self.lib_top)")
        SortedList2, depth_count = make_sorted_list(START_DIR, toplevel=self.lib_top)
        ext.t_end('no_print')  # 3907 songs =  0.1526460648

        if SORTED_LIST == SortedList2:
            # print('self.play_top_is_active:', self.play_top_is_active)
            message.ShowInfo(
                self.lib_top, thread=self.get_refresh_thread,
                title="Refresh music library",
                text="The same " + str(len(SORTED_LIST)) +
                     " songs are in the library.\n\n" +
                     "No changes to Music Location Tree.")
            return
        else:
            additions = list(set(SortedList2).difference(SORTED_LIST))
            deletions = list(set(SORTED_LIST).difference(SortedList2))
            answer = message.AskQuestion(
                self.lib_top, thread=self.get_refresh_thread,
                align='left', icon='warning',
                title="Refresh music library - EXPERIMENTAL !!!",
                text="Songs have changed in storage:\n" +
                     "\tAdditions:\t" + str(len(additions)) + "\n" +
                     "\tDeletions:\t" + str(len(deletions)) + "\n\n" +
                     "This experimental feature will backup these files:\n" +
                     "\t " + lc.FNAME_LAST_OPEN_STATES + "\n" +
                     "\t " + lc.FNAME_LAST_SONG_NDX + "\n" +
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
        shutil.copy(lc.FNAME_LAST_OPEN_STATES, lc.FNAME_LAST_OPEN_STATES + ".bak")
        shutil.copy(lc.FNAME_LAST_SONG_NDX, lc.FNAME_LAST_SONG_NDX + ".bak")
        shutil.copy(lc.FNAME_LAST_PLAYLIST, lc.FNAME_LAST_PLAYLIST + ".bak")

        SORTED_LIST = SortedList2
        self.fake_paths = SORTED_LIST
        lcs.register_fake_paths(self.fake_paths)
        self.lib_tree.delete(*self.lib_tree.get_children())
        # Copied from __init__
        dtb = message.DelayedTextBox(title="Building music location treeview",
                                     toplevel=None, width=1000)
        '''
                    B I G   T I C K E T   E V E N T
         
                     Create Music Location Treeview 
        '''
        self.populate_lib_tree(dtb)

        ''' Load last selections and begin playing with last song '''
        self.load_last_selections()  # Review: Memory/speed called in three places

    def set_tv_volume(self):
        """ Define TV volume to set during TV Commercials when mserve plays.
            TV Commercials A.K.A. Hockey Commercial and Hockey Intermission.
            Also set TV Sound source such as "Chrome" or "Firefox".
            Also set number of seconds for Commercial and for Intermission.
        """
        if self.tv_vol and self.tv_vol.top:
            self.tv_vol.top.lift()
            return

        self.tv_vol = tvVolume(top=self.lib_top, tooltips=self.tt,
                               thread=self.get_refresh_thread,
                               save_callback=self.get_hockey_state,
                               playlists=self.playlists, info=self.info)

    def calculator_open(self):
        """ Big Number Calculator allows K, M, G, T, etc. UoM """
        if self.calculator and self.calc_top:
            self.calculator_lift()
            return
        geom = monitor.get_window_geom('calculator')
        self.calc_top = tk.Toplevel()
        self.calculator = Calculator(self.calc_top, g.FONT, geom)
        ''' Set program icon in taskbar '''
        img.taskbar_icon(self.calc_top, 64, 'white', 'lightskyblue', 'black')
        ''' Trap <Escape> key and  '✘' Window Close Button '''
        self.calc_top.bind("<Escape>", self.calculator_close)
        self.calc_top.protocol("WM_DELETE_WINDOW", self.calculator_close)
        self.calc_top.update_idletasks()

    def calculator_lift(self):
        """ Lift Big Number Calculator above Music Location Tree window """
        if self.calculator and self.calc_top:
            self.calc_top.focus_force()
            self.calc_top.lift()
            return

    def calculator_close(self, *args):
        """ Save last geometry for next Calculator startup """
        last_geom = monitor.get_window_geom_string(
            self.calc_top, leave_visible=False)  # Destroy toplevel
        monitor.save_window_geom('calculator', last_geom)
        self.calculator = None  # Prevent lifting window
        self.calc_top = None

    def show_debug(self):
        """ Debugging - show machine info, monitors, windows, tooltips 
            locations, sql, metadata, global variables """

        ''' Make TMP names unique for multiple FileControls racing at once '''
        letters = string.ascii_lowercase + string.digits
        temp_suffix = (''.join(random.choice(letters) for _i in range(6)))
        self.debug_file = TMP_PRINT_FILE + "_" + temp_suffix  # def debug
        self.debug_recreate_file()  # Clear print file, title and text lists

        self.debug_header("\nglobal_variables.py (g) - Machine Information")
        self.debug_detail("g.OS_PLATFORM     :", g.OS_PLATFORM)
        self.debug_detail("g.OS_NAME         :", g.OS_NAME)
        self.debug_detail("g.OS_VERSION      :", g.OS_VERSION)
        self.debug_detail("g.OS_RELEASE      :", g.OS_RELEASE)

        self.debug_detail("g.USER            :", g.USER)
        self.debug_detail("g.USER_ID         :", g.USER_ID)
        self.debug_detail("g.HOME            :", g.HOME)
        self.debug_detail("g.USER_CONFIG_DIR :", g.USER_CONFIG_DIR)
        self.debug_detail("g.USER_DATA_DIR   :", g.USER_DATA_DIR)
        self.debug_detail("g.MSERVE_DIR      :", g.MSERVE_DIR)
        self.debug_detail("g.PROGRAM_DIR     :", g.PROGRAM_DIR)
        self.debug_detail("g.TEMP_DIR        :", g.TEMP_DIR)

        self.debug_detail("Python Version    :", sys.version)
        self.debug_detail('TK Version        :', tk.TkVersion)
        self.debug_detail("Process ID (PID)  :", os.getpid())
        self.debug_detail("Parent's PID      :", os.getppid())  # win needs > 3.2
        self.debug_output()  # self.info.fact() + print()

        self.debug_header("\nmon = monitor.Monitors()")
        mon = monitor.Monitors()            # Monitors class list of dicts

        self.debug_detail("mon.screen_width x mon.screen_height:",
                          mon.screen_width, "x", mon.screen_height, "\n")

        self.debug_detail("Number of monitors - mon.get_n_monitors():",
                          mon.get_n_monitors())
        self.debug_detail("for m in mon.monitors_list: -- self.debug_detail(' ', m):")
        for m in mon.monitors_list:
            self.debug_detail(" ", m)
        self.debug_detail('\nPrimary Monitor - mon.primary_monitor:\n  ',
                          mon.primary_monitor)
        self.debug_detail('\nActive Window Tuple -  active_win = mon.get_active_window():')
        active_win = mon.get_active_window()  # Get tuple

        ''' Window = namedtuple('Window', 'number, name, x, y, width, height')
        x_id, window_name, geom.xp, geom.yp, geom.width p, geom.height p) '''
        self.debug_detail('  active_win.number   :', active_win.number)
        self.debug_detail('  active_win. WxH+X+Y :',
                          active_win.width, "x", active_win.height, "+",
                          active_win.x, "x", active_win.y)
        self.debug_detail('  active_win.name     :', active_win.name[:75])
        self.debug_detail()  # blank line
        self.debug_detail("Active Monitor - mon.get_active_monitor():\n  ",
                          mon.get_active_monitor())
        self.debug_detail()
        self.debug_detail("sys.getfilesystemencoding()",
                          sys.getfilesystemencoding())
        self.debug_output()  # self.info.fact() + print()

        self.debug_header("\nAll Windows (Wnck) - mon.get_all_windows():")
        for i, window in enumerate(mon.get_all_windows()):
            ''' Testing desktop - should check each monitor individually '''
            if window.x > mon.screen_width or window.y > mon.screen_height:
                ''' When second monitor loses power '''
                self.debug_detail("\nERROR: Window is off screen at x+y:",
                                  window.x, "+", window.y)
                self.debug_detail("  ", window)
                if window.x > mon.screen_width:
                    adj_x = mon.screen_width - window.x - 500
                else:
                    adj_x = 0
                if window.y > mon.screen_height:
                    adj_y = mon.screen_height - window.y - 500
                else:
                    adj_y = 0
                self.debug_detail("     Adjust to edge -500 amount:", adj_x, "+", adj_y)
                new_x = window.x + adj_x
                new_y = window.y + adj_y
                self.debug_detail("        New coordinates:", new_x, "+", new_y, "\n")
                str_win = str(window.number)  # should remove L in python 2.7.5+
                int_win = int(str_win)  # https://stackoverflow.com/questions
                hex_win = hex(int_win)  # /5917203/python-trailing-l-problem
                # Move window to lower right - 500x500
                os.popen('xdotool windowmove ' + hex_win + ' ' +
                         str(new_x) + ' ' + str(new_y))
                # TODO: Use shark_move to more accurate original coordinates.
                #       Currently instantly appears at lower right -500x-500
            else:
                self.debug_detail(window)
        self.debug_output()  # self.info.fact() + print()


        #self.debug_header("\nTOOLTIPS - tt.line_dump()")
        lines = self.tt.line_dump()         # Show Tooltips in memory
        #for line in lines:
        #    self.debug_detail(line)
        #self.debug_output()
        self.debug_list("TOOLTIPS - tt.line_dump()", lines)

        self.debug_header("\nOpened Location")
        self.debug_detail("lcs.open_code       :", lcs.open_code)
        self.debug_detail("lcs.open_name       :", lcs.open_name)
        self.debug_detail("lcs.open_modify_time:", lcs.open_modify_time)
        self.debug_detail("lcs.open_image_path :", lcs.open_image_path)
        self.debug_detail("lcs.open_mount_point:", lcs.open_mount_point) 
        self.debug_detail("lcs.open_topdir     :", lcs.open_topdir)
        self.debug_detail("lcs.open_host       :", lcs.open_host)
        self.debug_detail("lcs.open_wakecmd    :", lcs.open_wakecmd)
        self.debug_detail("lcs.open_testcmd    :", lcs.open_testcmd)
        self.debug_detail("lcs.open_testrep    :", lcs.open_testrep)
        self.debug_detail("lcs.open_mountcmd   :", lcs.open_mountcmd)
        self.debug_detail("lcs.open_touchcmd   :", lcs.open_touchcmd)
        self.debug_detail("lcs.open_touchmin   :", lcs.open_touchmin)
        self.debug_detail("lcs.open_comments   :", lcs.open_comments)
        self.debug_detail("lcs.open_row_id     :", lcs.open_row_id)
        self.debug_output()


        self.debug_header("\nInformation Centre - self.info.dict[]")
        self.debug_detail("--- KEY ---   --- VALUE ---------------------\n")
        for key in self.info.dict:
            pre = ("[" + str(key) + "]").ljust(12) + ":"  # Padded key field
            if isinstance(self.info.dict[key], list):
                entries = self.info.dict[key]  # type list is a pattern or trace
                if len(entries) == 1:  # If zero, drop down to print regular line
                    self.debug_detail(pre, self.info.dict[key][0])
                    continue
                elif len(entries) > 1:  # If zero, drop down to print regular line
                    self.debug_detail(pre, "list[VALUES] on lines below.")
                    for entry in entries:
                        self.debug_detail(entry)
                    continue
            self.debug_detail(pre, self.info.dict[key])  # regular field type
        self.debug_output()


        self.debug_header("\nCURRENT SONG and COMMON VARIABLES")
        try:
            song_iid = self.saved_selections[self.ndx]
            song = self.lib_tree.item(song_iid)['text']
            album_iid = self.lib_tree.parent(song_iid)
            album = self.lib_tree.item(album_iid)['text']
            artist_iid = self.lib_tree.parent(album_iid)
            artist = self.lib_tree.item(artist_iid)['text']

            self.debug_detail("self.ndx   :", self.ndx, ' | Song iid:', song_iid, " |", song)
            self.debug_detail("tree values:", self.lib_tree.item(song_iid)['values'])
            self.debug_detail("Artist iid :", artist_iid, " |", artist,
                              " | Album iid:", album_iid, " |", album)
            self.debug_detail("real_path  :", self.real_path(int(song_iid)))
        except IndexError:  # list index out of range
            self.debug_detail("INVALID self.ndx for CURRENT_SONG:", self.ndx)

        try:
            self.debug_detail("self.playlist_paths[0]    :", self.playlist_paths[0])
            self.debug_detail("self.playlist_paths[-1]   :", self.playlist_paths[-1])
            self.debug_detail("len(self.playlist_paths)  :", len(self.playlist_paths),
                              " | sys.get size of(self.playlist_paths):",
                              sys.getsizeof(self.playlist_paths))
        except IndexError:  # list index out of range
            self.debug_detail("self.playlist_paths[] is empty.")
        try:
            self.debug_detail("self.saved_selections[0]  :", self.saved_selections[0],
                              " | self.saved_selections[-1]:", self.saved_selections[-1])
            self.debug_detail("len(self.saved_selections):", len(self.saved_selections),
                              " | sys.get size of(self.saved_selections):",
                              sys.getsizeof(self.saved_selections))
        except IndexError:  # list index out of range
            self.debug_detail("self.saved_selections[] is empty.")

        self.debug_detail("self.fake_paths[0]        :", self.fake_paths[0])
        self.debug_detail("self.fake_paths[-1]       :", self.fake_paths[-1])
        self.debug_detail("len(self.fake_paths)      :", len(self.fake_paths),
                          " | sys.get size of(self.fake_paths):",
                          sys.getsizeof(self.fake_paths))
        self.debug_detail("self.real_paths[0]        :", self.real_paths[0])
        self.debug_detail("self.real_paths[-1]       :", self.real_paths[-1])
        self.debug_detail("len(self.real_paths)      :", len(self.real_paths),
                          " | sys.get size of(self.real_paths):",
                          sys.getsizeof(self.real_paths))
        self.debug_detail()

        self.debug_detail("len(SORTED_LIST) Music Location Songs:",
                          len(SORTED_LIST))
        self.debug_detail('len(self.lib_tree.tag_has("Artist")) :',
                          len(self.lib_tree.tag_has("Artist")))
        self.debug_detail('len(self.lib_tree.tag_has("Album"))  :',
                          len(self.lib_tree.tag_has("Album")))
        self.debug_detail('len(self.lib_tree.tag_has("Song"))   :',
                          len(self.lib_tree.tag_has("Song")))
        self.debug_output()


        self.debug_header("\nself.Xxx_ctl = FileControl() instances opened")
        if self.play_ctl.metadata is not None:  # FileControl() always here
            self.debug_detail("Last file accessed - 'ffprobe' (self.play_ctl.metadata):")
            self.debug_detail("--------------------------------------------------------\n")
            for i in self.play_ctl.metadata:
                self.debug_detail(i, ":", self.play_ctl.metadata[i])

        if self.ltp_ctl and self.ltp_ctl.metadata is not None:
            self.debug_detail("\nLast file accessed - 'ffprobe' (self.ltp_ctl.metadata):")
            self.debug_detail("-------------------------------------------------------\n")
            for i in self.ltp_ctl.metadata:
                self.debug_detail(i, ":", self.ltp_ctl.metadata[i])

        if self.fine_tune and self.fine_tune.time_ctl.metadata is not None:
            self.debug_detail("\nLast file accessed - 'ffprobe', " +
                              "'(self.fine_tune.time_ctl.metadata):")
            self.debug_detail("-" * 68 + "\n")
            for i in self.fine_tune.time_ctl.metadata:
                self.debug_detail(i, ":", self.fine_tune.time_ctl.metadata[i])

        if self.mus_ctl and self.mus_ctl.metadata is not None:
            self.debug_detail("\nLast file accessed - 'ffprobe' (self.mus_ctl.metadata):")
            self.debug_detail("-------------------------------------------------------\n")
            for i in self.mus_ctl.metadata:
                self.debug_detail(i, ":", self.mus_ctl.metadata[i])
        self.debug_output()


        self.debug_header("\nGLOBAL VARIABLES")
        self.debug_detail("START_DIR  :", START_DIR, " | START_DIR.count(os.sep):",
                          START_DIR.count(os.sep))
        self.debug_detail("PRUNED_DIR :", PRUNED_DIR, " | PRUNED_COUNT:", PRUNED_COUNT)
        self.debug_detail("TV_VOLUME  :", TV_VOLUME, " | TV_SOUND:", TV_SOUND)
        self.debug_detail("TV_BREAK1  :", TV_BREAK1, " | TV_BREAK2:", TV_BREAK2)
        self.debug_detail("REW_FF_SECS:", REW_FF_SECS, " | REW_CUTOFF:", REW_CUTOFF)
        self.debug_detail("ENCODE_DEV :", ENCODE_DEV)
        self.debug_detail("self.get_pending_cnt_total():", self.get_pending_cnt_total())
        self.debug_detail("pending_apply() debug print flag DPRINT_ON:", DPRINT_ON)
        self.debug_output()


        self.debug_header("\nSQL - Sqlite3 Information")
        self.debug_detail("Sqlite3 Version:", sql.sqlite3.sqlite_version, "\n")
        rows = sql.con.execute("SELECT * FROM sqlite_master;").fetchall()
        for row in rows:  # create tables and indices information
            self.debug_detail(row)
        self.debug_detail()  # Blank line

        # Cannot run vacuum - need SQL version 3.22 for INTO option, current is 3.11
        #sql.con.execute("VACUUM INTO '/run/user/1000/mserve library.db'")

        if sql.ofb.blacks is not None:
            self.debug_detail("\nSQL Blacklisted songs")
            self.debug_detail("-" * 51, "\n")
            for i, entry in enumerate(sql.ofb.blacks):
                self.debug_detail(i, ":", entry)
            self.debug_detail("\nSQL Whitelist substitutes")
            self.debug_detail("-" * 51, "\n")
            for i, entry in enumerate(sql.ofb.whites):
                self.debug_detail(i, ":", entry)

        self.debug_detail("\nSQL Table Sizes")
        self.debug_detail("-" * 51, "\n")

        self.debug_show_sql_table_size("SQL Location Table", "Location")
        self.debug_show_sql_table_size("SQL Music Table", "Music")
        self.debug_show_sql_table_size("SQL History Table", "History")
        self.debug_show_sql_type_action('file', 'init')
        self.debug_show_sql_type_action('file', 'edit')
        self.debug_show_sql_type_action('meta', 'init')
        self.debug_show_sql_type_action('meta', 'edit')
        self.debug_show_sql_type_action('scrape', 'parm')
        self.debug_show_sql_type_action('lyrics', 'scrape')
        #sql.hist_tally_whole()  # Prints tons of lines
        # noinspection SpellCheckingInspection
        ''' To use Virtual Table
        # https://www.sqlite.org/dbstat.html
        try:
            sql.con.execute("CREATE VIRTUAL TABLE temp.stat USING dbstat(main);")
        except sql.sqlite3.Error as er:
            print('SQLite error: %s' % (' '.join(er.args)))
            print("Exception class is: ", er.__class__)
            print("SQL wasn't compiled with SQLITE_ENABLE_DBSTAT_VTAB")
        '''
        self.debug_output()


        if pav.pulse_is_working:
            ''' Fast method using pulse audio direct interface '''
            self.debug_header("\nPulse Audio - vu_pulse_audio.py PulseControl()")

            self.debug_detail("Pulse Audio - sink_input_list (sound sources)")
            self.debug_detail("-"*51, "\n")
            try:
                for sink in pav.pulse.sink_input_list():
                    self.debug_detail("sink:", sink, sink.proplist['application.name'])

                self.debug_detail("\nPulse Audio - sink_list (sound cards)")
                self.debug_detail("-"*51, "\n")
                for sink in pav.pulse.sink_list():
                    self.debug_detail("sink:", sink)

                self.debug_detail("\nPulse Audio - source_list (recording)")
                self.debug_detail("-"*51, "\n")
                for sink in pav.pulse.source_list():
                    self.debug_detail("sink:", sink)

                self.debug_detail("\nPulse Audio - card_list.profile_list")
                self.debug_detail("-"*51, "\n")
                card = pav.pulse.card_list()[0]
                self.debug_detail(card.profile_list)

                self.debug_detail("\nPulse Audio - pulse.server_info().default_sink_name")
                self.debug_detail("-"*51, "\n")
                self.debug_detail(pav.pulse.server_info().default_sink_name)
            except Exception as err:
                self.debug_detail("\nPulse Audio - Exception")
                self.debug_detail(err)
            self.debug_output()


        title = "show_debug() - mserve"
        text = "DEBUG information written to stdout (Standard Output)\n"
        text += "and to Information Centre (use 'View' dropdown menu)"
        #message.ShowInfo(self.lib_top, "DEBUG - mserve",
        #                 "DEBUG information written to stdout (Standard Output)",
        #                 thread=self.get_refresh_thread)
        #self.info.cast("DEBUG information written to stdout (Standard Output)")
        lcs.out_cast_show(title, text)

    # noinspection SpellCheckingInspection
    def debug_show_sql_table_size(self, title, key, prt=True):
        """ Print table page count and size of all pages. """

        sql_cmd = "SELECT count(*) FROM dbstat('main') WHERE name=?;"
        sql.cursor.execute(sql_cmd, [key])
        try:
            d = dict(sql.cursor.fetchone())
            page_count = d['count(*)']
        except sql.sqlite3.Error as er:
            page_count = 0
            self.debug_detail('SQLite error: %s' % (' '.join(er.args)))
            self.debug_detail("Exception class is: ", er.__class__)
            self.debug_detail("SQL wasn't compiled with SQLITE_ENABLE_DBSTAT_VTAB")

        sql_cmd = "SELECT sum(pgsize) FROM dbstat WHERE name=?"
        try:
            sql.cursor.execute(sql_cmd, [key])
        except sql.sqlite3.OperationalError as er:
            self.debug_detail('SQLite error: %s' % (' '.join(er.args)))
            self.debug_detail("Exception class is: ", er.__class__)
            self.debug_detail("SQL Error")
            return

        try:
            d = dict(sql.cursor.fetchone())
            pages_size = d['sum(pgsize)']
        except sql.sqlite3.Error as er:
            self.debug_detail('SQLite error: %s' % (' '.join(er.args)))
            self.debug_detail("Exception class is: ", er.__class__)
            self.debug_detail("SQL wasn't compiled with SQLITE_ENABLE_DBSTAT_VTAB")
            return

        # Location table only has 1 page so needs extra tab to line up size
        tabs = "\t\t" if key == "Location" else "\t"

        if prt:
            self.debug_detail(title, "\tPage Count:", '{:n}'.format(page_count),
                              tabs + "Size of all pages:", '{:n}'.format(pages_size))

        return page_count, pages_size

    def debug_show_sql_type_action(self, Type, Action):
        """ Copied from sql.hist_count_type_action() """
        count = sql.hist_count_type_action(Type, Action, prt=False)
        prt_type = " | Type='" + Type + "' | Action='" + Action + "' | "
        self.debug_detail("    " + 'History Table rows:', prt_type,
                          'count:', '{:n}'.format(count))

    def debug_recreate_file(self, clear_lists=True):
        """ Create an empty debug file and clear debug lists.
            Called when show_debug() first starts and by
            debug_read_print(clear_lists=False). """
        with open(self.debug_file, mode='w') as file_object:
            file_object.write("")
        if clear_lists:
            self.debug_title = []  # When show_debug() starts up, clear lists
            self.debug_text = []  # For debug_read_print(), don't clear lists

    def debug_header(self, *args, **kwargs):
        """ Receive print statement parameters and print to file.
            Read back print file and add to title list.
            If underline is True, add 80 * "=" to title list and "\n". """
        self.debug_print(*args)  # Write to print_file
        result = self.debug_read_print()  # Read print file (or error messages)
        if result:  # Should always be a result
            self.debug_title.append(result)

        ''' Add underlines after heading? '''
        underline = True  # Default as normally only one header + underline
        for key, value in kwargs. iteritems():
            if key == 'underline':
                underline = value
        if underline:
            self.debug_title.append("=" * 90 + "\n\n")

    def debug_detail(self, *args):
        """ Receive print statement parameters and print to file.
            Read back print file and add to text list. """
        self.debug_print(*args)  # Write to print_file
        result = self.debug_read_print()  # Read print file (or error messages)
        if result:  # Should always be a result
            self.debug_title.append(result)

    def debug_list(self, title, lines):
        """
        :param title: E.G. "TOOLTIPS - Line Dump()"
        :param lines: list of lines
        :return: Nothing
        """
        self.debug_header("\n" + title)
        for line in lines:
            self.debug_detail(line)
        self.debug_output()

    def debug_print(self, *args):
        """ Bullet-proof printing to print file """
        with open(self.debug_file, mode='a') as file_object:
            try:
                print(*args, file=file_object)
            except Exception as err:
                file_object.write("Printing to file FAILED. " + 
                                  " Attempting normal print to console.\n")
                try:
                    print("Exception:", err)
                    print("Attempting normal print to console")
                    print(*args)
                    file_object.write("Printing to console SUCCEEDED. " +
                                      " Check console for missed output.\n")
                except Exception as err:
                    print("Exception:", err)
                    print("Normal print to console FAILED TOO!")
                    file_object.write("Printing failed TWICE. See console.\n")

    def debug_read_print(self):
        """ Read results printed to file 
            Empty print_file when done. """
        with open(self.debug_file, mode='r') as file_object:
            result = file_object.read()  # read one line with \n at end
        self.debug_recreate_file(clear_lists=False)  # keep WIP lists in place
        return result

    def debug_output(self):
        """ Sent title and text lists to console and self.info.fact(). """

        for t in self.debug_title:
            print(t, end="")  # do not add "\n" to print stream
        for t in self.debug_text:
            print(t, end="")  # do not add "\n" to print stream
        self.info.fact(''.join(self.debug_title) + ''.join(self.debug_text),
                       collapsed=True, ms_font="TkFixedFont")
        self.debug_recreate_file(clear_lists=True)  # Clear title & text lists

    def show_pulse_audio(self):
        """ Debugging - show machine info, monitors, windows, tooltips
            locations, sql, metadata, global variables """

        ''' Make TMP names unique for multiple FileControls racing at once '''
        letters = string.ascii_lowercase + string.digits
        temp_suffix = (''.join(random.choice(letters) for _i in range(6)))
        self.debug_file = TMP_PRINT_FILE + "_" + temp_suffix  # def debug
        self.debug_recreate_file()  # Clear print file, title and text lists

        self.debug_header("\nPulse Audio Information")

        pactl_list = os.popen("pactl list").read().splitlines()
        self.debug_list("PA Control - 'pactl list'", pactl_list)

        pa_list_cards = os.popen("pacmd list-cards").read().splitlines()
        self.debug_list("PA Command - 'pacmd list-cards'", pa_list_cards)

        cmd = "pacmd list-sinks | " +\
              "grep -e 'name:'  -e 'alsa.device ' -e 'alsa.subdevice '"
        pa_list_sink_names = os.popen(cmd).read().splitlines()
        self.debug_list("'pacmd list-sinks | grep'", pa_list_sink_names)

        aplay_list = os.popen("aplay -l").read().splitlines()
        self.debug_list("aplay list - 'aplay -l'", aplay_list)

        """ Bluetooth doesn't reconnect after suspend 
        $ bluetoothctl
        [NEW] Controller 9C:B6:D0:10:37:F8 Dell AW17R3 [default]
        [NEW] Device D0:77:14:C8:BD:E4 Moto E (4)
        [NEW] Device 0C:A6:94:69:AE:D0 SONY:SRS-X5
        [bluetooth]# connect 0C:A6:94:69:AE:D0
        Attempting to connect to 0C:A6:94:69:AE:D0
        [CHG] Device 0C:A6:94:69:AE:D0 Connected: yes
        Failed to connect: org.bluez.Error.Failed
        [CHG] Device 0C:A6:94:69:AE:D0 Connected: no

        FINAL SOLUTION:
        
        1) bluetoothctl 
        2) power on
        3) connect 0C:A6:94:69:AE:D0
        4) quit
        
        USE 'expect' script:

        ~/python$ cat blueresume

        #!/usr/bin/expect -f
        # Resume bluetooth after sleep for Sony XRS speaker
        # Requires 'sudo apt install expect'
        # https://gist.github.com/RamonGilabert/046727b302b4d9fb0055
        
        ...
        
        """
    # ==============================================================================
    #
    #       Music Location Tree Processing - Top menu: SQL Music & SLQ History
    #
    # ==============================================================================

    def show_sql_music(self, sbar_width=14):
        """ Open SQL Music Location treeview. """
        ''' SQL Music Table View already active? '''
        if self.mus_top_is_active is True:
            self.mus_top.lift()
            return

        music_dict = sql.music_treeview()
        columns = ["os_filename", "track_number", "row_id", "os_atime",
                   "os_file_size", "artist", "album", "title", "lyrics", "genre"]
        toolkit.select_dict_columns(columns, music_dict)
        # toolkit.print_dict_columns(music_dict)

        ''' SQL Music Table View is now active '''
        self.mus_top_is_active = True
        self.mus_top = tk.Toplevel()
        self.mus_top.title("SQL Music Table - mserve")

        ''' Set program icon in taskbar '''
        img.taskbar_icon(self.mus_top, 64, 'white', 'lightskyblue', 'black')

        ''' Mount window at previously used location '''
        self.mus_top.minsize(width=g.WIN_MIN_WIDTH, height=g.WIN_MIN_HEIGHT)
        # What if there is no saved geometry?
        geom = monitor.get_window_geom('sql_music')
        self.mus_top.geometry(geom)
        self.mus_top.configure(background="Gray")
        self.mus_top.columnconfigure(0, weight=1)
        self.mus_top.rowconfigure(0, weight=1)

        ''' Create master frame for treeview and buttons '''
        master_frame = tk.Frame(self.mus_top, bg="LightGrey", relief=tk.RIDGE)
        master_frame.grid(sticky=tk.NSEW)
        master_frame.columnconfigure(0, weight=1)
        master_frame.rowconfigure(0, weight=1)

        ''' Create treeview frame with scrollbars '''
        self.mus_view = toolkit.DictTreeview(
            music_dict, self.mus_top, master_frame, columns=columns,
            sbar_width=sbar_width)

        ''' Treeview select item - custom select processing '''
        toolkit.MoveTreeviewColumn(self.mus_top, self.mus_view.tree,
                                   row_release=self.mus_button_3_click)
        self.mus_view.tree.bind("<Button-3>", self.mus_button_3_click)

        ''' Populate Treeview item list with all songs. '''
        dtb = message.DelayedTextBox(title="Building SQL Music Table View",
                                     toplevel=self.mus_top, width=1000)
        self.populate_mus_tree(dtb)
        dtb.close()

        ''' Treeview Buttons '''
        frame3 = tk.Frame(master_frame, bg="LightGrey", bd=2, relief=tk.GROOVE,
                          borderwidth=g.FRM_BRD_WID)
        frame3.grid_rowconfigure(0, weight=1)
        frame3.grid_columnconfigure(0, weight=0)
        frame3.grid(row=1, column=0, sticky=tk.NW)

        ''' ✘ Close Button '''
        self.mus_top.bind("<Escape>", self.mus_close)
        self.mus_top.protocol("WM_DELETE_WINDOW", self.mus_close)
        self.mus_view_btn1 = tk.Button(frame3, text="✘ Close",
                                       width=g.BTN_WID - 2, command=self.mus_close)
        self.mus_view_btn1.grid(row=0, column=0, padx=2)
        self.tt.add_tip(
            self.mus_view_btn1, "Close SQL Music Table view.",
            anchor="nw")

        ''' “🗑” U+1F5D1 (trash can) - Missing Metadata '''
        self.mus_view_btn2 = tk.Button(
            frame3, text="🗑 Missing Metadata", width=g.BTN_WID,
            command=self.missing_metadata)
        self.mus_view_btn2.grid(row=0, column=1, padx=2)
        self.tt.add_tip(
            self.mus_view_btn2, "No Metadata - Songs never played in mserve.",
            anchor="nw")

        ''' 🗑 Missing Lyrics '''
        self.mus_view_btn3 = tk.Button(
            frame3, text="🗑 Missing Lyrics", width=g.BTN_WID - 1,
            command=self.missing_lyrics)
        self.mus_view_btn3.grid(row=0, column=2, padx=2)
        self.tt.add_tip(self.mus_view_btn3,
                        "Lyrics have not be scraped from websites.", anchor="nw")

        ''' 🗑 Lyrics UnSynced '''
        self.mus_view_btn4 = tk.Button(
            frame3, text="🗑 Lyrics UnSynced", width=g.BTN_WID - 1,
            command=self.unsynchronized)
        self.mus_view_btn4.grid(row=0, column=3, padx=2)
        self.tt.add_tip(self.mus_view_btn4,
                        "Lyric score not time synchronized.", anchor="ne")

        ''' 🔍 Text Search '''
        self.mus_view_btn5 = tk.Button(
            frame3, text="🔍  Text Search", width=g.BTN_WID - 2,
            command=self.mus_text_search)
        self.mus_view_btn5.grid(row=0, column=4, padx=2)
        self.tt.add_tip(self.mus_view_btn5,
                        "Search for text strings everywhere.", anchor="ne")

        '''  🖸 (1f5b8) - Update Metadata '''
        self.mus_view_btn6 = tk.Button(
            frame3, text="🖸  Update Metadata", width=g.BTN_WID,
            command=self.missing_artwork)
        self.mus_view_btn6.grid(row=0, column=5, padx=2)
        self.tt.add_tip(self.mus_view_btn6,
                        "Apply metadata & show missing artwork.", anchor="ne")

        '''  “∑” (U+2211) - Summarize sizes and count rows '''
        self.mus_view_btn7 = tk.Button(frame3, text="∑  Summary",
                                       width=g.BTN_WID - 2, command=lambda:
                                       self.tree_summary(self.mus_view))
        self.mus_view_btn7.grid(row=0, column=6, padx=2)
        self.tt.add_tip(self.mus_view_btn7,
                        "Tally sizes and count rows.", anchor="ne")

        ''' Colors for tags '''
        self.ignore_item = None  # purpose?
        self.mus_view.tree.tag_configure('menu_sel', background='Yellow')
        self.mus_view.tree.tag_configure('no_audio', background='Red',
                                         foreground='White')

    def populate_mus_tree(self, delayed_textbox):
        """ Stuff SQL Music Table rows into treeview """
        sql.cursor.execute("SELECT * FROM Music INDEXED BY OsFileNameIndex\
                           ORDER BY OsFileName")
        rows = sql.cursor.fetchall()
        if rows:
            self.insert_view_lines(self.mus_view, rows, delayed_textbox)

    def mus_text_search(self):
        """ Search all Music Table treeview columns for text string """
        if self.mus_search:  # Already running? Close last search.
            self.mus_search.close()
        self.mus_search = toolkit.SearchText(self.mus_view, find_str=None,
                                             tt=self.tt)
        self.mus_search.find()  # Search the text string in all columns

    def missing_metadata(self):
        """ Uses string search function for metadata song title is None """
        if self.mus_search:
            self.mus_search.close()

        self.mus_search = toolkit.SearchText(
            self.mus_view, column='title', find_str='', find_op='==')
        self.mus_search.find_column()  # Find song title == None

        # Popup row count and total file sizes
        self.tree_summary(self.mus_view, title="Songs not played yet")

    def missing_lyrics(self):
        """ Find Songs that have no lyrics (no webscrape has been done) """
        if self.mus_search:
            self.mus_search.close()

        self.mus_search = toolkit.SearchText(
            self.mus_view, find_str='callback',
            callback=self.missing_lyrics_callback)
        self.mus_search.find_callback()  # Using callback

        # Popup row count and total file sizes
        self.tree_summary(self.mus_view, title="Songs with no Lyrics")

    def missing_lyrics_callback(self, _Id, values):
        """ Find Songs that have no lyrics (no webscrape has been done)

            If Treeview value is u'None' for song name so no lyrics anyway
            and return false. """
        title = self.mus_view.column_value(values, 'title')
        if title == u'None':  # Skip songs with no metadata, no chance for scrape
            return False  # Treeview value is u'None' for song name so no lyrics

        os_filename = self.mus_view.column_value(values, 'os_filename')
        lyrics, _time_index = sql.get_lyrics(os_filename)
        if lyrics is not None:
            return False  # Lyrics are non-blank.

        return True  # Song with metadata (title) has no lyrics.

    def unsynchronized(self):
        """ Find songs that have no time index (lyric score not synchronized) """
        if self.mus_search:
            self.mus_search.close()

        self.mus_search = toolkit.SearchText(
            self.mus_view, find_str='callback',
            callback=self.unsynchronized_callback)
        self.mus_search.find_callback()

        # Popup row count and total file sizes
        self.tree_summary(self.mus_view, title="Lyrics not synchronized")

    def unsynchronized_callback(self, _Id, values):
        """ Find Songs that have have lyrics but no time_index

            If Treeview value is u'None' for song name or if lyrics is None,
            skip test. Else test for time index existing. """
        title = self.mus_view.column_value(values, 'title')
        if title == u'None':
            return False  # Treeview value is u'None' for song name so no lyrics

        ''' Get lyrics and time index from SQL Music Table '''
        os_filename = self.mus_view.column_value(values, 'os_filename')
        lyrics, time_index = sql.get_lyrics(os_filename)

        if lyrics is None:
            return False  # Lyrics haven't been scraped so skip time check

        if time_index is not None:
            return False  # Time index is non-blank.

        return True  # Song with metadata (title) and lyrics has no time_index.

    def missing_artwork(self):
        """ Find Songs that have no artwork and update metadata
            Lengthy process so get permission to proceed.
            File may not exist in this location.
            If file does exist grab metadata with FileControl.new()
            Updates file last access time which needs to be reversed.
            Uses mus_ctl() class to verify file exists and read metadata so only
                one instance of SQL Music Table View can be opened at a time.
        """
        if self.mus_search:
            self.mus_search.close()  # Close old search

        answer = message.AskQuestion(
            self.mus_top, thread=self.get_refresh_thread, confirm='no',
            title='Update Metadata and Report "missing" confirmation - mserve',
            text="Every music file will be read. This takes 1 minute/1,000" +
                 " files. Missing metadata in the SQL\nMusic Table will be updated. " +
                 "Songs with no artwork (or no audio in red) will be displayed.\n\n" +
                 "Music will keep playing but some buttons will be disabled.\n\n" +
                 "Do you want to perform this lengthy process?")
        if answer.result != 'yes':
            return

        ''' Pause music if playing '''
        forced_pause = False
        ''' Aug 9/23 - experiment 2 
        if self.play_top_is_active:
            if self.pp_state == "Playing":
                self.pp_toggle()
                forced_pause = True
                # Need 1 second to fade out music and pause
                for _i in range(10):
                    self.refresh_play_top()  # Gently fade volume to 25%
                    self.play_top.after(33)
        '''

        ext.t_init("missing_artwork()")
        ''' TODO: Clear title when new button clicked '''
        self.mus_top.title("Music files with Missing Artwork (and " +
                           "missing Audio in Red) - mserve")

        self.info.cast("Begin Update Metadata and display missing artwork.")
        self.start_long_running_process()

        ''' Initialize reading file control instance '''
        self.mus_ctl = FileControl(self.lib_top, self.info, silent=True,
                                   log_level='error',  # don't log info facts
                                   get_thread=self.get_refresh_thread)

        ''' Initialize scan filter / tally instance '''
        #self.meta_scan = encoding.MetaScan(self.mus_top, self.get_refresh_thread)
        self.meta_scan = encoding.MetaScan(self.mus_top)  # Turn off refresh

        ''' Initialize delayed text box instance for user feed back '''
        self.missing_artwork_dtb = message.DelayedTextBox(
            title="SQL Music Table Scan", toplevel=self.mus_top, width=1000)

        ''' Initialize search instance with callback here (below)  '''
        self.mus_search = toolkit.SearchText(  # search all using callback
            self.mus_view, callback=self.missing_artwork_callback,
            find_str='callback', thread=self.get_refresh_thread)

        ''' Perform search for missing artwork & update metadata at same time '''
        self.mus_search.find_callback()  # attach desired to treeview
        self.end_long_running_process()

        ''' Unpause music '''
        if forced_pause:
            self.pp_toggle()  # Restore playing song that was paused
        
        ''' Close delayed text window '''
        if self.missing_artwork_dtb:
            self.missing_artwork_dtb.close()  # Close delayed text box
        ext.t_end("print")  #

        ''' Was window closed? '''
        if not self.meta_scan:
            return

        ''' Display summary counts '''
        text = "SQL Music Table rows: " + "{:,}".\
            format(self.meta_scan.total_scanned) + "\n" + \
            "In other locations: " + "{:,}".\
            format(self.meta_scan.missing_file_at_loc) + "\n" + \
            "Missing audio: " + "{:,}".\
            format(self.meta_scan.missing_audio) + "\n" + \
            "Missing artwork: " + "{:,}".\
            format(self.meta_scan.missing_artwork) + "\n" + \
            "Found artwork: " + "{:,}".\
            format(self.meta_scan.found_artwork) + "\n" + \
            "Metadata updated: " + "{:,}".\
            format(self.meta_scan.meta_data_updated) + "\n" + \
            "Metadata skipped: " + "{:,}".\
            format(self.meta_scan.meta_data_unchanged) + "\n\n" + \
            "Click 'OK' to close and then you can continue working.\n"

        title = "Update Metadata & Missing Artwork Summary"
        message.ShowInfo(self.mus_top, title, text,
                         thread=self.get_refresh_thread)
        self.info.fact(title + "\n\n" + text)

    def missing_artwork_callback(self, Id, values):
        """ Find Songs that have no artwork and update metadata
            sql.update_metadata() is called by get_ffprobe_metadata(os_filename)
            The .CheckArtwork() function will call self.refresh_play_top().
                This causes freeze up as play_top steals processing cycles.
            When file has artwork no need to update delayed text box because
                visual feedback is in treeview when file is detached from list.

            REMINDER:
            self.meta_scan = encoding.MetaScan(self.mus_top, self.get_refresh_thread)

        :param Id: Treeview Id
        :param values: mus_view.tree values for current row being processed
        :return: True if artwork exists, False if not or if different location
        """

        ''' Reading through filenames in mus_view.tree which also has music ID '''
        os_filename = self.mus_view.column_value(values, 'os_filename')
        #self.lib_top.update_idletasks()  # Give chance to 'X' the window
        if not self.mus_top:
            return  # None=closing. Others are False=detach and True=keep.
        self.mus_top.update()  # Aug 9/23 - Above is too slow to close

        ''' Aug 9/23 - Allow play_to_end() to run. '''
        lcs.fast_refresh(tk_after=False)  # Aug 9/23 keep spinning till end

        ''' Aug 20/23 - Quick check to see if over-legalizing dir names '''
        parts = os_filename.split(os.sep)
        legal_part1 = ext.legalize_dir_name(parts[0])
        legal_part2 = ext.legalize_dir_name(parts[1])
        legal_part3 = ext.legalize_dir_name(parts[2])
        if legal_part1 != parts[0]:
            print("over-legalized parts[0]", legal_part1)
        if legal_part2 != parts[1]:
            print("over-legalized parts[1]", legal_part2)
        if legal_part3 != parts[2]:
            print("over-legalized parts[2]", legal_part3)

        ''' Sep 6/23 - Duplicate size check in lib_populate_tree '''
        os_file_size = self.mus_view.column_value(values, 'os_file_size')
        if os_file_size < g.MUSIC_MIN_SIZE:
            # Not a valid music file
            str_size = '{:n}'.format(g.MUSIC_MIN_SIZE)
            ''' Show in Delayed Text Box but Control+C not working for copy. '''
            self.missing_artwork_dtb.update(
                "3) File size < " + str_size + " bytes: " + os_filename)
            self.meta_scan.total_scanned += 1
            self.meta_scan.missing_audio += 1
            toolkit.tv_tag_add(self.mus_view.tree, Id, 'no_audio')
            return True  # Keep in treeview

        ''' Must call first to populate file_ctl() class static variables '''
        if not self.mus_ctl.new(PRUNED_DIR + os_filename):  # get metadata
            # .new() returns False when file doesn't exist at this location
            self.missing_artwork_dtb.update("2) Other Location: " +
                                            os_filename)  # Refresh screen with song file name
            self.meta_scan.missing_file_at_loc += 1
            self.meta_scan.total_scanned += 1
            return False  # This could be separate button search

        if self.mus_ctl.invalid_audio:
            # Not a valid music file
            ''' Show in Delayed Text Box but Control+C not working for copy. '''
            self.missing_artwork_dtb.update("1) Not a music file: " +
                                            os_filename)  # Refresh screen with song file name
            self.meta_scan.total_scanned += 1
            self.meta_scan.missing_audio += 1
            toolkit.tv_tag_add(self.mus_view.tree, Id, 'no_audio')
            self.mus_ctl.close()  # Never was or no longer a music file.
            return True  # Keep in treeview

        ''' Update SQL metadata using this location's music file metadata '''
        result = self.update_sql_metadata(self.mus_ctl)  # Is this resetting?
        if not self.mus_top:  # Update below getting error when closing
            return  # None=closing. Others are False=detach and True=keep.
        self.meta_scan.UpdateChanges(result)  # Tally change counts

        ''' Check if file metadata has artwork '''
        has_art = self.meta_scan.CheckArtwork(self.mus_ctl.metadata)
        self.mus_ctl.close()  # close filename and reset all variables
        if has_art:
            ''' Will disappear from treeview to give user feedback '''
            return False  # Don't keep this one in treeview
        else:
            ''' Stays in treeview so update delayed text box for user feedback '''
            self.missing_artwork_dtb.update("Missing artwork: " +
                                            os_filename)  # Refresh screen with song file name
            return True  # keep this one in treeview

    # noinspection PyUnusedLocal
    def mus_close(self, *args):
        """ Close SQL Music Table View
            May be called with 'X' to close window while find callbacks running.
        """
        self.pretty_close()  # Will close his_top or lcs_top pretty too
        last_geometry = monitor.get_window_geom_string(
            self.mus_top, leave_visible=False)
        monitor.save_window_geom('sql_music', last_geometry)
        self.tt.close(self.mus_top)  # Close tooltips under top level
        self.mus_top_is_active = False
        self.mus_top.destroy()
        self.mus_top = None  # Checked in toolkit.py SearchText() class
        self.mus_search = None
        self.meta_scan = None
        if self.missing_artwork_dtb:
            self.missing_artwork_dtb.close()  # Close delayed text box
        self.missing_artwork_dtb = None
        if self.long_running_process:
            self.end_long_running_process()

    def show_sql_hist(self, sbar_width=14):
        """ Open SQL History treeview. Patterned after show_sql_music() """
        ''' SQL History Table View already active? '''
        if self.his_top_is_active is True:
            self.his_top.lift()
            return

        history_dict = sql.history_treeview()
        """ Define Data Dictionary treeview columns for history table.  Snippet:
            ("column", "time"), ("heading", "Time"), ("sql_table", "History"),
            ("column", "music_id"), ("heading", "Music ID"), ("sql_table", "History"),
            ("column", "user"), ("heading", "User"), ("sql_table", "History"),
            ("column", "type"), ("heading", "Type"), ("sql_table", "History"),
            ("column", "action"), ("heading", "Action"), ("sql_table", "History"),
            ("column", "master"), ("heading", "Master"), ("sql_table", "History"),
            ("column", "detail"), ("heading", "Detail"), ("sql_table", "History"),
            ("column", "target"), ("heading", "Target"), ("sql_table", "History"),
            ("column", "size"), ("heading", "Size"), ("sql_table", "History"),
            ("column", "count"), ("heading", "Count"), ("sql_table", "History"),
            ("column", "comments"), ("heading", "Comments"), ("sql_table", "History"),
            ("column", "seconds"), ("heading", "Seconds"), ("sql_table", "History"),
            ("column", "row_id"), ("heading", "Row ID"), ("sql_table", "History"),
            ("column", "reason"), ("heading", "Reason"), ("sql_table", "calc"),

        """
        # Note: Metadata may be none for artist, album, title, genre, etc.
        columns = ["time", "row_id", "music_id", "type", "action", "master",
                   "detail", "target", "size", "count", "seconds", "comments"]
        toolkit.select_dict_columns(columns, history_dict)
        # toolkit.print_dict_columns(history_dict)

        ''' SQL History Table View is now active '''
        self.his_top_is_active = True
        self.his_top = tk.Toplevel()
        self.his_top.title("SQL History Table - mserve")

        ''' Set program icon in taskbar '''
        img.taskbar_icon(self.his_top, 64, 'white', 'lightskyblue', 'black')

        ''' Mount window at previously used location '''
        self.his_top.minsize(width=g.WIN_MIN_WIDTH, height=g.WIN_MIN_HEIGHT)
        geom = monitor.get_window_geom('sql_history')
        self.his_top.geometry(geom)

        self.his_top.configure(background="Gray")
        self.his_top.columnconfigure(0, weight=1)
        self.his_top.rowconfigure(0, weight=1)

        ''' Create master frame for treeview and buttons '''
        master_frame = tk.Frame(self.his_top, bg="LightGrey", relief=tk.RIDGE)
        master_frame.grid(sticky=tk.NSEW)
        master_frame.columnconfigure(0, weight=1)
        master_frame.rowconfigure(0, weight=1)

        ''' Create treeview frame with scrollbars '''
        self.his_view = toolkit.DictTreeview(
            history_dict, self.his_top, master_frame, columns=columns,
            sbar_width=sbar_width)

        ''' Treeview select item - custom select processing '''
        toolkit.MoveTreeviewColumn(self.his_top, self.his_view.tree,
                                   row_release=self.his_button_3_click)
        self.his_view.tree.bind("<Button-3>", self.his_button_3_click)

        ''' Create Treeview item list with all history. '''
        dtb = message.DelayedTextBox(title="Building SQL History Table View",
                                     toplevel=self.his_top, width=1000)
        self.populate_his_tree(dtb)
        dtb.close()

        ''' Treeview Buttons '''
        frame3 = tk.Frame(master_frame, bg="LightGrey", bd=2, relief=tk.GROOVE,
                          borderwidth=g.FRM_BRD_WID)
        frame3.grid_rowconfigure(0, weight=1)
        frame3.grid_columnconfigure(0, weight=0)
        frame3.grid(row=1, column=0, sticky=tk.NW)

        ''' ✘ Close Button '''
        self.his_top.bind("<Escape>", self.his_close)
        self.his_top.protocol("WM_DELETE_WINDOW", self.his_close)
        self.his_view_btn1 = tk.Button(frame3, text="✘ Close",
                                       width=g.BTN_WID - 2, command=self.his_close)
        self.his_view_btn1.grid(row=0, column=0, padx=2)
        self.tt.add_tip(self.his_view_btn1,
                        "Close SQL History Table viewer .", anchor="nw")

        ''' Configuration Rows '''
        self.his_view_btn2 = tk.Button(
            frame3, text="🔍 Configuration Rows", width=g.BTN_WID + 2,
            command=self.his_configuration_rows)
        self.his_view_btn2.grid(row=0, column=1, padx=2)
        self.tt.add_tip(self.his_view_btn2, "History Rows used for configuration.",
                        anchor="nw")

        ''' Encode CD Rows '''
        self.his_view_btn3 = tk.Button(
            frame3, text="🔍 Encode CD Rows", width=g.BTN_WID + 2,
            command=self.his_encoding_rows)
        self.his_view_btn3.grid(row=0, column=2, padx=2)
        self.tt.add_tip(self.his_view_btn3, "History of CD encoding (Ripping).",
                        anchor="nw")

        ''' 🔍 Text Search '''
        self.his_view_btn5 = tk.Button(frame3, text="🔍  Text Search",
                                       width=g.BTN_WID - 2, command=self.his_text_search)
        self.his_view_btn5.grid(row=0, column=4, padx=2)
        self.tt.add_tip(self.his_view_btn5,
                        "Refresh view, removing any filters", anchor="ne")

        '''  “∑” (U+2211) - Summarize sizes and count rows '''
        self.his_view_btn7 = tk.Button(frame3, text="∑  Summary",
                                       width=g.BTN_WID - 2, command=lambda:
                                       self.tree_summary(self.his_view))
        self.his_view_btn7.grid(row=0, column=6, padx=2)
        self.tt.add_tip(self.his_view_btn7,
                        "Tally sizes and count rows.", anchor="ne")

        ''' Colors for tags '''
        self.ignore_item = None
        self.his_view.tree.tag_configure('menu_sel', background='Yellow')

    def populate_his_tree(self, delayed_textbox):
        """ Stuff SQL header rows into treeview """
        sql.hist_cursor.execute("SELECT * FROM History")
        rows = sql.hist_cursor.fetchall()
        if rows:
            self.insert_view_lines(self.his_view, rows, delayed_textbox)

    def his_text_search(self):
        """ Search all treeview columns for text string """
        if self.his_search is not None:
            self.his_search.close()

        self.his_search = toolkit.SearchText(
            self.his_view, find_str=None, tt=self.tt)
        self.his_search.find()

    def his_configuration_rows(self):
        """ Uses callback for Music ID = 0, <> 'Encoding' """
        if self.his_search is not None:
            self.his_search.close()

        ''' Initialize search instance with callback here (below)  '''
        self.his_search = toolkit.SearchText(  # search all using callback
            self.his_view, find_str='callback', callback=self.his_config_callback)

        ''' Perform search for missing artwork & update metadata at same time '''
        self.his_search.find_callback()  # attach desired to treeview

    def his_config_callback(self, _Id, values):
        """ Find History rows where Music ID = 0, SourceMaster != 'encode'
        :return: True if matches, else returns False
        """
        music_id = self.his_view.column_value(values, 'music_id')
        Type = self.his_view.column_value(values, 'type')

        return music_id == 0 and Type != 'encode'

    def his_encoding_rows(self):
        """ Uses callback for Music ID = 0, == 'Encoding' """
        if self.his_search is not None:
            self.his_search.close()
            ''' Initialize search instance with callback here (below)  '''
            self.his_search = toolkit.SearchText(  # search all using callback
                self.his_view, find_str='callback', callback=self.his_encode_callback)

            ''' Perform search for missing artwork & update metadata at same time '''
            self.his_search.find_callback()  # attach desired to treeview

    def his_encode_callback(self, _Id, values):
        """ Find History rows where Music ID = 0, SourceMaster == 'encode'
        :return: True if matches, else returns False
        """
        music_id = self.his_view.column_value(values, 'music_id')
        Type = self.his_view.column_value(values, 'type')

        return music_id == 0 and Type == 'encode'

    # noinspection PyUnusedLocal
    def his_close(self, *args):
        """ Close SQL History Table View """
        self.pretty_close()  # Inadvertently closes if opened by mus_top
        last_geometry = monitor.get_window_geom_string(
            self.his_top, leave_visible=False)
        monitor.save_window_geom('sql_history', last_geometry)
        self.tt.close(self.his_top)  # Close tooltips under top level
        self.his_top_is_active = False
        self.his_top.destroy()
        self.his_top = None  # Extra Insurance
        self.his_search = None

    def show_sql_location(self, sbar_width=14):
        """ Open SQL Location treeview. Patterned after show_sql_music() """

        ''' SQL Location Table View already active? '''
        if self.lcs_top_is_active is True:
            self.lcs_top.lift()
            return

        location_dict = sql.location_treeview()
        columns = ["code", "name", "topdir", "image_path", "host_name",
                   "comments"]
        toolkit.select_dict_columns(columns, location_dict)

        ''' SQL Location Table View is now active '''
        self.lcs_top_is_active = True
        self.lcs_top = tk.Toplevel()
        self.lcs_top.title("SQL Location Table - mserve")

        ''' Set program icon in taskbar '''
        img.taskbar_icon(self.lcs_top, 64, 'white', 'lightskyblue', 'black')

        ''' Mount window at previously used location '''
        self.lcs_top.minsize(width=g.WIN_MIN_WIDTH, height=g.WIN_MIN_HEIGHT)
        geom = monitor.get_window_geom('sql_location')
        self.lcs_top.geometry(geom)

        self.lcs_top.configure(background="Gray")
        self.lcs_top.columnconfigure(0, weight=1)
        self.lcs_top.rowconfigure(0, weight=1)

        ''' Create master frame for treeview and buttons '''
        master_frame = tk.Frame(self.lcs_top, bg="LightGrey", relief=tk.RIDGE)
        master_frame.grid(sticky=tk.NSEW)
        master_frame.columnconfigure(0, weight=1)
        master_frame.rowconfigure(0, weight=1)

        ''' Create treeview frame with scrollbars '''
        self.lcs_view = toolkit.DictTreeview(
            location_dict, self.lcs_top, master_frame, columns=columns,
            sbar_width=sbar_width)

        ''' Treeview select item - custom select processing '''
        toolkit.MoveTreeviewColumn(self.lcs_top, self.lcs_view.tree,
                                   row_release=self.lcs_button_3_click)
        self.lcs_view.tree.bind("<Button-3>", self.lcs_button_3_click)

        ''' Create Treeview item list with all history. '''
        dtb = message.DelayedTextBox(title="Building SQL Location Table View",
                                     toplevel=self.lcs_top, width=1000)
        self.populate_lcs_tree(dtb)
        dtb.close()

        ''' Treeview Buttons '''
        frame3 = tk.Frame(master_frame, bg="LightGrey", bd=2, relief=tk.GROOVE,
                          borderwidth=g.FRM_BRD_WID)
        frame3.grid_rowconfigure(0, weight=1)
        frame3.grid_columnconfigure(0, weight=0)
        frame3.grid(row=1, column=0, sticky=tk.NW)

        ''' ✘ Close Button '''
        self.lcs_top.bind("<Escape>", self.lcs_close)
        self.lcs_top.protocol("WM_DELETE_WINDOW", self.lcs_close)
        self.lcs_view_btn1 = tk.Button(frame3, text="✘ Close",
                                       width=g.BTN_WID - 2, command=self.lcs_close)
        self.lcs_view_btn1.grid(row=0, column=0, padx=2)
        self.tt.add_tip(self.lcs_view_btn1,
                        "Close SQL Location Table viewer .", anchor="nw")

        ''' 🔍 Text Search '''
        self.lcs_view_btn5 = tk.Button(frame3, text="🔍  Text Search",
                                       width=g.BTN_WID - 2, command=self.lcs_text_search)
        self.lcs_view_btn5.grid(row=0, column=4, padx=2)
        self.tt.add_tip(self.lcs_view_btn5,
                        "Refresh view, removing any filters", anchor="ne")

        '''  “∑” (U+2211) - Summarize sizes and count rows '''
        self.lcs_view_btn7 = tk.Button(frame3, text="∑  Summary",
                                       width=g.BTN_WID - 2, command=lambda:
                                       self.tree_summary(self.lcs_view))
        self.lcs_view_btn7.grid(row=0, column=6, padx=2)
        self.tt.add_tip(self.lcs_view_btn7,
                        "Tally sizes and count rows.", anchor="ne")

        ''' Colors for tags '''
        self.ignore_item = None
        self.lcs_view.tree.tag_configure('menu_sel', background='Yellow')

    def populate_lcs_tree(self, delayed_textbox):
        """ Stuff SQL header rows into treeview
            TODO: Review 'delayed_textbox'. If only used here, define it below.
        """
        sql.loc_cursor.execute("SELECT * FROM Location")
        rows = sql.loc_cursor.fetchall()
        if rows:
            self.insert_view_lines(self.lcs_view, rows, delayed_textbox)

    def lcs_text_search(self):
        """ Search all treeview columns for text string """
        if self.lcs_search is not None:
            self.lcs_search.close()

        self.lcs_search = toolkit.SearchText(
            self.lcs_view, find_str=None, tt=self.tt)
        self.lcs_search.find()

    # noinspection PyUnusedLocal
    def lcs_close(self, *args):
        """ Close SQL Location Table View """
        self.pretty_close()  # Inadvertently closes if opened by mus_top
        last_geometry = monitor.get_window_geom_string(
            self.lcs_top, leave_visible=False)
        monitor.save_window_geom('sql_location', last_geometry)
        self.tt.close(self.lcs_top)  # Close tooltips under top level
        self.lcs_top_is_active = False
        self.lcs_top.destroy()
        self.lcs_top = None  # Extra Insurance
        self.lcs_search = None

    @staticmethod
    def insert_view_lines(dd_view, rows, delayed_textbox, test=None):
        """ Stuff SQL table rows into treeview
            Used for populate_mus_view and populate_his_view
            test used to omit specific rows from view.
            TODO: Review if 'self.refresh_play_top()' should be called
                  Problem with previous/next song stalling other xxx_top running
        """
        first_id = None
        #for i, sql_row in enumerate(rows):
        for sql_row in rows:
            row = dict(sql_row)
            sql_row_id = row['Id']  # Used for treeview iid ('Id' in both tables)

            if test is not None:
                if not test(row):
                    dd_view.attached[str(sql_row_id)] = None  # Skipped
                    continue

            if first_id is None:
                first_id = sql_row_id  # Display first row when done

            # NOTE: dd_view.insert() has different parameters than tree.insert()!
            dd_view.insert("", dict(row), iid=str(sql_row_id), tags="unchecked")
            dd_view.attached[str(sql_row_id)] = True  # row is attached to view

            ''' Delayed Text Box (dtb_line) displays only if lag experienced  '''
            if 'OsFileName' in row:
                dtb_line = row['OsFileName']  # SQL Music Table only
            elif 'MusicId' in row:
                dtb_line = "History time: " + sql.sql_format_date(row['Time'])
            else:
                dtb_line = "Code-Name time: " + row['Code'] + "-" + row['Name']

            if delayed_textbox.update(dtb_line):
                # delayed_textbox returns true only when visible otherwise
                # in quiet mode because not enough time has passed.
                #dd_view.tree.see(sql_row_id)  # Takes long time
                #dd_view.tree.update()
                pass

        # Display first row
        dd_view.tree.see(first_id)
        dd_view.tree.update()

    def mus_button_3_click(self, event):
        """ Right button clicked to drill down on SQL Music treeview line.
            Left Click and hold on heading to drag column and change order. """
        self.view = self.mus_view  # Set self.view to self.his_view or self.mus_view
        self.common_top = self.mus_top
        self.common_button_3(event)

    def his_button_3_click(self, event):
        """ Right button clicked to drill down on SQL History treeview line.
            Left Click and hold on heading allows column to be dragged.
        """
        self.view = self.his_view  # Set self.view to self.his_view or self.mus_view
        self.common_top = self.his_top
        self.common_button_3(event)

    def lcs_button_3_click(self, event):
        """ Right button clicked to drill down on SQL Location treeview line.
            Left Click and hold on heading allows column to be dragged.
        """
        return  # Nothing to display.

    def common_button_3(self, event):
        """ Right button clicked in SQL Music, History or Location treeview.

            If clicked on a row then use message header dictionary to
            pretty format gmail message header details, or extract backup.

            If clicked on a heading then display data dictionary for
            that heading. Later expand to trap B1-Motion and move
            heading left or right to change column position in treeview.
            Then give option to save the custom view under a new name.

            If clicked on a separator then potentially do something to
            record column width change.

        """
        # Mimic CheckboxTreeview self._box_click() code
        x, y, widget = event.x, event.y, event.widget
        # elem = widget.identify("element", x, y)

        ''' Was region of treeview clicked a "separator"? '''
        clicked_region = self.view.tree.identify("region", event.x, event.y)
        if clicked_region == 'separator':
            # TODO adjust stored column widths
            return

        # From: https://stackoverflow.com/a/62724993/6929343
        if clicked_region == 'heading':
            column_number = self.view.tree.identify_column(event.x)  # returns '#?'
            if self.common_top == self.mus_top:
                title = "SQL Music Table"
            elif self.common_top == self.his_top:
                title = "SQL History Table"
            else:
                title = "SQL Location Table"
            self.create_window(title + ': ' + column_number,
                               900, 450)  # width, height - July 27/22 make wider.
            column_name = self.view.columns[int(column_number.replace('#', '')) - 1]
            column_dict = toolkit.get_dict_column(column_name, self.view.tree_dict)
            # Note: view_column stays open when SQL Music window is closed.
            view_column = sql.PrettyTreeHeading(column_dict)
            view_column.scrollbox = self.scrollbox
            # Document self.scrollbox
            sql.tkinter_display(view_column)
            return

        # At this point only other region is 'cell'
        self.view_iid = self.view.tree.identify_row(y)
        # Highlight the row in treeview
        toolkit.tv_tag_add(self.view.tree, self.view_iid, "menu_sel")
        # May 14, 2023 - New tv_tag_add() has error message if new tag already exists
        #tags = self.view.tree.item(self.view_iid)['tags']  # Append 'menu_sel' tag
        #if "menu_sel" not in tags:
        #    tags.append("menu_sel")
        #    self.view.tree.item(self.view_iid, tags=tags)

        # May 14, 2023 - If they clicked on it, it must be visible already.
        #self.view.tree.see(self.view_iid)  # Ensure message is visible

        values = self.view.tree.item(self.view_iid, "values")
        sql_row_id = self.view.column_value(values, "row_id")
        if sql_row_id is None:
            # Should never happen because sql_row_id is key field
            # always included even if not displayed.
            print('mserve.py common_button_3() sql_row_id is None')
            return

        ''' Create Pretty Displays from SQL tables 
            TODO: Move code after menu option is chosen.
        '''
        if self.view == self.his_view:
            pretty = sql.PrettyHistory(sql_row_id)
        else:
            pretty = sql.PrettyMusic(sql_row_id)

        ''' Place Window top-left of parent window with g.PANEL_HGT padding
            Lifted from: ~/mserve/encoding.py
        '''
        # Drop down menu to select headers, message body, daily backup
        self.right_click_menu(event, pretty)

    def right_click_menu(self, event, pretty):
        """ Right-clicked in common treeview. Popup menu """

        menu = tk.Menu(root, tearoff=0)
        menu.post(event.x_root, event.y_root)

        # If lambda isn't used the command is executed as soon as popup
        # menu is displayed, not when option is chosen.
        menu.add_command(label="View SQL Metadata", font=(None, g.MED_FONT),
                         command=lambda: self.view_sql_row(pretty))
        ''' view_library will trap Music ID = 0 and give message. '''
        menu.add_command(label="Open in library", font=(None, g.MED_FONT),
                         command=lambda: self.view_library(pretty))
        menu.add_separator()

        if self.view == self.mus_view:
            """ SQL Music Table must be opened for view_metadata() """
            menu.add_command(label="View Raw Metadata", font=(None, g.MED_FONT),
                             command=lambda: self.view_metadata(pretty))
            menu.add_separator()

        menu.add_command(label="Ignore click", font=(None, g.MED_FONT),
                         command=lambda: self.close_right_click_menu(menu))

        menu.tk_popup(event.x_root, event.y_root)
        # Without lambda executes immediately, without _: invalid # parameters
        menu.bind("<FocusOut>", lambda _: self.close_right_click_menu(menu))

    def close_right_click_menu(self, menu):
        """ Remove lib_top's popup menu """
        menu.unpost()
        # Remove tag 'red' - Reset color to normal
        toolkit.tv_tag_remove(self.view.tree, self.view_iid, "menu_sel")
        # May 14, 2023 - New tv_tag_remove() has error message if old tag doesn't exist
        #tags = self.view.tree.item(self.view_iid)['tags']  # Remove 'menu_sel' tag
        #if "menu_sel" in tags:
        #    tags.remove("menu_sel")
        #    self.view.tree.item(self.view_iid, tags=tags)

    def view_metadata(self, pretty, os_filename=None, top=None):
        """ View Metadata - Called from SQL Music Table popup menu
        Called from Music Location Tree popup menu and passes os_filename

        :param pretty: Dictionary for SQL Music Table. Used to get OsFileName
            and then recycled for metadata dictionary.
        :param os_filename: When called from Music Location Tree filename is passed.
        :param top: When called from Music Location Tree = self.lib_top.
        """
        if not os_filename:
            os_filename = PRUNED_DIR + pretty.dict['OS Filename']
        view_ctl = FileControl(self.lib_top, self.info)
        view_ctl.new(os_filename)  # Declaring new file populates metadata
        pretty = sql.PrettyMeta(view_ctl.metadata)
        view_ctl.close()

        # Requires override to def create_window
        self.create_window("Metadata (ID3 Tags) - mserve", 1400, 975, top=top)
        pretty.scrollbox = self.scrollbox
        sql.tkinter_display(pretty)

    def view_sql_row(self, pretty):
        """ View SQL - Music Table, History Table, or Location Table Row """
        self.create_window("Highlighted SQL Table Row - mserve", 1400, 975)
        pretty.scrollbox = self.scrollbox
        # If we did text search, highlight word(s) in yellow
        if self.mus_search is not None:
            # history doesn't have support. Music & history might both be open
            if self.mus_search.edit is not None:
                pretty.search = self.mus_search.edit.get()
        sql.tkinter_display(pretty)

    def view_library(self, pretty):
        """ View Library Treeview and open current song into view.
            TODO: When returning, collapse treeview parents forced to open. """
        music_id = pretty.dict['SQL Music Row Id']  # hist & music have same
        ''' SQL History Table configuration rows have music_id with "0" '''
        if music_id == "0":
            text = "Music Id 0 is not a real music song.\n" + \
                   "It cannot be opened in the Music Location."
            message.ShowInfo(self.view.toplevel, "Music Id 0 - mserve", text,
                             icon='warning', thread=self.get_refresh_thread)
            self.info.fact(text, 'warning', 'open')
            return

        d = sql.music_get_row(music_id)
        if d is None:
            text = "Music Id: '" + music_id + "' not found.\n" + \
                   "Reason unknown."
            message.ShowInfo(self.view.toplevel, "Music Id Not Found - mserve", text,
                             icon='error', thread=self.get_refresh_thread)
            self.info.fact(text, 'error', 'open')
            print("mserve.py view_library() music_id not found:", music_id)
            return

        self.lib_top.focus_force()  # Get focus
        self.lib_top.lift()  # Raise in stacking order

        # TODO: Faster performance and less code using:
        # self.real_paths.index(PRUNED_DIR + d['OsFileName'])

        groups = d['OsFileName'].split(os.sep)
        Artist = groups[0]
        Album = groups[1]
        Song = groups[2]
        song_found = False

        for artist_iid in self.lib_tree.get_children():
            artist = self.lib_tree.item(artist_iid)['text']
            if artist == Artist:
                self.lib_tree.item(artist_iid, 'open')
                for album_iid in self.lib_tree.get_children(artist_iid):
                    album = self.lib_tree.item(album_iid)['text']
                    if album == Album:
                        self.lib_tree.item(album_iid, 'open')
                        for song_iid in self.lib_tree.get_children(album_iid):
                            song = self.lib_tree.item(song_iid)['text']
                            if song == Song:
                                song_found = True
                                self.lib_tree.see(song_iid)  # Ensure song visible
                                break

        if not song_found:
            text = "Music Id: '" + music_id + "' not found.\n" + \
                   "No matching song Artist/Album/Title in Music Location."
            message.ShowInfo(self.view.toplevel, "No Match in Music Location - mserve", text,
                             icon='error', thread=self.get_refresh_thread)
            self.info.fact(text, 'error', 'open')
            print("mserve.py view_library() No match in Music Location:", music_id)

    def create_window(self, title, width, height, top=None):
        """ Create new window top-left of parent window with g.PANEL_HGT padding

            Before calling:
                Create pretty data dictionary using tree column data dictionary
            After calling / usage:
                create_window(title, width, height, top=None)
                pretty.scrollbox = self.scrollbox
                # If we did text search, highlight word(s) in yellow
                if self.mus_search is not None:
                    # history doesn't have support. Music & history might both be open
                    if self.mus_search.edit is not None:
                        pretty.search = self.mus_search.edit.get()
                sql.tkinter_display(pretty)

            When Music Location Tree calls from view_metadata it passes
            top=self.lib_top. In this case not called from SQL Music Table
            viewer.

            TODO: Instead of parent guessing width, height it would be nice
                  to pass a maximum and reduce size when text box has extra
                  white space.
        """
        if self.hdr_top is not None:
            self.hdr_top.lift()
            self.hdr_top.title(title)  # Maybe on different title
            return

        self.hdr_top = tk.Toplevel()  # New window for data dictionary display.
        self.hdr_top_is_active = True

        if top is None:  # When not None it is lib_top (Music Location)
            top = self.common_top  # Parent Window - mus_top, his_top
        xy = (top.winfo_x() + g.PANEL_HGT,
              top.winfo_y() + g.PANEL_HGT)
        self.hdr_top.minsize(width=g.BTN_WID * 10, height=g.PANEL_HGT * 4)
        # TODO: Geometry too large for a single treeview column dictionary
        #       Just about right for a gmail message pretty header
        self.hdr_top.geometry('%dx%d+%d+%d' % (width, height, xy[0], xy[1]))
        self.hdr_top.title(title)
        self.hdr_top.configure(background="Gray")
        self.hdr_top.columnconfigure(0, weight=1)
        self.hdr_top.rowconfigure(0, weight=1)

        ''' Set program icon in taskbar '''
        img.taskbar_icon(self.hdr_top, 64, 'white', 'lightskyblue', 'black')

        ''' Bind <Escape> to close window '''
        self.hdr_top.bind("<Escape>", self.pretty_close)
        self.hdr_top.protocol("WM_DELETE_WINDOW", self.pretty_close)

        ''' frame1 - Holds scrollable text entry '''
        frame1 = ttk.Frame(self.hdr_top, borderwidth=g.FRM_BRD_WID,
                           padding=(2, 2, 2, 2), relief=tk.RIDGE)
        frame1.grid(column=0, row=0, sticky=tk.NSEW)
        # 7 rows of text labels and string variables auto adjust with weight 1
        #        for i in range(7):
        #            frame1.grid_rowconfigure(i, weight=1)
        bs_font = (None, g.MON_FONTSIZE)  # bs = bserve, ms = mserve

        ''' Scrollable textbox to show selections / ripping status '''
        text = ("Retrieving SQL data.\n" +
                "If this screen can be read, there is a problem.\n\n" +
                "TIPS:\n\n" +
                "\tRun in Terminal: 'm' and check for errors.\n\n" +
                "\twww.pippim.com\n\n")

        # Text padding not working: https://stackoverflow.com/a/51823093/6929343
        self.scrollbox = toolkit.CustomScrolledText(
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

    def tree_summary(self, view, title="Summary"):
        """ Add up sizes and count number of rows.

            Display results in info message.
            view = self.his_view or self.mus_view """

        total_size = 0
        row_count = 0
        use_file_size = "os_file_size" in view.columns

        for iid in view.tree.get_children():
            # Loop through all rows
            row_count += 1
            values = view.tree.item(iid, "values")
            if use_file_size:
                size = view.column_value(values, "os_file_size")  # Music Table
            else:
                size = view.column_value(values, "size")  # History Table
            if size is None:
                print('mserve.py - tree_summary() size is None. iid:', iid)
                size = "0"
            int_size = int(size.replace(',', ''))
            total_size += int_size

        text = "Total size:  " + "{:,}".format(total_size) + "\n" + \
               "Row count:  " + "{:,}".format(row_count)
        message.ShowInfo(view.toplevel, title, text,
                         thread=self.get_refresh_thread)

    # noinspection PyUnusedLocal
    def pretty_close(self, *args):
        """ Close window painted by the create_window() function """
        if self.hdr_top is None:
            return
        #self.tt.close(self.hdr_top)  # Close tooltips (There aren't any yet)
        self.scrollbox.unbind("<Button-1>")
        self.hdr_top_is_active = False
        self.hdr_top.destroy()
        self.hdr_top = None

        ''' MusicLocationTree option view_metadata() doesn't use self.view '''
        # self.view_iid will also be None when clicked on heading not treeview row
        if self.view and self.view.tree and self.view_iid:
            # Reset color to normal in treeview line
            toolkit.tv_tag_remove(self.view.tree, self.view_iid, "menu_sel")

    def rip_cd(self):
        """ Rip CD using libdiscid, MusicBrainzNGS, CoverArtArchive.org,
            images copied from clipboard and mutagen. """
        if encoding.RIP_CD_IS_ACTIVE:
            self.rip_cd_class.cd_top.focus_force()  # Get focus
            self.rip_cd_class.cd_top.lift()  # Raise in stacking order
            title = "Rip CD Error"
            text = "Rip CD function is already running!"
            message.ShowInfo(self.rip_cd_class.cd_top, title, text,
                             icon='error', thread=self.get_refresh_thread)
            return

        try:
            with open(lc.ENCODE_DEV_FNAME, 'rb') as f:
                last_disc_contents = pickle.load(f)
        except Exception as err:
            print("Exception err:", err)  # If reboot [errno 2] file not found
            last_disc_contents = None
        last_disc = None  # For testing save 63 seconds reading discid
        if ENCODE_DEV and last_disc_contents:
            answer = message.AskQuestion(
                self.lib_top, thread=self.get_refresh_thread,
                title="Encode (Rip) CD Development Mode - mserve", confirm='no',
                text="Development Mode's last Disc ID: " + last_disc_contents.id +
                     "\n\nDo you want to reuse this DISC ID for Musicbrainz?")
            if answer.result != 'yes':
                last_disc_contents = None  # Reread disc ID.
            last_disc = last_disc_contents  # Reuse the last disc ID
        #if ENCODE_DEV and self.rip_cd_class and self.rip_cd_class.disc:
        #    if last_disc_contents:
        #        self.rip_cd_class.disc = last_disc_contents
        #    last_disc = self.rip_cd_class.disc  # Reuse the last disc ID

        self.rip_ctl = FileControl(self.lib_top, self.info,
                                   get_thread=self.get_refresh_thread)

        self.rip_cd_class = encoding.RipCD(
            self.lib_top, self.tt, self.info, self.rip_ctl, lcs,
            caller_disc=last_disc, thread=self.get_refresh_thread)
        return

    def write_playlist_to_disk(self, ShowInfo=True):
        """ Save Favorites using save_last_selections. Also saves current song ndx.
            if self.playlists.open_name used, then write to SQL Playlist Record instead.

        :param ShowInfo: Set to False when system is shutting down.
        """
        # Playlist options disabled in other functions
        self.file_menu.entryconfig("Save Favorites", state=tk.DISABLED)
        self.file_menu.entryconfig("Exit and CANCEL Pending", state=tk.DISABLED)

        self.set_title_suffix()  # Favorites or playlist in self.title_suffix now
        if len(self.saved_selections) <= 1 and ShowInfo:
            # Similar message in multiple places. Move to own function. Perhaps at top
            # making language changes easier.
            messagebox.showinfo(title="Cannot save " + self.title_suffix + ".",
                                message="You must select at least two songs.",
                                icon='error', parent=self.lib_top)
            return

        if self.playlists.open_name:
            self.playlists.save_playlist()  # act_id_list already up to date
        else:
            self.save_last_selections()  # Write location's favorites to disk

        self.pending_tot_add_cnt = 0        # Total changes made without being
        self.pending_tot_del_cnt = 0        # written to disk with "Save Favorites"
        self.enable_lib_menu()              # Reset dropdown menu choices for Playlists

        # TODO: broadcast message through Information Centre
        text = str(len(self.saved_selections)) + " songs in " + \
            self.title_suffix + " have been saved.\n\n" + \
            "Note the Playlist is automatically saved whenever you\n" + \
            "exit mserve, log out or the system shuts down normally.\n\n" + \
            "If you accidentally make drastic changes, use the option\n" + \
            "'Exit and CANCEL Pending' instead of 'Save Play and Exit'." + \
            "\n\nThen all changes since the last save are discarded."
        title = self.title_suffix + " saved."
        if ShowInfo:
            message.ShowInfo(self.lib_top, title, text, 'left',
                             thread=self.get_refresh_thread)
            self.info.cast(title + "\n\n" + text)

    def save_last_selections(self, new_playlist=False):

        """ Save to ~/.../mserve:
                last_location    = 'iid' in location master

            Save settings to disk to ~/.../mserve/L999/xxx_xxx
                last_open_states = Artist/Album expanded/collapsed states
                last_playlist    = songs selected for playing in user order
                last_song_ndx    = pointer into playlist to continue playing

        :param new_playlist: When True a new playlist is being opened so
            just saving current position for returning to favorites
        """

        global LODICT, START_DIR

        if self.playlists.open_name and not new_playlist:
            print("mserve.py save_last_selection() serious ERROR:" +
                  " playlists.open_name should be blank:", self.playlists.open_name)
            return

        ''' If self.saved_selections not populated, grab all checked songs 

        REMOVE OLD CODE: self.saved_selections are updated by pending_apply()

        if len(self.saved_selections) == 0:
            self.saved_selections = self.lib_tree.tag_has("song_sel")
            # BUG June 25, 2023. Above could be cause:
            # Favorites were resorted into alphabetical order after working
            # in L003 and then opened L004. Had also closed play_top before
            # exiting. Not sure which actually caused bug.
            print("mserve.py save_last_selection() WARNING: Saving " +
                  "Favorites in alphabetical order")
        '''

        ''' Save expanded/collapsed state of Artists & Albums '''
        self.lib_tree_open_states = self.make_open_states()
        with open(lc.FNAME_LAST_OPEN_STATES, "wb") as f:
            pickle.dump(self.lib_tree_open_states, f)  # Save open states

        ''' Save last opened location iid '''
        if not lcs.host_down:
            # TEMPORARY patch. When host_down below crashes because SQL closed
            # ProgrammingError: Cannot operate on a closed database.
            if lcs.open_code:  # Is there a location open?
                lcs.save_mserve_location(lcs.open_code)  # TODO: ditch parameter

        ''' Two songs needed to save, next startup uses previous save '''
        if len(self.saved_selections) < 2:
            print("mserve.py save_last_selection() WARNING: Need at least " +
                  "two songs to save playlist.")
            return

        ''' Save full path of selected songs in current play order '''
        save_songs = []
        for s_ndx in self.saved_selections:
            try:
                if s_ndx.startswith("I"):
                    print("mserve.py save_last_selections() 's_ndx' not song:",
                          s_ndx, self.lib_tree.item(s_ndx, 'text'))
                    continue
            except AttributeError:
                print("mserve.py save_last_selections() 's_ndx' not string:",
                      type(s_ndx), s_ndx)
                continue

            ndx = int(s_ndx)  # string to integer
            save_songs.append(self.real_paths[ndx])  # Get full path

        with open(lc.FNAME_LAST_PLAYLIST, "wb") as f:
            pickle.dump(save_songs, f)  # Save song list

        ''' Save last playing song  '''
        if self.ndx > (len(save_songs) - 1):
            self.ndx = 0
        with open(lc.FNAME_LAST_SONG_NDX, "wb") as f:
            pickle.dump(self.ndx, f)  # Save song index

    def make_open_states(self):
        """ Read lib_tree Artists & Albums to find those expanded (opened).
            Add qualified to open states list.

            Return list of tuples. Where each tuple contains:
                (Artist Name, Album Name or None, first_tag)
                    When Album Name is None, that means Artist is Open.
                    Can have Artist Open and an Album Open for two records.
                    Can have Artist Open and two Albums Open for three records.
                    first_tag is specifies "Artist" or "Album" type

                    Can have Album Open and Artist Closed for a single record.

            NOTE: being called twice on shut down.

        :return open_list: [(Artist Name, Album Name, tag_type), (), ... ()]
        """
        open_list = list()
        for Artist in self.lib_tree.get_children():  # Process artists
            self.append_if_open(Artist, None, open_list)
            for Album in self.lib_tree.get_children(Artist):  # Process albums
                self.append_if_open(Artist, Album, open_list)
        return open_list

    def append_if_open(self, artistId, albumId, open_states_list):
        """ NEW VERSION on Aug 17-23 
            open_states_states list is mutable. 
            Append when Artist/Album open
            tag is for sanity check, but no insanity test yet. """

        ''' Artist opened?, Artist Name, tag s/b "Artist" '''
        art_opened, art_text, art_tag = self.get_tree_state(artistId)

        ''' Artist is opened and No album passed. Append artist and return '''
        if art_opened == 1 or art_opened is True:
            test = (art_text, None, art_tag)
            if test not in open_states_list:
                open_states_list.append(tuple((art_text, None, art_tag)))
            if not albumId:
                return  # No album to check, leave now

        ''' Album opened?, Album Name, tag s/b "Album" '''
        alb_opened, alb_text, alb_tag = self.get_tree_state(albumId)
        if alb_opened == 1 or alb_opened is True:
            open_states_list.append(tuple((art_text, alb_text, alb_tag)))

    def get_tree_state(self, Id):
        """ Get expanded/collapsed state (opened/closed) of one Artist or Album:
            (opened 0/1, artist or album name, tag with u'Artist' or u'Album')
        :return tuple: (opened, text, "Artist" or "Album" tag)
        """
        try:
            item = self.lib_tree.item(Id)
        except tk.TclError:
            # Error occurs when quitting mserve
            # TclError: wrong # args: should be ".140484140082384.140484140082600.
            # 140484140084544.140484140084616 item item ?option ?value??..."
            #print("mserve.py get_tree_state() FAILED: self.lib_tree.item(Id)",
            #      Id)
            return 0, "Unknown", "Unknown"
        return item['open'], item['text'], item['tags'][0]  # First tag only

    def apply_all_open_states(self, open_states):
        """  Set expanded (opened) state of lib_tree Artists & Albums
        :param open_states: self.lib_tree_open_states[]
        """
        for Artist in self.lib_tree.get_children():  # Read all artists
            self.apply_open_state(Artist, None, open_states)
            for Album in self.lib_tree.get_children(Artist):  # Read all albums
                self.apply_open_state(Artist, Album, open_states)

    def apply_open_state(self, artistId, albumId, open_states_list):
        """ Set the expanded (Open) indicators (chevrons) for a single
            artist or album. """

        ''' Get Artist Name using generic get_tree_state() method '''
        art_opened, art_text, art_tag = self.get_tree_state(artistId)
        if albumId is None:  # Artist only check?
            test = (art_text, None, art_tag)
            if test in open_states_list:  # If not in list already, add Artist
                self.lib_tree.item(artistId, open=True)
            return

        ''' Check if Artist + Album should be opened '''
        alb_opened, alb_text, alb_tag = self.get_tree_state(albumId)
        test = (art_text, alb_text, alb_tag)
        if test in open_states_list:
            self.lib_tree.item(albumId, open=True)

    def load_last_selections(self):

        """ Load last favorites from ~/.../mserve/L999/last_playlist
            Load last open states from ~/.../mserve/L999/last_open_states
            Favorites sorted by last order shuffled. (self.saved_selections)
            Begin playing with song we left off at. (self.ndx)
            Mark selected (checkbox) songs in lib_tree.
        """
        ''' Call:
         m.main()
          mserve.main()
           MusicLocationTree(MusicLocTreeCommonSelf)  # Builds lib_top, lib_tree, etc. 
            load_last_selections()  # Load favorites for location
             play_selected_list()  # Builds play_top, chronology, etc.
              play_one_song()  # Setup song art, lyrics, etc.
               play_to_end()  # play song until end
                check ends  # even refresh_play_top() checks ending
                 '''

        # global LODICT  # Never change LODICT after startup!

        self.saved_selections = []  # Songs selected for playing
        self.filtered_selections = list(self.saved_selections)

        if NEW_LOCATION:
            ''' If parameter 1 is for random directory, we have no last location
                Variables have been set to null. Remove 'm' splash screen.
            '''
            if self.splash_toplevel:
                self.splash_toplevel.withdraw()  # Remove splash screen
                # Default background too bright: '#d9d9d9'
                #root.configure(background="#797979")  # Has no effect
            return

        ''' Check for Last selections file on disk '''
        if not os.path.isfile(lc.FNAME_LAST_PLAYLIST):
            return  # self.playlist_paths = pickle.load(f)
        if not os.path.isfile(lc.FNAME_LAST_OPEN_STATES):
            return  # self.lib_tree_open_states = pickle.load(f)
        if not os.path.isfile(lc.FNAME_LAST_SONG_NDX):
            return  # self.ndx = pickle.load(f)

        ext.t_init('load_last_selections() All Steps')
        ext.t_init('OPEN FILES')

        ''' Load last song playing index '''
        ext.t_init('FNAME_LAST_SONG_NDX')
        self.ndx = 0  # Index to saved_selections[] list of song ids in order
        with open(lc.FNAME_LAST_SONG_NDX, 'rb') as f:
            self.ndx = pickle.load(f)
            #print('current index:', self.ndx)
        ext.t_end('no_print')

        ''' Set selections numbers of playlist order in music library '''
        ext.t_init('FNAME_LAST_PLAYLIST')
        #self.playlist_paths = []  # Song paths with "song_sel" tag sorted by playlist order
        with open(lc.FNAME_LAST_PLAYLIST, 'rb') as f:
            self.playlist_paths = pickle.load(f)
            #print('len(self.playlist_paths):', len(self.playlist_paths))
            #print("self.playlist_paths[:10]:", self.playlist_paths[:10])  # DEBUG
            # [u'/media/rick/SANDISK128/Music/April\ Wine/Greatest Hits Live 2003/Just between you and me.mp3',
        ext.t_end('no_print')

        ''' Set library treeview opened states for Artists and Albums '''
        ext.t_init('FNAME_LAST_OPEN_STATES')
        #self.lib_tree_open_states = []  # List of expanded/collapsed flags
        with open(lc.FNAME_LAST_OPEN_STATES, 'rb') as f:
            self.lib_tree_open_states = pickle.load(f)
            #print('len(self.lib_tree_open_states):', len(self.lib_tree_open_states))
            #print('self.lib_tree_open_states[:10]:', self.lib_tree_open_states[:10])  # DEBUG
            # Next line added Aug 17/23 but should always have been here?
            self.apply_all_open_states(self.lib_tree_open_states)
            # self.lib_tree_open_states: [(0, u'10cc', u'Artist'),
            # (0, u'The Best of 10cc', u'Album'), (0, u'3 Doors Down',
        ext.t_end('no_print')

        ext.t_end('no_print')  # Jun 13, 2023 - OPEN FILES: 0.0121288300

        ext.t_init('Build self.saved_selections in playlist order')
        spam_count = 0
        for song in self.playlist_paths:
            try:
                ndx = self.real_paths.index(song)
            except ValueError:
                if spam_count < 10:
                    print('load_last_selections() Not found:', song)
                    # print(self.real_paths[spam_count])
                    spam_count += 1
                continue
            iid = str(ndx)
            self.saved_selections.append(iid)
        ext.t_end('no_print')  # Jun 13, 2023 - self.saved_selections 0.1488709450

        ext.t_init('set_all_checks_and_opened')
        self.set_all_checks_and_opened()
        ext.t_end('no_print')  # Jun 13, 2023 - checks_and_selects: 0.4508948326
        ext.t_init('Wrap up')

        # Keep host awake if necessary  - Aug 7/23 - how was this working?
        #if lcs.open_touchcmd:
        #    self.loc_keep_awake_is_active = True

        #if LODICT.get('activecmd', "") is not "":  # Commented Aug 7/23
        if lcs.open_touchcmd:  # Added Aug 7/23
            self.loc_keep_awake_is_active = True

            # May be restarting music player so keep awake immediately
            self.next_active_cmd_time = time.time()
            self.loc_keep_awake()

        # If self.ndx is greater than number in playlist, reset to 0
        if self.ndx > (len(self.saved_selections) - 1):
            # print('len(self.saved_selections):', len(self.saved_selections))
            print('last saved song index too large:', self.ndx, 'reset to zero')
            self.ndx = 0

        ''' Selected songs can be filtered by having time index or by Artist '''
        self.filtered_selections = list(self.saved_selections)  # Deep copy
        ext.t_end('no_print')  # Jun 13, 2023 - Wrap up: 0.0000181198
        ext.t_end('no_print')  # May 24, 2023 - load_last_selections(): 1.6982600689
        # Jun 13, 2023 - load_last_selections() All Steps: 0.6094801426

        if len(self.saved_selections) >= 2:
            # Continue playing where we left off
            self.play_from_start = False  # TODO: Review variable usage, kinda weird!
            # print('Continue playing with song#:', self.ndx)
            self.play_selected_list()
        elif self.splash_toplevel:
            self.splash_toplevel.withdraw()  # Remove splash screen

    def clear_all_checks_and_opened(self):
        """ Called from self.pending_reset() and self.playlists.apply_callback()
        """
        ext.t_init('Clear totals from Artists & Albums & clear checkboxes')
        self.lib_top.update_idletasks()
        self.lib_tree_open_states = []
        for Artist in self.lib_tree.get_children():  # Read all Artists
            self.clear_item_check_and_open(Artist, force_close=True)
            for Album in self.lib_tree.get_children(Artist):  # Read all Albums
                self.clear_item_check_and_open(Album, force_close=True)
                for Song in self.lib_tree.get_children(Album):  # Read all Albums
                    self.clear_item_check_and_open(Song)
                    ''' Force Play No. blank - erase 'Adding' and 'Deleting' '''
                    self.lib_tree.set(Song, "Selected", "")
        self.lib_top.update_idletasks()
        ext.t_end('no_print')  # 0.33 for 1500 selections
        # 0.1857478619  for 3 selections out of 3826 songs

    def clear_item_check_and_open(self, iid, force_close=False):
        """
        Clear checkbox and open state for single lib_tree item.
        :param iid: Treeview iid. Artists and Albums start with I.
        :param force_close: Processing an Artist or Album force open state to 0.
        :return:
        """
        item = self.lib_tree.item(iid)

        ''' Songs don't have an opened flag. Only Artists and Albums. '''
        if force_close:
            if item['open'] is True or item['open'] == 1:
                self.lib_tree.item(iid, open=False)

        ''' Update Tags '''
        update = False
        tags = item["tags"]
        if "song_sel" in tags:
            tags.remove("song_sel")
            update = True
        if "checked" in tags:
            tags.remove("checked")
            update = True
        if "tristate" in tags:
            tags.remove("tristate")
            update = True
        if "unchecked" not in tags:
            tags.append("unchecked")
            update = True

        if update:
            self.lib_tree.item(iid, tags=tags)

    def set_all_checks_and_opened(self):
        """ Called from self.pending_reset() and self.load_last_selections()
            June 15, 2023 - called from self.playlists.apply_callback().
            June 19, 2023 - opened=False for playlists which do not record
                open states for Artists ans Albums.
            June 24, 2023 - Playlists now supported, remove opened=True...

            BatchSelect() class for single update to parents' total selected.
            Before calling all items must be "unchecked" and "song_sel" blanked.
            self.saved_selections and self.lib_tree_open_states must be set.
        """

        ''' Set opened states for Artists and Albums, play number for Songs '''
        bs = BatchSelect(self.lib_tree)

        not_selected_count = 0
        selected_count = 0
        ext.t_init('Set open/closed, add BatchSelect totals')
        for Artist in self.lib_tree.get_children():  # Read all artists
            self.apply_open_state(Artist, None, self.lib_tree_open_states)
            for Album in self.lib_tree.get_children(Artist):  # Read all albums
                ''' Opening an Album will automatically open it's Artist '''
                self.apply_open_state(Album, None, self.lib_tree_open_states)

                for Song in self.lib_tree.get_children(Album):  # Read all songs
                    ''' Is song in playlist? '''
                    try:
                        ndx = self.saved_selections.index(Song)  # Song in playlist?
                    except ValueError:
                        not_selected_count += 1
                        if not_selected_count < 1:  # Change from 1 to debug
                            print('Skipping - Not in playlist:', full_path)
                        continue
                    ''' Set song checkbox tags in music library treeview '''
                    selected_count += 1
                    number_str = play_padded_number(
                        str(ndx+1), len(str(len(self.playlist_paths))))
                    adj_list = bs.add_select(Song, Album, Artist, number_str)
                    # Update treeview columns with selected size, count and seconds
                    self.tree_col_range_replace(Song, 8, adj_list)  # Column number passed
        ext.t_end('no_print')  # Jun 13, 2023 - open/closed and BatchSelect: 0.3233859539

        ext.t_init('Apply totals to Artists & Albums + set checkbox')
        for Artist in self.lib_tree.get_children():  # Read all Artists
            adj_list = bs.get_totals(Artist)
            # May 30, 2023 - was range_add()
            self.tree_col_range_replace(Artist, 8, adj_list, tagsel='artist_sel')
            for Album in self.lib_tree.get_children(Artist):  # Read all Albums
                adj_list = bs.get_totals(Album)
                # May 30, 2023 - was range_add()
                self.tree_col_range_replace(Album, 8, adj_list, tagsel='album_sel')
                ''' Toggle processing with BatchSelect() class '''
                for Song in self.lib_tree.get_children(Album):  # Read all Albums
                    tags = self.lib_tree.item(Song)["tags"]
                    if "song_sel" in tags:
                        # noinspection PyProtectedMember
                        self.lib_tree._check_ancestor(Song)  # in CheckboxTreeview()
                        break  # Only one Song has to be tested

        adj_list = bs.get_totals('lib_top_totals')
        self.tree_title_zero_selected()
        self.tree_title_range_add(8, adj_list)  # Pass start index
        self.display_lib_title()  # Title formatting with song counts & sizes
        ext.t_end('no_print')  # Jun 13, 2023 - Artists & Albums + set checkbox: 0.1274099350

    # ==============================================================================
    #
    #       Music Location Tree Processing - Play All Songs forever
    #
    # ==============================================================================

    def play_selected_list(self):
        """ Play songs in self.saved_selections[]. Define buttons:
                Close, Pause, Prev, Next, Commercial and Intermission """
        ''' Call:
         m.main()
          mserve.main()
           MusicLocationTree(MusicLocTreeCommonSelf)  # Builds lib_top, lib_tree, etc. 
            load_last_selections()  # Load favorites for location
             play_selected_list()  # Builds play_top, chronology, etc.
              play_one_song()  # Setup song art, lyrics, etc.
               play_to_end()  # play song until end
                check ends  # even refresh_play_top() checks ending
                 '''

        if self.long_running_process:
            title = "Long running process in progress"
            text = "Cannot start music after long running process started.\n\n"
            text += "Music started before long running process will continue\n"
            text += "playing."
            message.ShowInfo(self.lib_top, title, text, 'left',
                             thread=self.get_refresh_thread)
            self.info.cast(title + "\n\n" + text)
            return

        if self.play_top_is_active:  # Are we already playing songs?
            if self.play_on_top:
                # If we had the focus, give it up
                self.play_on_top = False
                self.lib_top.focus_force()  # Get focus
                self.lib_top.lift()  # Raise in stacking order
            else:
                # If we didn't have focus, take it
                self.play_on_top = True
                self.play_top.focus_force()  # Get focus
                self.play_top.lift()  # Raise in stacking order
            self.set_lib_tree_play_btn()  # Reset button to reflect play running
            return  # Don't start playing again

        ''' Reset text in lib_top "Show library" play button tool tip'''
        self.tt.set_text(self.lib_tree_play_btn, "Lift music library window up.")
        self.play_ctl.sink = ""     # Fix error if self.play_ctl.sink is not ""
        if self.play_ctl.path is not None:
            self.play_ctl.close()  # Update last song & reset class variables

        ''' Override to play songs checked in lib_top.tree? '''
        if self.play_from_start:
            ''' Get list of items tagged for playing in Artist/Album order '''
            new_selections = self.lib_tree.tag_has("song_sel")  # Alphabetical order
            if len(new_selections) != len(self.saved_selections):
                # Play new selections because old save out of date.
                self.saved_selections = list(new_selections)
            else:
                # Keeping current sorted selections.
                self.play_from_start = False  # Override the override - Review this

        self.lib_tree.update_idletasks()  # Wasn't done in load_last_selections() to save time
        ''' At least one song must be selected '''
        if len(self.saved_selections) <= 1:
            messagebox.showinfo(title="Invalid Playlist",
                                message="You must select at least two songs!",
                                parent=self.lib_top)
            return

        ''' Set lib_tree_play_btn text the open play_top window '''
        self.clear_buttons()  # Review for removal if unnecessary
        self.play_top = tk.Toplevel()
        self.play_top.minsize(g.WIN_MIN_WIDTH, g.WIN_MIN_HEIGHT)
        self.play_top_is_active = True

        # Set flags for child processes running
        self.ltp_top_is_active = False          # Sample middle 10 seconds / full
        self.sync_paused_music = False          # Important this is False now

        ''' Gather data to paint VU Meter
            TODO: June 6, 2023 - VU meters work with configured sound card source '''
        # /dev/hull prevents ALSA errors from clearing screen with errors:
        #   ALSA lib pcm.c: (snd_pcm_open_no update) Unknown PCM cards.pcm.rear
        #   ALSA lib pcm_route.c: Found no matching channel map
        # If this isn't done real error messages from mserve could be wiped out
        ext_name = "python vu_meter.py stereo 2>/dev/null"
        self.vu_meter_pid = \
            ext.launch_command(ext_name, toplevel=self.play_top)

        ''' Place Window top-left of parent window with g.PANEL_HGT padding '''
        self.play_top.minsize(width=g.BTN_WID * 10, height=g.PANEL_HGT * 10)
        geom = monitor.get_window_geom('playlist')  # June 1, 2021 sql history
        self.play_top.geometry(geom)
        self.set_title_suffix()  # Playlist name for title bar
        self.play_top_title = "Playing " + self.title_suffix + " - mserve"
        self.play_top.title(self.play_top_title)
        self.play_top.configure(background="Gray")
        self.play_top.columnconfigure(0, weight=1)  # Artwork stretches
        self.play_top.columnconfigure(3, weight=0)  # VU Meter Left no stretch
        self.play_top.columnconfigure(4, weight=0)  # VU Meter Right no stretch
        self.play_top.rowconfigure(0, weight=1)  # Artwork stretches (NEEDED)

        ''' Set program icon in taskbar '''
        img.taskbar_icon(self.play_top, 64, 'white', 'lightskyblue', 'black')

        ''' Create master frame '''
        self.play_frm = tk.Frame(self.play_top, borderwidth=g.FRM_BRD_WID,
                                 relief=tk.RIDGE)
        self.play_frm.grid(column=0, row=0, sticky=tk.NSEW)
        self.play_frm.grid_columnconfigure(2, minsize=50)
        self.play_frm.grid_rowconfigure(0, weight=1)  # Volume Slider
        ms_font = g.FONT

        ''' Artwork image spanning 20 rows (most are empty) '''
        self.art_width = 100  # Will be overriden by actual width
        self.art_height = 100  # ... and actual height
        self.play_no_art()  # Temporary starting image
        self.art_label = tk.Label(self.play_frm, borderwidth=0,
                                  image=self.play_current_song_art, font=ms_font)
        self.art_label.grid(row=0, rowspan=20, column=0, sticky=tk.W)
        self.art_label.bind("<Button-1>", self.pp_toggle)  # click artwork to pause/play
        # Leave empty row #5 for F3 frame (was row span=5)


        ''' Volume Slider Frame '''
        self.slider_frm = ttk.Frame(self.play_frm, borderwidth=0)
        self.slider_frm.grid(row=0, column=1, columnspan=2, sticky=tk.EW,
                             padx=5, pady=(8, 4))
        self.slider_frm.columnconfigure((0, 2), weight=0)  # speakers
        self.slider_frm.columnconfigure(1, weight=5)  # Volume Slider
        self.slider_frm.rowconfigure(0, weight=0)

        '''  self.ffplay_mute  LEFT: 🔉 U+F1509  RIGHT: 🔊 U+1F50A '''
        self.ffplay_mute = tk.Label(
            self.slider_frm, borderwidth=0, highlightthickness=0,
            text="    🔉", justify=tk.CENTER, font=g.FONT)  # justify not working
        self.ffplay_mute.grid(row=0, column=0, sticky=tk.W)
        self.ffplay_mute.bind("<Button-1>", lambda _: pav.fade(
            self.play_ctl.sink, float(pav.get_volume(self.play_ctl.sink)),
            25, .5, step_cb=self.init_ffplay_slider))
        # focus in/out aren't working :(
        self.ffplay_mute.bind("<FocusIn>", lambda _: print("focus in"))
        self.ffplay_mute.bind("<FocusOut>", lambda _: print("focus out"))

        text = "Speaker with one wave.\n"
        text += "Click to reduce the volume to 25%.\n"
        text += "Music keeps play with no sound.\n"
        text += "You can also click on album art to\n"
        text += "pause music and reduce the volume."
        self.tt.add_tip(self.ffplay_mute, tool_type='label',
                        text=text, anchor="sw")

        '''  self.ffplay_full  RIGHT: 🔊 U+1F50A '''
        self.ffplay_full = tk.Label(
            self.slider_frm, borderwidth=0, highlightthickness=0,
            text="    🔉", font=g.FONT)  # justify not working
        self.ffplay_full.grid(row=0, column=2)
        self.ffplay_full.bind("<Button-1>", lambda _: pav.fade(
            self.play_ctl.sink, float(pav.get_volume(self.play_ctl.sink)),
            100, .5, step_cb=self.init_ffplay_slider))

        text = "Speaker with three waves.\n"
        text += "Click to restore the volume to 100%."
        self.tt.add_tip(self.ffplay_full, tool_type='label',
                        text=text, anchor="se")

        ''' Volume Slider https://www.tutorialspoint.com/python/tk_scale.htm '''
        self.ffplay_slider = tk.Scale(  # highlight color doesn't seem to work?
            self.slider_frm, orient=tk.HORIZONTAL, tickinterval=0, showvalue=0,
            highlightcolor="Blue", activebackgroun="Gold", troughcolor="Black",
            command=self.set_ffplay_sink, borderwidth=0, cursor='boat red red')
        self.ffplay_slider.grid(row=0, column=1, padx=4, ipady=1, sticky=tk.EW)

        text = "Volume slider.\n"
        text += "Click and drag button to change volume.\n"
        text += "Click on space left of button to reduce volume.\n"
        text += "Click on space right of button to increase volume."
        self.tt.add_tip(self.ffplay_slider, tool_type='label',
                        text=text, anchor="sc")

        ''' Aug 9/23 
        https://soundcharts.com/blog/music-metadata
        https://images.prismic.io/soundcharts/868e0bf5c60017040f5ca7b84ca94ee1606204d5_
        macos-itunes-edit-metadata-how-to-2.jpg?auto=compress,format
        Fields displayed for metadata input screen:
        song, artist, album, album artist, composer (check box to show composer
        in views), grouping, genre, year, track 1 of 17, disk 1 of 1,
        compilation (Album is a compilation of songs by various artists)
        rating, bpm, play count (Reset play count button)

        https://support.apple.com/lv-lv/guide/music/musf438ffc97/mac
        https://help.apple.com/assets/63B876DC92F98156FB4566F1/
        63B876DD92F98156FB4566F8/en_US/c2fdb1929f0c3bde2eaa54ba01abc5bd.png

        Apple playing album has Song name in Black, Artist below in Red then
        Pop - 2022  5-stars  Dolby Logo
        To left is Big Album cover underneath Play and Shuffle buttons for album.

        Apple makes you buy a subscription to sync lyrics across devices.
        Note: Not all features are available in the Apple Music Voice Plan. 
        Apple Music, Apple Music Voice, lossless, and Dolby Atmos aren’t 
        available in all countries or regions. See the Apple Support article
        Availability of Apple Media Services.

        To right are scrolling lyrics with only four to give words per line
        wrapped. Double spaced lines, current line in black, others grey, bottom
        two lines fading to white. Above lyrics is slider for volume small
        speaker to large speaker.
        
        Button bar is up top with shuffle, REW, ||, FF, Loop icons. A box with
        album thumbnail, current song, artist, progress, slider for progress.
        '''

        ''' Controls to resize art to fit frame spanning metadata # rows '''
        self.play_frm.bind("<Configure>", self.on_resize)
        self.start_w = self.play_frm.winfo_reqheight()
        self.start_h = self.play_frm.winfo_reqwidth()

        ''' VU Meter canvas object spanning META_DISPLAY_ROWS '''
        self.vu_width = 30  # Always stays this value
        self.vu_height = 100  # Will be overriden
        self.vu_meter_first_time = True  # Patch for VU meter height repainting
        self.vu_meter_left, self.vu_meter_left_rect = self.create_vu_meter(18, 3)
        self.vu_meter_right, self.vu_meter_right_rect = self.create_vu_meter(18, 4)
        # Sep 7/23 below was 6 bump to 12 and loose short decays drop to 4
        self.VU_HIST_SIZE = 2  # Larger number = slower attack/decay
        # A better method is to paint line where peak used to be 1/3 second ago
        self.vu_meter_left_hist = [0.0] * self.VU_HIST_SIZE
        self.vu_meter_right_hist = [0.0] * self.VU_HIST_SIZE

        ''' self.lyrics_master_frm: Lyrics Frame - Title & Textbox with scrollbar
            Further divided into self.lyrics_frm and lyrics_score_box
            May 9, 2023 - Set row & column depending on frame size.
        '''
        PAD_X = 5

        self.play_frm.grid_columnconfigure(5, weight=1)  # 0's-COL 5
        self.lyrics_master_frm = tk.Frame(self.play_frm)
        self.lyrics_master_frm.grid(row=0, rowspan=20, column=5,
                                    padx=PAD_X, pady=PAD_X, sticky=tk.NSEW)
        self.lyrics_master_frm.grid_rowconfigure(1, weight=1)
        self.lyrics_master_frm.grid_columnconfigure(0, weight=1)

        # Define title frame top of lyrics_master_frm
        self.lyrics_frm = tk.Frame(self.lyrics_master_frm)
        self.lyrics_frm.grid(row=0, rowspan=1, column=0, sticky=tk.NSEW)
        self.lyrics_frm.grid_rowconfigure(0, weight=0)
        self.lyrics_frm.grid_columnconfigure(0, weight=1)

        # Rounded rectangle buttons mapped to same .grid using .remove
        # New Short form with 'config_all_labels()' doesn't need variables
        # Apply color codes to buttons - See set_artwork_colors()
        # There are four different combinations of rounded buttons with
        # tooltips:
        #   FROM     TO     WIDGET NAME                     Button Text
        #  Auto -> Manual   self.lyrics_panel_scroll_a_m    Auto Scrolling
        #  Time -> Manual   self.lyrics_panel_scroll_t_m    Time Scrolling
        #  Manual -> Auto   self.lyrics_panel_scroll_m_a    Manual Scroll
        #  Manual -> Time   self.lyrics_panel_scroll_m_t    Manual Scroll

        tt_text = "Auto Scrolling lyrics is active.\n" + \
                  "Click to scroll lyrics score manually."
        self.lyrics_panel_scroll_a_m =\
            self.create_scroll_button_and_tooltip(
                "Auto Scrolling", tt_text, ms_font=g.FONT)

        tt_text = "Lyrics line is highlighted using time index.\n" + \
                  "Click to scroll lyrics score manually."
        self.lyrics_panel_scroll_t_m =\
            self.create_scroll_button_and_tooltip(
                "Time Scrolling", tt_text, ms_font=g.FONT)

        tt_text = "Manual lyrics score scrolling is active.\n" + \
                  "Click to auto scroll lyrics at 1.5x speed."
        self.lyrics_panel_scroll_m_a =\
            self.create_scroll_button_and_tooltip(
                "Manual Scroll", tt_text, ms_font=g.FONT)

        tt_text = "Manual lyrics score scrolling is active.\n" + \
                  "Click to highlight lyrics using time index."
        self.lyrics_panel_scroll_m_t =\
            self.create_scroll_button_and_tooltip(
                "Manual Scroll", tt_text, ms_font=g.FONT)

        # Set four rounded rectangles to width of the longest rectangle to
        # prevent the longest rectangle right side showing under shorter ones
        self.set_max_dimensions()  # TODO rename to explicit

        # U+2630 in unicode and then U+22EE
        self.lyrics_panel_text = "0%, Blah blah, Line: 99 of: 99"

        # Extra padding around label so RoundedRectangle has enough space
        self.lyrics_panel_label = tk.Label(
            self.lyrics_frm, borderwidth=g.FRM_BRD_WID, padx=7, pady=7,
            text=self.lyrics_panel_text, font=g.FONT)
        self.lyrics_panel_label.place(relx=.6, rely=.5, anchor="center")

        self.lyrics_panel_last_line = 1  # Appears in title string

        self.tt.add_tip(self.lyrics_panel_label, tool_type='label',
                        text="Replace me!", anchor="se")

        """ Define Hamburger rounded rectangle button and it's tooltip """
        rounded_text = u"☰"
        tt_text = "Left-clicking hamburger icon displays a \n" + \
                  "context sensitive menu for web scraping,\n" + \
                  "editing lyrics score and time indexes."
        self.lyrics_panel_hamburger = img.RoundedRectangle(
            self.lyrics_frm, rounded_text, 'black', 'white', ms_font=g.FONT,
            stretch=False, command=self.play_lyrics_fake_right_click)
        self.lyrics_panel_hamburger.grid(row=0, column=1, sticky=tk.E)
        self.tt.add_tip(self.lyrics_panel_hamburger, text=tt_text,
                        tool_type='canvas_button', anchor="se")

        ''' dummy label to give padding above and below row '''
        # Extra padding around label so RoundedRectangle has enough
        # space. dummy is required because panel_label uses place to center
        # and doesn't permit padding with .place() command
        tk.Label(self.lyrics_frm, pady=14).grid(row=0, column=2, sticky='E')

        # Lyrics current state variables
        self.lyrics_scrape_pid = 0  # Process ID for web scrape
        self.lyrics_edit_is_active = False  # song lyrics being edited?
        self.lyrics_train_is_active = False  # basic training time index

        # undo=True provides support for Ctrl+Z and Ctrl+Shift+Z (Redo)
        self.lyrics_score_box = scrolledtext.ScrolledText(
            self.lyrics_master_frm, width=30, height=10, padx=3, pady=3, wrap=tk.WORD,
            insertbackground='white', font=g.FONT, undo=True)
        self.lyrics_score_box.grid(row=1, column=0, sticky=tk.NSEW)
        self.lyrics_score_box.bind("<1>", self.play_lyrics_left_click)
        self.lyrics_score_box.bind("<3>", self.play_lyrics_right_click)
        self.lyrics_score_box.tag_config('highlight', background='black',
                                         foreground='white')

        """ build_play_btn_frm() replaces Hockey Commercial button with Rewind 
            button and replaces Intermission button with Fast Forward button.
            grid row is 20 allowing 19 rows for Artwork, Metadata, Lyrics """
        self.build_play_btn_frm()  # Placement varies if Hockey enabled

        ''' Frame for Playlist (Chronology can be hidden) '''
        self.chron_frm = tk.Frame(self.play_top, borderwidth=g.FRM_BRD_WID,
                                  relief=tk.GROOVE)
        #self.chron_frm.configure(background="Black")  # No effect
        self.chron_frm.grid(row=30, column=0, sticky=tk.NSEW)  # Aug 9/23 was 8
        self.play_frm.grid_rowconfigure(30, weight=1)  # Aug 9/23 was 8
        self.chron_frm.grid_rowconfigure(0, weight=1)
        self.chron_frm.grid_columnconfigure(0, weight=1)  # Note weight to stretch
        self.build_chronology()  # Treeview in play order

        ''' Start at first playlist entry? '''
        if self.play_from_start:  # Caller can set starting index
            self.ndx = 0  # Control for current song 0 = 1st

        ''' When getting focus, see if overrides prevent buttons. '''
        self.play_top.bind("<FocusIn>", self.handle_play_top_focus)

        ''' Retrieve location's last playing/paused status, song progress seconds '''
        resume = self.get_resume()
        chron_state = self.get_chron_state()

        ''' Start songs in a loop until signal to close '''
        while self.play_top_is_active:  # Loop whilst play window is open
            if not self.play_one_song(resume=resume, chron_state=chron_state):
                self.play_close()  # Close button or shutting down
                break
            self.play_ctl.close()  # Update last song's last access if > 50% played
            resume = False  # Can only resume once
            chron_state = None  # Extra safety
            self.play_from_start = True  # Review variable usage... it's weird.

    def set_ffplay_sink(self, value=None):
        """ Copied from from tvVolume.set_sink()
            TODO: Check cross-fading songs there should be two "ffplay" running.
            Called when slider changes value. Set sink volume to slider setting.
            Credit: https://stackoverflow.com/a/19534919/6929343 """
        if value is None:
            print("Volume.set_ffplay_sink() 'value' argument is None")
            return

        if self.set_ffplay_sink_WIP:  # Already a WIP?
            return  # Slider can send dozens of values before message responds
        self.set_ffplay_sink_WIP = True  # function running, block future spam

        curr_vol, curr_sink = self.get_volume("ffplay")
        #print("self.curr_ffplay_volume:", self.curr_ffplay_volume,
        #      "curr_vol:", curr_vol)
        if self.pp_state == "Paused":
            #self.ffplay_slider.set(curr_vol)  # no longer needed 2 hours later
            title = "Music is paused"
            text = "Cannot change volume when music is paused. Begin\n"
            text += "playing music and then you can change the volume."
            message.ShowInfo(self.play_top, title, text,
                             thread=self.get_refresh_thread)
            self.init_ffplay_slider(curr_vol)
            self.set_ffplay_sink_WIP = False
            return

        pav.set_volume(curr_sink, value)
        self.curr_ffplay_volume = value  # Record for saving later
        self.set_ffplay_sink_WIP = False

    def init_ffplay_slider(self, value):
        """ Called above and from pav.poll_fades callback. """
        value = int(value)  # Might be float from pav.poll_fades() callback?
        self.set_ffplay_sink_WIP = True  # Not sure why we have to do this?
        self.curr_ffplay_volume = value
        self.ffplay_slider.set(self.curr_ffplay_volume)
        self.play_top.update_idletasks()
        self.set_ffplay_sink_WIP = False  # Not sure why we have to do this?

    @staticmethod
    def get_volume(name=None):
        """ from tvVolume - Get volume of 'ffplay' before resetting volume """
        all_sinks = pav.get_all_sinks()  # Recreates pav.sinks_now
        for Sink in all_sinks:
            if Sink.name == name:
                return int(Sink.volume), Sink.sink_no_str

        return None, None

    def display_metadata(self):
        """ Metadata varies from song to song.
            Using priority system, display up to 15 rows and set weight to 1 """

        control_list = [
            (SONG_LABEL_STR, self.play_ctl.Title, self.song_title_var, 1),
            ("year", self.play_ctl.FirstDate, self.song_first_date_var, 1),
            ("comment", self.play_ctl.Comment, self.song_comment_var, 1),
            ("artist", self.play_ctl.Artist, self.song_artist_var, 1),
            ("album", self.play_ctl.Album, self.song_album_var, 1),
            ("album artist", self.play_ctl.AlbumArtist, self.song_album_artist_var, 1),
            ("album date", self.play_ctl.AlbumDate, self.song_album_date_var, 1),
            ("composer", self.play_ctl.Composer, self.song_composer_var, 1),
            ("genre", self.play_ctl.Genre, self.song_genre_var, 1),
            ("play count", self.play_ctl.PlayCount, self.song_play_count, 2),
            ("last played", self.play_ctl.LastPlayTime, self.song_last_play_time, 2),
            ("disc number", self.play_ctl.DiscNumber, self.song_disc_var, 3),
            ("track number", self.play_ctl.TrackNumber, self.song_track_var, 3),
            ("compilation", self.play_ctl.Compilation, self.song_compilation, 4),
            ("creation time", self.play_ctl.CreationTime, self.song_creation_time, 4),
            ("gapless playback", self.play_ctl.GaplessPlayback, self.song_gapless_playback, 5),
            ("last access", self.play_ctl.OsAccessTime, self.song_access_time, 6),
            ("file size", self.play_ctl.OsFileSize, self.song_file_size, 6),
            ("playlist №", 999999, self.song_number_var, 7),
            ("progress", 999999, self.song_progress_var, 7)
            ]

        ''' Erase previous song's labels '''
        my_children = self.play_frm.winfo_children()  # Get play_frm children
        for wdg in my_children:  # Iterate over children
            wr = wdg.grid_info()['row']
            wc = wdg.grid_info()['column']
            if wr == 0:
                continue  # Skip artwork, volume slider, vu meters, lyrics
            if wc != 1 and wc != 2:
                continue  # Extra insurance
            #print("Widget:", type(wdg), "Row:", wr, "Column:", wc)
            if isinstance(wdg, tk.Label):
                #print("wdg.destroy():", wdg['text'])
                wdg.destroy()

        row = 1  # Start at row number 1 (which is really row 2)

        for priority in range(1, 8):  # Loop through 7 priorities
            for control in control_list:
                ctl_title, ctl_field, ctl_var, ctl_priority = control
                if ctl_priority != priority:
                    continue  # Wrong priority

                if ctl_field is 999999:  # Play № of 99 or Progress MM:SS.D of MM:SS
                    self.display_meta_row(row, ctl_title, ctl_var)
                    ctl_var.set("")  # A function will populate when playing
                    row += 1
                elif row < META_DISPLAY_ROWS - 2:  # leave two rows for priority 7
                    if not ctl_field:
                        continue  # Field value is None, "", 0 or 0.0
                    if str(ctl_field) == "0" or str(ctl_field) == "1/1":
                        continue  # If No compilation or disk 1/1, hide it
                    self.display_meta_row(row, ctl_title, ctl_var)
                    self.display_meta_var(ctl_field, ctl_var)
                    row += 1

        for i in range(1, row):  # row is +1 already, stop at last used.
            self.play_frm.grid_rowconfigure(i, weight=1)  # Populated row

        for i in range(row, 19):  # Stop at 18 because bottom lyrics on 19
            self.play_frm.grid_rowconfigure(i, weight=0)  # Empty row

        ''' play_frm rows 0-18 artwork, metadata, vu meters, lyrics (on right)
            row 19 (lyrics on bottom)
            row 20 button bar
            row 30 chronology  '''

    def display_meta_var(self, fld, var):
        """ Set tk.StringVar() with fld string contents unless special values.
            fld previously tested and it is not None, "", 0 or 0.0. """
        if fld is self.play_ctl.PlayCount:
            var.set('{:n}'.format(fld))
        elif fld is self.play_ctl.LastPlayTime:
            var.set(tmf.ago(self.play_ctl.LastPlayTime))
        elif fld is self.play_ctl.GaplessPlayback or \
                fld is self.play_ctl.Compilation:
            val = 'Yes' if fld == "1" else 'No'
            var.set(val)
        elif fld is self.play_ctl.OsAccessTime:
            var.set(tmf.ago(self.play_ctl.OsAccessTime))
        elif fld is self.play_ctl.OsFileSize:
            var.set(toolkit.human_mb(self.play_ctl.OsFileSize))
        else:
            # global E_WIDTH
            E_WIDTH = 32
            var.set(make_ellipsis(fld, E_WIDTH))

    def display_meta_row(self, row, text, var):
        """ Display single row """
        tk.Label(self.play_frm, text=text, font=g.FONT) \
            .grid(row=row, column=1, sticky=tk.W, padx=5)
        if text == SONG_LABEL_STR:
            tk.Label(self.play_frm, textvariable=var,
                     font=g.FONT+('bold',)).grid(row=row, column=2, sticky=tk.W)
        else:
            tk.Label(self.play_frm, textvariable=var,
                     font=g.FONT).grid(row=row, column=2, sticky=tk.W)

    def make_one_song_var(self, text, row):
        """ Make text tkinter label and StringVar() field pair """
        var = tk.StringVar()
        tk.Label(self.play_frm, text=text, font=g.FONT) \
            .grid(row=row, column=1, sticky=tk.W, padx=5)
        tk.Label(self.play_frm, text="", textvariable=var,
                 font=g.FONT).grid(row=row, column=2, sticky=tk.W)
        return var

    def create_vu_meter(self, r, col):
        """ Create VU Meter.  self.vu_height irrelevant. """
        vu_meter = tk.Canvas(self.play_frm, width=self.vu_width,
                             relief=tk.FLAT,  # Override tk.RIDGE
                             height=self.vu_height, bg='black')
        vu_meter.grid(row=0, rowspan=r, column=col, padx=8)
        vu_meter_rectangle = vu_meter.create_rectangle(
            0, self.vu_height, 0, self.vu_height)
        return vu_meter, vu_meter_rectangle

    def handle_play_top_focus(self, _event):
        """
            When lib_tree_play() or Playlists() windows are active,
            always stays above Music Location (lib_top).

            Credit: https://stackoverflow.com/a/44615104/6929343

        :param _event: Ignored
        :return: None
        """
        if not self.play_top_is_active:
            return  # Play window closed?

        ''' Synchronizing lyrics to time index controls music '''
        if self.fine_tune and self.fine_tune.top_is_active:
            self.fine_tune_lift()

        ''' Sampling random song in lib_tree '''
        if self.ltp_top_is_active:
            self.lib_tree_play_lift()  # Raise in stacking order

    def fine_tune_lift(self):
        """ lift fine-tune time index window to top of stacking order.
            TODO: Harmonize with lib_top handle focus lifting
        """
        if self.fine_tune and self.fine_tune.top_is_active:
            self.fine_tune.top.focus_force()  # Retest July 5, 2023
            self.fine_tune.top.lift()  # Retest July 5, 2023

    def set_lib_tree_play_btn(self):
        """ set text for lib_tree_btn to start playing, show playing or show library. """
        if not self.lib_top_is_active:
            return  # Closing down

        if self.play_top_is_active:  # Are we already playing songs?
            if self.play_on_top:
                #self.lib_tree_play_btn["text"] = "🎵  Show library"
                #self.tt.set_text(self.lib_tree_play_btn, "Lift music library window up.")
                pass
            else:
                self.lib_tree_play_btn["text"] = "🎵  Show playing"
                self.tt.set_text(self.lib_tree_play_btn, "Lift songs playing window up.")
        else:
            self.restore_lib_buttons()
        self.lib_tree.update_idletasks()

    def toggle_hockey(self):
        """ Swap buttons between Hockey Commercial & Hockey Intermission and
            Rewind & Fast Forward
            If Hockey countdown is already running, disallow
        """
        if self.play_hockey_active:
            quote = ("\n" +
                     "Cannot toggle FF/Rewind buttons when hockey countdown running.\n\n" +
                     "Click the time remaining button and cancel countdown.\n")
            # Even though message appears on lib_top we know play_top has the thread
            message.ShowInfo(self.lib_top, text=quote, align='center',
                             thread=self.get_refresh_thread,
                             title="Cannot toggle FF/Rewind Buttons Now - mserve")
            self.info.fact(quote)
            return

        self.play_hockey_allowed = not self.play_hockey_allowed  # Flip switch
        if self.play_hockey_allowed:
            self.tools_menu.entryconfigure(0, label="Enable FF/Rewind buttons")
            self.info.fact("Enable FF/Rewind buttons")
        else:
            self.tools_menu.entryconfigure(0, label="Enable TV Commercial buttons")
            self.info.fact("Enable TV Commercial buttons")

        if not self.play_top_is_active:
            return  # Only lib_top is open. No play window to rebuild buttons

        self.tt.close(self.play_btn_frm)  # Remove old tooltip buttons in play_btn frame
        self.play_btn_frm.grid_forget()
        self.play_btn_frm.destroy()
        self.play_btn_frm = None  # Extra insurance
        self.build_play_btn_frm()

        ''' Apply current artwork colors to newly built button bar '''
        self.play_btn_frm.configure(bg=self.theme_bg)
        toolkit.config_all_buttons(self.play_top, fg=self.theme_bg,
                                   bg=self.theme_fg)

        ''' Lift play_top to see new button frame '''
        self.play_top.lift()
        self.play_on_top = True

    def start_long_running_process(self):
        """ Remove buttons from play_top that freeze process
            TODO: synchronize locations displays "Hide" instead of "Show"
                  and tooltip is invalid with search widget errors.
        """
        self.long_running_process = True
        self.play_btn_frm.grid_forget()
        self.build_play_btn_frm()

    def end_long_running_process(self):
        """ Restore "normal" buttons to play_top """
        self.long_running_process = False
        self.play_btn_frm.grid_forget()
        self.build_play_btn_frm()

    def build_play_btn_frm(self):
        """ Create frame for play_top buttons.
            Dynamically create buttons depending on 'play_hockey_allowed'
            Less buttons for long running process. """
        ''' Frame for Buttons '''
        self.play_btn_frm = tk.Frame(self.play_top, bg="LightGrey",
                                     borderwidth=g.FRM_BRD_WID, relief=tk.GROOVE)
        self.play_btn_frm.grid(row=20, column=0, sticky=tk.NSEW)  # Aug 9/23 was 3
        # Leave empty row #2 for F3 frame (was row=2)
        self.play_btn_frm.grid_rowconfigure(0, weight=1)
        self.play_btn_frm.grid_columnconfigure(0, weight=0)

        if self.play_hockey_allowed:
            button_list = ["Close", "Shuffle", "Prev", "Com", "PP", "Int", "Next", "Chron"]
        else:
            button_list = ["Close", "Shuffle", "Prev", "Rew", "PP", "FF", "Next", "Chron"]

        if self.long_running_process:
            ''' 'Next' button stops music from playing. '''
            button_list = ["Close", "PP", "Chron"]

        for col, name in enumerate(button_list):
            if name == "Close":
                """" Close Button ✘ """
                self.close_button = tk.Button(self.play_btn_frm, text="✘ Close",
                                              width=g.BTN_WID2 - 6,
                                              command=self.play_close)
                self.close_button.grid(row=0, column=col, padx=2, sticky=tk.W)
                self.play_top.bind("<Escape>", self.play_close)  # DO ONLY ONCE?
                self.play_top.protocol("WM_DELETE_WINDOW", self.play_close)
                self.tt.add_tip(self.close_button, "Close playlist but mserve stays open.",
                                anchor="sw")
            elif name == "Shuffle":
                ''' Shuffle Button Em space + u 1f500 = 🔀 '''
                # BIG_SPACE = " "         # UTF-8 (2003) aka Em Space
                self.shuffle_button = tk.Button(self.play_btn_frm, text=" 🔀 Shuffle",
                                                width=g.BTN_WID2 - 3, command=self.play_shuffle)
                self.shuffle_button.grid(row=0, column=col, padx=2, sticky=tk.W)
                self.tt.add_tip(self.shuffle_button, "Shuffle songs into random order.",
                                anchor="sw")
            elif name == "PP":  # TODO: Check current pp_state and dynamically format
                ''' Pause/Play Button '''
                self.pp_button = tk.Button(self.play_btn_frm, text=self.pp_pause_text,
                                           width=g.BTN_WID2 - 5, command=self.pp_toggle)
                self.pp_button.grid(row=0, column=col, padx=2)
                text = "Pause music, pause artwork and\nallow manual lyrics scrolling."
                self.tt.add_tip(self.pp_button, text, anchor="sw")
            elif name == "Prev":
                ''' Prev Track Button '''
                # U+1f844 🡄         U+1f846 🡆         U_1f808 🠈         I+1f80a 🠊
                # June 17, 2023: Change 🠈 to last track button emoji (u+23ee) ⏮
                self.prev_button_text = self.previous_text
                self.prev_button = \
                    tk.Button(self.play_btn_frm, text=self.prev_button_text, width=g.BTN_WID2 - 2,
                              command=lambda s=self: s.song_set_ndx('prev'))
                self.prev_button.grid(row=0, column=col, padx=2, sticky=tk.W)
                self.tt.add_tip(self.prev_button, "Play previous song.",
                                anchor="sw")
            elif name == "Next":
                ''' Next Track Button '''
                # BIG_SPACE = " "         # UTF-8 (2003) aka Em Space
                # June 17, 2023: Change 🠊 to next track button 23ED ⏭
                self.next_button = \
                    tk.Button(self.play_btn_frm, text="Next  ⏭", width=g.BTN_WID2 - 7,
                              command=lambda s=self: s.song_set_ndx('next'))
                self.next_button.grid(row=0, column=col, padx=2, sticky=tk.W)
                self.tt.add_tip(self.next_button, "Play next song in playlist.",
                                anchor="sw")
            elif name == "Com":
                ''' Hockey Commercial Button '''
                if self.tt.check(self.com_button):
                    self.tt.close(self.com_button)  # Remove old tooltip from list
                # 📺 | television (U+1F4FA)
                #self.play_hockey_active = False  # U+1f3d2 🏒
                self.com_button = tk.Button(self.play_btn_frm, text="📺  Commercial",
                                            anchor=tk.CENTER,
                                            width=g.BTN_WID2 + 3, command=lambda
                                            s=self: s.start_hockey(TV_BREAK1))
                self.com_button.grid(row=0, column=col, padx=2, sticky=tk.W)
                self.tt.add_tip(self.com_button, "Play music for " +
                                sec_min_str(TV_BREAK1) + ".\n" +
                                "Turn down TV volume whilst playing.", anchor="sw")
            elif name == "Int":
                ''' Hockey Intermission Button '''
                self.int_button = tk.Button(self.play_btn_frm, text="🏒  Intermission",
                                            anchor=tk.CENTER,
                                            width=g.BTN_WID2 + 3, command=lambda
                                            s=self: s.start_hockey(TV_BREAK2))
                self.int_button.grid(row=0, column=col, padx=2, sticky=tk.W)
                self.tt.add_tip(self.int_button, "Play music for " +
                                sec_min_str(TV_BREAK2) + ".\n" +
                                "Turn down TV volume whilst playing.", anchor="se")
            elif name == "Rew":
                ''' Rewind Button -10 sec '''
                self.rew_button = tk.Button(self.play_btn_frm, text="⏪  -" + REW_FF_SECS + " sec",
                                            width=g.BTN_WID2 - 3, command=lambda
                                            s=self: s.song_rewind())
                self.rew_button.grid(row=0, column=col, padx=2, sticky=tk.W)
                self.tt.add_tip(self.rew_button, "Rewind song " + REW_FF_SECS +
                                " seconds back.", anchor="sw")
            elif name == "FF":
                ''' Fast Forward Button +10 sec'''
                self.ff_button = tk.Button(self.play_btn_frm, text="+" + REW_FF_SECS + " sec  ⏩",
                                           width=g.BTN_WID2 - 3, command=lambda
                                           s=self: s.song_ff())
                self.ff_button.grid(row=0, column=col, padx=2, sticky=tk.W)
                self.tt.add_tip(self.ff_button, "Fast Forward song " + REW_FF_SECS +
                                " seconds ahead.", anchor="se")
            elif name == "Chron":
                ''' Show/Hide Chronology (Playlist) toggle button (Frame 4) '''
                if self.chron_is_hidden is None:
                    self.chron_is_hidden = False  # Initialization starts shown

                ''' Code copied from self.set_chron_button_text(). Make DRY '''
                text, text2 = self.get_chron_button_text()
                self.chron_button = tk.Button(
                    self.play_btn_frm, text=text,
                    width=g.BTN_WID2 + 2, command=lambda s=self: s.chron_toggle())
                self.chron_button.grid(row=0, column=col, padx=2, sticky=tk.W)
                text = "placeholder"
                self.tt.add_tip(self.chron_button, text2, anchor="se")
            else:
                print("mserve.py build_play_btn_frm() Bad button name:", name)

        if self.pp_state is "Paused":  # Initially defined as if playing
            self.set_pp_button_text()  # Button text reflects match play/pause state

        if self.chron_is_hidden:
            ''' Toggle tooltip window position above/below buttons '''
            self.toggle_chron_tt_positions()

    def on_resize(self, event):
        """ Resize image and VU Meters when frame size changes """
        # images use ratio of original width/height to new width/height
        h_scale = float(event.height) / self.start_h
        w_scale = h_scale  # It's a square!
        self.art_width = int(w_scale) - 6  # Border width, this is awkward
        self.art_height = int(h_scale) - 6  # play_spin_art
        # Fix error:  ValueError: bad image size
        self.art_width = 1 if self.art_width < 1 else self.art_width
        self.art_height = 1 if self.art_height < 1 else self.art_height
        self.play_resized_art = self.play_original_art.resize(
            (self.art_width, self.art_height), Image.ANTIALIAS)
        self.play_current_song_art = ImageTk.PhotoImage(self.play_resized_art)

        self.set_vu_meter_height()  # VU Meter height dependant on art height

        # Sometimes 'pp_state' variable isn't defined yet, e.g. during init
        if hasattr(self, 'pp_state'):
            if self.pp_state is "Paused":
                # Recreate image to new size (doesn't resize in above line).
                self.show_paused_art()

    def set_vu_meter_height(self):
        """ Set height of VU meter after play_top resized. """
        self.vu_meter_left.config(height=100)  # So meta display fields get fresh start
        self.vu_meter_right.config(height=100)
        self.play_frm.update_idletasks()  # Artwork resize

        ''' Current height of metadata labels in column 1 '''
        _x, _y, _width, height = self.play_frm.grid_bbox(1, 0, 1, 18)
        self.vu_height = height - 12  # Padding for top & bottom vu meters
        self.vu_height = 1 if self.vu_height < 1 else self.vu_height
        self.vu_meter_left.config(height=self.vu_height)
        self.vu_meter_right.config(height=self.vu_height)
        self.play_vu_meter_blank()  # Fill with self.theme_bg

    def move_lyrics_right(self):
        """ Chronology (playlist) tree visible. Move lyrics score right. """
        self.play_frm.grid_rowconfigure(19, weight=0)  # Lyrics Row will be gone now
        self.play_frm.grid_columnconfigure(5, weight=1)  # Lyrics in column 5
        self.lyrics_master_frm.grid(row=0, rowspan=20, column=5, sticky=tk.NSEW)
        # Define title frame
        self.lyrics_frm.grid(row=0, rowspan=1, column=0, sticky=tk.NSEW)
        # song info column narrow as possible for wide lyrics lines
        self.play_frm.grid_columnconfigure(2, minsize=50, weight=0)
        self.play_frm.update_idletasks()
        self.lyrics_on_right_side = True  # self.play_frm =

    def move_lyrics_bottom(self):
        """ The chronology (playlist) tree is hidden. Move lyrics score down. """
        # May 9, 2023 - Reset for row 6, column 2 (1's based)
        self.play_frm.grid_columnconfigure(5, weight=0)  # Column 5 gone
        self.lyrics_master_frm.grid(row=19, rowspan=1, column=1, columnspan=4, sticky=tk.NSEW)
        self.play_frm.grid_rowconfigure(19, weight=5)  # Lyrics get more space
        # Define title frame
        self.lyrics_frm.grid(row=0, rowspan=1, column=0, sticky=tk.NSEW)
        # song info column wide as possible for wide lyrics lines
        self.play_frm.grid_columnconfigure(2, minsize=400, weight=1)
        self.play_frm.update_idletasks()
        self.lyrics_on_right_side = False

    def create_scroll_button_and_tooltip(self, rounded_text, tt_text, ms_font):
        """ Define a rounded rectangle button and it's tooltip """
        rectangle = img.RoundedRectangle(
            self.lyrics_frm, rounded_text, 'black', 'white', ms_font=ms_font,
            command=self.play_lyrics_toggle_scroll)

        # Colors reassigned for each song in set_artwork_colors()
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
        """ Set width and height of rounded rectangles to minimums """
        self.lyrics_panel_scroll_a_m.config(width=1, height=1)
        self.lyrics_panel_scroll_t_m.config(width=1, height=1)
        self.lyrics_panel_scroll_m_a.config(width=1, height=1)
        self.lyrics_panel_scroll_m_t.config(width=1, height=1)

    def play_no_art(self):
        """ Default image for No Artwork """
        self.play_original_art = img.make_image(NO_ART_STR,
                                                image_w=1200, image_h=1200)
        self.play_resized_art = self.play_original_art.resize(
            (self.art_width, self.art_height), Image.ANTIALIAS)
        self.play_current_song_art = ImageTk.PhotoImage(self.play_resized_art)

    def show_paused_art(self):
        """ Default image for Music Paused """
        paused_art = img.make_image(PAUSED_STR, image_w=1200,
                                    image_h=1200)
        paused_resized_art = paused_art.resize(
            (self.art_width, self.art_height), Image.ANTIALIAS)
        self.play_current_song_art = ImageTk.PhotoImage(paused_resized_art)
        self.art_label.configure(image=self.play_current_song_art)

    # noinspection PyUnusedLocal
    def pp_toggle(self, fade_then_stop=False, *args):
        """ Pause/Play button pressed. Signal ffplay and set button text
            When called from button click play/pause fade_the_stop,
            chron_apply_filter(), chron_reverse_filter and play_close()
            When called from self.song_set_ndx, fade_then_kill = True
        """
        if not self.play_top_is_active:
            return  # Play window closed?

        ''' Synchronizing lyrics to time index controls music '''
        if self.fine_tune and self.fine_tune.top_is_active:
            self.fine_tune_lift()
            return

        if self.pp_state is "Playing":
            self.pp_state = "Paused"  # Was Playing now is Paused
            self.set_pp_button_text()
            self.pp_toggle_fading_out = True  # Signal pause music fade out
            self.pp_toggle_fading_in = False  # cancel any play fade in signal
            pav.fade(self.play_ctl.sink, self.get_max_volume(), 25, .5,
                     step_cb=self.init_ffplay_slider,
                     finish_cb=self.pp_finish_fade_out)
            self.secs_before_pause = self.play_ctl.elapsed()
            if self.play_hockey_active:  # Is TV hockey broadcast on air?
                set_tv_sound_levels(25, 100)  # Restore TV sound to 100%
        else:
            ''' Important: self.song_set_ndx() repeats two lines below.
                           Check there when changing below. '''
            self.pp_state = "Playing"  # Was Paused now is Playing
            self.set_pp_button_text()
            if self.play_hockey_active:
                set_tv_sound_levels(100, 25)  # Soften volume on tv to 25%
            self.current_song_t_start = time.time()
            elapsed = self.play_ctl.elapsed()  # Must call after .cont()

            ''' Can be reversing fade out from Pause click. '''
            self.pp_toggle_fading_in = True  # Playing music fade in signal
            self.pp_toggle_fading_out = False  # Cancel pause fade out signal
            pav.fade(self.play_ctl.sink, 25, self.get_max_volume(), .5,
                     step_cb=self.init_ffplay_slider,
                     finish_cb=self.pp_finish_fade_in)

            if self.play_ctl.state == 'start':
                ''' Was playing, then clicked pause and fast clicked play 
                    The stop job was reversed faded and never finished. '''
                self.play_ctl.log('stop')  # Hack through the backdoor
            self.play_ctl.cont()

    def pp_finish_fade_out(self):
        """ Pause music fade out volume callback """
        if not self.pp_toggle_fading_out:
            print("pp_finish_fade_out(): pp_toggle_fading_out is FALSE")
            return  # Got cancelled and callback wasn't reversed

        self.pp_toggle_fading_out = False
        self.play_ctl.stop()

    def pp_finish_fade_in(self):
        """ Play music fade in volume callback """
        if not self.pp_toggle_fading_in:
            print("pp_finish_fade_in(): pp_toggle_fading_in is FALSE")
            return  # Got cancelled and callback wasn't reversed

        self.pp_toggle_fading_in = False

    def get_max_volume(self):
        """ Maximum volume is 100% except during Hockey TV Commercials """
        if self.play_hockey_active:
            max_vol = TV_VOLUME  # During hockey ads less than 100%
            # Uncomment line below to really hear the difference
            # max_vol = 30  # A real obvious low volume for testing
        else:
            max_vol = 100
        return max_vol

    def set_pp_button_text(self):
        """ Set Pause/Play button text to reflect current state. """
        if self.pp_state is "Playing":
            self.pp_button['text'] = self.pp_pause_text
            text = "Pause music and artwork.\n" +\
                   "Lyrics can be manually scrolled."
            self.tt.set_text(self.pp_button, text)

            ''' VU Meter is stopping at wrong time. Code moved from above '''
            ext.continue_pid_running(self.vu_meter_pid)  # VU Meter PID
        else:
            self.show_paused_art()              # Mount "Paused" artwork
            self.pp_button['text'] = self.pp_play_text
            text = "Play music and spin artwork.\n" +\
                   "Lyrics are automatically scrolled."
            self.tt.set_text(self.pp_button, text)

            ''' VU Meter is stopping at wrong time. Code moved from above '''
            ext.stop_pid_running(self.vu_meter_pid)  # Pause VU Meters
            for _ in range(self.VU_HIST_SIZE):  # Remove VU_meter rectangles
                self.play_vu_meter(stop='yes')  # Gradually declines as
                self.play_top.after(10)  # history list has more 0 levels
            self.play_vu_meter_blank()  # Fill with self.theme_bg

    def get_pp_state_callback(self):
        """ Hand off to methods so they can get current pp_state
            of "Playing" or "Paused". Could be 'None' if play_top closed.
        """
        return self.pp_state

    def song_rewind(self):
        """ Rewind song 10 seconds back. If near start then previous song """
        if self.current_song_secs < float(REW_CUTOFF):
            self.song_set_ndx('prev')  # Less than 12 seconds played, so previous
        else:
            new_time = self.current_song_secs - float(REW_FF_SECS)
            self.song_ff_rew_common(new_time)  # Restart 10 seconds earlier

    def song_ff(self):
        """ Fast Forward song 10 seconds ahead. If near end then next song """
        if self.play_ctl.DurationSecs:
            if self.current_song_secs + float(REW_FF_SECS) + 5.0 > \
                    float(self.play_ctl.DurationSecs):
                self.song_set_ndx('next')  # 15 seconds left so next song.
            else:
                start_secs = self.current_song_secs + float(REW_FF_SECS)
                self.song_ff_rew_common(start_secs)  # Restart 10 seconds later
        else:
            ''' A new song is starting already? '''
            pass  # self.play_ctl.DurationSecs was None on July 12, 2023

    def song_ff_rew_common(self, start_secs):
        """ Shared function for for song_ff() and song_rew() functions """
        self.play_ctl.restart(start_secs)
        if self.play_ctl.sink is not None:
            pav.set_volume(self.play_ctl.sink, 100.0)
        self.play_update_progress(start_secs)  # Update screen with song progress
        self.play_paint_lyrics(rewind=True)  # Highlight line currently being sung. BUG: Only

        if self.pp_state == "Paused":
            ''' Was paused. Stop newly created ffplay to reflect pause. Then begin play '''
            pav.set_volume(self.play_ctl.sink, 25)  # Mimic volume of paused song
            self.play_ctl.stop()
            self.pp_toggle()  # toggle pause to begin playing

    def corrupted_music_file(self, path):
        """ Not a valid music file or device off-line """
        quote = ("\n" + path + "\n\n"
                 "This music file is invalid. It cannot be played.\n\n" +
                 "Possibly the device location is off-line.\n\n" +
                 "Highlight and use <Control>+C to copy name.")

        # Cannot call self.get_refresh_thread because it calls refresh_play_top
        # which has a corrupted music file that cannot be played.
        message.ShowInfo(self.lib_top, text=quote, align='center', icon='error',
                         thread=self.refresh_lib_top,
                         title="Invalid music file - mserve")
        self.info.fact(quote, 'error', 'open')

    def validate_pa_sink(self, sink, path):
        """ Validate Pulse Audio Sink. Must not be blank.

            NOTE: July 3, 2023 discovery song start calculation was
                  past end of file. This test is probably no longer
                  needed.
        """
        # A blank sink indicates sink not found
        if sink != "":
            return True  # TODO: Add more checks for valid sink is working

        ''' Did not get sink for song. It could be Pulse Audio crashed. '''
        quote = ("\n" + path + "\n\n"
                 "Attempted to play above music file. Failed\n" +
                 "to getPulse Audio sink number:" + str(sink) +
                 "\n\nPlease check Pulse Audio settings with pavucontrol.")

        message.ShowInfo(self.lib_top, text=quote, align='center', icon='error',
                         thread=self.get_refresh_thread,
                         title="Failed to get Pulse Audio Sink - mserve")
        self.info.fact(quote, 'error', 'open')

        return False

    def song_set_ndx(self, seq):
        """ Set index to previous song, next song or restart song at start.

            When 'Next' / 'Prev' buttons are quickly clicked the rate of
            about 20 clicks per second is too quick for song startup of
            1/2 second. A work around is to keep track of the last song
            started.

            Functions use this test is used to discover fast clicking:
                '''   F A S T   C L I C K I N G   '''
                if not self.last_started == self.ndx:
                    return

        Processing flow:
            1) Call wrap up song which kills currently playing song.
            2) set self.song_set_ndx_just_run = True
            3) Increment, Decrement, Restart, or set specific self.ndx.
            4) Every 33ms play_to_end() function checks if song has ended.
            5) After play_to_end() the next call is queue_next_song()
            6) queue_next_song() skips increment when song_set_ndx_just_run

        """
        if not self.play_top_is_active:
            return  # Play window closed?

        ''' Synchronizing lyrics to time index controls music '''
        if self.fine_tune and self.fine_tune.top_is_active:
            self.fine_tune_lift()
            return

        self.wrapup_song(fade_then_kill=True)  # Close currently playing

        if self.chron_filter is not None:
            # Instead of prev/next song index, skip detached treeview items
            self.filter_song_set_ndx(seq)
        elif seq == 'prev':
            if self.current_song_secs > float(REW_CUTOFF):
                ''' TODO: Ensure LastPlayTime and PlayCount updated '''
                self.song_set_ndx('restart')  # Was > 12 seconds so restart
                # Recursive call above comes back here
                return
            if self.ndx == 0:  # If on first go to last
                self.ndx = len(self.saved_selections) - 1
            else:
                self.ndx -= 1  # Previous song
        elif seq == 'next':
            if self.ndx == len(self.saved_selections) - 1:
                self.ndx = 0  # On last so go to first
            else:
                self.ndx += 1  # Next song
        elif seq == 'restart':
            # Restarting same song. Fake the last song to pass new tests
            if self.ndx == 0:
                self.last_started = 1  # On first so pretend next
            else:
                self.last_started = self.ndx - 1  # Pretend previous
        else:
            self.ndx = int(seq)  # Jump to index passed

        ''' Tell queue_next_song() not to increment self.ndx '''
        self.song_set_ndx_just_run = True  # self.ndx set, don't use 'Next'

        ''' If music currently paused, set state as if playing '''
        if self.pp_state is "Paused":
            # Mimic what pp_toggle() does when un-pausing music
            if self.play_hockey_active:
                # Soften volume on tv to 25%
                set_tv_sound_levels(100, 25)
            self.pp_state = "Playing"  # Was Paused now is Playing
            self.set_pp_button_text()

    def filter_song_set_ndx(self, seq):
        """ Set index to previous or next song in filtered chronology tree

            TODO: chron_tree will support filtering playlist with:
                    1) Songs with time index (synchronized lyrics)
                    1) Songs with no time index (unsynchronized)
                    3) Songs for specific artist
                    4) Songs over 5 minutes long
                When filtered other songs are detached from treeview.
                When clicking next/previous and hitting detached song,
                    preform recursive call with same operation.

        """
        while True:
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
            elif seq == 'restart':
                # Option in chron_tree to restart playing the current song
                if self.ndx == 0:
                    self.last_started = 1  # On first so pretend next
                else:
                    self.last_started = self.ndx - 1  # Pretend previous
                return
            else:
                # TODO: Review why self.last_started not forced?
                self.ndx = int(seq)  # Jump to index passed
                return

            ''' prev or next passed so find attached treeview item. '''
            try:  # If song index is in the detached list we don't want it
                if self.chron_detached.index(str(self.ndx + 1)):
                    continue  # Playlist Number is detached in chron_tree
            except ValueError:  # ValueError: '5' is not in list
                break  # Playlist Number is attached (visible) in chron_tree

    def wrapup_song(self, fade_then_kill=False):
        """ Called from pending_apply(), song_set_ndx(),
            chron_apply_filter(), chron_reverse_filter and play_close()
            When called from self.song_set_ndx, fade_then_kill = True
        """
        if self.play_ctl.sink is not "":
            if self.play_ctl.state == "start":
                if fade_then_kill:
                    ''' Sep 6/23 - Simple method would be: 
                            curr_vol = pav.get_volume(self.play_ctl.sink)
                            pav.fade(self.play_ctl.sink, curr_vol, 0.0, 1,
                                     ext.kill_pid_running, self.play_ctl.pid)
                        New song starts at same time so hold fields used.
                    '''
                    ''' a little debugging. each song start vol 25, 20, 8, 2, 1, 0... 
                        July 12, 2023 - Next song on '''
                    hold_sink = (self.play_ctl.sink + '.')[:-1]  # break link
                    #print("\n fade_then_kill - hold_sink:",
                    #      hold_sink, id(hold_sink), id(self.play_ctl.sink))
                    hold_pid = self.play_ctl.pid + 1 - 1  # break link
                    #print("hold_pid:", hold_pid, id(hold_pid), id(self.play_ctl.pid))
                    curr_vol = pav.get_volume(hold_sink)
                    if curr_vol is not None:
                        hold_vol = curr_vol  # Break reference to sinks_now
                        #print("hold_vol:", hold_vol)
                        self.play_ctl.pid = 0  # Stop play_ctl from killing
                        if hold_pid != 0:
                            # Background process fades music, keep executing
                            pav.fade(hold_sink, hold_vol, 0.0, 1,
                                     ext.kill_pid_running, hold_pid)
                    else:
                        self.info.cast("wrapup_song(): Got None for volume on sink#: " +
                                       str(hold_sink))
                else:
                    self.play_ctl.stop()  # Note poll_fades is in outer loop.

            ''' July 9, 2023 - Doesn't matter anymore if volume down. '''
            #pav.set_volume(self.play_ctl.sink, 100)

        '''   K I L L   L Y R I C S   S C A P E   '''
        if self.lyrics_scrape_pid:
            ''' When resuming paused, Webscrape in progress stays up '''
            if ext.check_pid_running(self.lyrics_scrape_pid):
                ext.kill_pid_running(self.lyrics_scrape_pid)
            self.lyrics_scrape_pid = 0

        # Kill song (if running) and update last access time
        self.play_ctl.close()  # calls .end() which update last access

        if len(self.saved_selections) == 0:
            # Cannot get treeview iid if self.saved_selections[] is empty list
            return  # Empty list.  May 24, 2023 - should not be making this
                    #  test at late stage. Better 'self.play_ctl.pid == 0:'

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
        """ Commercial Button or Intermission Button was pressed.
            If pressed once, Gone Fishing called and countdown begins.
            When pressed second time, Option to end countdown is presented
        """

        ''' Synchronizing lyrics to time index controls music '''
        if self.fine_tune and self.fine_tune.top_is_active:
            self.fine_tune_lift()
            return

        ''' Want to end countdown? - second time button click '''
        if self.play_hockey_active:  # Already counting down?
            answer = message.AskQuestion(
                self.play_top, thread=self.get_refresh_thread,
                title="TV break in progress - mserve", confirm='no',
                text="There are " + sec_min_str(self.play_hockey_remaining) +
                     "\nremaining in commercial/intermission.\n\n" +
                     "Do you want to pause music and restore TV sound?")
            if answer.result != 'yes':
                return  # Keep hockey countdown going

            self.play_hockey_t_start = 0.0  # Elapsed time calc variable
            return  # End hockey countdown

        ''' Initialization to start countdown - first time button click '''
        self.play_hockey_active = True
        self.play_hockey_t_start = time.time()
        self.play_hockey_secs = secs  # Commercial = 90 seconds
        self.play_hockey_remaining = self.play_hockey_secs

        ''' Music is usually paused so start playing '''
        if self.pp_state is "Paused":
            self.pp_toggle()  # Play music Sets TV sound volume to 25% automatically
        else:  # Was already playing when commercial button pressed? Weird situation
            # Soften volume tv ads to 25%
            set_tv_sound_levels(100, 25)

        ''' GoneFishing gobbles up big screen with shark '''
        ext.t_init('Gone Fishing')
        self.gone_fishing = img.GoneFishing(self.play_top)
        # TODO: After hockey ends, remove "Always on Top" attribute from play_top
        ext.t_end('no_print')  # Time was: 1.3247601986

        self.gone_fishing.plot_move(COMPIZ_FISHING_STEPS)
        ''' May 18, 2023 - Compiz doing weird things so create COMPIZ_FISHING_STEPS
            Screens will clear all windows for a few seconds when 100 steps are used.
            Complete system lockup on May 18, 2023. Change steps to 200.

            System locks up. journal ctl -xe -b-2:
            May 18 18:51:25 alien kernel: compiz[4681]: segfault at 68 ip 00007fa0c6cb796e sp 00007f ff e6

            NOTE: Caused by 'gsettings' disabling and enabling 'place' window feature.
            Disable this functionality in image.py for now. '''

    def hockey_countdown(self, elapsed):
        """
            Update time remaining for commercials or intermission
        """
        if not self.play_top_is_active:
            return  # Play window closed?
        if not self.play_hockey_active:
            return  # Play hockey not active?

        if self.gone_fishing is not None:
            self.gone_fishing.shark_move()  # Move shark closer to falling man

        if elapsed < self.play_hockey_secs:
            remaining = int(self.play_hockey_secs - elapsed)
            if remaining == self.play_hockey_remaining:
                return  # Update 1/10th second, not every 1/33rd second
            self.play_hockey_remaining = remaining
            int_str = com_str = "🏒  Remaining: " + str(remaining)
        else:
            # All finished now repaint original hockey buttons
            com_str = "📺  Commercial"  # TODO: Make global constants
            int_str = "🏒  Intermission"  # E.G.  COM_BTN_STR
            if self.gone_fishing is not None:
                self.gone_fishing.close()
            self.gone_fishing = None  # So global close doesn't try

        self.com_button['text'] = com_str
        self.int_button['text'] = int_str

    # ==============================================================================
    #
    #       Play one song - Called on start up, then repeatedly for each new song.
    #
    # ==============================================================================

    def play_one_song(self, resume=False, chron_state=None, from_refresh=False):
        """ Play song from start. Called on startup, on playlist change and
            by next/prev/restart buttons.

        ------------------------------------------------------------------------
        BUG: When play_one_song fires and another treeview function is looping
             through get_children that loop gets destroyed along with it's tree. 
        ------------------------------------------------------------------------


        :param resume: When True, use self.resume_state and self.resume_song_secs
            from SQL history record Type: 'resume' Action: 'L00x' or 'P00000x'
        :param chron_state: Pass to "Show" (default) or "Hide" to force change.
            Used at startup 'chron_state' history, or Playlist load.
        :param from_refresh: Called from refresh_play_top() that ran out of
            music when song ended.
        """

        ''' Call:
         m.main()
          mserve.main()
           MusicLocationTree(MusicLocTreeCommonSelf)  # Builds lib_top, lib_tree, etc. 
            load_last_selections()  # Load favorites for location
             play_selected_list()  # Builds play_top, chronology, etc.
              play_one_song()  # Setup song art, lyrics, etc.
               play_to_end()  # play song until end
                check ends  # even refresh_play_top() checks ending
                 '''

        if not self.play_top_is_active:
            return False  # play_top window closed.

        ''' Get our song_list index number from user treeview selections '''
        if self.ndx > len(self.saved_selections) - 1:
            self.info.fact("Restarting with first song on playlist.")
            self.ndx = 0  # Restarted smaller list

        '''   F A S T   C L I C K I N G   '''
        self.last_started = self.ndx  # Catch fast clicking Next/Prev Buttons

        ''' Highlight current song in Library Treeview '''
        iid = self.saved_selections[self.ndx]  # Library Treeview iid for song
        album = self.lib_tree.parent(iid)
        artist = self.lib_tree.parent(album)

        ''' Highlight song in playlist, but no metadata to format line yet. '''
        self.play_chron_highlight(self.ndx, True)  # True = use short line

        '''   F A S T   C L I C K I N G   '''
        if self.last_started != self.ndx:  # Fast clicking Next button?
            pav.poll_fades()
            return True

        ''' Build full song path from song_list[] '''
        self.current_song_path = self.playlist_paths[self.ndx]

        opened = self.lib_tree.item(artist, 'open')
        if opened is not True:
            # Don't want to open artist, it opens all albums. The album
            # will be opened below and open artist at same time.
            self.play_opened_artist = True  # We opened artist
        else:
            self.play_opened_artist = False  # artist was already open

        '''   F A S T   C L I C K I N G   '''
        self.play_top.update_idletasks()
        pav.poll_fades()
        if self.last_started != self.ndx:
            # Fast clicking Next button?
            return True

        opened = self.lib_tree.item(album, 'open')
        if opened is not True:
            self.lib_tree.item(album, open=True)
            self.play_opened_album = True
        else:
            self.play_opened_album = False  # Album was already open

        '''   F A S T   C L I C K I N G   '''
        if self.play_top:  # Test added Aug 2/23 after 'NoneType' error
            self.play_top.update_idletasks()
        else:
            return True  # Parent should check play_top_is_active
        pav.poll_fades()
        if self.last_started != self.ndx:  # Fast clicking Next button?
            return True

        toolkit.tv_tag_add(self.lib_tree, iid, "play_sel")
        self.lib_tree.see(iid)  # Ensure song visible

        '''   F A S T   C L I C K I N G   '''
        #root.update()  # Do both lib_top & play_top updates
        # Above also gives time slice back to mus_search and compare locations
        # and they freeze up def missing_art
        self.lib_top.update_idletasks()
        self.play_top.update_idletasks()
        pav.poll_fades()
        if self.last_started != self.ndx:  # Fast clicking Next button?
            return True

        '''   F A S T   C L I C K I N G   '''
        self.play_top.update_idletasks()
        pav.poll_fades()
        if self.last_started != self.ndx:  # Fast clicking Next button?
            return True

        ''' Verify it's a real song - May want to do this after .see() '''
        if self.current_song_path is None or self.current_song_path is "":
            return True  # Treat like fast clicking Next button

        '''   D E C L A R E   N E W   S O N G   P A T H   '''
        self.play_ctl.new(self.current_song_path)
        if self.play_ctl.path is None:
            self.play_ctl.close()  # this caused failure but full reset needed.
            return True  # Treat like fast clicking Next button

        if self.play_ctl.invalid_audio:
            #print(self.play_ctl.metadata)
            self.play_ctl.close()
            self.corrupted_music_file(self.current_song_path)  # No blocking dialog box
            return False  # Was causing all kinds of failures when returning False

        if self.play_ctl.path is None:
            self.play_ctl.close()
            return True  # Treat like fast clicking Next button

        ''' Populate display with metadata retrieved using ffprobe '''
        ext.t_init("play_one_song - update_sql_metadata()")
        self.update_sql_metadata(self.play_ctl)  # Update SQL Music Table with metadata
        ext.t_end('no_print')

        self.play_top.update_idletasks()  # display_metadata taking .5 secs
        pav.poll_fades()

        ext.t_init("play_one_song - self.display_metadata()")
        self.display_metadata()
        ext.t_end('no_print')  # 1st: 0.0018 2nd: 0.0339 3rd: 0.0230 4th: 0.0229

        self.play_top.update_idletasks()  # display_metadata taking .5 secs
        pav.poll_fades()

        ''' Set current song # of: total song count '''
        self.song_number_var.set(str(self.ndx + 1) + " of: " +
                                 str(len(self.saved_selections)))

        self.saved_DurationSecs = self.play_ctl.DurationSecs
        self.saved_DurationMin = tmf.mm_ss(self.saved_DurationSecs)

        '''   F A S T   C L I C K I N G   '''
        self.play_top.update_idletasks()
        pav.poll_fades()
        if self.last_started != self.ndx:  # Fast clicking Next button?
            self.play_ctl.close()
            return True

        ''' Get artwork from metadata with ffmpeg '''
        ext.t_init("set_artwork_colors()")
        self.set_artwork_colors()
        pav.poll_fades()
        if not self.play_top_is_active:
            return False
        ext.t_end('no_print')

        '''   F A S T   C L I C K I N G   '''
        self.play_top.update_idletasks()
        pav.poll_fades()
        if self.last_started != self.ndx:  # Fast clicking Next button?
            # NOTE: Parent Artist/Album opened above is closed after return.
            self.play_ctl.close()
            return True

        ''' Gather song lyrics to fill text box '''
        self.play_init_lyrics()

        '''   F A S T   C L I C K I N G   '''
        self.play_top.update_idletasks()
        pav.poll_fades()
        if self.last_started != self.ndx:  # Fast clicking Next button?
            # NOTE: Parent Artist/Album opened above is closed after return.
            self.play_ctl.close()
            return True

        ''' Update playlist chronology (Frame 4) with short line = False '''
        self.play_chron_highlight(self.ndx, False)  # False = use metadata
        if not self.play_top_is_active:
            return False

        '''   F A S T   C L I C K I N G   '''
        self.play_top.update_idletasks()
        pav.poll_fades()
        if self.last_started != self.ndx:  # Fast clicking Next button?
            self.play_ctl.close()
            return True

        self.current_song_secs = 0  # How much time played
        self.secs_before_pause = 0  # How much played before pause

        ''' Hide chronology (playlist) to match last setting for location '''
        if chron_state and chron_state == "Hide":
            ''' resume process wants to hide chronology. '''
            self.chron_is_hidden = False  # Fake "Show" now then toggle to hide
            self.chron_toggle()  # Toggle chronology between Show and Hide

        ''' Start song with ffplay & Update tree view's last played time
            If resume is passed we are starting up or changing location '''
        self.pp_state = "Playing"
        self.set_pp_button_text()

        ''' Launch ffplay to play song using extra_opt for start position '''
        dead_mode = False  # Start song playing (not paused)
        start_secs = 0.0  # Start at song beginning
        if resume:  # Are we resuming?
            if self.resume_state == "Paused":  # Was music paused last time?
                dead_mode = True  # Start song in stopped mode
            start_secs = self.resume_song_secs

        '''   F A S T   C L I C K I N G   '''
        self.play_top.update_idletasks()
        pav.poll_fades()
        if self.last_started != self.ndx:  # Fast clicking Next button?
            self.play_ctl.close()
            return True

        ''' Start ffplay, get Linux PID and Pulseaudio Input Sink # '''
        self.play_ctl.start(start_secs, 0, 1, 0, TMP_CURR_SONG, dead_mode)
        # Limit 0. Fade in over 1 second, Fade out 0.
        self.current_song_t_start = time.time()  # For pp_toggle, whether resume or not

        if resume:
            ''' Restart Music from last session's save point. '''
            if self.resume_state == "Paused":  # Was resume saved as paused?
                pav.set_volume(self.play_ctl.sink, 25)
                self.init_ffplay_slider(25)
                self.pp_state = "Paused"  # Set Play/Pause status to paused
                self.set_pp_button_text()
            elif self.play_ctl.sink is not None:
                pav.set_volume(self.play_ctl.sink, 100.0)
                self.init_ffplay_slider(100.0)

            self.play_update_progress(self.resume_song_secs)  # mm:ss of mm:ss
            self.play_paint_lyrics()  # paint window fields, set highlight
            self.play_lyrics_rebuild_title()  # Required for line # in title

            self.resume_state = None  # Make sure code doesn't run again
            self.resume_song_secs = None

        elif self.play_ctl.sink is not None:
            pav.set_volume(self.play_ctl.sink, 100.0)
            self.init_ffplay_slider(100.0)

        # update treeview display and position treeview to current song
        self.update_lib_tree_song(iid)

        ''' If 'from_refresh' splash removed and play_to_end is running '''
        if from_refresh:
            return True  # Return back to self.refresh_play_top() which exits

        ''' Remove 'M' splash screen when mserve.py was called by 'm'. '''
        if self.splash_toplevel:
            self.splash_toplevel.withdraw()  # Remove splash screen
            self.splash_toplevel = None

        ''' Pulse Audio self.sinks_now are freshly updated.
            Check if speech-dispatcher is spamming sound input sinks. '''
        self.check_speech_dispatcher()

        ''' Weird glitch first time with Chronology, vu meter height wrong '''
        if self.vu_meter_first_time:
            self.set_vu_meter_height()  # Third time lucky?
            self.vu_meter_first_time = False

        ''' Play song to end, queue next song and close play_ctl '''
        if not self.play_to_end():  # Play entire song unless next/prev, etc.
            return False  # Shutdown
        self.queue_next_song()  # Save Lyrics Index & set next song
        self.play_ctl.close()
        return True

    def queue_next_song(self):
        """ Song ended. Get next song in list unless already done. """
        if True is True:
            # When training lyrics and clicking 'Next/Prev' buttons the
            # changes are automatically saved.  A better approach needed.
            pass

        if not self.song_set_ndx_just_run:  # Song wasn't manually set
            self.play_save_time_index()  # Save lyrics & time index
            self.song_set_ndx('next')  # Grab next song in playlist

        ''' Reset switch set earlier, or just now with self.song_set_ndx() '''
        self.song_set_ndx_just_run = False
        #if self.ndx + 1 >= len(self.playlist_paths):
        if self.ndx >= len(self.playlist_paths):  # Refine July 30, 2023
            print("Oops playlist was changed and self.ndx not changed.")
            self.ndx = 0
        else:
            self.current_song_path = self.playlist_paths[self.ndx]

    def check_speech_dispatcher(self):
        """ Four annoying speech dispatchers appear in Ubuntu
            TODO: clone to new function that resets Firefox volume from 89%
                  to 100%
        """
        global DELETE_SPEECH
        if not DELETE_SPEECH:
            return  # Already done or don't want to kill pids

        found_pids = list()
        for Sink in pav.sinks_now:
            if Sink.name == "speech-dispatcher":
                found_pids.append(Sink.pid)  # Found a gremlin :)

        if len(found_pids) == 0:
            return  # Nothing found, but can appear 18 minutes after boot.

        DELETE_SPEECH = False  # Don't show message again this session
        title = "Speech Dispatcher Jobs Discovered."
        text = str(len(found_pids)) + " instance(s) of Speech"
        text += "Dispatcher have been found.\n\n"
        text += "Do you want to cancel the job(s)?\n"  # centered: \t breaks
        answer = message.AskQuestion(self.play_top, title, text, 'no',
                                     thread=self.get_refresh_thread)
        text += "\n\t\tAnswer was: " + answer.result
        self.info.cast(title + "\n\n" + text)

        if answer.result != 'yes':
            return  # Don't delete pids
        for pid in found_pids:
            ext.kill_pid_running(pid)

    def check_chrome_tmp_files(self):
        """ Over a few days, chrome can chew up 5 GB of disk space. """
        global CHROME_TMP_FILES
        if not CHROME_TMP_FILES:
            return  # Already done or don't want to kill pids

        tmp = "/tmp/.com.google.Chrome.*"
        results = os.popen("du "+tmp+" -csh --time").read().splitlines()
        print("\ncheck_chrome_tmp_files() 'du", tmp,
              "-csh --time' last line:")
        if results:
            print(results[-1])
        else:
            print("\nERROR - check_chrome_tmp_files() - No results found!")
            print("Command used: 'du ", tmp, " -csh --time'")
            return

        CHROME_TMP_FILES = False  # Don't show message again this session

        title = "Chrome temporary files found."
        text = results[-1].split()[0] + " of Chrome Temporary files found.\n\n"
        text += "Do you want to delete the files?\n"  # 'no': centered \t breaks
        answer = message.AskQuestion(self.lib_top, title, text, 'no',
                                     thread=self.get_refresh_thread)
        text += "\n\t\tAnswer was: " + answer.result
        self.info.fact(title + "\n\n" + text)  # Change from cast to fact

        ''' 
            NOTE Oct 22/23 - When closing lib_top 100MB files are left in /tmp.
                When closing playlists only 4K (Selenium directory?) are left 
                in /tmp.
                
            BUG Oct 17/23 - info.cast(piggy_back  -  Chrome temporary files found.)
                This should not stay as a tooltip. Caused by play top taking
                more time to create than lifespan of info.cast.
        '''

        if answer.result != 'yes':
            return  # Don't delete files

        results = os.popen("rm -rfv "+tmp).read()
        print("\ncheck_chrome_tmp_files() 'rm -rfv ", tmp, "' results:")
        print(results)

    def update_lib_tree_song(self, iid):
        """ Update file's last played time in tkinter treeview.
            Linux only updates last access time once per day so use
            touch command to update last access. For example:
            https://opensource.com/article/20/6/linux-noatime
        :param iid: Integer iid
        """
        _old_time, new_time = self.play_ctl.touch_it()
        self.lib_tree.set(iid, 'StatTime', new_time)
        self.update_song_last_play_time(iid)  # Update treeview
        self.lib_tree.see(iid)  # Position listbox

    def update_song_last_play_time(self, iid):
        """ Called by self.update_lib_tree_song() and self.refresh_acc_times()
        :param iid: Integer iid
        """
        a_time = self.lib_tree.set(iid, 'StatTime')
        f_time = tmf.ago(float(a_time), seconds=True)  # Pretty time format
        self.lib_tree.set(iid, 'Access', f_time)

    def close_lib_tree_song(self, path, a_time):
        """ Final update of file's last played time in lib_top treeview.
            Called by self.play_ctl.close() -> close_callback()
            Use: close_callback=self.close_lib_tree_song
        """
        if path is None or a_time is None:
            return  # Fast clicking 'Next' song
        iid_ndx = self.real_paths.index(path)
        iid = str(iid_ndx)
        self.lib_tree.set(iid, 'StatTime', a_time)
        f_time = tmf.ago(float(a_time), seconds=True)  # Pretty time format
        self.lib_tree.set(iid, 'Access', f_time)

    def play_to_end(self):
        """ Play single song, refreshing screen 30 fps with refresh_play_top()

        Called from:
            play_one_song() to start a new song
            Indirectly called by refresh_play_top() when it calls play_one_song()
                when song ends during long running process like update metadata
            pp_toggle() to resume song after pausing """

        while True:
            ''' Call:
             m.main()
              mserve.main()
               MusicLocationTree(MusicLocTreeCommonSelf)  # Builds lib_top, lib_tree, etc. 
                load_last_selections()  # Load favorites for location
                 play_selected_list()  # Builds play_top, chronology, etc.
                  play_one_song()  # Setup song art, lyrics, etc.
                   play_to_end()  # play song until end
                    check ends  # even refresh_play_top() checks ending
                     '''
            if self.killer.kill_now:
                # SIGTERM to shut down / reboot was received
                print('\nmserve.py play_to_end() closed by SIGTERM')
                self.play_close()  # July 31, was closing everything.
                return False  # Not required because this point never reached.
            if not self.play_top_is_active:
                return False  # Play window closing - Not working when host disconnects
            if self.last_started != self.ndx:  # Different song requested
                return True  # self.song_set_ndx() used prev/next/restart
            if not self.play_ctl.check_pid():
                return True  # Song ended naturally
            self.refresh_play_top()  # Rotate art, update vu meter after(.033)

    def refresh_play_top(self, tk_after=True):
        """ Common code for updating graphics that can be called from anywhere
            Use this when stealing processing cycles from self.play_to_end()
            33 millisecond sleep gives 30 fps (frames per second) video speed.

            Must return True or False for message.py to check.
        """

        ''' Is system shutting down? '''
        if self.killer.kill_now:
            # SIGTERM to shut down / reboot was received
            print('\nmserve.py refresh_play_top() closed by SIGTERM')
            self.close()
            return False  # Not required because this point never reached.

        ''' Host down? (sshfs-fuse cannot be accessed anymore) '''
        if lcs.host_down:
            return False

        ''' Always give time slice to tooltips '''
        now = time.time()
        root.update_idletasks()
        self.tt.poll_tips()
        pav.poll_fades()

        ''' May be called from Library with no music playing (tooltip)  '''
        if not self.play_top_is_active:
            return False  # Used to be a "continue" statement

        ''' Synchronizing lyrics to time index controls music '''
        if self.fine_tune and self.fine_tune.top_is_active:
            #self.fine_tune.top_lift()  # Raise window focus to top
            # Above steals focus and keyboard from other applications !
            # Above was source of HUGE BUG July 4, 2023
            self.fine_tune.top.update()  # Without this no keyboard/mouse click
            sleep = SLEEP_PLAYING - (int(time.time() - now))
            sleep = 1 if sleep < 1 else sleep   # Sleep minimum 1 millisecond
            self.fine_tune.top.after(sleep)  # Wait until lyric sync
            return False  # Looks like True causes animations to freeze

        ''' Set previous or restart into button text '''
        if self.prev_button_text == self.previous_text:
            if self.current_song_secs > float(REW_CUTOFF):
                self.prev_button_text = self.restart_text
                self.prev_button['text'] = self.prev_button_text
                self.tt.set_text(self.prev_button, "Restart song at beginning.")

                ''' 
                # Quick test ShowInfo on program startup
                text = "Hello World !\n\n"
                text += "\tOne Tab\tTab 2\n"
                text += "\t\tDouble Tab\tAnother Tab"
                message.ShowInfo(self.play_top, text=text, align='left',
                                 thread=self.get_refresh_thread,
                                 title="debug if ShowInfo freezes")
                '''
        else:  # Previous button text says "Restart"
            if self.current_song_secs < float(REW_CUTOFF):
                self.prev_button_text = self.previous_text
                self.prev_button['text'] = self.prev_button_text
                self.tt.set_text(self.prev_button, "Play previous song.")

        ''' Playing music for Hockey Commercial or Intermission '''
        if self.play_hockey_active:                  # Is hockey active?
            elapsed = int(time.time() -
                          self.play_hockey_t_start)  # Elapsed time Hockey
            self.hockey_countdown(elapsed)           # Remaining in buttons
            if elapsed > self.play_hockey_secs:      # Has countdown ended?
                if self.pp_state is "Playing":       # Is music playing?
                    self.pp_toggle()
                # Important line below is done AFTER pp_toggle() is called
                # Otherwise getting sound spike below because moving
                # from 100% instead of 60% volume down
                self.play_hockey_active = False      # Turn off timer

        ''' When current state is "Paused" there is nothing to do but sleep now '''
        if self.pp_state is "Paused":
            #if not self.play_top_is_active:
            #    return False  # June 18, 2023 next line error on shutdown
            #if self.lib_top is not None:  # This is shut-down first as signal
            if not self.play_top_is_active:
                return False  # Added June 19, 2023
            if not self.lib_top_is_active:  # About to shutdown - First flag set
                return False  # June 18, 2023 next line caused error on shutdown
            self.play_top.update()           # Sept 20 2020 - Need for lib_top too

            ''' Aug 12/23 - Optional tk_after to speed up loops '''
            if not tk_after:
                return self.play_top_is_active

            # Jun 20 2023 - Losing 5 ms on average see: self.info.test_tt()
            now = time.time()  # June 20, 2023 - Use new self.last_sleep_time
            sleep = SLEEP_PAUSED - int(now - self.last_sleep_time)
            sleep = sleep if sleep > 0 else 1  # Sleep minimum 1 millisecond
            self.last_sleep_time = now
            if not self.play_top_is_active:
                return False  # Next line caused error July 31, 2023
            self.play_top.after(sleep)          # Wait until playing
            return self.play_top_is_active

        ''' May 23, 2023 - Updating metadata takes 10 minutes for 5,000 songs.
                Current song would end before completion. Also a song can end
                when .ShowInfo is active. So play next song in list.

            Aug 9/23 - cmp_update_files and missing_artwork_callback lock up
                because they call the first refresh_play_top which doesn't
                return because it spawns play_one_song() that generates new
                refresh_play_top return chain.
        '''
        self.play_ctl.check_pid()   # play_ctl class is omnipresent
        if self.play_ctl.path and self.play_ctl.pid == 0:
            # Music has stopped playing and code below has been run once because
            # self.play_ctl.path has been run
            self.play_ctl.close()   # Update last song's last access time
            self.song_set_ndx_just_run = False  # Aug 31/23 - same song repeats
            self.queue_next_song()  # Queue up next song in list
            #self.song_set_ndx_just_run = True  # So queue doesn't repeat...
            # Called by def play_to_end which is waiting for song to end
            # by checking self.last_started != self.ndx and then pid == 0.
            # play to end was called by def play_one_song
            self.lib_top.update()  # Big guns for ShowInfo frozen.
            ret = self.play_one_song(from_refresh=True)
            self.lib_top.update_idletasks()  # Pea-shooter instead.
            if ret is None:
                print("Error self.play_one_song(from_refresh=True)",
                      "returned 'None'")
                return False
            if ret is not True:
                print("Error self.play_one_song(from_refresh=True)",
                      "returned 'False'")
                return False
            return True  # Called self.play_one_song successfully.

        ''' Updated song progress and graphics for song that is playing 
            TODO: Review each function below for being called faster than 30 FPS
        '''
        self.play_update_progress()             # Update screen with song progress
        self.play_spin_art()                    # Rotate artwork 1°
        self.play_vu_meter()                    # Left & Right VU Meters
        self.play_paint_lyrics()                # Uses the lyrics time index
        if not self.play_top_is_active:
            return False                        # Play window closed so shutting down
        self.play_top.update()                  # Update artwork spinner & text

        ''' Aug 5/23 - Optional tk_after to speed up loops '''
        if not tk_after:
            return self.play_top_is_active

        # Jun 20 2023 - Losing 5 ms on average see: self.info.test_tt()
        now = time.time()  # June 20, 2023 - Use new self.last_sleep_time
        sleep = SLEEP_PLAYING - int(now - self.last_sleep_time)
        sleep = sleep if sleep > 0 else 1  # Sleep minimum 1 millisecond
        self.last_sleep_time = now
        if self.play_top:  # Aug 2/23 - exiting
            #self.play_top.after(sleep)  # Sleep until next 30 fps time
            self.lib_top.after(sleep)  # Aug 9/23 - Try lib_top.after() seems OK?
        return self.play_top_is_active

    def play_update_progress(self, start_secs=None):
        """ Calculate song progress. This is approximate value. Exact value
            obtained using: self.play_ctl.elapsed()

        :param start_secs: Optional. Song is starting at seconds passed.
        """
        if start_secs:
            # Exact seconds elapsed is passed
            self.current_song_secs = start_secs
            self.current_song_t_start = time.time() - start_secs
            if self.pp_state is "Playing":
                self.secs_before_pause = 0.0
            else:
                self.secs_before_pause = start_secs
        else:
            self.current_song_secs = \
                time.time() - self.current_song_t_start + self.secs_before_pause

        self.current_song_mm_ss_d = tmf.mm_ss(self.current_song_secs,
                                              trim=False, rem='d')

        # Two formats for displaying song's: "progress of: duration"
        if True is True:
            # FORMAT IS - hh:mm:ss of: hh:mm:ss
            self.song_progress_var.set(self.current_song_mm_ss_d +
                                       " of: " + self.saved_DurationMin)
        else:
            # FORMAT IS - 9999.9 seconds of: 9999.9
            self.song_progress_var.set(str('%.1f' % self.current_song_secs) +
                                       " seconds of: " + str(self.saved_DurationSecs))

    @staticmethod
    def update_sql_metadata(file_ctl):
        """ Legacy code crafted to new function June 28, 2023.
            Multiple file controls can be calling at same time.
            E.G. Playing Music and self.missing_artwork_callback()
        :param file_ctl: self.play_ctl, self.ltp_ctl, self.mus_ctl
        :returns False: when no changes were needed.
        """
        ''' Using instance of threading.Lock() '''
        with critical_function_lock:
            ''' This should ensure only one thread accesses at a time '''
            meta_update_succeeded = None
            if file_ctl.path.startswith(PRUNED_DIR):
                ''' July 18, 2023 conversion '''
                meta_update_succeeded = sql.update_metadata(file_ctl)
                # WARNING: Returns false when no changes made
            else:
                # July 21, 2023 - SQL created metadata from another location.
                #   Needs work ...
                print('mserve.py update_sql_metadata() path:', file_ctl.path)
                print('mserve.py update_sql_metadata() Missing PRUNED_DIR:', PRUNED_DIR)
                pass

            return meta_update_succeeded

    def play_spin_art(self):
        """
            Spin artwork clockwise, rotate artwork -1° each decisecond
            at 0° slide up and pixelate, -90° slide right, -180° slide down,
            and at -270° slide left.
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
                "RGBA", (self.art_width, self.art_height), self.theme_bg)
            rot = im.rotate(self.play_rotated_value)
            self.play_rotated_art.paste(rot, (0, 0), rot)
            ''' July 3, 2023, change self.play_frm_bg to self.theme_bg '''
            ''' ――If Pillow version >= 5 solution is simple
            self.play_rotated_art = self.play_resized_art. \
                                    rotate(self.play_rotated_value, \
                                    fillcolor=self.theme_bg)
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
            at 0° slide up, -90° slide right, -180° slide down, -270° slide left
        """
        if self.play_art_slide_count == 100 or self.art_width < 10:
            # Completed a loop + 1 idle loop using 100 %
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
            # Completed a full cycle - At 100% it breaks so do 99%:
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
            print('self.play_rotated_ar - format, size, mode:',
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
            # Completed a full cycle. Force graphical effects exit
            self.play_art_fade_count = 0  # Reset art fade count
            self.play_rotated_value = -361  # Force Spin Art
            return None

        # Initialize numpy arrays first time through
        if self.play_art_fade_count == 0:

            # Create contrasting black or white image to fade into (foreground)
            self.fade = Image.new('RGBA', self.play_rotated_art.size,
                                  color=self.theme_bg)

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
    #       Music Location Tree Processing - VU Meter
    #
    # ==============================================================================

    def play_vu_meter_blank(self):
        """ Display blank VU Meters (Left and Right), when music paused.
            Previous dynamic display rectangles have already been removed. """
        self.play_vu_meter_blank_side(self.vu_meter_left,
                                      self.vu_meter_left_rect)

        self.play_vu_meter_blank_side(self.vu_meter_right,
                                      self.vu_meter_right_rect)

    def play_vu_meter_blank_side(self, canvas, rectangle):
        """ Display one blank VU Meter (Left or Right), when music paused. """
        x0, y0, x1, y1 = 0, 0, self.vu_width, self.vu_height
        canvas.coords(rectangle, x0, y0, x1, y1)
        canvas.create_rectangle(x0, y0, self.vu_width, y1,
                                fill=self.theme_bg,
                                width=1, outline='black', tag="rect")

    def play_vu_meter(self, stop='no'):
        """ Update VU Meter display, either 'mono' or 'left' and 'right' """
        if stop == 'yes':
            # Stop display
            self.play_vu_meter_side(
                'stop', self.vu_meter_left,
                self.vu_meter_left_rect, self.vu_meter_left_hist)

            self.play_vu_meter_side(
                'stop', self.vu_meter_right,
                self.vu_meter_right_rect, self.vu_meter_right_hist)
            return

        # Regular display
        self.play_vu_meter_side(
            VU_METER_LEFT_FNAME, self.vu_meter_left,
            self.vu_meter_left_rect, self.vu_meter_left_hist)

        self.play_vu_meter_side(
            VU_METER_RIGHT_FNAME, self.vu_meter_right,
            self.vu_meter_right_rect, self.vu_meter_right_hist)

    def play_vu_meter_side(self, fname, canvas, rectangle, history):
        """ Update one VU Meter display
            One time bug: Aug 12/23 - 40 LED's were treated as two LED's of
                20 blocks each.
        """
        if fname == 'stop':
            # Pausing music but vu_meter.py will wait for sounds and
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
            # Have vu_max. set y0 to percentage of volume, 0 = 100% volume
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
        """ Number of rectangles depends on height:
                A rectangle must be at least 2 pixels high
                Space between rectangles must be at least 1 pixel

            100 possible steps but there can be scaling down. Reserve
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
                17 green rectangles (the remainder of 30 - others) """
        num_rect = height / 13  # How many rectangles will fit in height?
        if num_rect < 1:
            num_rect = 1  # Not enough height for rectangles
        r_hgt_pad = int(height / num_rect)
        r_hgt = r_hgt_pad - 2  # Experimental overrides
        if r_hgt < 1:
            r_hgt = 1  # Not enough height for rectangles

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

        num_rect = len(y_list)  # May end up with fewer rectangles

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
    #       Music Location Tree Processing - Lyrics Score
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

        #print('BEGIN:', self.play_ctl.Artist, self.play_ctl.Album,
        #      self.play_ctl.Title)

        if self.lyrics_time_list is None:
            # print('overriding lyrics time index from None to empty list.')
            self.lyrics_time_list = []  # Seconds time index

        if self.lyrics_score is not None:
            if len(self.lyrics_score) < 10:
                # "[Instrumental]" is the shortest lyrics stored so under 10 is empty
                # It is possible web scraper returns single character we call "None".
                self.lyrics_score = None

        if self.lyrics_score is None:
            # print('web scraping lyrics from internet')
            self.play_lyrics_from_web()  # scrape lyrics from web
        else:
            # print('getting lyrics from library, count:', len(self.lyrics_score))
            self.play_lyrics_from_library()  # lyrics in Music Table

        self.play_lyrics_rebuild_title()

    def play_lyrics_rebuild_title(self):
        """ Query status of widgets and make panel(title) over lyrics body """
        if not self.play_top_is_active:
            return  # Play window is closed

        '''
        # Redefine frame
        if self.lyrics_frm:
            for widget in self.lyrics_frm.winfo_children():
                widget.destroy()
                # _tkinter.TclError: bad window path name ".140066774294968..."
        WE MIGHT RESURRECT THIS CODE: 
        # Remove all widgets in top panel
        if self.lyrics_frm:
            self.lyrics_frm.destroy()
        self.lyrics_frm = tk.Frame(self.lyrics_master_frm)
        self.lyrics_frm.grid(row=0, row span=1, column=0, sticky=tk.NSEW)
        self.lyrics_frm.grid_rowconfigure(0, weight=0)
        self.lyrics_frm.grid_columnconfigure(0, weight=1)
        '''

        line_count = str(self.work_line_count)
        special = True  # Default to reverse highlight title
        # TODO: Set time-limit for scraping 30 seconds.
        #       Handle Lyrics=None many times for songs with invalid sql key
        scrape_text = \
            "Web scraping takes a couple of seconds.\n" + \
            "If no internet connection BAD THINGS HAPPEN\n" + \
            "NOTE: You can copy lyrics from any website and paste."

        ''' Web scraping mode '''
        if not self.lyrics_scrape_done and self.lyrics_scrape_pid == 0:
            self.lyrics_panel_text = \
                'Clicking Next/Prev song too fast for web scraping to finish'
            self.tt.set_text(self.lyrics_panel_label, text=scrape_text)

        elif not self.lyrics_scrape_done:
            # NOT TESTED
            self.lyrics_panel_text = "Web scrape in progress..."
            self.tt.set_text(self.lyrics_panel_label, text=scrape_text)

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

        elif self.fine_tune and self.fine_tune.top_is_active:
            ''' Fine-tune mode '''
            self.lyrics_panel_text = "Disabled during Fine-tune"
            self.tt.set_text(self.lyrics_panel_label, text="Finish fine-tuning.")

        else:
            ''' Normal mode - Nothing special going on '''
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
            #self.lyrics_update_title_line_number(1)  # TODO: This doesn't make sense
            if line_no == 0:  # July 6, 2023 - Little fix for if resume:
                line_no = 1  # possibly this ws reason it was forced to 1 above
            self.lyrics_update_title_line_number(line_no)
            self.lyrics_update_title_percentage()
            special = False  # Do not reverse highlight title or remove buttons

        # Lifted from set_artwork_colors()
        if special:
            # Reverse title to highlight special mode
            self.lyrics_frm.configure(bg=self.theme_fg)
            toolkit.config_all_labels(self.lyrics_frm, fg=self.theme_bg,
                                      bg=self.theme_fg)
            # Unfortunately can't change canvas color or text color, just the
            # outline background color. So tags are set up for rounded rectangle
            # and text within it. Below sets background around rounded corners.
            toolkit.config_all_canvas(self.lyrics_frm,
                                      bg=self.theme_fg)
            # hamburger colors are inverted during special
            self.lyrics_panel_hamburger.update_colors(
                self.theme_bg, self.theme_fg)
            self.lyrics_score_box.vbar.pack()

            # Hide four rounded rectangle buttons for auto/time/manual mode
            self.grid_remove_lyrics_panel_scroll()
            # Shrink size of four rounded rectangles
            self.set_min_dimensions()
            # place label text further to left
            self.lyrics_panel_label.place(relx=0, rely=.5, anchor="w")
        else:
            # Restore title to normal display
            self.lyrics_frm.configure(bg=self.theme_bg)
            toolkit.config_all_labels(self.lyrics_frm, fg=self.theme_fg,
                                      bg=self.theme_bg)
            toolkit.config_all_canvas(self.lyrics_frm,
                                      bg=self.theme_bg)
            # Hide .vbar scroll bar for lyrics score
            if self.lyrics_auto_scroll or self.lyrics_time_scroll:
                self.lyrics_score_box.vbar.pack_forget()
            else:
                self.lyrics_score_box.vbar.pack(side="right", fill="y")

            # Restore four rounded rectangle buttons for auto/time/manual mode
            self.set_max_dimensions()

            # hamburger colors were inverted during special so restore them
            self.lyrics_panel_hamburger.update_colors(
                self.theme_fg, self.theme_bg)

            # place label text back to center
            self.lyrics_panel_label.place(relx=.6, rely=.5, anchor="center")

        # Refresh panel label from new special or normal setup
        self.lyrics_panel_label['text'] = self.lyrics_panel_text

    def grid_remove_lyrics_panel_scroll(self):
        """ Remove rounded rectangles. """
        self.lyrics_panel_scroll_a_m.grid_remove()
        self.lyrics_panel_scroll_t_m.grid_remove()
        self.lyrics_panel_scroll_m_a.grid_remove()
        self.lyrics_panel_scroll_m_t.grid_remove()

    def grid_lyrics_panel_scroll(self):
        """ Display rounded rectangles. """
        self.lyrics_panel_scroll_a_m.grid()
        self.lyrics_panel_scroll_t_m.grid()
        self.lyrics_panel_scroll_m_a.grid()
        self.lyrics_panel_scroll_m_t.grid()

    def play_clear_lyrics(self):  # Reset all fields
        """ Reset lyrics score scrollbox. """
        self.lyrics_score_box.configure(state="normal")
        self.lyrics_score_box.delete("1.0", "end")  # Delete last lyrics
        self.lyrics_score_box.update()  # Refresh immediately
        self.lyrics_score_box.configure(state="disabled")
        if not self.lyrics_scrape_pid == 0:
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
        self.work_line_count = self.lyrics_line_count
        self.lyrics_score_box.update()

    def play_lyrics_from_web(self):
        """ turn on auto scrolling, it can be overridden from saved steps or
            if left-clicking on lyrics to set lyrics line to time index.
        """
        # webscrape.delete_files()  # Cleanup last run
        self.lyrics_line_count = 1  # Average about 45 lines

        ''' uni_str = byte_str.encode("utf-8")  DOES NOT WORK !!! 
                https://stackoverflow.com/questions/4182603/
                how-to-convert-a-string-to-utf-8-in-python
        '''
        artist = ext.shell_quote(self.play_ctl.Artist)  # backslash in front of '
        title = ext.shell_quote(self.play_ctl.Title)     # and " in variables
        # 'Bob Seeger & The Silver Bullet Band' finds nothing, while just
        # 'Bob Seeger' finds 'Shakedown' title.
        artist = artist.split('&', 1)[0]
        comment = time.asctime(time.localtime(time.time()))

        if self.lyrics_scrape_pid == 0:
            # Only start new search if last one is finished.
            MusicId = sql.music_id_for_song(self.play_make_sql_key())

            ''' MusicId is 0 when no Artist or Album '''
            if MusicId is None or MusicId == 0:
                self.info.cast("Songs with no Artist or no Album cannot be scraped.")
                return

            try:
                sql.hist_add(time.time(), MusicId, g.USER, 'scrape', 'parm',
                             artist, title, "", 0, 0, 0.0, comment)
                self.info.fact("Begin scraping lyrics for title: " + title)
            except sql.sqlite3.Error as er:  # Changed July 12, 2023: TEST IT
                print('SQLite error: %s' % (' '.join(er.args)))
                print("Exception class is: ", er.__class__)
                print('SQLite traceback: ')
                exc_type, exc_value, exc_tb = sys.exc_info()
                print(traceback.format_exception(exc_type, exc_value, exc_tb))
                ''' Move this error trapping into sql.py
                    Then remove: import sqlite3 
                            and: import trace 
                '''
                self.info.cast("sql.sqlite3.ProgrammingError: " + artist, 'error', 'update')
                return

            sql.con.commit()
            # Aug 25 fudge parameter list to skip no_parameters()
            parm = '"' + artist + ' ' + title + '" ' + str(MusicId)
            ext_name = 'python webscrape.py ' + parm
            self.lyrics_scrape_pid = ext.launch_command(
                ext_name, toplevel=self.play_top)
        else:
            text = 'Last instance of webscrape is still running.'
            print(text)
            self.info.cast(text)
            return

        self.lyrics_scrape_done = False  # Signal not done yet
        self.lyrics_auto_scroll = True
        self.lyrics_time_scroll = False
        # No lyrics found is checked later to override auto scrolling
        # print('initial self.lyrics_scrape_pid:', self.lyrics_scrape_pid, \
        #      'type:', type(self.lyrics_scrape_pid))

    def play_paint_lyrics(self, rewind=False):
        """ High level function to ensure window is up-to-date with all
            information. Scrolls lyrics as necessary and highlights current
            line if lyrics_time_list is populated.
        """
        if not self.lyrics_scrape_done:
            ''' It takes 4 seconds to get lyrics from internet '''
            self.lyrics_scrape_pid = ext.check_pid_running(self.lyrics_scrape_pid)
            if self.lyrics_scrape_pid == 0:
                self.play_process_scraped_lyrics()
                # Save the lyrics just scraped from the web
                self.play_save_score_erase_time()
                self.lyrics_scrape_done = True
                self.play_lyrics_rebuild_title()
                self.info.fact("Lyrics scraped for: " + self.play_ctl.Title)
            else:
                return  # Still fetching lyrics

        # Update percentage complete in lyrics title bar
        self.lyrics_update_title_percentage()

        ''' Scroll automatically or by interactive / recorded steps '''
        if self.lyrics_edit_is_active:
            return  # Is user editing lyrics?

        if self.lyrics_auto_scroll:
            self.play_lyrics_auto_scroll()
        else:
            self.play_lyrics_time_scroll(rewind=rewind)

        # Override auto_scroll
        if self.lyrics_score and self.lyrics_score.startswith("No lyrics found for"):
            # May 9, 2023 - Don't scroll instructions from webscrape
            # self.play_lyrics_toggle_scroll()
            # self.lyrics_auto_scroll = True
            self.lyrics_old_scroll = 'auto'  # Save auto scrolling state
            self.lyrics_auto_scroll = False  # Turn off auto scrolling
            self.lyrics_time_scroll = False  # Turn off time scrolling
            self.play_lyrics_rebuild_title()
            pass

    def play_process_scraped_lyrics(self):
        """ Read lyrics and populate text box """
        if self.lyrics_edit_is_active:
            return  # Is user editing lyrics?

        self.lyrics_score_box.configure(state="normal")
        with open(webscrape.SCRAPE_LYRICS_FNAME, "r") as ws_file:
            lines = ws_file.readlines()
            for line in lines:
                # Skip lines with all whitespace
                #if not line.isspace():
                #    self.lyrics_score_box.insert(tk.END, line)
                self.lyrics_score_box.insert(tk.END, line)  # Space is needed.

        self.lyrics_score_box.update()  # Is this necessary? CONFIRMED YES
        self.lyrics_score_box.configure(state="disabled")
        webscrape.delete_files()

        end = self.lyrics_score_box.index('end')  # returns line.column
        self.lyrics_line_count = int(end.split('.')[0]) - 1

    def play_make_sql_key(self):
        """ Create key to read Music index by OsFileName which is
            album/artist/99 song.ext.  PRUNED_DIR usually same as START_DIR
            except when called manually with path to Artist Name or Album Name
        """
        slice_from = len(PRUNED_DIR)  # Has / at end
        return self.real_path(int(self.saved_selections[self.ndx]))[slice_from:]

    def play_save_score_erase_time(self):
        """ Preliminary lyrics save that WIPES OUT the lyrics time index """
        if not self.play_top_is_active or self.lyrics_edit_is_active:
            return  # Play closed or user editing lyrics?

        self.lyrics_score = self.lyrics_score_box.get("1.0", 'end-1c')
        save = self.play_override_score()
        sql.update_lyrics(self.play_make_sql_key(), save, None)

    def play_override_score(self):
        """ If lyrics not found return None, else return them """
        if self.lyrics_score is None:
            return None  # Jan 3, 2023
        if self.lyrics_score.startswith("No lyrics found for "):
            # May 9, 2023 - This was broken and save was being done
            # However this is good so we don't keep trying to retrieve
            # You find using SQL Music Text String "No lyrics".
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

    def play_lyrics_time_scroll(self, rewind=False):
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

        if rewind is True:
            # Song rewound 10 seconds so current line resets and needs look up
            self.lyrics_curr_line = 0
            #print("rewind requested. self.current_song_secs:", self.current_song_secs)

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
            # Last line
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
                self.play_lyrics_see_ahead(rewind=rewind)

        self.lyrics_prev_line = self.lyrics_curr_line

        # Update 'Line: 99 of 99' in lyrics title bar (aka panel)
        self.lyrics_update_title_line_number(self.lyrics_curr_line)

    # ==============================================================================
    #
    #       Music Location Tree Processing - Basic time index
    #
    # ==============================================================================

    def play_train_lyrics(self):
        """ Train Lyrics was right-clicked.
        NOTE: Right click again to Save/Cancel.

        TODO:

        lyrics_time_list is copied into work_time_list  IS IT A DEEP COPY?
        work_time_list is copied into new_time_list  IS IT A DEEP COPY?
        changes are made to new_time_list. If posted then
        new -> work -> update SQL and lyrics_time_list


        """
        if not self.lyrics_scrape_pid == 0:
            print('lyrics are being web scraped. Please wait a second.')
            return

        if not self.play_top_is_active or \
                self.fine_tune and self.fine_tune.top_is_active:
            return

        print('TRAIN LYRICS:', self.play_ctl.Artist, self.play_ctl.Album,
              self.play_ctl.Title)

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
        """ Train Lyrics done. action='save' or 'cancel'.
            The menu option 'Done' actually calls 'cancel'.
            Only called from popup menu options:

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

        After play_to_end() comes queue_next_song() which calls:
            play_save_time_index(self):
                save = self.play_override_score()

                if self.lyrics_time_list is not None:
                    if len(self.lyrics_time_list) == 0:
                        self.lyrics_time_list = None

                sql.update_lyrics(self.play_make_sql_key(), save,
                                  self.lyrics_time_list)
        """
        self.lyrics_train_is_active = False  # Allow normal read/save ops

        # noinspection SpellCheckingInspection
        ''' ERROR on manual save (Luckily auto-save works when song ends):
TRAIN LYRICS: Bachman-Turner Overdrive The Definitive Collection Lookin' Out For #1
left click lyrics line not handled. line_cnt: 18 prev_line: 10 curr_line: 19
curr_line has been reset to prev_line
TRAIN LYRICS: Bachman-Turner Overdrive The Definitive Collection Lookin' Out For #1
Exception in Tkinter callback
Traceback (most recent call last):
  File "/usr/lib/python2.7/lib-tk/Tkinter.py", line 1540, in __call__
    return self.func(*args)
  File "/home/rick/python/mserve.py", line 9333, in <lambda>
    self.play_train_lyrics_done('save'),
  File "/home/rick/python/mserve.py", line 8792, in play_train_lyrics_done
    self.edit_current_cursor)
  File "/usr/lib/python2.7/lib-tk/Tkinter.py", line 3120, in mark_set
    self.tk.call(self._w, 'mark', 'set', markName, index)
TclError: wrong # args: should be ".139661069361096.139661064270480.139661063811800.139661063819208.139661063817768 
mark set markName index"
        '''

        # If cancel bail out
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
            # May 9, 2023 - Save lyrics before song ends gets this error:

            #   File "/home/rick/python/mserve.py", line 7087, in play_train_lyrics_done
            #     self.edit_current_cursor)
            #   File "/usr/lib/python2.7/lib-tk/Tkinter.py", line 3120, in mark_set
            #     self.tk.call(self._w, 'mark', 'set', markName, index)
            # TclError: wrong # args: should be ".139993090173192.139992691519856.
            # 139993090169744.139992694323392 mark set markName index"
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

            BEWARE: work_time_list, new_time_list and lyrics_time_list are
                    used differently.

            Lyrics were either retrieved from the internet (takes 2 seconds) or
            from SQL row in table Music indexed by OsFileName. There may be
            duplicates so read until Music.OsArtist and Music.OsAlbum match as
            well. Use self.real_paths

        """
        if self.lyrics_edit_is_active:
            # When editing lyrics, any left click is to position cursor and
            # not for changing highlighted line for synchronizing time index
            return

        if not self.lyrics_train_is_active:
            # If not in basic training, treat left-click as right-click
            #self.play_lyrics_right_click(event)
            # Disable left click to bring up menu. Too annoying when just
            # trying to select menu.
            return

        if self.pp_state is 'Paused':
            # If Pause/Play State is currently paused we can not synchronize
            # June 5/2021: change top level from self.play_top
            answer = message.AskQuestion(
                self.lyrics_score_box, thread=self.get_refresh_thread,
                title="Music is paused - mserve", confirm='no',
                text="Left clicking synchronizes lyrics\n" +
                     "but only works when music is playing.\n" +
                     "Do you want to resume playing?")
            if answer.result is 'yes':
                self.pp_toggle()  # Resume playing
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

        self.lyrics_frm.update()
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
            toolkit.print_trace()
            print('lyrics_update_title_line_number() string not found')
            # After deleting all lyrics get error:

            # File "/home/rick/python/mserve.py", line 7489, in play_to_end
            #     self.refresh_play_top()  # Rotate art, update vu meter after(.033)
            # File "/home/rick/python/mserve.py", line 7630, in refresh_play_top
            #     self.play_paint_lyrics()                # Uses the lyrics time index
            # File "/home/rick/python/mserve.py", line 8442, in play_paint_lyrics
            #     self.play_lyrics_auto_scroll()
            # File "/home/rick/python/mserve.py", line 8537, in play_lyrics_auto_scroll
            #     self.lyrics_update_title_line_number(line_no)
            # File "/home/rick/python/mserve.py", line 8893, in lyrics_update_title_line_number
            #     toolkit.print_trace()
            # File "/home/rick/python/toolkit.py", line 87, in print_trace
            #     for line in traceback.format_stack():
            # lyrics_update_title_line_number() string not found

            return

        suffix2 = suffix.split()[2:]
        self.lyrics_panel_text = prefix + "Line: " + str(line_no) + " " + \
            ' '.join(suffix2)
        self.lyrics_frm.update()
        self.lyrics_panel_last_line = line_no

    def play_lyrics_see_ahead(self, rewind=False):
        """ Should always see two lines ahead to coming up.
            If rewinding need to see previous two lines. """
        ''' July 4, 2023 Now show next five lines instead of next two. '''
        if rewind:
            # When rewinding song we are jumping backwards in lyrics
            line_no = self.lyrics_curr_line - 2  # show backwards
        else:
            line_no = self.lyrics_curr_line + 5  # Reveal up-coming

        if line_no > self.lyrics_line_count:
            line_no = self.lyrics_line_count
        elif line_no < 1:
            line_no = 1
        self.lyrics_score_box.see(str(line_no) + ".0")
        ''' July 6, 2023 override to ensure one line before is displayed '''
        if self.lyrics_curr_line > 1:
            self.lyrics_score_box.see(str(self.lyrics_curr_line - 1) + ".0")

    def play_lyrics_replace_time(self):
        """ Clicking same line again to reset start time.

            Called when:

            if self.lyrics_prev_line + 1 == self.lyrics_curr_line:
                if line_cnt > self.lyrics_curr_line:
                    play_lyrics_replace_time(self):
            elif self.lyrics_prev_line == self.lyrics_curr_line:
                    play_lyrics_replace_time(self):

        """
        #print('play_lyrics_replace_time() BEGIN')
        this_ndx = self.lyrics_curr_line - 1
        if self.lyrics_time_list[this_ndx] < self.current_song_secs:
            # Clicked ahead too quickly now going back. Keep time
            #print('Clicked ahead too quickly now going back. Keep time')
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
        """ Highlight Lyric's score line """
        self.lyrics_score_box.tag_add("highlight", "{}.0".format(n),
                                      "{}.0+1lines".format(n))

    def play_lyrics_remove_highlights(self):
        """ Remove all Lyric's score highlights """
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
    #       Music Location Tree class - Lyrics Right click menu - Edit, Scrape options
    #
    # ==============================================================================

    def play_lyrics_fake_right_click(self):
        """ Callback from RoundedRectangle click on hamburger menu
        """
        fake_event = message.FakeEvent(self.lyrics_frm)
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

        if self.fine_tune and self.fine_tune.top_is_active:
            self.fine_tune_lift()
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
                             command=lambda: self.start_fine_tune())
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
        if not self.lyrics_scrape_pid == 0:
            print('lyrics are already being web scraped. Please wait a second')
            return

        # Give warning box when lyrics exist all will be lost!
        if len(self.lyrics_score) > 10:
            answer = message.AskQuestion(
                self.play_top, thread=self.get_refresh_thread,
                title="Lyrics will scraped from web and replaced",
                text="If you have edited these lyrics all changes will be lost!" +
                "\n\nTIP: You can edit lyrics to copy and paste groups of lines.")
            if answer.result != 'yes':
                return

        self.play_clear_lyrics()  # Reset all fields
        if not self.play_top_is_active:
            return

        # print('GET NEW:',self.play_ctl.Artist,self.play_ctl.Album,
        # self.play_ctl.Title)
        # print('web scraping lyrics from internet')
        self.play_lyrics_from_web()  # scrape lyrics from web

        # When music is paused the lyrics never appear on their own
        while self.pp_state is 'Paused' and self.lyrics_scrape_done is False:
            ''' It takes a few seconds to get lyrics from internet '''
            self.play_paint_lyrics()
            self.refresh_play_top()

    def play_clip_paste_lyrics(self):
        """ Delete current song lyrics and insert text from clipboard.
        """
        # Give warning box when lyrics exist all will be lost!
        if len(self.lyrics_score) > 10:
            answer = message.AskQuestion(
                self.play_top, thread=self.get_refresh_thread,
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
    #       Music Location Tree Processing - Edit lyrics
    #
    # ==============================================================================

    def play_edit_lyrics(self):
        """ Edit Lyrics was right-clicked. Right click again to Save/Cancel.
            Typical usage:
                A. Copy [chorus] block and paste at next [chorus] tag.
                B. Correct works like "have" to "got" and vice versa.
                C. Remove line break before single comma on its own line.
        """
        if not self.lyrics_scrape_pid == 0:
            print('lyrics are being web scraped. Please wait a second.')
            return

        if not self.play_top_is_active or \
                self.fine_tune and self.fine_tune.top_is_active:
            return

        #print('EDIT LYRICS:', self.play_ctl.Artist, self.play_ctl.Album,
        #      self.play_ctl.Title)

        self.play_lyrics_remove_highlights()

        # Save current time index because by time editing is finished may be
        # on a different song.
        #self.play_save_time_index()

        # Turn on text editing make insert cursor visible by setting background
        # If too narrow set insert width=4 or more.
        self.lyrics_score_box.configure(state="normal",
                                        insertbackground=self.theme_fg)
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

            July 5, 2023 - Was copying reference to same object. Object was
            not being copied. https://stackoverflow.com/a/68209690/6929343
        """
        self.work_sql_key = self.play_make_sql_key()
        self.work_lyrics_score = self.lyrics_score
        self.work_time_list = list(self.lyrics_time_list)
        self.work_song_path = self.current_song_path
        self.work_song_secs = self.current_song_secs
        self.work_DurationSecs = self.play_ctl.DurationSecs
        self.work_Title = self.play_ctl.Title
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
        #print('current_cursor:', self.edit_current_cursor)
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
                self.play_top, thread=self.get_refresh_thread,
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

    def start_fine_tune(self):
        """ Called from dropdown menu """
        if self.fine_tune and self.fine_tune.top_is_active:
            ''' The <Focus> event should trap this error '''
            #self.fine_tune.top_lift()  # Need name change....
            # Above steals focus and keyboard from other applications !
            self.fine_tune_lift()
            self.info.cast('start_fine_tune(): Should not be here a second time.')
            return

        if not self.lyrics_scrape_pid == 0:
            ''' After lyrics scraped they still need Basic Time Index done. '''
            self.info.cast('lyrics are being web scraped.')
            return

        if self.pp_state is "Playing":          # Is music playing?
            self.pp_toggle()                    # Pause to synchronize lyrics
            self.sync_paused_music = True       # So we can resume play later

        self.play_lyrics_rebuild_title()
        self.play_create_lyrics_work_fields()  # sql key, lyrics & time list
        self.fine_tune = FineTune(
            self.play_top, self.tt, self.info, self.play_ctl, self.work_sql_key,
            self.work_lyrics_score, self.work_time_list, self.play_original_art,
            self.theme_fg, self.theme_bg, self.current_song_secs,
            self.get_refresh_thread, self.fine_tune_closed_callback)

    def fine_tune_closed_callback(self, new_lyrics_score, new_time_list):
        """ Called from FineTune() class """

        if not self.play_top_is_active:
            return  # Nothing to do if Playing window closed

        self.play_lyrics_rebuild_title()
        if self.sync_paused_music:  # Did Fine-Tune Index pause the music?
            self.pp_toggle()  # Resume play

        if new_lyrics_score is None or new_time_list is None:
            self.info.cast("Changes made to lyrics score / time index not saved.")
            return  # There were changes but not saved to SQL

        self.lyrics_time_list = new_time_list  # Do they need to be applied?
        self.lyrics_score = new_lyrics_score

        ''' Original play_top could have been closed and a new one opened '''
        self.play_init_lyrics()  # Rebuild lyrics and time indices from SQL

    # ==============================================================================
    #
    #       Music Location Tree class - Smaller sized functions
    #
    # ==============================================================================

    def set_artwork_colors(self):
        """ Get artwork for currently playing song.
            Apply artwork colors to panels, buttons and text. """

        if self.runSlideShow:
            if self.nextSlideIndex >= len(self.listSlideNames):
                self.nextSlideIndex = 0
            full_name = SLIDE_SHOW_DIR + os.sep + \
                self.listSlideNames[self.nextSlideIndex]
            self.play_original_art = Image.open(full_name)
            self.play_resized_art = self.play_original_art.resize(
                (self.art_width, self.art_height), Image.ANTIALIAS)
            self.play_current_song_art = ImageTk.PhotoImage(self.play_resized_art)
            self.nextSlideIndex += 1  # Always one past actual index
        else:
            self.play_current_song_art, self.play_resized_art, \
                self.play_original_art = \
                self.play_ctl.get_artwork(self.art_width, self.art_height)

        if self.play_current_song_art is None and ARTWORK_SUBSTITUTE:
            # print("Getting ARTWORK_SUBSTITUTE:", ARTWORK_SUBSTITUTE)
            self.play_current_song_art, self.play_resized_art, self.play_original_art = \
                storage_artwork(self.art_width, self.art_height)

        if self.play_current_song_art is None:
            self.play_no_art()  # Use "No Artwork" image

        # Get artwork color at 3,3 and calculate contrast color
        ''' July 3, 2023, play_frm_bg was self.play_frm_bg '''
        play_frm_bg = self.play_resized_art.getpixel((3, 3))
        hex_background = img.rgb_to_hex(play_frm_bg)
        dec_foreground = img.contrasting_rgb_color(play_frm_bg)
        hex_foreground = img.rgb_to_hex(dec_foreground)
        self.theme_bg = hex_background
        self.theme_fg = hex_foreground

        # Apply color codes to all play_top labels and buttons.
        self.play_frm.configure(bg=self.theme_bg)
        toolkit.config_all_labels(self.play_top, fg=self.theme_fg,
                                  bg=self.theme_bg)
        self.play_btn_frm.configure(bg=self.theme_bg)
        toolkit.config_all_buttons(self.play_top, fg=self.theme_bg,
                                   bg=self.theme_fg)

        # Volume slider
        self.ffplay_slider.config(troughcolor=self.theme_bg)

        # Apply color code to canvas rounded button and text
        #self.lyrics_panel_scroll.update_colors(hex_foreground, hex_background)
        self.lyrics_panel_scroll_a_m.update_colors(hex_foreground, hex_background)
        self.lyrics_panel_scroll_t_m.update_colors(hex_foreground, hex_background)
        self.lyrics_panel_scroll_m_a.update_colors(hex_foreground, hex_background)
        self.lyrics_panel_scroll_m_t.update_colors(hex_foreground, hex_background)
        self.lyrics_panel_hamburger.update_colors(hex_foreground, hex_background)

        # Apply color code to Lyrics
        self.lyrics_master_frm.config(bg=hex_background,
                                      highlightbackground=hex_foreground)
        self.lyrics_score_box.config(bg=hex_background, fg=hex_foreground,
                                     highlightbackground=hex_foreground)
        self.lyrics_score_box.tag_config('highlight', background=hex_foreground,
                                         foreground=hex_background)
        self.lyrics_score_box.vbar.config(troughcolor=hex_background,
                                          background="Gold")

        # List all widgets in lyrics panel
        #toolkit.list_widgets(self.lyrics_frm)  # uncomment for debugging

        self.play_top.update_idletasks()

        self.play_rotated_value = 0  # Set art rotation (spinning) degrees
        self.play_art_slide_count = 0  # Set art slide count
        self.play_art_fade_count = 0  # Set art fade in count

    def get_music_id_for_lib_tree_id(self, Id):
        """ Used when selecting treeview item to get SQL Music Table Row ID """
        full_path = self.real_path(int(Id))
        sql_path = full_path[len(PRUNED_DIR):]
        music_id = sql.music_id_for_song(sql_path)
        return music_id  # If music_id is 0, then OsFileName is not in SQL Music Table

    def real_path(self, ndx):
        """
            Convert '/<(No Artist>/<No Album>/song.m4a' to: '/song.m4a'
            Regular '/Artist/Album/song.m4a' isn't changed.

            July 3, 2023 - Use new self.real_paths instead of self.fake_paths.
                self.real_paths has <No Artist> stripped out
        """
        rpath = self.fake_paths[ndx]
        # Strip out /<No Artist> and /<No Album> strings added earlier
        rpath = rpath.replace(os.sep + g.NO_ARTIST_STR, '', 1)
        rpath = rpath.replace(os.sep + g.NO_ALBUM_STR, '', 1)
        return rpath

    def play_shuffle(self):
        """ Convert selections to list, shuffle, convert back to tuple
            Get confirmation because this cannot be undone. 'yes'

        """

        self.set_title_suffix()

        dialog = message.AskQuestion(
            self.play_top, thread=self.get_refresh_thread,
            title="Shuffle song order confirmation",
            text="\nThis will permanently change song order for:\n\n" +
                 " - " + self.title_suffix
        )
        if dialog.result != 'yes':
            return

        sql.hist_add_shuffle('remove', 'shuffle', self.saved_selections)
        Id = self.saved_selections[self.ndx]  # Save lib_top.tree song iid
        L = list(self.saved_selections)  # convert possible tuple to list
        shuffle(L)  # randomize list
        self.ndx = L.index(Id)  # restore old index
        self.saved_selections = L  # Reset iid list from lib_top.tree
        self.populate_chron_tree()  # Rebuild with new sort order
        # June 18, 2023 - Review history audit record. Probably overkill?
        #   Should call self.write_playlist_to_disk(override=selections_only)
        sql.hist_add_shuffle('edit', 'shuffle', self.saved_selections)
        if self.playlists.open_name:
            self.playlists.open_id_list = []
            for Id in self.saved_selections:
                music_id = self.get_music_id_for_lib_tree_id(Id)
                if music_id == 0:
                    toolkit.print_trace()
                    print("sql.music_id_for_song(insert_path[len(PRUNED_DIR):])")
                else:
                    self.playlists.open_id_list.append(music_id)
            self.playlists.save_playlist()

        self.info.cast("Shuffled Playlist: " + self.title_suffix + "with " +
                       str(len(self.saved_selections)) + " songs.", action='update')

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
        if self.play_top_is_active:  # Play window open?
            self.populate_chron_tree()  # Rebuild without removed song

    def play_insert(self, iid):
        """ Song has been checked. Insert it into sorted playlist.

            Convert selections to list, insert index, convert back to tuple
                #LIBRARY_SELECT_INSERT_PLAY_HERE = False  # Not supported
                LIBRARY_SELECT_INSERT_PLAY_NEXT = True
                #LIBRARY_SELECT_INSERT_PLAY_RANDOM = False  # Not supported
                #LIBRARY_SELECT_INSERT_PLAY_ORDER = False  # Not supported

            If an entire album or artist is inserted as anything but RANDOM
            then a new function to randomize those songs just inserted should
            be created.

            Only № is appearing in select column for newly inserted item
            Existing items do not have their № updated (incremented)
        """

        if not LIBRARY_SELECT_INSERT_PLAY_NEXT:
            print("LIBRARY_SELECT_INSERT_PLAY_NEXT must be true")
            return

        # Possible if nothing is playing and new library was loaded?
        if self.ndx > len(self.saved_selections) - 1:
            self.ndx = 0
            print('play_insert(): Unplanned resetting self.ndx = 0')

        # print('Inserting song iid:', iid, 'at:', self.ndx)
        curr_play_id = self.saved_selections[self.ndx]  # Get current song ID
        L = list(self.saved_selections)  # convert tkinter tuple to list
        L[self.ndx:self.ndx] = [iid]  # Insert song new ID here
        self.saved_selections = tuple(L)  # convert list back into tuple

        # Remove currently playing red tag
        tags = self.lib_tree.item(curr_play_id)['tags']
        if "play_sel" in tags:
            tags.remove("play_sel")
            self.lib_tree.item(curr_play_id, tags=tags)

        # Set treeview selection number
        number_str = play_padded_number(
            self.ndx + 1, len(str(len(self.saved_selections))))
        self.lib_tree.set(iid, "Selected", number_str)

        if self.play_top_is_active:  # Play window open?
            self.last_started = self.ndx  # For fast clicking 'Next'
            self.song_set_ndx(self.ndx)  # Start playing next song, ndx + 1
            # Remove red highlighting 'play_sel' of old song 'red'
            # If tagged as currently playing, remove it.
            self.populate_chron_tree()  # Rebuild with new song

    # noinspection PyUnusedLocal
    def play_close(self, *args):
        """ Close music player (Playlist) """
        # TODO: last_selections aren't being saved. When clicking play again
        #       shuffle order and last song index are lost.

        if not self.play_top_is_active:
            return  # play_close() already run.

        ''' Should not be able to call if self.fine_tune is active. '''
        if self.fine_tune and self.fine_tune.top_is_active:
            self.fine_tune.close()  # Prevents tons of exceptions.

        if self.tt and self.play_top:
            self.tt.close(self.play_top)  # Close tooltips under top level
        ''' July 9, 2023 - Doesn't matter if volume left turned down '''
        #if self.play_ctl.sink is not "":
        #    pav.set_volume(self.play_ctl.sink, 100)
        self.play_ctl.close()  # If playing song update last access time

        # Reverse filters so proper song index is saved
        if self.chron_filter:
            self.chron_reverse_filter()

        self.save_resume()  # playing/paused and seconds progress into song.
        self.save_chron_state()  # chronology tree state = "Show"/"Hide"
        self.save_hockey_state()  # Hockey buttons OR FF/Rewind buttons?
        self.save_open_states()  # This is saving for favorites & playlists?

        if self.play_hockey_active:
            set_tv_sound_levels(25, 100)
            # Restore TV sound

        self.play_top_is_active = False
        ext.kill_pid_running(self.vu_meter_pid)

        # Last known window position for playlist, saved to SQL
        last_playlist_geom = monitor.get_window_geom_string(
            self.play_top, leave_visible=False)
        monitor.save_window_geom('playlist', last_playlist_geom)

        # Save song playing seconds and paused/playing state to SQL

        #root.update()
        #root.after(50)  # Give events time to close down
        self.wrapup_song()  # kill song and collapse parent chevrons
        #        os.remove(TMP_CURR_SONG)           # Clean up /tmp directory
        if self.lib_top_is_active:
            self.restore_lib_buttons()  # Restore Library buttons to default

        self.play_top.destroy()
        self.play_top = None  # Extra Insurance
        self.pp_state = None

    def get_resume(self):
        """ Get state of playing / paused and seconds progress into song. """
        d = self.get_config_for_loc('resume')
        if d is None:
            return None

        if d['SourceDetail'] != str(self.ndx):
            if self.playlists.open_name:
                ''' self.ndx not initialized for playlists like last_location. '''
                self.ndx = int(d['SourceDetail'])
            else:
                print("mserve.py get_resume() Error 'SourceDetail' is:", d['SourceDetail'],
                      "but 'self.ndx' is:", self.ndx)
                print("Ignore this error if Playlist was changed in memory but not storage.")

        self.resume_state = d['SourceMaster']
        self.resume_song_secs = d['Seconds']
        return True

    def save_resume(self):
        """
            Save state of playing / paused and seconds progress into song.
        """
        Comments = "Last song playing/paused when play closed"
        self.save_config_for_loc(
            'resume', self.pp_state, str(self.ndx), self.current_song_path,
            Seconds=self.current_song_secs, Comments=Comments)

    def get_config_for_loc(self, Type):
        """ Wrapper Action is auto assigned as location or playlist number string
            TODO:   Same function in MusicLocationTree() class and tvVolume() class.
        """
        if NEW_LOCATION:
            return None

        if self.playlists.open_name:
            Action = self.playlists.open_code
        else:
            Action = lcs.open_code

        return sql.get_config(Type, Action)

    def save_config_for_loc(self, Type, SourceMaster="", SourceDetail="", Target="",
                            Size=0, Count=0, Seconds=0.0, Comments=""):
        """ Wrapper Action is auto assigned as location or playlist number string
            TODO:   Same function in MusicLocationTree() class and tvVolume() class.
        """
        if NEW_LOCATION:
            return None

        if self.playlists.open_name:
            Action = self.playlists.open_code
        else:
            Action = lcs.open_code

        sql.save_config(
            Type, Action, SourceMaster=SourceMaster, SourceDetail=SourceDetail,
            Target=Target, Size=Size, Count=Count, Seconds=Seconds,
            Comments=Comments)

    def get_chron_state(self):
        """ Get last saved state of Show/Hide Chronology button """
        d = self.get_config_for_loc('chron_state')
        if d is None:
            return None
        return d['SourceMaster']

    def save_chron_state(self):
        """ Save state of Show/Hide Chronology button """
        state = "Hide" if self.chron_is_hidden else "Show"
        Comments = "Chronology (playlist) 'Show' or 'Hide'"
        self.save_config_for_loc('chron_state', state, Comments=Comments)

    def get_hockey_state(self):
        """ Get saved state for Hockey TV Commercial Buttons and Volume """
        global TV_VOLUME  # mserve volume when TV commercial on air
        global TV_BREAK1, TV_BREAK2, TV_SOUND

        d = self.get_config_for_loc('hockey_state')
        if d is None:
            return False
        hockey_state = True if d['SourceMaster'] == "On" else False
        if 25 <= int(d['Size']) <= 100:
            TV_VOLUME = int(d['Size'])  # TV_VOLUME from 25 to 100 is valid
        else:
            print("mserve.py get_hockey_state() TV_VOLUME is invalid:",
                  int(d['Size']))

        # Initial versions didn't have these fields initialized
        if d['Count'] > 10:
            TV_BREAK1 = d['Count']
        if d['Seconds'] > 10:
            TV_BREAK2 = int(d['Seconds'])
        if d['SourceDetail'] != "":
            TV_SOUND = d['SourceDetail']

        # Hockey volume can now be changed. Note description must MATCH EXACTLY
        self.edit_menu.entryconfig("Volume During TV Commercials", state=tk.NORMAL)

        return hockey_state

    def save_hockey_state(self):
        """ Save state for Hockey TV Commercial Buttons and Volume """
        state = "On" if self.play_hockey_allowed else "Off"
        Comments = "Hockey TV Commercial Buttons used?"
        self.save_config_for_loc(
            'hockey_state', state, TV_SOUND, Size=TV_VOLUME, Count=TV_BREAK1,
            Seconds=float(TV_BREAK2), Comments=Comments)

    def get_open_states_to_list(self):
        """ Get list of artists and albums that are expanded (opened) """
        self.lib_tree_open_states = []

        d = self.get_config_for_loc('open_states')
        if d is None:
            return False

        ''' json.dumps converted list of tuples to list of lists, convert back '''
        open_states = json.loads(d['Target'])
        for open_state_list in open_states:
            open_state_tuple = tuple(open_state_list)
            self.lib_tree_open_states.append(open_state_tuple)

        return True

    def save_open_states(self):
        """ Save state of playing / paused and seconds progress into song. """
        open_states = self.make_open_states()
        Comments = "Artists and Albums that were expanded when play closed."
        self.save_config_for_loc(
            'open_states', Target=json.dumps(open_states), Comments=Comments)

    # ==============================================================================
    #
    #       Play song from Music Location Tree - middle 10 seconds or full song
    #
    # ==============================================================================

    def lib_tree_play(self, Id, sample='middle'):
        """ Sample middle 10 seconds or full song. Turn down other applications
            when starting and restore other application volume when ending. """
        ''' Build full song path '''
        path = self.real_path(int(Id))

        ''' FileControl() class for playing song. ltp = lib_tree_play '''
        self.ltp_ctl = FileControl(self.lib_top, self.info,
                                   close_callback=self.close_lib_tree_song)

        ''' Sanity check to see if file really has music inside '''
        self.ltp_ctl.new(path)  # Get metadata for music file
        if self.ltp_ctl.invalid_audio:
            print(self.ltp_ctl.metadata)
            self.corrupted_music_file(path)  # Non-blocking dialog box
            ''' Sanity check - Should .close() or .end() be used??? '''
            self.ltp_ctl.close()  # reset last access time to original value
            return

        self.update_sql_metadata(self.ltp_ctl)

        ''' Set start (beginning or middle) and duration (all or 10 seconds) '''
        if sample == 'middle':
            start = self.ltp_ctl.DurationSecs / 2 - 5.0
            limit = 10.0
        else:
            start = 0.0  # 'full' sample, start at beginning
            limit = self.ltp_ctl.DurationSecs

        if limit > self.ltp_ctl.DurationSecs:
            limit = self.ltp_ctl.DurationSecs
            start = 0.0

        if start + limit > self.ltp_ctl.DurationSecs:
            limit = self.ltp_ctl.DurationSecs
            start = 0.0

        ''' Start ffplay and get Linux PID and Pulseaudio Input Sink # '''
        self.ltp_ctl.start(start, limit, 1, 1, TMP_CURR_SAMPLE, False)
        if self.ltp_ctl.sink is not None:
            pav.set_volume(self.ltp_ctl.sink, 100.0)

        ''' Update lib_tree last access time display '''
        self.update_lib_tree_song(Id)

        ''' Create window '''
        self.ltp_top = tk.Toplevel()  # ltp = lib_tree_play
        self.ltp_top.minsize(g.WIN_MIN_WIDTH, g.WIN_MIN_HEIGHT)
        self.ltp_top_is_active = True
        self.ltp_paused_music = False

        if self.pp_state is "Playing":  # Is music playing?
            self.pp_toggle()  # Pause to play sample
            self.ltp_paused_music = True  # We will resume play later

        pav.fade_out_aliens(1)  # Turn down non-ffplay volumes to 0

        ''' Place Window top-left of parent window with g.PANEL_HGT padding '''
        xy = (self.lib_top.winfo_x() + g.PANEL_HGT,
              self.lib_top.winfo_y() + g.PANEL_HGT)
        self.ltp_top.minsize(width=g.BTN_WID * 10, height=g.PANEL_HGT * 4)
        self.ltp_top.geometry('+%d+%d' % (xy[0], xy[1]))
        if sample == 'middle':
            self.ltp_top.title("Play middle 10 seconds - mserve")
        else:
            self.ltp_top.title("Play whole song - mserve")
        self.ltp_top.configure(background="Gray")
        self.ltp_top.columnconfigure(0, weight=1)
        self.ltp_top.rowconfigure(0, weight=1)

        ''' Create master frame for artwork, song info and button '''
        sam_frm = tk.Frame(self.ltp_top, borderwidth=g.FRM_BRD_WID, relief=tk.RIDGE)
        sam_frm.grid(sticky=tk.NSEW)

        ''' Artwork image spanning 7 rows '''
        sample_art = img.make_image("Sample")
        sample_resized_art = sample_art.resize(
            (self.art_width, self.art_height), Image.ANTIALIAS)
        sample_display_art = ImageTk.PhotoImage(sample_resized_art)
        sample_art_label = tk.Label(sam_frm, image=sample_display_art,
                                    font=g.FONT)
        sample_art_label.grid(row=0, rowspan=7, column=0, sticky=tk.W)

        ''' Artist, Album, Song '''
        ''' TODO shared function with play_top non-blank metadata display '''
        tk.Label(sam_frm, text="Artist:\t" + self.ltp_ctl.Artist, padx=10,
                 font=g.FONT).grid(row=0, column=1, sticky=tk.W)
        # Truncate self.Album to 25 characters plus ...
        tk.Label(sam_frm, text="Album:\t" + self.ltp_ctl.Album, padx=10,
                 font=g.FONT).grid(row=1, column=1, sticky=tk.W)
        tk.Label(sam_frm, text="Title:\t" + self.ltp_ctl.Title, padx=10,
                 font=g.FONT).grid(row=2, column=1, sticky=tk.W)
        if self.ltp_ctl.Genre:
            tk.Label(sam_frm, text="Genre:\t" + self.ltp_ctl.Genre, padx=10,
                     font=g.FONT).grid(row=3, column=1, sticky=tk.W)
        if self.ltp_ctl.TrackNumber:
            tk.Label(sam_frm, text="Track:\t" + self.ltp_ctl.TrackNumber,
                     padx=10, font=g.FONT).grid(row=4, column=1, sticky=tk.W)
        if self.ltp_ctl.FirstDate:
            tk.Label(sam_frm, text="Date:\t" + self.ltp_ctl.FirstDate, padx=10,
                     font=g.FONT).grid(row=5, column=1, sticky=tk.W)
        if self.ltp_ctl.Duration:
            tk.Label(sam_frm, text="Duration:\t" + self.ltp_ctl.Duration,
                     padx=10, font=g.FONT).grid(row=6, column=1, sticky=tk.W)

        ''' Close Button ✘ '''
        tk.Button(sam_frm, text="✘ Close", width=g.BTN_WID2,
                  command=self.lib_tree_play_close) \
            .grid(row=8, column=0, padx=2, sticky=tk.W)
        self.ltp_top.bind("<Escape>", self.lib_tree_play_close)
        self.ltp_top.protocol("WM_DELETE_WINDOW", self.lib_tree_play_close)

        ''' Now mount real artwork '''
        artwork, resized_art, original_art = \
            self.ltp_ctl.get_artwork(self.art_width, self.art_height)
        if artwork is not None:
            sample_art_label.configure(image=artwork)

        ''' Loop until last second then exit during fade-out start '''
        self.ltp_top.update()
        while self.ltp_ctl.check_pid():
            self.ltp_top.update_idletasks()
            if not self.refresh_works(self.get_refresh_thread):
                break
            elapsed = self.ltp_ctl.elapsed()
            if elapsed - start + 1.0 > limit:
                #print("elapsed:", elapsed, " | start:", start, " | limit:", limit)
                break

        ''' Wrapup '''
        if self.ltp_top_is_active is False:
            return  # We are already closed

        self.lib_tree_play_close(normal=True)

    @staticmethod
    def refresh_works(get_refresh_thread):
        """ Refresh Tooltips, Pulse Audio fades and get user input
            Returns False when system shutting down
            TODO: Convert to lcs.fast_refresh(...)
        """
        thread = get_refresh_thread()
        if thread:
            thread()
            return True
        else:
            return False

    # noinspection PyUnusedLocal
    def lib_tree_play_close(self, normal=False, *args):  # *args required when lambda used
        """ Close self.ltp_top - Sample random song
            Called when song ends (normal=True) or with close button/Window 'X'
        """

        if self.ltp_top_is_active is False:
            return  # We are already closed

        if self.ltp_paused_music:  # Did we pause music player?
            self.pp_toggle()  # Resume playing

        if normal:
            ''' Ending as song is winding down '''
            pav.fade_in_aliens(1)  # Turn back non-ffplay volumes to original
            while self.ltp_ctl.check_pid():
                if not self.refresh_works(self.get_refresh_thread):
                    break
        else:
            ''' Demand close by 'X' window, <Escape> key or Close button '''
            pav.fade(self.ltp_ctl.sink, 100, 25, .33)  # Fast fade down
            now = time.time()
            while self.ltp_ctl.check_pid():
                if time.time() - now > .30:
                    break  # Drop down to close song politely
                if not self.refresh_works(self.get_refresh_thread):
                    break
            pav.fade_in_aliens(1)  # Turn back non-ffplay volumes to original

        self.ltp_ctl.close()  # Close FileControl(), reset ATIME
        # self.tt.close(self.ltp_top)  # No tooltips defined for ltp yet
        self.ltp_top_is_active = False

        if os.path.isfile(TMP_CURR_SAMPLE):
            os.remove(TMP_CURR_SAMPLE)  # Clean up /tmp directory

        if self.ltp_top:  # Ended already - Aug 16/23
            self.ltp_top.destroy()  # Close the window NOT self.lib_top !!!
        self.ltp_top = None  # Extra insurance
        self.ltp_top_is_active = False
        self.wrapup_lib_popup()  # Set color tags and counts

    def lib_tree_play_lift(self):
        """ Lift Music Location Tree to top of stacking order """
        self.ltp_top.focus_force()  # Get focus
        self.ltp_top.lift()  # Raise in stacking order

    # ==============================================================================
    #
    #       Playlist chronology
    #
    # ==============================================================================

    def build_chronology(self, _sbar_width=14):
        """ Chronology treeview List Box, Columns and Headings """

        ''' Create Chronology Treeview (chron_tree) and style Gold on Black '''
        style = ttk.Style(self.chron_frm)
        style.configure("chron.Treeview", background='Black',
                        fieldbackground='Black',
                        foreground='Gold')
        self.chron_tree = ttk.Treeview(self.chron_frm, show=('tree',),
                                       selectmode="none")
        self.chron_tree.configure(style="chron.Treeview")

        ''' Single column, when long, unfortunately can't scroll horizontally '''
        self.chron_tree.column("#0", minwidth=900, stretch=tk.YES)
        self.chron_tree.grid(row=0, column=0, sticky=tk.NSEW)

        ''' Chronology Treeview Vertical Scrollbar '''
        v_scroll = tk.Scrollbar(self.chron_frm, orient=tk.VERTICAL,
                                width=SCROLL_WIDTH,
                                command=self.chron_tree.yview)
        v_scroll.grid(row=0, column=1, sticky=tk.NS)
        self.chron_tree.configure(yscrollcommand=v_scroll.set)
        v_scroll.config(troughcolor='black', bg='gold')

        ''' Use tool_type="canvas_button" for entire treeview
            DISABLED - Leave comments here so mistake isn't repeated... 
        '''
        # Note this steals <Button-1>, <Motion> and <Leave> events from canvas
        # Which get stolen back in bindings further down
        #self.tt.add_tip(
        #    self.chron_tree, "Playlist Chronology\n" +
        #    "Right click on a song for action menus.",
        #    tool_type="canvas_button", anchor="nw")

        ''' Chronology treeview Colors .tag_configure() '''
        # Aug 23/23 - Chron Tree 'normal' tag no longer needed for colors
        #self.chron_tree.tag_configure('normal', background='Black',
        #                              foreground='Gold')
        self.chron_tree.tag_configure('chron_sel', background='ForestGreen',
                                      foreground='White')

        ''' Configure tag for row highlight '''
        self.chron_tree.tag_configure('highlight', background='LightBlue',
                                      foreground="Black")

        ''' Aug 23/23 - Configure tag for highlight of chron_sel line '''
        self.chron_tree.tag_configure('highlight_sel', background='Gold',
                                      foreground="Black")

        self.chron_tree.bind('<Motion>', self.chron_highlight_row)
        self.chron_tree.bind("<Leave>", self.chron_leave_row)

        ''' Mouse right-click for popup menu '''
        # Left click on works when clicked twice
        self.chron_tree.bind('<Button-3>', self.chron_tree_right_click)

        ''' Populate chronology treeview '''
        self.populate_chron_tree()

    def populate_chron_tree(self):
        """ Populate playlist chronology treeview listbox
        """

        ''' Delete all attached entries in current treeview '''
        self.chron_tree.delete(*self.chron_tree.get_children())

        for i, lib_tree_iid in enumerate(self.saved_selections):
            if not self.play_top_is_active:
                return  # Play window closed?

            ''' Add the #-song-artist line to chron listbox '''
            line, time_index = self.build_chron_line(i + 1, lib_tree_iid, True)
            song_iid = str(i + 1)  # song_number is 'i + 1'
            if time_index is None:
                values = ("no",)
            else:
                values = ("yes",)  # To find synchronized lyrics (time index)
            try:  # June 22, 2023 was 'iid = i + 1'
                self.chron_tree.insert('', 'end', iid=song_iid, text=line, values=values,
                                       tags=("normal",))
                self.chron_tree.tag_bind(song_iid, '<Motion>', self.chron_highlight_row)
            except tk.TclError:
                bad_msg = "mserve.py populate_chron_tree() bad line:"
                print(bad_msg, line)
                try:
                    self.chron_tree.insert('', 'end', iid=song_iid, text=bad_msg +
                                           " " + song_iid, tags=("normal",))
                    self.chron_tree.tag_bind(song_iid, '<Motion>', self.chron_highlight_row)
                except Exception as err:
                    print('mserve.py populate_chron_tree() insert failed with Error: %s' % (str(err)))
                    print()  # When it breaks tons of errors so separate into grouped msgs

        ''' Highlight current song

            Only songs that have been played once will have metadata for release
            date and duration. Otherwise a short line will be displayed

            TODO: Count songs with no metadata and advise with message:
            
            You can use "View", "SQL Music", "Missing artwork" to force metadata
            to be read for all songs in location. Then regular (full) lines are
            displayed in chronology treeview.    

        '''
        self.play_chron_highlight(self.ndx, True)  # True = use short line

    def chron_highlight_row(self, event):
        """ Cursor hovering over row highlights it in light blue """
        tree = event.widget
        item = tree.identify_row(event.y)
        if item is None:
            return  # Empty row

        if self.chron_last_row == item:
            return        # Get called dozens of times when still in same row

        self.chron_leave_row()  # If we left a row reset chron_tree background

        ''' Remove "normal" or "chron_sel" tag and replace with "highlight" '''
        tags = self.chron_tree.item(item)['tags']
        if "chron_sel" in tags:  # BRICS + AISUEE = BAR ICE ISSUE
            # Aug 23/23 - removing chron_sel gives pure highlight color
            toolkit.tv_tag_replace(self.chron_tree, item, "chron_sel", "highlight", strict=True)
            self.chron_last_tag_removed = "chron_sel"
            # Aug 23/23 - Try adding simply adding 'highlight' instead of replace
            # tag color stays chron_sel color and highlight color doesn't morph
            # Consider replacing chron_sel with play_sel and changing leave
            #toolkit.tv_tag_add(self.chron_tree, item, "highlight")
            #self.chron_last_tag_removed = "normal"  # Fake to keep chron_sel there
            pass  # Needs redesign.
        elif "normal" in tags:  # Aug 23/23 - No longer used for tree colors
            # Aug 22/23 - remove strict=True because already highlighted
            toolkit.tv_tag_replace(self.chron_tree, item, "normal", "highlight")
            self.chron_last_tag_removed = "normal"
        else:
            #print("chron_highlight_row() error tags:", tags, type(tags), "item:", item)
            return  # Get some false-positives, so don't bother printing

        self.chron_last_row = item

    # noinspection PyUnusedLocal
    def chron_leave_row(self, *args):
        """ Un-highlight row just left. *args because chron_close_popup() no parameters """
        if self.chron_last_row is None:
            return  # Nothing to remove. highlight_row() called just in case....

        tags = self.chron_tree.item(self.chron_last_row)['tags']
        # BUG tags is <type 'str'>
        if isinstance(tags, str):
            print("tv_tag_insert_first got tags type:", type(tags),
                  "item:", self.chron_last_row)
            return

        ''' Remove 'highlight' tag and replace with 'normal' or 'chron_sel' tag '''
        if not toolkit.tv_tag_replace(self.chron_tree, self.chron_last_row, "highlight",
                                      self.chron_last_tag_removed, strict=False):
            # "highlight" never existed, but need to add back old
            toolkit.tv_tag_add(self.chron_tree, self.chron_last_row,  # True = lots errors
                               self.chron_last_tag_removed, strict=False)
        self.chron_last_row = None
        self.chron_last_tag_removed = None

    def chron_tree_right_click(self, event):
        """ Popup menu:
                Play different song / Restart current song
                Kid3 to edit metadata / artwork
                Notes about song stored in SQL History Table
                Filter songs by artist, with time index, over 5 minutes
        """
        item = self.chron_tree.identify_row(event.y)

        if item is None:
            # self.info.cast("Cannot click on an empty row.")
            return  # Empty row, nothing to do

        ''' self.mouse_x, self.mouse_y for Kid3 '''
        self.mouse_x, self.mouse_y = event.x_root, event.y_root

        ''' After this function ends, tkinter invokes self.chron_leave_row()'''
        self.chron_last_row = None  # Trick chron_leave_row() to do nothing

        menu = tk.Menu(root, tearoff=0)
        menu.post(event.x_root, event.y_root)

        if self.ndx == (int(item) - 1):
            # Restart current song from beginning
            menu.add_command(label="Restart Song № " + item, font=g.FONT,
                             command=lambda: self.chron_tree_play_now(item))
        else:
            # Play different song in list / Sel. MB
            menu.add_command(label="Play Song № " + item, font=g.FONT,
                             command=lambda: self.chron_tree_play_now(item))
        menu.add_separator()
        if self.chron_filter is None:
            # Give three filter options
            menu.add_command(label="Filter Synchronized songs", font=g.FONT,
                             command=lambda: self.chron_apply_filter('time_index', item))
            menu.add_command(label="Filter not Synchronized", font=g.FONT,
                             command=lambda: self.chron_apply_filter('no_time_index', item))
            ''' July 18, 2023 - When Artist is "Compilations", narrow down to song artist '''
            menu.add_command(label="Filter by this Artist", font=g.FONT,
                             command=lambda: self.chron_apply_filter('artist_name', item))
            menu.add_command(label="Filter over 5 Minutes", font=g.FONT,
                             command=lambda: self.chron_apply_filter('over_5', item))
        else:
            # option to remove filters for full playlist
            menu.add_command(label="Full playlist unfiltered", font=g.FONT,
                             command=lambda: self.chron_reverse_filter())
        menu.add_separator()

        global KID3_INSTALLED, FM_INSTALLED
        KID3_INSTALLED = ext.check_command('kid3')
        FM_INSTALLED = ext.check_command(FM_COMMAND)

        if KID3_INSTALLED:
            menu.add_command(label="kid3", font=g.FONT,
                             command=lambda: self.chron_tree_kid3(item))
        if FM_INSTALLED:
            menu.add_command(label="Open " + FM_NAME, font=g.FONT,
                             command=lambda: self.chron_tree_fm(item))
        menu.add_separator()

        Id = item  # For copied code below
        os_filename = self.real_paths[int(Id)]
        # view_sql_metadata
        menu.add_command(label="View Raw Metadata", font=g.FONT,
                         command=lambda: self.view_metadata(
                             Id, os_filename=os_filename, top=self.play_top))
        menu.add_command(label="View SQL Metadata", font=g.FONT,
                         command=lambda: self.view_sql_music_id(
                             Id, self.play_ctl, top=self.play_top))

        menu.add_separator()

        menu.add_command(label="Ignore click", font=g.FONT,
                         command=lambda: self.close_chron_popup(menu, item))

        menu.tk_popup(event.x_root, event.y_root)
        menu.bind("<FocusOut>", lambda _: self.close_chron_popup(menu, item))
        # '_' prevents: TypeError: <lambda>() takes no arguments (1 given)

    def close_chron_popup(self, menu, item):
        """ Close the chronology try popup menu """
        self.chron_last_row = item  # Restore item stolen when menu built
        self.chron_leave_row()  # This was called when menu posted but item None
        menu.unpost()  # Remove popup menu

    def chron_tree_play_now(self, item):
        """ Play song highlighted in chronology treeview. """
        passed_ndx = int(item) - 1
        if self.ndx == passed_ndx:
            self.song_set_ndx('restart')  # Restart playing at beginning
        else:
            self.song_set_ndx(passed_ndx)  # Start playing selected song, ndx + 1

    def chron_apply_filter(self, option, item):
        """ Detach songs not matching filter from chron_tree. If less than two
            songs give message and reattach all songs.

            filtering playlist with:
                    1) Songs with time index (synchronized lyrics)
                    2) Songs for specific artist
                    3) Songs over 5 minutes long
                When filtered other songs are detached from treeview.
                In self.song_set_ndx(item - 1) when hitting detached song,
                    preform recursive call with same operation.

            :param option 'time_index', 'no_time_index', 'artist_name', 'over_5'
            :param item: item (iid) in chronology playlist
        """
        # Save song index we are about to change so we can restore later
        self.chron_org_ndx = self.ndx  # current playlist index number

        # Build list of filtered indices
        self.chron_attached = []
        if option is "artist_name":
            iid = self.saved_selections[int(item) - 1]  # Create treeview ID
            # Get artist in music library and build list of all checked songs
            album = self.lib_tree.parent(iid)
            artist = self.lib_tree.parent(album)  # Get the artist
            for album in self.lib_tree.get_children(artist):  # Read all albums
                for song in self.lib_tree.get_children(album):  # Read all songs
                    #if "checked" in self.lib_tree.item(song)['tags']:
                    # May 26, 2023 - "checked" brings up many irrelevant songs
                    if "song_sel" in self.lib_tree.item(song)['tags']:
                        values = self.lib_tree.item(song)['values']
                        pretty_no = values[2]  # E.G. "No.__21"
                        num = ""
                        for c in pretty_no:
                            if c.isdigit():
                                num = num + c  # E.G. Get "21"
                        # print("values:", values, "num:", num)
                        self.chron_attached.append(num)  # list of playlist number strings

        if option is "time_index":
            for i, iid in enumerate(self.chron_tree.get_children()):
                if iid.startswith("I"):
                    continue  # empty row
                time_index_flag = self.chron_tree.item(iid)['values'][0]
                #print("time_index_flag:", time_index_flag, "iid:", iid)
                if time_index_flag == 'yes':  # "is 'yes':" doesn't work !!!
                    self.chron_attached.append(iid)  # Playlist number strings
                    # print("synchronized:", time_index_flag, "iid:", iid)

        if option is "no_time_index":
            for i, iid in enumerate(self.chron_tree.get_children()):
                time_index_flag = self.chron_tree.item(iid)['values'][0]
                #print("time_index_flag:", time_index_flag, "iid:", iid)
                if time_index_flag == 'no':  # "is 'yes':" doesn't work !!!
                    self.chron_attached.append(iid)  # Playlist number strings
                    # print("synchronized:", time_index_flag, "iid:", iid)

        if option is "over_5":
            for i, iid in enumerate(self.chron_tree.get_children()):
                text = self.chron_tree.item(iid)['text']
                duration = text.split(" ")[-1]
                if ":" in duration:
                    minutes = duration.split(":")[0].strip()
                    if minutes.isdigit() and int(minutes) >= 5:
                        self.chron_attached.append(iid)  # Playlist number strings
                        # print("duration:", duration, "iid:", iid)

        kept_count = 0
        for i, iid in enumerate(self.chron_tree.get_children()):
            try:
                self.chron_attached.index(iid)
                # print("keep iid:", iid)
                kept_count += 1
            except ValueError:  # ValueError: '1' is not in list
                self.chron_tree.detach(iid)
                self.chron_detached.append(iid)

        #print("chron_apply_filter(self, option):", option)
        #print("kept_count:", kept_count)

        if kept_count < 2:
            #print("reattaching all items")
            self.chron_reverse_filter()
            quote = ("\n" +
                     "At least two matching songs are needed to filter playlist.\n" +
                     "Try again with different filter criteria.\n\n")

            message.ShowInfo(self.play_top, text=quote, align='left',
                             thread=self.get_refresh_thread,
                             title="Filter Playlist Failed - mserve")
            self.info.fact(quote)
            return  # TODO: Has this been tested? Use small playlist

        ''' Fix Synchronized sorted out of order. Artist is random order '''
        self.chron_attached.sort(key=int)
        #for i, attached in enumerate(self.chron_attached):
        #    print(i, attached)

        # Stop current song and remove highlighting in lib_tree
        if self.pp_state == "Playing":
            self.pp_toggle()  # Pause current song because it will be changing.
        self.wrapup_song()

        # Now reposition to first song on filtered playlist and highlight
        self.ndx = int(self.chron_attached[0]) - 1
        self.play_chron_highlight(self.ndx, True)  # True = use short line
        self.chron_tree.see(self.chron_attached[0])
        self.song_set_ndx(self.ndx)  # Force play and screen update

        #self.chron_tree.update_idletasks()

        self.chron_filter = option

    def chron_reverse_filter(self):
        """ Remove Playlist filter and restore old song index
        """
        for iid in self.chron_detached:
            # Order is messed up but reattach so they can be deleted
            self.chron_tree.reattach(iid, "", 0)
        self.chron_detached = []
        self.chron_attached = []
        self.wrapup_song()
        # Resume playing last song before filter applied
        self.ndx = self.chron_org_ndx
        self.chron_org_ndx = None  # Check not "None" when closing to restore
        self.chron_filter = None
        # List is built numbered backwards with kept items at bottom numbered forwards
        self.populate_chron_tree()  # Now totally rebuild from scratch
        self.song_set_ndx(self.ndx)  # Force play and screen update

    def chron_tree_kid3(self, item):
        """ Edit ID tags with kid3
            Id from song_selections[] vs. treeview Id """
        iid = self.saved_selections[int(item) - 1]  # Create treeview ID
        self.kid3_open(iid)

    def chron_tree_fm(self, item):
        """ Open File Manager
            Id from song_selections[] vs. treeview Id """
        iid = self.saved_selections[int(item) - 1]  # Create treeview ID
        self.fm_open(iid)

    def build_chron_line(self, playlist_no, lib_tree_iid, short_line):
        """ № (U+2116)  🎵  (1f3b5)  🎨  (1f3a8)  🖌  (1f58c)  🖸 (1f5b8)
            Big space  (2003)   “Tabular width”, the width of digits (2007)

            May 20, 2023 - short_line to be deprecated. Always make full line.
        """
        # BIG_SPACE = " "  # UTF-8 (2003) aka Em Space
        # DIGIT_SPACE = " "       # UTF-8 (2007)
        # NUMBER_PREFIX = "№ "    # UTF-8 (2116) + normal space
        TITLE_PREFIX = " 🎵 "  # big space + UTF-8 (1f3b5) + normal space
        ARTIST_PREFIX = " 🎨 "  # big space + UTF-8 (1f3a8) + normal space
        ALBUM_PREFIX = " 🖸 "  # big space + UTF-8 (1f5b8) + normal space
        # FUTURE SUPPORT:
        DATE_PREFIX = " 📅 "  # big space + UTF-8 (1f4c5) + normal space
        # CLOCK_PREFIX = " 🕐 "  # big space + UTF-8 (1f550) + normal space
        CLOCK_PREFIX = " 🕑 "  # big space + UTF-8 (1f551) + normal space
        TIME_PREFIX = " 🗲 "   # big space + Unicode Character “🗲” (U+1F5F2)."

        ''' Pad song number with spaces to line up song name evenly '''
        number_digits = len(str(len(self.saved_selections)))
        number_str = play_padded_number(playlist_no, number_digits)

        ''' Song title - remove track number and filename extension '''
        try:
            title = self.lib_tree.item(lib_tree_iid)['text']
        except tk.TclError:
            title = "Playlist Song not found: " + str(playlist_no)
            print(title)
            # TODO: Remove from playlist by posting "unchecked" to song.
        title = title.lstrip('0123456789.- ')  # Trim leading digit
        title = os.path.splitext(title)[0]  # Trim trailing ext
        line = number_str
        line = cat3(line, TITLE_PREFIX, title)

        ''' Extract Artist name from treeview parents '''
        try:
            album = self.lib_tree.parent(lib_tree_iid)
            artist = self.lib_tree.parent(album)
            line = cat3(line, ARTIST_PREFIX, self.lib_tree.item(artist)['text'])
            line = cat3(line, ALBUM_PREFIX, self.lib_tree.item(album)['text'])
        except tk.TclError as err:
            print("tk.TclError:", err)
            print("Bad playlist number must be unchecked but invisible.")
            print("Remove error checking in mserve.py populate_lib_tree().")
        ''' Build extended line using metadata for song in SQL Music Table '''
        try:
            path = self.real_path(int(lib_tree_iid))  # Remove <No Artist>, etc.
            sql_key = path[len(START_DIR):]  # Remove prefix from filename
        except tk.TclError:
            sql_key = "Crash/and/Burn Baby"

        ''' June 3, 2023 - Using new Blacklist '''
        d = sql.ofb.Select(sql_key)
        if d is None:
            return line, None  # No SQL Music Table Row exists, use short line

        try:
            line = number_str + TITLE_PREFIX + d['Title'].encode("utf8")
        except AttributeError:  # 'NoneType' object has no attribute 'encode'
            # When playing a new location no SQL library information exists
            return line, None  # No SQL Music Table Row exists, use short line
        line = line + ARTIST_PREFIX + d['Artist'].encode("utf8")
        line = line + ALBUM_PREFIX + d['Album'].encode("utf8")
        ''' July 18, 2023 '''
        if d['FirstDate'] is not None:
            line = line + DATE_PREFIX + d['FirstDate'].encode("utf8")
        '''
        if d['ReleaseDate'] is not None:
            line = line + DATE_PREFIX + d['ReleaseDate'].encode("utf8")
        '''
        line = line + CLOCK_PREFIX + d['Duration'].encode("utf8")
        # Replace "00:09:99" duration with "9:99" duration
        line = line.replace("00:0", "")
        line = line.replace("00:", "")  # Catch pink floyd Shine On 11 min song
        line = line.replace(CLOCK_PREFIX + "0", CLOCK_PREFIX)  # Catch 1-9 hour

        if d['LyricsTimeIndex'] is not None:
            line = line + TIME_PREFIX + " Synchronized"

        if short_line and playlist_no < 10:
            # We are called from create tree
            # print(playlist_no, song, path)
            pass
        if True is True:
            return line, d['LyricsTimeIndex']

    def play_chron_highlight(self, ndx, short_line):

        """ Remove 'chron_sel' tag applied to last song and apply 'normal' tag
            Append 'chron_sel' tag and remove 'normal' tag from selected.
            Rebuild extended line information if metadata unavailable previously.

            TODO: Review tags 'normal' and 'cron_sel' with chron_highlight_row
                  function debugged on June 27, 2023.
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
        if "normal" in tags:
            # Prevent ValueError: list.remove(x): x not in list
            tags.remove("normal")
        tags.append("chron_sel")
        self.chron_tree.item(Id, tags=tags)

        ''' When song starts playing, metadata is retrieved and SQL updated '''
        if short_line is False:  # REVIEW: probably not needed anymore
            lib_tree_iid = self.saved_selections[ndx]  # lib_tree iid
            ''' Add the #-song-artist line to chron listbox '''
            line, time_index = self.build_chron_line(int(Id), lib_tree_iid, False)
            self.chron_tree.item(Id, text=line)  # TODO: values for time_index

        ''' Position row to show previous 3, current and next 6 songs '''
        if self.chron_filter is None:
            count = len(self.saved_selections)
            position = ndx
        else:
            count = len(self.chron_attached)
            position = self.chron_attached.index(str(ndx+1))
        if position > 3:
            ThreeBefore = position - 3
        else:
            ThreeBefore = 0

        percent_view = float(ThreeBefore) / count
        # print('play_chron_highlight(self, ndx, short_line) Position:', Position)
        self.chron_tree.yview_moveto(percent_view)
        #root.update()

    def chron_toggle(self):
        """ Toggles chronology / "now playing" list below button bar

            Toggle chronology between "Hide" and "Show". When hidden
            lyrics scroll box positioned under song info + VU meters
            When shown Lyrics scroll box moved to right of VU meters.

        """
        if self.chron_is_hidden:  # Is playlist chronology currently hidden?
            self.chron_frm.grid()  # Restore hidden grid
            self.move_lyrics_right()  # Lyrics score right of VU meters
            self.chron_is_hidden = False  # Chronology no longer hidden
        else:  # Hide chronology (playlist)
            self.chron_frm.grid_remove()  # Hide grid but remember options
            self.move_lyrics_bottom()  # Lyrics score under VU meters
            self.chron_is_hidden = True  # Chronology is now hidden

        self.set_chron_button_text()
        ''' Toggle tooltip window position above/below buttons '''
        self.toggle_chron_tt_positions()

        self.play_chron_highlight(self.ndx, True)  # Required after shuffle songs
        self.chron_frm.update_idletasks()

    def set_chron_button_text(self):
        """ Called by toggle_chron(), long_running_process() and begin play """
        text, text2 = self.get_chron_button_text()
        self.chron_button['text'] = text
        self.tt.set_text(self.chron_button, text2)

    def get_chron_button_text(self):
        """ Called by set_chron_button_text() and build_play_btn_frm() """
        if self.chron_is_hidden:
            text = "🖸 Show Chronology"
            text2 = "Show last three songs played,\n" + \
                    "current song, and future six\n" + \
                    "songs in playlist."
        else:  # Hide chronology (playlist)
            text = "🖸 Hide Chronology"
            text2 = "Hide the chronology playlist below\n" + \
                    "double the size of spinning artwork."

        return text, text2

    def toggle_chron_tt_positions(self):
        """ Called by toggle_chron(), and build_play_btn_frm()) """
        self.tt.toggle_position(self.close_button)
        self.tt.toggle_position(self.shuffle_button)
        self.tt.toggle_position(self.pp_button)
        self.tt.toggle_position(self.prev_button)
        self.tt.toggle_position(self.next_button)
        if self.play_hockey_allowed:
            self.tt.toggle_position(self.com_button)
            self.tt.toggle_position(self.int_button)
        else:
            self.tt.toggle_position(self.rew_button)
            self.tt.toggle_position(self.ff_button)
        self.tt.toggle_position(self.chron_button)


# ==============================================================================
#
#       FineTune class - Fine-tune time index / Synchronize Lyrics
#
# ==============================================================================
class FineTune:
    """ Fine-tune time index (Synchronize Time Index to Lyrics)

        Startup check to ensure at least 80% of lines are already
        synchronized. If not, use message.ShowInfo with basic sync
        instructions. This is already done.

        Highlight current line based on elapsed time given by caller.

        NOTES: Mainline code converted to class in July 3, 2023.
               Merge lines and Insert line hasn't been tested.
               Save under various circumstances hasn't been tested.
               More testing to synchronize lines and document.

    """

    def __init__(self, play_top, tt, info, play_ctl, work_sql_key,
                 work_lyrics_score, work_time_list, play_original_art,
                 theme_fg, theme_bg, startup_elapsed,
                 get_refresh_thread, fine_tune_closed_callback):
        """
        """
        ''' self-ize parameters - Valid when called, can change moments later '''
        self.play_top = play_top  # For window geometry on start. unstable after
        self.tt = tt
        self.info = info
        self.play_ctl = play_ctl  # Valid on startup. Unstable after
        self.work_sql_key = work_sql_key
        self.work_lyrics_score = work_lyrics_score
        self.work_time_list = list(work_time_list)  # original can change later
        self.play_original_art = play_original_art
        self.theme_fg = theme_fg
        self.theme_bg = theme_bg
        # startup_elapsed must be passed because music paused in which case
        # self.play_ctl.elapsed() will not return valid elapsed time played.
        self.get_refresh_thread = get_refresh_thread  # Threads can change later
        self.fine_tune_closed_callback = fine_tune_closed_callback

        ''' Parent play_ctl() class variables can disappear moments later '''

        # Note: build_top_level() now merged here. Some self.variables can be
        #       made local variables

        self.play_Title = self.play_ctl.Title
        self.play_Artist = self.play_ctl.Artist
        self.play_Album = self.play_ctl.Album
        self.play_DurationSecs = self.play_ctl.DurationSecs
        self.play_path = self.play_ctl.path
        self.play_sink = self.play_ctl.sink  # play_top can close and reopen

        ''' Class Variables '''
        self.top_is_active = None   # When false, signal to end
        self.top = None  # Toplevel window. Bugs lift() and force_focus() ???
        self.song_art = None  # Converted artwork image in frame 1
        self.tree = None  # CheckboxTreeview in frame2
        self.tree_last_row = None  # For highlighting row under cursor
        self.tree_last_tag_removed = None
        self.check2 = None  # Duplicated treeview checkboxes
        self.btn_bar_frm = None  # Button bar built on the fly in frame 3
        self.pp_state = None  # Sample all is 'Playing' or 'Paused'
        self.pp_button = None  # text=self.pp_pause_text
        self.ffplay_is_running = None  # Already playing and syncing?
        self.sync_changed_score = None   # Was lyrics score changed?

        self.line_count_var = None  # Display # of lines in lyrics
        self.lyrics_line_count = self.work_lyrics_score.count("\n") + 1
        self.new_time_list = []  # As time list is edited these
        self.new_durations_list = []  # lists override synchronizing
        self.first_checked = None  # First check box to synchronize
        self.last_checked = None  # Last check box to synchronize
        self.curr_line_highlight = None  # When changes move bar
        self.curr_line_no = None  # Required for rewind buttons
        self.start_sec = None  # Offset to start syncing at
        self.limit_sec = None  # Duration to sync. 0 = quit
        self.elapsed_secs = None  # get with time_ctl.elapsed()
        self.old_sinks = None  # sink_master() - list of tuples

        self.time_ctl = None
        self.pp_play_text = "▶  Play"
        self.pp_pause_text = "❚❚ Pause"

        # 80% threshold required. Instructions window mounted if not reached.
        # If class, work_ are passed in tuple and unpacked. Returned as new_
        if not self.startup_check():
            self.close()

        # Set flags for child processes running
        self.ffplay_is_running = False  # Currently, playing and syncing?
        self.sync_changed_score = False  # For warning messages

        self.info.cast("Begin Fine-Tune Time Indexes")

        ''' Create window '''
        self.top = tk.Toplevel()
        self.top.minsize(g.WIN_MIN_WIDTH, g.WIN_MIN_HEIGHT)
        self.top_is_active = True

        ''' Set program icon in taskbar '''
        # Not sure why other windows don't need below?
        img.taskbar_icon(self.top, 64, 'white', 'lightskyblue', 'black')

        ''' Place Window top-left of play list window 
            TODO: Give own window with save position '''
        geometry = self.play_top.winfo_geometry()
        self.top.geometry(geometry)
        self.top.title("Fine-tune time index - mserve")
        self.top.configure(background=self.theme_bg)
        self.top.columnconfigure(0, weight=1)
        self.top.rowconfigure(1, weight=1)

        ''' frame1 - Song information 
            TODO: Looks plain. Add image from song maybe? '''
        frame1 = tk.Frame(self.top, background=self.theme_bg,
                          borderwidth=0)
        frame1.grid(row=0, column=0, sticky=tk.EW)
        frame1.grid_columnconfigure(0, weight=1)
        frame1.grid_columnconfigure(1, weight=1)
        frame1.grid_columnconfigure(2, weight=1)

        ''' Artwork Thumbnail '''
        # original_art  Haven't checked when paused or no artwork
        resized_art = self.play_original_art.resize(
            (120, 120), Image.ANTIALIAS)
        # Must need self. prefix or garbage collector removes it.
        self.song_art = ImageTk.PhotoImage(resized_art)
        art_label = tk.Label(frame1, borderwidth=0, image=self.song_art,
                             font=g.FONT)
        art_label.grid(row=0, rowspan=3, column=0, padx=5, pady=5, sticky=tk.W)

        ''' Song name and Duration Seconds '''
        # foreground=self.theme_fg, \
        ms_font = (None, MED_FONT)
        tk.Label(frame1, text="Title: " + self.play_Title,
                 font=ms_font, padx=10) \
            .grid(row=0, column=1, sticky=tk.W)
        tk.Label(frame1, text="Total seconds: " + str(self.play_DurationSecs),
                 font=ms_font, padx=10) \
            .grid(row=0, column=2, sticky=tk.W)

        tk.Label(frame1, text="Artist: " + self.play_Artist,
                 font=ms_font, padx=10) \
            .grid(row=1, column=1, sticky=tk.W)
        self.line_count_var = tk.StringVar()
        self.line_count_var.set("Line count: " + str(self.lyrics_line_count))
        tk.Label(frame1, textvariable=self.line_count_var,
                 font=ms_font, padx=10) \
            .grid(row=1, column=2, sticky=tk.W)

        tk.Label(frame1, text="Album: " + self.play_Album,
                 font=ms_font, padx=10) \
            .grid(row=2, column=1, sticky=tk.W)

        ''' frame2 - Treeview Listbox'''
        frame2 = tk.Frame(self.top, background=self.theme_bg,
                          borderwidth=g.FRM_BRD_WID, relief=tk.RIDGE)
        tk.Grid.rowconfigure(frame2, 1, weight=1)
        tk.Grid.columnconfigure(frame2, 0, weight=1)
        frame2.grid_columnconfigure(0, weight=1)
        frame2.grid_rowconfigure(1, weight=1)
        frame2.grid(row=1, column=0, sticky=tk.NSEW)

        ''' Treeview List Box, Columns and Headings 
            width and height temporary until treeview expands them
        '''
        width = int(geometry.split('x')[0])  # geometry from play_top
        width -= 680  # Not sure why subtracting 680?
        if width < 200:
            width = 200
        row_height = int(MON_FONTSIZE * 2.2)

        # From: https://stackoverflow.com/a/43834987/6929343
        style = ttk.Style(frame2)
        style.configure("syn.Treeview", background='Black',
                        fieldbackground='Black',
                        foreground='Gold')

        self.tree = CheckboxTreeview(
            frame2, columns=("new", "lyrics", "old_dur", "new_dur"),
            selectmode="none", show=('tree', 'headings',))
        self.tree.configure(style="syn.Treeview")

        self.tree.column("#0", width=200, anchor='w', stretch=tk.NO)
        self.tree.heading("#0", text="Time index")
        self.tree.column("new", width=150, stretch=tk.NO)
        self.tree.heading("new", text="New Time")
        self.tree.column("lyrics", width=width, stretch=tk.YES)
        self.tree.heading("lyrics", text="Lyrics")
        self.tree.column("old_dur", width=150, stretch=tk.NO)
        self.tree.heading("old_dur", text="Duration")
        self.tree.column("new_dur", width=150, stretch=tk.NO)
        self.tree.heading("new_dur", text="New Dur.")
        self.tree.grid(row=1, column=0, sticky=tk.NSEW)

        # self.tree.bind('<ButtonRelease-1>', self.tree_select)

        ''' Create images for checked, unchecked and tristate '''
        # Don't use self.checkboxes list as GC destroys others with that name
        self.check2 = img.make_checkboxes(row_height - 6, 'Gold', 'Black',
                                          'DodgerBlue')  # SkyBlue3 not in Pillow
        self.tree.tag_configure("unchecked", image=self.check2[0])
        self.tree.tag_configure("tristate", image=self.check2[1])
        self.tree.tag_configure("checked", image=self.check2[2])

        ''' Create Treeview item list '''
        self.populate_treeview()

        ''' sync lyrics Treeview Scrollbars '''
        # Create a vertical scrollbar linked to the frame.
        v_scroll = tk.Scrollbar(frame2, orient=tk.VERTICAL, width=SCROLL_WIDTH,
                                command=self.tree.yview)
        v_scroll.grid(row=1, column=1, sticky=tk.NS)
        self.tree.configure(yscrollcommand=v_scroll.set)
        v_scroll.config(troughcolor='black', bg='gold')

        ''' sync lyrics treeview Colors '''
        self.tree.tag_configure('normal', background='Black',
                                foreground='Gold')
        self.tree.tag_configure('sync_sel', background='grey18',
                                foreground='LightYellow')

        ''' Configure tag for row highlight '''
        self.tree.tag_configure('highlight', background='LightBlue',
                                foreground="Black")

        self.tree.bind('<Motion>', self.tree_highlight_row)
        self.tree.bind("<Leave>", self.tree_leave_row)

        '''   B U T T O N   B A R   F R A M E   '''
        self.btn_bar_frm = tk.Frame(self.top, relief=tk.GROOVE,
                                    background=self.theme_bg, borderwidth=g.FRM_BRD_WID)
        self.btn_bar_frm.grid(row=2, column=0, padx=2, pady=2, sticky=tk.W)
        self.build_btn_bar_frm()  # Defaults to 'top' for top main window

        ''' Set default checkbox for currently playing line in caller '''
        for i, start_time in enumerate(self.work_time_list):
            if start_time > startup_elapsed:
                # This line starts later than current time so use last (i).
                item = i - 1
                item = item if item > 0 else 1
                tags = self.tree.item(str(item))['tags']
                tags.remove("unchecked")
                tags.append("checked")
                self.tree.item(str(item), tags=tags)
                self.tree.see(str(item))
                break

        self.time_ctl = FileControl(self.top, self.info, silent=True)
        self.time_ctl.new(self.play_path)

    def tree_highlight_row(self, event):
        """ Cursor hovering over row highlights it in light blue """
        tree = event.widget
        item = tree.identify_row(event.y)
        if item is None:
            return  # Empty row

        if self.tree_last_row == item:
            return        # Get called dozens of times when still in same row

        self.tree_leave_row()  # If we left a row reset tree background

        ''' Remove "normal" or "sync_sel" tag and replace with "highlight" '''
        tags = self.tree.item(item)['tags']
        if "sync_sel" in tags:
            toolkit.tv_tag_replace(self.tree, item, "sync_sel", "highlight", strict=True)
            self.tree_last_tag_removed = "sync_sel"
        elif "normal" in tags:
            toolkit.tv_tag_replace(self.tree, item, "normal", "highlight", strict=True)
            self.tree_last_tag_removed = "normal"
        else:
            #print("tree_highlight_row() error tags:", tags, type(tags), "item:", item)
            return  # Get some false-positives, so don't bother printing

        self.tree_last_row = item

    # noinspection PyUnusedLocal
    def tree_leave_row(self, *args):
        """ Un-highlight row just left. *args because tree_close_popup() no parameters """
        if self.tree_last_row is None:
            return  # Nothing to remove. highlight_row() called just in case....

        tags = self.tree.item(self.tree_last_row)['tags']
        # BUG tags is <type 'str'>
        if isinstance(tags, str):
            print("tv_tag_insert_first got tags type:", type(tags),
                  "item:", self.tree_last_row)
            return

        ''' Remove 'highlight' tag and replace with 'normal' or 'sync_sel' tag '''
        if not toolkit.tv_tag_replace(self.tree, self.tree_last_row, "highlight",
                                      self.tree_last_tag_removed, strict=False):
            # "highlight" never existed, but need to add back old
            toolkit.tv_tag_add(self.tree, self.tree_last_row,  # True = lots errors
                               self.tree_last_tag_removed, strict=False)
        self.tree_last_row = None
        self.tree_last_tag_removed = None

    def build_btn_bar_frm(self, level='top'):
        """ Build buttons for top_level, begin sync and sample all """
        if not self.top_is_active:
            return
        if self.tt and self.btn_bar_frm:
            self.tt.close(self.btn_bar_frm)  # Remove old tooltip buttons in play_btn frame
        self.btn_bar_frm.grid_forget()
        self.btn_bar_frm.destroy()
        self.btn_bar_frm = None  # Extra insurance
        self.top.unbind("<Escape>")
        # Unbinds for all functions? https://bugs.python.org/issue31485

        ''' Frame for Buttons '''
        self.btn_bar_frm = tk.Frame(self.top, bg="LightGrey",
                                    borderwidth=g.FRM_BRD_WID, relief=tk.GROOVE)
        self.btn_bar_frm.grid(row=3, column=0, sticky=tk.NSEW)

        ''' Define three different button bars '''
        if level == 'top':
            button_list = ["Close", "Begin", "Delete", "Sample",
                           "Merge", "Insert", "Save", "HelpT"]
        elif level == 'sync':
            button_list = ["Sync", "DoneB", "RewindB", "HelpB"]
        elif level == 'sample_all':
            button_list = ["SampleS", "DoneS", "PP", "RewindS", "HelpS"]
        else:
            self.info.cast("Programming error bad button level: " + level)
            return

        ms_font = (None, MED_FONT)

        help_text = "Open new window in default web browser for\n"
        help_text += "videos and explanations on using this screen.\n"
        help_text += "https://www.pippim.com/programs/mserve.html#\n"

        for col, name in enumerate(button_list):
            if name == "Close":
                '''  FORMERLY: self.top_buttons '''
                ''' ✘ Close Button - Cancels changes '''
                # leading space when text begins with utf-8 symbol centers text better?
                close = tk.Button(self.btn_bar_frm, text=" ✘ Close", font=ms_font,
                                  width=g.BTN_WID2 - 4, command=self.close)
                close.grid(row=0, column=col, padx=2, sticky=tk.W)
                # Disable for now because Child process like "self.sync()" should
                # be trapping ESCAPE -- How do you unbind <Escape>
                self.top.bind("<Escape>", self.close)
                self.top.protocol("WM_DELETE_WINDOW", self.close)
                self.tt.add_tip(close, "Close Fine-Tune Time Index window.\n" +
                                "Abandon all changes.", anchor="nw")

            elif name == "Begin":
                ''' ▶  Begin Button - Synchronize selected lines '''
                begin = tk.Button(self.btn_bar_frm, text=" ▶ Begin sync", font=ms_font,
                                  width=g.BTN_WID2, command=self.sync)
                begin.grid(row=0, column=col)
                self.tt.add_tip(
                    begin, "First check boxes for first and last line.\n" +
                           "Then click this button to synchronize.", anchor="nw")

            elif name == "Delete":
                ''' 😒 Delete - 😒 (u+1f612) - Delete all '''
                delete = tk.Button(self.btn_bar_frm, text=" 😒 Delete all", font=ms_font,
                                   width=g.BTN_WID2, command=self.delete_all)
                delete.grid(row=0, column=col)
                self.tt.add_tip(
                    delete, "When time indices are hopelessly wrong,\n" +
                            "click this button to delete them all.", anchor="nw")

            elif name == "Sample":
                ''' 🎵  Sample all - Sample all show library '''
                sample = tk.Button(self.btn_bar_frm, text=" 🎵 Sample all", font=ms_font,
                                   width=g.BTN_WID2, command=self.sample_all)
                sample.grid(row=0, column=col)
                self.tt.add_tip(
                    sample, "Click to sample the first second of every line.",
                    anchor="nw")

            elif name == "Merge":
                ''' - Merge lines - Merge two lines together '''
                merge = tk.Button(self.btn_bar_frm, text="- Merge lines", font=ms_font,
                                  width=g.BTN_WID2 - 2, command=self.merge_lines)
                merge.grid(row=0, column=col)
                self.tt.add_tip(
                    merge, "First check two or more lines. Then\n" +
                           "click this button to merge together.", anchor="nw")

            elif name == "Insert":
                ''' + Insert line - Insert line line eg [chorus] or [bridge] '''
                insert = tk.Button(self.btn_bar_frm, text="+ Insert line", font=ms_font,
                                   width=g.BTN_WID - 2, command=self.insert_line)
                insert.grid(row=0, column=col)
                self.tt.add_tip(
                    insert, "First check line to insert before. Then\n" +
                            "click this button to insert a new line.", anchor="ne")

            elif name == "Save":
                ''' 💾  Save - Save lyrics (may be merged) and time indices '''
                save = tk.Button(self.btn_bar_frm, text=" 💾 Save", font=ms_font,
                                 width=g.BTN_WID2 - 4, command=self.save_changes)
                save.grid(row=0, column=col)
                self.tt.add_tip(
                    save, "Save time indices and close\n" +
                          "this fine-tune index window.", anchor="ne")

            elif name == "HelpT":
                ''' ⧉ Help - Videos and explanations on pippim.com '''
                help = tk.Button(self.btn_bar_frm, text="⧉ Help", width=g.BTN_WID2 - 4,
                                 font=ms_font, command=lambda: g.web_help("HelpT"))
                help.grid(row=0, column=col)
                self.tt.add_tip(help, help_text, anchor="ne")

            elif name == "Sync":
                ''' "Sync in progress" label FORMERLY: self.sync_buttons '''
                tk.Label(self.btn_bar_frm, text="Sync in progress...",
                         font=ms_font, padx=10) \
                    .grid(row=0, column=col, sticky=tk.W)

            elif name == "DoneB":
                ''' Done Button - Saves work and returns to parent '''
                begin_done = tk.Button(self.btn_bar_frm, text="Done", font=ms_font,
                                       width=g.BTN_WID2 - 6, command=self.sync_done)
                begin_done.grid(row=0, column=col, padx=2, sticky=tk.W)
                self.tt.add_tip(
                    begin_done, "Click this button to skip\n" +
                                "synchronizing remaining lines.", anchor="nw")

            elif name == "RewindB":
                ''' "Rewind 5 seconds" Button - Synchronize selected lines '''
                begin_rewind = tk.Button(self.btn_bar_frm, text="Rewind 5 seconds",
                                         width=g.BTN_WID2 + 2, font=ms_font,
                                         command=self.sync_rewind)
                begin_rewind.grid(row=0, column=col, padx=2)
                self.tt.add_tip(
                    begin_rewind, "Click this button to stop play,\n" +
                                  "go back 5 seconds and resume play.", anchor="nw")

            elif name == "HelpB":
                ''' ⧉ Help - Videos and explanations on pippim.com '''
                help = tk.Button(self.btn_bar_frm, text="⧉ Help", width=g.BTN_WID2-4,
                                 font=ms_font, command=lambda: g.web_help("HelpB"))
                help.grid(row=0, column=col)
                self.tt.add_tip(help, help_text, anchor="nw")

            elif name == "SampleS":
                ''' "Sample in progress" label  FORMERLY: self.sync_sample_buttons '''
                tk.Label(self.btn_bar_frm, text="Sample all in progress...",
                         font=ms_font, padx=10) \
                    .grid(row=0, column=col, sticky=tk.W)

            elif name == "DoneS":
                ''' Done Button - Saves work and returns to parent
                    TODO: Rename to "Apply changes" ? '''
                sample_done = tk.Button(self.btn_bar_frm, text="Done",
                                        width=g.BTN_WID2 - 6, font=ms_font,
                                        command=self.sample_done)
                sample_done.grid(row=0, column=col, padx=2, sticky=tk.W)
                self.tt.add_tip(sample_done, "Click this button to skip\n" +
                                "sampling remaining lines.", anchor="nw")

            elif name == "PP":
                ''' Pause/Play Button - Toggles state '''
                self.pp_state = 'Playing'
                self.pp_button = \
                    tk.Button(self.btn_bar_frm, text=self.pp_pause_text,
                              width=g.BTN_WID2 - 4,  font=ms_font,
                              command=self.toggle_play)
                self.pp_button.grid(row=0, column=col, padx=2, sticky=tk.W)
                self.tt.add_tip(
                    self.pp_button, "Click this button to toggle\n" +
                    "pause / playing of music.", anchor="nw")

            elif name == "RewindS":
                ''' Rewind 5 seconds Button '''
                sample_rewind = tk.Button(self.btn_bar_frm, text="Rewind 5 seconds",
                                          width=g.BTN_WID2 + 2, font=ms_font,
                                          command=self.sample_rewind)
                sample_rewind.grid(row=0, column=3, padx=2)
                self.tt.add_tip(
                    sample_rewind, "Click this button to stop play,\n" +
                    "go back 5 seconds and resume play.", anchor="ne")

            elif name == "HelpS":
                ''' ⧉ Help - Videos and explanations on pippim.com '''
                help = tk.Button(self.btn_bar_frm, text="⧉ Help", width=g.BTN_WID2 - 4,
                                 font=ms_font,
                                 command=lambda: g.web_help("HelpS"))
                help.grid(row=0, column=col)
                self.tt.add_tip(help, help_text, anchor="ne")

            else:
                self.info.cast("Oops unknown button name: " + name)

        self.btn_bar_frm.configure(bg=self.theme_bg)  # Why this and next??
        toolkit.config_all_buttons(self.top, fg=self.theme_bg,
                                   bg=self.theme_fg)
        self.top.update_idletasks()

    def populate_treeview(self):
        """ Called from init and tree_select() """
        start_time = 0.0
        duration = 0.0
        last_time = 0.0
        time_override_count = 0  # >= 1 negative durations?
        last_ndx = len(self.work_time_list) - 1
        for line_ndx, line in enumerate(self.work_lyrics_score.split('\n')):
            line = line.strip('\r')  # Microsoft Windows
            # time_override = False  # Adjusted negative durations?

            ''' Calculate line start time index and duration '''
            if line_ndx <= last_ndx:
                start_time = self.work_time_list[line_ndx]
                duration = self.play_DurationSecs - self.work_time_list[line_ndx]
            if line_ndx + 1 <= last_ndx:
                duration = self.work_time_list[line_ndx + 1] - \
                           self.work_time_list[line_ndx]

            # Override if this line number > total lines indexed
            if line_ndx > last_ndx:
                # print('lyrics score line_ndx:', line_ndx, \
                #       '> tine index last_ndx:', last_ndx)
                start_time = float(self.play_DurationSecs)
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
            ftime = play_padded_number(ftime, 8)
            fduration = play_padded_number(fduration, 7, prefix="")
            # FUTURE if time_override: insert with new duration else:
            self.tree.insert('', 'end', iid=str(line_ndx + 1), text=ftime,
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
                parent=self.top)

    def sync(self):
        """ Play music and synchronize time for checked treeview lines.

            Fill in all blank check boxes between first and last checked.
            If nothing was checked error is displayed, and we return.
            Set start time 4 seconds before first checked.
            Set end time to start of line following last checked.
            Call self.build_btn_bar_frm('sync')

        """
        if self.ffplay_is_running:
            self.info.cast('self.ffplay_is_running:')
            return  # Already playing

        # Fill first and last checked boxes. At least one line must be checked.
        self.first_checked, self.last_checked = self.check_all_boxes()
        if self.first_checked is None:  # Error message already
            return  # displayed so return.

        self.build_btn_bar_frm('sync')
        self.curr_line_highlight = 0  # When changes move bar
        self.ffplay_is_running = True  # We are now playing
        self.sync_play()  # Will turn down volume and calculate start
        self.sync_watch()  # Refresh threads in loop until done
        self.sync_done()

    def sync_play(self):
        """ Start ffplay and get Linux PID and Pulseaudio Input Sink #

            TODO: self.start_sec, self.first_checked and self.last_checked may be
                  greater that len(self.new_time_list)

        """

        # Give 2.5-second playing countdown before line to sync
        self.start_sec = self.new_time_list[self.first_checked - 1] - 2.5
        self.start_sec = 0.0 if self.start_sec < 0.0 else self.start_sec

        # July 13, 2023 - was checking < self.lyrics_line_count
        if self.last_checked + 1 < len(self.new_time_list):
            # Grab start time of line after last line to set duration+2 secs
            self.limit_sec = \
                self.new_time_list[self.last_checked] - self.start_sec + 2.0
        else:
            # TODO Append to self.new_time_list and share duration to lines
            self.limit_sec = self.play_DurationSecs - self.start_sec

        self.time_ctl.start(self.start_sec, self.limit_sec,
                            .5, .5, TMP_CURR_SYNC, True)
        pav.set_volume(self.time_ctl.sink, 100)  # Restore volume
        self.time_ctl.cont()
        pav.fade_out_aliens(.5)

    def sync_watch(self):
        """
            Used by Begin Sync - Synchronize each line as it is played
            Allow left click to select line and set new time index
            With no overrides, lines are auto highlighted based on time index
            Exit loop when there is 1 second left to play
        """
        self.elapsed_secs = 0.0
        self.curr_line_highlight = ""
        self.tree.bind("<ButtonRelease-1>", self.tree_select)
        while self.time_ctl.check_pid():
            if not self.top_is_active:
                return  # Window closed?
            self.elapsed_secs = self.time_ctl.elapsed()
            if self.elapsed_secs + .5 > self.start_sec + self.limit_sec:
                # Leave .5 second early so there is time to fade up others
                break
            self.set_highlight()  # Check highlight pos.
            # BUG: toggles highlight between previous and current

            if not self.refresh_works(self.get_refresh_thread):
                break

    @staticmethod
    def refresh_works(get_refresh_thread):
        """ Refresh Tooltips, Pulse Audio fades and get user input
            Returns False when system shutting down
            TODO: Convert to lcs.fast_refresh(...)
        """
        thread = get_refresh_thread()
        if thread:
            thread()
            return True
        else:
            return False

    def sync_rewind(self):
        """ Rewind 5 seconds.
            Temporarily hide buttons so, they can't be clicked for 2 seconds
            Ramp down our currently playing volume only (don't ramp up others)
            Kill currently playing
            Rewind 4 seconds from current spot, calculate new duration
            Restart play and ramp up only our volume
        """

        if not self.top_is_active or not self.time_ctl.check_pid():
            self.info.cast("Trying to rewind with no PID")
            return

        old_highlight = self.curr_line_highlight
        curr_sec = self.time_ctl.elapsed()  # def elapsed
        if self.time_ctl and self.time_ctl.state != 'stop':
            self.time_ctl.stop()  # If not already stopped, stop now
        self.start_sec = curr_sec - 5
        self.start_sec = 0.0 if self.start_sec < 0.0 else self.start_sec
        self.limit_sec = self.play_DurationSecs - self.start_sec
        self.set_highlight(self.start_sec)  # Set self.curr_line_highlight
        self.curr_line_no = self.curr_line_highlight
        ''' Set checkboxes from new highlight to old highlight '''
        if self.curr_line_highlight < old_highlight:
            self.check_range_of_boxes(self.curr_line_highlight, old_highlight)
        else:
            self.info.cast("Oops sync_rewind(() couldn't check boxes",
                           'error')

        fade_out = self.start_sec + self.limit_sec - .5
        self.time_ctl.restart(self.start_sec, self.limit_sec,
                              .5, fade_out, TMP_CURR_SYNC, False)
        pav.set_volume(self.time_ctl.sink, 100)  # Fading in from 0 anyway

    # noinspection PyUnusedLocal
    def tree_select(self, event=None):
        """ Process line left-clicked in treeview while music is playing.

            Set new start time. Shorten duration of previous line and
            increase duration of line clicked.
        """
        ''' TODO: event.y() fits coding conventions better than .focus() '''
        clicked_line = int(self.tree.focus())  # Line that was clicked
        print("clicked_line:", clicked_line,
              "self.curr_line_highlight:", self.curr_line_highlight)
        # clicked_line: 6 self.curr_line_highlight: 5

        if clicked_line < self.first_checked or \
                clicked_line > self.last_checked:  # Between first and last
            text = "Only click lines between first and last checkbox."
            print(text)
            self.info.cast(text)
            return  # Ignore everything else

        if clicked_line < self.curr_line_highlight:
            # Clicking previous line? Reset last changes back to original
            values = self.tree.item(str(clicked_line))['values']
            # values[0] = new_time, values[1]=line text, values[2]=old duration
            # values[3] = new_duration
            if values[3] != "":
                # A non-blank time was formatted so, we overrode previously
                # TODO: Recall create treeview routine
                self.tree.delete(*self.tree.get_children())
                self.populate_treeview()
                print('Start time changes (edits) removed.')
            else:
                print('You can only click previous line to cancel time edits.')
            return

        elif clicked_line == self.curr_line_highlight:
            # Clicking same line? We start later and extend previous time
            print('Start time reduced.')
            pass

        elif clicked_line != self.curr_line_highlight + 1:
            # Clicking next line? Quicken line start time and extend duration
            print('You can only click one line ahead to make it start sooner.')
            return

        ''' Remove everything highlighted '''
        self.remove_all_highlights()

        ''' Highlight current line clicked '''
        tags = self.tree.item(self.tree.focus())['tags']
        if "normal" in tags:
            tags.remove("normal")
            tags.append("sync_sel")  # Apply line highlight
            self.tree.item(self.tree.focus(), tags=tags)

        ''' Update time and duration for line clicked. 
            TODO: self.time_ctl.elapsed() to get song time offset. '''
        new_time = self.time_ctl.elapsed()
        values = self.tree.item(str(clicked_line))['values']
        # values[0] = new_time, values[1]=line text, values[2]=old duration
        # values[3] = new_duration
        if clicked_line + 1 <= len(self.new_time_list):
            new_duration = self.new_time_list[clicked_line] - new_time
        else:
            new_duration = self.play_DurationSecs - new_time
        values[0] = self.format_secs(new_time, 7)
        values[3] = self.format_secs(new_duration, 7)
        # Here's the kicker, clicked line maybe beyond len(time_list[])
        # Insert additional indices as necessary.
        # TODO:
        self.new_time_list[clicked_line - 1] = new_time
        self.new_durations_list[clicked_line - 1] = new_duration
        self.tree.item(str(clicked_line), values=values)

        ''' Update duration for previous line clicked '''
        previous_line = clicked_line - 1
        if previous_line > 0:
            values = self.tree.item(str(previous_line))['values']
            new_duration = self.new_time_list[clicked_line - 1] - \
                self.new_time_list[previous_line - 1]
            values[3] = self.format_secs(new_duration, 7)
            self.new_durations_list[previous_line - 1] = new_duration
            self.tree.item(str(previous_line), values=values)

        ''' Wrap up '''
        self.curr_line_highlight = clicked_line

    def sync_done(self):
        """ End the sync() function. Called by button: 'begin_done' """
        try:
            self.tree.unbind("<ButtonRelease-1>")  # Mouse left-click release.
        except tk.TclError:  # bad window path name
            #print("type self.tree.unbind", type(self.tree.unbind))
            pass  # Window closing
        # Without this, checking a box causes tree_select() to invoke during
        # refresh cycles and new_time and duration changes. Highlight bar
        # shifts up and down.
        if self.time_ctl and self.time_ctl.path is not None:
            self.time_ctl.stop()  # Don't want to close because path reset
        if not self.top_is_active:
            return
        self.remove_all_highlights()
        self.remove_all_checkboxes()  # Should original be restored?
        self.ffplay_is_running = False  # No longer playing "Playing"
        self.build_btn_bar_frm()  # Defaults to 'top' for top main window
        pav.fade_in_aliens(1)

    def remove_all_highlights(self):
        """ Remove everything highlighted.  TODO: shorten code """
        for item in self.tree.get_children():  # For all items
            self.tree.selection_remove(item)  # Remove selection
            tags = self.tree.item(item)['tags']  # Remove line highlight
            if "sync_sel" in tags:
                tags.remove("sync_sel")
                tags.append("normal")
                self.tree.item(item, tags=tags)

    def remove_all_checkboxes(self):
        """ Remove all checkboxes.  TODO: shorten code  """
        for line in self.tree.tag_has("checked"):
            tags = self.tree.item(line)['tags']
            tags.remove("checked")
            tags.append("unchecked")
            self.tree.item(line, tags=tags)

    @staticmethod
    def format_secs(secs, length, prefix=""):
        """ Format seconds as 999.9 """
        f_secs = '%.1f' % secs
        return play_padded_number(f_secs, length, prefix)

    def set_highlight(self, elapsed=None):
        """ As music plays, check if we need to reposition highlight bar.
            Save processing by passing elapsed time if known
        """

        """ calculate line that should be highlighted """
        # new_time = self.start_sec + self.elapsed_secs  # Where are we in song?
        if elapsed:
            new_time = elapsed
        else:
            new_time = self.time_ctl.elapsed()
        # if self.printed == False:
        #    print('new_time:', new_time, 'self.start_sec:', self.start_sec, \
        #          'self.elapsed_secs:', self.elapsed_secs)

        calculated_highlight = self.lyrics_line_count  # Default last line
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
        if self.curr_line_highlight == calculated_highlight:
            return
        self.tree.see(str(calculated_highlight))  # July 4 comment out

        # print('new_time:', new_time, 'self.start_sec:', self.start_sec,
        #      'self.elapsed_secs:', self.elapsed_secs)

        ''' Update tags to highlight current line '''
        self.remove_all_highlights()

        self.curr_line_highlight = calculated_highlight  # Set new current line
        tags = self.tree.item(str(self.curr_line_highlight))['tags']
        tags.remove("normal")  # Remove line normal
        tags.append("sync_sel")  # Apply line highlight
        # self.tree.item(str(self.curr_line_highlight), tags=tags)
        # Test if integer works when string is expected below.
        self.tree.item(self.curr_line_highlight, tags=tags)

    def check_all_boxes(self):
        """ Fill in all blank check boxes between first and last checked.
            At least one must be checked or return False.
        """
        # Find the first and last checked boxes.
        first_checked = self.lyrics_line_count
        last_checked = 0
        for line in self.tree.tag_has("checked"):
            i_line = int(line)
            if i_line < first_checked:
                first_checked = i_line
            if i_line > last_checked:
                last_checked = i_line

        # At least one line must be checked
        if last_checked == 0:
            messagebox.showinfo(title="Checkbox error", icon="error",
                                message="Check at least one box.",
                                parent=self.top)
            return None, None

        # Mark all lines between first checked and last checked.
        self.check_range_of_boxes(first_checked, last_checked)

        self.top.update_idletasks()  # Process pending events
        self.top.update()  # Update checkboxes on screen
        return first_checked, last_checked

    def check_range_of_boxes(self, first_checked, last_checked):
        """ Mark all checkboxes between first and last. """
        for line in range(first_checked, last_checked):
            # Next 5 lines can be made into global function called:
            # tree_tag_replace(tree, old, new). Return true if found.
            tags = self.tree.item(str(line))['tags']  # str() for pycharm
            if "unchecked" in tags:
                tags.remove("unchecked")
                tags.append("checked")
                self.tree.item(str(line), tags=tags)

    def delete_all(self):
        """ Time Indices hopelessly out of sync so Delete them.
        """
        if self.ffplay_is_running:
            return  # Already playing?

        answer = message.AskQuestion(
            self.top, thread=self.get_refresh_thread,
            title="Delete all time indices",
            text="All times will be permanently erased!!!\n\n" +
                 'To cancel time changes, click "Close" button instead.' +
                 "\n\nAfter deleting, Time Index window will be closed.")
        if answer.result != 'yes':
            return

        self.work_time_list = []
        self.new_time_list = []
        # Save SQL row
        if len(self.work_lyrics_score) == 0:
            self.work_lyrics_score = None
        sql.update_lyrics(self.work_sql_key, self.work_lyrics_score,
                          self.work_time_list)
        sql.hist_delete_time_index(self.work_sql_key)

        self.close()  # Bail out with nothing to do

    def sample_all(self):
        """ Play music 1 second for each line.
            Mount new buttons like sync has sync_done,
                 sync_rewind

            BUGS: Last two lines aren't checked.

            TODO: button to instantly adjust last line just played. Tagging
                  and coming back after entire song finishes takes too much
                  time and effort.

        """
        if self.ffplay_is_running:
            return  # Already playing

        # Check all boxes
        for line in range(1, self.lyrics_line_count + 1):
            tags = self.tree.item(str(line))['tags']
            if "unchecked" in tags:
                tags.remove("unchecked")
                tags.append("checked")
                self.tree.item(str(line), tags=tags)

        # Setup first and last checked boxes. At least one line must be checked.
        #self.first_checked, self.last_checked = self.check_all_boxes()
        #if not self.first_checked:  # Error message already
        #    self.info.cast("sample_all() at least one check needed.")
        #    return  # displayed so return.
        self.first_checked = 1
        self.last_checked = self.lyrics_line_count

        self.ffplay_is_running = True  # We are now playing
        self.build_btn_bar_frm('sample_all')

        self.sample_play()  # Start time & duration calculated
        self.sample_watch()  # Better
        self.sample_done()

    def sample_play(self):
        """ Called by sample all which uses sync_restart() on each line

            self.first_checked and self.last_checked is the line number range.

            Duration is initially the whole song and then it is restarted
            after two seconds played for each lien start.

        """

        # First line has 4 seconds. Remaining lines have 2 seconds
        # 1.5-second playing countdown before line to sample
        self.start_sec = self.new_time_list[self.first_checked - 1] - .5
        self.start_sec = 0.0 if self.start_sec < 0.0 else self.start_sec

        self.limit_sec = self.play_DurationSecs
        fade_out = self.start_sec + 3.25

        self.time_ctl.start(self.start_sec, self.limit_sec,
                            .5, fade_out, TMP_CURR_SYNC, True)
        pav.fade_out_aliens(.5)
        self.time_ctl.cont()  # dead_start=True. Resume play
        pav.set_volume(self.time_ctl.sink, 100)  # Fading in from 0 anyway

    def sample_watch(self):
        """
            Sample All - Play line for 1 second then skip to next.
            When we first start up music already playing for length of song.
            Allow two seconds first time before killing.
            After that, kill each line after 1 second of play
        """
        # First line has 4 seconds. Remaining lines have 1.25 seconds
        self.elapsed_secs = 0.0
        self.curr_line_highlight = ""

        play_seconds = 4.0  # First time play is for 4.0 seconds. Then 2 secs
        self.curr_line_no = 1

        while self.top_is_active:
            elapsed = self.time_ctl.elapsed()  # Fast .00017 seconds
            if elapsed > self.start_sec + play_seconds:
                # Uncheck line just played via CheckboxTreeview()
                # noinspection PyProtectedMember
                self.tree._uncheck_ancestor(str(self.curr_line_no))
                self.curr_line_no += 1
                if self.curr_line_no > len(self.new_time_list):
                    break  # Last line has been played
                self.tree.see(str(self.curr_line_no))  # str() for pycharm
                self.sample_restart(self.curr_line_no)  # kill & new PID

            self.set_highlight(elapsed)  # Change highlight if necessary
            if not self.refresh_works(self.get_refresh_thread):
                break
            play_seconds = 1.5  # restart used .25 in .5 out .75 full volume

        # Clear highlights
        # below is covered by sample_done() now called above
        #if not self.top_is_active:
        #    return  # Window closed?
        #self.remove_all_highlights()
        # Make first manually checked box visible (if any)
        #items = self.tree.tag_has("checked")
        #if items:
        #    self.tree.see(items[0])

    def sample_restart(self, line_no):
        """ Restart playing at line number for 1.25 seconds with
            .25 second fade in/out. Fake whole song duration but
            will restart manually
        """
        self.start_sec = self.new_time_list[line_no - 1] - .25
        self.start_sec = 0.0 if self.start_sec < 0.0 else self.start_sec
        self.limit_sec = self.play_DurationSecs - self.start_sec
        fade_out = self.start_sec + 1
        self.time_ctl.restart(self.start_sec, self.limit_sec,
                              .25, fade_out, TMP_CURR_SYNC, False)
        pav.set_volume(self.time_ctl.sink, 100)  # Fading in from 0 anyway

    def sample_rewind(self):
        """ Sample All Rewind 5 seconds.
            Temporarily hide buttons so, they can't be clicked for 2 seconds
            Ramp down our currently playing volume only (don't ramp up others)
            Kill currently playing
            Rewind 4 seconds from current spot, calculate new duration
            Restart play and ramp up only our volume
        """
        if not self.top_is_active or not self.time_ctl.check_pid():
            self.info.cast("Trying to rewind with no PID")
            return

        old_highlight = self.curr_line_highlight
        curr_sec = self.time_ctl.elapsed()  # def elapsed
        if self.time_ctl and self.time_ctl.state != 'stop':
            self.time_ctl.stop()  # If not already stopped, stop now
        self.start_sec = curr_sec - 5
        self.start_sec = 0.0 if self.start_sec < 0.0 else self.start_sec
        self.limit_sec = self.play_DurationSecs - self.start_sec
        self.set_highlight(self.start_sec)  # Set self.curr_line_highlight
        ''' Set checkboxes from new highlight to old highlight '''
        if self.curr_line_highlight < old_highlight:
            self.check_range_of_boxes(self.curr_line_highlight, old_highlight)
        else:
            self.info.cast("Oops sample_rewind(() couldn't check boxes",
                           'error')
        self.curr_line_no = self.curr_line_highlight
        self.sample_restart(self.curr_line_highlight)

    def sample_done(self):
        """ Save changes and quit sample_all() function
        """
        if self.time_ctl and self.time_ctl.state != 'stop':
            self.time_ctl.stop()  # Don't want to close because path reset
        if not self.top_is_active:
            return
        self.remove_all_highlights()
        self.remove_all_checkboxes()  # Do we want to leave them checked?
        self.ffplay_is_running = False  # No longer playing "Playing"
        # If clicked "Done" while music was paused, reset for next time
        if self.pp_state is 'Paused':
            self.pp_state = 'Playing'
            self.pp_button['text'] = self.pp_pause_text
            # self.toggle_play() - Don't use - stops / starts music
        self.build_btn_bar_frm()  # Defaults to 'top' for top main window
        pav.fade_in_aliens(1)

    def toggle_play(self):
        """ Toggle pause/play during Fine-Tune Sample All
        """
        if self.pp_state is 'Playing':
            self.pp_state = 'Paused'
            self.pp_button['text'] = self.pp_play_text
            if self.time_ctl and self.time_ctl.state != 'stop':
                self.time_ctl.stop()  # Don't want to close because path reset
        else:
            self.pp_state = 'Playing'
            self.pp_button['text'] = self.pp_pause_text
            # Resume(unpause) the music
            self.time_ctl.cont()  # def cont(self

        # self.top.update_idletasks()  # Process pending events
        self.top.update()

    def merge_lines(self):
        """ Merge two or more lines together.
            Error if no lines checked.
            Warning if one line checked it will be merged with next.
            Warning if more than 3 lines checked.
        """
        # Get first and last line numbers being processed.
        # Take care to subtract 1 when referencing corresponding list index.
        first, last = self.check_all_boxes()  # Verify checkbox(es)
        if first is None:
            return  # Error message already
        if first == last:
            answer = message.AskQuestion(
                self.top, thread=self.get_refresh_thread,
                title="Merge lines together",
                text="At least two lines must be selected to merge together." +
                     "\n\nThis will merge checked line and the line after it.")
            if answer.result == 'yes':
                last = first + 1
            else:
                return
        if last + 1 - first > 3:
            text = "Merging more than three lines can make new line too long."
            if self.four_checked_warning(text):
                return  # Warn > 3 checkboxes

        ''' Make first line duration longer Similar to tree_select() '''
        values = self.tree.item(str(first))['values']
        # values[0] = new_time, values[1]=line text, values[2]=old duration
        # values[3] = new_duration
        if last + 1 <= len(self.new_time_list):
            # last as index is 1 past last line.
            new_duration = self.new_time_list[last] - self.new_time_list[first - 1]
        elif last <= len(self.new_time_list):
            new_duration = self.play_DurationSecs - self.new_time_list[last - 1]
        else:
            new_duration = 0.0
        values[3] = self.format_secs(new_duration, 7)
        # print('first-1:', first-1, 'durations:', len(self.new_durations_list))
        self.new_durations_list[first - 1] = new_duration
        self.tree.item(str(first), values=values)

        ''' Merge checked lyrics line(s) into first checked line's lyrics. 

            Building new treeview when finished changing lyrics will lose all
            our work in progress new time and new duration columns. This will
            give illusion work has been saved when it really hasn't been. So
            we will manually massage treeview line by line instead.
        '''
        tree_count = len(self.tree.get_children())  # IMPORTANT it is here!
        for i in range(first, last):
            # print('Merging line:', i+1, 'to line:', i)
            # item = self.tree.item(str(i))
            # print('treeview item:', item)
            # trg_item = self.tree.item(str(i+1))
            # print('target item:', trg_item)
            ''' Update treeview lyrics line '''
            trg_values = self.tree.item(
                str(i + 1))['values']  # Get line values to delete
            self.tree.delete(str(i + 1))  # Delete from treeview
            self.delete_line(i + 1)  # Delete from lyrics score
            values[1] = values[1] + trg_values[1]  # Merge lyrics to line
            self.tree.item(str(first), values=values)  # Update lyrics line

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
            item = self.tree.item(str(trg_item))  # Save item to move
            self.tree.delete(str(trg_item))  # Delete item to move
            ''' TODO: ERROR when i = 0 '''
            self.tree.insert('', 'end', iid=str(i), text=item['text'],
                             values=item['values'], tags=item['tags'])
            # Red rider Neruda - Power song has "Image:" dictionary key empty
            # print('renumbered from:', trg_item, 'to:', i, 'item:', item)

        ''' Remove all checkboxes as they won't repeat this '''
        self.remove_all_checkboxes()

        ''' Update new line count in label field '''
        # self.line_count_var.set()

        ''' Update lyrics textbox '''
        self.sync_changed_score = True  # Lyrics score has been changed

    def delete_line(self, line_no):
        """ Delete one line from lyrics score.

            Examples 1 & 2 return a list, 3 returns a string:
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
        if line_no < self.lyrics_line_count:
            chunk2 = self.work_lyrics_score.split('\n')[line_no:
                                                        self.lyrics_line_count]
        else:
            chunk2 = self.work_lyrics_score.split('\n')[-1]
        # Merge chunks 1 & 2 for new lyrics score
        self.work_lyrics_score = ""
        for line in chunk1:
            self.work_lyrics_score += line + '\n'
        for line in chunk2:
            self.work_lyrics_score += line + '\n'
        self.lyrics_line_count -= 1  # Decrement line count
        self.line_count_var.set("Line count: " + str(self.lyrics_line_count))
        self.sync_changed_score = True  # For warning messages

    def four_checked_warning(self, msg):
        """ Give chance to abort - allows one-liner in caller.
            July 4, 2023 - No longer called because can easily cancel
                too many lines checked after starting process.
        """
        answer = message.AskQuestion(self.top, text=msg,
                                     thread=self.get_refresh_thread,
                                     title="More than three lines checked")
        return answer.result != 'yes'

    def insert_line(self):
        """ Insert line like [chorus], [bridge], [solo], "song lyrics line"
            Option to insert "Line(s) just copied" has added advantage of
            increasing time indices for all following lyric lines automatically.
        """
        first, last = self.check_all_boxes()  # Verify checkbox(es)
        if first is None:
            return  # Error message already

        if first != last:
            messagebox.showinfo(
                title="Check only one box", icon="error",
                message="Check the line to insert before.",
                parent=self.top)
            return

        self.remove_all_checkboxes()

    def save_changes(self):
        """ Save changes to time indices and possibly lyrics score too.
            Lyrics score changes by 'Merge lines' or 'Insert Tag' buttons.
        """
        if self.sync_changed_score is False and \
                self.work_time_list == self.new_time_list:
            answer = message.AskQuestion(
                self.top, thread=self.get_refresh_thread,
                title="Lyrics have NOT been fine-tuned",
                text="No changes to save. Force save anyway?")
            if answer.result != 'yes':
                return

        if len(self.work_lyrics_score) == 0:
            print('PROGRAM ERROR: There are no lyrics score to save!')
            self.work_lyrics_score = None  # Don't want to save ""
            return

        ''' write synchronized lyrics changes to SQL database '''
        sql.update_lyrics(self.work_sql_key, self.work_lyrics_score,
                          self.new_time_list)
        self.new_time_list = self.work_time_list  # To prevent close warning
        self.close()  # Close window & exit

    def top_lift(self):
        """ Bring to top of window stack. """
        self.top.focus_force()  # Grab back window focus
        # below is blocking other apps from getting focus
        #self.top.lift()  # Raise stacking order

    def startup_check(self):
        """ Check if fine-tuning time indices is appropriate.
            Use 80% threshold. Give advice on how to manually click each
            lyrics score line in song as it is being sung by the singer.
        """

        time_count = len(self.work_time_list)
        if float(self.lyrics_line_count) > 0.0:
            percent = float(time_count) / float(self.lyrics_line_count)
        else:
            percent = 0.0

        if percent > .8:
            return True

        ''' Instructions to obtain 80% synchronization with basic steps '''
        quote = ("\n" +

                 "Fine-tuning lyrics time indices can only be done after basic\n" +
                 "synchronization is completed for at least 80% of lines.\n\n\t" +

                 "Number of lines in lyrics score: " + str(self.lyrics_line_count) + "\n\t" +
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
                         thread=self.get_refresh_thread,
                         title="Fine-tune time index instructions - mserve")
        return False

    # noinspection PyUnusedLocal
    def close(self, *args):  # *args required for lambda
        """ Close Synchronize Time Index to Lyrics window
            Modeled after lib_tree_play_close() but with confirmation if changes made.
        """
        ret_lyrics_score = self.work_lyrics_score
        ret_time_list = list(self.work_time_list)  # Make shallow copy
        # Sometimes self.new_time_list isn't defined even though it should be []
        # so put in extra test below to ensure it isn't None
        if self.sync_changed_score or self.new_time_list and \
                self.work_time_list != self.new_time_list:
            # What if they merge two lines and insert 1 Tag? then count same!
            # TODO: Ensure merge & insert set self.sync_changed_score flag
            print('self.sync_changed_score:', self.sync_changed_score)
            print('len(self.work_time_list):', len(self.work_time_list))
            print('len(self.new_time_list):', len(self.new_time_list))
            # TypeError: object of type 'NoneType' has no len()
            print('differences:', list(set(self.work_time_list) -
                                       set(self.new_time_list)))
            answer = message.AskQuestion(self.top,
                                         thread=self.get_refresh_thread,
                                         title="Times have been fine-tuned",
                                         text="Changes will be lost!")
            if answer.result != 'yes':
                return
            else:
                ''' Wipe out all changes '''
                ret_lyrics_score = None
                ret_time_list = None

        self.ffplay_is_running = False  # Playing and syncing?
        self.top_is_active = False  # Lyrics Time Index window open?
        if self.tt and self.top:
            self.tt.close(self.top)  # Close tooltips under top level

        ''' July 5, 2023 - External call to close self.time_ctl_list was None '''
        ''' July 7, 2023 - Change "if self.time_ctl.sink" to "if self.time_ctl" '''
        if self.time_ctl and not self.time_ctl.sink == "":  # Our sink is still running.
            # Restore volume to other applications
            pav.fade_in_aliens(1)  # Doesn't take any time

        ''' With so much time spent synchronizing set last access to now '''
        if self.time_ctl and self.time_ctl.state != 'end':
            self.time_ctl.close()  # Resets last access time to original

        self.top.destroy()  # Close the window
        self.top = None  # Extra insurance
        if os.path.isfile(TMP_CURR_SYNC):
            os.remove(TMP_CURR_SYNC)  # Clean up /tmp directory

        self.fine_tune_closed_callback(ret_lyrics_score, ret_time_list)


# ==============================================================================
#
#       BatchSelect() class. Speed up processing from .82 second to .15 seconds
#
# ==============================================================================
class BatchSelect:
    """ Usage:

    bs = BatchSelect(self.lib_tree)
    for all songs:
        adj_list = bs.add_select(song, album, artist, song_number)
        self.tree_col_range_add(song, 8, adj_list)  # Column number passed

    for artist in all artists:
        adj_list = bs.get_totals(artist)
        self.tree_col_range_add(artist, 8, adj_list, tagsel='artist_sel')
        for album in all albums:
            adj_list = bs.get_totals(album)
            self.tree_col_range_add(album, 8, adj_list, tagsel='album_sel')

    adj_list = bs.get_totals('lib_top_totals')
    self.tree_title_range_add(8, adj_list)  # Pass start index
    self.display_lib_title()  # Was called thousands of times above.

    """

    def __init__(self, treeview):
        """
        BatchSelect replaces toggle_select() function on startup.
        Updating is done after thousands of playlist songs are selected in
        lib_tree:
            Artist (I1)
                Album (I2)
                    Song (3)
                    Song (4)
                Album (I3)
                    Song (6)
                    Song (7)
            Artist (I4)

        :param treeview: self.lib_tree
        :param lib_top_totals: self.lib_top_totals returned to caller
        """
        # root window is the parent window
        self.tree = treeview  # self.lib_tree
        self.totals = {}  # keyed by iid for Artist and Album or 'lib_top_totals'
        # Data elements are StatSize, Count, Seconds

    def add_select(self, song, album, artist, number_str):
        """ Toggle song selection on.
            Roll up totals into list of dictionaries.
            DO NOT update parents here. Update parents with batch_update()
        """
        # 0=PlayTime, 1=Size MB, 2=Selected Str, 3=Time, 4=StatSize,
        # 5=Count, 6=Seconds, 7=SelSize, 8=SelCount, 9=SelSeconds
        total_values = slice(4, 7)  # parm = start index, stop before index
        # slice(4, 7) = Set slice to grab StatSize, Count, Seconds

        tags = self.tree.item(song)['tags']
        tags.append("song_sel")  # Special handling by mserve only
        #tags.append("checked")  # CheckboxTreeview handling
        #tags.remove("unchecked")  # CheckboxTreeview handling
        self.tree.item(song, tags=tags)

        self.tree.set(song, "Selected", number_str)

        self.tree.change_state(song, "checked")  # in CheckboxTreeview()
        # With new design of load_last_selections() "checked" is now needed
        # in addition to "song_sel" tag.

        # We only need to _check_ancestor(song) after last song on an album
        # is selected
        # noinspection PyProtectedMember
        #self.tree._check_ancestor(song)  # in CheckboxTreeview()

        # Get StatSize, Count and Seconds
        adj_list = self.tree.item(song)['values'][total_values]
        self.totals_add(album, adj_list)
        self.totals_add(artist, adj_list)
        self.totals_add("lib_top_totals", adj_list)
        return adj_list

    def totals_add(self, iid, add_list):
        """ Add list of 3 values to values list in dictionary, key = iid
        """
        curr_values = self.get_totals(iid)

        for i, add_val in enumerate(add_list):
            curr_values[i] += add_val

        self.totals[iid] = curr_values

    def get_totals(self, iid):
        """ Get list of 3 values in dictionary, key = iid
        """
        if iid in self.totals:
            curr_values = self.totals[iid]  # iid already in totals
        else:
            curr_values = [0, 0, 0]  # Size, Count, Seconds
        return curr_values


# ==============================================================================
#
#       tvVolume() class. Tkinter slider to set application volume level
#
# ==============================================================================
class tvVolume:
    """ Usage by caller:

    self.tv_vol = tvVolume(parent, name, title, text, tooltips=self.tt,
                           thread=self.get_refresh_thread,
                           save_callback=self.save_callback
                           playlists=self.playlists, info=self.info)
          - Music must be playing (name=ffplay) or at least a song paused.
          - save_callback=function that will reread new variables saved.

    if self.tv_vol and self.tv_vol.top:
        - Volume top level exists so lift() overtop of self.lib_top

    """

    def __init__(self, top=None, name="ffplay", title=None, text=None,
                 tooltips=None, thread=None, save_callback=None, playlists=None,
                 info=None):
        """
        """
        # self-ize parameter list
        self.parent = top    # self.parent
        self.name = name            # Process name to search for current volume
        self.title = title          # E.G. "Set volume for mserve"
        self.text = text            # "Adjust mserve volume to match other apps"
        self.tt = tooltips          # Tooltips pool for buttons
        self.get_thread_func = thread        # E.G. self.get_refresh_thread
        self.save_callback = save_callback  # Set hockey fields to new values
        self.playlists = playlists
        self.info = info

        self.last_sink = None
        self.last_volume = None
        self.curr_volume = None
        self.slider = None
        if self.save_callback is None:
            toolkit.print_trace()
            print("mserve.py tvVolume() class self.save_callback is 'None'")
            return
        else:
            #print("Test self.save_callback():", self.save_callback)
            pass

        ''' Regular geometry is no good. Linked to lib_top is better '''
        self.top = tk.Toplevel()
        try:
            xy = (self.parent.winfo_x() + g.PANEL_HGT * 3,
                  self.parent.winfo_y() + g.PANEL_HGT * 3)
        except AttributeError:  # Music Location Tree instance has no attribute 'winfo_x'
            print("self.parent failed to get winfo_x")
            xy = (100, 100)

        self.top.minsize(width=g.BTN_WID * 10, height=g.PANEL_HGT * 10)
        self.top.geometry('+%d+%d' % (xy[0], xy[1]))
        self.top.title("Volume During TV Commercials - mserve")
        self.top.configure(background="#eeeeee")  # Replace "LightGrey"
        self.top.columnconfigure(0, weight=1)
        self.top.rowconfigure(0, weight=1)

        ''' Set program icon in taskbar '''
        img.taskbar_icon(self.top, 64, 'white', 'lightskyblue', 'black')

        ''' Create master frame '''
        self.vol_frm = tk.Frame(self.top, borderwidth=g.FRM_BRD_WID,
                                relief=tk.RIDGE, bg="#eeeeee")
        self.vol_frm.grid(column=0, row=0, sticky=tk.NSEW)
        self.vol_frm.columnconfigure(0, weight=1)
        self.vol_frm.columnconfigure(1, weight=5)
        self.vol_frm.rowconfigure(0, weight=1)
        ms_font = g.FONT

        ''' Instructions '''
        PAD_X = 5
        if not self.text:  # If text wasn't passed as a parameter use default
            self.text = "\nSet mserve volume during Hockey TV Commercials\n\n" + \
                "When TV commercials appear during a hockey game,\n" + \
                "you can click the commercial button and mserve\n" + \
                "will play music for the duration of the commercials.\n\n" + \
                "Sometimes the volume of the hockey game is lower than\n" + \
                "normal and you have the system volume turned up.\n" + \
                "In this case, you want to set mserve to a lower volume here. \n"
        tk.Label(self.vol_frm, text=self.text, justify="left", bg="#eeeeee",
                 font=ms_font)\
            .grid(row=0, column=0, columnspan=3, sticky=tk.W, padx=PAD_X)

        ''' Input fields: TV_BREAK1, TV_BREAK2 and TV_SOUND '''
        self.commercial_secs = tk.IntVar()
        self.intermission_secs = tk.IntVar()
        self.tv_application = tk.StringVar()
        tk.Label(self.vol_frm, text="Commercial seconds:", bg="#eeeeee",
                 font=ms_font).grid(row=1, column=0, sticky=tk.W)
        tk.Entry(self.vol_frm, textvariable=self.commercial_secs,
                 font=ms_font).grid(row=1, column=1, sticky=tk.W)
        tk.Label(self.vol_frm, text="Intermission seconds:", bg="#eeeeee",
                 font=ms_font).grid(row=2, column=0, sticky=tk.W)
        tk.Entry(self.vol_frm, textvariable=self.intermission_secs,
                 font=ms_font).grid(row=2, column=1, sticky=tk.W)
        tk.Label(self.vol_frm, text="TV application name:", bg="#eeeeee",
                 font=ms_font).grid(row=3, column=0, sticky=tk.W)
        tk.Entry(self.vol_frm, textvariable=self.tv_application,
                 font=ms_font).grid(row=3, column=1, sticky=tk.W)

        ''' Volume During TV Commercials Slider '''
        self.slider = tk.Scale(self.vol_frm, from_=100, to=25, tickinterval=5,
                               command=self.set_sink, bg="#eeeeee")
        self.slider.grid(row=0, column=3, rowspan=4, padx=5, pady=5, sticky=tk.NS)

        ''' button frame '''
        bottom_frm = tk.Frame(self.vol_frm, bg="#eeeeee")
        bottom_frm.grid(row=10, columnspan=4, pady=(10, 5), sticky=tk.E)

        ''' Apply Button '''
        self.apply_button = tk.Button(bottom_frm, text="✔ Apply",
                                      width=g.BTN_WID2 - 6, font=g.FONT,
                                      command=self.apply)
        self.apply_button.grid(row=0, column=0, padx=10, pady=5, sticky=tk.E)
        if self.tt:
            self.tt.add_tip(self.apply_button, "Save Volume Slider changes and exit.",
                            anchor="nw")
        self.top.bind("<Return>", self.apply)  # DO ONLY ONCE?

        ''' Help Button - 
            https://www.pippim.com/programs/mserve.html#HelpTvVolume '''
        ''' ⧉ Help - Videos and explanations on pippim.com '''

        help_text = "Open new window in default web browser for\n"
        help_text += "videos and explanations on using this screen.\n"
        help_text += "https://www.pippim.com/programs/mserve.html#\n"

        help_btn = tk.Button(
            bottom_frm, text="⧉ Help", font=g.FONT,
            width=g.BTN_WID2 - 4, command=lambda: g.web_help("HelpTvVolume"))
        help_btn.grid(row=0, column=1, padx=10, pady=5, sticky=tk.E)
        if self.tt:
            self.tt.add_tip(help_btn, help_text, anchor="ne")

        ''' Close Button '''
        self.close_button = tk.Button(bottom_frm, text="✘ Close",
                                      width=g.BTN_WID2 - 6, font=g.FONT,
                                      command=self.close)
        self.close_button.grid(row=0, column=2, padx=(10, 5), pady=5, 
                               sticky=tk.E)
        if self.tt:
            self.tt.add_tip(self.close_button, "Close Volume Slider, ignore changes.",
                            anchor="ne")
        self.top.bind("<Escape>", self.close)  # DO ONLY ONCE?
        self.top.protocol("WM_DELETE_WINDOW", self.close)

        ''' Get current volume & Read stored volume '''
        self.last_volume, self.last_sink = self.get_volume()  # Reset this value when ending
        if not self.read_vol():
            message.ShowInfo(self.parent, "Initialization of mserve in progress.",
                             "Cannot adjust volume until playlist loaded into mserve.",
                             icon='error', thread=self.get_thread_func)
            self.close()

        # Adjusting volume with no sound source isn't helpful
        if self.last_volume is None:
            title = "No Sound is playing."
            text = "Cannot adjust volume until a song is playing."
            message.ShowInfo(self.parent, title, text,
                             icon='warning', thread=self.get_thread_func)
            self.info.cast(title + "\n" + text, 'warning')
            self.close()

        if self.top:  # May have been closed above.
            self.top.update_idletasks()

    def get_volume(self, name=None):
        """ Get volume of 'ffplay' before resetting volume """
        if name is None:
            name = self.name  # self.name defaults to "ffplay"

        all_sinks = pav.get_all_sinks()  # Recreates pav.sinks_now
        for Sink in all_sinks:
            if Sink.name == name:
                return int(Sink.volume), Sink.sink_no_str

        return None, None

    def set_sink(self, value=None):
        """ Called when slider changes value. Set sink volume to slider setting.
            Credit: https://stackoverflow.com/a/19534919/6929343 """
        if value is None:
            print("tvVolume.set_sink() 'value' argument is None")
            return
        curr_vol, curr_sink = self.get_volume()
        pav.set_volume(curr_sink, value)
        self.curr_volume = value  # Record for saving later

    def read_vol(self):
        """ Get last saved volume.  Based on get_hockey. If nothing found
            set defaults. """
        self.curr_volume = 100  # mserve volume when TV commercial on air
        d = self.get_config_for_loc('hockey_state')
        if d is None:
            return None
        ''' Get hockey tv commercial volume '''
        if 25 <= int(d['Size']) <= 100:
            self.curr_volume = int(d['Size'])
        self.commercial_secs.set(d['Count'])
        self.intermission_secs.set(int(d['Seconds']))
        self.tv_application.set(d['SourceDetail'])
        if self.last_volume:
            pav.fade(self.last_sink, self.last_volume, self.curr_volume, 1)
        self.slider.set(self.curr_volume)
        self.top.update_idletasks()
        return True

    def save_vol(self):
        """ Save volume setting during TV Hockey Broadcast Commercials """

        ''' Reread hockey state in case user changed after set_tv_volume started '''
        d = self.get_config_for_loc('hockey_state')
        # If we don't rewrite fields they get blanked out. Action=Location
        try:
            d['Count'] = int(self.commercial_secs.get())  # int() wrapper not needed
            d['Size'] = float(self.intermission_secs.get())
        except ValueError:
            message.ShowInfo(self.top, "Invalid Seconds Entered.",
                             "Commercial or Intermission contains non-digit(s).",
                             icon='error', thread=self.get_thread_func)
            return False

        d['SourceDetail'] = self.tv_application.get()
        _volume, sink = self.get_volume(name=d['SourceDetail'])
        if sink is None:
            title = "Invalid TV Application Name."
            text = "The application '" + d['SourceDetail'] + \
                   "' does not have a stream opened for sound.\n\n" + \
                   "Ensure your browser has opened a video (it can be paused)."
            self.info.cast(title + "\n\n" + text, 'error')
            message.ShowInfo(self.top, title, text,
                             icon='error', thread=self.get_thread_func)
            return False

        self.save_config_for_loc(
            'hockey_state', d['SourceMaster'], d['SourceDetail'], Size=self.curr_volume,
            Count=d['Count'], Seconds=d['Seconds'], Comments=d['Comments'])
        self.save_callback()  # This resets global TV_VOLUME variable for us
        return True

    def get_config_for_loc(self, Type):
        """ Wrapper Action is auto assigned as location or playlist number string
            TODO:   Same function in MusicLocationTree() class and tvVolume() class.
                    Awkward that tvVolume() class needs to be passed Playlists().
        """
        if NEW_LOCATION:
            return None

        if self.playlists.open_name:
            Action = self.playlists.open_code
        else:
            Action = lcs.open_code
        return sql.get_config(Type, Action)

    def save_config_for_loc(self, Type, SourceMaster="", SourceDetail="", Target="",
                            Size=0, Count=0, Seconds=0.0, Comments=""):
        """ Wrapper Action is auto assigned as location or playlist number string
            TODO:   Same function in MusicLocationTree() class and tvVolume() class.
                    Awkward that tvVolume() class needs to be passed Playlists().
        """
        if NEW_LOCATION:
            return None
        if self.playlists.open_name:
            Action = self.playlists.open_code
        else:
            Action = lcs.open_code

        sql.save_config(
            Type, Action, SourceMaster=SourceMaster, SourceDetail=SourceDetail,
            Target=Target, Size=Size, Count=Count, Seconds=Seconds,
            Comments=Comments)

    ## no inspection PyUnusedLocal
    def close(self, *_args):
        """ Close Volume During TV Commercials Window """
        if self.tt and self.top:
            self.tt.close(self.top)
        self.top.destroy()
        self.top = None  # Indicate volume slider is closed

        ''' Adjust volume for playing mserve song back to starting level '''
        curr_volume, curr_sink = self.get_volume()  # last_sink may have changed
        if curr_volume and self.last_volume:
            # curr_volume will be None when shutting down.
            pav.fade(curr_sink, curr_volume, self.last_volume, 1)  # 1 second fade

    # noinspection PyUnusedLocal
    def apply(self, *args):
        """ Save volume setting """
        if self.save_vol():  # calls self.save_callback() which calls get_hockey_state()
            self.close()


# ==============================================================================
#
#   FileControl() Last File Access Time overrides. E.G. Look but do not touch.
#
# ==============================================================================
class FileControlCommonSelf:
    """ Variables in FileControl() that are reset with each .new()
    """
    def __init__(self):
        """ Reinitialize each time .new() called """

        ''' Fields for when a new file is declared '''
        self.statuses = []          # List of tuples (self.state, time.time())
        self.state = None           # == self.status[-1][0] - start/stop/end
        self.stat_start = None      # Snapshot at .new(path) initialization
        self.stat_end = None        # Snapshot at .close()- stat.ST_ATIME
        self.atime_done = None      # Did we calculate percent play and reset atime?
        self.final_atime = None     # atime set when song ended.
        self.path = None            # Full pathname to music file
        self.time_played = None     # How many seconds song was played
        self.time_stopped = None    # How many seconds song was paused
        self.percent_played = None  # self.time_played * 100 / self.DurationSecs

        ''' Fields required for Sanity Check '''
        self.metadata = None        # Dictionary containing metadata from music file
        self.artwork = []           # List of lines about artwork found
        self.audio = []             # List of lines about audio streams found

        ''' Fields extracted from Metadata '''
        ''' ID3 TAGS https://exiftool.org/TagNames/ID3.html'''
        self.metadata = None        # Dictionary containing metadata from music file
        self.artwork = []           # List of lines about artwork found
        self.audio = []             # List of lines about audio streams found
        self.valid_audio = None     # len(self.audio) > 0
        self.invalid_audio = None   # len(self.audio) == 0
        self.valid_artwork = None   # len(self.audio) > 0
        self.invalid_artwork = None  # len(self.audio) == 0

        self.ffMajor = None         # ffMpeg .get('MAJOR_BRAND', "None")
        self.ffMinor = None         # ffMpeg .get('MINOR VERSION', "None")
        self.ffCompatible = None    # ffMpeg .get('COMPATIBLE BRANDS', "None") 
        self.Title = None           # self.metadata.get('TITLE', "None")
        self.Artist = None          # self.metadata.get('ARTIST', "None")
        self.Album = None           # self.metadata.get('ALBUM', "None")
        self.Compilation = None     # self.metadata.get('COMPILATION', "None")
        self.AlbumArtist = None     # self.metadata.get('ALBUM_ARTIST', "None")
        self.AlbumDate = None       # self.metadata.get('RECORDING_DATE', "None")
        self.FirstDate = None       # self.metadata.get('DATE', "None")
        self.CreationTime = None    # new July 13, 2023 'CREATION_TIME'
        ''' ffMajor, ffMinor, ffCompatible, Title, Artist, Album, Compilation, 
        AlbumArtist, AlbumDate, FirstDate, CreationTime, DiscNumber, TrackNumber,
        Rating, Genre, Composer, Comment, Hyperlink, Duration, Seconds,
        GaplessPlayback, PlayCount, LastPlayTime, LyricsScore, LyricsTimeIndex 
        + EncodingFormat, DiscId, MusicBrainzDiscId, OsFileSize, OsAccessTime '''
        self.DiscNumber = None      # new July 13, 2023 'DISC'
        self.TrackNumber = None     # self.metadata.get('TRACK', "None")
        self.Genre = None           # self.metadata.get('GENRE', "None")
        self.Composer = None        # new July 13, 2023 'COMPOSER'
        self.Comment = None         # new July 13, 2023 'COMMENT'
        self.Duration = None        # self.metadata.get('DURATION', "0.0,0")
        self.DurationSecs = None    # hh:mm:ss sting converted to int seconds
        self.GaplessPlayback = None  # self.metadata.get('GAPLESS_PLAYBACK', "None")
        self.Encoder = None         # e.g. iTunes, mserve, etc.
        self.EncodingFormat = None  # 'wav', 'm4a', 'oga', etc.
        self.DiscId = None          # gstreamer adds to MP3 automatically
        self.MusicBrainzDiscId = None  # "       "           "
        self.AudioStream = None     # from ffmpeg self.audio[0] when checked
        self.ArtworkStream = None   # from ffmpeg self.artwork[0] when checked

        ''' mserve SQL Music Table Metadata Extras '''
        self.Rating = None          # Future Use
        self.Hyperlink = None       # Future Use
        self.PlayCount = None       # How many times 80% + was played
        self.LastPlayTime = None    # Time last played (float)
        self.OsFileSize = None      # File size when saved in SQL Music Table
        self.OsAccessTime = None    # Current time if > 80% played

        ''' Static variables for music control. '''
        self.action = None          # Action to perform ??? UNDEFINED
        self.pid = 0                # Linux Process Identification Number (Job #)
        self.sink = ""              # Pulse Audio Output Sink "999L" string
        self.vol = 100              # Output volume level
        self.elapsed_secs = 0.0     # How much of song has been played so far?

        ''' Parameters passed to FileControl.start() method '''
        self.start_sec = 0.0        # Seconds offset to start playing at
        self.limit_sec = 0.0        # Number of seconds to play. 0 = play all
        self.fade_in_sec = 0.0      # Number of seconds to fade in
        self.fade_out_sec = 0.0     # Number of seconds to fade out
        self.ff_name = None         # TMP_CURR_SONG, etc.
        self.dead_start = None      # Start song and pause it immediately


        ''' Variables for FTP / SSH '''
        # For FTP check if music file in cache. If not, retrieve to cache
        self.file_cached = None     # music file retrieved locally for playing?
        self.cache_name = None      # cached filename replaces self.path
        self.cache_size = None      # music file size
        self.cache_mtime = None     # music file lc.ModTime()


        ''' Clean up any previous work files '''
        try:
            if os.path.isfile(self.TMP_FFPROBE):
                os.remove(self.TMP_FFPROBE)
        except AttributeError:
            # FileControl instance has no attribute 'TMP_FFPROBE'
            pass
        try:
            if os.path.isfile(self.TMP_FFMPEG):
                os.remove(self.TMP_FFMPEG)
        except AttributeError:
            # FileControl instance has no attribute 'TMP_FFMPEG'
            pass


class FileControl(FileControlCommonSelf):
    """ Control Music Files, including play, pause, end """

    def __init__(self, tk_top, info, close_callback=None, silent=False,
                 log_level='all', get_thread=None):
        """ FileControlCommonSelf to remove last temporary files. """
        FileControlCommonSelf.__init__(self)

        ''' self-ize parameter list '''
        self.tk_top = tk_top        # Tkinter Toplevel window used by parent
        self.info = info            # Parent's InfoCentre() instance
        self.close_callback = close_callback
        self.block_cast = silent        # Messages broadcast are logged as facts
        self.log_level = log_level  # E.G when 'silent' often use 'error'
        self.get_thread = get_thread  # Refresh thread when dialog grabs screen
        self.last_path = None       # Use for fast clicking Next
        self.new_WIP = None         # .new() is Work In Progress
        self.close_WIP = None       # .close() is Work In Progress

        ''' Make TMP names unique for multiple FileControls racing at once '''
        letters = string.ascii_lowercase + string.digits
        self.temp_suffix = (''.join(random.choice(letters) for _i in range(6)))
        self.TMP_FFPROBE = TMP_FFPROBE + "_" + self.temp_suffix
        self.TMP_FFMPEG = TMP_FFMPEG + "_" + self.temp_suffix + ".jpg"

        ''' Variables for FTP / SSH - Override after init to self.act_host '''
        self.open_host = lcs.open_host  # Optional remote host name
        # For FTP check if music file in cache. If not, retrieve to cache
        self.open_ftp = lcs.open_ftp  # FTP login instance
        self.open_allows_mtime = None  # Can modification time be set?

    def new(self, path, action=None):
        """
        Declare new song file.
        :param path: Full path to music file
        :param action: Action to perform. When 'start' next four optional fields used.
        """
        FileControlCommonSelf.__init__(self)

        ''' Is last .new() method still running? '''
        if self.new_WIP:
            # Last new process is still running. Caused by fast clicking
            # 'next' or not acknowledging validation error message.
            #return  # Problem what if stuck for more than a few seconds?
            pass
        self.new_WIP = True  # Signal no new requests will be accepted.

        ''' Is host down? '''
        if lcs.host_down:
            return

        ''' Is last song file still open (path not none)? '''
        if self.path is not None:
            if self.block_cast:  # In silent mode, normal broadcasts become facts
                if self.log_level == 'all' or self.log_level == 'error':
                    self.info.fact("FileControl.new() last song still open:\n" +
                                   self.path, 'error')
            else:
                self.info.cast("FileControl.new() last song still open:\n" +
                               self.path, 'error')
            self.close()

        ''' Is there a programming error using .new(None)? '''
        if path is None:
            self.info.cast("FileControl.new() was given path of 'None'",
                           'error')
            return

        ''' Initialize parameters '''
        self.path = path  # Full path to music file
        #self.path = path.decode('utf-8')  # Full path to music file
        #self.path = toolkit.uni_str(path)  # Full path to music file
        #    self.stat_start = os.stat(self.last_path)
        # OSError: [Errno 2] No such file or directory:
        # '/media/rick/SANDISK128/Music/Filter/The Very Best Things_
        # 1995\xe2\x80\x932008/01 Hey Man Nice Shot.oga'
        # https://stackoverflow.com/questions/57568020/
        # whats-the-difference-of-xe2-x80-x93-and-in-python-how-do-i-change-all-t

        self.last_path = self.path  # Might be used in future, not July 1, 2023
        self.action = action        # Action to perform. Not used July 1, 2023
        # Keep original stat_start until .close() -> .end()
        # Use last_path because fast clicking Next call .close() who sets

        ''' Did fast clicking close the path? '''
        if self.path is None:
            # These messages needed during development. Should no longer appear.
            self.info.fact("FileControl.new() path went 'None' step 1")
            return

        try:
            self.stat_start = os.stat(self.last_path)
        except OSError:  # [Errno 2] No such file or directory
            # When searching all SQL metadata encountered OS filename
            # that has been deleted or belongs to another location.
            return False

        ''' Did fast clicking close the path? '''
        if self.path is None:
            self.info.fact("FileControl.new() path went 'None' step 2")
            return
        self.get_metadata()         # Get all specifications into self.metadata

        ''' Did fast clicking close the path? '''
        if self.path is None:
            self.info.fact("FileControl.new() path went 'None' step 3")
            return
        self.check_metadata()       # Get audio and video (artwork) specs

        ''' Did fast clicking close the path? '''
        if self.path is None:
            self.info.fact("FileControl.new() path went 'None' step 4")
            return
        self.touch_it()             # Last access time is now time.time()

        ''' Did fast clicking close the path? '''
        if self.path is None:
            self.info.fact("FileControl.new() path went 'None' step 5")
            return

        self.log('new')             # Initial event for base timeline
        self.new_WIP = False  # Signal new requests will be accepted.
        return True  # Needed for mserve.py missing_artwork()

    def get_metadata(self):
        """ Use ffprobe to write metadata to file self.TMP_FFPROBE
            Loop through self.TMP_FFPROBE lines to create dictionary self.metadata

            oga has DURATION and STREAM #0 first and second instead of near
            bottom.

            TODO: Huge time lag with .oga image of 10 MB inside 30 MB file.
        """

        who = "mserve.py get_metadata() - "
        self.metadata = OrderedDict()

        ''' Is host down? '''
        if lcs.host_down:
            return

        #print(who + "Calling ffprobe.")
        ext.t_init("FileControl.get_metadata() - ffprobe")
        ''' Problem ffprobe -xerror will crash on good files '''
        ''' Problem ffprobe without -xerror will crash on bad files 
            https://stackoverflow.com/questions/77054846/
            looking-for-ffprobe-ffmpeg-xerror-err-detect-that-works        
        '''
        cmd = 'ffprobe ' + '"' + self.last_path + '"' + ' 2>' + self.TMP_FFPROBE
        #print(who + "cmd=", cmd)
        result = os.popen(cmd).read().strip()
        ext.t_end('no_print')
        # ffprobe on good files: 0.0858271122 0.0899128914 0.0877139568
        # ffprobe on corrupted : 0.1700458527  (file contains dozen bytes of text)
        # Jim Stein man Bad for Good: ffprobe: 0.1356880665
        # 3-12 - Poison.oga (30 MB with 10 MB image) : 10.9 seconds !!!
        # 3-12 - Poison.oga using kid3 < 1 second

        #print(who + "Calling mutagen.")
        ext.t_init("FileControl.get_metadata() - mutagen")
        try:
            # Song: Heart/GreatestHits/17 Rock and Roll (Live).m4a
            # Song: /media/rick/SANDISK128/Music/Hello/There/smile.mp3
            m = mutagen.File(self.last_path)
            if m:  # .wav files have no metadata
                for _line in m:
                    #print("mutagen line:", _line)  # keys are in lowercase with _ removed
                    pass
        except Exception as err:
            print("Mutagen error on:", self.last_path)
            print("Exception:", err)

        #   File "/home/rick/python/mserve.py", line 12871, in get_metadata
        #     m = mutagen.File(self.last_path)
        #   File "/usr/lib/python2.7/dist-packages/mutagen/_file.py", line 251, in File
        #     return Kind(filename)
        #   File "/usr/lib/python2.7/dist-packages/mutagen/_file.py", line 42, in __init__
        #     self.load(filename, *args, **kwargs)
        #   File "/usr/lib/python2.7/dist-packages/mutagen/id3/__init__.py", line 1093, in load
        #     self.info = self._Info(file obj, offset)
        #   File "/usr/lib/python2.7/dist-packages/mutagen/mp3.py", line 185, in __init__
        #     self.__try(file obj, offset, size - offset, False)
        #   File "/usr/lib/python2.7/dist-packages/mutagen/mp3.py", line 223, in __try
        #     raise HeaderNotFoundError("can't sync to an MPEG frame")
        # HeaderNotFoundError: can't sync to an MPEG frame

        #     m = mutagen.File(self.last_path, easy=True)
        #   File "/usr/lib/python2.7/dist-packages/mutagen/_file.py", line 251, in File
        #     return Kind(filename)
        #   File "/usr/lib/python2.7/dist-packages/mutagen/_file.py", line 42, in __init__
        #     self.load(filename, *args, **kwargs)
        #   File "/usr/lib/python2.7/dist-packages/mutagen/id3/__init__.py", line 1093, in load
        #     self.info = self._Info(file obj, offset)
        #   File "/usr/lib/python2.7/dist-packages/mutagen/mp3.py", line 185, in __init__
        #     self.__try(file obj, offset, size - offset, False)
        #   File "/usr/lib/python2.7/dist-packages/mutagen/mp3.py", line 223, in __try
        #     raise HeaderNotFoundError("can't sync to an MPEG frame")
        # HeaderNotFoundError: can't sync to an MPEG frame

        #print("Mutagen m['title']:", m['title'])
        #print("Mutagen m['artist']:", m['artist'])
        #print("Mutagen m['album']:", m['album'])
        # print("Mutagen m:", m)
        # {'album':, 'title':, 'artist':, 'bpm':, 'genre':, 'date':,
        # 'tracknumber': [u'1/11'], 'disc number': [u'2/2']}
        ext.t_end('no_print')  # 40 times faster than ffprobe: 0.002
        # Jim Stein man Bad for Good: mutagen: 0.01
        # Coverart STREAM is in main tag section not in separate
        # DURATION  is in main tag section not in separate
        # 'Title' and 'Title(1)' are duplicated

        if len(result) > 1:
            print('mserve.py FileControl.get_metadata() ffprobe result:', result)

        ''' Create self.metadata{} dictionary 
            oga has 'DURATION' 2nd and 'STREAM #0' 3rd which need to be held
            and then inserted just before 'CREATION_TIME' '''

        input_encountered = False

        #print(who + "Calling open(self.TMP_FFPROBE)")
        with open(self.TMP_FFPROBE) as f:
            for line in f:
                line = line.rstrip()  # remove \r and \n
                #print(who + "line:", line)

                if not input_encountered:
                    if line.startswith('Input #0, '):
                        input_encountered = True
                        val = line.split('Input #0, ')[1]
                        self.metadata['INPUT #0'] = val
                    continue

                if ':' not in line:
                    continue  # No key/value pair

                if line.strip().upper().startswith("STREAM #0:"):
                    (key, val) = half_split(line, ':', 2)  # Split second only
                else:
                    (key, val) = line.split(':', 1)  # Split first ':' only

                key = key.strip()  # strip leading and trailing whitespace
                val = val.strip()  # Most keys are indented 2, 4 & 6 spaces.

                if not key or not val:
                    continue  # blank key or blank value

                ''' gstreamer bug - doubled up MP3 tags '''
                # For MP3, gstreamer automatically adds: "CDDB DiscID" and "discid"
                # For MP3, gstreamer automatically adds:
                #   "MusicBrainz DiscID" and "musicbrainz_discid"
                if key == "CDDB DiscID":
                    continue
                if key == "MusicBrainz DiscID":
                    continue

                ''' .m4a limitations for no custom tags - see encoding.py '''
                if key == 'category':  # Hijack the 'catg' tag for podcast category
                    key = "discid"
                if key == 'keywords':  # Hijack the 'keyw' tag for podcast keywords
                    key = "musicbrainz_discid"

                # Convert all keys to upper case for simpler lookups
                key_unique = toolkit.unique_key(key.upper(), self.metadata)
                self.metadata[key_unique] = val  # Comment can appear twice

        # noinspection SpellCheckingInspection
        '''

==== ffprobe SYNOPSIS  ==========================================================

WAV: 
Input #0, wav, from '/media/rick/SANDISK128/Music/Compilations/
                    Greatest Hits of the 80’s [Disc #3 of 3]/3-12 Poison.wav':
  Duration: 00:04:29.16, bitrate: 1411 kb/s
    Stream #0:0: Audio: pcm_s16le ([1][0][0][0] / 0x0001), 44100 Hz, 2 channels, s16, 1411 kb/s

OGG:
Input #0, ogg, from '/media/rick/SANDISK128/Music/Big Wreck/Ghosts/13 A Place to Call Home (reprise).oga':
  Duration: 00:01:07.24, start: 0.000000, bitrate: 303 kb/s
    Stream #0:0: Audio: vorbis, 44100 Hz, stereo, fltp, 224 kb/s
    Metadata:
      DISCID          : 9410610d
      DATE            : 2014-06-10
    Stream #0:1: Video: mjpeg, yuvj420p(pc, bt470bg/unknown/unknown), 1425x1425 [SAR 1:1 DAR 1:1], 90k tbr, 90k tbn,
    Metadata:
      comment         : Cover (front)
      title           : A Place to Call Home (reprise)

FLAC:
Input #0, flac, from '/media/rick/SANDISK128/Music/Compilations/
                      Greatest Hits of the 80’s [Disc #3 of 3]/3-12 Poison.flac':
  Metadata:
    TRACKTOTAL      : 14
    MUSICBRAINZ_DISCID: tjAnC0ReEc.f48DpI_lHjx1VEBA-
  Duration: 00:04:29.16, start: 0.000000, bitrate: 924 kb/s
    Chapter #0:0: start 0.000000, end 269.160000
    Metadata:
      title           : 
    Chapter #0:1: start 272.466667, end 269.160000
    Metadata:
      title           : 
    Stream #0:0: Audio: flac, 44100 Hz, stereo, s16
    Stream #0:1: Video: mjpeg, yuvj420p(pc, bt470bg/unknown/unknown), 500x408 [SAR 1:1 DAR 125:102], 90k tbr, 90k tbn,
    Metadata:
      comment         : Cover (front)
      title           : front cover

MP3:
Input #0, mp3, from '/media/rick/SANDISK128/Music/Compilations/
                     Greatest Hits of the 80’s [Disc #3 of 3]/3-12 Poison.mp3':
  Metadata:
    title           : Poison
    musicbrainz_discid: tjAnC0ReEc.f48DpI_lHjx1VEBA-
  Duration: 00:04:35.70, start: 0.000000, bitrate: 213 kb/s
    Stream #0:0: Audio: mp3, 44100 Hz, stereo, s16p, 211 kb/s
    Stream #0:1: Video: mjpeg, yuvj420p(pc, bt470bg/unknown/unknown), 500x408 [SAR 1:1 DAR 125:102], 90k tbr, 90k tbn,
    Metadata:
      title           : Front cover
      comment         : Cover (front)

MP4:
Input #0, mov,mp4,m4a,3gp,3g2,mj2, from '/media/rick/SANDISK128/Music/Compilations/
                Greatest Hits of the 80’s [Disc #3 of 3]/3-12 Poison.m4a':
  Metadata:
    major_brand     : mp42
    keywords        : tjAnC0ReEc.f48DpI_lHjx1VEBA-
  Duration: 00:04:29.14, start: 0.000000, bitrate: 195 kb/s
    Stream #0:0(eng): Audio: aac (LC) (mp4a / 0x6134706D), 44100 Hz, stereo, fltp, 191 kb/s (default)
    Metadata:
      creation_time   : 2023-08-19 19:14:07
      handler_name    : SoundHandler
    Stream #0:1: Video: mjpeg, yuvj420p(pc, bt470bg/unknown/unknown), 500x408 [SAR 1:1 DAR 125:102], 90k tbr, 90k tbn,


    1. All types start with: "Input #0, ogg, from '/media/....
    2. FLAC, MP3 and MP4 follow with: "Metadata:"
    3. OGG and WAV follow with: "Duration:"
    4. MP4 and FLAC "Stream #0:1" follow with Audio
    5. STREAM #0:0 is always audio, STREAM #0:1 is always Video (except WAV)
    6. OGG and FLAC have "track" and "TRACKTOTAL" auto-added as two fields.


        '''

        path_parts = self.path.split(os.sep)  # In case metadata missing song parts

        self.ffMajor = self.metadata.get('MAJOR_BRAND', None)
        self.ffMinor = self.metadata.get('MINOR_BRAND', None)
        self.ffCompatible = self.metadata.get('COMPATIBLE_BRANDS', None)

        self.Title = self.metadata.get('TITLE', "None")
        if self.Title == "None":  # Title missing, use OsFileName part
            self.Title = path_parts[-1].encode('utf-8')
        self.Title = toolkit.uni_str(self.Title)

        self.Artist = self.metadata.get('ARTIST', "None")  # If not in dict, use "None"
        if self.Artist == "None":  # Artist missing, use OsFileName part
            self.Artist = path_parts[-3].encode('utf-8')  # .wav files have no metadata
        self.Artist = toolkit.uni_str(self.Artist)

        self.Album = self.metadata.get('ALBUM', "None")
        if self.Album == "None":  # Album missing, use OsFileName part
            self.Album = path_parts[-2].encode('utf-8')
        self.Album = toolkit.uni_str(self.Album)
        ''' ffMajor, ffMinor, ffCompatible, Title, Artist, Album, Compilation, 
        AlbumArtist, AlbumDate, FirstDate, CreationTime, DiscNumber, TrackNumber,
        Rating, Genre, Composer, Comment, Hyperlink, Duration, Seconds,
        GaplessPlayback, PlayCount, LastPlayTime, LyricsScore, LyricsTimeIndex 
        + EncodingFormat, DiscId, MusicBrainzDiscId, OsFileSize, OsAccessTime '''
        self.Compilation = self.metadata.get('COMPILATION', None)
        self.AlbumArtist = self.metadata.get('ALBUM_ARTIST', None)
        self.AlbumDate = toolkit.uni_str(
            self.metadata.get('RECORDING_DATE', None))  # Use OGA
        if self.AlbumDate is None:  # No RECORDING_DATE
            self.AlbumDate = toolkit.uni_str(
                self.metadata.get('COPYRIGHT', None))  # Use M4A
        self.FirstDate = toolkit.uni_str(self.metadata.get('DATE', None))
        self.CreationTime = toolkit.uni_str(
            self.metadata.get('CREATION_TIME', None))
        self.DiscNumber = toolkit.uni_str(self.metadata.get('DISC', None))
        self.TrackNumber = toolkit.uni_str(self.metadata.get('TRACK', None))
        self.Genre = toolkit.uni_str(self.metadata.get('GENRE', None))
        self.Composer = toolkit.uni_str(self.metadata.get('COMPOSER', None))
        self.Comment = self.metadata.get('COMMENT', None)

        self.Duration = self.metadata.get('DURATION', "0.0,0").split(',')[0]
        self.Duration = toolkit.uni_str(self.Duration)
        #self.Duration = self.Duration.split('.')[0]  # Aug 10/23 - dec. secs
        convert = self.Duration.split('.')  # fractional second to part 2
        if convert:
            convert_out = convert_seconds(convert[0])  # Note must save in parent
            if convert[1]:
                convert_out = str(convert_out) + "." + convert[1]
            self.DurationSecs = float(convert_out)
        else:
            self.DurationSecs = 0.0  # Note must save in parent

        self.GaplessPlayback = self.metadata.get('GAPLESS_PLAYBACK', None)

        self.Encoder = self.metadata.get('ENCODER', None)

        ''' Aug 18/23 Bug fixed 3 months ago, not in production ffplay 
            https://trac.ffmpeg.org/ticket/9248 '''
        fmt = self.metadata.get('INPUT #0', None)
        if fmt:
            ''' Can be "wav." or "mov,mp4,m4a,3pg,3g2,mj2," '''
            fmt = fmt.split(' ', 1)[0]
            if fmt.endswith('.'):
                fmt = fmt.rstrip('.')
            else:
                fmt = fmt.rstrip(',')
                fmt = fmt.replace(',', ' ')
            self.EncodingFormat = fmt
        else:
            self.EncodingFormat = None

        ''' Aug 19/23 - Fields added to MP3 by gstreamer automatically '''
        self.DiscId = toolkit.uni_str(self.metadata.get('DISCID', None))
        self.MusicBrainzDiscId = \
            toolkit.uni_str(self.metadata.get('MUSICBRAINZ_DISCID', None))

        self.OsFileSize = self.stat_start.st_size
        self.OsAccessTime = self.stat_start.st_atime


    def check_metadata(self):
        """ Ensure Audio stream exists. """

        self.artwork = []           # List of lines about artwork found
        self.audio = []             # List of lines about audio streams found
        for key, value in self.metadata.iteritems():
            if key.startswith("STREAM"):
                if "Video:" in value:
                    self.artwork.append(value)
                if "Audio:" in value:
                    self.audio.append(value)

        self.valid_artwork = True if len(self.artwork) > 0 else False
        self.invalid_artwork = not self.valid_artwork
        self.valid_audio = True if len(self.audio) > 0 else False
        self.invalid_audio = not self.valid_audio

        text = "Title: \t" + self.Title + \
            " \tYear: \t" + str(self.FirstDate) + \
            "\nArtist: \t" + self.Artist + \
            " \tAlbum: \t" + self.Album + \
            "\nTrack:\t" + str(self.TrackNumber) + \
            "\tDuration:\t" + str(self.Duration) + "\n"

        for entry in self.audio:
            text += "Audio: \t" + entry[7:] + "\n"

        if self.valid_audio:
            audio_pattern = ("Audio:", "Green", "Black")
        else:
            audio_pattern = ("Audio:", "Red", "White")
            text += "Audio: \tNOT FOUND !!!\n"

        for entry in self.artwork:
            text += "Artwork: \t" + entry[7:] + "\n"

        if self.valid_artwork:
            artwork_pattern = ("Artwork:", "Green", "Black")
        else:
            artwork_pattern = ("Artwork:", "Red", "White")
            text += "Artwork: \tNOT FOUND !!!\n"

        patterns = [("Title:", "Green", "Black"),
                    ("Year:", "Green", "Black"),
                    ("Artist:", "Green", "Black"),
                    ("Album:", "Green", "Black"),
                    ("Track:", "Green", "Black"),
                    ("Date:", "Green", "Black"),
                    ("Duration:", "Green", "Black"),
                    audio_pattern,
                    artwork_pattern]

        if self.audio:
            self.AudioStream = self.audio[0]  # store first stream found
        if self.artwork:
            self.ArtworkStream = self.artwork[0]  # store first stream found
        ''' Aug 6/23 - Too annoying, change all to 'fact' for now 
            Aug 16/23 - Change back to cast when invalid audio or no artwork
        '''
        if self.valid_audio or self.block_cast:
            if self.log_level == 'all' or self.log_level == 'info':
                self.info.fact(text, 'info', patterns=patterns)
        elif self.invalid_audio or self.invalid_artwork:
            self.info.cast(text, 'error', patterns=patterns)
        else:
            if self.log_level == 'all' or self.log_level == 'info':
                self.info.fact(text, 'error', patterns=patterns)

    def log(self, state):
        """
        Important for song start, stop and end to be 100% in order to calculate
        if last access time should be reset based on percentage played threshold.

        :param state: 'start' = Playing, 'stop' = Paused, 'end' = killed
        :return: True but later could be False for sanity check errors
        """
        last_state = self.state
        self.state = state

        state_tuple = (self.state, time.time())
        self.statuses.append(state_tuple)
        if self.state == 'new' and last_state is None:
            return True
        if self.state == 'start' and \
                (last_state == 'new' or last_state == 'stop'):
            return True
        if self.state == 'stop' and last_state == 'start':
            return True
        if self.state == 'end' and last_state != 'end':
            return True

        text = "FileControl.log(state) programming error.\n\n"
        text += "New state passed is:\t" + self.state
        text += "\nIllogically, last state is:\t" + str(last_state)
        text += "\n"
        # toolkit.print_trace()  # Getting sick of seeing this !
        print("\n" + text)
        patterns = [("programming error", "White", "Black")]
        self.info.cast(text, 'error', 'add', patterns=patterns)
        return False

    def cast_stat(self, stat):
        """
        Debugging information.

        os.stat.ST_... fields
            stat.ST_UID - User id of the owner.
            stat.ST_GID - Group id of the owner.
            stat.ST_SIZE - Size in bytes of a plain file;...
            stat.st_atime - Time of last access.
            stat.ST_MTIME - Time of last modification.
            stat.ST_CTIME - The “ctime” as reported by the operating system.
        :param stat: Either self.stat_start or self.stat_end
        """

        ''' Which stat was passed as parameter?: stat_start or stat_end? 
            https://github.com/Sundar0989/WOE-and-IV/issues/2 '''
        stack = traceback.extract_stack()
        _filename, lineno, function_name, code = stack[-2]
        # print(type(code))  # <type 'str'>
        try:
            vars_name = re.compile(r'\((.*?)\).*$').search(code).groups()[0]
            _final = (re.findall(r"[\w']+", vars_name))[-1]
        except AttributeError:  # 'NoneType' object has no attribute 'groups'
            vars_name = "os.stat results: "
            #print("cast_stat() ERROR: re.compile()")  # tons of errors
        except IndexError:  # Happens when exiting mserve
            vars_name = "os.stat results: "

        ''' Pretty format of os.stat(filename) variables  '''
        text = vars_name + "\t" + self.path + "\n"
        text += "Access Time:\t\t" + time.asctime(time.localtime(stat.st_atime))
        text += "\t\t\t\tUser ID:\t" + str(stat.st_uid) + "\n"
        text += "Modify Time:\t\t" + time.asctime(time.localtime(stat.st_mtime))
        text += "\t\t\t\tGroup ID:\t" + str(stat.st_gid) + "\n"
        text += "Change Time:\t\t" + time.asctime(time.localtime(stat.st_ctime))
        text += "\t\t\t\tInode No:\t" + str(stat.st_ino) + "\n"
        patterns = [(vars_name, "White", "Black"),
                    ("Access Time:", "Green", "Black"),
                    ("Modify Time:", "Green", "Black"),
                    ("Change Time:", "Green", "Black"),
                    ("User ID:", "Green", "Black"),
                    ("Group ID:", "Green", "Black"),
                    ("Inode No:", "Green", "Black")]

        ''' Aug 6/23 - Too annoying, change all to 'fact' for now '''
        if self.block_cast:
            if self.log_level == 'all' or self.log_level == 'info':
                self.info.fact(text, patterns=patterns)
        else:
            if self.log_level == 'all' or self.log_level == 'info':
                self.info.fact(text, patterns=patterns)

    def get_artwork(self, width, height):
        """
            Use ffmpeg to get artwork for song into self.TMP_FFMPEG filename.
            Messages go to self.TMP_FFPROBE filename which is ignored for now.

            Called from:

            set_artwork_colors()
            lib_tree_play()
        """

        if len(self.artwork) == 0:
            # Song has no artwork that ffmpeg can identify.
            return None, None, None

        ''' Is host down? '''
        if lcs.host_down:
            return None, None, None

        # Don't reuse last artwork
        if os.path.isfile(self.TMP_FFMPEG):
            os.remove(self.TMP_FFMPEG)

        # noinspection SpellCheckingInspection
        ext.t_init("'ffmpeg -nostdin -y -vn -an -r 1 -i '")
        # noinspection SpellCheckingInspection
        cmd = 'ffmpeg -nostdin -y -vn -an -r 1 -i ' + '"' + \
              self.path + '" ' + self.TMP_FFMPEG + ' 2>' + self.TMP_FFPROBE
        result = os.popen(cmd).read().strip()
        ext.t_end('no_print')  # 0.1054868698 0.1005489826 0.0921740532

        # noinspection SpellCheckingInspection
        ''' ffmpeg options:
                -nostdin to suppress: Press [q] to stop, [?] for help
                -y to supppress error when file exists
                -vn = skip video
                -vn = skip audio
                -r 1 = frame rate 1
                -i = input filename
                2> = redirect stderr (where stdout is written) to filename
        '''

        if len(result) > 1:
            self.info.cast("FileControl.get_artwork(): Unknown Error:\n" +
                           result)
            return None, None, None

        if not os.path.isfile(self.TMP_FFMPEG):
            # Song has no artwork that ffmpeg can identify.
            self.info.cast("FileControl.get_artwork(): Programming Error:\n" +
                           "No artwork for:\n\n" + self.path + "\n\n"
                           "However this error should have been caught above.")
            print("\nError getting artwork:\n")
            print(self.TMP_FFPROBE)
            return None, None, None

        original_art = Image.open(self.TMP_FFMPEG)
        resized_art = original_art.resize(
            (width, height), Image.ANTIALIAS)
        return ImageTk.PhotoImage(resized_art), resized_art, original_art

    def test_middle(self):
        """ NOT USED
        
            ffplay will fail playing middle of some songs. This test is
            used by lib_tree_play() and FineTune() class.

            July 3, 2023 - 20 minutes after writing discovered this isn't
            needed. Keep around for documenting how FileControl() works.
        """

        if self.DurationSecs < 20:
            return False  # Not even a real song.

        old_block_cast = self.block_cast
        self.block_cast = True  # Don't broadcast what happens next
        start = self.DurationSecs / 2
        # Start halfway through, duration 5 seconds, with 4 second fade in
        self.start(start, 5, 4, 1, TMP_CURR_SAMPLE, True)
        time.sleep(.1)
        self.cont()
        time.sleep(.2)  # If ffplay breaks, job crashes in .1 second
        pid = self.check_pid()
        self.end()  # Kill song and restore last access time.
        self.block_cast = old_block_cast  # Restore original broadcast setting

        ''' Reset statuses '''
        self.statuses = []
        self.state = None
        self.atime_done = False
        self.log('new')

        if pid != 0:
            return True

        text = "The following song cannot be played in the middle:\n"
        text += self.path
        text += "\n\nHowever, you may still be able to play the song normally and"
        text += "\neven perform Basic Time Indexing (Lyrics Synchronization).\n\n"
        text += "You will not be able to sample middle 10 seconds of song or\n"
        text += "perform Fine-Tune Time Indexing (Lyrics Synchronization).\n\n"
        text += "The problem occurred because 'ffplay' crashed 0.2 seconds\n"
        text += "into playing the middle 5 seconds of the song."
        self.info.cast(text, 'error')

    def start(self, start_sec=0.0, limit_sec=0.0, fade_in_sec=0.0,
              fade_out_sec=0.0, ff_name=None, dead_start=None):

        """ Call start_ffplay() converting parameters to extra_opt format.

        :param start_sec: Seconds offset to start playing at
        :param limit_sec: Number of seconds to play. 0 = play all
        :param fade_in_sec: Number of seconds to fade in
        :param fade_out_sec: Number of seconds to fade out
        :param ff_name: Filename containing ffplay output. E.G TMP_CURR_SONG
        :param dead_start: Set to volume to 0 and immediately stop play
        :return self.pid, self.sink:
        """

        self.start_sec = start_sec          # Seconds offset to start playing at
        self.limit_sec = limit_sec          # Number of seconds to play. 0 = play all
        self.fade_in_sec = fade_in_sec      # Number of seconds to fade in
        self.fade_out_sec = fade_out_sec    # Number of seconds to fade out
        self.ff_name = ff_name              # TMP_CURR_SONG, etc.
        self.dead_start = dead_start        # Number of seconds to fade out

        ''' extra options passed to ffplay for fade-in, etc. '''
        extra_opt = ffplay_extra_opt(self.start_sec, self.fade_in_sec,
                                     self.fade_out_sec, self.limit_sec)

        # start = seconds offset to start song at. If 0.0, start at beginning
        # duration = seconds to play song for. If 0.0, entire song, skip duration set
        # fade_in = seconds to fade in for. If continuing, manually adjust volume
        # fade_out = seconds to fade out for. If pausing or ending, manually adjust
        # ff_name = Filename used by ffplay, ffmpeg and ffprobe with command
        #           Output. In this case it is ffplay output only.
        # dead_start = After starting song set volume to zero and stop running.
        #              When starting with fade-in there is no sound "pop"

        ''' Aug 18/23 Bug fixed 3 months ago, not in production ffplay 
            https://trac.ffmpeg.org/ticket/9248 '''
        if self.EncodingFormat and self.EncodingFormat == "wav":
            # noinspection SpellCheckingInspection
            extra_opt += ' -af "aformat=channel_layouts=stereo"'

        ''' uncomment for debugging 
        text = "FileControl.start(self.start_sec, \t" + str(self.start_sec) +\
            "\nself.limit_sec, \t" + str(self.limit_sec) + "\nself.fade_in_sec, \t" +\
            str(self.fade_in_sec) + "\nself.fade_out_sec, \t" + str(self.fade_out_sec) +\
            "\nself.dead_start, \t" + str(self.dead_start) + "\nself.ff_name, \t" + \
            str(self.ff_name) + "\n"
        self.info.cast("FileControl.start() path:\n" + self.path)
        self.info.cast("FileControl.start() extra_opt:\n" + extra_opt)
        self.info.cast(text)  # For debugging
        # Can't copy from file.info zoom window so print to console to copy
        print("FileControl.start() path:\n" + self.path)
        print("FileControl.start() extra_opt:\n" + extra_opt)
        #print(text)  # For debugging
        '''

        ''' Is host down? '''
        if lcs.host_down:
            return 0, ""  # No PID, No Sink

        '''   B I G   T I C K E T   E V E N T   '''
        self.pid, self.sink = start_ffplay(self.path, self.ff_name,
                                           extra_opt, toplevel=self.tk_top)

        ''' Sanity check '''
        if self.start_sec > self.DurationSecs:
            patterns = [("self.start_sec:", "Green", "Black"),
                        ("self.DurationSecs:", "Green", "Black")]
            self.info.cast("Programming Error in FileControl.start()\n" +
                           "\tself.start_sec: " + str(self.start_sec) +
                           " > self.DurationSecs: " + str(self.DurationSecs) +
                           "\n\tMeans no music will be being played at all!",
                           'error', patterns=patterns)

        ''' bad sink? '''
        if self.sink == "":
            # Pulse Audio failed to get sink we cannot do dead_start
            if self.pid > 0:
                print("FileControl.start() orphan PID is running:", self.pid)
            ''' When caller sees self.sink is blank, they will issue error '''
            return self.pid, self.sink

        self.log('start')

        if dead_start:
            pav.set_volume(self.sink, 0)  # Turn off volume
            ext.stop_pid_running(self.pid)  # Pause the music
            self.log('stop')

        return self.pid, self.sink

    def restart(self, start_secs, limit_sec=0.0, fade_in_sec=0.0,
                fade_out_sec=0.0, ff_name=None, dead_start=False):
        """
            Kill current running PID as a new one will be started

            Save old PID sink number to pass to start_ffplay who will
            then wait for sink to be closed. Then start_ffplay will
            know which sink number out of the active sinks to give back
            for song restarted here.
        """

        if self.check_pid():
            ext.kill_pid_running(self.pid)
            self.pid = 0  # def kill_song already does this
            self.sink = ""

        ''' Song may have been paused before getting killed above '''
        if self.state != 'stop':  # 'stop' code already logged. Don't repeat.
            self.log('stop')  # There is no 'kill' code so use 'stop' instead.

        if not ff_name:
            ''' TMP_CURR_SONG is required. If not passed use last '''
            ff_name = self.ff_name

        return self.start(start_sec=start_secs, limit_sec=limit_sec,
                          fade_in_sec=fade_in_sec, fade_out_sec=fade_out_sec,
                          ff_name=ff_name, dead_start=dead_start)

    def stop(self):
        """ Stop playing (pause) """
        ext.stop_pid_running(self.pid)  # Pause the music
        self.log('stop')

    def cont(self):
        """ Continue playing (un-pause) """
        ext.continue_pid_running(self.pid)  # Un-pause music
        self.log('start')

    def elapsed(self):
        """ How many seconds have elapsed """
        if self.ff_name is None or self.path is None or self.pid == 0:
            #print("FileControl.elapsed() requested when song ended")
            #print("This may screw up percent played calculation.")
            return 0.0

        ext.t_init("FileControl.elapsed()")
        self.elapsed_secs = get_curr_ffplay_secs(self.ff_name)
        job_time = ext.t_end('no_print')  # 0.0000710487 to 0.0001909733
        # Hardly any time used, but add half of job time to elapsed time
        self.elapsed_secs += job_time / 2
        return self.elapsed_secs  # In case parent requested

    def check_pid(self):
        """ Check if PID is still running. Else song is over. """
        if self.pid == 0:
            self.sink = ""
            return 0

        try:
            # os.kill 2nd parameter with 0 checks if process is active
            os.kill(self.pid, 0)
        except OSError:
            # Do not blank out self.current_song! It controls song_set_ndx('next')
            self.pid = 0
            self.sink = ""
            return 0  # Song has ended

        return self.pid

    def end(self):
        """ Kill Song and calculate what percentage was truly played.

            If duration of ffplay is less than x percentage total run time
            restore original access time. Same holds true for all
            get_metadata() and get_artwork() calls if music never played.

            NOTE: time_ctl continuously calls restart() and end()


        """
        if self.check_pid():
            ext.kill_pid_running(self.pid)
            self.pid = 0  # def kill_song already does this
            self.sink = ""

        ''' Was .end() already called? '''
        if (self.state and self.state == 'end') or self.atime_done:
            # Reproducible when fast clicking "Next" song. Also note fast
            # clicking isn't working and a couple seconds per song skipped
            # before target song starts playing.
            ''' Already called? '''
            text = "InfoCentre.end() called twice.\n" +\
                   "\tPath: \t\t" + str(self.path) +\
                   "\n\tself.state: \t\t" + str(self.state) +\
                   "\n\tself.atime_done:\t" + str(self.atime_done) +\
                   "\n\tUse 'View' dropdown menu, 'Show Debug' for traceback."
            print(text)
            self.info.cast(text, 'error', 'update')
            #toolkit.print_trace()  # Once sampling song and closing with X
            if self.atime_done:
                return  # Last access time has already been updated
        else:
            self.log('end')

        if self.path is None:
            return  # With fast clicking 'Next' self.path can be None soon

        if self.stat_end is None:
            ''' Below duplicated if self.close() was just called '''
            try:
                self.stat_end = os.stat(self.path)
            except OSError:  # [Errno 2] No such file or directory
                self.atime_done = True  # Extra precaution time isn't done twice
                return
            self.cast_stat(self.stat_end)  # Show in InfoCentre

        ''' loop through statuses[] to get time played and time stopped '''
        self.calc_time_played()

        ''' Uncomment to test '''
        text = "Time Statistics:\t\t" + self.path +\
               "\nTime played: \t" + str(self.time_played) + \
               "\t\tTime stopped: \t" + str(self.time_stopped) + \
               "\t\tPercent play: \t" + str(self.percent_played)
        patterns = [("Time Statistics:", "White", "Black"),
                    ("Time played:", "Green", "Black"),
                    ("Time stopped:", "Green", "Black"),
                    ("Percent play:", "Green", "Black")]

        ''' Aug 6/23 - Cast is too annoying, change all to 'fact' for now '''
        if self.block_cast:  # All casts being blocked switch on
            if self.log_level == 'all' or self.log_level == 'info':
                self.info.fact(text, 'info', 'update', patterns)
        else:
            # This used to be cast but too annoying
            if self.log_level == 'all' or self.log_level == 'info':
                self.info.fact(text, 'info', 'update', patterns)

        ''' Is host down? '''
        if lcs.host_down:
            return

        '''   B I G   T I C K E T   E V E N T   '''
        if self.percent_played < float(ATIME_THRESHOLD):
            ''' Didn't play long enough. Restore original access time '''
            old_time, new_time = self.touch_it(self.stat_start)
            # touch_it() returns None, None when no song path
            self.final_atime = new_time
            ''' Aug 6/23 - Too annoying, change all to 'fact' for now '''
            patterns = [("Restoring last access for:", "White", "Black"),
                        ("Current time:", "Green", "Black"),
                        ("Original time:", "Green", "Black")]
            if self.block_cast and old_time is not None:
                if self.log_level == 'all' or self.log_level == 'info':
                    self.info.fact("Restoring last access for: \t" + self.Title +
                                   "\n\tCurrent time:  \t" +
                                   tmf.ago(old_time).strip() +
                                   "\n\tOriginal time: \t" +
                                   tmf.ago(new_time).strip(),
                                   patterns=patterns)
            elif old_time is not None:
                if self.log_level == 'all' or self.log_level == 'info':
                    self.info.fact("Restoring last access for: \t" + self.Title +
                                   "\n\tCurrent time:  \t" +
                                   tmf.ago(old_time).strip() +
                                   "\n\tOriginal time: \t" +
                                   tmf.ago(new_time).strip(),
                                   patterns=patterns)
            else:
                if self.log_level == 'all' or self.log_level == 'info':
                    self.info.fact("Could not restore last access for: \t" +
                                   str(self.Title) +
                                   "\nLikely caused by fast clicking Next/Prev")
        else:
            ''' Song counts as being played > 80% '''
            if not sql.increment_last_play(self.path):
                self.info.fact("Error incrementing last play: \t" + self.Title,
                               icon='error')

        #start_atime = self.stat_start.st_atime
        #end_atime = self.stat_start.st_atime
        #print("start_atime:", tmf.ago(start_atime, seconds=True),
        #      "end_atime:", tmf.ago(end_atime, seconds=True))

        self.atime_done = True  # Extra precaution time isn't done twice

    def touch_it(self, new_stat=None):
        """
        Linux "touch" command to set last access time. When a file is accessed
        Linux doesn't update access time until end of day. Do it immediately so
        lib_top.tree will reflect when each song was played instantly.

        If less than threshold percentage of song is played (defaults to 80%)
        then reset last access time as if song was not played.

        NOTE: The file's "Change Time" is updated whenever touch is run

        :param new_stat: Optional stat.st_time to force, otherwise current time.
        :return old_time, new_time:
        """

        ''' Is host down? '''
        if lcs.host_down:
            return None, None

        if self.path is None:
            self.info.cast("FileControl.touch_it() called with No path")
            return None, None

        ''' Old (current) access time before it is forced. '''
        old_stat = os.stat(self.path)
        old_atime = old_stat.st_atime

        if new_stat:
            ''' The forced time passed. Likely self.stat_start instance '''
            forced_atime = new_stat.st_atime
            date_str = datetime.datetime.fromtimestamp(forced_atime)\
                .strftime('%Y-%m-%d %H:%M:%S')
            cmd = 'touch -a -c -d"' + date_str + '" "' + self.path + '"'
        else:
            ''' Force last access time (-a) to current time (-c)
                Called externally when parent opens new song for playing 
            '''
            cmd = 'touch -a -c ' + '"' + self.path + '"'

        ''' Change access time to forced. '''
        result = os.popen(cmd).read().strip()
        if len(result) > 1:
            self.info.cast("FileControl.touch_it(): Unknown Error:\n" +
                           result)
            return None, None

        forced_stat = os.stat(self.path)
        forced_atime = forced_stat.st_atime
        self.final_atime = forced_atime

        #delta = forced_atime - old_atime
        #print("InfoCentre.touch_it() time delta:", delta)
        # InfoCentre.touch_it() time delta: 0.0
        # InfoCentre.touch_it() time delta: 301.0
        # InfoCentre.touch_it() time delta: -302.0

        return old_atime, forced_atime

    def calc_time_played(self):
        """Calc self.time_played, self.time_paused & self.percent_played. """

        self.time_played = self.time_stopped = self.percent_played = 0.0
        last_action, last_time = self.statuses[0]  # 'new', time.time()

        for status in self.statuses:  # list of tuples (action, time)
            delta = status[1] - last_time
            if last_action == 'start':
                self.time_played += delta
            if last_action == 'stop':
                self.time_stopped += delta
            last_action, last_time = status  # 'start'/'stop'/'end', time

        if self.DurationSecs == 0.0:
            self.percent_played = 0.0
            # Kansas/The Ultimate Kansas 2/2-07 Play The Game Tonight.m4a
            # DURATION:	00:00:00.86, start: 0.000000, bit rate: 1721 kb/s
        else:
            self.percent_played = \
                float(self.time_played) * 100 / float(self.DurationSecs)
        ''' TODO: get_resume then reset it to zero when done. '''

    def close(self):
        """ When > 80 % of song played (Fast Forward resets to 0%), then set
            last access time to now. When < 80% reset to saved settings when
            file was declared with .new(path)

            functions .log('start'), .log('stop') and .log('end') populated
            self.statuses with status and event time. """
        self.close_WIP = None       # .close() is Work In Progress
        if self.path is None:
            FileControlCommonSelf.__init__(self)  # clear all from .new() down
            return  # Already closed.

        if self.state and self.state is 'end':
            # Fast clicking next/prev, atime is never done and we call end twice
            FileControlCommonSelf.__init__(self)  # clear all from .new() down
            return

        ''' Is host down? '''
        if lcs.host_down:
            FileControlCommonSelf.__init__(self)  # clear all from .new() down
            return

        if self.stat_end is None:
            ''' Below duplicated if self.end() was just called '''
            try:
                self.stat_end = os.stat(self.path)
            except OSError:  # [Errno 2] No such file or directory
                self.atime_done = True  # Extra precaution time isn't done twice
                return
            self.cast_stat(self.stat_end)  # Show in InfoCentre

        ''' Call .end() if not already logged or if Last Access Time not set '''
        if self.state and self.state is not 'end':
            self.end()  # calculate percent played and restore access time
        # Fast clicking next/prev, atime is never done and we call end twice
        #if not self.atime_done:
        #    self.end()  # calculate percent played and restore access time

        ''' Call to parent: close_lib_tree_song(path, a_time) '''
        if self.close_callback is not None and self.path is not None and \
                self.final_atime is not None:
            self.close_callback(self.path, self.final_atime)

        ''' Variables can be queried to check if song open. So clear all '''
        FileControlCommonSelf.__init__(self)  # clear all from .new() down


# ==============================================================================
#
#       Refresh() class.  NOT USED
#
# ==============================================================================
class Refresh:
    """ Usage:  NOT USED

        self.refresh = Refresh(30, self.get_refresh_thread)

        Functions:
            check(self):

    """

    def __init__(self, ms, get_thread_func):
        """ Work in Progress """
        ''' self-ize parameter list '''
        self.ms = ms
        self.get_thread_func = get_thread_func

        ''' Working fields '''
        self.last_time = time.time()

    def check(self):
        """ Work in Progress """
        now = time.time()
        elapsed = now - self.last_time
        if elapsed >= ms:
            thread = self.get_thread_func()  # Initial thread can change
            thread()  # Update window animations and check for input
            # NOTE: Should be option to delay new checkbox when current running
            self.last_time = now  # Do we want current time instead ???
            return True  # Right time for refresh
        return False  # Time isn't right


# ==============================================================================
#
#       Playlists() class.
#
# ==============================================================================
class PlaylistsCommonSelf:
    """ Class Variables used by Playlistss() class """
    def __init__(self):
        """ Called on mserve.py startup and for Playlists maintenance """

        ''' All Playlists work fields - Set on program start and saving changes '''
        self.all_numbers = []  # "P000001", "P000002", etc... can be holes
        self.all_names = []  # Names matching all_numbers
        self.all_descriptions = []  # Descriptions matching all_numbers
        self.names_for_loc = []  # Names sorted for this location
        self.names_all_loc = []  # Names sorted for all locations

        ''' Current Playlist work fields - History Record format '''
        self.act_row_id = None  # History record number
        self.act_code = None  # E.G. "P000001"
        self.act_loc_id = None  # E.G. "L004"
        self.act_name = None  # E.G. "Oldies"
        self.act_id_list = []  # Sorted in play order
        self.act_size = 0  # Size of all song files
        self.act_count = 0  # len(self.music_id_list)
        self.act_seconds = 0.0  # Duration of all songs
        self.act_description = None  # E.G. "Songs from 60's & 70's

        ''' Miscellaneous Playlist work fields '''
        self.state = None  # 'new', 'open', 'save', 'save_as', 'view'
        self.input_active = False  # Can enter Playlist Name & Description
        self.pending_counts = None

        ''' YouTube Playlist work fields '''
        self.youDebug = 1  # Debug level. 0=None, 1=min(default), 7=max
        self.isSmartPlayYouTube = False  # is Smart YouTube Player running?
        self.isViewCountBoost = False  # 30 second play to boost view counts?
        self.youViewCountSkipped = 0  # How many videos skipped so far?
        self.driver = None  # Is Selenium Webdriver opened?
        self.youWindow = None  # DM Browser Window
        self.nameYouTube = None  # = WEB_PLAY_DIR + os.sep + self.act_name + ".csv"
        self.linkYouTube = None  # YouTube links retrieved from .csv file
        self.listYouTube = None  # [dictYouTube, dictYouTube, ... dictYouTube]
        self.dictYouTube = None  # { name: link: duration: image: }
        self.photosYouTube = None  # Photos saved from garbage collector (GIC)
        self.privateYouTube = "0"  # Saved count of private/unavailable videos
        self.listMergeYouTube = None  # Stored list + new videos
        self.youLastLink = None  # Last video ID link found and verified
        self.listYouTubeCurrIndex = None  # Same as YouTube Tree 0's-Index (Integer)
        self.gotAllGoodLinks = None  # All 100 video chunk lists have scrolled
        self.youValidLinks = None  # Video links minus private and deleted videos
        self.youUnavailableShown = None  # Unavailable videos displayed?
        self.youFullScreen = None  # Was YouTube full screen before?
        self.youForceVideoFull = None  # After video starts send "f" key

        self.youTreeFrame = None  # .grid_remove() for youLrcFrame
        self.youLrcFrame = None  # .grid_remove() for youPlaylistFrame
        self.scrollYT = None  # Custom Scrolled Text Box
        self.youAssumedAd = None  # Volume was forced automatically down
        self.hasLrcForVideo = None  # Are synchronized lyrics (LRC) stored in dict?
        self.listLrcLines = None  # List of LRC ([mm:ss.hh] "lyrics line text")
        self.ndxLrcCurrentLine = None  # Current index within listYouTubeLRC
        self.youProLrcVar = None  # Progress label variable tk string
        self.youLrcTimeOffsetVar = None  # LRC time offset (+/- seconds)
        self.youLrcTimeOffset = None  # LRC time offset (+/- seconds)
        self.youLrcBgColorVar = None  # LRC highlight yellow/cyan/magenta
        self.youLrcBgColor = None  # LRC highlight yellow/cyan/magenta
        self.youFirstLrcTimeNdx = None  # 0-Index of first line with [mm:ss.99]
        self.youFirstLrcTime = None  # Float Seconds of [mm:ss.99]

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

        ''' Playlists Maintenance Window and fields '''
        self.top = None  # tk.Toplevel
        self.frame = None  # tk.Frame inside self.top
        self.you_btn_frm = None  # Tk.Frame button bar
        self.his_view = None  # SQL Hist tk.Treeview managed by Data Dictionary
        self.you_tree = None  # YouTube Playlist Tree
        self.fld_name = None  # Field tk.Entry for toggling readonly state
        self.fld_description = None
        self.scr_name = tk.StringVar()  # Input fields
        self.scr_description = tk.StringVar()
        self.scr_location = tk.StringVar()

        self.fld_count = None  # Playlist song count
        self.fld_size = None  # Playlist all songs MB
        self.fld_seconds = None  # Playlist all songs duration

        self.apply_button = None
        self.help_button = None
        self.close_button = None


class Playlists(PlaylistsCommonSelf):
    """ Usage:

        self.playlists = Playlists(parent, name, title, text, tooltips=self.tt,
                                   thread=self.get_refresh_thread,
                                   get_pending=self.get_pending_cnt_total,
                                   display_lib_title=self.display_lib_title)
              - Geometry in Type-'window', action-'pls_top'.
              - build_lib_menu will look at self.playlists.status

        Functions:
            new(self):
            rename(self):
            delete(self):
            open(self):
            save(self):
            save_as(self):
            close(self):

        if self.playlists.pls_top:
            - Playlists top level exists so lift() to top of stack

    History Record Formats

        Type-Playlist, Action-P999999, Master-L999, Detail-Playlist Name,
            Target-JSON list of sorted Music IDs, Size=MB, Count=# Songs,
            Seconds=Total Duration, Comments=Playlist Description

        Type-P999999, Action-'resume', Master-'playing'/'paused'...

        Type-P999999, Action-'chron_state', Master-'show'/'hide'...

        Type-P999999, Action-'hockey_state', Master-'on'/'off'...

        Type-P999999, Action-<Artist Name>, Master-<Image Pil>


    Functions:

        - show() - Show existing Playlists in treeview
        - new() - Prompt for Playlist Name and Description, clear checkboxes
        - open(P999999) - Pick existing Playlist and set checkboxes
        - save() - Save changes made to Playlist
        - save_as() - Save changes under new Playlist Name and Description
        - rename() - Rename Playlist
        - delete() - Delete Playlist - leaves hole in playlist numbers

NOTES FROM APPLE - Create playlists on iPhone

In the Music app , you can organize music into playlists that you can share
 with your friends.

Note: You can’t create playlists in the Apple Music Voice Plan. For more
information, see the Apple Support article How to use Apple Music Voice.
Create playlists to organize your music

    To create a new playlist, do any of the following:

        Tap Library, tap Playlists, then tap New Playlist.

        Touch and hold a song, album, or playlist; tap Add to a Playlist;
        then tap New Playlist.

        On the Now Playing screen, tap the More button, tap Add to a
        Playlist, then tap New Playlist.

    To more easily identify the playlist later, enter a name and description.

    To give your playlist cover art, tap the Camera button, then take a photo
     or choose an image from your photo library.

    To add music to the playlist, tap Add Music, then tap Listen Now, Browse,
    Library, or the search field.

    Choose or search for music, then tap the Add button to add it to the playlist.

Tip: If you want to add songs to your library when you add them to a playlist,
     go to Settings  > Music, then turn on Add Playlist Songs.

Edit a playlist you created on iPhone

Tap the playlist, tap the More button, tap Edit, then do any of the following:

    Add more songs: Tap Add Music, then choose music.

    You can also touch and hold an item (song, album, playlist, or music video),
     tap Add to a Playlist, then choose a playlist.

    Delete a song: Tap the Delete button, then tap Delete. Deleting a song
    from a playlist doesn't delete it from your library.

    Change the song order: Drag the Reorder button next to a song.

Changes you make to your music library are updated across all your devices when
Sync Library is turned on in Music settings. If you’re not an Apple Music
subscriber, the changes appear in your music library the next time you sync
with your computer.

Sort a playlist

    Tap a playlist, then tap the More button at the top right of the screen.

    Tap Sort By, then choose an option—Playlist Order, Title, Artist, Album,
    or Release Date.

Delete a playlist

Touch and hold the playlist, then tap Delete from Library.

You can also tap the playlist, tap the More button, then tap Delete from Library.

    """

    def __init__(self, tk_top=None, text=None, pending=None, info=None,
                 apply_callback=None, enable_lib_menu=None, play_close=None,
                 tooltips=None, thread=None, display_lib_title=None):
        """
        Usage:

        self.playlists = Playlists(parent, name, title, text, tooltips=self.tt,
                                   thread=self.get_refresh_thread,
                                   get_pending=self.get_pending_cnt_total,
                                   display_lib_title=self.display_lib_title)
              - Geometry in Type-'window', action-'pls_top'.
              - build_lib_menu will look at self.playlists.status

        """
        PlaylistsCommonSelf.__init__(self)  # Define self. variables

        ''' self-ize parameter list '''
        self.parent = tk_top  # FOR NOW self.parent MUST BE: lib_top
        self.text = text  # Text replacing treeview when no playlists on file
        self.get_pending = pending  # What is pending in parent?  - Could be favorites
        self.info = info  # InfoCentre()
        self.apply_callback = apply_callback
        self.play_close = play_close  # Main music playing window to close down
        self.enable_lib_menu = enable_lib_menu
        self.tt = tooltips  # Tooltips pool for buttons
        self.get_thread_func = thread  # E.G. self.get_refresh_thread
        self.display_lib_title = display_lib_title  # Rebuild lib_top menubar

        ''' Open Playlist fields - History Record format '''
        self.open_row_id = None  # History record number
        self.open_code = None  # E.G. "P000001"
        self.open_loc_id = None  # E.G. "L004"
        self.open_name = None  # E.G. "Oldies"
        self.open_id_list = []  # Sorted in play order
        self.open_size = 0  # Size of all song files
        self.open_count = 0  # len(self.music_id_list)
        self.open_seconds = 0.0  # Duration of all songs
        self.open_description = None  # E.G. "Songs from 60's & 70's

        ''' Save between Playlist Maintenance calls '''
        self.name = None  # Playlist name that is being played right now

# Playlists Class Toplevel Methods used by all entry points

    def create_window(self, name=None):
        """ Mount window with Playlist Treeview or placeholder text when none.
            :param name: "New Playlist", "Open Playlist", etc.
        """
        self.pending_counts = self.get_pending()
        ''' Rebuild playlist changes since last time '''
        self.build_playlists()
        ''' create_top() shared with buildYouTubePlaylist '''
        self.create_top(name)

        ''' Create master frame '''
        self.frame = tk.Frame(self.top, borderwidth=g.FRM_BRD_WID,
                              relief=tk.RIDGE)
        self.frame.grid(sticky=tk.NSEW)
        #self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=3)  # Data entry fields
        self.frame.rowconfigure(0, weight=1)
        ms_font = g.FONT

        ''' Instructions when no playlists have been created yet. '''
        if not self.text:  # If text wasn't passed as a parameter use default
            self.text = "\nNo Playlists have been created yet.\n\n" + \
                        "After Playlists have been created, they will\n" + \
                        "appear in this spot.\n\n" + \
                        "You can create a playlist by selecting\n" + \
                        "the 'New Playlist' option from the 'File' \n" + \
                        "dropdown menu bar.\n"

        if len(self.all_numbers) == 0:
            # No playlists have been created yet
            tk.Label(self.frame, text=self.text, justify="left", font=ms_font) \
                .grid(row=0, column=0, columnspan=3, sticky=tk.W, padx=5)
        else:
            self.populate_his_tree()  # Paint treeview of playlists

        ''' Playlist Name is readonly except for 'new' and 'rename' '''
        tk.Label(self.frame, text="Playlist name:",
                 font=ms_font).grid(row=1, column=0, sticky=tk.W, padx=5)
        self.fld_name = tk.Entry(self.frame, textvariable=self.scr_name,
                                 state='readonly', font=ms_font)
        self.fld_name.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        self.scr_name.set("")  # Clear left over from last invocation

        ''' Playlist Description is readonly except for 'new' and 'rename' '''
        tk.Label(self.frame, text="Playlist description:",
                 font=ms_font).grid(row=2, column=0, sticky=tk.W, padx=5)
        self.fld_description = tk.Entry(
            self.frame, textvariable=self.scr_description, state='readonly',
            font=ms_font)
        self.fld_description.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        self.scr_description.set("")  # Clear left over from last invocation

        ''' Device Location is always readonly '''
        tk.Label(self.frame, text="Device location:",
                 font=ms_font).grid(row=3, column=0, sticky=tk.W, padx=5)
        tk.Entry(self.frame, textvariable=self.scr_location, state='readonly',
                 font=ms_font).grid(row=3, column=1, sticky=tk.W, padx=5,
                                    pady=5)
        self.scr_location.set(lcs.open_code + " - " + lcs.open_name)
        self.input_active = False

        ''' Song Count display only field '''
        tk.Label(self.frame, text="Song Count:",
                 font=ms_font).grid(row=1, column=2, sticky=tk.W, padx=5)
        self.fld_count = tk.Label(self.frame, text="0", font=ms_font)
        self.fld_count.grid(row=1, column=3, sticky=tk.W, padx=5)

        ''' Size of Files display only field '''
        tk.Label(self.frame, text="Size of Files:",
                 font=ms_font).grid(row=2, column=2, sticky=tk.W, padx=5)
        self.fld_size = tk.Label(self.frame, text="0", font=ms_font)
        self.fld_size.grid(row=2, column=3, sticky=tk.W, padx=5)

        ''' Music Duration display only field '''
        tk.Label(self.frame, text="Music Duration:",
                 font=ms_font).grid(row=3, column=2, sticky=tk.W, padx=5)
        self.fld_seconds = tk.Label(self.frame, text="0", font=ms_font)
        self.fld_seconds.grid(row=3, column=3, sticky=tk.W, padx=5)

        ''' button frame '''
        bottom_frm = tk.Frame(self.frame)
        bottom_frm.grid(row=4, columnspan=4, sticky=tk.E)

        ''' Apply Button '''
        close_tt_text = "Close Playlist window."
        #if self.state != 'view':
        close_tt_text = "Discard any changes and close Playlist window."
        action = name.split(" Playlist")[0]
        self.apply_button = tk.Button(bottom_frm, text="✔ " + action,
                                      width=g.BTN_WID2 - 2, command=self.apply)
        self.apply_button.grid(row=0, column=0, padx=10, pady=5, sticky=tk.E)
        self.tt.add_tip(self.apply_button, action + " Playlist and return.",
                        anchor="nw")
        self.top.bind("<Return>", self.apply)

        ''' Help Button - https://www.pippim.com/programs/mserve.html#HelpPlaylists '''
        help_text = "Open new window in default web browser for\n"
        help_text += "videos and explanations on using this screen.\n"
        help_text += "https://www.pippim.com/programs/mserve.html#\n"
        self.help_button = tk.Button(
            bottom_frm, text="⧉ Help", font=g.FONT, width=g.BTN_WID2 - 4,
            command=lambda: g.web_help("HelpPlaylists"))
        self.help_button.grid(row=0, column=1, padx=10, pady=5, sticky=tk.E)
        self.tt.add_tip(self.help_button, help_text, anchor="ne")

        ''' Close Button - NOTE: This calls reset() function !!! '''
        self.close_button = tk.Button(bottom_frm, text="✘ Close",
                                      width=g.BTN_WID2 - 4, command=self.reset)
        self.close_button.grid(row=0, column=2, padx=(10, 5), pady=5,
                               sticky=tk.E)
        self.tt.add_tip(self.close_button, close_tt_text, anchor="ne")
        self.top.bind("<Escape>", self.reset)
        self.top.protocol("WM_DELETE_WINDOW", self.reset)

        ''' Refresh screen '''
        if self.top:  # May have been closed above.
            self.top.update_idletasks()

    def create_top(self, name):
        """ Shared with self.create_window(), self.displayMusicIds()
            and self.buildYouTubePlaylist() """

        self.top = tk.Toplevel()  # Playlists top level
        ''' Save geometry for Playlists() '''
        geom = monitor.get_window_geom('playlists')
        self.top.geometry(geom)
        self.top.minsize(width=g.BTN_WID * 10, height=g.PANEL_HGT * 10)
        name = name if name is not None else "Playlists"
        self.top.title(name + " - mserve")
        #self.top.configure(background="Gray")  # Sep 5/23 - Use new default
        self.top.configure(background="#eeeeee")  # Replace "LightGrey"
        self.top.columnconfigure(0, weight=1)
        self.top.rowconfigure(0, weight=1)
        ''' After top created, disable all File Menu options for playlists '''
        self.enable_lib_menu()
        ''' Set program icon in taskbar '''
        img.taskbar_icon(self.top, 64, 'white', 'lightskyblue', 'black')

    def enable_input(self):
        """ Turn on input fields for 'new', 'rename' and 'save_as' """
        self.input_active = True
        self.fld_name['state'] = 'normal'  # Allow input
        self.fld_description['state'] = 'normal'  # Allow input

    def build_playlists(self):
        """ Get ALL configuration history rows for Type = 'playlist'
            Create sorted list of names for current location. Called
            each time Playlists.function() used. """
        ''' Read all playlists from SQL History Table into work lists '''
        for row in sql.hist_cursor.execute(
                "SELECT * FROM History INDEXED BY TypeActionIndex " +
                "WHERE Type = 'playlist'"):
            d = dict(row)
            self.make_act_from_hist(d)
            self.all_numbers.append(self.act_code)
            self.all_names.append(self.act_name)
            self.names_all_loc.append(self.act_name)
            if self.act_loc_id == lcs.open_code:
                self.names_for_loc.append(self.act_name)
        self.names_all_loc.sort()
        self.names_for_loc.sort()

    def populate_his_tree(self):
        """ Use custom Data Dictionary routines for managing treeview. """
        ''' Data Dictionary and Treeview column names '''
        #history_dict = sql.history_treeview()  # Heart of Data Dictionary
        # Sep 25/23 switch to proper dictionary
        history_dict = sql.playlist_treeview()
        columns = ("detail", "comments", "count", "size", "seconds")
        toolkit.select_dict_columns(columns, history_dict)
        ''' Create treeview frame with scrollbars '''
        self.youTreeFrame = tk.Frame(self.frame, bg="LightGrey", relief=tk.RIDGE)
        self.youTreeFrame.grid(sticky=tk.NSEW, columnspan=4)
        self.youTreeFrame.columnconfigure(0, weight=1)
        self.youTreeFrame.rowconfigure(0, weight=1)
        self.his_view = toolkit.DictTreeview(
            history_dict, self.top, self.youTreeFrame, columns=columns,
            highlight_callback=self.highlight_callback)
        ''' Override formatting of 'size' column to MB '''
        self.his_view.change_column_format("MB", "size")
        ''' Override formatting of 'seconds' column to Days:Hours:Min:Sec '''
        self.his_view.change_column_format("days", "seconds")
        ''' Override generic column heading names for Playlist usage '''
        # Sep 25/23 - Put proper names in proper dictionary
        #self.his_view.tree.heading('detail', text='Playlist Name')
        #self.his_view.tree.heading('comments', text='Playlist Description')
        #self.his_view.tree.heading('count', text='Song Count')
        #self.his_view.tree.heading('size', text='Size of Files')
        #self.his_view.tree.heading('seconds', text='Duration')
        self.his_view.tree["displaycolumns"] = columns  # hide row_id
        ''' Treeview click and drag columns to different order '''
        # Moving columns needs work and probably isn't even needed
        #toolkit.MoveTreeviewColumn(self.top, self.his_view.tree,
        #                           row_release=self.his_button_click)
        ''' Treeview select item with button clicks '''
        self.his_view.tree.bind("<Button-1>", self.his_button_click)
        self.his_view.tree.bind("<Button-3>", self.his_button_click)
        self.his_view.tree.bind("<Double-Button-1>", self.apply)
        self.his_view.tree.tag_configure('play_sel', background='ForestGreen',
                                         foreground="White")
        ''' Loop through sorted lists, reread history and insert in tree '''
        for name in self.names_for_loc:  # Sorted alphabetically
            ndx = self.all_names.index(name)  # In key order P000001, P000002, etc.
            number_str = self.all_numbers[ndx]
            d = sql.get_config('playlist', number_str)  # Must be here
            self.his_view.insert("", d, iid=number_str, tags="unchecked")

    def his_button_click(self, event):
        """ Left button clicked on Playlist row. """
        number_str = self.his_view.tree.identify_row(event.y)
        if self.state == "new" or self.state == "save_as":
            # cannot use enable_input because rename needs to pick old name first
            text = "Cannot pick an old playlist when new playlist name required.\n\n" + \
                "Enter a new Playlist name and description below."
            message.ShowInfo(self.top, "Existing playlists for reference only!",
                             text, icon='warning', thread=self.get_thread_func)
        else:
            ''' Highlight row clicked '''
            toolkit.tv_tag_remove_all(self.his_view.tree, 'play_sel')
            toolkit.tv_tag_add(self.his_view.tree, number_str, 'play_sel')

            self.read_playlist(number_str)
            self.scr_name.set(self.act_name)
            self.scr_description.set(self.act_description)
            self.scr_location.set(self.act_loc_id)
            self.fld_count['text'] = '{:n}'.format(self.act_count)
            self.fld_size['text'] = toolkit.human_mb(self.act_size)
            self.youDebug = self.act_size  # YouTube Print Debug level
            self.fld_seconds['text'] = tmf.days(self.act_seconds)
            self.top.update_idletasks()
            #print("Music IDs", self.act_id_list)

    def highlight_callback(self, number_str):
        """ As lines are highlighted in treeview, this function is called.
        :param number_str: Playlist number used as iid inside treeview
        :return: None """
        pass

# Playlists Class YouTube Playlist Processing

    def checkYouTubePlaylist(self):
        """ Is Playlist from YouTube? """

        if not self.act_description.startswith("https://www.youtube.com"):
            return False
        self.nameYouTube = WEB_PLAY_DIR + os.sep + self.act_name + ".csv"
        #if not os.path.isfile(self.nameYouTube):
        #    return True
        self.linkYouTube = ext.read_into_list(self.nameYouTube)
        if not self.linkYouTube:
            #return False
            self.linkYouTube = []  # YouTube Video Links need to be built

        return True

    def buildYouTubePlaylist(self):
        """ Build list of dictionaries """
        self.listYouTube = []
        # self.dictYouTube = {}  # Oct 8/23 - wasn't referenced
        self.photosYouTube = []

        ''' Previous generation available? '''
        fname = self.nameYouTube.replace(".csv", ".pickle")
        fname2 = self.nameYouTube.replace(".csv", ".private")
        if os.path.isfile(fname):
            self.listYouTube = ext.read_from_pickle(fname)
            self.privateYouTube = ext.read_into_string(fname2)
            if self.linkYouTube and self.listYouTube:
                if len(self.linkYouTube) == len(self.listYouTube):
                    return True

        self.act_count = 0  # Music video count (excludes private & deleted)
        self.act_seconds = 0.0  # Duration of all songs

        ''' dtb for retrieving YouTube Images first time. '''
        dtb = message.DelayedTextBox(title="Get YouTube Playlist", width=1000,
                                     toplevel=self.top, startup_delay=0)
        for link in self.linkYouTube:
            try:  # split link into segments
                song_name = link.rsplit(";", 2)[0]
                link_name = link.rsplit(";", 2)[1]
                duration = link.rsplit(";", 2)[2].strip()
                video_name = link_name.split("/watch?v=")[1]  # 7lYOmkBRs3s
                image_name = "https://i.ytimg.com/vi/" + video_name
                image_name += "/" + YOUTUBE_RESOLUTION
                # YOUTUBE_RESOLUTION = "mqdefault.jpg"  # 63 videos = 176.4 KB
            except ValueError:
                print("buildYouTubePlaylist() Value Error.")
                continue

            try:  # grab image thumbnail
                raw_data = requests.get(image_name).content
            except requests.exceptions.RequestException as e:  # This is the correct syntax
                print("RequestException:", e)
                continue

            try:  # convert thumbnail image into tkinter format
                im = Image.open(BytesIO(raw_data))
                image = {
                    'pixels': im.tobytes(),
                    'size': im.size,
                    'mode': im.mode,
                }
                dictYouTube = dict()
                dictYouTube['name'] = song_name
                dictYouTube['link'] = link_name
                dictYouTube['duration'] = duration
                dictYouTube['image'] = image
                self.listYouTube.append(dictYouTube)
                # print("song:", song_name, "duration:", duration)
                self.act_count += 1
                self.act_seconds += float(tmf.get_sec(duration))

                if not lcs.fast_refresh():
                    self.driver.quit()
                    return False
                """
                thread = self.get_thread_func()  # repeated 3 times....
                if thread:
                    thread()
                else:
                    return False  # closing down...
                """
            except tk.TclError:  # Not sure if this works for PIL yet....
                print("buildYouTubePlaylist() tk.TclError.")
                continue
            dtb_line = "Name: " + song_name + " Image: " + image_name
            dtb.update(dtb_line)

        dtb.close()

        ''' Save list so it doesn't have to be regenerated '''
        self.save_act()  # Save count and seconds
        ext.write_to_pickle(fname, self.listYouTube)
        #return len(self.listYouTube) > 0
        return True  # smart play all will now automatically build list

    def mergeYouTubePlaylist(self, listVideos, private_count):
        """ Playlists already built with buildYouTubePlaylist. When opening
            YouTube new videos discovered. Rebuild using previous lists.

        """
        self.listMergeYouTube = []

        ''' Previous generation available? '''
        #fname = self.nameYouTube.replace(".csv", ".pickle")
        #if os.path.isfile(fname):
        #    self.listYouTube = ext.read_from_pickle(fname)
        #    if self.listYouTube and self.listYouTube:
        #        if len(self.linkYouTube) == len(self.listYouTube):
        #            return True

        self.act_count = 0
        self.act_seconds = 0.0  # Duration of all songs
        existing_count = new_count = 0

        ''' dtb for retrieving YouTube Images first time. '''
        dtb = message.DelayedTextBox(title="Merge YouTube Playlist", width=1000,
                                     toplevel=self.top, startup_delay=0)
        # for link in self.linkYouTube:
        for link in listVideos:
            try:  # split link into segments
                song_name = link.rsplit(";", 2)[0]
                song_name = toolkit.normalize_tcl(song_name)
                # Fix: self.tk.call((self._w, 'insert', index, chars) + args)
                # TclError: character U+1f98b is above the range (U+0000-U+FFFF) allowed by Tcl
                link_name = link.rsplit(";", 2)[1]
                duration = link.rsplit(";", 2)[2].strip()
                video_name = link_name.split("/watch?v=")[1]
                image_name = "https://i.ytimg.com/vi/" + video_name
                image_name += "/" + YOUTUBE_RESOLUTION
            except ValueError:
                print("mergeYouTubePlaylist() Value Error.")
                continue

            try:
                # If existing link / list, reuse it.
                ndx = self.linkYouTube.index(link)
                #dictYouTube = dict()
                dictExisting = self.listYouTube[ndx]
                self.listMergeYouTube.append(dictExisting)
                existing_count += 1
                self.act_count += 1
                self.act_seconds += float(tmf.get_sec(duration))
                continue
            except ValueError:
                # New video
                new_count += 1

            try:  # grab image thumbnail
                raw_data = requests.get(image_name).content
            except requests.exceptions.RequestException as e:  # This is the correct syntax
                print("RequestException:", e)
                continue

            # Below code shared with buildYouTubePlaylist -- DRY
            try:  # convert thumbnail image into tkinter format
                im = Image.open(BytesIO(raw_data))
                image = {
                    'pixels': im.tobytes(),
                    'size': im.size,
                    'mode': im.mode,
                }
                dictYouTube = dict()
                dictYouTube['name'] = song_name
                dictYouTube['link'] = link_name
                dictYouTube['duration'] = duration
                dictYouTube['image'] = image
                #self.listYouTube.append(dictYouTube)
                self.listMergeYouTube.append(dictYouTube)
                # print("song:", song_name, "duration:", duration)
                self.act_count += 1
                self.act_seconds += float(tmf.get_sec(duration))

                if not lcs.fast_refresh():
                    self.driver.quit()
                    return False

            except tk.TclError:  # Not sure if this works for PIL yet....
                print("mergeYouTubePlaylist() tk.TclError.")
                continue
            dtb_line = "Name: " + song_name + " Image: " + image_name
            dtb.update(dtb_line)

        dtb.close()

        # TODO: Save listVideos            as self.linkYouTube
        #            self.listMergeYouTube as self.listYouTube
        if True is True:
            print("existing_count:", existing_count, "new_count:", new_count)
            print("len(self.listMergeYouTube):", len(self.listMergeYouTube))
            print("self.listMergeYouTube[0]['name']:",
                  self.listMergeYouTube[0]['name'])
            print("self.listMergeYouTube[1]['name']:",
                  self.listMergeYouTube[1]['name'])
            print("self.listMergeYouTube[-2]['name']:",
                  self.listMergeYouTube[-2]['name'])
            print("self.listMergeYouTube[-1]['name']:",
                  self.listMergeYouTube[-1]['name'])
            self.listYouTube = self.listMergeYouTube

        ''' Save files '''
        fname = self.nameYouTube.replace(".csv", ".pickle")
        fname2 = self.nameYouTube.replace(".csv", ".private")
        self.save_act()  # Save count and seconds
        ext.write_to_pickle(fname, self.listYouTube)
        ext.write_from_string(fname2, str(private_count))
        ext.write_from_list(self.nameYouTube, listVideos)
        return len(self.listYouTube) > 0

    def displayYouTubePlaylist(self):
        """ Read all self.dictYouTube inside self.listYouTube and create
            treeview.
        """

        self.displayPlaylistCommonTop("YouTube")

        for i, self.dictYouTube in enumerate(self.listYouTube):
            song_name = self.dictYouTube['name']
            song_name = toolkit.normalize_tcl(song_name)
            duration = self.dictYouTube['duration']
            lrc = self.dictYouTube.get('lrc', None)
            if lrc:
                lrc_list = lrc.splitlines()
                song_name += "\n\n" + lrc_list[0]
            image = self.dictYouTube['image']
            # from bytes() converts jpg in memory instead of reading from disk
            im = Image.frombytes(image['mode'], image['size'], image['pixels'])

            # Text Draw duration over image & place into self.photosYouTube[]
            self.displayPlaylistCommonDuration(im, duration)
            """ # Text Draw duration over image
            width, height = im.size
            draw_font = ImageFont.truetype("DejaVuSans.ttf", 24)
            draw = ImageDraw.Draw(im)
            x0 = width - 75  # text start x
            y0 = height - 30  # text start y
            x1 = x0 + 70
            y1 = y0 + 25
            draw.rectangle((x0 - 10, y0 - 5, x1, y1), fill="#333")
            draw.text((x0, y0), duration, font=draw_font, fill="white")
            # Convert image to tk photo and save from garbage collection
            photo = ImageTk.PhotoImage(im)
            self.photosYouTube.append(photo)  # Save from GIC
            """
            # https://stackoverflow.com/questions/49307497/
            # python-tkinter-treeview-add-an-image-as-a-column-value
            self.you_tree.insert('', 'end', iid=str(i), text="№ " + str(i + 1),
                                 image=self.photosYouTube[-1],
                                 value=(song_name,))
            if not lcs.fast_refresh():
                self.driver.quit()
                return False

        self.displayPlaylistCommonBottom(player_button=True)

        if len(self.listYouTube) < 1:
            title = "YouTube Playlist Unknown"
            text = "The YouTube Playlist is unknown to mserve.\n\n"
            text += "It needs to be scanned for mserve to display songs.\n\n"
            text += "Do you want to scan it now?"
            answer = message.AskQuestion(self.top, confirm="No",
                                         thread=self.get_thread_func,
                                         title=title, text=text)
            if answer.result != 'yes':
                return
            else:
                ''' youTreeSmartPlayAll will calls us when done  '''
                self.youTreeSmartPlayAll()

    def displayPlaylistCommonTop(self, name):
        """ Shared by: displayYouTubePlaylist and displayMusicIds """

        if self.tt and self.tt.check(self.top):
            self.tt.close(self.top)
        if self.top:
            geom = monitor.get_window_geom_string(self.top, leave_visible=False)
            monitor.save_window_geom('playlists', geom)
            self.top.destroy()
            self.top = None

        ''' create_top() shared with create_window() '''
        common_name = " Playlist: " + self.act_name
        common_name += " - " + str(self.act_count) + " Videos."
        common_name += " - " + tmf.days(self.act_seconds)
        if name == "YouTube":
            # create_top does name += " - mserve"
            self.create_top("YouTube" + common_name)
        else:
            self.create_top("mserve" + common_name)

        ''' Create master frame '''
        self.frame = tk.Frame(self.top, borderwidth=g.FRM_BRD_WID,
                              relief=tk.RIDGE)
        self.frame.grid(sticky=tk.NSEW)

        ''' Refresh screen '''
        if self.top:  # May have been closed above.
            self.top.update_idletasks()

        ''' Create treeview frame with scrollbars '''
        self.youTreeFrame = tk.Frame(self.frame, bg="LightGrey", relief=tk.RIDGE)
        self.youTreeFrame.grid(row=0, sticky=tk.NSEW)
        self.youTreeFrame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        #         self.you_btn_frm = tk.Frame(self.frame)
        #         self.you_btn_frm.grid(row=4, columnspan=4, sticky=tk.NSEW)

        ''' Treeview style is large images in cell 0 '''
        style = ttk.Style()
        style.configure("YouTube.Treeview.Heading", font=(None, MED_FONT),
                        rowheight=int(g.LARGE_FONT * 2.2))  # FONT14 alias
        row_height = 200
        style.configure("YouTube.Treeview", font=g.FONT14, rowheight=row_height)

        # Create Treeview
        self.you_tree = ttk.Treeview(self.youTreeFrame, column=('name',),
                                     selectmode='none', height=4,
                                     style="YouTube.Treeview")
        self.you_tree.grid(row=0, column=0, sticky='nsew')
        v_scroll = tk.Scrollbar(self.youTreeFrame, orient=tk.VERTICAL,
                                width=SCROLL_WIDTH, command=self.you_tree.yview)
        v_scroll.grid(row=0, column=1, sticky=tk.NS)
        self.you_tree.configure(yscrollcommand=v_scroll.set)
        # v_scroll.config(troughcolor='black', bg='gold')
        # https://stackoverflow.com/a/17457843/6929343

        # Left-click, requires two presses to fire
        # self.you_tree.bind('<Button-1>', self.youTreeClick)  # Needs 2 clicks
        # self.you_tree.bind('<ButtonPress-1>', self.youTreeClick)  # Needs 2 clicks
        # self.you_tree.bind('<ButtonRelease-1>', self.youTreeClick)  # Needs 2 clicks
        # self.you_tree.bind("<<TreeviewSelect>>", self.youTreeClick)  # 1 click

        # Right-click - reliable works on first click, first time, all the time
        self.you_tree.bind('<Button-3>', self.youTreeClick)  # Right-click

        # Oct 1, 2023 - MouseWheel event does NOT capture any events
        self.you_tree.bind("<MouseWheel>", lambda event: self.youTreeMouseWheel(event))
        # Button-4 is mousewheel scroll up event
        self.you_tree.bind("<Button-4>", lambda event: self.youTreeMouseWheel(event))
        # Button-5 is mousewheel scroll down event
        self.you_tree.bind("<Button-5>", lambda event: self.youTreeMouseWheel(event))

        # Setup column heading
        self.you_tree.heading('#0', text='Thumbnail Image')
        if name == "YouTube":
            self.you_tree.heading('#1', text='Song Name', anchor='center')
        else:
            self.you_tree.heading('#1', text='Title / Artist / Album / Year')

        # #0, #01, #02 denotes the 0, 1st, 2nd columns

        # Setup column hqdefault
        # YouTube Resolution: default=120x90(2.8K), hqdefault=480x360(35.6K)
        # mqdefault = 320x180
        self.you_tree.column('#0', width=450, stretch=False)
        self.you_tree.column('name', anchor='center', width=570, stretch=True)

        # Give some padding between triangles and border, between tree & scroll bars
        self.you_tree["padding"] = (10, 10, 10, 10)  # left, top, right, bottom

        # Highlight current song in green background, white text
        self.you_tree.tag_configure('play_sel', background='ForestGreen',
                                    foreground="White")

    def displayPlaylistCommonDuration(self, im, duration):
        """ Text Draw duration over image
            Shared by: displayYouTubePlaylist and displayMusicIds
        """
        width, height = im.size  # 320x180
        draw_font = ImageFont.truetype("DejaVuSans.ttf", 24)
        draw = ImageDraw.Draw(im)
        x0 = width - 75  # text start x
        y0 = height - 30  # text start y
        x1 = x0 + 70
        y1 = y0 + 25
        draw.rectangle((x0 - 10, y0 - 5, x1, y1), fill="#333")
        draw.text((x0, y0), duration, font=draw_font, fill="white")

        photo = ImageTk.PhotoImage(im)
        self.photosYouTube.append(photo)  # Save from GIC

    def displayPlaylistCommonBottom(self, player_button=False):
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

        ''' Snapshot Pulse Audio '''
        pav.get_all_sinks

        ''' Refresh screen '''
        if self.top:  # May have been closed above.
            self.top.update_idletasks()

    def youSetCloseButton(self):
        """ Set self.close_button tooltip text to:
            "Close Playlist"
            "Close Synchronized Lyrics (LRC)" """
        if self.hasLrcForVideo:
            tt_text = "Close Synchronized Lyrics (LRC)"
        else:
            tt_text = "Close YouTube Playlist"
        self.tt.set_text(self.close_button, tt_text)

    def youTreeClick(self, event):
        """ Popup menu has two different sets of options:

            If self.isSmartPlayYouTube:
                ----
                return (EXPLICIT)

            ELSE NOT self.isSmartPlayYouTube: (IMPLICIT)
            ----
            return (IMPLICIT)

        """
        item = self.you_tree.identify_row(event.y)

        if item is None:
            # self.info.cast("Cannot click on an empty row.")
            return  # Empty row, nothing to do

        menu = tk.Menu(root, tearoff=0)
        menu.post(event.x_root, event.y_root)
        no = str(int(item) + 1)  # file_menu.add  # font=(None, MED_FONT)

        if self.isSmartPlayYouTube:
            # Already smart playing YouTube playlist
            menu.add_command(label="Smart Play Song № " + no, font=g.FONT,
                             command=lambda: self.youSmartPlaySong(item))
            menu.add_command(label="Middle 15 Seconds № " + no, font=g.FONT,
                             command=lambda: self.youSmartPlaySample(item))
            menu.add_command(label="Copy Link № " + no, font=g.FONT,
                             command=lambda: self.youTreeCopyLink(item))
            menu.add_separator()  # "#" replaced with: "№ "
            menu.add_command(label="Copy LRC Search № " + no, font=g.FONT,
                             command=lambda: self.youTreeCopySearchLrc(item))
            menu.add_command(label="Paste LRC № " + no, font=g.FONT,
                             command=lambda: self.youTreePasteLrc(item))
            # TODO: Next two Active only when LRC dictionary exists
            menu.add_command(label="View LRC № " + no, font=g.FONT,
                             command=lambda: self.youTreeViewLrc(item))
            menu.add_command(label="Delete LRC № " + no, font=g.FONT,
                             command=lambda: self.youTreeDeleteLrc(item))
            menu.add_separator()
            menu.add_command(label="Close Smart Playlist", font=g.FONT,
                             command=self.youClosePlayLrc)
            menu.add_command(label="Copy Playlist Link", font=g.FONT,
                             command=lambda: self.youTreeCopyAll())
            menu.add_separator()

            menu.add_command(label="30 Second View Counts", font=g.FONT,
                             command=lambda: self.youViewCountBoost())
            menu.add_command(label="Set Debug Level", font=g.FONT,
                             command=lambda: self.youSetDebug())
            menu.add_command(label="Ignore click", font=g.FONT,
                             command=lambda: self.youClosePopup(menu, item))

            menu.tk_popup(event.x_root, event.y_root)
            menu.bind("<FocusOut>", lambda _: self.youClosePopup(menu, item))
            return

        global XDOTOOL_INSTALLED, WMCTRL_INSTALLED
        XDOTOOL_INSTALLED = ext.check_command('xdotool')
        WMCTRL_INSTALLED = ext.check_command('wmctrl')

        if XDOTOOL_INSTALLED and WMCTRL_INSTALLED:
            menu.add_command(label="Smart Play All", font=g.FONT,
                             command=lambda: self.youSmartPlayAll())
            menu.add_separator()

        menu.add_command(label="Copy Playlist Link", font=g.FONT,
                         command=lambda: self.youTreeCopyAll())

        # TODO: Check selenium version installed:
        #   https://stackoverflow.com/a/76915412/6929343
        #       ~/.cache/selenium

        menu.add_separator()

        #menu.add_command(label="Play Song № " + no, font=g.FONT,
        #                 command=lambda: self.you_tree_play(item))

        # TODO: Check Selenium Installed
        #       Check ChromeDriver installed & matches version
        #       Check Firefox Driver installed

        #if XDOTOOL_INSTALLED and WMCTRL_INSTALLED:
        #    menu.add_command(label="Smart Play № " + no, font=g.FONT,
        #                     command=lambda: self.you_tree_smart_play(item))

        menu.add_command(label="Copy Link № " + no, font=g.FONT,
                         command=lambda: self.youTreeCopyLink(item))
        menu.add_separator()

        menu.add_command(label="Copy LRC Search № " + no, font=g.FONT,
                         command=lambda: self.youTreeCopySearchLrc(item))
        menu.add_command(label="Paste LRC № " + no, font=g.FONT,
                         command=lambda: self.youTreePasteLrc(item))
        # TODO: Next two appear only when LRC dictionary exists
        menu.add_command(label="View LRC № " + no, font=g.FONT,
                         command=lambda: self.youTreeViewLrc(item))
        menu.add_command(label="Delete LRC № " + no, font=g.FONT,
                         command=lambda: self.youTreeDeleteLrc(item))
        menu.add_separator()

        menu.add_command(label="Set Debug Level", font=g.FONT,
                         command=lambda: self.youSetDebug())
        menu.add_command(label="Ignore click", font=g.FONT,
                         command=lambda: self.youClosePopup(menu, item))

        menu.tk_popup(event.x_root, event.y_root)
        menu.bind("<FocusOut>", lambda _: self.youClosePopup(menu, item))
        # '_' prevents: TypeError: <lambda>() takes no arguments (1 given)

    @staticmethod
    def youClosePopup(menu, _item):
        """ Close the YouTube Playlist popup menu """
        menu.unpost()  # Remove popup menu

    def youClosePlayLrc(self, *_args):
        """ Close YouTube Playlist or Lrc Frame depending on active frame. """

        # Is Lrc Frame active?
        if self.hasLrcForVideo:
            self.youLrcFrame.grid_remove()  # Remove LRC frame
            self.youTreeFrame.grid()  # Restore Treeview frame
            self.hasLrcForVideo = None
            self.youSetCloseButton()
            return

        # Normal close window and destroy top
        if self.driver:
            self.driver.quit()
        self.reset()

    def you_tree_play(self, item):
        """ Play song highlighted in YouTube treeview.
            2023-12-02 - Not called by popup menu.
        """
        title = "NOT IMPLEMENTED."
        text = "Calling YouTube regular play"
        message.ShowInfo(self.top, title, text, icon='warning',
                         thread=self.get_thread_func)
        ndx = int(item)
        webbrowser.open_new(self.listYouTube[ndx]['link'])

    def you_tree_smart_play(self):
        """ Smart Play single YouTube song for unopened Playlist.
            2023-12-02 - Not called by popup menu.
        """
        title = "NOT IMPLEMENTED."
        text = "Calling YouTube regular play"
        message.ShowInfo(self.top, title, text, icon='warning',
                         thread=self.get_thread_func)
        ndx = int(item)
        webbrowser.open_new(self.listYouTube[ndx]['link'])

    def you_tree_play_all(self, item):
        """ Play all songs in treeview (Entire YouTube Playlist). 
            NOT TESTED YET (October 16, 2023)
        """

        title = "WARNING: Experimental feature"
        text = "Currently this features moves YouTube from right to left monitor."
        # message.ShowInfo(self.top, title, text, icon='warning',
        #                 thread=self.get_thread_func)
        mon = monitor.Monitors()  # Monitors class list of dicts
        # Start windows
        start_wins = mon.get_all_windows()

        ndx = int(item)
        webbrowser.open_new(self.listYouTube[ndx]['link'])
        time.sleep(1.0)  # TODO: Loop for 30 seconds until list changes
        end_wins = mon.get_all_windows()

        if not len(start_wins) + 1 == len(end_wins):
            print("Could not find new window")
            print("start/end window count:", len(start_wins), len(end_wins))
            return

        win_list = list(set(end_wins) - set(start_wins))
        window = win_list[0]
        #print("\n window list:", window)
        # [Window(number=130028740L, name='Mozilla Firefox', x=1920, y=24,
        #         width=1728, height=978)]

        str_win = str(window.number)  # should remove L in python 2.7.5+
        int_win = int(str_win)  # https://stackoverflow.com/questions
        hex_win = hex(int_win)  # /5917203/python-trailing-l-problem


        # If last usage was full screen, reverse it
        net_states = os.popen('xprop -id ' + str_win).read().strip()
        #print("net_states:", net_states)
        if "_NET_WM_STATE_FULLSCREEN" in net_states:
            os.popen('wmctrl -ir ' + hex_win +
                     ' -b toggle,fullscreen')  # DOES NOT WORK !!!
        # Remove maximized, don't have to test first
        os.popen('wmctrl -ir ' + hex_win +
                 ' -b remove,maximized_vert,maximized_horz')
        #os.popen('wmctrl - r: ACTIVE: -e 0, 300, 168, 740, 470')

        new_x = new_y = 30  # Move to top left monitor @ 30,30 (x, y)
        os.popen('xdotool windowmove ' + hex_win + ' ' +
                 str(new_x) + ' ' + str(new_y))
        #time.sleep(0.5)  # After window move, need a little time
        #message.ShowInfo(self.top, title, text, icon='warning',
        #                 thread=self.get_thread_func)

        # Could remove target window's above setting (Always On Top):
        #   os.popen('wmctrl -ir ' + trg_win + ' -b toggle,above')

        # Make full screen. Have to reverse before closing because setting
        # remembered by firefox for next window open

        os.popen('wmctrl -ir ' + hex_win + ' -b add,maximized_vert')
        os.popen('wmctrl -ir ' + hex_win + ' -b add,maximized_horz')
        # Making above removes system title bar
        os.popen('wmctrl -ir ' + hex_win + ' -b add,above')
        # Move to screen center and click to play
        #os.popen('xdotool mousemove 1860 900')  # 1920/2 x 1080/2
        time.sleep(7.0)  # Time for YouTube to load up and build page
        #os.popen('xdotool click --window ' + hex_win + ' --delay 5000 1')
        os.popen('xdotool key f')  # Full Screen
        os.popen('xdotool key space')  # Start playing

        # Selenium to watch for skip ad button to appear and click it
        # sudo apt install python-selenium

        web = webbrowser.get()
        print("browser name:", web.name)
        if web.name.startswith("xdg-open"):
            xdg_browser = os.popen("xdg-settings get default-web-browser"). \
                read().strip()
            if "FIREFOX" in xdg_browser.upper():
                self.driver = webdriver.Firefox()
                print("driver = webdriver.Firefox()")
            if "CHROME" in xdg_browser.upper():
                self.driver = webdriver.Chrome()
                print("driver = webdriver.Chrome()")

# Playlists Class YouTube Video Player

    def youSmartPlaySong(self, item):
        """
        Build: https://www.youtube.com/watch
            ?v=0n3cUPTKnl0
            &list=PLthF248A1c68TAKl5DBskfJ2fwr1sk9aM
            &index=17

        :param item: item (iid) in YouTube playlist
        :return: None
        """

        # Shared function to start playing at playlist index
        self.youPlaylistIndexStartPlay(item)

    def youSmartPlaySample(self, item):
        """ Start playing video then advance to middle of song
        :param item: item (iid) in YouTube playlist
        :return: None
        """

        self.youPlaylistIndexStartPlay(item)
        # Advance to middle of song
        duration_str = self.dictYouTube['duration']
        duration = int(tmf.get_sec(duration_str))
        mid_start = (duration / 2) - 8
        if mid_start > 0:
            self.driver.execute_script(
                'document.getElementsByTagName("video")[0].currentTime += ' +
                str(mid_start) + ';')

    def youPlaylistIndexStartPlay(self, item, restart=False):
        """ Shared by youSmartPlaySong and youSmartPlaySample methods

            Build full_link containing:
                https://www.youtube.com/watch
                ?v=0n3cUPTKnl0
                &list=PLthF248A1c68TAKl5DBskfJ2fwr1sk9aM
                &index=17

            self.act_description =
            	https://www.youtube.com/
            	playlist?list=PLthF248A1c68TAKl5DBskfJ2fwr1sk9aM

        :param item: item (iid) in YouTube playlist
        :param restart: End of Playlist, restart from beginning.
        :return: None
        """
        
        # Is last video playing in full screen?
        self.youForceVideoFull = self.youCheckVideoFullScreen()

        ndx = int(item)
        self.dictYouTube = self.listYouTube[ndx]
        link = self.dictYouTube['link']
        youPlaylistName = self.act_description.split("list=")[1]
        full_link = link + "&list=" + youPlaylistName
        full_link += "&index=" + item

        self.driver.get(full_link)
        status = self.youWaitMusicPlayer(debug=True, startup=True)
        while status == 99 or self.youCheckAdRunning():
            self.youVolumeOverride(True)  # Ad playing override
            self.driver.back()
            self.driver.forward()
            status = self.youWaitMusicPlayer(debug=True, startup=True)

        if restart:
            self.youPrint("Forced refresh at beginning:", full_link)
            # EXPECT:&list=PLthF248A1c68TAKl5DBskfJ2fwr1sk9aM
            # SHOWN: &list=PLthF248A1c68TAKl5DBskfJ2fwr1sk9aM
            # 01:20:38.8 STARTING Playlist - Song № 1     | a-Xfv64uhMI
            # https://www.youtube.com/watch?v=a-Xfv64uhMI&list=PLthF248A1c68TAKl5DBskfJ2fwr1sk9aM&index=1
            # 01:20:38.0 STARTING Playlist - Song № 1     | nYSdFra_Amc
            # 01:24:59.6 STARTING Playlist - Song № 1     | kuoZTxfe6tA
            time.sleep(2.0)
            self.driver.refresh()

    def youSmartPlayAll(self):
        """ Smart Play entire YouTube Playlist.

            1. youOpenSelenium() Get browser (web) and Open browser (self.driver)
            2. Open YouTube Playlist, Move window, 'Play all', full screen
            3. Loop forever playing all songs - self.youMonitorLinks()
            4. self.youMonitorPlayerStatus() Update progress and skip Ads

        TODO:
            Resume from suspend after day at work results in 443 ads. Set limit
                of 3 ads then interrupt and self.driver.get(video)

        """

        ''' 1. youOpenSelenium() Get browser (web) and Open browser (self.driver) '''
        self.driver, window = self.youOpenSelenium()
        if not window:
            if self.driver:
                self.driver.quit()
            return  # No window tuple, cannot proceed even if self.driver succeeded

        ''' 2. Open YouTube Playlist, Move window, 'Play all', full screen '''
        if not self.youPlayAllFullScreen(window):
            print("youPlayAllFullScreen(window) Failed!")
            self.driver.quit()
            return

        self.youLastLink = ""  # When link changes highlight row in self.you_tree
        self.durationYouTube = 0.0  # Extra insurance
        self.resetYouTubeDuration()
        self.buildYouTubeDuration()
        self.isSmartPlayYouTube = True  # Smart Play is active
        self.youDebug = self.act_size  # Print Debug level from last save

        ad_conflict_count = 0  # Player status -1 but No Ad visible (yet).
        lastHousekeepingTime = time.time()  # Check resume every minute

        ''' 3. Loop forever playing all songs - self.youMonitorLinks() '''
        while True:
            if not self.top:
                return False  # Closing down

            # play top refresh + .after(16). With this, CPU load is 3.5% not 6%
            if not lcs.fast_refresh(tk_after=True):
                if self.driver:
                    self.driver.quit()
                self.isSmartPlayYouTube = False
                self.driver = None
                return False

            ''' Housekeeping every minute 
                Respond to prompt: "Video paused. Continue Watching?" '''
            now = time.time()
            if now - lastHousekeepingTime > 60.0:
                lastHousekeepingTime = now
                self.youHousekeeping()

            ''' Check if Browser Address Bar URL link has changed. '''
            link = self.youMonitorLinks()
            if link is None:
                continue  # Error getting link

            # Get YouTube Music Player Status
            player_status = self.youGetPlayerStatus()
            if player_status is None:
                player_status = last_player_status  # Use last know state
                self.youPrint("player_status is <Type> 'None'!",
                              "Resorting to last status:", player_status)

            ''' 4. self.youMonitorPlayerStatus() Update progress and skip Ads '''
            self.youMonitorPlayerStatus(player_status, debug=False)

            self.youLastLink = link
            last_player_status = player_status

            # Continue beyond this point when YouTube Ad is running
            # self.driver.find_element(By.CSS_SELECTOR, ".ytp-ad-duration-remaining")
            if not self.youCheckAdRunning():
                if player_status == -1:
                    ad_conflict_count += 1
                continue  # Skip while loop below

            if ad_conflict_count > 0:
                self.youPrint("player_status == '-1' but no Ad running. Count:",
                              ad_conflict_count)
                ad_conflict_count = 0  # Reset for next group count

    def youOpenSelenium(self):
        """ Create Selenium browser instance
            Create Selenium self.driver instance
            Get Window ID for self.driver instance

        :return self.driver, window: Selenium self.driver and WM window tuple
        """

        self.driver = self.youWindow = None
        CHROME_DRIVER_VER = "chromedriver108"
        # TODO replace 108 with actual version
        # $ google-chrome --version
        # Google Chrome 108.0.5359.124
        ver = os.popen("google-chrome --version").read().strip()
        ver = ver.split()
        ver = ver[2].split(".")[0]
        CHROME_DRIVER_VER = CHROME_DRIVER_VER.replace("108", ver)
        CHROME_DRIVER_PATH = \
            g.PROGRAM_DIR + CHROME_DRIVER_VER + os.sep + "chromedriver"
        self.youPrint("CHROME_DRIVER_PATH:", CHROME_DRIVER_PATH, nl=True)

        web = webbrowser.get()
        #print("browser name:", web.name)  # xdg-open

        try:
            mon = monitor.Monitors()  # Monitors class list of dicts
            # Start windows
            end_wins = start_wins = mon.get_all_windows()
        except Exception as err:
            self.youPrint("youOpenSelenium() Exception:", err)
            return self.driver, window

        if web.name.startswith("xdg-open"):
            xdg_browser = os.popen("xdg-settings get default-web-browser"). \
                read().strip()
            if "FIREFOX" in xdg_browser.upper():
                """
                selenium has been replaced by marionette:

                https://firefox-source-docs.mozilla.org/python/marionette_driver.html

                For ubuntu:

                https://stackoverflow.com/a/39536091/6929343
                https://stackoverflow.com/questions/43272919/difference-between-webdriver-firefox-marionette-webdriver-gecko-driver
                https://stackoverflow.com/questions/38916650/what-are-the-benefits-of-using-marionette-firefoxdriver-instead-of-the-old-selen/38917100#38917100

                """
                self.driver = webdriver.Chrome(CHROME_DRIVER_PATH)
                    # Optional argument, if not specified will search path.

                # Automated Test Software message suppression (Doesn't work)
                # https://stackoverflow.com/a/71257995/6929343
                chromeOptions = webdriver.ChromeOptions()
                chromeOptions.add_experimental_option("excludeSwitches", ['enable-automation']);

                """
                    WebDriverException: Message: 'chromedriver' executable 
                    needs to be in PATH. Please see 
                    https://sites.google.com/a/chromium.org/chromedriver/home
                    New download links:
                    https://sites.google.com/chromium.org/driver/downloads?authuser=0
                """
            if "CHROME" in xdg_browser.upper():
                self.driver = webdriver.Chrome(CHROME_DRIVER_PATH)
                    # Optional argument, if not specified will search path.

                # Automated Test Software message suppression (Doesn't work)
                # https://stackoverflow.com/a/71257995/6929343
                chromeOptions = webdriver.ChromeOptions()
                chromeOptions.add_experimental_option("excludeSwitches", ['enable-automation']);

        start = time.time()
        while len(end_wins) == len(start_wins):
            end_wins = mon.get_all_windows()
            if time.time() - start > 5.0:
                title = "Could not start Browser"
                text = "Browser would not start.\n"
                text += "Check console for error\n"
                text += "messages and try again."
                message.ShowInfo(self.top, title, text, icon='error',
                                 thread=self.get_thread_func)
                return self.driver, self.youWindow

        if not len(start_wins) + 1 == len(end_wins):
            title = "Could not start Browser"
            text = "Old Window count:" + str(len(start_wins)) + "\n\n"
            text += "New Window count:" + str(len(end_wins)) + "\n\n"
            text += "There should only be one new window.\n"
            text += "Check console for error messages.\n"
            message.ShowInfo(self.top, title, text, icon='error',
                             thread=self.get_thread_func)
            return self.driver, self.youWindow

        win_list = list(set(end_wins) - set(start_wins))
        self.youWindow = win_list[0]

        return self.driver, self.youWindow

    def youPlayAllFullScreen(self, window):
        """ Open YouTube Playlist, Move window, 'Play all', full screen
            self.act_description =
            	https://www.youtube.com/
            	playlist?list=PLthF248A1c68TAKl5DBskfJ2fwr1sk9aM
        """

        self.driver.get(self.act_description)  # Open Youtube playlist
        #print("self.act_description   :", self.act_description)
        #print("self.driver.current_url:", self.driver.current_url)

        if self.act_description != self.driver.current_url:
            print("youPlayAllFullScreen(window) - Open YouTube Playlist Failed!")
            return False

        # print("\n window list:", window)
        # [Window(number=130028740L, name='Mozilla Firefox', x=1920, y=24,
        #         width=1728, height=978)]

        str_win = str(window.number)  # should remove L in python 2.7.5+
        int_win = int(str_win)  # https://stackoverflow.com/questions
        hex_win = hex(int_win)  # /5917203/python-trailing-l-problem
        #print("\n str_win:", str_win, "int_win:", int_win, "hex_win:", hex_win)

        # If last usage was full screen, reverse it
        net_states = os.popen('xprop -id ' + str_win).read().strip()
        # print("net_states:", net_states)
        if "_NET_WM_STATE_FULLSCREEN" in net_states:
            self.youFullScreen = True  # Was YouTube full screen before?
            os.popen('wmctrl -ir ' + hex_win +
                     ' -b toggle,fullscreen')  # DOES NOT WORK !!!

        # Remove maximized, don't worry if not maximized already
        os.popen('wmctrl -ir ' + hex_win +
                 ' -b remove,maximized_vert,maximized_horz')

        new_x = new_y = 30  # Move to top left monitor @ 30,30 (x, y)
        os.popen('xdotool windowmove ' + hex_win + ' ' +
                 str(new_x) + ' ' + str(new_y))

        # Could remove target window's above setting (Always On Top):
        #   os.popen('wmctrl -ir ' + trg_win + ' -b toggle,above')

        self.driver.maximize_window()
        # Making "Above" removes system title bar
        os.popen('wmctrl -ir ' + hex_win + ' -b add,above')

        # Automated Test Software message suppression (Doesn't work)
        # https://stackoverflow.com/a/71257995/6929343
        # Manually position mouse over "Automated Test Software" message
        os.popen('xdotool mousemove 1890 140')  # Assume top-left monitor Full HD
        # Send left click (1) after 50ms delay
        os.popen('xdotool click --window ' + hex_win + ' --delay 50 1')
        #os.popen('xdotool windowactivate ' + hex_win)  # Verify activate needed
        #os.popen('xdotool click 1')

        byline = self.driver.find_element(By.CLASS_NAME, 'byline-item')
        """ byline-item has video count in YouTube Playlist
            <span dir="auto" class="style-scope yt-formatted-string">47</span>
            <span dir="auto" class="style-scope yt-formatted-string"> videos</span>
            XPATH:
            /html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse[2]/
                ytd-playlist-header-renderer/div/div[2]/div[1]/div/div[1]/div[1]/
                ytd-playlist-byline-renderer/div/yt-formatted-string[1] """
        video_count = byline.get_attribute('innerHTML').split("</span>")[0]
        video_count = video_count.split(">")[1]

        self.youPrint("youPlayAllFullScreen() video_count:", video_count,
                      lv=8, nl=True)

        fname2 = self.nameYouTube.replace(".csv", ".private")
        self.privateYouTube = ext.read_into_string(fname2)
        if self.privateYouTube:  # Saved count of private videos in playlist
            private_links = int(self.privateYouTube)
        else:
            private_links = 0

        if int(video_count) - private_links != len(self.listYouTube):
            title = "YouTube Playlist Needs Updating"
            text = "mserve copy of YouTube Playlist is out-of-date.\n\n"
            text += "YouTube Playlist count: " + video_count + "\n\n"
            text += "mserve Playlist count:  " + str(len(self.listYouTube))
            message.ShowInfo(self.top, title, text, icon='warning',
                             thread=self.get_thread_func)
            start = time.time()  # Track elapsed time

            self.youShowUnavailableVideos()  # When hamburger menu exists

            self.youValidLinks, private_links, listVideos = \
                self.youGetAllGoodLinks(video_count)

            good_times, listTimes = self.youGetAllGoodTimes(self.youValidLinks)

            # Join two lists in same format as self.listYouTube
            for i, video in enumerate(listVideos):
                listVideos[i] = listVideos[i] + ';' + listTimes[i]

            #print("listVideos[0]:", listVideos[0],
            #      "listVideos[-1]:", listVideos[-1])

            self.mergeYouTubePlaylist(listVideos, private_links)
            self.displayYouTubePlaylist()  # Recreate Treeview see Song #19 added
            self.youShowUnavailableVideos(show=False)  # When hamburger menu exists
            self.youPrint("elapsed time:", time.time() - start)

        # Find and click to "Play all" button
        if not self.youDriverClick('link_text', "Play all"):
            # TODO: Fails when buried behind Firefox running full screen
            self.youPrint("Play all button click FAILED!")
            os.popen('xdotool mousemove 500 790')
            # Send left click (1) after 3 second delay
            time.sleep(3.0)  # Wait 3 seconds
            os.popen('xdotool click --window ' + hex_win + ' 1')
            #os.popen('xdotool windowactivate ' + hex_win)  # Verify activate needed
            #os.popen('xdotool click 1')  # Click on play all button

        # Skip commercial with driver.back() then driver.forward()
        status = self.youWaitMusicPlayer(debug=True, startup=True)
        while status == 99 or self.youCheckAdRunning():
            self.youVolumeOverride(True)  # Ad playing override
            self.driver.back()
            self.driver.forward()
            # Get player status without debug which can spam console
            status = self.youWaitMusicPlayer(startup=True)

        player_status = self.youGetPlayerStatus()
        if not player_status:
            self.driver.quit()
            title = "Smart Play FAILED"
            text = "Play All did not work. Try again later.\n\n"
            text += "Check console for messages."
            message.ShowInfo(self.top, title, text, icon='error',
                             thread=self.get_thread_func)
            return False

        ''' Make YouTube full screen '''
        actions = ActionChains(self.driver)
        actions.send_keys('f')  # work around self.driver.fullscreen_window()
        actions.perform()
        # self.driver.fullscreen_window()  # Doesn't work
        # driver.fullscreen_window()
        #   File "/home/rick/python/mserve.py", line 15834, in youTreeSmartPlayAll
        #     self.driver.fullscreen_window()
        # AttributeError: 'WebDriver' object has no attribute 'fullscreen_window'

        return True

    def youCheckVideoFullScreen(self):
        """ Check if YouTube Browser Window is currently full screen
            Use new self.youWindow variable. Called during startup and
            when video link changes (new video started)

            There is Full Screen in Desktop Manager (DM):

                _NET_WM_STATE(ATOM) =
                    _NET_WM_STATE_MAXIMIZED_VERT,
                    _NET_WM_STATE_MAXIMIZED_HORZ,
                    _NET_WM_STATE_FULLSCREEN,
                    _NET_WM_STATE_ABOVE

            DM not full screen:

                _NET_WM_STATE(ATOM) =

            To check if Video taking all of window in YouTube:

                full_screen = True
                try:
                    path = '//input[@id="search"]'
                    search_area = self.driver.find_element(By.XPATH, path)
                    full_screen = search_area.is_displayed()
                except:
                    print("Bad element path or too soon:", path)

        """
        # print("\n Browser Window:", self.youWindow)
        # [Window(number=130028740L, name='Mozilla Firefox', x=1920, y=24,
        #         width=1728, height=978)]

        str_win = str(self.youWindow.number)  # Remove L in python 2.7.5+
        int_win = int(str_win)  # https://stackoverflow.com/questions
        hex_win = hex(int_win)  # /5917203/python-trailing-l-problem
        #print("\n str_win:", str_win, "int_win:", int_win, "hex_win:", hex_win)

        # If last usage was full screen, reverse it
        net_states = os.popen('xprop -id ' + str_win).read().strip()
        # print("net_states:", net_states)
        self.youFullScreen = None  # Was YouTube full screen before?
        if "_NET_WM_STATE_FULLSCREEN" in net_states:
            self.youFullScreen = True  # YouTube is full screen

        self.youPrint("Full screen state:", self.youFullScreen)
        #self.youPrint("str_win:", str_win, "net_states:", net_states)
        self.youPrint("Window:", self.youWindow)

        self.youForceVideoFull = False
        if not self.youFullScreen:
            self.youPrint("self.youForceVideoFull:", self.youForceVideoFull)
            return self.youForceVideoFull

        try:
            # https://stackoverflow.com/a/72820435/6929343
            path = '//input[@id="search"]'
            search_area = self.driver.find_element(By.XPATH, path)
            self.youForceVideoFull = search_area.is_displayed() is not True
            self.youPrint("self.youForceVideoFull:", self.youForceVideoFull)
        except Exception as err:
            self.youPrint("youCheckVideoFullScreen() Exception:", err)
            print("Bad XPATH name or need to wait:", path)

        return self.youForceVideoFull

    def youGetAllGoodLinks(self, video_count):
        """ Get all the good links and private links in playlist. Scrolling
            is necessary after 100 video chunks.

        :return: good_links, private_links, listVideos
        """

        self.gotAllGoodLinks = None
        good_links, private_links, listVideos = self.youGetBatchGoodLinks()

        # last_good_links is stop-gap measure until show hidden videos
        # button is clicked on player hamburger menu.
        last_good_links = good_links
        # When more than 100 videos, need to scroll
        while good_links < int(video_count) - private_links:
            # HTML By.ID Looping forever when 242 < 243
            try:
                # Need wait until visible when playing random song
                wait = WebDriverWait(self.driver, 10)
                id_name = 'items'  # _located
                # element = self.driver.find_element_by_id(id_name)
                item_list = wait.until(EC.presence_of_element_located((
                    By.ID, id_name)))

                #print("item_list:", item_list)
                dictItem = self.driver.execute_script(
                    'var items = {}; \
                    for (index = 0; index < \
                    arguments[0].attributes.length; ++index) \
                    { items[arguments[0].attributes[index].name] = \
                    arguments[0].attributes[index].value }; \
                    return items;',
                    item_list)
                #print("dictItem:", dictItem)
                # dictItem: {u'class': u'playlist-items style-scope
                #           ytd-playlist-panel-renderer', u'id': u'items'}

                ActionChains(self.driver).move_to_element(item_list)
                # self.driver.send_keys(Keys.END) fails
                actions = ActionChains(self.driver)
                actions.send_keys(Keys.END)
                actions.perform()
                time.sleep(1.5)  # Oct 8/23: Verified necessary!
                good_links, private_links, listVideos = self.youGetBatchGoodLinks()
                if good_links == last_good_links:
                    # Oct 8/23 - Message no longer appears for private videos
                    title = "Unavailable Videos"
                    text = "YouTube reporting more videos than scrollable.\n"
                    text += 'Check for deleted videos and change this code.'
                    message.ShowInfo(self.top, title, text, icon='error',
                                     thread=self.get_thread_func)
                    break
                last_good_links = good_links
            except WebDriverException as err:
                title = "Selenium WebDriverException"
                text = str(err)
                message.ShowInfo(self.top, title, text, icon='error',
                                 thread=self.get_thread_func)
                self.youPrint("id_name = 'items' WebDriverException:\n", err)
                break
                # return None

        self.gotAllGoodLinks = True
        return good_links, private_links, listVideos

    def youGetBatchGoodLinks(self):
        """
            TODO: Devine item number to click on.
                  Note unavailable video setting.
                  Note stale element errors and video skipped.
        :return: good_links, private_links, listVideos
        """

        listVideos = []
        good_links = private_links = bad_links = 0
        links = self.driver.execute_script(
            "return document.querySelectorAll('a')")

        # ERROR:
        # CHROME_DRIVER_PATH: /home/rick/python/chromedriver108/chromedriver
        #
        # 07:11:59.3 youWaitMusicPlayer 930.478 ms | Null: 0  | Paused: 0  | Starting: 5  | Idle: 5
        #
        # 07:12:00.1 STARTING Playlist - Song № 1     | a-Xfv64uhMI
        #
        # 07:16:08.3 STARTING Playlist - Song № 2     | HnilTXUQtag
        # 07:16:08.7 Ad visible. Player status: 5
        # 07:16:10.8 MicroFormat found after: 0.4     | HnilTXUQtag
        # CHROME_DRIVER_PATH: /home/rick/python/chromedriver108/chromedriver
        # 07:17:23.8 Clicking xpath: //*[@id="page-manager"]/ytd-browse/
        #   ytd-playlist-header-renderer/div/div[2]/div[1]/div/div[1]/div[2]/ytd-menu-renderer
        # 07:17:24.4 Clicking 'Show unavailable videos': Show unavailable videos
        # Exception in Tkinter callback
        # Traceback (most recent call last):
        #   File "/usr/lib/python2.7/lib-tk/Tkinter.py", line 1540, in __call__
        #     return self.func(*args)
        #   File "/home/rick/python/mserve.py", line 15698, in <lambda>
        #     command=lambda: self.youTreeSmartPlayAll())
        #   File "/home/rick/python/mserve.py", line 15925, in youTreeSmartPlayAll
        #     if not self.youPlayAllFullScreen(window):
        #   File "/home/rick/python/mserve.py", line 16172, in youPlayAllFullScreen
        #     self.youGetAllGoodLinks(video_count)
        #   File "/home/rick/python/mserve.py", line 16237, in youGetAllGoodLinks
        #     good_links, private_links, listVideos = self.youGetBatchGoodLinks()
        #   File "/home/rick/python/mserve.py", line 16311, in youGetBatchGoodLinks
        #     link)
        #   File "/usr/lib/python2.7/dist-packages/selenium/webdriver/remote/webdriver.py", line 429, in execute_script
        #     {'script': script, 'args':converted_args})['value']
        #   File "/usr/lib/python2.7/dist-packages/selenium/webdriver/remote/webdriver.py", line 201, in execute
        #     self.error_handler.check_response(response)
        #   File "/usr/lib/python2.7/dist-packages/selenium/webdriver/remote/
        #       errorhandler.py", line 181, in check_response
        #     raise exception_class(message, screen, stacktrace)
        # StaleElementReferenceException: Message: stale element reference: element is not attached to the page document
        #   (Session info: chrome=108.0.5359.124)
        #   (Driver info: chromedriver=108.0.5359.71 (1e0e3868ee06e91ad636a874420e3ca3ae3756ac-refs/
        #       branch-heads/5359@{#1016}),platform=Linux 4.14.216-0414216-generic x86_64)
        for link in links:
            # StaleElementReferenceException:
            #   https://stackoverflow.com/a/40070927/6929343
            #       wait.until(ExpectedConditions.stalenessOf(whatever element));
            try:
                dictLink = self.driver.execute_script(
                    'var items = {}; \
                    for (index = 0; index < \
                    arguments[0].attributes.length; ++index) \
                    { items[arguments[0].attributes[index].name] = \
                    arguments[0].attributes[index].value }; \
                    return items;',
                    link)
            except StaleElementReferenceException:
                print("Stale element")
                continue

            link_url = dictLink.get('href', None)
            link_title = dictLink.get('title', None)
            class_list = dictLink.get('class', None)

            if u'[Private video]' == link_title:
                # Link # 119 is private video, get keys
                self.youPrint("link_url  :", link_url)
                self.youPrint("link_title:", link_title)
                self.youPrint("class_list:", class_list)
                private_links += 1
                continue
                #print("\ndictLink:", dictLink)

            if u'[Deleted video]' == link_title:
                # Link # 6 is deleted video, get keys
                self.youPrint("link_url  :", link_url)
                self.youPrint("link_title:", link_title)
                self.youPrint("class_list:", class_list)
                private_links += 1
                continue
                #print("\ndictLink:", dictLink)

            if not link_url or not link_title or not class_list or \
                    "style-scope ytd-playlist-video-renderer" \
                    not in class_list or len(link_title) < 1:
                bad_links += 1
                continue

            good_links += 1
            part = link_url.split("&list=")[0]
            listVideos.append(link_title + ";https://www.youtube.com" + part)

        self.youPrint("good_links:", good_links, "bad_links:", bad_links)

        return good_links, private_links, listVideos

    def youShowUnavailableVideos(self, show=True):
        """

        WHEN MENU BUTTON APPEARS:

document.querySelector("#page-manager > ytd-browse > ytd-playlist-header-renderer
> div > div.immersive-header-content.style-scope.ytd-playlist-header-renderer
> div.thumbnail-and-metadata-wrapper.style-scope.ytd-playlist-header-renderer
> div > div.metadata-action-bar.style-scope.ytd-playlist-header-renderer
> div.metadata-buttons-wrapper.style-scope.ytd-playlist-header-renderer
> ytd-menu-renderer")

        WHEN MENU BUTTON APPEARS:

//*[@id="page-manager"]/ytd-browse/ytd-playlist-header-renderer/div/div[2]/div[1]/div/div[1]/div[2]/ytd-menu-renderer

        <ytd-menu-renderer force-icon-button="" tonal-override=""
        class="style-scope ytd-playlist-header-renderer"
        safe-area=""><!--css-build:shady--><!--css-build:shady-->
        <div id="top-level-buttons-computed"
        class="top-level-buttons style-scope ytd-menu-renderer"></div>
        <div id="flexible-item-buttons"
        class="style-scope ytd-menu-renderer"></div>
        <yt-icon-button id="button"
        class="dropdown-trigger style-scope ytd-menu-renderer"
        style-target="button" hidden="">
        <!--css-build:shady--><!--css-build:shady-->
        <button id="button" class="style-scope yt-icon-button"
        aria-label="Action menu"><yt-icon class="style-scope ytd-menu-renderer">
        <!--css-build:shady--><!--css-build:shady-->
        <yt-icon-shape class="style-scope yt-icon"><icon-shape
        class="yt-spec-icon-shape"><
        div style="width: 100%; height: 100%; fill: currentcolor;">
        <svg enable-background="new 0 0 24 24" height="24"
        viewBox="0 0 24 24" width="24" focusable="false"
        style="pointer-events: none; display: block; width: 100%; height: 100%;">
        <path d="M12 16.5c.83 .... 1.5-1.5-.67-1.5-1.5-1.5-1.5.67-1.5 1.5z">
        </path></svg></div></icon-shape></yt-icon-shape></yt-icon></button>
        <yt-interaction id="interaction" class="circular style-scope yt-icon-button">
        <!--css-build:shady--><!--css-build:shady-->
        <div class="stroke style-scope yt-interaction"></div>
        <div class="fill style-scope yt-interaction"></div>
        </yt-interaction></yt-icon-button><yt-button-shape id="button-shape"
        version="modern" class="style-scope ytd-menu-renderer">
        <button class="yt-spec-button-shape-next
        yt-spec-button-shape-next--tonal yt-spec-button-shape-next--overlay
        yt-spec-button-shape-next--size-m yt-spec-button-shape-next--icon-button "
        aria-label="Action menu" title="" style="">
        <div class="yt-spec-button-shape-next__icon" aria-hidden="true">
        <yt-icon style="width: 24px; height: 24px;">
        <!--css-build:shady--><!--css-build:shady-->
        <yt-icon-shape class="style-scope yt-icon">
        <icon-shape class="yt-spec-icon-shape">
        <div style="width: 100%; height: 100%; fill: currentcolor;">
        <svg enable-background="new 0 0 24 24" height="24" viewBox="0 0 24 24"
        width="24" focusable="false" style="pointer-events: none;
        display: block; width: 100%; height: 100%;">
        <path d="M12 16.5c.83 ...  1.5-1.5-.67-1.5-1.5-1.5-1.5.67-1.5 1.5z"></path>
        </svg></div></icon-shape></yt-icon-shape></yt-icon></div>
        <yt-touch-feedback-shape style="border-radius: inherit;">
        <div class="yt-spec-touch-feedback-shape
        yt-spec-touch-feedback-shape--overlay-touch-response" aria-hidden="true">
        <div class="yt-spec-touch-feedback-shape__stroke" style=""></div>
        <div class="yt-spec-touch-feedback-shape__fill" style=""></div></div>
        </yt-touch-feedback-shape></button></yt-button-shape></ytd-menu-renderer>
        :return:
        """
        query = "#page-manager > ytd-browse > ytd-playlist-header-renderer \
            > div > \
            div.immersive-header-content.style-scope.ytd-playlist-header-renderer > \
            div.thumbnail-and-metadata-wrapper.style-scope.ytd-playlist-header-renderer \
            > div > \
            div.metadata-action-bar.style-scope.ytd-playlist-header-renderer > \
            div.metadata-buttons-wrapper.style-scope.ytd-playlist-header-renderer \
            > ytd-menu-renderer"

        xpath = '//*[@id="page-manager"]/ytd-browse/ytd-playlist-header-renderer'
        xpath += "/div/div[2]/div[1]/div/div[1]/div[2]/ytd-menu-renderer"
        if show:
            link_text = "Show unavailable videos"
        else:
            link_text = "Hide unavailable videos"
        # Reverse is "Hide unavailable videos"
        result1 = result2 = None
        try:
            result1 = self.driver.find_element(By.XPATH, xpath)
        except Exception as err:
            self.youPrint("Exception reading menu hamburger:\n", err)

        #print("result1:", result1, "result2:", result2)
        # Hamburger menu is hidden unless action can be taken
        if result1 and result1.is_displayed():
            self.youPrint("Clicking xpath:", xpath)
            self.youDriverClick("xpath", xpath)
            try:
                # Button is hidden until hamburger clicked
                result2 = self.driver.find_element(By.LINK_TEXT, link_text)
            except Exception as err:
                self.youPrint("Exception 'Show unavailable videos':\n", err)

        if result2:
            self.youPrint("Clicking: '" + link_text + "'.")
            self.youDriverClick("link_text", link_text)
            if self.youUnavailableShown is None:
                self.youUnavailableShown = True
        elif self.youUnavailableShown:
            self.youPrint("Cannot click: '" + link_text + "'.")
            self.youPrint("link_text not found!")
            self.youUnavailableShown = None

        """ Button to click:
        
        <a class="yt-simple-endpoint style-scope ytd-menu-navigation-item-renderer" tabindex="-1" href="/playlist?list=PLthF248A1c69kNWZ9Q39Dow3S2Lxp74mF">
    <tp-yt-paper-item class="style-scope ytd-menu-navigation-item-renderer" style-target="host" role="option" tabindex="0" aria-disabled="false"><!--css-build:shady-->
      <yt-icon class="style-scope ytd-menu-navigation-item-renderer"><!--css-build:shady--><!--css-build:shady--><yt-icon-shape class="style-scope yt-icon"><icon-shape class="yt-spec-icon-shape"><div style="width: 100%; height: 100%; fill: currentcolor;"><svg height="24" viewBox="0 0 24 24" width="24" focusable="false" style="pointer-events: none; display: block; width: 100%; height: 100%;"><path d="M12 8.91c1.7 0 3.09 1.39 3.09 3.09S13.7 15.09 12 15.09 8.91 13.7 8.91 12 10.3 8.91 12 8.91m0-1c-2.25 0-4.09 1.84-4.09 4.09s1.84 4.09 4.09 4.09 4.09-1.84 4.09-4.09S14.25 7.91 12 7.91zm0-1.73c3.9 0 7.35 2.27 8.92 5.82-1.56 3.55-5.02 5.82-8.92 5.82-3.9 0-7.35-2.27-8.92-5.82C4.65 8.45 8.1 6.18 12 6.18m0-1C7.45 5.18 3.57 8.01 2 12c1.57 3.99 5.45 6.82 10 6.82s8.43-2.83 10-6.82c-1.57-3.99-5.45-6.82-10-6.82z"></path></svg></div></icon-shape></yt-icon-shape></yt-icon>
      <yt-formatted-string class="style-scope ytd-menu-navigation-item-renderer">Show unavailable videos</yt-formatted-string>
    
</tp-yt-paper-item>
  </a>
  
        XPATH: //*[@id="items"]/ytd-menu-navigation-item-renderer/a
        JSPATH: document.querySelector("#items > ytd-menu-navigation-item-renderer > a")

        OUTER OUTER:
        <tp-yt-iron-dropdown horizontal-align="auto" vertical-align="top" aria-disabled="false" class="style-scope ytd-popup-container" prevent-autonav="true" style="outline: none; z-index: 2202; position: fixed; left: 208px; top: 439.5px;"><!--css-build:shady--><div id="contentWrapper" class="style-scope tp-yt-iron-dropdown">
  <ytd-menu-popup-renderer slot="dropdown-content" class="style-scope ytd-popup-container" tabindex="-1" use-icons="" style="outline: none; box-sizing: border-box; max-width: 244.477px; max-height: 52px;"><!--css-build:shady--><!--css-build:shady--><tp-yt-paper-listbox id="items" class="style-scope ytd-menu-popup-renderer" role="listbox" tabindex="0"><!--css-build:shady--><ytd-menu-navigation-item-renderer class="style-scope ytd-menu-popup-renderer iron-selected" use-icons="" system-icons="" role="menuitem" tabindex="-1" aria-selected="true"><!--css-build:shady--><!--css-build:shady-->
  <a class="yt-simple-endpoint style-scope ytd-menu-navigation-item-renderer" tabindex="-1" href="/playlist?list=PLthF248A1c69kNWZ9Q39Dow3S2Lxp74mF">
    <tp-yt-paper-item class="style-scope ytd-menu-navigation-item-renderer" style-target="host" role="option" tabindex="0" aria-disabled="false"><!--css-build:shady-->
      <yt-icon class="style-scope ytd-menu-navigation-item-renderer"><!--css-build:shady--><!--css-build:shady--><yt-icon-shape class="style-scope yt-icon"><icon-shape class="yt-spec-icon-shape"><div style="width: 100%; height: 100%; fill: currentcolor;"><svg height="24" viewBox="0 0 24 24" width="24" focusable="false" style="pointer-events: none; display: block; width: 100%; height: 100%;"><path d="M12 8.91c1.7 0 3.09 1.39 3.09 3.09S13.7 15.09 12 15.09 8.91 13.7 8.91 12 10.3 8.91 12 8.91m0-1c-2.25 0-4.09 1.84-4.09 4.09s1.84 4.09 4.09 4.09 4.09-1.84 4.09-4.09S14.25 7.91 12 7.91zm0-1.73c3.9 0 7.35 2.27 8.92 5.82-1.56 3.55-5.02 5.82-8.92 5.82-3.9 0-7.35-2.27-8.92-5.82C4.65 8.45 8.1 6.18 12 6.18m0-1C7.45 5.18 3.57 8.01 2 12c1.57 3.99 5.45 6.82 10 6.82s8.43-2.83 10-6.82c-1.57-3.99-5.45-6.82-10-6.82z"></path></svg></div></icon-shape></yt-icon-shape></yt-icon>
      <yt-formatted-string class="style-scope ytd-menu-navigation-item-renderer">Show unavailable videos</yt-formatted-string>
    
</tp-yt-paper-item>
  </a>
<dom-if class="style-scope ytd-menu-navigation-item-renderer"><template is="dom-if"></template></dom-if>
</ytd-menu-navigation-item-renderer>
</tp-yt-paper-listbox>
<div id="footer" class="style-scope ytd-menu-popup-renderer"></div>
</ytd-menu-popup-renderer>
</div>
</tp-yt-iron-dropdown>


        <yt-icon class="style-scope ytd-menu-navigation-item-renderer"><!--css-build:shady--><!--css-build:shady--><yt-icon-shape class="style-scope yt-icon"><icon-shape class="yt-spec-icon-shape"><div style="width: 100%; height: 100%; fill: currentcolor;"><svg height="24" viewBox="0 0 24 24" width="24" focusable="false" style="pointer-events: none; display: block; width: 100%; height: 100%;"><path d="M12 8.91c1.7 0 3.09 1.39 3.09 3.09S13.7 15.09 12 15.09 8.91 13.7 8.91 12 10.3 8.91 12 8.91m0-1c-2.25 0-4.09 1.84-4.09 4.09s1.84 4.09 4.09 4.09 4.09-1.84 4.09-4.09S14.25 7.91 12 7.91zm0-1.73c3.9 0 7.35 2.27 8.92 5.82-1.56 3.55-5.02 5.82-8.92 5.82-3.9 0-7.35-2.27-8.92-5.82C4.65 8.45 8.1 6.18 12 6.18m0-1C7.45 5.18 3.57 8.01 2 12c1.57 3.99 5.45 6.82 10 6.82s8.43-2.83 10-6.82c-1.57-3.99-5.45-6.82-10-6.82z"></path></svg></div></icon-shape></yt-icon-shape></yt-icon>
        XPATH FULL:
        /html/body/ytd-app/ytd-popup-container/tp-yt-iron-dropdown        

        TOP LEVEL?
<div id="contentWrapper" class="style-scope tp-yt-iron-dropdown">
  <ytd-menu-popup-renderer slot="dropdown-content" class="style-scope ytd-popup-container" tabindex="-1" use-icons="" style="outline: none; box-sizing: border-box; max-width: 244.477px; max-height: 52px;"><!--css-build:shady--><!--css-build:shady--><tp-yt-paper-listbox id="items" class="style-scope ytd-menu-popup-renderer" role="listbox" tabindex="0"><!--css-build:shady--><ytd-menu-navigation-item-renderer class="style-scope ytd-menu-popup-renderer iron-selected" use-icons="" system-icons="" role="menuitem" tabindex="-1" aria-selected="true"><!--css-build:shady--><!--css-build:shady-->
  <a class="yt-simple-endpoint style-scope ytd-menu-navigation-item-renderer" tabindex="-1" href="/playlist?list=PLthF248A1c69kNWZ9Q39Dow3S2Lxp74mF">
    <tp-yt-paper-item class="style-scope ytd-menu-navigation-item-renderer" style-target="host" role="option" tabindex="0" aria-disabled="false"><!--css-build:shady-->
      <yt-icon class="style-scope ytd-menu-navigation-item-renderer"><!--css-build:shady--><!--css-build:shady--><yt-icon-shape class="style-scope yt-icon"><icon-shape class="yt-spec-icon-shape"><div style="width: 100%; height: 100%; fill: currentcolor;"><svg height="24" viewBox="0 0 24 24" width="24" focusable="false" style="pointer-events: none; display: block; width: 100%; height: 100%;"><path d="M12 8.91c1.7 0 3.09 1.39 3.09 3.09S13.7 15.09 12 15.09 8.91 13.7 8.91 12 10.3 8.91 12 8.91m0-1c-2.25 0-4.09 1.84-4.09 4.09s1.84 4.09 4.09 4.09 4.09-1.84 4.09-4.09S14.25 7.91 12 7.91zm0-1.73c3.9 0 7.35 2.27 8.92 5.82-1.56 3.55-5.02 5.82-8.92 5.82-3.9 0-7.35-2.27-8.92-5.82C4.65 8.45 8.1 6.18 12 6.18m0-1C7.45 5.18 3.57 8.01 2 12c1.57 3.99 5.45 6.82 10 6.82s8.43-2.83 10-6.82c-1.57-3.99-5.45-6.82-10-6.82z"></path></svg></div></icon-shape></yt-icon-shape></yt-icon>
      <yt-formatted-string class="style-scope ytd-menu-navigation-item-renderer">Show unavailable videos</yt-formatted-string>
    
</tp-yt-paper-item>
  </a>
<dom-if class="style-scope ytd-menu-navigation-item-renderer"><template is="dom-if"></template></dom-if>
</ytd-menu-navigation-item-renderer>
</tp-yt-paper-listbox>
<div id="footer" class="style-scope ytd-menu-popup-renderer"></div>
</ytd-menu-popup-renderer>
</div>        
        """
        return

    def youGetAllGoodTimes(self, good_links):
        """ Get Relevant Video Durations (4x's more are irrelevant)
        :param good_links: Count to stop at
        :return: good_times, listTimes
        """

        listTimes = []
        good_times = bad_times = 0
        spans = self.driver.execute_script(
            "return document.querySelectorAll('span')")
        for span in spans:
            if good_times == good_links:
                break  # There are extra 90 durations not wanted
            dictSpan = self.driver.execute_script(
                'var items = {}; \
                for (index = 0; index < \
                arguments[0].attributes.length; ++index) \
                { items[arguments[0].attributes[index].name] = \
                arguments[0].attributes[index].value }; \
                return items;',
                span)
            class_list = dictSpan.get('class', None)
            duration_str = dictSpan.get('aria-label', None)
            span_id = dictSpan.get('id', None)
            if not class_list or not duration_str or not span_id or \
                    "style-scope ytd-thumbnail-overlay-time-status-renderer" \
                    not in class_list or span_id != "text":
                bad_times += 1
                # print("\ndictSpan:", dictSpan)
                continue

            good_times += 1
            # duration_str = duration_str.replace(",", ":")
            # duration = re.sub(r'[^0-9,:]', '', duration_str)
            # Above should work but isn't :(
            parts = duration_str.split(", ")
            mins = "0"
            secs = "00"
            if len(parts) == 1:
                # Either "minutes" or "seconds" is missing (so is zero)
                if "minutes" in parts[0]:
                    mins = parts[0].split(" ")[0]
                else:
                    secs = parts[0].split(" ")[0].rjust(2, "0")
            else:
                mins = parts[0].split(" ")[0]
                secs = parts[1].split(" ")[0].rjust(2, "0")

            listTimes.append(mins + ":" + secs)
            # if good_times < 10:
            # print("\ndictSpan:", dictSpan)
            #print("#", good_times, "duration_str:", duration_str,
            #      "duration:", mins + ":" + secs)

        self.youPrint("good_times:", good_times, "bad_times:", bad_times)

        return good_times, listTimes

    def youMonitorLinks(self):
        """ YouTube address bar URL link changes with each new video.
            Test if changed from last check and update treeview.
        :returns: None: Error getting link. Link: video ID link found
        """

        _now = time.time()
        link = self.youCurrentLink()
        _link_time = time.time() - _now  # 0.12 seconds
        if not link:
            return None

        if link == self.youLastLink:  # Oct 28/23 Was last_link
            return link

        if "/playlist?list=" in link:
            self.youPrint('"/playlist?list=" found in "link"!', link)
            self.youPrint('youMonitorLinks() cannot deal with this!')
            return None

        # FIRST SONG
        #   https://www.youtube.com/watch?v=a-Xfv64uhMI&list=
        #       PLthF248A1c68TAKl5DBskfJ2fwr1sk9aM
        # SECOND+ SONG
        #   https://www.youtube.com/watch?v=bePCRKGUwAY&list=
        #       PLthF248A1c68TAKl5DBskfJ2fwr1sk9aM&index=2

        try:
            video_link = link.split("&list=")[0]
        except IndexError:
            self.youPrint("Could not find '&list=' in link!", link)
            return None

        try:
            video_link_id = video_link.split("/watch?v=")[1]
        except IndexError:
            self.youPrint("Could not find '/watch?v=' in video_link!",
                          video_link)
            return None

        make_link = "https://www.youtube.com/watch?v=" + video_link_id
        you_tree_iid_int = self.youTreeNdxByLink(make_link)

        # Don't test you_tree_iid_int for True because first index is 0
        if you_tree_iid_int is None:
            self.youPrint("youTreeSmartPlayAll() - " +
                          "you_tree_iid_int is type: <None>", nl=True)
            self.youPrint("Error on make_link    :", make_link)
            self.youPrint("Original video_link   :", video_link)
            self.youPrint("Original video_link_id:", video_link_id)
            self.youPrint("len(self.listYouTube) :", len(self.listYouTube))
            self.youPrint("self.listYouTube[0]   :", self.listYouTube[0]['link'])
            self.youPrint("youViewCountSkipped   :",
                          self.youViewCountSkipped, lv=0)  # 2023-12-16 Always print
            self.youPrint("Remove:   '", self.act_description,
                          "'.csv', '.pickle' and '.private'")
            self.youPrint("Directory: '" + g.USER_DATA_DIR +
                          os.sep + "YouTubePlaylists'")
            '''
                06:22:17.2 STARTING Playlist - Song # 5     | bEWHpHlfuVU
                Link: https://www.youtube.com/watch?v=DLOth-BuCNY   NOT FOUND!
                                           Should be: bEWHpHlfuVU
            '''
            # May have hit end of list. Start over with first video.
            you_tree_iid_int = 0
            self.youPlaylistIndexStartPlay("0", restart=True)

        song_no = str(you_tree_iid_int + 1).ljust(4)
        self.youPrint("STARTING Playlist - Song №",
                      song_no, " |", video_link_id, nl=True)

        #self.youPrint("Assume Ad. Automatically turn down volume.")
        self.youVolumeOverride(ad=True)  # Set volume 25% for last sink
        # Some songs do not have ads at start so need to reverse manually
        self.youAssumedAd = True  # Reset after player status == 1

        self.youLrcDestroyFrame()  # If last song had lyrics, swap frames
        self.you_tree.see(str(you_tree_iid_int))

        toolkit.tv_tag_remove_all(self.you_tree, 'play_sel')
        toolkit.tv_tag_add(
            self.you_tree, str(you_tree_iid_int), 'play_sel')
        # Keep second place. See two past, then one above
        two_past = you_tree_iid_int + 2
        if two_past < len(self.listYouTube):
            self.you_tree.see(str(two_past))
        one_before = you_tree_iid_int - 1
        if one_before >= 0:
            self.you_tree.see(str(one_before))

        self.resetYouTubeDuration()  # Reset one song duration
        self.youCurrentIndex()  # Set self.durationYouTube var

        ''' Get lyrics from list of dictionaries '''
        lrc = self.listYouTube[you_tree_iid_int].get('lrc', None)
        if lrc:
            self.hasLrcForVideo = True
            self.listLrcLines = lrc.splitlines()
            self.youLrcBuildFrame(str(you_tree_iid_int))

        self.listYouTubeCurrIndex = you_tree_iid_int
        return link

    def youMonitorPlayerStatus(self, player_status, debug=False):
        """ Update progress display in button bar and skip commercials

            Check if self.topYouTreeLRC window exists and update lyrics
            line currently being sung with "lrc_sel" tag

        :param player_status: Music player status (-1, 1, 2, 3, 5)
        :param debug: Print debug statements
        :return: False mserve is closing, else True
        """

        if player_status not in [-1, 1, 2, 3, 5]:
            self.youPrint("Unknown player_status: ", player_status)
            # -1 = ad is playing

            # 0 = Unknown (First time appeared on Oct 29/23 - 9:50 am)
            # 09:50:17.0 STARTING Playlist - Song # 9     | mrojrDCI02k
            # 09:50:17.3 Ad visible. Player status: -1
            # 09:50:18.2 Ad visible. Player status: -1
            # 09:50:20.2 Forced driver refresh after: 0.9
            # 09:50:20.2 MicroFormat video found playing  | zQAd7eQzLus
            # 09:50:21.9 Browser Address Bar URL Link ID  | mrojrDCI02k
            # 09:50:22.0 Ad visible. Player status: -1
            # 09:50:26.4 MicroFormat found after: 0.7     | mrojrDCI02k
            # Unknown player_status:  0

            # 1 = playing
            # 2 = paused or user dragging YT progress bar
            # 3 = begin playing song or YouTube prompting to play after suspend
            # 5 = Status prior to Play All and starting Ad
            return

        now = time.time()
        if player_status == 1:
            # If volume was forced down set it back
            if self.youAssumedAd:
                self.youPrint("Reversing self.youAssumeAd", level=5)
                self.youAssumedAd = None
                self.youVolumeOverride(ad=False)
            delta = now - self.timeLastYouTube
            self.timeLastYouTube = now
            self.progressYouTube += delta
            #print("Duration:", tmf.mm_ss(self.progressYouTube, rem='d'),
            #      "of:", self.durationYouTube, self.youProVar.get(), end="\r")
            # mm_ss(seconds, brackets=False, trim=True, rem=None)

            if self.hasLrcForVideo and self.youLrcFrame:  # Oct 22/23
                self.youLrcHighlightLine()
        else:  
            self.timeLastYouTube = now

        self.youUpdatePlayerButton(player_status)
        self.updateYouTubeDuration()

        # Must wait to fix repeating song until "microformat" is refreshed
        MICRO_FORMAT_WAIT = 0.9  # 1.5x longest known early found of 0.6

        if self.isSongRepeating:
            micro_id = self.youGetMicroFormat()
            link_id = self.youCurrentVideoId()
            elapsed = time.time() - self.timeForwardYouTube

            # Has elapsed time reached wait limit?
            if elapsed > MICRO_FORMAT_WAIT:
                self.isSongRepeating = None  # Turn off future checks
                # Is micro_id inside video different than link?
                if micro_id != link_id:
                    self.youPrint("Force browser refresh after:",
                                  tmf.mm_ss(elapsed, rem='d'), "|", link_id, level=4)
                    self.driver.refresh()
                    self.youPrint("MicroFormat video found playing  |", micro_id, level=4)
                    self.youWaitMusicPlayer()  # wait for music player
                    self.youPrint("Browser Address Bar URL Link ID  |", link_id, level=4)
                    self.resetYouTubeDuration()  # Reset one song duration

            # Is micro_id inside video different than link?
            elif micro_id == link_id:
                # ID inside video matches address bar url
                self.isSongRepeating = None
                self.youPrint("MicroFormat found after:",
                              tmf.mm_ss(elapsed, rem='d'), "    |", micro_id, level=4)

        # Has YouTube popped up an ad?
        if not self.youCheckAdRunning():

            # DRY - Reset full screen if last video playing in full screen
            if self.youForceVideoFull:
                ''' Make YouTube full screen '''
                self.youPrint("Make YouTube full screen")
                actions = ActionChains(self.driver)
                actions.send_keys('f')  # Send full screen key
                actions.perform()
                self.youForceVideoFull = None

            # NOT WORKING:
            # 19:02:29.0 STARTING Playlist - Song № 2     | HnilTXUQtag
            # 19:02:29.0 Assume Ad. Automatically turn down volume.
            # 19:02:29.0 Reversing self.youAssumeAd
            # 19:02:29.2 Make YouTube full screen
            #
            # 19:02:30.7 STARTING Playlist - Song № 2     | HnilTXUQtag
            # 19:02:30.7 Assume Ad. Automatically turn down volume.
            # 19:02:31.0 Reversing self.youAssumeAd
            return True  # Nothing to do

        self.youVolumeOverride(True)  # Ad playing override

        ''' Ad Running - reset start variables '''
        self.isSongRepeating = None
        self.resetYouTubeDuration()  # Reset one song duration

        # Music Player final_status printed at top of loop below.
        final_status = self.youWaitMusicPlayer(debug=False)

        while True:  # Ad was visible. Loop until status is song playing (1)
            """  TODO: At start, quickly ramp down volume over 1/10 second
                       At end, Slowly ramp up volume over 1/2 second
                       However, setup mute mode too, so no ramping
                       Need to capture web browsers sink and then use: 
                            pav.fade(self.driver_sink, start, end, time) """

            """ No longer needed - inside youWaitMusicPlayer()
            # play top refresh + .after(16). With this, CPU load is 3.5% not 6%
            if not lcs.fast_refresh(tk_after=True):
                self.driver.quit()
                return False
            """

            ''' TODO: if self.youDebugLevel == 1: '''
            #self.youPrint("Ad visible. Player status:", final_status)

            #print(ext.t(short=True, hun=True),
            #      "Ad visible. Player status:", final_status)

            # TODO: Only all housekeeping when < .1 second since last time
            #       at this point. E.G.
            # 20:10:55.2 Ad visible. Player status: -1
            # 20:10:55.3 Ad visible. Player status: -1
            # 20:10:55.3 Ad visible. Player status: -1
            # 20:10:55.4 Ad visible. Player status: -1
            # 20:10:55.5 Ad visible. Player status: -1
            self.youHousekeeping()

            # Ad is running
            """  TODO: When resuming from suspend, 100's of ads can appear for
                       duration of sleep. Unlike above where Ads are .1 second
                       apart, these Ads are 2 seconds apart. Fastest way out is
                       to reload the last song. 
            """
            count = 0
            # self.driver.find_element(By.CSS_SELECTOR, ".ytp-ad-duration-remaining")

            if debug:
                self.youPrint("# 0. Player Status:",
                              self.youGetPlayerStatus(), lv=9, nl=True)

            while self.youCheckAdRunning():
                # Back button goes to previous song played
                self.youVolumeOverride(True)  # Ad playing override
                self.driver.back()
                if debug:
                    self.youPrint("BACK LOOP Ad still visible:", count, end="\r", level=9)
                if self.youCheckAdRunning():
                    count += 1
                    if not lcs.fast_refresh():
                        self.driver.quit()
                        return False

            if debug:
                print("driver.back() visible loops:", str(count).ljust(2),
                      " | Video Index:", self.youCurrentIndex(), lv=9, nl=True)
                # count is always 1?
                self.youPrint("# 1. Player Status:", self.youGetPlayerStatus(), lv=9)
                self.youPrint("# 1. Video Index before FIRST forward:",
                              self.youCurrentIndex(), lv=9)

            self.driver.forward()  # Send forward page event
            player_status = self.youWaitMusicPlayer(debug=False)
            # If status is NONE probably dialog prompt
            if not player_status:
                # Answer dialog box for "Video paused. Continue watching?"
                #self.youHousekeeping()  # Not working as intended...
                # Check now inside self.youWaitMusicPlayer
                player_status = self.youWaitMusicPlayer(debug=True)
                if not player_status:
                    self.youPrint("Shutting down, dialog prompt or player broken!",
                                  level=0)  # 0 = forced printing all the time
                    continue

            if debug:
                self.youPrint("# 2. Player Status after 400ms:",
                              self.youGetPlayerStatus(), level=9)
                self.youPrint("# 2. Video Index:", self.youCurrentIndex(), level=9)
                video_id = self.youGetMicroFormat()
                self.youPrint("# 2. youGetMicroFormat() video_id:", video_id, level=9)

            if self.youCheckAdRunning():
                # With this test, don't know if ad #1 or #2 is visible...
                self.driver.forward()
                if debug:
                    self.youPrint("THREE FORWARDS", "Video Index:",
                                  self.youCurrentIndex(), level=9)
                    self.youPrint("# 3A. Player Status: BEFORE 2nd forward wait",
                                  self.youGetPlayerStatus(), level=9)
                    self.youPrint("# 3A. Video Index:", self.youCurrentIndex(), level=9)
                    video_id = self.youGetMicroFormat()
                    self.youPrint("# 3A. youGetMicroFormat() video_id:", video_id, level=9)

                #self.top.after(350)  # 300 too short for triple ad
                player_status = self.youWaitMusicPlayer(debug=False)
                if not player_status:
                    self.youPrint("Shutting down or player broken!")
                    continue
                if debug:
                    self.youPrint("# 3B. Player Status after 350ms:",
                                  self.youGetPlayerStatus(), level=9)
                    self.youPrint("# 3B. URL Index:", self.youCurrentIndex(), level=9)
                    video_id = self.youGetMicroFormat()
                    self.youPrint("# 3B. youGetMicroFormat() video_id:", video_id, level=9)
            else:
                if debug:
                    self.youPrint("TWO FORWARDS",
                                  "Video Index:", self.youCurrentIndex(), level=9)
                    self.youPrint("# 3. Player Status:", self.youGetPlayerStatus(), level=9)
                    self.youPrint("# 3. Video Index:", self.youCurrentIndex(), level=9)
                    video_id = self.youGetMicroFormat()
                    self.youPrint("# 3. youGetMicroFormat() video_id:", video_id, level=9)

            # Could be within second ad but extra forward needed for next
            self.driver.forward()  # Extra forward needed for next song
            final_status = self.youWaitMusicPlayer(debug=False)
            if not final_status:
                print(ext.t(short=True, hun=True),
                      "Weird Error: youWaitMusicPlayer(self.driver, debug=False)")
                """ CAUSED BY INTERRUPTION to confirm to continue when screen dim

                    21:31:25.3 STARTING Playlist - Song # 16    | KZjnJ_9GR5o
                    21:31:26.7 Ad visible. Music player status: -1
                    
                    youWaitMusicPlayer() more than 10 seconds
                    
                    youWaitMusicPlayer() 10,001.6 Null: 0 Paused: 2953 Starting: 0 Between Songs: 0
                    
                    Weird Error: youWaitMusicPlayer(self.driver, debug=False)
                    
                    21:35:18.3 STARTING Playlist - Song # 17    | I9xpq3KGkSM
                    21:35:19.8 Ad visible. Music player status: -1
                    21:35:26.0 MicroFormat found early: I9xpq3KGkSM after: 0.6
                
                """
                return False  # Weird error

            if debug:
                self.youPrint("# 4. Player Status:", self.youGetPlayerStatus(), level=9)
                self.youPrint("# 4. Video Index:", self.youCurrentIndex(), level=9)
                video_id = self.youGetMicroFormat()  # From mini-player script
                self.youPrint("# 4. youGetMicroFormat() video_id:", video_id, level=9)
            else:
                video_id = self.youGetMicroFormat()  # From mini-player script

            if final_status == 1 and not self.youCheckAdRunning():
                self.isSongRepeating = True  # Means we have to check
                self.resetYouTubeDuration()  # Reset one song duration

                # DRY - Reset full screen if last video playing in full screen
                if self.youForceVideoFull:
                    ''' Make YouTube full screen '''
                    self.youPrint("Make YouTube full screen")
                    actions = ActionChains(self.driver)
                    actions.send_keys('f')  # Send full screen key
                    actions.perform()
                    self.youForceVideoFull = None

                return True

    def youWaitMusicPlayer(self, debug=False, startup=False):
        """ self.driver.forward() was just executed. Wait for browser to process.
            Wait until YouTube music player status is:
                1 Music Playing or,
               -1 Ad Playing

            :param debug: When True, print debug stats and counts
            :param startup: When True override 10 second timeout to 1 second
            :return: None = timeout reached, 99 = startup 1 sec timeout reached,
                     player_status = -1 ad playing, = 1 music playing """

        ''' Housekeeping every 1 second (out of 10) '''
        lastHousekeepingTime = time.time()

        count_none = count_2 = count_3 = count_5 = 0
        start = time.time()
        while True:
            if not lcs.fast_refresh(tk_after=False):
                return None
            elapsed = (time.time() - start) * 1000
            if elapsed > 10000.0:  # Greater than 10 seconds?
                self.youPrint("youWaitMusicPlayer() took",
                              "more than 10,000 milliseconds", lv=1, nl=True)
                self.youPrint(
                    "Elapsed:", '{:n}'.format(elapsed),
                    "ms  | Null:", count_none, " | Paused:", count_2,
                    " | Starting:", count_3, " | Idle:", count_5, "\n", lv=1)
                return None

            ad_playing = None
            player_status = self.youGetPlayerStatus()
            if player_status is None:
                count_none += 1  # Still initializing
            elif player_status == 2:
                count_2 += 1  # Music Paused... this is a problem
            elif player_status == 3:
                count_3 += 1  # Something is about to play
            elif player_status == 5:
                ad_playing = self.youCheckAdRunning()
                if ad_playing:
                    break  # Oct 5/23 new technique
                count_5 += 1  # Between songs or Ad before 1st song
                if elapsed > 1000.0 and startup:
                    print("Overriding 1 second IPL player delay")
                    return 99
            elif player_status == 1 or player_status == -1:
                break

            ''' Test 1 second out of 10 seconds when not startup '''
            now = time.time()
            if not startup and now - lastHousekeepingTime > 1.0:
                # Prints for song #10, #17
                self.youPrint(
                     "youWaitMusicPlayer() - 1 second Housekeeping check.")
                lastHousekeepingTime = now
                self.youHousekeeping()

        self.youPrint("youWaitMusicPlayer", '{:n}'.format(elapsed),
                      "ms | Null:", count_none, " | Paused:", count_2,
                      " | Starting:", count_3, " | Idle:", count_5, lv=7, nl=True)

        # Potentially reverse volume override earlier.
        # Getting many false positives as already at desired volume...
        ad = player_status == -1 or ad_playing
        if not ad:  # Music Video is playing
            #self.youPrint("Reversing self.youAssumeAd")
            self.youAssumedAd = None
            self.youVolumeOverride(ad)  # Restore volume 100%
        elif not self.youAssumedAd:  # Ad is running
            self.youVolumeOverride(ad)  # Turn down volume 25%
            self.youAssumedAd = True

        return player_status

    def youVolumeOverride(self, ad=True):
        """ If commercial at 100% set to 25%. If not commercial and
            25%, set to 100% """

        second = self.youGetChromeSink()  # Set active self.youPlayerSink
        first = self.youPlayerSink  # 2023-12-04 used to be 2nd, but swapped

        if self.youPlayerSink is None:
            self.youPrint("youVolumeOverride() sink failure!")
            # First video after age restricted video that won't play
            return

        sink_no = self.youPlayerSink.sink_no_str
        if self.youPlayerSink != first:
            self.youPrint("Multiple Google Chrome Audio Sinks !!!",
                          first.sink_no_str, sink_no)
            print("First :", first)
            print("Second:", second)

        try:
            vol = pav.get_volume(sink_no)
        except Exception as err:
            self.youPrint("youVolumeOverride() Exception:", err)
            return

        '''
Redundant calls after turning down to 25% and up to 100%:

18:18:10.3 STARTING Playlist - Song № 65    | rgWr2nln83s
18:18:10.3 Assume Ad. Automatically turn down volume.
18:18:10.3 Sink No: 870 Volume forced to 25%
18:18:11.0 Sink No: 870 Volume NOT forced: 25
18:18:11.2 Ad visible. Player status: -1
18:18:11.4 Sink No: 870 Volume NOT forced: 25
18:18:12.7 Sink No: 870 Volume forced to 100%
18:18:13.1 Sink No: 870 Volume NOT forced: 100
18:18:13.7 MicroFormat found after: 0.3     | rgWr2nln83s
18:22:02.3 Sink No: 870 Volume forced to 25%
18:22:02.4 Sink No: 870 Volume NOT forced: 25
18:22:02.4 Ad visible. Player status: -1
18:22:02.5 Sink No: 870 Volume NOT forced: 25
18:22:03.7 Ad visible. Player status: -1
18:22:04.3 Sink No: 870 Volume NOT forced: 25
18:22:05.2 Sink No: 870 Volume forced to 100%
18:22:05.3 Sink No: 870 Volume NOT forced: 100
        '''

        if vol != 25 and vol != 100:
            self.youPrint("Sink:", sink_no,
                          "Invalid VOLUME:", vol, type(vol))
        if ad:
            # self.youPrint("Sink:", self.youPlayerSink.sink_no_str,
            #              "Volume during commercial:", vol, type(vol))
            if vol == 100:
                pav.set_volume(sink_no, 25.0)
                self.youPrint("Sink No:", sink_no, "Volume forced to 25%", level=5)
            else:
                self.youPrint("Sink No:", sink_no, "Volume NOT forced:", vol, level=5)
                pass
        else:
            self.youPrint("Sink:", sink_no,
                          "Volume NO commercial:", vol, type(vol), level=5)
            if vol == 25:
                pav.set_volume(sink_no, 100.0)
                self.youPrint("Sink No:", sink_no, "Volume forced to 100%", level=5)
            else:
                self.youPrint("Sink No:", sink_no, "Volume NOT forced:", vol, level=5)
                pass

    def youLrcBuildFrame(self, item):
        """ Build Frame for YouTube Video LRC (synchronized lyrics)

            One time create LRC frame and TreeFrame.grid_remove()
            If created, TreeFrame.grid_remove() and lrcFrame.grid() reactivate.

        """
        if self.youLrcFrame:
            self.youTreeFrame.grid_remove()  # Remove row 0 Treeview Frame
            self.youLrcFrame.grid()  # Reactivate row 1 LRC Frame
            self.youSetCloseButton()  # Set close button text
        else:

            tree_width  = self.youTreeFrame.winfo_width()
            tree_height = self.youTreeFrame.winfo_height()
            self.youTreeFrame.grid_remove()  # Remove row 0 Treeview Frame

            # Master frame for Artwork and LRC Lyrics lines
            self.youLrcFrame = tk.Frame(self.frame, height=tree_height)
            self.youLrcFrame.grid_propagate(False)  # Don't grow the new frame
            self.youLrcFrame.grid(row=1, sticky=tk.NSEW)  # Row 1 new LRC frame
            self.youLrcFrame.columnconfigure(0, minsize=350, weight=1)  # Art
            self.youLrcFrame.columnconfigure(  # Subtract art & vert scroll size
                1, minsize=tree_width - 350, weight=1)  # for LRC lyrics width.

        ''' Song Artwork, Song Name, Progress, Time offset & highlight Color '''
        info_frame = tk.Frame(self.youLrcFrame)
        info_frame.grid(row=0, column=0, sticky=tk.NS)
        art_label = tk.Label(info_frame, borderwidth=0,
                             image=self.photosYouTube[int(item)])
        art_label.grid(row=0, column=0, sticky=tk.EW, padx=5, pady=10)

        song = tk.Label(info_frame, text=self.listYouTube[int(item)]['name'],
                        font=g.FONT14, wraplength=320, justify="center")
        song.grid(row=1, column=0, sticky=tk.EW, padx=5, pady=21)

        # Links https://stackoverflow.com/a/23482749/6929343
        link1 = tk.Label(info_frame, text="Google Song Meaning",
                         fg="blue", cursor="hand2",
                         font=g.FONT, wraplength=320, justify="center")
        link1.grid(row=2, column=0, sticky=tk.EW, padx=5, pady=21)
        url = "https://www.google.com/search?q=song meaning " + \
              self.listYouTube[int(item)]['name']
        link1.bind("<Button-1>", lambda e: webbrowser.open_new(url))

        # Song progress seconds into duration
        self.youProLrcVar = tk.StringVar()
        self.youProLrcVar.set("Progress: 0.0")
        position = tk.Label(info_frame, textvariable=self.youProLrcVar,
                            font=g.FONT, wraplength=320, justify="center")
        position.grid(row=3, column=0, sticky=tk.EW, padx=5, pady=21)

        # Lyrics Time Offset +/- seconds
        time_string = tk.Label(info_frame, text="Lyrics Time Offset",
                               font=g.FONT, wraplength=320, justify="center")
        time_string.grid(row=4, column=0, sticky=tk.EW, padx=5, pady=(20, 0))
        self.youLrcTimeOffsetVar = tk.DoubleVar()
        ndx = int(item)
        self.youLrcTimeOffset = self.listYouTube[ndx].get('lrc_timeoff', None)
        if self.youLrcTimeOffset is None:
            self.youLrcTimeOffset = 0.0
        self.youLrcTimeOffsetVar.set(self.youLrcTimeOffset)
        time_offset = tk.Entry(info_frame, textvariable=self.youLrcTimeOffsetVar,
                               font=g.FONT14, justify="center")
        time_offset.grid(row=5, column=0, sticky=tk.EW,
                         padx=5, pady=(0, 40))
        time_offset.bind("<FocusOut>", lambda e: self.youLrcUpdateTimeOffset(item))

        # Highlight background color
        bg_string = tk.Label(info_frame, text="Red / Green / Blue / Black" +
                                              " / Yellow / Cyan / Magenta",
                             font=g.FONT, wraplength=320, justify="center")
        bg_string.grid(row=6, column=0, sticky=tk.EW, padx=5, pady=(20, 0))
        self.youLrcBgColorVar = tk.StringVar()
        self.youLrcBgColor = self.listYouTube[ndx].get('lrc_color', None)
        if self.youLrcBgColor is None:
            self.youLrcBgColor = 'Yellow'
        self.youLrcBgColorVar.set(self.youLrcBgColor)
        bg_color = tk.Entry(info_frame, textvariable=self.youLrcBgColorVar,
                            font=g.FONT14, justify="center")
        # Want to increase X padding but it's forcing info_frame wider?
        bg_color.grid(row=7, column=0, sticky=tk.EW,
                      padx=5, pady=(0, 40))
        # bg_color.bind("<FocusOut>", self.youLrcUpdateBgColor)
        bg_color.bind("<FocusOut>", lambda e: self.youLrcUpdateBgColor(item))

        ''' Scrolled Text with LRC Lyrics '''
        # Text padding not working: https://stackoverflow.com/a/51823093/6929343
        self.scrollYT = toolkit.CustomScrolledText(
            self.youLrcFrame, state="normal", font=g.FONT14,
            borderwidth=15, relief=tk.FLAT)
        self.scrollYT.configure(background="#eeeeee")  # Replace "LightGrey"
        self.scrollYT.config(spacing1=20)  # Spacing above the first line in a block of text
        self.scrollYT.config(spacing2=10)  # Spacing between the lines in a block of text
        self.scrollYT.config(spacing3=20)  # Spacing after the last line in a block of text
        self.scrollYT.tag_configure("center", justify='center')

        ''' Insert Lyrics Lines '''
        self.youFirstLrcTimeNdx = None  # 0-Index of first line with [mm:ss.99]
        self.youFirstLrcTime = None
        self.scrollYT.configure(state="normal")
        for ndx, line in enumerate(self.listLrcLines):
            line_time, line_text = self.youLrcParseLine(line)
            # print("line_time:", line_time, "line_text:", line_text)
            if not line_time:  # two spaces for background color before & after
                # one extra leading space for left-margin gutter not highlighted
                line = self.youLrcParseMeta(line)
                self.scrollYT.insert("end", "   " + line + "  \n")
            else:
                self.scrollYT.insert("end", "   " + line_text + "  \n")
                if self.youFirstLrcTimeNdx is None:  # don't test for not 0
                    self.youFirstLrcTimeNdx = ndx
                    self.youFirstLrcTime = line_time

        self.scrollYT.configure(state="disabled")

        self.scrollYT.tag_add("center", "1.0", "end")
        self.scrollYT.grid(row=0, column=1, padx=3, pady=3, sticky=tk.NSEW)
        tk.Grid.rowconfigure(self.youLrcFrame, 0, weight=1)
        tk.Grid.columnconfigure(self.youLrcFrame, 1, weight=1)

        self.scrollYT.tag_config('red', background='Red', foreground='White',
                                 font=font.Font(size=14, weight="bold"))
        self.scrollYT.tag_config('green', background='Green', foreground='White',
                                 font=font.Font(size=14, weight="bold"))
        self.scrollYT.tag_config('blue', background='Blue', foreground='Yellow',
                                 font=font.Font(size=14, weight="bold"))
        self.scrollYT.tag_config('black', background='Black', foreground='Gold',
                                 font=font.Font(size=14, weight="bold"))
        self.scrollYT.tag_config('yellow', background='Yellow',
                                 font=font.Font(size=14, weight="bold"))
        self.scrollYT.tag_config('cyan', background='Cyan',
                                 font=font.Font(size=14, weight="bold"))
        self.scrollYT.tag_config('magenta', background='Magenta', foreground='White',
                                 font=font.Font(size=14, weight="bold"))

        # self.scrollYT.config(tabs=("2m", "40m", "50m"))  # Apr 9, 2023
        self.scrollYT.config(tabs=("2m", "65m", "80m"))  # Apr 27, 2023
        self.scrollYT.tag_configure("margin", lmargin1="2m", lmargin2="65m")
        # Fix Control+C  https://stackoverflow.com/a/64938516/6929343
        self.scrollYT.bind("<Button-1>", lambda event: self.scrollYT.focus_set())
        self.youLrcFrame.update()  # 2023-12-15 - Fix .dlineinfo() errors?

    def youLrcUpdateTimeOffset(self, item, *_args):
        """ Time Offset has just been changed. """
        old_time = self.youLrcTimeOffset
        self.youLrcTimeOffset = self.youLrcTimeOffsetVar.get()
        # Sanity check
        if not -150.0 < self.youLrcTimeOffset < 150.0:
            print("Offset entered:", self.youLrcTimeOffset, "is beyond 150 seconds.")
            self.youLrcTimeOffset = old_time
            self.youLrcTimeOffsetVar.set(self.youLrcTimeOffset)
            self.top.update()
            return

        if old_time == 0.0 and self.youLrcTimeOffset == 0.0:
            return  # No point saving default

        # Write new value to disk
        ndx = int(item)
        start = time.time()
        self.listYouTube[ndx]['lrc_timeoff'] = self.youLrcTimeOffset
        fname = self.nameYouTube.replace(".csv", ".pickle")
        ext.write_to_pickle(fname, self.listYouTube)
        print("youLrcUpdateTimeOffset():", self.youLrcTimeOffset, "ext.write_to_pickle:",
              tmf.mm_ss(time.time() - start, rem='h'), "sec")  # 1.55 sec

        self.top.update()

    def youLrcUpdateBgColor(self, item, *_args):
        """ Time Offset has just been changed. """
        old_color = self.youLrcBgColor
        self.youLrcBgColor = self.youLrcBgColorVar.get()
        if self.youLrcBgColor.lower() != 'red' and \
                self.youLrcBgColor.lower() != 'green' and \
                self.youLrcBgColor.lower() != 'blue' and \
                self.youLrcBgColor.lower() != 'black' and \
                self.youLrcBgColor.lower() != 'yellow' and \
                self.youLrcBgColor.lower() != 'cyan' and \
                self.youLrcBgColor.lower() != 'magenta':
            print("Bad color:", self.youLrcBgColor, " | Keeping old:", old_color)
            self.youLrcBgColor = old_color
            self.youLrcBgColorVar.set(self.youLrcBgColor)
            self.top.update()
            return

        if old_color.lower() == 'yellow' and self.youLrcBgColor.lower() == 'yellow':
            return  # No point saving default

        if old_color.lower() == self.youLrcBgColor.lower():
            return  # Color not changed

        self.scrollYT.tag_remove(old_color.lower(), "1.0", "end")
        print("New color:", self.youLrcBgColor, " | Old color:", old_color)

        # Write new value to disk
        ndx = int(item)
        start = time.time()
        self.listYouTube[ndx]['lrc_color'] = self.youLrcBgColor
        fname = self.nameYouTube.replace(".csv", ".pickle")
        ext.write_to_pickle(fname, self.listYouTube)
        print("bg_focusout():", self.youLrcBgColor, "ext.write_to_pickle:",
              tmf.mm_ss(time.time() - start, rem='h'), "sec")  # 1.55 sec

        self.top.update()

    def youLrcDestroyFrame(self, *_args):
        """ Remove Frame for YouTube Video LRC (synchronized lyrics) """
        if self.youLrcFrame is None:
            return  # Frame hasn't been created yet

        self.youLrcFrame.grid_remove()  # Remove LRC frame
        self.youTreeFrame.grid()  # Restore Treeview frame
        self.hasLrcForVideo = None
        self.youSetCloseButton()

    def youLrcHighlightLine(self):
        """ Highlight LRC (synchronized lyrics) line based on progress """

        # Calculate progress
        #position = tmf.mm_ss(self.progressYouTube, rem='d')  # decisecond
        position = tmf.mm_ss(self.progressYouTube)  # Less distracting seconds
        self.youProLrcVar.set("Progress: " + position)
        progress = self.progressYouTube + self.youLrcTimeOffset
        progress = 0.0 if progress < 0.0 else progress
        if self.progressYouTube and \
                self.progressYouTube == self.progressLastYouTube:
            self.youPrint("Video stuck? self.progressYouTube:",
                          self.progressYouTube)
        self.progressLastYouTube = self.progressYouTube

        # Find line matching progress
        last_ndx = len(self.listLrcLines) - 1
        for i, line in enumerate(self.listLrcLines):
            line_time, line_text = self.youLrcParseLine(line, i)
            #if i == 4:
            #    print(line_time, line_text)
            if i < last_ndx:
                next_line = self.listLrcLines[i + 1]
                next_time, _next_text = \
                    self.youLrcParseLine(next_line, i + 1)
            else:
                next_time = 9999999999999.9

            if line_time is None or next_time is None:
                continue  # Cannot test None

            if not line_time < progress < next_time:
                continue  # Line is the wrong time

            if i == self.ndxLrcCurrentLine:
                return  # index hasn't changed
            self.ndxLrcCurrentLine = i

            #print("New lyrics line:", line_text)
            # Remove pattern green for all
            # Apply pattern green for active line
            try:
                self.scrollYT.tag_remove(
                    self.youLrcBgColor.lower(), "1.0", "end")
            except tk.TclError:  # Oct 22/23 - 8:45pm
                # Working fine for week until housekeeping added
                self.youPrint("ERROR self.scrollYT.tag_remove()")

            two_before = i - 1 if i > 2 else 1
            two_before = str(two_before) + ".0"
            # Start highlight 1 char in so gutter isn't highlighted
            text_start = str(i + 1) + ".0+1c"  # start line + 1 for gutter
            text_end = str(i + 2) + ".0-1c"  # next line - 1 char = end line

            # TODO: More efficient using self.scrollYT.tag_add
            try:
                self.scrollYT.highlight_pattern(
                    "  " + line_text + "  ", self.youLrcBgColor.lower(),
                    start=text_start, end=text_end)
            except tk.TclError:  # Oct 22/23 - 8:45pm
                # Working fine for week until housekeeping added
                self.youPrint("ERROR self.scrollYT.highlight_pattern()")

            # https://stackoverflow.com/a/62765724/6929343
            self.scrollYT.see(text_start)  # Ensure highlighted line is visible
            self.top.update_idletasks()  # 2023-12-10 - Required before dlineinfo()
            # Prevent scrolling down to bottom.
            two_bbox = self.scrollYT.dlineinfo(two_before)  # bbox=[L,T,R,B]
            if two_bbox:
                # Scroll to top pixel of two lines before highlighted lyric line
                self.scrollYT.yview_scroll(two_bbox[1], 'pixels')
            else:
                self.youPrint("youLrcHighlightLine() two_bbox is NoneType!",
                              two_before, nl=True, lv=0)
                print("dict['name']:", self.dictYouTube.get('name', None))
                print("Video No.   :", self.listYouTubeCurrIndex + 1,
                      " | line_time   :", line_time)
                print("text_start  :", text_start, " | line_text:", line_text)

    def youLrcParseLine(self, line, ndx=None):
        """ Split line into seconds float and lyrics text
            ['[length:03:51.71]',
             '[re:www.megalobiz.com/lrc/maker]',
             '[ve:v1.2.3]',
             '[00:00.01]Ooh, stop',
                ...
             '[03:37.20]Ooh'
            ]

        When ndx == None populating scroll box. Else get line time.
        """
        time_float = None
        lyrics_text = None

        try:
            parts = line.split(']', 1)  # split "[00:00.00] Blah blah" in two
            time_str = parts[0].lstrip('[')
            colon_count = time_str.count(":")
            # Trap metadata which contains text instead of time
            contains_text = re.search('[a-zA-Z]', time_str)
            #print("colon_count:", colon_count, parts)
            if colon_count and not contains_text:
                time_float = tmf.get_sec(time_str)
        except IndexError:
            pass  # Could be a blank line

        try:
            lyrics_text = parts[1]
            if len(lyrics_text) == 0:
                # Scroll through Metadata Tags prior to first lyrics line
                if ndx is not None and self.youFirstLrcTimeNdx is not None and \
                        ndx < self.youFirstLrcTimeNdx:
                    # Calculate metadata tag artificial time
                    step = self.youFirstLrcTime / self.youFirstLrcTimeNdx
                    #time_float = step * (ndx + 1)
                    time_float = step * ndx  # 2023-11-25 17:55
                    time_float = float(time_float)  # just in case
                    lyrics_text = self.youLrcParseMeta(line)  # For highlighting
                    #print("step:", step, "time_float:", time_float)
        except IndexError:
            # Blank line
            #print("\nIndexError:", line)
            pass

        return time_float, lyrics_text

    @staticmethod
    def youLrcParseMeta(line):
        """ Pretty format LRC metadata

            [ar:Lyrics artist]
            [al:Album where the song is from]
            [ti:Lyrics (song) title]
            [au:Creator of the Songtext]
            [length:How long the song is]
            [by:Creator of the LRC file]
            [offset:+/- Overall timestamp adjustment in milliseconds, + shifts time up,
                - shifts down i.e. a positive value causes lyrics to appear sooner,
                a negative value causes them to appear later]
            [re:The player or editor that created the LRC file]
            [ve:version of program]
        """
        meta_dict = {"ar": "Artist",
                     "al": "Album",
                     "ti": "Song Title",
                     "au": "Composer",
                     "length": "Length",
                     "by": "LRC Creator",
                     "offset": "Timestamp adjustment in milliseconds",
                     "re": "LRC App",
                     "ve": "LRC App Version"}
        fmt_line = line
        stripped = fmt_line.strip()
        if len(stripped) < 2:
            #print("len(stripped):", len(stripped))
            return fmt_line
        if not stripped[0] == "[" or not stripped[-1] == "]":
            #print("stripped[0]:", stripped[0], "stripped[-1]:", stripped[-1])
            return fmt_line
        fmt_line = stripped.lstrip("[").rstrip("]")
        parts = fmt_line.split(":", 1)

        try:
            key = parts[0]
            value = parts[1].strip()
            tag = meta_dict.get(key.lower(), key)
            #print("key:", key, " | value:", value, " | tag:", tag)
            fmt_line = tag + ": " + value
            return fmt_line
        except IndexError:
            return fmt_line

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

"How often does YouTube update view count?
Though YouTube doesn't publish this information,
we know that it updates views approximately every
24 to 48 hours. It does not update views instantly.
Apr 13, 2021"

Yesterday 7,261 views.
Start 06:00. In 4 hours ~60 views last night ~80 views (7,461 est.)
2023-12-10 10:00 - video count boost start.
2023-12-10 13:25 - 371 boost views (program is counting)
2023-12-10 14:25 - 502 boost views
2023-12-10 15:25 - 627 boost views (shut down)
2023-12-10 19:35 - YT says 7,447 views, turn off speed boost.
2023-12-10 22:30 - Suspend

2023-12-11 05:33 - Restarted yesterday so far 57 views of 98 on Rock
2023-12-11 07:00 - 74 views (14 boosted)
2023-12-11 07:30 - 81 views (Suspend)
2023-12-11-16:32 - 82 views (Resume, YT still says 7,447 views)
2023-12-11-18:30 - 98 +  8 views (YT 7,447 views)
2023-12-11-19:05 - 98 + 16 views (stop playing)
2023-12-11-19:13 - Waiting for YT view count to update also at:
                19:25, 19:57, 20:20, finally at 20:23 ---
                YT reports 8,171 views. So 30 second video count
                boost has 1 day lag? 7,447 + 114 s/b 7,561 count.
                There are 8,171 - 7,561 = 610 extra videos
2023-12-11-20:28 - Speed boost on start 8,171 YT views
2023-12-11-20:53 - 50 speed views. Close program:
2023-12-11-20:57 - Restart with end of playlist printing:
                print("youViewCountSkipped   :", ...)
2023-12-11-21:48 - youViewCountSkipped   : 142
2023-12-11-22:10 - Suspend

2023-12-12-06:01 - youViewCountSkipped   : 261 (diff = 119)
2023-12-12-06:52 - youViewCountSkipped   : 364 (diff = 103)
2023-12-12-07:31 - Suspend (#74 of 98)
2023-12-12-16:33 - Resume
2023-12-12-16:47 - youViewCountSkipped   : 465 (diff = 101)
2023-12-12-17:39 - youViewCountSkipped   : 568 (diff = 103)
2023-12-12-18:32 - youViewCountSkipped   : 668 (diff = 100)
2023-12-12-19:24 - youViewCountSkipped   : 778 (diff = 110)
2023-12-12-19:25 - CHECK FOR UPDATE from 8,171 views also at:
                19:30, 19:45, 20:00, finally at 20:06
2023-12-12-20:06 - 8,437 views - 8,171 previous = 266 new views

2023-12-12-20:12 - Skipped: 0 - Restart for new YouTube Day
2023-12-12-21:05 - Skipped: 103, duplicates: 5, errors: 6
2023-12-12-21:58 - Skipped: 205, duplicates: 4, errors: 4
2023-12-12-22:08 - Suspend at song # 19 of 98

2023-12-13-05:33 - Resume at song # 19 of 98
2023-12-13-06:15 - Skipped: 307, duplicates: 4, errors: 2
2023-12-13-06:30 - SURVEY ERROR at skipped count ~340 crashed mserve:
                Restart mserve at 0 skipped #33 of 98
2023-12-13-07:11 - Bug Crash at list end. Previous skipped: ~400:
                Restart mserve at 0 skipped #41 of 98
2023-12-13-07:23 - Smart Play song # 96 of 98 to test code change
                Remember to add 400 to day totals !!!
2023-12-13-06:15 - Skipped: 26, duplicates: 0, errors: 0
2023-12-13-17:00 - Resume (#14 of 99 says YT author added 1 song)
2023-12-13-17:47 - Skipped: 130, duplicates: ?, errors: 3
2023-12-13-18:37 - Skipped: 237, duplicates: 9, errors: 4
2023-12-13-19:31 - Skipped: 344, duplicates: 6, errors: 3
2023-12-13-19:20 - CHECK FOR UPDATE from 8,171 views at:
                19:35, 19:50, 19:55 - YT updated at 9,293
2023-12-13-19:31 - Skipped: 391, duplicates: ?, errors: 2
2023-12-13-19:55 - 9,293 views - 8,437 previous = 856 new views
                Actual 391 + 400 est. = 791 view skipped count

2023-12-13-19:56 - Restart with 99 videos in mserve Rock playlist.
2023-12-13-20:50 - Skipped: 102, duplicates: 3, errors: 5
2023-12-13-21:43 - Skipped: 209, duplicates: 8, errors: 3
2023-12-13-22:10 - Suspend. Resume on 14th at 05:26

2023-12-14-05:56 - Skipped: 310, duplicates: 2, errors: 6
2023-12-14-06:49 - Skipped: 409, duplicates: 0, errors: 5
2023-12-14-07:31 - Suspend while playing #79 of 99. Resume at 16:51.
2023-12-14-17:03 - Skipped: 508, duplicates: 0, errors: 5
2023-12-14-17:56 - Skipped: 610, duplicates: 3, errors: 3
2023-12-14-18:50 - Skipped: 712, duplicates: 3, errors: 4
2023-12-14-19:43 - Skipped: 818, duplicates: 7, errors: 3
2023-12-14-20:11 - Skipped: 870, duplicates: 2, errors: 2 (stop at #50)
                YT updated: 10,053 - 9,293 previous = 760 new views
                870 view skipped count (missing 90 due to lag)

2023-12-14-20:15 - Restart mserve with new code
2023-12-14-21:05 - Skipped: 112, duplicates: 12, errors: 2
2023-12-14-22:03 - Skipped: 219, duplicates: 8, errors: 3
2023-12-14-22:21 - Suspend at song #34. Resume at 23:30 (est. time)
2023-12-14-23:59 - Skipped: 376, duplicates: 8, errors: 2
2023-12-14-23:59 - Suspend (glitches in the Matrix...)
2023-12-15-06:15 - Skipped: 479, duplicates: 4, errors: 6
2023-12-15-07:11 - Skipped: 589, duplicates: 1, errors: 3
2023-12-15-07:29 - Suspend while playing #32 of 99.
2023-12-15-16:40 - Resume #33 of 99.
2023-12-15-17:15 - Skipped: 695, duplicates: 7, errors: 6
2023-12-15-18:09 - Skipped: 807, duplicates: 13, errors: 3
2023-12-15-19:03 - Skipped: 916, duplicates: 10, errors: 1
2023-12-15-20:00 - Shutdown for concise counts. Skipped= 1,024.
2023-12-15-21:24 - Noticed 10,982 views - 10,053 = 929 new YT views (missing 95)

2023-12-16-08:19 - Restart mserve @ 10,982 views. dlineinfo() errors gone now.
2023-12-16-09:09 - Skipped: 102, duplicates: 3, errors: (one link not found)
2023-12-16-09:10 - Skipped: 103, duplicates: 1, errors: (two links not found)
2023-12-16-10:13 - Skipped: 209, duplicates: 7, errors: (only one link not found)
2023-12-16-10:56 - Skipped: 310, duplicates: 2, errors: (only one link not found)
2023-12-16-11:50 - Skipped: 412, duplicates: 3,     "       "       "
2023-12-16-12:43 - Skipped: 516, duplicates: 5,     "       "       "
2023-12-16-13:37 - Skipped: 614, duplicates: 0,     "       "       "
2023-12-16-14:30 - Skipped: 718, duplicates: 5, errors: 1 - OLD dlineinfo() bug
2023-12-16-17:36 - Skipped: 818, duplicates: 5, errors: 6 - OLD dlineinfo() bug
Shutdown - Google not updating daily count. Must add 818 (minimum) later.
2023-12-16-22:30 - Restart at song #3. YT playlist has 100 songs
2023-12-16-23:33 - Skipped: 98, duplicates: 0, errors: 3
2023-12-17-00:26 - Skipped: 198, duplicates: 0, errors: 1
2023-12-17-01:19 - Skipped: 299, duplicates: 1, errors: 2
2023-12-17-01:50 - Skipped: 356, SUSPEND at #59. Skipped = 1,174
2023-12-17-03:?? - Overnight 11,890 views - 10,982 = 908 new YT views (missing 266)

2023-12-17-09:00 - Restart mserve @ 11,890 views - Update song #92 lyrics for errors
2023-12-17-09:55 - Skipped: 110, duplicates: 10, error: 1 #92, line 5.0+1c
                Song #46 (Loosing My Religion) metadata tags had time index
                Song #92 (Chelsea Smile Lyrics) first lyrics line had [00:00.0]
2023-12-17-10:51 - Skipped: 215, duplicates: 5, errors: 0
2023-12-17-11:45 - Skipped: 321, duplicates: 6, errors: 0
2023-12-17-12:39 - Skipped: 423, duplicates: 2, errors: 0
2023-12-17-13:33 - Skipped: 528, duplicates: 5, errors: 0
2023-12-17-14:27 - Skipped: 633, duplicates: 5, errors: 0
2023-12-17-15:20 - Skipped: 733, duplicates: 0, errors: 0
2023-12-17-16:14 - Skipped: 837, duplicates: 4, errors: 1 - song #92 again
2023-12-17-16:25 - accidental CTRL+C at song #21/100
2023-12-17-16:30 - Restart.  Must add 858 skipped to Dec 17th total.
2023-12-17-17:20 - Skipped: 111+858, duplicates: 11, errors: 0
2023-12-17-18:10 - Skipped: 211+858, duplicates: 11, errors: 0

===============================================================================


===============================================================================

When pasting lyrics self.info.cast is called but Close button is missing. An
error is printed in console from ToolTips():

_close_cb(): Probably closed wrong widget
toolkit.py ToolTips.get_dict(): self.dict for "widget" not found
    .140563907705384.140563907705600.140563907705816.140563753007800.140563686969288
16:31.3687 _close_cb() - tt_dict not found for: 9288
youTreePasteLrc() ext.write_to_pickle: 2.75 sec
append lyrics[0]: Bring Me The Horizon - Chelsea Smile lyrics

=============================================================================

Survey Popup Window causes error when clicking play next:
"How are your recommendations today?
N/A, Bad, Fair, Good, Very Good, Extremely Good"

Exception in Tkinter callback
Traceback (most recent call last):
  File "/usr/lib/python2.7/lib-tk/Tkinter.py", line 1540, in __call__
    return self.func(*args)
  File "/home/rick/python/mserve.py", line 15812, in <lambda>
    command=lambda: self.youSmartPlayAll())
  File "/home/rick/python/mserve.py", line 16135, in youSmartPlayAll
    self.youMonitorPlayerStatus(player_status, debug=False)
  File "/home/rick/python/mserve.py", line 17009, in youMonitorPlayerStatus
    self.updateYouTubeDuration()
  File "/home/rick/python/mserve.py", line 18053, in updateYouTubeDuration
    except Exception as err:
  File "/usr/lib/python2.7/dist-packages/selenium/webdriver/remote/webelement.py",
        line 75, in click
    self._execute(Command.CLICK_ELEMENT)
  File "/usr/lib/python2.7/dist-packages/selenium/webdriver/remote/webelement.py",
        line 454, in _execute
    return self._parent.execute(command, params)
  File "/usr/lib/python2.7/dist-packages/selenium/webdriver/remote/webdriver.py",
        line 201, in execute
    self.error_handler.check_response(response)
  File "/usr/lib/python2.7/dist-packages/selenium/webdriver/remote/errorhandler.py",
        line 181, in check_response
    raise exception_class(message, screen, stacktrace)
WebDriverException: Message: element click intercepted:
        Element <a class="ytp-next-button ytp-button" role="button"
        data-title-no-tooltip="Next" aria-keyshortcuts="SHIFT+n"
        aria-disabled="false" aria-label="Next keyboard shortcut SHIFT+n"
        title="Next (SHIFT+n)"
        data-preview="https://i1.ytimg.com/vi/n6P0SitRwy8/mqdefault.jpg"
        data-tooltip-text="Nirvana - Heart-Shaped Box (Official Music Video)"
        href="https://www.youtube.com/watch?
        list=PLthF248A1c68TAKl5DBskfJ2fwr1sk9aM&amp;v=n6P0SitRwy8">...</a>
        is not clickable at point (152, 302). Other element would receive the click:
        <ytd-single-option-survey-option-renderer
        class="style-scope ytd-single-option-survey-renderer"
        vertical="">...</ytd-single-option-survey-option-renderer>
  (Session info: chrome=108.0.5359.124)
  (Driver info: chromedriver=108.0.5359.71
        (1e0e3868ee06e91ad636a874420e3ca3ae3756ac-refs/branch-heads/5359@{#1016}),
        platform=Linux 4.14.216-0414216-generic x86_64)
=============================================================================

        """
        if self.durationYouTube == 0.0:
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
            self.youViewCountSkipped += 1
            elem = self.driver.find_element_by_xpath(
                '//*[@class="ytp-next-button ytp-button"]')
            try:
                elem.click()  # survey can block next button
                return
            except WebDriverException as err:
                title = "updateYouTubeDuration WebDriverException"
                text = str(err)
                message.ShowInfo(self.top, title, text, icon='error',
                                 thread=self.get_thread_func)
                self.youPrint("updateYouTubeDuration WebDriverException:\n", err,
                              nl=True, lv=0)
                # Can't really do anything until user finishes survey or 'X' it

        if time_video > 0.0:
            self.progressYouTube = time_video
        percent = float(100.0 * self.progressYouTube / self.durationYouTube)
        self.youProVar.set(percent)
        self.youProBar.update_idletasks()

    def youUpdatePlayerButton(self, player_status):
        """ YouTube Music Player Status determines button text. 
            1 = Music video is playing
            2 = Music video is paused
            otherwise ad playing or music player idle
        """
        if player_status == 1:
            # self.youPlayerPauseText = "❚❚ Pause"
            self.youSetPlayerButton(self.youPlayerPauseText)
        elif player_status == 2:
            # self.youPlayerPlayText = "▶  Play"
            self.youSetPlayerButton(self.youPlayerPlayText)
        else:
            # self.youPlayerNoneText = "?  None"
            self.youSetPlayerButton(self.youPlayerNoneText)

    def youSetPlayerButton(self, new):
        """ If changed, Set button player text and tool tip.
            Get Audio Sink.
        """
        if new == self.youPlayerCurrText:
            return  # No change from previous text

        self.youPlayerCurrText = new
        try:
            self.youPlayerButton.config(text=new)
            if "None" in new:
                self.tt.set_text(self.youPlayerButton, "Nothing can be done")
            if "Play" in new:
                self.tt.set_text(self.youPlayerButton, "Resume playing video")
            if "Pause" in new:
                self.tt.set_text(self.youPlayerButton, "Pause music video")
        except Exception as err:
            self.youPrint("youSetPlayerButton Exception:", err)

        # Set Audio Sink number (Done too many times in program?)
        self.youGetChromeSink()

    def youGetChromeSink(self):
        """ Get Audio Sink.
            There is often two sinks for Chrome and the last is set
            The first is returned.
        """

        self.youPlayerSink = None
        second = self.youPlayerSink = None
        pav.get_all_sinks()
        for Sink in pav.sinks_now:
            if "Chrome" in Sink.name:
                self.youPlayerSink = Sink  # Audio Sink (sink_no_str)
                if self.youPlayerSink:
                    second = Sink
                #self.youPrint(self.youPlayerSink)
        return second

    def youTogglePlayer(self):
        """ Button has been clicked.
        """
        if self.youPlayerNoneText == self.youPlayerCurrText:
            # self.youPlayerButton = None  # Tkinter element mounted with .grid
            # self.youPlayerCurrText = None  # "None" / "Pause" / "Play" button
            # self.youPlayerNoneText = "?  None"  # Music Player Text options
            # self.youPlayerPlayText = "▶  Play"  # used when music player status
            # self.youPlayerPauseText = "❚❚ Pause"  # changes between 1 & 2
            return  # Can't divide by zero

        ''' YouTube toggle player with space bar '''
        actions = ActionChains(self.driver)
        actions.send_keys(' ')  # Send space
        actions.perform()

    def youCurrentIndex(self):
        """ Get link URL from Browser address bar & return index

            Before play all:
                https://www.youtube.com/playlist?list=
                   PLthF248A1c68TAKl5DBskfJ2fwr1sk9aM
            During play all:
                https://www.youtube.com/watch?v=bePCRKGUwAY&list=
                   PLthF248A1c68TAKl5DBskfJ2fwr1sk9aM&index=15

            self.driver.refresh() will increment index beyond reality.
            Lookup video ID to get the real index.

            :returns: None = closing down. 0 = Not found, invalid link.
                      >=1 = playlist video 1's index
        """

        """ Oct 4/23 - Method broken by self.driver.refresh().
                       Index will increment even though video ID is true
                       and stays the same.
        link = self.youCurrentLink() 
        try:
            currIndex = int(link.split("&index=")[1])
            return currIndex
        except IndexError:
            if link:
                try:
                    playlist = link.split("&list=")[1]
                    return playlist
                except IndexError:
                    print("ERROR #2 on link = youCurrentIndex()")
                    return None

        print("ERROR #1 on link = youCurrentIndex()")
        return None
        """
        if not self.top:
            return None  # Closing down
        self.durationYouTube = 0.0
        link = self.youCurrentLink()
        try:
            currVideo = link.split("&list=")[0]
        except IndexError:
            print("youCurrentIndex() Playing video not in saved list")
            print("Unknown results and instability may occur.")
            return 0

        index0s = self.youTreeNdxByLink(currVideo)
        if index0s is None:
            print("youCurrentIndex() Playing video not in saved list")
            print("Unknown results and instability may occur.")
            print("currVideo not found:", currVideo)
            return 0

        # Found valid index
        duration_str = self.dictYouTube['duration']
        self.durationYouTube = float(tmf.get_sec(duration_str))
        index1s = int(index0s) + 1
        return index1s

    def youCurrentVideoId(self):
        """ Get link URL from Browser address bar & return Video ID

            Before play all:
                https://www.youtube.com/playlist?list=
                   PLthF248A1c68TAKl5DBskfJ2fwr1sk9aM
            During play all:
                https://www.youtube.com/watch?v=bePCRKGUwAY&list=
                   PLthF248A1c68TAKl5DBskfJ2fwr1sk9aM&index=15

        """
        if not self.top:
            return None  # Closing down

        link = self.youCurrentLink()
        try:
            currVideo = link.split("&list=")[0]
            currVideo = currVideo.split("/watch?v=")[1]
            return currVideo
        except IndexError:
            if link:
                try:
                    # return first video in playlist
                    play_dict = self.listYouTube[0]
                    link_name = play_dict['link']
                    currVideo = link_name.split("/watch?v=")[1]
                    return currVideo
                except IndexError:
                    print("ERROR #2 on link = getCurrentVideo()")
                    return None

        print("ERROR #1 on link = getCurrentVideo()")
        return None

    def youCurrentLink(self):
        """ Get link URL from Browser address bar

            Before play all:
                https://www.youtube.com/playlist?list=
                   PLthF248A1c68TAKl5DBskfJ2fwr1sk9aM
            During play all:
                https://www.youtube.com/watch?v=bePCRKGUwAY&list=
                   PLthF248A1c68TAKl5DBskfJ2fwr1sk9aM&index=15
        """
        if not self.top:
            return None  # Closing down
        try:
            link = self.driver.current_url
            return link
        except Exception as err:
            print("Exception:", err)
            print("ERROR on link = self.driver.current_url")
            return None

    def youDriverClick(self, by, desc):
        """ Credit: https://itecnote.com/tecnote/
        python-wait-for-element-to-be-clickable-using-python-and-selenium/
        """
        start = time.time()
        wait = WebDriverWait(self.driver, 10)
        by = by.upper()
        try:
            if by == 'XPATH':
                wait.until(EC.element_to_be_clickable((By.XPATH, desc))).click()
            if by == 'ID':
                wait.until(EC.element_to_be_clickable((By.ID, desc))).click()
            if by == 'LINK_TEXT':
                wait.until(EC.element_to_be_clickable((By.LINK_TEXT, desc))).click()
        except TimeoutException:
            print("\nClickable element not found!")
            toolkit.print_trace()
            return False
        return time.time() - start < 9.0

    def youGetPlayerStatus(self):
        """ Credit: https://stackoverflow.com/q/29706101/6929343

2023-12-08 Resume from suspend error:

  File "/home/rick/python/mserve.py", line 16128, in youSmartPlayAll
    self.youMonitorPlayerStatus(player_status, debug=False)
  File "/home/rick/python/mserve.py", line 17133, in youMonitorPlayerStatus
    player_status = self.youWaitMusicPlayer(debug=True)
  File "/home/rick/python/mserve.py", line 17255, in youWaitMusicPlayer
    player_status = self.youGetPlayerStatus()
  File "/home/rick/python/mserve.py", line 18042, in youGetPlayerStatus
    player_status = self.driver.execute_script(
AttributeError: 'NoneType' object has no attribute 'execute_script'

        """
        try:
            # Player status for accurate duration countdown
            player_status = self.driver.execute_script(
                "return document.getElementById('movie_player').getPlayerState()")
            return player_status
        except WebDriverException as err:
            # WebDriverException: Message: javascript error: Cannot read
            #       properties of null (reading 'getPlayerState')
            #   (Session info: chrome=108.0.5359.124)
            #       (Driver info: chromedriver=108.0.5359.71
            #       (1e0e3868ee06e91ad636a874420e3ca3ae3756ac-refs/
            #       branch-heads/5359@{#1016}),
            #       platform=Linux 4.14.216-0414216-generic x86_64)
            #print("WebDriverException:", err)
            return None

    def youGetMicroFormat(self):
        """ Rock Song # 10 is playing but Address URL shows # 11 expected.

        microformat:

        <div id="microformat" class="style-scope ytd-watch-flexy">
        <ytd-player-microformat-renderer
        class="style-scope ytd-watch-flexy">
        <!--css-build:shady--><!--css-build:shady-->
        <script type="application/ld+json"
        id="scriptTag" nonce="VKUa9bVN8W-_ltE725Jfgw"
        class="style-scope ytd-player-microformat-renderer">
        {
            "@context":"https://schema.org",
            "@type":"VideoObject",
            "description":"I wish I could ... My beautiful girl.",
            "duration":"PT288S",
            "embedUrl":"https://www.youtube.com/embed/mS8xDo-qM8w
                       ?list=PLthF248A1c68TAKl5DBskfJ2fwr1sk9aM",
            "interactionCount":"21422290",
            "name":"City And Colour - The Girl (Lyrics)",
            "thumbnailUrl":["https://i.ytimg.com/vi/mS8xDo-qM8w/maxresdefault.jpg?
                          sqp=-oaymwEmCIAKENAF8quKqQMa8AEB-AG-B4AC0AWKAgwIABABGGU
                          gVShbMA8=&rs=AOn4CLBTqtLGNpEVXZ8uQBKGUfAZ7MkvnA"],
            "uploadDate":"2011-12-23",
            "genre":"Music",
            "author":"Fran Smyth"
        }
        </script> </ytd-player-microformat-renderer></div>

        """
        try:
            # Need wait until visible when playing random song
            wait = WebDriverWait(self.driver, 2)
            # Was waiting 10 seconds but that's way too long. Try 2 seconds
            id_name = 'microformat'  # _located
            #element = self.driver.find_element_by_id(id_name)
            element = wait.until(EC.presence_of_element_located((
                By.ID, id_name)))
        except WebDriverException as err:
            print(ext.t(short=True, hun=True),
                  "youGetMicroFormat() WebDriverException:\n", err)
            stat = self.youGetPlayerStatus()
            print(ext.t(short=True, hun=True), "self.youGetPlayerStatus():", stat)
            return None

        try:
            inner = element.get_attribute('innerHTML')
            dict_list = self.extract_dict(inner)
            video_id = None
            if len(dict_list) >= 1:
                inner_dict = dict_list[0]
                embed = inner_dict.get("embedUrl", None)
                '''
                "embedUrl":"https://www.youtube.com/embed/mS8xDo-qM8w
                       ?list=PLthF248A1c68TAKl5DBskfJ2fwr1sk9aM",
                '''
                link = embed.split('?list=')[0]
                video_id = link.rsplit("/", 1)[1]
            else:
                self.youPrint("youGetMicroFormat() innerHTML:", inner, nl=True)
                stat = self.youGetPlayerStatus()
                self.youPrint("self.youGetPlayerStatus():", stat)
                """ PROBLEM TWO DICTIONARIES:
                    {
                    "@context":"https://schema.org",
                    "@type":"VideoObject",
                    "description":"Official music  .../QigvUc",
                    "duration":"PT222S",
                    "embedUrl":"https://www.youtube.com/embed/9SRxBTtspYM?list=PLthF248A1c69kNWZ9Q39Dow3S2Lxp74mF",
                    "interactionCount":"240630662",
                    "name":"Ariana Grande, Social House - boyfriend (Official Video)",
                    "thumbnailUrl":["https://i.ytimg.com/vi/9SRxBTtspYM/maxresdefault.jpg"],
                    "uploadDate":"2019-08-01",
                    "genre":"Music",
                    "author":"ArianaGrandeVevo",
                    "publication":
                        [{
                        "@type":"BroadcastEvent",
                        "isLiveBroadcast":true,
                        "startDate":"2019-08-02T04:00:09+00:00",
                        "endDate":"2019-08-02T04:05:47+00:00"
                        }]
                    }
               """
            return video_id

        except Exception as err:
            print(ext.t(short=True, hun=True),
                  "youGetMicroFormat() Exception:\n", err)
            stat = self.youGetPlayerStatus()
            print(ext.t(short=True, hun=True), "self.youGetPlayerStatus():", stat)
            return None

    @staticmethod
    def extract_dict(s):
        """ Extract all valid dicts from a string.
            https://stackoverflow.com/a/63850091/6929343
        Args:
            s (str): A string possibly containing dicts.

        Returns:
            A list containing all valid dicts.

        """
        # REMOVE LIST WITH DICTIONARY (Publication)
        # https://stackoverflow.com/a/8784436/6929343
        s = re.sub(r'\[\{.+?\}\]', '"Deleted by mserve"', s)
        # ORIGINAL CODE
        results = []
        s_ = ' '.join(s.split('\n')).strip()
        exp = re.compile(r'(\{.*?\})')
        for i in exp.findall(s_):
            try:
                results.append(json.loads(i))
            except ValueError:
                pass  # JSON Python < 3.5
            except json.JSONDecodeError:
                pass  # JSON >= 3.5  https://stackoverflow.com/a/44714607/6929343
            except AttributeError:
                #   File "/home/rick/python/mserve.py", line 16387, in youMonitorPlayerStatus
                #     video_id = self.youGetMicroFormat()  # From mini-player script
                #   File "/home/rick/python/mserve.py", line 16753, in youGetMicroFormat
                #     dict_list = self.extract_dict(inner)
                #   File "/home/rick/python/mserve.py", line 16789, in extract_dict
                #     except json.JSONDecodeError:
                # AttributeError: 'module' object has no attribute 'JSONDecodeError'
                pass
        return results

    def youCheckAdRunning(self):
        """ NOTE: When ad starts playing it opens a new PulseAudio instance.
                  1) Turn down volume immediately
                  2) Test what happens when job is killed?

            NOTE: Player status will be "-1" while ad is running or "3" if ad
                  is starting. May also be "5" (in between songs)

        :return: True if ad displaying, False if no ad displayed
        """
        try:
            # TODO Start Duration Countdown
            _ad = self.driver.find_element(
                By.CSS_SELECTOR, ".ytp-ad-duration-remaining")
            return True

        except NoSuchElementException:
            return False

        except WebDriverException:
            return False

    def youHousekeeping(self):
        """ YouTube Housekeeping.
            Respond to prompt: "Video paused. Continue Watching?"

                                ......                  "Yes"

        """
        element = None
        #try:  # element is never found so comment out to save time
        #    element = self.driver.find_element_by_xpath(
        #        "//*[contains(text(), 'Video paused. Continue Watching?')]")
        #except NoSuchElementException:
        #    element = None
        try:
            element2 = self.driver.find_element_by_id("confirm-button")
        except NoSuchElementException:
            element2 = None
        if not element and not element2:
            return

        #print("youHousekeeping() - Found element:", element,
        #      " | element2:", element2)
        # youHousekeeping() - Found element: None  | element2:
        #   <selenium.webdriver.remote.webelement.WebElement
        #   (session="6ac4176d1ef05a453703aea114ac5541",
        #   element="0.16380191644441688-11")>
        if element2.is_displayed():
            # Initially element2 is not present. First time is present during
            # self.youWaitMusicPlayer() after 10 songs have played. Thereafter,
            # element2 is present during 1 minute check but is not displayed.
            # element2 is displayed for song #17. It is present every minute
            # until Song #20 and disappears during Song #21 which is first time
            # for MicroFormat is forced after 0.9 seconds. Song #30 gets confirm
            # when ad visible and player status -1 in endless loop.
            self.youPrint("youHousekeeping() - click ID: 'confirm-button'", lv=2, nl=True)
            stat = self.youGetPlayerStatus()  # Status = 2
            self.youPrint("Player Status BEFORE click:", stat, lv=2)
            element2.click()  # result1
            time.sleep(.33)  # Nov 6/23 was 1.0, try shorter time for Status
            stat = self.youGetPlayerStatus()  # Status = 1
            self.youPrint("Player Status AFTER click :", stat, "\n", lv=2)
            return
        '''
    <yt-button-renderer id="confirm-button" 
        class="style-scope yt-confirm-dialog-renderer" button-renderer="" 
        button-next="" dialog-confirm=""><!--css-build:shady--><yt-button-shape>
        <button class="yt-spec-button-shape-next yt-spec-button-shape-next--text 
        yt-spec-button-shape-next--call-to-action 
        yt-spec-button-shape-next--size-m" aria-label="Yes" title="" style="">

        <div class="yt-spec-button-shape-next__button-text-content">
        <span class="yt-core-attributed-string 
        yt-core-attributed-string--white-space-no-wrap" 
        role="text">Yes</span></div>

        <yt-touch-feedback-shape style="border-radius: inherit;">
        <div class="yt-spec-touch-feedback-shape 
            yt-spec-touch-feedback-shape--touch-response" aria-hidden="true">
            <div class="yt-spec-touch-feedback-shape__stroke" style=""></div>
            <div class="yt-spec-touch-feedback-shape__fill" style=""></div>
        </div>
        '''
        #if not self.youDriverClick("id", "confirm-button"):
        #    print("youHousekeeping(): Error clicking 'Yes' button")

        # youHousekeeping() - Found element: None
        #   element2: <selenium.webdriver.remote.webelement.WebElement
        #   (session="394498a9a5db08d5b6dbd83e27591f34", 
        #   element="0.951519416280243-15")>
        # youHousekeeping() - Found element: None 
        #   element2: <selenium.webdriver.remote.webelement.WebElement 
        #   (session="394498a9a5db08d5b6dbd83e27591f34", 
        #   element="0.951519416280243-15")>
        # Exception in Tkinter callback
        # Traceback (most recent call last):
        #   File "/usr/lib/python2.7/lib-tk/Tkinter.py", line 1540, in __call__
        #     return self.func(*args)
        #   File "/home/rick/python/mserve.py", line 15699, in <lambda>
        #     command=lambda: self.youTreeSmartPlayAll())
        #   File "/home/rick/python/mserve.py", line 16316, in youTreeSmartPlayAll
        #     self.youHousekeeping()
        #   File "/home/rick/python/mserve.py", line 17879, in youHousekeeping
        #     if not self.youDriverClick("id", "confirm-button"):
        #   File "/home/rick/python/mserve.py", line 17665, in youDriverClick
        #     wait.until(EC.element_to_be_clickable((By.ID, desc))).click()
        #   File "/usr/lib/python2.7/dist-packages/selenium/webdriver/support/wait.py", line 80, in until
        #     raise TimeoutException(message, screen, stacktrace)
        # TimeoutException: Message:

        return

    def youViewCountBoost(self, *_args):
        """ Toggle self.isViewCountBoost. """

        self.isViewCountBoost = not self.isViewCountBoost

        title = "30 second View Count Boost"
        text = \
            "View Count Boost active?: " + str(self.isViewCountBoost) + "\n\n" + \
            "Number of videos skipped: " + str(self.youViewCountSkipped) + "\n\n" + \
            "When View Count Boost is active, only the first 30 seconds" + "\n" + \
            "plays. This creates more view counts in YouTube tomorrow.\n"

        message.ShowInfo(self.top, title, text, thread=self.get_thread_func)

    def youSetDebug(self, *_args):
        """ Set Debug level (self.youDebug) for self.youPrint(level). """

        title = "Set YouTube Debug Level"

        text = \
            "Current Debug Level: " + str(self.youDebug) + "\n\n" + \
            "Print debug lines for the debug level and below:" + "\n\n" + \
            "0 = Nothing prints to console\n" + \
            "1 = Song numbers and initialization (Default)\n" + \
            "2 = Continue watching dialogs\n" + \
            "3 = Ad playing & player status\n" + \
            "4 = Video MicroFormat monitoring\n" + \
            "5 = Ad Volume up/down overrides\n" + \
            "6 = Multiple Audio Sinks when discovered\n" + \
            "7 = Selenium driver.back() / driver.forward()\n" + \
            "8 = Selenium query results\n" + \
            "9 = Detailed driver.back() / driver.forward()\n" + \
            "Enter single digit from '0' to '9' below\n\n"

        answer = message.AskString(
            self.top, thread=self.get_thread_func,  # update_display()
            title=title, text=text, icon="information")

        if answer.result != "yes":
            return False

        # print('answer.string:', answer.string)
        if len(answer.string) != 1:
            # TODO: ShowInfo that single digit from 0 to 7 is required.
            return False

        try:
            int_answer = int(answer.string)
        except Exception as err:
            print("self.youSetDebug() Exception:", err)
            return False

        self.youDebug = int_answer
        self.youPrint("Debug level set to:", self.youDebug, "\n", lv=0, nl=True)
        self.act_size = self.youDebug
        # Write history record from act_size
        self.save_act()
        return True

    def youPrint(self, *args, **kwargs):
        """ Print debug lines based on debug level (self.youDebug):
                0 = Nothing prints, except level=0
                1 = Song numbers and initialization (Default)
                2 = 1 and continue watching dialogs
                3 = 2 and Ad playing & player status
                4 = 3 and Video MicroFormat monitoring
                5 = 4 and Ad Volume up/down overrides
                6 = 5 and Multiple Audio Sinks when discovered
                7 = 6 and driver.back / driver.forward
        """
        # https://stackoverflow.com/a/37308684/6929343
        level = kwargs.pop('level', 1)  # 1 is default level (old name)
        lv = kwargs.pop('lv', 1)  # New level= being converted
        if lv != 1:
            level = lv
        nl = kwargs.pop('nl', False)  # New line before?

        if self.youDebug >= level:
            if nl:
                print()
            print(ext.t(short=True, hun=True), *args)

    def youTreeNdxByLink(self, link_search):
        """ Highlight row black & gold as second entry (see 2 below + 1 before)
            If same link used twice in playlist the first will be highlighted.

            https://www.youtube.com/playlist?list=PLthF248A1c68TAKl5DBskfJ2fwr1sk9aM
            https://www.youtube.com/watch?v=HAQQUDbuudY

        """
        for i, self.dictYouTube in enumerate(self.listYouTube):
            if link_search == self.dictYouTube['link']:
                return i

        self.youPrint("youTreeNdxByLink():", link_search,
                      "NOT FOUND!", nl=True, lv=0)
        # Always print error line (lv=0) with new line before (nl=True)
        return None

    def youTreeCopyLink(self, item):
        """ Copy Single Song link to clipboard. """
        ndx = int(item)
        self.youTreeSharedCopyText(self.listYouTube[ndx]['link'])

    def youTreeCopySearchLrc(self, item):
        """ Copy Single Song Name with search prefix to clipboard. """
        ndx = int(item)
        search_name = "synchronized lyrics lrc " + self.listYouTube[ndx]['name']
        self.youTreeSharedCopyText(search_name)

    def youTreeCopyAll(self):
        """ Copy Playlist link to clipboard. """
        self.youTreeSharedCopyText(self.act_description)

    def youTreeSharedCopyText(self, text):
        """ Copy text to clipboard. """
        r = tk.Tk()
        r.withdraw()
        r.clipboard_clear()
        r.clipboard_append(text)
        r.update()
        r.destroy()
        title = "Copy Complete."
        msg = "The following was copied to the Clipboard:\n\n"
        msg += text
        #message.ShowInfo(self.top, title, msg,
        #                 thread=self.get_thread_func)
        self.info.cast(title + "\n\n" + msg)

    def youTreePasteLrc(self, item):
        """ Paste Song's LRC (LyRiCs) to clipboard. """
        clip_text = self.youTreeSharedPaste()
        # TODO: validate [mm:ss.hh] 'blah blah' exists at least 10 times?

        # Write new LRC to disk
        ndx = int(item)
        start = time.time()
        self.listYouTube[ndx]['lrc'] = clip_text
        fname = self.nameYouTube.replace(".csv", ".pickle")
        ext.write_to_pickle(fname, self.listYouTube)
        print("youTreePasteLrc() ext.write_to_pickle:",
              tmf.mm_ss(time.time() - start, rem='h'), "sec")  # 1.55 sec
        #  New file self.lrcYouTube list[ list[], list[]... list[] ]?

        # Strip "\n\n" + old lyrics line 1 and insert new "\n\n" lyrics line 1.
        all_values = self.you_tree.item(item)['values']
        song_name = all_values[0].split("\n\n")[0]
        lrc = self.listYouTube[ndx].get('lrc', None)
        if lrc:
            lrc_list = lrc.splitlines()
            song_name += "\n\n" + lrc_list[0]  # first lrc line into treeview
            print("append lyrics[0]:", song_name)
        self.you_tree.item(item, values=(song_name,))
        self.you_tree.update_idletasks()

    def youTreeViewLrc(self, item):
        """ View Song's LRC (LyRiCs). """

        # Verify LRC exists in dictionary
        ndx = int(item)
        result = self.listYouTube[ndx].get('lrc', None)
        title = "View LRC № " + str(int(item) + 1)
        if result is None:
            text = "LRC not found!"
            message.ShowInfo(self.top, title, text,
                             thread=self.get_thread_func)
            return

        message.ShowInfo(self.top, title, result,
                         thread=self.get_thread_func)

    def youTreeDeleteLrc(self, item):
        """ Delete Song's LRC (LyRiCs).
            Confirm intent then delete.
        """

        # Delete old LRC from disk
        ndx = int(item)
        start = time.time()

        # Verify LRC exists in dictionary
        result = self.listYouTube[ndx].get('lrc', None)
        title = "Delete LRC № " + str(int(item) + 1)
        if result is None:
            text = "LRC not found!"
            message.ShowInfo(self.top, title, text,
                             thread=self.get_thread_func)
            return

        try:
            result = self.listYouTube[ndx].get('lrc', None)
            del self.listYouTube[ndx]['lrc']
            text = "LRC successfully deleted"
        except KeyError:
            self.youPrint("KeyError no LRC in dictionary")
            text = "LRC not found!"
            return

        if result is not None:
            # If None the key didn't exist
            fname = self.nameYouTube.replace(".csv", ".pickle")
            ext.write_to_pickle(fname, self.listYouTube)
            print("youTreeDeleteLrc() ext.write_to_pickle:",
                  tmf.mm_ss(time.time() - start, rem='h'), "sec")  # 1.55 sec

        # Strip "\n\n" + old lyrics line 1 and insert new "\n\n" lyrics line 1.
        all_values = self.you_tree.item(item)['values']
        song_name = all_values[0].split("\n\n")[0]
        lrc = self.listYouTube[ndx].get('lrc', None)
        if lrc:
            lrc_list = lrc.splitlines()
            song_name += "\n\n" + lrc_list[0]  # first lrc line into treeview
            print("append lyrics[0]:", song_name)
        self.you_tree.item(item, values=(song_name,))
        self.you_tree.update_idletasks()

    def youTreeSharedPaste(self):
        """ Read clipboard. """
        r = tk.Tk()
        r.withdraw()
        #r.clipboard_clear()
        try:
            c = r.clipboard_get()
        except tk.TclError:
            c = None  # https://stackoverflow.com/a/43328523/6929343
        r.update()
        r.destroy()
        title = "Paste Complete."
        text = "The following was read from the Clipboard:\n\n"
        text += c
        #message.ShowInfo(self.top, title, text,
        #                 thread=self.get_thread_func)
        self.info.cast(title + "\n\n" + text)
        return c

    @staticmethod
    def youTreeMouseWheel(event):
        """ Mousewheel scroll defaults to 5 units, but tree has 4 images """
        if event.num == 4:  # Override mousewheel scroll up
            event.widget.yview_scroll(-4, "units")  # tree = event.widget
            return "break"  # Don't let regular event handler do scroll of 5
        if event.num == 5:  # Override mousewheel scroll down
            event.widget.yview_scroll(4, "units")  # tree = event.widget
            return "break"  # Don't let regular event handler do scroll of 5

    def displayMusicIds(self):
        """ Read Music Id's from Playlist History record that was read using:
                self.act_id_list = ['Target']  # Music Id's in play order
        """

        self.displayPlaylistCommonTop("MusicIds")

        # file control class
        view_ctl = FileControl(self.top, self.info)
        self.photosYouTube = []

        for i, music_id in enumerate(self.act_id_list):
            d = sql.music_get_row(music_id)
            if not d:
                print("Invalid SQL music ID:", music_id)
                continue

            os_filename = PRUNED_DIR + d['OsFileName']
            view_ctl.new(os_filename)  # Declaring new file populates metadata

            # TODO: Image needs to be pre-stored for speed view_ctl
            #       get_artwork should pad edges when rectangle
            #       im = resized_art (rectangle), image = original art (square)
            photo, im, original = view_ctl.get_artwork(320, 180)
            if im is None:
                original = img.make_image(NO_ART_STR,
                                          image_w=1200, image_h=1200)
                im = original.resize((320, 180), Image.ANTIALIAS)
                #photo = ImageTk.PhotoImage(im)  Not needed

            song_name = d['Title']
            song_name += "\n\n\tartist \t" + d['Artist']
            song_name += "\n\talbum \t" + d['Album']
            if d['FirstDate']:
                song_name += "\n\tyear \t" + sql.sql_format_value(d['FirstDate'])[:4]
            duration = tmf.mm_ss(d['Seconds'])  # Strip hours and fractions

            # Text Draw duration over image & place into self.photosYouTube[]
            self.displayPlaylistCommonDuration(im, duration)
            self.you_tree.insert('', 'end', iid=str(i), text="№ " + str(i + 1),
                                 image=self.photosYouTube[-1],
                                 value=(song_name,))
            self.you_tree.see(str(i))
            self.top.update_idletasks()
            thread = self.get_thread_func()  # repeated 3 times...
            if thread:
                thread()
            else:
                return False  # closing down...

        view_ctl.close()

        # Below is identical to displayYouTubePlaylist()
        self.displayPlaylistCommonBottom()

# Playlists Class Methods called from Dropdown Menus

    def new(self):
        """ Called by lib_top File Menubar "New Playlist"
            If new songs are pending, do not allow playlist to open """
        if self.check_pending():  # lib_top.tree checkboxes not applied?
            return  # We are all done. No window, no processing, nada
        self.state = 'new'
        self.create_window("New Playlist")
        self.enable_input()

    def rename(self):
        """ Called by lib_top File Menubar "Rename Playlist" """
        self.state = 'rename'
        self.create_window("Rename Playlist")
        self.enable_input()

    def delete(self):
        """ Called by lib_top File Menubar "Delete Playlist" """
        self.state = 'delete'
        self.create_window("Delete Playlist")

    def view(self):
        """ Called by lib_top View Menubar "View Playlists" """
        self.state = 'view'
        self.create_window("View Playlists")

    def open(self):
        """ Called by lib_top File Menubar "Open Playlist"
            If new songs are pending, do not allow playlist to open """
        if self.check_pending():  # lib_top.tree checkboxes not applied?
            return  # We are all done. No window, no processing, nada
        self.state = 'open'
        self.create_window("Open Playlist")

    def save(self):
        """ DEPRECATED. Replaced by self.write_playlist_to_disk() """
        pass

    def save_as(self):
        """ NOT USED as of July 16, 2023 """
        self.state = 'save_as'
        self.create_window("Save Playlist As…")
        self.enable_input()

    def close(self):
        """ Close Playlist (use Favorites) called by def close_playlist()
            Blank out self.name and call display_lib_title()
            which forces Favorites into title bar when self.name is blank. """
        self.state = 'close'
        if not self.edit_playlist():  # Check if changes pending & confirm
            return False
        self.play_close()  # must be called before name is none
        self.reset_open_vars()
        self.display_lib_title()
        return True

# Playlists Class Data Processing

    def read_playlist(self, number_str):
        """ Use playlist number to read SQL History Row into work fields """
        d = sql.get_config('playlist', number_str)
        if d is None:
            return None
        self.make_act_from_hist(d)  # Playlist work fields from SQL Row
        return True

    def make_act_from_hist(self, d):
        """ Active Playlist being edited. Not to be confused with "open".
            The History Column: 'Type' will always contain: 'playlist' """
        self.act_row_id = d['Id']  # History record number
        self.act_code = d['Action']  # E.G. "P000001"
        self.act_loc_id = d['SourceMaster']  # E.G. "L004"
        self.act_name = d['SourceDetail']  # E.G. "Oldies"
        self.act_id_list = json.loads(d['Target'])  # Music Id's in play order
        self.act_size = d['Size']  # Size of all song files in bytes
        # For YouTube Playlist size self.youDebug (Print Debug) is used.
        self.act_count = d['Count']  # len(self.music_id_list)
        self.act_seconds = d['Seconds']  # Duration of all songs in seconds
        self.act_description = d['Comments']  # E.G. "Songs from 60's & 70's

    def make_open_from_act(self):
        """ Create open Playlist variables """
        self.open_row_id = self.act_row_id
        self.open_code = self.act_code
        self.open_loc_id = self.act_loc_id
        self.open_name = self.act_name
        self.open_id_list = self.act_id_list
        self.open_size = self.act_size
        self.open_count = self.act_count
        self.open_seconds = self.act_seconds
        self.open_description = self.act_description

    def reset_open_vars(self):
        """ Create open Playlist variables """
        self.open_row_id = None
        self.open_code = None
        self.open_loc_id = None
        self.open_name = None
        self.open_id_list = None
        self.open_size = None
        self.open_count = None
        self.open_seconds = None
        self.open_description = None

    def check_pending(self):
        """ When lib_top_tree has check boxes for adding/deleting songs that
            haven't been saved, cannot open playlist or create new playlist.
        :return: True if pending additions/deletions need to be applied """
        pending = self.get_pending()
        if pending == 0:
            return False
        ''' self.top window might not exist, so use self.parent instead '''
        text = "Checkboxes in Music Location have added songs or\n" +\
            "removed songs. These changes have not been saved to\n" +\
            "storage or cancelled.\n\n" +\
            "You must save changes or cancel before working with a\n" +\
            "different playlist."
        message.ShowInfo(self.parent, "Songs have not been saved!",
                         text, icon='error', align='left', thread=self.get_thread_func)

        return True  # We are all done. No window, no processing, nada

    def check_save_as(self):
        """ NOT USED.
            Display message this isn't working yet. Always return false. """
        # June 19, 2023 closing playing window when message mounted still causes crash.
        #    Maybe Playlists() should have it's own thread handler?
        # Aug 3/23 - See lcs.out_cast_show_print() to include here
        text = "The 'Save Playlist As...' function is a work in progress.\n\n" + \
            "When 'Save As...' is chosen any changes to current playlist\n" + \
            "(such as new songs) are lost and go to the new playlist.\n\n" +\
            "The 'Save As...' function will behave like the 'New Playlist'\n" + \
            "function except playlist is fully populated with what's in memory.\n\n" +\
            "\tOne Tab\tTwo Tabs\tThree Tabs\tFour Tabs\n" + \
            "\t\tTwo tabs at once\n" + \
            "\t\t\tThree tabs at once\n" + \
            "\t\t\t\tFour tabs at once\n" + \
            "\t\tPair of tabs\t\tAnother pair of tabs\n" + \
            "\t\t\t\t\t\tSix tabs at once\n" + \
            "\t\t\t\t\t\t\t\tEight tabs at once\n\n" + \
            "When there is a need for the function it will be written."
        message.ShowInfo(self.parent, "Save As...", text, icon='error',
                         align='left', thread=self.get_thread_func)
        return False  # We are all done. No window, no processing, nada

    def edit_playlist(self):
        """ Edit Playlist in current (active / "act_") work fields

            Type-'playlist', Action-P999999, Master-L999, Detail-Playlist Name,
                Target-JSON list of sorted Music IDs, Size=MB, Count=# Songs,
                Seconds=Total Duration, Comments=Playlist Description

            close() must be done first because no self.top window open """

        ''' View has no validation checks '''
        if self.state == 'view':
            return True

        ''' Save As... is not working. Bail out immediately '''
        if self.state == 'save_as':  # NOT USED.
            return self.check_save_as()
        ''' Closing Playlist and returning to Favorites? Do this test first
            because other tests are irrelevant. If pending song updates,
            confirm abandoning save to playlist '''
        if self.state == 'close' or self.state == 'new' or \
                self.state == 'open' or self.state == 'delete':
            if self.get_pending() > 0:
                # self.top window hasn't been created so use self.parent instead
                title = "Playlist has not been saved!"
                text = "Checkboxes in Music Location have added songs or\n" + \
                       "removed songs. These changes have not been saved to\n" + \
                       "storage."
                self.info.cast(title + "\n\n" + text, "warning")
                dialog = message.AskQuestion(  # Confirm will be added
                    self.parent, title, text, icon='warning',
                    align='left', thread=self.get_thread_func)
                if dialog.result != 'yes':
                    return False
            if self.state == 'close':
                return True  # close Playlists approved
        ''' Retrieve name and description from tkinter variables. '''
        new_name = self.scr_name.get()
        new_description = self.scr_description.get()
        if self.state == 'new' or self.state == 'save_as':
            ''' Blank out name and description for name change tests '''
            self.act_name = ""
            self.act_description = ""
        ''' A playlist name is always required '''
        if new_name == "":
            if self.input_active:
                text = "Enter a unique name for the playlist."
            else:
                text = "First click on a playlist entry."
            message.ShowInfo(self.top, "Name cannot be blank!",
                             text, icon='error', thread=self.get_thread_func)
            return False
        ''' A playlist description is recommended for Apple Users '''
        if new_description == "" and self.input_active:
            text = "Enter a playlist description gives more functionality\n" +\
                "in other Music Players such as iPhone."
            message.ShowInfo(self.top, "Description is blank?",
                             text, icon='warning', thread=self.get_thread_func)
        ''' Tests when playlist name and description are keyed in '''
        if self.input_active:
            ''' Same name cannot exist in this location '''
            if new_name in self.names_for_loc and \
                    new_name != self.act_name:
                text = "Playlist name has already been used."
                message.ShowInfo(self.top, "Name must be unique!",
                                 text, icon='error', thread=self.get_thread_func)
                return False
            if new_name in self.names_all_loc and \
                    new_name != self.act_name:
                title = "WARNING: Name is not unique"
                text = new_name + "\n\n"
                text += "Is used in another location. This might cause confusion."
                dialog = message.AskQuestion(  # Confirm will be added
                    self.parent, title, text, icon='warning',
                    align='left', thread=self.get_thread_func)
                if dialog.result != 'yes':
                    return False
        ''' Creating a new playlist? '''
        if self.state == 'new':
            # Passed all tests so create new number string
            if len(self.all_numbers) > 0:
                last_str = self.all_numbers[-1]  # Grab last number
                val = int(last_str[1:]) + 1  # increment to next available
                self.act_code = "P" + str(val).zfill(6)
            else:
                self.act_code = "P000001"  # Very first playlist
            self.act_loc_id = lcs.open_code
            self.act_id_list = []  # Empty list
            self.act_size = 0  # Size of all song files
            self.act_count = 0  # len(self.music_id_list)
            self.act_seconds = 0.0  # Duration of all songs
        ''' If values entered, update work variables self.act_xxx '''
        if self.input_active:
            self.act_name = new_name
            self.act_description = new_description

        if self.state == 'open':
            pass

        if self.state == 'delete':
            # self.top window hasn't been created so use self.parent instead
            text = "\nThere are " + '{:n}'.format(self.act_count) + \
                   " songs in the playlist.\n"
            if self.open_code == self.act_code:
                text += "\nThe playlist is currently playing and will be stopped.\n"
            dialog = message.AskQuestion(
                self.top, "Confirm playlist deletion", text, icon='warning',
                thread=self.get_thread_func)
            if dialog.result != 'yes':
                return False
            return True

        if self.state == 'save':
            # DEPRECATED, save() function is now used
            pass

        if self.state == 'save_as':  # NOT USED
            pass

        return True

    def save_playlist(self):
        """ Save Playlist in current (active / "act_") work fields

            Type-'playlist', Action-P999999, Master-L999, Detail-Playlist Name,
                Target-JSON list of sorted Music IDs, Size=MB, Count=# Songs,
                Seconds=Total Duration, Comments=Playlist Description """
        ''' Current Playlist work fields - History Record format '''
        if not self.open_code or not self.open_loc_id or not self.open_name:
            print("Playlists.save_playlist() Error: One of three are blank:")
            print("self.open_code:", self.open_code,
                  "  | self.open_loc_id:", self.open_loc_id,
                  "  | self.open_name:", self.open_name)
            toolkit.print_trace()
            return
        sql.save_config('playlist', self.open_code, self.open_loc_id,
                        self.open_name, json.dumps(self.open_id_list),
                        self.open_size, self.open_count, self.open_seconds,
                        self.open_description)

    def save_act(self):
        """ Save self.act_xxx vars after rename """

        sql.save_config('playlist', self.act_code, self.act_loc_id,
                        self.act_name, json.dumps(self.act_id_list),
                        self.act_size, self.act_count, self.act_seconds,
                        self.act_description)

    def open_playlist_with_browser(self):
        """ View music videos natively on website
        """
        try:
            webbrowser.open_new(self.act_description)
        except Exception as err:
            print("Exception:", err)

    def delete_playlist(self):
        """ Delete Playlist using History Row ID """
        sql.hist_cursor.execute("DELETE FROM History WHERE Id = ?",
                                [self.act_row_id])
        sql.con.commit()

    def reset(self, shutdown=False):
        """ Close Playlists Maintenance Window
            Named "reset" instead of "close" because, "close()" is used by
            callers to "close" playlist and use Default Favorites instead.
            When called with self.top.protocol("WM_DELETE_WINDOW", self.reset)
            shutdown will contain <Tkinter.Event instance at 0x7f4ebb968ef0>
        :param shutdown: True = shutdown so don't update lib_top """

        self.youLrcDestroyFrame()  # Lyrics window if open will close
        if self.tt and self.tt.check(self.top):
            self.tt.close(self.top)
        if self.top:
            geom = monitor.get_window_geom_string(self.top, leave_visible=False)
            monitor.save_window_geom('playlists', geom)
            self.top.destroy()
            self.top = None  # Extra insurance
        # print("self.top after .destroy()", self.top)
        PlaylistsCommonSelf.__init__(self)  # Define self. variables
        #self.top = None  # Indicate Playlist Maintenance is closed

        ''' Enable File, Edit & View Dropdown Menus for playlists '''
        if isinstance(shutdown, tk.Event):
            self.enable_lib_menu()  # <Escape> bind
        elif not shutdown:  # When shutting down lib_top may not exist.
            self.enable_lib_menu()  # Sep 9/23 - patch inside to fix errors

    # noinspection PyUnusedLocal
    def apply(self, *args):
        """ Validate, Analyze mode (state), update database appropriately. """
        if not self.edit_playlist():
            return

        if self.state == 'delete':
            # TODO: Delete resume, chron_state, hockey_state and open_states
            #       Or just set a deleted flag and not physically delete.
            self.info.cast("Deleted playlist: " + self.act_name, action="delete")
            self.delete_playlist()  # Doesn't use self.open_code
            if self.open_code == self.act_code:
                # Just deleted opened playlist
                print("After Playlists.delete_playlist() Calling def play_close()")
                self.play_close()  # must be called before name is set
                self.reset_open_vars()  # Set all self.open_xxx to None
                self.reset()  # Close everything down, E.G. destroy window
                self.display_lib_title()
                self.apply_callback(delete_only=True)

        elif self.state == 'open' and self.act_description.startswith("http"):
            self.info.cast("Opening Web Browser for: " + self.act_name + " at " +
                           self.act_description)
            self.open_playlist_with_browser()
            self.reset()  # Close everything down, E.G. destroy window

        elif self.state == 'open':
            self.info.cast("Opened playlist: " + self.act_name + " with " +
                           str(self.act_count) + " songs.")
            self.play_close()  # must be called before name is set
            self.make_open_from_act()
            self.reset()  # Close everything down, E.G. destroy window
            self.apply_callback()  # Parent will start playing (if > 1 song in list)

        elif self.state == 'new':
            self.info.cast("Created new playlist: " + self.act_name, action="add")
            self.play_close()  # must be called before name is set
            self.make_open_from_act()  #
            self.save_playlist()  # Save brand new playlist
            self.apply_callback()  # Tell parent to start marking checkboxes

        elif self.state == 'view':
            if self.checkYouTubePlaylist():
                if self.buildYouTubePlaylist():
                    #print("buildYouTubePlaylist() SUCCESS")
                    self.displayYouTubePlaylist()
                    return  # Can't destroy window below
                else:
                    print("buildYouTubePlaylist() FAILED")
            else:
                self.displayMusicIds()
                return  # Can't destroy window below

        elif self.state == 'rename':
            self.info.cast("Renamed playlist: " + self.act_name + " with " +
                           str(self.act_count) + " songs.", action="update")
            if self.open_code and self.open_code == self.act_code:
                self.open_name = self.act_name  # 'rename' title
                self.open_description = self.act_description
                # Not sure about saving config & wiping out any WIP
                self.display_lib_title()
            else:
                self.save_act()  # sql.save_config() self.act_code, etc.

        elif self.state == 'save':
            ''' Remaining options is Save '''
            self.save_playlist()
            self.info.cast("Saved playlist: " + self.act_name + " with " +
                           str(self.act_count) + " songs.", action="update")
        else:
            self.info.cast("Playlists.apply() bad state: " + self.state, 
                           action="update", icon='error')

        if self.parent:
            # During shutdown we somehow get to this point and below gets error
            # because lib_top no longer exists.
            self.display_lib_title()  # Important that self.open_name is ACCURATE

        self.reset()  # Close everything down, E.G. destroy window


# ==============================================================================
#
#       InfoCentre() class.
#
# ==============================================================================
class InfoCentre:
    """ Usage:

            self.info.cast() - Create dict and call zoom(show_close=False).
            self.info.fact() - Create dict only.
            self.info.zoom() - Expand/collapse frame. Show dict.
            self.info.view() - Call zoom(), but use close button to exit.

        TODO from PHONE:

            Delete cast type info already viewed.
            
            Add line numbers last viewed because may not have scrolled down.
            
            Initially keep all dict entries because selected deleting
            is complicated.

        NOTES:

            HUGE LAG when thousands of dictionaries. Currently use silent
            mode in FileControl() to fix that problem.
    """

    def __init__(self, lib_top=None, lib_tree=None, banner_frm=None,
                 tooltips=None):
        """  __init__ """
        # noinspection SpellCheckingInspection
        '''
            Thoughts.

            Currently pushing down lib_tree is smooth. It is annoying if checking
            boxes though.

            Sweeping over is jagged and annoying. Sweeping over is preferrable for
            checking boxes that don't move, or at least don't move much. If checking
            at the top then zoom covers it up.

            That said, if working on checking boxes and a new song starts the list
            is totally arranged to highlight new song. An indicator that boxes are
            being checked or albums are being expanded for last few seconds is
            needed. Then after idle, highlight current song in green. If clicking
            in tree go back to last position worked on.

            Text can be copied to clipboard. Enable entry state.  CTRL+C DOESN'T WORK.
            PLUS COLORS INTERRUPT MOUSE HIGHLIGHTING

            What about icon='error', icon='warning' option?

            Hamburger button at top right?    

            What does this mean button with hyperlink to pippim website for help text.

            Save message button? Where would save go?    

            Message recurs until acknowledged? E.G. New songs added to device and
                library can be refreshed.

            Interface to IoT? E.G. TV Powered / Eyesome

            Notes about song pops up when play starts? 

            Send message if mouse hasn't entered a monitor in say 15 minutes and offer
                to shut off the picture to save 100 watts? (TV stays on with sound).
                BASICALLY INCORPORATE DIMMER TECHNOLOGY?

        ======================================================================        

        Opening playlists slows down from <1 second to over 7 seconds.

        ----------------------------------------------------------------------
        SLOWDOWN BUG: https://gitlab.gnome.org/GNOME/gnome-shell/-/issues/3125
        SLOWDOWN BUG: https://gitlab.gnome.org/GNOME/gnome-shell/-/issues/2674
        '''

        ''' self-ize parameter list '''
        self.lib_top = lib_top
        self.lib_tree = lib_tree  # Used in development version will probably drop
        self.banner_frm = banner_frm  # Frame shared by button ruler and zoom
        self.tt = tooltips  # Tooltips() class instance

        ''' Window variables '''
        self.frame = None  # Zoom frame goes where button ruler line was
        self.widget = None  # parent widget passed to Tooltips()
        self.close_button = None  # Close zoom frame.  Only appears during .view()
        self.text = None  # tk.Text with scrollbars
        self.text_scroll_y = None  # scroll up and down (y-axis)
        self.height = None  # 33% of lib_top height
        self.width = None  # Full width of lib_top

        ''' Information Dictionary '''
        self.dict = OrderedDict()  # Use 'View' Dropdown Menu, 'Show Debug' to see last
        self.list = []  # list of self.dict. Newest first: self.list.insert(0, self.dict)
        self.zoom_is_active = False

        #self.info.cast(text)  # The text is cast into expanding frame for brief period
        # the frame collapses.  The casts are read by click on ruler bar button or
        # from View dropdown menu pick "Information Centre" option which is the same
        # self.info.view() function.

        # After reading a cast it is moved into cast history. A timestamp is auto-added to
        # all casts.

        #self.info.fact(text)  # facts which appears after last .splash
        # Then older .splash appear after .facts with most recent to oldest .splash for
        # the session.  .splashes are lost on restart.  After last splash is read it goes
        # into the history splash bucket but appears at top because it's the most recent.
        # A number of facts can be posted by fact type. When a new fact it posted if the
        # same type exists it is moved into splash history. A timestamp is auto-added to
        # all facts.

        # After reading, some facts are moved into fact history. For example "New Playlist"
        # is historic but "Open Playlist" is trivial and only needs to be viewed once.

        # Other facts are already stored in SQL History Table such as lyric scraping
        # and CD encoding.

        # facts are not cast when published. User must click on ruler bar button or
        # from View dropdown menu pick "Information Centre" option which is the same
        # function as a button click

        #self.info.view()  # The view function never fades out until user moves mouse out
        # of the region or picks the close button
        # Then older .splash appear after .facts with most recent to oldest .splash for
        # the session.  .splashes are lost on restart.  After last splash is read it goes
        # into the history splash bucket but appears at top because it's the most recent.
        # A number of facts can be posted by fact type. When a new fact it posted if the
        # same type exists it is moved into splash history.

        ''' Working fields for testing '''
        self.test = None
        self.test_label = None
        self.msg_recv = None
        self.test_results = []  # list of tuples (time.time(), alpha, dict fields?)

        self.start_time = None  # Time test started
        self.time = None  # Time message was received
        self.last_delta_time = 0.0
        self.original_sleep = None  # Override sleep time for polling tooltips

        ''' Track old and new y-axis position to keep same rows displayed '''
        self.old_y_top = self.old_y_end = 0.0

    def new_dict(self, new_type, text, severity=None, action=None, patterns=None,
                 collapsed=False, ms_font=None):
        """
        Create a new dictionary
        :param new_type: 'cast' or 'fact' 
        :param text: Formatted text (\n, \t, etc.)  for tk.Text widget.
        :param severity: 'info', 'warning', 'error'
        :param action: 'open', 'update', 'add', 'delete', 'rename'
        :param patterns: List of tuples ("search words", FG color, BG color)
        :param collapsed: When true, text is collapsed and click to expand
        :param ms_font: Optional font to use. e.g. ("courier", 11) or "TkFixedFont"
        :return now: time dictionary created
        """
        now = time.time()
        self.dict = \
            OrderedDict([
                ("time", now), ("source", []), ("type", "cast"),
                ("severity", "info"), ("action", ""), ("text", ""),
                ("text_start", ""), ("text_end", ""), ("patterns", []),
                ("collapsed", ""), ("font", ""), ("view_time", now)])
        # time: micro-seconds (epoch) serves as unique key
        # source: program name, class name, print_trace() results
        # type: 'cast', 'fact'
        # severity: 'info', 'warning', 'error'
        # action: 'add', 'update', 'rename', 'delete', 'open'
        # text: e.g. "Less < 80% played, last access time reset"
        # text_start: start position within tk.Text widget where text was painted
        # text_end: end position used with start_position to apply patterns
        # patterns: e.g. [("Added", "white", "green"), ("Deleted", "red", "LightGrey")]
        # start_collapsed: e.g. True is collapsed, click button to expand.
        #   start_collapsed is future function.
        # font: defaults to g.FONT
        # view_time: 0.0 = False. After viewing, some info_type+action deleted
        #   view_time is future function.

        self.dict['type'] = new_type
        # Always delete last three entries from InfoCentre (get_trace, new_dict, cast/fact)
        self.dict['source'] = toolkit.get_trace()[:-3]
        # TODO: Use "show_debug()" to see results and filter / merge lines.
        # noinspection SpellCheckingInspection
        ''' Some thoughts to shorten trace '''
        # If first two entries contain "/m" delete them

        # Read remaining lines backwards and build new 'source'
        # line.replace('File "' + cwd + os.sep', '')
        # line.replace('", line ', '@', 1)
        # two_lines = line.split(', in ')
        # part1 = two_lines[0]
        # two_liens = two_lines[1].split('\n  ')
        # part2 = two_lines[0]
        # part3 = two_lines[1]  # What do do about optional comments after "#"?
        # new_line = part1 + "-" + part_2 + "(): "

        if severity is None:
            severity = 'info'
        if action is None:
            action = 'open'  # Another choice would be 'run'
        if patterns is None:
            patterns = []
        self.dict['severity'] = severity
        self.dict['action'] = action
        self.dict['text'] = text
        self.dict['patterns'] = patterns
        self.dict['collapsed'] = collapsed
        if font:
            self.dict['font'] = ms_font
        else:
            self.dict['font'] = g.FONT
        return now

    def cast(self, text, severity=None, action=None, patterns=None,
             collapsed=False, ms_font=None):
        """ Briefly display message in expanding/collapsing Information Centre.

        :param text: Formatted text (\n, \t, etc.)  for tk.Text widget.
        :param severity: 'info', 'warning', 'error'
        :param action: 'open', 'update', 'add', 'delete', 'rename'
        :param patterns: List of tuples ("search words", FG color, BG color)
        :param collapsed: When true, text is collapsed and click to expand
        :param ms_font: Optional font to use. e.g. ("courier", 11) or "TkFixedFont"
        :return: time assigned to information centre entry. """

        ''' 
            PROCESSING STEPS:
                Create dictionary
                Insert dictionary in list
                Call splash function


            BUG Oct 17/23 - info.cast(piggy_back  -  Chrome temporary files found.)
                This should not stay as a tooltip.

                info.fact(piggy_back - Title: Can't Turn Back Year: 1983)
                This should not stay as a tooltip.

        '''

        ''' If zoom active and being spammed by .cast() '''
        if self.zoom_is_active:
            self._close_cb()
            self.tt.poll_tips()

        time_stamp = self.new_dict('cast', text, severity, action, patterns,
                                   collapsed, ms_font)
        self.list.insert(0, self.dict)  # self.dict stays in memory untouched

        ''' If last broadcast is still visible cannot launch another '''
        if not self.zoom_is_active:  # If zoom is active this will be fact
            self.zoom()  # Message broadcast
        return time_stamp  # time_stamp can be used by caller to massage text

    def fact(self, text, severity=None, action=None, patterns=None,
             collapsed=False, ms_font=None):
        """ Record fact without splashing the text.

        :param text: Formatted text (\n, \t, etc.)  for tk.Text widget.
        :param severity: 'info', 'warning', 'error'
        :param action: 'open', 'update', 'add', 'delete', 'rename'
        :param patterns: List of tuples ("search words", FG color, BG color)
        :param collapsed: When true, text is collapsed and click to expand
        :param ms_font: Optional font to use. e.g. ("courier", 11) or "TkFixedFont"
        :return: time assigned to information centre entry. """

        ''' PROCESSING STEPS:
                Create dictionary
                Insert dictionary in list '''

        time_stamp = self.new_dict('fact', text, severity, action, patterns,
                                   collapsed, ms_font)
        self.list.insert(0, self.dict)  # self.dict stays in memory untouched
        return time_stamp  # time_stamp can be used by caller to find dictionary

    def view(self):
        """ View dropdown menu, Information Centre option picked or
            button bar ruler line clicked.
        """

        ''' If zoom active and being spammed by .view() '''
        if self.zoom_is_active:
            self._close_cb()  # Pretend ToolTips() told us to close
            self.tt.poll_tips()

        self.zoom(show_close=True)  # Close button appears to close frame

    def zoom(self, show_close=False):
        """ "Zoom" messages by expanding/collapsing information centre panel
            self.dict is populated with all variables caller sent

        :param show_close: Display a close button and extend visible time """
        if self.zoom_is_active and show_close is False:
            ''' Zoom already active and being spammed by .cast() '''
            print("\nInfoCentre.zoom() defense lines breached in cast\n")
            print(self.dict['text'][0])
            return

        ''' Indicate zoom is active '''
        self.zoom_is_active = True
        fonts_used = []  # List of fonts used so far

        if self.frame:  # This test needed to catch programmer errors
            print("\nInfoCentre.zoom() SECOND defense line breached !!\n")
            print(self.dict['text'][0])
            self._close_cb()  # Pretend ToolTips() told us to close
            return

        ''' Get current lib_top coordinates  '''
        self.height = int(self.lib_top.winfo_height() / 3)
        self.width = self.lib_top.winfo_width()

        ''' Recycled test needs local instead of static variable defined '''
        text = self.dict['text']

        ''' June 21, 2023 - test work fields, leave for now '''
        self.test = True
        self.msg_recv = text  # Formatted text (with \n, \t) to be displayed
        # print("Caller says:", self.msg_recv)
        self.test_results = []  # Empty last test
        self.start_time = time.time()  # To calculate total elapsed time
        self.last_delta_time = self.start_time  # To calculate ms between calls

        ''' Build tk.Frame and tk.Text widgets. Optional tk.Button to close frame '''
        self.frame = tk.Frame(self.banner_frm, bg="black", height=7)
        self.frame.grid()
        if show_close:
            ''' Close Button - NOTE: This calls reset() function !!! '''
            self.close_button = tk.Button(self.frame, text="✘ Close", bg="gold",
                                          width=g.BTN_WID2 - 4, command=self._close_clicked)
            self.close_button.place(height=MON_FONTSIZE * 3, width=g.BTN_WID2 * 8,
                                    x=10, y=10)
            visible_span = 1000 * 60 * 2  # Visible for two minutes per line
        else:
            visible_span = 1000  # Visible 1 second per tk.Text line

        ''' Create custom (highlighting supported) tk.Text widget with scrollbars '''
        self.text = toolkit.CustomScrolledText(
            self.frame, bg="black", height=self.height, width=self.width, 
            fg="gold", font=g.FONT, state="normal")
        self.text.place(height=self.height-60, width=self.width-20, x=10, y=50)
        self.text.config(highlightthickness=0, borderwidth=0)
        self.text.vbar.config(troughcolor='black', bg='gold')
        self.text.vbar.config(width=SCROLL_WIDTH)

        ''' TODO: bind Control + C to copy text from customScrolledText 
                  Search on lyrics_score_box which allows <CTRL>+C
        '''
        ''' Below allows <Control> + C to copy from text scrollbox '''
        self.text.configure(state="normal")  # It's not working though...

        ''' Read all dictionaries and stuff into CustomScrolledText object '''
        for i, read_dict in enumerate(self.list):

            ''' Calculate length of line draw header which is part of message now '''
            line_draw = int(self.width / MON_FONTSIZE * .63)
            text_start = self.text.index("end")  # https://stackoverflow.com/a/19477323/6929343
            self._str_to_text_widget(
                "─" * line_draw + "┨ " + tmf.ago(read_dict['time']), g.FONT)
            text_body_start = self.text.index("end") 
            self._str_to_text_widget(read_dict['text'], read_dict['font'])
            text_end = self.text.index("end")

            ''' Update text_start and text_end without corrupting current self.dict '''
            read_dict['text_start'] = text_start
            read_dict['text_end'] = text_end
            self.list[i] = read_dict
            ''' Now apply patterns between text start and text end '''
            for entry in read_dict['patterns']:
                pattern, fg, bg = entry  # fg + bg color names forms the tag name
                self.text.tag_configure(fg + bg, foreground=fg, background=bg)
                self.text.highlight_pattern(pattern, fg + bg,
                                            start=text_start, end=text_end)

            ''' Font tag configuration each time new self.Text defined '''
            try:
                font_ndx = fonts_used.index(read_dict['font'])
                font_name = "TextFontNdx" + str(font_ndx)
                #print("FOUND font:", font_name, read_dict['font'])
            except ValueError:
                font_name = "TextFontNdx" + str(len(fonts_used))
                fonts_used.append(read_dict['font'])
                self.text.tag_configure(font_name, font=read_dict['font'])
                #print("Adding font:", font_name, read_dict['font'])

            self.text.tag_add(font_name, text_body_start, text_end)

            if not show_close:  # No close button is displayed
                break  # Called by .cast() so only most recent message displayed

        self.text.update()  # Is this necessary? CONFIRMED YES
        #self.text.configure(state="disabled")  # comment to test entry

        ''' .view() has close button, but .cast() doesn't. '''
        if show_close:
            self.widget = self.close_button
            anchor = "sw"  # South west under Close button
        else:
            self.widget = self.text
            anchor = "sc"  # South centered under wide ruler line

        ''' Add CustomScrolledText widget to Tooltips() as 'piggy_back' '''
        self.tt.add_tip(
            self.widget, text=text, anchor=anchor, tool_type="piggy_back",
            pb_alpha=self._alpha_cb, pb_leave=self._leave_cb,
            pb_ready=self._ready_cb, pb_close=self._close_cb, 
            visible_span=visible_span, extra_word_span=100,
            fade_in_span=300, visible_delay=201, fade_out_span=200
            # 2023 Limitation: 'visible_delay' must > 'fade_out_span'
        )

        ''' Start Tooltips() by saying mouse hovered over the text widget. '''
        self.tt.log_event('enter', self.widget, 10, 5)  # x=10, y=5

    def _close_clicked(self):
        """ When close button clicked tell Tooltips to start fading out """
        # Generates error inside ToolTips() because fade not finished when
        # widget is closed early.
        self.tt.log_event('press', self.widget, 100, 50)  # x=100, y=50

    def _str_to_text_widget(self, text, ms_font):
        """ Line draw border or single text message to tk.Text box """
        self.text.configure(state="normal", font=ms_font)
        self.text.insert(tk.END, text + "\n")
        self.text.update()  # Is this necessary? Don't know yet...
        self.text.configure(state="disabled")

    def test_tt(self, text):
        """ Use to log Tooltips() responses
        :param text: simple message "Hello World".
        :return: None """
        global SLEEP_PAUSED
        self.original_sleep = SLEEP_PAUSED  # Save for speedup tests
        SLEEP_PAUSED = 20  # Was 33. Setting to 20 gives 29 to 41 during fade out.

        ''' Get current lib_top coordinates  '''
        self.height = int(self.lib_top.winfo_height() / 3)
        self.width = self.lib_top.winfo_width()

        self.test = True
        self.msg_recv = text  # Formatted text (with \n, \t) to be displayed
        #print("Caller says:", self.msg_recv)
        self.test_results = []  # Empty last test
        self.start_time = time.time()  # To calculate total elapsed time
        self.last_delta_time = self.start_time  # To calculate ms between calls

        ''' Build new frame and Text widget. Add to Tooltips() '''
        self.frame = tk.Frame(self.banner_frm, bg="black", height=7)
        self.frame.grid()
        self.text = tk.Text(self.frame, bg="black", height=self.height,
                            width=self.width, fg="gold", font=g.FONT)
        self.text.place(height=self.height, width=self.width, x=40, y=10)
        self.text.config(highlightthickness=0, borderwidth=0)

        text = "\tInfoCentre._tt.test()\n\n" + \
               "\t\t          Why is it spelled that way?\n\n" + \
               '\t\t   In programming, "center" is an action.\n\n' +\
               '\t\t       In this case, "Centre" is a place.'

        ''' Aug 26/23 - Not updated to dict['font'] yet '''
        self._str_to_text_widget(text, g.FONT)  # Update object self.text with text
        # Limitation: 'visible_delay' must be greater than 'fade_out_span'
        self.widget = self.text
        self.tt.add_tip(
            self.widget, text=text, anchor="sc", tool_type="piggy_back",
            pb_alpha=self._alpha_cb, pb_leave=self._leave_cb,
            pb_ready=self._ready_cb, pb_close=self._close_cb, 
            visible_span=visible_span, extra_word_span=100,
            fade_in_span=300, visible_delay=201, fade_out_span=200
        )
        ''' DEFAULT OPTIONS:
VISIBLE_SPAN = 5000     # ms balloon tip remains on screen (5 sec/line)
EXTRA_WORD_SPAN = 500   # 1/2 second per word if > VISIBLE_SPAN
FADE_IN_SPAN = 500      # 1/4 second to fade in
FADE_OUT_SPAN = 400     # 1/5 second to fade out
        '''

        ''' Fake event as if mouse entered parent widget bbox '''
        self.tt.log_event('enter', self.widget, 100, 50)  # x=100, y=50

        ''' Need to update for first yview test in _alpha_cb '''
        #self.lib_tree.update_idletasks()  # Without this, yview stays same
        #print("Start:", self.lib_tree.yview())

        ''' Track old and new y-axis position to keep same rows displayed '''
        #self.old_y_top, self.old_y_end = self.lib_tree.yview()

    def _alpha_cb(self, alpha):
        """ Called from Tooltips whenever fading-in or fading-out alpha changes.
            Pushes treeview rows down smoothly but makes clicking boxes almost
            impossible when in motion. Plus visually distracting.
        :param alpha: % fading-in or fading-out from 0.0 to 1.0
        :return: None """
        ''' Expand / Collapse frame with tk.Text widget inside. '''
        new_height = int(self.height * alpha)
        self.frame.config(height=new_height, width=self.width)

    def _alpha_cb_dev(self, alpha):
        """ Called from Tooltips whenever fading-in or fading-out alpha changes
            Sweeps down over treeview rows down jaggedly. Clicking boxes is
            easier when in motion. Shaking is visually distracting.
        :param alpha: % fading-in or fading-out from 0.0 to 1.0
        :return: None
        """

        ''' Track old and new y-axis position to keep same rows displayed '''
        old_y_top, old_y_end = self.lib_tree.yview()

        ''' Expand / Collapse frame with tk.Text widget inside. '''
        new_height = int(self.height * alpha)
        self.frame.config(height=new_height, width=self.width)

        ''' Adjust y-axis so same row stays at bottom and tree relatively stable '''
        self.lib_tree.update_idletasks()  # Without this, yview stays same
        new_y_top, new_y_end = self.lib_tree.yview()
        end_moved = new_y_end - old_y_end
        self.lib_tree.yview_moveto(old_y_top - end_moved)

    def _alpha_cb_debug_version(self, alpha):
        """ Called from Tooltips whenever fading-in or fading-out alpha changes
        :param alpha: % fading-in or fading-out from 0.0 to 1.0
        :return: None """
        now = time.time()  # debug
        delta = now - self.start_time  # Debug
        perc = alpha * 100  # debug
        sleep = int((now - self.last_delta_time) * 1000)  # debug
        p_str = '({0:.3f}s, {1:n}ms, {2:.1f}%)'.format(delta, sleep, perc)
        self.test_results.append(p_str)  # debug

        ''' Track old and new y-axis position to keep same rows displayed '''
        old_y_top, old_y_end = self.lib_tree.yview()

        ''' Expand / Collapse frame with tk.Text widget inside. '''
        new_height = int(self.height * alpha)
        print(p_str, "new_height:", new_height)  # Debug
        self.frame.config(height=new_height, width=self.width)
        self.last_delta_time = now  # Debug

        ''' Adjust y-axis so same row stays at bottom and tree relatively stable '''
        self.lib_top.update_idletasks()  # Without this, yview stays same
        new_y_top, new_y_end = self.lib_tree.yview()
        end_moved = new_y_end - old_y_end
        self.lib_tree.yview_moveto(old_y_top - end_moved)

    def _leave_cb(self):
        """ Called from Tooltips if mouse moves out of Information Centre.
            Tell tt to start fading out.
        :return: None """

        elapsed = time.time() - self.start_time
        if elapsed > 1000.0:  # Ignore if less than 1 second
            self.tt.log_event('press', self.widget, 100, 50)  # x=100, y=50


    def _ready_cb(self):
        """ Called from Tooltips when ready for message to be displayed.
        :return: None """
        pass  # Nothing to do

    def _close_cb(self):
        """ Called from Tooltips when fading-out process has ended.
        :return: None """

        ''' May have manually closed frame at same time Tooltips closes '''
        if self.frame:
            self.frame.config(height=7)  # Last height can be 0 - 30px
            self.lib_top.update()  # Update before destroy or last stays

            ''' BUG Oct 17/23 - info.cast(piggy_back  -  Chrome temporary files found.)
                    The tooltip is staying. When _close is called, Chronology
                    button is closed, creating errors on hover. 
            
                Suspect problem info.cast called just before play top creation
                and tt.poll_tips isn't called to process info.cast until it
                expires. It begins fading out before it has faded in.         
            '''
            #self.tt.poll_tips()
            # RuntimeError: maximum recursion depth exceeded while
            # calling a Python object

            #print("Checking self.widget")
            if self.tt.check(self.widget, prefix_only=False):
                #print("Closing self.widget")
                self.tt.close(self.widget)  # Remove 'piggy_back' tooltip

                ''' Oct 18/23 TEST - '''
                if self.widget == self.text:
                    #toolkit.print_trace()
                    print("_close_cb(): Probably closed wrong widget")
                    tt_dict = self.tt.get_dict(self.widget)  # Not found
                    if tt_dict is None:
                        prt_time = datetime.datetime.now().strftime("%M:%S.%f")[:-2]
                        print(prt_time, "_close_cb() - tt_dict not found for:",
                              str(self.widget)[-4:])
                    # Next step is to print widget for Hide Chronology after
                    # built

            # Aug 12/23 - For some reason, self.frame is None for first time.
            if self.frame:
                self.frame.destroy()  # Nuke the frame used for info message
            self.frame = None

        ''' Ugly patch to show that zoom has finished '''
        self.zoom_is_active = False

        ''' If 33ms sleep was overriden, restore original value. '''
        if self.original_sleep is not None:
            global SLEEP_PAUSED
            SLEEP_PAUSED = self.original_sleep
            self.original_sleep = None  # Use normal 33ms updates


# ==============================================================================
#
#       Independent (Stand Alone) Functions
#
# ==============================================================================
def half_split(stg, sep, pos):
    """ Split string in halves. e.g. position 2 instead of position 1.
        From: https://stackoverflow.com/a/52008134/6929343
    """
    stg = stg.split(sep)
    return sep.join(stg[:pos]), sep.join(stg[pos:])


def play_padded_number(song_number, number_digits, prefix=NUMBER_PREFIX):
    """ Pad song number with spaces to line up song name evenly
        Called from refresh_acc_times() and build_chron_line()
    """
    padded_number = ""
    if song_number is None:
        print("mserve.py play_padded_number() received song_number '<type>None'")
        song_number = "?"
    this_digits = len(str(song_number))
    pad_digits = number_digits - this_digits
    for _ in range(pad_digits):
        padded_number = padded_number + DIGIT_SPACE
    return prefix + padded_number + str(song_number)


def make_ellipsis(text, cutoff):
    """ Change: 'Long long long long' to: 'Long long...' """
    if not text:
        print("mserve.py make_ellipsis() no text passed")
        return "???..."
    if len(text) > cutoff:
        return text[:cutoff - 3] + "..."
    return text


def sec_min_str(seconds):
    """ TV Hockey countdown remaining. """
    sec_str = '%.0f' % seconds
    min_str = '%.0f' % (seconds / 60)
    rem_str = '%02d' % (seconds % 60)
    return sec_str + " seconds (" + min_str + " min: " + rem_str + " sec)"


def convert_seconds(s):
    """ Convert duration d:hh:mm:ss to seconds """
    # Grab segments between : in hh:mm:ss
    if PYTHON_VER == "2":
        seg = map(int, s.split(':'))  # Python 2.x
    else:
        seg = list(map(int, s.split(':')))  # Python 3.x +
    return sum(n * sec for n, sec in zip(seg[::-1], (1, 60, 3600)))


def ffplay_extra_opt(start=None, fade_in=3.0, fade_out=0.0, duration_secs=0.0):
    """ Format extra_opt string to start playing song at x seconds
        :param start: whole number string or int to start playing song
        :param fade_in: Start volume at 0% and go to 100% over fade_in
        :param fade_out: Lower volume to 0% during fade_out.
        :param duration_secs: Optional duration to play, E.G. 10 seconds
            if fade_out is being used then duration_secs must be provided.
        :return extra_opt: formatted string passed to ffplay command
    """
    if start is None:
        start = 0
    extra_opt = ' -ss ' + str(start)  # start position

    if fade_in and float(fade_in) > 0.0:
        # noinspection SpellCheckingInspection
        extra_opt += ' -af "afade=type=in:start_time=' + str(start) + \
                     ':duration=' + str(fade_in) + '"'  # fade-in time

    if fade_out and float(fade_out) > 0.0 and \
            duration_secs and float(duration_secs) > 0.0:
        fade_start = float(start) + float(duration_secs) - float(fade_out)
        if fade_start < 0.0:
            print("ffplay_extra_opt() Programming error. fade_out:",
                  fade_out, " | duration_secs:", duration_secs)
        else:
            # noinspection SpellCheckingInspection
            extra_opt += ' -af "afade=type=out:start_time=' + str(fade_start) + \
                         ':duration=' + str(fade_out) + '"'

    if duration_secs and float(duration_secs) > 0.0:
        extra_opt += ' -t ' + str(duration_secs)  # could be int or float

    return extra_opt


def start_ffplay(song, tmp_name, extra_opt, toplevel=None):
    """ Start playing song. Wait short time to return pid and sink.

    :param song: unquoted song name, we'll add the quotes
    :param tmp_name: = /tmp/filename to send output of song name. E.G.:
                TMP_CURR_SONG = g.TEMP_DIR + "mserve.currently_playing"
                TMP_CURR_SAMPLE = g.TEMP_DIR + "mserve.current_sample"
    :param extra_opt: can be blank or, overrides to start, fade, etc.
                -ss = start seconds offset within song, normal is 0
                -t = how long to play song (duration in seconds)
                -af "a fade=type=in:start_time=99:duration=3"
    :param toplevel: When passed gets .after(sleep) time.
    :return pid, sink: Linux Process ID and Pulse Audio Sink Number
    """

    ''' ffplay start options to redirect output to temporary file '''
    # noinspection SpellCheckingInspection
    cmd = 'ffplay -autoexit ' + '"' + song + '" ' + \
          extra_opt + ' -nodisp 2>' + tmp_name

    ''' launch ffplay external command in background it polls for pid '''
    found_pid = ext.launch_command(cmd, toplevel=toplevel)
    found_sink = ""  # May 21, 2023 functions expect "" for no sink
    if found_pid == 0:
        print('Waited 10 seconds, aborting start_ffplay() get PID')
        print(song)
        return found_pid, found_sink

    found_sink = pav.find(found_pid)
    if not found_sink:
        print('Sink not found for pid:', found_pid)
        print(song)
        found_sink = ""  # pretty much same thing as 'None' anyway...

    return found_pid, found_sink


def get_curr_ffplay_secs(tmp_name):
    """
        July 5, 2023 - Should no longer call directly.
        FileControl.get_elapsed() calls get_curr_ffplay_secs(tmp_name).

        Get elapsed play time from ffplay output file in RAM
        If resuming play, first time is unreliable so return second time.
        If we've just paused then first time is reliable.
    """
    last_time = 0
    second_last = 0
    time_count = 0
    ''' File format (approximately the last 256 bytes positioned to with seek).
        79.21 M-A:  0.000 fd=   0 aq=   23KB vq=    0KB sq=    0B f=0/0   \r  # 69 bytes  
        79.24 M-A:  0.000 fd=   0 aq=   23KB vq=    0KB sq=    0B f=0/0   \r  
        79.27 M-A: -0.000 fd=   0 aq=   23KB vq=    0KB sq=    0B f=0/0   \r  
        79.30 M-A: -0.000 fd=   0 aq=   22KB vq=    0KB sq=    0B f=0/0   \r'  # 69 bytes    
    '''
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
        f.close()  # May 16 2023, add close but it should be automatic anyway

    return float(second_last)


def deprecated_list_diff(new_lst, old_lst, name):
    """ Return string variable added to new list not in old list
        Must be exactly one new item
    """
    count_diff = len(new_lst) - len(old_lst)
    diff_lst = list(set(new_lst) - set(old_lst))
    if not count_diff == 1 or not len(diff_lst) == 1:
        toolkit.print_trace()
        print("new_list_var() for " + name + " difference is not 1.")
        print("new_lst:", new_lst)
        print("old_lst:", old_lst)
        return diff_lst
    return str(diff_lst[0])


def deprecated_pid_list(program):
    """ Return list of PIDs for program name """
    PID = os.popen("pgrep " + program).read().strip().splitlines()
    return PID


def deprecated_sink_list(program):
    """ Return list of Firefox or ffplay input sinks indices
        Used for both old_lst and new_lst lists. old_lst may be empty.
    """
    indices = []
    all_sinks = sink_master()
    for entry in all_sinks:
        sink, vol, name = entry
        sink = str(sink)  # May 26 2023 - Sink must be string not int
        if program == name:
            indices.append(sink)
    return indices


def set_tv_sound_levels(start_percent, end_percent, _thread=None):
    """
        Set Firefox tv sound levels to given percentage
        Ending percent is 25 when going down and 100 when going up
    """
    pav.get_all_sinks()
    for Sink in pav.sinks_now:
        if Sink.name == TV_SOUND:
            pav.fade(Sink.sink_no_str, start_percent, end_percent, 1)


def storage_artwork(width, height):
    """
        Use image file stored in mserve directory as substitute
        artwork for song. Do this when song file has no artwork. EG WAV
    """

    if not os.path.isfile(ARTWORK_SUBSTITUTE):
        # Song has no artwork that ffmpeg can identify.
        print("mserve.py storage_artwork() os.path.isfile(ARTWORK_SUBSTITUTE) " +
              "failed test")
        return None, None

    original_art = Image.open(ARTWORK_SUBSTITUTE)
    resized_art = original_art.resize(
        (width, height), Image.ANTIALIAS)
    return ImageTk.PhotoImage(resized_art), resized_art, original_art


DPRINT_ON = False


def dprint(*args):
    """ Debug printing """
    global DPRINT_ON
    if DPRINT_ON:
        print(*args)


def cat3(line, prefix, text):
    """ Concatenating texts with latin characters has error:

            UnicodeEncodeError: 'ascii' codec can't encode character
            u'\xc6' in position 0: ordinal not in range(128)
    """
    # noinspection PyBroadException
    try:
        return line + prefix + text.encode("utf8")
    except:
        # noinspection PyProtectedMember
        print('cat3() called from:', sys._getframe(1).f_code.co_name,
              '() Latin character error in:', prefix, text)
        # noinspection SpellCheckingInspection
        ''' cat3() ... Latin character error in:  🎵  Ænema '''
        return line + prefix + "????????"


def get_dir(top, title, start):
    """ Get directory name same function in location.py """
    root.directory = filedialog.askdirectory(initialdir=start,
                                             parent=top,
                                             title=title)
    return root.directory


def custom_paste(event):
    """ Allow paste to wipe out current selection. Doesn't work yet!
        From: https://stackoverflow.com/a/46636970/6929343
        July 23, 2023 - Fix and move to toolkit.py
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
OLD_CWD = None  # Directory when 'm' or mserve.py was called
SORTED_LIST = []
root = None  # Tkinter toplevel object. Can be passed by `m`


def create_files():
    """ g.USER_DATA_DIR/mserve doesn't exist. Create directory and files. """
    # Create directory
    try:
        os.mkdir(g.USER_DATA_DIR)
        print("Created directory:", g.USER_DATA_DIR)
    except OSError:  # [Err no 17] File exists: '.../.local/share/mserve'
        print("Could not create directory:", g.USER_DATA_DIR)
        return False
    # Open and Close will create SQL database
    sql.open_db(LCS=lcs)  # sql needs use open_xxx vars in Locations() class
    sql.set_db_version()  # user_version = 3 as of Aug 19/23.
    sql.close_db()
    # create lc.FNAME_LOCATIONS
    lc.read()  # If no file, creates empty lc.LIST for favorites & last records
    lc.write()  # LIST is empty and written as pickle
    # create lc.FNAME_LAST_LOCATION is not needed now. It is saved at close


def open_files(old_cwd, prg_path, parameters, toplevel=None):
    """ If no passed music directory, or if passed directory doesn't exist,
        use default location directory. If no default location directory,
        use the startup directory when 'm' or 'mserve.py' was called. If that
        directory doesn't contain music, or subdirectories with music then
        prompt for a music directory. If prompt cancelled then exit.

        TODO: First time opening phone location asks for directory already there
              Two scans of a few minutes
              Then M stays open with no status for a few minutes.
              Then a few minutes to build Music Location Tree.

              Add three songs, apply playlist OK. When save favorites error:
                  "location.py Locations.save_mserve_location()
                   -Error reading location: new"

              Same error above when save play & exiting mserve.

              Second time opening phone location one scan of a few minutes.
              Then M stays open with no status for a few minutes.
              Then a few minutes to build Music Location Tree.
              Now able to save favorites ok

        """
    global root  # named when main() called by 'm' splash screen
    global SORTED_LIST  # os.walk() results: artist/album/songs
    global START_DIR  # Music directory. E.G. "/home/USER/Music
    global NEW_LOCATION  # True=Unknown music directory in parameter #1
    global LODICT  # Permanent copy of location dictionary never touched

    who = "mserve.py open_files() - "
    if prg_path is None:
        # it will never be None. Just don't want to code this stuff yet.
        print("prg_path is not used. Review:", prg_path)
        print("old_cwd:", old_cwd)
        print("parameters:", parameters)

    print()
    print(r'  ######################################################')
    print(r' //////////////                            \\\\\\\\\\\\\\')
    print(r'<<<<<<<<<<<<<<    mserve - Music Server     >>>>>>>>>>>>>>')
    print(r' \\\\\\\\\\\\\\                            //////////////')
    print(r'  ######################################################')
    print(r'                    Started:',
          datetime.datetime.now().strftime('%I:%M %p').strip('0'))

    ''' Has data directory been created? '''
    if os.path.exists(g.USER_DATA_DIR):
        ''' Sanity Checks '''
        if not os.path.isdir(g.USER_DATA_DIR):
            toolkit.print_trace()
            print("g.USER_DATA_DIR is a file but must be a directory:", 
                  g.USER_DATA_DIR)
            exit()
    else:
        create_files()

    ''' Was music_dir passed as parameter? '''
    parm1 = None
    try:
        parm1 = music_dir = parameters[1]
        hold_dir = os.getcwd()
        os.chdir(old_cwd)  # Temporarily change to original directory
        # Massage parameter 1 of ".", "..", "../Sibling", etc.
        music_dir = os.path.realpath(music_dir)
        os.chdir(hold_dir)  # Change back to mserve.py directory
        use_location = False
    except IndexError:  # list index out of range
        # Music directory not passed as parameter
        music_dir = None
        use_location = True

    ''' Is passed music_dir in our known locations? 
        Sep 5/23 - Cannot lookup by topdir name because two locations
                   can exist, e.g. L001 for ssh phone, L005 for ftp phone
                   Related: Need prompt for user to save new location before
                   exiting. Currently files are stored in .../mserve instead
                   of .../mserve/L999
    '''

    #print(who + "Contents of music_dir:", music_dir)
    #if music_dir is not None and lc.get_dict_by_dirname(music_dir):
    if parm1 and "L001" <= parm1 < "M":
        if lcs.read_location(parm1):
            use_location = True  # Override to use location found by dir name
            #print(who + 'Using location:', lc.DICT['iid'])
            # Make passed Top Directory our last known location then load it
            #lc.save_mserve_location(lc.DICT['iid'])  # Version 1 function
            ''' below read lcs.act_code, lcs.act_name & lcs.act_topdir, etc. '''
            lcs.save_mserve_location(lcs.act_code)
            music_dir = lcs.act_topdir  # Init by above command
            #print(who + 'Using Top Directory:', music_dir)
        else:
            print(who + 'New location not found in SQL Location Table:', parm1)
            print(who + "Continuing will cause endless loop. Exiting...")
            exit()
    elif music_dir is not None and lcs.get_dict_by_dirname(music_dir):
        ''' Passed directory name exists in known locations 
            Full pathname was passed as parameter 1 '''
        use_location = True  # Override to use location found by dir name
        print(who + 'Overriding music_dir:', music_dir,
              'to location:', lcs.act_code)
        # Make passed Top Directory our last known location then load it
        #lc.save_mserve_location(lc.DICT['iid'])
        lcs.save_mserve_location(lcs.act_code)
        music_dir = lcs.act_topdir  # Init by above command
        print(who + 'Using Top Directory:', music_dir)

    ''' create START_DIR, test location awake, check files exist '''
    if use_location:
        ''' When NEW_LOCATION is True no Locations() to read or save '''
        lcs.register_NEW(NEW_LOCATION)  # Register flag that indicates new
        # besides above flag, can check lcs.act_code.lower() == 'new'
        lcs.register_parent(root)  # ShowInfo will go to root window parent
        ''' Below mounts host testing window appropriately as required'''
        ret = lcs.load_last_location(root)  # Open last location and validate
        if ret == 0:
            START_DIR = lcs.open_topdir
            if not START_DIR.endswith(os.sep):
                START_DIR += os.sep
            return  # self.lib_top_playlist_name

        title = who + "Error retrieving Location to play"  # Error defaults
        text2 = "Proceeding to use music_dir: " + str(music_dir)
        if ret == 1:
            ''' last location code in SQL History Table not found '''
            text = "last location code in SQL History Table not found\n\n"
            text += text2
            print('\n' + who + 'ERROR:\n')
            print(text)  # Print to console and show message on screen at 100, 100
            message.ShowInfo(root, title=title, text=text, icon='error',
                             thread=dummy_thread)
        if ret == 2:
            ''' last location code in SQL History exists but not in Location Table '''
            text = "The last used location not found in SQL Location Table\n\n"
            text += text2
            print('\n' + who + 'ERROR:\n')
            print(text)  # Print to console and show message on screen at 100, 100
            message.ShowInfo(root, title=title, text=text, icon='error',
                             thread=dummy_thread)
        if ret == 3:
            ''' Top Directory doesn't exist or host is off-line '''
            text = "Top Directory doesn't exist or host is off-line.  Check:\n\t"
            text += lcs.open_topdir + "\n\n"
            text += text2
            print('\n' + who + 'ERROR:\n')
            print(text)  # Print to console and show message on screen at 100, 100
            message.ShowInfo(root, title=title, text=text, icon='error',
                             thread=dummy_thread)

    lcs.open_code = 'new'
    lcs.open_name = music_dir
    NEW_LOCATION = True  # Don't use location dictionary (LODICT) fields

    print(who + "Searching for songs in music_dir:", music_dir)

    while True:
        if music_dir is None:
            music_dir = g.HOME
        # Prompt to get startup directory using /home/USER as default
        START_DIR = get_dir(root, "Select Music Directory", music_dir)
        print(who + "START_DIR:", START_DIR, type(START_DIR))
        if isinstance(START_DIR, tuple):
            print(who + "Cancel selected from" +
                  " Select Music Directory dialog. Exiting.")
            exit()

        if START_DIR is None:
            START_DIR = old_cwd
            print(who + "START_DIR forced to old_cwd," +
                  " should not happen:", old_cwd)
        if not START_DIR.endswith(os.sep):
            START_DIR += os.sep

        # Check how many songs
        music_list, depth_count = make_sorted_list(START_DIR, toplevel=toplevel)
        if depth_count[0] == 0 and depth_count[1] == 0 and depth_count[2] == 0:
            # TODO: Splash screen "M" is still open but cannot be moved because
            #           it has no window decorations.
            #       Clicking Cancel in filepicker is an endless loop
            #       Entering '~/Music' into Filepicker and clicking 'OK' should work but doesn't
            #       Control+C doesn't terminate in terminal. Have to close tab
            title = "No music files found."
            text = "Music Location appears empty !!!\n\n" + \
                   "    " + START_DIR + "\n\n" + \
                   "No songs were found in target directory nor the\n" + \
                   "next three subdirectory levels under the target.\n\n" + \
                   "Verify the directory name and try again."
            message.ShowInfo(root, title=title, text=text, icon='error',
                             thread=dummy_thread)
            #messagebox.showinfo(title=title, message=text)
            #message.ShowInfo(root, title="No music files found.", text=text,
            #                 align='left', icon='error')  # Doesn't work without parent
            # NOTE: OK doesn't work so use messagebox.showinfo() instead
            #       Window appears on top-left monitor @ 30,30 so use messagebox instead
            continue

        print(who + "len(music_list):",
              len(music_list), "in START_DIR:", START_DIR)
        print(depth_count)
        #print(music_list)
        break

    ''' Replace existing, or append first parameter with massaged (realpath) 
        music directory. This is needed for mserve restart. '''
    if len(sys.argv) > 1:
        sys.argv[1] = music_dir
    else:
        sys.argv.append(music_dir)


pav = lcs = None  # Global classes: pav=PulseAudio() lcs=location.Locations()


def dummy_thread():
    """ Needed for ShowInfo from root window. """
    root.update()
    root.after(30)


def main(toplevel=None, cwd=None, parameters=None):
    """ Establish music location from sys.argv or last used location
    :param toplevel: Splash screen mounted by m for startup
    :param cwd: Current Working Directory when program started
    :param parameters: sys.argv used to call program """
    global root  # named when main() called
    global SORTED_LIST  # os.walk() results: artist/album/songs
    global START_DIR  # Music directory. E.G. "/home/USER/Music
    global NEW_LOCATION  # True=Unknown music directory in parameter #1
    global LODICT  # June 1, 2023 - Wasn't declared global before today
    global pav, lcs  # July 8, 2023 - global until start_ffplay relocated

    ''' cwd is saved and passed by "m" before calling mserve.py '''
    prg_path = os.path.dirname(os.path.realpath(__file__))
    # prg_path is already available in g.PROGRAM_DIR so deprecate it.
    ''' 'm' splash screen passes the old current working directory (cwd) '''
    if cwd is None:
        ''' Save current working directory - same code in m and mserve.py '''
        cwd = os.getcwd()
        if cwd != prg_path:
            #print("Changing to dir_path:", dir_path)
            os.chdir(prg_path)
    ''' parameters are passed by "m" to mserve.py '''
    if parameters is None:
        parameters = sys.argv

    ''' Create Tkinter "very top" Top Level window '''
    if toplevel is None:
        root = tk.Tk()  # Create "very top" toplevel for all top levels
    else:
        root = tk.Toplevel()  # `m` splash screen already used tk.Tk()
    root.wm_attributes('-type', 'splash')  # No window decorations
    monitor.center(root)
    root.withdraw()  # Remove default window because we have own windows

    ''' Is another copy of mserve running? '''
    #result = os.popen("ps aux | grep -v grep | grep python").read().splitlines()
    apps_running = ext.get_running_apps(PYTHON_VER)
    this_pid = os.getpid()  # Don't commit suicide!
    m_pid = mserve_pid = vu_meter_pid = 0  # Running PIDs found later
    ffplay_pid = ext.pid_list("ffplay")  # If more than one, kill the first seen
    ffplay_pid = 0 if len(ffplay_pid) == 0 else ffplay_pid[0]

    ''' Loop through all running apps with 'python' in name '''
    for pid, app in apps_running:
        if app == "m" and pid != this_pid:
            m_pid = pid  # 'm' splash screen found
        if app == "mserve.py" and pid != this_pid:
            mserve_pid = pid  # 'mserve.py' found
        if app == "vu_meter.py":  # VU meter isn't launched by this_pid yet
            vu_meter_pid = pid  # 'vu_meter.py' found

    ''' One or more fingerprints indicating another copy running? '''
    if m_pid or mserve_pid or vu_meter_pid:
        title = "Another copy of mserve is running!"
        text = "Cannot start two copies of mserve. Switch to the other version."
        text += "\n\nIf the other version crashed, the process(es) still running"
        text += " can be killed:\n\n"
        if m_pid:
            text += "\t'm' (" + str(m_pid) + ") - mserve splash screen\n"
        if mserve_pid:
            text += "\t'mserve.py' (" + str(mserve_pid) + \
                    ") - mserve without splash screen\n"
        if vu_meter_pid:
            text += "\t'vu_meter.py' (" + str(vu_meter_pid) + \
                    ") - VU Meter speaker to microphone\n"
        if ffplay_pid:
            text += "\t'ffplay' (" + str(ffplay_pid) + \
                    ") - Background music player\n"
        text += "\nDo you want to kill previous crashed version?"

        print(title + "\n\n" + text)
        answer = message.AskQuestion(
            root, title=title, text=text, align='left', confirm='no',
            icon='error', thread=dummy_thread)

        if answer.result != 'yes':
            exit()

        if m_pid:
            #print("killing m_pid:", m_pid)
            if not ext.kill_pid_running(m_pid):
                print("killing m_pid FAILED!:", m_pid)
        if mserve_pid:
            #print("killing mserve_pid:", mserve_pid)
            if not ext.kill_pid_running(mserve_pid):
                print("killing mserve_pid FAILED!:", mserve_pid)
        if vu_meter_pid:
            #print("killing vu_meter_pid:", vu_meter_pid)
            if not ext.kill_pid_running(vu_meter_pid):
                print("killing vu_meter_pid FAILED!:", vu_meter_pid)
        if ffplay_pid:
            #print("killing ffplay_pid:", ffplay_pid)
            if not ext.kill_pid_running(ffplay_pid):
                #print("killing ffplay_pid FAILED!:", ffplay_pid)
                # ffplay may have finished before ShowInfo close
                pass

    ''' Create initial instance of Locations class.'''
    lcs = lc.Locations(make_sorted_list)  # Pass reference

    ''' sql.open_db() is called again in sql.populate_tables()  '''
    sql.open_db(LCS=lcs)  # SQL needed to build location lists
    lcs.build_locations()  # Build SQL location lists for TopDir lookup

    # Get the default background at runtime, you can use the cget
    # https://stackoverflow.com/a/35409593/6929343  (Bryan Oakley)
    #system_bg = root.cget("background")
    """ From: https://stackoverflow.com/a/46636970/6929343
        Should deleted highlighted text when paste is used.
        Only applies to X11 because other systems do it automatically. 
    """
    root.bind_class("Entry", "<<Paste>>", custom_paste)  # X11 only test
    ''' Set font style for all fonts including tkSimpleDialog.py '''
    img.set_font_style()  # Make messagebox text larger for HDPI monitors
    ''' Set program icon in taskbar '''
    img.taskbar_icon(root, 64, 'white', 'lightskyblue', 'black')


    '''   B I G   T I C K E T   E V E N T    

          Open Files - If it fails it will exit()  '''
    open_files(cwd, prg_path, parameters)  # Create application directory


    ''' Sorted list of songs in the location - Need Delayed Text Box '''
    ext.t_init('make_sorted_list()')
    SORTED_LIST, depth_count = make_sorted_list(START_DIR, toplevel=toplevel)
    ext.t_end('no_print')  # May 24, 2023 - make_sorted_list(): 0.1631240845
    # July 24, 2023 - make_sorted_list(): 0.2467391491 (50% slower vs 2 mo ago)
    # Aug 2/23 - Over ssh new: 15.0521910191 restart cached: 1.5163669586

    ''' Is sorted list of location's music empty? '''
    if len(SORTED_LIST) == 0:
        title = "Music Location is empty!" 
        text = "Cannot find any music files in the directory below:"
        text += "\n\n  " + START_DIR
        print(title + "\n\n" + text)
        #message.ShowInfo(root, title=title, text=text, align='left',
        #                 icon='error', thread=dummy_thread)
        #   File "./m", line 75, in main
        #     mserve.main(toplevel=splash, cwd=cwd, parameters=sys.argv)
        #   File "/home/rick/python/mserve.py", line 16432, in main
        #     icon='error', thread=dummy_thread)
        #   File "/home/rick/python/message.py", line 343, in __init__
        #     simpledialog.Dialog.__init__(self, parent, title=title)
        #   File "/usr/lib/python2.7/lib-tk/tkSimpleDialog.py", line 85, in __init__
        #     self.grab_set()
        #   File "/usr/lib/python2.7/lib-tk/Tkinter.py", line 679, in grab_set
        #     self.tk.call('grab', 'set', self._w)
        # _tkinter.TclError: grab failed: another application has grab
        # NOTE: Tempting to exit now but need to proceed to select different location.

    ''' Process sorted list to create SQL Music Table '''
    # PROBLEM: Music Table Rows as soon as directory is opened, however
    #          a new location may not be saved and may never be accessed again.
    #          populate_tables should only be called when 'new' location is saved.
    #          Need function to prompt for location name, assign new code and
    #          then call sql.populate_tables()
    ext.t_init('sql.populate_tables()')
    #sql.populate_tables(SORTED_LIST, START_DIR, PRUNED_DIR, LODICT)
    sql.populate_tables(SORTED_LIST, START_DIR, PRUNED_DIR, None)
    ext.t_end('no_print')  # sql.create_tables(): 0.1092669964
    ''' Pulse Audio Instance for sinks and volume. '''
    pav = vu_pulse_audio.PulseAudio()
    ''' Open Music Location Tree and Favorites Playlist '''
    MusicLocationTree(toplevel, SORTED_LIST)  # Build treeview of songs
    ''' root mainloop '''
    # https://stackoverflow.com/questions/12800007/why-photoimages-dont-exist
    if toplevel is None:
        # `m` already has mainloop(). If `m` didn't pass toplevel, call mainloop().
        root.mainloop()


if __name__ == "__main__":
    main()

# End of mserve.py
