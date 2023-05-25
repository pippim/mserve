#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
#
#       global_variables.py - Global variables shared by all mserve modules
#
#       May 19, 2023 - appdirs for universal application & storage directories
#
# ==============================================================================

from __future__ import print_function       # Must be first import

from appdirs import *   # Get application & storage directory names
import os               # USER_ID = str(os.get uid())
import pwd              # USER = pwd.get pw uid(os.get uid()).pw_name

USER = None             # User ID, Name, GUID varies by platform
USER_ID = None          # Numeric User ID in Linux
HOME = None             # In Linux = /home/USER
USER_CONFIG_DIR = None  # /home/user/.config/mserve
USER_DATA_DIR = None    # /home/user/.local/share/mserve
MSERVE_DIR = None       # /home/user/.config/mserve <- historically wrong
                        # Bad name. It implies where mserve programs are
PROGRAM_DIR = None

# Same values used by gnome-terminal to prevent window shrinking too small
WIN_MIN_WIDTH = 142
WIN_MIN_HEIGHT = 63

# Many older Global variables first used in mmm (multiple monitors manager)
RESTART_SLEEP = .3      # Delay for mserve close down
KEEP_AWAKE_MS = 250     # Milliseconds between time checks
MON_FONTSIZE = 12       # Font size for monitor name
WIN_FONTSIZE = 11       # Font size for Window name
BIG_FONT = 18           # Font size not used
LARGE_FONT = 14         # Font size not used
MED_FONT = 10           # Medium Font size
BTN_WID = 17            # Width for buttons on main window
BTN_WID2 = 15           # Width for buttons on play window
BTN_BRD_WID = 3         # Width for button border
FRM_BRD_WID = 2         # Width for frame border
PANEL_HGT = 24          # Height of Unity panel
MAX_DEPTH = 3           # Sanity check if starting at c:\ or /
# If MAX_DEPTH changes you must update 'depth_count = [ 0, 0, 0 ]' below.


def init():
    """ This should only be called once by the main module
        Child modules will inherit values. For example if they contain
        
            import global_variables as g
            
        Later on they can reference 'g.USER' to get the User Login Name.
        or 'g.USER_ID' to get the Numerical User ID

        0   pw_name     Login name
        1   pw_passwd   Optional encrypted password
        2   pw_uid      Numerical user ID
        3   pw_gid      Numerical group ID
        4   pw_gecos    User name or comment field
        5   pw_dir      User home directory
        6   pw_shell    User command interpreter
    """
    global USER, USER_ID, HOME, USER_DATA_DIR, USER_CONFIG_DIR, MSERVE_DIR, PROGRAM_DIR

    if USER is not None:
        # print('User already set:', USER, USER_ID, HOME)
        return

    USER = pwd.getpwuid(os.getuid()).pw_name
    USER_ID = str(os.getuid())
    HOME = os.path.expanduser("~")  # Works in Windows too. EG C:\Users\rick
    # print('User:', USER, USER_ID, HOME)
    appname = "mserve"
    app_author = "pippim"
    USER_DATA_DIR = user_data_dir(appname, app_author)
    # print("USER_DATA_DIR:", USER_DATA_DIR)
    USER_CONFIG_DIR = MSERVE_DIR = user_config_dir(appname, app_author)
    MSERVE_DIR += os.sep
    PROGRAM_DIR = os.getcwd()
    PROGRAM_DIR += os.sep
    # print("USER_CONFIG_DIR:", USER_CONFIG_DIR)

# End of global_variables.py
