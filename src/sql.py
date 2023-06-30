#!/usr/bin/env python
# -*- coding: utf-8 -*-

#==============================================================================
#
#       sql.py - SQLite3 module
#
#       Tables:
#           
#           Music - Master table of songs in all locations
#           History - History table of events and settings
#           Location - Storage locations with host controls, last song, etc.
#
#       May. 07 2023 - Convert gmtime to localtime. Before today needs update.
#       Jun. 04 2023 - Use OsFileNameBlacklist() class for reading by song
#
#   TODO:

#    Need to fix file modification time which will make it greater than
#    creation time (not birth time which is unused) which is the time it
#    was copied to the directory and permissions were established. Use
#    ID3 tag: CREATION_TIME : 2012-08-20 17:06:42
#
#==============================================================================

from __future__ import print_function       # Must be first import
from __future__ import unicode_literals     # Unicode errors fix

import os
import re
import json
import time
import datetime
import sqlite3
from collections import namedtuple, OrderedDict


# local modules
import global_variables as g        # should be self-explanatory
if g.USER is None:
    #print('sql.py was forced to run g.init()')
    # sql.py runs init when mserve.py starts. Otherwise, location.py runs init.
    g.init()
import timefmt as tmf               # Our custom time formatting functions
import external as ext

try:
    from location import FNAME_LIBRARY  # SQL database name (SQLite3 format)
except ImportError:
    print("'from location import FNAME_LIBRARY' FAILED !!!")
    FNAME_LIBRARY = g.USER_DATA_DIR + os.sep + "library.db"
    print("Using hard-coded:", FNAME_LIBRARY)

CFG_THOUSAND_SEP = ","              # English "," to for thousands separator
CFG_DECIMAL_SEP = "."               # English "." for fractional amount
CFG_DECIMAL_PLACES = 1              # 1 decimal place, eg "38.5 MB"
CFG_DIVISOR_AMT = 1000000           # Divide by million
CFG_DIVISOR_UOM = "MB"              # Unit of Measure becomes Megabyte

NO_ARTIST_STR = "<No Artist>"       # global User defined labels
NO_ALBUM_STR = "<No Album>"
'''
From: https://www.sqlite.org/pragma.html#pragma_user_version

PRAGMA schema.user_version;
PRAGMA schema.user_version = integer ;

The user_version pragma will to get or set the value of the user-version 
integer at offset 60 in the database header. The user-version is an integer
that is available to applications to use however they want. SQLite makes 
no use of the user-version itself.

See also the application_id pragma and schema_version pragma.

Also from: https://stackoverflow.com/questions/2354696/
alter-table-sqlite-how-to-check-if-a-column-exists-before-alter-the-table/2354829#2354829

Need to add:
genius link, genius download time
azlyrics link, azlyrics download time
'''

# Global variables must be defined at module level
con = cursor = hist_cursor = None
START_DIR_SEP  = None
#MUSIC_ID  = None    # June 3, 2023 - Appears unused
_START_DIR = _PRUNED_DIR = _PRUNED_COUNT = _USER = _LODICT = None


def create_tables(SortedList, start_dir, pruned_dir, pruned_count, user, lodict):
    """ Create SQL tables out of OS sorted music top directory

        THIS IS VERY VERY UGLY... FIX ASAP

        if START_DIR = '/mnt/music/'
        then PRUNED_SUBDIRS = 0

        if START_DIR = '/mnt/music/Trooper/'
        then PRUNED_SUBDIRS = 1

        if START_DIR = '/mnt/music/Trooper/Hits From 10 Albums/'
        then PRUNED_SUBDIRS = 2

        if START_DIR = '/mnt/... 10 Albums/08 Raise A Little Hell.m4a'
        then PRUNED_SUBDIRS = 3

    """

    # global con, cursor, hist_cursor
    global START_DIR_SEP    # Count of / or \ separators in toplevel directory
    #global MUSIC_ID         # primary key into Music table used by History table

    global _START_DIR, _PRUNED_DIR, _PRUNED_COUNT, _USER, _LODICT
    _START_DIR = start_dir  # Startup music directory, EG /mnt/music/Artist
    _PRUNED_DIR = pruned_dir  # Toplevel directory, EG /mnt/music/
    _PRUNED_COUNT = pruned_count  # How many directory levels pruned?
    _USER = user            # User ID to be stored on history records.
    _LODICT = lodict        # Location dictionary

    open_db()

    LastArtist = ""         # For control breaks
    LastAlbum = ""

    START_DIR_SEP = start_dir.count(os.sep) - 1  # Number of / separators
    #print('PRUNED_SUBDIRS:', pruned_count)
    START_DIR_SEP = START_DIR_SEP - pruned_count

    for i, os_name in enumerate(SortedList):

        # split /mnt/music/Artist/Album/Song.m4a into list

        # TODO: Check of os_name in Music Table. If so continue loop
        #       Move this into mserve.py main loop and update access time in SQL.
        groups = os_name.split(os.sep)
        Artist = groups[START_DIR_SEP+1]  # May contain "<No Artist>"
        Album = groups[START_DIR_SEP+2]  # May contain "<No Album>"
        key = os_name[len(_START_DIR):]

        if Artist != LastArtist:
            # In future we can add Artist table with totals
            LastArtist = Artist
            LastAlbum = ""          # Force sub-total break for Album

        if Album != LastAlbum:
            # In future we can add Album table with totals
            LastAlbum = Album

        ''' Build full song path from song_list[] '''
        full_path = os_name
        full_path = full_path.replace(os.sep + NO_ARTIST_STR, '')
        full_path = full_path.replace(os.sep + NO_ALBUM_STR, '')
        sql_key = full_path[len(_START_DIR):]

        ''' June 2, 2023 - Do not store songs with missing artist or album '''
        if os.sep + NO_ARTIST_STR in key or os.sep + NO_ALBUM_STR in key:
            ofb.AddBlacklist(sql_key)
            continue

        ''' June 10, 2023 - Do not store songs without two os.sep '''
        if sql_key.count(os.sep) != 2:
            #print("skipping sql_key without 2 separators:", sql_key)
            ofb.AddBlacklist(sql_key)
            continue

        # os.stat gives us all of file's attributes
        stat = os.stat(full_path)
        #size = stat.st_size  # TODO: test if this extra step necessary
        # converted = float(size) / float(CFG_DIVISOR_AMT)   # Not used
        # fsize = str(round(converted, CFG_DECIMAL_PLACES))  # Not used

        ''' Add the song only if it doesn't exist (ie generates error) 
            What is lastrowid? https://stackoverflow.com/a/6242813/6929343
        '''
        sql = "INSERT OR IGNORE INTO Music (OsFileName, \
               OsAccessTime, OsModificationTime, OsCreationTime, OsFileSize) \
               VALUES (?, ?, ?, ?, ?)" 

        cursor.execute(sql, (key, stat.st_atime, stat.st_mtime,
                             stat.st_ctime, stat.st_size))

    con.commit()

    # Temporary during development to record history for lyrics web scrape and
    # time index synchronizing to lyrics.
    #ext.t_init("SQL startup functions to remove")
    #ext.t_init("hist_init_lost_and_found")
    #hist_init_lost_and_found(start_dir, user, lodict)
    #job_time = ext.t_end('print')
    #print("Did not print? job_time:", job_time)  # 0.0426070690155
    #ext.t_init("hist_init_lyrics_and_time")
    #hist_init_lyrics_and_time(start_dir, user, lodict)
    #job_time = ext.t_end('print')  # 0.0366790294647
    #print("Did not print? job_time:", job_time)
    #job_time = ext.t_end('print')  # 0.0793550014496
    #print("Did not print? job_time:", job_time)

    # June 3, 2023 before: sql.create_tables(): 0.1658391953
    # June 3, 2023 AFTER : sql.create_tables(): 0.0638458729


def open_db():
    """ Open SQL Tables - Music Table and History Table
        Create Tables and Indices that don't exist
    """
    global con, cursor, hist_cursor
    con = sqlite3.connect(FNAME_LIBRARY)

    # MUSIC TABLE
    # Avoid \t & \n in sqlite_master.
    #   See: https://stackoverflow.com/questions/76427995/
    #   how-do-i-clean-up-sqlite-master-format-in-python
    # Create the table (key must be INTEGER not just INT !
    #   See https://stackoverflow.com/a/7337945/6929343 for explanation
    con.execute("create table IF NOT EXISTS Music(Id INTEGER PRIMARY KEY, " +
                "OsFileName TEXT, OsAccessTime FLOAT, " +
                "OsModificationTime FLOAT, OsCreationTime FLOAT, " +
                "OsFileSize INT, MetaArtistName TEXT, MetaAlbumName TEXT, " +
                "MetaSongName TEXT, ReleaseDate FLOAT, OriginalDate FLOAT, " +
                "Genre TEXT, Seconds INT, Duration TEXT, PlayCount INT, " +
                "TrackNumber TEXT, Rating TEXT, UnsynchronizedLyrics BLOB, " +
                "LyricsTimeIndex TEXT)")

    con.execute("CREATE UNIQUE INDEX IF NOT EXISTS OsFileNameIndex ON " +
                "Music(OsFileName)")

    # HISTORY TABLE
    con.execute("create table IF NOT EXISTS History(Id INTEGER PRIMARY KEY, " +
                "Time FLOAT, MusicId INTEGER, User TEXT, Type TEXT, " +
                "Action TEXT, SourceMaster TEXT, SourceDetail TEXT, " +
                "Target TEXT, Size INT, Count INT, Seconds FLOAT, " +
                "Comments TEXT)")

    con.execute("CREATE INDEX IF NOT EXISTS MusicIdIndex ON " +
                "History(MusicId)")
    con.execute("CREATE INDEX IF NOT EXISTS TimeIndex ON " +
                "History(Time)")
    con.execute("CREATE INDEX IF NOT EXISTS TypeActionIndex ON " +
                "History(Type, Action)")

    '''
        INDEX on OsSongName and confirm original when OsArtistName and
            OsAlbumName match up to SORTED_LIST (aka self.song_list) which is
            format of:
                # split song /mnt/music/Artist/Album/Song.m4a into names:
                groups = os_name.split(os.sep)
                Artist = str(groups [START_DIR_SEP+1])
                Album = str(groups [START_DIR_SEP+2])
                Song = str(groups [START_DIR_SEP+3])

            (last_playlist and last_selections uses the same record format)

        Saving/retrieving LyricsTimeIndex (seconds from start):

        >>> import json
        >>> json.dumps([1.2,2.4,3.6])
        '[1.2, 2.4, 3.6]'
        >>> json.loads('[1.2, 2.4, 3.6]')
        [1.2, 2.4, 3.6]

    '''
    # Retrieve column names
    #    cs = con.execute('pragma table_info(Music)').fetchall() # sqlite column metadata
    #    print('cs:', cs)
    #    cursor = con.execute('select * from Music')
    #    names = [description[0] for description in cursor.description]
    #    print('names:', names)
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    hist_cursor = con.cursor()

    ''' Functions to fix errors in SQL database '''
    # fd = FixData("Thu Jun 10 23:59:59 2023")  # Class for common fix functions

    # fd.del_music_ids(3939, 5000, update=False)  # Leave range 3939-5000 for awhile
    # Patch run Jun 02, 2023 with "update=True". 39 Music Ids deleted 3908->3946
    # Patch run Jun 07, 2023 with "update=True". 1 Music Ids deleted 2186->2186
    # Patch run Jun 10, 2023 with "update=True". 160 Music Ids deleted 3908->4067
    # Jun 11, 2023 Duplicate "The Very Best Things". 14 Music Ids deleted 1092->1105
    # Jun 11, 2023 Duplicate "The Very Best Things". 14 Music Ids deleted 1106->1119

    #fd.fix_scrape_parm(update=False)
    # Patch run May 23, 2023 with "update=True". 66 corrupt scrape-parm deleted

    #fd.fix_meta_edit(update=False)
    # Patch run May 15, 2023 with "update=True". 290 duplicate meta-edit deleted

    #fd.fix_utc_dates(update=False)
    # NEVER RUN fd.fix_utc_dates() AGAIN OR PERMANENT DAMAGE !!!!!!!!!!!!!!!
    # Patch run May 12, 2023 with "update=True". Thousands converted utc to local


def close_db():
    con.commit()
    cursor.close()          # Aug 08/21 Fix "OperationalError:"
    hist_cursor.close()     # See: https://stackoverflow.com/a/53182224/6929343
    con.close()


class OsFileNameBlacklist:
    """ Music Player allows songs with "<No Artist>/" and "/<No Album>/"
        subdirectories but these cannot be stored in SQL Database.

        Music Table Key OsFileName is "Artist/Album/99 Song.ext"

        self.blacks[] list of songs that cannot be accessed.
        self.whites[] list of equivalent songs if possible or None.

        USAGE:

        ofb = OsFileNameBlackList()
        ofb.Select(key) get song from SQL directly or via whitelist
        ofb.CheckBlacklist(key) returns true if Blacklisted.
        ofb.CheckWhitelist(key) returns true if Blacklisted and a whitelist.
            key exists that is not 'None'. All blacklist keys have a
            whitelist key initially set to 'None'.
        ofb.AddBlacklist(key) adds key to blacklist and None to whitelist
            counterpart list.
        ofb.SetWhitelist(bad, good) Looks up bad key in blacklist to get
            index and sets whitelist @ index to good key passed.
        ofb.GetWhitelist(bad) returns the good key to replace the bad key
            or returns None.
    """

    def __init__(self):
        self.blacks = []
        self.whites = []

        self.white_key = None  # Used for GetWhitelist(key)

    def Select(self, key):
        """
        Wrapper for reading Music Table Row by OsFileName - "artist/album/99 song.ext"
        :param key: E.G. "Faith No More/17 Last Cup Of Sorrow.m4a"
        :return: Returns dictionary or None
        """

        cursor.execute("SELECT * FROM Music WHERE OsFileName = ?", [key])
        try:
            d = dict(cursor.fetchone())
            return d  # Normal successful read

        except TypeError:  # TypeError: 'NoneType' object is not iterable:
            if self.CheckBlacklist(key):
                if self.CheckWhitelist(key):
                    cursor.execute("SELECT * FROM Music WHERE OsFileName = ?",
                                   [self.white_key])
                    d = dict(cursor.fetchone())
                    return d
                else:
                    return None
            else:
                self.AddBlacklist(key)
                return None

    def CheckBlacklist(self, key):
        """ TODO: Simpler to use: 'if key in self.blacks' """
        try:
            _ndx = self.blacks.index(key)
            return True
        except ValueError:
            return False

    def AddBlacklist(self, key):
        try:
            ndx = self.blacks.index(key)
            print("sql.py AddBlacklist(key) already exists in list:", key,
                  "at 0's based index:", ndx)
            return False
        except ValueError:
            # This is normally expected
            self.blacks.append(key)
            self.whites.append(None)
            return True

    def CheckWhitelist(self, key):
        """ TODO: Simpler to use: 'if key in self.whites' """
        try:
            ndx = self.blacks.index(key)
            self.white_key = self.whites[ndx]  # Kind of cheating... but...
            return self.white_key is not None
        except ValueError:
            print("sql.py CheckWhitelist(key) key not in self.blacks:", key)
            return False  # More explicit than None

    def GetWhitelist(self, key):
        try:
            ndx = self.blacks.index(key)
            self.white_key = self.whites[ndx]  # Redundancy
            if self.white_key is None:
                print("sql.py GetWhitelist(key) WARNING:", key, "points to None")
            return self.white_key  # Value could still be None which is False
        except ValueError:
            print("sql.py GetWhitelist(key) WARNING:", key,
                  "does not exist in self.blacks")
            return None

    def SetWhitelist(self, black_key, white_key):
        try:
            ndx = self.blacks.index(black_key)
            self.whites[ndx] = white_key  # Overwrite 'None' with substitute song
        except ValueError:
            print("sql.py SetWhitelist(black_key, white_key) invalid black_key:",
                  black_key)
            return None


