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
#       July 22 2023 - Create Locations() class
#
#==============================================================================
import stat

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
import shutil
import pickle
import time
import datetime
from collections import OrderedDict

import global_variables as g
if g.USER is None:
    print('location.py was forced to run g.init()')
    g.init()
import message  # Dialog Box messages - ShowInfo(), AskQuestion()
import monitor  # Get Locations() class window geometry
import image as img  # Taskbar thumbnail image for Locations() window
import timefmt as tmf  # "date - ago" formatting for Locations()
import toolkit  # Data dictionary driven treeview for Locations()
import sql  # SQL Locations Table for Locations()

# Define ~/.../mserve/ directory
MSERVE_DIR = g.MSERVE_DIR
# print("MSERVE_DIR:", MSERVE_DIR)

# only files in USER_DATA_DIR/mserve/
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
    test_passed = test_host_up(host)
    
    # Wake up host if not on-line
    #if not wakecmd == "" or not wakecmd.isspace():
    if wakecmd.strip():
        if test_passed is True:
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
            if test_passed is True:
                break
            time.sleep(.1)

            # We don't want error messages in our result use 2>/dev/null
            result = os.popen(testcmd + ' 2>/dev/null').read().strip()
            if len(result) > 4:
                test_passed = True
                tests = i
    else:
        test_passed = True

    if test_passed is False:
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
            dtb.update("location.test() errors mounting:" + result)
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

        ''' All Locations work fields - Set on program start and saving changes '''
        self.all_codes = []  # "L001", "L002", etc... can be holes
        self.all_names = []  # Names matching all_codes
        self.all_topdir = []  # Top Directories matching all_codes
        self.names_for_loc = []  # Names sorted for this location
        self.names_all_loc = []  # Names sorted for all locations
        self.loc_list = []
        self.loc_dict = {}

        self.old_name = None  # Name before we changed it - Deprecate names soon.
        self.name = None  # Location name that is being played right now
        self.last_number_str = None  # Before operation started L01, etc.
        self.curr_number_str = None  # After operation completed L01, etc.
        self.audit_message = None  # Printable text of what was done.

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

        ''' Extended active variables '''
        self.act_host_is_mounted = True  # Assume local storage by default

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

        self.artwork = None  # Image of hardware, E.G. Server, Laptop, Cell
        self.art_width = None
        self.art_height = 200  # Width will be calculated proportionally
        self.disp_image = None  # Image scaled to height of 200
        self.art_label = None
        self.close_button = None
        self.test_button = None  # Test host
        self.apply_button = None

        ''' Test Window and fields '''
        self.test_top = None  # tk.Toplevel to Test Host
        self.test_frame = None  # tk.Frame holding CustomScrolledText
        self.test_box = None  # CustomScrolledText with test results


