#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
#
#       scrape.py - Scrape the Internet
#
# ==============================================================================

"""
Start with google search:   https://stackoverflow.com/a/43531098/6929343
Filtering:                  Skip youtube
Store results in:           /run/user/1000/mserve.scrape_list.txt

Next get lyrics:            https://stackoverflow.com/a/63436536/6929343
Filtering:                  Include genius.com
Store results in:           /run/user/1000/mserve.scrape_lyrics.txt

    TODO:

        Provide tkinter windows to display input, output and control selections

        A valid song should be less than 100 lines and each line should be less
        than 95 characters. Otherwise the result is just random.


"""

from __future__ import print_function  # Must be first import
from __future__ import with_statement  # Error handling for file opens

# from __future__ import unicode_literals     # Unicode errors fix
# Above causes error on save icon utf-8
# _tkinter.TclError: character U+1f4be is above the range (U+0000-U+FFFF) allowed by Tcl

try:
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

import sys
import os
import os.path
import json
import time

reload(sys)
sys.setdefaultencoding('utf8')

import requests
from six.moves import urllib            # Python 2/3 compatibility library
from bs4 import BeautifulSoup
import re
from operator import itemgetter         # To sort dictionary list by order
from operator import attrgetter         # To sort namedtuple list by order
from collections import namedtuple      # For Result=score, type, link
from collections import OrderedDict     # For treeview data dictionary

import global_variables as g
import external as ext  # Time formatting routines
import image as img
import monitor
import sql
import toolkit
import message

# Web scraping song lyrics IPC file names
SCRAPE_CTL_FNAME = '/run/user/1000/mserve.scrape_ctl.json'
SCRAPE_LIST_FNAME = '/run/user/1000/mserve.scrape_list.txt'
SCRAPE_LYRICS_FNAME = '/run/user/1000/mserve.scrape_lyrics.txt'

# Names list is used in our code for human readable formatting
NAMES_LIST = ['Metro Lyrics', 'AZ Lyrics', 'Lyrics',
              'Lyrics Mode', 'Lets Sing It', 'Genius',
              'Musix Match', 'Lyrics Planet']

# Website list is used in scrape.py for internet formatting
WEBSITE_LIST = ['www.metrolyrics.com', 'www.azlyrics.com', 'www.lyrics.com',
                'www.lyricsmode.com', 'www.letssingit.com', '//genius.com',
                'www.musixmatch.com', 'www.lyricsplanet.com']

# Empty control list (template)
CTL_LIST = [{} for _ in range(len(WEBSITE_LIST))]
# CTL_LIST = [ {}, {}, {}, {}, {}, {}, {}, {} ]

# If we try to print normally an error occurs when launched in background
# print("CTL_LIST:", CTL_LIST, file=sys.stderr)

# Empty control list dictionary element (template)
WS_DICT = {"rank": 0, "name": "", "website": "", "link": "",
           "time": 0.0, "score": 0, "flag": "", "html": "", "lyrics": ""}
''' rank:       User defined preference to select websites for lyrics.
    name:       Website name in descriptive format.
    website:    Website address in www. or // format.
    link:       Google search result link.
    time:       Time it took to scrape website for lyrics. > 1 second usually error.
    score:      Score assigned based on quality of lyrics found. 0 = No lyrics.
    flag:       Not used.
    html:       Raw HTML page retrieved using google search result.
    lyrics:     Filtered lyrics extracted from HTML page.
'''

''' When no SQL list exists use DEFAULT_LIST '''
DEFAULT_LIST = [
    {"rank": 1, "name": "Megalobiz", "website": "www.megalobiz.com",
     "link": "", "time": 0.0, "score": 0, "flag": "", "html": "", "lyrics": ""},
    {"rank": 2, "name": "Metro Lyrics", "website": "www.metrolyrics.com",
     "link": "", "time": 0.0, "score": 0, "flag": "", "html": "", "lyrics": ""},
    {"rank": 3, "name": "AZ Lyrics", "website": "www.azlyrics.com",
     "link": "", "time": 0.0, "score": 0, "flag": "", "html": "", "lyrics": ""},
    {"rank": 4, "name": "Lyrics", "website": "www.lyrics.com",
     "link": "", "time": 0.0, "score": 0, "flag": "", "html": "", "lyrics": ""},
    {"rank": 5, "name": "Lyrics Mode", "website": "www.lyricsmode.com",
     "link": "", "time": 0.0, "score": 0, "flag": "", "html": "", "lyrics": ""},
    {"rank": 6, "name": "Lets Sing It", "website": "www.letssingit.com",
     "link": "", "time": 0.0, "score": 0, "flag": "", "html": "", "lyrics": ""},
    {"rank": 7, "name": "Genius", "website": "//genius.com",
     "link": "", "time": 0.0, "score": 0, "flag": "", "html": "", "lyrics": ""},
    {"rank": 8, "name": "Musix Match", "website": "www.musixmatch.com",
     "link": "", "time": 0.0, "score": 0, "flag": "", "html": "", "lyrics": ""},
    {"rank": 9, "name": "Lyrics Planet", "website": "www.lyricsplanet.com",
     "link": "", "time": 0.0, "score": 0, "flag": "", "html": "", "lyrics": ""}
]

BLACK_LIST = ['youtube', 'wikipedia', 'facebook', 'pinterest']

BLACK_LIST_COUNT = 0
WHITE_LIST_COUNT = 0
list_output = []
lyrics_output = []              # Was not defined global in scrape()

# Global search string
SEARCH = ""
MUSIC_ID = ""