''' Global substitution for read Music Table by path '''
ofb = OsFileNameBlacklist()


def make_key(fake_path):
    """
        DEPRECATED: June 3, 2023

        Create key to read Music index by OsFileName which is
        /path/to/topdir/album/artist/song.ext

    TODO: What about PRUNED_SUBDIRS from mserve code?

        # Temporarily create SQL music tables until search button created.
        sql.CreateMusicTables(SORTED_LIST, START_DIR, PRUNED_SUBDIRS)

        What about '(NO_ARTIST)' and '(NO_ALBUM)' strings?
    """
    ''' Version prior to June 3, 2023 when new Blacklist implemented '''
    groups = fake_path.split(os.sep)
    artist = groups[START_DIR_SEP+1]
    album = groups[START_DIR_SEP+2]
    song = groups[START_DIR_SEP+3]

    ''' June 3, 2023 - <No Artist> already stripped for new Blacklist '''
    global _START_DIR
    suffix = fake_path
    suffix = suffix.replace(os.sep + NO_ARTIST_STR, '')
    suffix = suffix.replace(os.sep + NO_ALBUM_STR, '')
    suffix = suffix[len(_START_DIR):]

    #return suffix
    return artist + os.sep + album + os.sep + song


def update_lyrics(key, lyrics, time_index):
    """
        Apply Unsynchronized Lyrics and Lyrics Time Index.
        Should only be called when lyrics or time_index has changed.

        NOTE: May 21, 2023 - This is where lyrics - init, lyrics - edit,
        time - init and time - edit could be placed.
    """

    sql = "UPDATE Music SET UnsynchronizedLyrics=?, LyricsTimeIndex=? \
           WHERE OsFileName = ?" 

    if time_index is not None:
        # count = len(time_index)  # Not used
        time_index = json.dumps(time_index)
        # print('Saving', count, 'lines of time_index:', time_index)

    cursor.execute(sql, (lyrics, time_index, key))
    con.commit()


def get_lyrics(key):
    """
        Get Unsynchronized Lyrics and Lyrics Time Index
    """
    # global MUSIC_ID  # June 3, 2023 - Appears unused

    """ Version prior to June 3, 2023 
    cursor.execute("SELECT * FROM Music WHERE OsFileName = ?", [key])
    ''' For LyricsTimeIndex Music Table Column we need to do:
        >>> json.dumps([1.2,2.4,3.6])
        '[1.2, 2.4, 3.6]'
        >>> json.loads('[1.2, 2.4, 3.6]')
        [1.2, 2.4, 3.6]
    '''
    # Test if parent fields available:
    # print('self.Artist:',self.Artist)
    # NameError: global name 'self' is not defined
    try:
        d = dict(cursor.fetchone())
    except TypeError:  # TypeError: 'NoneType' object is not iterable:
        d = None
        #MUSIC_ID = None  # June 3, 2023 - Appears unused
        print("sql.py get_lyrics() Bad key:", key)
        return None, None
    """
    """ June 3, 2023 - May get whitelisted version """
    #print("sql.py get_lyrics(key):", key)
    d = ofb.Select(key)
    if d is None:
        return None, None
    #MUSIC_ID = d["Id"]  # June 3, 2023 - Appears unused

    if d["LyricsTimeIndex"] is not None:
        return d["UnsynchronizedLyrics"], json.loads(d["LyricsTimeIndex"])
    else:
        return d["UnsynchronizedLyrics"], None


def music_get_row(key):
    # Get row using the MusicID
    cursor.execute("SELECT * FROM Music WHERE Id = ?", [key])

    try:
        row = dict(cursor.fetchone())
    except TypeError:  # TypeError: 'NoneType' object is not iterable:
        row = None
    if row is None:
        print('sql.py - music_get_row() not found:', key)
        return None

    return OrderedDict(row)


update_print_count = 10  # Change this number to 0 to show first 10 songs


def update_metadata(key, artist, album, song, genre, tracknumber, date, 
                    seconds, duration):
    """
        Update Music Table with metadata tags.
        Called from mserve.py and encoding.py

        Check if metadata has changed. If no changes return False.

        Update metadata in library and insert history record:
            'meta' 'init' for first time
            'meta' 'edit' for 2nd and subsequent changes
    """

    # noinspection SpellCheckingInspection

    # Crazy all the time spent encoding has to be decoded for SQLite3 or error:
    # sqlite3.ProgrammingError: You must not use 8-bit bytestrings unless you
    # use a text_factory that can interpret 8-bit bytestrings (like
    # text_factory = str). It is highly recommended that you instead just
    # switch your application to Unicode strings.
    # TODO: Check for Python 3 may be required because Unicode is default type
    #artist = artist.decode("utf8")  # Queensrÿche
    # inspection SpellCheckingInspection
    #album = album.decode("utf8")
    #song = song.decode("utf8")

    ''' June 28, 2023 - song.decode("utf-8") has been removed. Need to test '''
    if type(date) is str:
        if date != "None":  # See "She's No Angel" by April Wine.
            # Problem with date "1993-01-26"
            try:
                date = float(date)  # Dumb idea because it's year
            except ValueError:
                pass  # Leave date as string

    if genre is not None:
        genre = genre.decode("utf8")

    # Don't allow GIGO which required FixData del_music_ids() function June 2023
    if artist is None or album is None or song is None:
        return False
    if artist == NO_ARTIST_STR or album == NO_ARTIST_STR:
        return False
    if artist == NO_ALBUM_STR or album == NO_ALBUM_STR:
        return False

    """ Prior to June 3, 2023 - TODO Add to Whitelist if possible
    cursor.execute("SELECT * FROM Music WHERE OsFileName = ?", [key])
    try:
        d = dict(cursor.fetchone())
    except TypeError:  # TypeError: 'NoneType' object is not iterable:
        d = None
        print("sql.py update_metadata() Bad key:", key)
    """
    d = ofb.Select(key)
    if d is None:
        ''' June 3, 2023 - See if Whitelist can be created '''
        # File and Directory names with ":", "?", "/" and "." replaced with "_"
        fudged_artist = ext.legalize_dir_name(artist)
        fudged_album = ext.legalize_dir_name(album)
        fudged_song = key.split(os.sep)[-1]  # "song" S/B "99 song.ext"
        fudged_song = ext.legalize_song_name(fudged_song)
        white_key = fudged_artist + os.sep + fudged_album + os.sep + fudged_song

        e = ofb.Select(white_key)  # If white key works, use it in Whitelist
        if e is not None:
            #print("Found substitute key:", e['OsFileName'])
            ofb.SetWhitelist(key, white_key)
            key = white_key  # Use white_key instead of passed key
            d = e  # Replace d (None) with e (good dictionary of valid SQL) 
        else:
            #print('sql.py update_metadata() error no music ID for:', key)
            return False

    # Are we adding a new 'init' or 'edit' history record?
    if d['MetaArtistName'] is None:
        # This happens when song has never been played in mserve
        action = 'init'
        #print('\nSQL adding metadata for:', key)
        # June 6, 2023 not legalized for white_key:
        # SQL adding metadata for: Filter/The Very Best Things: 1995–2008/01 Hey Man Nice Shot.oga
    elif \
        artist       != d['MetaArtistName'] or \
        album        != d['MetaAlbumName'] or \
        song         != d['MetaSongName'] or \
        genre        != d['Genre'] or \
        str(tracknumber)  != str(d['TrackNumber']) or \
        date         != d['ReleaseDate'] or \
        seconds      != d['Seconds'] or \
            duration != d['Duration']:
        # To test, use kid3 to temporarily change track number
        # float(date) != d['ReleaseDate'] or \ <- They both could be None
        # Metadata hsa changed from last recorded version
        action = 'edit'

    else:
        return False  # Metadata same as library

    # For debugging, set update_print_count to 0. Otherwise set initial value to 10
    global update_print_count
    if update_print_count < 10:
        print('\nSQL updating metadata for:', key)
        print('artist type :', type(artist), 'album type :', type(album),
              'song type :', type(song), 'tracknumber type :', type(tracknumber))
        print('SQL type    :', type(d['MetaArtistName']), 'album type :',
              type(d['MetaAlbumName']), 'song type :', type(d['MetaSongName']),
              'tracknumber type :', type(d['TrackNumber']))
        print(artist, d['MetaArtistName'])
        print(album, d['MetaAlbumName'])
        print(song, d['MetaSongName'])
        print(genre, d['Genre'])
        print(tracknumber, d['TrackNumber'])
        print(date, d['ReleaseDate'])
        print(seconds, d['Seconds'])
        print(duration, d['Duration'])

        if artist != d['MetaArtistName']:
            print('artist:', artist, d['MetaArtistName'])
        elif album != d['MetaAlbumName']:
            print('album:', album, d['MetaAlbumName'])
        elif song != d['MetaSongName']:
            print('song:', song, d['MetaSongName'])
        elif genre != d['Genre']:
            print('genre:', genre, d['Genre'])
        elif str(tracknumber)  != str(d['TrackNumber']):
            print('tracknumber:', tracknumber, d['TrackNumber'])
        elif date != d['ReleaseDate']:
            print('date:', date, d['ReleaseDate'])
        elif seconds != d['Seconds']:
            print('seconds:', seconds, d['Seconds'])
        elif duration != d['Duration']:
            print('duration:', duration, d['Duration'])
        else:
            print('All things considered EQUAL')

    update_print_count += 1

    # Update metadata for song into library Music Table
    sql = "UPDATE Music SET MetaArtistName=?, MetaAlbumName=?, MetaSongName=?, \
           Genre=?, TrackNumber=?, ReleaseDate=?, Seconds=?, Duration=? \
           WHERE OsFileName = ?" 

    cursor.execute(sql, (artist, album, song, genre, tracknumber, date,
                         seconds, duration, key))
    con.commit()

    # Add history record
    # Time will be file's last modification time

    ''' Build full song path '''
    full_path = _START_DIR.encode("utf8") + key
    # Below not needed because "<No Album>" strings not in Music Table filenames
    # June 2, 2023, no longer relevant because rejected above.
    full_path = full_path.replace(os.sep + NO_ARTIST_STR, '')
    full_path = full_path.replace(os.sep + NO_ALBUM_STR, '')

    # os.stat gives us all of file's attributes
    stat = ext.stat_existing(full_path)
    if stat is None:
        print("sql.update_metadata(): File below doesn't exist:\n")
        for i in d:
            # Pad name with spaces for VALUE alignment
            print('COLUMN:', "{:<25}".format(i), 'VALUE:', d[i])
        return False  # Misleading because SQL music table was updated

    Size = stat.st_size                     # File size in bytes
    Time = stat.st_mtime                    # File's current mod time
    SourceMaster = _LODICT['name']
    SourceDetail = time.asctime(time.localtime(Time))
    Comments = "Found: " + time.asctime(time.localtime(time.time()))
    if seconds is not None:
        FloatSeconds = float(str(seconds))  # Convert from integer
    else:
        FloatSeconds = 0.0

    Count = 0

    # If adding, the file history record may be missing too.
    if action == 'init' and \
       not hist_check(d['Id'], 'file', action):
        hist_add(Time, d['Id'], _USER, 'file', action, SourceMaster,
                 SourceDetail, key, Size, Count, FloatSeconds,
                 Comments)

    # Add the meta Found or changed record
    '''
    print(time.time(), d['Id'], _USER, 'meta', action, SourceMaster, \
             SourceDetail, key, Size, Count, FloatSeconds, 
             Comments, sep=" # ")
    '''
    hist_add(Time, d['Id'], _USER, 'meta', action, SourceMaster,
             SourceDetail, key, Size, Count, FloatSeconds, 
             Comments)

    con.commit()

    return True  # Metadata was updated in SQL database


def music_id_for_song(key):
    # Get the MusicID matching song file's basename
    d = ofb.Select(key)
    if d is None:
        return 0  # Doesn't exist and is now blacklisted

    if d['Id'] == 0:
        print('music_id_for_song(key) error music ID is 0:', key)
        return 0
    else:
        return d['Id']  # The actual Music ID found

#==============================================================================
#
#       sql.py - History table processing
#
#==============================================================================


def hist_get_row(key):
    # Get the MusicID matching song file's basename
    hist_cursor.execute("SELECT * FROM History WHERE Id = ?", [key])

    try:
        row = dict(hist_cursor.fetchone())
    except TypeError:  # TypeError: 'NoneType' object is not iterable:
        row = None
    if row is None:
        print('sql.py - hist_get_row not found():', key)
        return None

    return OrderedDict(row)


