# -*- coding: utf-8 -*-
#==============================================================================
#
#       location.py - Locations file, dictionary and global fields
#
#       After copying playlists between locations use:
#
#           cd ~/.config/mserve/L???    # Where ??? is 001, 002, etc.
#           sed -i 's#/mnt/chromeos/removable#/media/rick#' last_playlist
#           sed -i 's#/mnt/chromeos/removable#/media/rick#' last_selections
#
#==============================================================================

from __future__ import print_function       # Must be first import
import os
import sys
import shutil

import pickle
import time
import datetime

import message                              # manage dialog messages 

import global_variables as g
if g.USER is None:
    print('location.py was forced to run g.init()')
    g.init()

# Define /home/$USER/.config/mserve/ directory
MSERVE_DIR            = os.sep + "home" + os.sep + g.USER + os.sep + \
                        ".config" + os.sep + "mserve" + os.sep

# only files in  /home/$USER/.config/mserve/ directory
FNAME_LOCATIONS       = MSERVE_DIR + "locations"
FNAME_LAST_LOCATION   = MSERVE_DIR + "last_location"
FNAME_LIBRARY         = MSERVE_DIR + "library.db"

# These files are located to /home/$USER/.config/mserve/L999/ directory
FNAME_LAST_OPN_STATES = MSERVE_DIR + "last_open_states"
FNAME_LAST_SONG_NDX   = MSERVE_DIR + "last_song_ndx"
# May 25 2021 -  last_selections corrupted by refresh_lib_tree()
FNAME_LAST_SELECTIONS = MSERVE_DIR + "last_selections"      # Version 1
FNAME_LAST_PLAYLIST   = MSERVE_DIR + "last_playlist"        # Version 1

''' FUTURE VERSION '''
FNAME_ALL_SONGS       = MSERVE_DIR + "all_songs"            # Version 2
FNAME_CURR_PLAYING    = MSERVE_DIR + "curr_playing"         # Version 2
FNAME_CURR_SELECTIONS = MSERVE_DIR + "curr_selections"      # Version 2

"""
    FUTURE Version 1 to Version 2 silent upgrade

    If 'all_songs' doesn't exist, create it from SORTED_LIST global variable
    If 'last_selections' exists, rename it to 'curr_playing'
    If 'last_playlist' exists, rename it to 'curr_selections'


"""

FNAME_LAST_VARS       = MSERVE_DIR + "last_variables"       # TODO: Version 3

"""
- 0 - Last Song index
- 1 - Playlist name
- 2 - Playlist read time
- 3 - Shuffle time
- 4 - Manual reordered time
- 5 - Time played
- 6 - Time paused
- 7 - Spare string
- 8 - Spare float
- 9 - Spare float
- 10 - Spare int
"""

# There can be two open at once so unlike other global variables this is never
# replaced. It is simply used as base for creating new variable.
FNAME_MOD_TIME        = MSERVE_DIR + "modification_time"

#START_DIR = "" # in mserve for now....

# Create our configuration directory if it doesn't exist already
if not os.path.exists(MSERVE_DIR):
    os.makedirs(MSERVE_DIR)
    # print('Created directory:', MSERVE_DIR)


''' Global variables
'''
LIST = []                           # List of DICT's
DICT = {}                           # Location dictionary


def create_subdirectory(iid):

    """ Always try to create '~/.config/mserve/<iid>/' subdirectory """

    import os
    import errno
    directory = MSERVE_DIR + iid + os.sep

    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def set_location_filenames(iid):
    """ Called when mserve first starts up """
    global FNAME_LAST_SELECTIONS, FNAME_LAST_OPN_STATES
    global FNAME_LAST_PLAYLIST, FNAME_LAST_SONG_NDX
    global FNAME_ALL_SONGS, FNAME_CURR_PLAYING, FNAME_CURR_SELECTIONS

    FNAME_LAST_OPN_STATES = set_one_filename(FNAME_LAST_OPN_STATES, iid)
    FNAME_LAST_SONG_NDX   = set_one_filename(FNAME_LAST_SONG_NDX, iid)
    FNAME_LAST_SELECTIONS = set_one_filename(FNAME_LAST_SELECTIONS, iid)
    FNAME_LAST_PLAYLIST   = set_one_filename(FNAME_LAST_PLAYLIST, iid)
    FNAME_ALL_SONGS       = set_one_filename(FNAME_ALL_SONGS, iid)
    FNAME_CURR_PLAYING    = set_one_filename(FNAME_CURR_PLAYING, iid)
    FNAME_CURR_SELECTIONS = set_one_filename(FNAME_CURR_SELECTIONS, iid)


