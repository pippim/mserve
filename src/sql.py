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
#
#==============================================================================

from __future__ import print_function       # Must be first import
from __future__ import unicode_literals     # Unicode errors fix

import sqlite3
import os
import re
import json
import time
import datetime
from collections import namedtuple, OrderedDict


# local modules
import global_variables as g        # should be self-explanatory
import timefmt                      # Our custom time formatting functions
import external as ext

try:
    from location import FNAME_LIBRARY  # SQL database name (SQLite3 format)
except ImportError:
    FNAME_LIBRARY = "/home/rick/.config/mserve/library.db"

CFG_THOUSAND_SEP = ","              # English "," to for thousands separator
CFG_DECIMAL_SEP = "."               # English "." for fractional amount
CFG_DECIMAL_PLACES = 1              # 1 decimal place, eg "38.5 MB"
CFG_DIVISOR_AMT = 1000000           # Divide by million
CFG_DIVISOR_UOM = "MB"              # Unit of Measure becomes Megabyte


NO_ARTIST_STR = "(No Artist)"         # global User defined labels
NO_ALBUM_STR = "(No Album)"
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
MUSIC_ID  = None
_START_DIR = _USER = _LODICT = None


def create_tables(SortedList, start_dir, pruned_subdirs, user, lodict):
    """ Create SQL tables out of OS sorted music top directory

        if START_DIR = '/mnt/music/'
        then PRUNED_SUBDIRS = 0

        if START_DIR = '/mnt/music/Trooper/'
        then PRUNED_SUBDIRS = 1

        if START_DIR = '/mnt/music/Trooper/Hits From 10 Albums/'
        then PRUNED_SUBDIRS = 2

        if START_DIR = '/mnt/... 10 Albums/08 Raise A Little Hell.m4a'
        then PRUNED_SUBDIRS = 3

    """

    global con, cursor, hist_cursor
    global START_DIR_SEP    # Count of / or \ separators in toplevel directory
    global MUSIC_ID         # primary key into Music table used by History table

    global _START_DIR, _USER, _LODICT
    _START_DIR = start_dir  # Toplevel directory, EG /mnt/music/
    _USER = user            # User ID to be stored on history records.
    _LODICT = lodict        # Location dictionary

    open_db()

    last_time = hist_last_time('file', 'init')
    print('last_time:', last_time)
    # Fill the table
    LastArtist = ""
    LastAlbum = ""

    START_DIR_SEP = start_dir.count(os.sep) - 1  # Number of / separators
    #print('PRUNED_SUBDIRS:', pruned_subdirs)
    START_DIR_SEP = START_DIR_SEP - pruned_subdirs

    for i, os_name in enumerate(SortedList):

        # split /mnt/music/Artist/Album/Song.m4a into list
        '''
            Our sorted list may have removed subdirectory levels using:
            
            work_list = [w.replace(os.sep + NO_ALBUM_STR + os.sep, os.sep) \
                 for w in work_list]

        '''
        # TODO: Check of os_name in Music Table. If so continue loop
        #       Move this into mserve.py main loop and update access time in SQL.
        groups = os_name.split(os.sep)
        Artist = groups[START_DIR_SEP+1]
        Album = groups[START_DIR_SEP+2]
        # Song = groups[START_DIR_SEP+3]  # Not used
        key = make_key(os_name)

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

        # os.stat gives us all of file's attributes
        stat = os.stat(full_path)
        size = stat.st_size
        # converted = float(size) / float(CFG_DIVISOR_AMT)   # Not used
        # fsize = str(round(converted, CFG_DECIMAL_PLACES))  # Not used

        ''' Add the song only if it doesn't exist (ie generates error) '''
        sql = "INSERT OR IGNORE INTO Music (OsFileName, \
               OsAccessTime, OsModificationTime, OsCreationTime, OsFileSize) \
               VALUES (?, ?, ?, ?, ?)" 

        cursor.execute(sql, (key, stat.st_atime, stat.st_mtime,
                             stat.st_ctime, size))

    con.commit()
    # Temporary during development to record history for lyrics web scrape and
    # time index synchronizing to lyrics.
    hist_init_lost_and_found(start_dir, user, lodict)
    hist_init_lyrics_and_time(start_dir, user, lodict)