def hist_add_time_index(key, time_list):
    """
        Add time index if 'init' doesn't exist.
        If time index does exist, add an 'edit' if it has changed.
    """
    # Get the MusicID matching song file's basename
    MusicId = music_id_for_song(key)
    if MusicId == 0:
        print('SQL hist_add_time_index(key) error no music ID for:', key)
        return False

    if hist_check(MusicId, 'time', 'init'):
        # We found a time initialization record to use as default
        Action = 'edit'
        print('sql.hist_add_time_index(key) edit time, init:', key, HISTORY_ID)
        hist_cursor.execute("SELECT * FROM History WHERE Id = ?", [HISTORY_ID])
        d = dict(hist_cursor.fetchone())
        try:
            d = dict(hist_cursor.fetchone())
        except TypeError:  # TypeError: 'NoneType' object is not iterable:
            d = None

        if d is None:
            print('sql.hist_add_time_index() error no History ID:', key,
                  HISTORY_ID)
            return False
        # TODO: Read music row's time_list and to see if it's changed.
        #       If it hasn't changed then return. This means we have to
        #       add history before we update music table. Or parent only
        #       updates music table when lyrics or time index changes. In this
        #       case another history record is required for 'lyrics', 'edit'.
    else:
        # Add time initialization record
        Action = 'init'
        d = hist_default_dict(key, 'access')
        if d is None:
            print('sql.hist_add_time_index() error creating default dict.')
            return False

    d['Count'] = len(time_list)
    Comments = Action + " time: " + time.asctime(time.localtime(time.time()))
    hist_add(time.time(), d['Id'], _USER, 'time', Action, d['SourceMaster'],
             d['SourceDetail'], key, d['Size'], d['Count'], d['Seconds'], 
             Comments)

    return True


def hist_add_shuffle(Action, SourceMaster, SourceDetail):
    Type = "playlist"
    # Action = 'shuffle'
    if Type == Action == SourceMaster == SourceDetail:
        return  # Above test for pycharm checking  
  


def hist_default_dict(key, time_type='access'):
    """ Construct a default dictionary used to add a new history record """

    cursor.execute("SELECT * FROM Music WHERE OsFileName = ?", [key])

    try:
        d = dict(cursor.fetchone())
    except TypeError:  # TypeError: 'NoneType' object is not iterable:
        d = None

    if d is None:
        print('SQL hist_default_dict() error no music row for:', key)
        return None

    hist = {}                               # History dictionary
    SourceMaster = _LODICT['name']
    hist['SourceMaster'] = SourceMaster

    ''' Build full song path '''
    full_path = START_DIR.encode("utf8") + d['OsFileName']
    # Below not needed because (No Artist / No Album) not in filenames
    # full_path = full_path.replace(os.sep + NO_ARTIST_STR, '')
    # full_path = full_path.replace(os.sep + NO_ALBUM_STR, '')

    # os.stat gives us all of file's attributes
    stat = os.stat(full_path)
    size = stat.st_size                     # File size in bytes
    hist['Size'] = size
    hist['Count'] = 0                       # Temporary use len(time_list)
    if time_type == 'access':
        Time = stat.st_atime                # File's current access time
    elif time_type == 'mod':
        Time = stat.st_mtime                # File's current mod time
    elif time_type == 'birth':
        Time = stat.st_mtime                # File's birth/creation time
    else:
        print('SQL hist_default_dict(key, time_type) invalid type:', time_type)
        return None

    SourceDetail = time.asctime(time.localtime(Time))
    hist['SourceDetail'] = SourceDetail
    # Aug 10/2021 - Seconds always appears to be None
    if Seconds is not None:
        FloatSeconds = float(str(Seconds))  # Convert from integer
    else:
        FloatSeconds = 0.0
    hist['Seconds'] = FloatSeconds

    return hist                             # Some dict fields aren't populated


def hist_delete_time_index(key):
    """
        All time indexes have been deleted.
        Check if history 'init' record exists. If so copy it and use 'delete'
        to add new history record.
    """
    # Get the MusicID matching song file's basename
    MusicId = music_id_for_song(key)
    if MusicId == 0:
        print('SQL hist_delete_time_index(key) error no music ID for:', key)
        return False

    if not hist_check(MusicId, 'time', 'init'):
        print('sql.hist_delete_time_index(key) error no time, init:', key)
        return False

    # We found a time initialization record to use as default
    print('sql.hist_delete_time_index(key) HISTORY_ID:', key, HISTORY_ID)

    hist_cursor.execute("SELECT * FROM History WHERE Id = ?", [HISTORY_ID])
    try:
        d = dict(hist_cursor.fetchone())
    except TypeError:  # TypeError: 'NoneType' object is not iterable:
        d = None

    if d is None:
        print('sql.hist_delete_time_index(key) error no History ID:', key,
              HISTORY_ID)
        return False

    Comments = "Removed: " + time.asctime(time.localtime(time.time()))
    hist_add(time.time(), d['Id'], _USER, 'time', 'remove', d['SourceMaster'],
             d['SourceDetail'], key, d['Size'], d['Count'], d['Seconds'], 
             Comments)

    return True


def hist_init_lost_and_found(START_DIR, USER, LODICT):
    """ Tool to initialize history time for all songs in database.
        This step just records 'file' and 'init' for OS song filename.
        If metadata present then 'meta' and 'init' also recorded.

        The time for 'init' is the files modification time which should be
            lowest time across all devices if synced properly.

        If a file is both lost and found in the same second and the metadata
            matches that simply means the file was renamed / moved.

        The same song can be found in multiple locations and smaller devices
            might have fewer songs that the master location.

    """

    song_count = 0
    add_count = 0
    add_meta_count = 0
    # History Table columns
    # Time = time.time()    # Aug 8/21 use time.time() instead of job start
    User = USER             # From location.py
    Type = 'file'           # This records OS filename into history
    Action = 'init'         # Means we "found" the file or it was renamed
    '''
    LODICT (location dictionary in memory) format as of April 13, 2021:
    DICT={'iid': iid, 'name': name, 'topdir': topdir, 'host': host, 'wakecmd': \
      wakecmd, 'testcmd': testcmd, 'testrep': testrep, 'mountcmd': \
      mountcmd, 'activecmd': activecmd, 'activemin': activemin}
    '''
    SourceMaster = LODICT['name']
    #  Aug 8/21 comment out fields below not used
    #SourceDetail = 'Today'  # Formatted time string "DDD MMM DD HH:MM:SS YYYY"
    #Target = '/path/file'   # Replaced with OS filename below
    #Size = 0                # File size in bytes
    #Count = 0               # Number of renaming of path/name/filename
    #Seconds = 0.0           # Song duration
    Comments = 'Automatically added by hist_init_lost_and_found()'

    # Select songs that have lyrics (Python 'not None:' = SQL 'NOT NULL')
    for row in cursor.execute('SELECT Id, OsFileName, OsModificationTime, ' +
                              'MetaSongName, Seconds FROM Music'):
        song_count += 1
        # Check if history already exists for song
        MusicId = row[0]
        if hist_check(MusicId, Type, Action):
            continue

        # Name our Music Table columns needed for History Table
        OsFileName = row[1] 
        # OsModificationTime = row[2]  # Us as default for found time  # Not used
        MetaSongName = row[3]       # If name not blank, we have metadata
        Seconds = row[4]            # Song Duration in seconds (INT)

        ''' TODO: What about PRUNED_SUBDIRS from mserve code?

        # Temporarily create SQL music tables until search button created.
        sql.CreateMusicTables(SORTED_LIST, START_DIR, PRUNED_SUBDIRS)
        '''

        ''' Build full song path '''
        full_path = START_DIR.encode("utf8") + OsFileName

        # os.stat gives us all of file's attributes
        stat = ext.stat_existing(full_path)
        if stat is None:
            print("\nsql.hist_init_lost_and_found() - File below doesn't exist:")
            names = cursor.description
            for i, name in enumerate(names):
                # Pad name with spaces for VALUE alignment
                print('COLUMN:', "{:<25}".format(name[0]), 'VALUE:', row[i])
            continue  # TODO: do "lost" phase, mark song as deleted somehow

        Size = stat.st_size                     # File size in bytes
        Time = stat.st_mtime                    # File's current mod time
        SourceDetail = time.asctime(time.localtime(Time))
        if Seconds is not None:
            FloatSeconds = float(str(Seconds))  # Convert from integer
        else:
            FloatSeconds = 0.0

        Count = 0
        Target = OsFileName

        # Add the Song Found row
        # Aug 8/21 use time.time() instead of job start time.
        hist_add(time.time(), MusicId, User, Type, Action, SourceMaster, SourceDetail, 
                 Target, Size, Count, FloatSeconds, Comments)
        add_count += 1

        if MetaSongName is not None:
            # Add the Metadata Found row
            hist_add(time.time(), MusicId, User, 'meta', Action, SourceMaster,
                     SourceDetail, OsFileName, Size, Count, FloatSeconds, 
                     Comments)
            add_meta_count += 1

    #print('Songs on disk:', song_count, 'Added count:', add_count, \
    #      'Added meta count:', add_meta_count)

    con.commit()                                # Save database changes


HISTORY_ID = None


def hist_check(MusicId, check_type, check_action):
    """ History table usage for Music Lyrics:

        VARIABLE        DESCRIPTION
        --------------  -----------------------------------------------------
        Id              Primary integer key auto-incremented
        Time            In system format with nano-second precision
                        filetime = (unix time * 10000000) + 116444736000000000
                        Secondary key
        MusicId         Link to primary key in Music Table usually rowid
                        For setting (screen, monitor, window, etc) the
                        MusicId is set to 0.
        User            User name, User ID or GUID varies by platform.
        Type            'file', 'catalog', 'link', 'index', 'checkout', 'song',
                        'lyrics', 'time', 'fine-tune', 'meta', 'resume', 
                        'volume', 'window', 'chron-state', 'hockey'
        Action          'copy', 'download', 'remove', 'burn', 'edit', 'play',
                        'scrape', 'init', 'shuffle', 'save', 'load', 'level',
                        'show', 'hide', 'On', 'Off'
                        NAME 
        SourceMaster    'Genius', 'Metro Lyrics', etc.
                        Device name, Playlist
        SourceDetail    '//genius.com' or 'www.metrolyrics.com', etc.
                        Location number, song names in order (soon music IDs)
        Target          'https://www.azlyrics.com/lyrics/greenday/wake...html'
        Size            Total bytes in downloaded text file
                        Duration of lyrics synchronized (end - start time)
        Count           Number of lines in downloaded text file
                        Number of lyrics lines synchronized
        Seconds         How many seconds the operation took Float
        Comments        For most records formatted date time
    """
    global HISTORY_ID

    for row in hist_cursor.execute("SELECT Id, Type, Action FROM History " +
                                   "INDEXED BY MusicIdIndex " +  # Line added May 16 2023
                                   "WHERE MusicId = ?", [MusicId]):
        Id = row[0]
        Type = row[1]
        Action = row[2]
        if Type == check_type and Action == check_action:
            HISTORY_ID = Id
            return True

    HISTORY_ID = 0
    return False                # Not Found


def get_config(Type, Action):
    """ Get configuration history using 'Type' + 'Action' key

        VARIABLE        DESCRIPTION
        --------------  -----------------------------------------------------
        Type - Action   'window' - library, playlist, history, encoding,
                                   results, sql_music, sql_history
        Type - Action   'resume' - LODICT[iid]. SourceMaster = Playing/Paused
                        'chron_state' - LODICT[iid]. SourceMaster = hide/show
                        'hockey_state' - LODICT[iid]. SourceMaster = On/Off
        Target          For Type='window' = geometry (x, y, width, height)
    """
    hist_cursor.execute("SELECT * FROM History INDEXED BY TypeActionIndex " +
                        "WHERE Type = ? AND Action = ? LIMIT 1", (Type, Action))
    try:
        d = dict(hist_cursor.fetchone())
    except TypeError:  # TypeError: 'NoneType' object is not iterable:
        d = None

    return d


def save_config(Type, Action="", SourceMaster="", SourceDetail="", Target="", 
                Size=0, Count=0, Seconds=0.0, Comments=""):
    """ Save configuration history using 'Type' + 'Action' key
    """
    # Check if record exists
    d = get_config(Type, Action)
    if d is None:
        hist_add(time.time(), 0, g.USER, Type, Action, SourceMaster,
                 SourceDetail, Target, Size, Count, Seconds, Comments)
        return

    cmd = "UPDATE History SET Time=?, SourceMaster=?, SourceDetail=?, \
        Target=?, Size=?, Count=?, Seconds=?, Comments=? WHERE Id = ?"
    hist_cursor.execute(cmd, (time.time(), SourceMaster, SourceDetail, Target,
                              Size, Count, Seconds, Comments, d['Id']))
    con.commit()


def hist_last_time(check_type, check_action):
    """ Get the last time the type + action occurred

        Primarily used to get the last time an action was added / updated in
        history. If this time is greater than time top directory was
        last changed then refresh not required.

    """
    global HISTORY_ID

    for row in hist_cursor.execute("SELECT * FROM History " +
                                   "INDEXED BY TimeIndex " +
                                   "ORDER BY Time DESC"):
        d = dict(row)
        Id = d['Id']
        Type = d['Type']
        Action = d['Action']
        if Type == check_type and Action == check_action:
            HISTORY_ID = Id
            return d['Time']

    HISTORY_ID = 0
    return None                # Not Found


def hist_add(Time, MusicId, User, Type, Action, SourceMaster, SourceDetail, 
             Target, Size, Count, Seconds, Comments):
    """ Add History Row for Synchronizing Lyrics Time Indices.
    """
    # DEBUG:
    # InterfaceError: Error binding parameter 1 - probably unsupported type.
    # print("Time, MusicId, User, Type, Action, SourceMaster, SourceDetail,")
    # print("Target, Size, Count, Seconds, Comments:")
    # print(Time, MusicId, User, Type, Action, SourceMaster, SourceDetail,
    #      Target, Size, Count, Seconds, Comments)
    sql = "INSERT INTO History (Time, MusicId, User, Type, Action, \
           SourceMaster, SourceDetail, Target, Size, Count, Seconds, Comments) \
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    hist_cursor.execute(sql, (Time, MusicId, User, Type, Action, SourceMaster,
                              SourceDetail, Target, Size, Count, Seconds,
                              Comments))


def hist_delete_type_action(Type, Action):
    """ Delete History Rows for matching Type and Action.
        Created to get rid of thousands of 'meta' 'edit' errors
        NOTE:   Don't use this anymore
                Use sqlitebrowser instead
                Keep this as boilerplate for next time
    """

    # TODO: Use "INDEXED BY TypeActionIndex " +
    sql = "DELETE FROM History WHERE Type=? AND Action=?"

    hist_cursor.execute(sql, (Type, Action))
    deleted_row_count = hist_cursor.rowcount
    print('hist_delete_type_action(Type, Action):', Type, Action,
          'deleted_row_count:', deleted_row_count)
    con.commit()