# noinspection PyArgumentList
class Results:
    def __init__(self):
        self.blacklist_count = 0
        self.whitelist_count = 0
        # TODO: Get configuration from SQL History Table
        # Pretend we didn't get list from SQL
        if True is True:
            self.cfg_list = DEFAULT_LIST
        self.cfg_index = None
        self.cfg_dict = WS_DICT
        self.res_list = []
        self.Result_nt = namedtuple('Result', 'order, type, link')
        self.result = self.Result_nt(order=0, type="white", link='')

    def add_blacklist(self, link):
        self.blacklist_count += 1
        order = 1000 - self.blacklist_count
        self.result = self.Result_nt(order=order, type="black", link=link)
        self.res_list.append(self.result)

    def add_whitelist(self, link):
        self.whitelist_count += 1
        self.result = self.Result_nt(
            order=self.whitelist_count, type="white", link=link)
        self.res_list.append(self.result)

    def sort(self):
        # https://stackoverflow.com/a/12087992/6929343
        self.res_list = sorted(self.res_list, key=attrgetter('order'))
        self.cfg_list = sorted(self.cfg_list, key=itemgetter('score'))

    def set_dict_link(self, address):
        """ Website address is passed. Find matching dictionary entry in list.
            Assign passed address to 'link' key dictionary value. If 'link' is
            already set with a closer hit, then ignore.
        """
        self.cfg_index = None
        self.cfg_dict = {}

        for self.cfg_index, entry in enumerate(self.cfg_list):
            if entry['website'].decode('utf-8') in address.decode('utf-8'):
                if entry['link'] == "":
                    entry['link'] = address
                    self.cfg_list[self.cfg_index] = entry
                return True

        self.cfg_index = None
        self.cfg_dict = WS_DICT
        return False

    def set_dict_lyrics(self, scrape_func, address=None):
        """ If website address is passed, find matching dictionary entry in list.
            If address not passed, then process all dictionary entries.
            Scrape the lyrics from web page and update dictionary.
        """
        for self.cfg_index, self.cfg_dict in enumerate(self.cfg_list):
            if address is not None:
                if self.cfg_dict['website'] not in address:
                    continue  # Looking for specific address
            url = self.cfg_dict['link']
            if url == "":
                continue
            start = time.time()
            self.cfg_dict['html'], self.cfg_dict['lyrics'] = \
                scrape_func(self.cfg_dict['website'], url)
            self.cfg_dict['time'] = time.time() - start
            self.cfg_list[self.cfg_index] = self.cfg_dict

    def set_dict_score(self):
        """ Calculate website scores based on time, line length
            and line count..
        """

        for self.cfg_index, self.cfg_dict in enumerate(self.cfg_list):
            #if self.cfg_dict['time'] < 0.001:
            #    continue
            lengths = []
            for line in self.cfg_dict['lyrics']:
                lengths.append(len(line))
            total = sum(lengths)
            count = len(lengths)
            if count > 0:
                average = int(total / len(lengths))
            else:
                average = 0
            if len(self.cfg_dict['name']) < 8:  # 8 stops per tab
                tabs = '\t\t'
            else:
                tabs = '\t'
            print(self.cfg_dict['name'] + tabs, 'Total:', total, '\t Average:', average)
            print('\t\t Count:', len(lengths), '\t', 'Time:   ', self.cfg_dict['time'])
            #if self.cfg_dict['name'] != "Megalobiz":
            #    print(self.cfg_dict['lyrics'])
            self.cfg_list[self.cfg_index] = self.cfg_dict


results = Results()             # global class


def save_ctl():
    """
        CANCEL: scrape has full access to sql to see what has been
                downloaded in the past.

        Save Control file containing list of dictionaries

        USED by mserve and scrape.py
            mserve passes previous list of names with flags to scrape.
            scrape.py passes back name of website that was scraped.
            scrape.py passes names of websites that CAN BE scraped.
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
    """ USED by mserve and scrape.py """
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


# TODO: Create dictionary with website and last time scraped. This way we can
#       cycle through names and not bombard a single site with quick requests.
#       At two seconds per site it will be ~15 seconds between requests which
#       should satisfy most robot detectors. Dictionary is saved as pickle in
#       ~/.config/mserve/scrape.pkl


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
            9. Megalobiz
    """
    global WS_DICT, CTL_LIST
    global MEGALOBIZ, AZLYRICS, LYRICS, LYRICSMODE, LETSSINGIT
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

    limit = 100  # valid options 10, 20, 30, 40, 50, and 100
    #    page = requests.get(f"https://www.google.com/search?q={search}&num={limit}")
    query = "https://www.google.com/search?q={search}&num={limit}". \
        format(search=search, limit=limit, headers=headers)
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
                results.add_blacklist(t)
                continue
            else:
                list_output.append(t)
                results.add_whitelist(t)

            # Look up in list and assign link
            if results.set_dict_link(t):
                print('dictionary updated for:', t)
            else:
                pass  # Lyrics link isn't in list

    results.sort()

    # TODO: scrollable text with results
    print(*results.res_list, sep='\n')
    print(*results.cfg_list, sep='\n')

    # Save files
    with open(SCRAPE_LIST_FNAME, "w") as outfile:
        for line in list_output:
            outfile.write(line + "\n")

    # If we try to print normally an error occurs when launched in background
    # print("\nCTL_LIST after search:", CTL_LIST, file=sys.stderr)

    save_ctl()



