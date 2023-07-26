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
#       global_variables.py - Global variables shared by all mserve modules
#
#       May. 19 2023 - appdirs for universal application & storage directories
#       July 10 2023 - Begin mserve_config.py development (check dependencies)
#
# ==============================================================================

# Get application & storage directory names
from appdirs import user_data_dir, user_config_dir

import tempfile         # Gets TMP_DIR /tmp, C:\Temp, etc.
import os               # USER_ID = str(os.get uid())
import pwd              # USER = pwd.get pw uid(os.get uid()).pw_name
import webbrowser       # Display help text on www.pippim.com

''' Code duplicated in mserve_config.py '''
import platform as plat  # Gets OS Name, Version, Release
OS_PLATFORM = plat.platform()  # 'Linux-4.14.216-0414216-generic-x86_64-with-Ubuntu-16.04-xenial'
OS_NAME = plat.system()  # 'Linux'
OS_VERSION = plat.release()  # '4.14.216-0414216-generic'
OS_RELEASE = plat.version()  # '#202101171339 SMP Sun Jan 17 13:56:04 UTC 2021'

USER = None             # User ID, Name, GUID varies by platform
USER_ID = None          # Numeric User ID in Linux
HOME = None             # In Linux = /home/USER
USER_CONFIG_DIR = None  # /home/user/.config/mserve
USER_DATA_DIR = None    # /home/user/.local/share/mserve
MSERVE_DIR = None       # /home/user/.config/mserve <- historically wrong
                        # Bad name. It implies where mserve programs are
PROGRAM_DIR = None      # Directory where mserve.py is stored.
TEMP_DIR = None         # Directory for temporary files /run/user/1000 preferred

# Same values used by gnome-terminal to prevent window shrinking too small
WIN_MIN_WIDTH = 142
WIN_MIN_HEIGHT = 63
RESTART_SLEEP = .3      # Delay for mserve close down
KEEP_AWAKE_MS = 250     # Milliseconds between time checks

# Older Global variables from mmm (multiple monitors manager), so need renaming.
BIG_FONT = 18           # Font size not used
LARGE_FONT = 14         # Font size not used
MON_FONTSIZE = 12       # Font size for monitor name
WIN_FONTSIZE = 11       # Font size for Window name
MED_FONT = 10           # Medium Font size

BTN_WID = 17            # Width for buttons on main window
BTN_WID2 = 15           # Width for buttons on play window
BTN_BRD_WID = 3         # Width for button border
FRM_BRD_WID = 2         # Width for frame border
PANEL_HGT = 24          # Height of Unity panel
MAX_DEPTH = 3           # Sanity check if starting at c:\ or /
# If MAX_DEPTH changes you must update 'depth_count = [ 0, 0, 0 ]' below.

HELP_URL = "https://www.pippim.com/programs/mserve.html#"


def init(caller=None):
    """ This should only be called once by the main module
        Child modules will inherit values. For example if they contain
        
            import global_variables as g
            
        Then reference 'g.USER' to get the User Login Name.
        or 'g.USER_ID' to get the Numerical User ID

        0   pw_name     Login name
        1   pw_passwd   Optional encrypted password
        2   pw_uid      Numerical user ID
        3   pw_gid      Numerical group ID
        4   pw_gecos    User name or comment field
        5   pw_dir      User home directory
        6   pw_shell    User command interpreter
    """
    if caller and caller is not "mserve_config.py":
        if not cfg.main(caller):
            #print("mserve not fully installed. Aborting...")
            exit()
        else:
            # Cannot print from background jobs disk_get.py, mbz_get1.py, etc.
            #print("mserve_config.py is calling global_variables.py !")
            pass

    global USER, USER_ID, HOME, USER_DATA_DIR, USER_CONFIG_DIR, MSERVE_DIR
    global PROGRAM_DIR, TEMP_DIR

    if USER is not None:
        # print('User already set:', USER, USER_ID, HOME)
        return

    USER = pwd.getpwuid(os.getuid()).pw_name
    USER_ID = str(os.getuid())
    HOME = os.path.expanduser("~")  # Works in Windows too. EG C:\Users\rick
    # print('User:', USER, USER_ID, HOME)
    appname = "mserve"
    app_author = "pippim"
    USER_DATA_DIR = MSERVE_DIR = user_data_dir(appname, app_author)
    USER_CONFIG_DIR = user_config_dir(appname, app_author)
    # noinspection Pep8CodingStyleViolationW605
    '''
        What directory should your app use for storing user data? If running on Mac OS X, you
        should use::
        
            ~/Library/Application Support/<AppName>
        
        If on Windows (at least English Win XP) that should be::
        
            C:\\Documents and Settings\\<User>\\Application Data\\Local Settings\\<AppAuthor>\\<AppName>
        
        or possibly::
        
            C:\\Documents and Settings\\<User>\\Application Data\\<AppAuthor>\\<AppName>
        
        for `roaming profiles <http://bit.ly/9yl3b6>`_ but that is another story.
        
        On Linux (and other Unices) the dir, according to the `XDG
        spec <http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html>`_, is::
        
            ~/.local/share/<AppName>
        
    '''

    if not MSERVE_DIR.endswith(os.sep):
        MSERVE_DIR += os.sep
    PROGRAM_DIR = os.path.dirname(os.path.realpath(__file__))

    if not PROGRAM_DIR.endswith(os.sep):
        PROGRAM_DIR += os.sep
    # print("USER_CONFIG_DIR:", USER_CONFIG_DIR)

    TEMP_DIR = tempfile.gettempdir()
    if not TEMP_DIR.endswith(os.sep):
        TEMP_DIR += os.sep
    TEMP_DIR += USER_ID + "_"  # /tmp/1000_

    # Override if directory /run/user/ exists (no disk light flashing)
    systemd = "/run/user/" + USER_ID
    if os.path.isdir(systemd):
        TEMP_DIR = systemd + os.sep


# ==============================================================================
#
#       Independent (Stand Alone) Functions
#
# ==============================================================================


def web_help(id_name):
    # noinspection SpellCheckingInspection
    """
        g.HELP defined in global_variables.py imported as g.  It contains:
        https://www.pippim.com/programs/mserve.html#

    :param id_name: E.G. "HelpT", "HelpB" and "HelpS" used above
    :return None: You will see an error message if there is a typo in the link:
            gvfs-open: # https://www.pippim.com/programs/mserve.html#HelpT:
            error opening location: Error when getting information for file
            '/.../# https:/www.pippim.com/programs/mserve.html#HelpT':
            No such file or directory

    """
    link = HELP_URL + id_name
    webbrowser.open_new(link)
    # see: https://docs.python.org/3/library/webbrowser.html


def main(caller=None):
    """ July 10, 2023 - was always calling .init() directly. Test with main. """
    init(caller)
    return True


if __name__ == "__main__":
    main()

# End of global_variables.py