def hist_init_lyrics_and_time(START_DIR, USER, LODICT):
    """ Tool to initialize history time for all songs that have lyrics.
        The time will be the last file access time.

        If lyric time indices are set the lyrics webscrape is 5 minutes earlier
        and the index time is the file access time.

        Assume lyrics source is Genius but could have been clipboard or user
        direct entry.
    """
    song_count = 0
    add_count = 0
    add_time_count = 0
    # History Table columns
    # Time = time.time()    # Aug 8/21 not used
    User = USER             # From location.py
    Type = 'lyrics'
    Action = 'scrape'
    SourceMaster = 'Genius'  # Website lyrics were scraped from
    # Aug 8/21 comment out fields below not used
    # SourceDetail = 'Today'  # Formatted time string "DDD MMM DD HH:MM:SS YYYY"
    # Target = 'https://genius.com/artist/album/song.html'
    # Size = 0
    # Count = 0
    # Seconds = 0.0
    Comments = 'Automatically added by hist_init_lyrics_and_time()'

    # Select songs that have lyrics (Python 'not None:' = SQL 'NOT NULL')
    for row in cursor.execute("SELECT Id, OsFileName, UnsynchronizedLyrics, " +
                              "LyricsTimeIndex, OsAccessTime, Seconds FROM " +
                              "Music WHERE UnsynchronizedLyrics IS NOT NULL"):
        song_count += 1
        # Check if history already exists for song
        MusicId = row[0]
        if hist_check(MusicId, Type, Action):
            continue

        # Name our Music Table columns needed for History Table
        OsFileName = row[1] 
        UnsynchronizedLyrics = row[2]
        LyricsTimeIndex = row[3]
        # OsAccessTime = row[4]                   # At time of Music Row creation
        Seconds = row[5]                        # Song Duration

        ''' TODO: What about PRUNED_SUBDIRS from mserve code?

        # Temporarily create SQL music tables until search button created.
        sql.CreateMusicTables(SORTED_LIST, START_DIR, PRUNED_SUBDIRS)
        '''

        ''' Build full song path '''
        full_path = START_DIR.encode("utf8") + OsFileName
        # Below not needed because (No Xxx) stubs not in Music Table filenames
        full_path = full_path.replace(os.sep + NO_ARTIST_STR, '')
        full_path = full_path.replace(os.sep + NO_ALBUM_STR, '')

        # os.stat gives us all of file's attributes
        stat = os.stat(full_path)
        # size = stat.st_size                     # Not used
        # converted = float(size) / float(CFG_DIVISOR_AMT)
        # fsize = str(round(converted, CFG_DECIMAL_PLACES))

        Time = stat.st_atime                    # File's current access time
        SourceDetail = time.asctime(time.localtime(Time))
        Size = len(UnsynchronizedLyrics)        # Can change after user edits
        Count = UnsynchronizedLyrics.count('\n')
        Target = 'https://genius.com/' + OsFileName

        if LyricsTimeIndex is None:
            time_count = 0
            time_index_list = None
        else:
            time_index_list = json.loads(LyricsTimeIndex)
            time_count = len(time_index_list)
            if time_count < 5:
                print('time count:', time_count, Target)

        # Estimate 4 seconds to download lyrics (webscrape)
        hist_add(Time, MusicId, User, Type, Action, SourceMaster, SourceDetail, 
                 Target, Size, Count, 4.0, Comments)
        add_count += 1

        if time_count > 0:
            Time = stat.st_atime + 300          # 5 minutes to sync lyrics
            duration = time_index_list[-1] - time_index_list[0]
            Size = int(duration)                # Amount of time synchronized
            Count = len(time_index_list)        # How many lines synchronized
            '''
            As of April 12, 2021:
            DICT={'iid': iid, 'name': name, 'topdir': topdir, 'host': host, 'wakecmd':
              wakecmd, 'testcmd': testcmd, 'testrep': testrep, 'mountcmd': 
              mountcmd, 'activecmd': activecmd, 'activemin': activemin}
            '''
            hist_add(Time, MusicId, User, 'time', 'edit', LODICT['name'],
                     LODICT['iid'], OsFileName, Size, Count, float(Seconds), 
                     Comments)
            add_time_count += 1

    #print('Songs with lyrics:', song_count, 'Added count:', add_count, \
    #      'Added time count:', add_time_count)
    con.commit()


# ===============================  AUTHENTICATION =============================

class Authorization:
    """ NOT USED YET - Initially designed for MusicBrainz authorization """
    def __init__(self, toplevel, organization, http, message, tt=None, thread=None):
        self.top_level = toplevel
        self.organization = organization
        self.http = http
        self.message = message
        self.tt = tt                        # Tooltips
        self.thread = thread                # Thread run during idle loop (Tooltips)

        # Retrieved from file and read from screen
        self.user = None                    # Your name, company name or your website
        self.email = None                   # Your email if throttling limit exceeded

        # Columns in in SQL History Table Row
        self.HistoryId = None               # Primary Key Row Number integer
        self.MusicId = 0                    # Only song files have a Music ID.
        self.User = g.USER                  # User name when mserve started up
        self.Type = "User ID"
        self.Action = organization          # MusicBrainz
        self.SourceMaster = self.user       # User ID website knows you by
        self.SourceDetail = self.email      # Your email if throttling limit exceeded
        self.Target = http                  # https://musicbrainz.org
        # Size, Count, Seconds & Comments are hard coded below

    def Init(self):
        """ Check history table Action: "User ID"
                                Type:   self.organization

            Return True if found, False if no record
        """
        if self.GetUser():
            return True

        # Need prompt for message.AskString() for self.user and self.email
        # Neither can be blank
        print("sql.py Authorization.Init(): No '" + self.Type +
              "' for:", self.Action)
        return False

    def GetUser(self):
        """ Get User ID
        """
        if hist_check(0, self.Type, self.Action):
            # If record exists, we get HISTORY_ID set to row number primary key
            hist_cursor.execute("SELECT * FROM History WHERE Id = ?",
                                [HISTORY_ID])
            try:
                d = dict(hist_cursor.fetchone())
            except TypeError:  # TypeError: 'NoneType' object is not iterable:
                d = None

            if d is None:
                # If we get here there is programmer error
                print("sql.py Authorization.GetUser(): No '" + self.Type +
                      "' for:", self.Action)
                return False
            self.HistoryId = HISTORY_ID
            self.user  = self.SourceMaster = d['SourceMaster']
            self.email = self.SourceDetail = d['SourceDetail']
            return True
        else:
            # First time add the record
            return False

    def Save(self):
        """ Check history table master code: "User ID"
                                detail code: self.organization

            Return True if found, False if no record
        """
        if self.SourceMaster is None:
            # First time add the record
            hist_add(time.time(), 0, _USER, self.Type, self.Action, self.user,
                     self.email, self.Target, 0, 0, 0.0,
                     "User Authorization record created")
            con.commit()
            return True

        ''' We have the existing history record, simply replace the fields '''
        sql = "UPDATE History SET Time=?, SourceMaster=?, SourceDetail=?, \
              Comments=? WHERE Id = ?"

        cursor.execute(sql, (time.time(), self.user, self.email,
                       "User Authorization record updated", self.HistoryId))
        con.commit()


# =================================  WEBSCRAPE  ===============================


class Webscrape:
    """
                    not used - Future Class for webscrape.py
    """
    def __init__(self, music_id):
        # All columns in history row, except primary ID auto assigned.
        self.MusicId = music_id
        self.User = None
        self.Type = None
        self.Action = None
        self.SourceMaster = None
        self.SourceDetail = None
        self.Target = None
        self.Size = None
        self.Count = None
        self.Comments = None

    def set_ws_parm(self, music_id):
        """ Save Webscrape parameters - Currently in mserve.py:

            MusicId = sql.music_id_for_song(self.work_sql_key)
            sql.hist_add(time.time(), MusicId, USER,
                         'scrape', 'parm', artist, song,
                         "", 0, 0, 0.0,
                         time.asctime(time.localtime(time.time())))
            ext_name = 'python webscrape.py'
            self.lyrics_pid = ext.launch_command(ext_name,
                                                 toplevel=self.play_top)

        """
        pass

    def get_ws_parm(self, music_id):
        """ Get Webscrape parameters
            now = time.time()
            last_time = sql.hist_last_time('scrape', 'parm')
            hist_row = sql.hist_get_row(sql.HISTORY_ID)
            lag = now - last_time
            if lag > 1.0:
                print('It took more than 1 second for webscrape to start:', lag)
            else:
                print('webscrape start up time:', lag)
                pass
            print(hist_row)

        """
        pass

    def set_ws_result(self, music_id):
        """ Save Webscrape results
        """
        pass

    def get_ws_result(self, music_id):
        """ Get Webscrape results
        """
        pass

    def read_music_id(self, music_id):

        """
        ==========================   COPY from webscrape.py   =========================
            
        # Web scraping song lyrics IPC file names
        SCRAPE_CTL_FNAME    = '/run/user/" + g.USER_ID + "/mserve.scrape_ctl.json'
        SCRAPE_LIST_FNAME   = '/run/user/" + g.USER_ID + "/mserve.scrape_list.txt'
        SCRAPE_LYRICS_FNAME = '/run/user/" + g.USER_ID + "/mserve.scrape_lyrics.txt'
        
        # Names list is used in our code for human readable formatting
        NAMES_LIST =   ['Metro Lyrics',     'AZ Lyrics',        'Lyrics',
                        'Lyrics Mode',      'Lets Sing It',     'Genius',
                        'Musix Match',      'Lyrics Planet']
        
        # Website list is used in webscrape.py for internet formatting
        WEBSITE_LIST = ['www.metrolyrics.com', 'www.azlyrics.com',    'www.lyrics.com',
                        'www.lyricsmode.com',  'www.letssingit.com',  '//genius.com', 
                        'www.musixmatch.com',  'www.lyricsplanet.com']
        
        # Empty control list (template)
        CTL_LIST = [{} for _ in range(len(WEBSITE_LIST))]
        #CTL_LIST = [ {}, {}, {}, {}, {}, {}, {}, {} ]
        
        # If we try to print normally an error occurs when launched in background
        #print("CTL_LIST:", CTL_LIST, file=sys.stderr)
        
        # Empty control list dictionary element (template)
        WS_DICT = { "name":"", "website":"", "link":"", "flag":"" }
        ''' flag values: preference passed to webscrape.py. result passed to mserve
            preference:  1-8 try to get lyrics in this order, 'skip' = skip site
            result:      'found' lyrics returned. 'available' lyrics can be returned
                         'not found' no link or link is empty (eg artist but no lyrics)
        '''

def save_ctl():
    '''
        Save Control file containing list of dictionaries

        USED by mserve and webscrape.py
            mserve passes previous list of names with flags to scrape.
            webscrape.py passes back name of website that was scraped.
            webscrape.py passes names of websites that CAN BE scraped.
    '''
    with open(SCRAPE_CTL_FNAME, "w") as ctl:
        ctl.write(json.dumps(CTL_LIST))


def load_ctl():
    '''
        Return contents of CTL file or empty list of dictionaries
    '''
    data = CTL_LIST
    if os.path.isfile(SCRAPE_CTL_FNAME):
        with open(SCRAPE_CTL_FNAME, "r") as ctl:
            data = json.loads(ctl.read())

    return data


"""
        pass


# ==============================================================================
#
#       PrettyMusic, PrettyHistory & PrettyTreeHeading classes
#
#       Headings and indented field key / values
#
# ==============================================================================


class PrettyMusic:

    def __init__(self, sql_row_id, calc=None):
        """ 
            Build a pretty dictionary with user friendly field names
            Values are from current treeview row for SQL Row

            The pretty dictionary is passed to mserve.py functions.

        """

        self.calc = calc  # Calculated fields callback function
        self.dict = OrderedDict()  # Python 2.7 version not needed in 3.7
        self.scrollbox = None  # custom scrollbox for display
        self.search = None  # search text

        # List of part section starting positions in field display
        self.part_start = [0]  # First heading starts at field #0

        # List of part section headings at part_start[] list above
        self.part_names = ['SQL and Operating System Information',
                           'Metadata (available after song played once)',
                           'Lyrics score (usually after Webscraping)',
                           'History Time - Row Number      ' +
                           ' | Type - Action - Master - Detail - Comments',
                           'Metadata modified']
        # List of part colors - applied to key names in that part
        self.part_color = ['red',
                           'blue',
                           'green',
                           'red',
                           'blue']
                            # Calculated fields are assigned green

        # Get Music Table row, remove commas
        key = sql_row_id.replace(',', '')
        #print("sql_row_id:", sql_row_id, 'key:', key)
        # NOTE: This isn't using OsFileName key so ofb.Select() won't work
        cursor.execute("SELECT * FROM Music WHERE Id = ?", [key])

        try:  # NOTE: This isn't using OsFileName key so ofb.Select() won't work
            d = dict(cursor.fetchone())
        except TypeError:  # TypeError: 'NoneType' object is not iterable:
            d = None
        if d is None:
            print('sql.py.PrettyMusic() - No SQL for Music Table Id:', key)
            return  # Dictionary will be empty

        self.dict['SQL Music Row Id'] = sql_format_value(d['Id'])
        # 'SQL Music Row Id' is same name in PrettyHistory and is a lookup key
        self.dict['OS Filename'] = sql_format_value(d['OsFileName'])
        self.dict['File size'] = sql_format_int(d['OsFileSize'])
        self.dict['Last Access time'] = sql_format_date(d['OsAccessTime'])
        self.dict['Modification time'] = sql_format_date(d['OsModificationTime'])
        self.dict['Creation time'] = sql_format_date(d['OsCreationTime'])
        # Need modification to set creation time to last modified time if older
        self.part_start.append(len(self.dict))
        self.dict['Artist'] = sql_format_value(d['MetaArtistName'])
        self.dict['Album'] = sql_format_value(d['MetaAlbumName'])
        self.dict['Song Name'] = sql_format_value(d['MetaSongName'])
        self.dict['Album Track'] = sql_format_value(d['TrackNumber'])

        self.part_start.append(len(self.dict))
        if d["LyricsTimeIndex"] is None:
            time_index_list = ["No time index"]  # Nothing prints yet.
        else:
            time_index_list = json.loads(d["LyricsTimeIndex"])

        if d["UnsynchronizedLyrics"] is None:
            self.dict['Lyrics score'] = "Webscrape for lyrics not completed."
        else:
            lyrics = d["UnsynchronizedLyrics"]
            for i, line in enumerate(lyrics.splitlines()):
                # If time index exists, put value in front of lyric line
                try:
                    self.dict["{:.2f}".format(time_index_list[i])] = line
                except (IndexError, ValueError):
                    # IndexError: list index out of range
                    # ValueError: Unknown format code 'f' for object of type 'unicode'
                    self.dict['line # ' + str(i + 1)] = line

        self.part_start.append(len(self.dict))

        ''' SAMPLE FROM ABOVE sql = 
        "INSERT INTO History (Time, MusicId, User, Type, Action, \
           SourceMaster, SourceDetail, Target, Size, Count, Seconds, Comments) \
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    hist_cursor.execute(sql, (Time, MusicId, User, Type, Action, SourceMaster,
                              SourceDetail, Target, Size, Count, Seconds,
                              Comments))
        '''
        hist_cursor.execute("SELECT * FROM History INDEXED BY MusicIdIndex \
                            WHERE MusicId = ?", (d['Id'],))
        rows = hist_cursor.fetchall()
        for sql_row in rows:
            row = dict(sql_row)
            #print("TODO: finish populating song history into Pretty Music")
            #print("Target:", type(row['Target']), row['Target'])
            #print("Comments:", type(row['Comments']), row['Comments'])
            self.dict[sql_format_date(row['Time']) + " - " + str(row['Id'])] = \
                row['Type'] + " - " + row['Action'] + " - " + row['SourceMaster'] + " - " + \
                row['SourceDetail'] + " - " + row['Target'] + " - " + row['Comments']

        if self.calc is not None:
            self.calc(self.dict)  # Call external function passing our dict
            # print("self.calc(self.dict)  # Call external function passing our dict")

        # print('\n======================  pretty  =====================\n')
        # print(json.dumps(self.dict, indent=2))