def scrape(website, url):
    if url == "":
        return []

    html = ""
    lyrics = []
    if website == '//genius.com':
        html, lyrics = get_from_genius(url)

    if website == "www.megalobiz.com":
        html, lyrics = get_from_megalobiz(url)

    if website == "www.azlyrics.com":
        html, lyrics = get_from_azlyrics(url)

    if website == "www.metrolyrics.com":
        html, lyrics = get_from_metrolyrics(url)

    if website == "www.lyrics.com":
        html, lyrics = get_from_lyrics(url)

    if website == "www.lyricsmode.com":
        html, lyrics = get_from_lyricsmode(url)

    if website == "www.letssingit.com":
        html, lyrics = get_from_letssingit(url)

    if website == "www.musixmatch.com":
        html, lyrics = get_from_musixmatch(url)

    if website == "www.lyricsplanet.com":
        html, lyrics = get_from_lyricsplanet(url)

    return html, lyrics


def old_scrape():
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
            outfile.write(line + "\n")


def get_from_genius(url):

    text = ""
    lyrics = []

    # noinspection PyBroadException
    try:
        soup = BeautifulSoup(requests.get(url).content, 'lxml')
        text = soup.text
        for tag in soup.select('div[class^="Lyrics__Container"], \
                               .song_body-lyrics p'):
            t = tag.get_text(strip=True, separator='\n')
            if t:
                # print(t)
                lyrics.extend(t.split('\n'))  # \n\t
    except:
        lyrics.append('Error occurred retrieving genius.com lyrics')
        lyrics.append(url)
        lyrics.append('Search String: ' + SEARCH)

    #print('get_from_genius:')
    #print(soup.text)
    return text, lyrics


def get_from_azlyrics(url):
    """
        https://learn.co/lessons/python-scraping-beautiful_soup

        SEARCH:
            <div id="lyrics_text" class="js-new-text-select" style="position: relative;">
    """

    #print('===========================================================================')
    #print('get_from_azlyrics():')

    html_page = urllib.request.urlopen(url)
    soup = BeautifulSoup(html_page, 'html.parser')
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    #print(soup.prettify()[7000:10000])
    #links = soup.findAll('a')
    #print(links[10:40])
    #albums = soup.find_all('div', class_="ringtone")
    #print('Number of matches: {}'.format(len(albums)))
    #print('Object type: {}'.format(type(albums)))
    #print('Preview of objects:\n{}'.format(albums))
    #album = albums[0]
    #lyrics = album.findNextSiblings('a')
    #print(lyrics)

    html_pointer = soup.find('div', class_="ringtone")
    if html_pointer is None:
        print('get_from_azlyrics(url): html_pointer is None')
        return "", []

    result = html_pointer.find_next('div').text.strip().splitlines()

    lyrics = []
    if result is not None:
        lyrics = result

    # print(lyrics)
    #return html_page, lyrics
    return r.text, lyrics


def get_from_metrolyrics(url):
    from lxml import html

    """Load the lyrics from MetroLyrics."""
    page = requests.get(url)

    if page.status_code > 200:
        # raise ("No lyrics available for requested song")
        return

    # Forces utf-8 to prevent character mangling
    page.encoding = 'utf-8'

    tree = html.fromstring(page.text)
    #print('===========================================================================')
    #print('\n get_from_metrolyrics')
    #print(page.text)
    try:
        lyric_div = tree.get_element_by_id('lyrics-body-text')
        verses = [c.text_content() for c in lyric_div.find_class('verse')]
    except KeyError:
        verses = ['No lyrics available for requested song']
    else:
        # Not sure what do do with following line just yet (Feb 21 2021)
        # lyrics = '\n\n'.join(verses)
        pass

    return page.text, verses


def get_from_megalobiz(url):
    """ Song # 878 Creed - My Sacrifice

        Lyrics are split up into two lines versus one in Genius.com
        .LRC times are to 100th of a second
    """

    # https://stackoverflow.com/a/68980092/6929343
    #print(url)
    r = requests.get(url)
    #print('get_from_megalobiz')
    #print(r.text)
    soup = BeautifulSoup(r.text, 'lxml')

    d = soup.find('div', class_='lyrics_details entity_more_info')
    details = list(d.find('span').stripped_strings)

    #duration = details[0]
    lyrics = details[3:]
    #print('Duration:', duration)

    #print('===========================================================================')
    #print('Lyrics:')
    #print(*lyrics, sep='\n')
    return r.text, lyrics


def get_from_lyrics(url):
    """ Get from www.lyrics.com

          <meta content="My Sacrifice [Album Version] Lyrics by Creed from the Weathered
          album - including song video, artist biography, translations and more: Hello my friend we meet again
It's been a while, where should we begin
Feels like forever
Within my heart are memories
…" name="description"/>

        SO THE LYRICS ARE CHOPPED OFF UNLESS YOU BUY A PASS?
    """
    #print('===========================================================================')
    #print('get_from_lyrics:')
    r = requests.get(url)

    #soup = BeautifulSoup(r.text, 'lxml')
    #print('===========================================================================')
    #print('get_from_lyrics:     r.text')
    #print(soup.prettify()[:2000])

    #html_page = urllib.request.urlopen(url)
    #soup = BeautifulSoup(html_page, 'html.parser')
    #print('===========================================================================')
    #print('get_from_lyrics:     html_page')
    #print(soup.prettify()[:2000])

    #print('===========================================================================')
    #print('get_from_lyrics:     html_page.content')
    #html_page = requests.get(url)
    #try:
    #    soup = BeautifulSoup(html_page.content, 'html.parser')
    #except AttributeError:
    #    print('addinfourl instance has no attribute "content"')
    #print('===========================================================================')
    #print(soup.prettify()[500:5000])

    #print('===========================================================================')
    #for a in soup.find_all('a', href=True):
    #    ref = str(a['href']).upper()
    #    if "CREED" in ref:
    #        print("Found the URL:", a['href'])

    """ 
        Searching with:
            u'https://www.lyrics.com/lyric/5212265/Creed/My%2BSacrifice

        Probably want one of these:

            Found the URL: https://www.lyrics.com/lyric/5212265/Creed
                                            +
            Found the URL: /lyric/5212265/Creed/My+Sacrifice+%5BAlbum+Version%5D

            Found the URL: https://www.lyrics.com/lyric/5212265/Creed
                                            +
            Found the URL: /lyric/30501201/Creed/My+Sacrifice

    """
    #print('===========================================================================')

    return r.text, []


