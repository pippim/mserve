#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: pippim.com
License: GNU GPLv3. (c) 2020 - 2023
Source: This repository
Description: mserve - Music Server - Encode (Rip) CD to music files
"""

from __future__ import print_function  # Must be first import
from __future__ import with_statement  # Error handling for file opens
# from __future__ import unicode_literals  # Not needed.
import warnings  # 'warnings' advises which commands aren't supported
warnings.simplefilter('default')  # in future Python versions.

# ==============================================================================
#
#       encoding.py - Encode CD to '.oga', '.wav' or '.flac'
#
#       TODO:   Whilst encoding obtain lyrics and allow play song encoded with
#               full lyrics edit and time index synchronization.
#
#               Ditch the IPC pickles and use SQL history records to pass
#               variables back and forth. Also gives audit trail of encoding
#               process should something go wrong.
#
#       Aug. 22 2021 - toolkit.ToolTips() for fading tooltips on hover
#       May. 07 2023 - Convert gmtime to localtime. Before today needs update
#       June 22 2023 - Use CustomScrolledText ported to toolkit.py
#       July 12 2023 - Interface to/from mserve_config.py
#       July 13 2023 - Upgrade to new SQL database.
#       July 16 2023 - Prompt to override Artist, Album Artist, Album, AlbumDate,
#           Genre & Compilations. FirstDate overriden in table cell.
#       Aug. 15 2023 - Support M4A gstreamer and mutagen.
#       Aug. 16 2023 - Album level overrides & track level metadata editing.
#
# ==============================================================================
# noinspection SpellCheckingInspection
"""
TODO:

    Get/Set last history record 'encoding' - 'format', 'quality' & 'naming'
        copy mserve.py: self.play_hockey_allowed = self.get_hockey_state()
    With only 1 release passing filter, mark checkbox for Album Date, Tracks and
        middle artwork resolution. 

MP3 support:
    https://mutagen.readthedocs.io/en/latest/api/mp3.html

ID3 Tag reference:
    https://mutagen.readthedocs.io/en/latest/api/id3.html

How ffmpeg uses tags:
    https://gist.github.com/eyecatchup/0757b3d8b989fe433979db2ea7d95a01
    E.G.

Music Brainz NGS reference:
https://buildmedia.readthedocs.org/media/pdf/python-musicbrainz-ngs-jonnyjd/latest/python-musicbrainz-ngs-jonnyjd.pdf


    What is the correct iTunes song date?
    -------------------------------------
    If there is only one YEAR per iTunes song, should it be the:
        1. original song creator's publishing YEAR?
        2. YEAR as published by the Cover Artist?
        3. Apple Reissued YEAR version date?
    
    Id3v2 has the "TORY" (Original Release Year) frame
    foobar calls it "ORIGINAL RELEASE DATE"
        