class PrettyHistory:

    def __init__(self, sql_row_id, calc=None):
        """ 
            Build a pretty dictionary with user friendly field names
            Values are from current treeview row for SQL Row

            The pretty dictionary is passed to mserve.py functions.

        """

        self.calc = calc  # Calculated fields such as delete_on
        self.dict = OrderedDict()  # Python 2.7 version not needed in 3.7
        self.scrollbox = None  # custom scrollbox for display
        self.search = None  # search text

        # List of part section starting positions in field display
        self.part_start = [0]  # First heading starts at field #0

        # List of part section headings at part_start[] list above
        self.part_names = ['SQL Information',
                           'Time',
                           'History Category',
                           'Source and Target Data',
                           'Processing Details']
        # List of part colors - applied to key names in that part
        self.part_color = ['red',
                           'blue',
                           'green',
                           'red',
                           'blue']
                            # Calculated fields are assigned green

        # Get Music Table row, remove commas
        key = sql_row_id.replace(',', '')
        #print("sql_row_id:", sql_row_id, 'key:', key)
        hist_cursor.execute("SELECT * FROM History WHERE Id = ?", [key])

        try:
            d = dict(hist_cursor.fetchone())
        except TypeError:  # TypeError: 'NoneType' object is not iterable:
            d = None
        if d is None:
            print('sql.py.PrettyHistory() - No SQL for History Table Id:', key)
            return

        self.dict['SQL History Row Id'] = sql_format_value(d['Id'])
        self.dict['SQL Music Row Id'] = sql_format_value(d['MusicId'])
        self.dict['User'] = sql_format_value(d['User'])
        # 'SQL Music Row Id' is same name in PrettyMusic and is a lookup key

        self.part_start.append(len(self.dict))
        self.dict['Human Time'] = sql_format_date(d['Time'])
        self.dict['Time in seconds'] = sql_format_value(d['Time'])
        fmt_time = datetime.datetime.fromtimestamp(d['Time'])
        self.dict['System Time'] = fmt_time.strftime("%c")

        self.part_start.append(len(self.dict))
        self.dict['Record Type'] = sql_format_value(d['Type'])
        self.dict['Action'] = sql_format_value(d['Action'])

        self.part_start.append(len(self.dict))
        self.dict['Master Source Code'] = sql_format_value(d['SourceMaster'])
        self.dict['Detail Source Code'] = sql_format_value(d['SourceDetail'])
        self.dict['Target'] = sql_format_value(d['Target'])

        self.part_start.append(len(self.dict))
        self.dict['Size'] = sql_format_int(d['Size'])
        self.dict['Count'] = sql_format_int(d['Count'])
        self.dict['Comments'] = sql_format_value(d['Comments'])
        self.dict['Seconds'] = sql_format_value(d['Seconds'])

        if self.calc is not None:
            self.calc(self.dict)  # Call external function passing our dict
            # print("self.calc(self.dict)  # Call external function passing our dict")

        # print('\n======================  pretty  =====================\n')
        # print(json.dumps(self.dict, indent=2))


class PrettyTreeHeading:

    def __init__(self, column_dict):
        """ 
            Display data dictionary for selected heading.
            Build a pretty dictionary with user friendly field names
            Use column dictionary that was passed to Tkinter.
            The pretty dictionary is passed to mserve.py functions.
        """

        self.calc = None  # Calculated fields not for column data dictionary
        self.dict = OrderedDict()  # Python 2.7 version not needed in 3.7
        self.scrollbox = None  # scrollbox for display defined later
        self.search = None  # Not used but needed for tkinter_display()

        # Data dictionary for treeview column format is simple
        self.part_start = [0]  # Only 1 part
        self.part_names = ['Tkinter Treeview - Column Data Dictionary']
        self.part_color = ['red']
        for key, value in column_dict.iteritems():
            self.dict[key] = sql_format_value(value)


class PrettyMeta:

    def __init__(self, meta_dict):
        """ 
            Display data dictionary for selected heading.
            Build a pretty dictionary with user friendly field names
            Use column dictionary that was passed to Tkinter.
            RAW DATA:
               Input #0, mov,mp4,m4a,3gp,3g2,mj2, from '/media/rick/SANDISK128/Music/Men At Work/Contraband -
               The Best Of Men At Work/14 Man With Two Hearts.m4a':
               Metadata:
                 major_brand     : M4A
                 minor_version   : 0
                 compatible_brands: M4A mp42isom
                 creation_time   : 2011-02-27 12:05:58
                 title           : Man With Two Hearts
                 artist          : Men At Work
                 composer        : Colin Hay
                 album           : Contraband - The Best Of Men At Work
                 genre           : Pop
                 track           : 14/16
                 disc            : 1/1
                 date            : 1984
                 compilation     : 0
                 gapless_playback: 0
                 encoder         : iTunes 10.0.1.22, QuickTime 7.6.8
                 iTunSMPB        :  00000000 00000840 000000E4 00000000009E06DC 00000000 00000000
                 00000000 00000000 00000000 00000000 00000000 00000000
                 Encoding Params : vers
                 iTunNORM        :  00001110 000011B9 00009226 0000CBAB 0002B4B2 00035A23 00008000
                 00007FFF 0000FC3E 00000929
                 iTunes_CDDB_IDs : 16++
                 UFIDhttp://www.cddb.com/id3/taginfo1.html: 3CD3N27S7396714U2686A83124FE1E51E62C229DF55B180DA9EP6
               Duration: 00:03:54.89, start: 0.000000, bitrate: 265 kb/s
                 Stream #0:0(und): Audio: aac (LC) (mp4a / 0x6134706D), 44100 Hz, stereo, fltp, 262 kb/s (default)
                 Metadata:
                   creation_time   : 2011-02-27 12:05:58
                 Stream #0:1: Video: png, rgba(pc), 115x115, 90k tbr, 90k tbn, 90k tbc
        """

        self.calc = None  # Calculated fields not for column data dictionary
        self.dict = OrderedDict()  # Python 2.7 version not needed in 3.7
        self.scrollbox = None  # scrollbox for display defined later
        self.search = None  # Not used but needed for tkinter_display()

        # Data dictionary for treeview column format is simple
        self.part_start = [0]
        self.part_names = ['Source', 'Metadata', 'Encoding']
        self.part_color = ['red', 'blue', 'green']
        curr_line = 0
        for key, value in meta_dict.iteritems():
            curr_line += 1
            self.dict[key] = sql_format_value(value)
            if key.startswith("INPUT #"):
                # Set next section start
                if len(self.part_start) == 1:
                    # Assume only 1 input source
                    self.part_start.append(curr_line)
                else:
                    # Next section starts after last input.
                    self.part_start[1] = curr_line
            if key.startswith("DURATION"):
                # Section starts at this index offset
                self.part_start.append(curr_line - 1)


def sql_format_value(value):

    try:
        formatted = str(value)  # Convert from int
    except UnicodeEncodeError:
        formatted = value  # Already string
    # return formatted.encode('utf8')
    # TypeError: coercing to Unicode: need string or buffer, int found
    return formatted


def sql_format_int(value):

    if value is None:
        return None  # Do we want to return empty string instead?

    try:
        formatted = format(value, ",")
    except UnicodeEncodeError:
        formatted = value  # Already string
    except ValueError:
        formatted = "sql.py.sql_format_int() Error: " + sql_format_value(value)

    return formatted


def sql_format_date(value):

    if value is None:
        return None  # Do we want to return empty string instead?

    try:
        formatted = tmf.ago(value)
    except UnicodeEncodeError:
        formatted = value  # Already string

    return formatted


def tkinter_display(pretty):
    """ Popup display all values in pretty print format
        Uses new tkinter window with single text entry field

        Requires ordered dict and optional lists specifying sections
        (parts) the part names and part colors for key names.

        IDENTICAL function in ~/bserve/gmail_api.py

    """

    # Allow program changes to scrollable text widget
    pretty.scrollbox.configure(state="normal")
    pretty.scrollbox.delete('1.0', 'end')  # Delete previous entries

    curr_key = 0  # Current key index
    curr_level = 0  # Current dictionary part
    curr_color = 'black'
    # for key, value in pretty.dict.iteritems():    # Don't use iteritems
    for key in pretty.dict:  # Don't need iteritems on ordered dict
        if curr_key == pretty.part_start[curr_level]:
            curr_level_name = pretty.part_names[curr_level]
            curr_color = pretty.part_color[curr_level]
            pretty.scrollbox.insert("end", curr_level_name + "\n")
            # pretty.scrollbox.highlight_pattern(curr_level_name, 'yellow')
            curr_level += 1

            if curr_level >= len(pretty.part_start):
                curr_level = len(pretty.part_start) - 1
                # We are in last part so no next part to check
                # print('resetting curr_level at:', key)

        # Insert current key and value into text widget
        # TclError: character U+1f913 is above the range (U+0000-U+FFFF) allowed by Tcl
        pretty.scrollbox.insert("end", u"\t" + key + u":\t" +
                                pretty.dict[key] + u"\n", u"margin")

        pretty.scrollbox.highlight_pattern(key + u':', curr_color)
        curr_key += 1  # Current key index

    if pretty.search is not None:
        # NOTE: yellow, cyan and magenta are defined to highlight background
        pretty.scrollbox.highlight_pattern(pretty.search, "yellow")

    # Don't allow changes to displayed selections (test copy clipboard)
    pretty.scrollbox.configure(state="disabled")


def music_treeview():
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

    music_treeview_list = [

      OrderedDict([
        ("column", "row_id"), ("heading", "Row ID"), ("sql_table", "Music"),
        ("var_name", "Id"), ("select_order", 0), ("unselect_order", 1),
        ("key", False), ("anchor", "e"), ("instance", int), ("format", "{:,}"),
        ("display_width", 80), ("display_min_width", 60),
        ("display_long", None), ("stretch", 0)]),  # 0=NO, 1=YES

      OrderedDict([
        ("column", "os_filename"), ("heading", "OS Filename"), ("sql_table", "Music"),
        ("var_name", "OsFileName"), ("select_order", 0), ("unselect_order", 2),
        ("key", True), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 300), ("display_min_width", 200),
        ("display_long", None), ("stretch", 0)]),  # 0=NO, 1=YES

      OrderedDict([
        ("column", "os_atime"), ("heading", "Access Time"), ("sql_table", "Music"),
        ("var_name", "OsAccessTime"), ("select_order", 0), ("unselect_order", 3),
        ("key", False), ("anchor", "w"), ("instance", float), ("format", "date"),
        ("display_width", 300), ("display_min_width", 200),
        ("display_long", None), ("stretch", 0)]),  # 0=NO, 1=YES

      OrderedDict([
        ("column", "os_mtime"), ("heading", "Mod Time"), ("sql_table", "Music"),
        ("var_name", "OsModificationTime"), ("select_order", 0), ("unselect_order", 4),
        ("key", False), ("anchor", "w"), ("instance", float), ("format", "{0:,.0f}"),
        ("display_width", 180), ("display_min_width", 120),
        ("display_long", None), ("stretch", 0)]),

      OrderedDict([
        ("column", "os_ctime"), ("heading", "Create Time"), ("sql_table", "Music"),
        ("var_name", "OsCreationTime"), ("select_order", 0), ("unselect_order", 5),
        ("key", False), ("anchor", "e"), ("instance", float),
        ("format", "{0:,.0f}"), ("display_width", 180),
        ("display_min_width", 120), ("display_long", None), ("stretch", 0)]),

      OrderedDict([
        ("column", "os_file_size"), ("heading", "File Size"), ("sql_table", "Music"),
        ("var_name", "OsFileSize"), ("select_order", 0), ("unselect_order", 6),
        ("key", False), ("anchor", "e"), ("instance", int), ("format", "{:,}"),
        ("display_width", 150), ("display_min_width", 120),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "artist"), ("heading", "Artist"), ("sql_table", "Music"),
        ("var_name", "MetaArtistName"), ("select_order", 0), ("unselect_order", 7),
        ("key", False), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 200), ("display_min_width", 140),
        ("display_long", None), ("stretch", 1)]),  # 0=NO, 1=YES

      OrderedDict([
        ("column", "album"), ("heading", "Album"), ("sql_table", "Music"),
        ("var_name", "MetaAlbumName"), ("select_order", 0), ("unselect_order", 8),
        ("key", False), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 200), ("display_min_width", 140),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "song_name"), ("heading", "Song Name"), ("sql_table", "Music"),
        ("var_name", "MetaSongName"), ("select_order", 0), ("unselect_order", 9),
        ("key", False), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 200), ("display_min_width", 140),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "release_date"), ("heading", "Release Date"), ("sql_table", "Music"),
        ("var_name", "ReleaseDate"), ("select_order", 0), ("unselect_order", 10),
        ("key", False), ("anchor", "w"), ("instance", float), ("format", "{0:,.0f}"),
        ("display_width", 180), ("display_min_width", 120),
        ("display_long", None), ("stretch", 0)]),

      OrderedDict([
        ("column", "original_date"), ("heading", "Original Date"), ("sql_table", "Music"),
        ("var_name", "OriginalDate"), ("select_order", 0), ("unselect_order", 11),
        ("key", False), ("anchor", "w"), ("instance", float), ("format", "{0:,.0f}"),
        ("display_width", 180), ("display_min_width", 120),
        ("display_long", None), ("stretch", 0)]),

      OrderedDict([
        ("column", "genre"), ("heading", "Genre"), ("sql_table", "Music"),
        ("var_name", "Genre"), ("select_order", 0), ("unselect_order", 12),
        ("key", False), ("anchor", "center"), ("instance", str), ("format", None),
        ("display_width", 160), ("display_min_width", 140),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "seconds"), ("heading", "Seconds"), ("sql_table", "Music"),
        ("var_name", "Seconds"), ("select_order", 0), ("unselect_order", 13),
        ("key", False), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 160), ("display_min_width", 140),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "duration"), ("heading", "Duration"), ("sql_table", "Music"),
        ("var_name", "Duration"), ("select_order", 0), ("unselect_order", 14),
        ("key", False), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 160), ("display_min_width", 140),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "play_count"), ("heading", "Play Count"), ("sql_table", "Music"),
        ("var_name", "PlayCount"), ("select_order", 0), ("unselect_order", 15),
        ("key", False), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 160), ("display_min_width", 110),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "track_number"), ("heading", "Track Number"), ("sql_table", "Music"),
        ("var_name", "TrackNumber"), ("select_order", 0), ("unselect_order", 16),
        ("key", False), ("anchor", "e"), ("instance", str), ("format", None),
        ("display_width", 140), ("display_min_width", 100),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "rating"), ("heading", "Rating"), ("sql_table", "Music"),
        ("var_name", "Rating"), ("select_order", 0), ("unselect_order", 17),
        ("key", False), ("anchor", "w"), ("instance", int), ("format", "{:,}"),
        ("display_width", 120), ("display_min_width", 80),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "lyrics"), ("heading", "Lyrics"), ("sql_table", "Music"),
        ("var_name", "UnsynchronizedLyrics"), ("select_order", 0), ("unselect_order", 18),
        ("key", False), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 200), ("display_min_width", 140),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "time_index"), ("heading", "Time Index"), ("sql_table", "Music"),
        ("var_name", "LyricsTimeIndex"), ("select_order", 0), ("unselect_order", 19),
        ("key", False), ("anchor", "w"), ("instance", list), ("format", None),
        ("display_width", 160), ("display_min_width", 140),
        ("display_long", None), ("stretch", 1)])
    ]

    return music_treeview_list


