#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: Pippim
License: GNU GPLv3
Source: This repository
Description: Global variables shared by all Pippim mserve modules
"""
from __future__ import print_function  # Must be first import
from __future__ import with_statement  # Error handling for file opens

# ==============================================================================
#
#       webscrape.py - Search and scrape internet for song lyrics
#
#       June 25 2023 - Use toolkit.uni_str(line)
#       July 13 2023 - Interface to/from mserve_config.py
#
# ==============================================================================

"""
Start with google search:   https://stackoverflow.com/a/43531098/6929343
Filtering:                  Skip youtube
Store results in:           g.TEMP_DIR + "mserve.scrape_list.txt"

Next get lyrics:            https://stackoverflow.com/a/63436536/6929343
Filtering:                  Include genius.com
Store results in:           g.TEMP_DIR + "mserve.scrape_lyrics.txt"

    TODO:

        Provide tkinter windows to display input, output and control selections

        A valid song should be less than 100 lines and each line should be less
        than 95 characters. Otherwise the result is just random.


"""

try:  # Python 3
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

# Python Standard Library
import sys
try:
    reload(sys)  # June 25, 2023 - Without these commands, os.popen() fails on OS
    sys.setdefaultencoding('utf8')  # filenames that contain unicode characters
except NameError:  # name 'reload' is not defined
    pass  # Python 3 already in unicode by default
#print("Python version:", sys.version)
import os
#import os.path  # July 13, 2023... Huh?
import json
import time
import re
from collections import namedtuple

# Dist-packages
import requests
from six.moves import urllib            # Python 2/3 compatibility library
from bs4 import BeautifulSoup

# Pippim modules
import global_variables as g
if g.USER is None:
    g.init()  # Always have to run when background job

import external as ext  # Time formatting routines
import image as img
import monitor
import sql
import toolkit
import message

# Web scraping song lyrics IPC file names
SCRAPE_CTL_FNAME = g.TEMP_DIR + 'mserve.scrape_ctl.json'
SCRAPE_LIST_FNAME = g.TEMP_DIR + 'mserve.scrape_list.txt'
SCRAPE_LYRICS_FNAME = g.TEMP_DIR + 'mserve.scrape_lyrics.txt'

# Names list is used in our code for human readable formatting
NAMES_LIST = ['Metro Lyrics', 'AZ Lyrics', 'Lyrics',
              'Lyrics Mode', 'Lets Sing It', 'Genius',
              'Musix Match', 'Lyrics Planet']

# Website list is used in webscrape.py for internet formatting
WEBSITE_LIST = ['www.metrolyrics.com', 'www.azlyrics.com', 'www.lyrics.com',
                'www.lyricsmode.com', 'www.letssingit.com', '//genius.com',
                'www.musixmatch.com', 'www.lyricsplanet.com']

# Empty control list (template)
CTL_LIST = [{} for _ in range(len(WEBSITE_LIST))]
# CTL_LIST = [ {}, {}, {}, {}, {}, {}, {}, {} ]

# If we try to print normally an error occurs when launched in background
# print("CTL_LIST:", CTL_LIST, file=sys.stderr)

# Empty control list dictionary element (template)
WS_DICT = {"rank": 0, "name": "", "website": "",
           "link": "", "score": 0, "flag": "", "lyrics": ""}
''' flag values: preference passed to webscrape.py. result passed to mserve
    preference:  1-8 try to get lyrics in this order, 'skip' = skip site
    result:      'found' lyrics returned. 'available' lyrics can be returned
                 'not found' no link or link is empty (eg artist but no lyrics)
'''

DEFAULT_LIST = [
    {"rank": 1, "name": "Megalobiz", "website": "www.megalobiz.com",
     "link": "", "score": 0, "flag": "", "lyrics": ""},
    {"rank": 2, "name": "Metro Lyrics", "website": "www.metrolyrics.com",
     "link": "", "score": 0, "flag": "", "lyrics": ""},
    {"rank": 3, "name": "AZ Lyrics", "website": "www.azlyrics.com",
     "link": "", "score": 0, "flag": "", "lyrics": ""},
    {"rank": 4, "name": "Lyrics", "website": "www.lyrics.com",
     "link": "", "score": 0, "flag": "", "lyrics": ""},
    {"rank": 5, "name": "Lyrics Mode", "website": "www.lyricsmode.com",
     "link": "", "score": 0, "flag": "", "lyrics": ""},
    {"rank": 6, "name": "Lets Sing It", "website": "www.letssingit.com",
     "link": "", "score": 0, "flag": "", "lyrics": ""},
    {"rank": 7, "name": "Genius", "website": "'//genius.com",
     "link": "", "score": 0, "flag": "", "lyrics": ""},
    {"rank": 8, "name": "Musix Match", "website": "www.musixmatch.com",
     "link": "", "score": 0, "flag": "", "lyrics": ""},
    {"rank": 9, "name": "Lyrics Planet", "website": "www.lyricsplanet.com",
     "link": "", "score": 0, "flag": "", "lyrics": ""}
]

BLACK_LIST = ['youtube', 'wikipedia', 'facebook', 'pinterest']

BLACK_LIST_FOUND = []
WHITE_LIST_FOUND = []
list_output = []
lyrics_output = []              # Was not defined global in scrape()

# Global search string
SEARCH = ""
MUSIC_ID = ""


class Results:
    """ Work in progress """
    def __init__(self):
        self.black_list_count = 0
        self.white_list_count = 0
        self.list = []
        self.result = namedtuple('Result', 'order, type, link')

    def add_blacklist(self):
        self.black_list_count += 1

    def add_whitelist(self):
        self.white_list_count += 1


results = Results()             # global class


def save_ctl():
    """
        CANCEL: webscrape has full access to sql to see what has been
                downloaded in the past.

        Save Control file containing list of dictionaries

        USED by mserve and webscrape.py
            mserve passes previous list of names with flags to scrape.
            webscrape.py passes back name of website that was scraped.
            webscrape.py passes names of websites that CAN BE scraped.
    """
    with open(SCRAPE_CTL_FNAME, "w") as ctl:
        ctl.write(json.dumps(CTL_LIST))


def load_ctl():
    """
        Return contents of CTL file or empty list of dictionaries
    """
    data = CTL_LIST
    if os.path.isfile(SCRAPE_CTL_FNAME):
        with open(SCRAPE_CTL_FNAME, "r") as ctl:
            data = json.loads(ctl.read())

    return data


def check_files(select='all'):
    """ NOT USED """
    if select == 'all' or select == 'list':
        if not os.path.isfile(SCRAPE_LIST_FNAME):
            return False

    if select == 'all' or select == 'lyrics':
        if not os.path.isfile(SCRAPE_LYRICS_FNAME):
            return False

    return True


def delete_files(select='all'):
    """ USED by mserve and webscrape.py """
    if select == 'all' or select == 'list':
        try:
            os.remove(SCRAPE_LIST_FNAME)
        except OSError:
            pass

    if select == 'all' or select == 'lyrics':
        try:
            os.remove(SCRAPE_LYRICS_FNAME)
        except OSError:
            pass


# TODO: Create SQL History with website and last time scraped. This way we can
#       cycle through names and not bombard a single site with quick requests.
#       At two seconds per site it will be ~15 seconds between requests, which
#       should satisfy most robot detectors.


MEGALOBIZ = METROLYRICS = AZLYRICS = LYRICS = LYRICSMODE = None
LETSSINGIT = GENIUS = MUSIXMATCH = LYRICSPLANET = None


def google_search(search):
    """ Get google search results for "song lyrics" + Artist + Song
        TODO: Accept parameter for which of 8 websites to focus on getting:
            1. Metrolyrics
            2. AZ Lyrics
            3. Lyrics.com
            4. LyricsMode
            5. Letsingit
            6. Genius
            7. Musixmatch
            8. LyricsPlanet
    """
    global WS_DICT, CTL_LIST
    global MEGALOBIZ, METROLYRICS, AZLYRICS, LYRICS, LYRICSMODE, LETSSINGIT
    global GENIUS, MUSIXMATCH, LYRICSPLANET, list_output

    # If we try to print normally an error occurs when launched in background
    # print("CTL_LIST start search:", CTL_LIST, file=sys.stderr)

    # print('requests header:', requests.utils.default_headers())
    # Avoid google robot detection
    # noinspection SpellCheckingInspection
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1)' + \
                 'AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14'
    headers = {'User-Agent': user_agent,
               'Accept': 'text/html,application/xhtml+xml,application/' +
                         'xml;q=0.9,image/webp,*/*;q=0.8'}
    # inspection SpellCheckingInspection

    hit_count = 100  # valid options 10, 20, 30, 40, 50, and 100
    #    page = requests.get(f"https://www.google.com/search?q={search}&num={results}")
    query = "https://www.google.com/search?q={search}&num={results}". \
        format(search=search, results=hit_count, headers=headers)
    # print('query:', query)

    # noinspection PyBroadException
    try:
        page = requests.get(query)
    except:
        list_output.append('Internet not available.')
        # print('Internet not available.')
        return

    soup = BeautifulSoup(page.content, "html5lib")
    # print('soup:', soup)
    links = soup.findAll("a")
    for link in links:
        link_href = link.get('href')
        if "url?q=" in link_href and "webcache" not in link_href:
            t = (link.get('href').split("?q=")[1].split("&sa=U")[0])
            # if 'youtube' in t or 'wikipedia' in t or 'facebook' in t \
            # or 'pinterest' in t:
            if any(s in t for s in BLACK_LIST):
                # print('skipping youtube, wikipedia, facebook & pinterest')
                # TODO: keep these but put in blacklist
                add_blacklist(t)
                continue
            else:
                list_output.append(t)
                add_whitelist(t)

            # TODO: look up in list and get ranking
            if 'www.metalobiz.com' in t:
                MEGALOBIZ = t
            if 'www.metrolyrics.com' in t:
                METROLYRICS = t
            if 'www.azlyrics.com' in t:
                AZLYRICS = t
            if 'www.lyrics.com' in t:
                LYRICS = t
            if 'www.lyricsmode.com' in t:
                LYRICSMODE = t
            if 'www.letssingit.com' in t:
                LETSSINGIT = t
            if '//genius.com' in t:  # Trap out //dekgenius.com
                GENIUS = t
            if 'www.musixmatch.com' in t:
                MUSIXMATCH = t
            if 'www.lyricsplanet.com' in t:  # Not sure if '//' or 'www.' prefix
                LYRICSPLANET = t

            #if 'www.lyricfind.com' in t:  # Try substitute

            # New method February 21/2021
            for i, website in enumerate(WEBSITE_LIST):
                if website in t:
                    # If we try to print normally an error occurs when launched in background
                    # print("\ni, website in t:", i, website, NAMES_LIST[i], t, file=sys.stderr, sep=" | ")
                    # noinspection PyDictCreation
                    WS_DICT = {}  # Reset dynamic link to earlier elements
                    WS_DICT['name'] = NAMES_LIST[i]
                    WS_DICT['website'] = website
                    WS_DICT['link'] = t
                    WS_DICT['flag'] = "available"
                    CTL_LIST[i] = WS_DICT
                    break

    # Save files
    with open(SCRAPE_LIST_FNAME, "w") as outfile:
        for line in list_output:
            outfile.write(line + "\n")

    # If we try to print normally an error occurs when launched in background
    # print("\nCTL_LIST after search:", CTL_LIST, file=sys.stderr)

    save_ctl()


def add_blacklist(text):
    global BLACK_LIST_FOUND
    BLACK_LIST_FOUND.append(text)


def add_whitelist(text):
    global WHITE_LIST_FOUND
    WHITE_LIST_FOUND.append(text)


def scrape(search):
    global lyrics_output
    if GENIUS:
        get_from_genius()  # TODO: June 25, 2023 now it is lyricfind.com

    # We didn't find anything in genius.com
    if len(lyrics_output) == 0:
        if MEGALOBIZ:
            get_from_megalobiz()

    # We didn't find anything in megalobiz.com
    if len(lyrics_output) == 0:
        if AZLYRICS:
            get_from_azlyrics()

    # We didn't find anything in azlyrics.com
    if len(lyrics_output) == 0:
        if METROLYRICS:
            get_from_metrolyrics()

    if len(lyrics_output) == 0:
        # We didn't find anything in genius.com or azlyrics.com
        lyrics_output.append('No lyrics found for: ' + search)
        lyrics_output.append('Popular sites search results:')

        if METROLYRICS:
            lyrics_output.append(METROLYRICS)
        if AZLYRICS:
            lyrics_output.append(AZLYRICS)
        if LYRICS:
            lyrics_output.append(LYRICS)
        if LYRICSMODE:
            lyrics_output.append(LYRICSMODE)
        if LETSSINGIT:
            lyrics_output.append(LETSSINGIT)
        if GENIUS:
            lyrics_output.append(GENIUS)
        if MUSIXMATCH:
            lyrics_output.append(MUSIXMATCH)
        if LYRICSPLANET:
            lyrics_output.append(LYRICSPLANET)

        lyrics_output.append('Or consider scraping following sites for lyrics:')
        for line in list_output:
            # Write possible lyrics websites as song lyrics to display
            lyrics_output.append(line)

    # Save file
    with open(SCRAPE_LYRICS_FNAME, "w") as outfile:
        for line in lyrics_output:
            outfile.write(toolkit.uni_str(line) + "\n")


def get_from_genius():
    """ Glitch Chis de Burgh Spaceman splits one line into three:

            And over
            a village
            he halted his craft

        Reason is HTML extra <span> and <br/> that should be ignored.
        Screenshot of code: 'beautiful soup fails .get_text.png'