"""

# Must be before tkinter and released from interactive. Required to insert
# from clipboard.
# import gtk                     # Doesn't work. Use xclip instead
# gtk.set_interactive(False)

# noinspection SpellCheckingInspection
'''
Buried in functions:
from mutagen.flac import FLAC as audio_file
from mutagen.oggvorbis import OggVorbis as audio_file

from mutagen.oggvorbis import OggVorbis
from mutagen.flac import Picture

from mutagen.mp4 import MP4, MP4Cover

'''

''' Caller must be 'mserve.py' '''
import inspect
import os
try:
    filename = inspect.stack()[1][1]  # parent filename s/b "mserve.py"
    #(<frame object>, './m', 50, '<module>', ['import mserve\n'], 0)
    parent = os.path.basename(filename)
    if parent != "mserve.py":
        print("encoding.py must be called by 'mserve.py' but is called by:", 
              parent)
        exit()
except IndexError:  # list index out of range
    ''' Called from the command line '''
    print("encoding.py cannot be called from command line. Aborting...")
    exit()

try:  # Python 3
    import tkinter as tk
    import tkinter.ttk as ttk
    import tkinter.font as font
    import tkinter.filedialog as filedialog
    import tkinter.messagebox as messagebox
    import tkinter.scrolledtext as scrolledtext
    import tkinter.simpledialog as simpledialog

    PYTHON_VER = "3"
except ImportError:  # Python 2
    import Tkinter as tk
    import ttk
    import tkFont as font
    import tkFileDialog as filedialog
    import tkMessageBox as messagebox
    import ScrolledText as scrolledtext
    import tkSimpleDialog as simpledialog

    PYTHON_VER = "2"
# print ("Python version: ", PYTHON_VER)
from PIL import Image, ImageTk, ImageDraw, ImageFont
from ttkwidgets import CheckboxTreeview

try:
    import subprocess32 as sp

    SUBPROCESS_VER = '32'
except ImportError:  # No module named subprocess32
    import subprocess as sp

    SUBPROCESS_VER = 'native'
import sys
import os
import io
import re
import time
import datetime
import pickle
import json  # For debugging only
from pprint import pprint

# Dist-packages
import magic
import musicbrainzngs as mbz
import libdiscid as discid

# Pippim modules
import global_variables as g
import location as lc
import external as ext
import toolkit
import monitor  # To get/save window geometry
import message
import image as img
import timefmt as tmf  # Aug 13/2021 switch over to tmf abbreviation
import sql

EMAIL_ADDRESS = "pippim.com@gmail.com"  # TODO - setup variable in SQL History
# The email address isn't that important as throttling is by IP address.

''' File with dictionaries in pickle format passed between background jobs '''
IPC_PICKLE_FNAME = g.TEMP_DIR + "mserve_encoding_pickle"
RIP_CD_IS_ACTIVE = False  # Read by mserve.py

''' To save time during development, reused pickle datafiles saved last run '''
SAVED_MBZ1_PICKLE = ext.join(g.TEMP_DIR, "mserve_mbz_get1_pickle")
SAVED_MBZ2_PICKLE = ext.join(g.TEMP_DIR, "mserve_mbz_get2_pickle")
RIP_ARTWORK = ext.join(g.TEMP_DIR, "mserve_encoding_artwork")


# ==============================================================================
#
#       RipCD class - Encode songs on CD
#
# ==============================================================================


# noinspection PyProtectedMember,PyBroadException
class RipCD:
    """ Create self.cd_tree = tk.Treeview()
        Resizeable, Scroll Bars, select songs, play songs.
    """

    def __init__(self, toplevel, tooltips, info, rip_ctl, lcs,
                 caller_disc=None, thread=None, sbar_width=14):

        global RIP_CD_IS_ACTIVE

        self.lib_top = toplevel  # Use same variable name as mserve
        self.tt = tooltips  # Hovering fading tooltips
        self.info = info  # Information Centre               
        self.rip_ctl = rip_ctl  # FileControl()
        self.lcs = lcs  # location.py Locations() instance
        RIP_CD_IS_ACTIVE = True  # Shared with mserve
        #self.topdir = LODICT['topdir']  # What if there is no location dict?
        self.topdir = lcs.open_topdir  # What if it's a new location?
        self.caller_disc = caller_disc  # Development reuse last disc ID

        ''' Edit Window'''
        self.edit_top = None
        self.edit_frm = None
        self.edit_cancel_btn = None
        self.edit_proceed_btn = None
        self.edit_title_var = tk.StringVar()  # Can't change for display
        self.edit_artist_var = tk.StringVar()
        self.edit_first_date_var = tk.StringVar()
        self.edit_composer_var = tk.StringVar()
        self.edit_comment_var = tk.StringVar()

        ''' Confirmation Window '''
        self.confirm_top = None
        self.confirm_frm = None
        self.confirm_cancel_btn = None
        self.confirm_proceed_btn = None
        ''' match: self.selected_album_artist -> self.selected_gapless_playback '''
        self.album_artist_var = tk.StringVar()
        self.compilation_var = tk.StringVar()
        self.album_name_var = tk.StringVar()
        self.album_date_var = tk.StringVar()
        self.composer_var = tk.StringVar()
        self.comment_var = tk.StringVar()
        self.disc_number_var = tk.StringVar()
        self.genre_var = tk.StringVar()
        self.gapless_playback_var = tk.StringVar()

        ''' treeview work fields '''
        self.cd_tree_iid = None  # iid of track (song)

        ''' self.get_refresh_thread NOT USED. Use self.update_display() '''
        self.get_refresh_thread = thread  # returns refresh_Xxx_top()

        self.disc = None  # from python-libdiscid
        self.disc_count = None  # How many discs in Album?
        self.this_disc_number = None  # What is current disc number?
        self.release_list = None  # Musicbrainz release list
        self.rip_art = None  # List of art images to encode
        self.rotated_art = None  # Spinning album artwork
        self.play_current_song_art = None  # Photo image of rotating artwork
        self.image_data = None  # Image encoded into file
        self.selected_medium = None  # Musicbrainz dictionary
        self.image_count = None  # Album artwork selected

        # Ripping '#' multiple disc #. '99 - ' or '99 ' track numbering
        self.os_song_name = None  # '#-99 Song name.xxx'
        self.os_full_path = None  # top_dir/artist/album/#-99 Song name.xxx
        self.sqlOsFileName = None  # artist/album/#-99 Song name.xxx
        # When artist is "Various Artists" the directory is "Compilations" but
        # The metadata will contain real Artist Name, not "Compilations"
        self.song_seconds = None  # Above in seconds
        self.song_size = None  # Song file size

        # Meta - Values stored in treeview track iid
        self.track_meta_title = None  # Title with NO 'disc-track-' & NO .ext
        self.track_artist = None  # Different than album_artist
        self.track_first_date = None  # deep search used
        self.track_composer = None  # Probably in MBZ
        self.track_comment = None  # Inherited from Album defaults
        self.track_duration = None  # duration "hh:mm:ss"
        self.track_no = None  # Integer track number
        ''' Aug 16/23 - track_song_title will become track_comment '''
        self.track_song_title = None  # Song title from treeview '#-99 -'

        self.DiscNumber = None  # July 13, 2023
        self.CreationTime = None  # Initially same as stat.st_ctime
        self.rip_current_track = None  # Current track number start at 1
        self.song_rip_sec = 0  # How many seconds and blocks
        self.song_rip_blk = 0  # have been ripped for song?
        self.total_rip_sec = 0  # How many seconds and blocks
        self.total_rip_blk = 0  # ripped for selections?
        self.next_image_key_ndx = 0  # Next image to encode into music file
        self.reverse_checkbox = None  # Marked treeview checkbox error

        # Pulsating shades of green indicating which song is being ripped
        self.last_highlighted = None
        self.last_shade = None
        self.curr_shade = None
        self.skip_once = False  # First time through no last shade

        ''' Set font style for all fonts including tkSimpleDialog.py '''
        img.set_font_style()

        ''' Place Window top-left of parent window with g.PANEL_HGT padding '''
        self.cd_top = tk.Toplevel()
        self.cd_top_is_active = True
        self.cd_top.minsize(width=g.WIN_MIN_WIDTH, height=g.WIN_MIN_HEIGHT)
        geom = monitor.get_window_geom('encoding')
        self.cd_top.geometry(geom)
        self.cd_top.title("Reading CD - mserve")
        self.cd_top.configure(background="Gray")
        self.cd_top.columnconfigure(0, weight=1)
        self.cd_top.rowconfigure(0, weight=1)
        self.cd_top.bind("<FocusIn>", self.handle_cd_top_focus)

        ''' Set program icon in taskbar '''
        img.taskbar_icon(self.cd_top, 64, 'white', 'lightskyblue', 'black')

        ''' Create master frame '''
        master_frame = ttk.Frame(self.cd_top, padding=(3, 3, 12, 12))
        master_frame.grid(column=0, row=0, sticky=tk.NSEW)
        tk.Grid.rowconfigure(master_frame, 0, weight=1)
        tk.Grid.columnconfigure(master_frame, 0, weight=1)

        ''' frame1 - artwork and selections formatted for ripping. '''
        frame1 = ttk.Frame(master_frame, borderwidth=g.BTN_BRD_WID,
                           padding=(2, 2, 2, 2), relief=tk.RIDGE)
        frame1.grid(column=0, row=0, sticky=tk.NSEW)

        ''' Artwork image row 0, column 0 '''
        self.art_width = 375
        self.art_height = 375
        self.using_cd_image = None  # Used in make_default_art()
        self.original_art = None  # Used in make_default_art()
        self.resized_art = None  # Used in make_default_art()
        self.cd_song_art = None  # Used in make_default_art()
        self.make_default_art()
        self.cd_art_label = tk.Label(frame1, image=self.cd_song_art, font=g.FONT)
        self.cd_art_label.grid(row=0, column=0, sticky=tk.W)
        #self.cd_art_label.update()  Makes artwork tiny

        ''' Controls to resize image to fit frame '''
        self.start_w = frame1.winfo_reqheight()
        self.start_h = frame1.winfo_reqwidth()
        frame1.bind("<Configure>", self.on_resize)
        
        ''' Scrollable textbox to show selections / ripping status '''
        text = "It will take a minute to access Audio CD's Disc ID. "
        text += "It will take another minute to access\n"
        text += "the internet and Musicbrainz.\n\n"

        text += "If audio disc ID is not found in MusicBrainz, go to "
        text += "musicbrainz.com and search the Album\n"
        text += "and Artist. Copy the 28 character Release ID to the "
        text += "clipboard. Then paste it when asked.\n\n"

        text += "MusicBrainz CD track names will appear in listings "
        text += "below. Review and select a listing\n"
        text += "that most closely matches the CD. After selecting a "
        text += "listing, the contents appear here.\n\n"

        text += "MusicBrainz will be accessed using: " + EMAIL_ADDRESS + "\n\n"
        text += "If MusicBrainz is accessed too frequently, they may "
        text += "'throttle' your IP address. This\n"
        text += "means MusicBrainz will operate slower. It is not "
        text += "personal and all websites do this.\n"
        text += "If you have a MusicBrainz account, enter your email "
        text += "address above and you will get an\n"
        text += "email if your IP address gets 'throttled'.\n\n"

        text += "TIPS:\tClick Medium checkbox to select songs all at once.\n"
        text += "\tUse browser to copy images from websites and click "
        text += "'Clipboard image' button to paste.\n"
        text += "\tYou can override Artist Name, Album Name, etc., "
        text += "when the 'Rip Disc' button is clicked.\n"
        text += "\tYou can override First Date (first year song ever "
        text += "aired) by clicking inside listing.\n"
        text += "\tIt is important to note that the Album Date is "
        text += "later for remasters and Greatest Hits\n"
        text += "\tThree artwork choices are often provided. Avoid "
        text += "the ones greater than 1 Megabyte.\n"
        text += "\tAfter these tips disappear, you can review later "
        text += "using 'View', 'Information Centre'.\n"
        # Text padding not working: https://stackoverflow.com/a/51823093/6929343
        self.scrollbox = toolkit.CustomScrolledText(
            frame1, state="normal", font=g.FONT, borderwidth=15, relief=tk.FLAT)
        self.scrollbox.insert("end", text)
        self.scrollbox.grid(row=0, column=1, padx=3, pady=3, sticky=tk.NSEW)
        self.info.cast(text)
        tk.Grid.rowconfigure(frame1, 0, weight=1)
        tk.Grid.columnconfigure(frame1, 1, weight=1)
        self.scrollbox.tag_config('red', foreground='Red')
        self.scrollbox.tag_config('green', foreground='Green')
        self.scrollbox.tag_config('yellow', foreground='Yellow')
        self.scrollbox.tag_config('orange', foreground='Orange')
        #self.scrollbox.config(tabs=("28m", "56m", "106m"))  # Aug 16/23 grew wider?
        self.scrollbox.config(tabs=("22m", "50m", "100m"))  # Aug 16/23 grew wider?

        # https://hexcolor.co/hex/1b851b
        #        green_shades = [ "#93fd93", "#7fe97f", "#7fe97f", "#75df75", "#6bd56b",
        #                         "#61cb61", "#57c157", "#4db74d", "#43ad43", "#39a339"
        # Hard to find combination that doesn't hurt eyes :(
        green_shades = ["#93fd93", "#7fe97f", "#6bd56b", "#57c157", "#43ad43",
                        "#39a339", "#258f25", "#117b11", "#006700", "#004900"
                        ]
        #        green_shades = [ "#6bd56b", "#61cb61", "#57c157", "#4db74f", "#43ad43", 
        #                         "#39a339", "#2f992f", "#258f25", "#117b11", "#077107"
        #        green_shades = [ "#4db74f", "#43ad43", "#39a339", "#2f992f", "#258f25",
        #                         "#117b11", "#077107", "#006700", "#005d00", "#005300"
        # These are Milano Red https://hexcolor.co/hex/c0070b
        #        green_shades = [ "#ff6b6f", "#ff6165", "#ff575b", "#ff4d51", "#fc4347",
        #                         "#f2393d", "#e82f33", "#de2529", "#d41b1f", "#ca1115"
        ''' color shades for throbbing color effect during ripping '''
        for i, shade in enumerate(green_shades):
            self.scrollbox.tag_config(str(i), foreground=green_shades[i])

        ''' Below is future Authorization function - NOT USED '''
        http = "https://musicbrainz.org/"
        self.mbAuthorization = sql.Authorization(
            self.cd_top, "MusicBrainz", http, text, tt=self.tt)

        ''' frame2 - Treeview Listbox '''
        frame2 = ttk.Frame(master_frame, borderwidth=g.BTN_BRD_WID,
                           relief=tk.RIDGE)
        frame2.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)

        ''' Treeview List Box, Columns and Headings '''
        self.cd_tree = CheckboxTreeview(  # Duration & First Date columns displayed
            frame2, columns=("Meta Title", "Artist", "First Date", "Composer",
                             "Comment", "Duration", "Track №"), height=20, selectmode="none",
            show=('tree', 'headings'))
        self.cd_tree["displaycolumns"] = ("Duration", "First Date")
        self.cd_tree.column("#0", width=900, stretch=tk.YES)
        self.cd_tree.heading("#0", text="MusicBrainz Listings (Right click on " +
                             "song to change First Date, Composer, etc.)")
        self.cd_tree.column("Duration", width=160, anchor=tk.CENTER, stretch=tk.NO)
        self.cd_tree.heading("Duration", text="Duration / Size")  # wide enough for 10 mil
        self.cd_tree.column("First Date", width=120, anchor=tk.CENTER, stretch=tk.NO)
        self.cd_tree.heading("First Date", text="First Date")
        self.cd_tree.bind("<Button-3>", self.button_3_click)
        self.cd_tree.bind('<Motion>', self.cd_highlight_row)
        self.cd_tree.bind("<Leave>", self.cd_leave_row)
        self.cd_tree.tag_configure('highlight', background='lightblue')
        self.cd_tree.tag_configure('menu_sel', background='Yellow')
        self.cd_tree.tag_configure('update_sel', foreground='DarkGreen')

        # See: https://stackoverflow.com/questions/60954478/tkinter-treeview-doesnt-resize-with-window
        self.cd_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        ''' Treeview select item - custom select processing '''
        self.ignore_item = None
        self.last_click_expand = None
        self.last_click_collapse = None
        self.current_image_key = None
        self.selected_image_keys = []  # list of tuples links to "imagesel" tag

        ''' For compilations below is album_artist and artist must be real band '''
        self.selected_mbz_id = None  # Musicbrainz ID
        self.selected_medium = None  # Only one medium_id must be selected
        self.selected_tracks = 0  # Number tracks selected from CD total

        ''' Set in os_song_format() which is being revamped Aug 16/23'''
        self.selected_title = None  # Song name with track but no extension.

        ''' Match up: self.album_artist_var -> self.gapless_playback_var '''
        self.selected_album_artist = None  # Compilations show "Various Artists"
        self.selected_compilation = u"0"  # "1" or "0" for pseudo True/False flag.
        self.selected_album_name = None  # Album name to use on all tracks.
        self.selected_album_date = u""  # Album Date
        self.selected_composer = u""  # July 13, 2023 - Used to be unused country
        self.selected_comment = u""  # July 13, 2023 - new variable
        self.selected_disc_number = u""
        self.selected_genre = u""  # Manually entered. Not in Musicbrainz 2023
        self.selected_gapless_playback = u"0"  # "1" or "0" for pseudo True/False flag.
        '''
        Need 1 to 1 selected_xxx for:
        self.album_artist_var = tk.StringVar()
        self.compilation_var = tk.StringVar()
        self.album_name_var = tk.StringVar()
        self.album_date_var = tk.StringVar()
        self.composer_var = tk.StringVar()
        self.comment_var = tk.StringVar()
        self.disc_number_var = tk.StringVar()
        self.genre_var = tk.StringVar()
        self.gapless_playback_var = tk.StringVar()
        '''

        # Selected songs are accessed via "checked" tag in treeview
        self.our_parent = None  # Umm...
        self.parent_tags = ("rel_id", "mbz_id", "medium_id", "images_id", "clips_id")

        self.cd_tree.bind('<Button-1>', self.button_1_click)

        """ style ALREADY DEFINED IN mserve.py:
        style = ttk.Style()
        style.configure("Treeview.Heading", font=(None, g.MED_FONT), \
                        rowheight=int(g.MED_FONT*2.2))
        row_height=int(g.MON_FONTSIZE*2.2)
        style.configure("Treeview", font=(None, g.MON_FONTSIZE), \
                        rowheight=row_height)
        style.configure('Treeview', indent=row_height+6)
        """
        row_height = int(g.MON_FONTSIZE * 2.2)  # Copy from mserve

        ''' Create images for checked, unchecked and tristate '''
        self.checkboxes = img.make_checkboxes(row_height - 6, 'black',
                                              'white', 'deepskyblue')
        self.cd_tree.tag_configure("unchecked", image=self.checkboxes[0])
        self.cd_tree.tag_configure("tristate", image=self.checkboxes[1])
        self.cd_tree.tag_configure("checked", image=self.checkboxes[2])

        """ Already called in parent using ttk.style() applies here too.
        ''' Create images for open, close and empty '''
        width = row_height-9
        self.triangles = []             # list to prevent Garbage Collection
        img.make_triangles(self.triangles, width, 'black', 'grey')
        """

        ''' Treeview Scrollbars '''
        # Create a vertical scrollbar linked to the frame.
        v_sbar = tk.Scrollbar(frame2, width=sbar_width)
        v_sbar.pack(side=tk.RIGHT, fill=tk.Y)

        ''' Treeview Buttons '''
        frame3 = ttk.Frame(master_frame, relief=tk.GROOVE,
                           borderwidth=g.BTN_BRD_WID)
        # frame3.grid(row=2, column=0, sticky=tk.NW)
        # pad x & pad y below have no effect???
        frame3.grid(row=2, column=0, padx=2, pady=2, sticky=tk.NW)

        ''' ✘ Close Button - Always visible '''
        self.cd_top.bind("<Escape>", self.cd_close)
        self.cd_top.protocol("WM_DELETE_WINDOW", self.cd_close)
        self.cd_tree_btn1 = tk.Button(frame3, text="✘ Close",
                                      width=g.BTN_WID - 2, command=self.cd_close)
        self.cd_tree_btn1.grid(row=0, column=0, padx=2)
        text = "Close Rip CD window(s) but leave other mserve windows open."
        self.tt.add_tip(self.cd_tree_btn1, text=text, anchor='nw')

        ''' ▶  Rip Button - Validates songs and images are selected '''
        self.cd_tree_btn2 = tk.Button(
            frame3, text="▶  Rip Disc", width=g.BTN_WID, command=self.rip_cd)
        self.cd_tree_btn2.grid(row=0, column=1, padx=2)
        text = \
            "First select songs on CD to rip. Then select artwork from\n" + \
            "available sources or insert new artwork from clipboard.\n" + \
            "Finally ensure optional fields such as release date are\n" + \
            "either selected or manually entered.\n\n" + \
            'After all that, click this "▶  Rip Disc" button'

        self.tt.add_tip(self.cd_tree_btn2, text=text, anchor='nw')

        ''' 📋 Clipboard image - 📋 (u+1f4cb) Must be valid image format '''
        self.cd_tree_btn3 = tk.Button(
            frame3, text="📋  Clipboard image", width=g.BTN_WID + 4,
            command=self.image_from_clipboard)
        self.cd_tree_btn3.grid(row=0, column=2, padx=2)
        self.cd_tree_btn3.forget()
        self.image_from_clipboard_count = 0
        self.clipboard_images = []
        text = \
            "In your browser navigate to sites containing album cover\n" + \
            "artwork such as Amazon, Wikipedia, Musicbrainz, etc.\n" + \
            "Right click on images and copy to clipboard. Then return\n" + \
            'here and insert image using "📋  Clipboard image" button'
        self.tt.add_tip(self.cd_tree_btn3, text=text, anchor='nw')

        ''' ?  Review Button - Validates Artist, Album, Date, Composer, etc. '''
        self.cd_tree_btn4 = tk.Button(
            frame3, text="?  Override", width=g.BTN_WID, command=self.wait_confirm_tags)
        self.cd_tree_btn4.grid(row=0, column=3, padx=2)
        text = \
            "Override Musicbrainz Information\n" + \
            "Change spelling of Artist and Album Names.\n" + \
            "Set Compilation and Gapless Playback flags.\n" + \
            "Enter Composer, Album Date, Genre."
        self.tt.add_tip(self.cd_tree_btn4, text=text, anchor='ne')

        ''' Menu bars: Format, Quality '''
        # Format menu
        mb = tk.Menu(self.cd_top)
        fmt_bar = tk.Menu(mb, tearoff=0)
        self.fmt_var = tk.StringVar()
        self.fmt_var.set("oga")
        fmt_bar.add_radiobutton(
            label=".wav (Original CD format)", command=self.show_selections,
            font=g.FONT, value="wav", variable=self.fmt_var)
        fmt_bar.add_radiobutton(
            label=".m4a (AAC / MP4 compression)", command=self.show_selections,
            font=g.FONT, value="m4a", variable=self.fmt_var)
        fmt_bar.add_radiobutton(
            label=".oga (Ogg Vorbis compression)", command=self.show_selections,
            font=g.FONT, value="oga", variable=self.fmt_var)
        fmt_bar.add_radiobutton(
            label=".flac (Free Lossless Audio Codec)", command=self.show_selections,
            font=g.FONT, value="flac", variable=self.fmt_var)
        mb.add_cascade(label=" Format ▼ ", menu=fmt_bar, font=g.FONT)

        text = \
            "The Format dropdown menu allows you to pick the encoding\n" + \
            "technology for creating music files.  WAV files are original\n" + \
            "CD format with no images or ID tags such as album, artist or\n" + \
            "song names.  FLAC files provide same quality as WAV files\n" + \
            "and allow images and ID tags.  Both WAV and FLAC files take\n" + \
            "the largest space, about 35 MB.  OGA and AAC files balance size,\n" + \
            "about 6 MB, and quality with image and ID tag support."
        self.tt.add_tip(fmt_bar, text=text, tool_type='menu',
                        menu_tuple=(self.cd_top, 430, 10))  # First s/b 20 but 300

        ''' Quality menu. Usage for m4a below:
                quality_ndx = (int(self.quality_var.get()) - 30) / 10
                kbps = [96, 112, 128, 160, 192, 224, 256, 320]
                bitrate = kbps[quality_ndx] * 1000
                quality = 'bitrate=' + str(bitrate) '''
        self.quality_var = tk.IntVar()
        self.quality_var.set(70)
        quality_bar = tk.Menu(mb, tearoff=0)
        quality_bar.add_radiobutton(
            label="30 % (Smallest size, lowest quality)", command=self.show_selections,
            font=g.FONT, value=30, variable=self.quality_var)
        quality_bar.add_radiobutton(
            label="40 %", command=self.show_selections, font=g.FONT, value=40,
            variable=self.quality_var)
        quality_bar.add_radiobutton(
            label="50 %", command=self.show_selections, font=g.FONT, value=50,
            variable=self.quality_var)
        quality_bar.add_radiobutton(
            label="60 %", command=self.show_selections, font=g.FONT, value=60,
            variable=self.quality_var)
        quality_bar.add_radiobutton(
            label="70 % (Medium size, very good quality)",
            command=self.show_selections, font=g.FONT, value=70,
            variable=self.quality_var)
        quality_bar.add_radiobutton(
            label="80 %", command=self.show_selections, font=g.FONT, value=80,
            variable=self.quality_var)
        quality_bar.add_radiobutton(
            label="90 %", command=self.show_selections, font=g.FONT, value=90,
            variable=self.quality_var)
        quality_bar.add_radiobutton(
            label="100 % (Largest size, highest quality)",
            command=self.show_selections, font=g.FONT, value=100,
            variable=self.quality_var)
        mb.add_cascade(label=" Quality ▼ ", menu=quality_bar, font=g.FONT)
        text = \
            "The Quality dropdown menu allows you to pick the encoding\n" + \
            "sound quality for creating music files.  WAV files and FLAC\n" + \
            "files are always 100% sound quality.  OGA files can have the\n" + \
            "quality set from 30% to 100%.  The higher quality the larger\n" + \
            "size for the music file.  For OGA 70% appears the best balance\n" + \
            "between quality and file size.  Do some tests for yourself."
        self.tt.add_tip(quality_bar, text=text, tool_type='menu', anchor="sw",
                        menu_tuple=(self.cd_top, 650, 10))

        # Song naming format
        self.nam_var = tk.StringVar()
        self.nam_var.set("99 ")
        nam_bar = tk.Menu(mb, tearoff=0)
        nam_bar.add_radiobutton(
            label="99 Song name.ext", command=self.show_selections, font=g.FONT,
            value="99 ", variable=self.nam_var)
        nam_bar.add_radiobutton(
            label="99 - Song name.ext", command=self.show_selections, font=g.FONT,
            value="99 - ", variable=self.nam_var)
        mb.add_cascade(label=" Naming ▼ ", menu=nam_bar, font=g.FONT)
        text = \
            "The Naming dropdown menu allows you to choose the filenames\n" + \
            "assigned to music files.  The extension is automatic where\n" + \
            'WAV files are assigned as ".wav", FLAC files are assigned as\n' + \
            '".flac", OGA files are assigned as ".oga" and AAC files or\n' + \
            'MP4 files are are assigned as ".m4a". You can however\n' + \
            'choose the prefix of "99 " or "99 - " to prepend to filenames.\n\n' + \
            "Where '99' is the track number of the song."
        self.tt.add_tip(nam_bar, text=text, tool_type='menu', anchor="sw",
                        menu_tuple=(self.cd_top, 600, 10))

        # Target menu
        self.trg_var = tk.StringVar()
        self.trg_var.set(self.topdir)
        trg_bar = tk.Menu(mb, tearoff=0)
        trg_bar.add_radiobutton(
            label=self.topdir, command=self.show_selections, font=g.FONT,
            value=self.topdir, variable=self.trg_var)
        mb.add_cascade(label=" Target ▼ ", menu=trg_bar, font=g.FONT)

        # No tooltip for Target because there are no options to pick from yet

        # About Menu - Need author name?
        self.cd_top.config(menu=mb)
        self.cd_top.title("Reading CD - mserve")
        self.cd_top.update()

        ''' EVENT DRIVEN PROCESSING - Call programs in background with shell.
            This allows Treeview mainloop to keep running. When background
            tasks complete (monitored with 'ps aux' our own cd_tree buttons
            are activated. The following background programs are launched:

                disc_get.py - Read CD for Musicbrainz Id and track TOC
                mbz_get1.py - Get Musicbrainz release-list
                mbz_get2.py - Get Musicbrainz recordings
                caa_get1.py - Get Cover Art

                Build Treeview which can call:
                    disc_get.py above followed by cohorts

                    TODO: loc_copy.py copy encoded files to location (or many)
                          Part of larger project that keeps track of deleted
                          duplicate songs and reapplies them to locations.
                          Also tracks renamed directories / songs and applies
                          them to other locations.
                          
                          Scroll text box as songs encoded.
                          Set default disc id from musicbrainz when disc not
                          found and it was manually entered previously.
        '''

        self.get_discid_active = True  # First step
        self.disc_get_active = True
        self.get_discid_time = 0.0

        self.mbz_get1_active = False
        self.mbz_release_id = None  # = self.disc.id but can change
        self.mbz_get1_time = 0.0

        self.mbz_get2_active = False
        self.mbz_get2_time = 0.0
        self.image_dict = None  # Images passed in pickle

        self.treeview_active = False
        self.disc_enc_active = False

        self.encode_track_time = 0.0  # Time to encode track
        self.encode_album_time = 0.0  # Time to encode all tracks
        self.encode_album_seconds = 0  # Playing seconds in all songs
        self.encode_album_track_cnt = 0  # Number tracks encoded
        self.encode_album_size = 0  # File size of all songs
        self.music_id = None  # History's matching music ID
        self.tracknumber = None
        self.clip_parent = None
        self.gst_encoding = None  # gnome encoding format
        ''' Dropdown Menu defaults '''
        self.fmt = "mp4"  # TODO: Get from history record.
        self.quality = "70"  # TODO: Get from history record.
        self.naming = "99 "  # TODO: Get from history record.

        self.disc_id_manual_override = None  # Musicbrainz override of disc.id
        self.active_pid = 0  # 0 = no process ID is running
        self.cd_rotated_value = 0  # For rotating audio cd image
        self.background = self.resized_art.getpixel((3, 3))

        self.cd_run_to_close()  # At this point tkinter mainloop has
        # control and Music Players keeps spinning it's artwork. We have our
        # own spinner with CD Audio Disc image and 1 second text "Reading Disc"
        # with 1/2 second text off. Whilst our own disc image spins 1 degree
        # every 10th second in resizeable widget within resizeable frame2.

    def handle_cd_top_focus(self, _event):
        """ cd_top got focus. Put any popup windows above """
        if self.edit_top:
            self.edit_top.focus_force()  # Get focus
            self.edit_top.lift()  # Raise in stacking order

        if self.confirm_top:
            self.confirm_top.focus_force()  # Get focus
            self.confirm_top.lift()  # Raise in stacking order

    def make_default_art(self):
        """ Called on startup and when last image is unselected. """
        if os.path.isfile('AudioDisc.png'):
            self.using_cd_image = True
            self.original_art = Image.open('AudioDisc.png')
        else:
            self.using_cd_image = False
            self.original_art = img.make_image(
                "Encode /\nRip Disc", image_w=self.art_width, image_h=self.art_height)
        self.resized_art = self.original_art.resize(
            (self.art_width, self.art_height), Image.ANTIALIAS)
        self.cd_song_art = ImageTk.PhotoImage(self.resized_art)

    def on_resize(self, event):
        """ Resize image when frame size changes """
        # images use ratio of original width/height to new width/height
        # w_scale = float(event.width) / self.start_w
        h_scale = float(event.height) / self.start_h

        # Override maintain square by factoring width equally on height change
        w_scale = h_scale
        self.art_width = int(w_scale) - 8  # Awkward
        self.art_height = int(h_scale) - 8
        self.art_width = 100 if self.art_width < 1 else self.art_width
        self.art_height = 100 if self.art_height < 1 else self.art_height

        self.resized_art = self.original_art.resize(
            (self.art_width, self.art_height),
            Image.ANTIALIAS)
        self.cd_song_art = ImageTk.PhotoImage(self.resized_art)
        self.cd_art_label.configure(image=self.cd_song_art)

    @staticmethod
    def cd_highlight_row(event):
        """ Cursor hovering over row highlights it in light blue """
        tree = event.widget
        item = tree.identify_row(event.y)
        tree.tk.call(tree, "tag", "remove", "highlight")
        tree.tk.call(tree, "tag", "add", "highlight", item)

    @staticmethod
    def cd_leave_row(event):
        """ Un-highlight row just left """
        tree = event.widget
        tree.tk.call(tree, "tag", "remove", "highlight")

    def button_3_click(self, event):
        """ Right button clicked in cd_tree treeview.
            Validate clicks are for selected songs. """
        x, y, widget = event.x, event.y, event.widget
        ''' Was region of treeview clicked a "separator" or "heading"? '''
        clicked_region = self.cd_tree.identify("region", event.x, event.y)
        if clicked_region == 'separator':
            return
        if clicked_region == 'heading':
            return

        ''' Validate song is checked '''
        self.cd_tree_iid = self.cd_tree.identify_row(y)
        tags = self.cd_tree.item(self.cd_tree_iid, 'tags')
        if "checked" not in tags:
            message.ShowInfo(self.cd_top, "Right Click Error",
                             "Cannot select an unchecked row.",
                             icon='error', thread=self.update_display)
            return
        if "track_id" not in tags:
            message.ShowInfo(self.cd_top, "Right Click Error",
                             "Can only select songs.",
                             icon='error', thread=self.update_display)
            return

        ''' Popup menu '''
        toolkit.tv_tag_add(self.cd_tree, self.cd_tree_iid, "menu_sel")
        menu = tk.Menu(self.cd_tree, tearoff=0)
        menu.post(event.x_root, event.y_root)
        menu.add_command(label="Edit", font=(None, g.MED_FONT),
                         command=self.edit_song)
        menu.add_separator()
        menu.add_command(label="Ignore click", font=(None, g.MED_FONT),
                         command=lambda: self.close_right_click_menu(menu))
        menu.tk_popup(event.x_root, event.y_root)
        menu.bind("<FocusOut>", lambda _: self.close_right_click_menu(menu))

    def close_right_click_menu(self, menu):
        """ Remove edit song popup menu """
        menu.unpost()
        toolkit.tv_tag_remove(self.cd_tree, self.cd_tree_iid, "menu_sel")

    def edit_song(self):
        """ Popup Window to edit song's Artist, Composer, Comment & First Date """
        ''' Saved geometry is not good. Linked to cd_top is better '''
        self.edit_top = tk.Toplevel()
        try:
            xy = (self.cd_top.winfo_x() + g.PANEL_HGT * 3,
                  self.cd_top.winfo_y() + g.PANEL_HGT * 3)
        except AttributeError:  # CD Tree instance has no attribute 'winfo_x'
            print("self.cd_top failed to get winfo_x")
            xy = (100, 100)

        self.edit_top.minsize(width=g.BTN_WID * 10, height=g.PANEL_HGT * 10)
        self.edit_top.geometry('+%d+%d' % (xy[0], xy[1]))
        self.edit_top.title("Edit song differences - mserve")
        self.edit_top.configure(background="Gray")

        ''' Set program icon in taskbar '''
        img.taskbar_icon(self.edit_top, 64, 'white', 'lightskyblue', 'black')

        ''' Create master frame '''
        self.edit_frm = tk.Frame(self.edit_top, borderwidth=g.FRM_BRD_WID,
                                 relief=tk.RIDGE)
        self.edit_frm.grid(column=0, row=0, padx=5, pady=5, sticky=tk.NSEW)
        self.edit_frm.columnconfigure(0, weight=1)
        self.edit_frm.columnconfigure(1, weight=5)

        ''' Instructions '''
        text = "\nWhen song differences are entered for Artist Name, Composer\n"
        text += "and/or Comment, they are used instead of the album defaults.\n\n"
        text += "The Song Title is reformatted when the music file is created.\n"
        text += 'A "-" between track number and name is added when the "Naming\n'
        text += 'Option" is "99 -". If "Naming Option" is "99 ", then no dash.\n'
        text += 'Filename extension is automatically appended. Verify changes\n'
        text += 'to the real filename in the red "Files:" section in top frame.\n\n'
        text += "The First Date field is searched in MusicBrainz. If it can't be\n"
        text += "found, the Album Date is used as a default and you can change it.\n"
        tk.Label(self.edit_frm, text=text, justify='left', font=g.FONT).grid(
            row=0, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        tk.Label(self.edit_frm, text="Song Title:",
                 font=g.FONT).grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        tk.Entry(self.edit_frm, textvariable=self.edit_title_var,
                 font=g.FONT).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        tk.Label(self.edit_frm, text="Artist Name:",
                 font=g.FONT).grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        tk.Entry(self.edit_frm, textvariable=self.edit_artist_var,
                 font=g.FONT).grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        tk.Label(self.edit_frm, text="First Date",
                 font=g.FONT).grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        tk.Entry(self.edit_frm, textvariable=self.edit_first_date_var,
                 font=g.FONT).grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)
        tk.Label(self.edit_frm, text="Composer:",
                 font=g.FONT).grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        tk.Entry(self.edit_frm, textvariable=self.edit_composer_var,
                 font=g.FONT).grid(row=4, column=1, padx=5, pady=5, sticky=tk.EW)
        tk.Label(self.edit_frm, text="Comment:",
                 font=g.FONT).grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        tk.Entry(self.edit_frm, textvariable=self.edit_comment_var,
                 font=g.FONT).grid(row=5, column=1, padx=5, pady=5, sticky=tk.EW)

        ''' Set screen variables '''
        self.get_track_from_tree(self.cd_tree_iid)
        # song_composer was never retrieved from MusicBrainz Work Relationship
        if self.track_composer == "":  # set to "" during init
            self.track_composer = self.selected_composer
        if self.track_comment == "":  # set to "" during init
            self.track_comment = self.selected_comment
        self.edit_title_var.set(self.track_meta_title)
        self.edit_artist_var.set(self.track_artist)
        self.edit_first_date_var.set(self.track_first_date)
        self.edit_composer_var.set(self.track_composer)
        self.edit_comment_var.set(self.track_comment)
        self.edit_top.update_idletasks()

        ''' Go Back Button '''
        self.edit_cancel_btn = tk.Button(self.edit_frm, text="✘ Go Back",
                                         width=g.BTN_WID2 - 6,
                                         command=self.edit_cancel)
        self.edit_cancel_btn.grid(row=10, column=0, padx=5, pady=5, sticky=tk.W)
        if self.tt:
            self.tt.add_tip(self.edit_cancel_btn, "Return to main selection window.",
                            anchor="sw")
        self.edit_top.bind("<Escape>", self.edit_cancel)
        self.edit_top.protocol("WM_DELETE_WINDOW", self.edit_cancel)

        ''' Save Button '''
        self.edit_proceed_btn = tk.Button(self.edit_frm, text="✔ Save",
                                          width=g.BTN_WID2 - 6,
                                          command=self.edit_save)
        self.edit_proceed_btn.grid(row=10, column=1, padx=5, pady=5,
                                   sticky=tk.E)
        if self.tt:
            self.tt.add_tip(self.edit_proceed_btn, 
                            "Save changes and return to main selection window.",
                            anchor="se")
        self.edit_top.bind("<Return>", self.edit_save)


        if self.edit_top:  # May have been closed above.
            self.edit_top.update_idletasks()  # getting lag?
            self.edit_top.update()

    def edit_cancel(self):
        """ Clicked 'Cancel' or called from edit_proceed() """
        if self.tt and self.edit_top:
            self.tt.close(self.edit_top)
        self.edit_top.destroy()
        self.edit_top = None

    def edit_save(self):
        """ Clicked 'Save' button or called from edit_proceed().
            Save changes if not blank. 
            Too late to loop back so give error message blanks ignored.
        """
        # self.track_duration and self.track_no was initialized during read
        old_first_date = self.track_first_date
        self.track_meta_title = toolkit.uni_str(self.edit_title_var.get())
        self.track_artist = toolkit.uni_str(self.edit_artist_var.get())
        self.track_first_date = toolkit.uni_str(self.edit_first_date_var.get())
        self.track_composer = toolkit.uni_str(self.edit_composer_var.get())
        self.track_comment = toolkit.uni_str(self.edit_comment_var.get())
        self.set_track_to_tree(self.cd_tree_iid)
        # Note: Changes to green even when no changes
        toolkit.tv_tag_add(self.cd_tree, self.cd_tree_iid, 'update_sel')
        if old_first_date != self.track_first_date:
            # Update in treeview
            pass

        self.edit_top.update_idletasks()
        self.show_selections()
        self.edit_cancel()  # Just to remove window

    def get_track_from_tree(self, tree_iid):
        """ Get song details for give treeview item iid """
        values = self.cd_tree.item(tree_iid, 'values')
        ''' WHEN INSERTED: 
            new_values = (self.track_meta_title, self.track_artist, 
                  self.track_first_date, self.track_composer,
                  self.track_comment, self.track_duration, self.track_no) '''
        self.track_meta_title = values[0]
        self.track_artist = values[1]  # diff than album_artist for compilations
        self.track_first_date = values[2][:4]  # year portion only
        self.track_composer = values[3]  # Manually set, not in MBZ
        self.track_comment = values[4]  # Manually set, not in MBZ
        self.track_duration = values[5]  # string HH:MM:SS (0: trimmed)
        self.track_no = values[6]  # Integer track number

    def set_track_to_tree(self, tree_iid):
        """ Set song details to passed treeview item iid """
        new_values = (self.track_meta_title, self.track_artist, 
                      self.track_first_date, self.track_composer,
                      self.track_comment, self.track_duration, self.track_no)
        self.cd_tree.item(tree_iid, values=new_values)  # New values
        tree_song_title = \
            self.build_out_name(int(self.track_no), self.track_meta_title)
        out_name2 = self.build_out_name2(  # Append: | Artist | Composer
            tree_song_title, self.track_artist, self.track_composer)
        self.cd_tree.item(tree_iid, text=out_name2)  # New text line

    # ==============================================================================
    #
    #       RipCD class - Process programs in background
    #
    # ==============================================================================

    # noinspection PyTypeChecker
    def cd_run_to_close(self):
        """ This function is ALWAYS running at 30 fps and it loads external
            programs in background so they don't lag our animations.

            These flags tell us what stage we are at:
                self.disc_get_active = True
                self.mbz_get1_active = False
                self.mbz_get2_active = False
                self.treeview_active = False
                self.disc_enc_active = False
                self.active_pid = 0             # 0 = no process ID is running

        TODO: Calculate running time of background programs and kill stalls.

        """
        # If quiting kill spawned programs and return
        if RIP_CD_IS_ACTIVE is False:
            # Remove IPC_PICKLE_FNAME if it exists
            text = "End CD Ripping (encode.py)"
            self.info.cast(text)

            ext.remove_existing(IPC_PICKLE_FNAME)
            if self.active_pid > 0:
                # TODO: Use ext.kill_running
                os.popen('kill -9 ' + str(self.active_pid))
                self.active_pid = 0
            return

        if self.active_pid > 0:
            self.update_display()  # IPC background job is still active

        elif self.disc_get_active:
            # First step get disc ID in background and enter idle loop
            text = "Rip CD (encoding.py) - Begin Step 1. Getting Disc ID"
            self.info.cast(text)

            self.disc_get_active = False
            self.mbz_get1_active = True
            self.disc_id_manual_override = None

            ''' Delete all entries in old scrollbox '''
            # TODO: May have to drill down and delete grandchildren?
            self.cd_tree.delete(*self.cd_tree.get_children())
            self.get_discid_time = time.time()
            NO_STDOUT = " > " + g.TEMP_DIR + "mserve_disc_get_stdout"

            if self.caller_disc:
                ''' Disc ID passed to save time during development '''
                # ext_name = "python disc_get.py " + IPC_PICKLE_FNAME
                # self.active_pid = ext.launch_command(ext_name)
                self.active_pid = 0
                self.disc = self.caller_disc  # misleading disc object and string
                text = "ENCODE_DEV - Override with last Disc ID: " + self.disc.id
                self.info.cast(text)
                with open(IPC_PICKLE_FNAME, "wb") as f:
                    ''' Give next step what it expects to see in IPC file '''
                    pickle.dump(self.disc, f)  # Save dictionary as pickle file
            else:
                ext_name = "python disc_get.py " + IPC_PICKLE_FNAME + NO_STDOUT
                self.active_pid = ext.launch_command(ext_name)

        elif self.mbz_get1_active:

            # Update time for last step
            self.get_discid_time = time.time() - self.get_discid_time

            # Second step get Musicbrainz in background and enter idle loop
            self.mbz_get1_active = False
            self.mbz_get2_active = True
            self.mbz_get1_time = time.time()

            # Our last program has just finished. Get dictionary results
            self.disc = {}
            self.mbz_release_id = ""
            with open(IPC_PICKLE_FNAME, 'rb') as f:
                self.disc = pickle.load(f)
                # Error when no disc in drive will return dictionary, not object
                # print(self.disc)
                # pprint(vars(self.disc))

            ''' ENCODE_DEV - Save disc ID'''
            with open(lc.ENCODE_DEV_FNAME, "wb") as f:
                print("Saving", str(self.disc.id), "to:", lc.ENCODE_DEV_FNAME)
                pickle.dump(self.disc, f)  # Save dictionary as pickle file

            text = "Begin Step 2. Search MusicBrainz for Disc ID: "
            text += str(self.disc.id)
            text += "\n\nFinished Step 1. Getting Disc ID. Time: "
            text += str(self.get_discid_time)
            self.info.cast(text)

            try:
                # If valid disc object, checking dictionary causes error
                error = self.disc.get('error')
                self.mbz_get2_active = False  # Turn off next step
                #messagebox.showinfo(title="Rip CD Error", icon="error",
                #                    message="Audio CD not found", parent=self.cd_top)
                message.ShowInfo(self.cd_top, "Rip CD Error", 
                                 "Audio CD not found. Error: " + error,
                                 icon='error', thread=self.update_display)
                self.cd_close()
                return  # Empty dictionary = CD error
            except:
                # Have disc object, continue
                tracks = len(self.disc.track_lengths)
                length = sum(self.disc.track_lengths)
                sql.hist_add(
                    time.time(), 0, g.USER, 'encode', 'discid',
                    "CD/DVD Drive", "Audio CD", "libdiscid: " + self.disc.id,
                    length, tracks, self.get_discid_time,
                                                "Get disc ID: " + time.asctime(time.localtime(time.time())))

            # Note this can change in error 3 override from mbz_get1.py
            self.mbz_release_id = self.disc.id
            # self.disc

            if self.caller_disc and os.path.isfile(SAVED_MBZ1_PICKLE):
                ''' MBZ1 Pickle reused to save time during development '''
                self.active_pid = 0
                text = "ENCODE_DEV - Override with saved mbz_get1.py results:"
                text += "\n\t" + SAVED_MBZ1_PICKLE
                text += "\n\nTo prevent reuse, delete pickle file"
                self.info.cast(text)
                os.popen("cp " + SAVED_MBZ1_PICKLE + " " + IPC_PICKLE_FNAME)
            else:
    
                # Search Musicbrainz with disc object and search limit (parm 2)
                # When limit is 3 or less artwork may be limited (or non-existent)
                # TODO: When limit is 1, treeview closes
                NO_STDOUT = " > " + g.TEMP_DIR + "mserve_mbz_get1_stdout"
                ext_name = "python mbz_get1.py " + IPC_PICKLE_FNAME + " 10 " + \
                           EMAIL_ADDRESS + NO_STDOUT
                self.active_pid = ext.launch_command(ext_name,
                                                     toplevel=self.cd_top)
                # TODO: Status is getting MusicBrainz Release List with mbz_get1.py.

        elif self.mbz_get2_active:
            # Third step get mbz image list in background and enter idle loop
            self.mbz_get2_active = False
            self.treeview_active = True
            self.mbz_get1_time = time.time() - self.mbz_get1_time
            self.mbz_get2_time = time.time()

            # Our last program (mbz_get1) has just finished. Check results
            self.release_list = []
            with open(IPC_PICKLE_FNAME, 'rb') as f:
                self.release_list = pickle.load(f)

            ''' Copy for fast reloading saved pickle. '''
            os.popen("cp " + IPC_PICKLE_FNAME + " " + SAVED_MBZ1_PICKLE)
            print("Created mbz_get1.py reload results in:", SAVED_MBZ1_PICKLE)

            ''' json.dumps to file '''
            #debug_name = ext.join(g.TEMP_DIR, "mserve_mbz_get1_json")
            #with open(debug_name, "wb") as rec_f:
            #    rec_f.write(json.dumps(self.release_list))  # Dump
            #print("Created mbz_get1.py DEBUG results in:", debug_name)

            text = "Begin Step 3. Search MusicBrainz for Album Artwork: "
            text += "\n\nFinished Step 2. Search MusicBrainz for Disc ID. Time: "
            text += str(self.mbz_get1_time)
            self.info.cast(text)

            # Did mbz_get1.py report an error?
            # print('\nRELEASE LIST ==========================================')
            # pprint(self.release_list)  # To see release-list if error
            if type(self.release_list) is dict and self.release_list.get('error'):
                if self.release_list.get('error'):
                    # If dictionary type returned we know there is an error
                    self.treeview_active = False  # Turn off next step
                    err_no = self.release_list['error']
                    if err_no == "1":
                        msg = "CD contains Disc ID that isn't 28" + \
                              " characters long:\n\n" + self.disc.id + "\n"
                    elif err_no == "2":
                        # Temporary email address, replace with CFG file contents
                        msg = 'set_useragent("mserve", "0.1", EMAIL_ADDRESS)'
                    elif err_no == "3":
                        # Disc ID not found in musicbrainz, enter manually
                        if self.error_3():
                            # We have new string get for Disc ID
                            self.mbz_get1_time = time.time()
                            self.lib_top.after(33, self.cd_run_to_close)
                            return  # Don't want to execute below

                        self.cd_close()
                        return  # Empty dictionary = CD error
                    elif err_no == "4":
                        msg = "search_releases(limit=limit, strict=strict, **criteria)"
                    elif err_no == "5":
                        msg = "mbz.get_release_by_id(mbz_id, includes=['recordings'])"
                    elif err_no == "6":
                        msg = 'mbz.add_track_info() could not get release for id: '
                        msg = msg + self.release_list['message']
                        pprint(self.release_list['data'])
                        pprint(self.release_list['data2'])
                    elif err_no == "99":
                        msg = 'No internet access. Check your connections'
                        msg = msg + "OR verify discID:\n" + self.mbz_release_id
                    else:
                        msg = "Unknown error code: " + err_no

                    message.ShowInfo(title="mbz_get1.py: Musicbrainz Error",
                                     thread=self.update_display,
                                     text=msg, icon="error", parent=self.cd_top)
                    self.cd_close()
                    return  # Empty dictionary = CD error

            # Have musicbrainz release list. Log this step
            releases = len(self.release_list)
            first_release = self.release_list[0]

            self.selected_album_artist = first_release['artist-credit'][0]['artist']['name']
            self.selected_album_artist = toolkit.uni_str(self.selected_album_artist)
            self.selected_album_name = first_release['title']  # Album Title
            self.selected_album_name = toolkit.uni_str(self.selected_album_name)
            sql.hist_add(
                time.time(), 0, g.USER, 'encode', 'mbz_get1',
                self.selected_album_artist, self.selected_album_name,
                "Musicbrainz ID: " + self.mbz_release_id,
                0, releases, self.mbz_get1_time,
                "Get releases list: " + time.asctime(time.localtime(time.time())))

            if self.caller_disc and os.path.isfile(SAVED_MBZ2_PICKLE):
                ''' MBZ2 Pickle reused to save time during development '''
                self.active_pid = 0
                text = "ENCODE_DEV - Override with saved mbz_get2.py results:"
                text += "\n\t" + SAVED_MBZ2_PICKLE
                text += "\n\nTo prevent reuse, delete pickle file"
                self.info.cast(text)
                os.popen("cp " + SAVED_MBZ2_PICKLE + " " + IPC_PICKLE_FNAME)
            else:
    
                # Download images with 500x500 pixel (gets all parm. 500 ignored now)
                NO_STDOUT = " > " + g.TEMP_DIR + "mserve_mbz_get2_stdout"
                ext_name = "python mbz_get2.py " + IPC_PICKLE_FNAME + " 500" + NO_STDOUT
                self.active_pid = ext.launch_command(ext_name,
                                                     toplevel=self.cd_top)
                # TODO: Status update: getting MusicBrainz Album Artwork with mbz_get2.py.

        elif self.treeview_active:
            # Fourth step Populate Treeview and enter idle loop
            self.treeview_active = False
            # TODO: .grid() not working - button is always visible.
            # These buttons should be turned on after Medium selected
            #self.cd_tree_btn2.grid()  # Rip Disc button
            #self.cd_tree_btn3.grid()  # Image from clipboard button
            #self.cd_tree_btn4.grid()  # ? Override button
            #self.cd_top.title("Select CD song titles and cover art - mserve")

            # Our last program has just finished. Get dictionary results
            self.image_dict = {}
            with open(IPC_PICKLE_FNAME, 'rb') as f:
                self.image_dict = pickle.load(f)

            ''' Copy for fast reloading saved pickle. '''
            os.popen("cp " + IPC_PICKLE_FNAME + " " + SAVED_MBZ2_PICKLE)
            print("Created mbz_get2.py reload results in:", SAVED_MBZ2_PICKLE)

            # Did mbz_get2.py report an error?
            if self.image_dict.get('error'):
                # Errors getting Cover Art Archive images
                self.treeview_active = False  # Turn off next step
                err_no = self.image_dict['error']
                if err_no == "7":
                    msg = 'mbz_get2: Invalid dictionary passed. Check terminal output'
                    pprint(self.image.get['message'])
                elif err_no == "99":
                    msg = 'mbz_get2: No internet access. Check your connections'
                else:
                    msg = "Unknown error code: " + err_no

                message.ShowInfo(title="mbz_get2.py: Cover Art Error",
                                 thread=self.update_display,
                                 text=msg, icon="error", parent=self.cd_top)
                #thread=self.get_refresh_thread,
                self.cd_close()
                return  # Empty dictionary = CD error

            # Have musicbrainz cover art. Log this step
            releases = len(self.image_dict)
            size = sys.getsizeof(self.image_dict)

            self.mbz_get2_time = time.time() - self.mbz_get2_time

            text = "Begin Step 4. Create Treeview."
            text += "\n\nFinished Step 3. Search MusicBrainz for Album Artwork. Time: "
            text += str(self.mbz_get2_time)
            self.info.cast(text)

            # first_image = self.release_list[0]
            sql.hist_add(
                time.time(), 0, g.USER, 'encode', 'mbz_get2',
                self.selected_album_artist, self.selected_album_name, None,
                size, releases, self.mbz_get2_time,
                "Get cover art: " + time.asctime(time.localtime(time.time())))
            self.update_display()  # Give some time to lib_top()
            self.populate_cd_tree()
            self.cd_tree.update_idletasks()  # Refresh treeview display

        elif self.disc_enc_active:
            # self.encode_track_time = time.time()
            self.rip_next_track()

        else:
            pass  # Idle loop during song selections, overrides, etc.

        # Loop forever giving 30 fps control to parent
        self.lib_top.after(33, self.cd_run_to_close)

    def update_display(self):
        """ Called in cd_run_to_close() and by message.AskQuestion() """
        self.cd_spin_art()  # Rotate artwork 1°
        if self.cd_top and self.disc_enc_active:  # Ripping the CD now?
            self.update_rip_status()  # Update ripping progress
        self.active_pid = ext.check_pid_running(self.active_pid)
        self.lib_top.update()  # mserve.py lib_top
        return self.lcs.fast_refresh(tk_after=True)  # Give cycles to animations

    def error_3(self):
        """ disc.id not found in MusicBrainz """
        text = "Error encountered running command:\n\n" + \
               "mbz.get_releases_by_discid(mbz_id,\n" + \
               "includes=['artists','recordings'])\n\n" + \
               "Message is: " + \
               self.release_list['message'] + "\n\n" + \
               "Verify Disc ID retrieved from Audio CD:\n\n" + \
               self.mbz_release_id + "\n\n" + \
               "Look up correct Disc ID in musicbrainz.org.\n\n" + \
               "Would you like to manually input Disc ID?"

        answer = message.AskQuestion(
            # self.lib_top, thread=self.update_display, confirm='no', title=
            # Makes no difference play_top isn't updating display
            self.cd_top, thread=self.update_display, confirm='no',
            title="Disc ID not found in Musicbrainz", text=text, icon="question")

        if answer.result != "yes":
            return False  # Doesn't want to enter new Disc ID

        # Get the new Disk ID with AskString
        msg = "Verify Disc ID retrieved from Audio CD:\n\n" + \
              self.mbz_release_id + "\n\n" + \
              "In your browser navigate to musicbrainz.org.\n\n" + \
              "Search on Artist and Album then click on Disc ID.\n\n" + \
              "Copy 28 character Disc ID to your clipboard. Paste new\n" + \
              "Disc ID below by holding Control key and tapping V key.\n\n"

        answer = message.AskString(
            self.cd_top, thread=self.update_display,  # update_display()
            title="Enter Disc ID from Musicbrainz", text=msg, icon="information")

        if answer.result != "yes":
            return False

        # print('answer.string:', answer.string)
        if len(answer.string) != 28:
            # We could do another ShowInfo that encoding is aborting now.
            # print('answer.string length is not 28:', len(answer.string))
            return False

        self.disc_id_manual_override = answer.string

        # Write the new Disc ID to IPC pickle file
        # print('Contents of self.disc:', self.disc)
        # pprint(vars(self.disc))

        # Regenerate original pickle IPC with new discid
        with open(IPC_PICKLE_FNAME, "wb") as f:
            # store the data as binary data stream
            pickle.dump(self.disc, f)  # Save dictionary as pickle file

        # From: https://stackoverflow.com/a/17141572/6929343
        # Read in the file
        with open(IPC_PICKLE_FNAME, 'rb') as f:
            file_data = f.read()

        # Replace the target string
        file_data = file_data.replace(self.disc.id, self.disc_id_manual_override)

        # Write the file out again
        with open(IPC_PICKLE_FNAME, 'wb') as f:
            f.write(file_data)

        # Force cd_run_to_close() loop to backup one step
        self.disc_get_active = False
        self.mbz_get1_active = True
        self.mbz_get2_active = False
        self.get_discid_time = time.time()
        return True

    def cd_spin_art(self):
        """
            Spin artwork clockwise, rotate artwork 1° each decisecond
            Copied from mserve and then debug removed

            NOTE: Copied from mserve before update December 31, 2020
        """
        if RIP_CD_IS_ACTIVE is False:
            return  # CD Rip Window closed?

        if self.cd_rotated_value < -360:
            self.cd_rotated_value = 0
        self.cd_rotated_value -= 1  # Rotate another degree

        im = self.resized_art.convert('RGBA')
        self.rotated_art = Image.new(
            "RGBA", (self.art_width, self.art_height), self.background)
        rot = im.rotate(self.cd_rotated_value)
        self.rotated_art.paste(rot, (0, 0), rot)

        self.play_current_song_art = ImageTk.PhotoImage(self.rotated_art)
        self.cd_art_label.configure(image=self.play_current_song_art)

    def rip_cd(self):
        """ Rip the CD

            TODO: Hide button until all songs selected.
                  Add buttons to override Artist, Album, Composer
                  self.get_refresh

            Ensure songs selected.
            Warning if no artwork selected, Continue? Yes/No
            Warning if no date selected, Continue? Yes/No
            Warning If more than one artwork selected, alternate images
            Review window for Artist Name, Album Name, Release Date,
                First Date (If greatest hits of 80's, use 1985),
                Composer. Allow changing what release / recording used.
            Warning if Arist Name/Album Name already exists - all songs
                will go into existing path.
        """

        if not self.selected_medium:
            message.ShowInfo(
                self.cd_top, "No songs selected",
                "At least one song must be selected to Rip CD.",
                icon='error', thread=self.update_display)
                #icon = 'error', thread=self.get_refresh_thread)
            return

        self.image_count = len(self.selected_image_keys)
        if self.image_count == 0 and self.fmt != 'wav':
            #result = messagebox.askquestion(
            #    "No Images selected",
            #    "Songs will be ripped without artwork. Are You Sure?",
            #    icon='warning', parent=self.cd_top)
            #if result == 'no':
            #    return
            answer = message.AskQuestion(
                self.cd_top, "No Images selected",
                "Songs will be ripped without artwork.", confirm='yes',
                icon='warning', thread=self.update_display)
            if answer.result != 'yes':
                return

        if self.image_count > 1:
            # TODO: if .wav file this is bad.
            #result = messagebox.askquestion(
            #    "Multiple Images selected",
            #    "Songs will be ripped with alternating artwork. Are You Sure?",
            #    icon='info', parent=self.cd_top)
            #if result == 'no':
            #    return
            answer = message.AskQuestion(
                self.cd_top, "Multiple Images selected",
                "Songs will be ripped with alternating artwork.", confirm='yes',
                icon='info', thread=self.update_display)
            if answer.result != 'yes':
                return

        if not self.selected_album_date:
            #result = messagebox.askquestion(
            #    "No release date selected",
            #    "Songs will be ripped without a release date. Are You Sure?",
            #    icon='warning', parent=self.cd_top)
            # TODO: Get release date
            #if not result == 'yes':
            #    return
            answer = message.AskQuestion(
                self.cd_top, "No Album Date selected",
                "Songs will be ripped without a release date.", confirm='yes',
                icon='info', thread=self.update_display)
            if answer.result != 'yes':
                return

        self.wait_confirm_tags(final=True)

    def wait_confirm_tags(self, final=False):
        """ Allow changes to Artist, Album, Years, Compilations.
            Performs double duty confirming variables for ripping and to get
            overrides during song selection. Button is "Proceed" in the first
            case and "Save" in the latter.

        :param final: Last chance before ripping starts, Use 'Proceed' button
        :return None: The proceed button or save button triggers actions.
        """

        if not self.selected_medium:
            message.ShowInfo(
                self.cd_top, "No songs selected",
                "At least one song must be selected to override.",
                icon='error', thread=self.update_display)
            return

        ''' Saved geometry is not good. Linked to cd_top is better '''
        self.confirm_top = tk.Toplevel()
        try:
            xy = (self.cd_top.winfo_x() + g.PANEL_HGT * 3,
                  self.cd_top.winfo_y() + g.PANEL_HGT * 3)
        except AttributeError:  # CD Tree instance has no attribute 'winfo_x'
            print("self.cd_top failed to get winfo_x")
            xy = (100, 100)

        self.confirm_top.minsize(width=g.BTN_WID * 10, height=g.PANEL_HGT * 10)
        self.confirm_top.geometry('+%d+%d' % (xy[0], xy[1]))
        if final:
            self.confirm_top.title("Encode CD Final Confirmation - mserve")
        else:
            self.confirm_top.title("Album Level Overrides - mserve")
        self.confirm_top.configure(background="Gray")

        ''' Set program icon in taskbar '''
        img.taskbar_icon(self.confirm_top, 64, 'white', 'lightskyblue', 'black')

        ''' Create master frame '''
        self.confirm_frm = tk.Frame(self.confirm_top, borderwidth=g.FRM_BRD_WID,
                                    relief=tk.RIDGE)
        self.confirm_frm.grid(column=0, row=0, padx=5, pady=5, sticky=tk.NSEW)
        self.confirm_frm.columnconfigure(0, weight=1)
        self.confirm_frm.columnconfigure(1, weight=5)

        ''' Instructions '''
        PAD_X = 5
        if final:
            text = "\nFinal review before CD encoding starts.\n\n"
        else:
            text = "\nOverride Album Level variables that filter down to each\n"
            text += "Track on the Album. Track level unique values left alone."
        text += "The Genre is not provided by MusicBrainz. Enter it below.\n" + \
            "Verify correct spelling/capitalization of Artist and Album names.\n" + \
            "Verify accuracy of Album Date and Album's default Composer(s).\n" + \
            "If a compilation, Artist Name is forced to 'Various Artists'\n" + \
            "and the 1st sub-directory is forced to '" + os.sep + "Compilations'.\n" + \
            "Currently, 'Gapless Playback' has no effect in mserve.\n\n" + \
            "When overrides are applied, tracks matching the old value are given\n" + \
            "the new value. If track doesn't have old value it stays the same.\n\n" + \
            "After override, tracks can be given a unique Artist Name, First Date,\n" + \
            "Composer and Comment. Right click on any track to set uniqueness.\n\n"

        ''' Fields designated with * will update tracks matching old value 
            if self.track_artist == old_artist:  # careful here
                self.track_artist = self.selected_album_artist
            if self.track_first_date == old_date:  # careful here
                self.track_first_date = self.selected_album_date
                # Separate column # in treeview isn't updated.
            if self.track_composer == old_composer:
                self.track_composer = self.selected_composer
            if self.track_comment == old_comment:
                self.track_comment = self.selected_comment
        '''

        if final:
            text += "Once 'Proceed' is clicked, there is no going back.\n"
        else:
            text += "When 'Save' is clicked, selected songs are changed.\n"
        tk.Label(self.confirm_frm, text=text, justify="left", font=g.FONT)\
            .grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=PAD_X)
        tk.Label(self.confirm_frm, text="Album Artist:",
                 font=g.FONT).grid(row=1, column=0, padx=5, sticky=tk.W)
        tk.Entry(self.confirm_frm, textvariable=self.album_artist_var,
                 font=g.FONT).grid(row=1, column=1, padx=5, sticky=tk.EW)
        tk.Label(self.confirm_frm, text="Compilation?",
                 font=g.FONT).grid(row=2, column=0, padx=5, sticky=tk.W)
        c = tk.Entry(self.confirm_frm, textvariable=self.compilation_var,
                     font=g.FONT)
        c.grid(row=2, column=1, padx=5, sticky=tk.EW)
        ''' Clicking on compilation_var is treated like button click '''
        c.bind("<Button>", self.get_compilation)
        tk.Label(self.confirm_frm, text="Album Name:",
                 font=g.FONT).grid(row=3, column=0, padx=5, sticky=tk.W)
        tk.Entry(self.confirm_frm, textvariable=self.album_name_var,
                 font=g.FONT).grid(row=3, column=1, padx=5, sticky=tk.EW)
        tk.Label(self.confirm_frm, text="Album Date:",
                 font=g.FONT).grid(row=4, column=0, padx=5, sticky=tk.W)
        tk.Entry(self.confirm_frm, textvariable=self.album_date_var,
                 font=g.FONT).grid(row=4, column=1, padx=5, sticky=tk.EW)
        tk.Label(self.confirm_frm, text="Composer:",
                 font=g.FONT).grid(row=5, column=0, padx=5, sticky=tk.W)
        tk.Entry(self.confirm_frm, textvariable=self.composer_var,
                 font=g.FONT).grid(row=5, column=1, padx=5, sticky=tk.EW)
        tk.Label(self.confirm_frm, text="Genre:",
                 font=g.FONT).grid(row=6, column=0, padx=5, sticky=tk.W)
        tk.Entry(self.confirm_frm, textvariable=self.genre_var,
                 font=g.FONT).grid(row=6, column=1, padx=5, sticky=tk.EW)
        tk.Label(self.confirm_frm, text="Disc Number:",
                 font=g.FONT).grid(row=7, column=0, padx=5, sticky=tk.W)
        tk.Entry(self.confirm_frm, textvariable=self.disc_number_var,
                 font=g.FONT).grid(row=7, column=1, padx=5, sticky=tk.EW)
        tk.Label(self.confirm_frm, text="Gapless Playback:",
                 font=g.FONT).grid(row=8, column=0, padx=5, sticky=tk.W)
        gp = tk.Entry(self.confirm_frm, textvariable=self.gapless_playback_var,
                      font=g.FONT)
        gp.grid(row=8, column=1, padx=5, sticky=tk.EW)
        ''' Clicking on gapless_playback is treated like button click '''
        gp.bind("<Button>", self.get_gapless_playback)
        tk.Label(self.confirm_frm, text="Comments:",
                 font=g.FONT).grid(row=9, column=0, padx=5, sticky=tk.W)
        com = tk.Entry(self.confirm_frm, textvariable=self.comment_var,
                       font=g.FONT)
        com.grid(row=9, column=1, padx=5, sticky=tk.EW)

        ''' Set variables '''
        self.album_artist_var.set(self.selected_album_artist)
        self.compilation_var.set(self.selected_compilation)
        self.album_name_var.set(self.selected_album_name)
        self.album_date_var.set(self.selected_album_date)
        self.composer_var.set(self.selected_composer)
        self.comment_var.set(self.selected_comment)
        self.disc_number_var.set(self.selected_disc_number)
        self.genre_var.set(self.selected_genre)
        self.gapless_playback_var.set(self.selected_gapless_playback)

        ''' Go Back Button '''
        self.confirm_cancel_btn = tk.Button(self.confirm_frm, text="✘ Go Back",
                                            width=g.BTN_WID2 - 6,
                                            command=self.confirm_cancel)
        self.confirm_cancel_btn.grid(row=10, column=0, padx=5, pady=5, sticky=tk.W)
        if self.tt:
            self.tt.add_tip(self.confirm_cancel_btn, "Return to main selection window.",
                            anchor="sw")
        self.confirm_top.bind("<Escape>", self.confirm_cancel)
        self.confirm_top.protocol("WM_DELETE_WINDOW", self.confirm_cancel)

        if final:
            ''' Proceed Button '''
            self.confirm_proceed_btn = tk.Button(self.confirm_frm, text="✔ Proceed",
                                                 width=g.BTN_WID2 - 6,
                                                 command=self.confirm_proceed)
            self.confirm_proceed_btn.grid(row=10, column=1, padx=5, pady=5,
                                          sticky=tk.E)
            if self.tt:
                self.tt.add_tip(self.confirm_proceed_btn, "Save changes and begin encoding.",
                                anchor="se")
            self.confirm_top.bind("<Return>", self.confirm_proceed)
        else:
            ''' Save Button '''
            self.confirm_proceed_btn = tk.Button(self.confirm_frm, text="✔ Save",
                                                 width=g.BTN_WID2 - 6,
                                                 command=self.confirm_save)
            self.confirm_proceed_btn.grid(row=10, column=1, padx=5, pady=5,
                                          sticky=tk.E)
            if self.tt:
                self.tt.add_tip(self.confirm_proceed_btn, 
                                "Save changes and return to main selection window.",
                                anchor="se")
            self.confirm_top.bind("<Return>", self.confirm_save)


        if self.confirm_top:  # May have been closed above.
            self.confirm_top.update_idletasks()

    def apply_override_to_tracks(
            self, old_artist, old_date, old_composer, old_comment):
        """ Put new Album defaults into old tree items """
        if old_artist == self.selected_album_artist and \
                old_composer == self.selected_composer and \
                old_comment == self.selected_comment and \
                old_date == self.selected_album_date:
            return  # No changes

        ''' Loop through all tracks in medium finding old matches '''
        for i, track_id in enumerate(self.cd_tree.get_children(
                self.selected_medium)):
            self.get_track_from_tree(track_id)  # track values
            ''' If old values same, set to new values '''
            track_changed = False
            if self.track_artist == old_artist:  # careful here
                self.track_artist = self.selected_album_artist
                track_changed = True
            if self.track_first_date == old_date:  # careful here
                self.track_first_date = self.selected_album_date
                track_changed = True
            if self.track_composer == old_composer:
                self.track_composer = self.selected_composer
                track_changed = True
            if self.track_comment == old_comment:
                self.track_comment = self.selected_comment
                track_changed = True

            if track_changed:
                self.set_track_to_tree(track_id)  # save track values
                # Below sets every single track to Green which defeats purpose
                #toolkit.tv_tag_add(self.cd_tree, track_id, 'update_sel')
        title = "Check Track Details"
        text = "Track(s) changed with new Album Level Overrides."
        message.ShowInfo(self.cd_top, title, text, thread=self.update_display)

    def get_compilation(self, *args):
        """ Use AskQuestion to set "1" (yes) or "0" (no) """
        title = "Set Compilation Flag"
        text = "If a compilation, the Album is created under the sub-directory '"
        text += os.sep + "Compilations'.\n"
        text += "The Album Artist is forced as 'Various Artists' however, each "
        text += "music file will\nhave the real artist name encoded inside.\n\n"
        text += "Is this a compilation?"
        answer = message.AskQuestion(self.confirm_top, title, text, align='left',
                                     confirm='no', thread=self.update_display)
        if answer.result == 'yes':
            self.compilation_var.set("1")
        else:
            self.compilation_var.set("0")

    def get_gapless_playback(self, *args):
        """ Use AskQuestion to set "1" (yes) or "0" (no) """
        title = "Set Gapless Playback Flag"
        text = "mserve doesn't support Gapless Playback however some music\n"
        text += "players do support it. This option can be useful for other\n"
        text += "music players using the encoded music file.\n\n"
        text += "Use Gapless Playback?"
        answer = message.AskQuestion(self.confirm_top, title, text, align='left',
                                     thread=self.update_display)
        if answer.result == 'yes':
            self.gapless_playback_var.set("1")
        else:
            self.gapless_playback_var.set("0")

    def confirm_cancel(self, *args):
        """ Clicked 'Cancel' or called from confirm_proceed() """
        if self.tt and self.confirm_top:
            self.tt.close(self.confirm_top)
        self.confirm_top.destroy()
        self.confirm_top = None

    def confirm_save(self, *args):
        """ Clicked 'Save' button or called from confirm_proceed().
            Save changes if not blank. 
            Too late to loop back so give error message blanks ignored.
        """
        old_artist = self.selected_album_artist
        old_date = self.selected_album_date
        old_composer = self.selected_composer
        old_comment = self.selected_comment
        self.confirm_top.update_idletasks()  # New values not instant?
        self.selected_album_artist = self.confirm_non_blank(
            "Album Artist", self.album_artist_var, self.selected_album_artist)
        # Compilation treated like button invoking message.AskQuestion()
        self.selected_album_name = self.confirm_non_blank(
            "Album Name", self.album_name_var, self.selected_album_name)
        self.selected_album_date = self.confirm_non_blank(
            "Album Date", self.album_date_var, self.selected_album_date)
        self.selected_composer = self.confirm_non_blank(
            "Composer", self.composer_var, self.selected_composer)
        self.selected_comment = self.confirm_non_blank(
            "Comments", self.comment_var, self.selected_comment)
        self.selected_disc_number = self.confirm_non_blank(
            "Disc Number", self.disc_number_var, self.selected_disc_number)
        self.selected_genre = self.confirm_non_blank(
            "Album Artist", self.genre_var, self.selected_genre)
        # Gapless Playback treated like button invoking message.AskQuestion()
        self.apply_override_to_tracks(
            old_artist, old_date, old_composer, old_comment)
        self.show_selections()
        self.confirm_cancel(*args)  # Just to remove window
        return True  # Could return False to abort ripping

    def confirm_non_blank(self, fld_name, var_name, old_value):
        """ Confirm when blanking out fields. """
        new_value = toolkit.uni_str(var_name.get())
        if not new_value and old_value:
            title = "Confirm blanking out variable"
            text = fld_name + " old value was: " + str(old_value)
            text += "\nAre you sure you want to blank out the " + fld_name + "?"
            answer = message.AskQuestion(self.confirm_top, title, text, confirm='no',
                                         thread=self.update_display)
            if answer.result != 'yes':
                var_name.set(old_value)
                self.confirm_top.update_idletasks()
                return old_value
        return new_value

    def confirm_proceed(self, *args):
        """ Clicked 'Proceed' """
        if not self.confirm_save(*args):  # blank fields encountered?
            return  # Leave screen in play

        self.rip_current_track = 0  # Nothing has been ripped yet
        if not self.set_gst_encoding():  # Do this a LOT earlier
            exit()  # Programmer error - NEVER happens
        self.cd_top.title("Ripping CD to " + self.topdir + " - mserve")
        self.song_rip_sec = 0  # How many seconds and blocks
        self.song_rip_blk = 0  # have been ripped for song?
        self.total_rip_sec = 0  # How many seconds and blocks
        self.total_rip_blk = 0  # ripped for selections?

        # Pulsating shades of green indicating which song is being ripped
        self.last_highlighted = None
        self.last_shade = None
        self.skip_once = False
        self.next_image_key_ndx = 0

        ''' BIG EVENT TRIGGER '''
        self.disc_enc_active = True  # Start background processing