def history_treeview():
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

    history_treeview_list = [

      OrderedDict([
        ("column", "time"), ("heading", "Time"), ("sql_table", "History"),
        ("var_name", "Time"), ("select_order", 0), ("unselect_order", 1),
        ("key", False), ("anchor", "w"), ("instance", float),
        ("format", "date"), ("display_width", 300),
        ("display_min_width", 200), ("display_long", None), ("stretch", 0)]),

      OrderedDict([
        ("column", "music_id"), ("heading", "Music ID"), ("sql_table", "History"),
        ("var_name", "MusicId"), ("select_order", 0), ("unselect_order", 2),
        ("key", False), ("anchor", "e"), ("instance", int), ("format", "{:,}"),
        ("display_width", 100), ("display_min_width", 80),
        ("display_long", None), ("stretch", 0)]),  # 0=NO, 1=YES

      OrderedDict([
        ("column", "user"), ("heading", "User"), ("sql_table", "History"),
        ("var_name", "User"), ("select_order", 0), ("unselect_order", 3),
        ("key", False), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 150), ("display_min_width", 120),
        ("display_long", None), ("stretch", 1)]),  # 0=NO, 1=YES

      OrderedDict([
        ("column", "type"), ("heading", "Type"), ("sql_table", "History"),
        ("var_name", "Type"), ("select_order", 0), ("unselect_order", 4),
        ("key", False), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 80), ("display_min_width", 60),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "action"), ("heading", "Action"), ("sql_table", "History"),
        ("var_name", "Action"), ("select_order", 0), ("unselect_order", 5),
        ("key", False), ("anchor", "w"), ("instance", str),
        ("format", None), ("display_width", 80),
        ("display_min_width", 60), ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "master"), ("heading", "Master"), ("sql_table", "History"),
        ("var_name", "SourceMaster"), ("select_order", 0), ("unselect_order", 6),
        ("key", False), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 150), ("display_min_width", 100),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "detail"), ("heading", "Detail"), ("sql_table", "History"),
        ("var_name", "SourceDetail"), ("select_order", 0), ("unselect_order", 7),
        ("key", False), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 150), ("display_min_width", 100),
        ("display_long", None), ("stretch", 1)]),  # 0=NO, 1=YES

      OrderedDict([
        ("column", "target"), ("heading", "Target"), ("sql_table", "History"),
        ("var_name", "Target"), ("select_order", 0), ("unselect_order", 8),
        ("key", False), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 300), ("display_min_width", 200),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([  # Offset 8 cheating in mserve.py Playlists() populate_his_tree
        ("column", "size"), ("heading", "Size"), ("sql_table", "History"),
        ("var_name", "Size"), ("select_order", 0), ("unselect_order", 9),
        ("key", False), ("anchor", "e"), ("instance", int), ("format", "{:,}"),
        ("display_width", 100), ("display_min_width", 80),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "count"), ("heading", "Count"), ("sql_table", "History"),
        ("var_name", "Count"), ("select_order", 0), ("unselect_order", 10),
        ("key", False), ("anchor", "e"), ("instance", int), ("format", "{:,}"),
        ("display_width", 80), ("display_min_width", 60),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "comments"), ("heading", "Comments"), ("sql_table", "History"),
        ("var_name", "Comments"), ("select_order", 0), ("unselect_order", 11),
        ("key", False), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 160), ("display_min_width", 140),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "seconds"), ("heading", "Seconds"), ("sql_table", "History"),
        ("var_name", "Seconds"), ("select_order", 0), ("unselect_order", 12),
        ("key", False), ("anchor", "e"), ("instance", float), ("format", "{0:,.4f}"),
        ("display_width", 140), ("display_min_width", 80),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "row_id"), ("heading", "Row ID"), ("sql_table", "History"),
        ("var_name", "Id"), ("select_order", 0), ("unselect_order", 13),
        ("key", True), ("anchor", "e"), ("instance", int), ("format", "{:,}"),
        ("display_width", 80), ("display_min_width", 60),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "reason"), ("heading", "Reason"), ("sql_table", "calc"),
        ("var_name", "reason"), ("select_order", 0), ("unselect_order", 14),
        ("key", False), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 160), ("display_min_width", 140),
        ("display_long", None), ("stretch", 1)])
    ]

    ''' Future retention is calculated in order of Monthly, Weekly, Daily. 
        Last year retention is same as Future but Yearly test inserted first.
        The newest backup will always be classified as Monthly until tomorrow.
    '''

    return history_treeview_list


def playlist_treeview():
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

    playlist_treeview_list = [

      OrderedDict([
        ("column", "time"), ("heading", "Time"), ("sql_table", "History"),
        ("var_name", "Time"), ("select_order", 0), ("unselect_order", 1),
        ("key", False), ("anchor", "w"), ("instance", float),
        ("format", "date"), ("display_width", 300),
        ("display_min_width", 200), ("display_long", None), ("stretch", 0)]),

      OrderedDict([
        ("column", "music_id"), ("heading", "Music ID"), ("sql_table", "History"),
        ("var_name", "MusicId"), ("select_order", 0), ("unselect_order", 2),
        ("key", False), ("anchor", "e"), ("instance", int), ("format", "{:,}"),
        ("display_width", 100), ("display_min_width", 80),
        ("display_long", None), ("stretch", 0)]),  # 0=NO, 1=YES

      OrderedDict([
        ("column", "user"), ("heading", "User"), ("sql_table", "History"),
        ("var_name", "User"), ("select_order", 0), ("unselect_order", 3),
        ("key", False), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 150), ("display_min_width", 120),
        ("display_long", None), ("stretch", 1)]),  # 0=NO, 1=YES

      OrderedDict([
        ("column", "type"), ("heading", "Type"), ("sql_table", "History"),
        ("var_name", "Type"), ("select_order", 0), ("unselect_order", 4),
        ("key", False), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 80), ("display_min_width", 60),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "action"), ("heading", "Action"), ("sql_table", "History"),
        ("var_name", "Action"), ("select_order", 0), ("unselect_order", 5),
        ("key", False), ("anchor", "w"), ("instance", str),
        ("format", None), ("display_width", 80),
        ("display_min_width", 60), ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "master"), ("heading", "Master"), ("sql_table", "History"),
        ("var_name", "SourceMaster"), ("select_order", 0), ("unselect_order", 6),
        ("key", False), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 150), ("display_min_width", 100),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "detail"), ("heading", "Detail"), ("sql_table", "History"),
        ("var_name", "SourceDetail"), ("select_order", 0), ("unselect_order", 7),
        ("key", False), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 150), ("display_min_width", 100),
        ("display_long", None), ("stretch", 1)]),  # 0=NO, 1=YES

      OrderedDict([
        ("column", "target"), ("heading", "Target"), ("sql_table", "History"),
        ("var_name", "Target"), ("select_order", 0), ("unselect_order", 8),
        ("key", False), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 300), ("display_min_width", 200),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "size"), ("heading", "Size"), ("sql_table", "History"),
        ("var_name", "Size"), ("select_order", 0), ("unselect_order", 9),
        ("key", False), ("anchor", "e"), ("instance", int), ("format", "{:,}"),
        ("display_width", 100), ("display_min_width", 80),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "count"), ("heading", "Count"), ("sql_table", "History"),
        ("var_name", "Count"), ("select_order", 0), ("unselect_order", 10),
        ("key", False), ("anchor", "e"), ("instance", int), ("format", "{:,}"),
        ("display_width", 80), ("display_min_width", 60),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "comments"), ("heading", "Comments"), ("sql_table", "History"),
        ("var_name", "Comments"), ("select_order", 0), ("unselect_order", 11),
        ("key", False), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 160), ("display_min_width", 140),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "seconds"), ("heading", "Seconds"), ("sql_table", "History"),
        ("var_name", "Seconds"), ("select_order", 0), ("unselect_order", 12),
        ("key", False), ("anchor", "e"), ("instance", float), ("format", "{0:,.4f}"),
        ("display_width", 140), ("display_min_width", 80),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "row_id"), ("heading", "Row ID"), ("sql_table", "History"),
        ("var_name", "Id"), ("select_order", 0), ("unselect_order", 13),
        ("key", True), ("anchor", "e"), ("instance", int), ("format", "{:,}"),
        ("display_width", 80), ("display_min_width", 60),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "reason"), ("heading", "Reason"), ("sql_table", "calc"),
        ("var_name", "reason"), ("select_order", 0), ("unselect_order", 14),
        ("key", False), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 160), ("display_min_width", 140),
        ("display_long", None), ("stretch", 1)])
    ]

    ''' Future retention is calculated in order of Monthly, Weekly, Daily. 
        Last year retention is same as Future but Yearly test inserted first.
        The newest backup will always be classified as Monthly until tomorrow.
    '''

    return playlist_treeview_list


def update_history(scraped_dict):
    """ NOT USED """
    for i, website in enumerate(scraped_dict):
        if len(website['link']) > 2 and website['flag'] != 'skip':
            pass
            # Check for duplicates
        else:
            pass

# if there are existing history records identical to scraped_dict
# we want to skip adding. We might want to update time though.


def create_webscrape(music_id, website):
    """ NOT USED """
    # Read all history records finding the last one for each website
    # if the flag is 'downloaded' then set dict flag to 'skip'
    print('remove website parameter:', website)
    for website in webscape.WEBSITE_LIST:
        if get_history(music_id, website=website):
            # update dict
            pass
        else:
            add_dict(xxx)

# After loop go back and assign priority flags 1 to 8. Initial priority list 
#can be redefined by user.


def create_radio_buttons(music_id):
    """ NOT USED """
    # if already downloaded set text to grey with date in parentheses.
    # if no link add (no link) after website name.
    # can you make a deactivated tkinter radio button? Or simply
    # don't add unavailable to list.

    # From:
    # https://stackoverflow.com/questions/49061602/how-to-disable-multiple-radiobuttons-in-python

    print('music_id parameter not used:', music_id)
    sum_label['text'] += var.get()
    if sum_label['text'] >= 30:
        for key in radiobuttons:
            radiobuttons[key]['state'] = 'disabled'


def get_last_history(music_id, website='all'):
    """ NOT USED """
    # match is on website human formatted name not internet
    #  formatted name. EG "Genius' not '//genius.com'
    print('sql.py - get_last_history(music_id, website):', music_id, website)


# ==============================  FIX SQL ROWS  ============================


