#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: Pippim
License: GNU GPLv3
Source: This repository
Description: mserve - Music Server - Locations of Music Dirs & Devices
"""

from __future__ import print_function  # Must be first import
from __future__ import with_statement  # Error handling for file opens

#==============================================================================
#
#       location.py - Locations file, dictionary and global fields
#
#       July 12 2023 - Interface to/from mserve_config.py
#       July 22 2023 - Create Locations() class with new sshfs support
#       July 29 2023 - Create Compare() class
#       Sep. 04 2023 - Create FNAME_SIZE_DICT under version 3.5.0
#       Sep. 10 2023 - Retrieve FTP file for diff when curlftpfs chokes on '#'
#
#==============================================================================
#import stat
#import Tkinter

"""

    To support Chrome OS:
    
       After copying locations between locations use:

           cd ~/.../mserve/L???    # Where ??? is 001, 002, etc.
           sed -i 's#/mnt/chrome/removable#/media/rick#' last_location
           sed -i 's#/mnt/chrome/removable#/media/rick#' last_selections

"""

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
from PIL import Image, ImageTk

import os
import sys
import errno
import shutil
import pickle
import time
import datetime
import netrc  # network resource password file ~/.netrc - FUTURE NOT USED YET
import ftplib  # Communicate with FTP server
import random  # For Locations() make_temp
import string  # For Locations() make_temp
from collections import OrderedDict

import global_variables as g
if g.USER is None:
    print('location.py was forced to run g.init()')
    g.init()

import sql  # SQL Locations Table for Locations()
import toolkit  # Data dictionary driven treeview for Locations()
import message  # Dialog Box messages - ShowInfo(), AskQuestion()
import monitor  # Get Locations() class window geometry
import image as img  # Taskbar thumbnail image for Locations() window
import timefmt as tmf  # "date - ago" formatting for Locations()
import external as ext  # for ext.check_command for Locations()

# Define ~/.../mserve/ directory
MSERVE_DIR = g.MSERVE_DIR
# print("MSERVE_DIR:", MSERVE_DIR)

# Files in USER_DATA_DIR/mserve/
FNAME_LOCATIONS        = MSERVE_DIR + "locations"
FNAME_LAST_LOCATION    = MSERVE_DIR + "last_location"
FNAME_LIBRARY          = MSERVE_DIR + "library.db"  # Opened every session
FNAME_LIBRARY_NEW      = MSERVE_DIR + "library_new.db"  # Rarely used

# Path modified when opened to be: USER_DATA_DIR/mserve/L999/
FNAME_LAST_OPEN_STATES = MSERVE_DIR + "last_open_states"  # Open/Closed song list
FNAME_LAST_SONG_NDX    = MSERVE_DIR + "last_song_ndx"  # Last song played in list
# May 25 2021 -  last_selections corrupted by refresh_lib_tree()
# Jun 05 2023 -  last_selections DEPRECATED
FNAME_LAST_SELECTIONS  = MSERVE_DIR + "last_selections"  # Shuffled play order of songs
FNAME_LAST_PLAYLIST    = MSERVE_DIR + "last_playlist"  # Songs selected for playing
FNAME_MOD_TIME         = MSERVE_DIR + "modification_time"  # Android phone times
# Sep 04 2023 - Create FNAME_SIZE_DICT of tuples (fake_path, file_size)
FNAME_SIZE_DICT        = MSERVE_DIR + "size_dict"  # JSON dictionary
FNAME_WALK_LIST        = MSERVE_DIR + "walk_list"  # JSON list of tuples


# Files in /tmp/
# There can be two open at once so unlike other global variables this is never
# replaced. It is simply used as base for creating new variable.
FNAME_TEST             = g.TEMP_DIR + "mserve_test"  # Test if host up
FNAME_TEST_NMAP        = g.TEMP_DIR + "mserve_test_nmap"  # Test if host up

''' Temporary files also defined in mserve.py '''
TMP_STDOUT = g.TEMP_DIR + "mserve_stdout"  # _g7gh75 appended Defined mserve.py
TMP_STDERR = g.TEMP_DIR + "mserve_stderr"  # _u4rt5m appended Defined mserve.py
TMP_FTP_RETRIEVE = g.TEMP_DIR + "mserve_ftp_retr"  # _a87sd6 appended Defined mserve.py

''' Temporary files for encoding.py '''
IPC_PICKLE_FNAME = g.TEMP_DIR + "mserve_encoding_pickle"
ENCODE_DEV_FNAME = g.TEMP_DIR + "mserve_encoding_last_disc"

''' Global variables '''
LIST = []  # List of DICT entries - DEPRECATED August 2023
DICT = {}  # Location dictionary - DEPRECATED August 2023


def create_subdirectory(iid):

    """ Always try to create '~/.../mserve/<iid>/' subdirectory """

    import os
    import errno
    directory = MSERVE_DIR + iid + os.sep

    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


LAST_LOCATION_SET = False    


def set_location_filenames(iid):
    """ Called when mserve first starts up """
    global FNAME_LAST_OPEN_STATES, FNAME_LAST_PLAYLIST, FNAME_LAST_SONG_NDX
    global FNAME_MOD_TIME, FNAME_SIZE_DICT, FNAME_WALK_LIST, LAST_LOCATION_SET

    ''' Sanity check '''
    if LAST_LOCATION_SET:
        print("location.py set_location_filenames(iid) cannot be called twice!")
        return

    ''' Sanity check '''
    if iid.lower() == 'new':
        print("location.py set_location_filenames(iid) called with location:",
              iid)
        return

    FNAME_LAST_OPEN_STATES = set_one_filename(FNAME_LAST_OPEN_STATES, iid)
    FNAME_LAST_SONG_NDX    = set_one_filename(FNAME_LAST_SONG_NDX, iid)
    FNAME_LAST_PLAYLIST    = set_one_filename(FNAME_LAST_PLAYLIST, iid)
    FNAME_MOD_TIME         = set_one_filename(FNAME_MOD_TIME, iid)
    FNAME_SIZE_DICT        = set_one_filename(FNAME_SIZE_DICT, iid)
    FNAME_WALK_LIST        = set_one_filename(FNAME_WALK_LIST, iid)

    LAST_LOCATION_SET = True


def set_one_filename(filename, iid):
    """ Build filename string """
    return filename.replace(os.sep + "mserve" + os.sep,
                            os.sep + "mserve" + os.sep + iid + os.sep)


def rename_location_filenames(iid, old):
    """ Called when forgetting a location
        Rename higher locations to fill the hole.

        NOT TESTED!

    """
    global FNAME_LAST_SELECTIONS, FNAME_LAST_OPEN_STATES
    global FNAME_LAST_PLAYLIST, FNAME_LAST_SONG_NDX

    FNAME_LAST_OPEN_STATES = rnm_one_filename(FNAME_LAST_OPEN_STATES, iid, old)
    FNAME_LAST_SONG_NDX    = rnm_one_filename(FNAME_LAST_SONG_NDX, iid, old)
    #FNAME_LAST_SELECTIONS  = rnm_one_filename(FNAME_LAST_SELECTIONS, iid, old)
    FNAME_LAST_PLAYLIST    = rnm_one_filename(FNAME_LAST_PLAYLIST, iid, old)


def rnm_one_filename(old_fname, iid, old):
    """ Build new directory name - Start using Sep 5/23 """
    #print("renaming:", old, "to:", iid)
    return old_fname.replace(os.sep + "mserve" + os.sep + old + os.sep,
                             os.sep + "mserve" + os.sep + iid + os.sep)


def read():
    """ Read list of locations in pickle format. """
    global LIST
    LIST = []
    try:
        with open(FNAME_LOCATIONS, 'rb') as filehandle:
            # read the data as binary data stream
            LIST = pickle.load(filehandle)
            filehandle.close()
            return True
    except IOError:  # [Err no 2] No such file or directory: '.../mserve/locations'
        return False

    #print('location.read() LIST count:',len(LIST))    


# Read locations if it exists
if os.path.isfile(FNAME_LOCATIONS):
    read()
    #print('MODULE LOAD LIST count:',len(LIST))    


def write():
    """ Save LIST with DICT to disk """
    with open(FNAME_LOCATIONS, "wb") as f:
        # store the data as binary data stream
        pickle.dump(LIST, f)  # Save locations list of dictionaries
        f.close()


def insert(iid="", name="", topdir="", host="", wakecmd="", testcmd="",
           testrep=10, mountcmd="", activecmd="", activemin=10, create_dir=True):
    """ Insert new location into LIST """
    if iid is "":
        next_ndx = len(LIST)
        iid = ndx_to_iid(next_ndx)

    #if name.strip():
    if name == "" or name.isspace():
        # Empty or all blank names not allowed
        print("location.insert() Error: 'name' field is blank")
        return None

    #if topdir.strip():
    if topdir == "" or topdir.isspace():
        # Empty or all blank top directory not allowed
        print("location.insert() Error: 'topdir' field is blank")
        return None

    d = {'iid': iid, 'name': name, 'topdir': topdir, 'host': host, 'wakecmd':
         wakecmd, 'testcmd': testcmd, 'testrep': testrep, 'mountcmd':
         mountcmd, 'activecmd': activecmd, 'activemin': activemin}


    # We don't want to create if temporary for random music directory parameter
    if create_dir:
        LIST.append(d)  # Add to list of location dictionaries
        # Create directory '~/.../mserve/<iid>' Where <iid> = L001, L002, etc.
        create_subdirectory(iid)
        return iid  # Newly created location iid
    else:
        return d  # Just the dictionary to use as LODICT in mserve


def iid_to_ndx(iid):
    """ Convert location index (iid) to zero based index for LIST[ndx] """
    num = iid[-3:]             # Last 3 characters of "L999" = "999"
    return int(num) - 1


def ndx_to_iid(ndx):
    """ Convert zero based index from LIST[ndx] to location index (iid)"""
    suffix = str(ndx + 1)
    return "L" + suffix.zfill(3)


def get_children():
    """ Return IDs of LIST which currently is zero-based index
        Modelled after treeview for future alphabetic IDs

        TODO: Should probably return list of all DICT?
    """
    iid_list = []
    #read()
    #print('location.get_children() LIST count:',len(LIST))
    for i, ndx in enumerate(LIST):
        iid = ndx_to_iid(i)
        iid_list.append(iid)        # treeview uses string for indices
        # print('location.get_children:',i,ndx)
    return iid_list


def remove(iid):
    """ Delete location DICT from LIST """
    global LIST                     # List of location dictionaries

    # Build directory name to remove
    forget_dir = MSERVE_DIR + iid + os.sep
    # print('forget_dir:', forget_dir)

    # Directory may never have been created for older buggy versions or
    # remote locations without access or due to permissions
    if not os.path.isdir(forget_dir):
        print("Path is not a directory:", forget_dir)
        return False

    # Try to remove tree; if failed show an error using try...except on screen
    try:
        shutil.rmtree(forget_dir)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
        return False

    # Must delete DICT in LIST after directory removed
    ndx = iid_to_ndx(iid)           # treeview style string to LIST index
    # d = LIST[ndx]  # NOT USED - Comment out July 23, 2023
    # print('deleting iid:', d['iid'], d['name'])
    del LIST[ndx]
    # Save LIST changes 'lc.write()' is done in mserve.py 'loc_submit()'
    return True


def item(iid, **kwargs):
    """ If no arguments return iid of LIST which is DICT
        Else for each argument set it's value in DICT
    """
    global DICT                     # Put results in global DICT
    ndx = iid_to_ndx(iid)           # treeview style string to LIST index
    DICT = LIST[ndx]                # Get dictionary for LIST item

    keyword_found = False
    for key, value in kwargs.items():
        # print ("%s == %s" %(key, value))
        if key in DICT:
            DICT[key] = value
            keyword_found = True
        else:
            print('location.item() invalid keyword passed:', key)

    if keyword_found is True:
        # Dec 5, 2020 - Why does this work when LIST isn't global?
        LIST[ndx] = DICT            # Update DICT entry in LIST
    else:
        return DICT                 # No keywords so return DICT


def validate_host(iid, toplevel=None):
    """ Is it a host? """
    if item(iid)['host'] is "":
        return False                # Always return False when not a host

    return test(iid, toplevel)


def get_dict_by_dirname(dirname):
    """ Look up location dictionary using top directory path

        Not bullet-proof because two location codes can use same top directory.
        One location could be SSH and other location can be FTP both to same
        server. """
    global DICT                     # mserve.py will reference as lc.DICT
    stripped_last = dirname.rstrip(os.sep)
    for i, DICT in enumerate(LIST):
        topdir = DICT['topdir'].rstrip(os.sep)
        if topdir == stripped_last:
            return True             # DICT will be matching dirname

    DICT = {}                       # No match found DICT empty
    return False


def get_dict_by_code(code):
    """ Version 3.5.0 - Look up location dictionary using location code """
    global DICT                     # mserve.py will reference as lc.DICT
    for DICT in LIST:
        print("DICT['iid']:", DICT['iid'])
        if code == DICT['iid']:     # Version 1 key name
            return True             # DICT 'iid' matches 'code' requested

    DICT = {}                       # No match found DICT empty
    return False


def check_if_host_by_dirname(dirname, toplevel=None):
    """ If this directory (strip off trailing /) matches one of our Top Dirs
        (strip off trailing /) then wake that host up and set global flag so
        parent knows to keep host awake (if necessary).

        TODO: toplevel can be None
    """
    global DICT                     # CONFIRMED must be here!

    stripped_last = dirname.rstrip(os.sep)
    found = False
    host = ""                       # Added July 7, 2021 for pycharm error
    # TODO: Option to add command line parameter for top directory to our
    #       location master file?
    for i, DICT in enumerate(LIST):
        topdir = DICT['topdir'].rstrip(os.sep)
        if topdir == stripped_last:
            host = DICT['host']
            found = True
            break

    if found is False:
        return False

    if stripped_last == topdir:
        return True  # could have done earlier but need to chop legacy code below
    ''' Should delete code below but needs to be deleted in more places... 
        Sep 5/23 - Make it so code below never runs. Need to chop everywhere.
    '''
    
    # Wake up host
    if host is "":
        print('Top Directory found but host name is blank?')
        return False

    if not test(DICT['iid'], toplevel):
        return False

    # Do we need to do more to keep host awake?
    return True


def check_if_host_by_code(code, toplevel=None):
    """ Sep 5/23 - Overkill copy & paste from 'check_if_host_by_dirname()' """
    global DICT

    stripped_last = code.strip()  # remove all white space
    found = False
    host = ""
    for i, DICT in enumerate(LIST):
        if DICT['iid'] == stripped_last:  # Sep 5/23 'iid' is legacy key for 'code'
            host = DICT['host']
            found = True
            break

    if found is False:
        return False

    if stripped_last == DICT['iid']:
        return True  # could have done earlier but need to chop legacy code below

    ''' Should delete code below but needs to be deleted in more places... 
        Sep 5/23 - Make it so code below never runs. Need to chop everywhere.
    '''
    # Wake up host
    if host is "":
        print('Top Directory found but host name is blank?')
        return False

    if not test(DICT['iid'], toplevel):
        return False

    # Do we need to do more to keep host awake?
    return True


def save_mserve_location(iid):
    """ Called by mserve in a few places """
    with open(FNAME_LAST_LOCATION, "wb") as f:
        pickle.dump(iid, f)                         # Save location ID
        f.close()


def test_host_up(host):
    """ Simply test if host if up and return True or False """
    ''' TODO: Fix error:

        "This is nc from the netcat-openbsd package. An alternative nc is 
        available in the netcat-traditional package..."
        
        Happens when restarting with new music library: /home/rick/Music
    '''
    if host.strip():
        return True if os.system("nc -z " + host + " 22 > /dev/null") \
                                 is 0 else False
    else:
        # noinspection PyProtectedMember
        print('test_host_up() received blank host name from:',
              sys._getframe(1).f_code.co_name)
        return False


def test(iid, toplevel):

    """ Validate location. In the most simple form check that local machine's
        top directory exists. In the most complicated form location is on
        remote / host and host must be woken up, partition mounted and, then
        test if top directory exists.

        This function is called by loc_open().

        This function calls md = message.Open(...) to display messages to user.

        toplevel is parent window our new window is centered in. It can be None
        when program first starts and there is no toplevel yet.
    """

    ndx = iid_to_ndx(iid)           # treeview style "L002" to LIST index "1"
    d = LIST[ndx]                # Get dictionary for LIST index

    host = d['host']
    #if host == "" or host.isspace():
    # More elegant way Doesn't work!: if host.strip()
    if not host.strip():
        # There is no host so simply check Top Directory exists
        if os.path.exists(d['topdir']):
            return True
        else:
            print("location.test() Top Directory for Music doesn't exist:",
                  d['topdir'])
            return False

    ''' We have more complicated situation where remote / host is used. '''
    # Wake up host if necessary
    wakecmd = d['wakecmd']
    testcmd = d['testcmd']
    testrep = d['testrep']
    tests = 0

    # Test if host on-line
    title = "Testing location: " + d['name'] + ".  host: " + host
    dtb = message.DelayedTextBox(title=title, toplevel=toplevel,
                                 width=1000, height=260, startup_delay=0)
    #md = message.Open(title, toplevel, 800, 260)  # 500 wide, 160 high

    # https://serverfault.com/questions/696281/ping-icmp-open-socket-operation-not-permitted-in-vserver
    # chmod u+s $( which ping );
    # print('Initial test to see if host is awake')
    dtb.update('Initial test to see if host is awake')
    host_is_awake = test_host_up(host)
    
    # Wake up host if not on-line
    #if not wakecmd == "" or not wakecmd.isspace():
    if wakecmd.strip():
        if host_is_awake is True:
            # print("Host:", host, "is already awake.")
            dtb.update("Host: " + host + " is already awake.")
        else:
            # print('waking up host:', host, 'using:', wakecmd)
            dtb.update('waking up host: ' + host + ' using: ' + wakecmd)
            os.popen(wakecmd)
            # TODO: What about error messages on 2>?

    # Test host up if not already done
    #if not testcmd == "" or not testcmd.isspace():
    if testcmd.strip():
        # Loop # of iterations checking if host is up
        if testrep < 1:
            testrep = 1
        for i in range(testrep):
            if host_is_awake is True:
                break
            time.sleep(.1)

            # We don't want error messages in our result use 2>/dev/null
            result = os.popen(testcmd + ' 2>/dev/null').read().strip()
            if len(result) > 4:
                host_is_awake = True
                tests = i
    else:
        host_is_awake = True

    if host_is_awake is False:
        test_time = int(float(testrep) * .1)
        dtb.update("location.test() Host did not come up after: " +
                   str(test_time) + " seconds.")
        dtb.close()
        return False
    else:
        #print("location.test() Host up after:", tests, "tests.")
        dtb.update("location.test() Host up after: " + str(tests) + " tests.")
    
    # Check if already mounted - Needs fine tuning
    topdir = d['topdir'].rstrip(os.sep)
    
    if topdir is "":        # What if topdir is os.sep for a USB or something?
        topdir = os.sep

    result = os.popen("mount | grep " + topdir + " ").read().strip()
    if len(result) > 4:
        #print("location.test() Top Directory for Music already mounted")
        dtb.update("location.test() Top Directory for Music already mounted")
        dtb.close()
        return True

    # Mount host directory locally with sshfs
    mountcmd = d['mountcmd']
    mounted = False
    #if not mountcmd == "" or not mountcmd.isspace():
    if mountcmd.strip():
        # We want error messages in our result
        result = os.popen(mountcmd).read().strip()
        if len(result) > 4:
            #print("location.test() errors mounting:", result)
            dtb.update("location.test() errors mounting: " + result)
        else:
            mounted = True
    else:
        mounted = True

    if mounted is False:
        #print("location.test() Host Top Directory could not be mounted with:",
        #      d['mountcmd'])
        dtb.update("location.test() Host Top Directory could not be mounted with: " + 
                   d['mountcmd'])
        return False

    # Host is up and directory mounted, see if it exists
    if os.path.exists(d['topdir']):
        dtb.close()
        return True
    else:
        #print("location.test() Top Directory for Music doesn't exist:",
        #      d['topdir'])
        dtb.update("location.test() Top Directory for Music doesn't exist: " +
                   d['topdir'])
        dtb.close()
        return False


def get_dir(parent, title, start):
    """ Get directory name. NOTE: June 6, 2023 - This function is in mserve.py already! """
    root.directory = filedialog.askdirectory(
        initialdir=start, parent=parent, title=title)
    return root.directory       # July 7, 2021 - used to be in brackets, didn't test


def ftp_login():
    """ Test FTP stuff -- Sep. 3/23 No longer used Sep 5/23
        Need Error checking on every FTP transaction:


exception ftplib.error_reply

    Exception raised when an unexpected reply is received from the server.

exception ftplib.error_temp

    Exception raised when an error code signifying a temporary error (response codes in the range 400–499) is received.

exception ftplib.error_perm

    Exception raised when an error code signifying a permanent error (response codes in the range 500–599) is received.

exception ftplib.error_proto

    Exception raised when a reply is received from the server that does not fit the response specifications of the File Transfer Protocol, i.e. begin with a digit in the range 1–5.