[Verse 1: Chris De Burgh]
<br>
A spaceman came travelling on his ship from afar
<br>
<a href="/2172507/Chris-de-burgh-a-spaceman-came-travelling/Twas-light-years-of-time-since-his-mission-did-start"
class="ReferentFragmentdesktop__ClickTarget-sc-110r0d9-0 cehZkS"><span class="ReferentFragmentdesktop__Highlight-sc-110r0d9-1 jAzSMw">
'Twas light years of time since his mission did start</span></a>
<span tabindex="0" style="position:absolute;opacity:0;width:0;height:0;pointer-events:none;z-index:-1"></span>
<span><span tabindex="0" style="position:absolute;opacity:0;width:0;height:0;pointer-events:none;z-index:-1"></span>
<span tabindex="0" style="position:absolute;opacity:0;width:0;height:0;pointer-events:none;z-index:-1"></span></span>
<br>

And over <a href="/2172512/Chris-de-burgh-a-spaceman-came-travelling/A-village"
class="ReferentFragmentdesktop__ClickTarget-sc-110r0d9-0 cehZkS"><span class="ReferentFragmentdesktop__Highlight-sc-110r0d9-1 jAzSMw">
a village</span></a>
<span tabindex="0" style="position:absolute;opacity:0;width:0;height:0;pointer-events:none;z-index:-1"></span>
<span><span tabindex="0" style="position:absolute;opacity:0;width:0;height:0;pointer-events:none;z-index:-1"></span>
<span tabindex="0" style="position:absolute;opacity:0;width:0;height:0;pointer-events:none;z-index:-1"></span></span>
he halted his craft
<br>

