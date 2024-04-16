#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: pippim.com
License: GNU GPLv3. (c) 2020 - 2023
Source: This repository
Description: mserve - Music Server - SQLite3 Interface
"""

from __future__ import print_function  # Must be first import
from __future__ import with_statement  # Error handling for file opens
# from __future__ import unicode_literals  # Not needed.
import copy
import warnings  # 'warnings' advises which commands aren't supported
warnings.simplefilter('default')  # in future Python versions.

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
#       July 12 2023 - Interface to/from mserve_config.py
#       July 13 2023 - Add Music columns: LastPlayTime, DiscNumber, AlbumDate,
#                      FirstDate, (was ReleaseDate), CreationTime, Composer
#       Aug. 10 2023 - Add Music columns: AlbumArtist, Compilation, Comment,
#                      GaplessPlayback
#       Aug. 19 2023 - Add known SQL metadata to FileControl() variables.
#       Aug. 20 2023 - Print SQL Table sizes and Row Counts by Type
#       Mar. 09 2024 - print_windows() - Print Window offsets, sizes and name
#       Mar. 24 2024 - Save treeview configuration. Revamp dict_treeview.

#   TODO:

#   Create tables should not be saving OsFileNames that haven't been played
#       especially for locations that may never be saved 

#   Create Fix function to touch OsAccessTime using OsModifyTime

#   Create FileControl.get_last_played_time() for lib_tree display when N/A
#       use st.atime() instead.

#
#==============================================================================

# noinspection SpellCheckingInspection
''' TODO:

    SQL version 3 effects bserve.py. It needs upgrading now: 

Traceback (most recent call last):
  File "/usr/lib/python2.7/lib-tk/Tkinter.py", line 1540, in __call__
    return self.func(*args)
  File "/home/rick/bserve/bserve.py", line 1237, in bup_close
    monitor.save_window_geom('backups', last_backups_geom)
  File "/home/rick/bserve/monitor.py", line 886, in save_window_geom
    sql.hist_cursor.execute(sql_cmd, (time.time(), geom, sql.HISTORY_ID))
OperationalError: no such column: Timestamp



    History Table is very large. After a few months delete history prior
    to cutoff date. Output from mserve.py show_debug() is below:

    SQL Location Table      Page Count: 1           Size of all pages: 1,024
    SQL Music Table         Page Count: 3,874       Size of all pages: 3,966,976
    SQL History Table       Page Count: 4,520 	    Size of all pages: 4,628,480
            History Table rows:  | Type='file' | Action='init' |  count: 3,905
            History Table rows:  | Type='file' | Action='edit' |  count: 44
            History Table rows:  | Type='meta' | Action='init' |  count: 3,768
            History Table rows:  | Type='meta' | Action='edit' |  count: 9,784


    When vacuuming, the primary keys are left intact: 
        https://stackoverflow.com/questions/76940830/
        python-sqlite3-vacuum-with-and-without-reseting-primary-key?
        noredirect=1#comment135636425_76940830
    

    The SQLite VACUUM command https://www.sqlitetutorial.net/sqlite-vacuum/
    
    The VACUUM command does not change the content of the database except 
    the rowid values. If you use INTEGER PRIMARY KEY column, the VACUUM 
    does not change the values of that column. However, if you use un-aliased 
    rowid, the VACUUM command will reset the rowid values. Besides changing 
    the rowid values, the VACUUM command also builds the index from scratch.
    
    It is a good practice to perform the VACUUM command periodically, 
    especially when you delete large tables or indexes from a database.
    
    It is important to note that the VACUUM command requires storage to 
    hold the original file and also the copy. Also, the VACUUM command 
    requires exclusive access to the database file. In other words, the 
    VACUUM command will not run successfully if the database has a pending 
    SQL statement or an open transaction.
    
    Currently, as of version 3.9.2, you can run the VACUUM command on the 
    main database, not the attached database file.
    
    Even though SQLite enables the auto-vacuum mode that triggers the 
    vacuum process automatically with some limitations. It is a good 
    practice to run the VACUUM command manually.


'''

''' If not called by 'mserve.py' do nothing '''
import inspect
import os
try:
    filename = inspect.stack()[1][1]  # parent filename s/b "mserve.py"
    #(<frame object>, './m', 50, '<module>', ['import mserve\n'], 0)
    parent = os.path.basename(filename)
    if parent != "mserve.py":
        #print("sql.py must be called by 'mserve.py' but is being called " +
        #      "by: '" + parent + "'.")
        #exit()
        # sql.py must be called by 'mserve.py' but is called by: monitor.py
        pass
except IndexError:  # list index out of range
    ''' Called from the command line '''
    print("sql.py cannot be called from command line. Aborting...")
    exit()

import os
import re
import json
import math
import time
import datetime
from collections import OrderedDict

# dist-package?
import sqlite3

# pippim modules
import global_variables as g        # should be self-explanatory
if g.USER is None:
    print('sql.py was forced to run g.init()')
    g.init()
import toolkit
import timefmt as tmf               # Custom time formatting functions
import external as ext              # Custom date formatting used here

try:
    # Works when mserve.py is called by 'm'
    from location import FNAME_LIBRARY  # SQL database name (SQLite3 format)
    from location import FNAME_LIBRARY_NEW
except ImportError:
    # Appears when running mserve.py directly
    print("'from location import FNAME_LIBRARY' FAILED !!!")
    FNAME_LIBRARY = g.USER_DATA_DIR + os.sep + "library.db"
    FNAME_LIBRARY_NEW = g.USER_DATA_DIR + os.sep + "library_new.db"
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
con = cursor = hist_cursor = loc_cursor = None
new_con = new_cursor = new_hist_cursor = new_loc_cursor = None
NEW_LOCATION = False
SORTED_LIST = START_DIR = lcs = LODICT = None
PRUNED_DIR = ""  # When needed, the /artist/album/ prepended to build filename
PRUNED_COUNT = len(PRUNED_DIR)  # Length of prepended path


def populate_tables(SortedList, start_dir, pruned_dir, lodict):
    """ Create SQL tables out of OS sorted music top directory
    """
    global NEW_LOCATION, SORTED_LIST, START_DIR, PRUNED_DIR, LODICT
    SORTED_LIST = SortedList
    START_DIR = start_dir
    PRUNED_DIR = pruned_dir  # Toplevel directory, EG /mnt/music/
    LODICT = lodict  # Location dictionary Aug 3/23 - soon will be <type None>

    ''' NOTE from mserve.py June/2023:
    LODICT['iid'] = 'new'  # June 6, 2023 - Something new to fit into code
    LODICT['name'] = music_dir  # Name required for title bar
    NEW_LOCATION = True  # Don't use location dictionary (LODICT) fields

    Removed Aug 8/23:
    if LODICT:  # Temporary for conversion away from LODICT
        if LODICT['iid'] == 'new':
            NEW_LOCATION = True
    else:
        if lcs.open_code == 'new':
            NEW_LOCATION = True
    '''
    if lcs.open_code == 'new':
        NEW_LOCATION = True

    #open_db()  # July 24, 2023 Note new Locations() class has already opened
    #open_new_db()  # July 13, 2023

    ''' 2024-02-09 Artist & Album not used. 
    LastArtist = ""         # For control breaks
    LastAlbum = ""
    '''

    for i, os_name in enumerate(SORTED_LIST):

        ''' 2024-02-09 Artist & Album not used. 
        # split '/mnt/music/Artist/Album/Song.m4a' into list
        base_path = os_name[len(PRUNED_DIR):]
        groups = base_path.split(os.sep)
        Artist = groups[0]
        Album = groups[1]
        '''
        key = os_name[len(PRUNED_DIR):]

        ''' 2024-02-09 Artist & Album not used. 
        if Artist != LastArtist:
            LastArtist = Artist
            LastAlbum = ""          # Force sub-total break for Album

        if Album != LastAlbum:
            LastAlbum = Album
        '''

        ''' Build full song path from song_list[] '''
        full_path = os_name
        full_path = full_path.replace(os.sep + NO_ARTIST_STR, '')
        full_path = full_path.replace(os.sep + NO_ALBUM_STR, '')
        sql_key = full_path[len(PRUNED_DIR):]

        ''' June 2, 2023 - Do not store songs with missing artist or album '''
        if os.sep + NO_ARTIST_STR in key or os.sep + NO_ALBUM_STR in key:
            ofb.AddBlacklist(sql_key)
            continue

        ''' June 10, 2023 - Do not store songs without two os.sep '''
        if sql_key.count(os.sep) != 2:
            #print("skipping sql_key without 2 separators:", sql_key)
            ofb.AddBlacklist(sql_key)
            continue

        ''' For FTP curlftpfs takes too much time to stat each file '''
        d = ofb.Select(sql_key)
        if d:
            continue  # already in SQL Music Table

        ''' TODO: Make into function that sets LastPlayTime '''
        try:
            stat = os.stat(full_path)  # Get file attributes
        except OSError:
            print("Could not stat:", full_path)
            continue


        ''' Add SQL music metadata if it doesn't exist already. 
            Previously have validated:
                Full path of topdir/artist/album/song exists
                song is not in SQL music table yet
        '''
        sql = "INSERT OR IGNORE INTO Music (OsFileName, \
               OsAccessTime, OsModifyTime, OsChangeTime, OsFileSize) \
               VALUES (?, ?, ?, ?, ?)" 
        cursor.execute(sql, (key, stat.st_atime, stat.st_mtime,
                             stat.st_ctime, stat.st_size))

    con.commit()
    #print(cfg.defaults)
    #cfg.print_windows()  # Just a little test to remove later

    # Temporary during development to record history for lyrics web scrape and
    # time index synchronizing to lyrics.
    #ext.t_init("SQL startup functions to remove")
    #ext.t_init("hist_init_lost_and_found")
    #hist_init_lost_and_found()
    #job_time = ext.t_end('print')
    #print("Did not print? job_time:", job_time)  # 0.0426070690155
    #ext.t_init("hist_init_lyrics_and_time")
    #hist_init_lyrics_and_time()
    #job_time = ext.t_end('print')  # 0.0366790294647
    #print("Did not print? job_time:", job_time)
    #job_time = ext.t_end('print')  # 0.0793550014496
    #print("Did not print? job_time:", job_time)

    # June 3, 2023 before: sql.populate_tables(): 0.1658391953
    # June 3, 2023 AFTER : sql.populate_tables(): 0.0638458729
    ''' TODO: record history totals '''


def fix_os_last_access():
    """ Last access date corrupted by Nautilus scanning files starting in
        the Fall/Winter 2023.

    https://www.geeksforgeeks.org/python-os-utime-method/

    import os

    # Path
    path = '/home / me / Documents / file.txt'

    # Print current access and modification time
    print("Current access time (in seconds):", os.stat(path).st_atime)
    print("Current modification time (in seconds):", os.stat(path).st_mtime)

    # Access time in nanoseconds
    atime_ns = 20000000012345

    # Modification time in nanoseconds
    mtime_ns = 10000000012345

    tup = (atime_ns, mtime_ns)
    os.utime(path, ns=tup)

    print("\nAccess and modification time changed\n")

    # Print current access and modification time
    print("Current access time (in seconds):", os.stat(path).st_atime)
    print("Current modification time (in seconds):", os.stat(path).st_mtime)


    """
    global NEW_LOCATION, SORTED_LIST, START_DIR, PRUNED_DIR  # global not needed

    iRead = iNoAlbum = iNoSep = iNoSql = iNoStat = 0
    iDiff = iSame = iUpdate = iNoUpdate = 0
    if g.DEBUG_LEVEL:
        iPrintTen = 0  # 0 for debug and first 10 printed
    else:
        iPrintTen = 10  # 10 force already printed and no debug

    # noinspection PyTypeChecker
    for i, os_name in enumerate(SORTED_LIST):
        iRead += 1
        ''' Songs missing artist or album subdirectory not in SQL Music Table '''
        sql_key = os_name[len(PRUNED_DIR):]
        if os.sep + NO_ARTIST_STR in sql_key or os.sep + NO_ALBUM_STR in sql_key:
            iNoAlbum += 1
            if iPrintTen < 10:
                # Don't increment print counter as this is more like a warning
                print("iNoAlbum:", iNoAlbum, os_name)
            continue

        ''' Skip songs without two os.sep '''
        if sql_key.count(os.sep) != 2:
            iNoSep += 1
            continue

        ''' Get SQL Music Table Row as 'd' '''
        d = ofb.Select(sql_key)
        if not d:
            iNoSql += 1
            continue  # Not in SQL Music Table

        ''' Try to get OS information (metadata) on file '''
        try:
            stat = os.stat(os_name)  # Get file attributes
        except OSError:
            print("Could not stat os_name:", os_name)
            iNoStat += 1
            continue

        ''' Is last access time the same? '''
        fElapsed = math.fabs(d['OsAccessTime'] - stat.st_atime)
        # Fix stat.st_atime: 1694283346.0, d['LastPlayTime']: 1694283346.01
        try:
            fLastPlayTime = float(math.trunc(d['LastPlayTime']))
        except AttributeError:
            fLastPlayTime = 0.0
        fElapsed2 = math.fabs(fLastPlayTime - stat.st_atime)
        fCompare = 2.  # 2 second grace period
        if fElapsed < fCompare or fElapsed2 < fCompare:
            is_same = True
        else:
            is_same = False

        if is_same:
            iSame += 1
            if iPrintTen < 10:
                #iPrintTen += 1
                print("2 SECS 'OsAccessTime':", ext.t(d['OsAccessTime']),
                      " | 'LastPlayTime':", ext.t(fLastPlayTime),
                      "\n   ", sql_key, "\n   ", "stat.st_mtime:",
                      ext.t(stat.st_mtime), " | stat.st_atime:",
                      ext.t(stat.st_atime))
                pass
            continue

        ''' Last access time is different '''
        iDiff += 1
        if iPrintTen < 10:
            #iPrintTen += 1
            #print("DIFF stat.st_atime:", ext.t(stat.st_atime),
            #      "!= 'OsAccessTime':", ext.t(d['OsAccessTime']),
            #      "\n   ", sql_key)
            pass

        ''' Only update last access time > SQL initially recorded values '''
        if stat.st_atime < d['OsAccessTime']:
            if iPrintTen < 10:
                # Don't increment print counter as this is more like a warning
                print("ACCESS stat.st_atime :", ext.t(stat.st_atime),
                      "< 'OsAccessTime':", ext.t(d['OsAccessTime']),
                      "\n   ", sql_key)

            ''' 10% of records are an exception to the rule... 
            E.G.
ACCESS stat.st_atime : Feb 06 2021 05:00:00 PM < d['OsAccessTime']: Feb 07 2021 04:24:24 PM 
     Bad Company/10 From 6/01 Can't Get Enough.m4a
ACCESS stat.st_atime : May 24 2021 06:00:00 PM < d['OsAccessTime']: May 25 2021 04:50:55 PM 
     Nazareth/The Anthology [Disc #1 of 2]/1-04 Woke Up This Morning.oga
ACCESS stat.st_atime : Feb 06 2021 05:00:00 PM < d['OsAccessTime']: Feb 07 2021 03:58:37 PM 
     White Zombie/Best Of 90s Rock Volume 2 - 20th Century/12 More Human Than Human.m4a

            ... It's likely SQL last access time had a bug but it is easier to change
                File's time using existing code below.            
            '''
            fElapsed = d['OsAccessTime'] - stat.st_atime
            fCompare = 60.0 * 60.0 * 48  # Allow 48 hours / two days grace period
            if fElapsed > fCompare:
                iNoUpdate += 1
                continue
            else:
                print("2 DAYS stat.st_atime :", ext.t(stat.st_atime),
                      "< 'OsAccessTime':", ext.t(d['OsAccessTime']),
                      "\n   ", sql_key)

        ''' Only update SQL initially recorded values >= modification time '''
        if stat.st_mtime > d['OsAccessTime']:
            if stat.st_atime == stat.st_mtime:
                # Already set on previous run
                iSame += 1
                iDiff -= 1
                continue
            # Set new stat.st_atime to stat.st_mtime instead of OsAccessTime.
            print("MODIFY stat.st_mtime :", ext.t(stat.st_mtime),
                  "> 'OsAccessTime':", ext.t(d['OsAccessTime']),
                  "\n   ", sql_key)
            newAccessTime = stat.st_mtime
        else:
            newAccessTime = d['OsAccessTime']  # Use SQL Music Table Row's time
            if fLastPlayTime > newAccessTime:
                if stat.st_atime == fLastPlayTime:
                    # Already set on previous run
                    iSame += 1
                    iDiff -= 1
                    continue
                # Set new stat.st_atime to LastPlayTime.
                print("L_PLAY 'OsAccessTime':", ext.t(d['OsAccessTime']),
                      "<= 'LastPlayTime':", ext.t(fLastPlayTime),
                      "\n   ", sql_key, "\n   ", "stat.st_mtime:",
                      ext.t(stat.st_mtime), " | stat.st_atime:",
                      ext.t(stat.st_atime))
                newAccessTime = fLastPlayTime  # Use truncated LastPlayTime
            else:
                # Set new stat.st_atime to OsAccessTime.
                print("MODIFY stat.st_mtime:", ext.t(stat.st_mtime),
                      "<= 'OsAccessTime':", ext.t(d['OsAccessTime']),
                      "\n   ", sql_key)

        tup = (newAccessTime, stat.st_mtime)
        os.utime(os_name, tup)

        iUpdate += 1

    print()
    print("iRead:", iRead, " | iNoAlbum:", iNoAlbum, " | iNoSep:", iNoSep,
          " | iNoStat:", iNoStat, " | iNoSql:", iNoSql, " | iDiff:", iDiff)
    print("iSame:", iSame, " | iUpdate :", iUpdate,  " | iNoUpd:", iNoUpdate)
    print()  # Give me a little space!


def open_db(LCS=None):
    """ Open SQL Tables - Music Table and History Table
        Create Tables and Indices that don't exist
    :param LCS: instance of Location() class for lcs.open_code, etc.
    """

    #open_new_db()  # Database 'library_new.db' only used for conversions.

    global con, cursor, hist_cursor, loc_cursor, lcs
    if LCS:
        lcs = LCS  # Locations class

    con = sqlite3.connect(FNAME_LIBRARY)

    # MUSIC TABLE
    """ Version 3 """
    con.execute(
        "create table IF NOT EXISTS Music(Id INTEGER PRIMARY KEY, " +
        "OsFileName TEXT, OsAccessTime FLOAT, OsModifyTime FLOAT, " +
        "OsChangeTime FLOAT, OsFileSize INT, " +
        "ffMajor TEXT, ffMinor TEXT, ffCompatible TEXT, " +
        "Title TEXT, Artist TEXT, Album TEXT, Compilation TEXT, " +
        "AlbumArtist TEXT, AlbumDate TEXT, FirstDate TEXT, " +
        "CreationTime TEXT, DiscNumber TEXT, TrackNumber TEXT, " +
        "Rating TEXT, Genre TEXT, Composer TEXT, Comment TEXT, " +
        "Hyperlink TEXT, Duration TEXT, Seconds FLOAT, " +
        "GaplessPlayback TEXT, PlayCount INT, LastPlayTime FLOAT, " +
        "LyricsScore BLOB, LyricsTimeIndex TEXT)")

    """ Version 2 
    con.execute("CREATE TABLE IF NOT EXISTS Music(Id INTEGER PRIMARY KEY, " +
                "OsFileName TEXT, OsAccessTime FLOAT, OsModifyTime FLOAT, " +
                "OsChangeTime FLOAT, OsFileSize INT, " +
                "Title TEXT, Artist TEXT, Album TEXT, " +
                "ReleaseDate TEXT, RecordingDate TEXT, " +
                "CreationTime TEXT, DiscNumber TEXT, TrackNumber TEXT, " +
                "Rating TEXT, Genre TEXT, Composer TEXT, " +
                "Comment TEXT, Hyperlink TEXT, Duration TEXT, " +
                "Seconds INT, PlayCount INT, LastPlayTime FLOAT, " +
                "LyricsScore BLOB, LyricsTimeIndex TEXT)")
    """

    con.execute("CREATE UNIQUE INDEX IF NOT EXISTS OsFileNameIndex ON " +
                "Music(OsFileName)")

    # HISTORY TABLE
    """ Version 3 """
    con.execute(
        "create table IF NOT EXISTS History(Id INTEGER PRIMARY KEY, " +
        "Time FLOAT, MusicId INTEGER, User TEXT, Type TEXT, " +
        "Action TEXT, SourceMaster TEXT, SourceDetail TEXT, " +
        "Target TEXT, Size INT, Count INT, Seconds FLOAT, " +
        "Comments TEXT, Timestamp FLOAT)")

    """ Version 2 
    con.execute("CREATE TABLE IF NOT EXISTS History(Id INTEGER PRIMARY KEY, " +
                "Time FLOAT, MusicId INTEGER, User TEXT, Type TEXT, " +
                "Action TEXT, SourceMaster TEXT, SourceDetail TEXT, " +
                "Target TEXT, Size INT, Count INT, Seconds FLOAT, " +
                "Comments TEXT)")
    """

    con.execute("CREATE INDEX IF NOT EXISTS MusicIdIndex ON " +
                "History(MusicId)")

    """ Version 3 """
    con.execute("CREATE UNIQUE INDEX IF NOT EXISTS TimeIndex ON " +
                "History(Timestamp)")

    """ Version 2 
    con.execute("CREATE INDEX IF NOT EXISTS TimeIndex ON " +
                "History(Time)")
    """
    con.execute("CREATE INDEX IF NOT EXISTS TypeActionIndex ON " +
                "History(Type, Action)")

    # LOCATION TABLE
    con.execute(
        "CREATE TABLE IF NOT EXISTS Location(Id INTEGER PRIMARY KEY, " +
        "Code TEXT, Name TEXT, ModifyTime FLOAT, ImagePath TEXT, " +
        "MountPoint TEXT, TopDir TEXT, HostName TEXT, " +
        "HostWakeupCmd TEXT, HostTestCmd TEXT, HostTestRepeat INT, " +
        "HostMountCmd TEXT, HostTouchCmd TEXT, HostTouchMinutes INT, " +
        "Comments TEXT)")
    con.execute("CREATE UNIQUE INDEX IF NOT EXISTS LocationCodeIndex ON " +
                "Location(Code)")


    ''' For mserve.py rename_file() function to rename "the" to "The" '''
    con.execute("PRAGMA case_sensitive_like = ON;")

    ''' https://stackoverflow.com/a/19332352/6929343
def get_schema_version(conn):
    cursor = conn.execute('PRAGMA user_version')
    return cursor.fetchone()[0]

def set_schema_version(conn, version):
    conn.execute('PRAGMA user_version={:d}'.format(version))

def initial_schema(conn):
    # install initial schema
    # ...

def upgrade_1_2(conn):
    # modify schema, alter data, etc.

# map target schema version to upgrade step from previous version
upgrade_steps = {
    1: initial_schema,
    2: upgrade_1_2,
}

def check_upgrade(conn):
    current = get_schema_version(conn)
    target = max(upgrade_steps)
    for step in range(current + 1, target + 1):
        if step in upgrade_steps:
            upgrade_steps[step](conn)
            set_schema_version(conn, step)    
    '''
    user_cursor = con.execute("PRAGMA user_version;")
    user_version = user_cursor.fetchone()[0]
    if user_version != int(g.MSERVE_VERSION[:1]):
        print("SQL database incompatible user_version:", user_version)
        print("Contact www.pippim.com for details")

    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    hist_cursor = con.cursor()
    loc_cursor = con.cursor()

    ''' Functions to fix errors in SQL database '''
    #fd = FixData("Fri Aug 18 23:59:59 2023")  # Cutoff time for selections

    #fd.del_music_ids(3913, 5000, update=False)  # Encoding CD test errors
    # Patch run Jun 02, 2023 with "update=True". 39 Music Ids deleted 3908->3946
    # Patch run Jun 07, 2023 with "update=True". 1 Music Ids deleted 2186->2186
    # Patch run Jun 10, 2023 with "update=True". 160 Music Ids deleted 3908->4067
    # Jun 11, 2023 Duplicate "The Very Best Things". 14 Music Ids deleted 1092->1105
    # Jun 11, 2023 Duplicate "The Very Best Things". 14 Music Ids deleted 1106->1119
    # Aug 17, 2023 Encoding "Greatest Hits of the 80's". 27 Music Ids deleted 3913->3935

    #fd.fix_scrape_parm(update=False)
    # Patch run May 23, 2023 with "update=True". 66 corrupt scrape-parm deleted

    #fd.fix_meta_edit(update=False)
    # Patch run May 15, 2023 with "update=True". 290 duplicate meta-edit deleted

    #fd.fix_utc_dates(update=False)
    # NEVER RUN fd.fix_utc_dates() AGAIN OR PERMANENT DAMAGE !!!!!!!!!!!!!!!
    # Patch run May 12, 2023 with "update=True". Thousands converted utc to local

    ''' Restructure database with new columns '''
    #populate_new_database()  # Get from July 13, 2023 backup.
    #convert_to_database3()  # New conversion one-time use it will exit()


def set_db_version(version=3):
    """ Set the user_version when database is created. """
    cursor.execute("PRAGMA user_version = {v:d}".format(v=version))
    con.commit()


# noinspection SpellCheckingInspection
def convert_to_database3():
    """ Read database format 2 and create database format 3
        Backup ~/.local/share/library.db
        set live_update = True
        Review sqlitebrowser ~/.local/share/library_new.db
        If success cp ~/.local/share/library_new.db ~/.local/share/library.db
        After success run "View", "SQL Music", "Update Metadata"

        TODO: Full conversion run
                pgc, pgs = show_sql_table_size("convert", History, prt=False)
                missing_artwork
                new_pgc, new_pgs = show_sql_table_size("convert", History, prt=False)
                message.ShowInfo(... "x new history records", "y new size used"

             Turn off option in missing_artwork to create history records

    """
    live_update = True  # Cannot run twice, it will crash, delete library_new.db
    open_new_db()

    """ Set the user_version when database is created. """
    new_cursor.execute("PRAGMA user_version = {v:d}".format(v=3))
    new_con.commit()

    new_music_id = 0  # Temporary until last row id generated by add
    cursor.execute("SELECT * FROM Music")  # old cursor
    rows = cursor.fetchall()  # old cursor
    ext.t_init("populate_new_music()")
    for sql_row in rows:
        row = dict(sql_row)
        old_music_id = row['Id']
        new_music_id += 1
        if new_music_id == 1:
            print(row, "\n")
        ''' July 13, 2023 column layout
        con.execute("create table IF NOT EXISTS Music(Id INTEGER PRIMARY KEY, " +
                    "OsFileName TEXT, OsAccessTime FLOAT, OsModifyTime FLOAT, " +
                    "OsChangeTime FLOAT, OsFileSize INT, " +
                    "Title TEXT, Artist TEXT, Album TEXT, " +
                    "ReleaseDate TEXT, RecordingDate TEXT, " +
                    "CreationTime TEXT, DiscNumber TEXT, TrackNumber TEXT, " +
                    "Rating TEXT, Genre TEXT, Composer TEXT, " +
                    "Comment TEXT, Hyperlink TEXT, Duration TEXT, " +
                    "Seconds INT, PlayCount INT, LastPlayTime FLOAT, " +
                    "LyricsScore BLOB, LyricsTimeIndex TEXT)")

        July 18, 2023 column layout
        new_con.execute("create table IF NOT EXISTS Music(Id INTEGER PRIMARY KEY, " +
                        "OsFileName TEXT, OsAccessTime FLOAT, OsModifyTime FLOAT, " +
                        "OsChangeTime FLOAT, OsFileSize INT, " +
                        "ffMajor TEXT, ffMinor TEXT, ffCompatible TEXT, " +
                        "Title TEXT, Artist TEXT, Album TEXT, Compilation TEXT, " +
                        "AlbumArtist TEXT, AlbumDate TEXT, FirstDate TEXT, " +
                        "CreationTime TEXT, DiscNumber TEXT, TrackNumber TEXT, " +
                        "Rating TEXT, Genre TEXT, Composer TEXT, Comment TEXT, " +
                        "Hyperlink TEXT, Duration TEXT, Seconds INT, " +
                        "GaplessPlayback TEXT, PlayCount INT, LastPlayTime FLOAT, " +
                        "LyricsScore BLOB, LyricsTimeIndex TEXT)")

    JULY 18, 2023

        Adding iTunes: Compilation ("0" or "1"), GaplessPlayback, AlbumArtist
        Adding Pippim: 
        
        Change  ReleaseDate             -> AlbumDate
                RecordingDate           -> FirstDate

    Revise: mserve.py update_sql_metadata(fc)
            mserve.py rename_files to set Compilation flag or at least warning.
        '''
        OsFileName = row['OsFileName']
        OsAccessTime = row['OsAccessTime']
        OsModifyTime = row['OsModifyTime']
        OsChangeTime = row['OsChangeTime']
        OsFileSize = row['OsFileSize']
        ffMajor = None
        ffMinor = None
        ffCompatible = None
        Title = row['Title']
        Artist = row['Artist']
        Album = row['Album']
        artist_dir = OsFileName.rsplit(os.sep, 2)[0]
        if artist_dir == "Compilations":
            Compilation = "1"
            ''' Exceptions are Recharged by Linkin Park & UB40 Greatest Hits
                They get fixed by renaming out of /Compilations directory  '''
            AlbumArtist = "Various Artists"
        else:
            Compilation = "0"
            AlbumArtist = row['Artist']  # We should be getting metadata?
        AlbumDate = row['RecordingDate']  # Was init in version 2
        FirstDate = row['ReleaseDate']  # Was init in version 2
        if AlbumDate is None:
            AlbumDate = FirstDate  # Can change metadata
        CreationTime = row['CreationTime']
        if CreationTime is None:
            ''' What if creation time in metadata is earlier? '''
            #frmt_date = datetime.datetime.utcfromtimestamp(OsModifyTime).\
            #    strftime("%Y-%m-%d %H:%M:SS")
            # CreationTime = OsModifyTime FORMAT YYYY-MM-DD HH:MM:SS
            pass
        ''' (OsFileName, OsAccessTime, OsModifyTime, OsChangeTime,  
             OsFileSize, ffMajor, ffMinor, ffCompatible, 
             Title, Artist, Album, Compilation, AlbumArtist, 
             AlbumDate, FirstDate, CreationTime, DiscNumber, TrackNumber, 
             Rating, Genre, Composer, Comment, Hyperlink, Duration, Seconds, 
             GaplessPlayback, PlayCount, LastPlayTIme, LyricsScore, 
             LyricsTimeIndex)) '''

        DiscNumber = row['DiscNumber']  # We should be getting metadata?
        TrackNumber = row['TrackNumber']
        Rating = row['Rating']  # Rating is still none
        Genre = row['Genre']
        Composer = row['Composer']  # Can be None
        Comment = None
        Duration = row['Duration']
        try:
            Seconds = float(row['Seconds'])  # Convert from old Int to new Float
        except TypeError:
            print("\nExcept row['Seconds']", row['Seconds'], type(row['Seconds']))
            print("Duration:", Duration, Title)
            print("OsFileName:", OsFileName)
            Seconds = None  # dozen songs, probably no audio as well
        GaplessPlayback = "0"   # We should be getting metadata?
        Hyperlink = row['Hyperlink']  # Can be None
        PlayCount = row['PlayCount']
        LastPlayTime = row['LastPlayTime']
        LyricsScore = row['LyricsScore']
        LyricsTimeIndex = row['LyricsTimeIndex']

        if live_update:
            # 30 columns
            sql = "INSERT INTO Music \
                   (OsFileName, OsAccessTime, OsModifyTime, OsChangeTime, OsFileSize, \
                   ffMajor, ffMinor, ffCompatible, \
                   Title, Artist, Album, Compilation, AlbumArtist, \
                   AlbumDate, FirstDate, CreationTime, DiscNumber, TrackNumber, \
                   Rating, Genre, Composer, Comment, Hyperlink, Duration, Seconds, \
                   GaplessPlayback, PlayCount, LastPlayTime, LyricsScore, \
                   LyricsTimeIndex) \
                   VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, \
                          ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

            new_cursor.execute(  # new_cursor
                sql,
                (OsFileName, OsAccessTime, OsModifyTime, OsChangeTime, OsFileSize,
                 ffMajor, ffMinor, ffCompatible,
                 Title, Artist, Album, Compilation, AlbumArtist,
                 AlbumDate, FirstDate, CreationTime, DiscNumber, TrackNumber, 
                 Rating, Genre, Composer, Comment, Hyperlink, Duration, Seconds, 
                 GaplessPlayback, PlayCount, LastPlayTime, LyricsScore, 
                 LyricsTimeIndex))
            new_music_id = new_cursor.lastrowid
            populate_new_history(old_music_id, new_music_id)

    if live_update:
        populate_new_history(0, 0)  # Do all configuration records last
        populate_new_location()
        new_con.commit()  # new connection
    ext.t_end("print")  # no update: 0.12  live_update: 0.31
    close_new_db()
    close_db()
    exit()


def populate_new_history(oldMusicId, newMusicId):
    """ Copy old history new history changing only music id """
    hist_cursor.execute("SELECT * FROM History INDEXED BY MusicIdIndex \
                        WHERE MusicId = ?", (oldMusicId,))  # use old hist_cursor
    rows = hist_cursor.fetchall()  # old hist_cursor
    for sql_row in rows:
        row = dict(sql_row)
        Time = row['Time']
        #MusicId = row['MusicId']  Use newMusicId
        User = row['User']
        Type = row['Type']
        Action = row['Action']
        SourceMaster = row['SourceMaster']
        SourceDetail = row['SourceDetail']
        Target = row['Target']
        Size = row['Size']
        Count = row['Count']
        Seconds = row['Seconds']
        Comments = row['Comments']
        Timestamp = time.time()
        sql = "INSERT INTO History (Time, MusicId, User, Type, Action, \
               SourceMaster, SourceDetail, Target, Size, Count, Seconds, \
               Comments, Timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        new_hist_cursor.execute(
            sql,
            (Time, newMusicId, User, Type, Action, SourceMaster, SourceDetail,
             Target, Size, Count, Seconds, Comments, Timestamp))


def populate_new_location():
    """ Copy old location to new location """
    loc_cursor.execute("SELECT * FROM Location")  # use old loc_cursor
    rows = loc_cursor.fetchall()  # old loc_cursor
    for sql_row in rows:
        row = dict(sql_row)
        Code = row['Code']
        Name = row['Name']
        ModifyTime = row['ModifyTime']  # Don't think this is being saved yet
        ImagePath = row['ImagePath']
        MountPoint = row['MountPoint']
        TopDir = row['TopDir']
        HostName = row['HostName']
        HostWakeupCmd = row['HostWakeupCmd']
        HostTestCmd = row['HostTestCmd']
        HostTestRepeat = row['HostTestRepeat']
        HostMountCmd = row['HostMountCmd']
        HostTouchCmd = row['HostMountCmd']
        HostTouchMinutes = row['HostTouchMinutes']
        Comments = row['Comments']
        sql = "INSERT INTO Location (Code, Name, ModifyTime, ImagePath, \
               MountPoint, TopDir, HostName, HostWakeupCmd, HostTestCmd, \
               HostTestRepeat, HostMountCmd, HostTouchCmd, HostTouchMinutes, \
               Comments) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        new_loc_cursor.execute(
            sql,
            (Code, Name, ModifyTime, ImagePath, MountPoint, TopDir,
             HostName, HostWakeupCmd, HostTestCmd, HostTestRepeat, HostMountCmd,
             HostTouchCmd, HostTouchMinutes, Comments))


def open_new_db():
    """ Open SQL Tables - New Database create from existing database """
    global new_con, new_cursor, new_hist_cursor, new_loc_cursor

    new_con = sqlite3.connect(FNAME_LIBRARY_NEW)

    ''' 
    JULY 13, 2023
        Adding  DiscNumber, CreationTime, Composer, Comment, Hyperlink (all TEXT)
                LastPlayTime (FLOAT)

        Change  OsModificationTime      -> OsModifyTime
                OsCreationTime          -> OsChangeTime
                MetaSongName            -> Title  (CHANGE FIELD ORDER TOO)
                MetaArtistName          -> Artist
                MetaAlbumName           -> Album
                UnsynchronizedLyrics    -> LyricsScore
                ReleaseDate (FLOAT)     -> TEXT
                OriginalDate (FLOAT)    -> RecordingDate (TEXT)

    JULY 18, 2023

        Adding: Compilation ("0" or "1"), GaplessPlayback, AlbumArtist,
                ffMajor, ffMinor, ffCompatible
        
        Change  ReleaseDate             -> FirstDate
                RecordingDate           -> AlbumDate
                Seconds (INT)           -> Seconds (FLOAT)

        Change order of columns too more natural flow
        
        KID3 only has one "DATE" metadata field that only allows YYYY-MM entry.
            Title, Artist, Album, Comment, Date, Track Number, Genre,
            Compilation, Composer(but blank, manually add), Disc Number, 
            Picture, Gapless Playback

        ITUNES uses CREATION_TIME field name in YYYY-MM-DD HH:MM:SS format.
            Creation Time, Title, Artist, Composer, Album, Genre, Track
            Disc, Date, Compilation, Gapless Playback

        Review - mserve FileControl() where metadata is read
               - sql.update_metadata()
               - encoding.py
               - musicbrainzngs

        Consider storing extra FFMPEG Metadata:
            major_brand     : M4A 
            minor_version   : 0
            compatible_brands: M4A mp42i som

    '''
    ''' ID3 TAGS https://exiftool.org/TagNames/ID3.html '''
    new_con.execute("create table IF NOT EXISTS Music(Id INTEGER PRIMARY KEY, " +
                    "OsFileName TEXT, OsAccessTime FLOAT, OsModifyTime FLOAT, " +
                    "OsChangeTime FLOAT, OsFileSize INT, " +
                    "ffMajor TEXT, ffMinor TEXT, ffCompatible TEXT, " +
                    "Title TEXT, Artist TEXT, Album TEXT, Compilation TEXT, " +
                    "AlbumArtist TEXT, AlbumDate TEXT, FirstDate TEXT, " +
                    "CreationTime TEXT, DiscNumber TEXT, TrackNumber TEXT, " +
                    "Rating TEXT, Genre TEXT, Composer TEXT, Comment TEXT, " +
                    "Hyperlink TEXT, Duration TEXT, Seconds FLOAT, " +
                    "GaplessPlayback TEXT, PlayCount INT, LastPlayTime FLOAT, " +
                    "LyricsScore BLOB, LyricsTimeIndex TEXT)")

    new_con.execute("CREATE UNIQUE INDEX IF NOT EXISTS OsFileNameIndex ON " +
                    "Music(OsFileName)")

    new_con.execute("create table IF NOT EXISTS History(Id INTEGER PRIMARY KEY, " +
                    "Time FLOAT, MusicId INTEGER, User TEXT, Type TEXT, " +
                    "Action TEXT, SourceMaster TEXT, SourceDetail TEXT, " +
                    "Target TEXT, Size INT, Count INT, Seconds FLOAT, " +
                    "Comments TEXT, Timestamp FLOAT)")

    new_con.execute("CREATE INDEX IF NOT EXISTS MusicIdIndex ON " +
                    "History(MusicId)")
    new_con.execute("CREATE INDEX IF NOT EXISTS TimeIndex ON " +
                    "History(Timestamp)")
    new_con.execute("CREATE INDEX IF NOT EXISTS TypeActionIndex ON " +
                    "History(Type, Action)")

    # LOCATION TABLE
    new_con.execute("CREATE TABLE IF NOT EXISTS Location(Id INTEGER PRIMARY KEY, " +
                    "Code TEXT, Name TEXT, ModifyTime FLOAT, ImagePath TEXT, " +
                    "MountPoint TEXT, TopDir TEXT, HostName TEXT, " +
                    "HostWakeupCmd TEXT, HostTestCmd TEXT, HostTestRepeat INT, " +
                    "HostMountCmd TEXT, HostTouchCmd TEXT, HostTouchMinutes INT, " +
                    "Comments TEXT)")
    new_con.execute("CREATE UNIQUE INDEX IF NOT EXISTS LocationCodeIndex ON " +
                    "Location(Code)")


    ''' For mserve.py rename_file() function to rename "the" to "The" '''
    new_con.execute("PRAGMA case_sensitive_like = ON;")

    new_con.row_factory = sqlite3.Row
    new_cursor = new_con.cursor()
    new_hist_cursor = new_con.cursor()
    new_loc_cursor = new_con.cursor()


def close_db():
    """ Close 'library.db'. """
    con.commit()
    cursor.close()          # Aug 08/21 Fix "OperationalError:"
    hist_cursor.close()     # See: https://stackoverflow.com/a/53182224/6929343
    loc_cursor.close()
    con.close()
    # close_new_db()  # Old conversion can't use anymore


def close_new_db():
    """ The 'library_new.db' is only used during conversion. """
    new_con.commit()
    new_cursor.close()          # Aug 08/21 Fix "OperationalError:"
    new_hist_cursor.close()     # See: https://stackoverflow.com/a/53182224/6929343
    new_loc_cursor.close()
    new_con.close()


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
        :param key: E.G. "Faith No More/This is it_/17 Last Cup Of Sorrow.m4a"
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
        """ Music Location Library Tree has <No Artist>/<No Album> """
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
        """ Override found for <No Artist>/<No Album> """
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
        """ Add substitute song for <No Artist>/<No Album> """
        try:
            ndx = self.blacks.index(black_key)
            self.whites[ndx] = white_key  # Overwrite 'None' with substitute song
        except ValueError:
            print("sql.py SetWhitelist(black_key, white_key) invalid black_key:",
                  black_key)
            return None


''' Global substitution for read Music Table by path '''
ofb = OsFileNameBlacklist()


def update_lyrics(key, lyrics, time_index):
    """
        Apply Unsynchronized Lyrics and Lyrics Time Index.
        Should only be called when lyrics or time_index has changed.

        NOTE: May 21, 2023 - This is where lyrics - init, lyrics - edit,
        time - init and time - edit could be placed.
    """

    sql = "UPDATE Music SET LyricsScore=?, LyricsTimeIndex=? \
           WHERE OsFileName = ?" 

    if time_index is not None:
        # count = len(time_index)  # Not used
        time_index = json.dumps(time_index)
        # print('Saving', count, 'lines of time_index:', time_index)

    cursor.execute(sql, (lyrics, time_index, key))
    con.commit()


def get_lyrics(key):
    """
        Get Lyrics Score and Lyrics Time Index
    """
    """ June 3, 2023 - May get whitelisted version """
    d = ofb.Select(key)
    if d is None:
        return None, None
    if d["LyricsTimeIndex"] is not None:
        return d["LyricsScore"], json.loads(d["LyricsTimeIndex"])
    else:
        return d["LyricsScore"], None


def increment_last_play(full_path, a_time=None):
    """ Increment Play Count and update current time to Last Play Time
        using full filename path """
    # pycharm doesn't like PRUNED_DIR type 'None', expected 'Sized'
    # noinspection PyTypeChecker
    key = full_path[len(PRUNED_DIR):]  # Create OsFileName (base path)
    d = ofb.Select(key)
    if d is None:
        print("sql.py increment_last_play() key not found:", key)
        return False
    if d['PlayCount']:
        count = d['PlayCount'] + 1
    else:
        count = 1
    if a_time is None:
        a_time = time.time()
    update_last_play(key, count, a_time)
    return True


def update_last_play(key, play_count, last_play_time):
    """ Update Play Count and Last Play Time using OsFileName """
    sql = "UPDATE Music SET PlayCount=?, LastPlayTime=? WHERE OsFileName = ?"
    cursor.execute(sql, (play_count, last_play_time, key))
    con.commit()


def get_last_play(key):
    """ Get Play Count and Last Play Time with OsFileName """
    d = ofb.Select(key)
    if d is None:
        print("sql.py get_last_play() key not found:", key)
        return None, None
    else:
        # If never used, will be None
        return d["PlayCount"], d["LastPlayTime"]


def music_get_row(key):
    """ Get Music Table row using Music Id """
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


def loc_code():
    """ Simple function to return current location code for recording
        in d['SourceDetail'] SQL History Table column."""
    if LODICT:  # Temporary for conversion away from LODICT
        code = LODICT['iid']
    else:
        code = lcs.open_code
    return code


def loc_name():
    """ Aug 18/23 - created for database Version 2 to Version 3 update
        Simple function to return current location name for recording
        in d['SourceMaster'] SQL History Table column."""
    if LODICT:  # Temporary for conversion away from LODICT
        name = LODICT['name']
    else:
        name = lcs.open_name
    return name


def asc_time(Time=None):
    """ Return Time in "Tue Jun  4 22:58:44 2013" format for recording
        in d['SourceDetail'] SQL History Table column."""
    if not Time:
        Time = time.time()
    return time.asctime(time.localtime(Time))


update_print_count = 11  # Change to 0 to print first 10 songs


def update_metadata(fc, commit=True):
    """ Update SQL Music Table Row with metadata tags.
        Also update FileControl() (fc) with mserve unique metadata
        Called from mserve.py and encoding.py

        Check if metadata has changed. If no changes return False.
        Same song file name may exist in two locations where one
        location has more metadata than the other. Also the metadata
        may be different for example, Artist name. E.G.
        "Tom Cochran & Red Rider" in one location and "Red Rider" 
        in the other location.

        Update metadata in library and insert history record:
            'meta' 'init' for first time
            'meta' 'edit' for 2nd and subsequent changes

        Problem when one location has less metadata for song than another
        will be blanking out other location's extra metadata

    :param fc: File control block: mus_ctl, ltp_ctl and play_ctl.
    :param commit: Live run. Update SQL database if metadata changed. If
        not a live run, return changed row dictionary instead of False. 
    :returns: True if Metadata changed and SQL updated """

    # Don't allow GIGO which required FixData del_music_ids() function June 2023
    if fc.Artist is None or fc.Album is None or fc.Title is None:
        return False
    elif fc.Artist == NO_ARTIST_STR or fc.Album == NO_ARTIST_STR:
        return False  # <No Artist> placeholder skipped
    elif fc.Artist == NO_ALBUM_STR or fc.Album == NO_ALBUM_STR:
        return False  # <No Album> placeholder skipped

    # pycharm doesn't like PRUNED_DIR type 'None', expected 'Sized'
    # noinspection PyTypeChecker
    key = fc.path[len(PRUNED_DIR):]  # Create OsFileName (base path)
    d = ofb.Select(key)
    if d is None:
        # File and Directory names with ":", "?", "/", etc. replaced with "_"
        fudged_Artist = ext.legalize_dir_name(fc.Artist)
        fudged_Album = ext.legalize_dir_name(fc.Album)
        fudged_Title = key.split(os.sep)[-1]  # Expand "Title" to "99 Title.ext"
        fudged_Title = ext.legalize_song_name(fudged_Title)
        white_key = fudged_Artist + os.sep + fudged_Album + os.sep + fudged_Title

        e = ofb.Select(white_key)  # If white key works, use it in Whitelist
        if e is not None:
            print("Found substitute key\n\t:", e['OsFileName'])
            print("SQL substitute Music Id:", e['Id'])
            ofb.SetWhitelist(key, white_key)
            key = white_key  # Use white_key instead of passed key
            d = e  # Replace d (None) with e (good dictionary of valid SQL)
        else:
            print('sql.py update_metadata() error no music ID for:', key)
            return False

    ''' Update FileControl() (fc) with mserve unique metadata '''
    fc.Rating = d['Rating']  # Future Use
    fc.Hyperlink = d['Hyperlink']  # Future Use
    fc.PlayCount = d['PlayCount']  # How many times 80% + was played
    fc.LastPlayTime = d['LastPlayTime']  # Time last played (float)

    ''' Adding a new 'init' or 'edit' history record? '''
    if d['Artist'] is None:
        action = 'init'  # music file has never been played in mserve
    elif \
        fc.ffMajor         != d['ffMajor'] or \
        fc.ffMinor         != d['ffMinor'] or \
        fc.ffCompatible    != d['ffCompatible'] or \
        fc.Title           != d['Title'] or \
        fc.Artist          != d['Artist'] or \
        fc.Album           != d['Album'] or \
        fc.Compilation     != d['Compilation'] or \
        fc.AlbumArtist     != d['AlbumArtist'] or \
        fc.AlbumDate       != d['AlbumDate'] or \
        fc.FirstDate       != d['FirstDate'] or \
        fc.DiscNumber      != d['DiscNumber'] or \
        fc.TrackNumber     != d['TrackNumber'] or \
        fc.Genre           != d['Genre'] or \
        fc.Composer        != d['Composer'] or \
        fc.Comment         != d['Comment'] or \
        fc.Duration        != d['Duration'] or \
        fc.DurationSecs    != d['Seconds'] or \
            fc.GaplessPlayback != d['GaplessPlayback']:
        action = 'edit'
    else:
        return False  # Metadata same as library

    # For debugging, set update_print_count to 0. Otherwise set initial value to 10
    global update_print_count
    if update_print_count < 10:
        print('\nSQL updating metadata for:', key)
        # July 18, 2023 - There are more fields to add but info.cast instead?    
        print('fc.Artist type :', type(fc.Artist),
              '  | fc.Album type :', type(fc.Album),
              '  | fc.Title type :', type(fc.Title),
              '  | fc.TrackNumber type :', type(fc.TrackNumber))
        print('SQL type    :', type(d['Artist']), '  | Album type :',
              type(d['Album']), '  | fc.Title type :', type(d['Title']),
              '  | TrackNumber type :', type(d['TrackNumber']))
        print(fc.ffMajor, '  | ', d['ffMajor'])
        print(fc.ffMinor, '  | ', d['ffMinor'])
        print(fc.ffCompatible, '  | ', d['ffCompatible'])
        print(fc.Title, '  | ', d['Title'])
        print(fc.Artist, '  | ', d['Artist'])
        print(fc.Album, '  | ', d['Album'])
        print(fc.Compilation, '  | ', d['Compilation'])
        print(fc.AlbumArtist, '  | ', d['AlbumArtist'])
        print(fc.AlbumDate, '  | ', d['AlbumDate'])
        print(fc.FirstDate, '  | ', d['FirstDate'])
        print(fc.DiscNumber, '  | ', d['DiscNumber'])
        print(fc.TrackNumber, '  | ', d['TrackNumber'])
        print(fc.Genre, '  | ', d['Genre'])
        print(fc.Composer, '  | ', d['Composer'])
        print(fc.Comment, '  | ', d['Comment'])
        print(fc.Duration, '  | ', d['Duration'])
        print(fc.DurationSecs, '  | ', d['Seconds'])
        print(fc.GaplessPlayback, '  | ', d['GaplessPlayback'])

        if fc.ffMajor != d['ffMajor']:
            print('fc.ffMajor:', fc.ffMajor, '  | ', d['ffMajor'])
        elif fc.ffMinor != d['ffMinor']:
            print('fc.ffMinor:', fc.ffMinor, '  | ', d['ffMinor'])
        elif fc.ffCompatible != d['ffCompatible']:
            print('fc.ffCompatible:', fc.ffCompatible, '  | ', d['ffCompatible'])
        elif fc.Title != d['Title']:
            print('fc.Title:', fc.Title, '  | ', d['Title'])
        elif fc.Artist != d['Artist']:
            print('fc.Artist:', fc.Artist, '  | ', d['Artist'])
        elif fc.Album != d['Album']:
            print('fc.Album:', fc.Album, '  | ', d['Album'])
        elif fc.Compilation != d['Compilation']:
            print('fc.Compilation:', fc.Compilation, '  | ', d['Compilation'])
        elif fc.AlbumArtist != d['AlbumArtist']:
            print('fc.AlbumArtist:', fc.AlbumArtist, '  | ', d['AlbumArtist'])
        elif fc.AlbumDate != d['AlbumDate']:
            print('fc.AlbumDate:', fc.AlbumDate, '  | ', d['AlbumDate'])
        elif fc.FirstDate != d['FirstDate']:
            print('fc.FirstDate:', fc.FirstDate, '  | ', d['FirstDate'])
        elif str(fc.DiscNumber) != str(d['DiscNumber']):
            print('fc.DiscNumber:', fc.DiscNumber, '  | ', d['DiscNumber'])
        elif str(fc.TrackNumber)  != str(d['TrackNumber']):
            print('fc.TrackNumber:', fc.TrackNumber, '  | ', d['TrackNumber'])
        elif fc.Genre != d['Genre']:
            print('fc.Genre:', fc.Genre, '  | ', d['Genre'])
        elif fc.Composer != d['Composer']:
            print('fc.Composer:', fc.Composer, '  | ', d['Composer'])
        elif fc.Comment != d['Comment']:
            print('fc.Comment:', fc.Comment, '  | ', d['Comment'])
        elif fc.Duration != d['Duration']:
            print('fc.Duration:', fc.Duration, '  | ', d['Duration'])
        elif fc.DurationSecs != d['Seconds']:
            print('fc.DurationSecs:', fc.DurationSecs, '  | ', d['Seconds'])
        elif fc.GaplessPlayback != d['GaplessPlayback']:
            print('fc.GaplessPlayback:', fc.GaplessPlayback, 
                  '  | ', d['GaplessPlayback'])
        else:
            print('  | EQUAL - Need fix for sql.update_metadata2()')
        update_print_count += 1

    if not commit:
        return True  # Not updating but report back Metadata is different

    # Update metadata for music file into SQL Music Table
    sql = "UPDATE Music SET ffMajor=?, ffMinor=?, ffCompatible=?, \
           Title=?, Artist=?, Album=?, Compilation=?, \
           AlbumArtist=?, AlbumDate=?, FirstDate=?, DiscNumber=?, \
           TrackNumber=?, Genre=?, Composer=?, Comment=?, Duration=?, \
           Seconds=?, GaplessPlayback=? WHERE OsFileName=?"
    cursor.execute(
        sql, (fc.ffMajor, fc.ffMinor, fc.ffCompatible,
              fc.Title, fc.Artist, fc.Album, fc.Compilation,
              fc.AlbumArtist, fc.AlbumDate, fc.FirstDate, fc.DiscNumber,
              fc.TrackNumber, fc.Genre, fc.Composer, fc.Comment, fc.Duration,
              fc.DurationSecs, fc.GaplessPlayback, key))
    con.commit()

    # Add history record
    # Time will be file's last modification time
    ''' Build full music file path '''
    full_path = START_DIR.encode("utf8") + key
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
    #SourceMaster = lcs.open_name
    #SourceMaster = LODICT['name']
    #SourceDetail = time.asctime(time.localtime(Time))
    #Comments = "Found: " + time.asctime(time.localtime(time.time()))
    Comments = "Found: " + asc_time()
    if fc.DurationSecs is not None:
        FloatSeconds = float(str(fc.DurationSecs))  # Convert from integer
    else:
        FloatSeconds = 0.0

    Count = 0

    # If adding, the file history record may be missing too.
    if action == 'init' and \
       not hist_check(d['Id'], 'file', action):
        ''' Add file-init history if it doesn't exist already '''
        hist_add(Time, d['Id'], g.USER, 'file', action, loc_name(),
                 asc_time(Time), key, Size, Count, FloatSeconds,
                 Comments)
        #hist_add(Time, d['Id'], g.USER, 'file', action, SourceMaster,
        #         SourceDetail, key, Size, Count, FloatSeconds,
        #         Comments)  # Aug 3/23 conversion

    # Add the meta Found or changed record
    hist_add(Time, d['Id'], g.USER, 'meta', action, loc_name(),
             asc_time(Time), key, Size, Count, FloatSeconds,
             Comments)
    #hist_add(Time, d['Id'], g.USER, 'meta', action, SourceMaster,
    #         SourceDetail, key, Size, Count, FloatSeconds,
    #         Comments)  # Aug 3/23 conversion

    con.commit()

    return True  # Metadata was updated in SQL database


def music_id_for_song(key):
    """ Get Music Table Row using OsFileName """
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
    """ Get History Table row using Id """
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
    hist_add(time.time(), d['Id'], g.USER, 'time', Action, d['SourceMaster'],
             d['SourceDetail'], key, d['Size'], d['Count'], d['Seconds'], 
             Comments)

    return True


def hist_add_shuffle(Action, SourceMaster, SourceDetail):
    """  Does nothing, FUTURE USE
    Record action of shuffling playlist. """
    Type = "playlist"
    # Action = 'shuffle'
    if Type == Action == SourceMaster == SourceDetail:
        return  # Above test for pycharm checking  


def hist_add_music_var(MusicId, Type, Action, Time=None, User=None,
                       SourceMaster="", SourceDetail="", Target="",
                       Size=0, Count=0, Seconds=0.0, Comments=""):
    """ One variable per Type / Action can be stored per song.
        For example, Type="Volume", Action="Analyze"

        History variables:

            Time, MusicId, User, Type, Action, SourceMaster, SourceDetail,
            Target, Size, Count, Seconds, Comments

    """
    Time = time.time() if Time is None else Time
    User = g.USER if User is None else User
    d = hist_get_music_var(MusicId, Type, Action)
    if d:
        # Update existing row with new values
        now = time.time()
        cmd = "UPDATE History SET Time=?, SourceMaster=?, SourceDetail=?, \
            Target=?, Size=?, Count=?, Seconds=?, Comments=?, Timestamp=? \
            WHERE Id = ?"
        hist_cursor.execute(cmd, (now, SourceMaster, SourceDetail, Target,
                                  Size, Count, Seconds, Comments, now,
                                  d['Id']))
        con.commit()

    else:
        # Add new row with values
        hist_add(Time, MusicId, User, Type, Action, SourceMaster, SourceDetail,
                 Target, Size, Count, Seconds, Comments)


def hist_get_music_var(MusicId, Type, Action, SourceMaster=None):
    """  One variable per Type / Action / SourceMaster can be stored per song.
         For example, Type="Volume", Action="Analyze", SourceMaster="L004".

    """
    if hist_check(MusicId, Type, Action, check_master=SourceMaster):
        return hist_get_row(HISTORY_ID)
    return None


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

    hist = dict()  # History dictionary

    #SourceMaster = lcs.open_name
    #SourceMaster = LODICT['name']
    #hist['SourceMaster'] = SourceMaster  # Aug 3/23 - conversion
    hist['SourceMaster'] = loc_name()

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

    #SourceDetail = time.asctime(time.localtime(Time))
    #hist['SourceDetail'] = SourceDetail
    hist['SourceDetail'] = asc_time(Time)
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
    hist_add(time.time(), d['Id'], g.USER, 'time', 'remove', d['SourceMaster'],
             d['SourceDetail'], key, d['Size'], d['Count'], d['Seconds'], 
             Comments)

    return True


def hist_init_lost_and_found():
    """ Tool to initialize history time for all songs in database.
        This step just records 'file' and 'init' for OS song filename.
        If metadata present then 'meta' and 'init' also recorded.

        The time for 'init' is the files modification time (OsModifyTime)

        The same song can be found in multiple locations and smaller devices
            might have fewer songs that the master location.

        PROBLEM: Music Table Rows as soon as directory is opened, however
            a new location may not be saved and may never be accessed again.
            populate_tables should only be called when 'new' location is saved.
            Need function to prompt for location name, assign new code and
            then call sql.populate_tables()

    """

    song_count = 0
    add_count = 0
    add_meta_count = 0
    # History Table columns
    User = g.USER           # From location.py
    Type = 'file'           # This records OS filename into history
    Action = 'init'         # Means we "found" the file or it was renamed
    #SourceMaster = lcs.open_name
    #SourceMaster = LODICT['name']
    Comments = 'Automatically added by hist_init_lost_and_found()'

    ''' Read through all SQL Music Table Rows '''
    for row in cursor.execute('SELECT Id, OsFileName, OsModifyTime, ' +
                              'Title, Seconds FROM Music'):
        song_count += 1
        # Check if history already exists for song
        MusicId = row[0]
        if hist_check(MusicId, Type, Action):
            continue  # 'file'-'init' record already exists

        # Name our Music Table columns needed for History Table
        OsFileName = row[1] 
        Title = row[2]       # If name not blank, we have metadata
        Seconds = row[3]            # Song Duration in seconds (INT)

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
        #SourceDetail = time.asctime(time.localtime(Time))
        if Seconds is not None:
            FloatSeconds = float(str(Seconds))  # Convert from integer
        else:
            FloatSeconds = 0.0

        Count = 0
        Target = OsFileName

        # Add the Song Found row
        # Aug 8/21 use time.time() instead of job start time.
        hist_add(time.time(), MusicId, User, Type, Action, loc_name(), 
                 asc_time(Time), Target, Size, Count, FloatSeconds, Comments)
        #hist_add(time.time(), MusicId, User, Type, Action, SourceMaster, SourceDetail, 
        #         Target, Size, Count, FloatSeconds, Comments)  # Aug 3/23 - conversion
        add_count += 1

        if Title is not None:
            # Add the Metadata Found row
            hist_add(time.time(), MusicId, User, 'meta', Action, loc_name(),
                     asc_time(Time), OsFileName, Size, Count, FloatSeconds,
                     Comments)
            #hist_add(time.time(), MusicId, User, 'meta', Action, SourceMaster,
            #         SourceDetail, OsFileName, Size, Count, FloatSeconds, 
            #         Comments)  # Aug 3/23 - conversion
            add_meta_count += 1

    #print('Songs on disk:', song_count, 'Added count:', add_count, \
    #      'Added meta count:', add_meta_count)

    con.commit()                                # Save database changes


HISTORY_ID = None


def hist_check(MusicId, check_type, check_action, check_master=None):
    """ SQL History Table multi-purpose:

        VARIABLE        DESCRIPTION
        --------------  -----------------------------------------------------
        Id              Primary Key integer key auto-incremented
        Time            In system format with nano-second precision
                        filetime = (unix time * 10000000) + 116444736000000000
                        Secondary Key
        MusicId         Link to primary key in Music Table usually rowid
                        For setting (screen, monitor, window, etc) the
                        MusicId is set to 0. History's Tertiary Key
        User            User name, User ID or GUID varies by platform.
        Type            'file', 'catalog', 'link', 'index', 'checkout', 'song',
                        'lyrics', 'time', 'fine-tune', 'meta', 'resume', 
                        'scrape', 'volume', 'window', 'chron-state', 'hockey'
        Action          'copy', 'download', 'remove', 'burn', 'edit', 'play',
                        'parm', 'init', 'shuffle', 'save', 'load', 'level',
                        'scrape', 'show', 'hide', 'On', 'Off'

        NOTE: Type-Action is History's Quaternary key.
              Type-Action can be: 'scrape'-'parm' and 'lyrics'-'scrape'

                        EXAMPLES USING LYRICS WEBSCRAPING
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

    for row in hist_cursor.execute(
            "SELECT Id, Type, Action, SourceMaster FROM History " +
            "INDEXED BY MusicIdIndex WHERE MusicId = ?", [MusicId]):
        Id = row[0]
        Type = row[1]
        Action = row[2]
        SourceMaster = row[3]
        if Type == check_type and Action == check_action:
            # SourceMaster check is optional
            if not check_master or check_master == SourceMaster:
                HISTORY_ID = Id
                return True

    HISTORY_ID = 0
    return False                # Not Found


# ===========================  USER CONFIGURATION  ============================
class Config:
    """ User Configuration - Treeview, Scrollbox, Font, Color, Width, etc. """

    # Treeview background colors
    # background="LemonChiffon"    VERY NICE
    # background="NavajoWhite"     VERY NICE
    # background="OliveDrab"       TOO DARK for black text
    # background="PaleTurquoise"   OK but highlight bar not as strong
    # background="LightGoldenrod"  Similar to Lemon Chiffon (Very Nice)
    # background="RosyBrown"       NOT BAD but a little dark at night
    # background="AliceBlue"       BEST at day
    # background="LightSalmon"     BEST at night
    # background="WhiteSmoke"      BEST all around

    def __init__(self):
        """
        SQL History records for configuration.

        Type:           'cfg_lib_top' / 'cfg_play_top' / 'cfg_sql_music', etc.
        Action:         'toplevel' / 'treeview' / 'sql_treeview', etc.
        SourceMaster:   'style' / 'columns' /
        SourceDetail:   'color' / 'height & colors'
        Target:         [{}, {}, ... {}]  fields / columns / colors / fonts / buttons
        Comments:       "Version: 1.0 | Updated: yyyy-mm-dd hh:hh"

        """

        # Defaults Dictionary is used when no SQL override record exists.
        #   Key is tuple of "Action", "Type", "SourceMaster", "Source Detail"
        #   Value is another dictionary with key/value pairs
        self.defaults = {

            # mserve Music Library taskbar icon  # KEY is a tuple of 4 strings
            # Music Library AKA Library Tree AKA lib_top AKA lib_tree
            ('cfg_lib_top', 'toplevel', 'taskbar_icon', 'height & colors'):
                {"height": 64, "outline": 'White', "fill": 'LightSkyBlue',
                 "text": 'Black', "font_family": 'DejaVuSans.ttf',
                 "char": 'm'},  # VALUE dictionary or list
            ('cfg_lib_top', 'treeview', 'style', 'color'):
                {"name": 'mserve.Treeview', "foreground": "Black",
                 "background": "WhiteSmoke", "fieldbackground": "WhiteSmoke",
                 "edge_color": None, "edge_px": 0},

            # Playlist taskbar icon  # KEY is a tuple of 4 strings
            ('cfg_play_top', 'toplevel', 'taskbar_icon', 'height & colors'): 
                {"height": 64, "outline": 'Black', "fill": 'ForestGreen',
                 "text": 'White', "font_family": 'DejaVuSans.ttf',
                 "char": 'P'},  # VALUE dictionary or list
            # chron.Treeview frame is always the same height with no edge
            ('cfg_play_top', 'treeview', 'style', 'color'):
                {"name": 'chron.Treeview', "foreground": "Gold",
                 "background": "Black", "fieldbackground": "Black",
                 "font_size": g.MON_FONTSIZE,
                 "edge_color": "White", "edge_px": 0},
            # self.chron_tree.tag_configure('chron_sel', background=t['background'],
            #                               foreground=t['foreground'])
            ('cfg_play_top', 'treeview', 'style', 'chron_sel'):
                {"foreground": "White", "background": "ForestGreen"},
            ('cfg_play_top', 'treeview', 'style', 'highlight'):
                {"foreground": "Black", "background": "LightSkyBlue"},
            ('cfg_play_top', 'treeview', 'style', 'highlight_sel'):
                {"foreground": "Black", "background": "Gold"},

            # Locations Maintenance taskbar icon and treeview colors
            ('cfg_locations', 'toplevel', 'taskbar_icon', 'config'):
                {"height": 64, "outline": 'White', "fill": 'AliceBlue',
                 "text": 'Black', "font_family": 'DejaVuSans.ttf',
                 "char": 'lo'},  # VALUE dictionary or list
            # View SQL Music Table treeview displaycolumns (in order of appearance)
            # Must be sql_treeview for toolkit.py DictTreeview().__init__
            ('cfg_locations', 'sql_treeview', 'column', 'order'):
                ["detail", "comments", "count", "size", "seconds"],
            ('cfg_locations', 'sql_treeview', 'style', 'color'):
                {"name": 'location.Treeview', "foreground": "Black",
                 "background": "AliceBlue", "fieldbackground": "AliceBlue",
                 "edge_color": "White", "edge_px": 5},
            ('cfg_locations', 'sql_treeview', 'style', 'scroll'):
                {"name": 'location.Treeview', "width": 14},
            # 2024-04-07 Older "treeview" Action key replaced by "sql_treeview" key
            #('cfg_locations', 'treeview', 'style', 'color'):
            #    {"name": 'location.Treeview', "foreground": "Black",
            #     "background": "AliceBlue", "fieldbackground": "AliceBlue",
            #     "edge_color": "White", "edge_px": 5},
            ('cfg_locations', 'frame', 'style', 'color'):
                {"background": "WhiteSmoke"},
            # Location image border (use edge_px=0 to turn off border)
            # NOTE: Using tk.Label highlight and not tk.Label border
            ('cfg_locations', 'loc_image', 'style', 'color'):
                {"edge_color": "White", "edge_px": 3},

            # Compare Locations (Synchronize) taskbar icon and treeview colors
            ('cfg_locations', 'cmp_toplevel', 'taskbar_icon', 'config'):
                {"height": 64, "outline": 'White', "fill": 'NavajoWhite',
                 "text": 'Black', "font_family": 'DejaVuSans.ttf',
                 "char": 'C'},
            ('cfg_locations', 'cmp_treeview', 'style', 'color'):
                {"name": 'compare.Treeview', "foreground": "Black",
                 "background": "NavajoWhite", "fieldbackground": "NavajoWhite",
                 "edge_color": "White", "edge_px": 5},
            ('cfg_locations', 'cmp_treeview', 'style', 'scroll'):
                {"name": 'compare.Treeview', "width": 14},

            # Analyze Maximum Volume taskbar icon and treeview colors
            # Also Analyze 'loudnorm' Filter taskbar icon and treeview colors
            ('cfg_locations', 'avo_toplevel', 'taskbar_icon', 'config'):
                {"height": 64, "outline": 'White', "fill": 'NavajoWhite',
                 "text": 'Black', "font_family": 'DejaVuSans.ttf',
                 "char": 'A'},
            ('cfg_locations', 'avo_treeview', 'style', 'color'):
                {"name": 'analyze.Treeview', "foreground": "Black",
                 "background": "NavajoWhite", "fieldbackground": "NavajoWhite",
                 "edge_color": "White", "edge_px": 5},
            ('cfg_locations', 'avo_treeview', 'style', 'scroll'):
                {"name": 'analyze.Treeview', "width": 14},

            # Playlists Maintenance taskbar icon and treeview colors
            ('cfg_playlists', 'toplevel', 'taskbar_icon', 'height & colors'):
                {"height": 64, "outline": 'White', "fill": 'LemonChiffon',
                 "text": 'Black', "font_family": 'DejaVuSans.ttf',
                 "char": 'pl'},  # VALUE dictionary or list
            # View SQL Music Table treeview displaycolumns (in order of appearance)
            # Must be sql_treeview for toolkit.py DictTreeview().__init__
            ('cfg_playlists', 'sql_treeview', 'column', 'order'):
                ["detail", "comments", "count", "size", "seconds"],
            ('cfg_playlists', 'sql_treeview', 'style', 'color'):
                {"name": 'playlists.Treeview', "foreground": "Black",
                 "background": "LemonChiffon", "fieldbackground": "LemonChiffon",
                 "edge_color": "NavajoWhite", "edge_px": 5},
            ('cfg_playlists', 'sql_treeview', 'style', 'scroll'):
                {"name": 'playlists.Treeview', "width": 14},

            # View SQL Music Table taskbar icon
            ('cfg_sql_music', 'toplevel', 'taskbar_icon', 'height & colors'):
                {"height": 64, "outline": 'White', "fill": 'LemonChiffon',
                 "text": 'Black', "font_family": 'DejaVuSans.ttf', "char": 'M'},
            # View SQL Music Table treeview displaycolumns (in order of appearance)
            ('cfg_sql_music', 'sql_treeview', 'column', 'order'):
                ["os_filename", "track_number", "row_id", "os_atime",
                 "os_file_size", "artist", "album", "title", "lyrics", "genre"],
            # NOTE: When column order, width or headings changed they are
            # saved in a new history row:
            # ('cfg_sql_music', 'sql_treeview', 'column', 'custom'):
            #     [["os_filename", 242, "OS Filename"], ["row_id", 80, "Row ID"]...

            # Long term goal to remove 'column'; 'order'/'widths' & replace with:
            # 'cfg_sql_music', 'sql_treeview', 'custom_view', view_name (variable)
            # The view_name will be a full copy of music_treeview with new values

            ('cfg_sql_music', 'sql_treeview', 'style', 'color'):
                {"name": 'sql_music.Treeview', "foreground": "Black",
                 "background": "LemonChiffon", "fieldbackground": "LemonChiffon",
                 # Consider adding heading font, row font, sbar_width, sbar_colors
                 # See cfg_play_top treeview for highlight color, select color
                 "edge_color": "NavajoWhite", "edge_px": 5},
            ('cfg_sql_music', 'sql_treeview', 'style', 'scroll'):
                {"name": 'sql_music.Treeview', "width": 14},

            # View SQL History Table taskbar icon
            ('cfg_sql_history', 'toplevel', 'taskbar_icon', 'height & colors'):
                {"height": 64, "outline": 'White', "fill": 'NavajoWhite',
                 "text": 'Black', "font_family": 'DejaVuSans.ttf',
                 "char": 'H'},
            # View SQL History Table treeview displaycolumns
            ('cfg_sql_history', 'sql_treeview', 'column', 'order'):
                ["time", "row_id", "music_id", "type", "action", "master",
                 "detail", "target", "size", "count", "seconds", "comments"],
            ('cfg_sql_history', 'sql_treeview', 'style', 'color'):
                {"name": 'sql_history.Treeview', "foreground": "Black",
                 "background": "NavajoWhite", "fieldbackground": "NavajoWhite",
                 "edge_color": "LightSalmon", "edge_px": 5},
            ('cfg_sql_history', 'sql_treeview', 'style', 'scroll'):
                {"name": 'sql_history.Treeview', "width": 14},

            # View SQL Location Table taskbar icon
            ('cfg_sql_location', 'toplevel', 'taskbar_icon', 'height & colors'):
                {"height": 64, "outline": 'White', "fill": 'LightSalmon',
                 "text": 'Black', "font_family": 'DejaVuSans.ttf',
                 "char": 'L'},
            # View SQL Location Table treeview displaycolumns
            ('cfg_sql_location', 'sql_treeview', 'column', 'order'):
                ["code", "name", "topdir", "image_path", "host_name", "comments"],
            ('cfg_sql_location', 'sql_treeview', 'style', 'color'):
                {"name": 'sql_location.Treeview', "foreground": "Black",
                 "background": "LightSalmon", "fieldbackground": "LightSalmon",
                 "edge_color": "DarkOrange", "edge_px": 5},
            ('cfg_sql_location', 'sql_treeview', 'style', 'scroll'):
                {"name": 'sql_location.Treeview', "width": 14},

            # Big Number Calculator
            ('cfg_calculator', 'toplevel', 'taskbar_icon', 'height & colors'):
                {"height": 64, "outline": 'Black', "fill": 'LemonChiffon',
                 "text": 'Black', "font_family": 'DejaVuSans.ttf',
                 "char": 'C'},  # VALUE dictionary or list

            ('cfg_end', 'sql_treeview', 'end', 'end'):
                {"nothing": 1, "here": 2}  # To make inserting before end easier
        }
        # All column variables in history row, except primary ID auto assigned.
        # Variables are used to insert new history table row
        self.Time = time.time()
        self.MusicId = 0
        self.User = g.USER
        self.Type = None
        self.Action = None
        self.SourceMaster = None
        self.SourceDetail = None
        self.Target = None
        self.Size = 0
        self.Count = 0
        self.Seconds = 0.0
        self.Comments = None
        self.Timestamp = self.Time

        # window_names is used to get screen coordinates and sizes of windows
        # NOTE: TV volume during commercials always opens in same position and size
        # Type = "window", Action = window_name
        self.window_names = {
            "library": "Music Library Window (Main mserve Window)",
            "playlist": "Music Playing Window",
            "history": "Lyrics Scraping History Window (Future Use)",
            "encoding": "CD Encoding (Ripping) Window",
            "sql_music": "View SQL Music Table Window",
            "sql_history": "View SQL History Table Window",
            "sql_location": "View SQL Locations Table Window",
            "playlists": "Playlists Maintenance Window",
            "locations": "Locations Maintenance Window",
            "calculator": "Big Number Calculator Window",
            "pls_top": "DELETE this SQL record",
            "lcs_top": "DELETE this SQL record",
            "location": "DELETE this SQL record",
            "results": "DELETE this SQL record",
            "unknown": "Bad Window Name in SQL History Table"
        }

    @staticmethod
    def make_key(sql_key):
        """ Return tuple of four parts from converted passed key list """
        tup_key = None  # Just to make pyCharm smile :)
        if isinstance(sql_key, list):
            tup_key = tuple(sql_key)
        elif isinstance(sql_key, tuple):
            tup_key = sql_key
        else:
            print("sql.py - Config.make_key(): sql_key not tuple or list:\n\t")
            print(sql_key)
            toolkit.print_trace()
            exit()
        return tup_key

    def get_sql(self, sql_key, Id=False):
        """ Get SQL row matching key of four strings """
        tup_key = self.make_key(sql_key)
        self.Type, self.Action, self.SourceMaster, self.SourceDetail = tup_key
        hist_cursor.execute("SELECT * FROM History INDEXED BY TypeActionIndex " +
                            "WHERE Type = ? AND Action = ?",
                            (self.Type, self.Action))
        try:
            rows = hist_cursor.fetchall()
            for sql_row in rows:
                row = dict(sql_row)
                if self.SourceMaster == row['SourceMaster'] and \
                        self.SourceDetail == row['SourceDetail']:
                    if not Id:  # Default is to return 'Target' column
                        return json.loads(row['Target'])
                    else:
                        return row['Id']
        except sqlite3.ProgrammingError:
            # No configuration override so return default
            pass
        return []  # Return empty list of rows

    def get_cfg(self, sql_key):
        """ Get SQL Configuration from database or from defaults.

        :param sql_key: can be a list or tuple of four values """
        target = self.get_sql(sql_key)
        if target:  # If not empty list, then found in database

            # sql_key = [self.cfg_name, 'sql_treeview', 'dict_treeview', 'custom']
            '''
                If last 3 variables match then OrderedDict must be rebuild  
            '''
            key = list(sql_key)
            if key[1:4] == ['sql_treeview', 'dict_treeview', 'custom']:
                return self.convert_json_to_ordered(target)
            else:
                return target

        # SQL row doesn't exist in database so return defaults
        tup_key = self.make_key(sql_key)  # Convert list to tuple
        target = self.defaults.get(tup_key, None)

        if target is None:
            print("sql.py - Config.get_cfg(): sql_key NOT FOUND in defaults:\n\t")
            print(sql_key)
            toolkit.print_trace()
            exit()

        return target

    @staticmethod
    def convert_json_to_ordered(unordered_dicts):
        """ json.dumps() doesn't save ordered dicts in order. """
        sample_list = music_treeview()
        sample_dict = sample_list[0]  # ordered key/value pairs
        ordered_dicts = []
        for unordered in unordered_dicts:
            ordered = copy.deepcopy(sample_dict)
            ordered.update(unordered)
            ordered_dicts.append(ordered)
        return ordered_dicts

    def has_disk_cfg(self, sql_key):
        """ Check if Disk configuration exists. The get_cfg() method will
            return a real configuration or defaults.
        """
        target = self.get_sql(sql_key)
        if target:  # If not empty list, then found in database
            return target
        return None

    def insert_update_cfg(self, sql_key, custom_name, target):
        """ Insert or update SQL History Record configuration type row with
            list of column dictionaries placed into 'Target'. """

        self.Target = json.dumps(target)  # list or dict or both
        self.Time = time.time()  # Timestamp

        Id = self.get_sql(sql_key, Id=True)
        if Id:  # If existing Id update that row
            self.Comments = "Update " + custom_name
            sql = "UPDATE History SET Target=?, Comments=?, Timestamp=?" + \
                  " WHERE Id = ?"
            hist_cursor.execute(sql, (self.Target, self.Comments, self.Time, Id))
            con.commit()
            return 2  # Update

        self.Comments = "Create " + custom_name
        sql = "INSERT INTO History (Time, MusicId, User, Type, Action, \
               SourceMaster, SourceDetail, Target, Size, Count, Seconds, \
               Comments, Timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        hist_cursor.execute(
            sql,
            (self.Time, 0, self.User, self.Type, self.Action, self.SourceMaster,
             self.SourceDetail, self.Target, self.Size, self.Count, self.Seconds,
             self.Comments, self.Time))
        con.commit()
        return 1  # Insert

    def print_windows(self, line_dump=False):
        """ History table Window positions and sizes using window_names dictionary
            :returns line_dump: Printable lines with tabs
        """
        lines = []
        rows = None  # Just to make pyCharm smile :)
        if not line_dump:
            print("\nsql.py - print_windows() - SQL History Table's 'Action'='window'\n")
        hist_cursor.execute("SELECT * FROM History INDEXED BY TypeActionIndex " +
                            "WHERE Type = ?", ('window', ))
        try:
            rows = hist_cursor.fetchall()
        except TypeError:  # TypeError: 'NoneType' object is not iterable:
            if line_dump:
                lines.append("sql.py - print_windows(): No window names found !")
                lines.append("Possible names are:")
                lines.append(self.window_names)
            else:
                print("sql.py - print_windows(): No window names found !")
                print("Possible names are:")
                print(self.window_names)
                rows = None
            if line_dump:
                ret = lines  # Return print formatted string list
            else:
                ret = rows  # Return SQL dictionaries

            return ret

        for sql_row in rows:
            row = dict(sql_row)
            Action = row['Action']
            if self.window_names.get(Action, None):
                if line_dump:
                    lines.append("'Action':" + Action + "\tWindow Name:" +
                                 self.window_names[Action])
                    lines.append("\t'SourceMaster':\t" + row['SourceMaster'])
                    lines.append("\t'SourceDetail':\t" + row['SourceDetail'])
                    lines.append("\t'Comments':\t" + row['Comments'])
                else:
                    print("'Action':", Action, "\t Window Name:",
                          self.window_names[Action])
                    print("\t'SourceMaster':\t", row['SourceMaster'])
                    print("\t'SourceDetail':\t", row['SourceDetail'])
                    print("\t'Comments':\t", row['Comments'])
            else:
                if line_dump:
                    lines.append(Action + " is a BAD window name !")
                else:
                    print(Action, "BAD window name !")

        if line_dump:
            ret = lines  # Return print formatted string list
        else:
            ret = rows  # Return SQL dictionaries

        return ret

    def show_fonts(self, _toplevel):
        """ Quick and dirty - Enhance and place on Tools menu.

            1) Consolidate multiple versions of same name.
            2) Prefix with font name in default for ding bats or barcodes.
            3) Scroll wheel only works on scrollbar and not on canvas.
            4) Save geometry under window name "fonts".
            5) Make callable with starting font and return selection.
            6) Add buttons to Close, Search, Select & Help.
            7) Create taskbar icon with 'F' in SQL configuration.
            8) Create canvas colors with SQL Type = "cfg_fonts"

        """
        try:
            import tkinter as tk
            import tkinter.ttk as ttk
            import tkinter.font as font
            import tkinter.filedialog as filedialog
            import tkinter.messagebox as messagebox
            import tkinter.scrolledtext as scrolledtext
        except ImportError:  # Python 2
            import Tkinter as tk
            import ttk
            import tkFont as font
            import tkFileDialog as filedialog
            import tkMessageBox as messagebox
            import ScrolledText as scrolledtext

        if True is True:
            return  # Easy way out

        """ https://stackoverflow.com/a/53717785/6929343

        :return:
        """
        sql_key = ('cfg_fonts', 'toplevel', 'taskbar_icon', 'height & colors')
        sql_key = self.make_key(sql_key)
        print("TODO define sql.py Config.show_fonts() sql_key:\n", sql_key)
        toplevel = tk.Toplevel()
        toplevel.title('Font Families - mserve')
        fonts = list(font.families())
        fonts.sort()

        def onFrameConfigure(obj):
            """Reset the scroll region to encompass the inner frame"""
            obj.configure(scrollregion=obj.bbox("all"))

        can_top = tk.Canvas(toplevel, borderwidth=0, background="#ffffff")
        frame = tk.Frame(can_top, background="#ffffff")
        vsb = tk.Scrollbar(toplevel, orient="vertical", command=can_top.yview)
        can_top.configure(yscrollcommand=vsb.set)

        vsb.pack(side="right", fill="y")
        can_top.pack(side="left", fill="both", expand=True)
        can_top.create_window((4, 4), window=frame, anchor="nw")

        frame.bind("<Configure>", 
                   lambda event, lam_top=can_top: onFrameConfigure(lam_top))

        """ Put in the fonts """
        list_number = 1
        for item in fonts:
            _label = "list_label" + str(list_number)
            _label = tk.Label(frame, text=item, font=(item, 16)).pack()
            list_number += 1