def get_from_lyricsmode(url):
    r = requests.get(url)
    #print('===========================================================================')
    #print('get_from_lyricsmode:')
    #print(r.text)
    return r.text, []


def get_from_letssingit(url):
    # Website down Aug 31/2021 @ 9 pm
    # Still down September 8, 2021 @ 7:57 am
    html_page = ""
    try:
        html_page = urllib.request.urlopen(url, timeout=10)
        #soup = BeautifulSoup(html_page, 'html.parser')
    except urllib.error.HTTPError:
        print('<urlopen error [Error 404] Page not found>:')
    except urllib.error.URLError:
        print('<urlopen error [Error 110] Connection timed out>:')


    #print('===========================================================================')
    #print('get_from_letssingit:')
    #print(r.text)
    return html_page, []


def get_from_musixmatch(url):

    """ https://stackoverflow.com/a/47748644/6929343
        NOTE: Remove "Host" from headers which gives error message not found.

    """
    # Use headers to prevent error "Not Allowed"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
        "Upgrade-Insecure-Requests": "1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
    }
    r = requests.get(url, headers=headers)

    #print('===========================================================================')
    #print('get_from_musixmatch():')
    #print(r.text)

    soup = BeautifulSoup(r.text, 'lxml')
    #print(soup.prettify()[:1000])
    #print(soup.prettify()[-1000:])

    span = soup.find('span', {'class': 'lyrics__content__ok'})
    # create a list of lines corresponding to element texts
    #lines = [span.get_text().strip().splitlines() for span in spans]
    lyrics = None
    if span is not None:
        lyrics = span.get_text().strip().splitlines()
    if lyrics is None:
        print('get_from_musixmatch(url): no lyrics found')
        lyrics = []
    #print(lyrics)
    #html_page = urllib.request.urlopen(url)
    #soup = BeautifulSoup(html_page, 'html.parser')
    #print(soup.prettify()[7000:10000])
    #links = soup.findAll('a')
    #print(links[10:40])

    #albums = soup.find_all('div', class_="ringtone")
    #print('Number of matches: {}'.format(len(albums)))
    #print('Object type: {}'.format(type(albums)))
    #print('Preview of objects:\n{}'.format(albums))
    #album = albums[0]
    #lyrics = album.findNextSiblings('a')
    #print(lyrics)

    #html_pointer = soup.find('div', class_="ringtone")
    #if html_pointer is None:
    #    print('get_from_azlyrics(url): html_pointer is None')
    #    return "", []

    #result = html_pointer.find_next('div').text.strip().splitlines()

    #if result is not None:
    #    lyrics = result

    # print(lyrics)
    return r.text, lyrics


