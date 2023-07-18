#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: Pippim
License: GNU GPLv3
Source: This repository
Description: mserve - Music Server - Encode (Rip) CD's
"""

from __future__ import print_function  # Must be first import
from __future__ import with_statement  # Error handling for file opens

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
#
# ==============================================================================
# noinspection SpellCheckingInspection
"""
Solves problems like:
    https://askubuntu.com/questions/541977/
    a-music-player-with-cd-ripping-and-cddb-lookup/542030#542030
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

TODO: https://stackoverflow.com/a/44906491/6929343

from mutagen.mp4 import MP4

def get_description(filename):
    return MP4(filename).tags.get("desc", [None])[-1]

def set_description(filename, description):
    tags = MP4(filename).tags
    tags["desc"] = description
    tags.save(filename)

'''

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
import monitor                  # To get/save window geometry
import message
import image as img
import timefmt as tmf           # Aug 13/2021 switch over to tmf abbreviation
import sql

EMAIL_ADDRESS = "pippim.com@gmail.com"  # TODO - setup variable in SQL History
# The email address isn't that important as throttling is by IP address.

''' File with dictionaries in pickle format passed between background jobs '''
IPC_PICKLE_FNAME = g.TEMP_DIR + "mserve_encoding_pickle"
RIP_CD_IS_ACTIVE = False        # Read by mserve.py


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

    def __init__(self, toplevel, tooltips, info, LODICT, caller_disc=None,
                 thread=None, sbar_width=12):

        global RIP_CD_IS_ACTIVE

        self.lib_top = toplevel  # Use same variable name as mserve
        self.tt = tooltips                  # Hovering fading tooltips
        self.info = info                    # Information Centre               
        RIP_CD_IS_ACTIVE = True             # Shared with mserve
        self.topdir = LODICT['topdir']      # What if there is no location dict?
        self.caller_disc = caller_disc  # Development reuse last disc ID
        self.get_refresh_thread = thread    # returns refresh_Xxx_top()
        self.disc = None                    # from python-libdiscid
        self.disc_count = None              # How many discs in Album?
        self.this_disc_number = None        # What is current disc number?
        self.release_list = None            # Musicbrainz release list
        self.rip_art = None                 # List of art images to encode
        self.rotated_art = None             # Spinning album artwork
        self.play_current_song_art = None   # Photo image of rotated art
        self.image_data = None              # Image encoded into file
        self.selected_medium = None         # Musicbrainz dictionary
        self.image_count = None             # Album artwork selected
        self.selected_date = None           # Date from MBZ or User

        # Ripping '#' multiple disc #. '99 - ' or '99 ' track numbering
        self.song_name = None               # checked Song title from treeview '#-99 -'
        self.os_song_name = None            # '#-99 Song name.xxx'
        self.os_full_path = None            # top_dir/artist/album/#-99 Song name.xxx
        self.sqlOsFileName = None            # artist/album/#-99 Song name.xxx
        self.is_compilation = None          # True/False flag.
        # When artist is "Various Artists" the directory is "Compilations" but
        # The metadata will contain real Artist Name, not "Compilations"
        self.song_duration = None           # Song duration string "hh:mm:ss"
        self.song_seconds = None            # Above in seconds
        self.song_size = None               # Song file size
        self.DiscNumber = None              # July 13, 2023
        self.CreationTime = None            # Initially same as stat.st_ctime
        self.rip_current_track = None       # Current track number start at 1
        self.song_rip_sec = 0               # How many seconds and blocks
        self.song_rip_blk = 0               # have been ripped for song?
        self.total_rip_sec = 0              # How many seconds and blocks
        self.total_rip_blk = 0              # ripped for selections?

        # Pulsating shades of green indicating which song is being ripped
        self.last_highlighted = None
        self.last_shade = None
        self.curr_shade = None
        self.skip_once = False              # First time through no last shade
        self.next_image_key_ndx = 0
        # Tree view
        self.reverse_checkbox = None        # User picked illogically

        ''' Set font style for all fonts including tkSimpleDialog.py '''
        img.set_font_style()

        ''' Place Window top-left of parent window with g.PANEL_HGT padding '''
        self.cd_top = tk.Toplevel()
        self.cd_top_is_active = True
        self.cd_top.minsize(width=g.WIN_MIN_WIDTH, height=g.WIN_MIN_HEIGHT)
        #x = self.lib_top.winfo_x() + g.PANEL_HGT
        #y = self.lib_top.winfo_y() + g.PANEL_HGT
        #geom = '%dx%d+%d+%d' % (1400, 975, x, y)
        geom = monitor.get_window_geom('encoding')
        self.cd_top.geometry(geom)
        self.cd_top.title("Reading CD - mserve")
        self.cd_top.configure(background="Gray")
        self.cd_top.columnconfigure(0, weight=1)
        self.cd_top.rowconfigure(0, weight=1)

        ''' Set delayed message box coordinates relative to cd_top '''
        #dtb = message.DelayedTextBox(title="Building music view",
        #                             toplevel=self.cd_top, width=1000)

        ''' Set program icon in taskbar '''
        img.taskbar_icon(self.cd_top, 64, 'white', 'lightskyblue', 'black')

        ''' Create master frame '''
        master_frame = ttk.Frame(self.cd_top, padding=(3, 3, 12, 12))
        master_frame.grid(column=0, row=0, sticky=tk.NSEW)
        tk.Grid.rowconfigure(master_frame, 0, weight=1)
        tk.Grid.columnconfigure(master_frame, 0, weight=1)

        ''' frame1 - artwork and selections '''
        frame1 = ttk.Frame(master_frame, borderwidth=g.BTN_BRD_WID,
                           padding=(2, 2, 2, 2), relief=tk.RIDGE)
        frame1.grid(column=0, row=0, sticky=tk.NSEW)
        # 7 rows of text labels and string variables auto adjust with weight 1
        #        for i in range(7):
        #            frame1.grid_rowconfigure(i, weight=1)
        ms_font = (None, g.MON_FONTSIZE)

        ''' Artwork image row 0, column 0 '''
        self.art_width = None
        self.art_height = None
        self.original_art = img.make_image("Reading Disc",
                                           image_w=375, image_h=375)
        self.using_cd_image = False
        if os.path.isfile('AudioDisc.png'):
            self.using_cd_image = True
            self.original_art = Image.open('AudioDisc.png')

        # cd_image.show()
        # 375x375 is happy medium between 250 and 500
        self.resized_art = self.original_art.resize((375, 375),
                                                    Image.ANTIALIAS)
        self.cd_song_art = ImageTk.PhotoImage(self.resized_art)
        self.cd_art_label = tk.Label(frame1, image=self.cd_song_art, font=ms_font)
        # self.cd_art_label.grid(row=0, row span=7, column=0, sticky=tk.W)
        # self.cd_art_label.grid(row=0, column=0, pad x=3, pad y=3, sticky=tk.W)
        self.cd_art_label.grid(row=0, column=0, sticky=tk.W)

        ''' Controls to resize image to fit frame '''
        frame1.bind("<Configure>", self.on_resize)
        self.start_w = frame1.winfo_reqheight()
        self.start_h = frame1.winfo_reqwidth()

        http = "https://musicbrainz.org/"
        msg = ("The Musicbrainz website " + http + " will be searched.\n" +
               "This website contains Artist, Album and Song information\n" +
               "for most Audio CDs ever produced.\n\n" +
               "Enter your MusicBrainz account email address below.\n\n" +
               "TIPS:\tCheck Medium to select songs all at once.\n\n" +
               "\tUse browser to copy image from website (Amazon, etc.).\n" +
               "\tThen click 'Clipboard image' button below.\n\n" +
               "\tA blank release date entry can be checked and\n" +
               "\tthen a pop-up window will appear to enter date.\n\n")

        self.mbAuthorization = sql.Authorization(
            self.cd_top, "MusicBrainz", http,  msg, tt=tooltips)

        ''' Scrollable textbox to show selections / ripping status '''
        Quote = ("It will take a minute to access Audio CD and the internet.\n" +
                 "If audio disc is not found in MusicBrainz, search that site.\n" +
                 "Then you can select songs and images from listings below.\n" +
                 "What you select from listings will appear in this window.\n\n" +
                 "MusicBrainz Account is using: " + EMAIL_ADDRESS + "\n\n" +
                 "TIPS:\tCheck Medium to select songs all at once.\n\n" +
                 "\tUse browser to copy image from website (Amazon, etc.).\n" +
                 "\tThen click 'Clipboard image' button below.\n\n" +
                 "\tA blank release date entry can be checked and\n" +
                 "\tthen a pop-up window will appear to enter date.\n\n")
        # self.scrollbox = CustomScrolledText(frame1, state="readonly", font=ms_font)
        # TclError: bad state "readonly": must be disabled or normal
        # Text padding not working: https://stackoverflow.com/a/51823093/6929343
        self.scrollbox = toolkit.CustomScrolledText(
            frame1, state="normal", font=ms_font, borderwidth=15, relief=tk.FLAT)
        self.scrollbox.insert("end", Quote)
        self.scrollbox.grid(row=0, column=1, padx=3, pady=3, sticky=tk.NSEW)
        tk.Grid.rowconfigure(frame1, 0, weight=1)
        tk.Grid.columnconfigure(frame1, 1, weight=1)

        self.scrollbox.tag_config('red', foreground='Red')
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
        for i, shade in enumerate(green_shades):
            self.scrollbox.tag_config(str(i), foreground=green_shades[i])
        self.scrollbox.tag_config('green', foreground='Green')
        self.scrollbox.tag_config('yellow', foreground='Yellow')
        self.scrollbox.tag_config('orange', foreground='Orange')
        self.scrollbox.config(tabs=("28m", "56m", "106m"))

        ''' frame2 - Treeview Listbox '''
        frame2 = ttk.Frame(master_frame, borderwidth=g.BTN_BRD_WID,
                           relief=tk.RIDGE)
        frame2.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)
        # TODO: Below is row 1 of master_frame, not of frame2
        frame2.grid_rowconfigure(1, weight=1)
        frame2.grid_columnconfigure(0, weight=1)

        ''' July 13, 2023 (actually today is July 18 but use common search date
            def on_double_click(event):
                item_id = event.widget.focus()
                item = event.widget.item(item_id)
                values = item['values']
                url = values[0]
                print("the url is:", url)        

            root = tk.Tk()
            t=ttk.Treeview(root)
            t.pack(fill="both", expand=True)
            t.bind("<Double-Button-1>", on_double_click)

        '''


        ''' Treeview List Box, Columns and Headings '''
        self.cd_tree = CheckboxTreeview(
            frame2, columns=("Duration", "First"), height=20, selectmode="none",
            show=('tree', 'headings'))
        self.cd_tree.column("#0", width=900, stretch=tk.YES)
        self.cd_tree.heading("#0", text="Musicbrainz listings")
        self.cd_tree.column("Duration", width=120, anchor=tk.CENTER, stretch=tk.NO)
        self.cd_tree.heading("Duration", text="Duration")
        self.cd_tree.column("First", width=120, anchor=tk.CENTER, stretch=tk.NO)
        self.cd_tree.heading("First", text="First Date")

        # See: https://stackoverflow.com/questions/60954478/tkinter-treeview-doesnt-resize-with-window
        self.cd_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        ''' Treeview select item - custom select processing '''
        self.ignore_item = None
        self.last_click_expand = None
        self.last_click_collapse = None
        self.current_image_key = None
        self.selected_image_keys = []  # list of tuples links to "imagesel" tag
        self.selected_artist = None  # What about compilations?
        self.selected_album = None  # Album name to use on all songs.
        self.selected_title = None  # Song name with track or extension.
        self.selected_mbz_id = None  # Musicbrainz ID
        self.selected_medium = None  # Only one medium_id must be selected
        self.selected_date = None  # Can be blank or "????" so test it.
        """ July 13, 2023 - Need DiscNumber, FirstDate, CreationTime, Composer """
        self.selected_composer = None  # July 13, 2023 - Used to be unused country
        self.selected_tracks = 0  # Number tracks selected from CD total
        # Selected songs are accessed via "checked" tag in treeview
        self.our_parent = None  # Umm...
        self.parent_tags = ("rel_id", "mbz_id", "medium_id", "images_id", "clips_id")

        self.cd_tree.bind('<Button-1>', self.button_1_click)

        """ STYLE ALREADY DEFINED IN PARENT:
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

        ''' Create Treeview item list '''
        # self.lib_tree.grid(row=0, column=0, sticky=tk.NSEW)
        # self.populate_cd_tree(dtb) # Future use of message.DelayedTextbox()

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
        self.tt.add_tip(self.cd_tree_btn1, text=text)

        ''' ▶  Rip Button - Validates songs and images are selected '''
        self.cd_tree_btn2 = tk.Button(
            frame3, text="▶  Rip Disc", width=g.BTN_WID, command=self.rip_cd)
        self.cd_tree_btn2.grid(row=0, column=1, padx=2)
        text = \
            "First select songs on CD to rip. Then select artwork from\n" +\
            "available sources or insert new artwork from clipboard.\n" +\
            "Finally ensure optional fields such as release date are\n" +\
            "either selected or manually entered.\n\n" +\
            'After all that, click this "▶  Rip Disc" button'

        self.tt.add_tip(self.cd_tree_btn2, text=text)

        ''' 📋 Clipboard image - 📋 (u+1f4cb) Must be valid image format '''
        self.cd_tree_btn3 = tk.Button(
            frame3, text="📋  Clipboard image", width=g.BTN_WID + 4,
            command=self.image_from_clipboard)
        self.cd_tree_btn3.grid(row=0, column=2, padx=2)
        self.cd_tree_btn3.forget()
        self.image_from_clipboard_count = 0
        self.clipboard_images = []
        text = \
            "In your browser navigate to sites containing album cover\n" +\
            "artwork such as Amazon, Wikipedia, Musicbrainz, etc.\n" +\
            "Right click on images and copy to clipboard. Then return\n" +\
            'here and insert image using "📋  Clipboard image" button'
        self.tt.add_tip(self.cd_tree_btn3, text=text)

        ''' Menu bars: Format, Quality '''
        # Format menu
        mb = tk.Menu(self.cd_top)
        fmt_bar = tk.Menu(mb, tearoff=0)
        self.fmt_var = tk.StringVar()
        self.fmt_var.set("oga")
        fmt_bar.add_radiobutton(
            label=".wav (Original CD format)", command=self.show_selections,
            font=ms_font, value="wav", variable=self.fmt_var)
        fmt_bar.add_radiobutton(
            label=".oga (Ogg Vorbis compression)", command=self.show_selections,
            font=ms_font, value="oga", variable=self.fmt_var)
        fmt_bar.add_radiobutton(
            label=".flac (Free Lossless Audio Codec)", command=self.show_selections,
            font=ms_font, value="flac", variable=self.fmt_var)
        mb.add_cascade(label=" Format ▼ ", menu=fmt_bar, font=ms_font)

        text = \
            "The Format dropdown menu allows you to pick the encoding\n" +\
            "technology for creating music files.  WAV files are original\n" +\
            "CD format with no images or ID tags such as album, artist or\n" +\
            "song names.  FLAC files provide same quality as WAV files\n" +\
            "and allow images and ID tags.  Both WAV and FLAC files take\n" +\
            "the largest space, about 35 MB.  OGA files balance size, about\n" +\
            "6 MB, and quality with image and ID tag support."
        self.tt.add_tip(fmt_bar, text=text, tool_type='menu')

        # Quality menu
        self.quality_var = tk.IntVar()
        self.quality_var.set(70)
        quality_bar = tk.Menu(mb, tearoff=0)
        quality_bar.add_radiobutton(
            label="30 % (Smallest size, lowest quality)", command=self.show_selections,
            font=ms_font, value=30, variable=self.quality_var)
        quality_bar.add_radiobutton(
            label="40 %", command=self.show_selections, font=ms_font, value=40,
            variable=self.quality_var)
        quality_bar.add_radiobutton(
            label="50 %", command=self.show_selections, font=ms_font, value=50,
            variable=self.quality_var)
        quality_bar.add_radiobutton(
            label="60 %", command=self.show_selections, font=ms_font, value=60,
            variable=self.quality_var)
        quality_bar.add_radiobutton(
            label="70 % (Medium size, very good quality)",
            command=self.show_selections, font=ms_font, value=70,
            variable=self.quality_var)
        quality_bar.add_radiobutton(
            label="80 %", command=self.show_selections, font=ms_font, value=80,
            variable=self.quality_var)
        quality_bar.add_radiobutton(
            label="90 %", command=self.show_selections, font=ms_font, value=90,
            variable=self.quality_var)
        quality_bar.add_radiobutton(
            label="100 % (Largest size, highest quality)",
            command=self.show_selections, font=ms_font, value=100,
            variable=self.quality_var)
        mb.add_cascade(label=" Quality ▼ ", menu=quality_bar, font=ms_font)
        text = \
            "The Quality dropdown menu allows you to pick the encoding\n" +\
            "sound quality for creating music files.  WAV files and FLAC\n" +\
            "files are always 100% sound quality.  OGA files can have the\n" +\
            "quality set from 30% to 100%.  The higher quality the larger\n" +\
            "size for the music file.  For OGA 70% appears the best balance\n" +\
            "between quality and file size.  Do some tests for yourself."
        self.tt.add_tip(quality_bar, text=text, tool_type='menu', anchor="sw")

        # Song naming format
        self.nam_var = tk.StringVar()
        self.nam_var.set("99 ")
        nam_bar = tk.Menu(mb, tearoff=0)
        nam_bar.add_radiobutton(
            label="99 Song name.ext", command=self.show_selections, font=ms_font,
            value="99 ", variable=self.nam_var)
        nam_bar.add_radiobutton(
            label="99 - Song name.ext", command=self.show_selections, font=ms_font,
            value="99 - ", variable=self.nam_var)
        mb.add_cascade(label=" Naming ▼ ", menu=nam_bar, font=ms_font)
        text = \
            "The Naming dropdown menu allows you to choose the filenames\n" +\
            "assigned to music files.  The extension is automatic where\n" +\
            'WAV files are assigned as ".wav", FLAC files are assigned as\n' +\
            '".flac" and OGA files are assigned as ".oga". You can however\n' +\
            'choose the prefix of "99 " or "99 - " to prepend to filenames.\n\n' +\
            "Where '99' is the track number of the song."
        self.tt.add_tip(nam_bar, text=text, tool_type='menu', anchor="nw")

        # Target menu
        self.trg_var = tk.StringVar()
        self.trg_var.set(self.topdir)
        trg_bar = tk.Menu(mb, tearoff=0)
        trg_bar.add_radiobutton(
            label=self.topdir, command=self.show_selections, font=ms_font,
            value=self.topdir, variable=self.trg_var)
        mb.add_cascade(label=" Target ▼ ", menu=trg_bar, font=ms_font)

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


        self.get_discid_active = True       # First step
        self.disc_get_active = True
        self.get_discid_time = 0.0

        self.mbz_get1_active = False
        self.mbz_release_id = None          # = self.disc.id but can change
        self.mbz_get1_time = 0.0

        self.mbz_get2_active = False
        self.mbz_get2_time = 0.0
        self.image_dict = None              # Images passed in pickle

        self.treeview_active = False
        self.disc_enc_active = False
        self.encode_track_time = 0.0        # Time to encode track
        self.encode_album_time = 0.0        # Time to encode all tracks
        self.encode_album_seconds = 0       # Playing seconds in all songs
        self.encode_album_cnt = 0           # Number tracks encoded
        self.encode_album_size = 0          # File size of all songs
        self.music_id = None                # History's matching music ID
        self.tracknumber = None
        self.clip_parent = None
        self.gst_encoding = None            # gnome encoding format
        self.fmt = None                     # self.fmt_var.get()
        self.naming = None                  # self.nam_var.get()

        self.loc_copy_active = False        # Future copy to other locations
        self.disc_id_manual_override = None    # Musicbrainz override of disc.id
        self.active_pid = 0  # 0 = no process ID is running
        self.cd_rotated_value = 0  # For rotating audio cd image
        self.background = self.resized_art.getpixel((3, 3))

        self.cd_run_to_close()  # At this point tkinter mainloop has
        # control and Music Players keeps spinning it's artwork. We have our
        # own spinner with CD Audio Disc image and 1 second text "Reading Disc"
        # with 1/2 second text off. Whilst our own disc image spins 1 degree
        # every 10th second in resizeable widget within resizeable frame2.

    def on_resize(self, event):
        """ Resize image when frame size changes """
        # images use ratio of original width/height to new width/height
        #w_scale = float(event.width) / self.start_w
        h_scale = float(event.height) / self.start_h

        # Override maintain square by factoring width equally on height change
        w_scale = h_scale
        self.art_width = int(w_scale) - 8  # Awkward
        self.art_height = int(h_scale) - 8

        self.resized_art = self.original_art.resize(
            (self.art_width, self.art_height),
            Image.ANTIALIAS)
        self.cd_song_art = ImageTk.PhotoImage(self.resized_art)
        self.cd_art_label.configure(image=self.cd_song_art)

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
                self.loc_copy_active = False
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

            if self.caller_disc:
                #ext_name = "python disc_get.py " + IPC_PICKLE_FNAME
                #self.active_pid = ext.launch_command(ext_name)
                self.active_pid = 0
                self.disc = self.caller_disc
                text = "ENCODE_DEV - Override with last Disc ID: " + self.disc.id
                self.info.cast(text)
                with open(IPC_PICKLE_FNAME, "wb") as f:
                    ''' Give next step what it expects to see in IPC file '''
                    pickle.dump(self.disc, f)  # Save dictionary as pickle file
            else:
                ext_name = "python disc_get.py " + IPC_PICKLE_FNAME
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

            text = "Begin Step 2. Search MusicBrainz for Disc ID: "
            text += str(self.disc.id)
            text += "\n\nFinished Step 1. Getting Disc ID. Time: "
            text += str(self.get_discid_time)
            self.info.cast(text)

            try:
                # If valid disc object, checking dictionary causes error
                if self.disc.get('error'):
                    # TODO: Display errors 1, 2 & 3
                    self.mbz_get2_active = False  # Turn off next step
                    messagebox.showinfo(title="Rip CD Error", icon="error",
                                        message="Audio CD not found", parent=self.cd_top)
                    self.cd_close()
                    return  # Empty dictionary = CD error
                # TODO: Put in logging errors
                else:
                    # We still have a problem if this is a dictionary returned
                    self.mbz_get2_active = False  # Turn off next step
                    messagebox.showinfo(title="Rip CD Error", icon="error",
                                        message="Dictionary returned??", parent=self.cd_top)
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
            #self.disc

            # Search Musicbrainz with disc object and search limit (parm 2)
            # When limit is 3 or less artwork may be limited (or non-existent)
            # TODO: When limit is 1, treeview closes
            ext_name = "python mbz_get1.py " + IPC_PICKLE_FNAME + " 10 " + \
                       EMAIL_ADDRESS
            self.active_pid = ext.launch_command(ext_name,
                                                 toplevel=self.lib_top)
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

            text = "Begin Step 3. Search MusicBrainz for Album Artwork: "
            text += "\n\nFinished Step 2. Search MusicBrainz for Disc ID. Time: "
            text += str(self.mbz_get1_time)
            self.info.cast(text)

            # Did mbz_get1.py report an error?
            #pprint('\nRELEASE LIST ==========================================')
            #pprint(self.release_list)  # To see release-list if error
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

            self.selected_artist = first_release['artist-credit'][0]['artist']['name']
            self.selected_album = first_release['title']  # Album Title
            sql.hist_add(
                time.time(), 0, g.USER, 'encode', 'mbz_get1',
                self.selected_artist, self.selected_album,
                "Musicbrainz ID: " + self.mbz_release_id,
                0, releases, self.mbz_get1_time,
                "Get releases list: " + time.asctime(time.localtime(time.time())))

            # Download images with 500x500 pixel (gets all parm. 500 ignored now)
            ext_name = "python mbz_get2.py " + IPC_PICKLE_FNAME + " 500"
            self.active_pid = ext.launch_command(ext_name,
                                                 toplevel=self.lib_top)
            # TODO: Status is getting MusicBrainz Album Artwork with mbz_get2.py.

        elif self.treeview_active:
            # Fourth step Populate Treeview and enter idle loop
            self.treeview_active = False
            # TODO: .grid() not working - button is always visible.
            self.cd_tree_btn3.grid()  # Image from clipboard button
            self.cd_top.title("Select CD song titles and cover art - mserve")

            # Our last program has just finished. Get dictionary results
            self.image_dict = {}
            with open(IPC_PICKLE_FNAME, 'rb') as f:
                self.image_dict = pickle.load(f)

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
                                 text=msg, icon="error", parent=self.cd_top)
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
                self.selected_artist, self.selected_album, None,
                size, releases, self.mbz_get2_time,
                "Get cover art: " + time.asctime(time.localtime(time.time())))

            self.populate_cd_tree()
            self.cd_tree.update_idletasks()  # Refresh treeview display

        elif self.disc_enc_active:
            # self.encode_track_time = time.time()
            self.rip_next_track()

        # Loop forever giving 30 fps control to parent
        self.lib_top.after(33, self.cd_run_to_close)

    def update_display(self):
        """ Called in cd_run_to_close() and by message.AskQuestion() """
        self.cd_spin_art()  # Rotate artwork 1°
        if self.disc_enc_active:  # Ripping the CD now?
            self.update_rip_status()  # Update ripping progress
        self.active_pid = ext.check_pid_running(self.active_pid)
        self.lib_top.update()  # It's really mserve.py lib_top

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

        #print('answer.string:', answer.string)
        if len(answer.string) != 28:
            # We could do another ShowInfo that encoding is aborting now.
            #print('answer.string length is not 28:', len(answer.string))
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
        self.rotated_art = Image.new("RGBA",
                                     (self.art_width, self.art_height), self.background)
        rot = im.rotate(self.cd_rotated_value)
        self.rotated_art.paste(rot, (0, 0), rot)

        self.play_current_song_art = ImageTk.PhotoImage(self.rotated_art)
        self.cd_art_label.configure(image=self.play_current_song_art)

    def rip_cd(self):
        """ Rip the CD

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
                self.cd_top,
                "No songs selected",
                "At least one song must be selected to Rip CD.",
                icon='error')
            return

        self.image_count = len(self.selected_image_keys)
        if self.image_count == 0:
            # TODO: if .wav file this is good.
            result = messagebox.askquestion(
                "No Images selected",
                "Songs will be ripped without artwork. Are You Sure?",
                icon='warning', parent=self.cd_top)
            if result == 'no':
                return

        if self.image_count > 1:
            # TODO: if .wav file this is bad.
            result = messagebox.askquestion(
                "Multiple Images selected",
                "Songs will be ripped with alternating artwork. Are You Sure?",
                icon='info', parent=self.cd_top)
            if result == 'no':
                return

        if not self.review_before_rip():
            return

        if not self.selected_date:
            result = messagebox.askquestion(
                "No release date selected",
                "Songs will be ripped without a release date. Are You Sure?",
                icon='warning', parent=self.cd_top)
            # TODO: Get release date
            if not result == 'yes':
                return

        #rel_id = self.cd_tree.parent(self.selected_medium)
        #rip_selection = self.cd_tree.item(rel_id, 'text')
        self.rip_current_track = 0      # Nothing has been ripped yet
        if not self.set_gst_encoding():
            exit()                      # Programmer error
        self.cd_top.title("Ripping CD to " + self.topdir + " - mserve")
        # FUTURE: Show progress
        self.song_rip_sec = 0           # How many seconds and blocks
        self.song_rip_blk = 0           # have been ripped for song?
        self.total_rip_sec = 0          # How many seconds and blocks
        self.total_rip_blk = 0          # ripped for selections?

        # Pulsating shades of green indicating which song is being ripped
        self.last_highlighted = None
        self.last_shade = None
        self.skip_once = False
        self.next_image_key_ndx = 0

        ''' BIG EVENT TRIGGER '''
        self.disc_enc_active = True  # Start background processing


    def review_before_rip(self):
        """ Allow changes to Artist, Album, Years, Compilations """
        pass

    # noinspection SpellCheckingInspection,PyPep8Naming
    def set_gst_encoding(self):
        """ https://gstreamer.freedesktop.org/documentation/tools/gst-launch.html """
        if self.fmt == 'wav':
            self.gst_encoding = 'wavenc'
        elif self.fmt == 'flac':
            self.gst_encoding = 'flacenc'
            from mutagen.flac import FLAC as audio_file
        elif self.fmt == 'oga':
            quality = 'quality=' + str(float(self.quality_var.get()) / 100.0)
            self.gst_encoding = 'vorbisenc {} ! oggmux'.format(quality)
            from mutagen.oggvorbis import OggVorbis as audio_file
        else:
            print('Programmer ERROR set_gst_encoding() bad fmt=', fmt)
            return False

        return True

    # noinspection PyPep8Naming
    def rip_next_track(self):
        """ Rather awkward function called to update last rip 
            and start new rip in background 
        """

        # noinspection SpellCheckingInspection
        self.cd_rotated_value = 0  # Start next song right-side up

        # Below should be in a function called only once

        # Not first time? Did we just finish ripping a song?
        if self.rip_current_track > 0:
            # TODO: Add song to music table
            #       Add to history table 'init' and 'meta' actions
            #print('END:   self.encode_track_time:', time.time())
            self.encode_track_time = time.time() - self.encode_track_time
            #print('DIFF.: self.encode_track_time:', self.encode_track_time)
            self.add_sql_music()

            # TODO: Apply webscrape lyrics from buffer

            # Add to album totals
            self.encode_album_time += self.encode_track_time
            self.encode_album_seconds += self.song_seconds
            self.encode_album_cnt += 1
            self.encode_album_size += self.song_size

            # Tag song as completed
            self.scrollbox.highlight_pattern(self.os_song_name, "green")
            self.last_highlighted = self.os_song_name

            # Does song format support metadata?
            if not self.fmt == "wav":
                # Apply metadata to last song ripped
                self.add_metadata_to_song()
                self.add_sql_metadata()  # Also adds both history rows

                # Apply Cover art
                # print('self.image_count:',self.image_count)
                if self.image_count > 0:
                    if self.fmt == "oga":
                        self.add_image_to_oga()
                    elif self.fmt == "flac":
                        print('TODO: Add flac image support.')
                    else:
                        print('Programmer ERROR: Add unknown image support.')
            else:
                pass  # TODO: Manually add 'file' 'init' history record

        # Alternate tracks with next image list AND next clipboard list
        if self.image_count > 0:
            # TODO: Support individual track image assignment
            image_key = self.selected_image_keys[self.next_image_key_ndx]
            self.image_data = self.get_image_by_key(image_key)
            if self.image_data is None:
                self.image_count = 0  # Turn off all images
                print('Programmer ERROR: Failed to get image from list.')
            else:
                # TODO: We are building art in next line already, do we need above?
                # self.rip_art.append(ImageTk.PhotoImage(resized_art))

                # Update rotating artwork with current track's artwork
                self.image_data_to_frame(self.image_data)

            # Setup for next track
            self.next_image_key_ndx += 1
            if self.next_image_key_ndx == self.image_count:
                # End of image list, back to first image for song after next
                self.next_image_key_ndx = 0

        '''
        if self.rip_current_track <= self.disc.last_track:
            if self.get_next_rip_name():
                pass
            else:
                self.disc_enc_active = False  # Background processing done
                self.cd_close()
        else:
            self.disc_enc_active = False  # Background processing done
            self.cd_close()
        '''
        # Are we all done?
        if not self.get_next_rip_name():

            # Save SQL history for album
            if self.encode_album_cnt > 0:
                # If we ripped at least one track, add history 'encode' 'album'
                duration = tmf.mm_ss(self.encode_album_seconds)
                sql.hist_add(
                    time.time(), 0, g.USER, 'encode', 'album',
                    self.selected_artist, self.selected_album,
                    "Audio disc id: " + self.disc.id, self.encode_album_size,
                    self.encode_album_seconds, self.encode_album_time,
                    "Tracks: " + str(self.encode_album_cnt) +
                    " Duration: " + duration +
                    " Finished: " + time.asctime(time.localtime(time.time())))

            self.encode_album_time = 0.0
            self.encode_album_seconds = 0
            self.encode_album_cnt = 0
            self.encode_album_size = 0
            self.disc_enc_active = False  # Background processing done
            self.cd_close()
            return


        # Rip next track
        self.encode_track_time = time.time()
        #print('START: self.encode_track_time:', self.encode_track_time)
        # noinspection SpellCheckingInspection
        ext_name = 'gst-launch-1.0 cdiocddasrc track={} ! ' \
            .format(self.rip_current_track) + \
            'audioconvert ! {} ! '.format(self.gst_encoding) + \
            'filesink location="{}"'.format(self.os_full_path)
        # inspection SpellCheckingInspection

        # ext_name = "sleep 3"   # For speedy loop testing
        self.active_pid = ext.launch_command(ext_name,
                                             toplevel=self.lib_top)

        # TODO: Call webscrape and get lyrics into buffer
        return  # Loops for next song


    def add_sql_music(self):
        """ Populate SQL Music Table Row with new CD track """
        # os.stat gives us all of file's attributes
        stat = os.stat(self.os_full_path)
        self.song_size = stat.st_size
        self.CreationTime = stat.st_ctime
        # converted = float(self.song_size) / float(CFG_DIVISOR_AMT)   # Not used
        # fsize = str(round(converted, CFG_DECIMAL_PLACES))  # Not used

        ''' Add the song without metadata '''
        # Does 'sql' conflict with import? Try 'sql_cmd' instead


        sql_cmd = "INSERT OR IGNORE INTO Music (OsFileName, OsAccessTime, \
            OsModifyTime, OsChangeTime, OsFileSize, CreationTime) \
            VALUES (?, ?, ?, ?, ?, ?)"
        sql.cursor.execute(sql_cmd, (self.sqlOsFileName, stat.st_atime,
                           stat.st_mtime, stat.st_ctime, self.song_size,
                           stat.st_ctime))
        '''
        sql_cmd = "INSERT OR IGNORE INTO Music (OsFileName, \
            OsAccessTime, OsModificationTime, OsCreationTime, OsFileSize) \
            VALUES (?, ?, ?, ?, ?)"
        sql.cursor.execute(sql_cmd, (self.sqlOsFileName, stat.st_atime,
                           stat.st_mtime, stat.st_ctime, self.song_size))
        '''  # convert July 13, 2023



        sql.con.commit()
        music_id = sql.cursor.lastrowid
        sql.cursor.execute("SELECT Id FROM Music WHERE OsFileName = ?",
                           [self.sqlOsFileName])
        d = dict(sql.cursor.fetchone())
        self.music_id = d["Id"]
        if self.music_id != music_id:
            print('Song file already encoded! self.music_id:',
                  self.music_id, '!=', music_id)

        sql.hist_add(
            time.time(), self.music_id, g.USER, 'file', 'init',
            self.selected_artist, self.os_song_name, self.sqlOsFileName,
            self.song_size, self.song_seconds, self.encode_track_time,
            "encoded: " + time.asctime(time.localtime(time.time())))
        sql.hist_add(
            time.time(), self.music_id, g.USER, 'encode', 'track',
            self.selected_artist, self.os_song_name, self.sqlOsFileName,
            self.song_size, self.song_seconds, self.encode_track_time,
            "finished: " + time.asctime(time.localtime(time.time())))


    def add_sql_metadata(self):
        """ July 13, 2023 - Need DiscNumber, FirstDate, CreationTime, Composer """
        genre = None                # TODO: Get with tk.Entry like release date
        #genre = ""                  # None type breaks genre.decode("utf8")


        sql.update_metadata(
            self.sqlOsFileName, self.selected_artist, self.selected_album,
            self.selected_title, genre, self.tracknumber, self.selected_date,
            self.song_seconds, self.song_duration, self.DiscNumber, 
            self.selected_composer)
        '''
        sql.update_metadata(
            self.sqlOsFileName, self.selected_artist, self.selected_album,
            self.selected_title, genre, self.tracknumber, self.selected_date,
            self.song_seconds, self.song_duration)
        '''  # convert July 13, 2023 



        # Above automatically creates history records for 'meta' 'init'


    # noinspection PyPep8Naming
    def add_metadata_to_song(self):
        """ July 13, 2023 - Need DiscNumber, AlbumArtist, AlbumDate, Genre,
            Compilation "0" or "1". CreationTime, Composer """
        if self.fmt == 'flac':
            from mutagen.flac import FLAC as audio_file
        elif self.fmt == 'oga':
            from mutagen.oggvorbis import OggVorbis as audio_file
        else:
            print('Programmer ERROR: add_metadata_to_song() bad fmt=', self.fmt)
            return False

        # noinspection SpellCheckingInspection
        try:
            # Maybe Kid3 has batch tagging functionality?
            audio = audio_file(self.os_full_path)
        except UnicodeDecodeError as err:
            print(err)
            # noinspection SpellCheckingInspection
            print('add_metadata_to_song() ERROR mutagen.oggvorbis on file:')
            print(self.os_full_path)
            return False

        # Doesn't fix the error encoding with UTF-8
        # noinspection SpellCheckingInspection        
        # /home/rick/Music/Jim Steinem/Bad for Good/06 Surf’s Up.oga
        # 'ascii' codec can't decode byte 0xe2 in position 50: ordinal not in range(128)

        # print('Tagging track {}'.format(self.os_song_name))

        # noinspection SpellCheckingInspection
        self.tracknumber = str(self.rip_current_track) + "/" + str(self.disc.last_track)
        audio['DISC'] = self.DiscNumber  # July 13, 2023
        audio['TRACKNUMBER'] = self.tracknumber

        """ July 13, 2023 - Need Genre, FirstDate, CreationTime, Compilation, Composer """
        # 'ARTIST' goes to 'ALBUMARTIST' in Kid3 and iTunes
        # July 13, 2023 - Perhaps ALBUMARTIST is the original band/artist

        """ July 13, 2023 - 'ARTIST' would be Clarence Clemmons """
        audio['ARTIST'] = self.selected_artist

        """ July 13, 2023 - 'ALBUMARTST' would be Various Artists 
            Note iTunes didn't use ALBUMARTST tag on compilations? """
        audio['ALBUMARTIST'] = self.selected_artist

        """ July 13, 2023 - 'ALBUM' would be Greatest Hits [Disc 3] """
        audio['ALBUM'] = self.selected_album
        audio['TITLE'] = self.selected_title  # '99 -' and .ext stripped
        if self.selected_date:
            audio['DATE'] = self.selected_date
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
        '''
        # inspection SpellCheckingInspection

    def add_image_to_oga(self):
        """ FLAC and OGG have different methods. OGG has diff read/write too.
            See: https://mutagen.readthedocs.io/en/latest/user/vcomment.html
        """
        import base64
        from mutagen.oggvorbis import OggVorbis
        # noinspection PyProtectedMember
        from mutagen.flac import Picture

        try:
            file_ = OggVorbis(self.os_full_path)
        except UnicodeDecodeError as err:
            print(err)
            # noinspection SpellCheckingInspection
            print('add_image_to_oga() ERROR mutagen.oggvorbis on file:')
            print(self.os_full_path)
            return False

        picture = Picture()

        # Convert image to jpeg for saving

        # print('Opening image being encoded with picture.data')
        # TODO: There are two different python-magic, expand to handle that.
        import magic
        # print('magic contents:')
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
        picture.type = 17  # Hex 11 - A bright colorful fish
        picture.type = 3  # Hex 03 - Cover (Front)
        # picture.desc = u"mserve - add_image_to_oga()"
        # from: https://stackoverflow.com/questions/12053107/
        #       test-a-string-if-its-unicode-which-utf-standard-is-
        #       and-get-its-length-in-bytes
        try:
            # Ensure we are passing unicode to flac.py (which is patched)
            self.selected_title.decode('utf-8')
        except UnicodeError:
            self.selected_title.encode('utf-8')

        picture.desc = self.selected_title
        width, height, depth = 100, 100, 32
        picture.width = width  # Seems to have no effect?
        picture.height = height
        picture.depth = depth

        try:
            picture_data = picture.write()
        except UnicodeDecodeError as err:
            #   File "/usr/lib/python2.7/dist-packages/mutagen/flac.py", 
            # line 597, in write:  desc = self.desc.encode('UTF-8')

            print(err)
            print('add_image_to_oga() ERROR mutagen.flac.Picture.write on file:')
            print(self.os_full_path)
            return False

        encoded_data = base64.b64encode(picture_data)
        # noinspection SpellCheckingInspection
        vcomment_value = encoded_data.decode("ascii")

        file_["metadata_block_picture"] = [vcomment_value]
        file_.save()

    def get_next_rip_name(self):
        """ Get next song in selected list and convert to UTF-8.
            Set the song name, OS song name and full OS path song name
        """
        self.os_song_name = None
        self.song_name = ""
        i = 0  # To make pycharm charming :)
        for i, track_id in enumerate(self.cd_tree.get_children(
                self.selected_medium)):
            if i < self.rip_current_track:
                continue  # Skip ahead to next track to rip
            tags = self.cd_tree.item(track_id, 'tags')
            if 'checked' in tags:  # Was this song selected?
                self.song_name = self.cd_tree.item(track_id, 'text')
                self.song_name = self.song_name.encode("utf8")
                # Convert '99 - ' to '99 ' if necessary. Append extension
                self.os_song_name = self.os_song_format(self.song_name)
                self.song_duration = self.cd_tree.item(track_id, 'values')[0]
                self.song_seconds = tmf.get_sec(self.song_duration)
                break

        if self.os_song_name is None:
            self.rip_current_track = self.disc.last_track + 1
            return False  # No more songs

        # Does target directory exist?
        ''' July 15, 2023 Support compilations '''
        self.is_compilation = self.selected_artist == "Various Artists" 
        if self.is_compilation:
            artist = "Compilations"
        else:
            artist = self.selected_artist
        ''' June 3, 2023 Create legal names - Replace '/', '?', ':' with '_' '''
        part = ext.legalize_dir_name(artist.encode("utf8")) + os.sep + \
            ext.legalize_dir_name(self.selected_album.encode("utf8")) + os.sep
        prefix = self.topdir.encode("utf8") + os.sep + part
        if not os.path.isdir(prefix):
            try:
                os.makedirs(prefix)
            except:
                # TODO: show error message
                print('Could not make directory path:', prefix)
                self.song_name = ""  # Force exit
                self.rip_current_track = self.disc.last_track + 1
                return False

        # topdir/artist/album/99 song.ext - self.os_song_name already legal
        self.os_full_path = prefix + self.os_song_name  
        self.sqlOsFileName = part + self.os_song_name  # SQL music key  
        self.rip_current_track = i + 1
        return True

    def update_rip_status(self):
        """ Update songs done, songs todo, song in progress using
            pattern_highlight
        """
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
            # This is our first time updating rip status
            self.curr_shade = 0

        self.scrollbox.highlight_pattern(self.os_song_name,
                                         str(self.curr_shade))
        self.last_shade = self.curr_shade

# ============================================================================
#
#   Rip_CD class: populate_cd_tree
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
        #print("self.mbz_release_id:", self.mbz_release_id)
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
            #disc_list = disc['disc-list']
            # print('index i:', i, 'disc_list:', disc_list)
            disc_id = str(d['medium-list'][i]['disc-list'][0]['id'])
            #print("disc-list:", d['medium-list'][i]['disc-list'])
            for disc_id in d['medium-list'][i]['disc-list']:
                if disc_id['id'] == self.mbz_release_id:
                    disc_found = True
                    this_disc_number = int(d['medium-list'][i]['position'])
                    #this_disc_number = d['medium-list'][i]['disc-count']

        if disc_count > 1:
            d['title'] = d['title'] + " [Disc #" + str(this_disc_number) + \
                         " of " + str(disc_count) + "]"

        return disc_found, this_disc_number, disc_count

    def populate_cd_tree(self):
        """ Paint the release selection treeview """

        sep = "  |  "  # Note length of separator = 5 below

        for ndx, d in enumerate(self.release_list):
            #print('\nRelease ndx:', ndx, d['title'])
            ''' Parent line with score, artist and album
            '''
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
            # self.cd_tree.item(mbz_id, open = opened)
            # If no release date, create an entry for user to select.
            if 'release-event-list' not in d:
                d['release-event-list'][0]['date'] = "????"  # Denotes added here

            # Temporary override for testing
            # d['release-event-list'][0]['date'] = "????" # Denotes added here

            formatted = "Release date: " + d['release-event-list'][0]['date']
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
            if 'format' in d['medium-list'][mdm_ndx]:   # EG CD or Vinyl
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

            # TODO medium-list is 1 for second CD, etc.
            tracks_list = d['medium-list'][mdm_ndx]['track-list']
            # tracks_list = r['release']['medium-list'][mdm_ndx]['track-list']
            for i, track_d in enumerate(tracks_list):
                # print('track_d:\n',track_d)
                #position = track_d['position']
                #if i == 0:
                #    print("\n---------------------------------- First Track:")
                #    pprint(track_d)
                #    pass
                recording_d = track_d['recording']
                song = track_d['recording']['title']
                first_date = track_d['recording']['first-date']

                # Not sure why below getting pycharm errors...
                #try:
                #    first_date = track_d['recording']['first-date']
                #else:
                #    first_date = None
                length = recording_d.get('length', '0')

                # In database some tracks have no length key
                if length is None:
                    duration = 0
                else:
                    duration = int(length) / 1000

                hhmmss = tmf.mm_ss(duration, rem=None)
                track_name_fmt = "{:02} - {}"
                out_name = track_name_fmt.format(i + 1, song.encode("utf8")) \
                    .replace('/', '-')
                if self.disc_count > 1:
                    # Prepend disc number to track (song) name
                    out_name = str(self.this_disc_number) + "-" + out_name

                self.cd_tree.insert(medium_id, "end", text=out_name, 
                                    values=(hhmmss, first_date), 
                                    tags=("track_id", "unchecked"))

            ''' Our third parent line has online cover art  '''
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
                #first_time = False
            except Exception as err:
                print(err)
                continue  # Remove this line to see following error:
                # No JSON object could be decoded
                # print(entry)   # Can't do, image-data too large for screen

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

    def cd_tree_insert_image(self, rel_id, mbz_id, opened, image_list, first_time):
        """ Insert artwork lines into CD Treeview
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
                #size = str(len(d['image-data']))
                size = "{:,}".format(len(d['image-data']))
                self.cd_tree.insert(self.our_parent, "end", values=size,
                                    text=d['image'], tags=("image_id", "unchecked"))

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
            messagebox.showinfo(
                "Copy from clipboard error.",
                "You cannot copy image until Musicbrainz listing obtained.",
                icon='warning', parent=self.cd_top)
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
                messagebox.showinfo(
                    "Copy from clipboard error.",
                    "You must copy an image to the clipboard first.",
                    icon='error', parent=self.cd_top)
            else:
                messagebox.showinfo(
                    "Copy from clipboard error.",
                    err, icon='error', parent=self.cd_top)
            return

        if not pipe.returncode == 0:
            messagebox.showinfo(
                "Copy from clipboard error.",
                "An error occurred trying to grab image from clipboard.",
                icon='error', parent=self.cd_top)
            return

        if text:
            # Image is going direct to stdout instead of filename passed?
            self.image_data_to_frame(text)
        else:
            messagebox.showinfo("Copy from clipboard error.",
                                "Image should have been in clipboard but not found?",
                                icon='error', parent=self.cd_top)
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
            result = messagebox.askquestion(
                "Discard unique selections.",
                "All items will be selected and unique selections lost." +
                " Are You Sure?",
                icon='info', parent=self.cd_top)
            if result == 'no':
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
        """ Display song or art info. """

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

    def display_image(self, Id):
        """ Display image and
            return tuple of image key fields
        """
        # Get our image entry
        image_name = self.cd_tree.item(Id, 'text')
        clip_test = image_name.split(' ', 1)[0]
        if clip_test == "Clipboard":
            image_key = self.extract_image_from_clip(Id)
        else:
            image_key = self.extract_image_from_dict(Id)

        return image_key  # Will be None if an error

    def extract_image_from_dict(self, Id):
        """ Our key is 4 or 5 segments long comprised of dictionary keys """

        image_name = self.cd_tree.item(Id, 'text')
        medium_id = self.cd_tree.parent(Id)
        rel_id = self.cd_tree.parent(medium_id)
        release_id = self.get_mbz_id_for_rel_id(rel_id)  # embedded release_id

        image_data = None
        image_key = None
        i = 0                   # For pycharm unassigned warning
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
        self.background = self.resized_art.getpixel((3, 3))
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
        self.play_top.update_idletasks()

        '''

        self.cd_art_label.configure(image=self.cd_song_art)

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
        self.current_image_key = self.display_image(Id)
        if self.current_image_key in self.selected_image_keys:
            return False

        self.selected_image_keys.append(self.current_image_key)

    def unselect_image(self, Id):
        """ Unselect image. We can be called when image already unselected. """
        self.current_image_key = self.display_image(Id)
        if self.current_image_key not in self.selected_image_keys:
            return False

        self.selected_image_keys.remove(self.current_image_key)

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

        if self.selected_date is not None:
            # TODO: Prompt for release date
            messagebox.showinfo(title="Release date already selected",
                                message="Unselect the other release date first.",
                                icon='error', parent=self.cd_top)
            self.reverse_checkbox = True
            return False

        line = self.cd_tree.item(Id, 'text')
        release_date = line.split(' ', 3)[2]

        if release_date == "" or "?" in release_date:
            # When no release date it is manually inserted earlier as "????"
            # TODO: Prompt for release date testing.
            new_date = simpledialog.askstring("Release date error",
                                              "Blank dates cannot be used. Enter a release date",
                                              parent=self.cd_top)
            if new_date is None:
                self.reverse_checkbox = True
                return False
            else:
                release_date = new_date

        self.selected_date = release_date

    def unselect_date(self):
        """ Unselect release date """
        self.selected_date = None

    def select_medium(self, Id):
        """ Select medium
            Only one medium can be selected, prompt "Do you want to unselect?"
            Flag all songs as selected, even if manually unselected previously
            When self.selected_artist is "Various Artists" it's a compilation
        """
        if self.selected_medium is not None:
            if not Id == self.selected_medium:
                messagebox.showinfo(
                    parent=self.cd_top, title="Selection Error",
                    message="Another medium has already been selected.")
                self.reverse_checkbox = True
                return False

        # We are selecting this medium and all songs under it by default
        self.selected_medium = Id
        # Line 'score: 999   |  Artist: Joe Blow  |  Title: Getting Dough'
        rel_id = self.cd_tree.parent(Id)
        sep = "  |  "  # TODO: Make this global variable
        artist_str = self.cd_tree.item(rel_id, 'text').split(sep)[1]
        album_str = self.cd_tree.item(rel_id, 'text').split(sep)[2]
        self.selected_artist = artist_str.split(':', 1)[1].strip()
        self.is_compilation = self.selected_artist == "Various Artists" 
        # Filter title was missing : 1995-2008 so add ',1' to split.
        self.selected_album = album_str.split(':', 1)[1].strip()

    def unselect_medium(self, Id):
        """ Unselect medium
            Must be selected to qualify
            Flag all songs as unselected
        """
        if not Id == self.selected_medium:
            messagebox.showinfo(
                title="Selection Error", parent=self.cd_top,
                message="This medium is not selected.")

            return False

        # We are unselecting this medium and all songs under it by default
        self.selected_medium = None
        self.selected_artist = None
        self.selected_album = None

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
            messagebox.showinfo(title="Selection Error",
                                message="Song is not under the selected medium.",
                                icon='error', parent=self.cd_top)
            self.reverse_checkbox = True
            return False

    def unselect_song(self, Id):
        """ Unselect song. Programmatically set medium selection.
        """

        # Get our parent medium_id and if it is not equal to self.saved_medium_id
        # we have an error.
        parent_id = self.cd_tree.parent(Id)
        if not parent_id == self.selected_medium:
            messagebox.showinfo(
                title="Selection Error", parent=self.cd_top,
                message="Song is not under a selected medium.")
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
        self.scrollbox.delete('1.0', tk.END)    # Delete previous entries
        x = self.fmt                            # Menu bar format radiobutton
        self.scrollbox.insert("end", "Format:\t" + x)
        y = 100  # wav and flac are 100% quality
        if x == "oga":                          # Was "oga" selected?
            y = self.quality_var.get()          # Menu bar quality radiobutton
        self.scrollbox.insert("end", "\tQuality: " + str(y) + " %")
        z = self.naming                         # Menu bar naming radiobutton
        self.scrollbox.insert("end", "\tNaming: " + '"' + z + '"' + "\n")
        topdir = self.trg_var.get()             # Menu bar format target
        self.scrollbox.insert("end", "Target:\t" + topdir + "\n")

        if self.selected_artist:                # Artist name
            self.scrollbox.insert("end", "Artist:\t" +
                                  self.selected_artist + "\n")
        if self.selected_album:                 # Album name
            self.scrollbox.insert("end", "Album:\t" +
                                  self.selected_album + "\n")
        if self.selected_date:                  # Release date
            self.scrollbox.insert("end", "Date:\t" +
                                  self.selected_date + "\n")
        self.selected_tracks = 0                # Number tracks selected
        if self.selected_medium:                # Was this medium selected?
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
            self.scrollbox.insert("end", "Songs:")
            for track_id in self.cd_tree.get_children(self.selected_medium):
                tags = self.cd_tree.item(track_id, 'tags')
                if 'checked' in tags:  # Was this song selected?
                    os_name = self.os_song_format(
                        self.cd_tree.item(track_id, 'text'))
                    self.scrollbox.insert("end", "\t" + os_name + "\n")
                    self.selected_tracks += 1

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
                continue

            # noinspection PyTypeChecker
            t_file = io.BytesIO(image_data)
            original_art = Image.open(t_file)
            del t_file  # Delete object to save memory
            resized_art = original_art.resize(
                (175, 175), Image.ANTIALIAS)
            # print('resized_art done')
            # TODO: We rebuild art in ripping routine, do we need append below?
            self.rip_art.append(ImageTk.PhotoImage(resized_art))
            self.scrollbox.insert("end", '\nImage ' + str(i + 1) + ':\t')
            self.scrollbox.image_create("end", image=self.rip_art[i])
            self.scrollbox.insert("end", '\n')
        # ext.t_end('print')

        # apply the tag "red" to following word patterns
        pattern_list = ["Format:", "Quality:", "Naming:", "Artist:", "Album:",
                        "Musicbrainz ID:", "Medium:", "Songs:", "Image 1:",
                        "Image 2:", "Image 3:", "Image 4:", "Image 5", "Date:",
                        "Country:", "CD Tracks:", "Tracks selected:",
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
        """ Format song name as it will appear in operating system directory
            Set self.selected_title to use as metadata song name
        """
        offset_1 = 2    # Where the dash ("-") starts
        offset_2 = 4    # Where the song name starts

        if self.disc_count > 1:
            # Multi-disc medium have '#-' prepended to song name
            offset_1 = 4  # Dash stars later
            offset_2 = 6  # Song name starts later

        os_name = tree_name
        if self.naming == "99 ":
            # tree_name is "99 - Song name" force to "99 Song name"
            part1 = os_name[:offset_1]
            part2 = os_name[offset_2:]
            os_name = part1 + part2

        # HUGE PROBLEM: Why subtract 1 here and not use 1 less above?
        self.selected_title = os_name[offset_2 - 1:]  # For metadata song name
        os_name = os_name + '.' + self.fmt        # Add extension
        os_name = ext.legalize_song_name(os_name)  # Take out /, ?, :, . (not last .)
        #self.sqlOsFileName = os_name[offset_1:]  # Strip out 99 or 1-99
        #self.sqlOsFileName = self.sqlOsFileName[:-4]  # .wav, .oga, .flac
        return os_name  # os_name inserted into selection 


class ObsoleteCustomScrolledText(scrolledtext.ScrolledText):
    """A text widget with a new method, highlight_pattern()

            NOTE: This has been moved to toolkit.py

            AFTER TESTING NOT NEEDED, DELETE THIS Class

    example:

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
        expression according to TCL regular expression syntax.
        """

        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)

        count = tk.IntVar()
        while True:
            index = self.search(pattern, "matchEnd", "searchLimit",
                                count=count, regexp=regexp)
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
        """Remove the given tag to all text that matches the given pattern
        """

        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)

        count = tk.IntVar()
        while True:
            index = self.search(pattern, "matchEnd", "searchLimit",
                                count=count, regexp=regexp)
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

    def __init__(self, toplevel, thread=None):

        self.top_level = toplevel
        self.thread = thread

        self.total_scanned = 0
        self.missing_artwork = 0
        self.found_artwork = 0
        self.meta_data_updated = 0
        self.meta_data_unchanged = 0
        self.meta_dict = None

    def CheckArtwork(self, meta_dict):
        """ :param meta_dict: Key/Value Pairs of ID tags 
            :returns True if Song File has artwork, False if "Video" not found
        """
        if self.thread:
            self.thread()

        self.total_scanned += 1
        for key, value in meta_dict.iteritems():
            if key.startswith("STREAM"):
                if "Video:" in value:
                    self.found_artwork += 1
                    return True

        self.missing_artwork += 1
        return False

    def ChangedCounts(self, flag):
        """ :parameter flag: Can be True, False or None """
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