def open_db():
    """ Open SQL Tables """
    global con, cursor, hist_cursor
    # con = sqlite3.connect(":memory:")
    con = sqlite3.connect(FNAME_LIBRARY)
    # print('FNAME_LIBRARY:',FNAME_LIBRARY)

    # MUSIC TABLE
    
    # Create the table (key must be INTEGER not just INT !
    # See https://stackoverflow.com/a/7337945/6929343 for explanation
    con.execute("create table IF NOT EXISTS Music(Id INTEGER PRIMARY KEY, \
                OsFileName TEXT, OsAccessTime FLOAT, \
                OsModificationTime FLOAT, OsCreationTime FLOAT, \
                OsFileSize INT, MetaArtistName TEXT, MetaAlbumName TEXT, \
                MetaSongName TEXT, ReleaseDate FLOAT, OriginalDate FLOAT, \
                Genre TEXT, Seconds INT, Duration TEXT, PlayCount INT, \
                TrackNumber INT, Rating TEXT, UnsynchronizedLyrics BLOB, \
                LyricsTimeIndex TEXT)")

    con.execute("CREATE UNIQUE INDEX IF NOT EXISTS OsFileNameIndex ON \
                Music(OsFileName)")


    # HISTORY TABLE

    # One time table drop to rebuild new history format
    # con.execute("DROP TABLE IF EXISTS History")

    con.execute("create table IF NOT EXISTS History(Id INTEGER PRIMARY KEY, \
                Time FLOAT, MusicId INTEGER, User TEXT, Type TEXT, \
                Action TEXT, SourceMaster TEXT, SourceDetail TEXT, \
                Target TEXT, Size INT, Count INT, Seconds FLOAT, \
                Comments TEXT)")

    con.execute("CREATE INDEX IF NOT EXISTS MusicIdIndex ON \
                History(MusicId)")
    con.execute("CREATE INDEX IF NOT EXISTS TimeIndex ON \
                History(Time)")

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


def close_db():
    con.commit()
    cursor.close()          # Aug 08/21 Fix "OperationalError:"
    hist_cursor.close()     # See: https://stackoverflow.com/a/53182224/6929343
    con.close()


def make_key(fake_path):
    """ Create key to read Music index by OsFileName which is
        /path/to/topdir/album/artist/song.ext

    TODO: What about PRUNED_SUBDIRS from mserve code?

        # Temporarily create SQL music tables until search button created.
        sql.CreateMusicTables(SORTED_LIST, START_DIR, PRUNED_SUBDIRS)

        What about '(NO_ARTIST)' and '(NO_ALBUM)' strings?
    """

    groups = fake_path.split(os.sep)
    artist = groups[START_DIR_SEP+1]
    album = groups[START_DIR_SEP+2]
    song = groups[START_DIR_SEP+3]
    return artist + os.sep + album + os.sep + song