class FixData:
    # Date parameter in form "Sun May 22 23:59:59 2023"

    def __init__(self, cutoff_str):
        self.rows_count = 0
        self.rows_changed = 0
        self.fix_count = 0  # Can be two fields changed per row
        self.error_count = 0
        self.skipped_count = 0
        self.epoch_cutoff = time.mktime(time.strptime(cutoff_str))
        self.past_count = 0
        self.test = True
        self.successful_update_count = 0
        self.sql_cmd_error = False

    def del_music_ids(self, start, end, update=False):
        """ Delete range of music IDs that were created in error.
            First pass delete History Table rows matching MusicId range.
            Second pass delete Music Table rows matching Id range.

            FIXES ERRORS after another location wasn't handled properly:

sql.hist_init_lost_and_found(): File below doesn't exist:
COLUMN: Id                        VALUE: 3928
COLUMN: OsFileName                VALUE: Faith No More/<No Album>/19 The Perfect Crime.m4a
COLUMN: OsModificationTime        VALUE: 1448681593.0
COLUMN: MetaSongName              VALUE: None
COLUMN: Seconds                   VALUE: None

sql.hist_init_lost_and_found(): File below doesn't exist:
COLUMN: Id                        VALUE: 3936
COLUMN: OsFileName                VALUE: Fleetwood Mac/<No Album>/RandomSong2.m4a
COLUMN: OsModificationTime        VALUE: 1595468339.8
COLUMN: MetaSongName              VALUE: None
COLUMN: Seconds                   VALUE: None

        """
        # Backup database before updating
        self.backup(update)

        ''' PHASE I - Delete History Records linked to MusicId '''

        fix_list = list()
        sql = "SELECT * FROM History INDEXED BY MusicIdIndex " +\
              "WHERE MusicId >= ? AND MusicId <= ?"
        hist_cursor.execute(sql, (start, end))
        rows = hist_cursor.fetchall()

        for sql_row in rows:
            row = dict(sql_row)
            # self.rows_count += 1 We only count Music Rows in second pass
            print_all = False
            #if 15879 <= row['Id'] <= 15880:
            if row['MusicId'] == 999999:  # Change 999999 to MusicId to print for debugging
                print("\nFound history History Row Id:", row['Id'], "| MusicId:", row['MusicId'])
                print("\trow['SourceMaster'] =", row['SourceMaster'],
                      "| row['SourceDetail'] =", row['SourceDetail'])

                print_all = True

            fix_list.append(OrderedDict([('Id', row['Id']),
                                         ('MusicId', row['MusicId']),
                                         ('SourceMaster', row['SourceMaster']),
                                         ('SourceDetail', row['SourceDetail']),
                                         ('Count', 0), ('Error', 0)]))
            d = fix_list[len(fix_list) - 1]

            self.rows_changed += 1
            print(self.make_pretty_line(d))

            if self.test:
                continue  # Skip over update

            sql = "DELETE FROM History WHERE Id = ?"
            if not self.sql_cmd_error:
                key = row['Id']
                try:
                    hist_cursor.execute(sql, (key,))
                    self.successful_update_count += 1
                except Exception as err:
                    print('sql.del_music_ids() Update Failed:\n  Error: %s' % (str(err)))
                    print("  key:", key,)
                    print(sql, "\n", (detail, comment, key))
                    self.sql_cmd_error = True
                pass

        ''' PHASE II - Delete Music Rows in MusicId Range '''

        del_list = list()
        sql = "SELECT * FROM Music WHERE Id >= ? AND Id <= ?"
        cursor.execute(sql, (start, end))
        rows = cursor.fetchall()

        for sql_row in rows:
            row = dict(sql_row)
            self.rows_count += 1  # Not counted in first pass through history records
            print_all = False
            #if 15879 <= row['Id'] <= 15880:
            if row['Id'] == 999999:  # Change 999999 to MusicId to print for debugging
                print("\nFound history History Row Id:", row['Id'], "| MetaSongName:", row['MetaSongName'])
                print_all = True

            del_list.append(OrderedDict([('Id', row['Id']),
                                         ('MetaSongName', row['MetaSongName']),
                                         ('Count', 0), ('Error', 0)]))
            d = del_list[len(del_list) - 1]

            self.rows_changed += 1
            print(self.make_pretty_line(d))

            if self.test:
                continue  # Skip over update

            sql = "DELETE FROM Music WHERE Id = ?"
            if not self.sql_cmd_error:
                key = row['Id']
                try:
                    cursor.execute(sql, (key,))
                    self.successful_update_count += 1
                except Exception as err:
                    print('sql.del_music_ids() Update Failed:\n  Error: %s' % (str(err)))
                    print("  key:", key, " | sql:", sql)
                    self.sql_cmd_error = True
                pass

        # Print count total lines
        self.print_summary("del_music_ids() History", fix_list)
        self.print_summary("del_music_ids() Music", del_list)

        self.wrapup(update)

    def fix_scrape_parm(self, update=False):
        """ Fix MusicId 0 by looking up real MusicId
        """
        # Backup database before updating
        self.backup(update)

        fix_list = list()

        hist_cursor.execute("SELECT * FROM History")
        rows = hist_cursor.fetchall()

        for sql_row in rows:
            row = dict(sql_row)
            self.rows_count += 1
            print_all = False
            #if 15879 <= row['Id'] <= 15880:
            if row['MusicId'] == 999999:  # Change 999999 to MusicId to print for debugging
                print("\nFound history History Row Id:", row['Id'], "| MusicId:", row['MusicId'])
                print("\trow['SourceMaster'] =", row['SourceMaster'],
                      "| row['SourceDetail'] =", row['SourceDetail'])

                print_all = True

            if row['Type'] != 'scrape' or row['Action'] != 'parm':
                continue  # Wrong 'Type' and 'Action'

            # History time < bug fix date?
            date_str = row['Comments']
            if date_str is None:
                self.error_count += 1
                print("Cutoff date not found in scrape-parm history comments")
                print(" ", self.make_pretty_line(row))
                continue  # Error isolating date within comment

            try:
                time_obj = time.strptime(date_str)
                # Check to ensure date in comments is prior to cutoff date
                # fix_count and past_count are automatically updated for us.
                if not self.check_cutoff_date(time_obj):
                    continue  # Prior to cutoff date

            except ValueError:
                self.error_count += 1
                print('sql.py - fix_scrape_parm() time object error:', utc_date_str)
                print(" ", self.make_pretty_line(row))  # All keys in random order
                continue

            fix_list.append(OrderedDict([('Id', row['Id']),
                                         ('MusicId', row['MusicId']),
                                         ('SourceMaster', row['SourceMaster']),
                                         ('SourceDetail', row['SourceDetail']),
                                         ('Count', 0), ('Error', 0)]))
            d = fix_list[len(fix_list) - 1]

            self.rows_changed += 1
            print(self.make_pretty_line(d))
            if row['SourceMaster'] == "None":  # 12933 to 12940
                print(self.make_pretty_line(row), "\n")  # 8 strange records

            # Fuzzy search for MusicId
            # Get [songs by Artist Name, MusicId] list
            # This is too much work so simply delete 66 bad history records.

            if self.test:
                continue  # Skip over update

            sql = "DELETE FROM History WHERE Id = ?"
            if not self.sql_cmd_error:
                key = row['Id']
                try:
                    hist_cursor.execute(sql, (key,))
                    self.successful_update_count += 1
                except Exception as err:
                    print('sql.fix_scrape_parm() Update Failed:\n  Error: %s' % (str(err)))
                    print("  key:", key,)
                    print(sql, "\n", (detail, comment, key))
                    self.sql_cmd_error = True
                pass

        # Print count total lines
        self.print_summary("fix_parm_scrape()", fix_list)
        self.wrapup(update)

    def fix_meta_edit(self, update=False):
        """ Remove duplicate history records under Type "meta", Action "edit"

        """

        # Backup database before updating
        self.backup(update)

        fix_list = list()
        music_list = list()

        hist_cursor.execute("SELECT * FROM History")
        rows = hist_cursor.fetchall()

        for sql_row in rows:
            row = dict(sql_row)
            self.rows_count += 1
            print_all = False
            #if 15879 <= row['Id'] <= 15880:
            if row['MusicId'] == 999999:  # Change 999999 to MusicId to print for debugging
                print("\nFound history History Row Id:", row['Id'], "| MusicId:", row['MusicId'])
                print("\trow['MusicId'] =", row['MusicId'], "| row['Target'] =", row['Target'])
                print_all = True

            if row['Type'] != 'meta' or row['Action'] != 'edit':
                continue  # Wrong 'Type' and 'Action'

            if print_all:
                print("\tStep 1 for :", row['Id'])

            # If first time for this MusicId, don't delete. Just log it.
            if not row['MusicId'] in music_list:
                music_list.append(row['MusicId'])
                fix_list.append(OrderedDict([('KeepId', row['Id']),
                                             ('MusicId', row['MusicId']),
                                             ('Target', row['Target']),
                                             ('Count', 0), ('Error', 0)]))
                if print_all:
                    print("\tAdding to fix_list:", row['Id'], "position:", len(fix_list))
                self.skipped_count += 1  # First record is a keeper
                continue  # Nothing changes

            if print_all:
                print("\tStep 2 for :", row['Id'])

            date_str, rebuilt_prefix = self.date_from_comments("Found", row['Comments'])
            if rebuilt_prefix is None:
                self.error_count += 1
                print("Cutoff date not found in meta-edit history comments")
                print(" ", self.make_pretty_line(row))
                continue  # Error isolating date within comment

            if print_all:
                print("\tStep 3 for :", row['Id'])

            try:
                time_obj = time.strptime(date_str)
                # Check to ensure date in comments is prior to cutoff date
                # fix_count and past_count are automatically updated for us.
                if not self.check_cutoff_date(time_obj):
                    # print("epoch:", epoch, "epoch_cutoff:", epoch_cutoff)
                    # print('past_count  Type:', row['Type'], ' Action:', row['Action'],
                    #      ' SourceMaster:', row['SourceMaster'], ' Comments:', row['Comments'])
                    # print("\tPast cutoff date:", row['Id'], self.past_count)
                    continue  # Prior to cutoff date

            except ValueError:
                self.error_count += 1
                print('sql.py - fix_meta_edit() time object error:', utc_date_str)
                print(" ", self.make_pretty_line(row))  # All keys in random order
                continue

            if print_all:
                print("\tStep 4 for :", row['Id'])

            self.rows_changed += 1

            found_ok = False
            for d in fix_list:
                # Find matching MusicId setup previously in dictionary list
                if d['MusicId'] == row['MusicId']:
                    d['Count'] += 1
                    #print(self.make_pretty_line(d))
                    found_ok = True
                    break

            if print_all:
                print("Step 5 for :", row['Id'])

            if not found_ok:
                print("Not found:")
                print(self.make_pretty_line(d))

            if self.test:
                continue  # Skip over update

            sql = "DELETE FROM History WHERE Id = ?"
            if not self.sql_cmd_error:
                key = row['Id']
                try:
                    hist_cursor.execute(sql, (key,))
                    self.successful_update_count += 1
                except Exception as err:
                    print('sql.fix_meta_edit() Update Failed:\n  Error: %s' % (str(err)))
                    print("  key:", key,)
                    print(sql, "\n", (detail, comment, key))
                    self.sql_cmd_error = True
                pass

        # Print count total lines
        self.print_summary("fix_meta_edit()", fix_list)
        self.wrapup(update)


    def fix_utc_dates(self, update=False):
        """ Change UTC dates to Local format
            Summer time April to October (7 months) is UTC-6
            Winter time November to March (5 months) is UTC-7

    Code to desk check for converting gmtime to localtime prior to May 7, 2023

    'file' or 'meta + 'init' or 'edit'
    ./sql.py:521:    SourceDetail = time.asctime(time.localtime(Time))
    ./sql.py:790:    SourceDetail = time.asctime(time.localtime(Time))
    ./sql.py:522:    Comments = "Found: " + time.asctime(time.localtime(time.time()))
    ./sql.py:619:    Comments = Action + " time: " + time.asctime(time.localtime(time.time()))

    hist_default_dict(key, time_type='access'):
    'time', 'init' or 'edit'
    ./sql.py:669:    SourceDetail = time.asctime(time.localtime(Time))

    'time', 'remove'
    ./sql.py:707:    Comments = "Removed: " + time.asctime(time.localtime(time.time()))

    def hist_init_lyrics_and_time(START_DIR, USER, LODICT):
    'file' or 'meta + 'init' or 'edit'
    ./sql.py:989:        SourceDetail = time.asctime(time.localtime(Time))

    'scrape', 'parm'
    ./sql.py:1140:                         time.asctime(time.localtime(time.time())))
    ./mserve.py:6791:                         time.asctime(time.localtime(time.time())))

    'encode', 'discid'
    ./encoding.py:676:                   "Get disc ID: " + time.asctime(time.localtime(time.time())))
    'encode', 'mbz_get1'
    ./encoding.py:757:             "Get releases list: " + time.asctime(time.localtime(time.time())))
    'encode', 'mbz_get2'
    ./encoding.py:805:                "Get cover art: " + time.asctime(time.localtime(time.time())))
    'encode', 'album'
    ./encoding.py:1103:                    " Finished: " + time.asctime(time.localtime(time.time())))
    'file', 'init'
    ./encoding.py:1170:            "encoded: " + time.asctime(time.localtime(time.time())))
    'encode', 'track'
    ./encoding.py:1175:            "finished: " + time.asctime(time.localtime(time.time())))

        """

        # Backup database before updating
        self.backup(update)

        fix_list = list()
        # list of dictionaries Control Field 'SD' is SourceDetail
        # 'CM' For comment field with no prefix.
        # Otherwise Comments field contains date after passed prefix, E.G. "encoded"
        fix_list.append(self.utc_dict('file', 'init', 'SD'))  # SD = SourceDetail
        # ERROR: SourceDetail: '05 Love Has Remembered Me.oga'
        #   Type: 'file'  Action: 'init'  SourceMaster: 'April Wine'
        #   Comments: 'encoded: Sun Aug 15 23:43:22 2021'
        fix_list.append(self.utc_dict('file', 'edit', 'SD'))
        fix_list.append(self.utc_dict('meta', 'init', 'SD'))
        fix_list.append(self.utc_dict('meta', 'edit', 'SD'))
        fix_list.append(self.utc_dict('file', 'init', 'Found'))  # Comments start
        fix_list.append(self.utc_dict('file', 'edit', 'Found'))  # with "Found:"
        fix_list.append(self.utc_dict('meta', 'init', 'Found'))
        fix_list.append(self.utc_dict('meta', 'edit', 'Found'))

        fix_list.append(self.utc_dict('file', 'init', 'init time'))
        fix_list.append(self.utc_dict('file', 'edit', 'edit time'))
        fix_list.append(self.utc_dict('meta', 'init', 'init time'))
        fix_list.append(self.utc_dict('meta', 'edit', 'edit time'))

        fix_list.append(self.utc_dict('time', 'init', 'SD'))
        fix_list.append(self.utc_dict('time', 'edit', 'SD'))
        # ERROR: SourceDetail: L004
        #   Type: time  Action: edit  SourceMaster: SD Card SanDisk 128GB
        #   Comments: Automatically added by hist_init_lyrics_and_time()
        fix_list.append(self.utc_dict('time', 'remove', 'Removed'))
        fix_list.append(self.utc_dict('scrape', 'parm', 'CM'))  # CM = Comments
        fix_list.append(self.utc_dict('encode', 'discid', 'Get disc ID'))
        fix_list.append(self.utc_dict('encode', 'mbz_get1', 'Get releases list'))
        fix_list.append(self.utc_dict('encode', 'mbz_get2', 'Get cover art'))
        """ SPECIAL HANDLING FOR: Key 'Field': with value of: ' Finished' (has leading space)
            "Tracks: " + str(self.encode_album_cnt) +
            "Duration: " + duration +
            " Finished: " + time.asctime(time.localtime(time.time())))
        """
        fix_list.append(self.utc_dict('encode', 'album', ' Finished'))
        fix_list.append(self.utc_dict('file', 'init', 'encoded'))
        fix_list.append(self.utc_dict('encode', 'track', 'finished'))

        self.rows_count = 0
        self.rows_changed = 0

        hist_cursor.execute("SELECT * FROM History")
        rows = hist_cursor.fetchall()
        for sql_row in rows:
            row = dict(sql_row)
            self.rows_count += 1

            new_row = self.utc_process_row(row, fix_list)
            if new_row == row:
                continue  # Nothing has changed

            self.rows_changed += 1

            if self.test:
                continue  # Skip over update

            detail = new_row['SourceDetail']
            comment = new_row['Comments']
            key = row['Id']
            sql = "UPDATE History SET SourceDetail=?, Comments=? WHERE Id = ?"
            if not self.sql_cmd_error:
                try:
                    hist_cursor.execute(sql, (detail, comment, key))
                    self.successful_update_count += 1
                except Exception as err:
                    print('sql.fix_utc_dates() Update Failed:\n  Error: %s' % (str(err)))
                    print("  detail:", detail)
                    print("  comment:", comment)
                    print("  key:", key)
                    print(sql, "\n", (detail, comment, key))
                    self.sql_cmd_error = True

        # Print count total lines
        self.print_summary("fix_utc_dates()", fix_list)
        self.wrapup(update)

    @staticmethod
    def utc_dict(Type, Action, Field):
        """
            Build control dictionary. E.G.
                OrderedDict([('Type', 'encode'), ('Action', 'mbz_get2'),
                             ('Field', 'Get cover art'), ('Count', 0), ('Error', 0)]))
        """
        return OrderedDict([('Type', Type), ('Action', Action),
                            ('Field', Field), ('Count', 0), ('Error', 0)])

    def utc_process_row(self, row, fix_list):

        new_row = row.copy()
        for d in fix_list:

            if d['Type'] != row['Type'] or d['Action'] != row['Action']:
                continue

            # SPECIAL HANDLING for comments but first check they are not "None"
            if row['Comments'] and row['Comments'].startswith('encoded: '):
                # new_row['SourceDetail'] = self.utc_to_local(row['SourceDetail'], row)
                d['Count'] += 1
                d['Error'] += 1
                self.error_count += 1
                self.skipped_count += 1
                continue

            if row['Type'] == 'time' and row['Action'] == 'edit' and d['Field'] == 'SD' and \
                row['Comments'] and row['Comments']. \
                    startswith('Automatically added by hist_init_lyrics_and_time()'):
                self.skipped_count += 1
                # sql.py - utc_to_local() time object error: L004
                continue

            elif d['Field'] == 'SD':
                new_row['SourceDetail'] = self.utc_to_local(row['SourceDetail'], row)
                d['Count'] += 1

            elif row['Comments'] and row['Comments'].\
                    startswith('Automatically added by hist_init_lyrics_and_time()'):
                # If it was "SD" it would have been trapped now. Skip this comment only
                # from our tests
                d['Count'] += 1
                d['Error'] += 1
                self.error_count += 1
                self.skipped_count += 1
                continue

            elif d['Field'] == 'CM':
                new_row['Comments'] = self.utc_to_local(row['Comments'], row)
                d['Count'] += 1

            # SPECIAL HANDLING for comments but they might be "None"
            elif row['Comments'] and (row['Comments'].startswith(d['Field']) or
                                      (d['Field'] == " Finished" and
                                       d['Field'] in row['Comments'])):

                old_comment = row['Comments']  # Save to compare changes later.

                # One time fix for missing space before "Duration:" string
                if "Tracks:" in row['Comments'] and "Duration:" in row['Comments']:
                    if " Duration:" not in row['Comments']:
                        row['Comments'] = row['Comments'].replace("Duration:", " Duration:")
                        # Fix "Tracks: 2 Duration: 7:59 Finished: Thu Aug 26 01:28:39 2021"
                        # print(old_comment)
                        # print(row['Comments'])

                # Check to ensure date in comments is prior to cutoff date
                # fix_count and past_count are automatically updated for us.
                # If before cutoff date then convert utc time to local time
                new_row['Comments'] = self.utc_comment_wrapper(d['Field'], row['Comments'], row)
                if old_comment == new_row['Comments']:
                    # Nothing changed so date not found within comments or before cutoff.
                    self.skipped_count += 1
                    print('REVIEW:', self.make_pretty_line(row))
                    continue
                d['Count'] += 1

            if d['Count'] == 1:
                #print('GOOD  -', self.make_pretty_line(d))
                pass

            if d['Error'] == 1:
                #print('ERROR -', self.make_pretty_line(d))
                pass

        return new_row

    def utc_comment_wrapper(self, prefix, comment, row):
        """
            Date is at end of comment.

            :param prefix in comment E.G. "encoded"
            :param comment with ascii date suffix
            :param row is only used for error messages
        """
        ''' OLD CODE
        parts = comment.split(prefix)
        if len(parts) != 2:
            print('bad parts len:', len(parts))
            return comment

        date_str = parts[1][2:]
        local_date = self.utc_to_local(date_str, row)
        return parts[0] + prefix + ": " + local_date
        '''
        date_str, rebuilt_prefix = self.date_from_comments(prefix, comment)
        if rebuilt_prefix is None:
            return comment  # Error isolating date within comment
        # Check to ensure date in comments is prior to cutoff date
        # fix_count and past_count are automatically updated for us.
        # If before cutoff date then convert utc time to local time
        local_date = self.utc_to_local(date_str, row)
        return rebuilt_prefix + local_date

    def utc_to_local(self, utc_date_str, row):
        """
            :param utc_date_str from History SourceDetail or Comments
            :param row is only used for error messages
        """

        try:
            time_obj = time.strptime(utc_date_str)
            # Check to ensure date in comments is prior to cutoff date
            # fix_count and past_count are automatically updated for us.
            if not self.check_cutoff_date(time_obj):
                #print("epoch:", epoch, "epoch_cutoff:", epoch_cutoff)
                #print('past_count  Type:', row['Type'], ' Action:', row['Action'],
                #      ' SourceMaster:', row['SourceMaster'], ' Comments:', row['Comments'])
                return utc_date_str

        except ValueError:
            self.error_count += 1
            print('sql.py - utc_to_local() time object error:', utc_date_str)
            print('  Type:', row['Type'], ' Action:', row['Action'], ' SourceMaster:',
                  row['SourceMaster'], ' Comments:', row['Comments'])
            print(self.make_pretty_line(row))  # All keys in random order
            return utc_date_str

        if 3 < time_obj.tm_mon < 11:
            off = -6*3600  # Summer Time -6 hours from utc
        else:
            off = -7*3600  # Winter Time -7 hours from utc

        epoch += float(off)

        return time.asctime(time.localtime(epoch))

    # Shared FixData() class functions

    @staticmethod
    def make_pretty_line(d):
        line = ""
        for key in d:
            # Last 40 chars of value, right justified to 5 when only 1 to 4 characters
            line += key + ": " + str(d[key])[-40:].rjust(5) + " | "
        return line

    def backup(self, update):
        if update:
            self.test = False
            from location import FNAME_LIBRARY
            os.popen("cp -a " + FNAME_LIBRARY + " " + FNAME_LIBRARY + ".bak")

    def wrapup(self, update):
        print("=" * 80)
        if update:
            print("self.successful_update_count:", self.successful_update_count)
            if not self.sql_cmd_error:
                con.commit()
            else:
                print("self.sql_cmd_error: changes have been rolled back.")
                hist_cursor.execute("ROLLBACK")
            print("Backup created:", FNAME_LIBRARY + ".bak")
        else:
            print("Test Run Only - NO UPDATES TO:", FNAME_LIBRARY)
        print("=" * 80)

    def print_summary(self, parent, dict_list):
        print('\nsql.py FixData() ' + parent + ' Sub-Totals')
        for d in dict_list:
            if d['Count'] > 0:
                # Thousands of records so only print groups updated
                print(" ", self.make_pretty_line(d))

        print('\nsql.py FixData() ' + parent + ' Summary Counts')
        print('  rows_count   :', self.rows_count)
        print('  rows_changed :', self.rows_changed)
        print('  fix_count    :', self.fix_count)  # May be multiple fixes/row
        print('  skipped_count:', self.skipped_count)
        print('  error_count  :', self.error_count)
        print('  past cutoff  :', self.past_count)
        print()

    @staticmethod
    def date_from_comments(prefix, comment):
        """
            Date is at end of comment. E.G. "Found: Thu May 18 12:45:52 2023"
            There must always be colon ":" after the prefix. E.G. "Found" is passed.
            There must always be a space " " after the colon ":".

            :param prefix in comment E.G. "encoded". May be " Found" with leading space
                because it follows dynamic data.
            :param comment with ascii date
        """
        parts = comment.split(prefix)
        if len(parts) != 2:
            print('sql.py - date_from_comment() len(parts) != 2:', len(parts))
            return comment, None

        date_str = parts[1][2:]
        rebuilt_prefix = parts[0] + prefix + ": "
        return date_str, rebuilt_prefix

    def check_cutoff_date(self, time_obj):
        epoch = time.mktime(time_obj)
        if epoch < self.epoch_cutoff:
            self.fix_count += 1
            return True
        else:
            self.past_count += 1
            return False