def get_from_lyricsplanet(url):
    r = requests.get(url)
    #print('===========================================================================')
    #print('get_from_lyricsplanet:')
    #print(r.text)
    return r.text, []



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
    set_icon(root)

    ''' console splash message '''
    print(r'  ######################################################')
    print(r' //////////////                            \\\\\\\\\\\\\\')
    print(r'<<<<<<<<<<<<<<  scrape.py - Scrape Internet >>>>>>>>>>>>>>')
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

        # Fudge global for now
        global SEARCH

        # Define self. variables in results() where res_top frame is used.
        self.res_top = None                 # Toplevel for results
        self.res_top_is_active = None       # Is results top level open?
        self.res_view = None                # Treeview using data dictionary
        self.res_view_btn1 = None
        self.res_view_btn2 = None
        self.res_view_btn3 = None
        self.res_view_btn4 = None
        self.res_view_btn5 = None
        self.res_view_btn6 = None
        self.res_view_btn7 = None
        self.res_search = None              # Searching for trash, etc?

        self.hdr_top = None                 # Toplevel for gmail message header
        self.hdr_top_is_active = False      # Displaying gmail message header?
        self.scrollbox = None               # Holds pretty print dictionary

        ''' HistoryTree Instances '''
        self.view = None                    # = lib_view or res_view
        self.region = None                  # 'heading', 'separator' or 'cell'
        self.res_gen = None                 # Backup generations
        self.subject_list = []              # GMAIL_SUBJECT.split('!')
        self.iid = None

        ''' get parameters in SQL setup by mserve '''
        now = time.time()
        last_time = sql.hist_last_time('scrape', 'parm')
        if last_time is None:
            last_time = now
        hist_row = sql.hist_get_row(sql.HISTORY_ID)
        lag = now - last_time
        if lag > 1.0:
            print('It took more than 1 second for scrape to start:', lag)
        else:
            print('scrape start up time:', lag)
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
        self.his_top.title("SQL History Table - scrape")
        set_icon(self.his_top)

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

        ''' ✘ Close Button ✘ ✔ '''
        self.his_top.bind("<Escape>", self.close)
        self.his_top.protocol("WM_DELETE_WINDOW", self.close)
        self.close_text = "✘ Close"  # Variable button text
        self.his_tree_btn1 = tk.Button(frame3, text=self.close_text,
                                       width=g.BTN_WID - 2, command=self.close)
        self.his_tree_btn1.grid(row=0, column=0, padx=2)
        self.tt.add_tip(self.his_tree_btn1,
                        "Close scrape and any windows that scrape opened.")

        ''' ⎘ Results - # &#x2398 = ⎘ - Display webscrape results '''
        self.results_text = "⎘ Results"  # &#x2398 = ⎘
        self.his_tree_btn2 = tk.Button(frame3, text=self.results_text,
                                       width=g.BTN_WID, command=self.results)
        self.his_tree_btn2.grid(row=0, column=1, padx=2)
        self.tt.add_tip(self.his_tree_btn2, "Display Internet search results.")

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
                             command=self.close)

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

        self.his_top.update()
        search = simpledialog.askstring("Google Search String",
                                        "Enter a Google search string",
                                        parent=self.his_top)
        if search is not None:
            SEARCH = u' '.join(('song lyrics', search)).encode('utf-8')
            google_search(SEARCH)
            results.set_dict_lyrics(scrape)  # Pass scraping function name
            results.set_dict_score()            # Analyze lyrics
        #scrape(SEARCH)  # Parameter overridden when GENIUS <> ""

        ''' When load_last_selections() ends we need to enter idle loop
            until self.close() is called.
        '''

        while self.his_top:
            # Refresh every 50 ms
            self.his_top.update()
            if not self.his_top:
                # self.close() has set to None
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

            Used for populate_lib_view and populate_res_view
        """

        for i, sql_row in enumerate(rows):

            row = dict(sql_row)
            rowId = row['Id']  # Used for treeview iid

            if test is not None:
                # Optional test function to exclude (detach) rows
                # in treeview
                if not test(row):
                    dd_view.attached[rowId] = None  # Skipped
                    continue

            try:
                # NOTE: .insert for view not identical to tree!
                dd_view.insert("", dict(row), iid=rowId, tags="unchecked")
                dd_view.attached[rowId] = True  # row is attached to view
            except tk.TclError:

                # Character out of TCL displayable range or: x0 to xFF FF
                # TODO: Below copied from gmail. Remove or adapt to scrape.
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

        """ Left or Right button clicked to drill down on History treeview line.
        """
        self.view = self.his_view
        self.common_button_3(event, self.his_view)

    def res_button_3_click(self, event):

        """ Left or Right button clicked to drill down on Results treeview line.
        """

        self.view = self.res_view
        self.common_button_3(event, self.res_view)

    def common_button_3(self, event, view):
        """ Right button clicked in Library or Results treeview.

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
                               550, 450)  # width, height
            column_name = view.columns[int(column_number.replace('#', '')) - 1]
            column_dict = toolkit.get_dict_column(column_name, view.tree_dict)
            view_column = sql.PrettyHistory(column_dict)
            view_column.tkinter_display(self.scrollbox)
            return

        # At this point only other region is 'cell'

        self.iid = view.tree.identify_row(y)
        values = view.tree.item(self.iid, "values")
        if self.view == self.res_view:
            # Processing results list which doesn't have SQL row_id
            # print('scrape.py common_button_3() row_id is None')
            # noinspection PyArgumentList
            result = results.Result_nt(
                order=values[0], type=values[1], link=values[2])
            #print('result from treeview:', result)
            # noinspection PyProtectedMember
            row = OrderedDict(result._asdict())
            calc = self.res_calc_to_pretty
        else:
            row_id = view.column_value(values, "row_id")
            row = sql.hist_get_row(row_id)
            # For history view there are no calculated fields to append to display
            calc = None

        PrettyHistory = sql.PrettyHistory(row, calc=calc)

        ''' Place Window top-left of parent window with PANEL_HGT padding
            Lifted from: ~/mserve/encoding.py
        '''
        self.create_window("History row - scrape", 1200, 800)  # wid, hgt

        PrettyHistory.tkinter_display(self.scrollbox)
        # Error: TclError: character U+1f913 is above the range (U+0000-U+FFFF) allowed by Tcl
        #
        # Note self.scrollbox defined in multiple places, reduce in future
        # self.hdr_top.geometry('%dx%d+%d+%d' % (1400, 975, xy[0], xy[1]))

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

        # Use self.res_top when it is active, else self.his_top
        if self.res_top_is_active:
            xy = (self.res_top.winfo_x() + g.PANEL_HGT,
                  self.res_top.winfo_y() + g.PANEL_HGT)
        else:
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
        set_icon(self.hdr_top)

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
        Quote = ("It will take a few seconds to access internet.\n" +
                 "Then lyrics search results are displayed here.\n")
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

        self.scrollbox.config(tabs=("5m", "80m", "106m"))
        self.scrollbox.tag_configure("margin", lmargin1="5m", lmargin2="80m")
        # Fix Control+C  https://stackoverflow.com/a/64938516/6929343
        self.scrollbox.bind("<Button-1>", lambda event: self.scrollbox.focus_set())

    # noinspection PyUnusedLocal
    def pretty_close(self, *args):
        if self.hdr_top is None:
            return
        self.scrollbox.unbind("<Button-1>")
        self.hdr_top_is_active = False
        self.hdr_top.destroy()
        self.hdr_top = None

    def res_calc_to_pretty(self, pretty_dict):
        """ Add calculated fields from results.cfg_list[]

# Empty control list dictionary element (template)
WS_DICT = {"rank": 0, "name": "", "website": "", "link": "",
           "time": 0.0, "score": 0, "flag": "", "html": "", "lyrics": ""}
''' rank:       User defined preference to select websites for lyrics.
    name:       Website name in descriptive format.
    website:    Website address in www. or // format.
    link:       Google search result link.
    time:       Time it took to scrape website for lyrics. > 1 second usually error.
    score:      Score assigned based on quality of lyrics found. 0 = No lyrics.
    flag:       Not used.
    html:       Raw HTML page retrieved using google search result.
    lyrics:     Filtered lyrics extracted from HTML page.
'''

        """

        # self.iid is set when ____
        values = self.view.tree.item(self.iid)['values']
        link = self.view.column_value(values, 'link')
        print("'link = self.view.column_value(values,", link)
        found = False
        for self.cfg_index, self.cfg_dict in enumerate(results.cfg_list):
            if self.cfg_dict['link'] == link:
                found = True
                break

        if found is False:
            pretty_dict['html'] = 'HTML Page not selected for retrieval.'

        pretty_dict['time'] = str(self.cfg_dict['time'])
        pretty_dict['score'] = str(self.cfg_dict['score'])
        pretty_dict['flag'] = self.cfg_dict['flag']
        s = '\n\t\t'
        print(self.cfg_dict['lyrics'])
        # https://stackoverflow.com/a/28136464/6929343
        #pretty_dict['lyrics'] = s.join(''.join(c) for c in self.cfg_dict['lyrics'])
        pretty_dict['lyrics'] = s.join(c for c in self.cfg_dict['lyrics'])
        #pretty_dict['lyrics'] = s.join(''.join(self.cfg_dict['lyrics']))
        print(pretty_dict['lyrics'])
        pretty_dict['html'] = self.cfg_dict['html']

        # print('link found!:', self.cfg_dict['score'], self.cfg_dict['link'])
        # If columns were hidden something like below could be used
        #pretty_dict['reason'] = self.view.column_value(values, 'reason')
        #pretty_dict['row_id'] = self.view.column_value(values, "row_id")


    def lib_popup(self, *args):
        pass

    # noinspection PyUnusedLocal
    def close(self, *args):

        # Last known window position for message library, saved to SQL
        last_history_geom = monitor.get_window_geom_string(
            self.his_top, leave_visible=False)
        monitor.save_window_geom('history', last_history_geom)

        # Last known window position for message backups, saved to SQL
        if self.res_top_is_active is True:
            self.res_close()

        # TODO: Save treeview column orders and widths to SQL history.

        sql.close_db()
        self.his_top = None
        # root.after(100)
        root.destroy()

    # noinspection PyUnusedLocal
    def restart(self, *args):
        self.close()
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
        for iid in self.res_view.tree.get_children():
            # Loop through all rows in treeview
            values = self.res_view.tree.item(iid, "values")
            delete_on = self.res_view.column_value(values, "delete_on")
            if delete_on > now:
                continue

            row_count += 1
            size = self.res_view.column_value(values, "size")
            labels = self.res_view.column_value(values, "labels")
            labels_list = sql.label_string_to_list(labels)
            for label in labels_list:
                if label == "TRASH":
                    already_trashed_count += 1
                    continue

            new_labels_list = ["TRASH"]
            new_labels_list.extend(labels_list)
            new_labels = sql.label_list_to_string(new_labels_list)
            self.res_view.update_column(iid, 'labels', new_labels)
            sql.message_update_labels(iid, new_labels)

            int_size = int(size.replace(',', ''))
            total_size += int_size
            self.res_view.tree.tk.call(self.res_view.tree, "tag",
                                       "remove", "highlight")
            self.res_view.tree.see(iid)
            self.res_view.tree.tk.call(self.res_view.tree, "tag",
                                       "add", "highlight", iid)
            self.res_view.toplevel.update_idletasks()
            self.gma.trash_message(iid)
            '''
            # Testing purposes just delete first 10
            if row_count < 10:
                self.gma.trash_message(iid)
            else:
                # Simulate delay for trashing message
                self.res_view.toplevel.after(33)
            '''

        text = "Total size:  " + "{:,}".format(total_size) + "\n" + \
               "Row count:  " + "{:,}".format(row_count)

        message.ShowInfo(self.res_view.toplevel, "Backups trashed", text)

    def load_last_selections(self):
        pass

    '''
    def tree_title__add(self, ndx, val):
        """ Add a value to single index.
            Not efficient but created for conformity with other add functions.
        """
        self.his_top_totals[ndx] = self.his_top_totals[ndx] + add_list[i]
    '''

    # ==============================================================================
    #
    #       HistoryTree class - Results - results()
    #
    # ==============================================================================

    def results(self, sbar_width=12):
        """
            Open results treeview.
        """

        ''' Backups already active? '''
        if self.res_top_is_active is True:
            self.res_top.lift()
            return

        data_dict = results_treeview()
        columns = ["order", "type", "link"]
        toolkit.select_dict_columns(columns, data_dict)
        # toolkit.print_dict_columns(data_dict)

        ''' Backups is now active '''
        self.res_top_is_active = True
        self.res_top = tk.Toplevel()
        self.res_top.title("Webscrape results for Music ID: " + MUSIC_ID +
                           " - scrape")

        dtb = message.DelayedTextBox(title="Building results view",
                                     toplevel=self.res_top, width=1000)

        ''' Set program icon in taskbar '''
        set_icon(self.res_top)

        ''' Initial size of Window 75% of HD monitor size '''
        _w = int(1920 * .75)
        _h = int(1080 * .75)
        _root_xy = (3800, 200)  # Temporary hard-coded coordinates

        ''' Mount window at popup location '''
        self.res_top.minsize(width=g.WIN_MIN_WIDTH, height=g.WIN_MIN_HEIGHT)
        # What if there is no saved geometry?
        geom = monitor.get_window_geom('results')
        print('bad geometry with 0', geom)
        self.res_top.geometry(geom)

        self.res_top.configure(background="Gray")
        self.res_top.columnconfigure(0, weight=1)
        self.res_top.rowconfigure(0, weight=1)

        ''' Window Title bar.
        '''

        ''' Create master frame for treeview and buttons '''
        master_frame = tk.Frame(self.res_top, bg="olive", relief=tk.RIDGE)
        master_frame.grid(sticky=tk.NSEW)
        master_frame.columnconfigure(0, weight=1)
        master_frame.rowconfigure(0, weight=1)

        ''' Create treeview frame and treeview with scrollbars '''
        self.res_view = toolkit.DictTreeview(
            data_dict, self.res_top, master_frame, columns=columns,
            sbar_width=sbar_width)

        ''' Treeview select item - custom select processing '''
        toolkit.MoveTreeviewColumn(self.res_top, self.res_view.tree,
                                   row_release=self.res_button_3_click)
        self.res_view.tree.bind("<Button-3>", self.res_button_3_click)

        ''' Backup Generations - Yearly, Monthly, Weekly, Daily '''
        #self.res_gen = sql.BackupGenerations(
        #    self.res_view, KEEP_DAYS, KEEP_WEEKS, KEEP_MONTHS, KEEP_YEARS,
        #    GMAIL_SUBJECT, BACKUP_LABEL, eow=WEEKLY_DOW)

        ''' Filtering rows '''
        # match = sql.Filter(self.res_view.tree, self.res_view.tree_dict)

        ''' Create Treeview item list with NO backups selected. '''
        self.populate_res_tree(dtb)

        ''' Some Backup Generation tests '''
        # print('==================  YEARS  ===================', len(self.res_gen.years))
        # self.res_gen.print_dict(self.res_gen.years, 0, 5)
        # print('==================  MONTHS ===================', len(self.res_gen.months))
        # self.res_gen.print_dict(self.res_gen.months, 0, 5)
        # print('==================  WEEKS  ===================', len(self.res_gen.weeks))
        # self.res_gen.print_dict(self.res_gen.weeks, 0, 5)
        # print('==================  DAYS   ===================', len(self.res_gen.days))
        # self.res_gen.print_dict(self.res_gen.days, 0, 5)

        ''' Calculate 'delete_on' date and 'reason' why '''
        # self.res_gen.calc_delete_on()  # Refactor into calc_score

        ''' Treeview Buttons '''
        frame3 = tk.Frame(master_frame, bg="Blue", bd=2, relief=tk.GROOVE,
                          borderwidth=g.BTN_BRD_WID)
        frame3.grid_rowconfigure(0, weight=1)
        frame3.grid_columnconfigure(0, weight=0)
        frame3.grid(row=1, column=0, sticky=tk.NW)

        ''' ✘ Close Button ✘ ✔ '''
        self.res_top.bind("<Escape>", self.res_close)
        self.res_top.protocol("WM_DELETE_WINDOW", self.res_close)
        self.res_view_btn1 = tk.Button(frame3, text="✘ Close",
                                       width=g.BTN_WID - 2, command=self.res_close)
        self.res_view_btn1.grid(row=0, column=0, padx=2)
        self.tt.add_tip(self.res_view_btn1,
                        "Close backups view but bserve remains open.")

        ''' “🗑” U+1F5D1 (trash can) - Recently trashed backups '''
        self.res_view_btn2 = tk.Button(
            frame3, text="🗑 Recent", width=g.BTN_WID, command=self.recent_trash)
        self.res_view_btn2.grid(row=0, column=1, padx=2)
        self.tt.add_tip(self.res_view_btn2, "Recently trashed backups.")

        ''' Pending messages to trash '''
        self.res_view_btn3 = tk.Button(
            frame3, text="🗑 Pending", width=g.BTN_WID - 1, command=self.pending_trash)
        self.res_view_btn3.grid(row=0, column=2, padx=2)
        self.tt.add_tip(self.res_view_btn3, "Backups that will be trashed.")

        ''' Permanently deleted messages '''
        self.res_view_btn4 = tk.Button(
            frame3, text="🗑 Permanent", width=g.BTN_WID - 1, command=self.load_items)
        self.res_view_btn4.grid(row=0, column=3, padx=2)
        self.tt.add_tip(self.res_view_btn4, "Permanently deleted backups.")

        ''' 🗘 u1f5d8 - Refresh Backups '''
        self.res_view_btn5 = tk.Button(frame3, text="🗘  Refresh",
                                       width=g.BTN_WID - 2, command=self.res_refresh)
        self.res_view_btn5.grid(row=0, column=4, padx=2)
        self.tt.add_tip(self.res_view_btn5, "Refresh view, removing any filters")

        '''  🖸 (1f5b8) - Rotate backups '''
        self.res_view_btn6 = tk.Button(frame3, text="🖸  Rotate backups",
                                       width=g.BTN_WID - 2, command=self.rotate_backups)
        self.res_view_btn6.grid(row=0, column=5, padx=2)
        self.tt.add_tip(self.res_view_btn6, "Rotate daily, weekly, monthly, yearly backups.")

        '''  “∑” (U+2211) - Summarize sizes and count rows '''
        self.res_view_btn7 = tk.Button(frame3, text="∑  Summary",
                                       width=g.BTN_WID - 2, command=self.summary)
        self.res_view_btn7.grid(row=0, column=6, padx=2)
        self.tt.add_tip(self.res_view_btn7, "Tally sizes and count rows.")

        ''' Colors for tags '''
        self.ignore_item = None
        #self.res_view.tree.tag_configure('selected', foreground='Red')

    def populate_res_tree(self, delayed_textbox):

        """ Insert results list into treeview
        """

        self.insert_res_line(self.res_view, results.res_list, delayed_textbox)


    @staticmethod
    def insert_res_line(dd_view, res_list, delayed_textbox):
        """ Stuff SQL header rows into treeview

            Used for populate_lib_view and populate_res_view
        """

        for i, result in enumerate(res_list):

            # noinspection PyProtectedMember
            row = OrderedDict(result._asdict())
            rowId = row['order']  # Used for treeview iid


            # NOTE: .insert for view not identical to tree!
            dd_view.insert("", row, iid=rowId, tags="unchecked")

            ''' dtb_line displays only if lag experienced  '''
            dtb_line = str(row['order']) + " - " + row['type']

            if delayed_textbox.update(dtb_line):
                # delayed_textbox returns true only when visible otherwise
                # we are in quiet mode because not enough time has passed.
                dd_view.tree.see(rowId)
                dd_view.tree.update()

        # Display top row: https://stackoverflow.com/a/66035802/6929343
        children = dd_view.tree.get_children()
        if children:
            dd_view.tree.see(children[0])

    def res_popup(self):
        pass

    def res_refresh(self):
        """ Uses string_search function methods but on labels only """
        if self.res_search is not None:
            self.res_search.close()
            self.res_search = None

    def recent_trash(self):
        """ Uses string_search function methods but on labels only """
        if self.res_search is not None:
            self.res_search.close()

        self.res_search = toolkit.SearchText(
            self.res_view, column='labels', find_str='Trash')
        self.res_search.find_one()

    def pending_trash(self):
        """ Call rotate backups with trial run

            Show backups that will be deleted over next 90 days based
            on today's date. For testing purposes a future run date can
            be entered. EG next year.
        """
        if self.res_search is not None:
            self.res_search.close()

        now = str(datetime.date.today())
        self.res_search = toolkit.SearchText(
            self.res_view, column='delete_on', find_str=now, find_op='<=')
        self.res_search.find_one()

    def summary(self):
        """ Add up sizes and count number of rows.

            Display results in info message.

            TODO: Currently only used in res_view. What about lib_view?
        """

        total_size = 0
        row_count = 0
        for iid in self.res_view.tree.get_children():
            # Loop through all rows
            row_count += 1
            values = self.res_view.tree.item(iid, "values")
            size = self.res_view.column_value(values, "size")
            int_size = int(size.replace(',', ''))
            total_size += int_size

        text = "Total size:  " + "{:,}".format(total_size) + "\n" + \
               "Row count:  " + "{:,}".format(row_count)

        message.ShowInfo(self.res_view.toplevel, "Summary", text)

    # noinspection PyUnusedLocal
    def res_close(self, *args):
        last_results_geom = monitor.get_window_geom_string(
            self.res_top, leave_visible=False)
        monitor.save_window_geom('results', last_results_geom)
        self.res_top_is_active = False
        self.res_top.destroy()
        self.res_search = None


