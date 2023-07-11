#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
#       Sept 20 2020 - Start taking out or replacing 63 root.update()
#       Sept 23 2020 - Make compare button disappear (entire grid 4 remove)
#       Oct. 24 2020 - CheckboxTreeview() replace "songsel" tag with "checked"
#       Nov. 02 2020 - Remove old selection processing for new CheckboxTreeview 
#       Dec. 12 2020 - Chrome os doesn't support .grid_remove(). Comment out 15
#            self.loc_F4.grid_remove()
#       Dec. 28 2020 - Selected MB is now Song Number Sequence
#       Jan. 15 2021 - Add vu_meter.py as separate program
#       Feb. 07 2021 - Add webscrape.py as separate program
#       Mar. 05 2021 - Add fine-tune time index function (Lyrics Synchronization)
#       Mar. 13 2021 - Read ffplay output for current seconds instead of calc.
#       May. 02 2021 - mserve.py is now called by 'm' wrapper splash screen
#       May. 18 2021 - createToolTip() - Hover balloon (Deprecated 8/8/21)
#       Jun. 14 2021 - Rounded Rectangle Canvas widget
#       Aug. 08 2021 - New webscrape.py parameters/results via SQL History
#       Aug. 21 2021 - Revamp tooltips with toolkit.ToolTips
#       Jan. 18 2022 - Set tooltip location SW, SE, NW or NE of parent widget
#       Jan. 03 2023 - Shuffle broken when song with no lyrics is playing
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
#       June 01 2023 - Music Library checkboxes batch update to Playlist.
#       June 03 2023 - Handle <No Album> in lib_tree paths used in SQL tables
#       June 05 2023 - No location when passing music directory parameter.
#       June 07 2023 - Many changes. E.G. step_volume() takes list of sinks.
#       June 09 2023 - tvVolume() class for Hockey. Stanley=Vegas 2, Florida 1.
#       June 11 2023 - Add TV_BREAK and SOUND. Stanley Cup=Vegas 3, Panthers 1.
#       June 13 2023 - Develop Playlists() class. Vegas won Stanley Cup! (4-1)
#       June 18 2023 - Expanding/Collapsing Information Centre. InfoCentre()
#       June 21 2023 - 'M' splash screen disappears as late as possible.
#       June 23 2023 - Antonia's request to highlight hovered chron_tree row.
#       June 25 2023 - Check corrupt music files and device off-line.
#       June 26 2023 - New classes Refresh() and FileControl()
#       June 29 2023 - Restore last access when < 80% of song was played.
#       July 02 2023 - Temporary filenames Windows/Mac. Enhance artwork.
#       July 04 2023 - Create FineTune() class. Major bugs worked out.
#       July 05 2023 - Create Help buttons that open pippim website pages.
#       July 07 2023 - Begin vu_pulse_audio.py for pulsectl.Pulse interface.
#       July 09 2023 - New PA fading - faster, easier, smaller & more robust.

# noinspection SpellCheckingInspection
"""
# TODO:
# -----------------------------------------------------------------------------

#   Playlists

#     BUGS:
#       Open playlist, if music was paused, volume is only 25%
#       Close playlist and use favorites doesn't clear_all_checks
#       Shuffling Favorites then opening playlist will undo shuffle. Backup!!

#     TODO:
#       Save Playlist As... - If playlist created with 'new' option then a
#           rename option. Otherwise create a new playlist with new name.
#

#   Miscellaneous

#     TODO:
#       Setup watchmen. For example every 10 seconds check all sinks and warn
#           when the same sink number has volume between 50% and 99% two cycles
#           in a row.

#       Create help buttons for dropdown menu options.

#       When opening Artist, if only one Album, then open it too.

#   Language Conventions - Title should never be labled "song".
#       Song = Title (can have variations E.G. "Live in Paris" at end)
#              + Artist - Cover artists may sing the same Title
#              + Album - Artist can have same title on different albums

#   Music library name of lib_tree is too generic. There is already
#   SQL Music Table which is more like the real library of mserve.
#
#   Candidates:
#
#   1. Location song files (lsf_tree)  # Is misleading for Pruned Tree's
#   2. OS song file library (osf_tree)  # To close to: sql.ofb.Select()?
#   3. Filenames by Album by Artist (faa_tree)  # Sounds like a plane crash
#   4. Artist/Album/Title tree (aat_tree)  # probably subject to typo's
#   5. Collapsed OS walk (cow_tree)  # Sounds cool plus CoW used in industry
#   6. Grouped Song Files (gsf_tree)  # Same problem as osf and sounds like groupies
#   7. All Music Files (all_tree)  # Difficult if using "sel". E.G. "sel_all_ndx"

#   RENAME VARIABLES:
#       'self.saved_selections' -> 'self.play_order_iid'
#       'self.saved_selections' -> 'self.play_iid_seqs'
#       'self.saved_selections' -> 'self.playlist_iids'  # Depends on next section
#       'self.saved_selections' -> 'self.play_lib_iid'
#       'self.saved_selections' -> 'self.sel_lib_iids'
#       'self.saved_selections' -> 'self.sel_lib_tree_iids'
#       'self.saved_selections' -> 'self.play_iids'
#       'self.saved_selections' -> 'self.select_iids'
#       'self.saved_selections' -> 'self.sel_iids'
#       'self.saved_selections' -> 'self.fav_iid_list'
#       'self.saved_selections' -> 'self.play_iid_list'

#       'self.saved_playlist'   -> 'self.playlist_paths'  # Already DONE
#       'self.playlist_paths'   -> 'self.sel_lib_paths'
#       'self.playlist_paths'   -> 'self.sel_lib_tree_paths'
#       'self.playlist_paths'   -> 'self.select_paths'
#       'self.playlist_paths'   -> 'self.play_paths'
#       'self.playlist_paths'   -> 'self.fav_paths'  # Misleading when Playlists()
#       'self.playlist_paths'   -> 'self.select_paths'
#       'self.playlist_paths'   -> 'self.fav_path_list'  # Misleading when Playlists()
#       'self.playlist_paths'   -> 'self.play_path_list'

#       'self.song_list'        -> 'self.lib_tree_paths'
#       'self.song_list'        -> 'self.lib_song_paths'
#       'self.song_list'        -> 'self.fake_paths'  # Already DONE
# BIG PROBLEM. self.fake_paths may contain /<No Artist>/<No Album>
#              As self.fake_paths is read create self.real_paths
#              FIXED - July 3, 2023 keep self.fake_paths to rebuild lib_tree

#       'self.ndx'              -> 'self.curr_iid_ndx'
#       'self.ndx'              -> 'self.play_curr_ndx'
#       'self.ndx'              -> 'self.play_ndx'  # June 29, 2023 11 AM - Flavor De Jure
#       'self.ndx'              -> 'self.seq_ndx'
#       'self.ndx'              -> 'self.select_ndx'
#       'self.ndx'              -> 'self.sel_ndx'
#       'self.ndx'              -> 'self.sel_curr_ndx'
#       'self.ndx'              -> 'self.iid_ndx'
#       'self.ndx'              -> 'self.fav_ndx'  # Misleading when Playlists()

#       New brothers for '_ndx' -> 'self.---_iid"   # self.saved_selections[self.ndx]
#       New brothers for '_ndx' -> 'self.---_path"  # self.playlist_paths[self.ndx]
#       New brothers for '_ndx' -> 'self.---_pid"   # No longer necessary with
#       New brothers for '_ndx' -> 'self.---_sink"  # play_ctl.pid & play_ctl.sink

#   RENAME FUNCTIONS:
#       'self.song_set_ndx()'   -> 'self.set_sel_ndx()'
#       'self.song_set_ndx()'   -> 'self.set_select_ndx()'
#       'self.song_set_ndx()'   -> 'self.change_select_ndx()'
#       'self.song_set_ndx()'   -> 'self.play_new_song()'
#       'self.song_set_ndx()'   -> 'self.play_set_ndx()'
#       'self.song_set_ndx()'   -> 'self.set_play_ndx()'    # July 1, 2023 5:28pm
#       Advantage of changing "self.song_" to "self.play_" is below too:
#           self.song_artist_var.set(make_ellipsis(self.play_ctl.Artist, E_WIDTH))
#           self.song_album_var.set(make_ellipsis(self.play_ctl.Album, E_WIDTH))
#           self.song_title_var.set(make_ellipsis(self.play_ctl.Title, E_WIDTH))

#       'self.play_insert()'    -> 'self.add_selected()'
#       'self.play_insert()'    -> 'self.insert_selection()'

#    Need to fix file modification time which will make it greater than
#       creation time (not birth time which is unused) which is the time it
#       was copied to the directory and permissions were established. Use
#       ID3 tag: CREATION_TIME : 2012-08-20 17:06:42

#   Location processing is 1500 lines and really is never used after setup. Move
#       to separate file? Add generic processing for synchronizing programming
#       files across different devices?

#   Verify parameter #1 is directory. E.G. "START_DIR = sys.argv[1]"
#       If START_DIR is not a directory, use last location with warning message.
#       If no last location give error and select a good START_DIR.

#   Move ~/.config/mserve/library.db to ~/.local/share/mserve/library.db
#       New open_files() function that verifies "START_DIR" described above.
#       Also move all files and L999 directories. Update daily backup script.
#       Create message that directory ~/.local/share/mserve/ has been created
#       and the files 'locations' and 'library.db' have been created there.
#       Advise to add these files to daily backup along with subdirectories
#       ~/.local/share/mserve/L999.  Where 999 is subdirectory created for
#       music location configured on this device and other devices.
#       The ~/.config/mserve/ directory will be used in future to specify
#       windows vs linux vs chrome os vs MAC. Also to define color scheme 

#   def step_volume(sink, p_start, p_stop, steps, interval, thread=None):
#       TODO: The 1/2 second to ramp up one volume and ramp down another is
#             adding up with pauses to graphics and music. Spin off subprocess
#             that doesn't lag animations or introduce noticeable sound delays.
#             June 7, 2023 - UPDATE: will create ff.py module to do everything. 
#             June 27, 2023 - UPDATE: The new FileControl() class should do it.

#   History Type 'encode' uses MusicId 0 which is also used for configuration.
#       This will slow down configuration operations over time. Create new index
#       by History Type + Action. Then for example, get Type-"resume" +
#       Action-"L004", instead of search through all MusicId=0 records.

# BUGS:
# -----------------------------------------------------------------------------

#   When 'dell' File Server goes to sleep, there are 4 errors not trapped:
#       sql.update_metadata(): File below doesn't exist:
#           OsFileName-The Tea Party/Tangents/03 The Messenger.m4a
#       Waited > 2.5+ seconds, aborting start_ffplay() get sink
#       File ".../mserve.py", line 7269, in update_lib_tree_song
#           OSError: [Err no 2] No such file or directory:
#               '/mnt/music/The Tea Party/Tangents/03 The Messenger.m4a
#       The last song stops music but progress seconds go past duration
#       ALSO NOTE file serve was awake for 3 days after and very, VERY, HOT !!!
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
    sudo apt install python-pil              # Pillow graphics routines
    sudo apt install python-pil.imagetk      # Pillow image processing
    sudo apt install python-pyaudio          # For VU meters
    sudo apt install python-requests         # Get Cover Art
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

    FOR FUTURE Python 2.7 ttkthemes (Python 3 can use current version of ttkthemes):
    pip install -U setuptools
    python2 -m pip install ttkthemes==2.4.0

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

NOTES:
    File server needs to mount music directory if on idle partition:
        sudo mount -t auto -v /dev/sdb1 /mnt/music

TODO'S:
    verify external commands are in path:
        command -v cp, diff, ffplay, ffprobe, ffmpeg, gsettings, kid3, kill,
           pactl, pgrep, pqiv, ps, stat, touch, wmctrl, xclip, xdotool, xprop

    Compare Location - Make background process so music player keeps spinning
"""
    

# Similar imports in message.py, vu_pulse_audio.py, encoding.py, etc.
try:
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

#print("Python version: ", PYTHON_VER)
#print('TK Version:', tk.TkVersion)   # https://tkdocs.com/ Nov 2019 ver 8.6
#

import signal  # Shutdown signals
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
#print("Python version:", sys.version)

import os
import shutil
import json  # For List conversions to SQL
import time
import datetime
import sqlite3  # Only needed to trap "except sqlite3...:" errors
import re
import traceback  # To display call stack (functions that got us here)
import webbrowser

from collections import OrderedDict

from PIL import Image, ImageTk, ImageDraw, ImageFont
from ttkwidgets import CheckboxTreeview
import pickle
from random import shuffle

import notify2              # send inotify over python-dbus

import locale               # To set thousands separator as , or .
locale.setlocale(locale.LC_ALL, '')  # Use '' for auto locale selecting
import numpy as np          # For image processing speed boost

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
#   File "./m", line 25, in <module>
#     import image as img     # Pippim functions for image management
#   File "/home/rick/python/image.py", line 45, in <module>
#     import x11                  # x11 wrapper functions for GoneFishing() class
#   File "/home/rick/python/x11.py", line 55, in <module>
#     import Xlib.X
# ImportError: No module named 'Xlib'
import sql                  # SQLite3 functions DIFFERENT than bserve sql.py module
import monitor              # Display, Screen, Monitor and Window functions
import toolkit              # Functions for tkinter-tool kit interface
import timefmt as tmf       # Format date and time
import webscrape            # Get song lyrics via web scrape

# Subdirectory /pulsectl under directory where mserve.py located
from pulsectl import pulsectl  # July 7, 2023 to be Deprecated in mserve

import vu_pulse_audio as vup  # Volume Pulse Audio to replace pulsectl
# FUTURE thoughts: import vu_windows as vuw
#                  import vu_mac as vum


# Poor man's locale circa 2020 stuff that needs to be upgraded
"""
https://stackoverflow.com/a/956084/6929343
    locale.setlocale(locale.LC_ALL, 'de_DE') # use German locale; 
name might vary with platform
On Windows, I think it would be something like:
    locale.setlocale(locale.LC_ALL, 'deu_deu')
MSDN has a list of language strings and of country/region strings
"""
CFG_DECIMAL_PLACES = 1      # 1 decimal place, eg "38.5 MB"
CFG_DIVISOR_AMT = 1000000   # Divide by million
CFG_DIVISOR_UOM = "MB"      # Unit of Measure becomes Megabyte

# Global variables
RESTART_SLEEP = .3          # Delay for mserve close down
KEEP_AWAKE_MS = 250         # Milliseconds between time checks
SCROLL_WIDTH = 16           # Scroll bar width, July 3, 2023 used to be 12
MON_FONTSIZE = 12           # Font size for monitor name
WIN_FONTSIZE = 11           # Font size for Window name
BIG_FONT = 18               # Font size not used
LARGE_FONT = 14             # Font size not used
MED_FONT = 10               # Medium Font size
BTN_WID = 12                # Width for buttons on main window
BTN_WID2 = 12               # Width for buttons on play window
BTN_BRD_WID = 3             # Width for button border
FRM_BRD_WID = 2             # Width for frame border
# TODO: Calculate PANEL_HGT (height)
PANEL_HGT = 24              # Height of Unity panel
MAX_DEPTH = 3               # Sanity check if starting at c:\ or /
# If MAX_DEPTH changes from 3, change 'depth_count = [ 0, 0, 0 ]' below.

'''
TODO:

For multiple mserve.py instances running on rig. Need to revise
encoding.py to accept name of work files.

https://www.educative.io/answers/how-to-generate-a-random-string-in-python

import random
import string

letters = string.ascii_lowercase + string.digits
print ( ''.join(random.choice(letters) for i in range(8)) )

multiple mserve instances to run concurrently. However after a crash the
files will still be there instead of being recycled with next startup.

'''
# Temporary directory work filenames

TMP_CURR_SONG = g.TEMP_DIR + "mserve_song_playing"
TMP_CURR_SAMPLE = g.TEMP_DIR  + "mserve_song_sampling"
TMP_CURR_SYNC = g.TEMP_DIR + "mserve_song_syncing"
TMP_FFPROBE = g.TEMP_DIR + "mserve_ffprobe"
TMP_FFMPEG = g.TEMP_DIR + "mserve_ffmpeg.jpg"
# Must end in .jpg for ffmpeg to work

# Abandon process that takes .4 seconds to run. Use ffprobe instead
# ffmpeg -v error -i "' + song + '" -f null - 2>' + TMP_ERROR
#TMP_ERROR = "/run/user/" + g.USER_ID + "/mserve.error"


''' Volume Meter IPC filenames. Change in vu_meter.py too '''
# Mono output
VU_METER_FNAME = g.TEMP_DIR + "mserve_vu-meter-mono.txt"
# Stereo output (Left and Right)
VU_METER_LEFT_FNAME = g.TEMP_DIR + "mserve_vu-meter-left.txt"
VU_METER_RIGHT_FNAME = g.TEMP_DIR + "mserve_vu-meter-right.txt"

TMP_ALL_NAMES = [TMP_CURR_SONG, TMP_CURR_SAMPLE, TMP_CURR_SYNC,
                 TMP_FFPROBE, TMP_FFMPEG, VU_METER_FNAME,
                 VU_METER_LEFT_FNAME, VU_METER_RIGHT_FNAME]

KID3_INSTALLED = True
KID3_PROGRAM = "xrandr --dpi 144 && kid3 "
KID3_GEOMETRY = "1280x736"
# Command before running kid3: 'xrandr --dpi 144' Best resolution on HD or 4K
FM_INSTALLED = True
FM_PROGRAM = "nautilus"

# Chrome os Linux Beta doesn't support .grid_remove() properly
GRID_REMOVE_SUPPORTED = True

# When unselecting song in library, end song (if playing) and remove in list
# TODO: Unchecking current song in library leaves music player silent.
# Must click song in chron tree to start new song.
LIBRARY_UNSELECT_REMOVE_PLAYING = True

# When checking song in library, how does it go into currently playing list?
LIBRARY_SELECT_INSERT_PLAY_HERE = False
LIBRARY_SELECT_INSERT_PLAY_NEXT = True
LIBRARY_SELECT_INSERT_PLAY_RANDOM = False
LIBRARY_SELECT_INSERT_PLAY_ORDER = False
'''
If an entire album or artist is inserted as anything but RANDOM
then a new function to randomize those songs just inserted should
be created.

When inserting "HERE" and then playing we need a way to start with
first song inserted when the default would be the last song inserted.

'''

# Select music files only, no artwork
# TODO: Deep scan with python-magic to read each file for song type
FILE_TYPES = [".mp3", ".m4a", ".mp4", ".wma", ".oga", ".ogg", ".flac", ".wav", ".PCM"]
NO_ARTIST_STR = "<No Artist>"   # global User defined labels
NO_ALBUM_STR = "<No Album>"
NO_ART_STR = "No Artwork"
#PAUSED_STR = "|| Paused"  # < July 4, 2023 paused ImageDraw() text
# Unicode Character 'DOUBLE VERTICAL BAR' (U+23F8):  ⏸  # Too small
# Right half block + Left half block:  ▐ ▌  # Doesn't ImageDraw() properly
PAUSED_STR = "Pippim.\nmserve\nClick to\n!> Play"
NUMBER_PREFIX = "№ "            # UTF-8 (2116) + normal space
DIGIT_SPACE = " "             # UTF-8 (2007)

''' Music Library's top directory. E.G. /mnt/drive/home/user/Music/'''
START_DIR = ""
PRUNED_DIR = ""  # Same as START_DIR unless manually passing Music Artist

''' WATCHMEN global scope trouble shooting. Created July 5, 2023. '''
WATCHMEN = []

# noinspection SpellCheckingInspection
''' TODO: Start up announcement at 75% volume
    Setting should be for once a day. We don't want this dozens of times when
    we are developing and testing code. Need ~/.../mserve/last_start_time
$ pico2wave -w=/tmp/test.wav "m serve version 1.0"
$ aplay /tmp/test.wav
$ rm /tmp/test.wav
'''
# inspection SpellCheckingInspection

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

# June 20, 2023 - Losing average of 4ms per sleep loop when play_top paused
#   Created new SLEEP_XXX constants but also create 'self.last_sleep_time'
SLEEP_PAUSED = 33           # play_top open but music paused
SLEEP_PLAYING = 33          # play_top is playing music
SLEEP_NO_PLAY = 33          # play_top closed, refresh_lib_top() running


def make_sorted_list(start_dir, toplevel=None, idle=None):
    """ Build list of songs on storage device beginning at 'start_dir'
        Insert '/<No Artist>' and or '/<No Album>' subdirectory names
        Called at startup and by refresh_acc_times()
        Use DelayedTextBox for status updates on long-running processes
        which doesn't appear if process shorter than a second.
        
        TODO: dtb would crash system if tkinter import failed. REVIEW
    """

    ''' If system argument 1 is for random directory, we have no last location.
        It may not point to a music topdir, rather an Artist or Album. A single
        song cannot be passed because os.walk() returns nothing.

        TODO: 
        
        Error message if song is passed as start_dir. July 5, 2023 NOTE: -
        open_files() can trap this if not already.

        In os.walk() we process 100 ms at a time and call lib_top.after() 
        for 100 ms so album artwork keeps spinning.

        Before calling make_sorted_list() must ensure network is up. After
        resume from suspend, network may be down.

    '''

    global PRUNED_COUNT  # No topdir. Started pointing at artist or album.
    global PRUNED_DIR    # The real topdir. E.G. = '../' or '../../'

    if NEW_LOCATION:
        # print('WIP:', start_dir, "may point to topdir, Artist or Album")
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
    #   https://stackoverflow.com/questions/643694/
    #   what-is-the-difference-between-utf-8-and-unicode
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

    # Sort work list with fake ' /' inserted. Then normalize back to '/'
    work_list.sort()
    work_list = [w.replace(" " + os.sep, os.sep) for w in work_list]
    dtb.close()
    # print('make_sorted_list idle loop count:', idle_loops)

    # print(depth_count)
    # print(work_list)

    ''' NOT pointing at Topdir, eg An Artist or an Album is the target.
        If all three levels are zero, bail out because no music at all.
        If level 2 and 3 is zero, No Artist/No Album become dir_name-2/dir_name-1
        If 3 is zero, /No Album becomes Artist Name level
                      Artist Name becomes dir_name - 1
    '''
    PRUNED_DIR = START_DIR  # Needed to prune off /Artist Name/Album Name
    PRUNED_COUNT = 0

    if depth_count[0] == 0 and depth_count[1] == 0 and depth_count[2] == 0:
        return work_list, depth_count  # No songs, or started pointing at single song

    if depth_count[1] == 0 and depth_count[2] == 0:
        # No Artist & No Album encountered
        PRUNED_COUNT = 2

    if depth_count[1] > 0 and depth_count[2] == 0:
        # No Album encountered
        PRUNED_COUNT = 1

    ''' Create the pseudo start directory '''
    for i in range(0, PRUNED_COUNT):
        #print("looping through prunes:", i)
        PRUNED_DIR = PRUNED_DIR[:-1]  # Remove os.sep from end
        last_sub_dir = PRUNED_DIR.rfind(os.sep)  # Find last os.sep
        PRUNED_DIR = PRUNED_DIR[:last_sub_dir] + os.sep  # Shorten path

    if PRUNED_COUNT > 0:
        work_list = [w.replace(os.sep + NO_ALBUM_STR, '') for w in work_list]

    if PRUNED_COUNT > 1:
        work_list = [w.replace(os.sep + NO_ARTIST_STR, '') for w in work_list]

    return work_list, depth_count  # Started pointing at an album


# ==============================================================================
#
#       MusicTree class - Define lib (library of music)
#
# ==============================================================================

class PlayCommonSelf:
    """ Class Variables used by play_selected_list().
        Must appear before MusicTree() class
        
        TODO: Move suitable variables to FileControl().FileControlCommonSelf

    """

    def __init__(self):
        #def __init__(self, toplevel, song_list, sbar_width=12, **kwargs):

        self.killer = ext.GracefulKiller()  # Class to shut down

        self.play_top = None                # Music player selected songs
        self.play_on_top = None             # Is play frame overtop library?
        self.secs_before_pause = None       # get_curr_ffplay_secs(
        self.current_song_t_start = None    # time.time() started playing
        self.saved_DurationSecs = None      # self.play_ctl.DurationSecs
        self.saved_DurationMin = None       # Duration in Min:Sec.Deci
        self.current_song_secs = None       # How much time played
        self.current_song_mm_ss_d = None    # time in mm:ss.d (decisecond)
        self.song_set_ndx_just_run = None   # Song manually set, don't use 'Next'
        self.last_started = None            # self.ndx catch fast clicking Next
        self.play_opened_artist = None      # Play expanded artist in Library?
        self.play_opened_album = None       # Play expanded album in Library?

        # Below called with "python vu_meter.py stereo 2>/dev/null"
        self.vu_meter_pid = None            # Linux Process ID for vu_meter.py
        self.play_top_title = None          # Playlist: Xxx Xxx - mserve
        self.play_frm = None                # play_top master frame
        # July 3, 2023, comment out below. searchable still in comments
        #self.play_frm_bg = None             # "self.play_resized_art.get pixel((3,"
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

        self.current_song_number = None     # Playing song number in playlist
        self.song_artist_var = None         # Metadata Artist name (ellipses)
        self.song_album_var = None          # Metadata Album name (ellipses)
        self.current_song_path = None       # Not sure yet!!!!
        self.song_title_var = None          # Metadata song (Title) name
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
        self.play_frame3 = None             # tk.Frame(self.play_frm child)
        self.lyrics_frm = None              # tk.Frame(self.play_frame3 child)
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
        self.lyrics_score_box = None        # tk.Text(self.play_frame3

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
        self.pp_toggle_fading_out = None    # Used to reverse fade
        self.pp_toggle_fading_in = None     # Used to reverse fade
        self.pp_state = "Playing"
        self.pp_play_text = "▶  Play"       # Can make global var because
        self.pp_pause_text = "❚❚ Pause"     # same text used other classes

        # Resume from previous state when mserve starts up
        self.resume_state = None            # Can be "Paused" or "Playing"
        self.resume_song_secs = None        # Position to start playing song

        ''' Play Top Button frame (_btn) and Buttons (_button) '''
        self.play_btn_frm = None            # tk.Frame(self.play_top, bg="Blue"
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
        self.chron_is_hidden = None         # True/False=Frame .remove()/.grid()
        self.chron_button = None            # tk.Button(..."🖸 Hide Chronology"

        ''' Frame for Playlist Chronology '''
        self.F4 = None                      # tk.Frame(self.play_top, bg="Black

        self.play_ctl = None                # instance of FileControl() class
        self.sam_ctl = None
        self.mus_ctl = None

        # Popup menu
        self.mouse_x = None
        self.mouse_y = None
        self.kid3_window = None

        self.parm = None                    # sys arg parameters called with
        
        # Location common variables
        self.loc_top = None                 # Location toplevel
        self.loc_tree = None                # Tkinter Treeview
        self.loc_tree_btn1 = None           # ✘  Close
        self.loc_tree_btn2 = None           # ▶  Test
        self.loc_tree_btn3 = None           # 🔍 Show location
        self.loc_tree_btn4 = None           # 🗀 Add location
        self.loc_tree_btn5 = None           # 🗀 Edit location
        self.loc_tree_btn6 = None           # 🗀 Forget location
        self.loc_tree_btn7 = None           # 🔍 Compare
        self.loc_F4 = None                  # Frame for Location Data Entry
        self.awake_last_time_check = None
        self.next_active_cmd_time = None

        ''' Define tk variables for Location record used with .set() and .get() '''
        self.iid_var = None                 # L'001', L'002', '003', etc.
        self.name_var = None                # "Dell fileserver", "Phone", etc.
        self.topdir_var = None              # "/mnt/music", "~/music", etc.
        self.host_var = None                # Optional Host name EG "dell"
        self.wakecmd_var = None             # E.G. "wakeonlan 5c:f9:dd:5c:9c:53 ; sleep 4"
        self.testcmd_var = None             # Test if awake E.G. `ssh dell "ls /home/rick"`
        self.testrep_var = None             # Repeat test if awake # times. E.G. "50"
        self.mountcmd_var = None            # E.G. `sshfs "dell:/mnt/music/Users/Person/
                                            #   Music/iTunes/iTunes Media/Music/" /mnt/music`
        # NOTE: On 'dell' file server run `sudo mount -t auto -v /dev/sb1 /mnt/music`
        # 'dell' is running `/mnt/e/bin/ssh-activity` to stay awake when mserve running
        # 'Phone' (Mobile) needs to mount sshfs
        self.activecmd_var = None           # Keep host awake. E.G. `ssh dell "touch /tmp/mserve"`
        self.activemin_var = None           # Send Keep awake command every x minutes. E.G. "10"

        self.state = None                   # Tkinter 'normal' or 'readonly'
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

        ''' Compare locations variables '''
        self.cmp_top = None                 # Compare Locations toplevel - NEW?
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
        self.his_view_btn2 = None           # 🗑 Configuration rows
        self.his_view_btn3 = None           # 🗑
        self.his_view_btn4 = None           # 🗑
        self.his_view_btn5 = None           # ? Text Search
        self.his_view_btn6 = None           # 🖸
        self.his_view_btn7 = None           # ∑ Summary

        ''' SQL miscellaneous variables '''
        self.meta_scan = None               # Class for song metadata searching
        self.meta_scan_dtb = None           # metadata searching delayed textbox
        # NOTE: self.view used for both SQL Music and SQL History.
        #       self.view is the left-click and right-click menu for single row
        self.view = None                    # Shared view for SQL Music and SQL History
        self.common_top = None              # Top level clone for SQL Music or History
        # NOTE: self.hdr_top is window opened drilling down into treeview heading too
        self.hdr_top = None                 # hdr, iid & scrollbox for create_window()
        self.view_iid = None                # Treeview IID of row ID clicked on
        self.scrollbox = None               # Used by self.create_window()

        ''' Global variables of active children '''
        self.play_top_is_active = False     # Playing songs window open?
        self.sam_top_is_active = False      # sample middle of song open?
        self.loc_top_is_active = False      # locations treeview open?
        self.cmp_top_is_active = False      # compare locations open?
        #self.sync_top_is_active = False      # Sync Time Index window open?
        self.mus_top_is_active = False      # View SQL Music open?
        self.his_top_is_active = False      # View SQL History open?
        self.hdr_top_is_active = None       # Did we open SQL drill down window?
        self.sync_paused_music = False      # Important this is False now
        #self.sync_changed_score = False     # For warning messages
        #self.sync_ffplay_is_running = False     # Music playing for Syncing?
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
        self.tv_vol = None               # tvVolume() during Hockey TV commercials

        ''' Playlists stored in SQL database '''
        self.playlists = None               # Playlists()
        self.title_suffix = None  # title_suffix used in two places below

        ''' Menu bars: File, Edit, View + space + playlist information '''
        self.file_menu = None
        self.edit_menu = None
        self.view_menu = None
        self.playlist_bar = None

        ''' last_sleep_time for mor accurate 30 frames per second (fps) '''
        self.last_sleep_time = time.time()


class MusicTree(PlayCommonSelf):
    """ Create self.lib_tree = tk.Treeview() via CheckboxTreeview()

        Resizeable, Scroll Bars, select songs, play songs.

        If toplevel is not None then it is the splash screen to destroy.

    """

    def __init__(self, toplevel, song_list, sbar_width=12):

        PlayCommonSelf.__init__(self)  # Define self. variables
        ext.t_init('MusicTree() __init__(toplevel, song_list, sbar_width=12)')

        # If we are started by splash screen get object, else it will be None
        self.splash_toplevel = toplevel

        # Create our tooltips pool (hover balloons)
        self.tt = toolkit.ToolTips()

        dtb = message.DelayedTextBox(title="Building music view",
                                     toplevel=None, width=1000)
        self.ndx = 0  # Start song index
        self.play_from_start = True  # We start as normal
        self.fake_paths = song_list  # May contain /<No Artist>/<No Album>
        self.real_paths = []  # stripped out <No Artist> and <No Album>
        # self.fake_paths = song_list = SORTED_LIST = make_sorted_list(START_DIR)

        self.lib_top = tk.Toplevel()
        self.lib_top_is_active = True
        self.lib_top.minsize(g.WIN_MIN_WIDTH, g.WIN_MIN_HEIGHT)

        ''' Set program icon in taskbar '''
        img.taskbar_icon(self.lib_top, 64, 'white', 'lightskyblue', 'black')

        ''' Mount window at previously used location '''
        self.lib_top.minsize(width=BTN_WID * 10, height=PANEL_HGT * 4)
        ext.t_init("monitor.get_window_geom('library')")
        geom = monitor.get_window_geom('library')
        self.lib_top.geometry(geom)
        ext.t_end('no_print')  # June 13, 2023 - 0.0002460480

        self.lib_top.configure(background="Gray")
        self.lib_top.columnconfigure(0, weight=1)
        self.lib_top.rowconfigure(0, weight=1)

        ''' Create frames '''
        master_frame = tk.Frame(self.lib_top, bg="Olive", relief=tk.RIDGE)
        master_frame.grid(sticky=tk.NSEW)
        master_frame.columnconfigure(0, weight=1)
        master_frame.rowconfigure(0, weight=0)  # InfoCentre bar frame
        master_frame.rowconfigure(1, weight=1)  # treeview frame

        ''' Expanding/collapsing information centre Frame - PART I of II '''
        # noinspection SpellCheckingInspection
        self.banner_frm = tk.Frame(master_frame, bg="SkyBlue3", height=7)
        self.banner_frm.grid(row=0, column=0, sticky=tk.NSEW)
        self.banner_btn = None  # will be built in next line
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
        self.lib_tree.heading("Access", text="Count / Last Access")
        self.lib_tree.column("Size", width=50, anchor=tk.E, stretch=tk.YES)
        self.lib_tree.heading("Size", text="Size " + CFG_DIVISOR_UOM, anchor=tk.E)
        self.lib_tree.column("Selected", width=50, anchor=tk.E, stretch=tk.YES)
        self.lib_tree.heading("Selected", text="Play № / Sel. MB", anchor=tk.E)

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
        self.info = InfoCentre(self.lib_top, self.lib_tree, self.banner_frm,
                               self.banner_btn, self.build_banner_btn, self.tt)

        pav.registerInfoCentre(self.info)  # Wasn't available earlier

        patterns = [("using directory:", "Green", "Black")]
        self.info.fact("mserve started using directory: " + g.MSERVE_DIR,
                       patterns=patterns)

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
        self.lib_top_totals[0] = LODICT['name']
        self.lib_top_totals[1] = ""  # Playlist name makes title too long
        self.lib_top_playlist_name = ""  # appended to lib_top.title after totals

        ''' Music Library Dropdown Menu references Playlists() and InfoCentre() '''
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
        style.configure("Treeview", font=(None, MON_FONTSIZE),
                        rowheight=row_height)
        style.configure('Treeview', indent=row_height + 6)

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

        ''' Shortcut to save time. It works but is difficult to read.
            TODO: Save code in toolkit.py for potential resurrection.
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
        frame3 = tk.Frame(master_frame, bg="Blue", bd=2, relief=tk.GROOVE,
                          borderwidth=BTN_BRD_WID)
        frame3.grid_rowconfigure(0, weight=1)
        frame3.grid_columnconfigure(0, weight=0)
        frame3.grid(row=3, column=0, sticky=tk.NW)  # May 28, 2023 was row=2

        ''' ✘ Close Button ✘ ✔ '''
        self.lib_top.bind("<Escape>", self.close)
        self.lib_top.protocol("WM_DELETE_WINDOW", self.close)
        lib_tree_btn1 = tk.Button(frame3, text="✘ Close", width=BTN_WID - 2, 
                                  command=self.close)
        lib_tree_btn1.grid(row=0, column=0, padx=2)
        self.tt.add_tip(lib_tree_btn1, anchor="nw",
                        text="Close mserve and any windows mserve opened.")

        ''' ▶  Play Button '''
        self.play_text = "▶  Play"  # Appears when play_top is closed
        self.lib_tree_play_btn = tk.Button(
            frame3, text=self.play_text, width=BTN_WID + 2,
            command=self.play_selected_list)
        self.lib_tree_play_btn.grid(row=0, column=1, padx=2)
        self.tt.add_tip(self.lib_tree_play_btn, "Play favorite songs.", anchor="nw")

        ''' Refresh Treeview Button u  1f5c0 🗀 '''
        ''' 🗘  Update differences Button u1f5d8 🗘'''
        lib_tree_btn3 = tk.Button(frame3, text="🗘 Refresh library", 
                                  width=BTN_WID + 2, command=self.rebuild_lib_tree)
        lib_tree_btn3.grid(row=0, column=4, padx=2)
        self.tt.add_tip(lib_tree_btn3, anchor="ne",
                        text="Scan disk for songs added and removed.")

        ''' Rip CD Button 🖸 (1f5b8) '''
        lib_tree_btn4 = tk.Button(frame3, text="🖸  Rip CD", width=BTN_WID - 2,
                                  command=self.rip_cd)
        lib_tree_btn4.grid(row=0, column=5, padx=2)
        self.tt.add_tip(lib_tree_btn4, anchor="ne",
                        text="Convert songs from Audio CD to music files.")

        ''' Colors for tags '''
        self.ignore_item = None
        #self.lib_tree.tag_configure('popup_sel', foreground='ForestGreen')
        #self.lib_tree.tag_configure('play_sel', foreground='Red')
        self.lib_tree.tag_configure('play_sel', background='ForestGreen',
                                    foreground="White")
        self.lib_tree.tag_configure('popup_sel', background='yellow')

        ''' Refresh last played 999 ago, every minute '''
        self.last_inotify_time = None  # Last time bubble message sent
        self.refresh_acc_times(first_time=True)  # Update last access time every 60 seconds

        dtb.close()  # Close our startup messages delayed text box
        self.lib_top.bind("<FocusIn>", self.handle_lib_top_focus)
        ext.t_end('no_print')  # May 24, 2023 - MusicTree() : 1.0563580990
        # June 13, 2023 -    MusicTree() init__(toplevel...): 1.3379859924

        ''' Load last selections and resume playing music from last session '''
        self.load_last_selections()  # Play songs in favorites or playlists

        ''' When load_last_selections() ends we need to enter idle loop
            until self.close() is called. '''
        while self.refresh_lib_top():  # Sleeps for 33ms
            if self.lib_top is None:
                break

    def build_banner_btn(self):
        """ Called from init in MusicTree() class and InfoCentre() class
        """
        # Use lambda because self.info.view() hasn't been defined yet.
        self.banner_btn = tk.Button(self.banner_frm, height=0, bg="SkyBlue3",
                                    fg="black", command=lambda: self.info.view())
        self.banner_btn.place(height=7, width=7000)  # ...height of 7 override
        text = "▼ ▲ ▼ ▲  Expanding/Collapsing Information Centre  ▲ ▼ ▲ ▼ \n\n" +\
            "Click this ruler line and it expands to a large frame.\n\n" +\
            "Actions are displayed with the most recent at the top.\n\n" +\
            "You can also access using the 'View' Dropdown Menu and\n" +\
            "selecting the 'Information Centre option."
        self.tt.add_tip(self.banner_btn, text=text, anchor="sc",
                        visible_span=1000, extra_word_span=100,
                        visible_delay=150, fade_out_span=149)

    def build_lib_top_playlist_name(self):
        """ name goes into lib_top.title()
            self.playlists.name is inside Playlists() class
        """
        if self.playlists.name is not None:
            #self.lib_top_playlist_name = self.playlists.name
            self.lib_top_playlist_name = self.playlists.name.encode("utf-8")
            # Fix error message: tcl error > FFFF
            #    "  ☰ " + self.lib_top_playlist_name + " - mserve")
            # TclError: character U+1f3b5 is above the range(U + 0000 - U + FFFF) allowed by Tcl
            #   NOTE: “🎵” U+1F3B5 Musical Note Unicode Character
            #self.lib_top_playlist_name = toolkit.normalize_tcl(self.playlists.name)
            # "Rainy Days" becomes "Rain? Da?s".
            # June 17, 2023 patch normalize_tcl() to support "vwx yz" instead of "?"
            #print("build_lib_top_playlist_name() self.playlists.name:",
            #      self.playlists.name)  # Playlist "Rainy Days"
            #print("build_lib_top_playlist_name() self.lib_top_playlist_name:",
            #      self.lib_top_playlist_name)  # becomes "Rain? Da?s"
        else:
            self.lib_top_playlist_name = LODICT['iid'] + " - Default Favorites"

    def set_title_suffix(self):
        if self.playlists.name is not None:
            self.title_suffix = "Playlist: " + self.playlists.name
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
        self.lib_top.config(menu=mb)  # This takes a full second to run
        #self.lib_top['menu'] = mb  # Also takes a full second to run
        ext.t_end('no_print')

        ext.t_init('self.file_menu = tk.Menu(mb)')
        self.file_menu = tk.Menu(mb, tearoff=0)
        self.file_menu.add_command(label="New Location", font=(None, MED_FONT),
                                   command=lambda: self.loc_add_new(caller='Drop',
                                                                    mode='Add'))
        self.file_menu.add_command(label="Open Location & Play", font=(None, MED_FONT),
                                   command=lambda: self.loc_open_play(caller='Drop'))
        self.file_menu.add_separator()

        self.file_menu.add_command(label="Open Playlist", font=(None, MED_FONT),
                                   command=self.playlists.open, state=tk.DISABLED)
        self.file_menu.add_command(label="New Playlist", font=(None, MED_FONT),
                                   command=self.playlists.new, state=tk.DISABLED)
        self.file_menu.add_command(label="Rename Playlist", font=(None, MED_FONT),
                                   command=self.playlists.rename, state=tk.DISABLED)
        self.file_menu.add_command(label="Delete Playlist", font=(None, MED_FONT),
                                   command=self.playlists.delete, state=tk.DISABLED)
        self.file_menu.add_command(label="Save Playlist", font=(None, MED_FONT),
                                   command=self.write_playlist_to_disk, state=tk.DISABLED)
        self.file_menu.add_command(label="Save Playlist As…", font=(None, MED_FONT),
                                   command=self.playlists.save_as, state=tk.DISABLED)
        self.file_menu.add_command(label="Close Playlist (Use Favorites)", font=(None, MED_FONT),
                                   command=self.close_playlist, state=tk.DISABLED)
        self.file_menu.add_separator()  # NOTE: UTF-8 3 dots U+2026 …

        #self.file_menu.add_command(label="Save Play and Restart", font=(None, MED_FONT),
        #                           command=self.restart)
        # Uncomment above if heavy development changes needed for testing, beware:
        # of: SLOWDOWN BUG: https://gitlab.gnome.org/GNOME/gnome-shell/-/issues/2674
        # and: SLOWDOWN BUG: https://gitlab.gnome.org/GNOME/gnome-shell/-/issues/3125
        # The facts are apparent when you restart. To save time, just exit and type 'm'.

        self.file_menu.add_command(label="Save Play and Exit", font=(None, MED_FONT),
                                   command=self.close)
        self.file_menu.add_separator()

        self.file_menu.add_command(label="Save Favorites", font=(None, MED_FONT),
                                   command=self.write_playlist_to_disk, state=tk.DISABLED)
        self.file_menu.add_command(label="Exit and CANCEL Pending", font=(None, MED_FONT),
                                   command=self.exit_without_save, state=tk.DISABLED)

        mb.add_cascade(label="File", menu=self.file_menu, font=(None, MED_FONT))
        ext.t_end('no_print')  # 0.0009999275

        # Edit Menu - Edit Location
        ext.t_init('self.edit_menu = tk.Menu(mb)')
        self.edit_menu = tk.Menu(mb, tearoff=0)
        self.edit_menu.add_command(label="Edit Location", font=(None, MED_FONT),
                                   command=lambda: self.loc_edit(
                                   caller='Drop', mode='Edit'))
        self.edit_menu.add_command(label="Compare Location", font=(None, MED_FONT),
                                   command=lambda: self.loc_compare(
                                   caller='Drop', mode='Compare'))
        self.edit_menu.add_command(label="Forget Location", font=(None, MED_FONT),
                                   command=lambda: self.loc_forget(
                                   caller='Drop', mode='Forget'))
        self.edit_menu.add_separator()
        # Volume for Hocker Commercials state will be enabled by get_hockey_state()
        self.edit_menu.add_command(label="TV Volume for Hockey Commercials",
                                   font=(None, MED_FONT), state=tk.DISABLED,
                                   command=self.set_tv_volume)

        mb.add_cascade(label="Edit", menu=self.edit_menu, font=(None, MED_FONT))
        ext.t_end('no_print')  # 0.0004191399

        ext.t_init('self.view_menu = tk.Menu(mb)')
        # View menu - Show locations and SQL library  #command=lambda: self.info.test_tt("Hello")
        self.view_menu = tk.Menu(mb, tearoff=0)
        self.view_menu.add_command(label="Information Centre", font=(None, MED_FONT),
                                   command=self.info.view)
        self.view_menu.add_command(label="Show Location", font=(None, MED_FONT),
                                   command=lambda: self.show_location(
                                   caller='Drop', mode='Show'))
        self.play_hockey_allowed = self.get_hockey_state()
        if self.play_hockey_allowed:
            text = "Enable FF/Rewind buttons"  # TODO: Make self.variable names
        else:
            text = "Use TV Commercial buttons"
        self.view_menu.add_command(label=text, font=(None, MED_FONT),
                                   command=self.toggle_hockey)
        self.view_menu.add_separator()  # If countdown running, don't show options

        self.view_menu.add_command(label="SQL Music", font=(None, MED_FONT),
                                   command=self.show_sql_music)
        self.view_menu.add_command(label="SQL History", font=(None, MED_FONT),
                                   command=self.show_sql_hist)
        self.view_menu.add_separator()
        self.view_menu.add_command(label="Debug Information", font=(None, MED_FONT),
                                   command=self.show_debug)

        mb.add_cascade(label="View", menu=self.view_menu, font=(None, MED_FONT))
        ext.t_end('no_print')  # 0.0006351471

        self.enable_lib_menu()

    def enable_lib_menu(self):
        """
        Called from build_lib_menu() and passed to self.playlists to manually
        set options.
        :return: None
        """
        self.disable_playlist_menu()

        if self.playlists.top:  # If top level is open, everything disabled.
            return

        if self.playlists.name is not None:
            # Can close even if pending counts but there will be confirmation inside
            self.file_menu.entryconfig("Save Playlist As…", state=tk.NORMAL)
            self.file_menu.entryconfig("Close Playlist (Use Favorites)", state=tk.NORMAL)

        if self.get_pending_cnt_total() == 0:
            # If nothing pending can open create new playlist, etc.
            self.file_menu.entryconfig("Open Playlist", state=tk.NORMAL)
            self.file_menu.entryconfig("New Playlist", state=tk.NORMAL)
            self.file_menu.entryconfig("Rename Playlist", state=tk.NORMAL)
            self.file_menu.entryconfig("Delete Playlist", state=tk.NORMAL)

        # What do do when Favorites are pending?

        if self.pending_add_cnt != 0 or self.pending_del_cnt != 0:
            # Do not want save option until pending is applied or cancelled
            return

        if self.playlists.name is not None and self.get_pending_cnt_total() > 0:
            self.file_menu.entryconfig("Save Playlist", state=tk.NORMAL)
            self.file_menu.entryconfig("Save Playlist As…", state=tk.NORMAL)

    def disable_playlist_menu(self):
        """ Called above and self.pending_apply() when changes made to Favorites
            Also called as soon as Checkbox processing starts. June 17, 2023 error
            message in self.playlists.new() and .open() are no longer needed now.
        """
        self.file_menu.entryconfig("Open Playlist", state=tk.DISABLED)
        self.file_menu.entryconfig("New Playlist", state=tk.DISABLED)
        self.file_menu.entryconfig("Rename Playlist", state=tk.DISABLED)
        self.file_menu.entryconfig("Delete Playlist", state=tk.DISABLED)
        self.file_menu.entryconfig("Save Playlist", state=tk.DISABLED)
        self.file_menu.entryconfig("Save Playlist As…", state=tk.DISABLED)
        self.file_menu.entryconfig("Close Playlist (Use Favorites)", state=tk.DISABLED)

    def apply_playlists(self):
        """ Called from Playlists() class after 'new' or 'open' playlist
            self.playlists.apply_callback()

            TODO: After hundred restarts, takes 8 seconds to open playlist
                  so info.cast messages sent by Playlists() never appear?

            self.info.cast("Opened playlist: " + self.act_name)
            self.apply_callback()  # Parent will start playing (if > 1 song in list)
            #self.info.cast("Opened playlist: " + self.act_name)  # doesn't work either
        elif self.state == 'new':
            self.save_playlist()  # Save brand new playlist
            self.name = None
            self.curr_number_str = None  # Replaces .name in future
            self.play_close()  # must be called before name is set
            self.name = self.act_name  # Tell parent name of playlist
            self.last_number_str = self.curr_number_str  # Replaces .name in future
            self.curr_number_str = self.act_number_str
            # June 23, 2023 - info.cast isn't appearing?
            self.info.cast("Created new playlist: " + self.act_name, action="add")
            self.apply_callback()  # Begin editing new playlist



        """
        self.ndx = 0  # resume will set to last playing song
        self.saved_selections = []  # lib_tree id's in sorted play order
        self.playlist_paths = []  # full path names that need to be pruned
        self.clear_all_checks_and_opened()  # Clear in lib_tree (music library)

        # Build playlist_paths using Music Ids
        for music_id in self.playlists.act_id_list:
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

        self.get_open_states_to_list()
        self.set_all_checks_and_opened()

        ''' Restore previous open states when we first opened grid '''
        #self.apply_all_open_states(self.lib_tree_open_states)  # Will not work

        if self.playlists.state == 'open':
            self.info.cast("Opened playlist: " + self.playlists.act_name)
        elif self.state == 'new':
            self.info.cast("Created new playlist: " + self.playlists.act_name, action="add")

        if len(self.saved_selections) >= 2:
            self.play_from_start = False  # Continue playing where we left off
            self.play_selected_list()

    def close_playlist(self):
        """
            Called from File Dropdown Menu
        """
        if not self.playlists.close():
            ''' If user confirms, playlists.close() proceeds with:
                    self.play_close()  # close main playing window
                    self.name = None
                    self.display_lib_title()
            '''
            return  # Playlist changes haven't been saved yet

        # If there were any pending amounts, use chose not to save.
        self.pending_tot_add_cnt = self.pending_tot_del_cnt = 0
        self.pending_reset(ShowInfo=False)  # Just in case it was open.
        self.enable_lib_menu()
        self.load_last_selections()

    def handle_lib_top_focus(self, _event):
        """
            When tvVolume() Slider or Playlists() windows are active,
            always stays above Music Library (lib_top).

            Credit: https://stackoverflow.com/a/44615104/6929343

        :param _event: Ignored
        :return: None
        """
        if self.tv_vol and self.tv_vol.top:
            self.tv_vol.top.focus_force()  # Get focus
            self.tv_vol.top.lift()  # Raise in stacking order

        if self.playlists.top:
            self.playlists.top.focus_force()  # Get focus
            self.playlists.top.lift()  # Raise in stacking order

        ''' Synchronizing lyrics to time index controls music '''
        if self.fine_tune and self.fine_tune.top_is_active:
            #self.fine_tune.top_lift()  # Need name change....
            # Above steals focus and keyboard from other applications !
            #self.fine_tune.top.focus_force()
            #self.fine_tune.top.lift()
            self.fine_tune_lift()
        #if self.sync_top_is_active:
        #    # Although launched by play_top this probably won't hurt
        #    self.fine_tune.top_lift()  # Raise window focus to top

        ''' Sampling random song in lib_tree '''
        if self.sam_top_is_active:
            self.sample_song_lift()  # Raise in stacking order

        ''' Since lib_top is known to have focus can reset self.lib_tree_play_btn '''
        self.play_on_top = False
        self.set_lib_tree_play_btn()

    def refresh_lib_top(self):
        """ Wait until clicks to do something in lib_tree (like play music)
            NOTE: this would be a good opportunity for housekeeping
            TODO: Call refresh_acc_times() every 60 seconds
            
        """

        if not self.lib_top_is_active:
            return False  # self.close() has set to None

        ''' Is system shutting down? '''
        if self.killer.kill_now:
            print('\nmserve.py refresh_lib_top() closed by SIGTERM')
            self.close()
            return False  # Not required because this point never reached.

        ''' Synchronizing lyrics to time index controls music 
            Original code yanked July 7, 2023. Currently refresh_play_top()
            is only used. If play_top gets closed it automatically closes
            self.fine_tune class.
        # NOTE THIS IS BROKEN on July 7, 2023
        # First section isn't calling self.tt.poll_tips()
        # Below is duplicated code in self.refresh_play_top. DRY it.
        if self.fine_tune and self.fine_tune.top_is_active:
            self.fine_tune.top.update()  # Without this no keyboard/mouse click
            self.fine_tune.top.after(50)
            return False  # Looks like True causes animations to freeze
        '''

        ''' Always give time slice to tooltips '''
        self.tt.poll_tips()  # Tooltips fade in and out. self.info piggy backing
        pav.poll_fades()
        self.lib_top.update()  # process events in queue. E.G. message.ShowInfo()

        if not self.lib_top_is_active:  # Second check needed June 2023
            return False  # self.close() has set to None

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
        """ WIP """
        ''' Frame for Pending Playlist Updates from Checkbox Actions '''
        text = "Pending Playlist Updates from Checkbox Actions"
        self.pending_frame = tk.LabelFrame(
            master_frame, borderwidth=BTN_BRD_WID, text=text,
            relief=tk.GROOVE, font=('calibre', 13, 'bold'))
        self.pending_frame.grid(row=2, column=0, sticky=tk.NSEW)
        self.pending_frame.grid_columnconfigure(3, weight=5)  # Song name extra wide

        ms_font1 = (None, MON_FONTSIZE)  # Temporary for error message
        ms_font2 = (None, MON_FONTSIZE)  # Temporary for error message

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
        if not self.pending_grid_visible:
            # July 6, 2023 - happens when closing playlist when changes not saved
            print("mserve.py pending_remove_grid() called but already invisible.")
            return
        self.pending_grid_visible = False
        if GRID_REMOVE_SUPPORTED:
            self.pending_frame.grid_remove()

    def pending_restore_grid(self):
        # When applying or canceling updates, restore open_states
        self.lib_tree_open_states = self.get_all_open_states()
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
            message.ShowInfo(self.lib_top, thread=self.get_refresh_thread(),
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
            if self.playlists.name is not None:
                music_id = sql.music_id_for_song(delete_path[len(PRUNED_DIR):])
                if music_id == 0:
                    toolkit.print_trace()
                    print("sql.music_id_for_song(delete_path[len(PRUNED_DIR):])\n")
                else:
                    delete_ndx = self.playlists.act_id_list.index(music_id)
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

        ''' Delete music ids in reverse order from self.playlists.act_id_list '''
        if self.playlists.name is not None:
            for index in sorted(delete_music_ndx_list, reverse=True):
                music_id = self.playlists.act_id_list[index]
                del self.playlists.act_id_list[index]
                d = sql.music_get_row(music_id)
                if d is None:
                    print("ERROR bad song getting deleted (no meta)")
                else:
                    self.playlists.act_size -= d['OsFileSize']
                    self.playlists.act_count -= 1
                    self.playlists.act_seconds -= d['Seconds']
                dprint("deleting self.playlists.act_id_list[index]" +
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

            ''' Build list of Music IDs to insert into self.playlists.act_id_list '''
            if self.playlists.name is not None:
                #music_id = sql.music_id_for_song(insert_path[len(PRUNED_DIR):])
                d = sql.ofb.Select(insert_path[len(PRUNED_DIR):])
                if d is None:
                    print("Cannot process song when it hasn't been played (no meta)")
                else:
                    insert_music_ids.append(d['Id'])
                    self.playlists.act_size += d['OsFileSize']
                    self.playlists.act_count += 1
                    self.playlists.act_seconds += d['Seconds']
                    dprint("Building Music ID:", d['Id'])

        if len(insert_play_paths) != self.pending_add_cnt:
            dprint("len(insert_play_paths) != self.pending_add_cnt")
            dprint(len(insert_play_paths), "!=", self.pending_add_cnt)

        if len(self.pending_additions) != self.pending_add_cnt:
            dprint("len(self.pending_additions) != self.pending_add_cnt")
            dprint(len(self.pending_additions), "!=", self.pending_add_cnt)

        if insert_at >= len(self.saved_selections):
            self.saved_selections.extend(self.pending_additions)
            self.playlist_paths.extend(insert_play_paths)
            if self.playlists.name is not None:
                self.playlists.act_id_list.extend(insert_music_ids)
            dprint("Appending at end:", len(self.saved_selections),
                   "self.pending_additions:", self.pending_additions)
        else:
            self.saved_selections[insert_at:insert_at] = self.pending_additions
            # NEED to insert insert_music_id_list into act_music_id list in Playlists
            self.playlist_paths[insert_at:insert_at] = insert_play_paths
            if self.playlists.name is not None:
                self.playlists.act_id_list[insert_at:insert_at] = insert_music_ids
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
            self.info.cast("mserve.py pending_apply() self.ndx is negative:" +
                           self.ndx, 'error')
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
        if self.playlists.name is not None:
            self.enable_lib_menu()
            self.file_menu.entryconfig("Save Playlist", state=tk.NORMAL)
            # Save Playlist As hasn't been written yet.
            self.file_menu.entryconfig("Save Playlist As…", state=tk.DISABLED)
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
            self.lib_top, thread=self.get_refresh_thread(),
            align='left', title="Playlist changes applied.",
            text="Changes to checkboxes in Music Library saved in memory.\n\n" +
                 "Playlist in memory has been updated with:\n" +
                 add_del_str +
                 "\nPlaylist in storage has NOT been saved yet.")

        DPRINT_ON = False  # Turn off debug printing

    def get_refresh_thread(self):
        if self.play_top_is_active:
            thread = self.refresh_play_top
        elif self.lib_top_is_active:
            thread = self.refresh_lib_top
        else:
            thread = None  # June 26 2023 - Return None when destroyed
        return thread

    def pending_reset(self, ShowInfo=True):
        # Rebuild checkboxes, selected totals, song play order numbers
        # Get current open states to reopen after cancel processing
        # Uncheck all artists, albums, songs and "songsel" tags
        self.clear_all_checks_and_opened()  # Clear in lib_tree music library
        self.set_all_checks_and_opened()  # Rebuild using playlist in memory
        ''' Restore previous open states when we first opened grid '''
        self.apply_all_open_states(self.lib_tree_open_states)

        ''' When called from pending_apply(), no message to display '''
        if ShowInfo:
            message.ShowInfo(
                self.lib_top, thread=self.get_refresh_thread(),
                align='left', title="Playlist changes cancelled.",
                text="Changes to checkboxes in Music Library reversed.\n" +
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
            All songs are NOT selected. They will be selected LATER.

            NOTE: With cell phone, dtb() may be mounted and every 30 frames
                  the current artist/album is displayed.
        """

        LastArtist = ""
        LastAlbum = ""
        CurrAlbumId = ""  # When there are no albums?
        CurrArtistId = ""  # When there are no albums?
        level_count = [0, 0, 0]  # Count of Artists, Albums, Songs

        start_dir_sep = START_DIR.count(os.sep) - 1  # Number of / separators
        global PRUNED_COUNT
        # print('PRUNED_COUNT:', PRUNED_COUNT)
        start_dir_sep = start_dir_sep - PRUNED_COUNT

        for i, os_name in enumerate(self.fake_paths):

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
                level_count[0] += 1  # Increment artist count
                opened = False  # New installation would be more concise view for user
                CurrArtistId = self.lib_tree.insert(
                    "", "end", text=Artist, tags=("Artist", "unchecked"), open=opened,
                    values=("",  "",  "",  0.0,  0,  0,    0,  0,  0, 0))
                #           Access    Selected   StatSize  sSize   sSeconds
                #           0         2          4         6       8
                #   values=("",  "",  "",  0.0,  0,  0,    0,  0,  0 )
                #                1         3         5         7
                #                Size      StatTime  Count     sCount

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
            full_path = full_path.replace(os.sep + NO_ARTIST_STR, '')
            full_path = full_path.replace(os.sep + NO_ALBUM_STR, '')
            self.real_paths.append(full_path)

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
            ftime = tmf.ago(float(stat.st_atime), seconds=True)

            ''' Add the song '''
            self.lib_tree.insert(
                CurrAlbumId, "end", iid=str(i), text=Song, tags=("Song", "unchecked"),
                values=(ftime, fsize, '', float(stat.st_atime), stat.st_size, 1, 0, 0, 0, 0))
            self.tree_col_range_replace(str(i), 6, [1, 0, 0, 0, 0])
            self.lib_tree.tag_bind(str(i), '<Motion>', self.lib_highlight_row)

        self.display_lib_title()  # Was called thousands of times above.

    @staticmethod
    def lib_highlight_row(event):
        """ Cursor hovering over row highlights it in light blue
        """
        tree = event.widget
        item = tree.identify_row(event.y)
        tree.tk.call(tree, "tag", "remove", "highlight")
        tree.tk.call(tree, "tag", "add", "highlight", item)

    @staticmethod
    def lib_leave_row(event):
        """
        Un-highlight row just left
        """
        tree = event.widget
        tree.tk.call(tree, "tag", "remove", "highlight")

    def toggle_select(self, song, album, artist):
        """ Toggle song selection off and on. Update selected values and
            roll up totals into parents. Only called when manually checking
            boxes. Never called for batched checkbox processing on load or
            Process Pending functions.
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
            old = self.lib_tree.item(song)['values'][2]  # "Selected" column ndx 2
            if old == "Adding":
                self.lib_tree.set(song, "Selected", "")  # Reset to nothing
            else:
                self.lib_tree.set(song, "Selected", "Deleting")  # Will be deleted
            tags.remove("songsel")
            self.lib_tree.item(song, tags=tags)
            # noinspection PyProtectedMember
            self.lib_tree._uncheck_ancestor(song)  # in CheckboxTreeview()
            # Get StatSize, Count and Seconds multiplying by negative 1
            adj_list = [element * -1 for element in
                        self.lib_tree.item(song)['values'][total_values]]
            # [total_values] = slice(4,7)
        else:
            # We will toggle on and add to selected parent totals
            tags.append("songsel")
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
        human_all_sizes = human_mb(self.lib_top_totals[5])
        human_selected = human_mb(self.lib_top_totals[8])
        # Default format for NO songs selected
        self.lib_top_totals[2] = \
            "   🎵 " + '{:n}'.format(song_count) + ' songs.'
        self.lib_top_totals[3] = "   🖸 " + human_all_sizes + " used."

        if selected_count > 0:
            # Extend format for at least one song selected
            self.lib_top_totals[2] += " "+'{:n}'.format(selected_count) + ' selected.'
            self.lib_top_totals[3] += " " + human_selected + ' selected.'

        self.build_lib_top_playlist_name()  # More verbose than self.title_suffix
        self.lib_top.title(self.lib_top_totals[0] + self.lib_top_totals[1] +
                           self.lib_top_totals[2] + self.lib_top_totals[3] +
                           "   ☰ " + self.lib_top_playlist_name + " - mserve")
        # June 18, 2023 new error:
        #   File "/home/rick/python/mserve.py", line 2462, in display_lib_title
        #     self.lib_top.title(self.lib_top_totals[0] + self.lib_top_totals[1] +
        # AttributeError: 'NoneType' object has no attribute 'title'
        #self.lib_top.update_idletasks()  # Will this fix shutdown annoying problem?
        #self.lib_top.update()  # Will this fix shutdown annoying problem?
        #if self.play_top_is_active:
        #    self.play_top.update()  # Will this fix shutdown annoying problem?

    # ==============================================================================
    #
    #       MusicTree Processing - Location and Dropdown Menu options
    #
    # ==============================================================================


    def loc_close(self):
        #def loc_close(self, *args):  # June 19, 2023-found other places unnecessary
        """ Close location treeview """
        if self.loc_top_is_active is False:
            return  # We are already closed
        self.loc_top_is_active = False
        if self.cmp_top_is_active:
            self.cmp_close()  # Close Compare location treeview
        self.tt.close(self.loc_top)  # Close tooltips under top level
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
            # got lock up in refresh_acc_times() running first.  On file server
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

        ''' ✘ Close Button - Always visible '''
        self.loc_top.bind("<Escape>", self.loc_close)
        self.loc_top.protocol("WM_DELETE_WINDOW", self.loc_close)
        self.loc_tree_btn1 = tk.Button(frame3, text="✘ Close",
                                       width=BTN_WID, command=self.loc_close)
        self.loc_tree_btn1.grid(row=0, column=0, padx=2)

        ''' ▶  Test Button - Always visible '''
        self.loc_tree_btn2 = tk.Button(
            frame3, text="▶  Test", width=BTN_WID,
            command=lambda: self.loc_test(caller='Tree', mode='Test'))
        self.loc_tree_btn2.grid(row=0, column=1, padx=2)

        ''' ▶  Open Location Button '''
        if mode == 'Open':
            self.location_text = "Open Location"
            self.loc_tree_btn2 = tk.Button(
                frame3, text="▶  Open & play", width=BTN_WID,
                command=lambda: self.loc_open_play(caller='Tree'))
            self.loc_tree_btn2.grid(row=0, column=2, padx=2)
            # NOTE: If column 2 is missing, the other buttons shift left OK

        ''' Show button - Always visible '''
        # Magnifying glass “🔍” U+1F50D
        self.loc_tree_btn3 = tk.Button(
            frame3, text="🔍  Show location", width=BTN_WID,
            command=lambda: self.show_location(caller='Tree', mode='Show'))
        self.loc_tree_btn3.grid(row=0, column=3, padx=2)

        # Following buttons will only appear when those functions are callers
        ''' Add button '''
        if mode == 'Add':
            # File folder “🗀” U+1F5C0
            self.loc_tree_btn4 = tk.Button(
                frame3, text="🗀   Add location", width=BTN_WID,
                command=lambda: self.loc_add_new(caller='Tree', mode='Add'))
            self.location_text = "Add Location"
            self.loc_tree_btn4.grid(row=0, column=4, padx=2)

        ''' Edit button u  1f5c0 🗀 '''
        if mode == 'Edit':
            # File folder “🗀” U+1F5C0
            self.loc_tree_btn5 = tk.Button(
                frame3, text="🗀   Edit location", width=BTN_WID,
                command=lambda: self.loc_edit(caller='Tree', mode='Edit'))
            self.location_text = "Edit Location"
            self.loc_tree_btn5.grid(row=0, column=5, padx=2)

        ''' Forget Button u  1f5c0 🗀 '''
        if mode == 'Forget':
            # File folder “🗀” U+1F5C0
            self.loc_tree_btn6 = tk.Button(
                frame3, text="🗀   Forget location", width=BTN_WID,
                command=lambda: self.loc_forget(caller='Tree', mode='Forget'))
            self.location_text = "Forget Location"
            self.loc_tree_btn6.grid(row=0, column=6, padx=2)

        ''' Compare Button  “🔍” U+1F50D '''
        if mode == 'Compare':
            # Magnifying glass “🔍” U+1F50D
            self.loc_tree_btn7 = tk.Button(
                frame3, text="🔍  Compare", width=BTN_WID,
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
        self.activemin_fld = tk.Entry(self.loc_F4, font=ms_font2, state=self.state,
                                      textvariable=self.activemin_var)
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

    def loc_open_play(self, caller=""):
        """ Open location by calling loc_test() first to check success
            Called from File menu and from within self.loc_create_tree()
            Buttons are dynamic based on caller:
                'Drop' called from top bar dropdown menu
                'Tree' called from treeview button
        """
        global LODICT

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
        if self.playlists.name is not None:
            print("mserve.py loc_open_play() did not save playlist:",
                  self.playlists.name)
            self.info.cast("mserve.py loc_open_play() did not save playlist: " +
                           self.playlists.name)
        else:
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
        """ Forget location and remove ~/.../mserve/L999/* directory
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
            Remove '/home/$USER/.../mserve/L999' directory
            Rename higher '~/.../mserve/L999' directories 1 less
            Update higher iid in locations master file 1 less
            If our opened location iid is changing call:
                lc.set_location_filenames(iid)
                Rename LODICT('iid') with new number
        """
        global LODICT
        our_current_iid = LODICT['iid']
        if iid == our_current_iid:
            message.ShowInfo(
                self.loc_top, thread=self.get_refresh_thread(),
                align='left', icon='warning', title="Location Error",
                text="You cannot forget the location currently running.")
            return

        text  = "The location '" + iid + "' will be forgotten.\n" + \
                "Entry will be removed from list '~/.../mserve/locations'.\n" + \
                "The configuration directory '~/.../mserve/" + iid + \
                "' will be removed.\nThis directory may contain the files:\n" + \
                "- last_open_states - Expanded / Collapsed list of songs.\n" + \
                "- last_playlist - Songs selected for playing\n" + \
                "- last_song_ndx - Last song played in list.\n\n" + \
                "These actions cannot be undone!\n\n" + \
                "Song files, lyrics and synchronization are NOT effected."
        answer = message.AskQuestion(
            self.loc_top, thread=self.get_refresh_thread(), align='left',
            icon='warning', title="Forget Location Confirmation", text=text)
        # print('answer.result:', answer.result)
        if answer.result is not 'yes':
            return

        lc.remove(iid)  # Remove DICT and ~/.../mserve/L999 directory.

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
            #       directory in ~/.../mserve will have to be renamed.
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
            # Time must be in digits
            messagebox.showinfo(title="Location Error",
                                message="Number of times to repeat test command must be an integer.",
                                parent=self.loc_top)
            self.testrep_fld.focus_force()
            return False
        else:
            testrep = int(self.testrep_var.get())

        if not activemin.isdigit():
            # Time must be in digits
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
            self.cmp_build_toplevel(iid)
        else:
            print('submit() Bad self.loc_mode:', self.loc_mode)
            return

        ''' Close loc_tree when cmp_populate_tree() running gets error: 
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

    def cmp_build_toplevel(self, trg_dict_iid, sbar_width=12):
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

        # print('cmp_build_toplevel() get trg_dict',t(time.time()))
        trg_dict = lc.item(trg_dict_iid)  # get dictionary for iid
        self.cmp_target_dir = trg_dict['topdir']

        # If no optional `/` at end, add it for equal comparisons
        if not self.cmp_target_dir.endswith(os.sep):
            self.cmp_target_dir += os.sep

        self.cmp_top = tk.Toplevel()
        self.cmp_top.minsize(g.WIN_MIN_WIDTH, g.WIN_MIN_HEIGHT)
        self.cmp_top_is_active = True

        xy = (self.loc_top.winfo_x() + PANEL_HGT,
              self.loc_top.winfo_y() + PANEL_HGT)
        self.cmp_top.minsize(width=BTN_WID * 10, height=PANEL_HGT * 4)
        self.cmp_top.geometry('%dx%d+%d+%d' % (1800, 500, xy[0], xy[1]))  # 500 pix high
        title = "Compare Locations - SOURCE: " + PRUNED_DIR + \
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
        # self.cmp_tree.heading("#0", text = "➕ / ➖   Artist/Album/Song")
        self.cmp_tree.heading(
            "#0", text="Click ▼ (collapse) ▶ (expand) an Artist or Album")
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

        ''' ✘ Close Button '''
        # TODO: we aren't keeping remote location awake only home location!
        self.cmp_top.bind("<Escape>", self.cmp_close)
        self.cmp_top.protocol("WM_DELETE_WINDOW", self.cmp_close)
        self.cmp_close_btn = tk.Button(frame3, text="✘ Close",
                                       width=BTN_WID - 4, command=self.cmp_close)
        self.cmp_close_btn.grid(row=0, column=0, padx=2)

        ''' Create Treeview using source (START_DIR) as driver '''
        if not self.cmp_populate_tree(trg_dict_iid):  # populate_
            self.cmp_close()  # Files are identical
            return

        ''' 🗘  Update differences Button u1f5d8 🗘'''
        self.update_differences_btn = tk.Button(frame3, width=BTN_WID + 4,
                                                text="🗘  Update differences",
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
        self.tt.close(self.cmp_top)  # Close tooltips under top level
        root.update()
        root.after(50)  # Give time for treeview to close
        self.cmp_top.destroy()  # Close the treeview window

        return True

    def cmp_populate_tree(self, trg_dict_iid):

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

        for i, os_name in enumerate(self.fake_paths):
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
        # Extract real source path from treeview display e.g. strip <No Album>
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

        ''' Set object for warning messages below. '''
        if self.lib_tree.tag_has("Artist", item):
            parent = "Artist"
        elif self.lib_tree.tag_has("Album", item):
            parent = "Album"
        else:
            parent = None

        ''' Warning if status is tri-state, all will be selected. '''
        if self.lib_tree.tag_has("tristate", item):
            dialog = message.AskQuestion(
                self.lib_top, thread=self.get_refresh_thread(),
                title="Discard custom unchecked?",
                text="All songs under " + parent + " will be checked.\n" +
                     "Some Songs are unchecked and will be checked.")
            if dialog.result != 'yes':
                return

        ''' Warning if unchecking parent all children will be unchecked. '''
        if self.lib_tree.tag_has("checked", item) and parent is not None:
            dialog = message.AskQuestion(
                parent=self.lib_top, thread=self.get_refresh_thread(),
                title="Uncheck all songs below?",
                text="All songs under " + parent + " will be unchecked.")
            if dialog.result != 'yes':
                return

        ''' Warning if checking parent all children will be checked. '''
        if self.lib_tree.tag_has("unchecked", item) and parent is not None:
            dialog = message.AskQuestion(
                parent=self.lib_top, thread=self.get_refresh_thread(),
                title="Check all songs below?",
                text="All songs under " + parent + " will be checked.")
            if dialog.result != 'yes':
                return

        ''' ERROR if checking parent with <No Artist> or <No Album>  
            Note design allows unchecking because previous to June 7, 2023 some
            may have been checked or tri-state.
            
            WIP: still need to read up to parents of song, or Artist of Album.
        '''
        if self.lib_tree.tag_has("unchecked", item) and parent is not None\
                and (NO_ARTIST_STR in self.lib_tree.item(item, 'text') or
                     NO_ARTIST_STR in self.lib_tree.item(item, 'text')):
            message.ShowInfo(
                parent=self.lib_top, thread=self.get_refresh_thread(),
                title="Song(s) invalid for playlist when " + NO_ARTIST_STR +
                "\nor " + NO_ALBUM_STR + " exists.", icon='error',
                text="Song(s) under " + parent + " cannot be included in playlist.")
            return  # TODO lookup upwards from Song to parents for same message.

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
        """ We just unchecked the item, update totals
        """
        tags = self.lib_tree.item(item)['tags']
        if 'Artist' in tags or 'Album' in tags:
            self.set_all_parent(item, 'Del', event)
        elif 'Song' in tags:
            self.pending_append(item, 'Del')
            self.reverse(item)
        else:
            print('process_unchecked() bad line type tag:', tags)

    def process_checked(self, item, event):
        """ We just checked the item, update totals
        """
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
        last_time = time.time()
        thread = self.get_refresh_thread()
        for child in self.lib_tree.get_children(Id):
            ''' Preparing for future. May probe each song for duration '''
            now = time.time()
            elapsed = now - last_time  # TODO: make two line function
            if elapsed > 30:  # TODO: make three line function
                # Refresh takes about 3 ms on average to run
                thread()  # Call refresh thread
                last_time = now

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
        if self.playlists.name is not None:
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
        message.ShowInfo(self.lib_top, thread=self.get_refresh_thread(), align='left',
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
        if self.playlists.name is not None:
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
        if Id is None or Id is "":
            return  # clicked on whitespace (no row)

        # print ('popup Id:', Id)
        self.mouse_x, self.mouse_y = event.x_root, event.y_root
        self.kid3_window = ""
        # print ('self.mouse; x, y:', self.mouse_x, self.mouse_y)
        ''' Apply 'popup_sel' tag for visual feedback '''
        toolkit.tv_tag_add(self.lib_tree, Id, "popup_sel")

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
            toolkit.tv_tag_add(self.lib_tree, child, "popup_sel")

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
        menu.bind("<FocusOut>", lambda _: self.close_lib_popup(menu))

    def song_popup(self, event, Id):
        """ Popup menu for a song
            LONG TERM TODO: Display large 500x500 image and all metadata
        """

        menu = tk.Menu(root, tearoff=0)
        menu.post(event.x_root, event.y_root)
        # June 30, 2023 bug hunting
        #self.info.cast("InfoCentre() works here but breaks in lib_tree_play()")
        #print("self.info:", self.info)

        # If lambda isn't used the command is executed as soon as popup
        # menu is displayed, not when option is chosen.
        # self.info.cast is broken in sample_song so use 's=self: s.'
        menu.add_command(label="Sample middle 10 seconds", font=(None, MED_FONT),
                         command=lambda s=self: s.lib_tree_play(Id))
        menu.add_command(label="Sample whole song", font=(None, MED_FONT),
                         command=lambda s=self: s.lib_tree_play(Id, sample="full"))
        if KID3_INSTALLED:
            menu.add_command(label="kid3", font=(None, MED_FONT),
                             command=lambda: self.kid3_song(Id))
        menu.add_command(label="Ignore click", font=(None, MED_FONT),
                         command=lambda: self.remove_popup_sel())

        menu.tk_popup(event.x_root, event.y_root)
        # Without lambda executes immediately, without _: invalid # parameters
        menu.bind("<FocusOut>", lambda _: self.close_lib_popup(menu))

    def close_lib_popup(self, menu):
        self.remove_popup_sel()  # Remove 'popup_sel' tags
        menu.unpost()  # Remove popup menu

    def wrap_up_popup(self):
        self.remove_popup_sel()  # Remove 'popup_sel' tags

    def remove_popup_sel(self):
        # Remove special view popup selection tags to restore normal view
        tags_selections = self.lib_tree.tag_has("popup_sel")
        for child in tags_selections:
            toolkit.tv_tag_remove(self.lib_tree, child, "popup_sel")

    def collapse_all(self, Id):
        opened = self.lib_tree.item(Id, 'open')
        if opened is True or opened == 1:
            self.lib_tree.item(Id, open=False)
        self.wrap_up_popup()  # Set color tags and counts

    def reverse(self, Id):
        """ Toggle song tag on/off. Only used for song, not parent """
        if Id.startswith("I"):
            print("mserve.py reverse(" + Id + "): should not be called.")
            return  # Parents are a no-go
        album = self.lib_tree.parent(Id)
        artist = self.lib_tree.parent(album)
        self.toggle_select(Id, album, artist)

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

        # Set size of Kid3 window
        if KID3_GEOMETRY is not None:
            width = KID3_GEOMETRY.split('x')[0]
            height = KID3_GEOMETRY.split('x')[1]
            # noinspection SpellCheckingInspection
            os.popen('xdotool windowsize ' + self.kid3_window + ' ' +
                     width + ' ' + height)
            # inspection SpellCheckingInspection

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
0x05200004  0 6683     N/A A Momentary Lapse Of Reason [Remaster]  — Kid3
0x05200037  0 6683     N/A Add Frame — Kid3
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
        # 0x05200004  0 6683     N/A Momentary Lapse Of Reason — Kid3
        # 0x05200037  0 6683     N/A Add Frame — Kid3
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

    def exit_without_save(self):
        self.close(save=False)

    # noinspection PyUnusedLocal
    def close(self, save=True, *args):
        if save:
            if self.playlists.name is not None:
                # Saving requires reading stats from lib_tree
                self.write_playlist_to_disk(ShowInfo=False)
            else:
                self.save_last_selections()  # Last selections for next open
        self.close_sleepers()  # Shut down running functions
        self.tt.close(self.lib_top)  # Close tooltips under top level
        root.destroy()
        self.lib_top = None

    # noinspection PyUnusedLocal
    def restart(self, *args):
        self.close()
        # TODO: Test with `m` passing sys.argv via "parameters" keyword.
        os.execl(sys.executable, sys.executable, *sys.argv)

    # noinspection PyUnusedLocal
    def restart_new_parameters(self, *args):
        # NOTE: We've already saved selections and don't want to overwrite
        #       with new location iid
        self.close_sleepers()  # Shut down running functions
        root.destroy()

        print('Restarting with new music library:', self.parm)
        ''' Replace existing, or append first parameter with music directory '''
        if len(sys.argv) > 1:
            sys.argv[1] = self.parm
        else:
            sys.argv.append(self.parm)
        os.execl(sys.executable, sys.executable, *sys.argv)

    def close_sleepers(self):
        # Close loc_keep_awake() first as it has .25-second sleep cycle
        # TODO: Check other sleepers, one might have .5-second sleep cycle
        # COMMON CODE for restart and quit
        self.loc_keep_awake_is_active = False
        self.lib_top_is_active = False      # Tell refresh_acc_times() to bail out

        if self.gone_fishing is not None:
            self.gone_fishing.close()       # Shark eating man animation
            self.gone_fishing = None

        if self.cmp_top_is_active:          # Comparing Locations?
            self.cmp_close()                # Extreme lags when running 'diff'
        #if self.sync_top_is_active:          # Synchronizing lyrics time indices
        #    self.sync_close()
        if self.fine_tune and self.fine_tune.top_is_active:
            self.fine_tune.close()          # Synchronizing lyrics time indices
        if self.play_top_is_active:         # Is music playing?
            self.play_close()
        if self.sam_top_is_active:          # Sampling middle 10 seconds?
            self.lib_tree_play_close()
        if self.loc_top_is_active:          # Editing Locations?
            self.loc_close()
        if self.mus_top_is_active:          # Viewing SQL Music Table?
            self.mus_close()
        if self.his_top_is_active:          # Viewing SQL History Table?
            self.his_close()
        if self.tv_vol and self.tv_vol.top:
            self.tv_vol.close()             # Adjusting Volume during TV commercials?
        if self.playlists.top:              # Close Playlists window and tell it
            self.playlists.reset(shutdown=True)  # NOT to update other windows

        if encoding.RIP_CD_IS_ACTIVE:       # Ripping CD currently active?
            encoding.RIP_CD_IS_ACTIVE = False

        # Last known window position for music library, saved to SQL
        last_library_geom = monitor.get_window_geom_string(
            self.lib_top, leave_visible=False)
        monitor.save_window_geom('library', last_library_geom)

        ''' Remove temporary files '''
        for f in TMP_ALL_NAMES:
            if os.path.isfile(f):
                os.remove(f)

        time.sleep(RESTART_SLEEP)           # Extra insurance sleepers close

    def clear_buttons(self):
        """ When new windows open, disable TreeView buttons """
        self.lib_tree_play_btn["text"] = "🎵  Show library"  # Play button
        self.play_on_top = True
        self.lib_top.update_idletasks()

    def restore_lib_buttons(self):
        """ When playing window closes, restore TreeView buttons """
        self.lib_tree_play_btn["text"] = self.play_text
        self.tt.set_text(self.lib_tree_play_btn, "Play favorite songs.")

    def refresh_acc_times(self, first_time=False):
        """ Refresh songs last access time in Music Library treeview (lib_tree).

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
    #       MusicTree Processing - Refresh Library
    #
    # ==============================================================================

    def rebuild_lib_tree(self):
        """ If directories/songs have changed rebuild cd tree and position
            to first changed song.
            Called from lib_tree's "🗘 Refresh library" button.
        """
        if self.playlists.name is not None:
            self.info.cast("Rebuild music library - Only works when Favorites playing",
                           'error', 'open')
            message.ShowInfo(
                self.lib_top, thread=self.get_refresh_thread(),
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
                self.lib_top, thread=self.get_refresh_thread(),
                title="Refresh music library",
                text="The same " + str(len(SORTED_LIST)) +
                     " songs are in the library.\n\n" +
                     "No updates have been made to the view.")
            return
        else:
            additions = list(set(SortedList2).difference(SORTED_LIST))
            deletions = list(set(SORTED_LIST).difference(SortedList2))
            answer = message.AskQuestion(
                self.lib_top, thread=self.get_refresh_thread(), 
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
        # shutil.copy(lc.FNAME_LAST_SELECTIONS, lc.FNAME_LAST_SELECTIONS + ".bak")
        shutil.copy(lc.FNAME_LAST_PLAYLIST, lc.FNAME_LAST_PLAYLIST + ".bak")

        SORTED_LIST = SortedList2
        self.fake_paths = SORTED_LIST
        self.lib_tree.delete(*self.lib_tree.get_children())
        # Copied from __init__
        dtb = message.DelayedTextBox(title="Building music view",
                                     toplevel=None, width=1000)
        '''
                    B I G   T I C K E T   E V E N T
         
                     Create Music Library Treeview 
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

        self.tv_vol = tvVolume(parent=self.lib_top, tooltips=self.tt,
                               thread=self.get_refresh_thread(),
                               save_callback=self.get_hockey_state,
                               playlists=self.playlists, info=self.info)

    def show_debug(self):
        """ Debugging - show monitors, tooltips and full metadata
        """
        print("\nmserve.py - mon = monitor.py.Monitors()")
        print("=======================================\n")
        mon = monitor.Monitors()            # Monitors class list of dicts

        print("\nmon.screen_width x mon.screen_height:",
              mon.screen_width, "x", mon.screen_height, "\n")

        print("Number of monitors - mon.get_n_monitors():", mon.get_n_monitors())
        for m in mon.monitors_list:
            print(m)
            
        print('\nPrimary - mon.primary_monitor:', mon.primary_monitor)

        print('\n"active_win" - Active Window Tuple - mon.get_active_window():')
        active_win = mon.get_active_window()  # Get tuple
        '''
        Window = namedtuple('Window', 'number, name, x, y, width, height')
        x_id, window_name, geom.xp, geom.yp, geom.width p, geom.height p) 
        '''
        print('active_win.number:', active_win.number)
        print('active_win. x + y + Width x Height:',
              active_win.x, "+", active_win.y, "+", active_win.width,
              "x", active_win.height)
        print('active_win.name:', active_win.name)
        print()

        print("sys.getfilesystemencoding()", sys.getfilesystemencoding())
        #print("os.environ", os.environ)  # Environment is long long long

        print("\nAll Windows - mon.get_all_windows():")
        print("====================================\n")
        for i, window in enumerate(mon.get_all_windows()):
            if window.x > mon.screen_width or window.y > mon.screen_height:
                ''' When second monitor loses power '''
                print("\nERROR: Window is off screen at x+y:",
                      window.x, "+", window.y)
                print("  ", window)
                if window.x > mon.screen_width:
                    adj_x = mon.screen_width - window.x - 500
                else:
                    adj_x = 0
                if window.y > mon.screen_height:
                    adj_y = mon.screen_height - window.y - 500
                else:
                    adj_y = 0
                print("     Adjust to edge -500 amount:", adj_x, "+", adj_y)
                new_x = window.x + adj_x
                new_y = window.y + adj_y
                print("        New coordinates:", new_x, "+", new_y, "\n")
                str_win = str(window.number)  # should remove L in python 2.7.5+
                int_win = int(str_win)  # https://stackoverflow.com/questions
                hex_win = hex(int_win)  # /5917203/python-trailing-l-problem
                # Move window to lower right - 500x500
                os.popen('xdotool windowmove ' + hex_win + ' ' +
                         str(new_x) + ' ' + str(new_y))
                # TODO: Gets moved to dead zone where no monitor exists
                # ERROR: Window is off screen at x+y: 2330 + 3317
                #    Window(number=81788938L, name='Python 3', x=2330, y=3317, width=1300, height=902)
                #      Adjust to edge -500 amount: 0 + -577
                #         New coordinates: 2330 + 2740
                # TODO: Use shark_move to more accurate original coordinates.
                #       Currently instantly appears at lower right -500x-500
            else:
                print(window)

        print("\nCURRENT SONG and POPULAR VARIABLES")
        print("==================================\n")

        song_iid = self.saved_selections[self.ndx]
        song = self.lib_tree.item(song_iid)['text']
        album_iid = self.lib_tree.parent(song_iid)
        album = self.lib_tree.item(album_iid)['text']
        artist_iid = self.lib_tree.parent(album_iid)
        artist = self.lib_tree.item(artist_iid)['text']

        print("self.ndx:", self.ndx, ' | Song iid:', song_iid, " |", song)
        print("tree values:", self.lib_tree.item(song_iid)['values'])
        print("Artist iid:", artist_iid, " |", artist,
              " | Album iid:", album_iid, " |", album)
        print("real_path:", self.real_path(int(song_iid)))
        print("len(SORTED_LIST):", len(SORTED_LIST))
        print('len(self.lib_tree.tag_has("Artist")):',
              len(self.lib_tree.tag_has("Artist")))
        print('len(self.lib_tree.tag_has("Album")):',
              len(self.lib_tree.tag_has("Album")))
        print('len(self.lib_tree.tag_has("Song")):',
              len(self.lib_tree.tag_has("Song")))
        print()
        print("self.playlist_paths[0]:", self.playlist_paths[0],
              " | self.playlist_paths[-1]:", self.playlist_paths[-1])
        print("len(self.playlist_paths):", len(self.playlist_paths),
              " | sys.get size of(self.playlist_paths):",
              sys.getsizeof(self.playlist_paths))
        print()
        print("self.saved_selections[0]:", self.saved_selections[0],
              " | self.saved_selections[-1]:", self.saved_selections[-1])
        print("len(self.saved_selections):", len(self.saved_selections),
              " | sys.get size of(self.saved_selections):",
              sys.getsizeof(self.saved_selections))
        print()
        print("self.fake_paths[0]:", self.fake_paths[0],
              " | self.fake_paths[-1]:", self.fake_paths[-1])
        print("len(self.fake_paths):", len(self.fake_paths),
              "sys.get size of(self.fake_paths):",
              sys.getsizeof(self.fake_paths))
        print()
        print("self.real_paths[0]:", self.real_paths[0],
              " | self.real_paths[-1]:", self.real_paths[-1])
        print("len(self.real_paths):", len(self.real_paths),
              " | sys.get size of(self.real_paths):",
              sys.getsizeof(self.real_paths))
        print()

        print("\nTOOLTIPS - tt.line_dump()")
        print("====================================\n")

        lines = self.tt.line_dump()         # Show Tooltips in memory
        print(*lines, sep='\n')
        print()

        print("\nself.Xxx_ctl = FileControl() classes currently open")
        print("===================================================\n")

        if self.play_ctl.metadata is not None:  # FileControl() always here
            print("\nLast file accessed - 'ffprobe' (self.play_ctl.metadata):")
            print("--------------------------------------------------------\n")
            for i in self.play_ctl.metadata:
                print(i, ":", self.play_ctl.metadata[i])

        if self.sam_ctl and self.sam_ctl.metadata is not None:
            print("\nLast file accessed - 'ffprobe' (self.sam_ctl.metadata):")
            print("-------------------------------------------------------\n")
            for i in self.sam_ctl.metadata:
                print(i, ":", self.sam_ctl.metadata[i])

        if self.fine_tune and self.fine_tune.time_ctl.metadata is not None:
            print("\nLast file accessed - 'ffprobe', "
                  "'(self.fine_tune.time_ctl.metadata):")
            print("-" * 68 + "\n")
            for i in self.fine_tune.time_ctl.metadata:
                print(i, ":", self.fine_tune.time_ctl.metadata[i])

        if self.mus_ctl and self.mus_ctl.metadata is not None:
            print("\nLast file accessed - 'ffprobe' (self.mus_ctl.metadata):")
            print("-------------------------------------------------------\n")
            for i in self.mus_ctl.metadata:
                print(i, ":", self.mus_ctl.metadata[i])

        if sql.ofb.blacks is not None:
            print("\nSQL Blacklisted songs")
            print("====================================\n")
            for i, entry in enumerate(sql.ofb.blacks):
                print(i, ":", entry)
            print("\nSQL Whitelist substitutes")
            print("====================================\n")
            for i, entry in enumerate(sql.ofb.whites):
                print(i, ":", entry)

        print("\nGLOBAL VARIABLES")
        print("====================================\n")
        print("START_DIR:", START_DIR, " | START_DIR.count(os.sep):",
              START_DIR.count(os.sep))
        print("PRUNED_DIR:", PRUNED_DIR, " | PRUNED_COUNT:", PRUNED_COUNT)
        print("TV_VOLUME:", TV_VOLUME, " | TV_SOUND:", TV_SOUND)
        print("TV_BREAK1:", TV_BREAK1, " | TV_BREAK2:", TV_BREAK2)
        print("REW_FF_SECS:", REW_FF_SECS, " | REW_CUTOFF:", REW_CUTOFF)

        print("pending_apply() debug print flag DPRINT_ON:", DPRINT_ON)
        print("self.get_pending_cnt_total():", self.get_pending_cnt_total())

        print("\nOpened Location dictionary that never changes LODICT:")
        print(LODICT)

        print("\nSQL - Sqlite3 Information")
        print("====================================\n")

        print("Sqlite3 Version:", sql.sqlite3.sqlite_version, "\n")
        rows = sql.con.execute("SELECT * FROM sqlite_master;").fetchall()
        for row in rows:
            print(row, "\n")

        # Need SQL version 3.22 for INTO option, current is 3.11
        #sql.con.execute("VACUUM INTO '/run/user/1000/mserve library.db'")

        if pav.pulse_is_working:
            ''' Fast method using pulse audio direct interface '''
            print("\nPulse Audio - sink_input_list (sound sources)")
            print("="*51, "\n")

            for sink in pav.pulse.sink_input_list():
                print("sink:", sink, sink.proplist['application.name'])

            print("\nPulse Audio - sink_list (sound cards)")
            print("="*51, "\n")

            for sink in pav.pulse.sink_list():
                print("sink:", sink)

            print("\nPulse Audio - source_list (recording)")
            print("="*51, "\n")

            for sink in pav.pulse.source_list():
                print("sink:", sink)

            print("\nPulse Audio - card_list.profile_list")
            print("="*51, "\n")

            card = pav.pulse.card_list()[0]
            print(card.profile_list)

            print("\nPulse Audio - pulse.server_info().default_sink_name")
            print("="*51, "\n")

            print(pav.pulse.server_info().default_sink_name)

        #print("\nFrames in self.lib_top (Toplevel) see toolkit.py list_widgets())")
        # Show frame widgets defined in library. Scan options are: "All", "Toplevel",
        # "Frame", "Label", "Button", "Treeview", "Scrollbar", "Menu", "Canvas" & "Other"
        #toolkit.list_widgets(self.lib_top, scan="Frame")  # Too much info. Needs work!

        print("\n\n=======================================")
        print("\nInformation Centre - self.info.dict[] =\n")
        print("--- KEY ---\t  --- VALUE ---\n")
        for key in self.info.dict:
            if isinstance(self.info.dict[key], list):
                entries = self.info.dict[key]  # pattern or trace
                if len(entries) == 1:  # If zero, drop down to print regular line
                    print("['" + key + "']\t:", self.info.dict[key][0])
                    continue
                elif len(entries) > 1:  # If zero, drop down to print regular line
                    print("['" + key + "']\t: list[VALUES] on lines below.")
                    for entry in entries:
                        print(entry)
                    continue
                    # Looks ok for regular list like ['source]' but not for ['text']:

                    # ['text']	: Begin playing song: Moon age Daydream
                    # Artist:	Guardians of the Galaxy
                    # Album:	Awesome Mix Vol. 1
                    # Track:	4/12	Date:	2014	Duration:	00:04:42
                    # ['patterns']	: None

            print("['" + key + "']\t:", self.info.dict[key])  # regular line

        print("\n=======================================\n")

        message.ShowInfo(self.lib_top, "DEBUG - mserve.py",
                         "DEBUG information written to Stdout (Standard Output)", 
                         thread=self.get_refresh_thread())
        self.info.cast("DEBUG information written to Stdout (Standard Output)")

    # ==============================================================================
    #
    #       MusicTree Processing - Top menu: SQL Music & SLQ History
    #
    # ==============================================================================

    def show_sql_music(self, sbar_width=12):
        """
            Open SQL Music Library treeview.
        """

        ''' SQL Music Table View already active? '''
        if self.mus_top_is_active is True:
            self.mus_top.lift()
            return

        music_dict = sql.music_treeview()
        """ Define Data Dictionary treeview columns for Music table
            ("column", "row_id"), ("heading", "Row ID"), ("sql_table", "Music"),
            ("column", "os_filename"), ("heading", "OS Filename"), ("sql_table", "Music"),
            ("column", "os_atime"), ("heading", "Access Time"), ("sql_table", "Music"),
            ("column", "os_mtime"), ("heading", "Mod Time"), ("sql_table", "Music"),
            ("column", "os_ctime"), ("heading", "Create Time"), ("sql_table", "Music"),
            ("column", "os_file_size"), ("heading", "File Size"), ("sql_table", "Music"),
            ("column", "artist"), ("heading", "Artist"), ("sql_table", "Music"),
            ("column", "album"), ("heading", "Album"), ("sql_table", "Music"),
            ("column", "song_name"), ("heading", "Song Name"), ("sql_table", "Music"),
            ("column", "release_date"), ("heading", "Release Date"), ("sql_table", "Music"),
            ("column", "original_date"), ("heading", "Original Date"), ("sql_table", "Music"),
            ("column", "genre"), ("heading", "Genre"), ("sql_table", "Music"),
            ("column", "seconds"), ("heading", "Seconds"), ("sql_table", "Music"),
            ("column", "duration"), ("heading", "Duration"), ("sql_table", "Music"),
            ("column", "play_count"), ("heading", "Play Count"), ("sql_table", "Music"),
            ("column", "track_number"), ("heading", "Track Number"), ("sql_table", "Music"),
            ("column", "rating"), ("heading", "Rating"), ("sql_table", "Music"),
            ("column", "lyrics"), ("heading", "Lyrics"), ("sql_table", "Music"),
            ("column", "time_index"), ("heading", "Time Index"), ("sql_table", "Music"),

        """

        # Note: Metadata may be none for artist, album, song_name, genre, etc.
        columns = ["os_filename", "track_number", "row_id", "os_atime",
                   "os_file_size", "artist", "album", "song_name", "lyrics", "genre"]
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
        master_frame = tk.Frame(self.mus_top, bg="olive", relief=tk.RIDGE)
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

        ''' Create Treeview item list with all songs. '''
        dtb = message.DelayedTextBox(title="Building SQL Music Table View",
                                     toplevel=self.mus_top, width=1000)
        self.populate_mus_tree(dtb)
        dtb.close()

        ''' Treeview Buttons '''
        frame3 = tk.Frame(master_frame, bg="Blue", bd=2, relief=tk.GROOVE,
                          borderwidth=g.BTN_BRD_WID)
        frame3.grid_rowconfigure(0, weight=1)
        frame3.grid_columnconfigure(0, weight=0)
        frame3.grid(row=1, column=0, sticky=tk.NW)

        ''' ✘ Close Button ✘ ✔ '''
        self.mus_top.bind("<Escape>", self.mus_close)
        self.mus_top.protocol("WM_DELETE_WINDOW", self.mus_close)
        self.mus_view_btn1 = tk.Button(frame3, text="✘ Close",
                                       width=g.BTN_WID - 2, command=self.mus_close)
        self.mus_view_btn1.grid(row=0, column=0, padx=2)
        self.tt.add_tip(self.mus_view_btn1,
                        "Close backups view but bserve remains open.", anchor="nw")

        ''' “🗑” U+1F5D1 (trash can) - Missing Metadata '''
        self.mus_view_btn2 = tk.Button(
            frame3, text="🗑 Missing Metadata", width=g.BTN_WID, command=self.missing_metadata)
        self.mus_view_btn2.grid(row=0, column=1, padx=2)
        self.tt.add_tip(self.mus_view_btn2, "Song never played in mserve.", anchor="nw")

        ''' 🗑 Missing Lyrics '''
        self.mus_view_btn3 = tk.Button(
            frame3, text="🗑 Missing Lyrics", width=g.BTN_WID - 1, command=self.missing_lyrics)
        self.mus_view_btn3.grid(row=0, column=2, padx=2)
        self.tt.add_tip(self.mus_view_btn3,
                        "Lyrics have not be scraped from websites.", anchor="nw")

        ''' 🗑 Lyrics UnSynced '''
        self.mus_view_btn4 = tk.Button(
            frame3, text="🗑 Lyrics UnSynced", width=g.BTN_WID - 1, command=self.unsynchronized)
        self.mus_view_btn4.grid(row=0, column=3, padx=2)
        self.tt.add_tip(self.mus_view_btn4,
                        "Lyric score not time synchronized.", anchor="ne")

        ''' 🔍 Text Search '''
        self.mus_view_btn5 = tk.Button(frame3, text="🔍  Text Search",
                                       width=g.BTN_WID - 2, command=self.mus_text_search)
        self.mus_view_btn5.grid(row=0, column=4, padx=2)
        self.tt.add_tip(self.mus_view_btn5,
                        "Refresh view, removing any filters", anchor="ne")

        '''  🖸 (1f5b8) - Update Metadata '''
        self.mus_view_btn6 = tk.Button(frame3, text="🖸  Update Metadata",
                                       width=g.BTN_WID, command=self.missing_artwork)
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

    def populate_mus_tree(self, delayed_textbox):

        """ Stuff SQL header rows into treeview
        """

        sql.cursor.execute("SELECT * FROM Music INDEXED BY OsFileNameIndex\
                           ORDER BY OsFileName")
        rows = sql.cursor.fetchall()
        self.insert_view_lines(self.mus_view, rows, delayed_textbox)

    def mus_text_search(self):
        """ Search all treeview columns for text string """
        if self.mus_search:
            self.mus_search.close()

        self.mus_search = toolkit.SearchText(
            self.mus_view, find_str=None, tt=self.tt)
        self.mus_search.find()

    def missing_metadata(self):
        """ Uses string search function for song_name is None """
        if self.mus_search:
            self.mus_search.close()

        self.mus_search = toolkit.SearchText(
            self.mus_view, column='song_name', find_str='', find_op='==')
        self.mus_search.find_column()  # Find song_name == None

        # Popup row count and total file sizes
        self.tree_summary(self.mus_view, title="Songs not played yet")

    def missing_lyrics(self):
        """ Find Songs that have no lyrics (no webscrape has been done)
        """
        if self.mus_search:
            self.mus_search.close()

        self.mus_search = toolkit.SearchText(
            self.mus_view, find_str='callback', callback=self.missing_lyrics_callback)
        self.mus_search.find_callback()

        # Popup row count and total file sizes
        self.tree_summary(self.mus_view, title="Songs with no Lyrics")

    def missing_lyrics_callback(self, values):
        """ Find Songs that have no lyrics (no webscrape has been done)

            If Treeview value is u'None' for song name so no lyrics anyway
            and return false.
        """
        song_name = self.mus_view.column_value(values, 'song_name')
        if song_name == u'None':
            return False  # Treeview value is u'None' for song name so no lyrics

        os_filename = self.mus_view.column_value(values, 'os_filename')
        lyrics, _time_index = sql.get_lyrics(os_filename)
        if lyrics is not None:
            return False  # Lyrics are non-blank.

        return True  # Song with metadata (song_name) has no lyrics.

    def unsynchronized(self):
        """ Find songs that have no time index (lyric score not synchronized)
        """
        if self.mus_search:
            self.mus_search.close()

        self.mus_search = toolkit.SearchText(
            self.mus_view, find_str='callback', callback=self.unsynchronized_callback)
        self.mus_search.find_callback()

        # Popup row count and total file sizes
        self.tree_summary(self.mus_view, title="Lyrics not synchronized")

    def unsynchronized_callback(self, values):
        """ Find Songs that have have lyrics but no time_index

            If Treeview value is u'None' for song name so no lyrics just return false.
            If lyrics is None, then no need to test for time index just return false.
        """
        song_name = self.mus_view.column_value(values, 'song_name')
        if song_name == u'None':
            return False  # Treeview value is u'None' for song name so no lyrics

        os_filename = self.mus_view.column_value(values, 'os_filename')
        lyrics, time_index = sql.get_lyrics(os_filename)

        if lyrics is None:
            return False  # Lyrics haven't been scraped so skip time check

        if time_index is not None:
            return False  # Time index is non-blank.

        return True  # Song with metadata (song_name) and lyrics has no time_index.

    def missing_artwork(self):
        """ Find Songs that have no artwork and update metadata
            Lengthy process so get permission to proceed.
            Updates file last access time which needs to be reversed.
            Uses mus_ctl() class to verify file exists and read metadata so only
                one instance of SQL Music Table View can be opened at once.
        """
        if self.mus_search:
            self.mus_search.close()

        answer = message.AskQuestion(
            self.mus_top, thread=self.get_refresh_thread(),
            title="Songs with no Artwork confirmation - mserve", confirm='no',
            text="Every song file will be read which will take awhile.\n" +
                 "Missing metadata in SQL Music Table will be updated.\n" +
                 "Songs with no artwork are displayed.\n\n" +
                 "Do you want to perform this lengthy update?")

        if answer.result != 'yes':
            return

        self.mus_ctl = FileControl(self.lib_top, self.info)  # Class to get metadata

        self.meta_scan = encoding.MetaScan(self.mus_top, self.get_refresh_thread())
        self.meta_scan_dtb = message.DelayedTextBox(title="SQL Music Table Scan",
                                                    toplevel=self.mus_top, width=1000)

        self.mus_search = toolkit.SearchText(
            self.mus_view, find_str='callback', callback=self.missing_artwork_callback)
        self.mus_search.find_callback()
        self.meta_scan_dtb.close()  # Close delayed text box
        # TODO: no records found message and reset filter
        text = "Total scanned:      " + "{:,}".\
            format(self.meta_scan.total_scanned) + "\n" + \
            "Missing artwork:    " + "{:,}".\
            format(self.meta_scan.missing_artwork) + "\n" + \
            "Found artwork:      " + "{:,}".\
            format(self.meta_scan.found_artwork) + "\n" + \
            "Metadata updated:   " + "{:,}".\
            format(self.meta_scan.meta_data_updated) + "\n" + \
            "Metadata unchanged: " + "{:,}".\
            format(self.meta_scan.meta_data_unchanged) + "\n\n" + \
            "Click 'OK' to close. Then reload window for metadata refresh.\n"

        title = "Update Metadata & Metadata Summary"
        message.ShowInfo(self.mus_top, title, text, 
                         thread=self.get_refresh_thread())
        self.info.fact(title + "\n\n" + text)

    def missing_artwork_callback(self, values):
        """ Find Songs that have no artwork and update metadata
            sql.update_metadata() is called by get_ffprobe_metadata(os_filename)
            The .CheckArtwork() function will call self.refresh_play_top()
            
            REMINDER:
            self.meta_scan = encoding.MetaScan(self.mus_top, self.get_refresh_thread())
            self.meta_scan_dtb = message.DelayedTextBox(title="SQL Music Table Scan",
                                                    toplevel=self.mus_top, width=1000)

        :param values: mus_view.tree values for current row being processed
        :return: True if artwork exists, False if not
        """

        ''' Reading through filenames in mus_view.tree which also has music ID '''
        os_filename = self.mus_view.column_value(values, 'os_filename')
        self.mus_ctl.new(PRUNED_DIR + os_filename)  # get metadata
        if self.mus_ctl.invalid_file:
            # Not a valid music file
            return False
        result = self.update_sql_metadata(self.mus_ctl)
        # Update SQL metadata columns of Music Table using OsFileName key
        self.meta_scan_dtb.update(os_filename)  # Refresh screen with song file name
        self.meta_scan.ChangedCounts(result)

        has_art = self.meta_scan.CheckArtwork(self.mus_ctl.metadata)
        self.mus_ctl.close()  # close filename and reset last access time
        return has_art

    # noinspection PyUnusedLocal

    def mus_close(self, *args):
        self.pretty_close()  # Drill down may be open from create_window()
        last_geometry = monitor.get_window_geom_string(
            self.mus_top, leave_visible=False)
        monitor.save_window_geom('sql_music', last_geometry)
        self.tt.close(self.mus_top)  # Close tooltips under top level
        self.mus_top_is_active = False
        self.mus_top.destroy()
        self.mus_search = None
        self.meta_scan = None
        self.meta_scan_dtb = None


    def show_sql_hist(self, sbar_width=12):
        """
            Open SQL History treeview. Patterned after show_sql_music()
        """

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
        # Note: Metadata may be none for artist, album, song_name, genre, etc.
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
        master_frame = tk.Frame(self.his_top, bg="olive", relief=tk.RIDGE)
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
        frame3 = tk.Frame(master_frame, bg="Blue", bd=2, relief=tk.GROOVE,
                          borderwidth=g.BTN_BRD_WID)
        frame3.grid_rowconfigure(0, weight=1)
        frame3.grid_columnconfigure(0, weight=0)
        frame3.grid(row=1, column=0, sticky=tk.NW)

        ''' ✘ Close Button ✘ ✔ '''
        self.his_top.bind("<Escape>", self.his_close)
        self.his_top.protocol("WM_DELETE_WINDOW", self.his_close)
        self.his_view_btn1 = tk.Button(frame3, text="✘ Close",
                                       width=g.BTN_WID - 2, command=self.his_close)
        self.his_view_btn1.grid(row=0, column=0, padx=2)
        self.tt.add_tip(self.his_view_btn1,
                        "Close backups view but bserve remains open.", anchor="nw")

        ''' Configuration Rows '''
        self.his_view_btn2 = tk.Button(
            frame3, text="🔍 Configuration Rows", width=g.BTN_WID + 2,
            command=self.his_configuration_rows)
        self.his_view_btn2.grid(row=0, column=1, padx=2)
        self.tt.add_tip(self.his_view_btn2, "Song never played in mserve.", anchor="nw")

        ''' “🗑” U+1F5D1 (trash can) - 🗑 Missing Lyrics '''
        self.his_view_btn3 = tk.Button(
            frame3, text="🗑 Missing Lyrics", width=g.BTN_WID - 1, command=self.his_missing_lyrics)
        self.his_view_btn3.grid(row=0, column=2, padx=2)
        self.tt.add_tip(self.his_view_btn3,
                        "Lyrics have not be scraped from websites.", anchor="nw")

        ''' 🗑 Lyrics UnSynced '''
        self.his_view_btn4 = tk.Button(
            frame3, text="🗑 Lyrics UnSynced", width=g.BTN_WID - 1, command=self.his_unsynchronized)
        self.his_view_btn4.grid(row=0, column=3, padx=2)
        self.tt.add_tip(self.his_view_btn4,
                        "Lyric score not time synchronized.", anchor="ne")

        ''' 🔍 Text Search '''
        self.his_view_btn5 = tk.Button(frame3, text="🔍  Text Search",
                                       width=g.BTN_WID - 2, command=self.his_text_search)
        self.his_view_btn5.grid(row=0, column=4, padx=2)
        self.tt.add_tip(self.his_view_btn5,
                        "Refresh view, removing any filters", anchor="ne")

        '''  🖸 (1f5b8) - Apply Metadata '''
        self.his_view_btn6 = tk.Button(frame3, text="🖸  Apply Metadata",
                                       width=g.BTN_WID - 2, command=self.his_text_search)
        self.his_view_btn6.grid(row=0, column=5, padx=2)
        self.tt.add_tip(self.his_view_btn6,
                        "Read song files for metadata.", anchor="ne")

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
        """ Stuff SQL header rows into treeview
            TODO: Review 'delayed_textbox'. If only used here, define it below.
        """

        #sql.cursor.execute("SELECT * FROM History INDEXED BY TimeIndex\
        #                   ORDER BY Time")
        sql.hist_cursor.execute("SELECT * FROM History")
        rows = sql.hist_cursor.fetchall()
        self.insert_view_lines(self.his_view, rows, delayed_textbox)

    def his_text_search(self):
        """ Search all treeview columns for text string """
        if self.his_search is not None:
            self.his_search.close()

        self.his_search = toolkit.SearchText(
            self.his_view, find_str=None, tt=self.tt)
        self.his_search.find()

    def his_configuration_rows(self):
        """ Uses string search function for song_name is None """
        if self.his_search is not None:
            self.his_search.close()

        self.his_search = toolkit.SearchText(
            self.his_view, column='music_id', find_str=0, find_op='==')
        self.his_search.find_column()

    def his_missing_lyrics(self):
        """ Find Songs that have no lyrics (no webscrape has been done)
        """
        if self.his_search is not None:
            self.his_search.close()

        self.his_search = toolkit.SearchText(
            self.his_view, find_str='callback', callback=self.his_missing_lyrics_callback)
        self.his_search.find_callback()

    def his_missing_lyrics_callback(self, values):
        """ Find Songs that have no lyrics (no webscrape has been done)

            If Treeview value is u'None' for song name so no lyrics anyway
            and return false.
        """
        song_name = self.his_view.column_value(values, 'song_name')
        if song_name == u'None':
            return False  # Treeview value is u'None' for song name so no lyrics

        os_filename = self.his_view.column_value(values, 'os_filename')
        lyrics, _time_index = sql.get_lyrics(os_filename)
        if lyrics is not None:
            return False  # Lyrics are non-blank.

        return True  # Song with metadata (song_name) has no lyrics.

    def his_unsynchronized(self):
        """ Find songs that have no time index (lyric score not synchronized)
        """
        if self.his_search is not None:
            self.his_search.close()

        self.his_search = toolkit.SearchText(
            self.his_view, find_str='callback', callback=self.his_unsynchronized_callback)
        self.his_search.find_callback()

    def his_unsynchronized_callback(self, values):
        """ Find Songs that have have lyrics but no time_index

            If Treeview value is u'None' for song name so no lyrics just return false.
            If lyrics is None, then no need to test for time index just return false.
        """
        song_name = self.his_view.column_value(values, 'song_name')
        if song_name == u'None':
            return False  # Treeview value is u'None' for song name so no lyrics

        os_filename = self.his_view.column_value(values, 'os_filename')
        lyrics, time_index = sql.get_lyrics(os_filename)

        if lyrics is None:
            return False  # Lyrics haven't been scraped so skip time check

        if time_index is not None:
            return False  # Time index is non-blank.

        return True  # Song with metadata (song_name) and lyrics has no time_index.

    # noinspection PyUnusedLocal
    def his_close(self, *args):
        self.pretty_close()  # Drill down may be open from create_window()
        last_geometry = monitor.get_window_geom_string(
            self.his_top, leave_visible=False)
        monitor.save_window_geom('sql_history', last_geometry)
        self.tt.close(self.his_top)  # Close tooltips under top level
        self.his_top_is_active = False
        self.his_top.destroy()
        self.his_search = None


    @staticmethod
    def insert_view_lines(dd_view, rows, delayed_textbox, test=None):
        """ Stuff SQL table rows into treeview
            Used for populate_mus_view and populate_his_view
            test used to omit specific rows from view.
            TODO: Review if 'self.refresh_play_top()' should be called
        """
        first_id = None
        #for i, sql_row in enumerate(rows):
        for sql_row in rows:
            row = dict(sql_row)
            sql_row_id = row['Id']  # Used for treeview iid ('Id' in both tables)

            if test is not None:
                if not test(row):
                    dd_view.attached[sql_row_id] = None  # Skipped
                    continue

            if first_id is None:
                first_id = sql_row_id  # Display first row when done

            # NOTE: dd_view.insert() has different parameters than tree.insert()!
            dd_view.insert("", dict(row), iid=sql_row_id, tags="unchecked")
            dd_view.attached[sql_row_id] = True  # row is attached to view

            ''' Delayed Text Box (dtb_line) displays only if lag experienced  '''
            if 'OsFileName' in row:
                dtb_line = row['OsFileName']  # SQL Music Table only
            else:
                dtb_line = "History time: " + sql.sql_format_date(row['Time'])

            if delayed_textbox.update(dtb_line):
                # delayed_textbox returns true only when visible otherwise
                # we are in quiet mode because not enough time has passed.
                #dd_view.tree.see(sql_row_id)  # Takes long time
                #dd_view.tree.update()
                pass

        # Display first row
        dd_view.tree.see(first_id)
        dd_view.tree.update()

    def his_button_3_click(self, event):
        """ Left button clicked to drill down on SQL History treeview line.
            Short click to retrieve and display gmail message header.
            Click and hold changes cursor to hand and allows column to
            be moved in the treeview.
        """
        self.view = self.his_view  # Set self.view to self.his_view or self.mus_view
        self.common_top = self.his_top
        self.common_button_3(event)

    def mus_button_3_click(self, event):
        """ Left button clicked to drill down on Backups treeview line.
        """
        self.view = self.mus_view  # Set self.view to self.his_view or self.mus_view
        self.common_top = self.mus_top
        self.common_button_3(event)

    def common_button_3(self, event):
        """ Right button clicked in SQL History or SQL Music treeview.

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
            else:
                title = "SQL History Table"
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

        ''' Place Window top-left of parent window with PANEL_HGT padding
            Lifted from: ~/mserve/encoding.py
        '''
        # Drop down menu to select headers, message body, daily backup
        self.right_click_menu(event, pretty)

    def right_click_menu(self, event, pretty):
        """ Right-clicked treeview line. Popup menu with options:

            - Display Message Metadata
            - Display Message
            - Download backup to working directory

        """

        menu = tk.Menu(root, tearoff=0)
        menu.post(event.x_root, event.y_root)

        # If lambda isn't used the command is executed as soon as popup
        # menu is displayed, not when option is chosen.
        menu.add_command(label="View Current Row", font=(None, g.MED_FONT),
                         command=lambda: self.view_sql_row(pretty))
        menu.add_command(label="Open in library", font=(None, g.MED_FONT),
                         command=lambda: self.view_library(pretty))
        menu.add_separator()

        if self.view == self.mus_view:
            menu.add_command(label="View Metadata", font=(None, g.MED_FONT),
                             command=lambda: self.view_metadata(pretty))
            menu.add_separator()

        menu.add_command(label="Ignore click", font=(None, g.MED_FONT),
                         command=lambda: self.close_right_click_menu(menu))

        menu.tk_popup(event.x_root, event.y_root)
        # Without lambda executes immediately, without _: invalid # parameters
        menu.bind("<FocusOut>", lambda _: self.close_right_click_menu(menu))

    def close_right_click_menu(self, menu):
        menu.unpost()
        # Remove tag 'red' - Reset color to normal
        toolkit.tv_tag_remove(self.view.tree, self.view_iid, "menu_sel")
        # May 14, 2023 - New tv_tag_remove() has error message if old tag doesn't exist
        #tags = self.view.tree.item(self.view_iid)['tags']  # Remove 'menu_sel' tag
        #if "menu_sel" in tags:
        #    tags.remove("menu_sel")
        #    self.view.tree.item(self.view_iid, tags=tags)

    def view_metadata(self, pretty):
        """ View Metadata

            pretty is discarded and new one is created

        """
        #print("pretty:", pretty.dict)
        filename = PRUNED_DIR + pretty.dict['OS Filename']
        # TODO: Verify last access time is not touched
        view_ctl = FileControl(self.lib_top, self.info)
        view_ctl.new(filename)

        pretty = sql.PrettyMeta(view_ctl.metadata)
        view_ctl.close()

        self.create_window("Metadata (ID3 Tags) - mserve", 1400, 975)
        pretty.scrollbox = self.scrollbox
        sql.tkinter_display(pretty)
        # Note self.scrollbox defined in multiple places, reduce in future

    def view_sql_row(self, pretty):
        """ View SQL - Music Table Row or History Table Row """
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
            TODO: When returning, collapse treeview parents forced to open.
        """
        # TODO: Check 'No Album' string
        music_id = pretty.dict['SQL Music Row Id']  # hist & music have same
        ''' SQL History has music_id with zero '''
        if music_id is 0:
            text = "Music Id 0 is not a real music song.\n" + \
                   "It cannot be opened in the Music Library."
            message.ShowInfo(view.toplevel, "Music Id 0 - mserve", text,
                             icon='warning', thread=self.get_refresh_thread())
            self.info.fact(text, 'warning', 'open')
            return

        d = sql.music_get_row(music_id)
        if d is None:
            text = "Music Id: '" + music_id + "' not found.\n" + \
                   "Reason unknown."
            message.ShowInfo(view.toplevel, "Music Id Not Found - mserve", text,
                             icon='error', thread=self.get_refresh_thread())
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
                   "No matching song Artist/Album/Title in Music Library."
            message.ShowInfo(view.toplevel, "No Match in Music Library - mserve", text,
                             icon='error', thread=self.get_refresh_thread())
            self.info.fact(text, 'error', 'open')
            print("mserve.py view_library() No match in Music Library:", music_id)
            return

    def create_window(self, title, width, height, top=None):
        """ Place Window top-left of parent window with PANEL_HGT padding
            Lifted from: ~/mserve/encoding.py

            TODO: Instead of parent guessing width, height it would be nice
                  to pass a maximum and reduce size when text box has extra
                  white space.

                  IDENTICAL to webscrape.py. Consider module.

        """
        if self.hdr_top is not None:
            self.hdr_top.lift()
            self.hdr_top.title(title)  # Maybe on different title
            return

        self.hdr_top = tk.Toplevel()
        self.hdr_top_is_active = True

        if top is None:
            top = self.common_top  # Tkinter Top Level Window - either mus_top or his_top
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
        frame1 = ttk.Frame(self.hdr_top, borderwidth=g.BTN_BRD_WID,
                           padding=(2, 2, 2, 2), relief=tk.RIDGE)
        frame1.grid(column=0, row=0, sticky=tk.NSEW)
        # 7 rows of text labels and string variables auto adjust with weight 1
        #        for i in range(7):
        #            frame1.grid_rowconfigure(i, weight=1)
        bs_font = (None, g.MON_FONTSIZE)  # bs = bserve, ms = mserve

        ''' Scrollable textbox to show selections / ripping status '''
        Quote = ("Retrieving SQL data.\n" +
                 "If this screen can be read, there is a problem.\n\n" +
                 "TIPS:\n\n" +
                 "\tRun in Terminal: 'm' and check for errors.\n\n" +
                 "\twww.pippim.com\n\n")

        # self.scrollbox = toolkit.CustomScrolledText(frame1, state="readonly", font=font)
        # TclError: bad state "readonly": must be disabled or normal
        # Text padding not working: https://stackoverflow.com/a/51823093/6929343
        self.scrollbox = toolkit.CustomScrolledText(
            frame1, state="normal", font=bs_font, borderwidth=15, relief=tk.FLAT)
        self.scrollbox.insert("end", Quote)
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
            view = self.his_view or self.mus_view

        """

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
        #thread = self.get_refresh_thread()
        message.ShowInfo(view.toplevel, title, text, 
                         thread=self.get_refresh_thread())

    # noinspection PyUnusedLocal
    def pretty_close(self, *args):
        if self.hdr_top is None:
            return
        self.tt.close(self.hdr_top)  # Close tooltips under top level
        self.scrollbox.unbind("<Button-1>")
        self.hdr_top_is_active = False
        self.hdr_top.destroy()
        self.hdr_top = None
        if self.view_iid is None:
            return  # We clicked on heading not treeview row

        # Reset color to normal in treeview line
        toolkit.tv_tag_remove(self.view.tree, self.view_iid, "menu_sel")
        # May 14, 2023 - New tv_tag_remove() has error message if old tag doesn't exist
        #tags = self.view.tree.item(self.view_iid)['tags']  # Remove 'menu_sel' tag
        #if "menu_sel" in tags:
        #    tags.remove("menu_sel")
        #    self.view.tree.item(self.view_iid, tags=tags)


    def rip_cd(self):
        """ Rip CD using libdiscid, MusicBrainzNGS, CoverArtArchive.org,
            images copied from clipboard and mutagen.
        """

        if encoding.RIP_CD_IS_ACTIVE:
            messagebox.showinfo(title="Rip CD Error",
                                message="Rip CD function is already running!",
                                parent=self.lib_top)
            ''' lift toplevel .ShowInfo '''
            self.rip_cd_class.cd_top.focus_force()  # Get focus
            self.rip_cd_class.cd_top.lift()  # Raise in stacking order
            return

        # TODO: Spinning music player works when self.refresh_play_top() isn't passed:
        # Loop forever giving 30 fps control to parent
        # self.lib_top.after(33, self.cd_run_to_close)
        self.rip_cd_class = encoding.RipCD(self.lib_top, self.tt, LODICT)
        return

    def write_playlist_to_disk(self, ShowInfo=True):
        """ Save Favorites using save_last_selections. Also saves current song ndx.
            if self.playlists.name used, then write to SQL Playlist Record instead.

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

        if self.playlists.name is not None:
            # June 19, 2023 - Below wasn't working (perhaps clicked before saving?)
            #   Granular additions are now done in pending_apply() function where
            #   song duration is calculated.
            self.playlists.act_count = len(self.playlists.act_id_list)
            self.playlists.act_size = self.lib_top_totals[8]
            # TODO: Total Music duration hasn't been calculated yet for
            #       self.playlists.act_secs.  FIXED June 19, 2023.
            self.playlists.save_playlist()  # act_id_list already up to date
            # June 19, 2023 - interesting previously act_id_list updating live
        else:
            self.save_last_selections()

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
                             thread=self.get_refresh_thread())
            self.info.cast(title + "\n\n" + text)

    def save_last_selections(self):

        """ Save to ~/.../mserve:
                last_location    = 'iid' in location master

            Save settings to disk to ~/.../mserve/L999/xxx_xxx
                last_open_states = Artist/Album expanded/collapsed states
                last_playlist    = songs selected for playing in user order
                last_song_ndx    = pointer into playlist to continue playing

        """

        global LODICT, START_DIR

        if self.playlists.name is not None:
            print("mserve.py save_last_selection() serious ERROR:" +
                  " playlists.name should be blank:", self.playlists.name)
            return

        ''' If self.saved_selections not populated, grab all checked songs 

        REMOVE OLD CODE: self.saved_selections are updated by pending_apply()

        if len(self.saved_selections) == 0:
            self.saved_selections = self.lib_tree.tag_has("songsel")
            # BUG June 25, 2023. Above could be cause:
            # Favorites were resorted into alphabetical order after working
            # in L003 and then opened L004. Had also closed play_top before
            # exiting. Not sure which actually caused bug.
            print("mserve.py save_last_selection() WARNING: Saving " +
                  "Favorites in alphabetical order")
        '''

        ''' Save expanded/collapsed state of Artists & Albums '''
        self.lib_tree_open_states = self.get_all_open_states()
        with open(lc.FNAME_LAST_OPEN_STATES, "wb") as f:
            pickle.dump(self.lib_tree_open_states, f)  # Save open states

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
            return  # June 25, 2023 - Added return

        ''' Two songs needed to save, next startup uses previous save '''
        if len(self.saved_selections) < 2:
            print("mserve.py save_last_selection() WARNING: Need at least " +
                  "two songs to save favorites.")
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

    def get_all_open_states(self):
        """ 
        Get expanded/collapsed state (opened/closed) of lib_tree Artists & Albums
        Return list of tuples. Where each tuple contains:
            (opened 0/1, artist or album name, tag with u'Artist' or u'Album')

        Revised: June 24, 2023 - Was storing both the open and close states:
            22028 Jun 24 09:49 last_open_states
        Significant performance boost by storing just the open states:
              912 Jun 24 10:19 last_open_states

        :return open_list: [(opened, text, tag), (opened, text, tag), ... ()]
        """
        open_list = list()

        for Artist in self.lib_tree.get_children():  # Process artists
            self.append_open_state(Artist, open_list)  # Append opened, text, tag
            for Album in self.lib_tree.get_children(Artist):  # Process albums
                self.append_open_state(Album, open_list)  # Album text

        return open_list

    def get_open_state(self, Id):
        """ 
        Get expanded/collapsed state (opened/closed) of one Artist or Album:
            (opened 0/1, artist or album name, tag with u'Artist' or u'Album')
        :return tuple: (opened, text, tag)
        """
        item = self.lib_tree.item(Id)
        return item['open'], item['text'], item['tags'][0]  # First tag only

    def append_open_state(self, Id, open_states_list):
        """ open_states_states list is mutable. Append when Artist/Album open """
        opened, text, tag = self.get_open_state(Id)
        if opened == 1 or opened is True:
            open_states_list.append(tuple((1, text, tag)))

    def apply_all_open_states(self, open_states):
        """         
        Set expanded/collapsed state (opened/closed) of lib_tree Artists & Albums
        :param open_states: List of tuples [(opened, text, tag),... ()]
        """
        for Artist in self.lib_tree.get_children():  # Read all artists
            self.apply_open_state(Artist, open_states)
            for Album in self.lib_tree.get_children(Artist):  # Read all albums
                self.apply_open_state(Album, open_states)

    def apply_open_state(self, Id, open_states_list):
        """ Set the expanded/collapsed indicators (chevrons) for a single
            artist or album.
        """
        opened, text, tag = self.get_open_state(Id)  # lib_tree fields
        ''' Create tuple for search into storage open states list '''
        test_open = tuple((1, text, tag))  # tag=just "Artist" or "Album"
        if test_open in open_states_list:
            self.lib_tree.item(Id, open=True)

    def load_last_selections(self):

        """ Load last playlist from ~/.../mserve/L999/last_playlist
            Load last open states from ~/.../mserve/L999/last_open_states
            Playlist sorted by last order shuffled. (self.saved_selections)
            Begin playing with song we left off at. (self.ndx)
            Mark selected (checkbox) songs in lib_tree.
        """

        global LODICT  # Never change LODICT after startup!

        self.saved_selections = []  # Songs selected for playing
        self.filtered_selections = list(self.saved_selections)

        if NEW_LOCATION:
            ''' If parameter 1 is for random directory, we have no last location
                Variables have been set to null. Remove 'm' splash screen.
            '''
            if self.splash_toplevel:
                self.splash_toplevel.withdraw()  # Remove splash screen
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
        #self.playlist_paths = []  # Song paths with "songsel" tag sorted by playlist order
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
                    print('Not found:', song)
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

        # Keep host awake if necessary
        if LODICT.get('activecmd', "") is not "":
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
            # print('Continue playing with song#:',self.ndx)
            self.play_selected_list()

    def clear_all_checks_and_opened(self):
        """ Called from self.pending_reset() and self.playlists.apply_callback()
        """
        ext.t_init('Apply totals to Artists & Albums + set checkbox')
        self.lib_tree_open_states = []
        for Artist in self.lib_tree.get_children():  # Read all Artists
            self.clear_item_check_and_open(Artist, force_close=True)
            for Album in self.lib_tree.get_children(Artist):  # Read all Albums
                self.clear_item_check_and_open(Album, force_close=True)
                for Song in self.lib_tree.get_children(Album):  # Read all Albums
                    self.clear_item_check_and_open(Song)
                    ''' Force Play No. blank - erase 'Adding' and 'Deleting' '''
                    self.lib_tree.set(Song, "Selected", "")
        ext.t_end('no_print')

    def clear_item_check_and_open(self, iid, force_close=False):
        """
        Clear checkbox and open state for single lib_tree item.
        :param iid: Treeview iid. Artists and Albums start with I.
        :param force_close: Processing an Artist or Album force open state to 0.
        :return:
        """
        item = self.lib_tree.item(iid)
        tags = item["tags"]
        is_open = False

        ''' Songs don't have an opened flag. Only Artists and Albums. '''
        if force_close:
            is_open = True if item['open'] is True or item['open'] == 1 else False

        update = False
        if "songsel" in tags:
            tags.remove("songsel")
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
        if is_open:
            update = True

        if update:
            self.lib_tree.item(iid, tags=tags)
            if is_open:
                self.lib_tree.item(iid, open=0)

    def set_all_checks_and_opened(self, opened=True):
        """ Called from self.pending_reset() and self.load_last_selections()
            June 15, 2023 - called from self.playlists.apply_callback().
            June 19, 2023 - opened=False for playlists which do not record
                open states for Artists ans Albums.
            June 24, 2023 - Playlists now supported, remove opened=True...

            BatchSelect() class for single update to parents' total selected.
            Before calling all items must be "unchecked" and "songsel" blanked.
            self.saved_selections and self.lib_tree_open_states must be set.
        """

        ''' Set opened states for Artists and Albums, play number for Songs '''
        bs = BatchSelect(self.lib_tree)

        not_selected_count = 0
        selected_count = 0
        ext.t_init('Set open/closed, add BatchSelect totals')
        for Artist in self.lib_tree.get_children():  # Read all artists
            if opened:
                self.apply_open_state(Artist, self.lib_tree_open_states)
                #print("self.lib_tree_open_states:", self.lib_tree_open_states)
            else:
                self.lib_tree.item(Artist, open=False)

            for Album in self.lib_tree.get_children(Artist):  # Read all albums
                if opened:
                    self.apply_open_state(Album, self.lib_tree_open_states)
                else:
                    self.lib_tree.item(Album, open=False)

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
                    if "songsel" in tags:
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
    #       MusicTree Processing - Play All Songs forever
    #
    # ==============================================================================

    def play_selected_list(self):
        """ Play songs in self.saved_selections[]. Define buttons:
                Close, Pause, Prev, Next, Commercial and Intermission
        """

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
            new_selections = self.lib_tree.tag_has("songsel")  # Alphabetical order
            if len(new_selections) != len(self.saved_selections):
                # Play new selections because old save out of date.
                self.saved_selections = list(new_selections)
            else:
                # We will be keeping current sorted selections.
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
        self.sam_top_is_active = False          # Sample middle 10 seconds / full
        #self.sync_top_is_active = False          # Fine-tune time index running?
        #self.sync_ffplay_is_running = False     # Playing and syncing?
        self.sync_paused_music = False          # Important this is False now
        #self.sync_changed_score = False         # For warning messages

        ''' Gather data to paint VU Meter
            TODO: June 6, 2023 - VU meters only work with nvi dia HDMI sound card source 
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
        self.set_title_suffix()
        self.play_top_title = "Playing " + self.title_suffix + " - mserve"
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
        self.play_frm.grid_columnconfigure(2, minsize=50)
        ms_font = (None, MON_FONTSIZE)

        ''' Artwork image spanning 5 rows '''
        self.art_width = 200
        self.art_height = 200
        self.play_no_art()  # Temporary starting image
        self.art_label = tk.Label(self.play_frm, borderwidth=0,
                                  image=self.play_current_song_art, font=ms_font)
        self.art_label.grid(row=0, rowspan=6, column=0, sticky=tk.W)
        self.art_label.bind("<Button-1>", self.pp_toggle)  # click artwork to pause/play
        # Leave empty row #5 for F3 frame (was row span=5)

        ''' Controls to resize image to fit frame '''
        self.play_frm.bind("<Configure>", self.on_resize)
        self.start_w = self.play_frm.winfo_reqheight()
        self.start_h = self.play_frm.winfo_reqwidth()

        ''' Current song number '''
        PAD_X = 5
        self.current_song_number = tk.StringVar()
        # New Short form with 'config_all_labels()' doesn't need variables
        # Apply color codes to buttons - See set_artwork_colors()
        # № (U+2116)
        tk.Label(self.play_frm, text="Playlist №", font=ms_font) \
            .grid(row=0, column=1, sticky=tk.W, padx=PAD_X)
        tk.Label(self.play_frm, text="", textvariable=self.current_song_number,
                 font=ms_font).grid(row=0, column=2, sticky=tk.W)

        ''' Current artist '''
        self.song_artist_var = tk.StringVar()
        tk.Label(self.play_frm, text="Artist:", font=ms_font) \
            .grid(row=1, column=1, sticky=tk.W, padx=PAD_X)
        tk.Label(self.play_frm, text="", textvariable=self.song_artist_var,
                 font=ms_font).grid(row=1, column=2, sticky=tk.W)

        ''' Current album '''
        self.song_album_var = tk.StringVar()
        tk.Label(self.play_frm, text="Album:", font=ms_font) \
            .grid(row=2, column=1, sticky=tk.W, padx=PAD_X)
        tk.Label(self.play_frm, text="", font=ms_font,
                 textvariable=self.song_album_var) \
            .grid(row=2, column=2, sticky=tk.W)

        ''' Current title '''
        self.current_song_path = ""
        self.song_title_var = tk.StringVar()
        tk.Label(self.play_frm, text="Title:", font=ms_font) \
            .grid(row=3, column=1, sticky=tk.W, padx=PAD_X)
        tk.Label(self.play_frm, text="", textvariable=self.song_title_var,
                 font=ms_font).grid(row=3, column=2, sticky=tk.W)

        ''' Progress of play '''
        self.current_progress = tk.StringVar()
        tk.Label(self.play_frm, text="Progress:", font=ms_font) \
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

        ''' self.play_frame3: Lyrics Frame - Title & Textbox with scrollbar
            Further divided into self.lyrics_frm and lyrics_score_box
            May 9, 2023 - Set row & column depending on frame size.
        '''

        self.play_frm.grid_columnconfigure(5, weight=1)
        self.play_frame3 = tk.Frame(self.play_frm)
        self.play_frame3.grid(row=0, rowspan=5, column=5,
                              padx=PAD_X, pady=PAD_X, sticky=tk.NSEW)
        self.play_frame3.grid_rowconfigure(1, weight=1)
        self.play_frame3.grid_columnconfigure(0, weight=1)

        # Define title frame top of play_F3
        self.lyrics_frm = tk.Frame(self.play_frame3)
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

        rounded_text = "Auto Scrolling"
        tt_text = "Auto Scrolling lyrics is active.\n" + \
                  "Click to scroll lyrics score manually."
        self.lyrics_panel_scroll_a_m =\
            self.create_scroll_button_and_tooltip(
                rounded_text, tt_text, ms_font=ms_font)

        rounded_text = "Time Scrolling"
        tt_text = "Lyrics line is highlighted using time index.\n" + \
                  "Click to scroll lyrics score manually."
        self.lyrics_panel_scroll_t_m =\
            self.create_scroll_button_and_tooltip(
                rounded_text, tt_text, ms_font=ms_font)

        rounded_text = "Manual Scroll"
        tt_text = "Manual lyrics score scrolling is active.\n" + \
                  "Click to auto scroll lyrics at 1.5x speed."
        self.lyrics_panel_scroll_m_a =\
            self.create_scroll_button_and_tooltip(
                rounded_text, tt_text, ms_font=ms_font)

        rounded_text = "Manual Scroll"
        tt_text = "Manual lyrics score scrolling is active.\n" + \
                  "Click to highlight lyrics using time index."
        self.lyrics_panel_scroll_m_t =\
            self.create_scroll_button_and_tooltip(
                rounded_text, tt_text, ms_font=ms_font)

        # Set four rounded rectangles to width of the longest rectangle to
        # prevent the longest rectangle right side showing under shorter ones
        self.set_max_dimensions()  # TODO rename to explicit

        # U+2630 in unicode and then U+22EE
        self.lyrics_panel_text = "0%, Blah blah, Line: 99 of: 99"

        # We give extra padding around label so RoundedRectangle has enough space
        self.lyrics_panel_label = tk.Label(
            self.lyrics_frm, borderwidth=BTN_BRD_WID, padx=7, pady=7,
            #text=self.lyrics_panel_text, relief=tk.GROOVE,
            text=self.lyrics_panel_text, font=ms_font)
        #self.lyrics_panel_label.grid(row=0, column=2, sticky=tk.NSEW)
        #self.lyrics_panel_label.grid_rowconfigure(0, weight=0)
        #self.lyrics_panel_label.grid_columnconfigure(0, weight=1)  # Note weight to stretch
        # Center labels in panel
        #self.lyrics_frm.update()
        self.lyrics_panel_label.place(relx=.6, rely=.5, anchor="center")

        self.lyrics_panel_last_line = 1                 # Appears in title string

        self.tt.add_tip(self.lyrics_panel_label, tool_type='label',
                        text="Replace me!", anchor="se")

        """ Define Hamburger rounded rectangle button and it's tooltip """
        rounded_text = u"☰"
        tt_text = "Left-clicking this hamburger icon brings up a\n" + \
                  "context sensitive menu for web scraping,\n" + \
                  "editing lyrics score and time indexes.\n\n" + \
                  "You can also right-click on the lyrics score\n" + \
                  "and the same context sensitive menu appears."
        self.lyrics_panel_hamburger = img.RoundedRectangle(
            self.lyrics_frm, rounded_text, 'black', 'white', ms_font=ms_font, 
            stretch=False, command=self.play_lyrics_fake_right_click)
        self.lyrics_panel_hamburger.grid(row=0, column=1, sticky=tk.E)
        self.tt.add_tip(self.lyrics_panel_hamburger, text=tt_text,
                        tool_type='canvas_button', anchor="se")

        ''' dummy label to give padding above and below row '''
        # We give extra padding around label so RoundedRectangle has enough
        # space. dummy is required because panel_label uses place to center
        # and doesn't permit padding with .place() command
        tk.Label(self.lyrics_frm, pady=14).grid(row=0, column=2, sticky='E')

        # Lyrics current state variables
        self.lyrics_scrape_pid = 0  # Process ID for web scrape
        self.lyrics_edit_is_active = False  # song lyrics being edited?
        self.lyrics_train_is_active = False  # basic training time index

        # undo=True provides support for Ctrl+Z and Ctrl+Shift+Z (Redo)
        self.lyrics_score_box = scrolledtext.ScrolledText(
            self.play_frame3, width=30, height=10, padx=3, pady=3, wrap=tk.WORD,
            insertbackground='white', font=ms_font, undo=True)
        self.lyrics_score_box.grid(row=1, column=0, sticky=tk.NSEW)
        self.lyrics_score_box.bind("<1>", self.play_lyrics_left_click)
        self.lyrics_score_box.bind("<3>", self.play_lyrics_right_click)
        self.lyrics_score_box.tag_config('highlight', background='black',
                                         foreground='white')

        """ build_play_btn_frm() replaces Hockey Commercial button with Rewind 
            button and replaces Intermission button with Fast Forward button. 
        """
        self.build_play_btn_frm()  # Placement varies if Hockey enabled

        ''' F4 Frame for Playlist (Chronology) '''
        self.F4 = tk.Frame(self.play_top, borderwidth=BTN_BRD_WID,
                           relief=tk.GROOVE)
        #self.F4.configure(background="Black")  # No effect
        self.F4.grid(row=8, column=0, sticky=tk.NSEW)
        self.play_frm.grid_rowconfigure(8, weight=1)
        self.F4.grid_rowconfigure(0, weight=1)
        self.F4.grid_columnconfigure(0, weight=1)  # Note weight to stretch
        self.build_chronology()  # Treeview in play order

        ''' Start at first playlist entry? '''
        if self.play_from_start:  # Caller can set starting index
            self.ndx = 0  # Control for current song 0 = 1st

        ''' Remove splash screen if we were called with it. '''
        self.play_top.bind("<FocusIn>", self.handle_play_top_focus)

        #if self.splash_toplevel:
        #    self.splash_toplevel.withdraw()  # Remove splash screen
        #root.update()  # Remove June 21, 2023 - Not needed
        #root.after(1000)  # Remove May 9, 2023. Why was a WHOLE SECOND here???

        ''' Retrieve location's last playing/paused status, song progress seconds '''
        resume = self.get_resume()
        chron_state = self.get_chron_state()

        ''' Start songs in a loop until signal to close '''
        while self.play_top_is_active:  # Loop whilst play window is open
            # May 29, 2023 - When resuming buttons do not have art color assigned
            # June 18, 2023 - play_one_song() now called from self.apply_playlists() too.
            if not self.play_one_song(resume=resume, chron_state=chron_state):
                print("Catastrophic error that can't be backed out of")
                self.play_close()  # Catastrophic error that can't be backed out of
                break
            # Fast clicking 'Next' means there is no song to close. Need to
            # research self.last_started, self.ndx and self.current_song_path=""
            self.play_ctl.close()  # Update last song's last access if > 50% played
            ''' Rebuild last song's access time in lib_tree update_lib'''
            resume = False  # We can only resume once
            chron_state = None  # Extra safety
            self.play_from_start = True  # Review variable usage... it's weird.

    def handle_play_top_focus(self, _event):
        """
            When lib_tree_play() or Playlists() windows are active,
            always stays above Music Library (lib_top).

            Credit: https://stackoverflow.com/a/44615104/6929343

        :param _event: Ignored
        :return: None
        """
        if not self.play_top_is_active:
            return  # Play window closed?

        ''' Synchronizing lyrics to time index controls music '''
        #if self.sync_top_is_active:
        #    self.fine_tune.top_lift()  # Raise window focus to top
        #if self.fine_tune and self.fine_tune.top_is_active:
        #    self.fine_tune.top_lift()  # Need name change....
        # Above steals focus and keyboard from other applications !
        if self.fine_tune and self.fine_tune.top_is_active:
            self.fine_tune_lift()

        ''' Sampling random song in lib_tree '''
        if self.sam_top_is_active:
            self.sample_song_lift()  # Raise in stacking order

    def fine_tune_lift(self):
        if self.fine_tune and self.fine_tune.top_is_active:
            ''' July 4, 2023 - All the problems started when code converted
                to new class FineTune(). Somehow TCL gets confused and lifts
                the window overtop of other applications, not just tkinter.
                The focus_force() steals keyboard from PyCharm, Gnome Terminal
            '''
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
                             thread=self.get_refresh_thread(),
                             title="Cannot toggle FF/Rewind Buttons Now - mserve")
            self.info.fact(quote)
            return

        self.play_hockey_allowed = not self.play_hockey_allowed  # Flip switch
        if self.play_hockey_allowed:
            self.view_menu.entryconfigure(2, label="Enable FF/Rewind buttons")
            self.info.fact("Enable FF/Rewind buttons")
        else:
            self.view_menu.entryconfigure(2, label="Use TV Commercial buttons")
            self.info.fact("Use TV Commercial buttons")

        if not self.play_top_is_active:
            return

        self.tt.close(self.play_btn_frm)  # Remove old tooltip buttons in play_btn frame
        self.play_btn_frm.grid_forget()
        self.play_btn_frm.destroy()
        self.build_play_btn_frm()
        ''' Lift play_top to see new button frame '''
        self.play_top.lift()
        self.play_on_top = True

    def build_play_btn_frm(self):
        """ Create frame for play_top buttons.
            Dynamically create buttons depending on 'play_hockey_allowed' state.
        """

        ''' Frame for Buttons '''
        self.play_btn_frm = tk.Frame(self.play_top, bg="Olive",
                                     borderwidth=BTN_BRD_WID, relief=tk.GROOVE)
        self.play_btn_frm.grid(row=3, column=0, sticky=tk.NSEW)
        # Leave empty row #2 for F3 frame (was row=2)
        self.play_btn_frm.grid_rowconfigure(0, weight=1)
        self.play_btn_frm.grid_columnconfigure(0, weight=0)

        if self.play_hockey_allowed:
            button_list = ["Close", "Shuffle", "Prev", "Com", "PP", "Int", "Next", "Chron"]
        else:
            button_list = ["Close", "Shuffle", "Prev", "Rew", "PP", "FF", "Next", "Chron"]

        for col, name in enumerate(button_list):
            if name == "Close":
                """" Close Button ✘ """
                self.close_button = tk.Button(self.play_btn_frm, text="✘ Close",
                                              width=BTN_WID2 - 6,
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
                                                width=BTN_WID2 - 3, command=self.play_shuffle)
                self.shuffle_button.grid(row=0, column=col, padx=2, sticky=tk.W)
                self.tt.add_tip(self.shuffle_button, "Shuffle songs into random order.",
                                anchor="sw")
            elif name == "PP":  # TODO: Check current pp_state and dynamically format
                ''' Pause/Play Button '''
                self.pp_button = tk.Button(self.play_btn_frm, text=self.pp_pause_text,
                                           width=BTN_WID2 - 5, command=self.pp_toggle)
                self.pp_button.grid(row=0, column=col, padx=2)
                text = "Pause music, pause artwork and\nallow manual lyrics scrolling."
                self.tt.add_tip(self.pp_button, text, anchor="sw")
            elif name == "Prev":
                ''' Prev Track Button '''
                # U+1f844 🡄         U+1f846 🡆         U_1f808 🠈         I+1f80a 🠊
                # June 17, 2023: Change 🠈 to last track button emoji (u+23ee) ⏮
                self.prev_button_text = self.previous_text
                self.prev_button = \
                    tk.Button(self.play_btn_frm, text=self.prev_button_text, width=BTN_WID2 - 2,
                              command=lambda s=self: s.song_set_ndx('prev'))
                self.prev_button.grid(row=0, column=col, padx=2, sticky=tk.W)
                self.tt.add_tip(self.prev_button, "Play previous song.",
                                anchor="sw")
            elif name == "Next":
                ''' Next Track Button '''
                # BIG_SPACE = " "         # UTF-8 (2003) aka Em Space
                # June 17, 2023: Change 🠊 to next track button 23ED ⏭
                self.next_button = \
                    tk.Button(self.play_btn_frm, text=" Next ⏭ ", width=BTN_WID2 - 5,
                              command=lambda s=self: s.song_set_ndx('next'))
                self.next_button.grid(row=0, column=col, padx=2, sticky=tk.W)
                self.tt.add_tip(self.next_button, "Play next song in playlist.",
                                anchor="sw")
            elif name == "Com":
                ''' Hockey Commercial Button '''
                self.tt.close(self.com_button)  # Remove old tooltip from list
                # 📺 | television (U+1F4FA) @ Graphic
                #self.play_hockey_active = False  # U+1f3d2 🏒
                self.com_button = tk.Button(self.play_btn_frm, text="📺  Commercial",
                                            anchor=tk.CENTER,
                                            width=BTN_WID2 + 3, command=lambda
                                            s=self: s.start_hockey(TV_BREAK1))
                self.com_button.grid(row=0, column=col, padx=2, sticky=tk.W)
                self.tt.add_tip(self.com_button, "Play music for " +
                                sec_min_str(TV_BREAK1) + ".\n" +
                                "Turn down TV volume whilst playing.", anchor="sw")
            elif name == "Int":
                ''' Hockey Intermission Button '''
                self.int_button = tk.Button(self.play_btn_frm, text="🏒  Intermission",
                                            anchor=tk.CENTER,
                                            width=BTN_WID2 + 3, command=lambda
                                            s=self: s.start_hockey(TV_BREAK2))
                self.int_button.grid(row=0, column=col, padx=2, sticky=tk.W)
                self.tt.add_tip(self.int_button, "Play music for " +
                                sec_min_str(TV_BREAK2) + ".\n" +
                                "Turn down TV volume whilst playing.", anchor="se")
            elif name == "Rew":
                ''' Rewind Button -10 sec '''
                self.rew_button = tk.Button(self.play_btn_frm, text="⏪  -" + REW_FF_SECS + " sec",
                                            width=BTN_WID2 - 3, command=lambda
                                            s=self: s.song_rewind())
                self.rew_button.grid(row=0, column=col, padx=2, sticky=tk.W)
                self.tt.add_tip(self.rew_button, "Rewind song " + REW_FF_SECS +
                                " seconds back.", anchor="sw")
            elif name == "FF":
                ''' Fast Forward Button +10 sec'''
                self.ff_button = tk.Button(self.play_btn_frm, text="+" + REW_FF_SECS + " sec  ⏩",
                                           width=BTN_WID2 - 3, command=lambda
                                           s=self: s.song_ff())
                self.ff_button.grid(row=0, column=col, padx=2, sticky=tk.W)
                self.tt.add_tip(self.ff_button, "Fast Forward song " + REW_FF_SECS +
                                " seconds ahead.", anchor="se")
            elif name == "Chron":
                ''' Show/Hide Chronology (Playlist) toggle button (Frame 4) '''
                self.chron_is_hidden = False  # DO THIS ONCE?
                self.chron_button = tk.Button(
                    self.play_btn_frm, text="🖸 Hide Chronology",
                    width=BTN_WID2 + 5, command=lambda s=self: s.chron_toggle())
                self.chron_button.grid(row=0, column=col, padx=2, sticky=tk.W)
        
                # TODO: DRY - This text is duplicated in show/hide function
                text = "Hide the scrollable playlist below and\n" + \
                       "double the size of spinning artwork."
                self.tt.add_tip(self.chron_button, text, anchor="se")
            else:
                print("mserve.py build_play_btn_frm() Bad button name:", name)

        if self.pp_state is "Paused":  # Initially defined as if playing
            self.set_pp_button_text()  # Button text reflects match play/pause state

    def on_resize(self, event):
        """ Resize image and VU Meters when frame size changes """
        # images use ratio of original width/height to new width/height
        # OLD WAY: w_scale = float(event.width) / self.start_w
        h_scale = float(event.height) / self.start_h
        w_scale = h_scale  # It's a square!
        self.art_width = int(w_scale) - 6  # Border width, this is awkward
        self.art_height = int(h_scale) - 6  # play_spin_art

        # Quick fix for error:  ValueError: bad image size
        if self.art_width < 1:
            self.art_width = 1
        if self.art_height < 1:
            self.art_height = 1

        self.set_vu_meter_height()

        self.play_resized_art = self.play_original_art.resize(
            (self.art_width, self.art_height), Image.ANTIALIAS)
        self.play_current_song_art = ImageTk.PhotoImage(self.play_resized_art)

        # Sometimes 'pp_state' variable isn't defined yet, e.g. during init
        if hasattr(self, 'pp_state'):
            if self.pp_state is "Paused":
                # Recreate image to new size (doesn't resize in above line).
                self.show_paused_art()

    def set_vu_meter_height(self):
        # May 9, 2023 - self.art_height no longer suitable. Use five song info rows
        self.vu_meter_left.config(height=100)  # So title, progress, etc. get fresh start
        self.vu_meter_right.config(height=100)
        self.play_frm.update_idletasks()  # Artwork resize
        _x, _y, _width, height = self.play_frm.grid_bbox(1, 0, 1, 4)
        #print("height:", height, "_width:", _width)
        #print("self.art_height:", self.art_height)
        self.vu_height = height - 12  # Create some padding at top & bottom of vu meters
        if self.vu_height < 1:
            self.vu_height = 1

        self.vu_meter_left.config(height=self.vu_height)
        self.vu_meter_right.config(height=self.vu_height)
        # When stretching bar higher, the bottom will be black
        self.play_vu_meter_blank()          # Fill with self.theme_bg

    def move_lyrics_right(self):
        self.play_frm.grid_rowconfigure(5, weight=0)  # Lyrics Row will be gone now
        # May 9, 2023 - Reset for row 1, column 6 (1's based)
        self.play_frm.grid_columnconfigure(5, weight=1)
        self.play_frame3.grid(row=0, rowspan=5, column=5, sticky=tk.NSEW)
        self.play_frm.grid_rowconfigure(5, weight=0)  # Lyrics gone now
        # Define title frame top of play_F3
        self.lyrics_frm.grid(row=0, rowspan=1, column=0, sticky=tk.NSEW)
        # song info column narrow as possible for wide lyrics lines
        self.play_frm.grid_columnconfigure(2, minsize=50, weight=0)
        self.play_frm.update_idletasks()
        self.lyrics_on_right_side = True  # self.play_frm =

    def move_lyrics_bottom(self):
        # May 9, 2023 - Reset for row 6, column 2 (1's based)
        self.play_frm.grid_columnconfigure(5, weight=0)
        self.play_frame3.grid(row=5, rowspan=1, column=1, columnspan=4, sticky=tk.NSEW)
        self.play_frm.grid_rowconfigure(5, weight=5)  # Lyrics get more space
        # Define title frame top of play_F3
        self.lyrics_frm.grid(row=0, rowspan=1, column=0, sticky=tk.NSEW)
        # song info column wide as possible for wide lyrics lines
        self.play_frm.grid_columnconfigure(2, minsize=400, weight=1)
        self.play_frm.update_idletasks()
        self.lyrics_on_right_side = False

    def create_scroll_button_and_tooltip(self, rounded_text, tt_text, ms_font):
        """ Define rounded rectangle button and it's tooltip """

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


        # When paused music at 50%, even though ffplay closes need to
        # set volume to 100% because next load of ffplay inherits setting.
        if self.play_ctl.sink is not "":
            if self.play_ctl.state == "start":
                if fade_then_kill:
                    ''' a little debugging. each song start vol 25, 20, 8, 2, 1, 0... '''
                    hold_sink = (self.play_ctl.sink + '.')[:-1]
                    print("\nfade_then_kill - hold_sink:",
                          hold_sink, id(hold_sink), id(self.play_ctl.sink))
                    hold_pid = self.play_ctl.pid + 1 - 1
                    print("hold_pid:", hold_pid, id(hold_pid), id(self.play_ctl.pid))
                    curr_vol = pav.get_volume(hold_sink)
                    if curr_vol is not None:
                        hold_vol = curr_vol + 1 - 1  # Break reference to sinks_now
                        print("hold_vol:", hold_vol)
                        self.play_ctl.pid = 0  # Stop play_ctl from killing
                        pav.fade(hold_sink, hold_vol, 0.0, 1,
                                 ext.kill_pid_running, hold_pid)
                    else:
                        self.info.cast("wrapup_song(): Got None for volume on sink#: " +
                                       str(hold_sink))
                else:
                    self.play_ctl.stop()  # Note poll_fades is in outer loop.
            ''' July 9, 2023 - Doesn't matter anymore if volume down. '''
            #pav.set_volume(self.play_ctl.sink, 100)

        """
        # print('pp_toggle() has been called:', ext.h(time.time()))
        if not self.play_top_is_active:
            return  # Play window closed?

        ''' Synchronizing lyrics to time index controls music '''
        if self.fine_tune and self.fine_tune.top_is_active:
            #self.fine_tune.top_lift()  # Need name change....
            # Above steals focus and keyboard from other applications !
            self.fine_tune_lift()
            return
        #if self.sync_top_is_active:
        #    self.sync_time_index_lift()  # Raise window focus to top
        #    return

        if self.pp_state is "Playing":
            # maximum volume is usually 100% but 60% or so during hockey commercials
            ''' Use the new fade_then_stop() function 
            FAST CLICK PLAY THEN PAUSE:
            Illogically, last state is:	stop
            
            self.pp_toggle_fading_out = None    # Used to reverse fade
            self.pp_toggle_fading_in = None     # Used to reverse fade
            '''
            self.pp_toggle_fading_out = True
            if self.pp_toggle_fading_in:
                self.pp_toggle_fading_in = False
            pav.fade(self.play_ctl.sink, self.get_max_volume(), 25, .5,
                     finish_cb=self.pp_finish_fade_out)
            self.secs_before_pause = self.play_ctl.elapsed()  # Must call before .stop()
            self.pp_state = "Paused"  # Was Playing now is Paused
            self.set_pp_button_text()
            if self.play_hockey_active:  # Is TV hockey broadcast on air?
                set_tv_sound_levels(25, 100)  # Restore TV sound to 100%
        else:
            ''' Important: self.song_set_ndx() repeats some of below.
                           Check there when changing below.
            '''
            # Was paused so resume playing
            if self.play_hockey_active:
                set_tv_sound_levels(100, 25)  # Soften volume on tv to 25%
            self.current_song_t_start = time.time()
            elapsed = self.play_ctl.elapsed()  # Must call after .cont()
            ''' Can be reversing fade out from Pause the click to play
                A 1 second fade in when song already has 1 second fade in
                seems like volume starts right away after a second. 
            '''
            self.pp_toggle_fading_in = True
            if self.pp_toggle_fading_out:
                pav.fade(self.play_ctl.sink, 25, self.get_max_volume(), .5,
                         finish_cb=self.pp_finish_fade_in())
                self.pp_toggle_fading_out = False
            else:
                self.play_ctl.cont()
                pav.fade(self.play_ctl.sink, 25, self.get_max_volume(), .5)

            #pav.fade(self.play_ctl.sink, 25, self.get_max_volume(), 1)
            self.pp_state = "Playing"  # Was Paused now is Playing
            self.set_pp_button_text()

    def pp_finish_fade_out(self):
        """ Need def pp_finish_fade_in(self): to round out """
        if not self.pp_toggle_fading_out:
            print("pp_finish_fade_out(): pp_toggle_fading_out is FALSE")
            return  # Got cancelled and callback wasn't reversed

        self.pp_toggle_fading_out = False
        self.play_ctl.stop()

    def pp_finish_fade_in(self):
        """ Need def pp_finish_fade_in(self): to round out """
        if not self.pp_toggle_fading_in:
            print("pp_finish_fade_in(): pp_toggle_fading_in is FALSE")
            return  # Got cancelled and callback wasn't reversed

        self.pp_toggle_fading_in = False
        self.play_ctl.cont()

    def get_max_volume(self):
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
        if self.current_song_secs + float(REW_FF_SECS) + 5.0 > \
                float(self.play_ctl.DurationSecs):
            self.song_set_ndx('next')  # 15 seconds left so next song.
        else:
            start_secs = self.current_song_secs + float(REW_FF_SECS)
            self.song_ff_rew_common(start_secs)  # Restart 10 seconds later

    def song_ff_rew_common(self, start_secs):
        """ Shared function for for song_ff() and song_rew() functions """
        self.play_ctl.restart(start_secs)

        ''' a little debugging. each song start vol 25, 20, 8, 2, 1, 0... '''
        vol = pav.get_volume(self.play_ctl.sink)
        print("song_ff_rew_common() vol:", vol,
              "self.play_ctl.sink:", self.play_ctl.sink)
        #if vol and float(vol) != 100.0:
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

        message.ShowInfo(self.lib_top, text=quote, align='center', icon='error',
                         thread=self.get_refresh_thread(),
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
                         thread=self.get_refresh_thread(),
                         title="Failed to get Pulse Audio Sink - mserve")
        self.info.fact(quote, 'error', 'open')

        return False  # self.play_ctl.close() called after we return.

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
            2) Every 33ms play_to_end() function checks if song has ended.
            3) Seeing song has ended play_to_end calls queue_next_song()
            4) queue_next_song() aborts when self.song_set_ndx_just_run True

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
                # TODO: After 12 seconds, change text from "Previous" to "Restart"
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
            '''   F A S T   C L I C K I N G   '''
            # Restarting same song. Fake the last song to pass new tests
            if self.ndx == 0:
                self.last_started = 1  # On first so pretend next
            else:
                self.last_started = self.ndx - 1  # Pretend previous
        else:
            self.ndx = int(seq)  # Jump to index passed

        ''' Tell queue_next_song() not to increment self.ndx '''
        self.song_set_ndx_just_run = True  # self.ndx set, don't use 'Next'
        #self.current_song_path = ""

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
                    2) Songs for specific artist
                    3) Songs over 5 minutes long
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
                    ''' a little debugging. each song start vol 25, 20, 8, 2, 1, 0... '''
                    hold_sink = (self.play_ctl.sink + '.')[:-1]
                    print("\nfade_then_kill - hold_sink:",
                          hold_sink, id(hold_sink), id(self.play_ctl.sink))
                    hold_pid = self.play_ctl.pid + 1 - 1
                    print("hold_pid:", hold_pid, id(hold_pid), id(self.play_ctl.pid))
                    curr_vol = pav.get_volume(hold_sink)
                    if curr_vol is not None:
                        hold_vol = curr_vol + 1 - 1  # Break reference to sinks_now
                        print("hold_vol:", hold_vol)
                        self.play_ctl.pid = 0  # Stop play_ctl from killing
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
        if self.lyrics_scrape_pid is not 0:
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
            #self.fine_tune.top_lift()  # Need name change....
            # Above steals focus and keyboard from other applications !
            self.fine_tune_lift()
            return
        #if self.sync_top_is_active:
        #    self.sync_time_index_lift()  # Raise window focus to top
        #    # Popup message needed advising button is disabled
        #    # Make function: if check_sync_in_progress: return
        #    # Better yet, self.sync_top should remove all buttons on other
        #    #   windows!
        #    return

        ''' Want to end countdown? - second time button click '''
        if self.play_hockey_active:  # Already counting down?
            answer = message.AskQuestion(
                self.play_top, thread=self.get_refresh_thread(),
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
                # We don't want to update every 1/33rd second
                return
            self.play_hockey_remaining = remaining
            int_str = com_str = "🏒  Remaining: " + str(remaining)
        else:
            # All finished now repaint original hockey buttons
            com_str = "📺  Commercial"  # TODO: Make global constants
            int_str = "🏒  Intermission"  # E.G.  COM_BTN_STR
            if self.gone_fishing is not None:
                self.gone_fishing.close()
            self.gone_fishing = None  # So global close doesn't try
            ''' June 4, 2023 - comment out below because pp_toggle() does it '''
            #set_tv_sound_levels(25, 100, thread=self.play_vu_meter)
            # Restore TV sound

        self.com_button['text'] = com_str
        self.int_button['text'] = int_str

    # ==============================================================================
    #
    #       Play one song - Called on start up, then repeatedly for each new song.
    #
    # ==============================================================================

    def play_one_song(self, resume=False, chron_state=None, real_start=True):
        """ Play song from start. Called on startup and by next/prev/restart.

            When resume=True, use self.resume_state and self.resume_song_secs from
            SQL history record Type 'resume' Action <location iid> to override.

            param: real_start: If false parent is "refresh_play_top" which ran
                out of music to play.
        """

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
            return True  # self.play_ctl.close() called after we return.

        ''' Build full song path from song_list[] '''
        #list_index = int(iid)  # list_index variable reused couple pages down
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
        if self.last_started != self.ndx:  # Fast clicking Next button?
            return True  # self.play_ctl.close() called after we return.

        opened = self.lib_tree.item(album, 'open')
        if opened is not True:
            self.lib_tree.item(album, open=True)
            self.play_opened_album = True  # We opened album
        else:
            self.play_opened_album = False  # Album was already open

        '''   F A S T   C L I C K I N G   '''
        self.play_top.update_idletasks()
        pav.poll_fades()
        if self.last_started != self.ndx:  # Fast clicking Next button?
            return True  # self.play_ctl.close() called after we return.

        toolkit.tv_tag_add(self.lib_tree, iid, "play_sel")
        # May 16 2023 - New compact code
        #tags = self.lib_tree.item(iid)['tags']  # Append 'play_sel' tag
        #if "play_sel" not in tags:
        #    tags.append("play_sel")
        #    self.lib_tree.item(iid, tags=tags)
        self.lib_tree.see(iid)  # Ensure song visible

        '''   F A S T   C L I C K I N G   '''
        root.update()  # Do both lib_top & play_top updates
        pav.poll_fades()
        if self.last_started != self.ndx:  # Fast clicking Next button?
            return True  # self.play_ctl.close() called after we return.

        ''' Set current song # of: total song count '''
        self.current_song_number.set(str(self.ndx + 1) + " of: " +
                                     str(len(self.saved_selections)))

        '''   F A S T   C L I C K I N G   '''
        self.play_top.update_idletasks()
        pav.poll_fades()
        if self.last_started != self.ndx:  # Fast clicking Next button?
            return True  # self.play_ctl.close() called after we return.

        ''' Verify it's a real song - May want to do this after .see() '''
        if self.current_song_path is None or self.current_song_path is "":
            return True  # Treat like fast clicking Next button

        '''   D E C L A R E   N E W   S O N G   P A T H   '''
        self.play_ctl.new(self.current_song_path)
        if self.play_ctl.path is None:
            self.play_ctl.close()  # this caused failure but full reset needed.
            return True  # Treat like fast clicking Next button

        if self.play_ctl.invalid_file:
            print(self.play_ctl.metadata)
            self.corrupted_music_file(self.current_song_path)  # No blocking dialog box
            self.play_ctl.close()
            return False  # TODO: Restore screen? Play next? What to do now?

        if self.play_ctl.path is None:
            self.play_ctl.close()
            return True  # Treat like fast clicking Next button

        ''' Populate display with metadata using ffprobe '''
        ext.t_init("play_one_song - update_sql_metadata()")
        self.update_sql_metadata(self.play_ctl)  # Update SQL Music Table with metadata
        #global E_WIDTH
        E_WIDTH = 32
        # TODO: self.get_ffprobe_metadata() is called by missing_artwork()
        #       for every song. However .set() is only done here using meta
        self.song_artist_var.set(make_ellipsis(self.play_ctl.Artist, E_WIDTH))
        self.song_album_var.set(make_ellipsis(self.play_ctl.Album, E_WIDTH))
        self.song_title_var.set(make_ellipsis(self.play_ctl.Title, E_WIDTH))
        self.saved_DurationSecs = self.play_ctl.DurationSecs
        self.saved_DurationMin = tmf.mm_ss(self.saved_DurationSecs)
        ext.t_end('no_print')

        '''   F A S T   C L I C K I N G   '''
        self.play_top.update_idletasks()
        pav.poll_fades()
        if self.last_started != self.ndx:  # Fast clicking Next button?
            self.play_ctl.close()
            return True  # self.play_ctl.close() called after we return.

        ''' Get artwork from metadata with ffmpeg '''
        ext.t_init("set_artwork_colors()")
        self.set_artwork_colors()
        pav.poll_fades()
        if not self.play_top_is_active:
            return False  # self.play_ctl.close() called after we return.
        ext.t_end('no_print')

        '''   F A S T   C L I C K I N G   '''
        self.play_top.update_idletasks()
        pav.poll_fades()
        if self.last_started != self.ndx:  # Fast clicking Next button?
            # NOTE: Parent Artist/Album opened above is closed after return.
            self.play_ctl.close()
            return True  # self.play_ctl.close() called after we return.

        ''' Gather song lyrics to fill text box '''
        self.play_init_lyrics()

        '''   F A S T   C L I C K I N G   '''
        self.play_top.update_idletasks()
        pav.poll_fades()
        if self.last_started != self.ndx:  # Fast clicking Next button?
            # NOTE: Parent Artist/Album opened above is closed after return.
            self.play_ctl.close()
            return True  # self.play_ctl.close() called after we return.

        ''' Update playlist chronology (Frame 4) with short line = False '''
        self.play_chron_highlight(self.ndx, False)  # True = use short line
        if not self.play_top_is_active:
            return False  # self.play_ctl.close() called after we return.

        '''   F A S T   C L I C K I N G   '''
        self.play_top.update_idletasks()
        pav.poll_fades()
        if self.last_started != self.ndx:  # Fast clicking Next button?
            self.play_ctl.close()
            return True  # self.play_ctl.close() called after we return.

        self.current_song_secs = 0  # How much time played
        self.secs_before_pause = 0  # How much before paused

        ''' Hide chronology (playlist) to match last setting for location '''
        if chron_state and chron_state == "Hide":
            self.chron_is_hidden = False  # Fake hidden now then toggle to show
            self.chron_toggle()  # Toggle chronology between hidden and show

        ''' Start song with ffplay & Update tree view's last played time
            If resume is passed we are starting up or changing location 
        '''
        ''' June 18, 2023 - Default for music to be playing '''
        self.pp_state = "Playing"  # Is song_set_ndx() duplicating this?
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
            return True  # self.play_ctl.close() called after we return.

        ''' Start ffplay, get Linux PID and Pulseaudio Input Sink # '''
        self.play_ctl.start(start_secs, 0, 1, 0, TMP_CURR_SONG, dead_mode)
        # Limit 0. Fade in over 1 second, Fade out 0.
        self.current_song_t_start = time.time()  # For pp_toggle, whether resume or not

        if resume:
            ''' Restart Music from last session's save point. '''
            if self.resume_state == "Paused":  # Was resume saved as paused?
                pav.set_volume(self.play_ctl.sink, 25)
                self.pp_state = "Paused"  # Set Play/Pause status to paused
                self.set_pp_button_text()
                ''' a little debugging. each song start vol 25, 20, 8, 2, 1, 0... '''
                vol = pav.get_volume(self.play_ctl.sink)
                print("\nplay_on_song() - Resume Paused:", vol,
                      " | self.play_ctl.sink:", self.play_ctl.sink,
                      " | self.play_ctl.pid:", self.play_ctl.pid)
            else:
                ''' a little debugging. each song start vol 25, 20, 8, 2, 1, 0... '''
                vol = pav.get_volume(self.play_ctl.sink)
                print("\nplay_on_song() - Resume volume:", vol,
                      " | self.play_ctl.sink:", self.play_ctl.sink,
                      " | self.play_ctl.pid:", self.play_ctl.pid)
                #if vol and float(vol) != 100.0:
                if self.play_ctl.sink is not None:
                    pav.set_volume(self.play_ctl.sink, 100.0)

            self.play_update_progress(self.resume_song_secs)  # mm:ss of mm:ss
            self.play_paint_lyrics()  # paint window fields, set highlight
            self.play_lyrics_rebuild_title()  # Required for line # in title

            self.resume_state = None  # Make sure code doesn't run again
            self.resume_song_secs = None
        else:
            ''' a little debugging. each song start vol 25, 20, 8, 2, 1, 0... '''
            vol = pav.get_volume(self.play_ctl.sink)
            print("\nplay_one_song() Check Volume:", vol,
                  " | self.play_ctl.sink:", self.play_ctl.sink,
                  " | self.play_ctl.pid:", self.play_ctl.pid)
            #if vol and float(vol) != 100.0:  # hold_sink:
            if self.play_ctl.sink is not None:
                pav.set_volume(self.play_ctl.sink, 100.0)


        # update treeview display and position treeview to current song
        self.update_lib_tree_song(iid)


        ''' Remove 'M' splash screen when mserve.py was called by 'm'. '''
        if self.splash_toplevel:
            self.splash_toplevel.withdraw()  # Remove splash screen
            self.splash_toplevel = None

        if real_start:
            self.play_to_end()  # play song until end
            self.queue_next_song()  # Save Lyrics Index & set next song
        else:
            ''' refresh_play_top() is caller so return chain jacked '''
            #print("self.last_started:", self.last_started, "self.ndx:", self.ndx)
            #self.last_started = self.ndx  # ShowInfo waiting for OK click
            print("\nself.current_song_path:", self.current_song_path)
            self.play_to_end()  # Added July 9, 2023 fix skipping bug???

        self.play_ctl.close()  # Set last access time for song just finished

        return True

    def queue_next_song(self):
        #if self.current_song_path is not "":  # next/prev set new name?
        if not self.song_set_ndx_just_run:  # Song wasn't manually set
            # When training lyrics and clicking 'Next/Prev' buttons the
            # changes will be lost because save below isn't run.
            self.play_save_time_index()  # Save lyrics & time index
            self.song_set_ndx('next')  # Grab next song in playlist

        ''' Reset switch set earlier, or just now with self.song_set_ndx() '''
        self.song_set_ndx_just_run = False
        self.current_song_path = self.playlist_paths[self.ndx]


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
        """
        Play single song, refreshing screen 30 fps with refresh_play_top()

        Called from:
            play_one_song() to start a new song
            Indirectly called by refresh_play_top() when it calls play_one_song() 
                when song ends during long running process like update metadata
            pp_toggle() to resume song after pausing

        """
        while True:
            if self.killer.kill_now:
                # SIGTERM to shut down / reboot was received
                print('\nmserve.py play_to_end() closed by SIGTERM')
                self.close()
                return  # Not required because this point never reached.

            if not self.play_top_is_active:
                return  # Play window closing

            if self.last_started != self.ndx:  # Different song requested
                return  # self.song_set_ndx() used prev/next/restart

            if not self.play_ctl.check_pid():
                return  # Song ended naturally

            self.refresh_play_top()  # Rotate art, refresh vu meter

    def refresh_play_top(self):
        """
        Common code for updating graphics that can be called from anywhere
        Use this when stealing processing cycles from self.play_to_end()

        33 millisecond sleep gives 30 fps (frames per second) video speed.

        April 24, 2023 - Must return something so checks in message.py will
            know a function is being passed as valid "thread=..." parameter.
        """

        ''' Is system shutting down? '''
        if self.killer.kill_now:
            # SIGTERM to shut down / reboot was received
            print('\nmserve.py refresh_play_top() closed by SIGTERM')
            self.close()
            return False  # Not required because this point never reached.

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
            sleep = 50 - (int(time.time() - now))
            sleep = 1 if sleep < 1 else sleep   # Sleep minimum 1 millisecond
            self.fine_tune.top.after(sleep)           # Wait until lyric sync
            return False  # Looks like True causes animations to freeze

        ''' Set previous or restart into button text '''
        if self.prev_button_text == self.previous_text:
            if self.current_song_secs > float(REW_CUTOFF):
                self.prev_button_text = self.restart_text
                self.prev_button['text'] = self.prev_button_text
                self.tt.set_text(self.prev_button, "Restart song at beginning.")
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

            # Jun 20 2023 - Losing 5 ms on average see: self.info.test_tt()
            now = time.time()  # June 20, 2023 - Use new self.last_sleep_time
            sleep = SLEEP_PAUSED - int(now - self.last_sleep_time)
            sleep = sleep if sleep > 0 else 1  # Sleep minimum 1 millisecond
            self.last_sleep_time = now
            self.play_top.after(sleep)          # Wait until playing
            return True  # June 20, 2023 this was False. Don't know effect.

        ''' May 23, 2023 - Updating metadata takes 10 minutes for 5,000 songs.
                Current song would end before completion. Also a song can end
                when .ShowInfo is active. So play next song in list.
        '''
        self.play_ctl.check_pid()   # play_ctl class is omnipresent
        if self.play_ctl.pid == 0:  # Music has stopped playing
            self.play_ctl.close()   # Update last song's last access time
            self.queue_next_song()  # Queue up next song in list
            ''' Play next song with signal to return back here '''
            if not self.play_one_song(real_start=False):  # Start song & come back
                self.play_close()   # Catastrophic error that can't be backed out of
                print("Catastrophic error that can't be backed out of")
                return False  # search short cut def play_one_song
            ''' Return back to normal refresh_play_top() loop '''
            self.play_ctl.close()   # Update our song's last access time
            return True

        ''' Updated song progress and graphics for song that is playing '''
        self.play_update_progress()             # Update screen with song progress
        self.play_spin_art()                    # Rotate artwork 1°
        self.play_vu_meter()                    # Left & Right VU Meters
        self.play_paint_lyrics()                # Uses the lyrics time index
        if not self.play_top_is_active:
            return False                        # Play window closed so shutting down
        self.play_top.update()                  # Update artwork spinner & text

        # Jun 20 2023 - Losing 5 ms on average see: self.info.test_tt()
        now = time.time()  # June 20, 2023 - Use new self.last_sleep_time
        sleep = SLEEP_PAUSED - int(now - self.last_sleep_time)
        sleep = sleep if sleep > 0 else 1  # Sleep minimum 1 millisecond
        self.last_sleep_time = now
        self.play_top.after(sleep)              # Sleep until next 30 fps time
        return True

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
        # Two methods of displaying song progress. In future user can configure.
        if True is True:
            # FORMAT IS - hh:mm:ss of: hh:mm:ss
            self.current_progress.set(self.current_song_mm_ss_d +
                                      " of: " + self.saved_DurationMin)
        else:
            # FORMAT IS - 9999.9 seconds of: 9999.9
            self.current_progress.set(str('%.1f' % self.current_song_secs) +
                                      " seconds of: " + str(self.saved_DurationSecs))

    @staticmethod
    def update_sql_metadata(file_ctl):
        """ Legacy code crafted to new function June 28, 2023.
        """
        meta_update_succeeded = None
        if file_ctl.path.startswith(PRUNED_DIR):
            sql_key = file_ctl.path[len(PRUNED_DIR):]  # Remove prefix from filename
            # returns true if metadata changed and row updated
            meta_update_succeeded = \
                sql.update_metadata(
                    sql_key, file_ctl.Artist, file_ctl.Album, file_ctl.Title,
                    file_ctl.Genre, file_ctl.Track, file_ctl.Date,
                    file_ctl.DurationSecs, file_ctl.Duration)
        else:
            # Not really an error but needs more testing and enhancing
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
    #       MusicTree Processing - VU Meter
    #
    # ==============================================================================

    def play_vu_meter_blank(self):
        """
            Display blank VU Meters (Left and Right), when music paused.
            Previous dynamic display rectangles have already been removed.
        """
        self.play_vu_meter_blank_side(self.vu_meter_left,
                                      self.vu_meter_left_rectangle)

        self.play_vu_meter_blank_side(self.vu_meter_right,
                                      self.vu_meter_right_rectangle)

    def play_vu_meter_blank_side(self, canvas, rectangle):
        """
            Display one blank VU Meter (Left or Right), when music paused.
        """
        # Function to display single large rectangle
        x0, y0, x1, y1 = 0, 0, self.vu_width, self.vu_height
        canvas.coords(rectangle, x0, y0, x1, y1)
        canvas.create_rectangle(x0, y0, self.vu_width, y1,
                                fill=self.theme_bg,
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
    #       MusicTree Processing - Lyrics Score
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
        self.lyrics_frm = tk.Frame(self.play_frame3)
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
        song = ext.shell_quote(self.play_ctl.Title)     # and " in variables
        # 'Bob Seeger & The Silver Bullet Band' finds nothing, while just
        # 'Bob Seeger' finds 'Shakedown' song.
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
                             artist, song, "", 0, 0, 0.0, comment)
                self.info.fact("Begin scraping lyrics for song: " + song)
            except sqlite3.Error as er:
                print('SQLite error: %s' % (' '.join(er.args)))
                print("Exception class is: ", er.__class__)
                print('SQLite traceback: ')
                exc_type, exc_value, exc_tb = sys.exc_info()
                print(traceback.format_exception(exc_type, exc_value, exc_tb))
                ''' Move this error trapping into sql.py
                    Then remove: import sqlite3 
                            and: import trace 
                '''
                self.info.cast("sqlite3.ProgrammingError: " + artist, 'error', 'update')
                return

            sql.con.commit()
            # Aug 25 fudge parameter list to skip no_parameters()
            parm = '"' + artist + ' ' + song + '" ' + str(MusicId)
            ext_name = 'python webscrape.py ' + parm
            self.lyrics_scrape_pid = ext.launch_command(
                ext_name, toplevel=self.play_top)
        else:
            print('Last instance of webscrape is still running.')
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
                # We have to save the lyrics we just scraped from the web
                self.play_save_score_erase_time()
                self.lyrics_scrape_done = True
                self.play_lyrics_rebuild_title()
                self.info.fact("Lyrics scraped for: " + self.play_ctl.Title)
            else:
                return  # We are still fetching lyrics

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
                self.play_lyrics_see_ahead(rewind=rewind)

        self.lyrics_prev_line = self.lyrics_curr_line

        # Update 'Line: 99 of 99' in lyrics title bar (aka panel)
        self.lyrics_update_title_line_number(self.lyrics_curr_line)


    # ==============================================================================
    #
    #       MusicTree Processing - Basic time index
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

        #if not self.play_top_is_active or self.sync_top_is_active:
        #    return
        if not self.play_top_is_active or \
                self.fine_tune and self.fine_tune.top_is_active:
            return

        print('TRAIN LYRICS:', self.play_ctl.Artist, self.play_ctl.Album,
              self.play_ctl.Title)

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

            Need option for "Lyrics horribly wrong. Get new ones"

        NOTE: May 21, 2023 - This is where lyrics - init, lyrics - edit,
        time - init and time - edit could be placed.

        """
        self.lyrics_train_is_active = False  # Allow normal read/save ops

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

            WARNING: work_time_list, new_time_list and lyrics_time_list are
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
            self.play_lyrics_right_click(event)
            return

        if self.pp_state is 'Paused':
            # If Pause/Play State is currently paused we can not synchronize
            # June 5/2021: change top level from self.play_top
            answer = message.AskQuestion(
                self.lyrics_score_box, thread=self.get_refresh_thread(),
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
            return

        suffix2 = suffix.split()[2:]
        self.lyrics_panel_text = prefix + "Line: " + str(line_no) + " " + ' '.join(suffix2)
        self.lyrics_frm.update()
        self.lyrics_panel_last_line = line_no

    def play_lyrics_see_ahead(self, rewind=False):
        """ Should always see two lines ahead to coming up.
            If rewinding need to see previous two lines.
        """
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

        # If we are synchronizing lyrics activate that window instead
        #if self.sync_top_is_active:   if self.fine_tune and
        #    self.sync_time_index_lift()
        #    return
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
                self.play_top, thread=self.get_refresh_thread(),
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
            # root.after(50)  # May 23 2023 - This suppresses tooltips
            self.refresh_play_top()


    def play_clip_paste_lyrics(self):
        """ Delete current song lyrics and insert text from clipboard.
        """
        # Give warning box when lyrics exist all will be lost!
        if len(self.lyrics_score) > 10:
            answer = message.AskQuestion(
                self.play_top, thread=self.get_refresh_thread(),
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
        if not self.lyrics_scrape_pid == 0:
            print('lyrics are being web scraped. Please wait a second.')
            return

        if not self.play_top_is_active or \
                self.fine_tune and self.fine_tune.top_is_active:
            return

        print('EDIT LYRICS:', self.play_ctl.Artist, self.play_ctl.Album, 
              self.play_ctl.Title)

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
                self.play_top, thread=self.get_refresh_thread(),
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
    #       MusicTree class - Smaller sized functions
    #
    # ==============================================================================

    def set_artwork_colors(self):
        """
            Get artwork for currently playing song.
            Apply artwork colors to panels, buttons and text.
        """
        self.play_current_song_art, self.play_resized_art, self.play_original_art = \
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
        # Consider name self.theme_bg and self.theme_fg
        self.theme_bg = hex_background
        self.theme_fg = hex_foreground

        # Apply color codes to all play_top labels and buttons.
        self.play_frm.configure(bg=self.theme_bg)
        toolkit.config_all_labels(self.play_top, fg=self.theme_fg,
                                  bg=self.theme_bg)
        self.play_btn_frm.configure(bg=self.theme_bg)
        toolkit.config_all_buttons(self.play_top, fg=self.theme_bg,
                                   bg=self.theme_fg)

        # Apply color code to canvas rounded button and text
        #self.lyrics_panel_scroll.update_colors(hex_foreground, hex_background)
        self.lyrics_panel_scroll_a_m.update_colors(hex_foreground, hex_background)
        self.lyrics_panel_scroll_t_m.update_colors(hex_foreground, hex_background)
        self.lyrics_panel_scroll_m_a.update_colors(hex_foreground, hex_background)
        self.lyrics_panel_scroll_m_t.update_colors(hex_foreground, hex_background)
        self.lyrics_panel_hamburger.update_colors(hex_foreground, hex_background)

        # Apply color code to Lyrics
        self.play_frame3.config(bg=hex_background,
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
        rpath = rpath.replace(os.sep + NO_ARTIST_STR, '', 1)
        rpath = rpath.replace(os.sep + NO_ALBUM_STR, '', 1)
        return rpath

    def play_shuffle(self):
        """ Convert selections to list, shuffle, convert back to tuple
            Get confirmation because this cannot be undone. 'yes'

        """

        self.set_title_suffix()

        dialog = message.AskQuestion(
            self.play_top, thread=self.get_refresh_thread(),
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
        if self.playlists.name is not None:
            self.playlists.act_id_list = []
            for Id in self.saved_selections:
                music_id = self.get_music_id_for_lib_tree_id(Id)
                if music_id == 0:
                    toolkit.print_trace()
                    print("sql.music_id_for_song(insert_path[len(PRUNED_DIR):])")
                else:
                    self.playlists.act_id_list.append(music_id)
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
                LIBRARY_SELECT_INSERT_PLAY_HERE = False
                LIBRARY_SELECT_INSERT_PLAY_NEXT = True
                LIBRARY_SELECT_INSERT_PLAY_RANDOM = False
                LIBRARY_SELECT_INSERT_PLAY_ORDER = False

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
        # TODO: last_selections aren't being saved. When clicking play again
        #       shuffle order and last song index are lost.

        if not self.play_top_is_active:
            return  # play_close() already run.

        ''' Should not be able to call if self.fine_tune is active. '''
        if self.fine_tune and self.fine_tune.top_is_active:
            self.fine_tune.close()  # Prevents tons of exceptions.

        self.tt.close(self.play_top)  # Close tooltips under top level
        ''' July 9, 2023 - Doesn't matter if volume left turned down '''
        #if self.play_ctl.sink is not "":
        #    pav.set_volume(self.play_ctl.sink, 100)
        self.play_ctl.close()  # If playing song update last access time

        # Reverse filters so proper song index is saved
        if self.chron_filter is not None:
            self.chron_reverse_filter()

        self.save_resume()  # playing/paused and seconds progress into song.
        self.save_chron_state()  # chronology tree state = "Show"/"Hide"
        self.save_hockey_state()  # Hockey buttons OR FF/Rewind buttons?
        if self.playlists.name is not None:
            self.save_open_states()

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

        root.update()
        root.after(50)  # Give events time to close down
        self.wrapup_song()  # kill song and collapse parent chevrons
        #        os.remove(TMP_CURR_SONG)           # Clean up /tmp directory
        self.restore_lib_buttons()  # Restore Library buttons to default

        self.play_top.destroy()
        self.pp_state = None
        #self.play_top = None  #Nonetype error, try reassigning and destroy first

    def get_resume(self):
        """
            Get last saved state of playing / paused and seconds progress into song.
        """
        d = self.get_config_for_loc('resume')
        if d is None:
            return None

        # print("Found SourceMaster:", d['SourceMaster'], "SourceDetail:", d['SourceDetail'])
        if d['SourceDetail'] != str(self.ndx):
            if self.playlists.name is not None:
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
            TODO:   Same function in MusicTree() class and tvVolume() class.
                    Awkward that tvVolume() class needs to be passed Playlists().
        """
        if NEW_LOCATION:
            return None

        if self.playlists.name is not None:
            Action = self.playlists.act_number_str
        else:
            Action = LODICT['iid']
        return sql.get_config(Type, Action)

    def save_config_for_loc(self, Type, SourceMaster="", SourceDetail="", Target="",
                            Size=0, Count=0, Seconds=0.0, Comments=""):
        """ Wrapper Action is auto assigned as location or playlist number string
            TODO:   Same function in MusicTree() class and tvVolume() class.
                    Awkward that tvVolume() class needs to be passed Playlists().
        """
        if NEW_LOCATION:
            return None
        if self.playlists.name is not None:
            Action = self.playlists.act_number_str
        else:
            Action = LODICT['iid']

        sql.save_config(
            Type, Action, SourceMaster=SourceMaster, SourceDetail=SourceDetail,
            Target=Target, Size=Size, Count=Count, Seconds=Seconds,
            Comments=Comments)

    def get_chron_state(self):
        """
            Get last saved state of Show/Hide Chronology button
        """
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
        self.edit_menu.entryconfig("TV Volume for Hockey Commercials", state=tk.NORMAL)

        return hockey_state

    def save_hockey_state(self):
        """ Save state for Hockey TV Commercial Buttons and Volume """
        state = "On" if self.play_hockey_allowed else "Off"
        Comments = "Hockey TV Commercial Buttons used?"
        self.save_config_for_loc(
            'hockey_state', state, TV_SOUND, Size=TV_VOLUME, Count=TV_BREAK1,
            Seconds=float(TV_BREAK2), Comments=Comments)

    def get_open_states_to_list(self):
        """
            Get list of artists and albums that are expanded (opened)
        """
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
        """
            Save state of playing / paused and seconds progress into song.
        """
        open_states = self.get_all_open_states()
        Comments = "Artists and Albums that were expanded when play closed."
        self.save_config_for_loc(
            'open_states', Target=json.dumps(open_states), Comments=Comments)

    # ==============================================================================
    #
    #       Sample song from lib_tree - middle 10 seconds or full song
    #
    # ==============================================================================

    def lib_tree_play(self, Id, sample='middle'):
        """
            Sample middle 10 seconds or full song. Turn down other applications
            when starting and restore other application volume when ending.

        """
        ''' Build full song path '''
        path = self.real_path(int(Id))

        ''' Use self.lib_top because self.sam_top not declared yet. '''
        self.sam_ctl = FileControl(self.lib_top, self.info,
                                   close_callback=self.close_lib_tree_song)

        ''' When clicking Zombies/Liar and Zombies/Pretty no sink available '''
        # June 30, 2023 debugging stuff that was never really solved and
        #   patched with JACK-HAMMER
        # July 2, 2023 turns out songs simply cannot be played in middle.

        ''' Sanity check to see if file really has music inside '''
        self.sam_ctl.new(path)  # Get metadata for music file
        if self.sam_ctl.invalid_file:
            print(self.sam_ctl.metadata)
            self.corrupted_music_file(path)  # Non-blocking dialog box
            ''' Sanity check - Should .close() or .end() be used??? '''
            self.sam_ctl.close()  # reset last access time to original value
            return

        ''' July 3, 2023 - test is not needed. No problem with ffplay
        if not self.sam_ctl.test_middle():
            self.sam_ctl.close()
            return
        '''

        ''' Set start (beginning or middle) and duration (all or 10 seconds) '''
        if sample == 'middle':
            # July 3, 2023 - BIG BUG was using self.DurationSecs which was
            #                really self.play_ctl.DurationSecs and twice length
            start = self.sam_ctl.DurationSecs / 2 - 5.0
            limit = 10.0
        else:
            start = 0.0  # 'full' sample, start at beginning
            limit = self.sam_ctl.DurationSecs

        if limit > self.sam_ctl.DurationSecs:
            limit = self.sam_ctl.DurationSecs
            start = 0.0

        if start + limit > self.sam_ctl.DurationSecs:
            limit = self.sam_ctl.DurationSecs
            start = 0.0

        ''' Start ffplay and get Linux PID and Pulseaudio Input Sink # '''
        #self.sam_ctl.start(start, limit, 1, 1, TMP_CURR_SAMPLE, True)
        # Fade in and out for one second. True = start in paused state.
        self.sam_ctl.start(start, limit, 1, 1, TMP_CURR_SAMPLE, False)

        ''' a little debugging. each song start vol 25, 20, 8, 2, 1, 0... '''
        vol = pav.get_volume(self.sam_ctl.sink)
        print("\nlib_tree_play() Check Volume:", vol,
              " | self.sam_ctl.sink:", self.sam_ctl.sink,
              " | self.sam_ctl.pid:", self.sam_ctl.pid)
        # if vol and float(vol) != 100.0:  # hold_sink:
        if self.sam_ctl.sink is not None:
            pav.set_volume(self.sam_ctl.sink, 100.0)

        """ TODO: Fade out all others except ffplay. 
            Save their starting values to backup list
        """

        ''' Update lib_tree last access time display '''
        self.update_lib_tree_song(Id)

        ''' Create window '''
        self.sam_top = tk.Toplevel()
        self.sam_top.minsize(g.WIN_MIN_WIDTH, g.WIN_MIN_HEIGHT)
        self.sam_top_is_active = True
        self.sam_paused_music = False

        if self.pp_state is "Playing":  # Is music playing?
            self.pp_toggle()  # Pause to play sample
            self.sam_paused_music = True  # We will resume play later

        pav.fade_out_aliens(1)  # Turn down non-ffplay volumes to 0

        ''' Place Window top-left of parent window with PANEL_HGT padding '''
        xy = (self.lib_top.winfo_x() + PANEL_HGT,
              self.lib_top.winfo_y() + PANEL_HGT)
        self.sam_top.minsize(width=BTN_WID * 10, height=PANEL_HGT * 4)
        self.sam_top.geometry('+%d+%d' % (xy[0], xy[1]))
        if sample == 'middle':
            self.sam_top.title("Play middle 10 seconds - mserve")
        else:
            self.sam_top.title("Play whole song - mserve")
        self.sam_top.configure(background="Gray")
        self.sam_top.columnconfigure(0, weight=1)
        self.sam_top.rowconfigure(0, weight=1)

        ''' Create master frame for artwork, song info and button '''
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
        tk.Label(sam_frm, text="Artist:\t" + self.sam_ctl.Artist, padx=10,
                 font=(None, MON_FONTSIZE)).grid(row=0, column=1, sticky=tk.W)
        # Truncate self.Album to 25 characters plus ...
        tk.Label(sam_frm, text="Album:\t" + self.sam_ctl.Album, padx=10,
                 font=(None, MON_FONTSIZE)).grid(row=1, column=1, sticky=tk.W)
        tk.Label(sam_frm, text="Title:\t" + self.sam_ctl.Title, padx=10,
                 font=(None, MON_FONTSIZE)).grid(row=2, column=1, sticky=tk.W)
        tk.Label(sam_frm, text="Genre:\t" + self.sam_ctl.Genre, padx=10,
                 font=(None, MON_FONTSIZE)).grid(row=3, column=1, sticky=tk.W)
        tk.Label(sam_frm, text="Track:\t" + self.sam_ctl.Track, padx=10,
                 font=(None, MON_FONTSIZE)).grid(row=4, column=1, sticky=tk.W)
        tk.Label(sam_frm, text="Date:\t" + self.sam_ctl.Date, padx=10,
                 font=(None, MON_FONTSIZE)).grid(row=5, column=1, sticky=tk.W)
        tk.Label(sam_frm, text="Duration:\t" + self.sam_ctl.Duration, padx=10,
                 font=(None, MON_FONTSIZE)).grid(row=6, column=1, sticky=tk.W)

        ''' Close Button ✘ '''
        tk.Button(sam_frm, text="✘ Close", width=BTN_WID2,
                  command=self.lib_tree_play_close) \
            .grid(row=8, column=0, padx=2, sticky=tk.W)
        self.sam_top.bind("<Escape>", self.lib_tree_play_close)
        self.sam_top.protocol("WM_DELETE_WINDOW", self.lib_tree_play_close)

        ''' Now mount real artwork '''
        artwork, resized_art, original_art = \
            self.sam_ctl.get_artwork(self.art_width, self.art_height)
        if artwork is not None:
            sample_art_label.configure(image=artwork)

        ''' Loop until last second then exit during fade-out start '''
        self.sam_top.update()
        while self.sam_ctl.check_pid():
            self.sam_top.update_idletasks()
            if not self.refresh_works(self.get_refresh_thread):
                break
            elapsed = self.sam_ctl.elapsed()
            if elapsed - start + 1.0 > limit:
                #print("elapsed:", elapsed, " | start:", start, " | limit:", limit)
                break

        ''' Wrapup '''
        if self.sam_top_is_active is False: 
            return  # We are already closed

        self.lib_tree_play_close(normal=True)

    @staticmethod
    def refresh_works(get_refresh_thread):
        """ Refresh Tooltips, Pulse Audio fades and get user input
            Returns False when system shutting down
        """
        thread = get_refresh_thread()
        if thread:
            thread()
            return True
        else:
            return False

    # noinspection PyUnusedLocal
    def lib_tree_play_close(self, normal=False, *args):  # *args required when lambda used
        """ Close self.sam_top - Sample random song
            Can come here twice. Once normally and again with close button.
        """

        if self.sam_top_is_active is False:
            return  # We are already closed

        if self.sam_paused_music:  # Did we pause music player?
            self.pp_toggle()  # Resume playing


        if normal:
            ''' Ending as song is winding down '''
            pav.fade_in_aliens(1)  # Turn back non-ffplay volumes to original
            while self.sam_ctl.check_pid():
                if not self.refresh_works(self.get_refresh_thread):
                    break
        else:
            ''' Demand close by 'X' window, <Escape> key or Close button '''
            pav.fade(self.sam_ctl.sink, 100, 25, .33)  # Fast fade down
            now = time.time()
            while self.sam_ctl.check_pid():
                if time.time() - now > .30:
                    break  # Drop down to close song politely
                if not self.refresh_works(self.get_refresh_thread):
                    break
            pav.fade_in_aliens(1)  # Turn back non-ffplay volumes to original

        self.sam_ctl.close()  # Close FileControl(), reset ATIME
        self.tt.close(self.sam_top)  # Close tooltips under top level
        self.sam_top_is_active = False

        if os.path.isfile(TMP_CURR_SAMPLE):
            os.remove(TMP_CURR_SAMPLE)  # Clean up /tmp directory

        self.sam_top.destroy()  # Close the window
        self.wrap_up_popup()  # Set color tags and counts

    def sample_song_lift(self):
        self.sam_top.focus_force()  # Get focus
        self.sam_top.lift()  # Raise in stacking order

    # ==============================================================================
    #
    #       Playlist chronology
    #
    # ==============================================================================

    def build_chronology(self, _sbar_width=12):
        """ Chronology treeview List Box, Columns and Headings
        """
        #style = ttk.Style(self.F4)
        #style.configure("black.Treeview", background="black")
        self.chron_tree = ttk.Treeview(self.F4, show=('tree',), selectmode="none")
        #self.chron_tree.configure(style="black.Treeview")
        # https://stackoverflow.com/a/43834987/6929343
        # black background isn't working. set each row bg color instead
        self.chron_tree.column("#0", minwidth=900, stretch=tk.YES)
        self.chron_tree.grid(row=0, column=0, sticky=tk.NSEW)
        #self.chron_tree.rowconfigure(0, weight=1)  # Doesn't fix background prob.

        ''' Chronology Treeview Scrollbars '''
        # Create a vertical scrollbar linked to the frame.
        # MON_FONTSIZE
        v_scroll = tk.Scrollbar(self.F4, orient=tk.VERTICAL, width=SCROLL_WIDTH,
                                command=self.chron_tree.yview)
        v_scroll.grid(row=0, column=1, sticky=tk.NS)
        self.chron_tree.configure(yscrollcommand=v_scroll.set)
        v_scroll.config(troughcolor='black', bg='gold')
        # v_scroll.config(width=SCROLL_WIDTH)


        # horizontal scrollbar does nothing in treeview with single column.
        #h_scroll = tk.Scrollbar(self.F4, orient=tk.HORIZONTAL, width=_sbar_width,
        #                        command=self.chron_tree.xview)
        #h_scroll.grid(row=1, column=0, sticky=tk.EW)
        #self.chron_tree.configure(x scroll command=h_scroll.set)

        ''' Use tool_type="canvas_button" for entire treeview
            DISABLED - Leave comments here so mistake isn't repeated... 
        '''
        # Note this steals <Button-1>, <Motion> and <Leave> events from canvas
        # Which get stolen back in bindings further down
        #self.tt.add_tip(
        #    self.chron_tree, "Playlist Chronology\n" +
        #    "Right click on a song for action menus.",
        #    tool_type="canvas_button", anchor="nw")

        ''' Chronology treeview Colors '''
        self.chron_tree.tag_configure('normal', background='Black',
                                      foreground='Gold')
        self.chron_tree.tag_configure('chron_sel', background='grey18',
                                      foreground='LightYellow')

        ''' Configure tag for row highlight '''
        self.chron_tree.tag_configure('highlight', background='LightBlue')

        self.chron_tree.bind('<Motion>', self.chron_highlight_row)
        self.chron_tree.bind("<Leave>", self.chron_leave_row)

        ''' Trap left mouse click to select song for playing '''
        # Left click on works when clicked twice
        #self.chron_tree.bind('<Button-1>', self.chron_tree_left_click)
        #self.chron_tree.bind('<Button-1>', self.chron_tree_right_click)
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

        ''' Create empty rows when row count < 10 '''
        row_count = len(self.chron_tree.get_children())
        fake_rows = self.chron_tree.tag_has("empty")  # existing number fake rows
        needed_rows = 10 - row_count
        needed_rows = 0 if needed_rows < 0 else needed_rows
        if needed_rows > len(fake_rows):
            add_cnt = needed_rows - len(fake_rows)
            for _ in range(add_cnt):
                self.chron_tree.insert('', 'end', tags=("normal", "empty"))
        elif len(fake_rows) > needed_rows:
            del_cnt = len(fake_rows) - needed_rows
            for i, _ in enumerate(range(del_cnt)):
                self.chron_tree.delete(fake_rows[i])

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
        """ Cursor hovering over row highlights it in light blue
        """
        tree = event.widget
        item = tree.identify_row(event.y)
        #print("item:", item)  # Never getting called?
        if item.startswith("I"):
            return

        if self.chron_last_row == item:
            return        # Get called dozens of times when still in same row

        self.chron_leave_row()  # If we left a row reset chron_tree background

        ''' Remove "normal" or "chron_sel" tag and replace with "highlight" '''
        tags = self.chron_tree.item(item)['tags']
        if "chron_sel" in tags:
            toolkit.tv_tag_replace(self.chron_tree, item, "chron_sel", "highlight", strict=True)
            self.chron_last_tag_removed = "chron_sel"
        elif "normal" in tags:
            toolkit.tv_tag_replace(self.chron_tree, item, "normal", "highlight", strict=True)
            # Got error that "normal" wasn't in tags when using strict=True June 23, 2023
            # Probably fixed because 'not' was missing in chron_leave_row() function
            self.chron_last_tag_removed = "normal"
        else:
            # print("chron_highlight_row() error tags:", tags, type(tags), "item:", item)
            # Tkinter bug? item is blank and tags is empty string
            # Happens when you are on top row and go up into play_top button bar
            return

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

    def chron_tree_left_click(self, event):
        """
            Binding goes directly to chron_tree_right_click()
        """
        #item = self.chron_tree.identify_row(event.y)
        #print('mserve.py chron_tree_left_click(self, event):', item)
        self.chron_tree_right_click(event)

    def chron_tree_right_click(self, event):
        """ Drop down menu:
                Play different song / Restart current song
                Kid3 to edit metadata / artwork
                Notes about song stored in SQL History Table
                Filter songs by artist, with time index, over 5 minutes
        """
        item = self.chron_tree.identify_row(event.y)
        if item.startswith("I"):
            self.info.cast("Cannot click on an empty row.")
            return

        ''' self.mouse_x, self.mouse_y for Kid3 '''
        self.mouse_x, self.mouse_y = event.x_root, event.y_root

        ''' After this function ends, tkinter invokes self.chron_leave_row()'''
        self.chron_last_row = None  # Trick chron_leave_row() to do nothing

        menu = tk.Menu(root, tearoff=0)
        menu.post(event.x_root, event.y_root)

        if self.ndx == (int(item) - 1):
            # Restart current song from beginning
            menu.add_command(label="Restart Song № " + item, font=(None, MED_FONT),
                             command=lambda: self.chron_tree_play_now(item))
        else:
            # Play different song in list / Sel. MB
            menu.add_command(label="Play Song № " + item, font=(None, MED_FONT),
                             command=lambda: self.chron_tree_play_now(item))
        menu.add_separator()
        if self.chron_filter is None:
            # Give three filter options
            menu.add_command(label="Filter Synchronized songs", font=(None, MED_FONT),
                             command=lambda: self.chron_apply_filter('time_index', item))
            menu.add_command(label="Filter not Synchronized", font=(None, MED_FONT),
                             command=lambda: self.chron_apply_filter('no_time_index', item))
            menu.add_command(label="Filter by this Artist", font=(None, MED_FONT),
                             command=lambda: self.chron_apply_filter('artist_name', item))
            menu.add_command(label="Filter over 5 Minutes", font=(None, MED_FONT),
                             command=lambda: self.chron_apply_filter('over_5', item))
        else:
            # option to remove filters for full playlist
            menu.add_command(label="Full playlist unfiltered", font=(None, MED_FONT),
                             command=lambda: self.chron_reverse_filter())
        menu.add_separator()
        # Future Song/Playlist Notes kept in SQL History
        #menu.add_command(label="Notes", font=(None, MED_FONT),
        #                 command=lambda: self.chron_tree_notes(item))
        if KID3_INSTALLED:
            menu.add_command(label="kid3", font=(None, MED_FONT),
                             command=lambda: self.chron_tree_kid3(item))
        menu.add_separator()
        menu.add_command(label="Ignore click", font=(None, MED_FONT),
                         command=lambda: self.close_chron_popup(menu, item))

        menu.tk_popup(event.x_root, event.y_root)
        menu.bind("<FocusOut>", lambda _: self.close_chron_popup(menu, item))
        # '_' prevents: TypeError: <lambda>() takes no arguments (1 given)

    def close_chron_popup(self, menu, item):
        self.chron_last_row = item  # Restore item stolen when menu built
        self.chron_leave_row()  # This was called when menu posted but item None
        menu.unpost()  # Remove popup menu

    def chron_tree_play_now(self, item):
        """ Play song highlighted in chronology treeview.
        """
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
                    if "songsel" in self.lib_tree.item(song)['tags']:
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
                if iid.startswith("I"):
                    continue  # empty row
                time_index_flag = self.chron_tree.item(iid)['values'][0]
                #print("time_index_flag:", time_index_flag, "iid:", iid)
                if time_index_flag == 'no':  # "is 'yes':" doesn't work !!!
                    self.chron_attached.append(iid)  # Playlist number strings
                    # print("synchronized:", time_index_flag, "iid:", iid)

        if option is "over_5":
            for i, iid in enumerate(self.chron_tree.get_children()):
                if iid.startswith("I"):
                    continue  # empty row
                text = self.chron_tree.item(iid)['text']
                duration = text.split(" ")[-1]
                if ":" in duration:
                    minutes = duration.split(":")[0].strip()
                    if minutes.isdigit() and int(minutes) >= 5:
                        self.chron_attached.append(iid)  # Playlist number strings
                        # print("duration:", duration, "iid:", iid)

        kept_count = 0
        for i, iid in enumerate(self.chron_tree.get_children()):
            if iid.startswith("I"):
                continue  # empty row
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
                             thread=self.get_refresh_thread(),
                             title="Filter Playlist Failed - mserve")
            self.info.fact(quote)
            return  # TODO: Has this been tested? Use small playlist

        # Synchronized comes out ordered. Artist is random order
        self.chron_attached.sort(key=int)
        #for i, attached in enumerate(self.chron_attached):
        #    print(i, attached)

        # Stop current song and remove highlighting in lib_tree
        if self.pp_state == "Playing":
            # Note something is stopping vu_meter, but it's not this
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
        #print("restoring original self.ndx:", self.ndx)

    def chron_tree_notes(self, Id):
        """ Edit notes for song using Id number
        """
        # Notes kept in SQL History Type = "notes" Action = "playlist"
        #   SourceMaster = <Tags> SourceDetail = <Notes Body> Comments = ?
        _x, _y, width, height = self.play_frm.grid_bbox(0, 0, 4, 4)
        print("4,4 width, height:", width, height)
        _x, _y, width, height = self.play_frm.grid_bbox(0, 0, 5, 5)
        print("5,5 width, height:", width, height)
        iid = self.saved_selections[Id - 1]
        full_path = self.real_path(int(iid))
        print("full_path:", full_path)  # get_artist _opened

        # Mount screen above current highlighted line. set width to play_frm width - 20
        # Use scroll bar on right side only. Window height half of self.art_height

    def chron_tree_kid3(self, item):
        """ Edit ID tags with kid3
            Id from song_selections[] vs. treeview Id
        """
        iid = self.saved_selections[int(item) - 1]  # Create treeview ID
        self.kid3_song(iid)

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
        song_name = self.lib_tree.item(lib_tree_iid)['text']
        song_name = song_name.lstrip('0123456789.- ')  # Trim leading digit
        song_name = os.path.splitext(song_name)[0]  # Trim trailing ext
        line = number_str
        line = cat3(line, TITLE_PREFIX, song_name)

        ''' Extract Artist name from treeview parents '''
        album = self.lib_tree.parent(lib_tree_iid)
        artist = self.lib_tree.parent(album)
        line = cat3(line, ARTIST_PREFIX, self.lib_tree.item(artist)['text'])
        line = cat3(line, ALBUM_PREFIX, self.lib_tree.item(album)['text'])

        ''' Build extended line using metadata for song in SQL Music Table '''
        #path = self.real_path(int(playlist_no - 1))  # Remove <No Artist>, etc.
        path = self.real_path(int(lib_tree_iid))  # Remove <No Artist>, etc.
        sql_key = path[len(START_DIR):]  # Remove prefix from filename

        ''' June 3, 2023 - Using new Blacklist '''
        d = sql.ofb.Select(sql_key)

        if d is None:
            return line, None  # No SQL Music Table Row exists, use short line

        try:
            line = number_str + TITLE_PREFIX + d['MetaSongName'].encode("utf8")
        except AttributeError:  # 'NoneType' object has no attribute 'encode'
            # When playing a new location no SQL library information exists
            #print("Bad song (sql_key):", sql_key)
            #print("d['Id']:", d['Id'])
            return line, None  # No SQL Music Table Row exists, use short line

        line = line + ARTIST_PREFIX + d['MetaArtistName'].encode("utf8")
        line = line + ALBUM_PREFIX + d['MetaAlbumName'].encode("utf8")

        # line = line + DATE_PREFIX + str(d['ReleaseDate'])  # bad idea having float
        date = None
        if type(d['ReleaseDate']) is str:
            if d['ReleaseDate'] != "None":  # Strange but true... See "She's No Angel" by April Wine.
                date = d['ReleaseDate']
        elif type(d['ReleaseDate']) is float:
            date = str(int(d['ReleaseDate']))
        if date is not None:
            line = line + DATE_PREFIX + date  # bad idea having float

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
        if self.chron_is_hidden:  # Is playlist currently hidden?
            self.F4.grid()  # Restore hidden grid
            self.move_lyrics_right()  # Lyrics score right of VU meters
            self.chron_is_hidden = False
            text = "🖸 Hide Chronology"
            text2 = "Hide the scrollable playlist below\n" +\
                    "double the size of spinning artwork."

        else:  # Hide chronology (playlist)
            self.F4.grid_remove()  # Hide grid but remember options
            self.move_lyrics_bottom()  # Lyrics score under VU meters
            self.chron_is_hidden = True
            text = "🖸 Show Chronology"
            text2 = "Show last three songs played,\n" +\
                    "current song, and next six\n" +\
                    "songs in playlist."

        self.set_vu_meter_height()  # It is double or half previous height

        self.chron_button['text'] = text
        self.tt.set_text(self.chron_button, text2)
        ''' Toggle tooltip window position above/below buttons '''
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

        self.play_chron_highlight(self.ndx, True)  # Required after shuffle songs
        #root.update()
        self.F4.update_idletasks()


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
                             font=(None, MON_FONTSIZE))
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
                          borderwidth=BTN_BRD_WID, relief=tk.RIDGE)
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
        style.configure("syn.Treeview", background=self.theme_bg,
                        fieldbackground=self.theme_bg,
                        foreground=self.theme_fg)

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

        ''' Treeview select item - custom select processing '''
        # self.tree.bind('<ButtonRelease-1>', self.tree_select)

        ''' Create images for checked, unchecked and tristate '''
        # Don't use self.checkboxes list as GC destroys others with that name
        self.check2 = img.make_checkboxes(row_height - 6, self.theme_fg,
                                          self.theme_bg, 'DodgerBlue')  # SkyBlue3 not in Pillow
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

        ''' sync lyrics treeview Colors '''
        self.tree.tag_configure('normal', background=self.theme_bg,
                                foreground=self.theme_fg)
        self.tree.tag_configure('sync_sel', background=self.theme_fg,
                                foreground=self.theme_bg)

        '''   B U T T O N   B A R   F R A M E   '''
        self.btn_bar_frm = tk.Frame(self.top, relief=tk.GROOVE,
                                    background=self.theme_bg, borderwidth=BTN_BRD_WID)
        self.btn_bar_frm.grid(row=2, column=0, padx=2, pady=2, sticky=tk.W)
        self.build_btn_bar_frm()  # Defaults to 'top' for top main window

        ''' Set default checkbox for currently playing line in caller '''
        for i, start_time in enumerate(self.work_time_list):
            if start_time > startup_elapsed:
                # This line starts later than current time so use last (i).
                item = i - 1
                item = item if item > 0 else 1
                tags = self.tree.item(item)['tags']
                tags.remove("unchecked")
                tags.append("checked")
                self.tree.item(item, tags=tags)
                self.tree.see(item)
                break

        self.time_ctl = FileControl(self.top, self.info, silent=True)
        self.time_ctl.new(self.play_path)

    def build_btn_bar_frm(self, level='top'):
        """ Build buttons for top_level, begin sync and sample all """
        if not self.top_is_active:
            return
        self.tt.close(self.btn_bar_frm)  # Remove old tooltip buttons in play_btn frame
        self.btn_bar_frm.grid_forget()
        self.btn_bar_frm.destroy()
        self.top.unbind("<Escape>")
        # Unbinds for all functions? https://bugs.python.org/issue31485

        ''' Frame for Buttons '''
        self.btn_bar_frm = tk.Frame(self.top, bg="Olive",
                                    borderwidth=BTN_BRD_WID, relief=tk.GROOVE)
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
                                  width=BTN_WID2 - 4, command=self.close)
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
                                  width=BTN_WID2, command=self.sync)
                begin.grid(row=0, column=col)
                self.tt.add_tip(
                    begin, "First check boxes for first and last line.\n" +
                           "Then click this button to synchronize.", anchor="nw")

            elif name == "Delete":
                ''' 😒 Delete - 😒 (u+1f612) - Delete all '''
                delete = tk.Button(self.btn_bar_frm, text=" 😒 Delete all", font=ms_font,
                                   width=BTN_WID2, command=self.delete_all)
                delete.grid(row=0, column=col)
                self.tt.add_tip(
                    delete, "When time indices are hopelessly wrong,\n" +
                            "click this button to delete them all.", anchor="nw")

            elif name == "Sample":
                ''' 🎵  Sample all - Sample all show library '''
                sample = tk.Button(self.btn_bar_frm, text=" 🎵 Sample all", font=ms_font,
                                   width=BTN_WID2, command=self.sample_all)
                sample.grid(row=0, column=col)
                self.tt.add_tip(
                    sample, "Click to sample the first second of every line.",
                    anchor="nw")

            elif name == "Merge":
                ''' - Merge lines - Merge two lines together '''
                merge = tk.Button(self.btn_bar_frm, text="- Merge lines", font=ms_font,
                                  width=BTN_WID2 - 2, command=self.merge_lines)
                merge.grid(row=0, column=col)
                self.tt.add_tip(
                    merge, "First check two or more lines. Then\n" +
                           "click this button to merge together.", anchor="nw")

            elif name == "Insert":
                ''' + Insert line - Insert line line eg [chorus] or [bridge] '''
                insert = tk.Button(self.btn_bar_frm, text="+ Insert line", font=ms_font,
                                   width=BTN_WID - 2, command=self.insert_line)
                insert.grid(row=0, column=col)
                self.tt.add_tip(
                    insert, "First check line to insert before. Then\n" +
                            "click this button to insert a new line.", anchor="ne")

            elif name == "Save":
                ''' 💾  Save - Save lyrics (may be merged) and time indices '''
                save = tk.Button(self.btn_bar_frm, text=" 💾 Save", font=ms_font,
                                 width=BTN_WID2 - 4, command=self.save_changes)
                save.grid(row=0, column=col)
                self.tt.add_tip(
                    save, "Save time indices and close\n" +
                          "this fine-tune index window.", anchor="ne")

            elif name == "HelpT":
                ''' 🔗 Help - Videos and explanations on pippim.com '''
                help = tk.Button(self.btn_bar_frm, text="🔗 Help", width=BTN_WID2 - 4,
                                 font=ms_font, command=lambda: get_help("HelpT"))
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
                                       width=BTN_WID2 - 6, command=self.sync_done)
                begin_done.grid(row=0, column=col, padx=2, sticky=tk.W)
                self.tt.add_tip(
                    begin_done, "Click this button to skip\n" +
                                "synchronizing remaining lines.", anchor="nw")

            elif name == "RewindB":
                ''' "Rewind 5 seconds" Button - Synchronize selected lines '''
                begin_rewind = tk.Button(self.btn_bar_frm, text="Rewind 5 seconds",
                                         width=BTN_WID2 + 2, font=ms_font,
                                         command=self.sync_rewind)
                begin_rewind.grid(row=0, column=col, padx=2)
                self.tt.add_tip(
                    begin_rewind, "Click this button to stop play,\n" +
                                  "go back 5 seconds and resume play.", anchor="nw")

            elif name == "HelpB":
                ''' 🔗 Help - Videos and explanations on pippim.com '''
                help = tk.Button(self.btn_bar_frm, text="🔗 Help", width=BTN_WID2-4,
                                 font=ms_font, command=lambda: get_help("HelpB"))
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
                                        width=BTN_WID2 - 6, font=ms_font,
                                        command=self.sample_done)
                sample_done.grid(row=0, column=col, padx=2, sticky=tk.W)
                self.tt.add_tip(sample_done, "Click this button to skip\n" +
                                "sampling remaining lines.", anchor="nw")

            elif name == "PP":
                ''' Pause/Play Button - Toggles state '''
                self.pp_state = 'Playing'
                self.pp_button = \
                    tk.Button(self.btn_bar_frm, text=self.pp_pause_text,
                              width=BTN_WID2 - 4,  font=ms_font,
                              command=self.toggle_play)
                self.pp_button.grid(row=0, column=col, padx=2, sticky=tk.W)
                self.tt.add_tip(
                    self.pp_button, "Click this button to toggle\n" +
                    "pause / playing of music.", anchor="nw")

            elif name == "RewindS":
                ''' Rewind 5 seconds Button '''
                sample_rewind = tk.Button(self.btn_bar_frm, text="Rewind 5 seconds",
                                          width=BTN_WID2 + 2, font=ms_font,
                                          command=self.sample_rewind)
                sample_rewind.grid(row=0, column=3, padx=2)
                self.tt.add_tip(
                    sample_rewind, "Click this button to stop play,\n" +
                    "go back 5 seconds and resume play.", anchor="ne")

            elif name == "HelpS":
                ''' 🔗 Help - Videos and explanations on pippim.com '''
                help = tk.Button(self.btn_bar_frm, text="🔗 Help", width=BTN_WID2 - 4,
                                 font=ms_font,
                                 command=lambda: get_help("HelpS"))
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

            TODO: Messages when syncing Janine by Trooper:

                count: 31 first: 18 last: 19
                Failed to get sink input information: No such entity
                Failed to get sink input information: No such entity
                Failed to get sink input information: No such entity
                Failed to get sink input information: No such entity

            May have to append " 2>/dev/null" but that will also hide bad
            programming using "pactl" external command
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

        if self.last_checked + 1 < self.lyrics_line_count:
            # Grab start time of line after last line to set duration+2 secs
            self.limit_sec = self.new_time_list[self.last_checked] - \
                                 self.start_sec + 2.0
        else:
            # TOP: self.play_DurationSecs = self.play_DurationSecs
            self.limit_sec = self.play_DurationSecs - self.start_sec

        self.time_ctl.start(self.start_sec, self.limit_sec,
                            .5, .5, TMP_CURR_SYNC, True)
        pav.set_volume(self.time_ctl.sink, 100)  # Restore volume def start(s
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
        for line in range(first_checked, last_checked):
            # Next 5 lines can be made into global function called:
            # tree_tag_replace(tree, old, new). Return true if found.
            tags = self.tree.item(line)['tags']
            if "unchecked" in tags:
                tags.remove("unchecked")
                tags.append("checked")
                self.tree.item(line, tags=tags)

    def delete_all(self):
        """ Time Indices hopelessly out of sync so Delete them.
        """
        if self.ffplay_is_running:
            return  # Already playing?

        answer = message.AskQuestion(
            self.top, thread=self.get_refresh_thread(),
            title="Delete all time indices",
            text="All times will be permanently erased!!!\n\n" +
                 'To cancel time changes, click "Close" button instead.' +
                 "\n\nAfter deleting, Time Index window will be closed.")
        # print('answer.result:', answer.result)
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
                self.tree.see(self.curr_line_no)
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
                self.top, thread=self.get_refresh_thread(),
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
                                     thread=self.get_refresh_thread(),
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
                self.top, thread=self.get_refresh_thread(),
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
                         thread=self.get_refresh_thread(),
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
                                         thread=self.get_refresh_thread(),
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
        # 'values' 0=Access, 1=Size, 2=Selected Size, 3=StatTime, 4=StatSize,
        #          5=Count, 6=Seconds, 7=SelSize, 8=SelCount, 9=SelSeconds
        total_values = slice(4, 7)  # parm = start index, stop before index
        # slice(4, 7) = Set slice to grab StatSize, Count, Seconds

        tags = self.tree.item(song)['tags']
        tags.append("songsel")  # Special handling by mserve only
        #tags.append("checked")  # CheckboxTreeview handling
        #tags.remove("unchecked")  # CheckboxTreeview handling
        self.tree.item(song, tags=tags)

        self.tree.set(song, "Selected", number_str)

        self.tree.change_state(song, "checked")  # in CheckboxTreeview()
        # With new design of load_last_selections() "checked" is now needed
        # in addition to "songsel" tag.

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
                           thread=self.get_refresh_thread(),
                           save_callback=self.save_callback
                           playlists=self.playlists, info=self.info)
          - Music must be playing (name=ffplay) or at least a song paused.
          - save_callback=function that will reread new variables saved.

    if self.tv_vol and self.tv_vol.top:
        - Volume top level exists so lift() overtop of self.lib_top

    """

    def __init__(self, parent=None, name="ffplay", title=None, text=None,
                 tooltips=None, thread=None, save_callback=None, playlists=None,
                 info=None):
        """
        """
        # self-ize parameter list
        self.parent = parent    # self.parent
        self.name = name            # Process name to search for current volume
        self.title = title          # E.G. "Set volume for mserve"
        self.text = text            # "Adjust mserve volume to match other apps"
        self.tt = tooltips          # Tooltips pool for buttons
        self.thread = thread        # E.G. self.get_refresh_thread()
        self.save_callback = save_callback  # Set hockey fields to new values
        self.playlists = playlists
        self.info = info

        self.last_volume = None
        self.last_sink = None
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
            xy = (self.parent.winfo_x() + PANEL_HGT * 3,
                  self.parent.winfo_y() + PANEL_HGT * 3)
        except AttributeError:  # MusicTree instance has no attribute 'winfo_x'
            print("self.parent failed to get winfo_x")
            xy = (100, 100)

        self.top.minsize(width=BTN_WID * 10, height=PANEL_HGT * 10)
        self.top.geometry('+%d+%d' % (xy[0], xy[1]))
        self.top.title("TV Volume during Commercials - mserve")
        self.top.configure(background="Gray")
        self.top.columnconfigure(0, weight=1)
        self.top.rowconfigure(0, weight=1)

        ''' Set program icon in taskbar '''
        img.taskbar_icon(self.top, 64, 'white', 'lightskyblue', 'black')

        ''' Create master frame '''
        self.vol_frm = tk.Frame(self.top, borderwidth=BTN_BRD_WID,
                                relief=tk.RIDGE)
        self.vol_frm.grid(column=0, row=0, sticky=tk.NSEW)
        self.vol_frm.columnconfigure(0, weight=1)
        self.vol_frm.columnconfigure(1, weight=5)
        self.vol_frm.rowconfigure(0, weight=1)
        ms_font = (None, MON_FONTSIZE)

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
        tk.Label(self.vol_frm, text=self.text, justify="left", font=ms_font)\
            .grid(row=0, column=0, columnspan=3, sticky=tk.W, padx=PAD_X)

        ''' Input fields: TV_BREAK1, TV_BREAK2 and TV_SOUND '''
        self.commercial_secs = tk.IntVar()
        self.intermission_secs = tk.IntVar()
        self.tv_application = tk.StringVar()
        tk.Label(self.vol_frm, text="Commercial seconds:",
                 font=ms_font).grid(row=1, column=0, sticky=tk.W)
        tk.Entry(self.vol_frm, textvariable=self.commercial_secs,
                 font=ms_font).grid(row=1, column=1, sticky=tk.W)
        tk.Label(self.vol_frm, text="Intermission seconds:",
                 font=ms_font).grid(row=2, column=0, sticky=tk.W)
        tk.Entry(self.vol_frm, textvariable=self.intermission_secs,
                 font=ms_font).grid(row=2, column=1, sticky=tk.W)
        tk.Label(self.vol_frm, text="TV application name:",
                 font=ms_font).grid(row=3, column=0, sticky=tk.W)
        tk.Entry(self.vol_frm, textvariable=self.tv_application,
                 font=ms_font).grid(row=3, column=1, sticky=tk.W)
        ''' TV Volume Slider '''
        self.slider = tk.Scale(self.vol_frm, from_=100, to=25, tickinterval=5,
                               command=self.set_sink)
        self.slider.grid(row=0, column=3, rowspan=4, padx=5, pady=5, sticky=tk.NS)
        ''' Close Button '''
        self.close_button = tk.Button(self.vol_frm, text="✘ Close",
                                      width=BTN_WID2 - 6,
                                      command=self.close)
        self.close_button.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        if self.tt:
            self.tt.add_tip(self.close_button, "Close TV Volume Slider, ignore changes.",
                            anchor="nw")
        self.top.bind("<Escape>", self.close)  # DO ONLY ONCE?
        self.top.protocol("WM_DELETE_WINDOW", self.close)
        ''' Apply Button '''
        self.apply_button = tk.Button(self.vol_frm, text="✔ Apply",
                                      width=BTN_WID2 - 6,
                                      command=self.apply)
        self.apply_button.grid(row=4, column=3, padx=5, pady=5, sticky=tk.W)
        if self.tt:
            self.tt.add_tip(self.apply_button, "Save TV Volume Slider changes and exit.",
                            anchor="ne")
        self.top.bind("<Return>", self.apply)  # DO ONLY ONCE?
        ''' Get current volume & Read stored volume '''
        self.last_volume, self.last_sink = self.get_volume()  # Reset this value when ending
        if not self.read_vol():
            message.ShowInfo(self.parent, "Initialization of mserve in progress.",
                             "Cannot adjust volume until playlist loaded into mserve.",
                             icon='error', thread=self.thread)
            self.close()

        if self.last_volume is None:
            title = "No Sound is playing."
            text = "Cannot adjust volume until a song is playing."
            message.ShowInfo(self.parent, title, text,
                             icon='warning', thread=self.thread)
            self.info.cast(title + "\n" + text, 'warning')
            self.close()

        if self.top:  # May have been closed above.
            self.top.update_idletasks()

    def get_volume(self, name=None):
        """ Get volume of 'ffplay' before modification and at end """
        if name is None:
            name = self.name  # self.name defaults to "ffplay"

        all_sinks = pav.get_all_sinks()  # Recreates pav.sinks_now
        print("\nmserve.py tvVolume.get_volume():\n")
        for Sink in all_sinks:
            # Doesnt' find sink. While error message up cycles
            # next song. 1 per second
            print("Sink:", Sink, "\nSearch name:", name, type(name),
                  "Sink.name:", Sink.name, type(Sink.name))
            # Sink:  Sink(sink_no_str='917', volume=100, name='ffplay', pid=32413, user='rick')
            # Sink:  Sink(sink_no_str='917', volume=70, name='ffplay', pid=32413, user='rick')
            if Sink.name == name:
                return int(Sink.volume), Sink.sink_no_str

        '''
        # TODO: Upgrade to pav.get_volume_by_name()?
        all_sinks = sink_master()
        # TODO: Upgrade to pav.get_volume_by_name()?
        for entry in all_sinks:
            sink, volume, app_name = entry
            if app_name == name:
                #print("get_volume():", volume)
                return int(volume), sink
        '''
        return None, None
    
    def set_sink(self, value=None):
        """
            Called when slider changes value. Set sink volume to slider setting.
            Credit: https://stackoverflow.com/a/19534919/6929343

            July 9, 2023 - Convert to new vu_pulse_audio.py functions.
        """
        if value is None:
            print("Volume() class, set_sink() 'value' argument is None")
            return
        ''' July 9, 2023 - Convert to new vu_pulse_audio.py functions.
        all_sinks = sink_list(self.name)
        if len(all_sinks) == 0 or all_sinks[0] == "":
            return

        sink = all_sinks[0]
        step_time, err = set_volume(sink, value)
        if err:
            print("Volume() class, set_sink() err:", err)
        else:
            self.curr_volume = value  # Record for saving later
        '''
        curr_vol, curr_sink = self.get_volume()
        pav.set_volume(curr_sink, value)
        self.curr_volume = value  # Record for saving later

    def read_vol(self):
        """
            Get last saved volume.  Based on get_hockey. If nothing found
            set defaults.
        """

        self.curr_volume = 100  # mserve volume when TV commercial on air
        d = self.get_config_for_loc('hockey_state')
        if d is None:
            return None

        ''' Get hockey tv commercial volume '''
        if 25 <= int(d['Size']) <= 100:
            self.curr_volume = int(d['Size'])
            #print("self.curr_volume 1:", self.curr_volume)  # 60

        self.commercial_secs.set(d['Count'])
        self.intermission_secs.set(int(d['Seconds']))
        self.tv_application.set(d['SourceDetail'])

        #print("self.curr_volume 2:", self.curr_volume)  # 60
        if self.last_volume:
            pav.fade(self.last_sink, self.last_volume, self.curr_volume, 1)
            ''' July 9, 2023 - Convert to new vu_pulse_audio.py functions
            hold = self.curr_volume  # June 10, 2023 - Create hold field
            step_volume(self.last_sink, self.last_volume, self.curr_volume,
                        10, .05, thread=self.thread)
            #print("self.curr_volume 3:", self.curr_volume)  # 25
            self.curr_volume = hold  # June 10, 2023 - Strange but true
            #print("self.curr_volume 4:", self.curr_volume)  # 60
            '''

        self.slider.set(self.curr_volume)
        self.top.update_idletasks()

        return True

    def save_vol(self):
        """
            Save volume
        """
        ''' Reread hockey state in case user changed after set_tv_volume started '''
        d = self.get_config_for_loc('hockey_state')
        # If we don't rewrite fields they get blanked out. Action=Location
        try:
            d['Count'] = self.commercial_secs.get()
            d['Size'] = float(self.intermission_secs.get())
        except ValueError:
            message.ShowInfo(self.top, "Invalid Seconds Entered.",
                             "Commercial or Intermission contains non-digit(s).",
                             icon='error', thread=self.thread)
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
                             icon='error', thread=self.thread)
            return False

        self.save_config_for_loc(
            'hockey_state', d['SourceMaster'], d['SourceDetail'], Size=self.curr_volume,
            Count=d['Count'], Seconds=d['Seconds'], Comments=d['Comments'])
        self.save_callback()  # This resets global TV_VOLUME variable for us
        return True

    def get_config_for_loc(self, Type):
        """ Wrapper Action is auto assigned as location or playlist number string
            TODO:   Same function in MusicTree() class and tvVolume() class.
                    Awkward that tvVolume() class needs to be passed Playlists().
        """
        if NEW_LOCATION:
            return None

        if self.playlists.name is not None:
            Action = self.playlists.act_number_str
        else:
            Action = LODICT['iid']
        return sql.get_config(Type, Action)

    def save_config_for_loc(self, Type, SourceMaster="", SourceDetail="", Target="",
                            Size=0, Count=0, Seconds=0.0, Comments=""):
        """ Wrapper Action is auto assigned as location or playlist number string
            TODO:   Same function in MusicTree() class and tvVolume() class.
                    Awkward that tvVolume() class needs to be passed Playlists().
        """
        if NEW_LOCATION:
            return None
        if self.playlists.name is not None:
            Action = self.playlists.act_number_str
        else:
            Action = LODICT['iid']

        sql.save_config(
            Type, Action, SourceMaster=SourceMaster, SourceDetail=SourceDetail,
            Target=Target, Size=Size, Count=Count, Seconds=Seconds,
            Comments=Comments)

    # noinspection PyUnusedLocal
    def close(self, *args):
        if self.tt:
            self.tt.close(self.top)
        self.top.destroy()
        #print("self.top after .destroy()", self.top)
        self.top = None  # Indicate volume slider is closed

        ''' Adjust volume for playing mserve song back to starting level '''
        curr_volume, curr_sink = self.get_volume()  # last_sink may have changed
        # without parameter TV_SOUND, the name "ffplay" will be used.
        #step_volume(curr_sink, curr_volume, self.last_volume, 10, .05,
        #            self.thread)
        if self.last_volume is not None:
            pav.fade(curr_sink, curr_volume, self.last_volume, 1)  # 1 second fade

    # noinspection PyUnusedLocal
    def apply(self, *args):
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
        self.metadata = None        # Dictionary containing metadata from music file
        self.artwork = []           # List of lines about artwork found
        self.audio = []             # List of lines about audio streams found
        self.valid_file = None      # len(self.audio) > 0
        self.invalid_file = None    # len(self.audio) == 0
        self.Artist = None          # self.metadata.get('ARTIST', "None")
        self.Album = None           # self.metadata.get('ALBUM', "None")
        self.Title = None           # self.metadata.get('TITLE', "None")
        self.Genre = None           # self.metadata.get('GENRE', "None")
        self.Track = None           # self.metadata.get('TRACK', "None")
        self.Date = None            # self.metadata.get('DATE', "None")
        self.Duration = None        # self.metadata.get('DURATION', "0.0,0")
        self.DurationSecs = None    # hh:mm:ss sting converted to int seconds

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
        self.last_sink = None       # Tell start_ffplay what's closing


class FileControl(FileControlCommonSelf):
    """ Control Music Files, including play, pause, end """

    def __init__(self, parent, info, close_callback=None, silent=False,
                 get_thread=None):
        """
        """
        FileControlCommonSelf.__init__(self)
        ''' self-ize parameter list '''
        self.tk_top = parent        # Tkinter Toplevel window used by parent
        self.info = info            # Parent's InfoCentre() instance
        self.close_callback = close_callback
        self.silent = silent        # Messages broadcast are logged as facts
        self.get_thread = get_thread
        self.last_path = None       # Not used as of July 1, 2023
        self.new_WIP = None         # .new() is Work In Progress
        self.start_WIP = None       # .start() or .restart() is WIP
        self.close_WIP = None       # .close() is Work In Progress

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

        ''' Is last song file still open (path not none)? '''
        if self.path is not None:
            if self.silent:  # In silent mode, normal broadcasts become facts
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
        self.path = path            # Full path to music file
        self.last_path = self.path  # Might be used in future, not July 1, 2023
        self.action = action        # Action to perform. Not used July 1, 2023
        # Keep original stat_start until .close() -> .end()
        # Use last_path because fast clicking Next call .close() who sets

        ''' Did fast clicking close the path? '''
        if self.path is None:
            self.info.fact("FileControl.new() path went 'None' step 1")
            return
        self.stat_start = os.stat(self.last_path)

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

    def get_metadata(self):
        """ Use ffprobe to write metadata to file TMP_FFPROBE
            Loop through TMP_FFPROBE lines to create dictionary self.metadata
        """
        self.metadata = OrderedDict()

        ext.t_init("FileControl.get_metadata()")
        cmd = 'ffprobe ' + '"' + self.last_path + '"' + ' 2>' + TMP_FFPROBE
        result = os.popen(cmd).read().strip()
        ext.t_end('no_print')
        # ffprobe on good files: 0.0858271122 0.0899128914 0.0877139568
        # ffprobe on corrupted : 0.1700458527  (file contains dozen bytes of text)

        if len(result) > 1:
            print('mserve.py FileControl.get_metadata() ffprobe result:', result)

        ''' Create self.metadata{} dictionary '''
        with open(TMP_FFPROBE) as f:
            for line in f:
                line = line.rstrip()  # remove \r and \n
                # print('line:', line)
                if line.startswith('  configuration:'):
                    continue
                if line.startswith('Input #0, '):
                    val = line.split('Input #0, ')[1]
                    self.metadata['INPUT #0'] = val
                    continue
                # noinspection PyBroadException
                try:
                    (key, val) = line.split(':', 1)  # Split first ':' only
                except:
                    continue  # No ':' on line

                key = key.strip()  # strip leading and
                val = val.strip()  # trailing whitespace
                if key is not "" and val is not "":
                    # Convert all keys to upper case for simpler lookups
                    key_unique = toolkit.unique_key(key.upper(), self.metadata)
                    # Key "Stream #0" appears twice
                    self.metadata[key_unique] = val

        path_parts = self.path.split(os.sep)
        self.Artist = self.metadata.get('ARTIST', "None")  # If not in dict, use "None"
        if self.Artist == "None":
            self.Artist = path_parts[-3].encode('utf-8')  # .wav files have no metadata
        self.Artist = toolkit.uni_str(self.Artist)

        self.Album = self.metadata.get('ALBUM', "None")
        if self.Album == "None":
            self.Album = path_parts[-2].encode('utf-8')
        self.Album = toolkit.uni_str(self.Album)

        self.Title = self.metadata.get('TITLE', "None")
        if self.Title == "None":
            self.Title = path_parts[-1].encode('utf-8')
        self.Title = toolkit.uni_str(self.Title)

        self.Genre = toolkit.uni_str(self.metadata.get('GENRE', "None"))
        self.Track = toolkit.uni_str(self.metadata.get('TRACK', "None"))
        self.Date = toolkit.uni_str(self.metadata.get('DATE', "None"))

        self.Duration = self.metadata.get('DURATION', "0.0,0").split(',')[0]
        self.Duration = toolkit.uni_str(self.Duration)
        self.Duration = self.Duration.split('.')[0]
        self.DurationSecs = convert_seconds(self.Duration)  # Note must save in parent

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

        text = "Title: \t" + self.Title + \
            "\nArtist: \t" + self.Artist + \
            " \tAlbum: \t" + self.Album + \
            "\nTrack:\t" + self.Track + \
            "\tDate:\t" + self.Date + \
            "\tDuration:\t" + self.Duration + "\n"

        for entry in self.audio:
            text += "Audio: \t" + entry + "\n"

        self.valid_file = len(self.audio) > 0
        self.invalid_file = not self.valid_file

        if self.valid_file:
            audio_pattern = ("Audio:", "Green", "Black")
        else:
            audio_pattern = ("Audio:", "Red", "White")
            text += "Audio: \tNOT FOUND !!!"

        for entry in self.artwork:
            text += "Artwork: \t" + entry + "\n"

        patterns = [("Title:", "Green", "Black"),
                    ("Artist:", "Green", "Black"),
                    ("Album:", "Green", "Black"),
                    ("Track:", "Green", "Black"),
                    ("Date:", "Green", "Black"),
                    ("Duration:", "Green", "Black"),
                    audio_pattern,
                    ("Artwork:", "Green", "Black")]

        if self.valid_file or self.silent:
            self.info.fact(text, 'info', patterns=patterns)
        else:
            self.info.cast(text, 'error', patterns=patterns)

    def log(self, state):
        """
        Important for song start, stop and end to be 100% in order to calculate
        if last access time should be reset based on percentage played threshold.

        :param state: 'start' = Playing, 'stop' = Paused, 'end' = killed
        :return: True but later could be False for sanity check errors
        """
        last_state = self.state
        self.state = state

        ''' Spam last state and current state. Temporary for debugging
        if self.path is None:
            #toolkit.print_trace()
            print("\nlog(): Path is None")
            path = u"???"
        else:
            path = self.path
        patterns = [("last_state:", "Green", "Black"),
                    ("curr state:", "Green", "Black"),
                    ("path:", "Green", "Black")]
        if self.silent:  # bugs in lib_tree_play()
            self.info.fact("last_state: \t" + str(last_state) + "\tcurr state: \t" +
                           self.state + "\tpath: \t" + path, patterns=patterns)
        else:
            self.info.cast("last_state: \t" + str(last_state) + "\tcurr state: \t" +
                           self.state + "\tpath: \t" + path, patterns=patterns)
        '''

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
        text += "\n\nCheck console log for traceback"
        # toolkit.print_trace()  # Getting sick of seein this !
        print(text)
        self.info.cast(text, 'error', 'add')
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
        filename, lineno, function_name, code = stack[-2]
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

        if self.silent:
            self.info.fact(text, patterns=patterns)
        else:
            self.info.cast(text, patterns=patterns)

    def get_artwork(self, width, height):
        """
            Use ffmpeg to get artwork for song into TMP_FFMPEG filename.
            Messages go to TMP_FFPROBE filename which is ignored for now.

            Called from:

            set_artwork_colors()
            lib_tree_play()
        """

        if len(self.artwork) == 0:
            # Song has no artwork that ffmpeg can identify.
            return None, None, None

        # Don't reuse last artwork
        if os.path.isfile(TMP_FFMPEG):
            os.remove(TMP_FFMPEG)

        # noinspection SpellCheckingInspection
        ext.t_init("'ffmpeg -nostdin -y -vn -an -r 1 -i '")
        # noinspection SpellCheckingInspection
        cmd = 'ffmpeg -nostdin -y -vn -an -r 1 -i ' + '"' + self.path + '" ' + \
              TMP_FFMPEG + ' 2>' + TMP_FFPROBE
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

        if not os.path.isfile(TMP_FFMPEG):
            # Song has no artwork that ffmpeg can identify.
            self.info.cast("FileControl.get_artwork(): Programming Error:\n" +
                           "No artwork for:\n\n" + self.path + "\n\n"
                           "However this error should have been caught above.")
            print("\nError getting artwork:\n")
            print(TMP_FFPROBE)
            return None, None, None

        original_art = Image.open(TMP_FFMPEG)
        resized_art = original_art.resize(
            (width, height), Image.ANTIALIAS)
        return ImageTk.PhotoImage(resized_art), resized_art, original_art

    def test_middle(self):
        """ ffplay will fail playing middle of some songs. This test is
            used by lib_tree_play() and FineTune() class.

            July 3, 2023 - 20 minutes after writing discovered this isn't
            needed. Keep around for documenting how FileControl() works.
        """

        if self.DurationSecs < 20:
            return False  # Not even a real song.

        old_silent = self.silent
        self.silent = True  # Don't broadcast what happens next
        start = self.DurationSecs / 2
        # Start halfway through, duration 5 seconds, with 4 second fade in
        self.start(start, 5, 4, 1, TMP_CURR_SAMPLE, True)
        time.sleep(.1)
        self.cont()
        time.sleep(.2)  # If ffplay breaks, job crashes in .1 second
        pid = self.check_pid()
        self.end()  # Kill song and restore last access time.
        self.silent = old_silent  # Restore original broadcast setting

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
              fade_out_sec=0.0, ff_name=None, dead_start=None, last_sink=None):
        """ Start playing song with parameters passed.
            Sanity check when start+limit > duration

        :param start_sec: Seconds offset to start playing at
        :param limit_sec: Number of seconds to play. 0 = play all
        :param fade_in_sec: Number of seconds to fade in
        :param fade_out_sec: Number of seconds to fade out
        :param ff_name: Filename containing ffplay output. E.G TMP_CURR_SONG
        :param dead_start: Set to volume to 0 and immediately stop play
        :param last_sink: Tell start_ffplay what's closing
        :return self.pid, self.sink:
        """

        self.start_WIP = None       # .start() or .restart() is WIP
        self.start_sec = start_sec          # Seconds offset to start playing at
        self.limit_sec = limit_sec          # Number of seconds to play. 0 = play all
        self.fade_in_sec = fade_in_sec      # Number of seconds to fade in
        self.fade_out_sec = fade_out_sec    # Number of seconds to fade out
        self.ff_name = ff_name              # TMP_CURR_SONG, etc.
        self.dead_start = dead_start        # Number of seconds to fade out
        self.last_sink = last_sink          # Tell start_ffplay what's closing

        # When action = 'start'
        # start = seconds offset to start song at. If 0.0, start at beginning
        # duration = seconds to play song for. If 0.0, entire song, skip duration set
        # fade_in = seconds to fade in for. If continuing, manually adjust volume
        # fade_out = seconds to fade out for. If pausing or ending, manually adjust
        # ff_name = Filename used by ffplay, ffmpeg and ffprobe with command
        #           Output. In this case it is ffplay output only.
        # dead_start = After starting song set volume to zero and stop running.
        #              When starting with fade-in there is no sound "pop"

        ''' extra options passed to ffplay for fade-in, etc. '''
        extra_opt = ffplay_extra_opt(self.start_sec, self.fade_in_sec,
                                     self.fade_out_sec, self.limit_sec)
        ''' uncomment for debugging 
        text = "FileControl.start(self.start_sec, \t" + str(self.start_sec) +\
            "\nself.limit_sec, \t" + str(self.limit_sec) + "\nself.fade_in_sec, \t" +\
            str(self.fade_in_sec) + "\nself.fade_out_sec, \t" + str(self.fade_out_sec) +\
            "\nself.dead_start, \t" + str(self.dead_start) + "\nself.ff_name, \t" + \
            str(self.ff_name) + "\n"
        self.info.cast("FileControl.start() extra_opt:\n" + extra_opt)
        self.info.cast(text)  # For debugging
        #print(text)  # For debugging
        '''

        '''   B I G   T I C K E T   E V E N T   '''
        # TODO: Move start_ffplay() code up to self.start_ffplay()
        #thread = self.get_thread()
        self.pid, self.sink = start_ffplay(self.path, self.ff_name,
                                           extra_opt, toplevel=self.tk_top)
        #                                   thread=thread)

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
                fade_out_sec=0.0, ff_name=None, dead_start=False,
                last_sink=None):
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
            last_sink = self.sink
            self.sink = ""

        ''' Song may have been paused before getting killed above '''
        if self.state != 'stop':  # 'stop' code already logged. Don't repeat.
            self.log('stop')  # There is no 'kill' code so use 'stop' instead.

        if not ff_name:
            ''' TMP_CURR_SONG is required. If not passed use last '''
            ff_name = self.ff_name

        return self.start(start_sec=start_secs, limit_sec=limit_sec,
                          fade_in_sec=fade_in_sec, fade_out_sec=fade_out_sec,
                          ff_name=ff_name, dead_start=dead_start,
                          last_sink=last_sink)

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
            print("FileControl.elapsed() requested when song ended")
            print("This may screw up percent played calculation.")
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
            self.stat_end = os.stat(self.path)  # get current timestamps
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

        if self.silent:  # bugs in lib_tree_play()
            self.info.fact(text, 'info', 'update', patterns)
        else:
            self.info.cast(text, 'info', 'update', patterns)

        '''   B I G   T I C K E T   E V E N T   '''
        if self.percent_played < float(ATIME_THRESHOLD):
            ''' Didn't play long enough. Restore original access time '''
            old_time, new_time = self.touch_it(self.stat_start)
            # touch_it() returns None, None when no song path
            self.final_atime = new_time
            patterns = [("Restoring last access for:", "White", "Black"),
                        ("Current time:", "Green", "Black"),
                        ("Original time:", "Green", "Black")]
            if self.silent and old_time is not None:
                self.info.fact("Restoring last access for: \t" + self.Title +
                               "\n\tCurrent time:  \t" +
                               tmf.ago(old_time).strip() +
                               "\n\tOriginal time: \t" +
                               tmf.ago(new_time).strip(),
                               patterns=patterns)
            elif old_time is not None:
                self.info.cast("Restoring last access for: \t" + self.Title +
                               "\n\tCurrent time:  \t" +
                               tmf.ago(old_time).strip() +
                               "\n\tOriginal time: \t" +
                               tmf.ago(new_time).strip(),
                               patterns=patterns)
            else:
                self.info.cast("Could not restore last access for: \t" +
                               str(self.Title) +
                               "\nLikely caused by fast clicking Next/Prev")

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

        REVIEW:
            import os
            os.utime(path_to_file, (access_time, modification_time))
            https://www.tutorialspoint.com/python/os_utime.htm

        :param new_stat: Optional stat.st_time to force, otherwise current time.
        :return old_time, new_time:
        """

        '''' During a crash for other reasons, following popped up too '''
        #     old_atime = old_stat.st_atime
        # TypeError: coercing to Unicode: need string or buffer, NoneType found
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
            ''' Force last access time to current time
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

        self.percent_played = \
            float(self.time_played) * 100 / float(self.DurationSecs)
        ''' TODO: get_resume then reset it to zero when done. '''

    def close(self):
        """ 
            When > 80 % of song played (Fast Forward resets to 0%), then set
            last access time to now. When < 80% reset to saved settings when
            file was declared with .new(path)
             
            functions .log('start'), .log('stop') and .log('end') populated
            self.statuses with status and event time.
        """
        self.close_WIP = None       # .close() is Work In Progress
        if self.path is None:
            FileControlCommonSelf.__init__(self)  # clear all from .new() down
            return  # Already closed.

        if self.state and self.state is 'end':
            # Fast clicking next/prev, atime is never done and we call end twice
            FileControlCommonSelf.__init__(self)  # clear all from .new() down
            return

        if self.stat_end is None:
            ''' Below duplicated if self.end() was just called '''
            self.stat_end = os.stat(self.path)  # get current timestamps
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
#       Refresh() class.
#
# ==============================================================================

class Refresh:
    """ Usage:

        self.refresh = Refresh(30, self.get_refresh_thread)

        Functions:
            check(self):

    """

    def __init__(self, ms, get_thread_func):
        """

        """
        ''' self-ize parameter list '''
        self.ms = ms
        self.get_thread_func = get_thread_func

        ''' Working fields '''
        self.last_time = time.time()

    def check(self):
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
#       Playlist() class.
#
# ==============================================================================

class Playlists:
    """ Usage:

        self.playlists = Playlists(parent, name, title, text, tooltips=self.tt,
                                   thread=self.get_refresh_thread(),
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
        - copy_to(P999999, L999) - Copy Playlist to location, deleting any orphans
        - copy_from(P999999, L999) - Copy Playlist from location, deleting orphans
        - delete_all(P999999) - Delete entire Playlist
        - delete_song(P999999, M999999) - Delete one song from Playlist
        - add_song(P999999, M999999, ndx) - Add song to Playlist

Create playlists on iPhone

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

    def __init__(self, parent=None, text=None, pending=None, info=None,
                 apply_callback=None, enable_lib_menu=None, play_close=None,
                 tooltips=None, thread=None, display_lib_title=None):
        """

        """
        ''' self-ize parameter list '''
        self.parent = parent  # FOR NOW self.parent MUST BE: lib_top
        self.text = text  # Text replacing treeview when no playlists on file
        self.get_pending = pending  # What is pending in parent?  - Could be favorites
        self.info = info  # InfoCentre()
        self.apply_callback = apply_callback
        self.play_close = play_close  # Main music playing window to close down
        self.enable_lib_menu = enable_lib_menu
        self.tt = tooltips  # Tooltips pool for buttons
        self.get_thread_func = thread  # E.G. self.get_refresh_thread()
        self.thread = self.get_thread_func()  # E.G. self.get_refresh_thread()
        self.display_lib_title = display_lib_title  # Rebuild lib_top menubar

        ''' All Playlists work fields - Set on program start and saving changes '''
        self.all_numbers = []  # "P000001", "P000002", etc... can be holes
        self.all_names = []  # Names matching all_numbers
        self.all_descriptions = []  # Descriptions matching all_numbers
        self.names_for_loc = []  # Names sorted for this location
        self.names_all_loc = []  # Names sorted for all locations

        self.old_name = None  # Name before we changed it - Deprecate names soon.
        self.name = None  # Playlist name that is being played right now
        self.last_number_str = None  # Before operation started P00001, etc.
        self.curr_number_str = None  # After operation completed P00001, etc.
        self.audit_message = None  # Printable text of what was done.

        ''' Current Playlist work fields - History Record format '''
        self.act_row_id = None  # History record number
        self.act_number_str = None  # E.G. "P000001"
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

        ''' Input Window and fields '''
        self.top = None  # tk.Toplevel
        self.frame = None  # tk.Frame inside self.top
        self.his_view = None  # SQL Hist tk.Treeview managed by Data Dictionary

        self.fld_name = None  # Field tk.Entry for toggling readonly state
        self.fld_description = None
        self.scr_name = tk.StringVar()  # Input fields
        self.scr_description = tk.StringVar()
        self.scr_location = tk.StringVar()

        self.fld_count = None  # Field display only
        self.fld_size = None
        self.fld_seconds = None

        self.artwork = None  # Not used
        self.close_button = None
        self.apply_button = None
        ''' Find all existing playlists '''
        self.build_playlists()  # Build working fields for all playlists
        #print("Initialization self.get_pending:", self.get_pending())

    def create_window(self, name=None):
        """ Mount window with Playlist Treeview or placeholder text when none.
            :param name: "New Playlist", "Open Playlist", etc.
        """
        self.thread = self.get_thread_func()  # E.G. self.get_refresh_thread()
        self.pending_counts = self.get_pending()
        ''' Save current name to old_name to make decisions when different. '''
        self.old_name = self.name

        ''' Rebuild playlist changes since last time '''
        self.build_playlists()
        ''' Save geometry for Playlists() '''
        self.top = tk.Toplevel()  # Playlists top level
        geom = monitor.get_window_geom('pls_top')
        self.top.geometry(geom)
        self.top.minsize(width=BTN_WID * 10, height=PANEL_HGT * 10)
        name = name if name is not None else "Playlists"
        self.top.title(name + " - mserve")
        self.top.configure(background="Gray")
        self.top.columnconfigure(0, weight=1)
        self.top.rowconfigure(0, weight=1)
        ''' After top created, disable all File Menu options for playlists '''
        self.enable_lib_menu()
        ''' Set program icon in taskbar '''
        img.taskbar_icon(self.top, 64, 'white', 'lightskyblue', 'black')
        ''' Create master frame '''
        self.frame = tk.Frame(self.top, borderwidth=BTN_BRD_WID,
                              relief=tk.RIDGE)
        self.frame.grid(sticky=tk.NSEW)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=3)  # Data entry fields
        self.frame.rowconfigure(0, weight=1)
        ms_font = (None, MON_FONTSIZE)

        ''' Instructions when no playlists have been created yet. '''
        if not self.text:  # If text wasn't passed as a parameter use default
            self.text = "\nNo Playlists have been created yet.\n\n" + \
                        "After Playlists have been created, they will\n" + \
                        "appear in this spot.\n\n" + \
                        "You can create a playlist by selecting\n" + \
                        "the 'New Playlist' option or 'Copy Playlist'\n" + \
                        "option from the 'File' dropdown menu bar.\n"

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
        self.fld_name.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.scr_name.set("")  # Clear left over from last invocation
        ''' Playlist Description is readonly except for 'new' and 'rename' '''
        tk.Label(self.frame, text="Playlist description:",
                 font=ms_font).grid(row=2, column=0, sticky=tk.W, padx=5)
        self.fld_description = tk.Entry(
            self.frame, textvariable=self.scr_description, state='readonly',
            font=ms_font)
        self.fld_description.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.scr_description.set("")  # Clear left over from last invocation
        ''' Device Location is always readonly '''
        tk.Label(self.frame, text="Device location:",
                 font=ms_font).grid(row=3, column=0, sticky=tk.W, padx=5)
        tk.Entry(self.frame, textvariable=self.scr_location, state='readonly',
                 font=ms_font).grid(row=3, column=1, sticky=tk.W, padx=5,
                                    pady=5)
        self.scr_location.set(LODICT['iid'] + " - " + LODICT['name'])

        self.input_active = False

        ''' Artwork '''
        # self.name_var.set(... state=self.state self.state =
        #self.artwork = tk.Scale(self.frame, from_=100, to=25, tick interval=5,
        #                        command=self.set_sink)
        #self.artwork.grid(row=0, column=3, row span=4, pad x=5, pad y=5, sticky=tk.NS)

        ''' Close Button - NOTE: This calls reset() function !!! '''
        self.close_button = tk.Button(self.frame, text="✘ Close",
                                      width=BTN_WID2 - 4, command=self.reset)
        self.close_button.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.tt.add_tip(self.close_button, "Ignore changes and return.",
                        anchor="nw")
        self.top.bind("<Escape>", self.reset)
        self.top.protocol("WM_DELETE_WINDOW", self.reset)

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

        ''' Apply Button '''
        action = name.split(" Playlist")[0]
        self.apply_button = tk.Button(self.frame, text="✔ " + action,
                                      width=BTN_WID2 - 2, command=self.apply)
        self.apply_button.grid(row=4, column=3, padx=5, pady=5, sticky=tk.W)
        self.tt.add_tip(self.apply_button, action + " Playlist and return.",
                        anchor="ne")
        self.top.bind("<Return>", self.apply)  # DO ONLY ONCE?

        ''' Refresh screen '''
        if self.top:  # May have been closed above.
            self.top.update_idletasks()

    def build_playlists(self):
        """ Get ALL configuration history rows for Type = 'playlist'
            Create sorted list of names for current location. Called
            each time Playlists.function() used.
        """
        ''' Lists already declared in Init but must reset between calls 
            Put this into newly created CommonSelf()
        '''
        self.all_numbers = []  # "P000001", "P000002", etc... can be holes
        self.all_names = []  # Names matching all_numbers
        self.all_descriptions = []  # Descriptions matching all_numbers
        self.names_for_loc = []  # Names sorted for this location
        self.names_all_loc = []  # Names sorted for all locations
        ''' Read all playlists from SQL History Table into work lists '''
        for row in sql.hist_cursor.execute("SELECT * FROM History " +
                                           "INDEXED BY TypeActionIndex " +
                                           "WHERE Type = ?", ('playlist',)):
            d = dict(row)
            self.make_act_from_hist(d)
            self.all_numbers.append(self.act_number_str)
            self.all_names.append(self.act_name)
            self.names_all_loc.append(self.act_name)
            if self.act_loc_id == LODICT['iid']:
                self.names_for_loc.append(self.act_name)

        self.names_all_loc.sort()
        self.names_for_loc.sort()

    def populate_his_tree(self):
        """
            Use custom Data Dictionary routines for managing treeview.
        """

        ''' Data Dictionary and Treeview column names '''
        history_dict = sql.history_treeview()  # Heart of Data Dictionary
        columns = ("detail", "comments", "count", "size", "seconds")
        toolkit.select_dict_columns(columns, history_dict)

        ''' Create treeview frame with scrollbars '''
        tree_frame = tk.Frame(self.frame, bg="olive", relief=tk.RIDGE)
        tree_frame.grid(sticky=tk.NSEW, columnspan=4)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        self.his_view = toolkit.DictTreeview(
            history_dict, self.top, tree_frame, columns=columns,
            highlight_callback=self.highlight_callback)

        ''' Override formatting for Size of Files to MB '''
        self.his_view.change_column_format("MB", "size")  # human_mb()
        self.his_view.change_column_format("days", "seconds")  # days()

        ''' Override generic column heading names for Playlist usage '''
        self.his_view.tree.heading('detail', text='Playlist Name')
        self.his_view.tree.heading('comments', text='Playlist Description')
        self.his_view.tree.heading('count', text='Song Count')
        self.his_view.tree.heading('size', text='Size of Files')
        self.his_view.tree.heading('seconds', text='Duration')
        self.his_view.tree["displaycolumns"] = columns  # hide row_id

        ''' Treeview select item with button clicks '''
        # Moving columns needs work and probably isn't even needed
        #toolkit.MoveTreeviewColumn(self.top, self.his_view.tree,
        #                           row_release=self.his_button_click)
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
        """ Left button clicked to select a row.

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
            else:
                title = "SQL History Table"
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

        """

        number_str = self.his_view.tree.identify_row(event.y)
        if self.state == "new" or self.state == "save_as":
            self.thread = self.get_thread_func()  # FIX huge problem when play_close()
            # cannot use enable_input because rename needs to pick old name first
            text = "Cannot pick an old playlist when new playlist name required.\n\n" + \
                "Enter a new Playlist name and description below."
            message.ShowInfo(self.top, "Existing playlists for reference only!",
                             text, icon='warning', thread=self.thread)
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
            self.fld_seconds['text'] = toolkit.days(self.act_seconds)
            self.top.update_idletasks()
            #print("Music IDs", self.act_id_list)

    def highlight_callback(self, number_str):
        """
        As lines are highlighted in treeview, this function is called.
        :param number_str: Playlist number used as iid inside treeview
        :return: None
        """
        #print("number_str:", number_str)
        pass

    def active(self):
        """
        Returns active curr_number_str or None.

        Important active curr_number_str is to set to None when there is no
        playlist. Also important curr_number_str is never blank because
        that is also considered None or False.

        Callers need to know when Favorites are in use. Callers test with:

            if self.playlists.active():
                ...
            else:
                ...

        Internally, Playlists() functions need to know if an existing
        opened playlist is the same as themselves using test:
            open_number_str = active()
            if open_number_str:
                if open_number_str = self.act_number_str:
                    ... we are changing ourselves
                else:
                    ... close down
            else:
                ... brand new instance, nothing to worry about

        """
        return self.curr_number_str

    def new(self):
        """ Called by lib_top File Menubar "New Playlist"
            If new songs are pending, do not allow playlist to open
        """
        if self.check_pending():  # lib_top.tree checkboxes not applied?
            return  # We are all done. No window, no processing, nada

        self.state = 'new'
        self.create_window("New Playlist")
        self.enable_input()

    def enable_input(self):
        """ Turn on input fields for 'new', 'rename' and 'save_as' """
        self.input_active = True
        self.fld_name['state'] = 'normal'  # Allow input
        self.fld_description['state'] = 'normal'  # Allow input

    def rename(self):
        """ Called by lib_top File Menubar "Rename Playlist" """
        self.state = 'rename'
        self.create_window("Rename Playlist")
        self.enable_input()

    def delete(self):
        """ Called by lib_top File Menubar "Delete Playlist" """
        self.state = 'delete'
        self.create_window("Delete Playlist")

    def open(self):
        """ Called by lib_top File Menubar "Open Playlist"
            If new songs are pending, do not allow playlist to open
        """
        if self.check_pending():  # lib_top.tree checkboxes not applied?
            return  # We are all done. No window, no processing, nada

        self.state = 'open'
        self.create_window("Open Playlist")

    def save(self):
        """ DEPRECATED. Replaced by self.write_playlist_to_disk() """
        pass

    def save_as(self):
        """
            Called by lib_top File Menubar "Save Playlist As..."
        """
        self.state = 'save_as'
        self.create_window("Save Playlist As…")
        self.enable_input()

    def close(self):
        """
            Called by close_playlist() that finishes processing.

            Blank out self.name and call display_lib_title()
            which forces Favorites into title bar when self.name is blank.

            June 19, 2023 - 'self.playlists.name is not None' checks by
                callers will be replaced by 'self.playlists.active()'.
        """

        self.state = 'close'
        if self.edit_playlist():  # Check if changes pending & confirm
            self.play_close()  # must be called before name is none
            self.curr_number_str = None
            self.name = None
            self.display_lib_title()
            return True
        else:
            return False

    def read_playlist(self, number_str):
        """ Use playlist number to read SQL History Row into work fields """
        d = sql.get_config('playlist', number_str)
        if d is None:
            return None

        ''' Current Playlist work fields - from History Record '''
        self.make_act_from_hist(d)

        return True

    def make_act_from_hist(self, d):
        """ The History Column: 'Type' will always contains: 'playlist'
        """
        self.act_row_id = d['Id']  # History record number
        self.act_number_str = d['Action']  # E.G. "P000001"
        self.act_loc_id = d['SourceMaster']  # E.G. "L004"
        self.act_name = d['SourceDetail']  # E.G. "Oldies"
        self.act_id_list = json.loads(d['Target'])  # Music Id's in play order
        self.act_size = d['Size']  # Size of all song files in bytes
        self.act_count = d['Count']  # len(self.music_id_list)
        self.act_seconds = d['Seconds']  # Duration of all songs in seconds
        self.act_description = d['Comments']  # E.G. "Songs from 60's & 70's

    def check_pending(self):
        """
        When lib_top_tree has check boxes for adding/deleting songs that
        haven't been saved, cannot open playlist or create new playlist.

        :return: True if pending additions/deletions need to be applied
        """
        pending = self.get_pending()
        if pending == 0:
            return False

        # self.top window hasn't been created so use self.parent instead
        text = "Checkboxes in Music Library have added songs or\n" +\
            "removed songs. These changes have not been saved to\n" +\
            "storage or cancelled.\n\n" +\
            "You must save changes or cancel before working with a\n" +\
            "different playlist."
        self.thread = self.get_thread_func()  # FIX huge problem when play_close()
        message.ShowInfo(self.parent, "Songs have not been saved!",
                         text, icon='error', align='left', thread=self.thread)

        return True  # We are all done. No window, no processing, nada

    def check_save_as(self):
        """
            Display message this isn't working yet. Always return false.

            HUGE PROBLEM with passing self.thread to ShowInfo when
            refresh_play_top() is no longer active. Need to refresh first.
        """
        # self.top window hasn't been created so use self.parent instead
        self.thread = self.get_thread_func()  # FIX huge problem when play_close()

        # June 19, 2023 closing playing window when message mounted still causes crash.
        #    Maybe Playlists() should have it's own thread handler?


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
        message.ShowInfo(self.parent, "Save As... doesn't work yet !!!",
                         text, icon='error', align='left', thread=self.thread)

        return False  # We are all done. No window, no processing, nada

    def edit_playlist(self):
        """
            Edit Playlist in current (active / "act_") work fields

            Type-'playlist', Action-P999999, Master-L999, Detail-Playlist Name,
                Target-JSON list of sorted Music IDs, Size=MB, Count=# Songs,
                Seconds=Total Duration, Comments=Playlist Description

            close() must be done first because no self.top window open
        """

        ''' Save As... is not working. Bail out immediately '''
        if self.state == 'save_as':
            return self.check_save_as()

        ''' Closing Playlist and returning to Favorites? Do this test first
            because other tests are irrelevant. If pending song updates,
            confirm abandoning save to playlist
        '''
        if self.state == 'close':
            if self.get_pending() > 0:
                # self.top window hasn't been created so use self.parent instead
                text = "Checkboxes in Music Library have added songs or\n" + \
                       "removed songs. These changes have not been saved to\n" + \
                       "storage."
                dialog = message.AskQuestion(
                    self.parent, "Playlist has not been saved!", text, icon='warning',
                    align='left', thread=self.get_thread_func())

                if dialog.result != 'yes':
                    return False

            return True  # We can close Playlists

        ''' Retrieve name and description from tkinter variables. '''
        new_name = self.scr_name.get()
        new_description = self.scr_description.get()
        if self.state == 'new' or self.state == 'save_as':
            # Blank out name and description for name change tests
            self.act_name = ""
            self.act_description = ""

        ''' We need a playlist name no matter the operation performed '''
        if new_name == "":
            if self.input_active:
                text = "Enter a unique name for the playlist."
            else:
                text = "First click on a playlist entry."
            self.thread = self.get_thread_func()  # FIX huge problem when play_close()
            message.ShowInfo(self.top, "Name cannot be blank!",
                             text, icon='error', thread=self.thread)
            return False

        ''' A playlist description is recommended for Apple Users '''
        if new_description == "" and self.input_active:
            text = "Enter a playlist description gives more functionality\n" +\
                "in other Music Players such as iPhone."
            self.thread = self.get_thread_func()  # FIX huge problem when play_close()
            message.ShowInfo(self.top, "Description is blank?",
                             text, icon='warning', thread=self.thread)

        ''' Tests when playlist name and description are keyed in '''
        if self.input_active:
            ''' Same name cannot exist in this location '''
            if new_name in self.names_for_loc and \
                    new_name != self.act_name:
                text = "Playlist name has already been used."
                self.thread = self.get_thread_func()  # FIX huge problem when play_close()
                message.ShowInfo(self.top, "Name must be unique!",
                                 text, icon='error', thread=self.thread)
                return False
            if new_name in self.names_all_loc and \
                    new_name != self.act_name:
                print("Warning Name in another location. Are you sure?")
                # TODO: message.ShowInfo() with location iid and name
                #       requires expanding from list to list of tuples.

        # TODO: Warning for 'rename' operation but name or description wasn't changed

        ''' Creating a new playlist? Similar tests for Save As... '''
        if self.state == 'new':
            # Passed all tests so create new number string
            if len(self.all_numbers) > 0:
                last_str = self.all_numbers[-1]  # Grab last number
                val = int(last_str[1:]) + 1  # increment to next available
                self.act_number_str = "P" + str(val).zfill(6)
            else:
                self.act_number_str = "P000001"  # Very first playlist
            self.act_loc_id = LODICT['iid']
            self.act_id_list = []  # Empty list
            self.act_size = 0  # Size of all song files
            self.act_count = 0  # len(self.music_id_list)
            self.act_seconds = 0.0  # Duration of all songs

        if self.input_active:
            self.act_name = new_name
            self.act_description = new_description

        if self.state == 'open':
            # TODO broadcast message to Information Centre
            pass

        if self.state == 'delete':
            # self.top window hasn't been created so use self.parent instead
            text = "\nThere are " + '{:n}'.format(self.act_count) + \
                   " songs in the playlist.\n"
            if self.curr_number_str == self.act_number_str:
                text += "\nThe playlist is currently playing and will be stopped.\n"
            self.thread = self.get_thread_func()  # FIX huge problem when play_close()
            dialog = message.AskQuestion(
                self.top, "Confirm playlist deletion", text, icon='warning',
                thread=self.thread)
            if dialog.result != 'yes':
                return False

            return True

        if self.state == 'save':
            # DEPRECATED, save() function is not used
            pass

        if self.state == 'save_as':
            pass

        return True

    def save_playlist(self):
        """
            Save Playlist in current (active / "act_") work fields

            Type-'playlist', Action-P999999, Master-L999, Detail-Playlist Name,
                Target-JSON list of sorted Music IDs, Size=MB, Count=# Songs,
                Seconds=Total Duration, Comments=Playlist Description

        """
        ''' Current Playlist work fields - History Record format '''
        sql.save_config('playlist', self.act_number_str, self.act_loc_id,
                        self.act_name, json.dumps(self.act_id_list),
                        self.act_size, self.act_count, self.act_seconds,
                        self.act_description)

    def delete_playlist(self):
        """
            Delete Playlist using History Row ID
        """
        sql.hist_cursor.execute("DELETE FROM History WHERE Id = ?",
                                [self.act_row_id])
        sql.con.commit()

    # noinspection PyUnusedLocal
    # def reset(self, *args):
    def reset(self, shutdown=False):
        """
        Named "reset" instead of "close" because, "close()" is used by
        callers to "close" playlist and use Default Favorites instead.

        When shutting down, if Playlists.top is not none,
        self.playlists.reset(shutdown=True) is used to close Playlists window.
        """
        if self.tt:
            self.tt.close(self.top)
        if self.top:
            geom = monitor.get_window_geom_string(self.top, leave_visible=False)
            monitor.save_window_geom('pls_top', geom)
            self.top.destroy()
        # print("self.top after .destroy()", self.top)
        self.top = None  # Indicate Playlist Maintenance is closed
        ''' After top destroyed, enable File Dropdown Menu options for playlists '''
        if not shutdown:
            self.enable_lib_menu()

    # noinspection PyUnusedLocal
    def apply(self, *args):
        """ Validate, Analyze mode (state), update database appropriately. """
        if self.edit_playlist() is False:
            return

        if self.state == 'delete':
            # TODO: Delete resume, chron_state, hockey_state and open_states
            #       Or just set a deleted flag and not physically delete.
            self.delete_playlist()
            self.info.cast("Deleted playlist: " + self.act_name, action="delete")
            if self.curr_number_str == self.act_number_str:
                self.name = None
                self.last_number_str = self.curr_number_str  # Replaces .name in future
                self.curr_number_str = None  # Replaces .name in future
                self.play_close()  # must be called before name is set
                self.name = self.act_name  # Tell parent name of playlist
                self.curr_number_str = None  # Was deleted, no longer exists.
        elif self.state == 'open':
            self.name = None
            self.curr_number_str = None  # Replaces .name in future
            self.play_close()  # must be called before name is set
            self.name = self.act_name  # Tell parent name of playlist
            self.last_number_str = self.curr_number_str  # Replaces .name in future
            self.curr_number_str = self.act_number_str
            self.reset()  # Close everything down, E.G. destroy window
            # June 23, 2023 - info.cast isn't appearing?
            self.info.cast("Opened playlist: " + self.act_name + " with " +
                           str(self.act_count) + " songs.")
            self.apply_callback()  # Parent will start playing (if > 1 song in list)
            #self.info.cast("Opened playlist: " + self.act_name)  # doesn't work either
        elif self.state == 'new':
            self.save_playlist()  # Save brand new playlist
            self.name = None
            self.curr_number_str = None  # Replaces .name in future
            self.play_close()  # must be called before name is set
            self.name = self.act_name  # Tell parent name of playlist
            self.last_number_str = self.curr_number_str  # Replaces .name in future
            self.curr_number_str = self.act_number_str
            # June 23, 2023 - info.cast isn't appearing?
            self.info.cast("Created new playlist: " + self.act_name, action="add")
            self.apply_callback()  # Tell parent to start editing playlist
            #self.info.cast("Created new playlist: " + self.act_name)  # doesn't work either
            # apply_callback will end right away after closing lib selections
        else:
            ''' Remaining options are Save, Save As, Rename '''
            self.save_playlist()
            self.name = self.act_name  # In case of 'rename' title updates
            self.curr_number_str = self.act_number_str
            self.info.cast("Saved playlist: " + self.act_name + " with " +
                           str(self.act_count) + " songs.", action="update")

        # TODO: New design with self.last_number_str and self.curr_number_str

        if self.parent:
            # During shutdown we somehow get to this point and below gets error
            # because lib_top no longer exists.
            self.display_lib_title()  # Important that self.name is ACCURATE
            # June 19, 2023 TODO: For rename change current playing window title too.

        ''' Sanity check '''
        if self.curr_number_str == "":
            toolkit.print_trace()
            print('self.curr_number_str == ""')

        self.reset()  # Close everything down, E.G. destroy window


# ==============================================================================
#
#       InfoCentre() class.  Name change?  InfoCentre?

# noinspection SpellCheckingInspection
'''
    Thoughts.

    Message duration based on words and lines like tooltips? Consider fact user
    should quickly browse then message collapses out of the way. If needed can
    click on banner button and message stays up until focus is removed. Put a
    close button on the message banner.

    Some messages are trivial "Playlist: 'Golden Oldies' has been opened".

    Post a tip to hover into and out of message to collapse Information Centre.
    
    Horizontal and vertical scrollbars initially.

    Text can be copied to clipboard. Enable entry state.

    Ago/Away time: - Just now, A minute ago, A few minutes ago, Xxx minutes ago    
    
    What about icon='error', icon='warning' option?
    
    Should a message have an author / sender name? E.G. webscrape, encode,
    playlist.
        - Lyrics have been scraped
        - CD Track 9 has been encoded and is ready to be played. Would you like
            to play it now? Yes/No 
    
    Could a History row ID and/or Music Row ID be passed? 
    
    What about custom image for the information centre? switchboard operator? 

    Hamburger button at top right?    

    What does this mean button with hyperlink to pippim website for help text.
    
    Save message button? Where would save go?    
    
    Set alarm like "take clothes out of washer and put in dryer".
    
    Speak alarms?
    
    Receive messages over IP?
    
    Status updates like SSHSFS host kept awake?
    
    Message recurs until acknowledged? E.G. New songs added to device and
        library can be refreshed.

    Interface to Google Calendar / Google Mail?        

    Interface to IoT? E.G. TV Powered
    
    Notes about song pops up when play starts? 

    Notebook Tabs to select message type? E.G. all inotify messages on one tab.

    Send message if mouse hasn't entered a monitor in say 15 minutes and offer
        to shut off the picture to save 100 watts? (TV stays on with sound).

    Thank goodness there is no thread=self.get_refresh_thread() needed so the
        Playlists() class nightmare isn't relived !

======================================================================        

Opening playlists slows down from <1 second to over 7 seconds.

----------------------------------------------------------------------
SLOWDOWN BUG: https://gitlab.gnome.org/GNOME/gnome-shell/-/issues/3125

Default ibus-daemon causes high cpu usage and startup delay for a tcl / tk application
Closed

Default ibus-daemon causes high cpu usage and startup delay for a tcl / tk application
Affected version

I tested Ubuntu 18.04 / 20.04 & Centos 7 / 8 (also current beta versions) but I think
 every gnome3 Version will be affected.

Bug summary

If we start our big TCL/TK application using gnome3 the startup time increases 
from 1 sec (KDE, Mate, ...) up to 60 sec. In the meantime ibus-daemon & ibus-X11 
are using both a full CPU. After the application is started, it can be used 
without any problems. If I stop the ibus-damon (ibus exit) and restart the 
application everything is working fine.

After playing around a bit I could nail it down to the "--xim" option. If I 
remove this option, the application starts fast.

As a workaround I restart ibus-daemon without the --xim option at session login.

I tested many other environments like KDE, Xfce, Mate also using the ibus-daemon
but there the problem does not occur (also with the --xim option). So I think 
it could be a problem between the gnome3 ibus implementation & tcl/tk (8.5.X)?

Has anybody seen this before? Please tell me, what you need to analyze the 
problem and I will do (strace, ...).

Since our application is a commercial software I cannot easily provide a 
test driver to reproduce this behavior (but I will do, if really necessary).

Thanks in advance for your help!

Best regards, Roland    

----------------------------------------------------------------------
SLOWDOWN BUG: https://gitlab.gnome.org/GNOME/gnome-shell/-/issues/2674

Tkinter/Python3 app launch slow down each time it is killed instead of closed
Open

Tkinter/Python3 app launch slow down each time it is killed instead of closed

The bug is present in the following setup:

    Ubuntu 18.04.3 LTS (tested also on 20.04 LTS beta)
    gnome-shell package is version 3.28.4-0ubuntu18.04.2
    Linux x 4.15.0-96-generic #97 (closed)-Ubuntu SMP Wed Apr 1 03:25:46 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux

Tested and problem reproducible on:

    GNOME Flashback (Compiz) - default on my machine
    Ubuntu on Wayland
    GNOME on Xorg

Tested and problem is not detected on:

    Live Kubuntu 18.04 LTS on other machine
    vanilla LXDE installed in my Ubuntu 18.04.3 LTS

The problem is whenever a Tkinter/Python3 application I am working on is 
killed with Ctrl-C or killall python3 the subsequent launch of the 
application takes more time. When the window is closed with the X button 
no time is added to subsequent runs. When the user logs out and logs in 
launch time is back to the original.

I have attached a simple python script (slow.py) that demonstrates the issue. 
I also attached a bash script (runme) that runs the script in a loop and uses 
grep to print relevant time.

Steps to reproduce:

    run ./runme
    Close the window using the X symbol a number of time (e.g. 10 times)

    20640    0.206    0.000    0.206    0.000 {method 'call' of '_tkinter.tkapp' objects}
    20640    0.209    0.000    0.209    0.000 {method 'call' of '_tkinter.tkapp' objects}
    20640    0.233    0.000    0.233    0.000 {method 'call' of '_tkinter.tkapp' objects}
    20640    0.217    0.000    0.217    0.000 {method 'call' of '_tkinter.tkapp' objects}
    20640    0.207    0.000    0.207    0.000 {method 'call' of '_tkinter.tkapp' objects}
    20640    0.230    0.000    0.230    0.000 {method 'call' of '_tkinter.tkapp' objects}
    20640    0.215    0.000    0.215    0.000 {method 'call' of '_tkinter.tkapp' objects}
    20640    0.215    0.000    0.215    0.000 {method 'call' of '_tkinter.tkapp' objects}

The second column indicating time spent in all calls of the "call" method is 
consistent between calls.

    Kill the application, I use killall python3 run in a separate window. Do 
    this a number of times (e.g. 10). Close the application with X (the first
     close reports wrong time, so please do this a couple of times)

    20640    1.331    0.000    1.331    0.000 {method 'call' of '_tkinter.tkapp' objects}
    20640    1.383    0.000    1.383    0.000 {method 'call' of '_tkinter.tkapp' objects}
    20640    1.321    0.000    1.321    0.000 {method 'call' of '_tkinter.tkapp' objects}
    20640    1.377    0.000    1.377    0.000 {method 'call' of '_tkinter.tkapp' objects}

Now the time spend in the "call" method is significantly higher.

    When the user logs out and in the time is back to about 0.210 until the 
    app is killed with killall python3 or Ctrl-C

The problem is that the launch time of the app increased. The expected behavior
is that there is no rise in launch time of the application. On other window
managers - LXDE and KDE the problem does not manifest itself.

For the application I am working on the launch time increase is significant. 
Killing the application once adds about 6 seconds to the launch time.

'''
#
# ==============================================================================


class InfoCentre:
    """ Usage:

            self.info = InfoCentre(
                self.banner_frm, self.banner_btn, self.build_banner_btn,
                self.build_banner_canvas, self.tt, title_font, text_font):

            self.info.cast() - Create dict and call zoom(show_close=False).
            self.info.fact() - Create dict only.
            self.info.zoom() - Expand/collapse frame. Show dict.
            self.info.view() - Call zoom(), but use close button to exit.

        TODO from PHONE:

            Delete cast type info already viewed.
            
            Add line numbers last viewed because may not have scrolled down.
            
            Initially keep all dict entries because selected deleting is complicated.

    """

    def __init__(self, lib_top=None, lib_tree=None, banner_frm=None,
                 banner_btn=None, build_banner_btn=None, tooltips=None):
        """
            
        """
        ''' self-ize parameter list '''
        self.lib_top = lib_top
        self.lib_tree = lib_tree  # Used in development version will probably drop
        self.banner_frm = banner_frm  # Frame shared by button ruler and zoom
        self.banner_btn = banner_btn  # The button appearing as thin ruler line
        self.build_banner_btn = build_banner_btn  # Function to call when finished
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
        self.song_playing = None  # To shift lib_tree so current song is highlighted

        self.start_time = None  # Time test started
        self.time = None  # Time message was received
        self.last_delta_time = 0.0
        self.original_sleep = None  # Override sleep time for polling tooltips

        ''' Track old and new y-axis position to keep same rows displayed '''
        self.old_y_top = self.old_y_end = 0.0

    def new_dict(self, new_type, text, severity=None, action=None, patterns=None):
        """
        Create a new dictionary
        :param new_type: 'cast' or 'fact' 
        :param text: Formatted text (\n, \t, etc.)  for tk.Text widget.
        :param severity: 'info', 'warning', 'error'
        :param action: 'open', 'update', 'add', 'delete', 'rename'
        :param patterns: List of tuples ("search words", FG color, BG color)
        :return now: time dictionary created
        """
        now = time.time()
        self.dict = \
            OrderedDict([
                ("time", now), ("source", []), ("type", "cast"), ("severity", "info"),
                ("action", ""), ("text", ""), ("text_start", ""), ("text_end", ""),
                ("patterns", []), ("view_time", 0.0)])
        # time: micro-seconds (epoch) serves as unique key
        # source: program name, class name, print_trace() results
        # type: 'cast', 'fact'
        # severity: 'info', 'warning', 'error'
        # action: 'add', 'update', 'rename', 'delete', 'open'
        #   NOTE: 'run' is currently considered to be same as 'open'
        # text: "mserve START-UP:\n\t999 Artists\n\t999 Albums\n\t 9,999 Songs"
        # text_start: start position within tk.Text widget where text is painted
        # text_end: end position used with start_position to apply patterns
        #   NOTE: Probably won't be retrieved but useful for debugging.
        # patterns: [("Added", "white", "green"), ("Deleted", "red", "grey")]
        #   CHALLENGE: highlighting applies to all messages in Text, need start line number
        # view_time: 0.0 = False. After viewing, some info_type+action deleted

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
        return now

    def cast(self, text, severity=None, action=None, patterns=None):
        """
        Briefly display message in expanding/collapsing Information Centre.
        If user interested they can use view() function to slowly read message.
        After reading, most messages are deleted, but some are kept in session history.

        :param text: Formatted text (\n, \t, etc.)  for tk.Text widget.
        :param severity: 'info', 'warning', 'error'
        :param action: 'open', 'update', 'add', 'delete', 'rename'
        :param patterns: List of tuples ("search words", FG color, BG color)
        :return: time assigned to information centre entry.
        """
        ''' 
            PROCESSING STEPS:
                Queue operation if previous cast is still active.
                Create dictionary
                Insert dictionary in list
                Call splash function
        '''

        # REVIEW: Recursive call if first cast is still active.

        #if self.zoom_is_active:  # If zoom is active this will be fact
        #    print("\nInfoCentre.cast() Last self.zoom() still active\n")
        #    print(self.dict['text'][0])
        #    pass
        ''' If zoom active and being spammed by .cast() '''
        if self.zoom_is_active:
            self._close_cb()
            self.tt.poll_tips()

        time_stamp = self.new_dict('cast', text, severity, action, patterns)
        self.list.insert(0, self.dict)  # self.dict stays in memory untouched

        ''' If last broadcast is still visible cannot launch another '''
        if not self.zoom_is_active:  # If zoom is active this will be fact
            self.zoom()  # Message broadcast
        return time_stamp  # time_stamp can be used by caller to massage text

    def fact(self, text, severity=None, action=None, patterns=None):
        """
        Record fact that is not broadcast.
        If user interested they can use view() function to slowly read message.
        After reading, most messages are deleted, but some are kept in session history.

        :param text: Formatted text (\n, \t, etc.)  for tk.Text widget.
        :param severity: 'info', 'warning', 'error'
        :param action: 'open', 'update', 'add', 'delete', 'rename'
        :param patterns: List of tuples ("search words", FG color, BG color)
        :return: time assigned to information centre entry.
        """
        ''' 
            PROCESSING STEPS:
                Queue operation if previous cast is still active.
                Create dictionary
                Insert dictionary in list
                Call splash function
        '''

        time_stamp = self.new_dict('fact', text, severity, action, patterns)
        self.list.insert(0, self.dict)  # self.dict stays in memory untouched
        return time_stamp  # time_stamp can be used by caller to massage text

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
        """
            "Zoom" messages by expanding/collapsing information centre panel
            self.dict is populated with all variables caller sent

            :param show_close: Display a close button and extend visible time
        """
        #print("InfoCentre.zoom() called.", tmf.ago(time.time()))
        ''' Zoom already active and being spammed by .cast()? '''
        if self.zoom_is_active and show_close is False:
            print("\nInfoCentre.zoom() defense lines breached in cast\n")
            print(self.dict['text'][0])
            #print("\nInfoCentre.zoom() Resetting to allow next attacker\n")
            #self.zoom_is_active = False
            return

        ''' Indicate zoom is active '''
        self.zoom_is_active = True

        if self.frame:  # This test should no longer be needed
            print("\nInfoCentre.zoom() SECOND defense line breached !!\n")
            print(self.dict['text'][0])
            self._close_cb()  # Pretend ToolTips() told us to close
            return



        ''' Get current lib_top coordinates and current playing song '''
        # During init there was no size for window
        self.height = int(self.lib_top.winfo_height() / 3)
        self.width = self.lib_top.winfo_width()
        self.song_playing = self.lib_tree.tag_has("play_sel")
        # print("song_playing:", self.song_playing)

        ''' Recycled test needs local instead of static variable defined '''
        text = self.dict['text']

        ''' June 21, 2023 - test work fields, leave for now '''
        self.test = True
        self.msg_recv = text  # Formatted text (with \n, \t) to be displayed
        # print("Caller says:", self.msg_recv)
        self.test_results = []  # Empty last test
        self.start_time = time.time()  # To calculate total elapsed time
        self.last_delta_time = self.start_time  # To calculate ms between calls

        ''' Destroy banner button in Tooltips() and banner button '''
        self.tt.close(self.banner_btn)
        self.banner_btn.destroy()  # Real Estate commandeered for zoom frame

        ''' Build tk.Frame and tk.Text widgets. Optional tk.Button to close frame '''
        self.frame = tk.Frame(self.banner_frm, bg="black", height=7)
        self.frame.grid()
        if show_close:
            ''' Close Button - NOTE: This calls reset() function !!! '''
            self.close_button = tk.Button(self.frame, text="✘ Close", bg="gold",
                                          width=BTN_WID2 - 4, command=self._close_clicked)
            self.close_button.place(height=MON_FONTSIZE * 3, width=BTN_WID2 * 8,
                                    x=10, y=10)
            visible_span = 1000 * 60 * 2  # Visible for two minutes per line
        else:
            visible_span = 1000  # Visible 1 second per tk.Text line

        ''' Create custom (highlighting supported) tk.Text widget with scrollbars '''
        self.text = toolkit.CustomScrolledText(
            self.frame, bg="black", height=self.height, width=self.width, fg="gold",
            font=(None, MON_FONTSIZE), state="normal")
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
                "─" * line_draw + "┨ " + tmf.ago(read_dict['time']))
            self._str_to_text_widget(read_dict['text'])
            text_end = self.text.index("end")

            ''' Update text_start and text_end without corrupting current self.dict '''
            read_dict['text_start'] = text_start
            read_dict['text_end'] = text_end
            self.list[i] = read_dict
            ''' Now apply patterns between text start and text end '''
            for entry in read_dict['patterns']:
                pattern, fg, bg = entry  # fg + bg color names forms the tag name
                self.text.tag_configure(fg + bg, foreground=fg, background=bg)
                self.text.highlight_pattern(pattern, fg + bg, start=text_start, end=text_end)

            if not show_close:  # No close button is displayed
                break  # Called by .cast() so only most recent message displayed

        self.text.update()  # Is this necessary? CONFIRMED YES
        #self.text.configure(state="disabled")  # comment to test entry

        ''' .view() has close button, but .cast() doesn't. '''
        if show_close:
            self.widget = self.close_button
            anchor = "sw"
        else:
            self.widget = self.text
            anchor = "sc"

        ''' Add CustomScrolledText widget to Tooltips() as 'piggy_back' '''
        self.tt.add_tip(
            self.widget, text=text, anchor=anchor, tool_type="piggy_back",
            pb_alpha=self._alpha_cb, pb_leave=self._leave_cb, 
            pb_ready=self._ready_cb, pb_close=self._close_cb, 
            visible_span=visible_span, extra_word_span=100,
            fade_in_span=300, visible_delay=201, fade_out_span=200
            # Limitation: 'visible_delay' must be greater than 'fade_out_span'
        )

        #tt_dict = self.tt.get_dict(self.widget)
        #print('\nInfoCentre.zoom() tooltips self.widget dictionary BEFORE:')
        #print(tt_dict, "\n")
        ''' Start Tooltips() by saying mouse hovered over the text widget. '''
        self.tt.log_event('enter', self.widget, 10, 5)  # x=10, y=5
        #self.tt.poll_tips()
        #print('\nInfoCentre.zoom() tooltips self.widget dictionary AFTER:')
        #print(tt_dict, "\n")  # 'enter_time' = 1688148501.804852
        # Funny tt_dict is live reference that didn't need updating....

    def _close_clicked(self):
        """ When close button clicked tell Tooltips to start fading out """
        self.tt.log_event('press', self.widget, 100, 50)  # x=100, y=50

    def _str_to_text_widget(self, text):
        """ Line draw border or single text message to tk.Text box """
        self.text.configure(state="normal")
        self.text.insert(tk.END, text + "\n")
        self.text.update()  # Is this necessary? Don't know yet...
        self.text.configure(state="disabled")

    def test_tt(self, text):
        """
        Use to log Tooltips() responses

        :param text: simple message "Hello World".
        :return: None
        """
        global SLEEP_PAUSED
        self.original_sleep = SLEEP_PAUSED
        SLEEP_PAUSED = 20  # Was 33. Setting to 20 gives 29 to 41 during fade out.

        # During init there was no size for window
        self.height = int(self.lib_top.winfo_height() / 3)
        self.width = self.lib_top.winfo_width()
        self.song_playing = self.lib_tree.tag_has("play_sel")
        #print("song_playing:", self.song_playing)

        self.test = True
        self.msg_recv = text  # Formatted text (with \n, \t) to be displayed
        #print("Caller says:", self.msg_recv)
        self.test_results = []  # Empty last test
        self.start_time = time.time()  # To calculate total elapsed time
        self.last_delta_time = self.start_time  # To calculate ms between calls

        ''' Destroy banner button in Tooltips() '''
        self.tt.close(self.banner_btn)
        self.banner_btn.destroy()  # Destroy banner button. Real Estate commandeered

        ''' Build new frame and Text widget. Add to Tooltips() '''
        self.frame = tk.Frame(self.banner_frm, bg="black", height=7)
        self.frame.grid()
        self.text = tk.Text(self.frame, bg="black", height=self.height,
                            width=self.width, fg="gold", font=(None, MON_FONTSIZE))
        self.text.place(height=self.height, width=self.width, x=40, y=10)
        self.text.config(highlightthickness=0, borderwidth=0)

        text = "\t▼ ▲ ▼ ▲  Expanding/Collapsing Information Centre  ▲ ▼ ▲ ▼ \n\n" + \
               "\t\t          Why is it spelled that way?\n\n" + \
               '\t\t   In programming, "center" is an action.\n\n' +\
               '\t\t       In this case, "Centre" is a place.'

        self._str_to_text_widget(text)
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
        """
        Called from Tooltips whenever fading-in or fading-out alpha changes

        :param alpha: % fading-in or fading-out from 0.0 to 1.0
        :return: None
        """
        ''' Expand / Collapse frame with tk.Text widget inside. '''
        new_height = int(self.height * alpha)
        self.frame.config(height=new_height, width=self.width)

    def _alpha_cb_dev(self, alpha):
        """
        Called from Tooltips whenever fading-in or fading-out alpha changes

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
        """
        Called from Tooltips whenever fading-in or fading-out alpha changes

        :param alpha: % fading-in or fading-out from 0.0 to 1.0
        :return: None
        """
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

        if self.song_playing:
            #    self.lib_tree.yview_scroll(1, "units")  # Just to test
            #else:
            #    self.lib_tree.yview_scroll(-1, "units")  # Just to test
            pass

    def _leave_cb(self):
        """
        Called from Tooltips if mouse moves out of Information Centre.

        The idea is to now tell tt to start fading out.

        :return: None
        """
        #print("InfoCentre() _leave_cb() mouse left widget window.",
        #      "total time:", time.time() - self.start_time)

        # InfoCentre() _leave_cb() mouse left widget window. total time: 0.532470941544
        # InfoCentre() _leave_cb() mouse left widget window. total time: 0.504528999329
        # InfoCentre() _leave_cb() mouse left widget window. total time: 0.451492786407
        # InfoCentre() _leave_cb() mouse left widget window. total time: 0.519959926605
        # InfoCentre() _leave_cb() mouse left widget window. total time: 0.521574020386
        # InfoCentre() _leave_cb() mouse left widget window. total time: 0.519021034241
        # InfoCentre() _leave_cb() mouse left widget window. total time: 0.537034034729
        # InfoCentre() _leave_cb() mouse left widget window. total time: 0.505052089691
        # InfoCentre() _leave_cb() mouse left widget window. total time: 0.508666992188

        ''' Feed fake button press event to cause info message to collapse
            right away. Only works occasionally!
            
            When called by button bar leaves right away and closes
            When called by View Information Centre doesn't leave at all
            
            Low priority because view will have a close button and banner button is short
        '''
        elapsed = time.time() - self.start_time
        if elapsed > 1000.0:  # Ignore if less than 1 second
            self.tt.log_event('press', self.widget, 100, 50)  # x=100, y=50
            # Notice first event is ignored. Then next is treated as real
            # InfoCentre() _leave_cb() mouse left widget window. total time: 0.527550935745
            # InfoCentre() _leave_cb() mouse left widget window. total time: 2.58352994919
        pass


    def _ready_cb(self):
        """
        Called from Tooltips when ready for message to be displayed.
        :return: None
        """
        #print("InfoCentre() _ready_cb() message can be displayed now.",
        #      "total time:", time.time() - self.start_time)

        #self.test_label = tk.Label(self.frame, text="I am inside a Frame", font='Arial 17 bold')
        #self.test_label.place(rel x=0.5, rely=0.5, anchor=tk.CENTER)
        #self.test_label.update()
        #self.frame.grid_propagate(True)
        #self.lib_top.update()
        #root.update()
        pass

    def _close_cb(self):
        """
        Called from Tooltips when fading-out process has ended.
        :return: None
        """
        #print("InfoCentre() _close_cb() tooltip processing has ended.",
        #      "total time:", time.time() - self.start_time)

        ''' Fix rounding errors - Ensure old bottom row is restored '''
        #self.lib_tree.update_idletasks()  # Need to prevent row creep next run.
        #new_y_top, new_y_end = self.lib_tree.yview()
        #end_moved = new_y_end - self.old_y_end
        #self.lib_tree.yview_moveto(self.old_y_top - end_moved)
        #self._alpha_cb_dev(0.01)  # Use this with development version

        ''' May have manually closed frame at same time Tooltips closes '''
        if self.frame:
            self.frame.config(height=7)  # Last height can be 0 - 30px
            self.lib_top.update()  # Update before destroy or last stays
            self.frame.destroy()  # Nuke the frame used for info message
            self.tt.close(self.widget)  # Remove 'piggy_back' tooltip
            self.frame = None

        ''' Rebuild banner button '''
        self.build_banner_btn()
        self.test = False

        ''' Ugly patch to show that zoom has finished '''
        self.zoom_is_active = False

        ''' If 33ms sleep was overriden, restore original value. '''
        if self.original_sleep is not None:
            global SLEEP_PAUSED
            SLEEP_PAUSED = self.original_sleep
            self.original_sleep = None

        
# ==============================================================================
#
#       Independent (Stand Alone) Functions
#
# ==============================================================================


def get_help(id_name):
    # noinspection SpellCheckingInspection
    """
        g.HELP defined in global_variables.py imported as g.  It contains:
        https://www.pippim.com/programs/mserve.html#

    :param id_name: E.G. "HelpT", "HelpB" and "HelpS" used above
    :return None: You will see an error message if there is a typo in the link:
            gvfs-open: # https://www.pippim.com/programs/mserve.html#HelpT:
            error opening location: Error when getting information for file
            '/.../# https:/www.pippim.com/programs/mserve.html#HelpT':
            No such file or directory

    """
    link = g.HELP_URL + id_name
    webbrowser.open_new(link)
    # see: https://docs.python.org/3/library/webbrowser.html


def play_padded_number(song_number, number_digits, prefix=NUMBER_PREFIX):
    """ Pad song number with spaces to line up song name evenly
        Called from refresh_acc_times() and build_chron_line()
    """
    padded_number = ""
    this_digits = len(str(song_number))
    pad_digits = number_digits - this_digits
    for _ in range(pad_digits):
        padded_number = padded_number + DIGIT_SPACE
    return prefix + padded_number + str(song_number)


def make_ellipsis(string, cutoff):
    """ Change: 'Long long long long' to: 'Long long...' """
    if len(string) > cutoff:
        return string[:cutoff - 3] + "..."
    return string


def human_mb(size):
    """ Change '99,999,999' bytes to '99.9 MB'
        Called by MusicTree() class and Playlists() class
        June 18, 2023 - Ported to toolkit.py without CFG_XXX constants.
    """
    converted = float(size) / float(CFG_DIVISOR_AMT)
    rounded = round(converted, CFG_DECIMAL_PLACES)
    rounded = '{:n}'.format(rounded)  # Test will locale work for float?
    return rounded + " " + CFG_DIVISOR_UOM


def sec_min_str(seconds):
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


def ffplay_extra_opt(start=None, fade_in=3, fade_out=0.0, duration_secs=0.0):
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


def start_ffplay(song, tmp_name, extra_opt, toplevel=None, thread=None):
    """ start_ffplay parameters:
            song = unquoted song name, we'll add the quotes
            tmp_name = /tmp/filename to send output of song name EG:
                TMP_CURR_SONG="/tmp/mserve.currently_playing"
                TMP_CURR_SAMPLE="/tmp/mserve.current_sample"
            extra_opt can be blank or, they can be:
                -ss = start seconds offset within song, normal is 0
                -t = how long to play song (duration in seconds)
                -af "a fade=type=in:start_time=99:duration=3"
            last_sink is known pulse audio sink that may not have
                closed down and we must wait for it to close.

    :param song: unquoted song name, we'll add the quotes
    :param tmp_name: = /tmp/filename to send output of song name
    :param extra_opt: can be blank or, overrides to start, fade, etc.
    :param toplevel: When passed gets .after(sleep) time.
    :param thread: Failed attempt to pass on to pav.find()
    :return pid, sink: Linux Process ID and Pulse Audio Sink Number
    """

    ''' ffplay start options to redirect output to temporary file '''
    # noinspection SpellCheckingInspection
    cmd = 'ffplay -autoexit ' + '"' + song + '" ' + extra_opt + \
          ' -nodisp 2>' + tmp_name

    ''' launch ffplay external command in background it polls for pid '''
    found_pid = ext.launch_command(cmd, toplevel=toplevel)
    found_sink = ""  # May 21, 2023 functions expect "" for no sink
    if found_pid == 0:
        print('Waited 10 seconds, aborting start_ffplay() get PID')
        return found_pid, found_sink

    found_sink = pav.find(found_pid, thread=thread)
    if not found_sink:
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


# TODO: Move into functions that use pulse<Instance>.<Method> or
#                                    pulse<Instance>.<Class/Static Variable>
# Existing functions now need to use: pulse = get_pulse_control()
#PULSE_WORKS = True
#try:
#    ext.t_init("pulse = pulsectl.Pulse()")
#    pulse = pulsectl.Pulse()
#    # print("pulse:", dir(pulse))
#    ext.t_end('no_print')  # 0.0037407875
#
#except Exception as p_err:  # CallError, socket.error, IOError (pidfile), OSError (os.kill)
#    PULSE_WORKS = False
#    raise pulsectl.PulseError('mserve.py get_pulse_control() Failed to ' +
#                              'connect to pulse {} {}'.format(type(err), err))


def deprecated_sink_master():
    """ Get PulseAudio list of all sinks
        Return list of tuples with sink #, flat volume and application name
        April 29, 2023 - app_vol has glitch "0]" for speech-dispatcher
    """

    all_sinks = []                              # List of tuples

    # If Python pulseaudio is working, use the fast method
    if PULSE_WORKS:
        for sink in pulse.sink_input_list():
            this_volume = str(sink.volume)
            # sink.volume = channels = 2, volumes = [100 % 100 %]
            this_volume = this_volume.split('[')[1]
            this_volume = this_volume.split(' ')[0]
            this_volume = this_volume.replace('%', '')
            if this_volume.endswith(']'):
                # Bug end up with "0]" fixed Bug April 29, 2023
                this_volume = this_volume[:-1]
            all_sinks.append(tuple((str(sink.index), int(this_volume),
                                    str(sink.proplist['application.name']))))
        return all_sinks


    # If no Python pulseaudio, then use the slow method
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


def deprecated_step_volume(sink, p_start, p_stop, steps, interval, thread=None):
    """
        TODO: The 1/2 second to ramp up one volume and ramp down another is
              adding up with pauses to graphics and music. Spin off subprocess
              that doesn't lag animations or introduce noticeable sound delays.

        Step volume up or down for Pulseaudio Input Sink #
        if p_stop > p_start we are going up, else we are going down
        interval is time between steps when call to pa adjusts volume
    """
    # If a single sink is passed, convert it to list for conformity
    if isinstance(sink, str):
        if sink is "":
            toolkit.print_trace()
            print("mserve.py step_volume(): Input Sink # is blank")
            return
        sinks = [sink]  # Convert single sink string into list
    elif isinstance(sink, list):
        sinks = sink
        for sink_entry in sinks:
            if sink_entry is "":
                toolkit.print_trace()
                print("mserve.py step_volume(): Input Sink # is blank")
                return
    else:
        print("mserve.py step_volume(): Input Sink # must be string or list")
        return
    adjust = (float(p_stop) - float(p_start)) / float(steps)
    #print("adjust = int((p_stop - p_start) / steps)",
    #      adjust, p_stop, p_start, steps)
    perc = float(p_start) + adjust  # positive (up) or negative (down)
    for i in range(steps):
        t_start = time.time()
        ''' June 4, 2023 - list of sinks (could be one entry) ramped in unison '''
        job_time = 0.0
        for sink_entry in sinks:
            step_time, err = pav.set_volume(sink_entry, int(perc))
            job_time += step_time
            if err is not None:
                print("mserve.py step_volume():", i, "  | Error:", err)
        if thread:
            # Update graphics or VU meters, etc.
            thread()
        root.update_idletasks()  # May 27 2023 - Was below sleep calc. Move up.
        # Sleep in milliseconds to interval time and allow screen updates
        sleep = interval * 1000 - (time.time() - t_start) * 1000
        if sleep < 1:
            sleep = 1
        if job_time < interval:
            root.after(int(sleep))
        perc += + adjust  # positive (up) or negative (down)


pulse_error_cnt = 0  # Limit number of errors printed.


def deprecated_set_volume(target_sink, percent):
    """ Set volume and return time required to do it
        Trap error messages with 2>&1
    """
    global pulse_error_cnt

    #print("\n set_volume() -- looking for sink:", target_sink,
    #      "setting volume to:", percent, "%",
    #      "float(percent) / 100.0:", float(percent) / 100.0)
    # If Python pulseaudio is working, use the fast method
    if PULSE_WORKS:
        ''' Fast method using pulse audio direct interface '''
        ext.t_init('set_volume() -- pulse.volume_change')
        err = None  # No known pulsectl errors have appeared yet
        for sink in pulse.sink_input_list():
            if str(sink.index) == target_sink:
                pulse.volume_set_all_chans(sink, float(percent) / 100.0)
                job_time = ext.t_end('no_print')
                return job_time, err
        ext.t_end('no_print')

    if PULSE_WORKS and pulse_error_cnt < 10:
        pulse_error_cnt += 1  # Limit to 10 errors printed
        if pulse_error_cnt < 10:
            print("\nmserve.py set_volume() pulsectl missing sink:", target_sink)
            all_sinks = list()
            for sink in pulse.sink_list():
                all_sinks.append(sink)
            print("all sinks:", all_sinks)
            print("resorting to CLI 'pactl' command")

    ''' Slow method using CLI (command line interface) to pulse audio '''
    # Build command line list for subprocess
    # noinspection PyListCreation
    command_line_list = []
    command_line_list.append("pactl")
    command_line_list.append("set-sink-input-volume")
    command_line_list.append(target_sink)
    command_line_list.append(str(percent) + '%')
    #command_str = " ".join(command_line_list)  # list to printable string
    #print("command_str:", command_str)

    ext.t_init('set_volume() -- pactl set-sink-input-volume')
    pipe = sp.Popen(command_line_list, stdout=sp.PIPE, stderr=sp.PIPE)
    text, err = pipe.communicate()  # This performs .wait() too
    job_time = ext.t_end('no_print')
    if text:
        print("standard output of set_volume() subprocess:")
        print(text)
    if err:
        pulse_error_cnt += 1  # Limit to 10 errors printed
        if pulse_error_cnt < 10:
            print("standard error of set_volume() subprocess:")
            print('set_volume() ERROR. sink:', target_sink,
                  'percent:', percent,
                  'job_time:', job_time)
            print('error:', err)
    # if pipe.return_code == 0:                  # Future use
    return job_time, err


def set_tv_sound_levels(start_percent, end_percent, _thread=None):
    """
        Set Firefox tv sound levels to given percentage
        Ending percent is 25 when going down and 100 when going up
    """
    pav.get_all_sinks()
    for Sink in pav.sinks_now:
        if Sink.name == TV_SOUND:
            pav.fade(Sink.sink_no_str, start_percent, end_percent, 1)
    #tv_sound_list = sink_list(TV_SOUND)  # Browser can have multiple entries
    #step_volume(tv_sound_list, start_percent, end_percent, 10, .05, thread=thread)


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
    global DPRINT_ON
    if DPRINT_ON:
        print(*args)


# ==============================================================================
#
#       Miscellaneous Functions
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
        ''' cat3() ... Latin character error in:  🎵  Ænema '''
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
        June 6, 2023 - Made safe to be called multiple times.
    """

    global START_DIR, LODICT  # Never change LODICT after startup!

    ''' Check for Last known location iid '''
    if not os.path.isfile(lc.FNAME_LAST_LOCATION):
        print("lc.FNAME_LAST_LOCATION not found:", lc.FNAME_LAST_LOCATION)
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
    LODICT = lc.item(iid)  # local permanent copy of loc dictionary
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
    """ DEPRECATED. Simplified version of message.ToolTip() """

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
OLD_CWD = None  # Directory when 'm' or mserve.py was called
SORTED_LIST = []
root = None  # Tkinter toplevel object. Can be passed by `m`


def create_files():
    """ g.USER_DATA_DIR/mserve doesn't exist. Create directory and files. 
    """

    # Create directory
    try:
        os.mkdir(g.USER_DATA_DIR)
        print("Created directory:", g.USER_DATA_DIR)
    except OSError:  # [Err no 17] File exists: '.../.local/share/mserve'
        print("Could not create directory:", g.USER_DATA_DIR)
        return False

    # Open and Close will create SQL database
    sql.open_db()
    sql.close_db()
    print("Created SQL database:", lc.FNAME_LIBRARY)

    # create lc.FNAME_LOCATIONS
    lc.read()  # If no file, creates empty lc.LIST
    lc.write()  # LIST is empty and written as pickle

    # create lc.FNAME_LAST_LOCATION is not needed


def open_files(old_cwd, prg_path, parameters, toplevel=None):
    """
        If no passed music directory, or if passed directory doesn't exist,
        use default location directory. If no default location directory,
        use the startup directory when 'm' or 'mserve.py' was called. If that
        directory doesn't contain music, or subdirectories with music then
        prompt for a music directory. If prompt cancelled then exit.
    """

    global root  # named when main() called
    global SORTED_LIST  # os.walk() results: artist/album/songs
    global START_DIR  # Music directory. E.G. "/home/USER/Music
    global NEW_LOCATION  # True=Unknown music directory in parameter #1
    global LODICT  # Permanent copy of location dictionary never touched

    print()  # A little separation
    print(r'  ######################################################')
    print(r' //////////////                            \\\\\\\\\\\\\\')
    print(r'<<<<<<<<<<<<<<    mserve - Music Server     >>>>>>>>>>>>>>')
    print(r' \\\\\\\\\\\\\\                            //////////////')
    print(r'  ######################################################')

    #print("def open_files(old_cwd, prg_path, parameters):",
    #      old_cwd, prg_path, parameters)
    print("prg_path is not used. Review:", prg_path)

    ''' Has data directory been created? '''
    if os.path.exists(g.USER_DATA_DIR):
        ''' Sanity Checks 
            TODO: Check individual files exist in DATA_DIR
        '''
        if os.path.isdir(g.USER_DATA_DIR):
            #print("g.USER_DATA_DIR exists:", g.USER_DATA_DIR)
            pass
        else:
            toolkit.print_trace()
            print("g.USER_DATA_DIR is a file but must be a directory:", 
                  g.USER_DATA_DIR)
            exit()
    else:
        print("g.USER_DATA_DIR must be created:", g.USER_DATA_DIR)
        create_files()
    print()

    ''' Was music_dir passed as parameter? '''
    #music_dir = None  # Just to make pycharm "happy:)"
    try:
        music_dir = parameters[1]
        #print("mserve.py open_files() using music_dir:", music_dir)
        hold_dir = os.getcwd()
        os.chdir(old_cwd)  # Temporarily change to original directory
        # Massage parameter 1 of ".", "..", "../Sibling", etc.
        music_dir = os.path.realpath(music_dir)
        os.chdir(hold_dir)  # Change back to mserve.py directory
        use_location = False
    except IndexError:  # list index out of range
        # Music directory not passed as parameter
        #print("mserve.py open_files() using last location")
        music_dir = None
        use_location = True

    ''' Is passed music_dir in our known locations? '''
    if music_dir is not None and lc.get_dict_by_dirname(music_dir):
        use_location = True  # Override to use location found by dir name
        print('mserve.py open_files() Overriding music_dir:', music_dir,
              'to location:', lc.DICT['iid'])
        # Make passed Top Directory our last known location then load it
        lc.save_mserve_location(lc.DICT['iid'])

    ''' create START_DIR, test location awake, check files exist '''
    if use_location:
        if load_last_location():
            # If no optional `/` at end, add it for equal comparisons
            if not START_DIR.endswith(os.sep):
                START_DIR += os.sep
            #print('mserve.py open_files() Last location read. START_DIR:',
            #      START_DIR)
            return
        else:
            print("mserve.py open_files() load_last_location() FAILED !!!!")
            print("Proceeding to use music_dir:", music_dir)

    ''' Does music_dir or it's subdirectories contain music files? 
    
        DO THIS EARLIER. After Music Directory is set then look
        if it's in location master.
    
    '''
    # print('START_DIR not in location master file:', START_DIR)
    LODICT['iid'] = 'new'  # June 6, 2023 - Something new to fit into code
    LODICT['name'] = music_dir  # Name required for title bar
    NEW_LOCATION = True  # Don't use location dictionary (LODICT) fields

    print("mserve.py open_files() Searching for songs in music_dir:", music_dir)

    while True:
        if music_dir is None:
            music_dir = g.HOME
        # Prompt to get startup directory using /home/USER as default
        START_DIR = get_dir(root, "Select Music Directory", music_dir)
        print("mserve.py open_files() START_DIR:", START_DIR, type(START_DIR))
        if isinstance(START_DIR, tuple):
            print("mserve.py open_files() Cancel selected from" +
                  " Select Music Directory dialog. Exiting.")
            exit()

        if START_DIR is None:
            START_DIR = old_cwd
            print("mserve.py open_files() START_DIR forced to old_cwd," +
                  " should not happen:", old_cwd)
        if not START_DIR.endswith(os.sep):
            print("\nmserve.py open_files() File picker shortfall, adding" +
                  " / to end of:", START_DIR)
            print()
            START_DIR += os.sep
        # Check how many songs
        music_list, depth_count = make_sorted_list(START_DIR, toplevel=toplevel)
        if depth_count[0] == 0 and depth_count[1] == 0 and depth_count[2] == 0:
            # TODO: Splash screen "M" is still open but cannot be moved because
            #           it has no window decorations.
            #       Clicking Cancel in filepicker is an endless loop
            #       Entering '~/Music' into Filepicker and clicking 'OK' should work but doesn't
            #       Control+C doesn't terminate in terminal. Have to close tab
            text = "Music Library appears empty !!!\n\n" + \
                   "    " + START_DIR + "\n\n" + \
                   "No songs were found in target directory nor the\n" + \
                   "next three subdirectory levels under the target.\n\n" + \
                   "Verify the directory name and try again."
            messagebox.showinfo(title="No music files found.", message=text)
            #message.ShowInfo(root, title="No music files found.", text=text,
            #                 align='left', icon='error')  # Doesn't work without parent
            # NOTE: OK doesn't work so use messagebox.showinfo() instead
            #       Window appears on top-left monitor @ 30,30 so use messagebox instead
            continue

        print("mserve.py open_files() len(music_list):",
              len(music_list), "in START_DIR:", START_DIR)
        print(depth_count)
        #print(music_list)
        break

    ''' Replace existing, or append first parameter with massaged (realpath) 
        music directory. This is needed for mserve restart. 
    '''
    if len(sys.argv) > 1:
        sys.argv[1] = music_dir
    else:
        sys.argv.append(music_dir)

    print("End of open_files()")


pav = None


def main(toplevel=None, cwd=None, parameters=None):
    """
    Establish our file locations from sys.argv or last used location

    :type toplevel: Object
    :param toplevel: Splash screen mounted by m for startup
    :param cwd: Current Working Directory when program started
    :param parameters: sys.argv used to call program
    """

    global root  # named when main() called
    global SORTED_LIST  # os.walk() results: artist/album/songs
    global START_DIR  # Music directory. E.G. "/home/USER/Music
    global NEW_LOCATION  # True=Unknown music directory in parameter #1
    global LODICT  # June 1, 2023 - Wasn't declared global before today
    global pav  # July 8, 2023 - global until start_ffplay relocated

    ''' cwd is saved and passed by "m" before calling mserve.py '''
    prg_path = os.path.dirname(os.path.realpath(__file__))
    # prg_path is already available in g.PROGRAM_DIR so deprecate it.
    if cwd is None:
        ''' Change to working path - same code in m and mserve.py '''
        cwd = os.getcwd()
        if cwd != prg_path:
            #print("Changing to dir_path:", dir_path)
            os.chdir(prg_path)

    ''' parameters are passed by "m" to mserve.py '''
    if parameters is None:
        parameters = sys.argv

    # Create Tkinter "very top" Top Level window
    if toplevel is None:
        root = tk.Tk()  # Create "very top" toplevel for all top levels
    else:
        root = tk.Toplevel()  # `m` splash screen already used tk.Tk()
    root.withdraw()  # Remove default window because we have own windows

    """ From: https://stackoverflow.com/a/46636970/6929343
        Should deleted highlighted text when paste is used.
        Only applies to X11 because other systems do it automatically. 
    """
    root.bind_class("Entry", "<<Paste>>", custom_paste)  # X11 only test

    ''' Set font style for all fonts including tkSimpleDialog.py '''
    img.set_font_style()  # Make messagebox text larger for HDPI monitors
    ''' Set program icon in taskbar '''
    img.taskbar_icon(root, 64, 'white', 'lightskyblue', 'black')

    open_files(cwd, prg_path, parameters)  # Create application directory
    
    # Find location dictionary matching top directory passed as argument
    """ June 8, 2023 This code now in open_files() function 
    try:
        ''' mserve called with parameter to Music Directory? '''
        START_DIR = parameters[1]

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
        START_DIR += os.sep
    """

    # Build list of songs in the location
    ext.t_init('make_sorted_list()')
    SORTED_LIST, depth_count = make_sorted_list(START_DIR, toplevel=toplevel)
    #print(depth_count)
    ext.t_end('no_print')  # May 24, 2023 - make_sorted_list(): 0.1631240845

    # TODO: Use message.ShowInfo()  Perform this test when selecting start dir
    if len(SORTED_LIST) == 0:
        text = "Music Library appears empty !!!\n\n" + \
               "    " + START_DIR + "\n\n" + \
               "If this is a remote host check connection by listing\n" + \
               "files on mount point.\n\n" + \
               "If you run command below and get the error below:\n" +\
               "    $ sshfs 'host:/mnt/music/' /mnt/music\n" + \
               "    fuse: bad mount point `/mnt/music`: " + \
               "Transport endpoint is not connected\n\n" + \
               "Then unmount the point with:\n" + \
               "    $ sudo umount -l /mnt/music'"
        print('\nmserve.py main() ERROR:\n')
        print(text)  # Print to console and show message on screen at 100, 100
        message.ShowInfo(root, title="No music files found.", text=text,
                         align='left', icon='error')
        # NOTE: Tempting to exit now but need to proceed to select different location.

    # Temporarily create SQL music tables until search button created.
    # TODO: How to create music tables when location hasn't been defined yet?
    ext.t_init('sql.create_tables()')
    sql.create_tables(SORTED_LIST, START_DIR, PRUNED_DIR, PRUNED_COUNT, g.USER, LODICT)
    ext.t_end('no_print')  # sql.create_tables(): 0.1092669964
        # May 24, 2023 -  sql.create_tables(): 0.1404261589
        # June 3, 2023 -  sql.create_tables(): 0.0638458729

    pav = vup.PulseAudio()
    #print("pav.pulse_is_working:", pav.pulse_is_working)
    #print(pav.sinks_at_init)

    MusicTree(toplevel, SORTED_LIST)  # Build treeview of songs

    # https://stackoverflow.com/questions/12800007/why-photoimages-dont-exist
    if toplevel is None:
        # `m` already has mainloop(). If `m` didn't pass toplevel, call mainloop().
        root.mainloop()


if __name__ == "__main__":
    main()

# End of mserve.py