# ==============================  FIX SQL ROWS  ============================


class Versions:
    """
        Get installed version numbers. Can be called by CLI or GUI.
    """

    def __init__(self):

        self.inst_list = []                 # List of dictionaries
        self.inst_dict = {}                 # Dictionary of single program keys:
        # prg_name, prg_ver, pkg_name, pkg_ver, prg_cmd, get_ver_parm,
        # comments (E.G. special notes, version date/time, etc)

        # History Time: [file modification time], MusicId: 0, User: [pkg_name],
        #   Type: 'version', Action: 'program', SourceMaster: [name]
        #   SourceDetail: [version installed], Target: [/usr/bin/blahBlah],
        #   Size: [file size], Count: [line count if script], Seconds: 0.0
        #   Comments: "Used in mserve.py"

        # History Time: [file modification time], MusicId: 0, User: [package_name],
        #   Type: 'version', Action: 'program', SourceMaster: 'prg_get_ver'
        #   SourceDetail: [parsing method], Target: [command to get version],
        #   Size: [major_ver], Count: [minor_ver], Seconds: [sub_minor.sub_sub_minor]
        #   Comments: "Used by encoding.py"

        # History Time: [file modification time], MusicId: 0, User: [package_name],
        #   Type: 'version', Action: 'program', SourceMaster: 'package_get_version'
        #   SourceDetail: [parsing method], Target: [command to get version],
        #   Size: [major_version], Count: [minor_version], Seconds: [sub_minor.sub_sub_minor]
        #   Comments: "Used by disc_get.py"
        """
            con.execute("create table IF NOT EXISTS History(Id INTEGER PRIMARY KEY, \
                Time FLOAT, MusicId INTEGER, User TEXT, Type TEXT, \
                Action TEXT, SourceMaster TEXT, SourceDetail TEXT, \
                Target TEXT, Size INT, Count INT, Seconds FLOAT, \
                Comments TEXT)")

        """

    def build_apt_list(self, update=False):
        """ Samples
            $ gst-launch-1.0 --gst-version
            GStreamer Core Library version 1.8.3

            $ apt list | grep python-tk
            python-tk/xenial-updates,now 2.7.12-1~16.04 amd64 [installed]
            python-tkcalendar/xenial,xenial,now 1.5.0-1 all [installed]

            $ wc mserve.py
             10826  46134 492518 mserve.py

TO GET installed packages
$ time apt list | grep "\[installed" > apt_list_installed.txt
real	0m1.454s
user	0m1.395s
sys	    0m0.095s

$ ll *.txt
-rw-rw-r-- 1 rick rick 3377347 May 18 15:18 apt_list_full.txt
-rw-rw-r-- 1 rick rick  185301 May 18 15:19 apt_list_installed.txt

$ head apt_list_installed.txt
a11y-profile-manager-indicator/xenial,now 0.1.10-0ubuntu3 amd64 [installed]
abiword/xenial-updates,now 3.0.1-6ubuntu0.16.04.1 amd64 [installed]
abiword-common/xenial-updates,xenial-updates,now 3.0.1-6ubuntu0.16.04.1 all [installed,automatic]
abiword-plugin-grammar/xenial-updates,now 3.0.1-6ubuntu0.16.04.1 amd64 [installed,automatic]
account-plugin-facebook/xenial,xenial,now 0.12+16.04.20160126-0ubuntu1 all [installed]
account-plugin-flickr/xenial,xenial,now 0.12+16.04.20160126-0ubuntu1 all [installed]
account-plugin-google/xenial,xenial,now 0.12+16.04.20160126-0ubuntu1 all [installed]
accountsservice/xenial-updates,xenial-security,now 0.6.40-2ubuntu11.6 amd64 [installed]
acl/xenial,now 2.2.52-3 amd64 [installed]
acpi/xenial,now 1.7-1 amd64 [installed]

        """
        pass


# =================================  MISCELLANEOUS  ===========================


def alter_table1(cur, table, *args):
    """ Copied from simple_insert(), Needs more code !!! """
    query = 'INSERT INTO '+table+' VALUES (' + '?, ' * (len(args)-1) + '?)'
    cur.execute(query, args)


def simple_insert(cur, table, *args):
    query = 'INSERT INTO '+table+' VALUES (' + '?, ' * (len(args)-1) + '?)'
    cur.execute(query, args)


def insert_blank_line(table_name):
    """ NOT USED...
        Add underscores to insert_blank_line and table_name for pycharm syntax checking.
        If pragma breaks then remove underscores.
    """
    default_value = {'TEXT': '""', 'INT': '0', 'FLOAT': '0.0', 'BLOB': '""'}
    cs = con.execute('pragma table_info('+table_name+')').fetchall()  # sqlite column metadata
    con.execute('insert into '+table_name+' values ('+','.join([default_value[c[2]] for c in cs])+')')
 
    #insert into Music(id) values (null);         # Simpler method
    ''' DELETED Q&A: https://stackoverflow.com/questions/66072570/
    how-to-initialize-all-columns-of-sqlite3-table?no redirect=1#comment116823421_66072570
  
Inserting zeros and empty strings (what you explicitly asked for)

default_value={'TEXT':'""','INT':'0','FLOAT':'0.0','BLOB':'""'}
def insert_blank_line(table_name):
  cs = con.execute('pragma table_info(Music)').fetchall() # sqlite column metadata
  con.execute('insert into '+table_name+' values ('+','.join([default_value[c[2]] for c in cs])+')')

Then you can call this by using: insert_blank_line('Music')
Insert nulls and use null-aware selects (alternative solution)

Instead of using this blank line function you could just insert a bunch of nulls

insert into Music(id) values (null);

And then upon selection, you treat the null data, in the following example you'll get no artist when it is null:

select if null(OsArtistName,'no artist') from Music;

or

select coalesce(OsArtistName,'no artist') from Music

Final note

Be aware that sqlite types are not enforced in the same way other databases
enforce. In fact they are not enforced at all. If you insert a string in a 
sqlite number column or a string to a sqlite number column, the data is 
inserted as requested not as the data column specifies - each unit of data 
has its own datatype.

    '''




# End of sql.py