ftplib.all_errors

    The set of all exceptions (as a tuple) that methods of FTP instances may raise as a result of problems with the FTP connection (as opposed to programming errors made by the caller). This set includes the four exceptions listed above as well as OSError and EOFError.

    """

    ftp = ftplib.FTP()
    # ftp 2221 rick 1234  # ftp PORT USER PASSWORD
    ftp.connect('phone', 2221)
    ftp.login('rick', '1234')
    # dr-x------   3 user group            0 Aug 27 16:32 Compilations
    print("ftp.getwelcome():", ftp.getwelcome())
    # noinspection SpellCheckingInspection
    """
    ftp.sendcmd("chmod -R +W /")  # / relative to mount point "/SD Card/Music"
    #   File "/home/rick/python/location.py", line 594, in ftp_login
    #     ftp.sendcmd("chmod -R +W /")  # / relative to mount point "/SD Card/Music"
    #   File "/usr/lib/python2.7/ftplib.py", line 249, in sendcmd
    #     return self.getresp()
    #   File "/usr/lib/python2.7/ftplib.py", line 224, in getresp
    #     raise error_perm, resp
    # error_perm: 502 Command CHMOD not implemented.
    """
    ext.t_init('Transfer one file 875 bytes')
    with open("example.lrc", "rb") as fh:
        ftp.storbinary("STOR example.lrc", fh)
    job_time = ext.t_end('print')
    kbps = (875.0 / 1000.0) / job_time
    print("KB/s:", kbps)
    print(" " * 40, ext.t(time.time()))

    ext.t_init('Transfer one file 168,680 bytes')
    with open("last_selections", "rb") as fh:
        ftp.storbinary("STOR last_selections", fh)
    job_time = ext.t_end('print')
    kbps = (168680.0 / 1000.0) / job_time
    print("KB/s:", kbps)
    print(" " * 40, ext.t(time.time()))

    ext.t_init('Transfer second file 168,680 bytes')
    with open("last_playlist", "rb") as fh:
        ftp.storbinary("STOR last_playlist", fh)
    job_time = ext.t_end('print')
    kbps = (168680.0 / 1000.0) / job_time
    print("KB/s:", kbps)
    print(" " * 40, ext.t(time.time()))

    ext.t_init('Transfer 10 MB file 8,192 block size')
    with open("03 I'm Not In Love.m4a", "rb") as fh:
        ftp.storbinary("STOR 03 I'm Not In Love.m4a", fh)
    job_time = ext.t_end('print')
    kbps = (10450423.0 / 1000.0) / job_time
    print("KB/s:", kbps)
    print(" " * 40, ext.t(time.time()))

    ext.t_init('Re-transfer second file 168,680 bytes')
    with open("last_playlist", "rb") as fh:
        ftp.storbinary("STOR last_playlist", fh)
    job_time = ext.t_end('print')
    kbps = (168680.0 / 1000.0) / job_time
    print("KB/s:", kbps)
    print(" " * 40, ext.t(time.time()))

    ext.t_init('Re-Transfer 10 MB file 32,768 block size')
    with open("03 I'm Not In Love.m4a", "rb") as fh:
        ftp.storbinary("STOR 03 I'm Not In Love.m4a", fh, blocksize=32768)
    job_time = ext.t_end('print')
    kbps = (10450423.0 / 1000.0) / job_time
    print("KB/s:", kbps)
    print(" " * 40, ext.t(time.time()))

    ext.t_init('Re-Transfer 10 MB file 65,536 block size')
    with open("03 I'm Not In Love.m4a", "rb") as fh:
        ftp.storbinary("STOR 03 I'm Not In Love.m4a", fh, blocksize=65536)
    job_time = ext.t_end('print')
    kbps = (10450423.0 / 1000.0) / job_time
    print("KB/s:", kbps)
    print(" " * 40, ext.t(time.time()))

    ext.t_init('Re-Transfer 10 MB file 262,144 block size')
    with open("03 I'm Not In Love.m4a", "rb") as fh:
        ftp.storbinary("STOR 03 I'm Not In Love.m4a", fh, blocksize=262144)
    job_time = ext.t_end('print')
    kbps = (10450423.0 / 1000.0) / job_time
    print("KB/s:", kbps)
    print(" " * 40, ext.t(time.time()))

    ext.t_init('Re-Transfer 10 MB file 1,048,576 block size')
    with open("03 I'm Not In Love.m4a", "rb") as fh:
        ftp.storbinary("STOR 03 I'm Not In Love.m4a", fh, blocksize=1048576)
    job_time = ext.t_end('print')
    kbps = (10450423.0 / 1000.0) / job_time
    print("KB/s:", kbps)
    print(" " * 40, ext.t(time.time()))

    ext.t_init('Re-Transfer 10 MB file 4,194,304 block size')
    with open("03 I'm Not In Love.m4a", "rb") as fh:
        ftp.storbinary("STOR 03 I'm Not In Love.m4a", fh, blocksize=4194304)
    job_time = ext.t_end('print')
    kbps = (10450423.0 / 1000.0) / job_time
    print("KB/s:", kbps)
    print(" " * 40, ext.t(time.time()))

    ext.t_init('Re-Transfer 10 MB file 262,144 block size')
    with open("03 I'm Not In Love.m4a", "rb") as fh:
        ftp.storbinary("STOR 03 I'm Not In Love.m4a", fh, blocksize=262144)
    job_time = ext.t_end('print')
    kbps = (10450423.0 / 1000.0) / job_time
    print("KB/s:", kbps)
    print(" " * 40, ext.t(time.time()))

    ext.t_init('Re-Transfer 10 MB file 65,536 block size')
    with open("03 I'm Not In Love.m4a", "rb") as fh:
        ftp.storbinary("STOR 03 I'm Not In Love.m4a", fh, blocksize=65536)
    job_time = ext.t_end('print')
    kbps = (10450423.0 / 1000.0) / job_time
    print("KB/s:", kbps)
    print(" " * 40, ext.t(time.time()))

    ext.t_init('Transfer 10 MB file 8,192 block size')
    with open("03 I'm Not In Love.m4a", "rb") as fh:
        ftp.storbinary("STOR 03 I'm Not In Love.m4a", fh)
    job_time = ext.t_end('print')
    kbps = (10450423.0 / 1000.0) / job_time
    print("KB/s:", kbps)
    print(" " * 40, ext.t(time.time()))

    ext.t_init('Re-Transfer 10 MB file 262,144 block size')
    with open("03 I'm Not In Love.m4a", "rb") as fh:
        ftp.storbinary("STOR 03 I'm Not In Love.m4a", fh, blocksize=262144)
    job_time = ext.t_end('print')
    kbps = (10450423.0 / 1000.0) / job_time
    print("KB/s:", kbps)
    print(" " * 40, ext.t(time.time()))

    ext.t_init('Transfer 10 MB file 16,384 block size')
    with open("03 I'm Not In Love.m4a", "rb") as fh:
        ftp.storbinary("STOR 03 I'm Not In Love.m4a", fh, blocksize=16384)
    job_time = ext.t_end('print')
    kbps = (10450423.0 / 1000.0) / job_time
    print("KB/s:", kbps)
    print(" " * 40, ext.t(time.time()))

    ext.t_init('Re-Transfer 10 MB file 32,768 block size')
    with open("03 I'm Not In Love.m4a", "rb") as fh:
        ftp.storbinary("STOR 03 I'm Not In Love.m4a", fh, blocksize=32768)
    job_time = ext.t_end('print')
    kbps = (10450423.0 / 1000.0) / job_time
    print("KB/s:", kbps)
    print(" " * 40, ext.t(time.time()))

    ext.t_init('Re-Transfer 10 MB file 65,536 block size')
    with open("03 I'm Not In Love.m4a", "rb") as fh:
        ftp.storbinary("STOR 03 I'm Not In Love.m4a", fh, blocksize=65536)
    job_time = ext.t_end('print')
    kbps = (10450423.0 / 1000.0) / job_time
    print("KB/s:", kbps)
    print(" " * 40, ext.t(time.time()))

    ext.t_init('Transfer 10 MB file 8,192 block size')
    with open("03 I'm Not In Love.m4a", "rb") as fh:
        ftp.storbinary("STOR 03 I'm Not In Love.m4a", fh)
    job_time = ext.t_end('print')
    kbps = (10450423.0 / 1000.0) / job_time
    print("KB/s:", kbps)
    print(" " * 40, ext.t(time.time()))


    def walk(path, all):
        """ walk the path """
        files = []
        ftp.dir(path, files.append)  # callback = files.append(line)
        # Filename could be any position on line so can't use line[52:] below
        # dr-x------   3 user group            0 Aug 27 16:32 Compilations
        for f in files:
            line = ' '.join(f.split())  # compress multiple whitespace to one space
            parts = line.split()  # split on one space
            size = parts[4]
            # Date format is either: MMM DD hh:mm or MMM DD  YYYY or MMM DD YYYY
            date3 = parts[7] + " "  # doesn't matter if the size is same as YEAR
            # No shortcut ' '.join(parts[8:]) - name could have had double space
            name = f.split(date3)[1]
            if f.startswith("d"):  # directory?
                # Print all directories to see permissions
                print(f)
                new_path = path + name + os.sep
                walk(new_path, all)  # back down the rabbit hole
            else:
                # /path/to/filename.ext <SIZE>
                all.append(path + name + " <" + size.strip() + ">")

    all_files = []
    if True is True:
        # Quick test of root directory
        ext.t_init('quick dir on topdir')
        ftp.dir(os.sep, all_files.append)
        for line in all_files[-12:]:
            print(line)  # Print last dozen lines in root directory
        ext.t_end('print')
    else:
        # Long test of all sub-dirs and files
        ext.t_init('walk(os.sep, all_files):')
        walk(os.sep, all_files)  # 41 seconds. Nautilus is split second
        for i in range(10):
            print(all_files[i])  # Print first ten lines
        ext.t_end('print')
    print("len(all_files):", len(all_files))  # 4,074 files incl 163 + 289 subdirs
    return all_files


class ModTime:
    """ Open list of modification times
        Analyze location to see if 'touch -m -r src_path trg_path' works.
        If not utilize timestamp file to get last modification time.

        Problem when kid3 updates metadata on phone no way to see it...

    """

    def __init__(self, code, fast_refresh=None):
        self.change_cnt = 0         # Number of songs where new time changed
        self.delete_cnt = 0         # Number of songs deleted because time changed
        self.new_cnt = 0            # Number of songs added with old & new time
        self.mod_dict = {}          # Dictionary stored as pickle in mserve/L009
        ''' Using iid as code need to get topdir without modifying self.act_xxx
            Split read_location() into two parts w/ get_sql_row(Code) returns d 
        '''
        d = sql.loc_read(code)
        if d is None:
            print("location.py ModTime.__init__() invalid location code:",
                  code)
            self.allows_mtime = True  # Assume best-case scenario
            return
        self.topdir = d['TopDir']  # SQL Location Table column name
        self.filename = FNAME_MOD_TIME
        #print("Opened Location:", code, self.filename)
        parts = self.filename.split(os.sep)
        parts[-2] = code
        self.filename = os.sep.join(parts)
        #print("Massaged Location:", code, self.filename)

        # Does location support modification timestamping?
        testfile = ext.join(self.topdir, "mserve_test_time")
        for i in range(100):
            try:
                with open(testfile, "w") as text_file:
                    text_file.write("Test Modification Time")
                #print("location.py ModTime __init__(): Loop count:", i + 1)
                break  # Success
            except Exception as err:
                # IOError: [Errno 5] Input/output error: '/mnt/music/mserve_test_time'
                if i == 99:
                    print("Exception:", err)  # Host was off-line when encountered
                    print("location.py ModTime __init__(): Looped 100 times Host is off-line")
                    self.allows_mtime = False
                    return
            if fast_refresh:
                fast_refresh(tk_after=True)  # Update play_top animations
            else:
                time.sleep(.1)

        before_touch = os.stat(testfile).st_mtime
        os.popen("touch -m -t 196305180000 " + testfile)
        after_touch = os.stat(testfile).st_mtime
        try:
            os.remove(testfile)
        except Exception as err:
            print("Exception:", err)
            print("File:", testfile, "not found.")
            print("location.py ModTime __init__(): File should have existed.")

        if before_touch == after_touch:
            self.allows_mtime = False
            #print("Top dir doesn't allow timestamps:",self.topdir)
        else:
            self.allows_mtime = True
            #print("Top dir allows timestamps:",self.topdir)
            return

        # Initialize dictionary with previous modification_time file results
        #print("lc.ModTime() self.filename:", self.filename)
        if os.path.isfile(self.filename):
            with open(self.filename, 'rb') as filehandle:
                # read the data as binary data stream
                self.mod_dict = pickle.load(filehandle)

        if True is False:
            self.print(0, 10)  # Print debug stuff


    def get(self, path, mtime):
        """ Check if modification time has list entry for new time. """
        if self.allows_mtime:
            return mtime  # Nothing to do

        mtime = float(mtime)  # Ensure it's a float
        #print("NO mtime:", tmf.ago(mtime), path)
        # See if file is in our dictionary
        dict_old_time, dict_new_time = self.mod_dict.get(path, (0.0, 0.0))

        #print("dict_old_time:", tmf.ago(dict_old_time),
        #      "dict_new_time:", tmf.ago(dict_new_time))

        if dict_new_time == mtime:
            return mtime                    # Nothing has changed
        if dict_old_time == 0:
            return mtime                    # It's a new filename for our dict
        elif dict_new_time == mtime:
            print('The passed mtime matches last dict_new_time already')
            print('ModTime.get() This SHOULD NOT happen?')
            return mtime                    # 
        elif dict_new_time == dict_old_time:
            print('ModTime.get() dict_new_time == dict_old_time')
            print('This SHOULD NOT happen?')
            return mtime                    # 
        elif dict_old_time == mtime:
            ''' Expected results '''
            #print('ModTime.get() Return existing override time')
            return dict_new_time            # It's existing filename same time
        elif dict_new_time == mtime:
            print('The passed mtime matches last dict_new_time already')
            print('ModTime.get() This SHOULD NOT happen?')
            return mtime                    # 
        else:
            print('ModTime.get() Delete existing dictionary mtime:', t(mtime))
            print('path:', path)
            del self.mod_dict[path]
            self.delete_cnt += 1
            return mtime                    # It's existing filename diff time

    def update(self, path, old_mtime, new_mtime):
        """ If new modification time record it in list entry. """
        if self.allows_mtime:
            return        # Nothing to do

        dict_old_time, dict_new_time = self.mod_dict.get(path, (0, 0))
        old_mtime = float(old_mtime)
        new_mtime = float(new_mtime)
        dict_old_time = float(dict_old_time)
        dict_new_time = float(dict_new_time)
        if dict_old_time == old_mtime and dict_new_time == new_mtime:
            print('ModTime.update() no changes')
            return                          # Nothing has changed

        if dict_old_time == 0:
            # print('ModTime.update() New entry for our dictionary')
            pass
        elif not dict_new_time == new_mtime:
            # print('ModTime.update() Dictionary new time updated with new time.')
            pass
        elif dict_new_time == new_mtime:
            print('ModTime.update() Dictionary new time stayed the same')
            print('This SHOULD NOT happen?')
            return
        elif dict_old_time == new_mtime:
            print('dict_old_time same as new mtime to assign to dict_new_time.')
            print('ModTime.update() This SHOULD NOT happen?')
            return
        else:
            print('ModTime.update() Something weird happened.')

        # Add or update dict_new_time
        self.mod_dict[path] = (old_mtime, new_mtime)
        #print('ModTime.update() old_mtime:', t(old_mtime), 'new_mtime:', t(new_mtime))

    def print(self, start_i, end_i):
        """ Print dictionary elements.  Print first 11 chars of date string
            and only print last 45 characters of key to prevent line wrap.
        """
        if self.allows_mtime:
            return  # Nothing to do

        for i, (k, v) in enumerate(self.mod_dict.items()):
            if i == 0:
                print("location.py ModTime() mod_dict. start_i:",
                      start_i, "end_i:", end_i)
            if i > end_i:
                break
            if i > start_i:
                old_time, new_time = v
                old = tmf.ago(old_time)
                new = tmf.ago(new_time)
                print("old: {} | new: {} | key: {}".format(old[:11], new[:11],
                                                           k[-45:]))

    def close(self):
        """ If new modification time record it in list entry. """
        if self.allows_mtime:
            return        # Nothing to do
        with open(self.filename, "wb") as f:
            # store the data as binary data stream
            pickle.dump(self.mod_dict, f)


def t(float_time):
    """
    TODO: This is in external.py module now!

    Simple little function to return current timestamp """
    ftime = datetime.datetime.fromtimestamp(float_time)
    return ftime.strftime("%b %d %Y %H:%M:%S")


# ==============================================================================
#
#       Locations() class.  Copied from mserve.py Playlists() class
#
# ==============================================================================

class LocationsCommonSelf:
    """ Class Variables used by Locations() class """
    def __init__(self):
        """ Called on mserve.py startup and for Playlists maintenance """

        ''' Lists of all Locations - Built on program start and each maintenance '''
        self.all_codes = []  # "L001", "L002", etc... can be holes
        self.all_names = []  # Names matching all_codes
        self.all_topdir = []  # Top Directories matching all_codes
        self.loc_list = []  # Inserted into Treeview
        self.loc_dict = {}  # Single line inserted into Treeview

        ''' Current Location work fields - Mirrors SQL Location Table Row '''
        self.act_code = None  # Replacement for 'iid'
        self.act_name = None
        self.act_modify_time = None  # New
        self.act_image_path = None  # New
        self.act_mount_point = None  # New
        self.act_topdir = None
        self.act_host = None  # AKA host_name, HostName
        self.act_wakecmd = None  # Name added to pycharm spelling dictionary
        self.act_testcmd = None
        self.act_testrep = None
        self.act_mountcmd = None  # Can be sshfs, curlftpfs or FTP
        self.act_touchcmd = None  # Replaces activecmd
        self.act_touchmin = None  # Replaces activemin
        self.act_comments = None
        self.act_row_id = None  # Location SQL Primary Key
        self.act_ftp = None  # libftp.FTP() instance

        ''' fld_intro = 
            Code: L001 | Last modified: <time> | Free: 99,999 MB of 999,999 MB '''
        self.fld_intro = None  # Formatted: fld_code + fld_modify_time
        self.total_bytes = None  # Size of filesystem in bytes
        self.free_bytes = None  # Number of free bytes that ordinary users

        ''' For toggling input/read-only status of Location variables '''
        self.fld_code = None  # Replacement for 'iid'
        self.fld_name = None
        self.fld_image_path = None  # New
        self.fld_topdir = None
        self.fld_host = None  # AKA host_name, HostName
        self.fld_wakecmd = None  # Requires pycharm add to dictionary
        self.fld_testcmd = None
        self.fld_testrep = None
        self.fld_mountcmd = None
        self.fld_touchcmd = None  # Replaces activecmd
        self.fld_touchmin = None  # Replaces activemin
        self.fld_comments = None

        ''' Window tk.Entry variables '''
        self.scr_code = tk.StringVar()  # Replacement for 'iid'
        self.scr_name = tk.StringVar()
        self.scr_image_path = tk.StringVar()  # New
        self.scr_mount_point = tk.StringVar()  # New
        self.scr_topdir = tk.StringVar()
        self.scr_host = tk.StringVar()  # AKA host_name, HostName
        self.scr_wakecmd = tk.StringVar()
        self.scr_testcmd = tk.StringVar()
        self.scr_testrep = tk.IntVar()
        self.scr_mountcmd = tk.StringVar()
        self.scr_touchcmd = tk.StringVar()  # Was activecmd
        self.scr_touchmin = tk.IntVar()  # Was activemin
        self.scr_comments = tk.StringVar()  # New

        ''' Miscellaneous Location work fields '''
        self.state = None  # 'load', 'new', 'open', 'save', 'save_as', 'view'
        self.input_active = False  # Can enter Location Name & Description
        self.pending_counts = None

        ''' Input Window and fields '''
        self.main_top = None  # tk.Toplevel
        self.main_frame = None  # tk.Frame inside self.main_top
        self.btn_frame = None  # tk.Frame inside main_frame
        self.loc_view = None  # tk.Treeview managed by Data Dictionary
        self.no_locations_label = None  # When no locations are on file
        self.tree_frame = None

        self.artwork = None  # Image of hardware, E.G. Server, Laptop, Cell
        self.art_width = None
        self.art_height = 200  # Width will be calculated proportionally
        self.disp_image = None  # Image scaled to height of 200
        self.art_label = None
        self.main_close_button = None  # Close the main window
        self.main_help_button = None  # Help on the main window
        self.test_host_button = None  # Test host
        self.apply_button = None  # Apply changes to SQL Location Table Row

        ''' Test Window and fields '''
        self.called_from_main_top = None  # Was test called from main_top?
        self.test_top = None  # tk.Toplevel to Test Host from mserve.py
        self.test_frame = None  # tk.Frame holding self.test_scroll_frame & details
        self.test_scroll_frame = None  # tk.Frame holding CustomScrolledText
        self.test_box = None  # CustomScrolledText with test results
        self.test_dtb = None  # Delayed Text Box fallback when test window broken
        self.test_close_button = None  # Close the test window
        self.test_help_button = None  # Help in the test window
        self.test_host_is_mounted = True  # Assume local storage by default
        self.test_host_was_asleep = False  # Assume host wasn't asleep
        self.test_sshfs_used = False  # Assume host wasn't asleep
        self.curr_row = None  # Variable Location Detail Rows depending on ssh, etc.
        self.curr_frame = None  # Either self.main_frame or self.test_frame

        ''' Compare (Synchronize) Window and fields '''
        self.cmp_top = None  # tk.Toplevel to Test Host from mserve.py
        self.cmp_frame = None  # tk.Frame holding self.cmp_scroll_frame & details
        self.cmp_scroll_frame = None  # tk.Frame holding CustomScrolledText
        self.cmp_box = None  # CustomScrolledText with compare results
        self.cmp_dtb = None  # Delayed Text Box
        self.cmp_close_button = None  # Close the compare window
        self.cmp_help_button = None  # Help in the compare window
        self.cmp_host_is_mounted = True  # Assume local storage by default
        self.cmp_keep_awake_is_active = False  # Target has 10 minute wakeup cycle
        self.awake_last_time_check = None  # E.G. 10 minutes ago.
        self.next_active_cmd_time = None  # E.G. 10 minutes from now.
        ''' Need to keep host awake using touch command every 10 minutes.
            Source (self.open_host) and target (self.act_host) could both
            require keeping awake.  When host goes down sshfs-fuse freezes
            for 10 minutes (< 2017 version) then reports:
            IOError: [Errno 5] Input/output error: u'/mnt/music/test19630518'
        '''
        self.cmp_host_down = False  # If host goes down, have to bail immediately
        self.cmp_host_was_asleep = False  # Assume host wasn't asleep
        self.cmp_sshfs_used = False  # Assume host wasn't asleep

        ''' Compare locations variables '''
        self.cmp_top = None  # Compare Locations toplevel window
        self.cmp_top_is_active = False  # mserve.py uses False, not None
        self.cmp_target_dir = None  # OS directory comparing to
        self.cmp_tree = None  # Treeview w/difference between src and trg
        self.cmp_btn_frm = None  # Button frame for update diff / progress bar
        self.cmp_close_btn = None  # Button to close Compare Locations window
        self.update_differences_btn = None  # Click button to synchronize
        self.cmp_found = 0  # Number of files goes into differences button
        self.cmp_command_list = []  # iid,command_str,src_to_trg,src_time,trg_time
        self.cmp_return_code = 0  # Indicate how update failed
        self.src_mt = None  # Source modification time using ModTime() class
        self.src_paths_and_sizes = None  # To avoid os.stat.st_size
        self.trg_mt = None  # Target modification time using ModTime() class
        self.trg_paths_and_sizes = None  # To avoid os.stat.st_size
        self.cmp_trg_missing = []  # Source files not found in target location
        self.cmp_msg_box = None  # message.Open()
        self.last_fast_refresh = 0.0  # Calling refresh many times.
        self.start_long_running = None  # To control mserve playing buttons
        self.end_long_running = None  # To control mserve playing buttons

        ''' Make TMP names unique for multiple OS jobs running at once '''
        letters = string.ascii_lowercase + string.digits
        self.temp_suffix = (''.join(random.choice(letters) for _i in range(6)))
        self.TMP_STDOUT = TMP_STDOUT + "_" + self.temp_suffix
        self.TMP_STDERR = TMP_STDERR + "_" + self.temp_suffix
        self.TMP_FTP_RETRIEVE = TMP_FTP_RETRIEVE + "_" + self.temp_suffix


class Locations(LocationsCommonSelf):
    """ Usage:

        lcs = Locations()

        lcs loads first. Most relevant instances aren't ready to be passed.
        They are registered later with:

            lcs.register_parent(root / self.lib_top)
            lcs.register_tt(self.tt)
            lcs.register_FileControl(fc)
            lcs.register_thread(self.get_refresh_thread)
            lcs.register_info(self.info)
            lcs.register_menu(self.enable_lib_menu)
            lcs.register.fake_paths(self.fake_paths)
            lcs.register_pending(self.get_pending_cnt_total)
            lcs.register_NEW(NEW_LOCATION)
            lcs.register_oap_cb(self.open_and_play_callback)

        Major Tier 1 Methods:
    
            - view() - Show existing Locations in treeview
            - new() - Prompt for Location variables and add to database
            - open() - Pick existing Location and play music
            - edit() - Edit existing location and update database
            - delete() - Delete existing location and update database
            - synchronize() - Compare open location to target location & sync
            - test_common() - Test nmap, host wakeup, mount and topdir
            - load_last_location() - Reopen location from last mserve session

        Version 3.5.1 FTP MINOR UPGRADE PLANS:
            - Phone as host taking many minutes to read files twice on start.
            - Only need to read first few subdirectories to get 10 songs
            - Create dedicated FTP login function that stays connected until
              host response is in error. Then give chance to check phone, etc.
            - Check Host with nc / nmap as before
            - Then run command to wakeup host: "ftp user password"
            - curlftpfs command moves down to mount topdir command.

        Version 3.5.2 FTP MAJOR UPGRADE PLANS
            - Top Directory for Music becomes internal list of filenames.
            - Walk all dirs / files over 30 seconds and save for reusing.
            - On startup, 1 second to download last saved song.
            - when music is playing, separate thread runs to get previous / next
            - FTP binary get has call-back per block-size of 8,192 (the best speed)
            - During call-back call fast_refresh if > 10ms has passed.

    """

    def __init__(self, make_sorted_list):
        """
        :param make_sorted_list(): Function to verify TopDir is valid.
        """
        LocationsCommonSelf.__init__(self)  # Define self. variables

        ''' Variables registered by mserve.py when available '''
        self.make_sorted_list = make_sorted_list  # Check if music files exist
        self.parent = None  # FOR NOW self.parent MUST BE: lib_top
        self.NEW_LOCATION = None  # When it's new location nothing to open
        self.text = None  # Text replacing treeview when no locations on file
        self.get_pending = None  # What is pending in parent? - Could be favorites
        self.open_and_play_callback = None
        self.target_callback = None  # After getting target location for copy
        self.info = None  # InfoCentre() class instance initialized in mserve.py
        self.FileControl = None  # FileControl() class RAW. Needed to reset atime.
        self.enable_lib_menu = None  # Set Locations options on/off in Dropdown
        self.tt = None  # Tooltips pool for buttons
        self.get_thread_func = None  # E.G. self.get_refresh_thread()
        self.fake_paths = None  # SORTED_LIST for mserve.py open location

        ''' Opened Location SQL variables - DON'T TOUCH !!! '''
        self.open_code = None  # Replacement for 'iid'
        self.open_name = None
        self.open_modify_time = None  # New
        self.open_image_path = None  # New
        self.open_mount_point = None  # New
        self.open_topdir = None  # Can't change when opened.
        self.open_host = None  # AKA host_name, HostName
        self.open_wakecmd = None  # Name added to pycharm spelling dictionary
        self.open_testcmd = None
        self.open_testrep = None
        self.open_mountcmd = None
        self.open_touchcmd = None  # Replaces activecmd
        self.open_touchmin = None  # Replaces activemin
        self.open_comments = None
        self.open_row_id = None  # SQL Location Table Primary ID (int)
        self.open_ftp = None  # libftp.FTP() instance

        ''' Additional Open Location variables not in SQL '''
        self.host_down = False  # For emergency shutdown
        self.open_fusermount_used = False  # Using sshfs or curlftpfs

        ''' External Commands Installed? Flags '''
        self.nmap_installed = False  # Set in display_main_window()
        self.ssh_installed = False
        self.sshfs_installed = False  # includes fusermount test
        self.wakeonlan_installed = False

        ''' Miscellaneous variables not reset on 'new', 'edit', etc. '''
        self.do_tell_commands = True  # Tell about missing commands one-time

    def register_parent(self, parent):
        """ Register lib_top parent after it's declared in mserve.py """
        self.parent = parent  # Tooltips pool for buttons

    def register_NEW(self, NEW_LOCATION):
        """ Register NEW_LOCATION after it's declared in mserve.py
            When True, there is nothing to do in Locations() class. 
        """
        self.NEW_LOCATION = NEW_LOCATION  # mserve.py isn't using a location

    def register_tt(self, tt):
        """ Register Tooltips() after it's declared in mserve.py """
        self.tt = tt  # Tooltips pool for buttons

    def register_info(self, info):
        """ Register InfoCentre() after it's declared in mserve.py """
        self.info = info  # InfoCentre()

    def register_FileControl(self, fc):
        """ Register FileControl() after it's declared in mserve.py """
        self.FileControl = fc  # InfoCentre()

    def register_get_thread(self, get_thread):
        """ Register get_refresh_thread after it's declared in mserve.py """
        self.get_thread_func = get_thread  # E.G. self.get_refresh_thread()

    def register_menu(self, enable_menu_func):
        """ Register Dropdown Menu off/on after it's declared in mserve.py """
        self.enable_lib_menu = enable_menu_func  # E.G. self.enable_lib_menu()

    def register_fake_paths(self, fake_paths):
        """ Register self.fake_paths after make_sorted_list() in mserve.py """
        self.fake_paths = fake_paths  # Called in two places in mserve.py

    def register_pending(self, get_pending):
        """ Register get_pending_cnt_total after it's declared in mserve.py """
        self.get_pending = get_pending

    def register_oap_cb(self, open_and_play_callback):
        """ Register open_and_play_callback() function from mserve.py """
        self.open_and_play_callback = open_and_play_callback  # Open Loc/play music

    def register_target_cb(self, target_callback):
        """ Register target New Location to receive copied files using 
            "Tools" Dropdown Menu, "Copy Checked To New Location"
        """
        self.target_callback = target_callback  # Open Loc/play music

    # ==============================================================================
    #
    #       Locations() Processing - tkinter Window Methods
    #
    # ==============================================================================

    def display_main_window(self, name=None):
        """ Mount window with Location Treeview or placeholder text for no tree
            :param name: "New Location", "Open Location", etc.
        """
        ''' Build various lists of locations for treeview and validations '''
        self.build_locations()

        ''' Get saved geometry for Locations() '''
        self.main_top = tk.Toplevel()  # Locations top level
        self.enable_lib_menu()  # disable all Menu options for locations
        geom = monitor.get_window_geom('locations')
        self.main_top.geometry(geom)
        self.main_top.minsize(width=g.BTN_WID * 10, height=g.PANEL_HGT * 10)
        name = name if name is not None else "Locations"
        self.main_top.title(name + " - mserve")

        ''' Common Top configuration, icon and main_top master frame '''
        self.main_frame = self.make_display_frame(self.main_top)
        self.btn_frame = tk.Frame(self.main_frame)
        self.btn_frame.grid(row=14, columnspan=3, sticky=tk.E)

        ''' Instructions when no locations have been created yet. '''
        if not self.text:  # If text wasn't passed as a parameter use default
            self.text = "\nNo Locations have been created yet.\n\n" + \
                        "After Locations have been created, they will\n" + \
                        "appear in this spot.\n\n" + \
                        "You can create a location by selecting\n" + \
                        "the 'New Location' option from the 'File' \n" + \
                        "dropdown menu bar.\n"

        if len(self.all_codes) == 0:  # No locations have been created yet
            self.no_locations_label = tk.Label(self.main_frame, text=self.text, 
                                               justify="left", font=g.FONT)
            self.no_locations_label.grid(row=0, column=0, columnspan=4, 
                                         sticky=tk.W, padx=5)
        else:  # Treeview of existing locations in first frame
            self.no_locations_label = None
            self.populate_loc_tree()  # Paint treeview of locations

        ''' Shared function between display_main_window() and test_host() '''
        self.display_location_details(self.main_frame, name)
        self.input_active = False  # Screen fields are 'readonly'

        ''' Close Button - NOTE: This calls reset() function !!! '''
        self.make_main_close_button()

        ''' Help Button - https://www.pippim.com/programs/mserve.html#locations '''
        ''' ⧉ Help - Videos and explanations on pippim.com '''
        self.make_main_help_button()

        ''' Test Host Button whenever a wakeup command present '''
        if self.fld_wakecmd:  # Is wakeonlan installed?
            self.wakecmd_focusout()

        ''' Refresh screen '''
        self.main_top.update_idletasks()

        ''' Preamble messages '''
        if self.state == 'delete':
            title = "About the Delete Location function"
            text = "This does NOT delete any music files.\n\n"
            text += "It only deletes a location record.\n\n"
            text += "Only information about a location is deleted."
            self.out_fact_show(title, text, align='left')

        if self.state == 'synchronize':
            title = "About the Synchronize Location function"
            text = "This function does NOT add or delete any music files.\n\n"
            text += "It copies existing files between locations and updates files' "
            text += "modify timestamps.\n\n"
            text += "A typical music file takes about 0.1 "
            text += "second to copy locally over SSD. Copying to a \n"
            text += "cell phone over WiFi is much slower. When copying to a "
            text += "remote host that is asleep,\nthe host is woken up and "
            text += "kept awake until synchronization ends. The first time\n"
            text += "synchronization is run, it can take a long time if "
            text += "files have different dates. The\nsecond time will be "
            text += "instantaneous unless some music files were changed.\n\n"
            text += "The first time will be fast if, the music files were "
            text += "created with 'cp -a' or 'cp -p'\nto preserve timestamps.\n\n"
            text += "Music will keep playing but some buttons will be disabled. "
            self.out_fact_show(title, text, align='left')

    def make_main_close_button(self):
        """ Added by main window, removed by testing. """
        ''' Close Button - After selecting location, changes to "✘ Cancel" '''
        self.main_close_button = tk.Button(
            self.btn_frame, text="✘ Close", font=g.FONT,
            width=g.BTN_WID2 - 4, command=self.reset)
        self.main_close_button.grid(row=14, column=3, padx=(10, 5), pady=5,
                                    sticky=tk.E)
        # Columns: 0 = Apply, 1 = Test, 2 = Help, 3 = Close
        if self.tt:
            self.tt.add_tip(self.main_close_button, "Ignore changes and return.",
                            anchor="ne")
        self.main_top.bind("<Escape>", self.reset)
        self.main_top.protocol("WM_DELETE_WINDOW", self.reset)

    def make_main_help_button(self):
        """ Added by main window, removed by testing. """

        ''' Help Button - https://www.pippim.com/programs/mserve.html#locations '''
        ''' ⧉ Help - Videos and explanations on pippim.com '''

        if self.state == 'synchronize':
            help_id = "HelpSynchronizeLocation"
        else:
            help_id = "HelpLocations"
        help_text = "Open new window in default web browser for\n"
        help_text += "videos and explanations on using this screen.\n"
        help_text += "https://www.pippim.com/programs/mserve.html#\n"

        self.main_help_button = tk.Button(
            self.btn_frame, text="⧉ Help", font=g.FONT,
            width=g.BTN_WID2 - 4, command=lambda: g.web_help(help_id))
        self.main_help_button.grid(row=14, column=2, padx=10, pady=5, sticky=tk.E)
        # Columns: 0 = Apply, 1 = Test, 2 = Help, 3 = Close
        if self.tt:
            self.tt.add_tip(self.main_help_button, help_text, anchor="ne")

    def display_test_window(self):
        """ Mount test host window when not using Playlist Maintenance Window
            Called from within mserve.py
        """
        self.test_top = tk.Toplevel()  # Locations top level
        mon = monitor.Monitors()
        act_mon = mon.get_active_monitor()
        geom = "1100x750+" + str(act_mon.x + 30) + "+" + str(act_mon.y + 30)
        self.test_top.geometry(geom)
        mon.tk_center(self.test_top)  # centers on active monitor
        self.test_top.title("Test Host: " + self.act_host + " - mserve")

        ''' Common Top configuration, icon and Test Host master frame '''
        self.test_frame = self.make_display_frame(self.test_top)
        self.btn_frame = tk.Frame(self.test_frame)
        self.btn_frame.grid(row=14, columnspan=3, sticky=tk.E)

        ''' Create frame for test host scrolled text box '''
        self.make_test_box(self.test_frame)

        ''' Shared between display_main_window() and display_test_window() '''
        self.display_location_details(self.test_frame)

        ''' Put active location variables onto freshly painted window '''
        self.set_scr_variables(self.test_top)  # Tell them whose calling
        self.input_active = False  # Screen fields are 'readonly'

        ''' Close Button - calls test_close_window() to wrap up '''
        self.make_test_close_button()

        ''' Help Button - https://www.pippim.com/programs/mserve.html#
                          Optional-Remote-Host-Support '''
        self.make_test_help_button()
        self.test_top.update()

    def make_test_box(self, frame):
        """ Can be in main_top or test_top """
        ''' Create frame for test scrolled text box '''
        self.test_scroll_frame = tk.Frame(frame, bg="LightGrey", relief=tk.RIDGE)
        self.test_scroll_frame.grid(row=0, column=0, sticky=tk.NSEW, columnspan=4)
        self.test_scroll_frame.columnconfigure(0, weight=1)
        self.test_scroll_frame.rowconfigure(0, weight=1)

        ''' Custom Scrolled Text Box '''
        text = "Beginning test of Host: " + self.act_host + "\n"
        self.test_box = toolkit.CustomScrolledText(
            self.test_scroll_frame, state="normal", font=g.FONT,
            borderwidth=15, relief=tk.FLAT)
        self.test_box.configure(background="Black", foreground="Green")
        self.test_box.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)
        self.test_box.tag_config('green', foreground='Green')
        self.test_box.tag_config('yellow', foreground='Yellow')

        self.test_show(text, pattern=self.act_host)

        self.test_box.config(tabs=("10m", "20m", "40m"))
        self.test_box.tag_configure("margin", lmargin1="2m", lmargin2="40m")
        # Fix Control+C  https://stackoverflow.com/a/64938516/6929343
        self.test_box.bind("<Button-1>", lambda event: self.test_box.focus_set())

    def make_test_close_button(self):
        """ Can be called for new test_top or to replace existing main_top """
        ''' Close Button - calls test_close_window() to wrap up '''
        self.test_close_button = tk.Button(
            self.btn_frame, text="✘ Close Test Results", font=g.FONT,
            width=g.BTN_WID2 + 6, command=self.test_close_window)
        self.test_close_button.grid(row=0, column=3, padx=(10, 5), pady=5,
                                    sticky=tk.E)
        # Columns: 0 = Apply, 1 = Test, 2 = Help, 3 = Close
        if not self.called_from_main_top:  # no main_top, so escape closes test_top
            self.test_top.bind("<Escape>", self.test_close_window)
            self.test_top.protocol("WM_DELETE_WINDOW", self.test_close_window)
        if self.tt:  # During early boot toolkit.Tooltips() is still 'None'
            self.tt.add_tip(self.test_close_button, "End test of Host: " +
                            self.act_host, anchor="ne")

    def make_test_help_button(self):
        """ Can be called for new test_top or to replace existing main_top
            BUG: Aug 29/23 - when called from main_top, tooltip not found errors
                But close button tooltip works?

                Could be previous "⧉ Help" grid removed is conflict?
                Rename to ""⧉ Help Test" to debug if this is the case. YES

                This doesn't happen when a window with a close button calls
                another window with a close button? etc.

                Apparently two button with the same text on one tk.TopLevel()
                breaks tt.tooltips()?

        """
        ''' Help Button - https://www.pippim.com/programs/mserve.html#
                          Optional-Remote-Host-Support '''
        help_text = "Open new window in default web browser for\n"
        help_text += "videos and explanations on using this screen.\n"
        help_text += "https://www.pippim.com/programs/mserve.html#\n"
        self.test_help_button = tk.Button(
            self.btn_frame, text="⧉ Help Test", font=g.FONT,
            width=g.BTN_WID2, command=lambda: g.web_help("HelpTestHostStatus"))
        self.test_help_button.grid(row=0, column=2, padx=10, pady=5, sticky=tk.E)
        # Columns: 0 = Apply, 1 = Test, 2 = Help, 3 = Close
        if self.tt:  # During early boot toolkit.Tooltips() is still 'None'
            self.tt.add_tip(self.test_help_button, help_text, anchor="ne")


    @staticmethod
    def make_display_frame(top):
        """ Make display window frame for main_top and test_top """

        ''' Common top configuration '''
        top.configure(background="Gray")
        top.columnconfigure(0, weight=1)
        top.rowconfigure(0, weight=1)

        ''' Set program icon in taskbar '''
        img.taskbar_icon(top, 64, 'white', 'lightskyblue', 'black')

        ''' Create master frame '''
        frame = tk.Frame(top, borderwidth=g.BTN_BRD_WID, relief=tk.RIDGE)
        frame.grid(sticky=tk.NSEW)
        frame.columnconfigure(0, weight=0)
        frame.columnconfigure(1, weight=0)
        frame.columnconfigure(2, weight=3)  # Data entry fields
        frame.rowconfigure(0, weight=1)
        return frame
    
    def display_location_details(self, frame, mode=None):
        """ Declare location detail window fields and blank them out.
            Shared by display_main_window() method and test() method
            When mode is passed it is: 'New', 'Add', 'Open'

        :param frame: Parent container for location details.
        :param mode: Mode is 'New', 'Edit', 'Open', etc. or None for test host
        """
        ''' See which external commands are available.
            Could be done during init but that slows boot process.
            Also being done here allows user to install missing apps and
            call again without rebooting mserve.
        '''
        self.nmap_installed = ext.check_command('nmap')
        if self.nmap_installed:
            ''' Command 'nc' also required to quickly check if host is up '''
            self.nmap_installed = ext.check_command('nc')
        self.ssh_installed = ext.check_command('ssh')
        self.sshfs_installed = ext.check_command('sshfs')
        if self.sshfs_installed:
            self.sshfs_installed = ext.check_command('fusermount')
        self.wakeonlan_installed = ext.check_command('wakeonlan')

        ''' TEST: Remove comments to force screen fields off. '''
        #self.nmap_installed = False  # Test
        #self.ssh_installed = False  # Test
        #self.sshfs_installed = False  # Test
        #self.wakeonlan_installed = False  # Test

        ''' Artwork image spanning 4 rows '''
        self.make_default_image()  # Dummy Image for picture of location
        self.art_label = tk.Label(frame, borderwidth=0, image=self.disp_image)
        self.art_label.grid(row=1, rowspan=4, column=0, sticky=tk.W,
                            padx=5, pady=5)

        ''' Instructions persist until a Location's Intro Line is formatted '''
        if mode and not mode == 'New Location':
            ''' Select a location above to 'Open', 'Edit'  '''
            text = "🡅 🡅  Click on row above to " + mode + "  🡅 🡅"
        elif mode and mode == 'New Location':
            ''' For New Location, cannot select existing location  '''
            text = "🡇 🡇  Enter New Location details below  🡇 🡇"
        else:  # When mode==None, the window is for testing host.
            ''' When testing host, there are no Treeview rows above '''
            text = "🡅 🡅  Slide scrollbar above to see Test Host results  🡅 🡅"
        self.fld_intro = tk.Label(frame, text=text, font=g.FONT)
        self.fld_intro.grid(row=1, column=1, columnspan=3, pady=5, stick=tk.EW)

        ''' one_loc_var() wrapper for creating all screen input variables '''
        self.curr_row = 2  # Current row number for self.one_loc_var to incr
        self.curr_frame = frame  # Current frame for self.one_loc_var to ref
        self.fld_name = self.one_loc_var(
            "Location Name", self.scr_name, "")
        self.fld_topdir = self.one_loc_var(
            "Music Top Directory", self.scr_topdir, "")

        """ Remote Host variables will depend on the commands installed:
                self.nmap_installed = ext.check_command('nmap')  # TWO!
                self.nmap_installed = ext.check_command('nc')  # TWO TOO!
                self.ssh_installed = ext.check_command('ssh')
                self.sshfs_installed = ext.check_command('sshfs')
                self.wakeonlan_installed = ext.check_command('wakeonlan')
        """
        if self.nmap_installed:  # Includes 'nc' installed
            self.fld_host = self.one_loc_var(
                "Optional Remote Host Name", self.scr_host, "")
        if self.nmap_installed and self.wakeonlan_installed:
            self.fld_wakecmd = self.one_loc_var(
                "Command to wake up sleeping Host", self.scr_wakecmd, "")
            ''' Focus out - not trapped when testing host '''
            if mode:
                self.wakecmd_focusout()  # Set/Remove test host button
        if self.nmap_installed and self.ssh_installed:
            self.fld_testcmd = self.one_loc_var(
                "Command to test if Host is awake", self.scr_testcmd, "")
            self.fld_testrep = self.one_loc_var(
                "Maximum tests every 0.1 second", self.scr_testrep, 0)
        if self.nmap_installed and self.sshfs_installed:
            self.fld_mountcmd = self.one_loc_var(
                "Command to mount Host Music locally", self.scr_mountcmd, "")
        if self.nmap_installed and self.ssh_installed:
            self.fld_touchcmd = self.one_loc_var(
                "Command to prevent Host sleeping", self.scr_touchcmd, "")
            self.fld_touchmin = self.one_loc_var(
                "Send prevent sleep every x minutes", self.scr_touchmin, 0)

        ''' Comments appear on all windows '''
        self.fld_comments = self.one_loc_var(
            "Optional Comments", self.scr_comments, "")

        self.fld_image_path = self.one_loc_var(
            "Optional picture of Location", self.scr_image_path, "")

    def one_loc_var(self, text, scr_name, scr_value):
        """ Create single location detail screen field.
            self.curr_row starts at 2 and self.curr_frame is either
            self.main_frame or self.test_frame.  Buttons always start on
            row 14 regardless if location details end on row 8 or row 12.

        :param text: text label.  E.G. "Command to wake up sleeping Host"
        :param scr_name: scr_ variable name.  E.G. self.scr_wakecmd
        :param scr_value: scr_ clearing value.  "" for string / 0 for int
        :return self.fld_ variable name: E.G. self.fld_wakecmd """
        col = 1 if self.curr_row < 5 else 0  # Column number for text
        span = 1 if self.curr_row < 5 else 2  # Column span for text

        tk.Label(self.curr_frame, text=text, font=g.FONT).\
            grid(row=self.curr_row, column=col, columnspan=span, sticky=tk.W)
        fld = tk.Entry(self.curr_frame, textvariable=scr_name,
                       state='readonly', font=g.FONT)
        fld.grid(row=self.curr_row, column=2, columnspan=2, sticky=tk.EW,
                 padx=5, pady=5)
        scr_name.set(scr_value)  # Assign clearing value
        self.curr_row += 1  # Set for next field
        return fld

    def wakecmd_focusout(self):
        """ If scr_wakecmd field non-blank show Test button.
            Automatically called when screen field loses focus.
            Manually called when caller updates location details.

            TODO: Being called from self.test_top too!
        """
        if not self.nmap_installed or not self.wakeonlan_installed:
            return  # Can't test without commands installed

        if self.scr_wakecmd.get():
            ''' Wakeup command exists. Create 'Test Host Wakeup' button. '''
            if self.test_host_button:
                return  # Button already created
            # print("self.scr_wakecmd.get():", self.scr_wakecmd.get())
            self.test_host_button = tk.Button(
                self.btn_frame, text="🔍 Test Host Wakeup", font=g.FONT,
                width=g.BTN_WID2 + 4, command=lambda: self.test_common(self.main_top))
            self.test_host_button.grid(row=14, column=1, padx=10, pady=5, 
                                       sticky=tk.E)
            if self.tt:
                self.tt.add_tip(self.test_host_button,
                                "Test command to wake up Host.", anchor="ne")
            #self.called_from_main_top = True  # main_top calling test, no test_top
        elif self.test_host_button:
            ''' No wakeup command. Destroy button created earlier. '''
            self.tt.close(self.test_host_button)
            self.test_host_button.destroy()
            self.test_host_button = None  # Destroying doesn't set to 'None' for testing
            #self.called_from_main_top = False  # no main_top, so create test_top

    def populate_loc_tree(self):
        """ Use custom Data Dictionary routines for managing treeview. """

        ''' Data Dictionary and Treeview column names '''
        location_dict = sql.location_treeview()  # Heart of Data Dictionary
        columns = ("code", "name", "topdir")
        toolkit.select_dict_columns(columns, location_dict)

        ''' Create treeview frame with scrollbars '''
        self.tree_frame = tk.Frame(self.main_frame, bg="LightGrey", relief=tk.RIDGE)
        self.tree_frame.grid(row=0, column=0, sticky=tk.NSEW, columnspan=4)
        self.tree_frame.columnconfigure(0, weight=1)
        self.tree_frame.rowconfigure(0, weight=1)
        self.loc_view = toolkit.DictTreeview(
            location_dict, self.main_top, self.tree_frame, columns=columns,
            highlight_callback=self.highlight_callback)

        ''' Override generic column heading names for Location usage '''
        self.loc_view.tree.heading('name', text='Location Name')
        self.loc_view.tree["displaycolumns"] = columns

        ''' Treeview select item with button clicks '''
        # Moving columns needs work and probably isn't even needed
        toolkit.MoveTreeviewColumn(self.main_top, self.loc_view.tree,
                                   row_release=self.loc_button_click)
        self.loc_view.tree.bind("<Button-1>", self.loc_button_click)
        self.loc_view.tree.bind("<Button-3>", self.loc_button_click)
        #self.loc_view.tree.bind("<Double-Button-1>", self.apply)
        # Above too dangerous. Maybe for View locations OK?
        self.loc_view.tree.tag_configure('loc_sel', background='ForestGreen',
                                         foreground="White")

        ''' Loop through all location dictionaries and insert/update in tree '''
        for loc_dict in self.loc_list:
            code = loc_dict['Code']
            self.loc_view.insert("", loc_dict, code)  # Updates when in treeview

    def loc_button_click(self, event):
        """ Left button clicked to select a row.

        ''' Was region of treeview clicked a "separator"? '''
        clicked_region = self.view.tree.identify("region", event.x, event.y)
        if clicked_region == 'separator':
            # TODO adjust stored column widths
            return

        # From: https://stackoverflow.com/a/62724993/6929343
        if clicked_region == 'heading':
            column_number = self.view.tree.identify_column(event.x)  # returns '#?'
            self.display_main_window(title + ': ' + column_number,
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

        tree_code = self.loc_view.tree.identify_row(event.y)
        if not tree_code:
            return  # clicked on empty row

        if self.state == 'new':
            title = "Existing locations for reference only!"
            text = "Cannot pick existing location when a new location name " + \
                   "is required.\n\nEnter a Unique Name for the new Location."
            self.out_fact_show(title, text, 'error')
            return

        title = "Location is currently open!"
        text = None  # Dual-purpose flag if delete or open
        if tree_code == self.open_code:
            if self.state == 'open':
                text = "Cannot reopen the currently opened location."
            if self.state == 'target':
                text = "Cannot copy currently opened location to itself."
            if self.state == 'delete':
                text = "Cannot delete currently opened location."
            if self.state == 'synchronize':
                text = "Cannot compare currently opened location to itself."
            if text:  # When no text there is no error.
                return self.out_fact_show(title, text, 'error')

        ''' Highlight row clicked '''
        toolkit.tv_tag_remove_all(self.loc_view.tree, 'loc_sel')
        toolkit.tv_tag_add(self.loc_view.tree, tree_code, 'loc_sel')

        if not self.read_location(tree_code):
            print("location.py Locations.loc_button_click()",
                  "error reading location:", tree_code)
            return

        ''' Display self.scr_xxx variables '''
        self.set_scr_variables(self.main_top)
        if self.state == 'edit':
            self.enable_input()  # .new() calls this directly at very start
        self.make_apply_button()  # For everyone except "New Location"
        self.main_top.update_idletasks()

    def set_scr_variables(self, top_name):
        """ Called from self.loc_button_click() and self.display_test_window()
            top_name ignored because fields must be identical or get corrupted.
        """

        ''' Format image at 150 pix height '''
        if self.act_image_path:
            # Try to build photo image into self.disp_image variable
            try:
                self.disp_image = self.make_image_from_path(self.act_image_path)
            except tk.TclError:
                self.disp_image = None
            if not self.disp_image:
                # Could not convert file to TK photo image format
                self.make_default_image()
        else:
            # No image path use generic image
            self.make_default_image()

        if self.disp_image:
            try:
                self.art_label.configure(image=self.disp_image)
            except tk.TclError:
                print("=" * 80)
                print("self.disp_image:", self.disp_image)
                print("=" * 80)
            # Catch error;
            #   File "/home/rick/python/location.py", line 1413, in set_scr_variables
            #     self.art_label.configure(image=self.disp_image)
            #   File "/usr/lib/python2.7/lib-tk/Tkinter.py", line 1329, in configure
            #     return self._configure('configure', cnf, kw)
            #   File "/usr/lib/python2.7/lib-tk/Tkinter.py", line 1320, in _configure
            #     self.tk.call(_flatten((self._w, cmd)) + self._options(cnf))
            # TclError: invalid command name ".139778335789568.139778088451752.139778088448656"
            pass

        ''' Playlist Maintenance Window has a location introduction line '''
        if top_name == self.main_top:
            self.format_intro_line()  # Format introduction line

        ''' fields that are always present '''
        self.scr_name.set(self.act_name)
        self.scr_topdir.set(self.act_topdir)
        self.scr_comments.set(self.act_comments)
        self.scr_image_path.set(self.act_image_path)

        ''' If Test Host fields not defined, no scr_ fields exist '''
        if self.fld_host:  # nmap and nc installed?
            self.scr_host.set(self.act_host)
        if self.fld_wakecmd:  # Is wakeonlan installed?
            if "ftp_login()" in self.act_wakecmd:
                files = ftp_login()  # Just to see what it looks like
                # Returns
            self.scr_wakecmd.set(self.act_wakecmd)
            # Only main screen will turn on the Test Host button.
            if top_name == self.main_top:
                self.wakecmd_focusout()  # Display test host button when non-blank
        if self.fld_testcmd:  # Is ssh installed?
            self.scr_testcmd.set(self.act_testcmd)
            self.scr_testrep.set(self.act_testrep)
        if self.fld_mountcmd:  # Is sshfs installed?
            self.scr_mountcmd.set(self.act_mountcmd)
        if self.fld_touchcmd:  # Is ssh installed?
            self.scr_touchcmd.set(self.act_touchcmd)
            self.scr_touchmin.set(self.act_touchmin)

    def enable_input(self):
        """ Turn on input fields for 'new' and 'edit' modes. """
        self.input_active = True
        self.fld_name['state'] = 'normal'  # Allow input

        ''' Changing TopDir restricted '''
        if self.state == 'new':
            self.fld_topdir['state'] = 'normal'  # Always allow when 'new'

        ''' Clicking on scr_topdir is treated like button click '''
        self.fld_topdir.bind("<Button>", self.get_topdir)

        if self.state == 'edit' and not self.open_topdir == self.act_topdir:
            self.fld_topdir['state'] = 'normal'  # Allow input
        elif self.state == 'edit':
            title = "Location is currently open."
            text = "Changes to Music Top Directory disabled when editing " + \
                   "currently opened location.\n\nYou can start mserve with a " + \
                   "random Artist as parameter 1 if you need to change.\n\n" + \
                   "You can also 'Open and Play' a different location and then " + \
                   "'Edit' this current location."
            self.out_fact_show(title, text, 'warning')

        text = ""  # If text stays blank, then all commands are installed
        if self.fld_host:  # nmap and nc installed?
            self.fld_host['state'] = 'normal'
        else:
            text += "- 'nmap' and/or 'nc' commands were not found.\n"
        if self.fld_wakecmd:  # Is wakeonlan installed?
            self.fld_wakecmd['state'] = 'normal'
        else:
            text += "- 'wakeonlan' command was not found.\n"
        if self.fld_testcmd:  # Is ssh installed?
            self.fld_testcmd['state'] = 'normal'
            self.fld_testrep['state'] = 'normal'
        else:
            text += "- 'ssh' command was not found.\n"
        if self.fld_mountcmd:  # Is sshfs installed?
            self.fld_mountcmd['state'] = 'normal'
        else:
            text += "= 'sshfs' command was not found.\n"
        if self.fld_touchcmd:  # Is ssh installed?
            self.fld_touchcmd['state'] = 'normal'  # Replaces activecmd
            self.fld_touchmin['state'] = 'normal'  # Replaces activemin
            # No need for more text as 'ssh' is covered above in fld_testcmd
        if text and self.do_tell_commands:
            title = "Some features are hidden!"
            text = "The following command(s) not found:\n\n" + text
            text += "\nClick the 'Help' button to go to the pippim.com website."
            text += "\nYou can review what the commands do and if you need them."
            self.out_fact_show(title, text)
            self.do_tell_commands = False  # Only show msg once per session.

        self.fld_comments['state'] = 'normal'
        self.fld_image_path['state'] = 'normal'
        ''' Clicking on scr_image_path is treated like button click '''
        self.fld_image_path.bind("<Button>", self.get_act_image_path)

    def make_apply_button(self):
        """ Location just picked from treeview
            Create apply button actions of: "Add", "Save", "Delete", etc. """
        if self.state == 'view':
            return  # No button for view

        ''' Apply Buttons variable text '''
        if self.state == 'new':
            text = "Add"
        elif self.state == 'edit':
            text = "Save"
        elif self.state == 'delete':
            text = "Delete"
        elif self.state == 'synchronize':
            text = "Synchronize"
        elif self.state == 'open':
            text = "Open"
        elif self.state == 'target':
            text = "Copy To"
        else:
            toolkit.print_trace()
            text = "Missing!"

        self.apply_button = tk.Button(
            self.btn_frame, text="✔ " + text, font=g.FONT,
            width=g.BTN_WID2 - 2, command=self.apply)
        self.apply_button.grid(row=14, column=0, padx=10, pady=5, sticky=tk.E)
        # Columns: 0 = Apply, 1 = Test, 2 = Help, 3 = Close
        self.main_top.bind("<Return>", self.apply)
        self.main_close_button['text'] = "✘ Cancel"  # Change from "✘ Cancel"
        ''' toolkit.Tooltips() guaranteed to be active for Apply button '''
        # Aug 29/23 - used to be: "Synchronize Location and update records."
        self.tt.add_tip(self.apply_button, text +
                        " Location and Update.", anchor="nw")

    def format_intro_line(self):
        """ Format introduction line
            self.act_code will be blank when adding a new location 
            In this case line already repurposed with instructions. """
        if not self.act_code:
            return  # There is nothing to format
        
        # text line to build for row 1 of main_frame or test_frame
        text = "Code: " + self.act_code
        ''' Bail out early if off-line remote host '''
        if self.act_host and self.act_host != self.open_host:
            text += "  | Last modified time and free space not available."
            self.fld_intro['text'] = text
            return

        self.act_modify_time = 0.0  # Assume worse-case scenario
        self.total_bytes = 0
        self.free_bytes = 0
        # noinspection PyBroadException
        try:
            ''' Top Directory last modified time '''
            file_stat = os.stat(self.act_topdir)
            self.act_modify_time = file_stat.st_mtime
            ''' Total space and free space '''
            statvfs = os.statvfs(self.act_topdir)
            self.total_bytes = statvfs.f_frsize * statvfs.f_blocks  # Size of filesystem in bytes
            self.free_bytes = statvfs.f_frsize * statvfs.f_bavail  # Number of free bytes that ordinary users
        except:
            pass  # TODO: cast error message
        if self.act_modify_time != 0.0:
            text += "  | Last modified: "
            text += tmf.ago(self.act_modify_time)
        if self.total_bytes != 0:
            text += "  | Free: " + toolkit.human_bytes(self.free_bytes)
            text += " of: " + toolkit.human_bytes(self.total_bytes)
        self.fld_intro['text'] = text

    # noinspection PyUnusedLocal
    def get_topdir(self, *args):
        """ Get Music Top Directory name. Bound to tk.Entry field <Button>
            NOTE: filedialog.askdirectory() is a blocking function.
        """
        if not self.input_active:
            return  # Clicked on filename but input not allowed now

        new_topdir = filedialog.askdirectory(
            parent=self.main_top, initialdir=self.act_topdir,
            title="Select Music Top Directory")
        ''' New AskDirectory class under development '''
        #new_topdir = message.AskDirectory(...thread=self.get_thread_func


        if new_topdir == self.act_topdir:
            return  # No changes
        if not new_topdir:
            return  # Clicked cancel
        #if not new_topdir.endswith(os.sep):
        #    new_topdir += os.sep  # Commented out Aug 7/23

        ''' Validate Music Top Directory has Artists/Albums/Songs '''
        work_list, depth_count = self.make_sorted_list(
            new_topdir, self.main_top, check_only=True)
        print("depth_count:", depth_count)
        if depth_count[2] < 10:
            title = "Invalid Music Top Directory"
            text = "Invalid Directory: '" + new_topdir + "'\n\n"
            text += "A valid top directory would be something like 'My Music'.\n\n"
            text += "Underneath the top directory would be Artist subdirectories.\n"
            text += "Underneath each Artist would be one or more Album subdirectories.\n"
            text += "Within each Album subdirectory would be one or more music files.\n"
            text += "Up to 100 files checked and didn't find 10 music files for Albums."
            text += "\n\nMusic file search results at three levels:\n"
            text += "\n\tTop Directory: {}".format(depth_count[0])
            text += "\n\tArtist Level : {}".format(depth_count[1])
            text += "\n\tAlbum Level  : {}".format(depth_count[2])
            text += "\n\nDouble check your music directories."
            text += "\n\nIs this a new location you plan to copy files to later?"
            answer = message.AskQuestion(self.main_top, title, text, align='left',
                                         confirm='no', thread=self.get_thread_func)
            self.info.cast(title + "\n\n" + text + "\n\n\t\t" +
                           "Answer was: " + answer.result, 'info')
            if answer.result == "yes":
                self.act_topdir = new_topdir
            else:
                pass  # Keep old name
        else:
            self.act_topdir = new_topdir
        self.scr_topdir.set(self.act_topdir)

        ''' Validate Music Top Directory has modify_time '''
        # noinspection PyBroadException
        try:
            file_stat = os.stat(self.act_topdir)
            self.act_modify_time = file_stat.st_mtime
            ''' Total space and free space for ordinary users
                Doesn't work for File Server mounted at /mnt/music as
                Local storage is reported. 
            '''
            statvfs = os.statvfs(self.act_topdir)
            self.total_bytes = statvfs.f_frsize * statvfs.f_blocks  # Size of filesystem in bytes
            self.free_bytes = statvfs.f_frsize * statvfs.f_bavail  # Number of free bytes that ordinary users
        except:
            title = "os.stat FAILED !"

        ''' Format introduction line (repeats os.stat call) '''
        self.format_intro_line()  # If False should restore topdir...

    # noinspection PyUnusedLocal
    def get_act_image_path(self, *args):
        """ Get image filename. Bound to tk.Entry field <Button>
            NOTE: filedialog.askopenfilename() is a blocking function.
        """
        if not self.input_active:
            return  # Clicked on filename but input not allowed now

        try:
            ''' If file ends in .png use that as default extension 
                DOESN'T WORK. Default always first option JPG/JPEG
            '''
            ext = os.path.splitext(self.act_image_path)[1]
        except AttributeError:  # 'NoneType' object has no attribute 'rfind'
            ext = "jpg"  # Assume most popular extension?

        if ext == "jpg":
            # askopenfilename will search for first filetypes to display
            filetypes = [("JPG/JPEG", ".jpg .jpeg"), ("PNG", ".png")]
            ext = "jpg"
        else:
            # askopenfilename will search for first filetypes to display
            filetypes = [("PNG", ".png"), ("JPG/JPEG", ".jpg .jpeg")]
            ext = "png"

        ''' Assume images are stored in mserve.py program directory '''
        new_image_path = filedialog.askopenfilename(  # Blocking function !!!
            parent=self.main_top, title="Image Filename", initialdir=g.PROGRAM_DIR,
            initialfile=self.act_image_path, defaultextension=ext,
            filetypes=filetypes)

        if new_image_path == self.act_image_path:
            return  # No changes

        if not new_image_path:
            return  # Clicked cancel

        # If image invalid image, error message will be displayed
        new_photo_image = self.make_image_from_path(new_image_path)
        if new_photo_image:
            self.disp_image = new_photo_image
            self.act_image_path = new_image_path
            self.scr_image_path.set(self.act_image_path)
            self.art_label.configure(image=self.disp_image)

    def make_default_image(self):
        """ Make a default image when one isn't specified. """
        self.art_width = None
        self.art_height = 150
        image = img.make_image("Location\nPicture", image_w=150, image_h=150)
        self.disp_image = ImageTk.PhotoImage(image)

    def make_image_from_path(self, image_path):
        """ Make a image from path. Returns None for invalid filename.
            Caller should ensure image_path is NOT 'None' <type>.
        """
        self.art_width = None
        self.art_height = 150
        # noinspection PyBroadException
        try:
            image = Image.open(image_path)
            scale = 150.0 / image.height
            new_width = int(image.width * scale)
            resized_image = image.resize((new_width, 150), Image.ANTIALIAS)
            photo_image = ImageTk.PhotoImage(resized_image)
            return photo_image
        except:
            pass

        ''' Image path could be returned as tuple '''
        if isinstance(image_path, tuple):
            if len(image_path) > 0:
                image_path = str(image_path[0])
            else:
                image_path = ""  # Empty string
        title = "Invalid Image File"
        text = "Can't convert filename: '" + image_path + "'\n\n"
        text += "Only '.png' and '.jpg' files should be used.\n\n"
        text += "Image will be scaled to 150 pixels high, so\n"
        text += "larger images only waste storage space."
        self.out_fact_show(title, text, 'error')
        return False

    def highlight_callback(self, tree_code):
        """ Called as lines are highlighted in treeview.
        :param tree_code: Location number used as iid inside treeview
        :return: None """
        # Future function to instantly show location details highlighted
        pass

    def build_locations(self):
        """ Build lists of all SQL Location Table rows """
        self.all_codes = []  # "L001", "L002", etc... can be holes
        self.all_names = []  # Names matching all_codes
        self.all_topdir = []  # Descriptions matching all_codes
        self.loc_list = []  # List of dictionaries inserted into Treeview
        global LIST  # Temporary
        #LIST = []  # Temporary "   ☰ " + self.lib_top_playlist_name + " - mserve")
        #_tkinter.TclError: character U+1f3b5 is above the range (U+0000-U+FFFF) allowed by Tcl
        # SQL is unicode but old LODICT is <type str>
        ''' Read all locations from SQL Location Table into work lists '''
        for row in sql.loc_cursor.execute("SELECT * FROM Location"):
            d = dict(row)
            self.make_act_from_sql_dict(d)
            self.loc_dict = OrderedDict(d)  # Line inserted into Treeview
            self.loc_list.append(self.loc_dict)  # All lines inserted into TV
            self.all_codes.append(self.act_code)  # must match all_topdir order
            self.all_names.append(self.act_name)  # use to verify unique names
            self.all_topdir.append(self.act_topdir)  # must match all_codes order
            #LIST.append(self.make_ver1_dict_from_sql_dict(d))  # Temporary

    def get_dict_by_dirname(self, dirname):
        """ Look up location using top directory path

            Not bullet-proof because two location codes can use same top directory.
            One location could be SSH and other location can be FTP both to same
            server. """

        ''' Read backwards assuming last location added is correct one '''
        for i, topdir in reversed(list(enumerate(self.all_topdir))):
            if topdir.rstrip(os.sep) == dirname.rstrip(os.sep):
                if self.read_location(self.all_codes[i]):
                    return True
                break
                
        return False

    def out_cast_show_print(self, title, text, icon='info', align="center"):
        """ Send self.info.cast(), message.ShowInfo() and print(). """
        if self.info:
            self.info.cast(title + "\n\n" + text, icon)
        self.out_show(title, text, icon, align)
        print("\n" + title + "\n\n" + text + "\n")
        return icon == 'info'  # Return value has little importance.

    def out_cast_show(self, title, text, icon='info', align="center"):
        """ Send self.info.cast() and message.ShowInfo() with print() backup. """
        if self.info:
            self.info.cast(title + "\n\n" + text, icon)
        if not self.out_show(title, text, icon, align):
            # Give them something in console because message.ShowInfo() broken
            print("\n" + title + "\n\n" + text + "\n")
        return icon == 'info'  # Return value has little importance.

    def out_cast_print(self, title, text, icon='info'):
        """ Send self.info.cast() and print(). """
        if self.info:
            self.info.cast(title + "\n\n" + text, icon)
        print("\n" + title + "\n\n" + text + "\n")
        return icon == 'info'  # Return value has little importance.

    def out_fact_print(self, title, text, icon='info'):
        """ Send self.info.fact() and print(). """
        if self.info:
            self.info.fact(title + "\n\n" + text, icon)
        print("\n" + title + "\n\n" + text + "\n")
        return icon == 'info'  # Return value has little importance.
    
    def out_fact_show(self, title, text, icon='info', align="center"):
        """ Send self.info.fact() and message.ShowInfo() with print() backup. """
        if self.info:
            self.info.fact(title + "\n\n" + text, icon)
        if not self.out_show(title, text, icon, align):
            # Give them something in console because message.ShowInfo() broken
            print("\n" + title + "\n\n" + text + "\n")
        return icon == 'info'  # Return value has little importance.

    def out_fact(self, title, text, icon='info'):
        """ send self.info.fact() with print() backup. """
        if self.info:
            self.info.fact(title + "\n\n" + text, icon)
        else:
            # Give them something in console because self.info not defined
            print("\n" + title + "\n\n" + text + "\n")
        return icon == 'info'  # Return value has little importance.

    def out_show(self, title, text, icon='info', align="center"):
        """ Called above to save 5 lines of code. """
        if self.get_thread_func:
            top = self.out_get_parent()
            if top:
                # Aug 4/23 ShowInfo() revised to accept get_thread_func w/o ()
                message.ShowInfo(top, title, text, icon=icon, align=align,
                                 thread=self.get_thread_func)
                return True
        return False

    def out_get_parent(self):
        """ Return self.main_top, self.parent or None """
        if self.cmp_top:
            top = self.cmp_top  # Compare locations
        elif self.test_top:  # Aug 5/23 - added but not tested.
            # 'root' is used as very toplevel to self.test_top...
            top = self.test_top  # Test if Host is Awake
        elif self.main_top:
            top = self.main_top  # Locations Maintenance Window
        elif self.parent:
            top = self.parent  # mserve.py lib_top, play_top, etc.
        else:
            top = None
        return top
        
    # ==============================================================================
    #
    #       Locations() Processing - methods called from mserve.py Dropdown Menus
    #
    # ==============================================================================

    def new(self):
        """ Called by lib_top File Menubar "New Location"
            In future may be called by mainline when no location found.
            If new songs are pending, do not allow location to open
        """
        if self.get_pending:  # 'None' = MusicLocationTree not called yet.
            ''' Music Location Tree checkboxes pending to apply? '''
            if self.check_pending():  # lib_top.tree checkboxes not applied?
                return  # We are all done. No window, no processing, nada

        LocationsCommonSelf.__init__(self)  # Define self. variables
        self.state = 'new'
        self.display_main_window("New Location")
        self.enable_input()  # Allow data entry right off the bat
        self.make_apply_button()  # Set "Add" into last button

    def open(self):
        """ Called by lib_top File Menubar "Open Location and Play"

            If new songs are pending, do not allow opening new location.
            This is NOT called by main() prior to make_sorted_list().
            For that purpose load_last_location() is called. """
        if self.get_pending:  # 'None' = MusicLocationTree not called yet.
            ''' Music Location Tree checkboxes pending to apply? '''
            if self.check_pending():  # lib_top.tree checkboxes not applied?
                return  # We are all done. No window, no processing, nada

        LocationsCommonSelf.__init__(self)  # Define self. variables
        self.state = 'open'
        self.display_main_window("Open Location and Play")

    def target(self):
        """ Called by lib_top Tools Menubar "Copy Checked To Location"
            If new songs are pending, do not allow opening new location. """

        if self.get_pending:  # 'None' = MusicLocationTree not called yet.
            ''' Music Location Tree checkboxes pending to apply? '''
            if self.check_pending():  # lib_top.tree checkboxes not applied?
                return  # We are all done. No window, no processing, nada

        LocationsCommonSelf.__init__(self)  # Define self. variables
        self.state = 'target'
        self.display_main_window("Copy Checked Files To Location")

    def edit(self):
        """ Called by lib_top File Menubar "Edit Location"
            If new songs are pending, do not allow location to open """
        if self.get_pending:  # 'None' = MusicLocationTree not called yet.
            ''' Music Location Tree checkboxes pending to apply? '''
            if self.check_pending():  # lib_top.tree checkboxes not applied?
                return  # We are all done. No window, no processing, nada

        LocationsCommonSelf.__init__(self)  # Define self. variables
        self.state = 'edit'
        self.display_main_window("Edit Location")

    def delete(self):
        """ Called by lib_top Edit Menubar 'Delete Location' """
        LocationsCommonSelf.__init__(self)  # Define self. variables
        self.state = 'delete'
        self.display_main_window("Delete Location")

    def synchronize(self, start_long_running, end_long_running):
        """ Called by lib_top Edit Menubar 'Synchronize Location'
        Click Synchronize Button:
            Warning message appears that it is remote host, but nothing happens
            Run Test Host which wakes up successfully
        Then Click Synchronize Button again:
            Test is run a second time when it should have been run first time
            Now locks up because:
                # File "/home/rick/python/location.py", line 3151, in apply
                #     self.cmp_build_toplevel(sbar_width=14)
                # File "/home/rick/python/location.py", line 3207, in cmp_build_toplevel
                #     self.cmp_keep_awake()
                # File "/home/rick/python/location.py", line 3346, in cmp_keep_awake
                #     test_passed = self.test_host_up()  # Quick & dirty nc test
                # File "/home/rick/python/location.py", line 2517, in test_host_up
                #     toolkit.print_trace()
                # File "/home/rick/python/toolkit.py", line 87, in print_trace
                #     for line in traceback.format_stack():
                # location.py Locations() test_host_up() blank host name. cmp_keep_awake
                # Remote Host Disconnected!
                # Dell Inspiron 17R SE 7720 File Server is off-line. Shutting down... 
        """
        LocationsCommonSelf.__init__(self)  # Define self. variables
        self.state = 'synchronize'
        self.start_long_running = start_long_running
        self.end_long_running = end_long_running
        self.display_main_window("Synchronize Location")

    def view(self):
        """ Called by lib_top View Menubar 'View Locations' """
        LocationsCommonSelf.__init__(self)  # Define self. variables
        self.state = 'view'
        self.display_main_window("View Locations")

    def close(self):
        """ Originally designed to be called by mserve shutdown.
            However, shutdown calls self.reset().

            When Location Maintenance window closes self.reset() is also used. 

            As of July 27, 2023 this function is not used. The last location
            is saved when "Open Location and Play" opens a new location. The
            last location is also saved by mserve.py save_last_selections().
            Also when Music Directory passed in parameter 1 and 
            lc.get_dict_by_dirname(music_dir) returns True.
 
        """

        self.state = 'close'
        sql.save_config('location', 'last', self.open_code, self.open_name,
                        self.open_topdir, Comments="Last location opened.")
        if self.cmp_keep_awake_is_active:  # Keeping remote host awake?
            self.cmp_keep_awake_is_active = False  # Has 10 minute wakeup cycle
        if self.cmp_top_is_active:
            self.cmp_close()  # Close Compare Locations window
            

    # ==============================================================================
    #
    #       Locations() Processing - SQL Database Access
    #
    # ==============================================================================


    @staticmethod
    def build_fake_locations():
        """  TEMPORARY DURING CONVERSION
        Use existing LIST to create fake SQL Location Table rows """
        for i, d in enumerate(LIST):
            ImagePath = None  # Make pycharm happy :)
            if i == 0:
                ImagePath = "Motorola Moto E4 Plus.png"
            if i == 1:
                # noinspection SpellCheckingInspection
                ImagePath = "Dell Inspiron 17R SE 7720.jpg"
            if i == 2:
                ImagePath = "Dell Alienware AW17R3.png"
            if i == 3:
                ImagePath = "Sandisk 128GB.png"
            sql.loc_add(
                d['iid'], d['name'], time.time(), ImagePath, 'MountPoint',
                d['topdir'], d['host'], d['wakecmd'], d['testcmd'], d['testrep'],
                d['mountcmd'], d['activecmd'], d['activemin'], u"Comments")

    def get_dict_by_dirname(self, dirname):
        """ Look up location dictionary using top directory path
            Called by mserve.py when it was started using parameter 1 to
            specify top directory. In this case look up to see if it's a
            location already defined.
        """
        stripped_last = dirname.rstrip(os.sep)
        for i, topdir in enumerate(self.all_topdir):
            if topdir == stripped_last:
                return self.read_location(self.all_codes[i])

        dir_dict = {}  # No match found DICT empty
        return dir_dict

    def read_location(self, code):
        """ Use location code to read SQL Location Row into work fields """
        d = sql.loc_read(code)
        if d is None:
            return None  # Sep 11/23 s/b False but need to test everywhere first

        ''' Current Location work fields - from SQL Location Table Row '''
        self.make_act_from_sql_dict(d)

        return True

    def add_location(self):
        """ Save Location when 'Add' button applied. """
        sql.loc_add(
            self.act_code, self.act_name, self.act_modify_time, self.act_image_path,
            self.act_mount_point, self.act_topdir, self.act_host, self.act_wakecmd,
            self.act_testcmd, self.act_testrep, self.act_mountcmd,
            self.act_touchcmd, self.act_touchmin, self.act_comments)

        ''' Create subdirectory .../mserve/L009 '''
        directory = MSERVE_DIR + self.act_code + os.sep
        try:
            os.makedirs(directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def save_mserve_location(self, Code):
        """ Called by mserve in a four places. TODO: Check to enhance. """
        if not self.read_location(Code):
            title = "Programming Error!"
            text = "location.py Locations.save_mserve_location() -" + \
                   "Error reading location: " + Code
            self.out_cast_show_print(title, text, 'error')
            return
        
        sql.save_config('location', 'last', self.act_code, self.act_name,
                        self.act_topdir, Comments="Last location opened.")

    def save_touch_time(self, compare=False):
        """ Called by mserve to keep track of last touch time.
            Uses self.open_xxx variables !
        """
        if compare:
            sql.save_config('location', 'last', self.act_code, self.act_name,
                            self.act_topdir, Comments="Last location opened.")
        else:
            sql.save_config('location', 'last', self.open_code, self.open_name,
                            self.open_topdir, Comments="Last location opened.")

    def save_location(self):
        """ Save Location when 'Save' button applied. """
        sql.loc_update(
            self.act_code, self.act_name, self.act_modify_time, self.act_image_path,
            self.act_mount_point, self.act_topdir, self.act_host, self.act_wakecmd,
            self.act_testcmd, self.act_testrep, self.act_mountcmd,
            self.act_touchcmd, self.act_touchmin, self.act_comments, self.act_row_id)

    def delete_location(self):
        """ Delete Location  when 'Delete' button applied. """
        sql.loc_cursor.execute("DELETE FROM Location WHERE Id=?", [self.act_row_id])
        sql.con.commit()  # con.commit() must follow cursor.execute()

    def make_act_from_empty_dict(self):
        """ July 27, 2023 - Currently only used when mserve calls lcs.new(). """
        self.act_code = ""  # Replacement for 'iid'
        self.act_name = ""
        self.act_modify_time = 0.0
        self.act_image_path = ""
        self.act_mount_point = ""  # July 27, 2023 - Plan to use for remote host?
        self.act_topdir = ""
        self.act_host = ""
        self.act_wakecmd = ""
        self.act_testcmd = ""
        self.act_testrep = 0
        self.act_mountcmd = ""
        self.act_touchcmd = ""
        self.act_touchmin = 0
        self.act_comments = ""

    def make_act_from_sql_dict(self, d):
        """ Make 'Active' location fields from SQL Location Table Row """
        self.act_code = d['Code']  # Replacement for 'iid'
        self.act_name = d['Name']
        self.act_modify_time = d['ModifyTime']
        self.act_image_path = d['ImagePath']
        self.act_mount_point = d['MountPoint']
        self.act_topdir = d['TopDir']
        self.act_host = d['HostName']
        self.act_wakecmd = d['HostWakeupCmd']
        self.act_testcmd = d['HostTestCmd']
        self.act_testrep = d['HostTestRepeat']
        self.act_mountcmd = d['HostMountCmd']
        self.act_touchcmd = d['HostTouchCmd']
        self.act_touchmin = d['HostTouchMinutes']
        self.act_comments = d['Comments']
        self.act_row_id = d['Id']  # Location SQL Primary Key

    def make_open_from_sql_dict(self, d):
        """ Make 'Open' location fields from SQL Location Table Row """
        self.open_code = d['Code']  # Replacement for 'iid'
        self.open_name = d['Name']
        self.open_modify_time = d['ModifyTime']
        self.open_image_path = d['ImagePath']
        self.open_mount_point = d['MountPoint']
        self.open_topdir = d['TopDir']
        self.open_host = d['HostName']
        self.open_wakecmd = d['HostWakeupCmd']
        self.open_testcmd = d['HostTestCmd']
        self.open_testrep = d['HostTestRepeat']
        self.open_mountcmd = d['HostMountCmd']
        self.open_touchcmd = d['HostTouchCmd']
        self.open_touchmin = d['HostTouchMinutes']
        self.open_comments = d['Comments']
        self.open_row_id = d['Id']  # Location SQL Primary Key

    @staticmethod
    def code_to_ndx(code):
        """ Convert 'L001' to 1, 'L002' to 2, etc. """
        return int(code[1:]) - 1

    @staticmethod
    def ndx_to_code(ndx):
        """ Convert 1 to 'L001', 2 to 'L002', etc. """
        return "L" + str(ndx + 1).zfill(3)
    
    @staticmethod
    def make_ver1_dict_from_sql_dict(d):
        """ Make version 1 dictionary from SQL Location Table Row """
        v = OrderedDict()
        v['iid'] = d['Code']  # Replacement for 'iid'
        v['name'] = d['Name']
        v['topdir'] = d['TopDir']
        v['host'] = d['HostName']
        v['wakecmd'] = d['HostWakeupCmd']
        v['testcmd'] = d['HostTestCmd']
        v['testrep'] = d['HostTestRepeat']
        v['mountcmd'] = d['HostMountCmd']
        v['activecmd'] = d['HostTouchCmd']
        v['activemin'] = d['HostTouchMinutes']
        return v
    
    def check_pending(self):
        """ When lib_top_tree has check boxes for adding/deleting songs that
        haven't been saved, cannot open location or create new location.

        :return: True if pending additions/deletions need to be applied
        """
        pending = self.get_pending()
        if pending == 0:
            return False

        # self.main_top window hasn't been created so use self.parent instead
        title = "Playlist has not been saved!"
        text = "Checkboxes in Music Location Tree have added songs or\n" + \
               "removed songs. These changes have not been saved to\n" + \
               "storage or cancelled.\n\n" + \
               "You must save changes or cancel before working with a\n" + \
               "different location."
        self.out_cast_show(title, text, 'error')

        return True  # We are all done. No window, no processing, nada

    # new_xxx fields only exist for fld_xxx and pycharm things might be undef
    # noinspection PyUnboundLocalVariable
    def validate_location(self):
        """ Validate Location's self.scr_xxx input data entry.
            Called when apply() invoked.
        """
        if not self.state == 'new' and not self.state == 'edit':
            return True  # Only 'edit' or 'new' validate input fields.

        ''' Retrieve name and description from tkinter scr_ variables. '''
        new_name = self.scr_name.get().strip()
        if new_name.endswith(os.sep):
            new_name = new_name[:-1]  # Directory picker appends slash at end
            self.scr_name.set(new_name)
        new_topdir = self.scr_topdir.get().strip()
        ''' Retrieve optional remote host from tkinter scr_ variables. '''
        if self.fld_host:  # nmap and nc installed?
            new_host = self.scr_host.get().strip()
        if self.fld_wakecmd:  # wakeonlan installed?
            new_wakecmd = self.scr_wakecmd.get().strip()
        if self.fld_testcmd:  # Is ssh installed?
            new_testcmd = self.scr_testcmd.get().strip()
            try:
                new_testrep = self.scr_testrep.get()
            except ValueError:
                new_testrep = 0  # A blank was entered
        if self.fld_mountcmd:  # Is sshfs installed?
            new_mountcmd = self.scr_mountcmd.get().strip()
        if self.fld_touchcmd:  # Is ssh installed?
            new_touchcmd = self.scr_touchcmd.get().strip()
            try:
                new_touchmin = self.scr_touchmin.get()
            except ValueError:
                new_touchmin = 0  # A blank was entered
        ''' Other "regular" tkinter scr_ variables. '''
        new_comments = self.scr_comments.get().strip()
        if self.fld_image_path:  # Doesn't exist on test window
            new_image_path = self.act_image_path

        if self.state == 'new':
            self.make_act_from_empty_dict()

        ''' We need a location name no matter the operation performed '''
        if not new_name:
            title = "Location Name cannot be blank!"
            text = "Enter a unique name for the location."
            return self.out_fact_show(title, text, 'error')

        ''' A location music top directory always required '''
        if not new_topdir:
            title = "Music Top Directory required!"
            text = "Select a Music Top Directory.\n"
            text += "If network location, ensure it is active first."
            return self.out_fact_show(title, text, 'error')

        ''' Same name cannot exist in this location '''
        if new_name in self.all_names and \
                new_name != self.act_name:
            title = "Name must be unique!"
            text = "Location name has already been used."
            return self.out_fact_show(title, text, 'error')

        ''' -o debug causes lockup '''
        if self.fld_mountcmd:  # Is sshfs installed?
            # noinspection SpellCheckingInspection
            bad_apple = "-odebug"
            if bad_apple in new_mountcmd:
                title = bad_apple + " not allowed!"
                text = bad_apple + " option hijacks processing and causes mserve to freeze."
                return self.out_fact_show(title, text, 'error')

        ''' Creating a new location? Use next available location code '''
        if self.state == 'new':
            if len(self.all_codes) > 0:
                last_str = self.all_codes[-1]  # Grab last number
                val = int(last_str[1:]) + 1  # increment to next available
                self.act_code = "L" + str(val).zfill(3)
            else:
                self.act_code = "L001"  # Very first location

        ''' All validation tests passed. Setup to add new location / save old '''
        self.act_name = new_name
        self.act_topdir = new_topdir
        if self.fld_host:  # nmap and nc installed?
            self.act_host = new_host
        if self.fld_wakecmd:  # wakeonlan installed?
            self.act_wakecmd = new_wakecmd
        if self.fld_testcmd:  # Is ssh installed?
            self.act_testcmd = new_testcmd
            self.act_testrep = new_testrep
        if self.fld_mountcmd:  # Is sshfs installed?
            self.act_mountcmd = new_mountcmd
        if self.fld_touchcmd:  # Is ssh installed?
            self.act_touchcmd = new_touchcmd
            self.act_touchmin = new_touchmin
        self.act_comments = new_comments
        if self.fld_image_path:
            # No image on test screen
            self.act_image_path = new_image_path

        return True  # All tests passed, self.act_xxx ready for saving

    def load_last_location(self, toplevel=None):
        """ Called by mserve.py open_files(). """
        #print(ext.t(time.time()), "load_last_location()")
        self.state = 'load'

        ''' Retrieve SQL History for last location used. '''
        hd = sql.get_config('location', 'last')
        if hd is None:
            print("The last location in SQL History Table wasn't found:",
                  "Type='location', Action='last")
            self.NEW_LOCATION = True
            return 1

        ''' Retrieve SQL Location Table last location used. '''
        d = sql.loc_read(hd['SourceMaster'])
        if d is None:
            print("The last location used for mserve.py has been deleted:",
                  hd['SourceMaster'])
            self.NEW_LOCATION = True
            return 2

        ''' Initialize working variables '''
        self.make_act_from_sql_dict(d)  # self.act_ used for testing host
        self.make_open_from_sql_dict(d)  # self.open_ changed only on load

        global DICT  # Be glad when this old code is gone !!!
        DICT = self.make_ver1_dict_from_sql_dict(d)
        set_location_filenames(self.act_code)  # Call global function at top

        # Display keep awake values
        #if self.open_touchcmd:
        #    print('Touch command:', self.open_touchcmd,
        #          'every', self.open_touchmin, 'minutes.')

        ''' If host used, wake it up and validate topdir '''
        if self.validate_host(toplevel=toplevel):
            # Sep 5/23 - Need to get self.act_ftp variable from host tests into
            self.open_ftp = self.act_ftp
            return 0  # else not a host or host won't wake up

        ''' Check if last used location's music top directory has subdirs '''
        if os.path.exists(self.open_topdir) and len(os.listdir(self.open_topdir)):
            return 0

        print('Location contains invalid or off-line directory:', 
              self.open_topdir)
        return 3

    # ==============================================================================
    #
    #       Locations() Processing - Remote Host validations
    #
    # ==============================================================================

    # no inspection of out_fact_print(text) for debugging    
    # noinspection PyUnusedLocal 
    def validate_host(self, toplevel=None):
        """ Check current self.act_host variable to see if it a host 
            Called my mserve.py call to self.load_last_location()
            Always use self.open_xxx and never self.act_xxx fields which
            can be changed in Maintenance.

            TODO:
                - Sign into host
                - Run simple command and test results 

            DEBUG -------------------------------------------------------------

            HOST (Open a terminal enter command to run forever):
                mserve_client.sh -d

            CLIENT (Copy to terminal and replace "<HOST>" with Host name):
                while : ; do ssh <HOST> "cat /tmp/mserve_client.log" ; sleep 60 ; done

        """
        #print("location.py Locations.validate_host(toplevel):", toplevel)
        title = "location.py Locations.validate_host()"
        d = sql.get_config('location', 'last')
        if d['SourceMaster'] == self.open_code:
            last_time = d['Time']
        else:
            last_time = 0.0

        ''' If 10 minutes is touch frequency as 12.5 minutes is safe cutoff '''
        cutoff_time = last_time + self.open_touchmin * 60 * 1.25
        start = time.time()
        #self.out_cast_show_print(title, "STARTUP: " + ext.t(start), 'info')

        if self.open_host and cutoff_time >= start:
            ''' Avoid 6.5 second 'nmap' test and use .003 second 'nc' test'''
            text = "Using 'nc'. cutoff_time >= start. Seconds: "
            text += '{0:.1f}'.format(cutoff_time - start)
            #self.out_cast_show_print(title, text, 'info')
            self.test_init(toplevel, True)  # Open window and maybe keep open
            ''' 'nc' takes split second when host connected but many seconds
                when host disconnected. Use display_test_window and immediately
                remove it. 

                    $ time nc -z dell 22  # 0.003s - Host Up
                    $ time nc -z dell 22  # 24.601s - Host down for 1 minute
                    $ time nc -z dell 22  # 6.137s - Suspend client and resume
            '''
            result = os.system("nc -z " + self.open_host + " 22 > /dev/null")
            # Wait for command to end. It takes 0.003 seconds when the host
            # is up. A once connected host, that disconnects, takes 37 seconds.
            if result == 0:
                # Testing Window is still open !
                text = "HOST is CONNECTED"
                #self.out_fact_print(title, text, 'info')
                ''' TODO: Make mounting separate method'''
                if self.open_mountcmd:
                    ''' Always unmounted when mserve closes. Mount quickly '''
                    text = "Mounting with: " + self.open_mountcmd
                    #self.out_fact_print(title, text, 'info')
                    result = os.system(self.open_mountcmd)
                    if result == 0:
                        text = "Mount SUCCESS!"
                        #self.out_fact_print(title, text, 'info')
                        self.open_fusermount_used = True
                        if os.path.exists(self.open_topdir) and \
                                len(os.listdir(self.open_topdir)):
                            #text = "FAST STARTUP... Artist count: ",
                            #text += str(len(os.listdir(self.open_topdir)))
                            # TypeError: can only concatenate tuple (not "str") to tuple
                            count = len(os.listdir(self.open_topdir))
                            text = "FAST STARTUP... Artist count: " + str(count)
                            #self.out_fact_print(title, text, 'info')
                            self.test_close_window()  # Old design was to leave it open sometimes
                            return True
                        else:
                            ''' No subdirs under TopDir. Do full test '''
                            text = "No subdirs under TopDir! Fallback"
                            self.out_fact_print(title, text, 'error')
                            self.sshfs_close()  # unmount for full test
                            # Keep window up and don't run nmap
                            return self.test_common(toplevel, run_nmap=False)
                    else:
                        # fusermount: failed to access mount point /mnt/music: Permission denied
                        text = "Mount FAILED! Fallback. result=" + str(result)
                        self.out_fact_print(title, text, 'error')
                        # Keep window up and don't run nmap
                        return self.test_common(toplevel, run_nmap=False)
                elif os.path.exists(self.open_topdir) and \
                        len(os.listdir(self.open_topdir)):
                    ''' No mount required, permanent host path of some sort. '''
                    text = "No mount required and TopDir is good"
                    #self.out_fact_print(title, text, 'info')
                    self.test_close_window()
                    return False  # This actually means a good thing :)
                else:
                    text = "No mount required but TopDir is empty"
                    self.out_fact_print(title, text, 'error')
                    self.test_close_window()
                    return self.test_common(toplevel)
            else:
                ''' 'nc' didn't find host '''
                text = "'nc' Didn't find host SECONDS: "
                text += '{0:.1f}'.format(time.time() - start)
                self.out_fact_print(title, text, 'warning')
                self.test_close_window()
                return self.test_common(toplevel)
        elif self.open_host:  # Remote Host past 12 minute cut-off time
            ''' Avoid 37 second 'nc' test and use 6.5 second 'nmap' test
                Note if resuming from suspend, the 37 second delay disappears
                and back to regular a few second delay. Needs to be timed. 
            '''
            text = "Skipping 'nc' now - cutoff_time: "
            text += '{0:.1f}'.format(time.time() - cutoff_time)
            self.out_fact(title, text, 'warning')  # Early boot still prints
            return self.test_common(toplevel)
        else:
            ''' Return False when not a host and parent will test for topdir '''
            return False  #

    def test_host_up(self, host=None):
        """ Simply test if host is up and return True or False
            Only called from mserve.py to check if connection still up.
            Always use self.open_xxx and never self.act_xxx fields which
            can be changed in Maintenance.

            When called from Synchronize Location host=self.act_host
        """
        if not host:
            host = self.open_host  # Cannot use in parameters. gets init error
        if host:
            ''' nc returns 0 if host is on-line '''
            #print(ext.t(time.time()), "test_host_up()")
            result = os.system("nc -z " + host + " 22 > /dev/null")
            # Above waits for command to end 0.003 seconds when host up
            # If a long suspend and host went down its a few seconds.
            # A once good host suddenly disconnected takes 37 seconds
            # Since music has been paused 10+ minutes user will not see this
            return result == 0

        else:
            # Determine function name from within that function
            # http://farmdev.com/src/secrets/framehack/index.html
            toolkit.print_trace()
            # noinspection PyProtectedMember
            print('location.py Locations() test_host_up() blank host name.',
                  sys._getframe(1).f_code.co_name)
            return False

    def test_common(self, toplevel, run_nmap=True, called_from_sync=False):
        """ Validate Host Connect. 

            In simple form, check that local machine's top directory exists. 

            In complicated form, a remote host is woken up, the a remote partition
            is mounted locally and finally, test if top directory exists.

            Called by mserve.py -> lcs.load_last_location() -> lcs.validate_host()

            Also called by mserve.py: open_and_play_callback(self, code, topdir)

            Called internally from self.main_top -> self.test_host_button.

        :param toplevel: 'toplevel' can be 'main_top' used for test.
            'toplevel' can be 'root', then new window is created.
        :param run_nmap: If 'nc' was used for quick test, no need to run 'nmap'.
            Also display_test_window() was already done.
        :param called_from_sync: True if synchronize() is caller. """

        ''' Simple method to set self.called_from_main_top '''
        self.called_from_main_top = toplevel == self.main_top
        #print("simple self.called_from_main_top:", self.called_from_main_top)

        ''' Perform fastest test for mserve.py open_and_play_callback() '''
        if not self.called_from_main_top and not self.act_host:
            if os.path.exists(self.act_topdir) and \
                    len(os.listdir(self.act_topdir)) > 0:
                self.test_host_is_mounted = True
                if self.act_mountcmd:
                    self.open_fusermount_used = True  # better than nothing...
                return True  # Probably not even a host.

        # noinspection SpellCheckingInspection, Pep8CodingStyleViolationW605
        ''' extraordinary notes on sshfs not mounting on Android 10

Mobile Phone Host

Try three USB cables and the third will allow data transfer

USB option doesn't say it's charger only setting

Click and select File Transfer

A new volume will show up in Nautilus left pane

Use Nautilus to copy your music files from local storage to your phone

See mount points. First is CD, second is the phone:

``` bash
/run/user/1000/gvfs$ ll
total 0
dr-x------  4 rick rick   0 Aug 19 22:30 ./
drwx------ 12 rick rick 800 Aug 27 17:05 ../
drwx------  1 rick rick   0 Dec 31  1969 cdda:host=sr0/
dr-x------  1 rick rick   0 Dec 31  1969 mtp:host=%5Busb%3A001%2C009%5D/
```

Install Banana Studio SSH/SFTP on port 2222. Optionally setup user.

Create local mount point: /mnt/phone

Change local directory pointing to phone:

``` bash
rick@alien:/run/user/1000/gvfs/mtp:host=%5Busb%3A001%2C009%5D$ cdd
────────────────────────────────────────────────────────────────────────────────────────────
rick@alien:/run/user/1000/gvfs/mtp:host=%5Busb%3A001%2C009%5D/SD card$ cdd
────────────────────────────────────────────────────────────────────────────────────────────
rick@alien:/run/user/1000/gvfs/mtp:host=%5Busb%3A001%2C009%5D/SD card/Music$ 
```

Log into your router: 
https://www.highspeedinternet.com/resources/how-to-log-in-to-your-router

Assign static IP address:
https://business.shaw.ca/support/business-router-settings-dhcp-reservation

Q&A: https://askubuntu.com/a/1179873/307523

Debug SSHFS error "Connection reset by peer" add -oedebug option:

Use guest account with no password for testing


Look at Banana SSH/SFTP Users screen for ssh where both internal and external
are assigned to use directory name you can't list:

``` bash
 2|:/storage/emulated/0 $ cd /storage/4A21-0000/

:/storage/4A21-0000 $ ls
Alarms  DCIM     Movies Notifications Podcasts  
Android Download Music  Pictures      Ringtones 

1|:/storage/4A21-0000 $ ls Music   
10cc             My Chemical Romance
3 Doors Down     Nancy Sinatra                   
   (... SNIP ...)
Mr. Scruff      last_song_ndx       
  
:/storage/4A21-0000 $ cd Music
:/storage/4A21-0000/Music $ 

# Next line keeps connection alive

:/storage/4A21-0000/Music $ while : ; do ls last_song_ndx ; sleep 60 ; done
last_song_ndx
        
```

sshfs is broken connecting to phone running SSH/SFTP server:

``` bash

LATEST ATTEMPT password is 1234:

$ echo 1234 | sshfs -odebug,sshfs_debug,loglevel=debug -o password_stdin -p 2222 
rick@phone:/storage/4A21-0000/Music /mnt/phone
SSHFS version 2.5
FUSE library version: 2.9.4
nullpath_ok: 0
nopath: 0
utime_omit_ok: 0
executing <ssh> <-x> <-a> <-oClearAllForwardings=yes> <-ologlevel=debug> 
<-oPort=2222> <-oNumberOfPasswordPrompts=1> <-2> <rick@phone> <-s> <sftp>
debug1: Reading configuration data /etc/ssh/ssh_config
debug1: /etc/ssh/ssh_config line 19: Applying options for *
debug1: Connecting to phone [192.168.0.11] port 2222.
debug1: Connection established.
debug1: identity file /home/rick/.ssh/id_rsa type 1
debug1: key_load_public: No such file or directory
debug1: identity file /home/rick/.ssh/id_rsa-cert type -1
debug1: key_load_public: No such file or directory
debug1: identity file /home/rick/.ssh/id_dsa type -1
debug1: key_load_public: No such file or directory
debug1: identity file /home/rick/.ssh/id_dsa-cert type -1
debug1: key_load_public: No such file or directory
debug1: identity file /home/rick/.ssh/id_ecdsa type -1
debug1: key_load_public: No such file or directory
debug1: identity file /home/rick/.ssh/id_ecdsa-cert type -1
debug1: key_load_public: No such file or directory
debug1: identity file /home/rick/.ssh/id_ed25519 type -1
debug1: key_load_public: No such file or directory
debug1: identity file /home/rick/.ssh/id_ed25519-cert type -1
debug1: Enabling compatibility mode for protocol 2.0
debug1: Local version string SSH-2.0-OpenSSH_7.2p2 Ubuntu-4ubuntu2.10
debug1: Remote protocol version 2.0, remote software version SSH Server - Banana Studio
debug1: no match: SSH Server - Banana Studio
debug1: Authenticating to phone:2222 as 'rick'
debug1: SSH2_MSG_KEXINIT sent
debug1: SSH2_MSG_KEXINIT received
debug1: kex: algorithm: ecdh-sha2-nistp256
debug1: kex: host key algorithm: ssh-rsa
debug1: kex: server->client cipher: aes128-ctr MAC: hmac-sha2-256 compression: none
debug1: kex: client->server cipher: aes128-ctr MAC: hmac-sha2-256 compression: none
debug1: sending SSH2_MSG_KEX_ECDH_INIT
debug1: expecting SSH2_MSG_KEX_ECDH_REPLY
debug1: Server host key: ssh-rsa SHA256:3mNL574rJyHCOGm1e7Upx4NHXMg/YnJJzq+jXhdQQxI
debug1: Host '[phone]:2222' is known and matches the RSA host key.
debug1: Found key in /home/rick/.ssh/known_hosts:6
debug1: rekey after 4294967296 blocks
debug1: SSH2_MSG_NEWKEYS sent
debug1: expecting SSH2_MSG_NEWKEYS
debug1: SSH2_MSG_NEWKEYS received
debug1: rekey after 4294967296 blocks
debug1: SSH2_MSG_SERVICE_ACCEPT received
debug1: Authentications that can continue: password,keyboard-interactive
debug1: Next authentication method: keyboard-interactive
Password authentication
debug1: Authentication succeeded (keyboard-interactive).
Authenticated to phone ([192.168.0.11]:2222).
debug1: channel 0: new [client-session]
debug1: Entering interactive session.
debug1: pledge: network
debug1: Sending environment.
debug1: Sending env LANG = en_CA.UTF-8
debug1: Sending subsystem: sftp
Server version: 3
debug1: client_input_channel_req: channel 0 rtype exit-status reply 0
debug1: channel 0: free: client-session, nchannels 1
debug1: fd 0 clearing O_NONBLOCK
Transferred: sent 1960, received 1752 bytes, in 0.1 seconds
Bytes per second: sent 15449.5, received 13810.0
debug1: Exit status 0
remote host has disconnected

Extra insurance Ubuntu Firewall allow port 2222, Use:

``` bash
sudo ufw allow 2222
```

sshfs was discontinued in 2022. NFS is an option:
https://android.stackexchange.com/questions/200867/how-to-mount-nfs-on-android-with-correct-permissions




# Install Google Play Medha Wifi FTP Server

Port defaults to 2221

``` bash
sudo ufw allow 2221
```

Mount directory:

    curlftpfs -o user=android:android phone:2221 /mnt/phone  (OWNED BY ROOT)
    curlftpfs -o uid=1000,gid=1000,umask=0022,user=android:android phone:2221 /mnt/phone


See: https://github.com/JackSlateur/curlftpfs/blob/master/README

Start sync at 10:44 pm finish 12:13am (90 minutes)

    All files have wrong timestamp so diff takes 1 second for every song.

    Some interesting error messages:
    
# diff: /mnt/phone//Arcade Fire/Funeral/01 Neighborhood #1 (Tunnels).m4a: Permission denied
# diff: /mnt/phone//Arcade Fire/Funeral/02 Neighborhood #2 (Laika).m4a: Permission denied
# diff: /mnt/phone//Arcade Fire/Funeral/04 Neighborhood #3 (Power Out).m4a: Permission denied
# diff: /mnt/phone//Arcade Fire/Funeral/05 Neighborhood #4 (7 Kettles).m4a: Permission denied
# diff: /mnt/phone//Bachman-Turner Overdrive/The Definitive Collection/13 Lookin' Out For #1.m4a: Permission denied
        
From: https://github.com/JackSlateur/curlftpfs/blob/master/README

Note
========

This is _not_ the official project, which can be found there:
http://curlftpfs.sourceforge.net/
I just added some code the correctly handle filename which contains
url-special chars (actually, just # and %) by url-encoding them :
 % -> %25
 # -> %23
Using that, curl will not translate them, and will target the correct
filename.

        
        '''

        ''' If using Test Button, validate_location() sets self.act_xxx vars '''
        if self.called_from_main_top and not self.validate_location():
            return False  # Called from main_top and error given to user to fix

        ''' Long running process - Turn off some play_top buttons '''
        #self.start_long_running()

        ''' If nmap requested and called from test mount the display. '''
        display_test = run_nmap and not self.called_from_main_top
        #print("test_common() calling test_init(display_test):", display_test)
        '''
        ERROR:
            display_test is true called from view() main_top after synchronize run
            display_test is false called from view() main_top normally
            display_test is false called from synchronize() test host
            display_test is false called from synchronize() synchronize button
        '''
        self.test_init(toplevel, display_test)  # Open delayed text box

        if run_nmap:
            host_is_up, host_is_awake = self.test_nmap(toplevel)
        else:
            ''' Host is up because 'nc' tested already '''
            host_is_up = host_is_awake = True

        ''' Wake up host if not on-line '''
        if self.act_wakecmd:  # Is there a command to wakeup host?
            if host_is_awake:  # Is host already awake?
                # nmap leaves extra blank line already
                text = "Host: " + self.act_host + " is already awake. "
                text += "Skipping Host wakeup command:\n\t" + self.act_wakecmd
                self.test_show(text, pattern="Skipping Host wakeup")
                pass
            else:
                ''' Host is sleeping '''
                if host_is_up:
                    # nmap leaves extra blank line already
                    text = 'Host: ' + self.act_host
                    text += ' can be accessed but is NOT awake.'
                    self.test_show(text, pattern='NOT awake')

                text = '\nWaking up host: ' + self.act_host + ' using:\n\t '
                text += self.act_wakecmd
                self.test_show(text, pattern=self.act_wakecmd)

                ''' Launch wakeup command (don't use '&& sleep 4' anymore). '''
                if self.act_wakecmd.startswith("wakeonlan"):
                    os.popen(self.act_wakecmd)
                else:
                    self.act_ftp = ftplib.FTP()
                    if not self.test_ftp_login(self.act_ftp, self.act_host,
                                               self.act_wakecmd):
                        return self.test_failure()

        ''' Keep testing host until it is awake '''
        host_is_awake = False
        if self.act_testcmd:
            if os.path.exists(FNAME_TEST):
                os.remove(FNAME_TEST)
            cmd1 = ext.shell_quote(self.act_testcmd)
            if "#" in cmd1:  # Remove any comments from command to append redirects
                cmd1 = cmd1.split('#')[0]
            cmd = cmd1 + " > " + FNAME_TEST + " 2>&1 &"

            def repeated_test():
                """ Repeated test before and at bottom of loop
                :return: Nothing
                """
                if self.act_ftp:
                    print("Test host awake with ftplib.FPT() instance")
                    welcome = self.act_ftp.getwelcome()
                    if welcome.startswith("220 "):
                        f_list = ["FTP Success", welcome, ""]
                        ext.write_from_list(FNAME_TEST, f_list)
                else:
                    print("Test host awake with cmd:", cmd)
                    os.popen(cmd)  # Launch background command to list files to temp file
            full_text = "\nRunning test to see if Host awake:\n\t" + cmd + "\n"
            self.test_show(full_text, pattern=cmd1)

            text = "Waiting for '" + FNAME_TEST + "' output results to appear.\n"
            self.test_show(text, pattern=FNAME_TEST)

            testrep = self.act_testrep
            if testrep < 1:
                text = "testrep is < 1: " + str(testrep)
                self.test_show(text, pattern=testrep)
                testrep = 300  # Override negative or zero to 30 seconds
            start = time.time()
            self.test_show("Dummy Line to replace 2")
            for i in range(testrep):
                # .1 second wait
                self.test_refresh(toplevel, i + 1, testrep, start,
                                  "test if Host awake")
                # noinspection PyBroadException
                try:
                    # Read results from command, must be > 2 characters
                    strings = ext.read_into_list(FNAME_TEST)
                    if len(strings) > 2:
                        self.test_show("\tHost Response first line:\t" + strings[0],
                                       pattern=strings[0])
                        self.test_show("\tResponse last line " + "[" +
                                       str(len(strings)) + "]:\t" + strings[-1],
                                       pattern=strings[-1])
                        host_is_awake = True
                        text = "\tHost communicating after: " + str(i + 1) + " tests."
                        self.test_show(text, pattern="Host communicating")
                        break
                except:
                    pass
                repeated_test()  # Inner function defined before loop

            if not host_is_awake:
                test_time = int(float(self.act_testrep) * .1)
                text = "Host did not come up after: " + \
                       str(test_time) + " seconds."
                self.test_show(text, pattern=str(test_time))
                return self.test_failure()
        else:
            ''' Host has no keep awake command, assume test passed. '''
            text = "\nCan't check if Host is awake. Test command NOT provided!"
            self.test_show(text, pattern="Test command NOT provided!")

        ''' Check if Top Directory already mounted '''
        text = '\nChecking for Music Top Directory:\n\t' + self.act_topdir
        self.test_show(text, pattern=self.act_topdir)
        if self.test_topdir():
            text = "\nTop Directory for Music already mounted"
            self.test_show(text, pattern="already mounted")
            if not self.called_from_main_top:
                self.test_host_is_mounted = True  # Still mounted after prev wakeup?
                if self.act_mountcmd:
                    self.open_fusermount_used = True
                else:
                    self.open_fusermount_used = False
            if self.act_ftp:
                self.test_ftp_walk(self.act_ftp)
            return self.test_success(called_from_sync)

        ''' sshfs host's music top directory to local mount point '''
        mountcmd = self.act_mountcmd.strip()
        self.test_host_is_mounted = False  # Assume host isn't mounted
        if mountcmd:  # Need Non-blank mount command to run
            text = '\nMounting: ' + self.act_topdir + \
                   ' using:\n\t' + self.act_mountcmd + "\n"
            self.test_show(text, pattern=self.act_mountcmd)
            # noinspection SpellCheckingInspection
            ''' Advice about fuse error '''
            text = "NOTE: 'sshfs' and 'curlftpfs' can stall and cause mserve to freeze.\n" + \
                   "If so, you can test by listing files on mount point.\n\n" + \
                   "The following commands might help:\n" + \
                   "    $ fusermount -u " + self.act_topdir + "\n" + \
                   "    $ sudo umount -l " + self.act_topdir + "\n"
            if self.act_mountcmd.startswith("sshfs") or \
                    self.act_mountcmd.startswith("curlftpfs"):
                self.test_show(text, pattern='NOTE:')
            # We want error messages in our result
            result = os.popen(mountcmd).read().strip()
            text = "\nMount command result: " + result
            self.test_show(text, pattern=result)
            if "Connection reset" in result:
                text = "\nError mounting Top Directory: " + result
                self.test_show(text, pattern=result)
            else:
                self.test_host_is_mounted = True
        else:
            text = "\nSkipping Host mount. Mount command NOT provided!"
            self.test_show(text, pattern="Mount command NOT provided!")
            self.test_host_is_mounted = True  # When no mountcmd assume mounted

        if self.test_host_is_mounted is False:
            text = "\nHost's Music Top Directory could not be mounted with:"
            text += "\n\t" + self.act_mountcmd
            self.test_show(text, pattern=self.act_mountcmd)
            return self.test_failure()

        text = '\nTest if Music Top Directory exists with files:\n\t' + \
               self.act_topdir
        self.test_show(text, pattern=self.act_topdir)

        ''' Host is up and directory mounted. Check if TopDir has subdirs '''
        if os.path.exists(self.act_topdir) and \
                len(os.listdir(self.act_topdir)) > 0:
            if self.act_ftp:
                self.test_ftp_walk(self.act_ftp)
            return self.test_success(called_from_sync)  # Finally we're good to go!
        else:
            if os.path.exists(self.act_topdir):
                text = "Music Top Directory exists, but it is empty:"
                pattern = "is empty"
            else:
                text = "Music Top Directory doesn't exist:"
                pattern = "doesn't exist"
            text += "\n\t" + self.act_topdir
            self.test_show(text, pattern=pattern)
            return self.test_failure()

    def test_init(self, toplevel, display_test):
        """ Initialize variables for Testing Host """

        ''' if 'nc' previously run test window already up.
            if self.test_called_from_main = True then using main_top variables. 
        '''
        if toplevel == self.main_top:
            if display_test:
                print("location.py test_init(): display_test is True!!!")
        elif not display_test:
            print("location.py test_init(): display_test is False!!!")

        if display_test:
            ''' Careful here... Check call chain before revisions... '''
            #print(ext.t(time.time()), "mounting display_test_window")
            self.display_test_window()
            toplevel.update()
            self.set_scr_variables(self.test_top)
            self.test_top.update()

        if self.called_from_main_top:
            ''' Called from main_top using 'Test Host' or 'Synchronize' button '''
            if self.no_locations_label:
                self.no_locations_label.grid_remove()
            else:
                self.tree_frame.grid_remove()
            self.main_close_button.grid_remove()
            self.main_help_button.grid_remove()
            self.test_host_button.grid_remove()
            if self.apply_button:
                self.apply_button.grid_remove()
            #self.main_top.update()
            ''' test box will replace treeview '''
            self.make_test_box(self.main_frame)  # Replaces treeview
            ''' new buttons replace grid_remove '''
            self.make_test_close_button()
            self.make_test_help_button()
            self.main_top.update()

        text = 'Initial test to see if host: ' + self.act_host + ' is connected.'
        title = "Test Host: " + self.act_host + " - mserve"
        self.test_show(text, pattern=self.act_host)
        self.test_dtb = message.DelayedTextBox(
            title=title, toplevel=toplevel, width=1000, height=260, startup_delay=0)

    def test_close_window(self):
        """ Close Test Host Window """
        if self.called_from_main_top:  # main_top exists, so test_top not needed
            ''' Remove test window overrides and restore original main window '''
            if self.tt:
                # Buttons can disappear when synchronize location cancelled
                if self.tt.check(self.test_close_button):
                    self.tt.close(self.test_close_button)
                if self.tt.check(self.test_help_button):
                    self.tt.close(self.test_help_button)
            self.test_close_button.destroy()
            self.test_help_button.destroy()
            self.test_scroll_frame.destroy()
            self.test_close_button = None
            self.test_help_button = None
            self.test_scroll_frame = None

            if self.no_locations_label:
                self.no_locations_label.grid()  # Empty treeview instructions
            else:
                self.tree_frame.grid()  # Restore treeview of locations
            self.main_close_button.grid()
            self.main_help_button.grid()
            self.test_host_button.grid()
            if self.apply_button:  # If apply button exists, restore it
                self.apply_button.grid()
            self.main_top.update()
        else:
            self.test_top.destroy()  # What about tooltips? - There are none
            self.test_top = None  # Destroying doesn't set to 'None'

    def test_nmap(self, toplevel):
        """ Run the nmap command when 'nc' command has not been run. """
        ''' nmap returns results in lumps '''
        if os.path.exists(FNAME_TEST_NMAP):
            os.remove(FNAME_TEST_NMAP)
        cmd = "nmap -Pn " + self.act_host + " 2>&1 > " + FNAME_TEST_NMAP + " &"
        os.popen(cmd)
        text = "\nUsing 'nmap' (Network Mapper) to test if: "
        text += self.act_host + " is connected."
        self.test_show(text, pattern="(Network Mapper)")
        self.test_show("Command: " + cmd, pattern="nmap -Pn " + self.act_host)

        text = "\nWaiting for 'nmap' output results to appear in: "
        text += FNAME_TEST_NMAP + "\n"
        self.test_show(text, pattern="'nmap'")
        limit = 300  # 30 second time limit. dell takes 6.5 seconds
        text = ""
        start = time.time()
        self.test_show("Dummy Line to replace")
        for i in range(limit):
            self.test_refresh(toplevel, i + 1, limit, start,
                              "'nmap' results shown below")
            # noinspection PyBroadException
            try:
                text = ext.read_into_string(FNAME_TEST_NMAP)
            except:
                continue  # File hasn't appeared yet
            if "Nmap done:" in text:
                break

        ''' Check nmap results '''
        host_is_up = "(1 host up)" in text
        host_is_awake = "22/tcp open" in text  # what if more spaces? Use re
        self.test_host_was_asleep = not host_is_awake  # Can do this better...
        if limit == 0:
            self.test_show("\n'nmap' FAILED! 10 second timeout exceeded.",
                           pattern="'nmap' FAILED!")
        else:
            self.test_show(text, pattern="(1 host up)")

        return host_is_up, host_is_awake

    def test_ftp_login(self, ftp, host, ftp_string):
        """ Connect and log into FTP Host """
        # ftp 2221 rick 1234  # ftp PORT USER PASSWORD
        parts = ftp_string.split()
        passed = True
        if len(parts) < 4:
            passed = False
        elif parts[0] != "ftp":
            passed = False
        try:
            port = int(parts[1])
        except ValueError:
            passed = False

        if not passed:
            title = "Location Information Error"
            text = "The field: 'Command to wake up sleeping Host',\n"
            text += "contains: " + ftp_string
            text += "\n\nFour parts, separated by a space, are required:\n\n"
            text += "\tftp  \t- The letters: ftp (without quotes)\n"
            text += "\tPort \t- The numeric port number\n"
            text += "\tUser ID  - The user ID/name the host expects\n"
            text += "\tPassword - Password for user the host expects "
            self.out_cast_show_print(title, text, 'error', align='left')
            return False
        #print("parts:", parts)
        # PORT: Convert u"2221" to int 2221
        try:
            ftp.connect(host, int(parts[1]))  # TODO: split into test_ftp_connect
            ftp.login(parts[2], parts[3])  # TODO: return error codes
        except Exception as err:
            print("Exception:", err)
            title = "Login Error"
            text = "Could not log into Remote Host.\n"
            text += "\nHost name:\t " + host
            text += "\nUsing port:\t" + parts[1]
            text += "\nUser name: \t" + parts[2]
            text += "\nPassword: \t" + parts[3]
            text += "\n\nFTP returned error message:\n\n"
            text += str(err)
            text += "\n\nEnsure FTP Server is running and enabling logins."
            self.out_cast_show_print(title, text, 'error', align='left')
            return False
        return True

    def test_ftp_walk(self, ftp, show=True):
        """ Walk FTP directories
            TODO: Simply read fake_paths_size
        """

        ''' Build fake_paths_size filename (FNAME) using open location) '''
        size_name = rnm_one_filename(FNAME_SIZE_DICT, self.act_code, self.open_code)
        walk_name = rnm_one_filename(FNAME_WALK_LIST, self.act_code, self.open_code)
        if os.path.isfile(size_name) and os.path.isfile(walk_name):
            return True  # Save time and reuse last session. Tree will rebuild slow

        def walk(topdir, path, all, walks):
            """ walk the path """
            files = []
            dirs = []
            base_names = []
            if topdir.endswith(os.sep):
                u_topdir = topdir.rsplit(os.sep, 1)[0]
            else:
                u_topdir = topdir
            u_topdir = toolkit.uni_str(u_topdir).encode('utf-8')
            u_path = toolkit.uni_str(path)
            ftp.dir(u_path, files.append)  # callback = files.append(line)
            # Filename could be any position on line so can't use line[52:] below
            # dr-x------   3 user group            0 Aug 27 16:32 Compilations
            for f in files:
                lin = ' '.join(f.split())  # compress multiple whitespace to one space
                parts = lin.split()  # split on one space
                size = parts[4]
                # Date format is either: MMM DD hh:mm or MMM DD  YYYY or MMM DD YYYY
                date3 = parts[7] + " "  # doesn't matter if the size is same as YEAR
                # No shortcut ' '.join(parts[8:]) - name could have had double space
                name = f.split(date3)[1]
                if f.startswith("d"):  # directory?
                    # Print all directories to see permissions
                    self.test_show(f)  # self. doesn't work inside inner func.
                    self.fast_refresh()  # Update animations
                    new_path = path + name + os.sep
                    dirs.append(name.encode('utf-8'))
                    walk(topdir, new_path, all, walks)  # back down the rabbit hole
                else:
                    # /path/to/filename.ext <SIZE>
                    u_name = toolkit.uni_str(name)
                    base_names.append(u_name.encode('utf-8'))
                    int_size = int(size.strip())
                    u_size = u'{:n}'.format(int_size)
                    entry = u_path + u_name + u" < " + u_size + u" > "
                    #all.append(entry.encode('utf-8'))  # no more list, now dict
                    full_path = u_path + u_name
                    all[u_topdir + full_path.encode('utf-8')] = int_size
                    if show:
                        self.test_show(entry.encode('utf-8'))
            #walk_tuple = tuple((u_path.encode('utf-8'), dirs, base_names))
            #walks.append(walk_tuple)
            if u_path.endswith(os.sep):
                u_path = u_path.rsplit(os.sep, 1)[0]
            walks.append((u_topdir + u_path.encode('utf-8'), dirs, base_names))

        all_files = {}
        all_walks = []
        # Long test of all sub-dirs and files
        ext.t_init('walk(os.sep, all_files)')
        print("self.act_topdir:", self.act_topdir)
        walk(self.act_topdir, os.sep, all_files, all_walks)  # 41 seconds. Nautilus is split second
        success = ext.write_from_json(size_name, all_files)
        if not success:
            print("ext.write_from_json(FNAME_SIZE_DICT, all_files)... FAILED")
        else:
            print("FILE SAVED:", size_name)
        all_walks.sort()  # Sep 6/23 previously "/Compilations" was first in list
        success = ext.write_from_json(walk_name, all_walks)
        if not success:
            print("ext.write_from_json(FNAME_WALK_LIST, all_files)... FAILED")
        else:
            print("FILE SAVED:", walk_name)
        for i, line in enumerate(all_walks):
            if i < 3:  # Print first 3
                print(i, "MAKE Walk:", all_walks[i])
            if i > len(all_walks) - 4:  # Print last 3
                print(i, "MAKE Walk:", all_walks[i])

        walk_time = ext.t_end('print')
        text = "\nFTP Walk completed in: " + tmf.mm_ss(walk_time) + " seconds."
        text += "\nFake paths and sizes saved to: " + size_name
        text += "\nos.walk(dir, topdown) list to: " + walk_name
        self.test_show(text, pattern=FNAME_SIZE_DICT)
        #self.test_show("\nFTP Walk completed in: " +
        #               tmf.mm_ss(walk_time) + " seconds.")
        print("len(all_files):", len(all_files))  # 4,074 files incl 452 subdirs
        return

    def test_show(self, text, pattern=None):
        """ Insert into self.test_box (scrolled text box) and print to console.
            Also use dtb (delayed text box), however by design not all lines will
            appear there. dtb serves as GUI backup when test_window doesn't appear.

            last_insert is used by test_refresh to replace previous line.
        :param text: Text line for self.test_box. "\n" appended
        :return: Nothing
        """
        #last_insert = self.test_box.tag_ranges("last_insert")
        #print("last_insert:", last_insert)
        self.test_box.tag_remove("last_insert", "1.0", "end")
        #if last_insert:
        #    self.test_box.delete(last_insert[0], last_insert[1])
        self.test_box.insert("end", text + "\n", "last_insert")
        last_insert = self.test_box.tag_ranges("last_insert")
        if pattern:
            self.test_box.highlight_pattern(pattern, 'yellow', start=last_insert[0])
        self.test_box.see("end")
        self.test_scroll_frame.update_idletasks()
        #self.test_dtb.update(text)  # DTB too busy now that Test Window works

    def test_refresh(self, top, step, steps, start, text):
        """ Refresh last test_box line with .1 second updates
            Credit: https://stackoverflow.com/a/53639572/6929343 """
        now = time.time()
        try:
            last_insert = self.test_box.tag_ranges("last_insert")
        except tk.TclError:
            last_insert = ("end", "end")
        self.test_box.delete(last_insert[0], last_insert[1])
        self.test_box.tag_remove("last_insert", "1.0", "end")
        secs = '{0:.1f}'.format(now - start)
        full_text = str(step) + " of: " + str(steps) + " steps. "
        full_text += "Waited: " + secs + " seconds for: " + text + "."
        self.test_box.insert("end", full_text + "\n", "last_insert")
        self.test_box.highlight_pattern(text, 'yellow')
        self.test_box.see("end")
        self.test_scroll_frame.update_idletasks()
        if self.get_thread_func:  # Update animations & poll tooltips
            thread = self.get_thread_func()
            thread()
        elapsed = time.time() - now  # Sleep .1 seconds between tests
        sleep = int((.1 - elapsed) * 1000)  # fractional to milliseconds
        sleep = 1 if sleep < 1 else sleep
        top.after(sleep)

    def test_topdir(self):
        """ Short test if topdir is visible """
        return os.path.exists(self.act_topdir) and \
            len(os.listdir(self.act_topdir)) > 0

    def test_success(self, called_from_sync):
        """ End test with success """
        success = "\nHost successfully accessed. Click 'Close Test Results' button."
        self.test_show(success, pattern="'Close Test Results'")
        self.test_dtb.close()
        if not self.called_from_main_top:
            ''' This is a live situation. Set self.open_xxx '''
            if self.test_host_is_mounted and self.open_mountcmd:
                self.open_fusermount_used = True
            else:
                self.open_fusermount_used = False
            self.test_close_window()  # main_top allows reviewing results

        if self.called_from_main_top and called_from_sync:
            self.test_close_window()  # synchronize in progres
            self.test_host_button.grid_remove()
            if self.apply_button:
                self.apply_button.grid_remove()

        ''' Long running process - Restore play_top buttons '''
        #self.end_long_running()

        return True

    def test_failure(self):
        """ End test with Failure """
        failure = "\nHost FAILURE. Review and then click 'Close' button."
        self.test_show(failure, pattern="FAILURE")
        self.test_dtb.close()

        ''' Long running process - Restore play_top buttons '''
        #self.end_long_running()

        # Leave test window open
        return False

    # ==============================================================================
    #
    #       Locations() Processing - Wrapup
    #
    # ==============================================================================

    def sshfs_close(self):
        # noinspection SpellCheckingInspection
        """ When exiting need to unmount sshfs music directories. Also when
            test_host_up() fails with 'nc' test this must be done. Finally,
            this must be run during mserve.py self.open_and_play_callback().

            After the "Test Host" button finishes this needs to be run,
            unless self.act_host = self.open_host.

            It might be tempting to run command all the time:
                $ time fusermount -u Temp
                fusermount: entry for /home/rick/Temp not found in /etc/mtab
                real	0m0.003s

            When mserve.py is running, look inside '/etc/mtab':
                $ cat /etc/mtab | grep music
                dell:/mnt/music/Users/Person/Music/iTunes/iTunes\040Media/Music/
                /mnt/music fuse.sshfs rw,nosuid,nodev,relatime,user_id=1000,group_id=1000 0 0

            From: https://help.ubuntu.com/community/SSHFS
            (add to command help module mserve_config.py)
                Your ssh session will automatically log out if it is idle.
                To keep the connection active (alive) add this to
                ~/.ssh/config or to /etc/ssh/ssh_config on the client.

        """
        if self.open_fusermount_used and not self.open_topdir:
            title = "Programming Error."
            text = "location.py Locations.sshfs_close() called with no topdir."
            self.out_cast_show_print(title, text, 'error')

        if self.open_fusermount_used:
            cmd = "fusermount -u " + self.open_topdir
            os.popen(cmd)
            title = "Locations.sshfs_close() called at: " + ext.t(time.time())
            text = "Running: " + cmd
            self.out_fact_print(title, text, 'warning')
            self.open_fusermount_used = False

    def reset(self, shutdown=False):
        """ Named "reset" because used by shutdown as well.
            When called with self.main_top.protocol("WM_DELETE_WINDOW", self.reset)
            shutdown will contain <Tkinter.Event instance at 0x7f4ebb968ef0> """
        if self.tt and self.main_top:  # toolkit.Tooltips() won't exist during early startup
            self.tt.close(self.main_top)
        if self.main_top:
            geom = monitor.get_window_geom_string(self.main_top, leave_visible=False)
            monitor.save_window_geom('locations', geom)
            self.main_top.destroy()
            self.main_top = None  # Destroying doesn't set to 'None' for testing
        ''' Temporary close compare locations window '''
        if self.cmp_top_is_active:
            self.cmp_close()
        LocationsCommonSelf.__init__(self)  # Reset self. variables
        ''' Enable File, Edit & View Dropdown Menus for locations '''
        if isinstance(shutdown, tk.Event):
            self.enable_lib_menu()  # <Escape> bind
        elif not shutdown:  # When shutting down lib_top may not exist.
            self.enable_lib_menu()  # Restore deactivated options

    # noinspection PyUnusedLocal
    def apply(self, *args):
        """ Validate, Analyze mode (state), update database appropriately.
            Only called within Locations() class, never by mserve.py.
        """
        if not self.validate_location():
            return  # Reject apply when data errors

        if self.state == 'new':
            self.add_location()  # Save brand new location
            self.info.cast("Created new location: " + self.act_name, action="add")
        elif self.state == 'edit':
            self.save_location()
            self.info.cast("Saved location: " + self.act_name, action="update")
        elif self.state == 'delete':
            self.delete_location()
            self.info.cast("Deleted location: " + self.act_name, action="delete")
        elif self.state == 'open':
            self.info.cast("Open location: " + self.act_name, action="open")
            self.open_and_play_callback(self.act_code, self.act_topdir)
            # Above restarts mserve (assuming no errors) so never come back here
        elif self.state == 'target':
            self.info.cast("Target location: " + self.act_name, action="update")
            self.target_callback(self.act_name, self.act_topdir)
        elif self.state == 'synchronize':
            self.cmp_build_toplevel(sbar_width=14)
            # Problem: We don't want to do reset below, cmp must close itself
            return  # cmp_close closes cmp_window and main_top stays open for next
        else:
            toolkit.print_trace()
            print("Unknown Locations.apply() self.state:", self.state)

        self.reset()  # Destroy window & reset self. variables

    # ==============================================================================
    #
    #       Locations() - Compare locations and update file differences
    #
    # ==============================================================================

    def cmp_build_toplevel(self, sbar_width=14):
        """ Compare target location songs to build treeview of differences.

            Source is self.open_code, Target is self.act_code.

            After comparison:
                - Set modification time (mtime) of target to match source
                - Set modification time (mtime) of source to match target
                - Copy files from source to target maintaining mtime
                - Copy files from target to source maintaining mtime

            NOTE: Doesn't export or import songs
                  Android doesn't allow setting mod time so track in mserve """

        ''' Wake up host as required and keep awake '''
        if self.act_host:
            title = "Synchronize to Remote Host System? "
            text = self.act_host + " is a Remote Host.\n"
            text += "\n\nContinue with synchronization?\n"
            answer = message.AskQuestion(
                self.main_top, title, text, confirm='no', icon='info',
                thread=self.get_thread_func)
            self.info.cast(title + "\n\n" + text + "\n\n\t\t" +
                           "Answer was: " + str(answer.result), 'warning')
            if answer.result != "yes":
                #print("answer not yes", answer.result)
                return  # Let sleeping dogs lie
            #self.called_from_main_top = True  # Added Aug 28/23
            #print("answer yes, calling test_common_self.main_top")
            ''' Problems in test_common:
                    Help button is not assigned tooltip properly
                    Close test results button stays up after test host
                    clicking close test results:
                    # Exception in Tkinter callback
                    # Traceback (most recent call last):
                    #   File "/usr/lib/python2.7/lib-tk/Tkinter.py", line 1540, in __call__
                    #     return self.func(*args)
                    #   File "/home/rick/python/location.py", line 2979, in test_close_window
                    #     self.test_top.destroy()
                    # AttributeError: 'NoneType' object has no attribute 'destroy'
            '''
            if not self.test_common(self.main_top, called_from_sync=True):
                # Aug 28/23 - def test_common( returned false and did nothing
                #self.called_from_main_top = False  # Added Aug 28/23
                # def test_common
                return  # Refuses to connect to host
            if self.act_touchcmd:
                self.cmp_keep_awake_is_active = True
                self.cmp_keep_awake()

        self.start_long_running()  # Remove mserve full playlist buttons

        ''' Open FTP super-fast access file paths & sizes '''
        # print(who + "lcs.open_ftp:", lcs.open_ftp)
        if self.open_ftp:
            self.src_paths_and_sizes = \
                ext.read_from_json(FNAME_SIZE_DICT)
            #if self.src_paths_and_sizes:
            #    print("\nFNAME_SIZE_DICT:", FNAME_SIZE_DICT, "size:",
            #          len(self.src_paths_and_sizes))
        if self.act_ftp:
            fname = rnm_one_filename(FNAME_SIZE_DICT, self.act_code, self.open_code)
            self.trg_paths_and_sizes = \
                ext.read_from_json(fname)
            print("self.act_ftp:", self.act_ftp, type(self.act_ftp))
            #if self.trg_paths_and_sizes:
            #    print("\nfname:", fname, "size:",
            #          len(self.trg_paths_and_sizes))

        ''' Create Compare Locations top window - self.cmp_top '''
        self.cmp_top = tk.Toplevel()
        self.cmp_top.minsize(g.WIN_MIN_WIDTH, g.WIN_MIN_HEIGHT)
        self.cmp_top_is_active = True
        xy = (self.main_top.winfo_x() + g.PANEL_HGT,
              self.main_top.winfo_y() + g.PANEL_HGT)
        self.cmp_top.minsize(width=g.BTN_WID * 10, height=g.PANEL_HGT * 4)
        self.cmp_top.geometry('%dx%d+%d+%d' % (1800, 500, xy[0], xy[1]))  # 500 pix high
        if self.open_topdir.endswith(os.sep):  # the "source" location
            self.open_topdir = self.open_topdir[:-1]
        self.cmp_target_dir = self.act_topdir  # The "other/target" location
        if self.cmp_target_dir.endswith(os.sep):
            self.cmp_target_dir = self.cmp_target_dir[:-1]
        title = "Compare Locations - SOURCE: " + self.open_topdir + \
                " - TARGET: " + self.cmp_target_dir
        self.cmp_top.title(title)
        self.cmp_top.columnconfigure(0, weight=1)
        self.cmp_top.rowconfigure(0, weight=1)
        ''' Set program icon in taskbar '''
        img.taskbar_icon(self.cmp_top, 64, 'white', 'lightskyblue', 'black')

        ''' Create frames '''
        master_frame = tk.Frame(self.cmp_top, bg="LightGrey", relief=tk.RIDGE)
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
                                              "TrgSize", "Action", "src_time", "trg_time"),
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
        self.cmp_tree.heading("SrcSize", text="Source " + g.CFG_DIVISOR_UOM)
        self.cmp_tree.column("TrgSize", width=140, anchor=tk.E,
                             stretch=tk.YES)
        self.cmp_tree.heading("TrgSize", text="Target " + g.CFG_DIVISOR_UOM)
        self.cmp_tree.column("Action", width=280, stretch=tk.YES)
        self.cmp_tree.heading("Action", text="Action")
        self.cmp_tree.column("src_time")  # Hidden modification time
        self.cmp_tree.column("trg_time")  # Hidden modification time
        self.cmp_tree.grid(row=0, column=0, sticky=tk.NSEW)
        self.cmp_tree["displaycolumns"] = ("SrcModified", "TrgModified",
                                           "SrcSize", "TrgSize", "Action")
        ''' Treeview Scrollbars - Vertical & Horizontal '''
        v_scroll = tk.Scrollbar(frame2, orient=tk.VERTICAL, width=sbar_width,
                                command=self.cmp_tree.yview)
        v_scroll.grid(row=0, column=1, sticky=tk.NS)
        self.cmp_tree.configure(yscrollcommand=v_scroll.set)
        self.cmp_tree.tag_configure('cmp_sel', background='ForestGreen',
                                    foreground="White")

        # noinspection SpellCheckingInspection
        ''' Aug 5/23 - Horizontal Scrollbar removed for lack of purpose 
        h_scroll = tk.Scrollbar(frame2, orient=tk.HORIZONTAL, width=sbar_width,
                                command=self.cmp_tree.xview)
        h_scroll.grid(row=1, column=0, sticky=tk.EW)
        self.cmp_tree.configure(xscrollcommand=h_scroll.set)
        '''
        ''' Frame3 for Treeview Buttons '''
        self.cmp_btn_frm = tk.Frame(master_frame, bg="LightGrey", bd=2, relief=tk.GROOVE,
                                    borderwidth=g.BTN_BRD_WID)
        self.cmp_btn_frm.grid_rowconfigure(0, weight=1)
        self.cmp_btn_frm.grid_columnconfigure(0, weight=1)
        self.cmp_btn_frm.grid(row=1, column=0, sticky=tk.E)

        ''' Help Button - https://www.pippim.com/programs/mserve.html#HelpSynchronizeActions
                          Optional-Remote-Host-Support '''
        help_text = "Open new window in default web browser for\n"
        help_text += "videos and explanations on using this screen.\n"
        help_text += "https://www.pippim.com/programs/mserve.html#\n"
        self.cmp_help_button = tk.Button(
            self.cmp_btn_frm, text="⧉ Help", font=g.FONT,
            width=g.BTN_WID2 - 4, command=lambda: g.web_help("HelpSynchronizeActions"))
        self.cmp_help_button.grid(row=0, column=1, padx=10, pady=5, sticky=tk.E)

        # Aug 28/23 newly added help button, there are no tooltips used in window
        #if self.tt:  # During early boot toolkit.Tooltips() is still 'None'
        #    self.tt.add_tip(self.cmp_help_button, help_text, anchor="ne")

        ''' ✘ Close Button '''
        self.cmp_top.bind("<Escape>", self.cmp_close)
        self.cmp_top.protocol("WM_DELETE_WINDOW", self.cmp_close)
        self.cmp_close_btn = tk.Button(self.cmp_btn_frm, text="✘ Close",
                                       width=g.BTN_WID - 4, command=self.cmp_close)
        self.cmp_close_btn.grid(row=0, column=2, padx=(10, 5), pady=5,
                                sticky=tk.E)
        ''' Create Treeview. If no differences it gives message '''
        if not self.cmp_populate_tree():
            self.cmp_close()  # Files are identical
            return

        # NOTE: Only appears AFTER tree is built.
        ''' 🗘  Update differences Button u1f5d8 🗘 extra wide for count '''
        self.update_differences_btn = tk.Button(
            self.cmp_btn_frm, width=g.BTN_WID + 12, command=self.cmp_update_files,
            text="🗘  Update " + '{:,}'.format(self.cmp_found) + " differences")
        self.update_differences_btn.grid(row=0, column=0, padx=10, pady=5,
                                         sticky=tk.E)

        if self.cmp_top_is_active is False:
            #self.called_from_main_top = False  # Added Aug 28/23
            return
        self.cmp_tree.update_idletasks()

    def cmp_keep_awake(self):
        """ Every x minutes issue keep awake command for server. For example:
            'ssh dell "touch /tmp/mserve"' works for ssh-activity bash script.

            Recursive call to self

            For Debugging, run the following commands on the host and client:

            HOST - Open a terminal and enter command which runs forever:
              mserve_client.sh -d

            CLIENT - Open a terminal, and paste below, replacing "<HOST>" with Host name:
              while : ; do ssh <HOST> "cat /tmp/mserve_client.log" ; sleep 60 ; done

        """
        ''' Copied from mserve.py loc_keep_awake '''
        if not self.cmp_keep_awake_is_active:
            return  # Compare Location is closing

        self.awake_last_time_check = time.time()
        if self.awake_last_time_check > self.next_active_cmd_time:
            ''' Test if Host still connected before sending touch command '''
            test_passed = self.test_host_up(host=self.act_host)  # Quick & dirty nc test
            if not self.cmp_keep_awake_is_active:
                return  # Shutting down now
            if test_passed is False:
                mount_point = self.act_mountcmd  # Extract '/mnt/music' at end
                mount_point = mount_point.split()[-1]  # last part after space
                title = "Remote Host Disconnected!"
                text = self.act_name + " is off-line. Shutting down...\n\n"
                text += "'sshfs' MAY leave drive mounted for 15 minute timeout.\n"
                text += "Try: 'fusermount -u " + mount_point + "\n\n"
                text += "You can also try 'sshfs -o reconnect' option.\n\n"
                text += "OR... reboot, or do 15 minutes of other other work."
                text += "\n15 minute sshfs-fuse bug reportedly fixed Oct 27 2017:"
                text += "\nhttps://bugs.launchpad.net/ubuntu/+source/sshfs-fuse/+bug/912153"

                ''' Cannot show message because other threads keep closing? '''
                print(title + "\n" + text)
                self.out_cast_show_print(title, text, 'error')  # CRASHES
                # July 30, 2023, restarting will access /mnt/music and stall
                # If host suspends when mserve running, use 'ssh-activity -d'.
                self.cmp_host_down = True  # Don't close files on frozen sshfs-fuse
                self.cmp_close()  # Close compare files windows
                self.cmp_keep_awake_is_active = False
                return

            # Host is awake. Set next test time.
            result = os.popen(self.act_touchcmd).read().strip()
            ''' 10 minutes from now can be 4 hours from now when laptop is
                suspended. During that time host may have gone to sleep. So
                read time (not elapsed CPU time) is required.
                
                Below save_touch_time() is for self.OPEN_host not self.act_host
                which is needed.
                
                There can be a signal fired by refresh_thread when system has
                awoke from sleep. Formula based upon last saved time in memory
                > x seconds / minutes.
            '''
            self.save_touch_time(compare=True)  # Record compare location time
            if len(result) > 4:  # Did nc -z have error results?
                title = "location.py Locations.cmp_keep_awake()"
                text = "Running command: 'nc -z " + self.act_host + " 22'"
                text += "\n\nReceived unexpected results show below:\n\n"
                text += result
                self.out_cast_show_print(title, text, 'error')
            self.awake_last_time_check = time.time()
            #self.next_active_cmd_time = self.awake_last_time_check + (60 * LODICT['activemin'])
            self.next_active_cmd_time = self.awake_last_time_check + (60 * self.act_touchmin)

            title = "Keeping Remote Host awake."
            text = "Running: " + self.act_touchcmd + "\n"
            text += "  | This time: " + ext.t(self.awake_last_time_check)
            text += "  | Next time: " + ext.t(self.next_active_cmd_time)
            self.out_fact(title, text, 'info')

            if not self.cmp_keep_awake_is_active:
                return  # Compare Location is closing

        if not self.act_touchmin:
            # TODO: new variable name and move outside of loop.
            print("Override self.act_touch_min from 'None' to 10 minutes.")
            self.act_touchmin = 10
        self.act_touchmin = 10 if self.act_touchmin < 2 else self.act_touchmin
        mill = int(self.act_touchmin * 60 * 1000)  # convert to milliseconds
        print("location.py cmp_keep_awake() main_top.after - mill:", mill)
        self.main_top.after(mill, self.cmp_keep_awake)  # cmp_top may close early

    # *args reported as unused, but is required for binding <Escape> to cmp_close()
    # noinspection PyUnusedLocal 
    def cmp_close(self, *args):
        """ Close Compare location treeview """

        self.end_long_running()  # Restore mserve full playlist buttons

        if self.cmp_keep_awake_is_active:  # Keeping remote host awake?
            self.cmp_keep_awake_is_active = False  # Has 10 minute wakeup cycle
        if not self.cmp_top_is_active:
            return  # Already closed
        self.cmp_top_is_active = False
        if self.tt and self.cmp_top:
            if self.tt.check(self.cmp_top):  # Were tooltips created?
                self.tt.close(self.cmp_top)  # Close tooltips under top level
        self.cmp_top.destroy()  # Close the treeview window
        self.cmp_top = None

        self.reset()  # Safest way to avoid self.act_ftp corruption running again.

        return True

    def cmp_populate_tree(self):

        """ Add Artist, Album and Song to treeview self.cmp_tree.
            Similar to add_items() in Music Location Tree

        :returns True: When locations are different
        """
        # How many path separators '/' are there in source?
        start_dir_sep = self.open_topdir.count(os.sep)
        self.src_mt = ModTime(self.open_code)
        self.trg_mt = ModTime(self.act_code)

        ''' TODO: Put self....mt.allows_mtime on screen: 
                  perhaps in test host frame?
                  perhaps in format_info() line?
        '''
        #print("self.src_mt.allows_mtime:", self.src_mt.allows_mtime)
        #print("self.trg_mt.allows_mtime:", self.trg_mt.allows_mtime)

        LastArtist = LastAlbum = CurrAlbumId = CurrArtistId = ""
        #self.cmp_found = 0

        ext.t_init("Build compare target")
        ''' Traverse fake_paths created by mserve.py make_sorted_list() '''
        for i, fake_path in enumerate(self.fake_paths):
            if not self.cmp_top_is_active:
                return False  # Closing down, False indicates no differences

            self.fast_refresh(tk_after=False)  # Update play_top animations

            # split song /mnt/music/Artist/Album/Song.m4a into variable names
            groups = fake_path.split(os.sep)
            Artist = str(groups[start_dir_sep + 1])
            Album = str(groups[start_dir_sep + 2])
            Song = str(groups[start_dir_sep + 3])

            if Artist != LastArtist:
                try:
                    CurrArtistId = self.cmp_tree.insert(
                        "", "end", text=Artist, tags=("Artist",), open=True)
                except tk.TclError:
                    return False  # close button
                LastArtist = Artist
                LastAlbum = ""  # Force subtotal break for Album

            if Album != LastAlbum:
                try:
                    CurrAlbumId = self.cmp_tree.insert(
                        CurrArtistId, "end", text=Album, tags=("Album",))
                except tk.TclError:
                    return False  # close button
                LastAlbum = Album
                self.cmp_top.update_idletasks()  # Allow close button to abort


            if not self.cmp_top_is_active:
                return False  # Closing down, False indicates no differences

            ''' Compare two files '''
            action, src_path, src_size, src_time, trg_path, \
                trg_size, trg_time = self.compare_path_pair(fake_path)

            if action == "Missing":
                self.cmp_trg_missing.append(trg_path)  # Not used yet
                self.cmp_tree.see(CurrAlbumId)  # Files identical
                continue
            if action == "Same":
                self.cmp_tree.see(CurrAlbumId)  # Files identical
                continue
            if action == "OOPS":
                self.cmp_tree.see(CurrAlbumId)  # Files identical
                continue

            ''' Make pretty fields '''
            converted = float(src_size) / float(g.CFG_DIVISOR_AMT)
            src_fsize = '{:n}'.format(round(converted, 3))  # 3 decimal places
            converted = float(trg_size) / float(g.CFG_DIVISOR_AMT)
            trg_fsize = '{:n}'.format(round(converted, 3))
            # Format date as "Abbreviation - 99 Xxx Ago"
            src_ftime = tmf.ago(float(src_time))
            trg_ftime = tmf.ago(float(trg_time))

            if not self.cmp_top_is_active:
                return False  # Closing down, False indicates no differences

            ''' Insert song into comparison treeview and show on screen '''
            self.cmp_tree.insert(CurrAlbumId, "end", iid=str(i), text=Song,
                                 values=(src_ftime, trg_ftime, src_fsize, trg_fsize, action,
                                         float(src_time), float(trg_time)),
                                 tags=("Song",))
            self.cmp_tree.see(str(i))
            self.cmp_top.update_idletasks()  # Allow close button to abort
            self.cmp_found += 1

            if self.cmp_top_is_active is False:
                return False  # Closing down, False indicates no differences

        ext.t_end('print')  # No Refresh: Build compare target: 1.2339029312
        # Refresh thread (33ms after)   : Build compare target: 158.4349091053
        # Refresh tk_after=False     : Build compare target: 26.8863759041

        ''' Prune tree - Albums with no differences, Artists with no Albums '''
        for artist in self.cmp_tree.get_children():
            album_count = 0
            for album in self.cmp_tree.get_children(artist):
                if self.cmp_top_is_active is False:
                    return False  # Closing down, False indicates no differences
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
            title = "Files identical"
            text = "Files common to both locations are identical."
            self.out_fact_show(title, text)
            return False

    @staticmethod
    def real_from_fake_path(fake_path):
        """ Remove <No Artist> and <No Album> from fake paths """
        real_path = fake_path.replace(os.sep + g.NO_ARTIST_STR, '')
        return real_path.replace(os.sep + g.NO_ALBUM_STR, '')

    def compare_path_pair(self, fake_path):
        """ Called when inserting in treeview and after copy/touch command.

            NOTES for sshfs:
                First sync is 8,261 seconds 2 hours 18 minutes for
                3,800 songs 'diff'.

                Second sync is 1 minute

                Run bash script 'test-for-sync.sh' to change files
                    in ~/Music/Compilations

                Use Kid3 on song to change some metadata

            RETURNS:

                return action, src_path, src_size, src_time, \
                    trg_path, trg_size, trg_time

            WHERE:
                src_path = self.open_topdir + real bottom path
                trg_path = self.act_topdir + real bottom path
                size = integer file size in bytes
                mtime = modification time to filesystems' nanosecond precision

            Possible return actions (hidden detached from treeview):
                "Missing" - In target(other) location (hidden from view)
                "Same" - within 2 seconds so no action required (hidden)
                "Error: Size different, time same" - Don't know copy direction
                "Error: contents different, time same" -    "   "   "   "
                "Error: Permission denied from 'diff' command"
                "OOPS" - programming error that should never happen (hidden)
                "Copy Trg -> Src (Size)" - Based on size difference
                "Copy Src -> Trg (Size)" - Based on size difference
                "Copy Trg -> Src (Diff)" - Based on file difference
                "Copy Src -> Trg (Diff)" - Based on file difference
                "Timestamp Trg -> Src" - Prevents future checks
                "Timestamp Src -> Trg" - Prevents future checks """

        action = ""  # to make pycharm happy

        ''' Build real song path from fake_path and stat '''
        src_path = self.real_from_fake_path(fake_path)
        
        ''' Is os.stat() call necessary? '''
        src_size = 0
        src_time = 0.0
        if self.src_paths_and_sizes:
            src_size = self.src_paths_and_sizes.get(src_path, 0)
        if not self.src_mt.allows_mtime:
            old_time, src_time = self.src_mt.mod_dict.get(src_path, (0.0, 0.0))

        if src_size == 0 or src_time == 0.0:
            src_stat = os.stat(src_path)  # os.stat provides file attributes
            src_size = src_stat.st_size
            src_time = float(src_stat.st_mtime)

        ''' Build target path, check if exists and use os.stat '''
        trg_path = src_path.replace(self.open_topdir, self.cmp_target_dir)

        ''' Is os.stat() call necessary? '''
        trg_size = 0
        trg_time = 0.0
        if self.trg_paths_and_sizes:
            trg_size = self.trg_paths_and_sizes.get(trg_path, 0)
        if not self.trg_mt.allows_mtime:
            old_time, trg_time = self.trg_mt.mod_dict.get(trg_path, (0.0, 0.0))

        ''' check if exists and use os.stat '''
        if trg_size == 0 or trg_time == 0.0:
            if not os.path.isfile(trg_path):  # If target missing, then return
                action = "Missing"  # Will not appear in treeview
                return action, src_path, src_size, src_time, \
                    trg_path, None, None

            trg_stat = os.stat(trg_path)  # os.stat provides file attributes
            trg_size = trg_stat.st_size
            trg_time = float(trg_stat.st_mtime)

        ''' When Android not updating modification time, keep track ourselves '''
        src_time = self.src_mt.get(src_path, src_time)
        trg_time = self.trg_mt.get(trg_path, trg_time)
        time_diff = abs(src_time - trg_time)  # time diff between src & trg

        ''' Size and modify times match? Already synchronized. '''
        if src_size == trg_size and time_diff <= 2:
            action = "Same"  # Will not appear in treeview
            return action, src_path, src_size, src_time, \
                trg_path, trg_size, trg_time

        ''' Check difference based on size or diff command '''
        if src_size != trg_size:
            ''' Sizes are different - Copy newer file to older file '''
            if src_time < trg_time:
                action = "Copy Trg -> Src (Size)"
            elif src_time > trg_time:
                action = "Copy Src -> Trg (Size)"
            else:
                action = "Error: Size different, time same"
            return action, src_path, src_size, src_time, \
                trg_path, trg_size, trg_time

        self.run_one_command(
            'diff -s ' + '"' + src_path + '" "' + trg_path + '"', src_size)

        ''' Permission denied if curlftpfs chokes on files with # in name '''
        if self.act_ftp and self.cmp_return_code != 0:
            print("Retrying self.act_ftp and self.cmp_return_code != 0:")
            base_path = trg_path.replace(self.act_topdir, '')
            self.ftp_retrieve(self.act_ftp, base_path)  # Retrieve manually
            self.cmp_return_code = 0  # Reset for repeating test
            self.run_one_command(
                'diff -s ' + '"' + src_path + '" "' +
                self.TMP_FTP_RETRIEVE + '"', src_size)
            print(ext.read_into_string(self.TMP_STDOUT))
            """ 
            TODO:
            1. Assume target is Android and Android is never the source
            2. ftp file transfer to /tmp/mserve_ftp_recv_zs8k6f
            3. diff between src_path and /tmp file (self.TMP_FTP_RETRIEVE)
            4. See ftp_retrieve
            """

        ''' Permission denied - Do nothing, just report and skip copy '''
        if self.cmp_return_code != 0:
            action = "Error: Permission denied on 'diff' check"
            #print("\nError on file:", trg_path)
            print(action, "return code:", self.cmp_return_code, "\n")
            self.cmp_return_code = 0  # Reset so doesn't force end
            return action, src_path, src_size, src_time, \
                trg_path, trg_size, trg_time

        # Get stdout contents STDOUT from 'diff' command
        out = self.get_file_data(self.TMP_STDOUT)
        if not out.strip().endswith(" are identical"):  # TODO: Horrible testing stdout
            print("out:", out)

            ''' Size same but contents different - Copy newer file to older '''
            if src_time < trg_time:
                action = "Copy Trg -> Src (Diff)"

                ''' Size same but contents different - Copy newer file to older '''
            elif src_time < trg_time:
                action = "Copy Trg -> Src (Diff)"
            elif src_time > trg_time:
                action = "Copy Src -> Trg (Diff)"
            else:
                action = "Error: contents different, time same"

        else:
            ''' Size and contents the same. Set timestamp to oldest time '''
            # File contents same so modification times must be synced
            if src_time > trg_time:
                action = "Timestamp Trg -> Src"
            elif src_time < trg_time:
                action = "Timestamp Src -> Trg"
            else:
                # Time or Size were different before now same
                # Another job running perhaps?
                title = "location.py Locations.compare_song_pair()"
                text = "Programming error. Different pair now look like twins:\n\n"
                text += "  - action   :  " + action + "\n"
                text += "  - src_path :  " + src_path + "\n"
                text += "  - trg_path :  " + trg_path + "\n"
                text += "  - src_size :  " + str(src_size) + "\n"
                text += "  - trg_size :  " + str(trg_size) + "\n"
                text += "  - src_time :  " + str(src_time) + "\n"
                text += "  - trg_time :  " + str(trg_time) + "\n"
                text += "  - trg_size :  " + str(trg_size) + "\n\n"
                text += "Was another job running? Contact www.pippim.com"
                self.out_cast_show_print(title, text, 'error', align="left")
                action = "OOPS"

        return action, src_path, src_size, src_time, \
            trg_path, trg_size, trg_time

    def ftp_retrieve(self, ftp, path):
        """ Retrieve file from FTP host """

        prefix, basename = path.rsplit(os.sep, 1)
        ftp.cwd(prefix)
        with open(self.TMP_FTP_RETRIEVE, 'wb') as f:
            ftp.retrbinary('RETR ' + basename, f.write)
        # error_perm: 550 No such directory.

    def cmp_update_files(self):
        """ Called via "Update differences" button on cmp_top """

        ''' Replace "update differences" button with progress bar '''
        self.update_differences_btn.grid_remove()  # Button can't click again
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(
            self.cmp_btn_frm, variable=progress_var, length=1200)
        progress_bar.grid(row=0, column=1, padx=2)  # skinny
        progress_bar.grid(row=0, column=1, padx=2, pady=2, sticky=tk.NSEW)
        #self.cmp_btn_frm.columnconfigure(1, weight=1)
        self.cmp_btn_frm.pack_slaves()

        ''' Build list of commands. Cannot update_idle inside loop (crash) '''
        self.cmp_return_code = 0  # Indicate how update failed
        self.cmp_command_list = list()  # List of tuples [(commands, parameters)]
        self.fast_refresh(tk_after=True)  # Update play_top animations
        for artist in self.cmp_tree.get_children():
            for album in self.cmp_tree.get_children(artist):
                for song in self.cmp_tree.get_children(album):
                    if not self.build_command_list(song):
                        self.cmp_return_code = 1  # Indicate how update failed
                        break  # Programmer error
        self.fast_refresh(tk_after=True)  # Update play_top animations

        ''' Tally sizes of all files to be copied. For granular progress bars. '''
        all_sizes = 0
        command_count = len(self.cmp_command_list)
        for iid, command, size, src_to_trg, src_time, trg_time in \
                self.cmp_command_list:
            if command.startswith("cp"):
                all_sizes += float(size)  # Total size of all files copied

        last_sel_iid = None  # Last row highlighted in green
        run_count = 0  # How many commands have be run so far
        copy_time_so_far = 0.0  # To estimate time remaining
        copy_size_so_far = 0  # To calculate progress bar percent
        all_start_time = time.time()  # To give total time duration when done

        ''' Process self.build_command_list(song) list '''
        for iid, command, size, src_to_trg, src_time, trg_time in \
                self.cmp_command_list:
            # Variable src_to_trg: True=source->target. False=target->source

            ''' Initialization '''
            if self.cmp_return_code != 0:
                break  # Could be from previous loop too

            ''' Uncomment code below for enough lag to watch progress bar '''
            #for _i in range(10):  # About 1/2 second lag to test play_top
            #    time.sleep(.05)
            #    self.fast_refresh(tk_after=True)

            fake_path = self.fake_paths[int(iid)]  # TODO: put paths in tuple?
            src_path = self.real_from_fake_path(fake_path)
            trg_path = src_path.replace(self.open_topdir, self.cmp_target_dir)

            if not self.fast_refresh():  # No sleep after should only take few ms
                return  # Already know closing down

            ''' 1. Highlight command being run '''
            ''' Shutting down? '''
            if not self.cmp_top_is_active:
                return
            self.cmp_tree.see(iid)  # tree.see() crashes when window is closed
            if last_sel_iid:
                toolkit.tv_tag_remove(self.cmp_tree, last_sel_iid, 'cmp_sel')
            toolkit.tv_tag_add(self.cmp_tree, iid, 'cmp_sel')
            last_sel_iid = iid  # Save highlight for removing next cycle

            ''' 2. Run the copy or touch command '''
            start_time = time.time()
            if not self.run_one_command(command, size):
                #self.cmp_return_code can be set to 2, 3, 4 or 5
                break  # Run one command failed

            ''' 3. Refresh progress bar '''
            run_count += 1
            percent = float(100.0 * run_count / command_count)
            progress_var.set(percent)
            if command.startswith("cp"):
                copy_time_so_far += time.time() - start_time
                copy_size_so_far += float(size)  # Total size of all files copied
                percent = float(100.0 * copy_size_so_far / all_sizes)
                if True is False:
                    progress_var.set(percent)  # No good - timestamps are short.
            if not self.fast_refresh():  # No sleep after should only take few ms
                return

            ''' 4. Update modification times for Android cell phones '''
            self.update_mod_times(
                src_to_trg, src_path, src_time, trg_path, trg_time)
            if not self.fast_refresh():  # No sleep after
                return

            ''' 5. Compare source and target again to verify success '''
            c_action, c_src_path, c_src_size, c_src_time, c_trg_path, \
                c_trg_size, c_trg_time = self.compare_path_pair(fake_path)
            if not c_action == "Same":
                print("Error: action should be 'Same' but isn't:", c_action)
                print("c_src_path:", c_src_path)
                print("c_src_size:", c_src_size)
                print("c_trg_path:", c_trg_path)
                print("c_trg_size:", c_trg_size)
                self.cmp_return_code = 10  # Files not same
                # self.cmp_return_code UNUSED 6, 7, 8 and 9
                break

        ''' Shutting down? '''
        if not self.cmp_top_is_active:
            return

        ''' Remove last highlight and close ModTime instances '''
        toolkit.tv_tag_remove(self.cmp_tree, last_sel_iid, 'cmp_sel')
        self.src_mt.close()  # Save modification_time to disk
        self.trg_mt.close()  # If no changes then simply exit

        ''' Error message first '''
        if not self.cmp_return_code == 0:  # An error was found
            title = "location.py Locations.cmp_update_files()"
            text = "received non-zero self.cmp_return_code: "
            text += str(self.cmp_return_code)
            self.out_cast_show_print(title, text, 'error')

        ''' Summary message '''
        missing_count = len(self.cmp_trg_missing)
        elapsed = time.time() - all_start_time
        if copy_time_so_far:
            speed = float(all_sizes) / copy_time_so_far
        else:
            speed = 0.0

        print("commands:", command_count, "\tsize:", all_sizes,
              "\telapsed:", '{:n}'.format(round(copy_time_so_far, 3)),
              "\tspeed:", '{:n}'.format(round(speed, 3)))

        title = "Locations synchronized"
        text = "Open Location:  " + self.open_name
        # TODO: Open Location missing: 999 music files.
        text += "\nOther Location: " + self.act_name
        if missing_count:
            text += "\nOther location is missing: " + '{:n}'.format(missing_count)
            text += " music files."
        text += "\n\nFile synchronization count: " + '{:n}'.format(run_count)
        if speed > 0:
            text += "\n\nCopy speed (MB/s): " + '{:n}'.format(speed)
        text += "\n\nTotal time (D.HH:MM:SS): " + tmf.mm_ss(elapsed)
        self.out_cast_show_print(title, text, align="left")

        # All done, close treeview as it's no longer relevant
        self.cmp_close()

    def run_one_command(self, command, size):
        """ Run 'touch' or 'cp' command. """
        ''' Remove previous stdout/stderr '''
        self.rm_file(self.TMP_STDOUT)  # Remove Standard Output results file
        self.rm_file(self.TMP_STDERR)  # Remove Standard Error results file
        if command.startswith("touch"):
            ''' Touch doesn't write to stdout and takes .003 seconds '''
            result = os.popen(command).read().strip()
            if len(result) > 4:
                with open(self.TMP_STDERR, "w") as text_file:
                    text_file.write(result)
                print("run_one_command() touch command returned results (stderr)")
                self.cmp_return_code = 2  # Indicate how update failed
            return self.fast_refresh()  # Give little time slice to other threads
        else:
            ''' Copy writes to stdout and takes .01 second / MB 
                'diff' over Wifi FTP Server takes .16 second / MB  '''
            return self.wait_for_cmd_output(command, size)

    def wait_for_cmd_output(self, command, size):
        """ Wait for cp (copy) command to complete
            Check cmp_top_is_active at top of each loop.
            Maximum time for STDOUT or STDERR to appear is 10 seconds. """

        ''' Build full command with stdout & stderr appended '''
        command += " 1>" + self.TMP_STDOUT  # mserve_stdout_5sh18d
        command += " 2>" + self.TMP_STDERR  # mserve_stderr_5sh18d
        start_time = time.time()
        result = os.popen(command + " &").read().strip()
        if len(result) > 4:
            print("wait_for_cmd_output() os.popen() unknown result:", result)
            self.cmp_return_code = 3  # Indicate how update failed
            return False

        loop_count = 0
        while True:
            loop_count += 1
            elapsed = time.time() - start_time
            if elapsed > 60.0:  # Aug 31/23 WiFi change 10.0 to 60.0 for `diff`
                # Loops: 270,211 	Size: 8,090,133 	Elapsed sec: 25.513 	Speed (MB/s): 0.317
                # Loops: 94,729 	Size: 4,726,205 	Elapsed sec: 9.85 	Speed (MB/s): 0.48
                print("wait_for_cmd_output() 60 second time-out")
                ''' TODO: Test host(s) and set down flags '''
                self.cmp_return_code = 4  # Indicate how update failed
                return False

            ''' stdout and stderr may be created with no information yet '''
            out = self.get_file_data(self.TMP_STDOUT)
            err = self.get_file_data(self.TMP_STDERR)
            if len(out) == 0 and len(err) == 0:
                # 'cp' over ethernet, False = 50 loops, True = 8 loops
                # 'diff' over Wifi, False = 30k to 100k loops, single-Core 100%
                # 'diff' over Wifi, False = 5k to 20k loops, single-Core 50%
                if not self.fast_refresh(tk_after=True):
                    return False
                continue  # No files or empty files

            ''' TODO: Record test results and cmp_return_code to audit log. '''
            speed = float(size) / elapsed / 1000000.0
            print("Loops:", '{:n}'.format(loop_count),
                  "\tSize:", size,  # size is unicode, not int
                  "\tElapsed sec:", '{:n}'.format(round(elapsed, 3)),
                  "\tSpeed (MB/s):", '{:n}'.format(round(speed, 3)))

            ''' stdout or stderr have been populated by cp command '''
            if len(err) > 0:
                print("'diff -s' or 'cp -v' errors reported below:\n", err)
                if len(out) > 0:
                    print("cp verbose reported too!:", out)
                self.cmp_return_code = 5
                return False
            if len(out) > 0:
                return True

    @staticmethod
    def get_file_data(f):
        """ Get data from STDOUT or STDERR """
        data = ""
        if os.path.isfile(f):
            with open(f, 'r') as fh:
                data = fh.read()
        return data

    def update_mod_times(self, src_to_trg, src_path, src_time, trg_path, trg_time):
        """ Update for Android, does nothing for other OS """
        ''' Update Modification Times from old time to new time '''
        if src_to_trg:  # Copy/Touch direction is from Src -> Trg
            self.src_mt.update(src_path, trg_time, src_time)
            self.trg_mt.update(trg_path, trg_time, src_time)
        else:  # Action is from Trg -> Src
            self.src_mt.update(src_path, src_time, trg_time)
            self.trg_mt.update(trg_path, src_time, trg_time)

    def fast_refresh(self, tk_after=False):
        """ Quickly update animations with no sleep after """

        if not self.get_thread_func:
            return True  # Still 'NoneType' during mserve startup & no windows

        if not self.last_fast_refresh:
            self.last_fast_refresh = 0.0  # Not init. May be mserve.py call.
        elapsed = time.time() - self.last_fast_refresh
        ''' Refresh designed for .033 seconds. If less art spins faster. '''
        if elapsed > .02:  # .02 + refresh time close to .033 for 30 FPS.
            # Aug 9/23 elapsed change from .2 to .1 for missing_artwork_callback
            #          No performance improvement so it's simply metadata read
            thr = self.get_thread_func()  # main_top, play_top or lib_top
            thr_ret = thr(tk_after=tk_after)
            if not thr_ret:
                print("fast_refresh() called thr(tk_after=tk_after))",
                      "and it returned False")
                return False
            self.last_fast_refresh = time.time()
        if self.cmp_top_is_active:
            return self.cmp_top_is_active is True
        else:
            return True  # Could be called from encoding.py, etc.

    @staticmethod
    def rm_file(fname):
        """ Remove file if it exists """
        if os.path.isfile(fname):
            os.remove(fname)

    def build_command_list(self, iid):
        """ Extract commands from treeview and stick into list """
        ''' fields from .insert() method
            self.cmp_tree.insert(CurrAlbumId, "end", iid=str(i), text=Song,
                values=(src_ftime, trg_ftime, src_fsize, trg_fsize, action,
                                    float(src_time), float(trg_time)), '''
        action = self.cmp_tree.item(iid)['values'][4]  # 6th treeview column
        if action.startswith("Error:"):  # Modification time unknown.
            return True  # True = looks like command built so action displayed

        src_time = self.cmp_tree.item(iid)['values'][5]
        trg_time = self.cmp_tree.item(iid)['values'][6]
        """ Set REAL paths for source and target """
        fake_path = self.fake_paths[int(iid)]
        src_path = self.real_from_fake_path(fake_path)
        trg_path = src_path.replace(self.open_topdir, self.cmp_target_dir)
        ''' src=from path, trg=to path. Can be flipped src_path/trg_path '''
        src, trg = self.cmp_decipher_arrow(action, src_path, trg_path)
        if src is None:
            print("Programmer made error - src is None")
            return False  # Programmer made error
        src_to_trg = src == src_path  # src_to_trg same(True) or flipped(False)
        if src_to_trg:
            size = self.cmp_tree.item(iid)['values'][2]  # str src size 3 dec
        else:
            size = self.cmp_tree.item(iid)['values'][3]  # str trg size 3 dec

        ''' Build command line so far '''
        if action.startswith("Copy "):  # Is it a copy?
            command_str = u"cp --preserve=timestamps --verbose"
        elif action.startswith("Timestamp "):  # Is it a timestamp?
            command_str = u"touch -m -r"
        else:  # None of above? - ERROR!
            title = "location.py Locations.build_command_list()"
            text = "Programming error. 'action' is not 'Copy' or 'Timestamp':\n\n"
            text += "  - action  :  " + action + "\n\n"
            text += "Contact www.pippim.com"
            self.out_cast_show_print(title, text, 'error', align="left")
            return False  # False = action not displayed in treeview

        ''' Complete command line with extra space:  "source"  "target" '''
        command_str += u'  "' + src + u'"  "' + trg + u'"'

        ''' add command & control tuple to list '''
        self.cmp_command_list.append((iid, command_str, size, src_to_trg,
                                      src_time, trg_time))

        return True

    def cmp_decipher_arrow(self, action, src_path, trg_path):
        """ Flip src_path (full_path) and trg_path (full_path2) around """
        if "Trg -> Src" in action:
            return trg_path, src_path
        elif "Src -> Trg" in action:
            return src_path, trg_path
        else:
            title = "location.py Locations.build_command_list()"
            text = "Programming error. Method failed to return results:\n\n"
            text += "self.cmp_decipher_arrow(action, src_path, trg_path):\n"
            text += "  - action  :  " + action + "\n"
            text += "  - src_path:  " + src_path + "\n"
            text += "  - trg_path:  " + trg_path + "\n\n"
            text += "Contact www.pippim.com"
            self.out_cast_show_print(title, text, 'error', align="left")
            return None, None


# End of location.py