<a href="/2172509/Chris-de-burgh-a-spaceman-came-travelling/And-it-hung-in-the-sky-like-a-star-just-like-a-star"
class="ReferentFragmentdesktop__ClickTarget-sc-110r0d9-0 cehZkS"><span class="ReferentFragmentdesktop__Highlight-sc-110r0d9-1 jAzSMw">
And it hung in the sky like a star, just like a star</span></a>
<span tabindex="0" style="position:absolute;opacity:0;width:0;height:0;pointer-events:none;z-index:-1"></span>
<span><span tabindex="0" style="position:absolute;opacity:0;width:0;height:0;pointer-events:none;z-index:-1"></span>
<span tabindex="0" style="position:absolute;opacity:0;width:0;height:0;pointer-events:none;z-index:-1"></span></span>
<br><br>

    """
    global lyrics_output

    url = GENIUS
    # noinspection PyBroadException
    try:
        soup = BeautifulSoup(requests.get(url).content, 'lxml')
        for tag in soup.select('div[class^="Lyrics__Container"], \
                               .song_body-lyrics p'):
            t = tag.get_text(strip=True, separator='\n')
            if t:
                lyrics_output.append(t)

            # Failed attempts at fixing Spaceman Came Travelling song
            # https://stackoverflow.com/a/17639192/6929343
            #t = tag.get_text()  # Gives one big lump of text
            #soup = BeautifulSoup(tag)
            #for linebreak in soup.find_all('br'):
            #    t = linebreak.extract()
            #    if t:
            #        lyrics_output.append(t)
    except:
        lyrics_output.append('Error occurred retrieving genius.com lyrics')
        lyrics_output.append(url)
        lyrics_output.append('Search String: ' + SEARCH)


def get_from_azlyrics():
    global lyrics_output

    url = AZLYRICS

    # noinspection PyBroadException
    try:
        html_page = urllib.request.urlopen(url)
        soup = BeautifulSoup(html_page, 'html.parser')
        html_pointer = soup.find('div', attrs={'class': 'ringtone'})
        # song_name = html_pointer.find_next('b').contents[0].strip()
        lyrics = html_pointer.find_next('div').text.strip()
        lyrics_output.append(lyrics)
    except:
        lyrics_output.append('Error occurred retrieving azlyrics.com lyrics')
        lyrics_output.append(url)
        lyrics_output.append('Search String: ' + SEARCH)


def get_from_metrolyrics():
    """ Load the lyrics from MetroLyrics. """
    from lxml import html
    global lyrics_output

    url = METROLYRICS
    page = requests.get(url)

    if page.status_code > 200:
        # raise TswiftError("No lyrics available for requested song")
        return

    # Forces utf-8 to prevent character mangling
    page.encoding = 'utf-8'

    tree = html.fromstring(page.text)
    try:
        lyric_div = tree.get_element_by_id('lyrics-body-text')
        verses = [c.text_content() for c in lyric_div.find_class('verse')]
    except KeyError:
        # raise "No lyrics available for requested song"
        return
    else:
        # Not sure what do do with following line just yet (Feb 21 2021)
        # lyrics = '\n\n'.join(verses)
        pass

    return verses


"""
<div id="lrc_54479852_member_box" class="lyrics_member_box">
    <div class="lyrics_title">
        <span class="related_media_page name" 
        title="Creed - My Sacrifice [HQ]" data-page="lrc/maker/Creed+-+My+Sacrifice+%5BHQ%5D.54479852" 
        style="cursor:pointer;">
            5059 - Creed - My Sacrifice [HQ]
                         [04:47.14]</span>
        <span class="datetime" title="Saturday, July 7th 2018, at 01:07:14 pm">3 years ago</span>
    </div>

    <div style="margin-top:10px;">
        <span class="text_reading">by</span>
            Guest
    </div>

    <div class="lyrics_options">
        <div style="margin:10px 0;text-align:left;font-size:14px;color:#444;">
            <div>
                <input id="lrc_54479852_keep_unused_lines" name="keep_unused_lines" type="checkbox" value="1">
                <label for="lrc_54479852_keep_unused_lines">Keep untagged brackets and blank lines?</label>
            </div>
            <div>
                <input id="lrc_54479852_show_lyrics_only" name="show_lyrics_only" type="checkbox" value="1">
                <label for="lrc_54479852_keep_unused_lines">Show Lyrics Only (without LRC tag)</label>
            </div>
        </div>
        <div>
            <span id="lrc_54479852_copier_message" class="success_message">Copied</span>
            <div id="lrc_54479852_copier" class="lrc_text_copier text_copier">
                <img src="https://www.megalobiz.com/pics/images/max20h/office_copy_icon.png" \
                alt="Office Copy Icon" title="Copy" width="20" height="20"><span class="reading_text">Copy</span>
            </div>

            <span class="reading_text text_copier"><a href="/lrc/maker?lrc=54479852">Edit Time [xx:yy.zz]</a></span>
            <span class="stats lrc_text_copier">x 111</span>

            <span class="stats lrc_text_copier text_copier">Views x 839</span>

            <span id="lrc_54479852_file_download" class="lyrics_button">Download</span>
            <span class="stats">x 239</span>
        </div>
    </div>


    <div class="lyricer_options">
        <span class="lyricer_info">LRC TIME [04:47.14] may not match your music. Click 
                <span class="bold_text">Edit Time</span> 
            above and in the LRC Maker &amp; \
            Generator page simply apply an offset (+0.8 sec, -2.4 sec, etc.)</span>
    </div>

    <div class="adsense_responsive_container">
        <!-- Responsive Links -->
        <ins class="adsbygoogle" style="margin:5px auto;display:block;min-height:160px;" \
            data-ad-client="ca-pub-6522515743514671" data-ad-slot="2271059873" data-ad-format="link">
        </ins>
        <script>
            (adsbygoogle = window.adsbygoogle || []).push({});
        </script>
    </div>

    <div id="lrc_54479852_details" class="lyrics_details entity_more_info">
                                    <span id="lrc_54479852_lyrics">[length:04:47.14]<br>
        [re:www.megalobiz.com/lrc/maker]<br>
        [ve:v1.2.3]<br>
        [00:33.09]Hello my friend<br>
        [00:34.59] we meet again<br>
        ...
        [04:20.53]hello again<br>
        [04:26.02]My sacrifice</span>
    </div>