#
#  Ripping Methods
#

    # noinspection SpellCheckingInspection,PyPep8Naming
    def set_gst_encoding(self):
        """ https://gstreamer.freedesktop.org/documentation/tools/gst-launch.html """
        if self.fmt == 'wav':
            self.gst_encoding = 'wavenc'
        elif self.fmt == 'flac':
            self.gst_encoding = 'flacenc'
            from mutagen.flac import FLAC as audio_file
        elif self.fmt == 'oga':
            # "70" percent qaulity becomes "0.7"
            quality = 'quality=' + str(float(self.quality_var.get()) / 100.0)
            self.gst_encoding = 'vorbisenc {} ! oggmux'.format(quality)
            from mutagen.oggvorbis import OggVorbis as audio_file
        elif self.fmt == 'm4a':
            # Later quality can set Bitrate. Assume 256kbps is 70% quality for now
            # Highest bitrate is 320kbps. gstreamer default is 128kbps
            # https://gstreamer.freedesktop.org/documentation/voaacenc/index.html?gi-language=c
            quality_ndx = (int(self.quality_var.get()) - 30) / 10  # 30% to 100%
            kbps = [96, 112, 128, 160, 192, 224, 256, 320]
            bitrate = kbps[quality_ndx] * 1000
            quality = 'bitrate=' + str(bitrate)
            self.gst_encoding = 'voaacenc {} ! mp4mux '.format(quality)
            from mutagen.mp4 import MP4 as audio_file

            ''' Tags: https://mutagen.readthedocs.io/en/latest/api/mp4.html#mutagen.mp4.MP4Tags
            Bases: mutagen._util.DictProxy, mutagen.Tags
            Dictionary containing Apple iTunes metadata list key/values.
            Keys are four byte identifiers, except for freeform (’—-‘) keys. 
            Values are usually unicode strings, but some atoms have a special
            structure:
            Text values (multiple values per key are supported):
                ‘\xa9nam’ – track title
                ‘\xa9alb’ – album
                ‘\xa9ART’ – artist
                ‘aART’ – album artist
                ‘\xa9wrt’ – composer
                ‘\xa9day’ – year
                ‘\xa9cmt’ – comment
                ‘\xa9grp’ – grouping
                ‘\xa9gen’ – genre
                ‘\xa9lyr’ – lyrics
                ‘\xa9too’ – encoded by
                ‘cprt’ – copyright
                ‘\xa9wrk’ – work
                ‘\xa9mvn’ – movement
            
            Boolean values:
                ‘cpil’ – part of a compilation
                ‘pgap’ – part of a gapless album
                ‘pcst’ – podcast (iTunes reads this only on import)
            
            Tuples of ints (multiple values per key are supported):
                ‘trkn’ – track number, total tracks
                ‘disk’ – disc number, total discs
            
            Integer values:
                ‘tmpo’ – tempo/BPM
                ‘\xa9mvc’ – Movement Count
                ‘\xa9mvi’ – Movement Index
                ‘shwm’ – work/movement
                ‘stik’ – Media Kind
                ‘hdvd’ – HD Video
                ‘rtng’ – Content Rating
                ‘tves’ – TV Episode
                ‘tvsn’ – TV Season
                ‘plID’, ‘cnID’, ‘geID’, ‘atID’, ‘sfID’, ‘cmID’, ‘akID’ 
                    – Various iTunes Internal IDs
            
            Others:
                ‘covr’ – cover artwork, list of MP4Cover objects (which are 
                         tagged strs)
                ‘gnre’ – ID3v1 genre. Not supported, use ‘\xa9gen’ instead.
            
            The freeform ‘—-’ frames use a key in the format ‘—-:mean:name’ 
            where ‘mean’ is usually ‘com.apple.iTunes’ and ‘name’ is a 
            unique identifier for this frame. The value is a str, but is 
            probably text that can be decoded as UTF-8. Multiple values 
            per key are supported.
            
            MP4 tag data cannot exist outside of the structure of an MP4 
            file, so this class should not be manually instantiated.
            
            Unknown non-text tags and tags that failed to parse will be 
            written back as is.            

            https://gist.github.com/lemon24/ebd0b8fa9b223be1948cddc279ea7970
            shutil.copy('original.mp4', 'new.mp4')

            # mutagen.File knows how to open any file (works with both MP4 and M4A):
            #
            # https://mutagen.readthedocs.io/en/latest/user/gettingstarted.html    
            # https://mutagen.readthedocs.io/en/latest/api/base.html#mutagen.File

            '''
        else:
            print('Programmer ERROR set_gst_encoding() bad fmt=', fmt)
            return False

        return True

    # noinspection PyPep8Naming, SpellCheckingInspection
    def rip_next_track(self):
        """ If just finished a track, update last rip with metadata.
            Start new rip in background and return.
            Main loop waits until active_pid finishes.
        """

        self.cd_rotated_value = 0  # Start next song with animation right-side up

        ''' Just finish ripping a song? '''
        if self.rip_current_track > 0:
            # print('END:   self.encode_track_time:', time.time())
            self.encode_track_time = time.time() - self.encode_track_time
            self.add_sql_music()  # Create base sql Music Table Row
            self.encode_album_time += self.encode_track_time
            self.encode_album_seconds += self.song_seconds
            self.encode_album_track_cnt += 1
            self.encode_album_size += self.song_size
            self.scrollbox.highlight_pattern(self.os_song_name, "green")
            self.last_highlighted = self.os_song_name  # Tag song as completed

            if not self.fmt == "wav":  # Does song format support metadata?
                self.add_metadata_to_song()  # Use Metagen to update song
                self.add_sql_metadata()  # Update SQL with metadata
                if self.image_count > 0:  # Apply Cover art
                    if self.fmt == "oga":
                        self.add_image_to_oga()
                    elif self.fmt == "flac":
                        self.add_image_to_flac()
                    elif self.fmt == "m4a":
                        self.add_image_to_m4a()
                    else:
                        print('Programmer ERROR: Add unknown image support.')
            else:
                ''' TODO: Review adding .wav to SQL ffMajor (MAJOR_BRAND)
                          reported by `ffprobe` would state 'WAV' to identify. '''
                pass  # TODO: Manually add 'file' 'init' history record

        if self.image_count > 0:  # Alternate tracks with next image
            image_key = self.selected_image_keys[self.next_image_key_ndx]
            self.image_data = self.get_image_by_key(image_key)
            self.image_data_to_frame(self.image_data) # Update artwork
            self.next_image_key_ndx += 1  # Setup for next track
            if self.next_image_key_ndx == self.image_count:
                self.next_image_key_ndx = 0  # End of image list, back 1st

        if not self.get_next_rip_name():  # Last track just finished?
            if self.encode_album_track_cnt > 0:  # Save SQL history for album
                duration = tmf.mm_ss(self.encode_album_seconds)
                sql.hist_add(
                    time.time(), 0, g.USER, 'encode', 'album',
                    self.selected_album_artist, self.selected_album_name,
                    "Audio disc id: " + self.disc.id, self.encode_album_size,
                    self.encode_album_seconds, self.encode_album_time,
                    "Tracks: " + str(self.encode_album_track_cnt) +
                    " Duration: " + duration +
                    " Finished: " + time.asctime(time.localtime(time.time())))
            '''
            Expand message.ShowInfo() with totals:
                # Add to album totals
                self.encode_album_time += self.encode_track_time
                self.encode_album_seconds += self.song_seconds
                self.encode_album_track_cnt += 1
                self.encode_album_size += self.song_size
            '''
            title = "Encoding (Ripping) is complete."
            text = "Restart mserve to see new songs in Music Location Tree."
            message.ShowInfo(
                self.cd_top, title, text,
                thread=self.get_refresh_thread)  # Don't use update_display()

            self.disc_enc_active = False  # Signal background processing over
            self.cd_close()  # Close windows
            return  # Last command - All done

        # Rip next track
        self.encode_track_time = time.time()
        NO_STDOUT = " > " + g.TEMP_DIR + "mserve_gst_launch"
        ext_name = 'gst-launch-1.0 cdiocddasrc track={} ! ' \
                   .format(self.rip_current_track) + \
                   'audioconvert ! {} '.format(self.gst_encoding)
        ext_name += ' ! filesink location="{}"'.format(self.os_full_path)
        ext_name += NO_STDOUT

        # ext_name = "sleep 3" # Activate this for speedy loop testing
        self.active_pid = ext.launch_command(ext_name,
                                             toplevel=self.cd_top)

        # TODO: Call webscrape and get lyrics into buffer
        return  # Loops for next song

    def add_sql_music(self):
        """ Populate SQL Music Table Row with new CD track before encoding
            success. """
        # os.stat returns file attributes object
        stat = os.stat(self.os_full_path)
        self.song_size = int(stat.st_size)
        ''' Set creation time for metadata storage '''
        dt = datetime.datetime.fromtimestamp(stat.st_mtime)
        self.CreationTime = dt.strftime('%Y-%m-%d %H:%M:%S')  # This is correct 2nd time

        ''' Add the song without metadata '''
        # 'sql' conflict with import. Use 'sql_cmd' instead
        sql_cmd = "INSERT OR IGNORE INTO Music (OsFileName, OsAccessTime, \
            OsModifyTime, OsChangeTime, OsFileSize) \
            VALUES (?, ?, ?, ?, ?)"
        sql.cursor.execute(sql_cmd, (self.sqlOsFileName, stat.st_atime,
                                     stat.st_mtime, stat.st_ctime, self.song_size))
        sql.con.commit()
        last_music_id = sql.cursor.lastrowid
        # returning last history # 20,659 when no insert (already exists)

        ''' Check if song existed previously in SQL. '''
        sql.cursor.execute("SELECT Id FROM Music WHERE OsFileName = ?",
                           [self.sqlOsFileName])
        d = dict(sql.cursor.fetchone())
        self.music_id = d["Id"]
        if self.music_id != last_music_id:
            ''' The last encoding may be different quality and file size.
                use new stat variables and leave metadata / lyrics on file. '''
            text = "Song file already encoded. Updating file times and size in SQL."
            print("\n" + text)
            print('self.music_id:', self.music_id, "last_music_id:", last_music_id)
            self.info.cast(text)
            sql_cmd = "UPDATE Music SET OsAccessTime=?, OsModifyTime=?, \
                OsChangeTime=?, OsFileSize=? WHERE OsFileName = ?"
            sql.cursor.execute(sql_cmd,
                               (stat.st_atime, stat.st_mtime, stat.st_ctime,
                                self.song_size, self.sqlOsFileName))
            sql.con.commit()  # This update not working, times show 1/2 hour ago.

        self.rip_ctl.new(self.os_full_path)  # Setup FileControl() after SQL added

        sql.hist_add(
            time.time(), self.music_id, g.USER, 'file', 'init',
            self.track_artist, self.os_song_name, self.sqlOsFileName,
            self.song_size, self.song_seconds, self.encode_track_time,
            "encoded: " + time.asctime(time.localtime(time.time())))
        sql.hist_add(
            time.time(), self.music_id, g.USER, 'encode', 'track',
            self.track_artist, self.os_song_name, self.sqlOsFileName,
            self.song_size, self.song_seconds, self.encode_track_time,
            "finished: " + time.asctime(time.localtime(time.time())))

    def add_sql_metadata(self):
        """ July 13, 2023 - Need DiscNumber, FirstDate, CreationTime, Composer,
            GaplessPlayback, AlbumDate, Compilation, """
        genre = None  # TODO: Get with tk.Entry like release date
        # genre = ""                  # None type breaks genre.decode("utf8")

        ''' July 18, 2023 (actually August 12, 2023) Version 3 '''
        sql.update_metadata(self.rip_ctl)

        ''' July 13, 2023 (actually August 12, 2023) Version 2  
        sql.update_metadata(  # old version 2 parameters
            self.sqlOsFileName, self.selected_album_artist, self.selected_album_name,
            self.selected_title, genre, self.tracknumber, self.selected_album_date,
            self.song_seconds, self.track_duration, self.DiscNumber,
            self.selected_composer)
        '''
        ''' Old version 1 parameters
        sql.update_metadata(
            self.sqlOsFileName, self.selected_album_artist, self.selected_album_name,
            self.selected_title, genre, self.tracknumber, self.selected_album_date,
            self.song_seconds, self.track_duration)
        '''  # convert July 13, 2023 

        # Above automatically creates history records for 'meta' 'init'

    # noinspection PyPep8Naming, SpellCheckingInspection
    def add_metadata_to_song(self):
        """ July 13, 2023 - Need DiscNumber, AlbumArtist, AlbumDate, Genre,
            Compilation "0" or "1". CreationTime, Composer """
        if self.fmt == 'flac':
            from mutagen.flac import FLAC as audio_file
        elif self.fmt == 'oga':
            from mutagen.oggvorbis import OggVorbis as audio_file
        elif self.fmt == 'm4a':
            from mutagen.mp4 import MP4 as audio_file
        else:
            print('Programmer ERROR: add_metadata_to_song() bad fmt=', self.fmt)
            return False

        try:
            audio = audio_file(self.os_full_path)
        except UnicodeDecodeError as err:
            print(err)
            print('UnicodeDecodeError ERROR mutagen.oggvorbis on file:')
            print(self.os_full_path)
            return False
        except TypeError as err:  # load() takes exactly 3 arguments (2 given)
            print(err)
            print('TypeError ERROR mutagen.mp4 on file:')
            print(self.os_full_path)
            return False

        # print("self.tracknumber before rip track:", self.tracknumber)
        self.tracknumber = str(self.rip_current_track) + \
            "/" + str(self.disc.last_track)
        self.tracknumber = toolkit.uni_str(self.tracknumber)

        if self.fmt == "m4a":
            audio['\xa9too'] = "mserve " + g.MSERVE_VERSION
            audio['\xa9nam'] = self.track_meta_title
            audio['\xa9ART'] = self.track_artist
            audio['\xa9alb'] = self.selected_album_name
            if self.selected_album_artist:
                audio['aART'] = self.selected_album_artist
            if self.track_composer:
                audio['\xa9wrt'] = self.track_composer
            if self.track_first_date:
                audio['\xa9day'] = self.track_first_date
            if self.track_comment:
                audio['\xa9cmt'] = self.track_comment
            if self.selected_genre:
                audio['\xa9gen’'] = self.selected_genre
            if self.selected_album_date:
                audio['cprt'] = self.selected_album_date
            if self.selected_compilation:
                audio['cpil'] = int(self.selected_compilation)
            if self.selected_gapless_playback:
                audio['pgap'] = int(self.selected_gapless_playback)
            if self.DiscNumber:
                str_a, str_b = self.DiscNumber.split("/")
                audio['disk'] = [(int(str_a), int(str_b))]
                # https://stackoverflow.com/a/70563415/6929343
            if self.tracknumber:
                str_a, str_b = self.tracknumber.split("/")
                audio['trkn'] = [(int(str_a), int(str_b))]
            if self.CreationTime:  # ID3.2.4 tag works in Kid 3
                audio['TDEN'] = self.CreationTime
        else:
            ''' Assume below will be ignored by mutagen MP4 '''
            audio['ENCODER'] = "mserve " + g.MSERVE_VERSION

            """ July 13, 2023 - Need Genre, FirstDate, CreationTime, Compilation, 
                                Composer, Comment, Gapless Playback """
            # July 13, 2023 - Perhaps ALBUMARTIST is the original band/artist

            """ July 13, 2023 - 'ARTIST' would be Clarence Clemmons """
            audio['TITLE'] = self.track_meta_title  # '99 -' and .ext stripped
            # 'ARTIST' goes to 'ALBUMARTIST' in Kid3 and iTunes
            audio['ARTIST'] = self.track_artist
            audio['ALBUM'] = self.selected_album_name
            audio['TRACK_NUMBER'] = self.tracknumber  # kid3 show 'Track Number'
            if self.selected_album_artist:
                audio['ALBUM_ARTIST'] = self.selected_album_artist

            """ July 13, 2023 - 'ALBUM' would be Greatest Hits [Disc 3] 
            if self.selected_compilation:
                audio['cpil'] = int(self.selected_compilation)
            if self.selected_gapless_playback:
                audio['pgap'] = int(self.selected_gapless_playback)
            """
            if self.track_composer:
                audio['COMPOSER'] = self.track_composer
            if self.track_first_date:  # first_date
                audio['DATE'] = self.track_first_date
            if self.selected_genre:
                audio['GENRE'] = self.selected_genre
            if self.selected_album_date:
                audio['RECORDING_DATE'] = self.selected_album_date
            if self.track_comment:
                # self.selected_comment may exist but would be applied to tracks.
                audio['COMMENT'] = self.track_comment
            if self.DiscNumber:
                audio['DISC_NUMBER'] = self.DiscNumber  # July 13, 2023
            if self.CreationTime:  # Apple iTunes m4a no tag, use 'TDEN' ID3.2.4
                audio['CREATION_TIME'] = self.CreationTime  # July 13, 2023 CreationTime
            # What about Musicbrainz ID? It is auto added along with discid
            # Add comment "Encoded 2020-10-16 12:15, format: x, quality: y
            # Already has comment in 'file' command header

        # audio.save(v2_version=3)    # Version 4 causing problems?
        audio.save()  # v2_version flag unknown

        # noinspection SpellCheckingInspection
        '''
            Other ripping image options from:
    https://www.programcreek.com/python/example/84797/mutagen.id3.ID3
    def modified_id3(self, file_name, info):
            id3 = ID3()
            id3.add(TRCK(encoding=3, text=str(info['track'])))
            id3.add(TDRC(encoding=3, text=str(info['year'])))
            id3.add(TIT2(encoding=3, text=info['song_name']))
            id3.add(TALB(encoding=3, text=info['album_name']))
            id3.add(TPE1(encoding=3, text=info['artist_name']))
            id3.add(TPOS(encoding=3, text=str(info['cd_serial'])))
            lyric_data = self.get_lyric(info)
            id3.add(USLT(encoding=3, text=lyric_data)) if lyric_data else None
            #id3.add(TCOM(encoding=3, text=info['composer']))
            #id3.add(WXXX(encoding=3, desc=u'xiami_song_url', text=info['song_url']))
            #id3.add(TCON(encoding=3, text=u'genre'))
            #id3.add(TSST(encoding=3, text=info['sub_title']))
            #id3.add(TSRC(encoding=3, text=info['disc_code']))
            id3.add(COMM(encoding=3, desc=u'Comment', \
                text=info['comment']))
            id3.add(APIC(encoding=3, mime=u'image/jpeg', type=3, \
                desc=u'Front Cover', data=self.get_cover(info)))
            id3.save(file_name) 

    Another example: https://stackoverflow.com/a/14040318/6929343

    from mutagen.id3 import ID3NoHeaderError
    from mutagen.id3 import ID3, TIT2, TALB, TPE1, TPE2, COMM, TCOM, TCON, TDRC

    # Read ID3 tag or create it if not present
    try: 
        tags = ID3(fname)
    except ID3NoHeaderError:
        print("Adding ID3 header")
        tags = ID3()

    tags["TIT2"] = TIT2(encoding=3, text=title)
    tags["TALB"] = TALB(encoding=3, text=u'mutagen Album Name')
    tags["TPE2"] = TPE2(encoding=3, text=u'mutagen Band')
    tags["COMM"] = COMM(encoding=3, lang=u'eng', desc='desc', text=u'mutagen comment')
    tags["TPE1"] = TPE1(encoding=3, text=u'mutagen Artist')
    tags["TCOM"] = TCOM(encoding=3, text=u'mutagen Composer')
    tags["TCON"] = TCON(encoding=3, text=u'mutagen Genre')
    tags["TDRC"] = TDRC(encoding=3, text=u'2010')
    tags["TRCK"] = TRCK(encoding=3, text=u'track_number')

    tags.save(fname)
    
    
    What Media Monkey says about dates:
    
    MediaMonkey 5,4 and 3, by default save Year and Date metadata in 
    ID3 v2.3 tags to TYER / TDRC frames. Although this is generally a 
    good approach for maximum compatibility, some users may wish to 
    change this since TDRC is normally associated with ID3 v2.4 tags 
    and Winamp will not read the TDRC field for an ID3v2.3 tag. This 
    can be done by modifying MediaMonkey’s .ini file with the following 
    section which allows you to enable/disable frames at will:

    [MP3Tagging]
    DisableFrames=TDAT;TDRC
    EnableFrames=TYER
    
    To also solve the problem of Original Year being saved twice, the 
    MP3Tagging section in MediaMonkey.ini should look like this:
    
    [MP3Tagging]
    DisableFrames=TDRC;TDOR;
    EnableFrames=TYER;TDAT;TORY;
    
    This disables the ID3v2.4 TDOR which MM is using for Original Year, 
    and enables use of the ID3v2.3 TORY, intended for original release year.
        '''

    # noinspection SpellCheckingInspection
    def add_image_to_oga(self):
        """ FLAC and OGG have different methods. OGG has diff read/write too.
            See: https://mutagen.readthedocs.io/en/latest/user/vcomment.html
        """
        import base64
        from mutagen.oggvorbis import OggVorbis
        # noinspection PyProtectedMember
        from mutagen.flac import Picture

        try:
            audio = OggVorbis(self.os_full_path)
        except UnicodeDecodeError as err:
            print(err)
            print('add_image_to_oga() ERROR mutagen.oggvorbis on audio:')
            print(self.os_full_path)
            return False

        picture = Picture()  # For FLAC files

        # Convert image to jpeg for saving

        # print('Opening image being encoded with picture.data')
        # TODO: There are two different python-magic, expand to handle that.
        # print('magic contents:')
        ''' TODO: Also saving in add_image_to_m4a() '''
        m = magic.open(magic.MAGIC_MIME_TYPE)
        m.load()
        mime_type = m.buffer(self.image_data)
        picture.mime = mime_type.encode('utf-8')
        # print(mime_type)

        #        self.image_data_to_frame(self.image_data)               # Shortcut
        #        width, height = self.original_art.size
        #        mode_to_bpp = {"1": 1, "L": 8, "P": 8, "RGB": 24, "RGBA": 32, \
        #                       "CMYK": 32, "YCbCr": 24, "LAB": 24, "HSV": 24, \
        #                       "I": 32, "F": 32}
        #        depth = mode_to_bpp[self.original_art.mode]
        #        print('width, height, depth, format:', width, height, depth, form)

        picture.data = self.image_data
        picture.type = 3  # Hex 03 - Cover (Front)
        picture.desc = self.track_meta_title
        #width, height, depth = 100, 100, 32  # Defaults have no effect
        #picture.width = width  # Seems to have no effect?
        #picture.height = height
        #picture.depth = depth

        try:
            picture_data = picture.write()
        except UnicodeDecodeError as err:  # desc = self.desc.encode('UTF-8')
            print(err)
            print('add_image_to_oga() ERROR mutagen.flac.Picture.write on file:')
            print(self.os_full_path)
            return False

        encoded_data = base64.b64encode(picture_data)
        vcomment_value = encoded_data.decode("ascii")

        audio["metadata_block_picture"] = [vcomment_value]
        audio.save()

    def add_image_to_flac(self):
        """ From: https://stackoverflow.com/a/7282712/6929343
            NOT TESTED as of Aug 16/23
        """
        from mutagen import File  # User comments this no longer exists
        from mutagen.flac import Picture, FLAC
        audio = File(self.os_full_path)
        image = Picture()
        image.type = 3

        m = magic.open(magic.MAGIC_MIME_TYPE)
        m.load()
        mime = m.buffer(self.image_data)
        if mime == "image/jpeg":
            art_name = RIP_ARTWORK + ".jpg"  # .ext for PIL to figure out
        else:
            art_name = RIP_ARTWORK + ".png"
        image.mime = mime  # Missing in original answer
        ''' Save image as file for mutagen to read back in '''
        t_file = io.BytesIO(self.image_data)
        self.original_art = Image.open(t_file)
        self.original_art.save(art_name)
        del t_file  # Delete object to save memory

        #if albumart.endswith('png'):  # From original answer, but mime not used?
        #    mime = 'image/png'
        #else:
        #    mime = 'image/jpeg'
        image.desc = 'front cover'
        with open(art_name, 'rb') as f:
            image.data = f.read()

        audio.add_picture(image)
        audio.save()

    def add_image_to_m4a(self):
        """ See: https://mutagen.readthedocs.io/en/latest/api/mp4.html#mutagen.mp4.MP4Tags

        """
        from mutagen.mp4 import MP4, MP4Cover

        video = MP4(self.os_full_path)

        ''' TODO: Also saving in add_image_to_oga() '''
        m = magic.open(magic.MAGIC_MIME_TYPE)
        m.load()
        mime_type = m.buffer(self.image_data)
        print("mime_type:", mime_type)  # image/jpeg
        if mime_type == "image/jpeg":
            cover_format = 'MP4Cover.FORMAT_JPEG'  # for Mutagen to figure out
            art_name = RIP_ARTWORK + ".jpg"  # .ext for PIL to figure out
        else:
            cover_format = 'MP4Cover.FORMAT_PNG'
            art_name = RIP_ARTWORK + ".png"

        ''' Save image as file for mutagen to read back in '''
        t_file = io.BytesIO(self.image_data)
        self.original_art = Image.open(t_file)
        self.original_art.save(art_name)
        del t_file  # Delete object to save memory

        # https://stackoverflow.com/a/56673959/6929343
        with open(art_name, 'rb') as f:
            art = MP4Cover(f.read(), imageformat=cover_format)
        video['covr'] = [bytes(art)]

        video.save()

    def get_next_rip_name(self):
        """ Get next song in selected list and convert to UTF-8.
            Set the song name, OS song name and full OS path song name
        """
        self.os_song_name = None
        #self.track_song_title = ""  # Aug 16/23 - no longer used
        i = 0  # To make pycharm charming :)
        for i, track_id in enumerate(self.cd_tree.get_children(
                self.selected_medium)):
            if i < self.rip_current_track:
                continue  # Skip ahead to next track to rip
            tags = self.cd_tree.item(track_id, 'tags')
            if 'checked' in tags:  # Was this song selected?
                self.get_track_from_tree(track_id)  # Grab values from treeview
                tree_song_title = \
                    self.build_out_name(self.track_no, self.track_meta_title)
                self.os_song_name = self.os_song_format(tree_song_title)
                self.song_seconds = tmf.get_sec(self.track_duration)
                break

        if self.os_song_name is None:
            self.rip_current_track = self.disc.last_track + 1
            return False  # No more songs

        ''' July 18, 2023 Support compilations. Could check " | Type:" flag too! 
            rel_type = d['release-group']['type']

            formatted = 'Score: ' + str(match_score) + '%' + sep + \
                        'Artist: ' + d['artist-credit'][0]['artist']['name'] \
                        + sep + 'Title: ' + d['title'] + sep + "Type: " + rel_type
        '''
        self.selected_compilation = "1" if self.selected_album_artist == "Various Artists" else "0"
        if self.selected_compilation == "1":
            artist_dir = u"Compilations"
        else:
            artist_dir = self.selected_album_artist

        # Does target directory exist?
        ''' June 3, 2023 Create legal names - Replace '/', '?', ':' with '_' '''
        part = ext.legalize_dir_name(artist_dir.encode("utf8")) + os.sep + \
            ext.legalize_dir_name(self.selected_album_name.encode("utf8")) + os.sep
        prefix = self.topdir.encode("utf8") + os.sep + part

        ''' Problems with os.path.join'''
        #print("OLD prefix:", prefix, type(prefix))
        #legal_artist_dir = ext.legalize_dir_name(toolkit.uni_str(artist_dir))
        #legal_album_name = ext.legalize_dir_name(toolkit.uni_str(self.selected_album_name))
        #part = ext.join(legal_artist_dir, legal_album_name)  # Inserts leading /
        #prefix = ext.join(self.topdir, part)  # Topdir already legalized
        #print("self.topdir:", self.topdir, type(self.topdir))
        #print("part:", part, type(part))
        #print("joined prefix:", prefix, type(prefix))
        if not os.path.isdir(prefix):
            try:
                os.makedirs(prefix)
                self.info.cast("Created directory: " + prefix)
            except:
                title = "Error creating directory."
                return self.abort_no_dir(title, prefix)  # Always false
        elif os.path.isfile(prefix):
            title = "Directory path already exists as a filename."
            return self.abort_no_dir(title, prefix)  # Always false

        # topdir/artist/album/99 song.ext - self.os_song_name already legal
        legal_song_name = ext.legalize_song_name(self.os_song_name)
        #self.os_full_path = prefix + self.os_song_name
        self.os_full_path = ext.join(prefix, legal_song_name)
        self.os_full_path = toolkit.uni_str(self.os_full_path)
        #self.sqlOsFileName = part + self.os_song_name  # SQL music key
        #self.sqlOsFileName = ext.join(part, legal_song_name)  # Adds leading /
        self.sqlOsFileName = part + os.sep + legal_song_name
        self.sqlOsFileName = toolkit.uni_str(self.sqlOsFileName)
        #print("self.sqlOsFileName:", self.sqlOsFileName, type(self.sqlOsFileName))
        ''' TODO: Advise when legalized name different than original name '''
        self.rip_current_track = i + 1
        return True

    def abort_no_dir(self, title, prefix):
        """ Can't create directory """
        text = "Could not create directory path:\n\t"
        text += prefix
        message.ShowInfo(self.cd_top, title, text, icon='error',
                         align='left', thread=self.update_display)
        self.rip_current_track = self.disc.last_track + 1  # Force exit
        self.info.cast(title + "\n\n" + text, 'error')
        return False  # return False just to save caller 1 line of code

    def update_rip_status(self):
        """ Update songs done, songs todo, song in progress using
            pattern_highlight """
        if self.skip_once:
            # Refresh every .2 seconds instead of every .1 second.
            self.skip_once = False
            return
        else:
            self.skip_once = True

        if self.last_shade is not None:
            # Remove last shade before applying next shade
            self.scrollbox.unhighlight_pattern(self.os_song_name,
                                               str(self.last_shade))
            self.curr_shade = self.last_shade + 1
            if self.curr_shade == 10:
                self.curr_shade = 0
        else:
            self.curr_shade = 0  # First time updating rip status

        self.scrollbox.highlight_pattern(self.os_song_name,
                                         str(self.curr_shade))
        self.last_shade = self.curr_shade

    # ============================================================================
    #
    #   Rip_CD class: populate_cd_tree - Takes a second to run
    #
    # ============================================================================

    def parse_medium(self, d):
        """ Parse:   'medium-list': [{'disc-count': 1, """
        # noinspection SpellCheckingInspection
        '''
                 'medium-count': 1,
                 'medium-list': [{},
                                 {'disc-count': 2,
                                  'disc-list': [],
                                  'format': 'CD',
                                  'track-count': 10,
                                  'track-list': []}],

  'medium-list': [{'disc-count': 1,
                   'disc-list': [{'id': 'kCLR_YoMATVISdL_AtoVY8AX.ks-',
                                  'sectors': '343743'}],
                   'format': 'CD',
                   'position': '1',
                   'track-count': 19,
                   'track-list': [{'id': '79ca6008-0ea9-3589-b6c7-4cf4c8558e38',
                                   'length': '229000',
                                   'number': '1',
                                   'position': '1',
                                   'recording': {'id': 'fcddfe79-501e-43a0-9980-694a4e4c4f0f',
                                                 'length': '229000',
                                                 'title': 'Razzmatazz'},
                            "artist-credit-phrase": "Clarence Clemons & Jackson Browne",
                            "first-date": "1996",
                            "id": "8b7bf5b2-3566-4eaf-9c5e-54f75dbf9886",
                            "length": "290840",
                            "title": "You\u2019re a Friend of Mine"

....
                  {'disc-count': 1,
                   'disc-list': [{'id': '3PIFUhCvw37NzxaTVkKAjXi0u_k-',
                                  'sectors': '355605'}],
                   'format': 'CD',
                   'position': '2',
                   'track-count': 19,


        :rtype: object
        '''

        # Loop to find mdm_ndx matching self.disc.id
        # Move up to top and do before assigning album name to append [Disc #1 of 2]
        disc_found = False
        disc_count = 0
        this_disc_number = 0
        # print("self.mbz_release_id:", self.mbz_release_id)
        # i = 0
        # print('searching for DiscID:', self.mbz_release_id)
        for i, disc in enumerate(d['medium-list']):
            # print('disc ==============================================')
            # pprint(disc)
            if 'disc-list' not in disc:
                continue

            disc_count += 1
            '''
FIRST RELEASE don't want - TWO DIFFERENT TITLES !:
            "artist-credit": [
                {
                    "artist": {
                        "disambiguation": "add compilations to this artist",
                        "id": "89ad4ac3-39f7-470e-963a-56509c546377",
                        "name": "Various Artists",
                        "sort-name": "Various Artists",
                        "type": "Other"
                    }
                }
            ],
            "artist-credit-phrase": "Various Artists",
            "first-release-date": "2001",
            "id": "228b5789-024b-4a64-b497-cf4957930a0c",
            "primary-type": "Album",
            "secondary-type-list": [
                "Compilation"
            ],
            "title": "Greatest Hits of the 80\u2019s",
            "type": "Compilation"
        },
        "status": "Official",
        "text-representation": {
            "language": "eng",
            "script": "Latn"
        },
        "title": "Greatest Hits of the Eighties, Volume 1"

SECOND RELEASE wanted MATCHING TITLES !:
            "title": "Greatest Hits of the 80\u2019s",
            "type": "Compilation"
        },
        "status": "Official",
        "text-representation": {
            "language": "eng",
            "script": "Latn"
        },
        "title": "Greatest Hits of the 80\u2019s"
    }
]

if r['title'] != r['release-group']['title']            
            '''
            # disc_list = disc['disc-list']
            # print('index i:', i, 'disc_list:', disc_list)
            disc_id = str(d['medium-list'][i]['disc-list'][0]['id'])
            # print("disc-list:", d['medium-list'][i]['disc-list'])
            for disc_id in d['medium-list'][i]['disc-list']:
                if disc_id['id'] == self.mbz_release_id:
                    disc_found = True
                    this_disc_number = int(d['medium-list'][i]['position'])
                    # this_disc_number = d['medium-list'][i]['disc-count']

        if disc_count > 1:
            d['title'] = d['title'] + " [Disc #" + str(this_disc_number) + \
                         " of " + str(disc_count) + "]"

        return disc_found, this_disc_number, disc_count

    def populate_cd_tree(self):
        """ Paint the release selection treeview """

        sep = "  |  "  # Note length of separator = 5 below

        for ndx, d in enumerate(self.release_list):
            # print('\nRelease ndx:', ndx, d['title'])
            ''' Parent line with score, artist and album '''
            ''' July 17, 2023 skip false positive - mbz_get1 now does this test '''
            if d['title'] != d['release-group']['title']:
                # In the first release group
                # d['title'] = "Greatest Hits of the Eighties, Volume 1"
                # d['release-group']['title'] = "Greatest Hits of the 80's"
                # We are looking for "Greatest Hits of the 80's" Disc #3 but
                # that is in the second release_list dictionary
                text = "Skipping Release: " + d['title']
                text += "\nRelease Group: " + d['release-group']['title']
                self.info.cast(text)
                continue

            # Parse medium to get exact disc from multi-disc set.
            disc_found, self.this_disc_number, self.disc_count = \
                self.parse_medium(d)
            self.DiscNumber = \
                str(self.this_disc_number) + "/" + str(self.disc_count)
            self.DiscNumber = toolkit.uni_str(self.DiscNumber)  # for Mutagen
            self.selected_disc_number = self.DiscNumber  # quick fix

            # Filter and Meatloaf have no matching scores (only one hit)
            if d.get('ext:score'):
                # Jim Steinem can have 10 hits, each with a weighted score
                # They fixed it after couple of months so Disc ID is found.
                match_score = int(d['ext:score'])
            else:
                match_score = 100

            rel_type = d['release-group']['type']

            formatted = 'Score: ' + str(match_score) + '%' + sep + \
                        'Artist: ' + d['artist-credit'][0]['artist']['name'] \
                        + sep + 'Title: ' + d['title'] + sep + "Type: " + rel_type

            # TODO: Can't seem to set opened state to closed???
            if match_score == 100:
                tags = ("rel_id", "tag100", "unchecked")
                opened = True
            elif match_score > 89:
                tags = ("rel_id", "tag90", "unchecked")
                opened = True
            else:
                tags = ("rel_id", "tag_low", "unchecked")
                opened = False
            rel_id = self.cd_tree.insert("", "end", text=formatted,
                                         tags=tags, open=opened)

            ''' Our second parent line with Musicbrainz ID '''
            formatted = 'Id: ' + d['id'] + sep + 'Barcode: ' + d.get('barcode', '')
            if match_score == 100:
                opened = True
            else:
                opened = False
            mbz_id = self.cd_tree.insert(rel_id, "end", text=formatted,
                                         tags=("mbz_id", "unchecked"), open=opened)

            # If no release date, create an entry for user to select.
            if 'release-event-list' not in d:
                d['release-event-list'][0]['date'] = "????"  # Denotes added here

            formatted = "Album date: " + d['release-event-list'][0]['date']
            # Aug 2023 - Drop Country and use Compilation instead
            # +sep+ 'Country: ' + d['release-event-list'][0]['area']['name']
            self.cd_tree.insert(
                mbz_id, "end", text=formatted, tags=("date_id", "unchecked"))

            if 'label-info-list' in d:
                # Sometimes [1] has catalog-number key and not [0]
                for label in d['label-info-list']:
                    if 'label' in label:
                        label_str = label['label']['name']
                    else:
                        label_str = ""
                    if 'catalog-number' in label:
                        formatted = "Catalog number: " + \
                                    label['catalog-number'] + sep + 'Label: ' + label_str
                        self.cd_tree.insert(
                            mbz_id, "end", text=formatted,
                            tags=("label_id", "unchecked"))

            if disc_found:
                mdm_ndx = self.this_disc_number - 1
            else:
                # For Filter mdn_ndx = 0. For Jim Steinem mdm_ndx = 1
                # Jim Steinem never had CD listing though, until months later
                mdm_ndx = len(d['medium-list']) - 1

            found_id = d['medium-list'][mdm_ndx]['disc-list'][0]['id']
            for disc_id in d['medium-list'][mdm_ndx]['disc-list']:
                if disc_id['id'] == self.mbz_release_id:
                    found_id = disc_id['id']

            formatted = ""  # Our formatted line for tree view
            if 'medium-count' in d:
                formatted = formatted + "Medium count: " + \
                            str(d['medium-count']) + sep
            if 'format' in d['medium-list'][mdm_ndx]:  # EG CD or Vinyl
                formatted = formatted + "Medium format: " + \
                            d['medium-list'][mdm_ndx]['format'] + sep
            if 'position' in d['medium-list'][mdm_ndx]:  # Really the CD disk #
                formatted = formatted + "Disc number: " + \
                            str(d['medium-list'][mdm_ndx]['position']) + sep
            if 'disc-list' in d['medium-list'][mdm_ndx]:
                formatted = formatted + "Disc ID: " + \
                            str(found_id) + sep

            formatted = formatted[:-len(sep)]
            medium_id = self.cd_tree.insert(
                rel_id, "end", text=formatted,
                tags=("medium_id", "unchecked"), open=opened)

            ''' Loop through all tracks in medium list '''
            tracks_list = d['medium-list'][mdm_ndx]['track-list']
            for i, track_d in enumerate(tracks_list):
                recording_d = track_d['recording']
                song = track_d['recording']['title']  # Becomes out_name
                first_date = track_d['recording']['first-date'][:4]  # Year only

                song_artist = track_d['recording']['artist-credit-phrase']
                length = recording_d.get('length', '0')  # length in milliseconds
                duration = int(length) / 1000
                hhmmss = tmf.mm_ss(duration, rem=None)

                self.track_meta_title = toolkit.uni_str(song)
                self.track_artist = toolkit.uni_str(song_artist)
                self.track_first_date = toolkit.uni_str(first_date)
                self.track_composer = u""  # This + artist & comment in out_name2
                self.track_comment = u""  # This + composer & artist in out_name2
                self.track_duration = toolkit.uni_str(hhmmss)
                self.track_no = i + 1
                tree_song_title = \
                    self.build_out_name(self.track_no, self.track_meta_title)

                out_name2 = self.build_out_name2(  # Append: | Artist | Composer
                    tree_song_title, self.track_artist, self.track_composer)

                self.cd_tree.insert(
                    medium_id, "end", text=out_name2, tags=("track_id", "unchecked"),
                    values=(self.track_meta_title, self.track_artist, 
                            self.track_first_date, self.track_composer,
                            self.track_comment, self.track_duration, self.track_no))

            self.update_display()  # Give some time to lib_top()

            ''' Our third parent line has online cover art '''
            if not d['id'] in self.image_dict:
                continue
            entry = self.image_dict[d['id']]

            # print("\n\n=================== entry: ======================\n")
            first_time = True
            try:
                # Insert Image detail lines into CD treeview
                image_list = entry['images']
                self.cd_tree_insert_image(rel_id, d['id'], opened, image_list,
                                          first_time)
                # first_time = False
            except Exception as err:
                print(err)
                continue  # Remove this line to see following error:
                # No JSON object could be decoded
                # print(entry)   # Can't do, image-data too large for screen

            self.update_display()  # Give some time to lib_top()

        return

    # noinspection SpellCheckingInspection
    """
        PSEUDO PRETTY PRINT:
        
{u'comment': u'',
 u'thumbnails': {
        u'large': u'http://coverartarchive.org/release/0b69663c-ca24-420f-b7a2-38d314cf6e62/21173090370-500.jpg', 
        u'large-data': u'\x1ah\xfe\xea\xb3\x01\xbb', 
        u'small': u'http://coverartarchive.org/release/0b69663c-ca24-420f-b7a2-38d314cf6e62/21173090370-250.jpg', 
        u'small-data': u'\x1ah\xfe\xea\xb3\x01\xbb', 
        u'250': u'http://coverartarchive.org/release/0b69663c-ca24-420f-b7a2-38d314cf6e62/21173090370-250.jpg', 
        u'1200': u'http://coverartarchive.org/release/0b69663c-ca24-420f-b7a2-38d314cf6e62/21173090370-1200.jpg', 
        u'500': u'http://coverartarchive.org/release/0b69663c-ca24-420f-b7a2-38d314cf6e62/21173090370-500.jpg'},
 u'edit': 56629703, 
 u'image': u'http://coverartarchive.org/release/0b69663c-ca24-420f-b7a2-38d314cf6e62/21173090370.jpg', 
 u'image-data': u'\x1ah\xfe\xea\xb3\x01\xbb', 
 u'back': False, 
 u'id': 21173090370, 
 u'front': False, 
 u'approved': True, 
 u'types': [u'Other']}

    """


    # inspection SpellCheckingInspection
    def build_out_name(self, track, song):
        """ Add 'DISC-TRACK - ' prefix accordingly but no extension
        :param track: Integer track number
        :param song: "Song Name" no prefix and no suffix
        :returns out_name: Optional Artist Name, composer and comment appended
        """
        if self.naming == "99 ":  # Doesn't work, default is "99- "
            track_name_fmt = "{:02} {}"  # format: '01 song name'
        else:  # self.naming == "99 - "
            track_name_fmt = "{:02} - {}"  # format: '01 - song name'
        out_name = track_name_fmt.format(int(track), song)
        if self.disc_count > 1:  # '01 song name' -> '2-01 song name'
            out_name = str(self.this_disc_number) + "-" + out_name
        return out_name

    def build_out_name2(self, out_name, art, comp):
        """ Add ' | artist: Artist Name ' and ' | composer: Composer Name'
            to treeview detail line. Repeatedly called as Artist Name,
            Composer Name and Comment are changed.
        :param out_name: "D-99 Song Name"
        :param art: song_artist
        :param comp: song_composer
        :returns out_name2: Optional Artist Name and Composer appended
        """
        out_name2 = out_name
        artist = art if len(art) <= 15 else art[:12] + "..."  # Max 20 chars
        composer = comp if len(comp) <= 15 else comp[:12] + "..."  # Max 20 chars
        if art != self.selected_album_artist:  # Highlight track diff from album
            out_name2 += "  | artist: " + artist
        if comp != self.selected_composer:  # Highlight track diff from album
            out_name2 += "  | composer: " + composer
        return out_name2

    def cd_tree_insert_image(self, rel_id, mbz_id, opened, image_list, first_time):
        """ Insert artwork lines into CD Treeview
            TODO: Set reasonable limit of 2 MB for images added to songs.
                  Over 2 MB put into Album directory as real time image
                  when song is played.
            NOTE: Original design was to be reentrant with first_time and
                  self.our_parent variables. But not used for now....
        """
        if first_time:
            # First time we insert collapsable/expandable parent line
            self.our_parent = self.cd_tree.insert(
                rel_id, "end", tags=("images_id", "unchecked"), open=opened,
                text="Artwork from: http://coverartarchive.org/release/" + mbz_id)

        for d in image_list:
            # There are only dictionaries at list index 0
            if 'thumbnails' in d:
                if 'small' in d['thumbnails']:
                    # TODO: When size is 14 no file was downloaded
                    # size = str(len(d['thumbnails']['small-data']))
                    size = "{:,}".format(len(d['thumbnails']['small-data']))
                    self.cd_tree.insert(self.our_parent, "end", values=size,
                                        text=d['thumbnails']['small'],
                                        tags=("image_id", "unchecked"))
                if 'large' in d['thumbnails']:
                    # size = str(len(d['thumbnails']['large-data']))
                    size = "{:,}".format(len(d['thumbnails']['large-data']))
                    self.cd_tree.insert(self.our_parent, "end", values=size,
                                        text=d['thumbnails']['large'],
                                        tags=("image_id", "unchecked"))
            if 'image' in d:
                size = "{:,}".format(len(d['image-data']))
                self.cd_tree.insert(self.our_parent, "end", values=size,
                                    text=d['image'], 
                                    tags=("image_id", "unchecked"))

    def cd_close(self):
        """ Wrapup """
        global RIP_CD_IS_ACTIVE
        RIP_CD_IS_ACTIVE = False
        if self.active_pid > 0:
            os.popen('kill -9 ' + str(self.active_pid))
            self.active_pid = 0
        # Delete any lurking pickle
        ext.remove_existing(IPC_PICKLE_FNAME)

        # Clean up tooltips under cd_top widget prefix.
        self.tt.close(self.cd_top)
        # Last known window position for encoding, saved to SQL
        last_geom = monitor.get_window_geom_string(
            self.cd_top, leave_visible=False)
        monitor.save_window_geom('encoding', last_geom)

        self.cd_top.destroy()
        self.cd_top = None

    # ==============================================================================
    #
    #       RipCD class - Get image from clipboard and other image functions
    #
    # ==============================================================================

    def image_from_clipboard(self):
        """ Doesn't work. Use xclip instead
        try:
            # image grab works for Windows and OSX only :(
            from PIL import ImageGrab
            im= ImageGrab.grab clipboard()
        except:
            clipboard = gtk.clipboard_get()
            im= clipboard.wait_for_image()
        if isinstance(im, Image.Image):
            print('clipboard contains image')
        else:
            print('clipboard does not contain image')
        """
        # Cannot insert until cd_tree has children
        children = self.cd_tree.get_children()
        if len(children) == 0:
            #messagebox.showinfo(
            #    "Paste from clipboard error.",
            #    "Cannot paste image until Musicbrainz listing obtained.",
            #    icon='warning', parent=self.cd_top)
            message.ShowInfo(self.cd_top, "Paste from clipboard error.",
                             "Cannot paste image until Musicbrainz listing obtained.",
                             icon='warning', thread=self.update_display)
            return

        # $ xclip -selection clipboard -target image/png -out > out.png
        # Feb 26 2021 = Remove unneeded filename and command string NOT TESTED YET
        #        filename = "/tmp/mserve.image" + str(self.image_from_clipboard_count)
        command_line_list = ["xclip", "-selection", "clipboard", "-target",
                             "image/png", "-out"]
        #                             "image/png", "-out", ">" ]
        #        command_line_list.append(filename)
        # xclip -selection clipboard -target image/png -out > image.png
        #        command_str = " ".join(command_line_list)   # list to printable string
        # self.cmp_msg box.update(command_str)         # Display status line

        # Conventional Method
        pipe = sp.Popen(command_line_list, stdout=sp.PIPE, stderr=sp.PIPE)
        text, err = pipe.communicate()  # This performs .wait() too

        # From: https://stackoverflow.com/a/64512790/6929343
        # suppress stdout and stderr so messages appear on screen
        # pipe = sp.P open(command_line_list)
        # pipe.communicate()              # This performs .wait() too
        # err = None
        # text = None

        # From: https://stackoverflow.com/a/64512435/6929343
        # Write print output to file.
        # pipe = sp.P open(command_line_list,
        #                stdout=open('/tmp/mbz_results.txt', 'w'), \
        #                stderr=sp.PIPE)
        # text, err = pipe.communicate()              # This performs .wait() too

        if err:
            if "Error: target image/png not available" in err:
                #messagebox.showinfo(
                #    "Paste from clipboard error.",
                #    "You must copy an image to the clipboard first.",
                #    icon='error', parent=self.cd_top)
                message.ShowInfo(self.cd_top, "Paste from clipboard error.",
                                 "You must copy an image to the clipboard first.",
                                 icon='error', thread=self.update_display)
            else:
                #messagebox.showinfo(
                #    "Paste from clipboard error.",
                #    err, icon='error', parent=self.cd_top)
                message.ShowInfo(self.cd_top, "Paste from clipboard error.", err,
                                 icon='error', thread=self.update_display)
            return

        if not pipe.returncode == 0:
            #messagebox.showinfo(
            #    "Paste from clipboard error.",
            #    "An error occurred trying to grab image from clipboard.",
            #    icon='error', parent=self.cd_top)
            message.ShowInfo(self.cd_top, "Paste from clipboard error.",
                             "An error occurred reading from clipboard.",
                             icon='error', thread=self.update_display)
            return

        if text:
            # Image is going direct to stdout instead of filename passed?
            self.image_data_to_frame(text)
        else:
            #messagebox.showinfo("Paste from clipboard error.",
            #                    "Image should have been in clipboard but not found?",
            #                    icon='error', parent=self.cd_top)
            message.ShowInfo(self.cd_top, "Paste from clipboard error.",
                             "Image should have been in clipboard but not found?",
                             icon='error', thread=self.update_display)
            return

        ''' Insert image name in tree '''
        if self.image_from_clipboard_count == 0:
            rel_ids = self.cd_tree.get_children()
            rel_id = rel_ids[0]  # Put under first release
            # First time we insert collapsable/expandable parent line
            self.clip_parent = self.cd_tree.insert(
                rel_id, "end", text="Cover Art from clipboard",
                tags=("clips_id", "unchecked"), open=True)

        self.clipboard_images.append(text)  # Add our image next in list
        self.image_from_clipboard_count += 1

        size = str(len(text))
        self.cd_tree.insert(
            self.clip_parent, "end", values=(size,), tags=("image_id", "unchecked"),
            text="Clipboard Image " + str(self.image_from_clipboard_count))

    # ==============================================================================
    #
    #       RipCD class - Select songs and art in CD treeview
    #
    # ==============================================================================

    def button_1_click(self, event):
        """ Call CheckboxTreeview to manage "checked" and "unchecked" tags.
            When it finishes validate what was just checked or unchecked and
            reverse if validation fails.
        """

        # Mimic CheckboxTreeview self._box_click() code
        x, y, widget = event.x, event.y, event.widget
        elem = widget.identify("element", x, y)
        if "image" not in elem:
            return  # Image was not clicked

        # get item id (iid) matching checkbox that was just clicked
        item = self.cd_tree.identify_row(y)

        """ Warning if status is tri-state, all will be selected. """
        # Call CheckboxTreeview function first to let it flag item(s).
        if self.cd_tree.tag_has("tristate", item):
            answer = message.AskQuestion(
                self.cd_top, "Discard unique selections.",
                "All items will be selected and unique selections lost.", 
                confirm='yes', icon='warning', thread=self.update_display)
            if answer.result != 'yes':
                return

        """ Check or uncheck box when clicked. """
        # Call CheckboxTreeview function first to let it flag item(s).
        self.cd_tree._box_click(event)

        # Execute our pseudo-callback functions
        self.reverse_checkbox = False
        if self.cd_tree.tag_has("unchecked", item):
            self.process_unchecked(item)
            if self.reverse_checkbox:
                # Call CheckboxTreeview functions to reverse uncheck
                self.cd_tree._check_ancestor(item)
                self.cd_tree._check_descendant(item)
        elif self.cd_tree.tag_has("checked", item):
            self.process_checked(item)
            if self.reverse_checkbox:
                # Call CheckboxTreeview functions to reverse checked
                self.cd_tree._uncheck_ancestor(item)
                self.cd_tree._uncheck_descendant(item)
        else:
            # No need to test tristate, item must be checked or unchecked.
            print("button_1_click() ERROR: No 'checked' or 'unchecked' tag.",
                  self.cd_tree.item(item, 'tags'))
            return

    def process_unchecked(self, item):
        """ We just unchecked the item, use self.unselect on tag
        """

        tags = self.cd_tree.item(item)['tags']

        if 'medium_id' in tags:
            # Do individual parent tag test before group test
            self.unselect_medium(item)
        elif 'image_id' in tags:
            # We are an image ID so display artwork
            self.unselect_image(item)
        elif 'track_id' in tags:
            # We are on a song ID, turn it off or on if under selected medium_id
            self.unselect_song(item)
        elif 'date_id' in tags:
            # We unchecked release date underneath mbz_id parent
            self.unselect_date()
        elif 'mbz_id' in tags:
            # We unchecked Musicbrainz ID propagate to children
            for child in self.cd_tree.get_children(item):
                # TODO: why isn't if tests working???
                # if self.cd_tree.tag_has("checked", child):
                # if 'checked' in self.cd_tree.item(child)['tags']:
                self.process_unchecked(child)
        elif 'clips_id' in tags or 'images_id' in tags:
            # We unchecked All Clipboard Images or Covert Art Archive Images
            for child in self.cd_tree.get_children(item):
                self.unselect_image(child)
        elif 'rel_id' in tags:
            # We are an release ID propagate to children
            for child in self.cd_tree.get_children(item):
                # Parent maybe tristate so can't test just "checked"
                self.process_unchecked(child)
        elif 'label_id' in tags:
            pass  # Nothing to do for these Item tags
        else:
            # Undefined.
            print('Programmer ERROR. Unknown Id, Tags:', item, tags)

        self.show_selections()

    def process_checked(self, item):
        """ An item was checked, set self.selected_X tag
        """

        tags = self.cd_tree.item(item)['tags']

        if 'medium_id' in tags:
            # Do individual parent tag test before group test

            self.select_medium(item)
            # If another medium is selected we get error and skip song tagging
            if not self.reverse_checkbox:
                child = item  # Give a default when no children
                for child in self.cd_tree.get_children(item):
                    self.select_song(child)
                self.ensure_visible(child)
        elif 'image_id' in tags:
            # We are an image ID so display artwork
            self.select_image(item)
        elif 'track_id' in tags:
            # We are on a song ID, turn it off or on if under selected medium_id
            self.select_song(item)
            # self.select_medium(item)
        elif 'date_id' in tags:
            # We are a release date so use it and unselect any previous one.
            self.select_date(item)
        elif 'mbz_id' in tags:
            # We checked Musicbrainz ID propagate to children like release date
            for child in self.cd_tree.get_children(item):
                self.process_checked(child)
        elif 'clips_id' in tags or 'images_id' in tags:
            # We checked All Clipboard Images or Covert Art Archive Images
            for child in self.cd_tree.get_children(item):
                self.select_image(child)
        elif 'rel_id' in tags:
            # We are an release ID propagate to children
            for child in self.cd_tree.get_children(item):
                # Parent maybe tristate so can't test just "unchecked"
                self.process_checked(child)
        elif 'label_id' in tags:
            pass  # Nothing to do for these Item tags
        else:
            # Undefined.
            print('Programmer ERROR. Unknown Id, Tags:', item, tags)

        self.show_selections()

    def ensure_visible(self, Id):
        """ Ensure treeview item is visible in listbox """
        opened = self.cd_tree.item(Id, 'open')
        if opened is not True:
            self.cd_tree.item(Id, open=True)
        # Get children and ensure last child is visible
        last_child = Id  # Should always have children but got error
        for child in self.cd_tree.get_children(Id):
            last_child = child
            ''' 
                TODO:
                    When rel_id "checked" mbz_id and ImagesId should expand.
            '''
        self.cd_tree.see(last_child)

    def display_item_details(self, Id):
        """ NOT USED
            Display song or art info. """

        # duration = self.cd_tree.item(Id, 'values')[0]  
        # 'values'[0] causes error on Release date: under "mbz_id"
        duration = self.cd_tree.set(Id, '#1')
        if duration == "":
            return  # No values, then no image

        tags = self.cd_tree.item(Id)['tags']
        if 'image_id' in tags:
            if int(duration) > 1000:
                # Anything less than 1,000 isn't an image
                # print('Displaying new image')
                ext.t_init('Display image')
                self.current_image_key = self.display_image(Id)
                ext.t_end('print')

    def display_image(self, Id, select=False):
        """ Display image and return tuple of image key fields
            TODO: Set reasonable limit of 2 MB for images added to songs.
                  Over 2 MB put into Album directory as real time image
                  when song is played. """
        # Get our image entry
        image_name = self.cd_tree.item(Id, 'text')
        image_size = self.cd_tree.item(Id, 'values')[0]
        int_size = image_size.replace(",", "")  # American integer display
        int_size = int(int_size.replace('.', ''))  # European integer display
        ''' TODO: Make 2 MB a global variable. Option to put image in dir. '''
        if select and int_size > 2 * 1000 * 1000:  # If selecting image
            title = "Image file over 2 MB (" + image_size + ")"
            text = "You probably don't want to include this image:\n\n"
            text += image_name
            message.ShowInfo(self.cd_top, title, text, thread=self.update_display)
            #print(title + "\n\n" + text)
        clip_test = image_name.split(' ', 1)[0]
        if clip_test == "Clipboard":
            image_key = self.extract_image_from_clip(Id)
        else:
            image_key = self.extract_image_from_dict(Id)

        return image_key  # Will be None if an error

    def extract_image_from_dict(self, Id):
        """ Key is 4 or 5 segments long comprised of dictionary keys

            TODO: Set reasonable limit of 2 MB for images added to songs.
                  Over 2 MB put into Album directory as real time image
                  when song is played. """

        image_name = self.cd_tree.item(Id, 'text')
        medium_id = self.cd_tree.parent(Id)
        rel_id = self.cd_tree.parent(medium_id)
        release_id = self.get_mbz_id_for_rel_id(rel_id)  # embedded release_id

        image_data = None
        image_key = None
        i = 0  # For pycharm unassigned warning
        # looping over large images costs .01 second for each image dictionary
        for i, d in enumerate(self.image_dict[release_id]['images']):
            # There are only dictionaries at list index 0
            if 'thumbnails' in d:
                if 'small' in d['thumbnails']:
                    # print('Searching:',d['thumbnails']['small'])
                    if d['thumbnails']['small'] == image_name:
                        image_data = d['thumbnails']['small-data']
                        image_key = \
                            (release_id, 'images', i, 'thumbnails', 'small-data')
                if 'large' in d['thumbnails']:
                    if d['thumbnails']['large'] == image_name:
                        image_data = d['thumbnails']['large-data']
                        image_key = \
                            (release_id, 'images', i, 'thumbnails', 'large-data')
            if 'image' in d:
                if d['image'] == image_name:
                    image_data = d['image-data']
                    image_key = (release_id, 'images', i, 'image-data')

            if image_data is not None:
                break

        if image_data is None:
            print('display_image() ERROR: Could not get image_data. i=', i)
            return None

        self.image_data_to_frame(image_data)
        return image_key

    def extract_image_from_clip(self, Id):
        """ Our key is only 1 segment long, containing image list index """
        text = self.cd_tree.item(Id)['text']
        clip_no = text.rsplit(' ', 1)[-1]
        clip_ndx = int(clip_no) - 1
        clipboard_data = self.clipboard_images[clip_ndx]
        self.image_data_to_frame(clipboard_data)
        return clip_ndx,  # Return tuple with one key segment

    def image_data_to_frame(self, image_data):
        """ Must wrap bytes in file io:
            https://pillow.readthedocs.io/en/5.1.x/reference/Image.html """
        t_file = io.BytesIO(image_data)
        self.original_art = Image.open(t_file)
        del t_file  # Delete object to save memory
        self.resized_art = self.original_art.resize(
            (self.art_width, self.art_height), Image.ANTIALIAS)
        self.cd_song_art = ImageTk.PhotoImage(self.resized_art)
        self.cd_art_label.configure(image=self.cd_song_art)
        self.background = self.resized_art.getpixel((3, 3))  # For spinning 
        # TODO: Apply colors to all labels and buttons
        ''' From mserve:

        # Get background color of x=3, y=3 for filling corners when rotating
        # which "squares the circle".
        self.play_frm_bg = self.play_resized_art.get pixel((3,3))
        hex_background = img.rgb_to_hex(self.play_frm_bg)
        dec_foreground = img.contrasting_rgb_color(self.play_frm_bg)
        hex_foreground = img.rgb_to_hex(dec_foreground)
        self.play_frm.configure(bg=hex_background)
        # Apply color codes to all labels and buttons

        toolkit.config_all_labels(self.play_top, fg=hex_foreground, \
                                  bg=hex_background)
        self.play_btn.configure(bg=hex_background)
        toolkit.config_all_buttons(self.play_top, fg=hex_background, \
                                  bg=hex_foreground)
        self.play_top.update_idletasks() '''

    def get_mbz_id_for_rel_id(self, rel_id):
        """ Get Musicbrainz ID from first child under rel_id tag """
        for child in self.cd_tree.get_children(rel_id):
            child_tags = self.cd_tree.item(child)['tags']
            if 'mbz_id' in child_tags:
                # Get 'Id: xxx  |  Barcode: 9999999
                line = self.cd_tree.item(child, 'text')
                release_id = line.split(' ', 2)[1]
                # print('release_id:',release_id)
                return release_id

        print('get_mbz_id_for_rel_id() ERROR: mbz release_id not found:', rel_id)
        return None

    def select_image(self, Id):
        """ Select image. We can be called when image already selected. """
        self.current_image_key = self.display_image(Id, select=True)
        if self.current_image_key in self.selected_image_keys:
            return  # Already in key list, can't remove

        self.selected_image_keys.append(self.current_image_key)

    def unselect_image(self, Id):
        """ Unselect image. We can be called when image already unselected. """
        self.current_image_key = self.display_image(Id, select=False)
        if self.current_image_key not in self.selected_image_keys:
            return  # Not in key list, can't remove

        self.selected_image_keys.remove(self.current_image_key)

        if len(self.selected_image_keys) == 0:
            '''' No images. Set default image to self.art_label'''
            self.make_default_art()
            self.cd_art_label.configure(image=self.cd_song_art)
            self.cd_top.update_idletasks()
        else:
            '''' Assign first available image to self.art_label'''
            image_key = self.selected_image_keys[0]
            self.image_data = self.get_image_by_key(image_key)
            self.image_data_to_frame(self.image_data)
            pass

    def select_date(self, Id):
        """ Select release date.
            1. The release date for mbz_id is automatically initialized
               and can't be changed. It can only be excluded leaving no date.
            2. Release date should be YYYY or YYYY-MM.
            3. MBZ uses the recording date as release date.
            4. Option required to override release date and enter a new
               field for recording date.
            5. Another option required for Compilation flag and Artist Name.
            6. simpledialog.askstring() is blocking function.
               message.AskString should be used instead.
        """

        if self.selected_album_date:
            # TODO: Prompt for release date
            #messagebox.showinfo(title="Album Date already selected",
            #                    message="Unselect the other Album Date first.",
            #                    icon='error', parent=self.cd_top)
            message.ShowInfo(self.cd_top, "Album Date already selected",
                             "Unselect the other Album Date first.",
                             icon='error', thread=self.update_display)
            self.reverse_checkbox = True
            return False

        line = self.cd_tree.item(Id, 'text')
        release_date = line.split(' ', 3)[2]

        if release_date == "" or "?" in release_date:
            # When no release date it is manually inserted earlier as "????"
            # TODO: Prompt for release date testing.
            new_date = simpledialog.askstring("Album Date error",
                                              "Blank dates cannot be used. Enter a release date",
                                              parent=self.cd_top)
            if new_date is None:
                self.reverse_checkbox = True
                return False
            else:
                release_date = new_date

        self.selected_album_date = release_date

    def unselect_date(self):
        """ Unselect release date """
        self.selected_album_date = None

    def select_medium(self, Id):
        """ Select medium
            Only one medium can be selected, prompt "Do you want to unselect?"
            Flag all songs as selected, even if manually unselected previously
            When self.selected_album_artist is "Various Artists" it's a compilation
        """
        if self.selected_medium is not None:
            if not Id == self.selected_medium:
                #messagebox.showinfo(
                #    parent=self.cd_top, title="Selection Error",
                #    message="Another medium has already been selected.")
                message.ShowInfo(self.cd_top, "Selection Error",
                                 "Another medium has already been selected.",
                                 icon='error', thread=self.update_display)
                self.reverse_checkbox = True
                return False

        # We are selecting this medium and all songs under it by default
        self.selected_medium = Id
        # Line 'score: 999   |  Artist: Joe Blow  |  Title: Getting Dough'
        rel_id = self.cd_tree.parent(Id)
        sep = "  |  "  # TODO: Make this global variable
        artist_str = self.cd_tree.item(rel_id, 'text').split(sep)[1]
        album_str = self.cd_tree.item(rel_id, 'text').split(sep)[2]
        self.selected_album_artist = artist_str.split(':', 1)[1].strip()
        self.selected_compilation = "1" if self.selected_album_artist == "Various Artists" else "0"
        # Filter title was missing : 1995-2008 so add ',1' to split.
        self.selected_album_name = album_str.split(':', 1)[1].strip()

    def unselect_medium(self, Id):
        """ Unselect medium
            Must be selected to qualify
            Flag all songs as unselected
        """
        if not Id == self.selected_medium:
            #messagebox.showinfo(
            #    title="Selection Error", parent=self.cd_top,
            #    message="This medium is not selected.")
            message.ShowInfo(self.cd_top, "Selection Error",
                             "This medium is not selected.",
                             icon='error', thread=self.update_display)

            return False

        # We are unselecting this medium and all songs under it by default
        self.selected_medium = None
        self.selected_album_artist = None
        self.selected_album_name = None

    def select_song(self, Id):
        """ Select song. Programmatically set medium selection.
        """

        # Get our parent medium_id and if it is not equal to self.saved_medium_id
        # we have an error.
        parent_id = self.cd_tree.parent(Id)

        if not self.selected_medium:
            # No medium selected so use this song's parent as medium
            self.select_medium(parent_id)

        if not parent_id == self.selected_medium:
            #messagebox.showinfo(title="Selection Error",
            #                    message="Song is not under the selected medium.",
            #                    icon='error', parent=self.cd_top)
            message.ShowInfo(self.cd_top, "Selection Error",
                             "Song is not under the selected medium.",
                             icon='error', thread=self.update_display)
            self.reverse_checkbox = True
            return False

    def unselect_song(self, Id):
        """ Unselect song. Programmatically set medium selection.
        """

        # Get our parent medium_id and if it is not equal to self.saved_medium_id
        # we have an error.
        parent_id = self.cd_tree.parent(Id)
        if not parent_id == self.selected_medium:
            #messagebox.showinfo(
            #    title="Selection Error", parent=self.cd_top,
            #    message="Song is not under a selected medium.")
            message.ShowInfo(self.cd_top, "Selection Error",
                             "Song is not under the selected medium.",
                             icon='error', thread=self.update_display)
            self.reverse_checkbox = True
            return False

        # Did we just unselect last song under medium? If so unselect medium
        for track_id in self.cd_tree.get_children(parent_id):
            tags = self.cd_tree.item(track_id)['tags']
            if 'checked' in tags:
                return True  # Song we unselected wasn't last

        # We unchecked the last song so uncheck the medium parent as well
        self.unselect_medium(parent_id)

    def show_selections(self):
        """ Update our scrollable textbox with current selections 
            Called when boxes checked and drop down menu is changed.
        """
        self.fmt = self.fmt_var.get()
        self.naming = self.nam_var.get()
        # For consistency should create self.quality instance 

        # Allow program changes to displayed selections
        self.scrollbox.configure(state="normal")
        self.scrollbox.delete('1.0', tk.END)  # Delete previous entries
        x = self.fmt  # Menu bar format radiobutton
        self.scrollbox.insert("end", "Format:\t" + x)
        y = 100  # wav and flac are 100% quality
        if x == "m4a" or x == "oga":  # "oga" or "m4a" selected?
            y = self.quality_var.get()  # Menu bar quality radiobutton
        self.scrollbox.insert("end", "\tQuality: " + str(y) + " %")
        self.scrollbox.insert("end", "\tNaming: " + '"' + self.naming + '"' + "\n")
        topdir = self.trg_var.get()  # Menu bar format target
        self.scrollbox.insert("end", "Target:\t" + topdir + "\n")

        if self.selected_album_artist:  # Album Artist (may not be Song Artist)
            self.scrollbox.insert("end", "Artist:\t" +
                                  self.selected_album_artist + "\n")
        if self.selected_album_name:  # Album name
            self.scrollbox.insert("end", "Album:\t" +
                                  self.selected_album_name + "\n")

        compounded = ""
        if self.selected_album_date:  # Album Date (Not First Date)
            compounded += "Date: " + self.selected_album_date + "\t"
        if self.selected_genre:  # Genre
            compounded += "Genre: " + self.selected_genre + "\t"
        if self.selected_composer:  # Default Composer
            compounded += "Composer: " + self.selected_composer
        if compounded:
            # first field E.G. "Genre: " becomes "Genre:\t"
            compounded = compounded.replace(": ", ":\t", 1)
            self.scrollbox.insert("end", compounded + "\n")
        ''' Old format of one per line
        if self.selected_album_date:  # Album Date (Not First Date)
            self.scrollbox.insert("end", "Date:\t" +
                                  self.selected_album_date + "\n")
        if self.selected_genre:  # Genre
            self.scrollbox.insert("end", "Genre:\t" +
                                  self.selected_genre + "\n")
        if self.selected_composer:  # Default Composer
            self.scrollbox.insert("end", "Composer:\t" +
                                  self.selected_composer + "\n")
        '''
        self.selected_tracks = 0  # Number tracks selected
        if self.selected_medium:  # Was this medium selected?
            # Remove " |  Disc ID: .." from end it's added later
            # Note sep has two spaces
            sep = "  |  "
            medium = self.cd_tree.item(self.selected_medium, 'text')
            # print('medium:', medium)
            position = medium.find(sep + "Disc ID:")
            if position:
                shortened_string = medium[:position]
            else:
                shortened_string = medium
            # print('shortened_string:', shortened_string)
            self.scrollbox.insert("end", "Medium:\t" + shortened_string + "\n")
            self.scrollbox.insert("end", "Files:")
            for track_id in self.cd_tree.get_children(self.selected_medium):
                tags = self.cd_tree.item(track_id, 'tags')
                self.get_track_from_tree(track_id)  # May need to reformat all
                if 'checked' in tags:  # Was this song selected?
                    tree_song_title = \
                        self.build_out_name(self.track_no, self.track_meta_title)
                    os_name = self.os_song_format(tree_song_title)  # add ext
                    self.scrollbox.insert("end", "\t" + os_name + "\n")
                    self.selected_tracks += 1
                self.set_track_to_tree(track_id)  # In case naming changes

        self.scrollbox.insert("end", "CD Tracks:\t" +
                              str(self.disc.last_track) + "\tTracks " +
                              "selected: " + str(self.selected_tracks) + "\n")
        self.scrollbox.insert("end", "CD Musicbrainz ID:\t\t" +
                              self.mbz_release_id + "\n")

        # ext.t_init('show_selections() display images')
        self.rip_art = []  # Prevent garbage collection
        for i, image_key in enumerate(self.selected_image_keys):

            # Get image for tuple key
            image_data = self.get_image_by_key(image_key)
            if image_data is None:
                print("encoding.py show_selections() Bad image key:", image_key)
                continue

            # noinspection PyTypeChecker
            t_file = io.BytesIO(image_data)
            original_art = Image.open(t_file)
            del t_file  # Delete object to save memory
            resized_art = original_art.resize(
                (175, 175), Image.ANTIALIAS)  # Thumbnail size for selections
            self.rip_art.append(ImageTk.PhotoImage(resized_art))
            self.scrollbox.insert("end", '\nImage ' + str(i + 1) + ':\t')
            self.scrollbox.image_create("end", image=self.rip_art[i])
            self.scrollbox.insert("end", '\n')
            self.update_display()  # Give some time to lib_top
        # ext.t_end('print')

        # apply the tag "red" to following word patterns
        pattern_list = ["Format:", "Quality:", "Naming:", "Artist:", "Album:",
                        "Musicbrainz ID:", "Medium:", "Files:", "Image 1:",
                        "Image 2:", "Image 3:", "Image 4:", "Image 5", "Date:",
                        "Genre:", "Composer:", "CD Tracks:", "Tracks selected:",
                        "CD Musicbrainz ID:", "Target:", "Clipboard Image 1:",
                        "Clipboard Image 2:", "Clipboard Image 3:",
                        "Clipboard Image 4:", "Clipboard Image 5:"]

        for pattern in pattern_list:
            self.scrollbox.highlight_pattern(pattern, "red")

        # Don't allow changes to displayed selections, must be done in tree
        self.scrollbox.configure(state="disabled")
        self.cd_tree.update_idletasks()

    def get_image_by_key(self, image_key):
        """ Return image matching search key """
        seg1 = image_key[0]
        if len(image_key) == 1:  # Clipboard image?
            # Amazon picture not encoding for Surf's Up. Try cover art archive
            # and then lower resolution clipboard image.
            image_data = self.clipboard_images[seg1]
        else:
            # Images in cover art archive dictionary
            seg2 = image_key[1]
            seg3 = image_key[2]
            seg4 = image_key[3]
            if len(image_key) == 4:
                image_data = self.image_dict[seg1][seg2][seg3][seg4]
            elif len(image_key) == 5:
                seg5 = image_key[4]
                image_data = self.image_dict[seg1][seg2][seg3][seg4][seg5]
            else:
                print('Programmer ERROR: image key tuple is not ' +
                      '4 or 5 segments:', len(image_key))
                print(image_key)
                return None

        return image_data

    def os_song_format(self, tree_name):
        """ Format song name as it will appear in operating system.
        :param tree_name: Formatted with Disk, Track & "-" but no extension.
            Previously created with build_out_name() and NOT build_out_name2().
        returns os_name: Legalized tree_name with extension appended
        """
        os_name = tree_name + u'.' + toolkit.uni_str(self.fmt)  # Add extension
        os_name = ext.legalize_song_name(os_name)  # Take out '/', '>', etc.
        return os_name  # os_name inserted into selection