class Locations(LocationsCommonSelf):
    """ Usage:

        lcs = Locations(make_sorted_list)

        Called from mainline when relevant instances aren't ready to be passed.
        They are registered later with:

            lcs.register_parent(root / self.lib_top)
            lcs.register_tt(self.tt)
            lcs.register_thread(self.get_refresh_thread)
            lcs.register_info(self.info)
            lcs.register_menu(self.enable_lib_menu)
            lcs.register_pending(self.get_pending_cnt_total)
            lcs.register_NEW(NEW_LOCATION)

        Functions:
    
            - view() - Show existing Locations in treeview
            - new() - Prompt for Location variables and add to database
            - open() - Pick existing Location and play music
            - edit() - Edit existing location and update database
            - load_last_location() - Reopen location last used

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
        self.info = None  # InfoCentre()
        self.apply_callback = None
        self.play_close = None  # Main music playing window to close down
        self.enable_lib_menu = None
        self.tt = None  # Tooltips pool for buttons
        self.get_thread_func = None  # E.G. self.get_refresh_thread()
        self.thread = None  # E.G. self.get_refresh_thread()
        self.display_lib_title = None  # Rebuild lib_top menubar

        ''' Opened Location variables - DON'T TOUCH !!! '''
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
        self.open_row_id = None

        self.open_host_is_mounted = True  # Assume local storage by default

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

    def register_get_thread(self, get_thread):
        """ Register get_refresh_thread after it's declared in mserve.py """
        self.get_thread_func = get_thread  # E.G. self.get_refresh_thread()

    def register_menu(self, enable_menu_func):
        """ Register get_refresh_thread after it's declared in mserve.py """
        self.enable_lib_menu = enable_menu_func  # E.G. self.get_refresh_thread()

    def register_pending(self, get_pending):
        """ Register get_pending_cnt_total after it's declared in mserve.py """
        self.get_pending = get_pending  # E.G. self.get_refresh_thread()

    def display_main_window(self, name=None):
        """ Mount window with Location Treeview or placeholder text when none.
            :param name: "New Location", "Open Location", etc.
        """
        self.pending_counts = self.get_pending()
        ''' Save current name to old_name to make decisions when different. '''
        self.old_name = self.name

        ''' Rebuild location changes since last time '''
        self.build_locations()

        ''' Get saved geometry for Locations() '''
        self.main_top = tk.Toplevel()  # Locations top level
        geom = monitor.get_window_geom('locations')
        self.main_top.geometry(geom)
        self.main_top.minsize(width=g.BTN_WID * 10, height=g.PANEL_HGT * 10)
        name = name if name is not None else "Locations"
        self.main_top.title(name + " - mserve")
        self.main_top.configure(background="Gray")
        self.main_top.columnconfigure(0, weight=1)
        self.main_top.rowconfigure(0, weight=1)
        ''' After top created, disable all File Menu options for locations '''
        self.enable_lib_menu()
        ''' Set program icon in taskbar '''
        img.taskbar_icon(self.main_top, 64, 'white', 'lightskyblue', 'black')
        ''' Create master frame '''
        self.main_frame = tk.Frame(self.main_top, borderwidth=g.BTN_BRD_WID,
                                   relief=tk.RIDGE)
        self.main_frame.grid(sticky=tk.NSEW)
        self.main_frame.columnconfigure(0, weight=0)
        self.main_frame.columnconfigure(1, weight=0)
        self.main_frame.columnconfigure(2, weight=3)  # Data entry fields
        self.main_frame.rowconfigure(0, weight=1)
        ms_font = (None, g.MON_FONTSIZE)

        ''' Instructions when no locations have been created yet. 
            TODO: When "New" location is picked, changed message below.
        '''
        if not self.text:  # If text wasn't passed as a parameter use default
            self.text = "\nNo Locations have been created yet.\n\n" + \
                        "After Locations have been created, they will\n" + \
                        "appear in this spot.\n\n" + \
                        "You can create a location by selecting\n" + \
                        "the 'New Location' option from the 'File' \n" + \
                        "dropdown menu bar.\n"

        if len(self.all_codes) == 0:
            # No locations have been created yet
            tk.Label(self.main_frame, text=self.text, justify="left", font=ms_font) \
                .grid(row=0, column=0, columnspan=4, sticky=tk.W, padx=5)
        else:
            self.populate_loc_tree()  # Paint treeview of locations

        ''' Shared function between display_main_window() and test_host() '''
        self.display_location_details(self.main_frame, name)

        self.input_active = False  # Screen fields are 'readonly'

        ''' Close Button - NOTE: This calls reset() function !!! '''
        self.close_button = tk.Button(self.main_frame, text="✘ Close",
                                      width=g.BTN_WID2 - 4, command=self.reset)
        self.close_button.grid(row=14, column=0, padx=5, pady=5, sticky=tk.W)
        self.tt.add_tip(self.close_button, "Ignore changes and return.",
                        anchor="nw")
        self.main_top.bind("<Escape>", self.reset)
        self.main_top.protocol("WM_DELETE_WINDOW", self.reset)

        ''' Help Button - https://www.pippim.com/programs/mserve.html#locations '''
        ''' 🔗 Help - Videos and explanations on pippim.com '''

        help_text = "Open new window in default web browser for\n"
        help_text += "videos and explanations on using this screen.\n"
        help_text += "https://www.pippim.com/programs/mserve.html#\n"

        help = tk.Button(self.main_frame, text="🔗 Help", width=g.BTN_WID2 - 4,
                         font=ms_font, command=lambda: g.web_help("HelpLocations"))
        help.grid(row=14, column=1, padx=5, pady=5, sticky=tk.W)
        self.tt.add_tip(help, help_text, anchor="nw")

        ''' Test Host Button '''
        if self.act_host:
            self.test_button = tk.Button(self.main_frame, text="✔ " + text,
                                         width=g.BTN_WID2 - 2, command=self.test)
            self.test_button.grid(row=14, column=2, padx=5, pady=5, sticky=tk.W)
            self.tt.add_tip(self.test_button, text + " Location and return.",
                            anchor="ne")

        ''' Apply Button '''
        action = name.split(" Location")[0]
        if not action == "View":
            text = action
            if action == "New":
                text = "Add"
            if action == "Edit":
                text = "Save"
            self.apply_button = tk.Button(self.main_frame, text="✔ " + text,
                                          width=g.BTN_WID2 - 2, command=self.apply)
            self.apply_button.grid(row=14, column=3, padx=5, pady=5, sticky=tk.W)
            self.tt.add_tip(self.apply_button, text + " Location and return.",
                            anchor="ne")
            self.main_top.bind("<Return>", self.apply)

        ''' Refresh screen '''
        if self.main_top:  # May have been closed above.
            self.main_top.update_idletasks()

    def display_test_window(self, cover_top=True):
        """ Mount test host window """
        ''' Use main_window geometry for Test Host window '''
        self.test_top = tk.Toplevel()  # Locations top level
        if cover_top:
            geom = monitor.get_window_geom_raw(self.main_top)
            print("display_test_window:", geom)
        else:
            ''' Need to override for first time '''
            geom = monitor.get_window_geom('locations')

        self.test_top.geometry(geom)  # Cover up Locations Window
        self.test_top.title("Test Host - mserve")
        self.test_top.configure(background="Gray")
        self.test_top.columnconfigure(0, weight=1)
        self.test_top.rowconfigure(0, weight=1)

        ''' Set program icon in taskbar '''
        img.taskbar_icon(self.test_top, 64, 'white', 'lightskyblue', 'black')
        ''' Create master frame '''
        self.test_frame = tk.Frame(self.test_top, borderwidth=g.BTN_BRD_WID,
                                   relief=tk.RIDGE)
        self.test_frame.grid(sticky=tk.NSEW)
        self.test_frame.columnconfigure(0, weight=0)
        self.test_frame.columnconfigure(1, weight=0)
        self.test_frame.columnconfigure(2, weight=3)  # Data entry fields
        self.test_frame.rowconfigure(0, weight=1)
        ms_font = (None, g.MON_FONTSIZE)

        ''' Create treeview frame with scrollbars '''
        scroll_frame = tk.Frame(self.main_frame, bg="olive", relief=tk.RIDGE)
        scroll_frame.grid(sticky=tk.NSEW, columnspan=4)
        scroll_frame.columnconfigure(0, weight=1)
        scroll_frame.rowconfigure(0, weight=1)

        ''' Custom Scrolled Text Box '''
        Quote = "Testing Host: " + self.act_host + "\n"
        self.test_box = toolkit.CustomScrolledText(
            scroll_frame, state="normal", font=bs_font, borderwidth=15, relief=tk.FLAT)
        self.test_box.insert("end", Quote)
        self.test_box.grid(row=0, column=1, padx=3, pady=3, sticky=tk.NSEW)
        #tk.Grid.rowconfigure(test_frame, 0, weight=1)  # TODO
        #tk.Grid.columnconfigure(test_frame, 1, weight=1)

        self.test_box.tag_config('red', foreground='Red')
        self.test_box.tag_config('blue', foreground='Blue')
        self.test_box.tag_config('green', foreground='Green')
        self.test_box.tag_config('black', foreground='Black')
        self.test_box.tag_config('yellow', background='Yellow')
        self.test_box.tag_config('cyan', background='Cyan')
        self.test_box.tag_config('magenta', background='Magenta')

        self.test_box.highlight_pattern(self.act_host, 'Green')

        self.test_box.config(tabs=("2m", "20m", "40m"))
        self.test_box.tag_configure("margin", lmargin1="2m", lmargin2="40m")
        # Fix Control+C  https://stackoverflow.com/a/64938516/6929343
        self.test_box.bind("<Button-1>", lambda event: self.test_box.focus_set())

        ''' Shared function between display_main_window() and test_host() '''
        self.display_location_details(self.test_frame)

        self.input_active = False  # Screen fields are 'readonly'

        ''' Close Button - NOTE: This calls reset() function !!! '''
        self.close_button = tk.Button(self.test_frame, text="✘ Close",
                                      width=g.BTN_WID2 - 4, command=self.end_test)
        self.close_button.grid(row=14, column=0, padx=5, pady=5, sticky=tk.W)
        self.tt.add_tip(self.close_button, "End test of Host: " + self.act_host,
                        anchor="nw")
        self.test_top.protocol("WM_DELETE_WINDOW", self.end_test)

        ''' Refresh screen '''
        if self.test_top:  # May have been closed above.
            self.test_top.update_idletasks()

    def end_test(self):
        """ Close Test Host Window """
        self.test_top.destroy()

    def display_location_details(self, frame, name=None):
        """ Shared by display_main_window() and Host testing functions """

        ms_font = (None, g.MON_FONTSIZE)  # Unfortunately repeat again

        ''' Artwork image spanning 3 rows '''
        self.make_default_image()

        ''' Placeholder for Image '''
        self.art_label = tk.Label(frame, borderwidth=0,
                                  image=self.disp_image, font=ms_font)
        self.art_label.grid(row=1, rowspan=4, column=0, sticky=tk.W,
                            padx=5, pady=5)

        ''' When testing host, there are no Treeview rows above '''
        if name:
            text = "🡅 🡅  Click on row to " + name + "  🡅 🡅"
        else:
            text = "Testing Host"
        self.fld_intro = tk.Label(frame, text=text, font=ms_font)
        self.fld_intro.grid(row=1, column=1, columnspan=3, stick=tk.W)

        ''' Location Name '''
        tk.Label(frame, text="Location name:",
                 font=ms_font).grid(row=2, column=1, sticky=tk.W)
        self.fld_name = tk.Entry(frame, textvariable=self.scr_name,
                                 state='readonly', font=ms_font)
        self.fld_name.grid(row=2, column=2, columnspan=2, sticky=tk.EW,
                           padx=5, pady=5)
        self.scr_name.set("")  # Clear left over from last invocation

        ''' Music Top Directory readonly except for 'New' button? '''
        tk.Label(frame, text="Music Top Directory:",
                 font=ms_font).grid(row=3, column=1, sticky=tk.W)
        self.fld_topdir = tk.Entry(
            frame, textvariable=self.scr_topdir, state='readonly',
            font=ms_font)
        self.fld_topdir.grid(row=3, column=2, columnspan=2, sticky=tk.EW,
                             padx=5, pady=5)
        self.fld_topdir.bind("<Button>", self.get_topdir)
        self.scr_topdir.set("")  # Clear left over from last invocation

        ''' Host Name '''
        tk.Label(frame, text="Optional Host Name:",
                 font=ms_font).grid(row=4, column=1, sticky=tk.W)
        self.fld_host = tk.Entry(
            frame, textvariable=self.scr_host, state='readonly',
            font=ms_font)
        self.fld_host.grid(row=4, column=2, columnspan=2, sticky=tk.EW,
                           padx=5, pady=5)
        self.scr_host.set("")  # Clear left over from last invocation

        ''' Host Wakeup Command '''
        tk.Label(frame, text="Command to wake up sleeping Host:",
                 font=ms_font).grid(row=5, column=0, columnspan=2,
                                    sticky=tk.W, padx=5)
        self.fld_wakecmd = tk.Entry(
            frame, textvariable=self.scr_wakecmd, state='readonly',
            font=ms_font)
        self.fld_wakecmd.grid(row=5, column=2, columnspan=2, sticky=tk.EW,
                              padx=5, pady=5)
        self.scr_wakecmd.set("")  # Clear left over from last invocation

        ''' Test if Host is awake Command '''
        tk.Label(frame, text="Command to test if Host is awake:",
                 font=ms_font).grid(row=6, column=0, columnspan=2,
                                    sticky=tk.W, padx=5)
        self.fld_testcmd = tk.Entry(
            frame, textvariable=self.scr_testcmd, state='readonly',
            font=ms_font)
        self.fld_testcmd.grid(row=6, column=2, columnspan=2, sticky=tk.EW,
                              padx=5, pady=5)
        self.scr_testcmd.set("")  # Clear left over from last invocation

        ''' Number of times to repeat test every .1 second '''
        tk.Label(frame, text="Maximum tests every 0.1 second:",
                 font=ms_font).grid(row=7, column=0, columnspan=2,
                                    sticky=tk.W, padx=5)
        self.fld_testrep = tk.Entry(
            frame, textvariable=self.scr_testrep, state='readonly',
            font=ms_font)
        self.fld_testrep.grid(row=7, column=2, columnspan=2, sticky=tk.EW,
                              padx=5, pady=5)
        self.scr_testrep.set(0)  # Clear left over from last invocation

        ''' Mount Host's Music Partition Command  '''
        tk.Label(frame, text="Command to mount Music on Host:",
                 font=ms_font).grid(row=8, column=0, columnspan=2,
                                    sticky=tk.W, padx=5)
        self.fld_mountcmd = tk.Entry(
            frame, textvariable=self.scr_mountcmd, state='readonly',
            font=ms_font)
        self.fld_mountcmd.grid(row=8, column=2, columnspan=2, sticky=tk.EW,
                               padx=5, pady=5)
        self.scr_mountcmd.set("")  # Clear left over from last invocation

        ''' Touch Host Command  '''
        tk.Label(frame, text="Command to prevent Host sleeping:",
                 font=ms_font).grid(row=9, column=0, columnspan=2,
                                    sticky=tk.W, padx=5)
        self.fld_touchcmd = tk.Entry(
            frame, textvariable=self.scr_touchcmd, state='readonly',
            font=ms_font)
        self.fld_touchcmd.grid(row=9, column=2, columnspan=2, sticky=tk.EW,
                               padx=5, pady=5)
        self.scr_touchcmd.set("")  # Clear left over from last invocation

        ''' Touch Minutes  '''
        tk.Label(frame, text="Send prevent sleep every x minutes:",
                 font=ms_font).grid(row=10, column=0, columnspan=2,
                                    sticky=tk.W, padx=5)
        self.fld_touchmin = tk.Entry(
            frame, textvariable=self.scr_touchmin, state='readonly',
            font=ms_font)
        self.fld_touchmin.grid(row=10, column=2, columnspan=2, sticky=tk.EW,
                               padx=5, pady=5)
        self.scr_touchmin.set(0)  # Clear left over from last invocation

        ''' Comments '''
        tk.Label(frame, text="Optional Comments:",
                 font=ms_font).grid(row=11, column=0, columnspan=2,
                                    sticky=tk.W, padx=5)
        self.fld_comments = tk.Entry(
            frame, textvariable=self.scr_comments, state='readonly',
            font=ms_font)
        self.fld_comments.grid(row=11, column=2, columnspan=2, sticky=tk.EW,
                               padx=5, pady=5)
        self.scr_comments.set("")  # Clear left over from last invocation

        ''' Image path - not displayed when testing host '''
        if name:
            tk.Label(frame, text="Optional Location Device Image:",
                     font=ms_font).grid(row=12, column=0, columnspan=2,
                                        sticky=tk.W, padx=5)
            self.fld_image_path = tk.Entry(
                frame, textvariable=self.scr_image_path, state='readonly',
                font=ms_font)
            self.fld_image_path.grid(row=12, column=2, columnspan=2, sticky=tk.EW,
                                     padx=5, pady=5)
            self.scr_image_path.set("")  # Clear left over from last invocation


    def populate_loc_tree(self):
        """ Use custom Data Dictionary routines for managing treeview. """

        ''' Data Dictionary and Treeview column names '''
        location_dict = sql.location_treeview()  # Heart of Data Dictionary
        columns = ("code", "name", "topdir")
        toolkit.select_dict_columns(columns, location_dict)

        ''' Create treeview frame with scrollbars '''
        tree_frame = tk.Frame(self.main_frame, bg="olive", relief=tk.RIDGE)
        tree_frame.grid(sticky=tk.NSEW, columnspan=4)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        self.loc_view = toolkit.DictTreeview(
            location_dict, self.main_top, tree_frame, columns=columns,
            highlight_callback=self.highlight_callback)

        ''' Override generic column heading names for Location usage '''
        #self.loc_view.tree.heading('code', text='Code')
        self.loc_view.tree.heading('name', text='Location Name')
        #self.loc_view.tree.heading('topdir', text='Music Top Directory')
        self.loc_view.tree["displaycolumns"] = columns  # hide row_id

        ''' Treeview select item with button clicks '''
        # Moving columns needs work and probably isn't even needed
        toolkit.MoveTreeviewColumn(self.main_top, self.loc_view.tree,
                                   row_release=self.loc_button_click)
        self.loc_view.tree.bind("<Button-1>", self.loc_button_click)
        self.loc_view.tree.bind("<Button-3>", self.loc_button_click)
        self.loc_view.tree.bind("<Double-Button-1>", self.apply)
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

        number_str = self.loc_view.tree.identify_row(event.y)
        if not number_str:
            return  # clicked on empty row

        if self.state == "new" or self.state == "save_as":
            self.thread = self.get_thread_func()  # FIX huge problem when play_close()
            # cannot use enable_input because rename needs to pick old name first
            text = "Cannot pick an old location when new location name required.\n\n" + \
                   "Enter a new Location name and Top Directory below."
            message.ShowInfo(self.main_top, "Existing locations for reference only!",
                             text, icon='warning', thread=self.thread)
        else:
            ''' Highlight row clicked '''
            toolkit.tv_tag_remove_all(self.loc_view.tree, 'loc_sel')
            toolkit.tv_tag_add(self.loc_view.tree, number_str, 'loc_sel')

            if not self.read_location(number_str):
                print("location.py Locations.loc_button_click()",
                      "error reading location:", number_str)
                return
            
            ''' Format image at 150 pix height '''
            if self.act_image_path:
                # Try to build photo image into self.disp_image variable
                self.disp_image = self.make_image_from_path(self.act_image_path)
                if not self.disp_image:
                    # Could not convert file to TK photo image format
                    self.make_default_image()
            else:
                # No image path use generic image
                self.make_default_image()
            self.art_label.configure(image=self.disp_image)

            self.format_intro_line()  # Format introduction line
            self.scr_name.set(self.act_name)
            self.scr_topdir.set(self.act_topdir)
            self.scr_host.set(self.act_host)
            self.scr_wakecmd.set(self.act_wakecmd)
            self.scr_testcmd.set(self.act_testcmd)
            self.scr_testrep.set(self.act_testrep)
            self.scr_mountcmd.set(self.act_mountcmd)
            self.scr_touchcmd.set(self.act_touchcmd)  # Was activecmd
            self.scr_touchmin.set(self.act_touchmin)  # Was activemin
            self.scr_comments.set(self.act_comments)  # New
            self.scr_image_path.set(self.act_image_path)  # New

            self.main_top.update_idletasks()

    def format_intro_line(self):
        """ Format introduction line """
        text = ""
        if self.act_code:
            text = "Code: " + self.act_code
            if self.act_modify_time:
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
                    self.act_modify_time = 0.0
                    self.total_bytes = 0
                    self.free_bytes = 0

                text += "  | Last modified: "
                text += tmf.ago(self.act_modify_time)
                if not self.act_host:
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
        #thread = self.get_thread_func()
        #new_topdir = message.AskDirectory(
        #    parent=self.main_top, initialdir=self.act_topdir,
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

            self.info.cast(title + "\n\n" + text, 'error')
            thread = self.get_thread_func()
            message.ShowInfo(self.main_top, title, text, icon='error', thread=thread)
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
        image = img.make_image("Device\nImage", image_w=150, image_h=150)
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
        self.info.cast(title + "\n\n" + text, 'error')
        thread = self.get_thread_func()
        message.ShowInfo(self.main_top, title, text,
                         icon='error', thread=thread)
        return False

    def highlight_callback(self, number_str):
        """
        As lines are highlighted in treeview, this function is called.
        :param number_str: Location number used as iid inside treeview
        :return: None
        """
        # print("number_str:", number_str)
        pass

    def build_locations(self):
        """ Get ALL configuration history rows for Type = 'location'
            Create sorted list of names for current location. Called
            each time Locations.function() used.
        """
        ''' Lists already declared in Init but must reset between calls 
            Put this into newly created CommonSelf()
        '''
        #self.build_fake_locations()  # Create sample data

        LocationsCommonSelf.__init__(self)  # Define self. variables

        self.all_codes = []  # "L001", "L002", etc... can be holes
        self.all_names = []  # Names matching all_codes
        self.all_topdir = []  # Descriptions matching all_codes
        self.names_for_loc = []  # Names sorted for this location
        self.names_all_loc = []  # Names sorted for all locations
        self.loc_list = []
        ''' Read all locations from SQL Location Table into work lists '''
        for row in sql.loc_cursor.execute("SELECT * FROM Location"):
            d = dict(row)
            self.make_act_from_sql_dict(d)
            self.loc_dict = OrderedDict(d)
            self.loc_list.append(self.loc_dict)
            self.all_codes.append(self.act_code)
            self.all_names.append(self.act_name)
            self.all_topdir.append(self.act_topdir)
            self.names_all_loc.append(self.act_name)
            #if self.act_code == DICT['iid']:  # Not sure DICT['iid'] is error???
            #    self.names_for_loc.append(self.act_name)

        self.names_all_loc.sort()
        self.names_for_loc.sort()

    @staticmethod
    def build_fake_locations():
        """ Use existing LIST to create fake SQL Location Table rows
        self.act_code.set(loc_dict['code'])  # Replacement for 'iid'
        self.act_name.set(loc_dict['name'])
        self.act_modify_time.set(loc_dict['modify_time'])  # New
        self.act_image_path.set(loc_dict['image_path'])  # New
        self.act_mount_point.set(loc_dict['mount_point'])  # New
        self.act_topdir.set(loc_dict['topdir'])
        self.act_host.set(loc_dict['host'])
        self.act_wakecmd.set(loc_dict['wakecmd'])
        self.act_testcmd.set(loc_dict['testcmd'])
        self.act_testrep.set(loc_dict['testrep'])
        self.act_mountcmd.set(loc_dict['mountcmd'])
        self.act_touchcmd.set(loc_dict['touch_cmd'])  # Replaces 'activecmd'
        self.act_touchmin.set(loc_dict['touch_min'])  # Replaces 'activemin'
        self.act_comments.set(loc_dict['comments'])  # New
        """
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
                d['mountcmd'], d['activecmd'], d['activemin'], "Comments")

    @staticmethod
    def get_dict_by_dirname(dirname):
        """ Look up location dictionary using top directory path """
        stripped_last = dirname.rstrip(os.sep)
        for i, dir_dict in enumerate(LIST):
            topdir = dir_dict['topdir'].rstrip(os.sep)
            if topdir == stripped_last:
                return dir_dict  # DICT will be matching dirname

        dir_dict = {}  # No match found DICT empty
        return dir_dict

    def new(self):
        """ Called by lib_top File Menubar "New Location"
            In future may be called by mainline when no location found.
            If new songs are pending, do not allow location to open
        """
        ''' Music Location Tree checkboxes pending to apply? '''
        if self.get_pending:  # 'None' = MusicLocationTree not called yet.
            if self.get_pending():  # lib_top.tree checkboxes not applied?
                return  # We are all done. No window, no processing, nada

        LocationsCommonSelf.__init__(self)  # Define self. variables
        self.state = 'new'
        self.display_main_window("New Location")
        self.enable_input()

        # After "Add" button click, create the subdirectory - '.../mserve/L009'

    def enable_input(self):
        """ Turn on input fields for 'new', 'edit' and 'open'

            From this answer:https://stackoverflow.com/a/4453715/6929343
            def find_mount_point(path):
                path = os.path.abspath(path)
                while not os.path.ismount(path):
                    path = os.path.dirname(path)
                return path

            After getting mount point can find out there are no files or
            directories and know nothing is mounted yet.
            Use the 100/10 test described below. Or will theount test file
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

        ''' If len(last_playlist) > 0: error can't change TopDir. '''
        count = 1  # Count of favorites stored in L009. When 0 can change TopDir
        if self.state == 'new' or self.state == 'edit' and count == 0:
            self.fld_topdir['state'] = 'normal'  # Allow input

        self.fld_host['state'] = 'normal'  # TODO: Host can be it's own class
        self.fld_wakecmd['state'] = 'normal'  # Requires pycharm add to dictionary
        self.fld_testcmd['state'] = 'normal'
        self.fld_testrep['state'] = 'normal'
        self.fld_mountcmd['state'] = 'normal'
        self.fld_touchcmd['state'] = 'normal'  # Replaces activecmd
        self.fld_touchmin['state'] = 'normal'  # Replaces activemin
        self.fld_comments['state'] = 'normal'
        self.fld_image_path['state'] = 'normal'
        self.fld_image_path.bind("<Button>", self.get_act_image_path)


    def edit(self):
        """Called by lib_top File Menubar "Edit Location"
            If new songs are pending, do not allow location to open """
        if self.get_pending:  # 'None' = MusicLocationTree not called yet.
            ''' Music Location Tree checkboxes pending to apply? '''
            if self.get_pending():  # lib_top.tree checkboxes not applied?
                return  # We are all done. No window, no processing, nada

        LocationsCommonSelf.__init__(self)  # Define self. variables
        self.state = 'edit'
        self.display_main_window("Edit Location")
        self.enable_input()

    def rename(self):
        """ Called by lib_top File Menubar "Rename Location"
            TODO: Probably want to drop this function
        """
        LocationsCommonSelf.__init__(self)  # Define self. variables
        self.state = 'rename'
        self.display_main_window("Rename Location")
        self.enable_input()

    def delete(self):
        """ Called by lib_top File Menubar "Delete Location" """
        LocationsCommonSelf.__init__(self)  # Define self. variables
        self.state = 'delete'
        self.display_main_window("Delete Location")

    def open(self):
        """ 
            Called by main() prior to make_sorted_list()
            Called by lib_top File Menubar "Open Location"
            If new songs are pending, do not allow location to open
        """
        ''' Music Location Tree checkboxes pending to apply? '''
        if self.get_pending:  # 'None' = MusicLocationTree not called yet.
            if self.get_pending():  # lib_top.tree checkboxes not applied?
                return  # We are all done. No window, no processing, nada

        LocationsCommonSelf.__init__(self)  # Define self. variables
        self.state = 'open'
        self.display_main_window("Open Location and Play")

    def view(self):
        """ View Locations """
        LocationsCommonSelf.__init__(self)  # Define self. variables
        self.state = 'view'
        self.display_main_window("View Locations")

    def close(self):
        """ Called by mserve shutdown.
            When Location Maintenance window closes the self.reset() is used. 
        """

        self.state = 'close'
        sql.save_config('location', 'last', self.open_code, self.open_name,
                        self.open_topdir, Comments="Last location opened.")
        '''
        if self.validate_location():  # Check if changes pending & confirm
            #self.curr_number_str = None
            #self.name = None
            #self.display_lib_title()
            return True
        else:
            return False
        '''
        
    def load_last_location(self):
        """ Called by mserve.py early in startup process. No lib_top yet. """

        """ CURRENT CODE from mserve.py:

    def load_last_location():
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
        """
        self.state = 'load' 

        ''' Retrieve SQL History for last location used. '''
        hd = sql.get_config('location', 'last')

        if hd is None:
            print("The last location in SQL History Table wasn't found:",
                  "Type='location', Action='last")
            self.NEW_LOCATION = True
            return 1

        ''' sql.save_config('location', 'last', self.open_code, self.open_name,
                            self.open_topdir, Comments=comments) '''
        d = sql.loc_read(hd['SourceMaster'])
        if d is None:
            print("The last location used for mserve.py has been deleted:",
                  hd['SourceMaster'])
            self.NEW_LOCATION = True
            return 2

        self.make_open_from_sql_dict(d)

        # Display keep awake values
        if self.open_touchcmd:
            print('Keep awake command:', self.open_touchcmd,
                  'every', self.open_touchmin, 'minutes.')

        # Check if host name not blank and then wake it up and validate topdir
        if self.validate_host(self.open_code):  # No toplevel for parm 2
            return 0

        ''' See if last location path and see if it is mounted '''
        if not os.path.isdir(self.open_topdir):
            print('Location contains invalid or off-line directory:', START_DIR)
            return 3

        return 0  # 0 = success
    
    def read_location(self, number_str):
        """ Use location number to read SQL Location Row into work fields """
        d = sql.loc_read(number_str)
        if d is None:
            return None

        ''' Current Location work fields - from SQL Location Table Row '''
        self.make_act_from_sql_dict(d)

        return True

    def save_location(self):
        """ Save Location """
        pass

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
        """
        When lib_top_tree has check boxes for adding/deleting songs that
        haven't been saved, cannot open location or create new location.

        :return: True if pending additions/deletions need to be applied
        """
        pending = self.get_pending()
        if pending == 0:
            return False

        # self.main_top window hasn't been created so use self.parent instead
        text = "Checkboxes in Music Location have added songs or\n" + \
               "removed songs. These changes have not been saved to\n" + \
               "storage or cancelled.\n\n" + \
               "You must save changes or cancel before working with a\n" + \
               "different location."
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
        # self.main_top window hasn't been created so use self.parent instead
        self.thread = self.get_thread_func()  # FIX huge problem when play_close()

        # June 19, 2023 closing playing window when message mounted still causes crash.
        #    Maybe Locations() should have it's own thread handler?

        text = "The 'Save Location As...' function is a work in progress.\n\n" + \
               "When 'Save As...' is chosen any changes to current location\n" + \
               "(such as new songs) are lost and go to the new location.\n\n" + \
               "The 'Save As...' function will behave like the 'New Location'\n" + \
               "function except location is fully populated with what's in memory.\n\n" + \
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

    def validate_location(self):
        """ Validate Location for current ("scr_") fields
            Call shared function: validate_host() for special processing.
        """

        ''' NOTE: redesign for self.input_active is always True '''

        ''' Retrieve name and description from tkinter variables. '''
        new_name = self.scr_name.get().strip()
        new_topdir = self.scr_topdir.get().strip()
        new_host = self.scr_host.get().strip()
        new_wakecmd = self.scr_wakecmd.get().strip()
        new_testcmd = self.scr_testcmd.get().strip()
        new_testrep = self.scr_testrep.get()
        new_mountcmd = self.scr_mountcmd.get().strip()
        new_touchcmd = self.scr_touchcmd.get().strip()
        new_touchmin = self.scr_touchmin.get()
        new_comments = self.scr_comments.get().strip()
        if self.state == 'new' or self.state == 'save_as':
            # Blank out name and description for name change tests
            self.act_name = ""
            self.act_topdir = ""

        ''' We need a location name no matter the operation performed '''
        if new_name == "":
            if self.input_active:
                text = "Enter a unique name for the location."
            else:
                text = "First click on a location entry."
            self.thread = self.get_thread_func()  # FIX huge problem when play_close()
            message.ShowInfo(self.main_top, "Name cannot be blank!",
                             text, icon='error', thread=self.thread)
            return False

        ''' A location description is recommended for Apple Users '''
        if new_topdir == "" and self.input_active:
            text = "Enter a location description gives more functionality\n" + \
                   "in other Music Players such as iPhone."
            self.thread = self.get_thread_func()  # FIX huge problem when play_close()
            message.ShowInfo(self.main_top, "Description is blank?",
                             text, icon='warning', thread=self.thread)

        ''' Tests when location name and description are keyed in '''
        if self.input_active:
            ''' Same name cannot exist in this location '''
            if new_name in self.all_names and \
                    new_name != self.act_name:
                title = "Name must be unique!"
                text = "Location name has already been used."
                self.info.cast(title + "\n\n" + text, 'error')
                thr = self.get_thread_func()
                message.ShowInfo(self.main_top, title, text, icon='error', thread=thr)
                return False

        ''' Creating a new location? Similar tests for Save As... '''
        if self.state == 'new':
            # Passed all tests so create new number string
            if len(self.all_codes) > 0:
                last_str = self.all_codes[-1]  # Grab last number
                val = int(last_str[1:]) + 1  # increment to next available
                self.act_code = "L" + str(val).zfill(3)
            else:
                self.act_code = "L001"  # Very first location

        if self.input_active:
            self.act_name = new_name
            self.act_topdir = new_topdir

        if self.state == 'open':
            # TODO broadcast message to Information Centre
            pass

        if self.state == 'delete':
            # self.main_top window hasn't been created so use self.parent instead
            if self.curr_number_str == self.act_code:
                text += "\nThe location is currently playing and will be stopped.\n"
            self.thread = self.get_thread_func()  # FIX huge problem when play_close()
            dialog = message.AskQuestion(
                self.main_top, "Confirm location deletion", text, icon='warning',
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

    def validate_host(self, iid, toplevel=None):
        """ Is it a host? """
        if item(iid)['host'] is "":
            return False  # Always return False when not a host

        return self.test(iid, toplevel)

    @staticmethod
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
            # Determine function name from within that function
            # http://farmdev.com/src/secrets/framehack/index.html
            print('test_host_up() received blank host name from:',
                  sys._getframe(1).f_code.co_name)
            return False

    @staticmethod
    def code_to_ndx(self, code):
        """ Convert 'L001' to 1, 'L002' to 2, etc. """
        return int(code[1:]) - 1

    @staticmethod
    def ndx_to_code(self, ndx):
        """ Convert 1 to 'L001', 2 to 'L002', etc. """
        return "L" + str(ndx + 1).zfill(3)

    def test(self, iid, toplevel):

        """ Validate location. In the most simple form check that local machine's
            top directory exists. In the most complicated form location is on
            remote / host and host must be woken up, partition mounted and, then
            test if top directory exists.

            This function is called by loc_open().

            This function calls md = message.Open(...) to display messages to user.

            toplevel is parent window our new window is centered in. It can be None
            when program first starts and there is no toplevel yet.

            Create "Test Host" command button. This will wake up host if
            necessary and get top music directory, last modified time and
            free space.
        """

        ndx = self.code_to_ndx(iid)  # treeview style "L002" to LIST index "1"
        d = LIST[ndx]  # Get dictionary for LIST index

        host = d['host']
        # if host == "" or host.isspace():
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


        """ TODO: Mount test host window """
        # Test if host on-line
        #title = "Testing location: " + d['name'] + ".  host: " + host
        #dtb = message.DelayedTextBox(title=title, toplevel=toplevel,
        #                             width=1000, height=260, startup_delay=0)
        # md = message.Open(title, toplevel, 800, 260)  # 500 wide, 160 high

        # https://serverfault.com/questions/696281/ping-icmp-open-socket-operation-not-permitted-in-vserver
        # chmod u+s $( which ping );
        # print('Initial test to see if host is awake')
        #dtb.update('Initial test to see if host is awake')
        test_passed = self.test_host_up(host)

        # Wake up host if not on-line
        # if not wakecmd == "" or not wakecmd.isspace():
        if wakecmd.strip():
            if test_passed is True:
                # print("Host:", host, "is already awake.")
                dtb.update("Host: " + host + " is already awake.")
            else:
                # print('waking up host:', host, 'using:', wakecmd)
                #dtb.update('waking up host: ' + host + ' using: ' + wakecmd)
                os.popen(wakecmd)
                # TODO: What about error messages on 2>?

        # Test host up if not already done
        # if not testcmd == "" or not testcmd.isspace():
        if testcmd.strip():
            # Loop # of iterations checking if host is up
            if testrep < 1:
                testrep = 1
            for i in range(testrep):
                if test_passed is True:
                    break
                time.sleep(.1)

                # We don't want error messages in our result use 2>/dev/null
                result = os.popen(testcmd + ' 2>/dev/null').read().strip()
                if len(result) > 4:
                    test_passed = True
                    tests = i
        else:
            test_passed = True

        if test_passed is False:
            test_time = int(float(testrep) * .1)
            #dtb.update("location.test() Host did not come up after: " +
            #           str(test_time) + " seconds.")
            #dtb.close()
            return False
        else:
            # print("location.test() Host up after:", tests, "tests.")
            #dtb.update("location.test() Host up after: " + str(tests) + " tests.")
            pass

        # Check if already mounted - Needs fine tuning
        topdir = d['topdir'].rstrip(os.sep)

        if topdir is "":  # What if topdir is os.sep for a USB or something?
            topdir = os.sep

        result = os.popen("mount | grep " + topdir + " ").read().strip()
        if len(result) > 4:
            # print("location.test() Top Directory for Music already mounted")
            #dtb.update("location.test() Top Directory for Music already mounted")
            #dtb.close()
            return True

        # Mount host directory locally with sshfs
        mountcmd = d['mountcmd']
        self.open_host_is_mounted = False
        # if not mountcmd == "" or not mountcmd.isspace():
        if mountcmd.strip():
            # We want error messages in our result
            result = os.popen(mountcmd).read().strip()
            if len(result) > 4:
                # print("location.test() errors mounting:", result)
                dtb.update("location.test() errors mounting:" + result)
            else:
                self.open_host_is_mounted = True
        else:
            self.open_host_is_mounted = True

        if self.open_host_is_mounted is False:
            # print("location.test() Host Top Directory could not be mounted with:",
            #      d['mountcmd'])
            #dtb.update("location.test() Host Top Directory could not be mounted with: " +
            #           d['mountcmd'])
            return False

        # Host is up and directory mounted, see if it exists
        if os.path.exists(d['topdir']):
            #dtb.close()
            return True
        else:
            # print("location.test() Top Directory for Music doesn't exist:",
            #      d['topdir'])
            #dtb.update("location.test() Top Directory for Music doesn't exist: " +
            #           d['topdir'])
            #dtb.close()
            return False

    def delete_location(self):
        """ Delete Location using Location Row ID """
        sql.loc_cursor.execute("DELETE FROM Location WHERE Id=?", [self.act_row_id])
        sql.con.commit()

    # noinspection PyUnusedLocal
    def reset(self, *args):
        """ Named "reset" because used by shutdown as well. """
        if self.tt:
            self.tt.close(self.main_top)
        if self.main_top:
            geom = monitor.get_window_geom_string(self.main_top, leave_visible=False)
            monitor.save_window_geom('locations', geom)
            self.main_top.destroy()
        LocationsCommonSelf.__init__(self)  # Reset self. variables

    # noinspection PyUnusedLocal
    def apply(self, *args):
        """ Validate, Analyze mode (state), update database appropriately. """
        if self.validate_location() is False:
            return

        if self.state == 'delete':
            # TODO: Delete resume, chron_state, hockey_state and open_states
            #       Or just set a deleted flag and not physically delete.
            self.delete_location()
            self.info.cast("Deleted location: " + self.act_name, action="delete")
            if self.curr_number_str == self.act_code:
                self.name = None
                self.last_number_str = self.curr_number_str  # Replaces .name in future
                self.curr_number_str = None  # Replaces .name in future
                self.play_close()  # must be called before name is set
                self.name = self.act_name  # Tell parent name of location
                self.curr_number_str = None  # Was deleted, no longer exists.
        elif self.state == 'open':
            self.name = None
            self.curr_number_str = None  # Replaces .name in future
            self.play_close()  # must be called before name is set
            self.name = self.act_name  # Tell parent name of location
            self.last_number_str = self.curr_number_str  # Replaces .name in future
            self.curr_number_str = self.act_code
            self.reset()  # Close everything down, E.G. destroy window
            # June 23, 2023 - info.cast isn't appearing?
            self.info.cast("Opened location: " + self.act_name)
            self.apply_callback()  # Parent will start playing (if > 1 song in list)
            # self.info.cast("Opened location: " + self.act_name)  # doesn't work either
        elif self.state == 'new':
            self.save_location()  # Save brand new location
            self.name = None
            self.curr_number_str = None  # Replaces .name in future
            self.play_close()  # must be called before name is set
            self.name = self.act_name  # Tell parent name of location
            self.last_number_str = self.curr_number_str  # Replaces .name in future
            self.curr_number_str = self.act_code
            # June 23, 2023 - info.cast isn't appearing?
            self.info.cast("Created new location: " + self.act_name, action="add")
            self.apply_callback()  # Tell parent to start editing location
            # self.info.cast("Created new location: " + self.act_name)  # doesn't work either
            # apply_callback will end right away after closing lib selections
        else:
            ''' Remaining options are Save, Save As, Rename '''
            self.save_location()
            self.name = self.act_name  # In case of 'rename' title updates
            self.curr_number_str = self.act_code
            self.info.cast("Saved location: " + self.act_name, action="update")

        self.reset()  # Destroy window & reset self. variables




# End of location.py