def set_one_filename(filename, iid):
    return filename.replace(os.sep + "mserve" + os.sep,
                            os.sep + "mserve" + os.sep + iid + os.sep)


def rename_location_filenames(iid, old):
    """ Called when forgetting a location
        Rename higher locations to fill the hole.

        NOT TESTED!

    """
    global FNAME_LAST_SELECTIONS, FNAME_LAST_OPN_STATES
    global FNAME_LAST_PLAYLIST, FNAME_LAST_SONG_NDX, FNAME_MOD_TIME
    global FNAME_ALL_SONGS, FNAME_CURR_PLAYING, FNAME_CURR_SELECTIONS

    FNAME_LAST_OPN_STATES = rnm_one_filename(FNAME_LAST_OPN_STATES, iid, old)
    FNAME_LAST_SONG_NDX   = rnm_one_filename(FNAME_LAST_SONG_NDX, iid, old)
    FNAME_LAST_SELECTIONS = rnm_one_filename(FNAME_LAST_SELECTIONS, iid, old)
    FNAME_LAST_PLAYLIST   = rnm_one_filename(FNAME_LAST_PLAYLIST, iid, old)
    FNAME_ALL_SONGS       = rnm_one_filename(FNAME_ALL_SONGS, iid, old)
    FNAME_CURR_PLAYING    = rnm_one_filename(FNAME_CURR_PLAYING, iid, old)
    FNAME_CURR_SELECTIONS = rnm_one_filename(FNAME_CURR_SELECTIONS, iid, old)
    FNAME_MOD_TIME        = rnm_one_filename(FNAME_MOD_TIME, iid, old)


def rnm_one_filename(old_fname, iid, old):
    """ rename on directory name

        TODO: Check if file/path exists before renaming

    """
    old_fname.replace(os.sep + "mserve" + os.sep + old + os.sep,
                      os.sep + "mserve" + os.sep + iid + os.sep)

    return old_fname    # Assume failure


def read():
    global LIST
    with open(FNAME_LOCATIONS, 'rb') as filehandle:
        # read the data as binary data stream
        LIST = pickle.load(filehandle)
        filehandle.close()
    #print('location.read() LIST count:',len(LIST))    


# Read locations if it exists
if os.path.isfile(FNAME_LOCATIONS):
    read()
    #print('MODULE LOAD LIST count:',len(LIST))    


def write():
    with open(FNAME_LOCATIONS, "wb") as f:
        # store the data as binary data stream
        pickle.dump(LIST, f)                      # Save locations list
        f.close()