# ==============================================================================
#
#       MetaScan class - Search Metadata for Artwork
#
# ==============================================================================

class MetaScan:
    """ Search Metadata for artwork

        Example DATA:

            STREAM #0:0(und): Audio: aac (LC) (mp4a / 0x6134706D), 44100 Hz, 
                stereo, f ltp, 270 kb/s (default)

            STREAM #0:1: Video: png, rgba(pc), 225x225, 90k tbr, 90k tbn, 90k tbc

        NOTE: Only used by mserve.py. May want to relocate there???

    """

    def __init__(self, toplevel, get_refresh_thread=None):
        
        self.top_level = toplevel
        self.get_refresh_thread = get_refresh_thread

        self.total_scanned = 0
        self.missing_file_at_loc = 0  # Tallied by caller
        self.missing_audio = 0  # Tallied by caller
        self.missing_artwork = 0
        self.found_artwork = 0
        self.meta_data_updated = 0
        self.meta_data_unchanged = 0
        self.last_thread_call = time.time()

    def CheckArtwork(self, meta_dict):
        """ :param meta_dict: Key/Value Pairs of ID tags 
            :returns True if Song File has artwork, False if "Video" not found
        """
        if self.top_level:
            self.top_level.update_idletasks()  # Allow X to close window
        else:
            return  # Closed window
        if self.get_refresh_thread:
            ''' Call refresh thread for tool tips, etc. '''
            now = time.time()
            if now - self.last_thread_call > .033:  # Was .033
                # Calling every 33 ms causes slight animation lag
                # When current song ends, MetaScan stops?
                thread = self.get_refresh_thread()  # Can change if play_top closes
                thread(sleep_after=False)  # Crashes when next song is played
                self.last_thread_call = now  # Adds 4 seconds but should be less :(
                # When called: 389 seconds, but no tooltips
                # Sleep after = False: 483.6583168507

            #thread = self.get_refresh_thread()  # Can change if play_top closes
            #thread(sleep_after=True)  # Using False causes starves music play
            # next song causing it to crash Tkinter.
        self.total_scanned += 1

        ''' Move to mserve.py missing_artwork_callback() function '''
        """
        if not meta_dict:
            self.missing_file_at_loc += 1
            return False  # Driven by FileControl.new() when OSError
        """
        
        ''' TODO: Use FileControl.valid_artwork add counts for missing audio '''
        for key, value in meta_dict.iteritems():
            if key.startswith("STREAM"):
                if "Video:" in value:
                    self.found_artwork += 1  # Not showing up
                    return True

        self.missing_artwork += 1  # Shows up in missing_file_at_loc ???
        return False

    def UpdateChanges(self, flag):
        """ :parameter flag: Can be True, False or None """
        if not self.top_level:
            return  # Closed window
        if flag:
            self.meta_data_updated += 1
        else:
            self.meta_data_unchanged += 1

    """  2008 Nissan Alt ima Coupe Bose 6-CD Changer - Specification chart:

    Supported media             CD, CD-R, CD-RW
    Supported file systems      ISO9660 LEVEL1, ISO9660 LEVEL2, Apple ISO, Romeo, Joliet 
                                * ISO9660 Level 3 (packet writing) is not supported.
    Supported versions*1
    MP3
        Version                 MPEG1, MPEG2, MPEG2.5
        Sampling frequency      8 kHz - 48 kHz
        Bit rate                8 kbps - 320 kbps, VBR
    WMA
        Version                 WMA7, WMA8, WMA9
        Sampling frequency      32 kHz - 48 kHz
        Bit rate                48 kbps - 192 kbps, VBR
    Tag information             ID3 tag VER1.0, VER1.1, VER2.2, VER2.3 (MP3 only)
    Folder levels               Folder levels: 8, Max folders: 255 (including root folder), 
                                Files: 512 (Max. 255 files for one folder)
    Text character number limit 128 characters
    Displayable char. codes*2   01: ASCII, 02: ISO-8859-1, 03: UNICODE (UTF-16 BOM Big 
                                Endian), 04: UNICODE (UTF-16 Non-BOM Big Endian), 05:
                                UNICODE (UTF-8), 06: UNICODE (Non-UTF-16 BOM Little Endian)

    *1 Files created with a combination of 48 kHz sampling frequency and 64 kbps bit rate cannot be played.
    *2 Available codes depend on what kind of media, versions and information are going to be displayed.

    NOTES ON-LINE:
        Audio CD sampling frequency is 44.1 KHz
        Audio CD bit rate is always 1,411 kilobits per second (Kbps). The MP3 format can range from around
        96 to 320Kbps, and streaming services like Spotify range from around 96 to 160Kbps.

    """

# End of encoding.py
