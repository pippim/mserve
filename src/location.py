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
#
#==============================================================================
#import stat
import Tkinter

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
FNAME_LAST_OPEN_STATES = MSERVE_DIR + "last_open_states"     # Expanded/Collapsed song list
FNAME_LAST_SONG_NDX    = MSERVE_DIR + "last_song_ndx"        # Last song played in list
# May 25 2021 -  last_selections corrupted by refresh_lib_tree()
# Jun 05 2023 -  last_selections DEPRECATED
FNAME_LAST_SELECTIONS  = MSERVE_DIR + "last_selections"      # Shuffled play order of songs
FNAME_LAST_PLAYLIST    = MSERVE_DIR + "last_playlist"        # Songs selected for playing

# Files in /tmp/
FNAME_TEST             = g.TEMP_DIR + "mserve_test"

# There can be two open at once so unlike other global variables this is never
# replaced. It is simply used as base for creating new variable.
FNAME_MOD_TIME        = MSERVE_DIR + "modification_time"

''' Global variables
'''
LIST = []                           # List of DICT entries
DICT = {}                           # Location dictionary


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
    global FNAME_LAST_SELECTIONS, FNAME_LAST_OPEN_STATES
    global FNAME_LAST_PLAYLIST, FNAME_LAST_SONG_NDX
    global LAST_LOCATION_SET

    ''' Sanity check '''
    if LAST_LOCATION_SET:
        print("location.py set_location_filenames(iid) cannot be called twice!")
        return

    FNAME_LAST_OPEN_STATES = set_one_filename(FNAME_LAST_OPEN_STATES, iid)
    FNAME_LAST_SONG_NDX    = set_one_filename(FNAME_LAST_SONG_NDX, iid)
    FNAME_LAST_PLAYLIST    = set_one_filename(FNAME_LAST_PLAYLIST, iid)

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
    """ rename on directory name

        TODO: Check if file/path exists before renaming

    """
    old_fname.replace(os.sep + "mserve" + os.sep + old + os.sep,
                      os.sep + "mserve" + os.sep + iid + os.sep)

    return old_fname    # Assume failure


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
    # April 25, 2023 - Why does this work when LIST is not global?
    with open(FNAME_LOCATIONS, "wb") as f:
        # store the data as binary data stream
        pickle.dump(LIST, f)                      # Save locations list
        f.close()


def unpickle_list(filename):

    """ generic open and unpickling to use everywhere:

            https://stackoverflow.com/questions/33307623/
                python-exception-safe-pickle-use/33308573

        NOT TESTED!

    """
    
    try:
        with open(filename, 'rb') as filehandle:
            # read the data as binary data stream
            return pickle.load(filehandle)
    except pickle.UnpicklingError:
        # normal, somewhat expected
        return []
    except (AttributeError,  EOFError, ImportError, IndexError) as e:
        # secondary errors
        print(traceback.format_exc(e))
        return []
    except Exception as e:
        # everything else, possibly fatal
        print(traceback.format_exc(e))
        return []


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
    """ Look up location dictionary using top directory path """
    global DICT                     # mserve.py will reference as lc.DICT
    stripped_last = dirname.rstrip(os.sep)
    for i, DICT in enumerate(LIST):
        topdir = DICT['topdir'].rstrip(os.sep)
        if topdir == stripped_last:
            return True             # DICT will be matching dirname

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


class ModTime:
    """ Open list of modification times
        Analyze location to see if 'touch -m -r src_path trg_path' works.
        If not utilize timestamp file to get last modification time.
    """

    def __init__(self, iid):
        self.change_cnt = 0         # Number of songs where new time changed
        self.delete_cnt = 0         # Number of songs deleted because time changed
        self.new_cnt = 0            # Number of songs added with old & new time
        self.loc_dict = item(iid)   # Keep copy of dictionary
        self.topdir = self.loc_dict['topdir']
        self.filename = FNAME_MOD_TIME
        self.filename = set_one_filename(self.filename, iid)
        #print('modification_time filename:',self.filename)

        # print('Initializing iid:',iid,'dict:',self.loc_dict)

        # Does location support modification timestamping?
        if not self.topdir.endswith(os.sep):
            self.topdir += os.sep
        testfile = self.topdir + "test19630518"
        with open(testfile, "w") as text_file:
            text_file.write("Test Modification Time")
        before_touch = os.stat(testfile).st_mtime
        os.popen("touch -m -t 196305180000 " + testfile)
        after_touch = os.stat(testfile).st_mtime
        os.remove(testfile)

        if before_touch == after_touch:
            self.allows_mtime = False
            #print("Top dir doesn't allow timestamps:",self.topdir)
        else:
            self.allows_mtime = True
            #print("Top dir allows timestamps:",self.topdir)
            return                          # No need for shadow filesystem

        # TODO: Temporary list until read/write done
        self.mod_dict = {}
        # Initialize dictionary if modification_time file already exists
        if os.path.isfile(self.filename):
            with open(self.filename, 'rb') as filehandle:
                # read the data as binary data stream
                self.mod_dict = pickle.load(filehandle)


    def get(self, path, mtime):
        """ Check if modification time has list entry for new time.
        """
        if self.allows_mtime:
            return mtime  # Nothing to do

        # See if file is in our dictionary
        dict_old_time, dict_new_time = self.mod_dict.get(path, (0.0, 0.0))
        mtime = float(mtime)
        dict_old_time = float(dict_old_time)
        dict_new_time = float(dict_new_time)
        #print('ModTime.get() dict_old_time:',dict_old_time,
        #                    'dict_new_time:',dict_new_time,'mtime:',mtime)
        #print('ModTime.get() dict_old_time:',t(dict_old_time),
        #                    'dict_new_time:',t(dict_new_time),'mtime:',t(mtime))
        if dict_new_time == mtime:
            #print ('ModTime.get() no changes')
            return mtime                    # Nothing has changed

        if dict_old_time == 0:
            #print('ModTime.get() New entry for our dictionary')
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
            # print('ModTime.get() Return existing override time')
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
        """ If new modification time record it in list entry.
        """
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


    def close(self):
        """ If new modification time record it in list entry.
        """
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
        self.act_mountcmd = None
        self.act_touchcmd = None  # Replaces activecmd
        self.act_touchmin = None  # Replaces activemin
        self.act_comments = None
        self.act_row_id = None  # Location record number

        ''' Internal location Code: L001  +
            | Top Directory last modified: <time>  +
            | Mount Point: /mnt/Music, etc. 
            | Free: 99,999 MB of 999,999 MB 
        '''
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
        self.called_from_main_top = False  # Was test called from main_top?
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

        ''' Need to keep host awake using touch command every 10 minutes.
            Source (self.open_host) and target (self.act_host) could both
            require keeping awake.
        '''
        self.cmp_host_was_asleep = False  # Assume host wasn't asleep
        self.cmp_sshfs_used = False  # Assume host wasn't asleep

        ''' Compare locations variables '''
        self.cmp_top = None  # Compare Locations toplevel window
        self.cmp_top_is_active = False  # mserve.py uses False, not None
        self.cmp_target_dir = None  # OS directory comparing to
        self.cmp_tree = None  # Treeview w/difference between src and trg
        self.cmp_close_btn = None  # Button to close Compare Locations window
        self.update_differences_btn = None  # Click button to synchronize
        self.src_mt = None  # Source modification time using ModTime() class
        self.trg_mt = None  # Target modification time using ModTime() class
        self.src_fc = None  # Source FileControl() instance
        self.trg_fc = None  # Target FileControl() instance
        self.cmp_trg_missing = []  # Source files not found in target location
        self.cmp_msg_box = None  # message.Open()
        