def results_treeview():
    """ Define Data Dictionary treeview columns for results list.

        Note the var_name is lower case to match namedtuple.

        Mirrors setup in sql.history_treeview but is placed here because
        this is the only place used.

# Empty control list dictionary element (template)
WS_DICT = {"rank": 0, "name": "", "website": "",
           "link": "", "time": 0.0, "score": 0, "flag": "", "html": "", "lyrics": ""}

BLACK_LIST = ['youtube', 'wikipedia', 'facebook', 'pinterest']

BLACK_LIST_COUNT = 0
WHITE_LIST_COUNT = 0
list_output = []
lyrics_output = []              # Was not defined global in scrape() function

# Global search string
SEARCH = ""
MUSIC_ID = ""


# noinspection PyArgumentList
class Results:
    def __init__(self):
        self.blacklist_count = 0
        self.whitelist_count = 0
        # TODO: Get configuration from SQL History Table
        # Pretend we didn't get list from SQL
        if True is True:
            self.cfg_list = DEFAULT_LIST
        self.cfg_index = None
        self.cfg_dict = WS_DICT
        self.res_list = []
        self.Result_nt = namedtuple('Result', 'order, type, link')
        self.result = self.Result_nt(order=0, type="white", link='')

    """

    results_treeview_list = [

      OrderedDict([
        ("column", "order"), ("heading", "Order"), ("sql_table", "calc"),
        ("var_name", "order"), ("select_order", 0), ("unselect_order", 1),
        ("key", False), ("anchor", "e"), ("instance", int),
        ("format", None), ("display_width", 120),
        ("display_min_width", 80), ("display_long", None), ("stretch", 0)]),

      OrderedDict([
        ("column", "type"), ("heading", "Type"), ("sql_table", "calc"),
        ("var_name", "type"), ("select_order", 0), ("unselect_order", 2),
        ("key", False), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 150), ("display_min_width", 120),
        ("display_long", None), ("stretch", 0)]),  # 0=NO, 1=YES

      OrderedDict([
        ("column", "link"), ("heading", "Search result link"), ("sql_table", "calc"),
        ("var_name", "link"), ("select_order", 0), ("unselect_order", 3),
        ("key", False), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 800), ("display_min_width", 600),
        ("display_long", None), ("stretch", 1)])
    ]

    return results_treeview_list


def set_icon(toplevel):
    """ Set icon in taskbar. Called from 4 places """
    img.taskbar_icon(toplevel, 64, 'black', 'green', 'red', char='W')


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
    #scrape(SEARCH)  # Parameter overridden when GENIUS <> ""

    # https://stackoverflow.com/a/47420863/6929343
    # Error goes away when print() is removed


if __name__ == "__main__":
    main()

# End of scrape.py