def unpickle_list(filename):

    """ generic open and unpickling to use everywhere:

            https://stackoverflow.com/questions/33307623/
                python-exception-safe-pickle-use/33308573

                with open(self.session_filename, "rb") as f:
                    data = cPickle.loads(zlib.decompress(f.read()))

        Compression not used but if needed see:

            https://stackoverflow.com/questions/18474791/
                decreasing-the-size-of-cpickle-objects

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
           testrep=10, mountcmd="", activecmd="", activemin=10):
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

    LIST.append(d)

    # Create directory '~/.config/mserve/<iid>' Where <iid> = L001, L002, etc.
    create_subdirectory(iid)

    return iid


def iid_to_ndx(iid):
    """ Convert location index (iid) to zero based index for LIST[ndx] """
    sndx = iid[-3:]             # Last 3 characters of "L999" = "999"
    return int(sndx) - 1


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


def onetime():

    # Onetime setup of new L999 location IDs (iid)

    exit()  # Remove when you will be changing below to do something
    read()
    for i, d in enumerate(LIST):
        new_iid = ndx_to_iid(i)
        d['iid'] = new_iid
    write()


def remove(iid):
    """ Delete location from LIST """
    ndx = iid_to_ndx(iid)           # treeview style string to LIST index
    del LIST[ndx]


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
            print('location.item() invalid key passed:', key)

    if keyword_found is True:
        # Dec 5, 2020 - Why does this work when LIST isn't global?
        LIST[ndx] = DICT            # Update DICT entry in LIST
    else:
        return DICT                 # No keywords so return DICT


def validate_host(iid, toplevel=None):
    """
    """
    # Is it a host?
    if item(iid)['host'] is "":
        return False                # Always return False when not a host

    return test(iid, toplevel)


def get_dict_by_dirname(dirname):
    global DICT                     # NOT confirmed if it needs to be here!
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

    This is nc from the netcat-openbsd package. An alternative nc is available
    in the netcat-traditional package.
    usage: nc [-46bCDdhjklnrStUuvZz] [-I length] [-i interval] [-O length]
    [-P proxy_username] [-p source_port] [-q seconds] [-s source]
    [-T toskeyword] [-V rtable] [-w timeout] [-X proxy_protocol]
    [-x proxy_address[:port]] [destination] [port]
    
    Restarting with new music library: /home/rick/Music
    '''
    if host.strip():
        return True if os.system("nc -z " + host + " 22 > /dev/null") \
                                 is 0 else False
    else:
        print('test_host_up() receved blank host name from:',
              sys._getframe(1).f_code.co_name)
        return False


def test(iid, toplevel):

    """ Validate location. In the most simple form check that local machine's
        top directory exists. In the most complicated form location is on
        remote / host and host must be woken up, parition mounted and, then
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
        # Loop # of interations checking if host is up
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
        testtime = int(float(testrep) * .1)
        #print("location.test() Host did not come up after:",
        #      testtime,"seconds.")
        dtb.update("location.test() Host did not come up after: " +
                   str(testtime) + " seconds.")
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
    """ Get directory name """
    root.directory = filedialog.askdirectory(
        initialdir=start, parent=parent, title=title)
    return root.directory       # July 7, 2021 - used to be in brackets, didn't test


class ModTime:

    def __init__(self, iid):
        """ Open list of modification times
            Analyze location to see if 'touch -m -r src_path trg_path' works.
            If not utilize timestamp file to get last modification time.
        """
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
            text_file.write("Test Modifcation Time")
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


def remove_iid(iid, open_iid):
    """ PARENT WILL:
            Confirm forgetting location. Cannot be current open location.
            If our opened location iid is changing call:
                lc.set_location_filenames(iid)
                Set FNAME_LAST_LOCATION files iid
                Rename LODICT('iid') with new number

        THIS FUNCTION WILL:
            Remove '/home/$USER/.config/mserve/L999' directory
            Rename higher '~/.config/mserve/L999' directories 1 less
            Update higher iid's in locations master file 1 less
            return iid mserve is now using for active location
    """

    ''' Remove /home/$USER/.config/mserve/L999 directory and files within
    
        - need to change globally opened filenames in lc.FNAME as well. 
          Use .replace("/"+from+"/","/"+to+"/")
        - os.rename(topdir + "/" + from, topdir + "/" + to)
        - can .config be residing on a host? If so does os.rename() still work?

    '''
    global MSERVE_DIR

    ''' Parent already did this check but double check anyway '''
    if iid == open_iid:
        print('ERROR. iid:', iid, 'cannot be active location')
        return open_iid

    # Build directory name to remove
    forget_dir = MSERVE_DIR + os.sep + iid + os.sep

    # Directory may never have been created for older buggy versions or
    # remote locations without access or due to permissions
    if not os.path.isfile(forget_dir):
        return None

    # Try to remove tree; if failed show an error using try...except on screen
    try:
        shutil.rmtree(forget_dir)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))

    # TODO: Decrement location ID's higher than deleted one.
    return open_iid                 # The active location's iid hasn't changed


def renumber_iid():

    """ To iid will be deleted then from iid is renamed to it.

        - need to change globally opened filenames in lc.FNAME as well.
          Use .replace("/"+from+"/","/"+to+"/")
        - os.rename(topdir + "/" + from, topdir + "/" + to)
        - can .config be residing on a host? If so does os.rename() still work?

    """

    pass

# End of location.py