</div>


</span>
        </div>
    </div>

                        </div>
                </div>

"""


def get_from_megalobiz():
    """ Song # 878 Creed - My Sacrifice

        Lyrics are split up into two lines versus one in Genius.com
        .LRC times are to 100th of a second
    """

    from lxml import html
    global lyrics_output

    url = MEGALOBIZ
    """Load the lyrics from MetroLyrics."""
    page = requests.get(url)

    if page.status_code > 200:
        # raise TswiftError("No lyrics available for requested song")
        return

    # Forces utf-8 to prevent character mangling
    page.encoding = 'utf-8'

    tree = html.fromstring(page.text)

    try:
        lyric_div = tree.get_element_by_id('lyrics_details entity_more_info')
        verses = [c.text_content() for c in lyric_div.find_class('verse')]
    except KeyError:
        # raise "No lyrics available for requested song"
        return
    else:
        # Not sure what do do with following line just yet (Feb 21 2021)
        # lyrics = '\n\n'.join(verses)
        pass

    return verses


root = None


def no_parameters():
    """ Called with no parameters """
    global root
    sql.open_db()
    root = tk.Tk()  # Create "very top" toplevel for all top levels
    root.withdraw()  # Remove default window because we have treeview
    # background From: https://stackoverflow.com/a/11342481/6929343
    default_bg = root.cget('bg')
    print('default_bg:', default_bg)  # d9d9d9 It's a little bright

    ''' Set font style for all fonts including tkSimpleDialog.py '''
    img.set_font_style()  # Make messagebox text larger for HDPI monitors
    ''' Set program icon in taskbar '''
    img.taskbar_icon(root, 64, 'black', 'green', 'red', char='W')

    ''' console splash message '''
    print(r'  ######################################################')
    print(r' //////////////                            \\\\\\\\\\\\\\')
    print(r'<<<<<<<<<<<<<<   webscrape.py - Get Lyrics  >>>>>>>>>>>>>>')
    print(r' \\\\\\\\\\\\\\                            //////////////')
    print(r'  ######################################################')

    HistoryTree()  # Build treeview of sql history

    root.mainloop()  # When splash screen calls us there is mainloop


# ==============================================================================
#
#       HistoryTree class - Define lib (library of Message Headers)
#
# ==============================================================================


class HistoryTree:
    """ Create self.his_tree = tk.Treeview() via CheckboxTreeview()

        Resizeable, Scroll Bars, select songs, play songs.

        If toplevel is not None then it is the splash screen to destroy.

    """

    def __init__(self, sbar_width=12):

        # Define self. variables in backups() where play_top frame is used.
        self.bup_top = None  # Toplevel for Backups
        self.bup_top_is_active = None  # Is backups top level open?
        self.bup_view = None  # Treeview using data dictionary
        self.bup_view_btn1 = None
        self.bup_view_btn2 = None
        self.bup_view_btn3 = None
        self.bup_view_btn4 = None
        self.bup_view_btn5 = None
        self.bup_view_btn6 = None
        self.bup_view_btn7 = None
        self.bup_search = None  # Searching for trash, etc?

        self.hdr_top = None  # Toplevel for gmail message header
        self.hdr_top_is_active = False  # Displaying gmail message header?
        self.scrollbox = None  # Holds pretty print dictionary

        ''' HistoryTree Instances '''
        self.view = None  # = lib_view or bup_view
        self.region = None  # 'heading', 'separator' or 'cell'
        self.bup_gen = None  # Backup generations
        self.subject_list = []  # GMAIL_SUBJECT.split('!')
        self.view_iid = None

        ''' get parameters in SQL setup by mserve '''
        if SEARCH != "":
            now = time.time()
            last_time = sql.hist_last_time('scrape', 'parm')
            if last_time is None:
                last_time = now
            hist_row = sql.hist_get_row(sql.HISTORY_ID)
            lag = now - last_time
            if lag > 1.0:
                print('It took more than 1 second for webscrape to start:', lag)
            else:
                print('webscrape start up time from mserve:', lag)
                pass
            print(hist_row)

        ''' TODO: Relocate dtb '''
        dtb = message.DelayedTextBox(title="Building history table view",
                                     toplevel=None, width=1000)

        # If we are started by splash screen get object, else it will be None
        # self.splash_toplevel = toplevel
        self.splash_toplevel = tk.Toplevel()

        self.splash_removed = False  # Did we remove splash screen?

        # Create our tooltips pool (hover balloons)
        self.tt = toolkit.ToolTips()

        ''' Create toplevel and set program icon in taskbar '''
        self.his_top = tk.Toplevel()
        self.his_top.title("SQL History Table - webscrape")
        img.taskbar_icon(self.his_top, 64, 'black', 'green', 'red', char='W')

        ''' Initial size of Window 75% of HD monitor size '''
        _w = int(1920 * .75)
        _h = int(1080 * .75)
        _root_xy = (3800, 200)  # Temporary hard-coded coordinates

        ''' Mount window at popup location '''
        self.his_top.minsize(width=g.WIN_MIN_WIDTH, height=g.WIN_MIN_HEIGHT)
        # self.his_top.geometry('%dx%d+%d+%d' % (_w, _h, _root_xy[0], _root_xy[1]))
        geom = monitor.get_window_geom('history')
        self.his_top.geometry(geom)

        self.his_top.configure(background="Gray")
        self.his_top.columnconfigure(0, weight=1)
        self.his_top.rowconfigure(0, weight=1)

        ''' Create frames '''
        master_frame = tk.Frame(self.his_top, bg="olive", relief=tk.RIDGE)
        master_frame.grid(sticky=tk.NSEW)
        master_frame.columnconfigure(0, weight=1)
        master_frame.rowconfigure(0, weight=1)

        ''' Create treeview '''
        history_dict = sql.history_treeview()
        columns = ["time", "type", "action", "master", "detail", "target",
                   "size", "count", "seconds", "music_id", "comments"]
        """ FIELDS NOT SHOWN:
            ("column", "row_id"), ("heading", "Row ID"), ("sql_table", "History"),
            ("column", "user"), ("heading", "User"), ("sql_table", "History"),
            ("column", "delete_on"), ("heading", "Delete On"), ("sql_table", "calc"),
            ("column", "reason"), ("heading", "Reason"), ("sql_table", "calc"),

        """
        toolkit.select_dict_columns(columns, history_dict)

        self.his_view = toolkit.DictTreeview(
            history_dict, self.his_top, master_frame, columns=columns,
            sbar_width=sbar_width)

        # toolkit.print_dict_columns(history_dict)

        '''
                    B I G   T I C K E T   E V E N T

        Create Treeview item list with NO songs selected YET. '''
        self.manually_checked = False  # Used for self.reverse/self.toggle
        self.populate_his_tree(dtb)

        ''' Treeview Buttons '''
        frame3 = tk.Frame(master_frame, bg="Blue", bd=2, relief=tk.GROOVE,
                          borderwidth=g.BTN_BRD_WID)
        frame3.grid_rowconfigure(0, weight=1)
        frame3.grid_columnconfigure(0, weight=0)
        frame3.grid(row=1, column=0, sticky=tk.NW)

        ''' Global variables of active children '''
        self.play_top = None  # Backup server selected headers
        self.play_top_is_active = False  # Playing songs window open?

        ''' ✘ Close Button ✘ ✔ '''
        self.his_top.bind("<Escape>", self.quit)
        self.his_top.protocol("WM_DELETE_WINDOW", self.quit)
        self.close_text = "✘ Close"  # Variable button text
        self.his_tree_btn1 = tk.Button(frame3, text=self.close_text,
                                       width=g.BTN_WID - 2, command=self.quit)
        self.his_tree_btn1.grid(row=0, column=0, padx=2)
        # if self.refresh_play_top:
        #    thread = self.refresh_play_top
        # else:
        #    thread = None
        self.tt.add_tip(self.his_tree_btn1,
                        "Close webscrape and any windows webscrape opened.")

        ''' ⎘ Backups - Display backup message archives '''
        self.backup_text = "⎘ Backups"  # &#x2398 = ⎘
        self.his_tree_btn2 = tk.Button(frame3, text=self.backup_text,
                                       width=g.BTN_WID, command=self.save_items)
        self.his_tree_btn2.grid(row=0, column=1, padx=2)
        self.tt.add_tip(self.his_tree_btn2, "Display backups in Gmail.")

        ''' Save button '''
        # Floppy Disk U+1F4BE 💾  Hard Disk U+1F5B4 🖄
        self.save_text = "💾  Save view"  # save songs window is opened.
        self.his_tree_btn3 = tk.Button(frame3, text=self.save_text,
                                       width=g.BTN_WID - 1, command=self.save_items)
        self.his_tree_btn3.grid(row=0, column=2, padx=2)
        self.tt.add_tip(self.his_tree_btn3, "Save treeview column order and widths.")

        ''' Load button '''
        self.load_text = "💾  Load view"  # Load songs window is opened.
        self.his_tree_btn4 = tk.Button(frame3, text=self.load_text,
                                       width=g.BTN_WID - 1, command=self.load_items)
        self.his_tree_btn4.grid(row=0, column=3, padx=2)
        self.tt.add_tip(self.his_tree_btn4, "Load treeview column order and widths.")

        ''' Refresh Treeview Button u  1f5c0 🗀 '''
        ''' 🗘  Update differences Button u1f5d8 🗘'''
        self.rebuild_text = "🗘 Refresh history"  # Rebuild HistoryTree
        self.his_tree_btn5 = tk.Button(frame3, text=self.rebuild_text,
                                       width=g.BTN_WID - 1, command=self.refresh_his_tree)
        self.his_tree_btn5.grid(row=0, column=4, padx=2)
        self.tt.add_tip(self.his_tree_btn5,
                        "Refresh history view with current changes.")

        ''' U+1F50D LEFT-POINTING MAGNIFYING GLASS (🔍) Search '''
        self.search_text = "🔍  Search"
        self.his_tree_btn6 = tk.Button(frame3, text=self.search_text,
                                       width=g.BTN_WID - 2, command=self.string_search)
        self.his_tree_btn6.grid(row=0, column=5, padx=2)
        self.tt.add_tip(self.his_tree_btn6, "Search word(s) in any column.")

        ''' Colors for tags '''
        self.ignore_item = None
        self.his_view.tree.tag_configure('menu_sel', foreground='Red')

        ''' Refresh last played 999 ago, every minute '''
        self.his_top_is_active = True  # Tell refresh_items() to run
        self.last_inotify_time = None  # Last time bubble message sent
        self.refresh_items()  # Update elapsed play time

        ''' Menu bars: File, Edit, View, Search, About '''
        mb = tk.Menu(self.his_top)
        file_bar = tk.Menu(mb, tearoff=0)
        file_bar.add_command(label="New Backup Set", font=(None, g.MED_FONT),
                             command=lambda: self.loc_add_new(caller='Drop',
                                                              mode='Add'))
        file_bar.add_command(label="Discover backups",
                             font=(None, g.MED_FONT),
                             command=lambda: self.loc_open_play(caller='Drop',
                                                                mode='Open'))

        file_bar.add_separator()
        file_bar.add_command(label="Restart", font=(None, g.MED_FONT),
                             command=self.restart)
        file_bar.add_command(label="Exit", font=(None, g.MED_FONT),
                             command=self.quit)

        mb.add_cascade(label="File", menu=file_bar, font=(None, g.MED_FONT))

        # Edit Menu - Edit Location
        edit_bar = tk.Menu(mb, tearoff=0)
        edit_bar.add_command(label="Edit Backup Set", font=(None, g.MED_FONT),
                             command=lambda: self.loc_edit(caller='Drop',
                                                           mode='Edit'))
        edit_bar.add_command(label="Compare Backups", font=(None, g.MED_FONT),
                             command=lambda: self.loc_compare(caller='Drop',
                                                              mode='Compare'))
        edit_bar.add_command(label="Forget Backup Set", font=(None, g.MED_FONT),
                             command=lambda: self.loc_forget(caller='Drop',
                                                             mode='Forget'))

        mb.add_cascade(label="Edit", menu=edit_bar, font=(None, g.MED_FONT))

        # View menu - Song order (strip track and extension)
        view_bar = tk.Menu(mb, tearoff=0)
        view_bar.add_command(label="Show Backups", font=(None, g.MED_FONT),
                             command=lambda: self.backups)

        mb.add_cascade(label="View", menu=view_bar, font=(None, g.MED_FONT))

        # Search menu - search by words in any order
        # About Menu - Need author name?

        self.his_top.config(menu=mb)
        dtb.close()  # Close our startup messages dtb

        ''' Treeview select item - custom select processing '''
        toolkit.MoveTreeviewColumn(self.his_top, self.his_view.tree,
                                   row_release=self.his_button_3_click)
        self.his_view.tree.bind("<Button-3>", self.his_button_3_click)

        ''' Load last selections and begin playing with last song '''
        self.saved_selections = []
        self.load_last_selections()

        ''' Remove splash screen if we were called with it. '''
        if self.splash_toplevel:
            self.splash_toplevel.withdraw()  # Remove splash screen
            self.splash_removed = True  # No more splash screen!

        ''' When load_last_selections() ends we need to enter idle loop
            until self.quit() is called.
        '''
        while self.his_top:
            # Refresh every 50 ms
            self.his_top.update()
            if not self.his_top:
                # self.quit() has set to None
                break
            self.tt.poll_tips()
            self.his_top.after(50)

    def populate_his_tree(self, delayed_textbox):

        """ Stuff SQL header rows into treeview
        """

        sql.hist_cursor.execute("SELECT * FROM History INDEXED BY TimeIndex\
                                ORDER BY Time DESC")
        rows = sql.hist_cursor.fetchall()

        self.insert_view_line(self.his_view, rows, delayed_textbox)

    def insert_view_line(self, dd_view, rows, delayed_textbox, test=None):
        """ Stuff SQL header rows into treeview

            Used for populate_lib_view and populate_bup_view
        """

        for i, sql_row in enumerate(rows):

            row = dict(sql_row)
            rowId = row['Id']  # Used for treeview iid

            if test is not None:
                if not test(row):
                    dd_view.attached[rowId] = None  # Skipped
                    continue

            try:
                # NOTE: .insert for view not identical to tree!
                dd_view.insert("", dict(row), iid=rowId, tags="unchecked")
                dd_view.attached[rowId] = True  # row is attached to view
            except tk.TclError:

                # Character out of TCL displayable range or: x0 to xFF FF
                r = dict(row)  # 'sqlite3.row' doesn't allow item assignment
                r['Subject'] = self.normalize_tcl(r['Subject'])
                r['Snippet'] = self.normalize_tcl(r['Snippet'])
                # TODO - Update database with changes
                # print('subject:', subject)

                dd_view.insert("", dict(r), iid=rowId, tags="unchecked")
                dd_view.attached[rowId] = True  # row is attached to view

            ''' dtb_line displays only if lag experienced  '''
            dtb_line = row['Type'] + " - " + row['Action'] + \
                " - " + row['SourceMaster']

            if delayed_textbox.update(dtb_line):
                # delayed_textbox returns true only when visible otherwise
                # we are in quiet mode because not enough time has passed.
                dd_view.tree.see(rowId)
                dd_view.tree.update()

        # Display top row: https://stackoverflow.com/a/66035802/6929343
        children = dd_view.tree.get_children()
        if children:
            dd_view.tree.see(children[0])

    @staticmethod
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
            else:
                new_s += '?'

        return new_s

    def his_button_3_click(self, event):

        """ Left button clicked to drill down on library treeview line.
            Short click to retrieve and display history row.
            be moved in the treeview.
        """
        self.view = self.his_view
        self.common_button_3(event, self.his_view)

    def bup_button_3_click(self, event):

        """ Left button clicked to drill down on Backups treeview line.
        """

        self.view = self.bup_view
        self.common_button_3(event, self.bup_view)

    def common_button_3(self, event, view):
        """ Right button clicked in Library or Backups treeview.

            If clicked on a row then use message header dictionary to
            pretty format history details.

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
        self.region = self.view.tree.identify("region", event.x, event.y)
        if self.region == 'separator':
            # TODO adjust stored column widths
            return

        self.view = view

        # From: https://stackoverflow.com/a/62724993/6929343
        if self.region == 'heading':
            column_number = view.tree.identify_column(event.x)  # returns '#?'
            self.create_window('Data Dictionary for column: ' + column_number,
                               900, 450)  # width, height - July 27/22 make wider.
            column_name = view.columns[int(column_number.replace('#', '')) - 1]
            column_dict = toolkit.get_dict_column(column_name, view.tree_dict)
            #view_column = sql.PrettyHistory(None, column_dict)
            #view_column.tkinter_display(self.scrollbox)  # May 1, 2023 updated
            view_column = sql.PrettyTreeHeading(column_dict)
            view_column.scrollbox = self.scrollbox
            # Document self.scrollbox
            sql.tkinter_display(view_column)
            return

        # At this point only other region is 'cell'

        self.view_iid = view.tree.identify_row(y)
        # Color the row 'red'.
        tags = self.view.tree.item(self.view_iid)['tags']  # Append 'menu_sel' tag
        if "menu_sel" not in tags:
            tags.append("menu_sel")
            self.view.tree.item(self.view_iid, tags=tags)
        self.view.tree.see(self.view_iid)  # Ensure message is visible

        values = view.tree.item(self.view_iid, "values")
        sql_row_id = view.column_value(values, "row_id")
        if sql_row_id is None:
            # Should never happen because row_id is key field
            # always included even if not displayed.
            print('webscrape.py common_button_3() row_id is None')
            return

        pretty = sql.PrettyHistory(sql_row_id)

        ''' Place Window top-left of parent window with PANEL_HGT padding
            Lifted from: ~/mserve/encoding.py
        '''
        self.create_window("History row - webscrape", 1400, 575)
        pretty.scrollbox = self.scrollbox

        # pretty class dictionary display method
        sql.tkinter_display(pretty)

    def create_window(self, title, width, height):

        """ Place Window top-left of parent window with PANEL_HGT padding
            Lifted from: ~/mserve/encoding.py

            TODO: Instead of parent guessing width, height it would be nice
                  to pass a maximum and reduce size when text box has extra
                  white space.
                  
                  IDENTICAL to bserve.py. Consider module.

        """
        if self.hdr_top is not None:
            self.hdr_top.lift()
            return

        self.hdr_top = tk.Toplevel()
        self.hdr_top_is_active = True

        xy = (self.his_top.winfo_x() + g.PANEL_HGT,
              self.his_top.winfo_y() + g.PANEL_HGT)
        self.hdr_top.minsize(width=g.BTN_WID * 10, height=g.PANEL_HGT * 4)
        # TODO: Geometry too large for a single treeview column dictionary
        #       Just about right for a gmail message pretty header
        self.hdr_top.geometry('%dx%d+%d+%d' % (width, height, xy[0], xy[1]))
        self.hdr_top.title(title)
        self.hdr_top.configure(background="Gray")
        self.hdr_top.columnconfigure(0, weight=1)
        self.hdr_top.rowconfigure(0, weight=1)

        ''' Set program icon in taskbar '''
        img.taskbar_icon(self.hdr_top, 64, 'black', 'green', 'red', char='W')

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
                 "\tRun in Terminal: 'webscrape.py' and check for errors.\n\n" +
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

        self.scrollbox.config(tabs=("5m", "80m", "106m"))
        self.scrollbox.tag_configure("margin", lmargin1="5m", lmargin2="80m")
        # Fix Control+C  https://stackoverflow.com/a/64938516/6929343
        self.scrollbox.bind("<Button-1>", lambda event: self.scrollbox.focus_set())

    # noinspection PyUnusedLocal
    def pretty_close(self, *args):
        if self.hdr_top is None:
            return
        self.tt.close(self.hdr_top)  # Close tooltips under top level
        self.scrollbox.unbind("<Button-1>")
        self.hdr_top_is_active = False
        self.hdr_top.destroy()
        self.hdr_top = None

        # Reset color to normal in treeview line
        tags = self.view.tree.item(self.view_iid)['tags']  # Remove 'menu_sel' tag
        if "menu_sel" in tags:
            tags.remove("menu_sel")
            self.view.tree.item(self.view_iid, tags=tags)

    def bup_calc_to_pretty(self, pretty_dict):
        """ Add calculated fields from BackupGenerations and date matrix """

        values = self.view.tree.item(self.view_iid)['values']
        pretty_dict['delete_on'] = self.view.column_value(values, 'delete_on')
        pretty_dict['reason'] = self.view.column_value(values, 'reason')
        pretty_dict['row_id'] = self.view.column_value(values, "row_id")

        date_matrix = self.view.column_value(values, "date_matrix")
        pretty_dict['date_matrix'] = date_matrix
        dm = sql.DateMatrix()
        dm.use_string(date_matrix)
        # dm = sql.DateMatrix.use_string(date_matrix)
        #   TypeError: unbound method use_string() must be called with
        # DateMatrix instance as first argument (got unicode instance instead)

        pretty_dict['this_date'] = unicode(dm.this)
        pretty_dict['we_date'] = unicode(dm.we)
        we_row_id = self.bup_gen.message_for_date(
            self.bup_gen.weeks, dm.we)
        pretty_dict['we_row_id'] = unicode(we_row_id)

        pretty_dict['me_date'] = unicode(dm.me)
        me_row_id = self.bup_gen.message_for_date(
            self.bup_gen.months, dm.me)
        pretty_dict['me_row_id'] = unicode(me_row_id)

        pretty_dict['ye_date'] = unicode(dm.ye)
        ye_row_id = self.bup_gen.message_for_date(
            self.bup_gen.years, dm.ye)
        pretty_dict['ye_row_id'] = unicode(ye_row_id)

        # Test to ensure gmail message subject matches backup set
        # Note identical code in bserve.py and sql.py, consider function
        subject = self.view.column_value(values, "subject")
        pretty_dict['subject'] = subject
        backup_in_subject = False
        for s in self.subject_list:
            if s in subject:
                backup_in_subject = True
                break
        pretty_dict['backup_in_subject'] = unicode(backup_in_subject)

        labels = self.view.column_value(values, "labels")
        pretty_dict['labels'] = labels
        backup_in_label = False
        if BACKUP_LABEL in labels:
            backup_in_label = True
        pretty_dict['backup_in_label'] = unicode(backup_in_label)

        already_trashed = False
        if "trash" in labels.lower():
            already_trashed = True
        pretty_dict['already_trashed'] = unicode(already_trashed)

    def lib_popup(self, *args):
        pass

    # noinspection PyUnusedLocal
    def quit(self, *args):

        # Last known window position for message library, saved to SQL
        last_history_geom = monitor.get_window_geom_string(
            self.his_top, leave_visible=False)
        monitor.save_window_geom('history', last_history_geom)

        # Last known window position for message backups, saved to SQL
        if self.bup_top_is_active is True:
            self.bup_close()

        # TODO: Save treeview column orders and widths to SQL history.

        sql.close_db()
        self.his_top = None
        # root.after(100)
        root.destroy()

    # noinspection PyUnusedLocal
    def restart(self, *args):
        self.quit()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def save_items(self):
        pass

    def load_items(self):
        pass

    def refresh_items(self):
        pass

    def new_items(self):
        pass

    def append_items(self):
        pass

    def refresh_his_tree(self):
        """ Reload sql table """

        self.his_view.tree.delete(*self.his_view.tree.get_children())
        ''' TODO: Relocate dtb '''
        dtb = message.DelayedTextBox(title="Building history table view",
                                     toplevel=None, width=1000)
        self.populate_his_tree(dtb)
        print('Refresh History Table')
        print('Before:', 0)
        print('After:', 0)

    def string_search(self):
        """ Search all columns for string
        """
        toolkit.SearchText(self.his_view)

    def rotate_backups(self):
        """ Rotate Yearly, Monthly, Weekly, Daily backups.
        """

        total_size = 0
        row_count = 0
        already_trashed_count = 0

        now = str(datetime.date.today())
        for iid in self.bup_view.tree.get_children():
            # Loop through all rows in treeview
            values = self.bup_view.tree.item(iid, "values")
            delete_on = self.bup_view.column_value(values, "delete_on")
            if delete_on > now:
                continue

            row_count += 1
            size = self.bup_view.column_value(values, "size")
            labels = self.bup_view.column_value(values, "labels")
            labels_list = sql.label_string_to_list(labels)
            for label in labels_list:
                if label == "TRASH":
                    already_trashed_count += 1
                    continue

            new_labels_list = ["TRASH"]
            new_labels_list.extend(labels_list)
            new_labels = sql.label_list_to_string(new_labels_list)
            self.bup_view.update_column(iid, 'labels', new_labels)
            sql.message_update_labels(iid, new_labels)

            int_size = int(size.replace(',', ''))
            total_size += int_size
            self.bup_view.tree.tk.call(self.bup_view.tree, "tag",
                                       "remove", "highlight")
            self.bup_view.tree.see(iid)
            self.bup_view.tree.tk.call(self.bup_view.tree, "tag",
                                       "add", "highlight", iid)
            self.bup_view.toplevel.update_idletasks()
            self.gma.trash_message(iid)
            '''
            # Testing purposes just delete first 10
            if row_count < 10:
                self.gma.trash_message(iid)
            else:
                # Simulate delay for trashing message
                self.bup_view.toplevel.after(33)
            '''

        text = "Total size:  " + "{:,}".format(total_size) + "\n" + \
               "Row count:  " + "{:,}".format(row_count)

        message.ShowInfo(self.bup_view.toplevel, "Backups trashed", text)

    def load_last_selections(self):
        pass

    '''
    def tree_title__add(self, ndx, val):
        """ Add a value to single index.
            Not efficient but created for conformity with other add functions.
        """
        self.his_top_totals[ndx] = self.his_top_totals[ndx] + add_list[i]
    '''


def main():
    global SEARCH, MUSIC_ID, CTL_LIST

    delete_files()
    CTL_LIST = load_ctl()

    if (len(sys.argv)) == 3:
        # Caller is mserve
        SEARCH = sys.argv[1]
        MUSIC_ID = sys.argv[2]
    else:
        # Called from command line
        no_parameters()
        return

    SEARCH = u' '.join(('song lyrics ', SEARCH)).encode('utf-8')
    google_search(SEARCH)
    scrape(SEARCH)  # Parameter overridden when GENIUS <> ""

    # https://stackoverflow.com/a/47420863/6929343
    # Error goes away when print() is removed


if __name__ == "__main__":
    main()

# End of webscrape.py