class Locations(LocationsCommonSelf):
    """ Usage:

        lcs = Locations(make_sorted_list)

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
            - compare() - Compare open location to target location & synchronize
            - load_last_location() - Reopen location from last mserve session

    """

    def __init__(self, make_sorted_list):
        """
        :param make_sorted_list(): Function to verify TopDir is valid.
        """
        LocationsCommonSelf.__init__(self)  # Define self. variables

        ''' self-ize parameter list '''
        self.make_sorted_list = make_sorted_list  # Check if music files exist

        ''' Variables registered by mserve.py when available '''
        self.parent = None  # FOR NOW self.parent MUST BE: lib_top
        self.NEW_LOCATION = None  # When it's new location nothing to open
        self.text = None  # Text replacing treeview when no locations on file
        self.get_pending = None  # What is pending in parent? - Could be favorites
        self.open_and_play_callback = None
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

        ''' Additional Open Location variables not in SQL '''
        self.host_down = False  # For emergency shutdown
        self.open_sshfs_used = False

        ''' External Commands Installed? Flags '''
        self.nmap_installed = False  # Set in display_main_window()
        self.nmap_installed = False
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
        """ Register Tooltips after it's declared in mserve.py """
        self.tt = tt  # Tooltips pool for buttons

    def register_info(self, info):
        """ Register InfoCentre() after it's declared in mserve.py """
        self.info = info  # InfoCentre()

    def register_FileControl(self, fc):
        """ Register InfoCentre() after it's declared in mserve.py """
        self.FileControl = fc  # InfoCentre()

    def register_get_thread(self, get_thread):
        """ Register get_refresh_thread after it's declared in mserve.py """
        self.get_thread_func = get_thread  # E.G. self.get_refresh_thread()

    def register_menu(self, enable_menu_func):
        """ Register Dropdown Menu off/on after it's declared in mserve.py """
        self.enable_lib_menu = enable_menu_func  # E.G. self.enable_lib_menu()

    def register_fake_paths(self, fake_paths):
        """ Register self.fake_paths after make_sorted_list() in mserve.py """
        self.fake_paths = fake_paths

    def register_pending(self, get_pending):
        """ Register get_pending_cnt_total after it's declared in mserve.py """
        self.get_pending = get_pending

    def register_oap_cb(self, open_and_play_callback):
        """ Register open_and_play_callback() function from mserve.py """
        self.open_and_play_callback = open_and_play_callback
        self.open_and_play_callback = open_and_play_callback  # E.G. self.get_refresh_thread()

    # ==============================================================================
    #
    #       Locations() Processing - tkinter Window Methods
    #
    # ==============================================================================

    def display_main_window(self, name=None):
        """ Mount window with Location Treeview or placeholder text when none.
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
        ''' 🔗 Help - Videos and explanations on pippim.com '''
        self.make_main_help_button()

        ''' Test Host Button whenever a wakeup command present '''
        if self.fld_wakecmd:  # Is wakeonlan installed?
            self.wakecmd_focusout()

        ''' Refresh screen '''
        self.main_top.update_idletasks()

    def make_main_close_button(self):
        """ Added by main window, removed by testing. """

        ''' Close Button - NOTE: This calls reset() function !!! '''
        self.main_close_button = tk.Button(
            self.main_frame, text="✘ Close", font=g.FONT,
            width=g.BTN_WID2 - 4, command=self.reset)
        self.main_close_button.grid(row=14, column=0, padx=5, pady=5, sticky=tk.W)
        if self.tt:
            self.tt.add_tip(self.main_close_button, "Ignore changes and return.",
                            anchor="nw")
        self.main_top.bind("<Escape>", self.reset)
        self.main_top.protocol("WM_DELETE_WINDOW", self.reset)

    def make_main_help_button(self):
        """ Added by main window, removed by testing. """

        ''' Help Button - https://www.pippim.com/programs/mserve.html#locations '''
        ''' 🔗 Help - Videos and explanations on pippim.com '''

        help_text = "Open new window in default web browser for\n"
        help_text += "videos and explanations on using this screen.\n"
        help_text += "https://www.pippim.com/programs/mserve.html#\n"

        self.main_help_button = tk.Button(
            self.main_frame, text="🔗 Help", font=g.FONT,
            width=g.BTN_WID2 - 4, command=lambda: g.web_help("HelpLocations"))
        self.main_help_button.grid(row=14, column=1, padx=5, pady=5, sticky=tk.W)
        if self.tt:
            self.tt.add_tip(self.main_help_button, help_text, anchor="nw")

    def display_test_window(self):
        """ Mount test host window """
        self.test_top = tk.Toplevel()  # Locations top level
        mon = monitor.Monitors()
        act_mon = mon.get_active_monitor()
        geom = "1100x750+" + str(act_mon.x + 30) + "+" + str(act_mon.y + 30)
        self.test_top.geometry(geom)
        mon.tk_center(self.test_top)  # centers on active monitor
        self.test_top.title("Test Host: " + self.act_host + " - mserve")

        ''' Common Top configuration, icon and Test Host master frame '''
        self.test_frame = self.make_display_frame(self.test_top)

        ''' Create frame for test host scrolled text box '''
        self.make_test_box(self.test_frame)

        ''' Shared between display_main_window() and display_test_window() '''
        self.display_location_details(self.test_frame)

        ''' Put active location variables onto freshly painted window '''
        self.set_scr_variables(self.test_top)  # Tell them whose calling
        self.input_active = False  # Screen fields are 'readonly'

        ''' Close Button - calls test_close_window() to wrap up '''
        self.make_test_close_button(self.test_frame)

        ''' Help Button - https://www.pippim.com/programs/mserve.html#
                          Optional-Remote-Host-Support '''
        self.make_test_help_button(self.test_frame)
        self.test_top.update_idletasks()  # Not powerful enough?
        self.test_top.update()  # More power !

    def make_test_box(self, frame):
        """ Can be in main_top or test_top """
        ''' Create frame for test scrolled text box '''
        #print("frame:", frame, "self.main_frame:", self.main_frame,
        #      "self.test_frame:", self.test_frame)
        self.test_scroll_frame = tk.Frame(frame, bg="olive", relief=tk.RIDGE)
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

        #self.test_box.insert("end", Quote)
        #self.test_box.highlight_pattern(self.act_host, 'yellow')
        self.test_show(text, pattern=self.act_host)

        self.test_box.config(tabs=("10m", "20m", "40m"))
        self.test_box.tag_configure("margin", lmargin1="2m", lmargin2="40m")
        # Fix Control+C  https://stackoverflow.com/a/64938516/6929343
        self.test_box.bind("<Button-1>", lambda event: self.test_box.focus_set())

    def make_test_close_button(self, frame):
        """ Can be called for new test_top or to replace existing main_top """
        ''' Close Button - calls test_close_window() to wrap up '''
        self.test_close_button = tk.Button(
            frame, text="✘ Close Test Results", font=g.FONT,
            width=g.BTN_WID2 + 6, command=self.test_close_window)
        self.test_close_button.grid(row=14, column=0, padx=5, pady=5, sticky=tk.W)
        if not self.called_from_main_top:  # no main_top, so escape closes test_top
            self.test_top.bind("<Escape>", self.test_close_window)
            self.test_top.protocol("WM_DELETE_WINDOW", self.test_close_window)
        if self.tt:  # During early boot toolkit.Tooltips() is still 'None'
            self.tt.add_tip(self.test_close_button, "End test of Host: " +
                            self.act_host, anchor="nw")

    def make_test_help_button(self, frame):
        """ Can be called for new test_top or to replace existing main_top """
        ''' Help Button - https://www.pippim.com/programs/mserve.html#
                          Optional-Remote-Host-Support '''
        help_text = "Open new window in default web browser for\n"
        help_text += "videos and explanations on using this screen.\n"
        help_text += "https://www.pippim.com/programs/mserve.html#\n"
        self.test_help_button = tk.Button(
            frame, text="🔗 Help", font=g.FONT,
            width=g.BTN_WID2 - 4, command=lambda: g.web_help("HelpTestHost"))
        self.test_help_button.grid(row=14, column=1, padx=5, pady=5, sticky=tk.W)
        if self.tt:  # During early boot toolkit.Tooltips() is still 'None'
            self.tt.add_tip(self.test_help_button, help_text, anchor="nw")


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
            Shared by display_main_window() method and test() methods
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
        #self.nmap_installed = False  # Test
        if self.nmap_installed:
            ''' Command 'nc' also required to quickly check if host is up '''
            self.nmap_installed = ext.check_command('nc')
        self.ssh_installed = ext.check_command('ssh')
        #self.ssh_installed = False  # Test
        self.sshfs_installed = ext.check_command('sshfs')
        if self.sshfs_installed:
            self.sshfs_installed = ext.check_command('fusermount')
        #self.sshfs_installed = False  # Test
        self.wakeonlan_installed = ext.check_command('wakeonlan')
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
        else:  # When no mode passed, the window is for testing host.
            ''' When testing host, there are no Treeview rows above '''
            text = "🡅 🡅  Slide scrollbar above to see Test Host results  🡅 🡅"
        self.fld_intro = tk.Label(frame, text=text, font=g.FONT)
        self.fld_intro.grid(row=1, column=1, columnspan=3, stick=tk.EW)

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

        ''' Image path doesn't appear on test window
            July 28, 2023 causes corruption if two windows hae different fields.
        if mode:
        '''
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
                self.main_frame, text="🔍 Test Host Wakeup", font=g.FONT,
                width=g.BTN_WID2 + 4, command=lambda: self.test_common(self.main_top))
            self.test_host_button.grid(row=14, column=2, padx=5, pady=5, sticky=tk.W)
            if self.tt:
                self.tt.add_tip(self.test_host_button,
                                "Test command to wake up Host.", anchor="ne")
            self.called_from_main_top = True  # main_top calling test, no test_top
        elif self.test_host_button:
            ''' No wakeup command. Destroy button created earlier. '''
            self.tt.close(self.test_host_button)
            self.test_host_button.destroy()
            self.test_host_button = None  # Destroying doesn't set to 'None' for testing
            self.called_from_main_top = False  # no main_top, so create test_top

    def populate_loc_tree(self):
        """ Use custom Data Dictionary routines for managing treeview. """

        ''' Data Dictionary and Treeview column names '''
        location_dict = sql.location_treeview()  # Heart of Data Dictionary
        columns = ("code", "name", "topdir")
        toolkit.select_dict_columns(columns, location_dict)

        ''' Create treeview frame with scrollbars '''
        self.tree_frame = tk.Frame(self.main_frame, bg="olive", relief=tk.RIDGE)
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
                text = "Cannot reopen the same location."
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
        self.enable_last_button()  # For everyone except "New Location"
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

        ''' Test Host doesn't have a location introduction line '''
        if top_name == self.main_top:
            self.format_intro_line()  # Format introduction line

        self.scr_name.set(self.act_name)
        self.scr_topdir.set(self.act_topdir)

        ''' If Test Host fields not defined, no scr_ fields exist '''
        if self.fld_host:  # nmap and nc installed?
            self.scr_host.set(self.act_host)
        if self.fld_wakecmd:  # Is wakeonlan installed?
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
        self.scr_comments.set(self.act_comments)

        #if top_name == self.main_top:  # No self.scr_image_path on self.test_frame
        self.scr_image_path.set(self.act_image_path)  # New

    def enable_input(self):
        """ Turn on input fields for 'new' and 'edit'

            THOUGHTS about scr_mount_point variable:

            From this answer:https://stackoverflow.com/a/4453715/6929343
            def find_mount_point(path):
                path = os.path.abspath(path)
                while not os.path.ismount(path):
                    path = os.path.dirname(path)
                return path

            After getting mount point can find out there are no files or
            directories and know nothing is mounted yet.
            Use the 100/10 test described below. Or will mount test file
            walking back through invalid paths?

            When FileControl.stat_start is called it will generate an error
             if file system is not mounted. Errno 2.

            Open last location can have 'New' button if the old mount
            point is fine. Or an 'Edit' button if TopDir has changed. When
            changing TopDir close music player if current location. Rename
            all favorites with new TopDir. What if some files don't exist
            in new TopDir?

            If locations defined default to open. If no locations only
            'New' button is available.

        """
        self.input_active = True
        self.fld_name['state'] = 'normal'  # Allow input

        ''' Changing TopDir restricted '''
        if self.state == 'new':
            self.fld_topdir['state'] = 'normal'  # Always allow when 'new'

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

    def enable_last_button(self):
        """ Location just picked from treeview
            Create last button actions of: "Add", "Save", "Delete" or "Open"
        """
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
        else:
            toolkit.print_trace()
            text = "Missing!"

        self.apply_button = tk.Button(
            self.main_frame, text="✔ " + text, font=g.FONT,
            width=g.BTN_WID2 - 2, command=self.apply)
        self.apply_button.grid(row=14, column=3, padx=5, pady=5, sticky=tk.W)
        self.main_top.bind("<Return>", self.apply)
        ''' toolkit.Tooltips() guaranteed to be active for Apply button '''
        self.tt.add_tip(self.apply_button, text + 
                        " Location and update records.", anchor="ne")

    def format_intro_line(self):
        """ Format introduction line
            self.act_code will be blank when adding a new location
        """
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
            pass
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
        #thread = self.get_thread_func()
        #new_topdir = message.AskDirectory(
        #    parent=self.main_top, initial dir=self.act_topdir,
        #    title="Select Music Top Directory", thread=thread)
        #print("new_topdir.result:", new_topdir.result)
        # Traceback (most recent call last):
        #   File "/usr/lib/python2.7/lib-tk/Tkinter.py", line 1540, in __call__
        #     return self.func(*args)
        #   File "/home/rick/python/location.py", line 1308, in get_topdir
        #     if not new_topdir.endswith(os.sep):
        # AttributeError: AskDirectory instance has no attribute 'endswith'

        if new_topdir == self.act_topdir:
            return  # No changes

        if not new_topdir:
            return  # Clicked cancel

        if not new_topdir.endswith(os.sep):
            new_topdir += os.sep

        ''' Validate Music Top Directory has Artists/Albums/Songs '''
        work_list, depth_count = self.make_sorted_list(new_topdir, self.main_top, check_only=True)
        if depth_count[2] < 10:
            title = "Invalid Music Top Directory"
            text = "Invalid Directory: '" + new_topdir + "'\n\n"
            text += "A valid top directory would be something like 'My Music'.\n\n"
            text += "Underneath the top directory would be Artist subdirectories.\n"
            text += "Underneath each Artist would be one or more Album subdirectories.\n"
            text += "Within each Album subdirectory would be one or more music files.\n"
            text += "Up to 100 files checked and didn't find 10 music files for Albums."
            text += "\n\nMusic file search results at three levels:\n"
            text += "\nTop Directory: {}\n".format(depth_count[0])
            text += "\nArtist Level : {}\n".format(depth_count[1])
            text += "\nAlbum Level  : {}\n".format(depth_count[2])
            text += "\n\nReview your music directories and try again."
            text += "\n\nNote you can start mserve and pass a directory name to play."
            text += "\nIn this case a location is not required. For example, at the:"
            text += "\ncommand line you can type: 'm /home/me/Music/Compilations'"
            self.out_cast_show(title, text, 'error')  # Splash instructions

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

    def out_cast_show_print(self, title, text, icon='info'):
        """ Send self.info.cast(), message.ShowInfo() and print(). """
        if self.info:
            self.info.cast(title + "\n\n" + text, icon)
        self.out_show(title, text, icon)
        print("\n" + title + "\n\n" + text + "\n")
        return icon == 'info'  # Return value has little importance.

    def out_cast_show(self, title, text, icon='info'):
        """ Send self.info.cast() and message.ShowInfo() with print() backup. """
        if self.info:
            self.info.cast(title + "\n\n" + text, icon)
        if not self.out_show(title, text, icon):
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
    
    def out_fact_show(self, title, text, icon='info'):
        """ Send self.info.fact() and message.ShowInfo() with print() backup. """
        if self.info:
            self.info.fact(title + "\n\n" + text, icon)
        if not self.out_show(title, text, icon):
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

    def out_show(self, title, text, icon='info'):
        """ Called above to save 5 lines of code. """
        if self.get_thread_func:
            top = self.out_get_parent()
            if top:
                # Aug 4/23 ShowInfo() revised to accept get_thread_func w/o ()
                message.ShowInfo(top, title, text, icon=icon,
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
        self.enable_last_button()  # Set "Add" into last button

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

    def synchronize(self):
        """ Called by lib_top Edit Menubar 'Synchronize Location' """
        LocationsCommonSelf.__init__(self)  # Define self. variables
        self.state = 'synchronize'
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
            return None

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

    def save_touch_time(self):
        """ Called by mserve to keep track of last touch time.
            Uses self.open_xxx variables !
        """
        if self.main_top:
            return  # Don't want to wipe out current data entry buffer

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
        """ July 27, 2023 - Currently only used when lcs.new() is called. """
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
        self.act_row_id = d['Id']  # Location record number

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
        self.open_row_id = d['Id']  # Location record number

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
            Called by lcs.apply().
        """
        if not self.state == 'new' and not self.state == 'edit':
            return True  # Only 'edit' or 'new' are validated.

        ''' Retrieve name and description from tkinter scr_ variables. '''
        new_name = self.scr_name.get().strip()
        new_topdir = self.scr_topdir.get().strip()
        ''' Retrieve optional remote host from tkinter scr_ variables. '''
        if self.fld_host:  # nmap and nc installed?
            new_host = self.scr_host.get().strip()
        if self.fld_wakecmd:  # wakeonlan installed?
            new_wakecmd = self.scr_wakecmd.get().strip()
        if self.fld_testcmd:  # Is ssh installed?
            new_testcmd = self.scr_testcmd.get().strip()
            new_testrep = self.scr_testrep.get()
        if self.fld_mountcmd:  # Is sshfs installed?
            new_mountcmd = self.scr_mountcmd.get().strip()
        if self.fld_touchcmd:  # Is ssh installed?
            new_touchcmd = self.scr_touchcmd.get().strip()
            new_touchmin = self.scr_touchmin.get()
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

    def validate_host(self, toplevel=None):
        """ Check current self.act_host variable to see if it a host 
            Called my mserve.py call to self.load_last_location()
            Always use self.open_xxx and never self.act_xxx fields which
            can be changed in Maintenance.

# NOTE: For Debugging, run the following commands on the host and client:
#       HOST (Open a terminal enter command to run forever):
#           mserve_client.sh -d
#       CLIENT (Copy to terminal and replace "<HOST>" with Host name):
#           while : ; do ssh <HOST> "cat /tmp/mserve_client.log" ; sleep 60 ; done

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
                        self.open_sshfs_used = True
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

    def test_host_up(self):
        """ Simply test if host is up and return True or False
            Only called from mserve.py to check if connection still up.
            Always use self.open_xxx and never self.act_xxx fields which
            can be changed in Maintenance.
        """
        if self.open_host:
            ''' nc returns 0 if host is on-line '''
            #print(ext.t(time.time()), "test_host_up()")
            result = os.system("nc -z " + self.open_host + " 22 > /dev/null")
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

    def test_common(self, toplevel, run_nmap=True):
        """ Validate Host Connect. 

            In simple form, check that local machine's top directory exists. 

            In complicated form, a remote host is woken up, the a remote partition
            is mounted locally and finally, test if top directory exists.

            Called by mserve.py -> lcs.load_last_location() -> lcs.validate_host()

            Also called by mserve.py: open_and_play_callback(self, code, topdir)

            Called internally from self.main_top -> self.test_host_button.

        :param toplevel: 'toplevel' can be 'main_top' that test window fully covers. 
            'toplevel' can be 'root' and then window centered on active monitor.
        :param run_nmap: If 'nc' was used for quick test, no need to run 'nmap'.
            Also display_test_window() was already done. """

        ''' Perform fastest test for mserve.py open_and_play_callback() '''
        if not self.called_from_main_top and not self.act_host:
            if os.path.exists(self.act_topdir) and \
                    len(os.listdir(self.act_topdir)) > 0:
                self.test_host_is_mounted = True
                if self.act_mountcmd:
                    self.open_sshfs_used = True  # better than nothing...
                return True  # Probably not even a host.

        ''' If using Test Button, validate_location() sets self.act_xxx vars '''
        if self.called_from_main_top and not self.validate_location():
            return False  # Called from main_top and error given to user to fix

        ''' We have more complicated situation where remote / host is used. '''
        display_test = run_nmap and not self.called_from_main_top
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

                ''' Launch wakeup command (don't use && sleep 4). '''
                os.popen(self.act_wakecmd)

        ''' Keep testing host until it is awake '''
        host_is_awake = False
        if self.act_testcmd:
            if os.path.exists(FNAME_TEST):
                os.remove(FNAME_TEST)
            cmd1 = ext.shell_quote(self.act_testcmd)
            if "#" in cmd1:  # Remove any comments from command to append redirects
                cmd1 = cmd1.split('#')[0]
            cmd = cmd1 + " > " + FNAME_TEST + " 2>&1 &"
            os.popen(cmd)  # Launch background command to list files to temp file
            full_text = "\nRunning test to see if Host awake:\n\t" + cmd + "\n"
            self.test_show(full_text, pattern=cmd1)

            text = "Waiting for '" + FNAME_TEST + "' output results to appear\n."
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
                os.popen(cmd)  # Launch background command to list files to temp file

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
                    self.open_sshfs_used = True
                else:
                    self.open_sshfs_used = False
            return self.test_success()

        ''' sshfs host's music top directory to local mount point '''
        mountcmd = self.act_mountcmd.strip()
        self.test_host_is_mounted = False  # Assume host isn't mounted
        if mountcmd:  # Need Non-blank mount command to run
            text = '\nMounting: ' + self.act_topdir + \
                   ' using:\n\t' + self.act_mountcmd + "\n"
            self.test_show(text, pattern=self.act_mountcmd)
            # noinspection SpellCheckingInspection
            ''' Advice about fuse error '''
            text = "NOTE: 'sshfs' can stall and cause mserve to freeze.\n" + \
                   "If so, you can test by listing files on mount point.\n\n" + \
                   "Run the command below and check for the error below:\n" + \
                   "    $ sshfs '" + self.act_host + ":/mnt/music' /mnt/music\n" + \
                   "    fuse: bad mount point `/mnt/music`:\n" + \
                   "    Transport endpoint is not connected\n\n" + \
                   "If you get the 'fuse' error, unmount the point with:\n" + \
                   "    $ sudo umount -l /mnt/music'"
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
            return self.test_success()  # Finally we're good to go!
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
        if display_test:
            ''' Careful here... Check call chain before revisions... '''
            #print(ext.t(time.time()), "mounting display_test_window")
            self.display_test_window()
            toplevel.update()
            self.set_scr_variables(self.test_top)
            self.test_top.update()

        if self.called_from_main_top:
            ''' Called from main_top using 'Test Host' button '''
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
            self.make_test_box(self.main_frame)  # Appears bottom of main_frame?
            ''' new buttons replace grid_remove '''
            self.make_test_close_button(self.main_frame)
            self.make_test_help_button(self.main_frame)
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
                self.tt.close(self.test_close_button)
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
            self.test_top.destroy()
            self.test_top = None  # Destroying doesn't set to 'None'

    def test_nmap(self, toplevel):
        """ Run the nmap command when 'nc' command has not been run. """
        ''' nmap returns results in lumps '''
        if os.path.exists(FNAME_TEST):
            os.remove(FNAME_TEST)
        cmd = "nmap -Pn " + self.act_host + " 2>&1 > " + FNAME_TEST + " &"
        os.popen(cmd)
        text = "\nUsing 'nmap' (Network Mapper) to test if: "
        text += self.act_host + " is connected."
        self.test_show(text, pattern="(Network Mapper)")
        self.test_show("Command: " + cmd, pattern="nmap -Pn " + self.act_host)

        text = "\nWaiting for 'nmap' output results to appear in: "
        text += FNAME_TEST + "\n"
        self.test_show(text, pattern="'nmap'")
        limit = 300  # 30 second time limit. dell takes 6.5 seconds
        string = ""
        start = time.time()
        self.test_show("Dummy Line to replace")
        for i in range(limit):
            self.test_refresh(toplevel, i + 1, limit, start,
                              "'nmap' results shown below")
            # noinspection PyBroadException
            try:
                string = ext.read_into_string(FNAME_TEST)
            except:
                continue  # File hasn't appeared yet
            if "Nmap done:" in string:
                break

        ''' Check nmap results '''
        host_is_up = "(1 host up)" in string
        host_is_awake = "22/tcp open" in string  # what if more spaces? Use re
        self.test_host_was_asleep = not host_is_awake  # Can do this better...
        if limit == 0:
            self.test_show("\n'nmap' FAILED! 10 second timeout exceeded.",
                           pattern="'nmap' FAILED!")
        else:
            self.test_show(string, pattern="(1 host up)")

        return host_is_up, host_is_awake

    def test_show(self, text, pattern=None):
        """ Insert into self.test_box (scrolled text box) and print to console.
            Also use dtb (delayed text box), however by design not all lines will
            appear there. dtb serves as GUI backup when test_window doesn't appear.

            last_insert is used by test_refresh to replace previous line.
        :param text: Text line for self.test_box. "\n" appended
        :return: Nothing
        """
        last_insert = self.test_box.tag_ranges("last_insert")
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
        last_insert = self.test_box.tag_ranges("last_insert")
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

    def test_success(self):
        """ End test with success """
        success = "\nHost successfully accessed. Click 'Close' button."
        self.test_show(success, pattern="'Close'")
        self.test_dtb.close()
        if not self.called_from_main_top:
            ''' This is a live situation. Set self.open_xxx '''
            if self.test_host_is_mounted and self.open_mountcmd:
                self.open_sshfs_used = True
            else:
                self.open_sshfs_used = False
            self.test_close_window()  # main_top allows reviewing results
        return True

    def test_failure(self):
        """ End test with Failure """
        failure = "\nHost FAILURE. Review and then click 'Close' button."
        self.test_show(failure, pattern="FAILURE")
        self.test_dtb.close()
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
        if self.open_sshfs_used and not self.open_topdir:
            title = "Programming Error."
            text = "location.py Locations.sshfs_close() called with no topdir."
            self.out_cast_show_print(title, text, 'error')

        if self.open_sshfs_used:
            cmd = "fusermount -u " + self.open_topdir
            os.popen(cmd)
            title = "Locations.sshfs_close() called at: " + ext.t(time.time())
            text = "Running: " + cmd
            self.out_fact_print(title, text, 'warning')
            self.open_sshfs_used = False

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
            #self.open_and_play_callback()  # Should be using self.act_code
            # Inside above function it's using old act_code and old act_topdir
            self.open_and_play_callback(self.act_code, self.act_topdir)
            # Above restarts mserve (assuming no errors) so never come back here
        elif self.state == 'synchronize':
            self.info.cast("Synchronize location: " + self.act_name, action="open")
            self.cmp_build_toplevel(self.act_code, sbar_width=16)
            # Problem: We don't want to do reset below, cmp must close itself
        else:
            toolkit.print_trace()
            print("Unknown Locations.apply() self.state:", self.state)

        self.reset()  # Destroy window & reset self. variables

    # ==============================================================================
    #
    #       Locations() - Compare locations and update file differences
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

            NOTE: Doesn't export or import songs
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
        #trg_dict = lc.item(trg_dict_iid)  # get dictionary for iid
        #self.cmp_target_dir = trg_dict['topdir']
        if not self.read_location(trg_dict_iid):
            print("if not self.read_location(trg_dict_iid):", trg_dict_iid)
            return
        self.cmp_target_dir = self.act_topdir  # Can just use this all the time.

        ''' Aug 5/23 - can no longer append slash '''
        # If no optional `/` at end, add it for equal comparisons
        #if not self.cmp_target_dir.endswith(os.sep):
        #    self.cmp_target_dir += os.sep

        self.cmp_top = tk.Toplevel()
        self.cmp_top.minsize(g.WIN_MIN_WIDTH, g.WIN_MIN_HEIGHT)
        self.cmp_top_is_active = True

        ''' cmp_top should be retrieved from SQL History '''
        xy = (self.main_top.winfo_x() + g.PANEL_HGT,
              self.main_top.winfo_y() + g.PANEL_HGT)

        self.cmp_top.minsize(width=g.BTN_WID * 10, height=g.PANEL_HGT * 4)
        self.cmp_top.geometry('%dx%d+%d+%d' % (1800, 500, xy[0], xy[1]))  # 500 pix high
        title = "Compare Locations - SOURCE: " + self.open_topdir + \
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
        self.cmp_tree.heading("SrcSize", text="Source " + g.CFG_DIVISOR_UOM)
        self.cmp_tree.column("TrgSize", width=140, anchor=tk.E,
                             stretch=tk.YES)
        self.cmp_tree.heading("TrgSize", text="Target " + g.CFG_DIVISOR_UOM)
        self.cmp_tree.column("Action", width=280, stretch=tk.YES)
        self.cmp_tree.heading("Action", text="Action")
        self.cmp_tree.column("src_mtime")  # Hidden modification time
        self.cmp_tree.column("trg_mtime")  # Hidden modification time
        self.cmp_tree.grid(row=0, column=0, sticky=tk.NSEW)
        self.cmp_tree["displaycolumns"] = ("SrcModified", "TrgModified",
                                           "SrcSize", "TrgSize", "Action")
        ''' Treeview Scrollbars - Vertical & Horizontal '''
        v_scroll = tk.Scrollbar(frame2, orient=tk.VERTICAL, width=sbar_width,
                                command=self.cmp_tree.yview)
        v_scroll.grid(row=0, column=1, sticky=tk.NS)
        self.cmp_tree.configure(yscrollcommand=v_scroll.set)
        h_scroll = tk.Scrollbar(frame2, orient=tk.HORIZONTAL, width=sbar_width,
                                command=self.cmp_tree.xview)
        h_scroll.grid(row=1, column=0, sticky=tk.EW)
        self.cmp_tree.configure(xscrollcommand=h_scroll.set)
        ''' Frame3 for Treeview Buttons '''
        frame3 = tk.Frame(master_frame, bg="Blue", bd=2, relief=tk.GROOVE,
                          borderwidth=g.BTN_BRD_WID)
        frame3.grid_rowconfigure(0, weight=1)
        frame3.grid_columnconfigure(0, weight=0)
        frame3.grid(row=1, column=0, sticky=tk.NW)

        ''' ✘ Close Button '''
        # TODO: we aren't keeping remote location awake only home location!
        self.cmp_top.bind("<Escape>", self.cmp_close)
        self.cmp_top.protocol("WM_DELETE_WINDOW", self.cmp_close)
        self.cmp_close_btn = tk.Button(frame3, text="✘ Close",
                                       width=g.BTN_WID - 4, command=self.cmp_close)
        self.cmp_close_btn.grid(row=0, column=0, padx=2)
        ''' Create Treeview. If no differences give message and return '''
        #ret = self.cmp_populate_tree()
        #print("self.cmp_populate_tree() return value:", ret)  # True (it's working)
        if not self.cmp_populate_tree():
            self.cmp_close()  # Files are identical
            return
        ''' 🗘  Update differences Button u1f5d8 🗘'''
        self.update_differences_btn = tk.Button(frame3, width=g.BTN_WID + 4,
                                                text="🗘  Update differences",
                                                command=self.cmp_update_files)
        self.update_differences_btn.grid(row=0, column=1, padx=2)

        if self.cmp_top_is_active is False:
            return
        self.cmp_tree.update_idletasks()

    # noinspection PyUnusedLocal Required for *args when binding <Escape>
    def cmp_close(self, *args):
        """ Close Compare location treeview """
        if not self.cmp_top_is_active:
            return  # Already closed
        self.cmp_top_is_active = False
        if self.tt and self.cmp_top:
            if self.tt.check(self.cmp_top):  # Were tooltips created?
                self.tt.close(self.cmp_top)  # Close tooltips under top level
        self.cmp_top.destroy()  # Close the treeview window
        self.cmp_top = None
        return True

    def cmp_populate_tree(self):

        """ Add Artist, Album and Song to treeview self.cmp_tree.
            Similar to add_items() in Music Location Tree

            TODO: Rest of mserve is unresponsive while this is running.
                  Take all compare location code and make new python module
                  called compare.py imported as cmp

            It takes 1.5 hour to stat 4,000 songs on phone mounted on sshfs
            over Wi-Fi. Speed up with: https://superuser.com/questions/344255/
            faster-way-to-mount-a-remote-file-system-than-sshfs

            -o auto_cache,reconnect,defer_permissions
            -o Ciphers=aes128-ctr -o Compression=no
        :returns True: When locations are different
        """
        # How many path separators '/' are there in source and target?
        start_dir_sep = self.open_topdir.count(os.sep)
        #target_dir_sep = self.cmp_target_dir.count(os.sep) - 1
        self.src_mt = ModTime(self.open_code)
        self.trg_mt = ModTime(self.act_code)
        self.src_fc = self.FileControl(self.cmp_top, self.info, 
                                       get_thread=self.get_thread_func)
        self.trg_fc = self.FileControl(self.cmp_top, self.info, 
                                       get_thread=self.get_thread_func)

        LastArtist = ""
        LastAlbum = ""
        CurrAlbumId = ""  # When there are no albums?
        CurrArtistId = ""

        for i, os_name in enumerate(self.fake_paths):
            self.cmp_top.update()  # Allow close button to abort right away

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
                return False  # Closing down, False indicates no differences

            ''' Build full song path from self.fake_paths '''
            src_path = os_name
            src_path = src_path.replace(os.sep + g.NO_ARTIST_STR, '')
            src_path = src_path.replace(os.sep + g.NO_ALBUM_STR, '')

            # os.stat gives us all of file's attributes
            src_stat = os.stat(src_path)
            src_size = src_stat.st_size
            src_mtime = float(src_stat.st_mtime)

            # Get target list's size and mtime
            trg_path = src_path.replace(self.open_topdir, self.cmp_target_dir)
            if not os.path.isfile(trg_path):
                self.cmp_tree.see(CurrAlbumId)
                ''' TODO: build lists of '''
                self.cmp_trg_missing.append(trg_path)
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
                    return False  # Closing down, False indicates no differences
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

            converted = float(src_size) / float(g.CFG_DIVISOR_AMT)
            # Aug 4/23 - DEC_PLACE used to be 1 now it's 0
            src_fsize = '{:n}'.format(round(converted, g.CFG_DECIMAL_PLACES + 2))
            converted = float(trg_size) / float(g.CFG_DIVISOR_AMT)
            trg_fsize = '{:n}'.format(round(converted, g.CFG_DECIMAL_PLACES + 2))
            # Format date as "Abbreviation - 99 Xxx Ago"
            src_ftime = tmf.ago(float(src_stat.st_mtime))
            trg_ftime = tmf.ago(float(trg_stat.st_mtime))

            ''' Insert song into comparison treeview and show on screen '''
            self.cmp_tree.insert(CurrAlbumId, "end", iid=str(i), text=Song,
                                 values=(src_ftime, trg_ftime, src_fsize, trg_fsize, action,
                                         float(src_stat.st_mtime), float(trg_stat.st_mtime)),
                                 tags=("Song",))
            self.cmp_tree.see(str(i))

            # Sept 23 2020 - Treeview doesn't scroll after update button added?
            # After clicking update differences can you click it again?
            if self.cmp_top_is_active is False:
                return False  # Closing down, False indicates no differences
            self.cmp_tree.update_idletasks()

            # do_debug_steps += 1
            # if do_debug_steps == 10000: break     # Set to short for testing

        ''' Prune tree - Albums with no songs, then artists with no albums '''
        for artist in self.cmp_tree.get_children():
            album_count = 0
            for album in self.cmp_tree.get_children(artist):
                if self.cmp_top_is_active is False:
                    return False  # Closing down, False indicates no differences
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
            print("self.cmp_top_is_active:", self.cmp_top_is_active)
            print("self.main_top:", self.main_top)
            print("self.parent:", self.parent)
            title = "File differences found"
            text = "This message only shown to figure out why windows closing."
            self.out_cast_show(title, text)
            return True
        else:
            title = "Files identical"
            text = "Files common to both locations are identical."
            self.out_fact_show(title, text)
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
                    self.cmp_top.update_idletasks()
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

            NOTE: self.open_topdir may become target_path and target_dir may become
                  source_path after deciphering arrow
        """

        # action = 'Copy Trg -> Src (Size)', 'Timestamp Src -> Trg', etc.
        action = self.cmp_tree.item(iid)['values'][4]  # 6th treeview column
        src_mtime = self.cmp_tree.item(iid)['values'][5]
        trg_mtime = self.cmp_tree.item(iid)['values'][6]
        # Extract real source path from treeview display e.g. strip <No Album>
        src_path = self.real_path(int(iid))
        # replace source topdir with target topdir for target full path
        trg_path = src_path.replace(self.open_topdir, self.cmp_target_dir)

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

    def sneaky_sleep(self):
        """ Sneaky_sleep sleeps as little as possible.
            The objective is to allow 30 fps response time for music player.
            Start by sleeping if refresh_thread takes 10 ms then 20 ms of
            work can be done between calls. If refresh_thread only takes 2 ms
            then 28 ms of work can be done.

        """
        print(self.top)



# End of location.py