# ==========================  SYSTEM CONFIGURATION  ===========================
def get_config(Type, Action):
    # noinspection SpellCheckingInspection
    """ Get system configuration recorded in SQL history table in the
        'Type' + 'Action' columns. Not to be confused with user configurations
        kept in sql.Config() class above.

        VARIABLE        DESCRIPTION
        --------------  -----------------------------------------------------
        Type - Action   'window' - library, playlist(Music Playing), history,
                        encoding, sql_music, sql_history, sql_location,
                        playlists(maintenance),
                        locations(maintenance), calculator, results(DELETE)
                        See: monitory.py - get_window_geom(name)
        Type - Action   'resume' - L999 or P999999. SourceMaster = Playing/Paused
                        'chron_state' - L999 or P999999. SourceMaster = hide/show
                        'hockey_state' - L999 or P999999. SourceMaster = On/Off
                        'make_lrc' - L999 or P999999. FUTURE use
                        'copy_new' - L999 or P999999. FUTURE use
        Type - Action   'location' - 'last': The last location played.
                        SourceMaster = loc. Code, SourceDetail = loc. Name,
                        Target = TopDir
        Type - Action   'encoding' - 'format': Target = oga, mp4, flac or wav
                        'encoding' - 'quality': Size = 30 to 100
                        'encoding' - 'naming': SM = '99 ' or '99 - '
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
    """ Save system configuration recorded in SQL history table in the
        'Type' + 'Action' columns. Not to be confused with user configurations
        kept in sql.Config() class above.
    """
    # Check if record exists
    d = get_config(Type, Action)
    if d is None:
        hist_add(time.time(), 0, g.USER, Type, Action, SourceMaster,
                 SourceDetail, Target, Size, Count, Seconds, Comments)
        return

    now = time.time()
    cmd = "UPDATE History SET Time=?, SourceMaster=?, SourceDetail=?, \
        Target=?, Size=?, Count=?, Seconds=?, Comments=?, Timestamp=? \
        WHERE Id = ?"
    hist_cursor.execute(cmd, (now, SourceMaster, SourceDetail, Target,
                              Size, Count, Seconds, Comments, now,
                              d['Id']))

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
    """ Add History Row for Synchronizing Lyrics Time Indices. """
    # DEBUG:
    # InterfaceError: Error binding parameter 1 - probably unsupported type.
    # print("Time, MusicId, User, Type, Action, SourceMaster, SourceDetail,")
    # print("Target, Size, Count, Seconds, Comments:")
    # print(Time, MusicId, User, Type, Action, SourceMaster, SourceDetail,
    #      Target, Size, Count, Seconds, Comments)
    sql = "INSERT INTO History (Time, MusicId, User, Type, Action, \
           SourceMaster, SourceDetail, Target, Size, Count, Seconds, Comments, \
           Timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    hist_cursor.execute(sql, (Time, MusicId, User, Type, Action, SourceMaster,
                              SourceDetail, Target, Size, Count, Seconds,
                              Comments, time.time()))


def hist_delete_type_action(Type, Action):
    """ Delete History Rows for matching Type and Action.
        Created to get rid of thousands of 'meta' 'edit' errors
        NOTE:   Don't use this anymore
                Use sqlite browser instead
                Keep this as boilerplate for next time
    """

    sql = "DELETE FROM History WHERE Type=? AND Action=?"

    hist_cursor.execute(sql, (Type, Action))
    deleted_row_count = hist_cursor.rowcount
    print('hist_delete_type_action(Type, Action):', Type, Action,
          'deleted_row_count:', deleted_row_count)
    con.commit()


def hist_rename_type_action(Type, Action, newType, newAction):
    """ Rename History Rows for matching Type and Action.
        Created to rename "Volume", "Analyze" to "volume", "detect_1"
    """

    print("sql.py hist_rename_type_action(Type, Action...) <--- OLD")
    hist_count_type_action(Type, Action)
    hist_count_type_action(newType, newAction)

    sql = "UPDATE History INDEXED BY TypeActionIndex " +\
          "SET Type = ?, Action = ? " +\
          "WHERE Type = ? AND Action = ? "
    hist_cursor.execute(sql, (newType, newAction, Type, Action))
    con.commit()

    print("sql.py hist_count_type_action(...newType, newAction) <--- NEW")
    hist_count_type_action(newType, newAction)


def hist_count_type_action(Type, Action, prt=True, tab=True):
    """ Count History Rows for matching Type and Action. """

    sql = "SELECT * FROM History INDEXED BY TypeActionIndex " +\
          "WHERE Type = ? AND Action = ? "
    hist_cursor.execute(sql, (Type, Action))
    rows = hist_cursor.fetchall()
    row_count = len(rows)

    tabs = "\t\t" if tab else ""  # show_debug() will want a tab to align
    prt_type = " | Type='" + Type + "' | Action='" + Action + "' | "
    if prt:
        print(tabs + 'History Table rows:', prt_type,
              'count:', '{:n}'.format(row_count))

    return row_count


def hist_count_type_action_master(Type, Action, SourceMaster, prt=True, tab=True):
    """ Count History Rows for matching Type, Action and SourceMaster. 
        Created 2024-04-13 to tally Type == "Volume", Action == "Analyze",
            SourceMaster == "L004" (Location Code)
    """

    sql = "SELECT * FROM History INDEXED BY TypeActionIndex " +\
          "WHERE Type = ? AND Action = ? AND SourceMaster =  ?"
    hist_cursor.execute(sql, (Type, Action, SourceMaster))
    rows = hist_cursor.fetchall()
    row_count = len(rows)

    tabs = "\t\t" if tab else ""  # show_debug() will want a tab to align
    prt_type = " | Type='" + Type + "' | Action='" + Action + "' | " +\
               "SourceMaster: '" + SourceMaster + "' | "
    if prt:
        print(tabs + 'SQL History:', prt_type,
              'count:', '{:n}'.format(row_count))

    return row_count


def hist_tally_whole(prt=True, tab=True):
    """ Tally All History Rows by Type and Action. """

    sql = "SELECT max(Id) FROM History;"
    hist_cursor.execute(sql)
    d = hist_cursor.fetchone()
    print("SELECT max(Id) FROM History;", d)


    tally = {}
    sql = "SELECT * FROM History;"
    hist_cursor.execute(sql)
    rows = hist_cursor.fetchall()
    for sql_row in rows:
        row = dict(sql_row)
        Type = row['Type']
        Action = row['Action']
        if Type+"-"+Action in tally:
            tally[Type+"-"+Action] += 1
        else:
            tally[Type+"-"+Action] = 1

    tabs = "\t\t" if tab else ""  # show_debug() will want a tab to align
    if prt:
        total = 0
        for key in tally:
            print(tabs+key[:12], '\t{:n}'.format(tally[key]))
            total += tally[key]
        print(tabs+"Total all Type-Action:", '{:n}'.format(total))

    return tally


def hist_init_lyrics_and_time():
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
    User = g.USER
    Type = 'lyrics'
    Action = 'scrape'
    SourceMaster = 'Genius'  # Website lyrics were scraped from
    Comments = 'Automatically added by hist_init_lyrics_and_time(): '
    Comments += asc_time()

    # Select songs that have lyrics (Python 'not None:' = SQL 'NOT NULL')
    for row in cursor.execute("SELECT Id, OsFileName, LyricsScore, " +
                              "LyricsTimeIndex, Seconds FROM " +
                              "Music WHERE LyricsScore IS NOT NULL"):
        song_count += 1
        # Check if history already exists for song
        MusicId = row[0]
        if hist_check(MusicId, Type, Action):
            continue

        # Name our Music Table columns needed for History Table
        OsFileName = row[1] 
        LyricsScore = row[2]
        LyricsTimeIndex = row[3]
        Seconds = row[4]                        # Song Duration

        ''' Build full song path '''
        full_path = START_DIR.encode("utf-8") + OsFileName
        # Below not needed because (No Xxx) stubs not in Music Table filenames
        full_path = full_path.replace(os.sep + NO_ARTIST_STR, '')
        full_path = full_path.replace(os.sep + NO_ALBUM_STR, '')

        # os.stat gives us all of file's attributes
        stat = os.stat(full_path)
        Time = stat.st_atime                    # File's current access time
        #SourceDetail = time.asctime(time.localtime(Time))
        Size = len(LyricsScore)        # Can change after user edits
        Count = LyricsScore.count('\n')
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
        hist_add(Time, MusicId, User, Type, Action, SourceMaster, 
                 asc_time(Time), Target, Size, Count, 4.0, Comments)
        #hist_add(Time, MusicId, User, Type, Action, SourceMaster, SourceDetail, 
        #         Target, Size, Count, 4.0, Comments)  # Aug 3/23 - conversion
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
            hist_add(Time, MusicId, User, 'time', 'edit', loc_name(),
                     loc_code(), OsFileName, Size, Count, float(Seconds), 
                     Comments)
            #hist_add(Time, MusicId, User, 'time', 'edit', LODICT['name'],
            #         LODICT['iid'], OsFileName, Size, Count, float(Seconds), 
            #         Comments)  # Aug 3/23 - conversion
            add_time_count += 1

    #print('Songs with lyrics:', song_count, 'Added count:', add_count, \
    #      'Added time count:', add_time_count)
    con.commit()


# ============================  LOCATION TABLE  ===============================
def loc_add(Code, Name, ModifyTime, ImagePath, MountPoint, TopDir, HostName,
            HostWakeupCmd, HostTestCmd, HostTestRepeat, HostMountCmd,
            HostTouchCmd, HostTouchMinutes, Comments):
    """ Add SQL Location Table Row """
    sql = "INSERT INTO Location (Code, Name, ModifyTime, ImagePath, \
           MountPoint, TopDir, HostName, HostWakeupCmd, HostTestCmd, \
           HostTestRepeat, HostMountCmd, HostTouchCmd, HostTouchMinutes, \
           Comments) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    loc_cursor.execute(
        sql, 
        (Code, Name, ModifyTime, ImagePath, MountPoint, TopDir, HostName, 
         HostWakeupCmd, HostTestCmd, HostTestRepeat, HostMountCmd, HostTouchCmd, 
         HostTouchMinutes, Comments))
    con.commit()


def loc_update(Code, Name, ModifyTime, ImagePath, MountPoint, TopDir, HostName,
               HostWakeupCmd, HostTestCmd, HostTestRepeat, HostMountCmd,
               HostTouchCmd, HostTouchMinutes, Comments, Id):
    """ Update SQL Location Table Row """
    sql = "UPDATE Location SET Code=?, Name=?, ModifyTime=?, ImagePath=?, \
           MountPoint=?,  TopDir=?, HostName=?, HostWakeupCmd=?, HostTestCmd=?, \
           HostTestRepeat=?, HostMountCmd=?, HostTouchCmd=?, HostTouchMinutes=?, \
           Comments=? WHERE Id=?"
    loc_cursor.execute(
        sql, 
        (Code, Name, ModifyTime, ImagePath, MountPoint, TopDir, HostName, 
         HostWakeupCmd, HostTestCmd, HostTestRepeat, HostMountCmd, HostTouchCmd, 
         HostTouchMinutes, Comments, Id))
    con.commit()


def loc_read(Code):
    """ Read SQL Location Table Row for location code """
    loc_cursor.execute("SELECT * FROM Location WHERE Code = ?", [Code])
    try:
        d = dict(loc_cursor.fetchone())
    except TypeError:  # TypeError: 'NoneType' object is not iterable:
        d = None

    return d


# ==============================  AUTHENTICATION  =============================
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
            hist_add(time.time(), 0, g.USER, self.Type, self.Action, self.user,
                     self.email, self.Target, 0, 0, 0.0,
                     "User Authorization record created")
            con.commit()
            return True

        ''' We have the existing history record, simply replace the fields '''
        sql = "UPDATE History SET Timestamp=?, SourceMaster=?, SourceDetail=?, \
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
                NOT USED - Reviewed Sep 10/23 and considered deleting...

        ==========================   COPY from webscrape.py   =========================
            
        # Web scraping song lyrics IPC file names
        SCRAPE_CTL_FNAME    = g.TEMP_DIR + "mserve_scrape_ctl.json'
        SCRAPE_LIST_FNAME   = g.TEMP_DIR + "mserve_scrape_list.txt'
        SCRAPE_LYRICS_FNAME = g.TEMP_DIR + "mserve_scrape_lyrics.txt'
        
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
    """ SQL Music Table viewer Popup menu for 'View Current Row'. 
        Also called from Music Location Tree popup menu for music file.
    """

    def __init__(self, sql_row_id, calc=None, file_ctl=None):
        """ Build a pretty dictionary with user friendly field names
            Values are from current treeview row for SQL Row. See note above.

            The pretty dictionary is passed to mserve.py functions. """

        self.calc = calc  # Calculated fields callback function
        self.dict = OrderedDict()  # Python 2.7 version not needed in 3.7
        self.scrollbox = None  # custom scrollbox for display
        self.search = None  # search text
        self.synchronized = 0.0  # Only used for PrettyMusic dictionary.

        # List of part section starting positions in field display
        self.part_start = [0]  # First heading starts at field #0

        # List of part section headings at part_start[] list above
        self.part_names = ['SQL and OS Info (at first encounter!)',
                           'SQL Metadata Subset (more when song playing)',
                           'Lyrics score (usually after Webscraping)',
                           'History Time - Row Number       | Type | Action' +
                           ' | Master | Detail | Target | Comments',
                           'Metadata modified']
        # List of part colors - applied to key names. After 5 parts rest are green
        self.part_color = ['red', 'green', 'green', 'red', 'blue', 'green']
        # text 'Seconds' appears in 6th group which turns 'seconds' in 2nd & 3rd
        # groups to green for that word only. So make 2nd & 3rd 'green' too.

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
        self.dict['Last Access'] = sql_format_date(d['OsAccessTime'])
        self.dict['Modification time'] = sql_format_date(d['OsModifyTime'])
        self.dict['Change time'] = sql_format_date(d['OsChangeTime'])
        self.part_start.append(len(self.dict))

        self.dict['Title'] = sql_format_value(d['Title'])
        if d['FirstDate']:
            self.dict['Year'] = sql_format_value(d['FirstDate'])
        self.dict['Artist'] = sql_format_value(d['Artist'])
        self.dict['Album'] = sql_format_value(d['Album'])
        if d['Compilation']:
            self.dict['Compilation'] = 'Yes' if d['Compilation'] == "1" else 'No'
        if d['AlbumArtist']:
            self.dict['Album Artist'] = sql_format_value(d['AlbumArtist'])
        if d['AlbumDate']:
            self.dict['Album Date'] = sql_format_value(d['AlbumDate'])
        if d['CreationTime']:
            self.dict['Encoded'] = sql_format_value(d['CreationTime'])
        if d['DiscNumber']:
            self.dict['Disc Number'] = sql_format_value(d['DiscNumber'])
        if d['TrackNumber']:
            self.dict['Track Number'] = sql_format_value(d['TrackNumber'])
        if d['Rating']:
            self.dict['Rating'] = sql_format_value(d['Rating'])

        ''' ffMajor, ffMinor, ffCompatible, Title, Artist, Album, Compilation, 
        AlbumArtist, AlbumDate, FirstDate, CreationTime, DiscNumber, TrackNumber,
        Rating, Genre, Composer, Comment, Hyperlink, Duration, Seconds,
        GaplessPlayback, PlayCount, LastPlayTime, LyricsScore, LyricsTimeIndex 
        PLUS: EncodingFormat, DiscId, MusicBrainzDiscId, OsFileSize, OsAccessTime '''
        if d['Genre']:
            self.dict['Genre'] = sql_format_value(d['Genre'])
        if d['Composer']:
            self.dict['Composer'] = sql_format_value(d['Composer'])
        if d['Comment']:
            self.dict['Comment'] = sql_format_value(d['Comment'])
        if d['Hyperlink']:
            self.dict['Hyperlink'] = sql_format_value(d['Hyperlink'])
        if d['Duration']:
            self.dict['Duration'] = sql_format_value(d['Duration'])
        if d['Seconds']:
            self.dict['Seconds'] = sql_format_value(d['Seconds'])
        if d['GaplessPlayback'] and d['GaplessPlayback'] != "0":
            self.dict['Gapless Playback'] = sql_format_value(d['GaplessPlayback'])
        if d['PlayCount']:
            self.dict['Play Count'] = sql_format_value(d['PlayCount'])
        if d['LastPlayTime']:
            self.dict['Last Play Time'] = sql_format_date(d['LastPlayTime'])
        if d['ffMajor']:
            self.dict['Major Version'] = sql_format_value(d['ffMajor'])
        if d['ffMinor']:
            self.dict['Minor Version'] = sql_format_value(d['ffMinor'])
        if d['ffCompatible']:
            self.dict['Compatible Brands'] = sql_format_value(d['ffCompatible'])

        ''' If file_ctl passed, path is not none, and matches, use extra data '''
        # pycharm doesn't like PRUNED_DIR type 'None', expected 'Sized'
        # noinspection PyTypeChecker
        if file_ctl and file_ctl.path and \
                file_ctl.path[len(PRUNED_DIR):] == d['OsFileName']:
            if file_ctl.Encoder:
                self.dict['Encoder'] = file_ctl.Encoder
            if file_ctl.EncodingFormat:
                self.dict['Encoding Format'] = file_ctl.EncodingFormat
            if file_ctl.AudioStream:
                self.dict['Audio Stream'] = file_ctl.AudioStream[:80]
            if file_ctl.ArtworkStream:
                self.dict['Artwork Stream'] = file_ctl.ArtworkStream[:80]
            if file_ctl.DiscId:
                self.dict['CDDB Disc ID'] = file_ctl.DiscId
            if file_ctl.MusicBrainzDiscId:
                self.dict['MusicBrainz ID'] = file_ctl.MusicBrainzDiscId

        self.part_start.append(len(self.dict))

        lyrics_count = 0.0
        time_count = 0.0
        if d["LyricsTimeIndex"] is None:
            time_index_list = ["No time index"]  # Nothing prints yet.
        else:
            time_index_list = json.loads(d["LyricsTimeIndex"])
        if d["LyricsScore"] is None:
            self.dict['Lyrics score'] = "Webscrape for lyrics not completed."
        else:
            lyrics = d["LyricsScore"]
            lyrics_count = lyrics.count("\n")  # TODO: Test in Windows

            for i, line in enumerate(lyrics.splitlines()):
                # If time index exists, put value in front of lyric line
                try:
                    # pycharm doesn't like time_index_list, unexpected type str
                    # no inspection PyStringFormat
                    self.dict[tmf.mm_ss(time_index_list[i], trim=False,
                                        rem='h', brackets=True)] = line
                    time_count += 1.0
                except (IndexError, ValueError):
                    # IndexError: list index out of range
                    # ValueError: Unknown format code 'f' for object of type 'unicode'
                    self.dict['line # ' + str(i + 1)] = line

        if lyrics_count:
            self.synchronized = float(time_count / lyrics_count)
        else:
            self.synchronized = 0.0
        #print("time_count:", time_count, "lyrics_count:", lyrics_count,
        #      "percent:", self.synchronized)
        self.part_start.append(len(self.dict))

        ''' Append SQL History Table Rows matching Music ID '''
        hist_cursor.execute("SELECT * FROM History INDEXED BY MusicIdIndex \
                            WHERE MusicId = ?", (d['Id'],))
        rows = hist_cursor.fetchall()
        for sql_row in rows:
            row = dict(sql_row)
            ''' SQL is in Unicode, to concatenate "-" convert to strings '''
            self.dict[sql_format_date(row['Time']) + " - " + str(row['Id'])] = \
                " | " + str(row['Type']) + " | " + str(row['Action']) + " | " + \
                str(row['SourceMaster']) + " | " + str(row['SourceDetail']) + \
                " | " + str(row['Target']) + " | " + str(row['Comments'])

        if self.calc is not None:
            ''' TODO: Run 'ffprobe' for more metadata: 
                      Encoder Settings
                      Encoding Time
                      Free DiscId
                      Musicbrainz DiscId
            '''
            self.calc(self.dict)  # Call external function passing our dict


class PrettyHistory:
    """ Format History Row using data dictionary """
    def __init__(self, sql_row_id, calc=None):
        """ 
            Build a pretty dictionary with user friendly field names
            Values are from current treeview row for SQL Row

            The pretty dictionary is passed to mserve.py functions.

        """

        self.calc = calc  # Calculated fields such as delete_on
        self.dict = OrderedDict()
        self.scrollbox = None  # custom scrollbox for display
        self.search = None  # search text

        # List of part section starting positions in field display
        self.part_start = [0]  # First heading starts at field #0

        # List of part section headings at part_start[] list above
        self.part_names = [  # List of parts each colored separately
            'SQL Information', 'Time', 'Timestamp', 'History Category',
            'Source and Target Data', 'Processing Details']
        self.part_color = [  # Colors in order of parts.
            'red', 'green', 'green', 'red', 'blue', 'green']
        # text 'Seconds' appears in 6th group which turns 'seconds' in 2nd & 3rd
        # groups to green for that word only. So make 2nd & 3rd 'green' too.

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
        self.dict['Human Time '] = sql_format_date(d['Timestamp'])
        self.dict['Time in seconds '] = sql_format_value(d['Timestamp'])
        fmt_time = datetime.datetime.fromtimestamp(d['Timestamp'])
        self.dict['System Time '] = fmt_time.strftime("%c")

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
        self.dict['User'] = sql_format_value(d['User'])  # 2024-03-29 not appearing?

        if self.calc is not None:
            self.calc(self.dict)  # Call external function passing our dict
            # print("self.calc(self.dict)  # Call external function passing our dict")

        # print('\n======================  pretty  =====================\n')
        # print(json.dumps(self.dict, indent=2))


class PrettyLocation:
    """ Format Location Row using data dictionary """
    def __init__(self, sql_row_id):
        """
            Build a pretty dictionary with user friendly field names
            Values are from current treeview row for SQL Row

            The pretty dictionary is passed to mserve.py functions.

        """

        self.dict = OrderedDict()
        self.scrollbox = None  # custom scrollbox for display
        self.search = None  # search text

        # List of part section starting positions in field display
        self.part_start = [0]  # First heading starts at field #0

        # List of part section headings at part_start[] list above
        self.part_names = ['Required Information', 'Optional Host Details']
        self.part_color = ['blue', 'green']

        # Get Music Table row, remove commas
        key = sql_row_id.replace(',', '')
        #print("sql_row_id:", sql_row_id, 'key:', key)
        loc_cursor.execute("SELECT * FROM Location WHERE Id = ?", [key])

        try:
            d = dict(loc_cursor.fetchone())
        except TypeError:  # TypeError: 'NoneType' object is not iterable:
            d = None
        if d is None:
            print('sql.py.PrettyLocation() - No SQL for Location Row Id:', key)
            return

        self.dict['SQL Location Row Id'] = sql_format_value(d['Id'])
        self.dict['Location Code'] = sql_format_value(d['Code'])
        self.dict['Name'] = sql_format_value(d['Name'])
        self.dict['Modified Time'] = sql_format_date(d['ModifyTime'])
        self.dict['Image Path'] = sql_format_value(d['ImagePath'])
        self.dict['Mount Point'] = sql_format_value(d['MountPoint'])
        self.dict['Music Top Directory'] = sql_format_value(d['TopDir'])
        self.dict['Comments'] = sql_format_value(d['Comments'])
        self.part_start.append(len(self.dict))
        self.dict['Host Name'] = sql_format_value(d['HostName'])
        self.dict['Host Wakeup Command'] = sql_format_value(d['HostWakeupCmd'])
        self.dict['Host Test Command'] = sql_format_value(d['HostTestCmd'])
        self.dict['Host Test Repeat'] = sql_format_value(d['HostTestRepeat'])
        self.dict['Host Mount Command'] = sql_format_value(d['HostMountCmd'])
        self.dict['Host Touch Command'] = sql_format_value(d['HostTouchCmd'])
        self.dict['Host Touch Minutes'] = sql_format_value(d['HostTouchMinutes'])


class PrettyTreeHeading:
    """ Format pretty dictionary for treeview column fields """
    def __init__(self, column_dict):
        """ Display data dictionary for selected heading.
            Build a pretty dictionary with user friendly field names
            Use column dictionary that was passed to Tkinter.
            The pretty dictionary is passed to mserve.py functions. """
        self.calc = None  # Calculated fields not for column data dictionary
        self.dict = OrderedDict()  # Python 2.7 version not needed in 3.7
        self.scrollbox = None  # scrollbox for display defined later
        self.search = None  # Not used but needed for tkinter_display()

        # Data dictionary for treeview column format is simple
        self.part_start = [0]  # Only 1 part
        self.part_names = ['Column Keys\tAttributes\n']
        self.part_color = ['red']
        for key, value in column_dict.iteritems():
            self.dict[key] = sql_format_value(value)


class PrettyMeta:
    """ Format data dictionary for Song Metadata """
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
                 compatible_brands: M4A mp42i som
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
                 gap less_playback: 0
                 encoder         : iTunes 10.0.1.22, QuickTime 7.6.8
                 iTunS MPB        :  00000000 00000840 000000E4 00000000009E06DC 00000000 00000000
                 00000000 00000000 00000000 00000000 00000000 00000000
                 Encoding Params : vers
                 iTunNORM        :  00001110 000011B9 00009226 0000C BAB 0002B4B2 00035A23 00008000
                 00007FFF 0000FC3E 00000929
                 iTunes_CDDB_IDs : 16++
                 UFIDhttp://www.cddb.com/id3/taginfo1.html: 3CD3N27S7396714U2686A83124FE1E51E62C229DF55B180DA9EP6
               Duration: 00:03:54.89, start: 0.000000, bit rate: 265 kb/s
                 Stream #0:0(und): Audio: aac (LC) (mp4a / 0x6134706D), 44100 Hz, stereo, fl tp, 262 kb/s (default)
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
    """ Format variable based on data dictionary """
    if value is None:
        return None  # Do we want to return empty string instead?

    try:
        formatted = str(value)  # Convert from int
    except UnicodeEncodeError:
        formatted = value  # Already string
    # return formatted.encode('utf8')
    # TypeError: coercing to Unicode: need string or buffer, int found
    return formatted


def sql_format_int(value):
    """ Format variable based on data dictionary """
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
    """ Format variable based on data dictionary """
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

        IDENTICAL function in ~/bserve/gmail_api.py (bserve has own sql.py)

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
        try:
            value = pretty.dict[key]
            if value is None:
                value = "None"
            pretty.scrollbox.insert("end", u"\t" + key + u":\t" +
                                    value + u"\n", u"margin")
        except TypeError:  # 2024-03-30
            print("sql.py tkinter_display() pretty.scrollbox.insert",
                  "TypeError: key:", key)

        pretty.scrollbox.highlight_pattern(key + u':', curr_color)
        ''' Hoping | isn't used often, highlight in yellow for field separator '''
        pretty.scrollbox.highlight_pattern(u'|', 'magenta')
        curr_key += 1  # Current key index

    if pretty.search is not None:
        # Breakdown string into set of words
        words = pretty.search.split()
        # NOTE: yellow, cyan and magenta are defined to highlight background
        #pretty.scrollbox.highlight_pattern(pretty.search, "yellow")
        for w in words:
            pretty.scrollbox.highlight_pattern(w, "yellow")

    # Don't allow changes to displayed selections (test copy clipboard)
    pretty.scrollbox.configure(state="disabled")


def music_treeview():
    """ Define Data Dictionary treeview columns for Music table
        2024-03-24 used to be ("instance", int) but json.dumps would crash.
                RENAME: int -> "int", str -> "str", float -> "float"
        2024-04-07 - title, lyrics and os_file_size must be keys for buttons
            in mus_view to function properly.
    """

    music_treeview_list = [

      OrderedDict([
        ("column", "row_id"), ("heading", "Row ID"), ("sql_table", "Music"),
        ("var_name", "Id"), ("select_order", 0), ("unselect_order", 1),
        ("key", True), ("anchor", "e"), ("instance", "int"), ("format", "{:,}"),
        ("width", 80), ("minwidth", 50), ("stretch", 0)]),  # 0=NO, 1=YES

      OrderedDict([
        ("column", "os_filename"), ("heading", "OS Filename"), ("sql_table", "Music"),
        ("var_name", "OsFileName"), ("select_order", 0), ("unselect_order", 2),
        ("key", True), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 200), ("minwidth", 50), ("stretch", 1)]),  # 0=NO, 1=YES

      OrderedDict([
        ("column", "os_atime"), ("heading", "Access Time"), ("sql_table", "Music"),
        ("var_name", "OsAccessTime"), ("select_order", 0), ("unselect_order", 3),
        ("key", False), ("anchor", "w"), ("instance", "float"), ("format", "date"),
        ("width", 180), ("minwidth", 50), ("stretch", 0)]),  # 0=NO, 1=YES

      OrderedDict([
        ("column", "os_mtime"), ("heading", "Modify Time"), ("sql_table", "Music"),
        ("var_name", "OsModifyTime"), ("select_order", 0), ("unselect_order", 4),
        ("key", False), ("anchor", "w"), ("instance", "float"), ("format", "date"),
        ("width", 180), ("minwidth", 50), ("stretch", 0)]),

      OrderedDict([
        ("column", "os_ctime"), ("heading", "Change Time"), ("sql_table", "Music"),
        ("var_name", "OsChangeTime"), ("select_order", 0), ("unselect_order", 5),
        ("key", False), ("anchor", "e"), ("instance", "float"), ("format", "date"),
        ("width", 180), ("minwidth", 50), ("stretch", 0)]),

      OrderedDict([
        ("column", "os_file_size"), ("heading", "File Size"), ("sql_table", "Music"),
        ("var_name", "OsFileSize"), ("select_order", 0), ("unselect_order", 6),
        ("key", True), ("anchor", "e"), ("instance", "int"), ("format", "{:,}"),
        ("width", 150), ("minwidth", 50), ("stretch", 0)]),  # key for missing art

      OrderedDict([
        ("column", "artist"), ("heading", "Artist"), ("sql_table", "Music"),
        ("var_name", "Artist"), ("select_order", 0), ("unselect_order", 7),
        ("key", False), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 200), ("minwidth", 50), ("stretch", 1)]),  # 0=NO, 1=YES

      OrderedDict([
        ("column", "album"), ("heading", "Album"), ("sql_table", "Music"),
        ("var_name", "Album"), ("select_order", 0), ("unselect_order", 8),
        ("key", False), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 200), ("minwidth", 50), ("stretch", 1)]),

      OrderedDict([
        ("column", "title"), ("heading", "Title"), ("sql_table", "Music"),
        ("var_name", "Title"), ("select_order", 0), ("unselect_order", 9),
        ("key", True), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 200), ("minwidth", 50), ("stretch", 1)]),  # key for metadata

      OrderedDict([
        ("column", "first_date"), ("heading", "Year"), ("sql_table", "Music"),
        ("var_name", "FirstDate"), ("select_order", 0), ("unselect_order", 10),
        ("key", False), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 80), ("minwidth", 50), ("stretch", 0)]),

      OrderedDict([
        ("column", "album_date"), ("heading", "Album Date"), ("sql_table", "Music"),
        ("var_name", "AlbumDate"), ("select_order", 0), ("unselect_order", 11),
        ("key", False), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 120), ("minwidth", 50), ("stretch", 0)]),

      OrderedDict([
        ("column", "genre"), ("heading", "Genre"), ("sql_table", "Music"),
        ("var_name", "Genre"), ("select_order", 0), ("unselect_order", 12),
        ("key", False), ("anchor", "center"), ("instance", "str"), ("format", None),
        ("width", 160), ("minwidth", 50), ("stretch", 1)]),

      OrderedDict([
        ("column", "seconds"), ("heading", "Seconds"), ("sql_table", "Music"),
        ("var_name", "Seconds"), ("select_order", 0), ("unselect_order", 13),
        ("key", False), ("anchor", "e"), ("instance", "str"), ("format", None),
        ("width", 80), ("minwidth", 50), ("stretch", 1)]),

      OrderedDict([
        ("column", "duration"), ("heading", "Duration"), ("sql_table", "Music"),
        ("var_name", "Duration"), ("select_order", 0), ("unselect_order", 14),
        ("key", False), ("anchor", "center"), ("instance", "str"), ("format", None),
        ("width", 80), ("minwidth", 50), ("stretch", 1)]),

      OrderedDict([
        ("column", "play_count"), ("heading", "Play Count"), ("sql_table", "Music"),
        ("var_name", "PlayCount"), ("select_order", 0), ("unselect_order", 15),
        ("key", False), ("anchor", "center"), ("instance", "int"), ("format", "{:,}"),
        ("width", 70), ("minwidth", 50), ("stretch", 1)]),

      OrderedDict([
        ("column", "track_number"), ("heading", "Track"), ("sql_table", "Music"),
        ("var_name", "TrackNumber"), ("select_order", 0), ("unselect_order", 16),
        ("key", False), ("anchor", "e"), ("instance", "str"), ("format", None),
        ("width", 80), ("minwidth", 50), ("stretch", 1)]),

      OrderedDict([
        ("column", "rating"), ("heading", "Rating"), ("sql_table", "Music"),
        ("var_name", "Rating"), ("select_order", 0), ("unselect_order", 17),
        ("key", False), ("anchor", "w"), ("instance", "int"), ("format", "{:,}"),
        ("width", 80), ("minwidth", 50), ("stretch", 1)]),

      OrderedDict([
        ("column", "lyrics"), ("heading", "Lyrics"), ("sql_table", "Music"),
        ("var_name", "LyricsScore"), ("select_order", 0), ("unselect_order", 18),
        ("key", True), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 200), ("minwidth", 50), ("stretch", 1)]),  # key for missing lyrics

      OrderedDict([
        ("column", "time_index"), ("heading", "Time Index"), ("sql_table", "Music"),
        ("var_name", "LyricsTimeIndex"), ("select_order", 0), ("unselect_order", 19),
        ("key", True), ("anchor", "w"), ("instance", "list"), ("format", None),
        ("width", 100), ("minwidth", 50), ("stretch", 1)]),  # key for unsync'd

      OrderedDict([
        ("column", "creation_time"), ("heading", "Creation Time"), ("sql_table", "Music"),
        ("var_name", "CreationTime"), ("select_order", 0), ("unselect_order", 20),
        ("key", False), ("anchor", "w"), ("instance", "float"), ("format", "date"),
        ("width", 180), ("minwidth", 50), ("stretch", 0)]),

      OrderedDict([
        ("column", "last_play_time"), ("heading", "Last Play Time"), ("sql_table", "Music"),
        ("var_name", "LastPlayTime"), ("select_order", 0), ("unselect_order", 21),
        ("key", False), ("anchor", "w"), ("instance", "float"), ("format", "date"),
        ("width", 180), ("minwidth", 50), ("stretch", 0)]),

      OrderedDict([
        ("column", "disc_number"), ("heading", "Disc #"), ("sql_table", "Music"),
        ("var_name", "DiscNumber"), ("select_order", 0), ("unselect_order", 22),
        ("key", False), ("anchor", "center"), ("instance", "str"), ("format", None),
        ("width", 160), ("minwidth", 50), ("stretch", 1)]),

      OrderedDict([
        ("column", "composer"), ("heading", "Composer"), ("sql_table", "Music"),
        ("var_name", "Composer"), ("select_order", 0), ("unselect_order", 23),
        ("key", False), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 160), ("minwidth", 50), ("stretch", 1)]),

      OrderedDict([
        ("column", "comment"), ("heading", "Comment"), ("sql_table", "Music"),
        ("var_name", "Comment"), ("select_order", 0), ("unselect_order", 24),
        ("key", False), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 160), ("minwidth", 50), ("stretch", 1)]),

      OrderedDict([
        ("column", "hyperlink"), ("heading", "Hyperlink"), ("sql_table", "Music"),
        ("var_name", "Hyperlink"), ("select_order", 0), ("unselect_order", 25),
        ("key", False), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 160), ("minwidth", 50), ("stretch", 1)]),

      OrderedDict([
        ("column", "album_artist"), ("heading", "Album Artist"), ("sql_table", "Music"),
        ("var_name", "AlbumArtist"), ("select_order", 0), ("unselect_order", 26),
        ("key", False), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 160), ("minwidth", 50), ("stretch", 1)]),

      OrderedDict([
        ("column", "compilation"), ("heading", "Compilation"), ("sql_table", "Music"),
        ("var_name", "Compilation"), ("select_order", 0), ("unselect_order", 27),
        ("key", False), ("anchor", "center"), ("instance", "str"), ("format", None),
        ("width", 80), ("minwidth", 50), ("stretch", 0)]),

      OrderedDict([
        ("column", "gapless"), ("heading", "Gapless Playback"), ("sql_table", "Music"),
        ("var_name", "GaplessPlayback"), ("select_order", 0), ("unselect_order", 28),
        ("key", False), ("anchor", "center"), ("instance", "str"), ("format", None),
        ("width", 80), ("minwidth", 50), ("stretch", 0)]),

      OrderedDict([
        ("column", "ff_major"), ("heading", "Major Brand"), ("sql_table", "Music"),
        ("var_name", "ffMajor"), ("select_order", 0), ("unselect_order", 29),
        ("key", False), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 80), ("minwidth", 50), ("stretch", 0)]),

      OrderedDict([
        ("column", "ff_minor"), ("heading", "Minor Version"), ("sql_table", "Music"),
        ("var_name", "ffMinor"), ("select_order", 0), ("unselect_order", 30),
        ("key", False), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 80), ("minwidth", 50), ("stretch", 0)]),

      OrderedDict([
        ("column", "compatible"), ("heading", "Compatible Brands"), ("sql_table", "Music"),
        ("var_name", "ffMinor"), ("select_order", 0), ("unselect_order", 31),
        ("key", False), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 160), ("minwidth", 50), ("stretch", 1)]),

    ]

    return music_treeview_list


def history_treeview():
    """ Define Data Dictionary treeview columns for history table.

        2024-04-07 - Music ID must be key for buttons
        in his_view to function properly.
    """

    history_treeview_list = [

      OrderedDict([
        ("column", "time"), ("heading", "Time"), ("sql_table", "History"),
        ("var_name", "Time"), ("select_order", 0), ("unselect_order", 1),
        ("key", False), ("anchor", "w"), ("instance", "float"), ("format", "date"),
        ("width", 300), ("minwidth", 200), ("stretch", 0)]),

      OrderedDict([
        ("column", "music_id"), ("heading", "Music ID"), ("sql_table", "History"),
        ("var_name", "MusicId"), ("select_order", 0), ("unselect_order", 2),
        ("key", True), ("anchor", "e"), ("instance", "int"), ("format", "{:,}"),
        ("width", 100), ("minwidth", 80), ("stretch", 0)]),  # 0=NO, 1=YES

      OrderedDict([
        ("column", "user"), ("heading", "User"), ("sql_table", "History"),
        ("var_name", "User"), ("select_order", 0), ("unselect_order", 3),
        ("key", False), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 150), ("minwidth", 120), ("stretch", 1)]),  # 0=NO, 1=YES

      OrderedDict([
        ("column", "type"), ("heading", "Type"), ("sql_table", "History"),
        ("var_name", "Type"), ("select_order", 0), ("unselect_order", 4),
        ("key", False), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 80), ("minwidth", 60), ("stretch", 1)]),

      OrderedDict([
        ("column", "action"), ("heading", "Action"), ("sql_table", "History"),
        ("var_name", "Action"), ("select_order", 0), ("unselect_order", 5),
        ("key", False), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 80), ("minwidth", 60), ("stretch", 1)]),

      OrderedDict([
        ("column", "master"), ("heading", "Master"), ("sql_table", "History"),
        ("var_name", "SourceMaster"), ("select_order", 0), ("unselect_order", 6),
        ("key", False), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 150), ("minwidth", 100), ("stretch", 1)]),

      OrderedDict([
        ("column", "detail"), ("heading", "Detail"), ("sql_table", "History"),
        ("var_name", "SourceDetail"), ("select_order", 0), ("unselect_order", 7),
        ("key", False), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 150), ("minwidth", 100), ("stretch", 1)]),  # 0=NO, 1=YES

      OrderedDict([
        ("column", "target"), ("heading", "Target"), ("sql_table", "History"),
        ("var_name", "Target"), ("select_order", 0), ("unselect_order", 8),
        ("key", False), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 300), ("minwidth", 200), ("stretch", 1)]),

      OrderedDict([  # Hard coded as Offset 8 in Playlists().populate_his_tree()
        ("column", "size"), ("heading", "Size"), ("sql_table", "History"),
        ("var_name", "Size"), ("select_order", 0), ("unselect_order", 9),
        ("key", False), ("anchor", "e"), ("instance", "int"), ("format", "{:,}"),
        ("width", 100), ("minwidth", 80), ("stretch", 1)]),

      OrderedDict([
        ("column", "count"), ("heading", "Count"), ("sql_table", "History"),
        ("var_name", "Count"), ("select_order", 0), ("unselect_order", 10),
        ("key", False), ("anchor", "e"), ("instance", "int"), ("format", "{:,}"),
        ("width", 80), ("minwidth", 60), ("stretch", 1)]),

      OrderedDict([
        ("column", "comments"), ("heading", "Comments"), ("sql_table", "History"),
        ("var_name", "Comments"), ("select_order", 0), ("unselect_order", 11),
        ("key", False), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 160), ("minwidth", 140), ("stretch", 1)]),

      OrderedDict([
        ("column", "seconds"), ("heading", "Seconds"), ("sql_table", "History"),
        ("var_name", "Seconds"), ("select_order", 0), ("unselect_order", 12),
        ("key", False), ("anchor", "e"), ("instance", "float"), ("format", "{0:,.4f}"),
        ("width", 140), ("minwidth", 80), ("stretch", 1)]),

      OrderedDict([
        ("column", "row_id"), ("heading", "Row ID"), ("sql_table", "History"),
        ("var_name", "Id"), ("select_order", 0), ("unselect_order", 13),
        ("key", True), ("anchor", "e"), ("instance", "int"), ("format", "{:,}"),
        ("width", 80), ("minwidth", 60), ("stretch", 1)]),

      OrderedDict([
        ("column", "timestamp"), ("heading", "Timestamp"), ("sql_table", "History"),
        ("var_name", "Timestamp"), ("select_order", 0), ("unselect_order", 14),
        ("key", False), ("anchor", "w"), ("instance", "float"), ("format", "date"),
        ("width", 300), ("minwidth", 200), ("stretch", 0)]),

      OrderedDict([
        ("column", "reason"), ("heading", "Reason"), ("sql_table", "calc"),
        ("var_name", "reason"), ("select_order", 0), ("unselect_order", 15),
        ("key", False), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 160), ("minwidth", 140), ("stretch", 1)])
    ]

    return history_treeview_list


def playlist_treeview():
    """ Define Data Dictionary treeview columns for playlists in history table.
        self.his_view.tree.heading('detail', text='Playlist Name')
        self.his_view.tree.heading('comments', text='Playlist Description')
        self.his_view.tree.heading('count', text='Song Count')
        self.his_view.tree.heading('size', text='Size of Files')
        self.his_view.tree.heading('seconds', text='Duration')

                sql.save_config('playlist', self.open_code, self.open_loc_id,
                        self.open_name, json.dumps(self.open_id_list),
                        self.open_size, self.open_count, self.open_seconds,
                        self.open_description)