def update_lyrics(key, lyrics, time_index):
    """
        Apply Unsynchronized Lyrics and Lyrics Time Index.
        Should only be called when lyrics or time_index has changed.
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
    global MUSIC_ID

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
    d = dict(cursor.fetchone())

    MUSIC_ID = d["Id"]

    if d["LyricsTimeIndex"] is not None:
        return d["UnsynchronizedLyrics"], json.loads(d["LyricsTimeIndex"])
    else:
        return d["UnsynchronizedLyrics"], None


def update_metadata(key, artist, album, song, genre, tracknumber, date, 
                    seconds, duration):
    """
        Update Music Table with metadata tags.
        Called from mserve.py and encoding.py

        TODO: Check if history has a 'file' record first. If not then add it.
              Add webscrape history record
              Add lyrics 'init' record
              Add time 'init' record
              Add lyrics 'edit' record
              Add time 'edit' record
              Add History view functions with filters for done or none


        First check if metadata has changed. If not then exit.

        Update metadata in library and insert history record:
            'meta' 'init' for first time
            'meta' 'edit' for 2nd and subsequent changes

        Metadata tags passed from following mserve variables:

        Id = self.saved_selections[self.ndx]
        list_index = int(Id)
        key = self.song_list[list_index]

        self.Artist=self.metadata.get('ARTIST', "None")
        self.Album=self.metadata.get('ALBUM', "None")
        self.Title=self.metadata.get('TITLE', "None")
        self.Genre=self.metadata.get('GENRE', "None")
        self.Track=self.metadata.get('TRACK', "None")
        self.Date=self.metadata.get('DATE', "None")
        self.Duration=self.metadata.get('DURATION', "0,0").split(',')[0]
        self.Duration=self.Duration.split('.')[0]
        self.DurationSecs=self.getSec(self.Duration)

        sql.update_metadata(self.play_make_sql_key(), self.Artist, self.Album, \
                            self.Title, self.Genre, self.Track, self.Date, \
                            self.DurationSecs, self.Duration)

    """

    # noinspection SpellCheckingInspection

    # Crazy all the time spent encoding has to be decoded for SQLite3 or error:
    # sqlite3.ProgrammingError: You must not use 8-bit bytestrings unless you
    # use a text_factory that can interpret 8-bit bytestrings (like
    # text_factory = str). It is highly recommended that you instead just
    # switch your application to Unicode strings.
    # TODO: Check for Python 3 may be required because Unicode is default type
    artist = artist.decode("utf8")          # Queensrÿche
    # inspection SpellCheckingInspection
    album = album.decode("utf8")
    song = song.decode("utf8")
    if type(date) is str:
        if date != "None":      # Strange but true... See "She's No Angel" by April Wine.
            # Problem with date "1993-01-26"
            try:
                date = float(date)
            except ValueError:
                pass  # Leave date as string
    if genre is not None:
        genre = genre.decode("utf8")

    #print('artist type:', type(artist), type(album), type(song))

    cursor.execute("SELECT * FROM Music WHERE OsFileName = ?", [key])
    d = dict(cursor.fetchone())
    if d is None:
        print('SQL update_metadata() error no music ID for:', key)
        return

    # Debugging information to comment out later (or perhaps logging?)
    '''
    print('\nSQL updating metadata for:',key)
    print('artist type :', type(artist), type(album), type(song), \
                           type(genre))
    print('library type:', type(d['MetaArtistName']), \
                           type(d['MetaAlbumName']), \
                           type(d['MetaSongName']), type(d['Genre']))
    print(artist       , d['MetaArtistName'])
    print(album        , d['MetaAlbumName'])
    print(song         , d['MetaSongName'])
    print(genre        , d['Genre'])
    print(tracknumber  , d['TrackNumber'])
    print(date         , d['ReleaseDate'])
    print(seconds      , d['Seconds'])
    print(duration     , d['Duration'])

    if artist      != d['MetaArtistName']:
        print('artist:', artist, d['MetaArtistName'])
    elif album       != d['MetaAlbumName']:
        print('album:', album, d['MetaAlbumName'])
    elif song        != d['MetaSongName']:
        print('song:', song, d['MetaSongName'])
    elif genre       != d['Genre']:
        print('genre:', genre, d['Genre'])
    elif tracknumber != d['TrackNumber']:
        print('tracknumber:', tracknumber, d['TrackNumber'])
    elif date        != d['ReleaseDate']:
        print('date:', date, d['ReleaseDate'])
    elif seconds     != d['Seconds']:
        print('seconds:', seconds, d['Seconds'])
    elif duration    != d['Duration']:
        print('duration:', duration, d['Duration'])
    else:
        print('All things considered EQUAL')
    '''

    # Are we adding a new 'init' or 'edit' history record?
    if d['MetaArtistName'] is None:
        action = 'init'
        # print('\nSQL adding metadata for:',key)
    elif \
        artist       != d['MetaArtistName'] or \
        album        != d['MetaAlbumName'] or \
        song         != d['MetaSongName'] or \
        genre        != d['Genre'] or \
        tracknumber  != d['TrackNumber'] or \
        date         != d['ReleaseDate'] or \
        seconds      != d['Seconds'] or \
            duration != d['Duration']:
        # To test, use kid3 to temporarily change track number
        # float(date) != d['ReleaseDate'] or \ <- They both could be None
        # Metadata hsa changed from last recorded version
        action = 'edit'

    else:
        return                                  # Metadata same as library

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
    # Below not needed because (No Xxx) stubs not in Music Table filenames
    full_path = full_path.replace(os.sep + NO_ARTIST_STR, '')
    full_path = full_path.replace(os.sep + NO_ALBUM_STR, '')

    # os.stat gives us all of file's attributes
    stat = ext.stat_existing(full_path)
    if stat is None:
        print("sql.update_metadata(): File below doesn't exist:\n")
        for i in d:
            # Pad name with spaces for VALUE alignment
            print('COLUMN:', "{:<25}".format(i), 'VALUE:', d[i])
        return

    Size = stat.st_size                     # File size in bytes
    Time = stat.st_mtime                    # File's current mod time
    SourceMaster = _LODICT['name']
    SourceDetail = time.asctime(time.gmtime(Time))
    Comments = "Found: " + time.asctime(time.gmtime(time.time()))
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


#==============================================================================
#
#       sql.py - History table processing
#
#==============================================================================


def hist_get_row(key):
    # Get the MusicID matching song file's basename
    cursor.execute("SELECT * FROM History WHERE Id = ?", [key])
    row = cursor.fetchone()
    if row is None:
        print('sql.py - row not found:', key)
        return None

    return OrderedDict(row)


def hist_get_music_id(key):
    # Get the MusicID matching song file's basename
    cursor.execute("SELECT Id FROM Music WHERE OsFileName = ?", [key])
    row = cursor.fetchone()
    if row is None:
        print('hist_get_music_id(key) error no music ID for:', key)
        return 0
    elif row[0] == 0:
        print('hist_get_music_id(key) error music ID is 0:', key)
        return 0
    else:
        return row[0]


def hist_add_time_index(key, time_list):
    """
        Add time index if 'init' doesn't exist.
        If time index does exist, add an 'edit' if it has changed.
    """
    # Get the MusicID matching song file's basename
    MusicId = hist_get_music_id(key)
    if MusicId == 0:
        print('SQL hist_add_time_index(key) error no music ID for:', key)
        return False

    if hist_check(MusicId, 'time', 'init'):
        # We found a time initialization record to use as default
        Action = 'edit'
        print('sql.hist_add_time_index(key) edit time, init:', key, HISTORY_ID)
        hist_cursor.execute("SELECT * FROM History WHERE Id = ?", [HISTORY_ID])
        d = dict(hist_cursor.fetchone())
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
    Comments = Action + " time: " + time.asctime(time.gmtime(time.time()))
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
    d = dict(cursor.fetchone())
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

    SourceDetail = time.asctime(time.gmtime(Time))
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
    MusicId = hist_get_music_id(key)
    if MusicId == 0:
        print('SQL hist_delete_time_index(key) error no music ID for:', key)
        return False

    if not hist_check(MusicId, 'time', 'init'):
        # We found a time initialization record to use as default
        print('sql.hist_delete_time_index(key) error no time, init:', key)
        return False

    print('sql.hist_delete_time_index(key) HISTORY_ID:', key, HISTORY_ID)

    hist_cursor.execute("SELECT * FROM History WHERE Id = ?", [HISTORY_ID])
    d = dict(hist_cursor.fetchone())
    if d is None:
        print('sql.hist_delete_time_index(key) error no History ID:', key,
              HISTORY_ID)
        return False

    Comments = "Removed: " + time.asctime(time.gmtime(time.time()))
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
    As of April 13, 2021:
    DICT={'iid': iid, 'name': name, 'topdir': topdir, 'host': host, 'wakecmd':
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
            print("sql.hist_init_lost_and_found(): File below doesn't exist:\n")
            names = cursor.description
            for i, name in enumerate(names):
                # Pad name with spaces for VALUE alignment
                print('COLUMN:', "{:<25}".format(name[0]), 'VALUE:', row[i])
            continue  # TODO: do "lost" phase, mark song as deleted somehow

        Size = stat.st_size                     # File size in bytes
        Time = stat.st_mtime                    # File's current mod time
        SourceDetail = time.asctime(time.gmtime(Time))
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
        Type            'file', 'catalog', 'link', 'index', 'checkout', 'song'
                        'lyrics', 'time', 'fine-tune', 'meta', 'playlist'
        Action          'copy', 'download', 'remove', 'burn', 'edit', 'play'
                        'scrape', 'init', 'shuffle', 'save', 'load'
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
                                   "WHERE MusicId = ?", [MusicId]):
        Id = row[0]
        Type = row[1]
        Action = row[2]
        if Type == check_type and Action == check_action:
            HISTORY_ID = Id
            return True

    HISTORY_ID = 0
    return False                # Not Found


def hist_last_time(check_type, check_action):
    """ Get the last time the type + action occurred

        Primarily used to get the last time a song was added / updated in
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
    """
    # DEBUG:
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
        SourceDetail = time.asctime(time.gmtime(Time))
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


# =================================  WEBSCRAPE  ===============================

class Webscrape:

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

            MusicId = sql.hist_get_music_id(self.work_sql_key)
            sql.hist_add(time.time(), MusicId, USER,
                         'scrape', 'parm', artist, song,
                         "", 0, 0, 0.0,
                         time.asctime(time.gmtime(time.time())))
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
        return


# ==============================================================================
#
#       PrettyHistory class - DIFFERENT than ~/bserve/sql.py
#
# ==============================================================================


class PrettyHistory:

    def __init__(self, history_dict, calc=None):
        """ 
            Copied from bserve/gmail_api.py PrettyHistory

                1) top level dictionary key/values like Id, size

             After massaging, four sections are at single dictionary level
             Dictionary keys can be walked and compared to count of keys at
             each part for separating sections in display.

            This class serves double duty (for now) to display treeview column
            data dictionary for class view()) at column name.

            calc is optional function to append calculated fields to the
            pretty dictionary.

        """

        self.calc = calc  # Calculated fields such as delete_on
        self.dict = OrderedDict()  # Python 2.7 version not needed in 3.7
        self.scrollbox = None  # custom scrollbox for display

        # IF dictionary for treeview column, format is straight forward
        self.part_start = [0]  # Only 1 part
        self.part_names = ['Tkinter Treeview']
        self.part_color = ['red']
        for key, value in history_dict.iteritems():
            self.dict[key] = self.format_value(value)

        if calc is None:
            # If no calc callback we are done.
            return

        # List of part section headings at part_start[] list above
        self.part_names = ['Google search results',
                           'Webscrape results']
        # List of part colors - applied to key names in that part
        self.part_color = ['red',
                           'blue']

        self.part_start.append(len(self.dict))

        self.calc(self.dict)  # Call external function passing our dict
        # print("self.calc(self.dict)  # Call external function passing our dict")

        # print('\n======================  pretty  =====================\n')
        # print(json.dumps(self.dict, indent=2))

    @staticmethod
    def format_value(value):

        try:
            formatted = str(value)  # Convert from int
        except UnicodeEncodeError:
            formatted = value
        # return formatted.encode('utf8')
        return formatted

    def tkinter_display(self, scrollbox):
        """ Popup display all values in pretty print format
            Uses new tkinter window with single text entry field

            Requires ordered dict and optional lists specifying sections
            (parts) the part names and part colors for key names.
        """

        self.scrollbox = scrollbox  # Temporary until code craft

        # Allow program changes to scrollable text widget
        self.scrollbox.configure(state="normal")
        self.scrollbox.delete('1.0', 'end')  # Delete previous entries

        curr_key = 0  # Current key index
        curr_level = 0  # Current dictionary part
        curr_color = 'black'
        # for key, value in self.dict.iteritems():    # Don't use iteritems
        for key in self.dict:  # Don't need iteritems on ordered dict
            if curr_key == self.part_start[curr_level]:
                curr_level_name = self.part_names[curr_level]
                curr_color = self.part_color[curr_level]
                self.scrollbox.insert("end", curr_level_name + "\n")
                # self.scrollbox.highlight_pattern(curr_level_name, 'yellow')
                curr_level += 1

                if curr_level >= len(self.part_start):
                    curr_level = len(self.part_start) - 1
                    # We are in last part so no next part to check
                    # print('resetting curr_level at:', key)

            # Insert current key and value into text widget
            # TclError: character U+1f913 is above the range (U+0000-U+FFFF) allowed by Tcl
            # noinspection PyBroadException
            try:
                self.scrollbox.insert("end", u"\t" + key + u":\t" +
                                      self.dict[key] + u"\n", u"margin")
            #                                  value + u"\n", "margin")
            except:
                normal = normalize_tcl(self.dict[key])
                self.scrollbox.insert("end", u"\t" + key + u":\t" +
                                      normal + u"\n", u"margin")

            self.scrollbox.highlight_pattern(key + u':', curr_color)
            curr_key += 1  # Current key index

        # Override for auto trader that contains multiple keys within value
        self.scrollbox.highlight_pattern(
            "From:To:Subject:Date:List-Unsubscribe:List-Unsubscribe-Post:" +
            "MIME-Version: Reply-To:List-ID:X-CSA-Complaints:Message-ID:" +
            "Content-Type:", "black")

        self.scrollbox.highlight_pattern(
            "Date:Message-ID:Content-Type:Subject:To:", "black")

        # Override for disqus that contains multiple keys within value
        self.scrollbox.highlight_pattern(
            "Subject:From:To:", "black")

        # Don't allow changes to displayed selections (test copy clipboard)
        self.scrollbox.configure(state="disabled")


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


def music_treeview():
    """ Define Data Dictionary treeview columns for history table
    """

    music_treeview_list = [

      OrderedDict([
        ("column", "row_id"), ("heading", "Row ID"), ("sql_table", "Music"),
        ("var_name", "Id"), ("select_order", 0), ("unselect_order", 1),
        ("key", False), ("anchor", "e"), ("instance", int), ("format", "{,,}"),
        ("display_width", 150), ("display_min_width", 80),
        ("display_long", None), ("stretch", 0)]),  # 0=NO, 1=YES

      OrderedDict([
        ("column", "os_filename"), ("heading", "OS Filename"), ("sql_table", "Music"),
        ("var_name", "OsFileName"), ("select_order", 0), ("unselect_order", 2),
        ("key", True), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 200), ("display_min_width", 120),
        ("display_long", None), ("stretch", 0)]),  # 0=NO, 1=YES

      OrderedDict([
        ("column", "os_atime"), ("heading", "Access Time"), ("sql_table", "Music"),
        ("var_name", "OsAccessTime"), ("select_order", 0), ("unselect_order", 3),
        ("key", False), ("anchor", "w"), ("instance", float), ("format", "{0,,f}"),
        ("display_width", 80), ("display_min_width", 80),
        ("display_long", None), ("stretch", 0)]),  # 0=NO, 1=YES

      OrderedDict([
        ("column", "os_mtime"), ("heading", "Mod Time"), ("sql_table", "Music"),
        ("var_name", "OsModificationTime"), ("select_order", 0), ("unselect_order", 4),
        ("key", False), ("anchor", "w"), ("instance", float), ("format", "{0,,f}"),
        ("display_width", 80), ("display_min_width", 80),
        ("display_long", None), ("stretch", 0)]),

      OrderedDict([
        ("column", "os_ctime"), ("heading", "Create Time"), ("sql_table", "Music"),
        ("var_name", "OsCreationTime"), ("select_order", 0), ("unselect_order", 5),
        ("key", False), ("anchor", "e"), ("instance", float),
        ("format", "{0,,f}"), ("display_width", 80),
        ("display_min_width", 80), ("display_long", None), ("stretch", 0)]),

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
        ("display_width", 400), ("display_min_width", 140),
        ("display_long", None), ("stretch", 1)]),  # 0=NO, 1=YES

      OrderedDict([
        ("column", "album"), ("heading", "Album"), ("sql_table", "Music"),
        ("var_name", "Album"), ("select_order", 0), ("unselect_order", 8),
        ("key", False), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 400), ("display_min_width", 140),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "song_name"), ("heading", "Song Name"), ("sql_table", "Music"),
        ("var_name", "MetaSongName"), ("select_order", 0), ("unselect_order", 9),
        ("key", False), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 400), ("display_min_width", 140),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "release_date"), ("heading", "Release Date"), ("sql_table", "Music"),
        ("var_name", "ReleaseDate"), ("select_order", 0), ("unselect_order", 10),
        ("key", False), ("anchor", "w"), ("instance", float), ("format", "{0,,f}"),
        ("display_width", 80), ("display_min_width", 80),
        ("display_long", None), ("stretch", 0)]),

      OrderedDict([
        ("column", "original_date"), ("heading", "Original Date"), ("sql_table", "Music"),
        ("var_name", "OriginalDate"), ("select_order", 0), ("unselect_order", 11),
        ("key", False), ("anchor", "w"), ("instance", float), ("format", "{0,,f}"),
        ("display_width", 80), ("display_min_width", 80),
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
        ("display_width", 160), ("display_min_width", 140),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "track_number"), ("heading", "Track Number"), ("sql_table", "Music"),
        ("var_name", "TrackNumber"), ("select_order", 0), ("unselect_order", 16),
        ("key", False), ("anchor", "e"), ("instance", str), ("format", None),
        ("display_width", 160), ("display_min_width", 140),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "rating"), ("heading", "Rating"), ("sql_table", "Music"),
        ("var_name", "Rating"), ("select_order", 0), ("unselect_order", 17),
        ("key", False), ("anchor", "w"), ("instance", int), ("format", "{:,}"),
        ("display_width", 160), ("display_min_width", 140),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "lyrics"), ("heading", "Lyrics"), ("sql_table", "Music"),
        ("var_name", "UnsynchronizedLyrics"), ("select_order", 0), ("unselect_order", 18),
        ("key", False), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 600), ("display_min_width", 140),
        ("display_long", None), ("stretch", 1)]),

      OrderedDict([
        ("column", "time_index"), ("heading", "Time Index"), ("sql_table", "Music"),
        ("var_name", "LyricsTimeIndex"), ("select_order", 0), ("unselect_order", 19),
        ("key", False), ("anchor", "w"), ("instance", str), ("format", None),
        ("display_width", 160), ("display_min_width", 140),
        ("display_long", None), ("stretch", 1)])
    ]

    return music_treeview_list


def history_treeview():
    """ Define Data Dictionary treeview columns for history table.  Snippet:
        ("column", "row_id"), ("heading", "Row ID"), ("sql_table", "History"),
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
        ("column", "delete_on"), ("heading", "Delete On"), ("sql_table", "calc"),
        ("column", "reason"), ("heading", "Reason"), ("sql_table", "calc"),

    """

    history_treeview_list = [

      OrderedDict([
        ("column", "time"), ("heading", "Time"), ("sql_table", "History"),
        ("var_name", "Time"), ("select_order", 0), ("unselect_order", 1),
        ("key", False), ("anchor", "w"), ("instance", float),
        ("format", "{0:,.4f}"), ("display_width", 240),
        ("display_min_width", 120), ("display_long", None), ("stretch", 0)]),

      OrderedDict([
        ("column", "music_id"), ("heading", "Music ID"), ("sql_table", "History"),
        ("var_name", "MusicId"), ("select_order", 0), ("unselect_order", 2),
        ("key", False), ("anchor", "e"), ("instance", int), ("format", None),
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
        ("key", True), ("anchor", "e"), ("instance", int), ("format", None),
        ("display_width", 140), ("display_min_width", 100),
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


def update_history(scraped_dict):

    for i, website in enumerate(scraped_dict):
        if len(website['link']) > 2 and website['flag'] != 'skip':
            pass
            # Check for duplicates
        else:
            pass

# if there are existing history records identical to scraped_dict
# we want to skip adding. We might want to update time though.


def create_webscrape(music_id, website):

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

    # match is on website human formatted name not internet
    #  formatted name. EG "Genius' not '//genius.com'
    print('music_id parameter not used:', music_id, website)

    pass


# =================================  MISCELLANEOUS  ===========================


def alter_table1(cur, table, *args):
    """ Copied from simple_insert(), still needs to be changed. """
    query = 'INSERT INTO '+table+' VALUES (' + '?, ' * (len(args)-1) + '?)'
    cur.execute(query, args)


def simple_insert(cur, table, *args):
    query = 'INSERT INTO '+table+' VALUES (' + '?, ' * (len(args)-1) + '?)'
    cur.execute(query, args)


default_value = {'TEXT': '""', 'INT': '0', 'FLOAT': '0.0', 'BLOB': '""'}


def insert_blank_line(table_name):
    """ Add underscores to insert_blank_line and table_name for pycharm syntax checking.
        If pragma breaks then remove underscores.
    """
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