def save_config(Type, Action="", SourceMaster="", SourceDetail="", Target="",
                Size=0, Count=0, Seconds=0.0, Comments=""):
    # Check if record exists
    d = get_config(Type, Action)
    if d is None:
        hist_add(time.time(), 0, g.USER, Type, Action, SourceMaster,
                 SourceDetail, Target, Size, Count, Seconds, Comments)

    """

    playlist_treeview_list = [

      OrderedDict([
        ("column", "time"), ("heading", "Time"), ("sql_table", "History"),
        ("var_name", "Time"), ("select_order", 0), ("unselect_order", 1),
        ("key", False), ("anchor", "w"), ("instance", "float"), ("format", "date"),
        ("width", 300), ("minwidth", 200), ("stretch", 0)]),

      OrderedDict([
        ("column", "music_id"), ("heading", "Always 0"), ("sql_table", "History"),
        ("var_name", "MusicId"), ("select_order", 0), ("unselect_order", 2),
        ("key", False), ("anchor", "e"), ("instance", "int"), ("format", "{:,}"),
        ("width", 100), ("minwidth", 80), ("stretch", 0)]),  # 0=NO, 1=YES

      OrderedDict([
        ("column", "user"), ("heading", "User"), ("sql_table", "History"),
        ("var_name", "User"), ("select_order", 0), ("unselect_order", 3),
        ("key", False), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 150), ("minwidth", 120), ("stretch", 1)]),  # 0=NO, 1=YES

      OrderedDict([
        ("column", "type"), ("heading", "'Playlist'"), ("sql_table", "History"),
        ("var_name", "Type"), ("select_order", 0), ("unselect_order", 4),
        ("key", False), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 80), ("minwidth", 60), ("stretch", 1)]),

      OrderedDict([
        ("column", "action"), ("heading", "P999999"), ("sql_table", "History"),
        ("var_name", "Action"), ("select_order", 0), ("unselect_order", 5),
        ("key", False), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 80), ("minwidth", 60), ("stretch", 1)]),

      OrderedDict([
        ("column", "master"), ("heading", "Loc. Code"), ("sql_table", "History"),
        ("var_name", "SourceMaster"), ("select_order", 0), ("unselect_order", 6),
        ("key", False), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 150), ("minwidth", 100), ("stretch", 1)]),

      OrderedDict([
        ("column", "detail"), ("heading", "Playlist Name"), ("sql_table", "History"),
        ("var_name", "SourceDetail"), ("select_order", 0), ("unselect_order", 7),
        ("key", False), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 150), ("minwidth", 100), ("stretch", 1)]),  # 0=NO, 1=YES

      OrderedDict([
        ("column", "target"), ("heading", "Music ID list"), ("sql_table", "History"),
        ("var_name", "Target"), ("select_order", 0), ("unselect_order", 8),
        ("key", False), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 300), ("minwidth", 200), ("stretch", 1)]),

      OrderedDict([
        ("column", "size"), ("heading", "Size of Files"), ("sql_table", "History"),
        ("var_name", "Size"), ("select_order", 0), ("unselect_order", 9),
        ("key", False), ("anchor", "e"), ("instance", "int"), ("format", "{:,}"),
        ("width", 100), ("minwidth", 80), ("stretch", 1)]),

      OrderedDict([
        ("column", "count"), ("heading", "Song Count"), ("sql_table", "History"),
        ("var_name", "Count"), ("select_order", 0), ("unselect_order", 10),
        ("key", False), ("anchor", "e"), ("instance", "int"), ("format", "{:,}"),
        ("width", 80), ("minwidth", 60), ("stretch", 1)]),

      OrderedDict([
        ("column", "comments"), ("heading", "Playlist Description"), ("sql_table", "History"),
        ("var_name", "Comments"), ("select_order", 0), ("unselect_order", 11),
        ("key", False), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 500), ("minwidth", 300), ("stretch", 1)]),

      OrderedDict([
        ("column", "seconds"), ("heading", "Duration"), ("sql_table", "History"),
        ("var_name", "Seconds"), ("select_order", 0), ("unselect_order", 12),
        ("key", False), ("anchor", "e"), ("instance", "float"), ("format", "{0:,.4f}"),
        ("width", 140), ("minwidth", 80), ("stretch", 1)]),

      OrderedDict([
        ("column", "row_id"), ("heading", "Row ID"), ("sql_table", "History"),
        ("var_name", "Id"), ("select_order", 0), ("unselect_order", 13),
        ("key", True), ("anchor", "e"), ("instance", "int"), ("format", "{:,}"),
        ("width", 80), ("minwidth", 60), ("stretch", 1)]),

      OrderedDict([
        ("column", "timestamp"), ("heading", "Timestamp"), ("sql_table", "History"),
        ("var_name", "Timestamp"), ("select_order", 0), ("unselect_order", 14),
        ("key", False), ("anchor", "w"), ("instance", "float"), ("format", "date"),
        ("width", 300), ("minwidth", 200), ("stretch", 0)]),

    ]

    return playlist_treeview_list


def location_treeview():
    """ Define Data Dictionary treeview columns for location table. """

    location_treeview_list = [

      OrderedDict([  # 'iid' in old version replaced by 'code'
        ("column", "code"), ("heading", "Code"), ("sql_table", "Location"),
        ("var_name", "Code"), ("select_order", 0), ("unselect_order", 1),
        ("key", True), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 80), ("minwidth", 100), ("stretch", 0)]),

      OrderedDict([
        ("column", "name"), ("heading", "Name"), ("sql_table", "Location"),
        ("var_name", "Name"), ("select_order", 0), ("unselect_order", 2),
        ("key", False), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 300), ("minwidth", 200), ("stretch", 1)]),  # 0=NO, 1=YES

      OrderedDict([
        ("column", "modify_time"), ("heading", "Modified Time"),
        ("sql_table", "Location"), ("var_name", "ModifyTime"), ("select_order", 0),
        ("unselect_order", 3), ("key", False), ("anchor", "w"), ("instance", "float"),
        ("format", "date"), ("width", 240), ("minwidth", 180), ("stretch", 1)]),

      OrderedDict([
        ("column", "image_path"), ("heading", "Location Image Path"),
        ("sql_table", "Location"), ("var_name", "ImagePath"), ("select_order", 0),
        ("unselect_order", 4), ("key", False), ("anchor", "w"), ("instance", "str"),
        ("format", None), ("width", 80), ("minwidth", 60), ("stretch", 1)]),

      OrderedDict([
        ("column", "mount_point"), ("heading", "Mount Point"),
        ("sql_table", "Location"), ("var_name", "MountPoint"), ("select_order", 0),
        ("unselect_order", 5), ("key", False), ("anchor", "w"), ("instance", "str"),
        ("format", None), ("width", 80), ("minwidth", 60), ("stretch", 1)]),

      OrderedDict([
        ("column", "topdir"), ("heading", "Music Top Directory"),
        ("sql_table", "Location"), ("var_name", "TopDir"), ("select_order", 0),
        ("unselect_order", 6), ("key", False), ("anchor", "w"), ("instance", "str"),
        ("format", None), ("width", 300), ("minwidth", 200), ("stretch", 1)]),

      OrderedDict([
        ("column", "host_name"), ("heading", "Host Name"),
        ("sql_table", "Location"), ("var_name", "HostName"), ("select_order", 0),
        ("unselect_order", 7), ("key", False), ("anchor", "w"), ("instance", "str"),
        ("format", None), ("width", 200), ("minwidth", 120), ("stretch", 1)]),

      OrderedDict([
        ("column", "wake_cmd"), ("heading", "Host Wakeup Command"),
        ("sql_table", "Location"), ("var_name", "HostWakeupCmd"), ("select_order", 0),
        ("unselect_order", 8), ("key", False), ("anchor", "w"), ("instance", "str"),
        ("format", None), ("width", 200), ("minwidth", 100), ("stretch", 1)]),  # 0=NO, 1=YES

      OrderedDict([
        ("column", "test_cmd"), ("heading", "Host Test Command"),
        ("sql_table", "Location"), ("var_name", "HostTestCmd"), ("select_order", 0),
        ("unselect_order", 9), ("key", False), ("anchor", "w"), ("instance", "str"),
        ("format", None), ("width", 300), ("minwidth", 200), ("stretch", 1)]),

      OrderedDict([
        ("column", "test_repeat"), ("heading", "Host Test Repeat"),
        ("sql_table", "Location"), ("var_name", "HostTestRepeat"), ("select_order", 0),
        ("unselect_order", 10), ("key", False), ("anchor", "w"), ("instance", "int"),
        ("format", "{:,}"),  ("width", 100), ("minwidth", 80), ("stretch", 1)]),

      OrderedDict([
        ("column", "mount_cmd"), ("heading", "Mount Command"),
        ("sql_table", "Location"), ("var_name", "HostMountCmd"), ("select_order", 0),
        ("unselect_order", 11), ("key", False), ("anchor", "w"), ("instance", "str"),
        ("format", None), ("width", 300), ("minwidth", 200), ("stretch", 1)]),

      OrderedDict([
        ("column", "touch_cmd"), ("heading", "Host Touch Command"),
        ("sql_table", "Location"), ("var_name", "HostTouchCmd"), ("select_order", 0),
        ("unselect_order", 12), ("key", False), ("anchor", "w"), ("instance", "str"),
        ("format", None), ("width", 160), ("minwidth", 140), ("stretch", 1)]),

      OrderedDict([
        ("column", "touch_cmd_minutes"), ("heading", "Host Touch Minutes"),
        ("sql_table", "Location"), ("var_name", "HostTouchMinutes"), ("select_order", 0),
        ("unselect_order", 13), ("key", False), ("anchor", "w"), ("instance", "int"),
        ("format", "{:,}"), ("width", 140), ("minwidth", 80), ("stretch", 1)]),

      OrderedDict([
        ("column", "comments"), ("heading", "Comments"), ("sql_table", "Location"),
        ("var_name", "Comments"), ("select_order", 0), ("unselect_order", 14),
        ("key", True), ("anchor", "w"), ("instance", "str"), ("format", None),
        ("width", 300), ("minwidth", 200), ("stretch", 1)]),

      OrderedDict([
        ("column", "row_id"), ("heading", "Row ID"), ("sql_table", "Location"),
        ("var_name", "Id"), ("select_order", 0), ("unselect_order", 15),
        ("key", True), ("anchor", "e"), ("instance", "int"), ("format", "{:,}"),
        ("width", 80), ("minwidth", 60), ("stretch", 1)]),

    ]

    return location_treeview_list


# ==============================  FIX SQL ROWS  ============================
class FixData:
    """ Class driver for various database repairs
        Change 999999 to Music ID to start granular printing.
    """
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

            Remember to physically delete corrupted music files or they
            will be added back on mserve.py startup !!!
        """
        # Backup database before updating
        self.backup(update)
        print_all = None

        ''' PHASE I - Delete History Records linked to MusicId '''

        fix_list = list()
        sql = "SELECT * FROM History INDEXED BY MusicIdIndex " +\
              "WHERE MusicId >= ? AND MusicId <= ?"
        hist_cursor.execute(sql, (start, end))
        rows = hist_cursor.fetchall()

        for sql_row in rows:
            row = dict(sql_row)
            print_all = False
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
                print("\nFound Music Table Row Id:", row['Id'], "| Title:", row['Title'])
                print_all = True

            del_list.append(OrderedDict([('Id', row['Id']),
                                         ('Title', row['Title']),
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

        # pycharm things print_all was never used:
        if True is False:
            print("print_all", print_all)

        self.wrapup(update)

    def fix_scrape_parm(self, update=False):
        """ Fix MusicId 0 by looking up real MusicId """
        # Backup database before updating
        self.backup(update)

        print_all = None
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

        # pycharm things print_all was never used:
        if True is False:
            print("print_all", print_all)

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
                print("fix_meta_edit() not found for music id:", row['MusicId'])

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
            sql = "UPDATE History SET SourceDetail=?, Comments=?, Timestamp=?" + \
                  " WHERE Id = ?"
            if not self.sql_cmd_error:
                try:
                    hist_cursor.execute(sql, (detail, comment, time.time(), key))
                    self.successful_update_count += 1
                except Exception as err:
                    print('sql.fix_utc_dates() Update Failed:\n  Error: %s' % (str(err)))
                    print("  detail:", detail)
                    print("  comment:", comment)
                    print("  time:", time.time())
                    print("  key:", key)
                    print(sql, "\n", (detail, comment, time.time(), key))
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
        """ Process single history row """
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

        epoch = 0.0

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

        ''' Lost setting epoch somewhere sometime '''
        # epoch =

        if 3 < time_obj.tm_mon < 11:
            off = -6*3600  # Summer Time -6 hours from utc
        else:
            off = -7*3600  # Winter Time -7 hours from utc

        epoch += float(off)

        return time.asctime(time.localtime(epoch))

    # Shared FixData() class functions

    @staticmethod
    def make_pretty_line(d):
        """ Make single data dictionary line """
        line = ""
        for key in d:
            # Last 40 chars of value, right justified to 5 when only 1 to 4 characters
            line += key + ": " + str(d[key])[-40:].rjust(5) + " | "
        return line

    def backup(self, update):
        """ Backup 'library.db' to 'library.db.bak """
        if update:
            self.test = False
            from location import FNAME_LIBRARY
            os.popen("cp -a " + FNAME_LIBRARY + " " + FNAME_LIBRARY + ".bak")

    def wrapup(self, update):
        """ Print summary lines """
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

    def print_summary(self, caller, dict_list):
        """ Print summary """
        print('\nsql.py FixData() ' + caller + ' Sub-Totals')
        for d in dict_list:
            if d['Count'] > 0:
                # Thousands of records so only print groups updated
                print(" ", self.make_pretty_line(d))

        print('\nsql.py FixData() ' + caller + ' Summary Counts')
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
        """ Is history row prior to cutoff date? """
        epoch = time.mktime(time_obj)
        if epoch < self.epoch_cutoff:
            self.fix_count += 1
            return True
        else:
            self.past_count += 1
            return False

    def populate_lib_tree(self, delayed_textbox):
        """ Fix os.stat Last Access Time using stored SQL last Access Time """

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

            ''' When using FTP, get size from size_dict, else os.stat() '''
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

# End of sql.py
