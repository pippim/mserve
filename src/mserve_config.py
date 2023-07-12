#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: Pippim
License: GNU GPLv3
Source: This repository
Description: mserve - Music Server - Configuration
"""

from __future__ import print_function  # Must be first import
from __future__ import with_statement  # Error handling for file opens

# ==============================================================================
#
#       mserve_config.py - Check dependencies
#
#       July 10 2023 - Initial version. Check for mandatory and optional.
#
# ==============================================================================
# from __future__ import unicode_literals  # Not needed.
try:
    import warnings  # 'warnings' advises which commands aren't supported
    warnings.simplefilter('default')  # in future Python versions.
except ImportError:
    pass

"""
    Called by global_variables.py to ensure all necessary imports are available.
"""


''' Check Python version is minimal 2.7.12 '''
import sys

current_version = "Python 2.7.12 or a more recent version is required.\n" + \
    "           Version installed is: " + str(sys.version_info[0]) + "." + \
    str(sys.version_info[1]) + "." + str(sys.version_info[2])
# Test notes below will force failure even if you are already on version 2.7.12
if sys.version_info[0] < 2:  # test change 2 to 4
    raise Exception("001: " + current_version)
if sys.version_info[0] >= 2 and sys.version_info[1] < 7:  # test change 7 to 8
    raise Exception("002: " + current_version)
if sys.version_info[0] >= 2 and sys.version_info[1] >= 7 and sys.version_info[2] < 12:
    raise Exception("003: " + current_version)

import inspect
import importlib

''' Load global variables first before Pippim modules
try:
    g = importlib.import_module("global_variables")
except ImportError:
    g = None  # Just to make pycharm happy
    print("mserve not fully installed. Missing 'global_variables.py'.")
    exit()

if not hasattr(g, "USER"):
    print('mserve_config.py - importlib failed on global_variables')
    import global_variables as g
    g.init("mserve_config.py")

print("\ndir(g)):\n", dir(g))  # Very long list
print("\ninspect.getmembers(g):\n", inspect.getmembers(g, inspect.isfunction))  # returns empty list
print("\nUsing global_variables.py as 'g' from path:\n",
      inspect.getfile(g), "\n")
'''


#before = [str(m) for m in sys.modules]
#import os               # USER_ID = str(os.get uid())

#print(inspect.getfile(importlib))
#print(dir(importlib))
#ret = importlib.import_module("vu_pulse_audio")
#print("ret:", ret)
#print(inspect.getfile(vu_pulse_audio))
#print(dir(vu_pulse_audio))
#ret = importlib.import_module("ttkwidgets", "ttkwidgets.CheckboxTreeview")  # WORKS but all
#ret = importlib.import_module("ttkwidgets.CheckboxTreeview")  # ImportError: No module named CheckboxTreeview
#ret = importlib.import_module("CheckboxTreeview", "ttkwidgets.CheckboxTreeview")  # No module named CheckboxTreeview
#ret = importlib.import_module("CheckboxTreeview", "ttkwidgets")  # ImportError: No module named CheckboxTreeview
#ret = importlib.import_module("ttkwidgets", "CheckboxTreeview")  # WORKS but all
#ret = importlib.import_module("ttkwidgets.CheckboxTreeview", "ttkwidgets")  # No module named CheckboxTreeview
''' below works
full = importlib.import_module("ttkwidgets")
ret = full.CheckboxTreeview
del full
print("\nret:", ret)  # from ttkwidgets import CheckboxTreeview
#print("\n", dir(ret))  # Very long list
#print(inspect.getmembers(ret, inspect.isfunction))  # returns empty list
#print(help(ret))  # Impressive !
#print("Using ttkwidgets.py CheckboxTreeview from path:",
#      inspect.getfile(CheckboxTreeview))
'''


DEFAULT_CFG = []


def make_default_cfg():
    global DEFAULT_CFG
    DEFAULT_CFG += make_g_cfg()
    DEFAULT_CFG += make_vup_cfg()


def make_g_cfg():
    """ Configuration for: 'import global_variables as g' """
    g_list = list()  # Return list of dictionaries

    # noinspection SpellCheckingInspection
    '''
    Contents of global_variables.py:

        import mserve_config as cfg
        
        # Get application & storage directory names
        from appdirs import user_data_dir, user_config_dir
        
        import tempfile         # Gets TMP_DIR = /tmp, C:\temp, etc.
        import os               # USER_ID = str(os.get uid())
        import pwd              # USER = pwd.get pw uid(os.get uid()).pw_name
    '''
    caller = "global_variables"
    g_list.append(make_a_dict(caller, "caller_data_dir", "appdirs"))
    g_list.append(make_a_dict(caller, "caller_config_dir", "appdirs"))
    # noinspection SpellCheckingInspection
    g_list.append(make_a_dict(caller, None, "tempfile"))
    g_list.append(make_a_dict(caller, None, "os"))
    g_list.append(make_a_dict(caller, None, "pwd"))
    return g_list


def make_vup_cfg():
    """ Configuration for: 'import vu_pulse_audio as vup' """
    vup_list = list()  # Return list of dictionaries

    # noinspection SpellCheckingInspection
    '''
    Contents of vu_pulse_audio.py:

        import global_variables as g
        import os
        import time
        from collections import OrderedDict, namedtuple
        from pulsectl import pulsectl
        import external as ext
        import timefmt as tmf
        import toolkit
    '''
    caller = "vu_pulse_audio"
    vup_list.append(make_a_dict(caller, "g", "global_variables"))
    vup_list.append(make_a_dict(caller, None, "os"))
    vup_list.append(make_a_dict(caller, None, "time"))
    vup_list.append(make_a_dict(caller, "OrderedDict", "Collections"))
    vup_list.append(make_a_dict(caller, "namedtuple", "Collections"))
    vup_list.append(make_a_dict(caller, "pulsectl", "pulsectl",
                                "github.com/mk-fg/python-pulse-control"))
    vup_list.append(make_a_dict(caller, "ext", "external", "pippim.com"))
    vup_list.append(make_a_dict(caller, "tmf", "timefmt", "pippim.com"))
    vup_list.append(make_a_dict(caller, None, "toolkit", "pippim.com"))
    return vup_list


def make_toolkit_cfg():
    """ Configuration for: 'import vu_pulse_audio as toolkit' """
    toolkit_list = list()  # Return list of dictionaries

    # noinspection SpellCheckingInspection
    '''
    Contents of toolkit.py:
        
        try:
            import tkinter as tk
            import tkinter.ttk as ttk
            import tkinter.font as font
            import tkinter.filedialog as filedialog
            import tkinter.messagebox as messagebox
            import tkinter.scrolledtext as scrolledtext
            PYTHON_VER = "3"
        except ImportError:  # Python 2
            import Tkinter as tk
            import ttk
            import tkFont as font
            import tkFileDialog as filedialog
            import tkMessageBox as messagebox
            import ScrolledText as scrolledtext
            PYTHON_VER = "2"
        # print ("Python version: ", PYTHON_VER)
        
        # For MoveTreeviewColumn
        from PIL import Image, ImageTk
        from collections import namedtuple
        from os import popen
        
        import time
        import datetime
        from ttkwidgets import CheckboxTreeview
        from collections import OrderedDict, namedtuple
        
        import global_variables as g
        import external as ext      # Time formatting routines
        import image as img         # Pippim image.py module
        import re                   # w, h, old_x, old_y = re.split(...
        import traceback            # To display call stack

    Optional gnome_screenshot() for MoveTreeviewColumn function imports:
        import gi
        gi.require_version('Gdk', '3.0')
        gi.require_version('Gtk', '3.0')
        gi.require_version('Wnck', '3.0')
        # gi.require_versions({"Gtk": "3.0", "Gdk": "3.0", "Wnck": "3.0"})
    
        from gi.repository import Gdk, GdkPixbuf, Gtk, Wnck
    
    '''
    caller = "toolkit"
    toolkit_list.append(make_a_dict(caller, "g", "global_variables"))
    toolkit_list.append(make_a_dict(caller, "tk", "tkinter",
                                    "https://github.com/tcltk/tk", "3",
                                    "python3-tk"))
    toolkit_list.append(make_a_dict(caller, "tk", "Tkinter",
                                    "https://github.com/tcltk/tk", "2",
                                    "python-tk"))
    toolkit_list.append(make_a_dict(caller, "ttk", "tkinter.ttk",
                                    "https://github.com/tcltk/tk", "3",
                                    "python3-tk"))
    toolkit_list.append(make_a_dict(caller, None, "ttk",
                                    "https://github.com/tcltk/tk", "2",
                                    "python-tk"))
    toolkit_list.append(make_a_dict(caller, "font", "tkinter.font",
                                    "https://github.com/tcltk/tk", "3",
                                    "python3-tk"))
    toolkit_list.append(make_a_dict(caller, "font", "tkFont",
                                    "https://github.com/tcltk/tk", "2",
                                    "python-tk"))
    toolkit_list.append(make_a_dict(caller, "filedialog", "tkinter.filedialog",
                                    "https://github.com/tcltk/tk", "3",
                                    "python3-tk"))
    toolkit_list.append(make_a_dict(caller, "filedialog", "tkFileDialog",
                                    "https://github.com/tcltk/tk", "2",
                                    "python-tk"))
    toolkit_list.append(make_a_dict(caller, "messagebox", "tkinter.messagebox",
                                    "https://github.com/tcltk/tk", "3",
                                    "python3-tk"))
    toolkit_list.append(make_a_dict(caller, "messagebox", "tkMessageBox",
                                    "https://github.com/tcltk/tk", "2",
                                    "python-tk"))
    toolkit_list.append(make_a_dict(caller, "scrolledtext", "tkinter.scrolledtext",
                                    "https://github.com/tcltk/tk", "3",
                                    "python3-tk"))
    toolkit_list.append(make_a_dict(caller, "scrolledtext", "ScrolledText",
                                    "https://github.com/tcltk/tk", "2",
                                    "python-tk"))
    toolkit_list.append(make_a_dict(caller, "Image", "PIL",
                                    "https://github.com/tcltk/tk", "2",
                                    "python-tk"))
    '''
from PIL import Image, ImageTk
from collections import namedtuple
import os    
    '''
    toolkit_list.append(make_a_dict(caller, None, "time"))
    toolkit_list.append(make_a_dict(caller, "OrderedDict", "Collections"))
    toolkit_list.append(make_a_dict(caller, "namedtuple", "Collections"))
    toolkit_list.append(make_a_dict(caller, "pulsectl", "pulsectl",
                                    "github.com/mk-fg/python-pulse-control"))
    toolkit_list.append(make_a_dict(caller, "ext", "external", "pippim.com"))
    toolkit_list.append(make_a_dict(caller, "tmf", "timefmt", "pippim.com"))
    toolkit_list.append(make_a_dict(caller, None, "toolkit", "pippim.com"))
    return toolkit_list


def make_a_dict(caller, imp_as, imp_from, developer="python", versions=[],
                repository=None):
    cfg_dict = \
        {"caller": caller,
         "imp_as": imp_as,
         "imp_from": imp_from,
         "developer": developer,
         "versions": versions,
         "repository": repository}
    return cfg_dict


def whats_installed():
    """

    :return inst_list:
    """
    pass

    # noinspection SpellCheckingInspection
    '''
ll /usr/lib/python2.7/dist-packages
total 3732
drwxr-xr-x 127 root root  12288 May 19 09:01 ./
drwxr-xr-x  28 root root  20480 Mar  4  2021 ../
-rw-r--r--   1 root root    192 May 12  2016 adium_theme_ubuntu-0.3.4.egg-info
-rw-r--r--   1 root root  48776 Dec 30  2013 alsaaudio.so
drwxr-xr-x   2 root root   4096 May 19 09:01 appdirs-1.4.0.egg-info/
-rw-r--r--   1 root root  22374 Aug 17  2014 appdirs.py
-rw-r--r--   1 root root  20522 May 19 09:01 appdirs.pyc
drwxr-xr-x   3 root root   4096 Jun 15  2021 apt/
-rw-r--r--   1 root root  52200 Apr 29  2021 apt_inst.x86_64-linux-gnu.so
-rw-r--r--   1 root root 342696 Apr 29  2021 apt_pkg.x86_64-linux-gnu.so
drwxr-xr-x   2 root root   4096 Jun 15  2021 aptsources/
drwxr-xr-x   4 root root   4096 Nov 22  2020 babel/
drwxr-xr-x   2 root root   4096 Nov 22  2020 Babel-1.3.egg-info/
lrwxrwxrwx   1 root root     52 Jun 17  2012 BeautifulSoup-3.2.1.egg-info -> ../../../share/pyshared/BeautifulSoup-3.2.1.egg-info
drwxr-xr-x   2 root root   4096 Jun 30  2019 beautifulsoup4-4.4.1.egg-info/
lrwxrwxrwx   1 root root     40 Jun 17  2012 BeautifulSoup.py -> ../../../share/pyshared/BeautifulSoup.py
-rw-r--r--   1 root root  69174 Feb  7  2021 BeautifulSoup.pyc
lrwxrwxrwx   1 root root     45 Jun 17  2012 BeautifulSoupTests.py -> ../../../share/pyshared/BeautifulSoupTests.py
-rw-r--r--   1 root root  41529 Feb  7  2021 BeautifulSoupTests.pyc
drwxr-xr-x   4 root root   4096 Jun 30  2019 bs4/
-rw-r--r--   1 root root   3687 Aug 29  2017 bzr-2.7.0.egg-info
-rw-r--r--   1 root root    268 Jul 22  2014 bzr_builddeb-2.8.6.egg-info
drwxr-xr-x  17 root root  20480 Mar 10  2019 bzrlib/
drwxr-xr-x   2 root root   4096 Aug  3  2018 cairo/
drwxr-xr-x   2 root root   4096 Jun 21  2021 ccm/
-rw-r--r--   1 root root    246 Feb 21  2018 ccsm-0.9.12.3.egg-info
drwxr-xr-x   2 root root   4096 Jan 21  2021 cffi/
drwxr-xr-x   2 root root   4096 Jan 21  2021 cffi-1.5.2.egg-info/
-rw-r--r--   1 root root 155840 Feb 18  2016 _cffi_backend.x86_64-linux-gnu.so
drwxr-xr-x   2 root root   4096 Mar 10  2019 chardet/
drwxr-xr-x   2 root root   4096 Mar 10  2019 chardet-2.3.0.egg-info/
-rw-r--r--   1 root root    244 Feb 21  2018 compizconfig_python-0.9.12.3.egg-info
-rw-r--r--   1 root root 118272 Feb 21  2018 compizconfig.x86_64-linux-gnu.so
drwxr-xr-x   3 root root   4096 Jan 19  2020 concurrent/
drwxr-xr-x   2 root root   4096 Mar 10  2019 configobj-5.0.6.egg-info/
-rw-r--r--   1 root root  89613 Jul 21  2015 configobj.py
-rw-r--r--   1 root root  67024 Mar 10  2019 configobj.pyc
drwxr-xr-x  10 root root   4096 Mar 10  2019 Crypto/
drwxr-xr-x   4 root root   4096 Nov  7  2020 cryptography/
drwxr-xr-x   2 root root   4096 Nov  7  2020 cryptography-1.2.3.egg-info/
drwxr-xr-x   2 root root   4096 Mar 10  2019 curl/
drwxr-xr-x   2 root root   4096 Jan 17  2021 cycler-0.9.0.egg-info/
-rw-r--r--   1 root root   8289 Jul  3  2015 cycler.py
-rw-r--r--   1 root root  10655 Jan 17  2021 cycler.pyc
drwxr-xr-x   3 root root   4096 Jan 17  2021 dateutil/
drwxr-xr-x   3 root root   4096 Mar 10  2019 dbus/
-rw-r--r--   1 root root 163160 Jan 20  2016 _dbus_bindings.x86_64-linux-gnu.so
-rw-r--r--   1 root root  11040 Jan 20  2016 _dbus_glib_bindings.x86_64-linux-gnu.so
-rw-r--r--   1 root root    146 Apr  4  2016 deb822.py
-rw-r--r--   1 root root    317 Mar 10  2019 deb822.pyc
-rw-r--r--   1 root root   5971 May  8  2019 debconf.py
-rw-r--r--   1 root root   6013 Jun  5  2019 debconf.pyc
drwxr-xr-x   2 root root   4096 Mar 10  2019 debian/
-rw-r--r--   1 root root  16277 Oct 15  2015 debianbts.py
-rw-r--r--   1 root root  15870 Mar 10  2019 debianbts.pyc
drwxr-xr-x   2 root root   4096 Mar 10  2019 debian_bundle/
drwxr-xr-x   2 root root   4096 Jan 16  2021 decorator-4.0.6.egg-info/
-rw-r--r--   1 root root  15682 Dec 10  2015 decorator.py
-rw-r--r--   1 root root  14297 Jan 16  2021 decorator.pyc
drwxr-xr-x   2 root root   4096 Mar 10  2019 defusedxml/
-rw-r--r--   1 root root  35931 Aug 31  2017 defusedxml-0.4.1.egg-info
drwxr-xr-x   2 root root   4096 Sep 30  2018 dfeet/
drwxr-xr-x   2 root root   4096 Apr 22  2021 distro_info-0.14ubuntu0.2.egg-info/
-rw-r--r--   1 root root   9905 Apr 21  2021 distro_info.py
-rw-r--r--   1 root root  10860 Apr 22  2021 distro_info.pyc
drwxr-xr-x   2 root root   4096 Apr 22  2021 distro_info_test/
drwxr-xr-x   2 root root   4096 Mar 10  2019 DNS/
-rw-r--r--   1 root root    126 Apr 10  2016 easy_install.py
-rw-r--r--   1 root root    315 Nov  6  2018 easy_install.pyc
drwxr-xr-x   3 root root   4096 Jan 19  2020 enum/
-rw-r--r--   1 root root  29087 Jan 23  2016 enum34-1.1.2.egg-info
drwxr-xr-x   2 root root   4096 Jun 22  2021 ewmh/
drwxr-xr-x   2 root root   4096 Jun 22  2021 ewmh-0.1.5.egg-info/
drwxr-xr-x   2 root root   4096 Jul 28  2020 eyeD3/
lrwxrwxrwx   1 root root     45 Jun 30  2012 eyeD3-0.6.18.egg-info -> ../../../share/pyshared/eyeD3-0.6.18.egg-info
drwxr-xr-x   2 root root   4096 Jan 19  2020 futures-3.0.5.egg-info/
drwxr-xr-x   5 root root   4096 Aug  3  2018 gi/
drwxr-xr-x   2 root root   4096 Aug  3  2018 glib/
drwxr-xr-x   2 root root   4096 Aug  3  2018 gobject/
drwxr-xr-x   2 root root   4096 Mar 10  2019 gpgme/
drwxr-xr-x   4 root root   4096 Aug  3  2018 gtk-2.0/
drwxr-xr-x   8 root root   4096 Jun 30  2019 html5lib/
drwxr-xr-x   2 root root   4096 Jun 30  2019 html5lib-0.999.egg-info/
drwxr-xr-x   2 root root   4096 Mar 10  2019 httplib2/
-rw-r--r--   1 root root   2272 Oct 23  2015 httplib2-0.9.1.egg-info
drwxr-xr-x   2 root root   4096 Jan 19  2020 idna/
drwxr-xr-x   2 root root   4096 Jan 19  2020 idna-2.0.egg-info/
drwxr-xr-x   3 root root   4096 Aug  2  2018 indicator_keyboard/
drwxr-xr-x   2 root root   4096 Nov  7  2018 iotop/
lrwxrwxrwx   1 root root     42 Jun  7  2013 iotop-0.6.egg-info -> ../../../share/pyshared/iotop-0.6.egg-info
drwxr-xr-x   2 root root   4096 Jan 19  2020 ipaddress-1.0.16.egg-info/
-rw-r--r--   1 root root  79904 Dec 28  2015 ipaddress.py
-rw-r--r--   1 root root  75525 Jan 19  2020 ipaddress.pyc
drwxr-xr-x   5 root root   4096 Mar 10  2019 keyring/
drwxr-xr-x   2 root root   4096 Mar 10  2019 keyring-7.3.egg-info/
drwxr-xr-x   4 root root   4096 Mar 10  2019 launchpadlib/
drwxr-xr-x   2 root root   4096 Mar 10  2019 launchpadlib-1.10.3.egg-info/
drwxr-xr-x   4 root root   4096 Jul 30  2019 lazr/
drwxr-xr-x   2 root root   4096 Jul 30  2019 lazr.restfulclient-0.13.4.egg-info/
drwxr-xr-x   2 root root   4096 Mar 10  2019 lazr.uri-1.0.3.egg-info/
drwxr-xr-x   3 root root   4096 Sep 24  2020 libdiscid/
lrwxrwxrwx   1 root root     38 Aug  2  2018 lsb_release.py -> ../../../share/pyshared/lsb_release.py
-rw-rw-r--   1 root root  11010 Aug  2  2018 lsb_release.pyc
drwxr-xr-x   5 root root   4096 Mar 31  2021 lxml/
drwxr-xr-x   2 root root   4096 Mar 31  2021 lxml-3.5.0.egg-info/
-rw-r--r--   1 root root    217 May 12  2020 Magic_file_extensions-0.2.egg-info
-rw-r--r--   1 root root   6662 Sep 15  2014 magic.py
-rw-r--r--   1 root root   8256 Jul 30  2020 magic.pyc
drwxr-xr-x  13 root root   4096 Jan 17  2021 matplotlib/
drwxr-xr-x   2 root root   4096 Jan 17  2021 matplotlib-1.5.1.egg-info/
-rw-r--r--   1 root root    323 Mar 21  2016 matplotlib-1.5.1-nspkg.pth
drwxr-xr-x   7 root root   4096 Jan 17  2021 mpl_toolkits/
drwxr-xr-x   2 root root   4096 Sep 25  2020 musicbrainzngs/
-rw-r--r--   1 root root    696 Oct 25  2014 musicbrainzngs-0.5.egg-info
drwxr-xr-x   5 root root   4096 Oct 21  2020 mutagen/
-rw-r--r--   1 root root   1448 Jan  7  2016 mutagen-1.31.egg-info
drwxr-xr-x   3 root root   4096 Jan 19  2020 ndg/
drwxr-xr-x   2 root root   4096 Jan 19  2020 ndg_httpsclient-0.4.0.egg-info/
-rw-r--r--   1 root root    296 Nov  5  2015 ndg_httpsclient-0.4.0-nspkg.pth
-rw-r--r--   1 root root  54701 Nov  9  2015 ndiff.py
-rw-r--r--   1 root root  53466 Jun 30  2019 ndiff.pyc
-rw-r--r--   1 root root   2453 Oct 26  2014 notify2-0.3.egg-info
-rw-r--r--   1 root root  11710 May 14  2012 notify2.py
-rw-r--r--   1 root root  13427 Oct 31  2020 notify2.pyc
drwxr-xr-x  15 root root   4096 Dec  4  2019 numpy/
drwxr-xr-x   2 root root   4096 Dec  4  2019 numpy-1.11.0.egg-info/
drwxr-xr-x   2 root root   4096 Mar 10  2019 oauth/
drwxr-xr-x   2 root root   4096 Mar 10  2019 oauth-1.0.1.egg-info/
drwxr-xr-x   3 root root   4096 Jan 19  2020 OpenSSL/
-rw-r--r--   1 root root   6366 Jun 25  2015 pathlib-1.0.1.egg-info
-rw-r--r--   1 root root  41481 Sep  3  2014 pathlib.py
-rw-r--r--   1 root root  44058 Jul 30  2020 pathlib.pyc
drwxr-xr-x   2 root root  20480 Mar 12  2021 PIL/
drwxr-xr-x   2 root root   4096 Mar 12  2021 PILcompat/
-rw-r--r--   1 root root     10 Feb 10  2013 PILcompat.pth
drwxr-xr-x   2 root root   4096 Mar 12  2021 Pillow-3.1.2.egg-info/
drwxr-xr-x  10 root root   4096 Oct  6  2020 pip/
drwxr-xr-x   2 root root   4096 Oct  6  2020 pip-8.1.1.egg-info/
drwxr-xr-x   4 root root   4096 Jul  8  2020 pkg_resources/
drwxr-xr-x   2 root root   4096 Jan 21  2021 ply/
drwxr-xr-x   2 root root   4096 Jan 21  2021 ply-3.7.egg-info/
-rw-r--r--   1 root root  38528 Jan 18  2016 _portaudio.so
-rw-r--r--   1 root root  19808 Oct 23  2015 _posixsubprocess.x86_64-linux-gnu.so
-rw-r--r--   1 root root    890 Dec 30  2013 pyalsaaudio-0.7.egg-info
drwxr-xr-x   5 root root   4096 Jan 19  2020 pyasn1/
drwxr-xr-x   2 root root   4096 Jan 19  2020 pyasn1-0.1.9.egg-info/
-rw-r--r--   1 root root   1540 Jan 18  2016 PyAudio-0.2.8.egg-info
-rw-r--r--   1 root root  38281 Feb 16  2014 pyaudio.py
-rw-r--r--   1 root root  33017 Jan 14  2021 pyaudio.pyc
drwxr-xr-x   2 root root   4096 Jan 21  2021 pycparser/
-rw-r--r--   1 root root    602 Sep 15  2015 pycparser-2.14.egg-info
-rw-r--r--   1 root root    666 Mar 30  2018 pycrypto-2.6.1.egg-info
-rw-r--r--   1 root root   4537 Mar 10  2016 pycurl-7.43.0.egg-info
-rw-r--r--   1 root root 128176 Mar 10  2016 pycurl.x86_64-linux-gnu.so
-rw-r--r--   1 root root    755 Feb 17  2014 pydns-2.3.6.egg-info
drwxr-xr-x  10 root root   4096 May  1  2021 pyglet/
-rw-r--r--   1 root root   1039 Dec 14  2015 pyglet-1.1.4.egg-info
-rw-r--r--   1 root root   1013 Mar 25  2016 pygobject-3.20.0.egg-info
-rw-r--r--   1 root root    889 Mar 31  2016 pygpgme-0.3.egg-info
drwxr-xr-x   2 root root   4096 Aug  3  2018 pygtkcompat/
-rw-r--r--   1 root root      8 Jan 28  2016 pygtk.pth
-rw-r--r--   1 root root   2966 Jan 28  2016 pygtk.py
-rw-r--r--   1 root root   2051 Aug  3  2018 pygtk.pyc
drwxr-xr-x   2 root root   4096 May  2 11:49 PyKate4/
-rw-r--r--   1 root root     90 Jan 10  2016 pylab.py
-rw-r--r--   1 root root    240 Jan 17  2021 pylab.pyc
drwxr-xr-x   2 root root   4096 Jan 19  2020 pyOpenSSL-0.15.1.egg-info/
drwxr-xr-x   2 root root   4096 Jan 17  2021 pyparsing-2.0.3.egg-info/
-rw-r--r--   1 root root 158256 Aug 15  2014 pyparsing.py
-rw-r--r--   1 root root 156779 Jan 17  2021 pyparsing.pyc
drwxr-xr-x   2 root root   4096 Mar 10  2019 pysimplesoap/
-rw-r--r--   1 root root    246 Apr 29  2021 python_apt-1.1.0.b1_ubuntu0.16.04.12.egg-info
drwxr-xr-x   2 root root   4096 Jan 17  2021 python_dateutil-2.4.2.egg-info/
drwxr-xr-x   2 root root   4096 Mar 10  2019 python_debian-0.1.27.egg-info/
-rw-r--r--   1 root root    716 Oct 23  2015 python_debianbts-2.6.0.egg-info
drwxr-xr-x   2 root root   4096 Sep 24  2020 python_libdiscid-0.4.1.egg-info/
-rw-r--r--   1 root root    209 Jan 18  2016 python_sane-2.8.2.egg-info
-rw-r--r--   1 root root    242 Sep 14  2015 python_xlib-0.14.egg-info
drwxr-xr-x   2 root root   4096 Nov 22  2020 pytz/
drwxr-xr-x   2 root root   4096 Nov 22  2020 pytz-2014.10.egg-info/
drwxr-xr-x   2 root root   4096 Dec 14  2021 pyudev/
drwxr-xr-x   2 root root   4096 Dec 14  2021 pyudev-0.16.1.egg-info/
-rw-r--r--   1 root root   1665 Jan 18  2016 PyYAML-3.11.egg-info
-rw-r--r--   1 root root    119 Mar  1  2021 README
drwxr-xr-x   3 root root   4096 Mar 10  2019 reportbug/
drwxr-xr-x   2 root root   4096 Mar 10  2019 reportbug-6.6.6ubuntu1.egg-info/
drwxr-xr-x   3 root root   4096 Sep 26  2020 requests/
drwxr-xr-x   2 root root   4096 Sep 26  2020 requests-2.9.1.egg-info/
-rw-r--r--   1 root root  13594 Aug  7  2015 sane.py
-rw-r--r--   1 root root  15423 Dec  4  2019 sane.pyc
-rw-r--r--   1 root root  45496 Jan 18  2016 _sane.x86_64-linux-gnu_d.so
-rw-r--r--   1 root root  19768 Jan 18  2016 _sane.x86_64-linux-gnu.so
drwxr-xr-x  21 root root   4096 Jan 16  2021 scipy/
-rw-r--r--   1 root root   2103 Jan 26  2016 scipy-0.17.0.egg-info
drwxr-xr-x   2 root root   4096 Mar 10  2019 secretstorage/
-rw-r--r--   1 root root   4120 Dec 20  2015 SecretStorage-2.1.3.egg-info
drwxr-xr-x   4 root root   4096 Nov  6  2018 setuptools/
drwxr-xr-x   2 root root   4096 Nov  6  2018 setuptools-20.7.0.egg-info/
drwxr-xr-x   3 root root   4096 Mar 10  2019 simplejson/
-rw-r--r--   1 root root   2735 Jan 18  2016 simplejson-3.8.1.egg-info
drwxr-xr-x   2 root root   4096 Mar 10  2019 six-1.10.0.egg-info/
-rw-r--r--   1 root root  30098 Oct  6  2015 six.py
-rw-r--r--   1 root root  30098 Mar 10  2019 six.pyc
drwxr-xr-x   2 root root   4096 Mar 10  2019 SOAPpy/
drwxr-xr-x   2 root root   4096 Mar 10  2019 SOAPpy-0.12.22.egg-info/
-rw-r--r--   1 root root    641 Oct 23  2015 subprocess32-3.2.6.egg-info
-rw-r--r--   1 root root  74362 Apr 23  2014 subprocess32.py
-rw-r--r--   1 root root  49677 Sep 15  2020 subprocess32.pyc
-rw-r--r--   1 root root  10888 Mar 14  2016 talloc.x86_64-linux-gnu.so
drwxr-xr-x   2 root root   4096 Nov 22  2020 tkcalendar/
drwxr-xr-x   2 root root   4096 Nov 22  2020 tkcalendar-1.5.0.egg-info/
drwxr-xr-x   7 root root   4096 Oct 24  2020 ttkwidgets/
drwxr-xr-x   2 root root   4096 Oct 24  2020 ttkwidgets-0.10.0.egg-info/
drwxr-xr-x   2 root root   4096 Mar 10  2019 ubuntu_dev_tools-0.155ubuntu2.egg-info/
drwxr-xr-x   6 root root   4096 Mar 10  2019 ubuntutools/
-rw-r--r--   1 root root    258 Mar 18  2014 unity_lens_photos-1.0.egg-info
drwxr-xr-x   5 root root   4096 Oct  6  2020 urllib3/
drwxr-xr-x   2 root root   4096 Oct  6  2020 urllib3-1.13.1.egg-info/
-rw-r--r--   1 root root  47237 Aug 25  2014 validate.py
-rw-r--r--   1 root root  47556 Mar 10  2019 validate.pyc
-rw-r--r--   1 root root     21 Aug 25  2014 _version.py
-rw-r--r--   1 root root    163 Mar 10  2019 _version.pyc
drwxr-xr-x   3 root root   4096 Mar 10  2019 wadllib/
drwxr-xr-x   2 root root   4096 Mar 10  2019 wadllib-1.3.2.egg-info/
drwxr-xr-x   5 root root   4096 Nov  6  2018 wheel/
drwxr-xr-x   2 root root   4096 Nov  6  2018 wheel-0.29.0.egg-info/
drwxr-xr-x   3 root root   4096 Mar 10  2019 wstools/
drwxr-xr-x   2 root root   4096 Mar 10  2019 wstools-0.4.3.egg-info/
drwxr-xr-x   7 root root   4096 Jan 27  2020 Xlib/
drwxr-xr-x   2 root root   4096 Sep 27  2020 yaml/
-rw-r--r--   1 root root 190912 Jan 18  2016 _yaml.so
drwxr-xr-x   3 root root   4096 Mar 10  2019 zope/
drwxr-xr-x   2 root root   4096 Mar 10  2019 zope.interface-4.1.3.egg-info/
-rw-r--r--   1 root root    299 Jan 18  2016 zope.interface-4.1.3-nspkg.pth

    '''

    return


def main(caller=None):
    """
    Load saved configuration if it exists. Otherwise create new configuration.
    Loop through every configuration dictionary and tests if it exists.

    Set flags on what modules/methods exist. The flags are used to check which
    features will work. E.G. if 'xdo-tool' is not available 'kid3' window cannot
    be moved.

    Save configuration so tests can be skipped next time.

    """
    print("mserve_config.py startup called from:", caller)
    make_default_cfg()  # Create default configuration
    for cfg_dict in DEFAULT_CFG:
        print("Default Configuration Dictionary for:", cfg_dict['caller'])
        for key in cfg_dict:
            if key is not "caller":
                print("\t", key.ljust(10), ":", cfg_dict[key])
    
    ''' from: https://www.tutorialspoint.com/
    How-to-find-which-Python-modules-are-being-imported-from-a-package '''
    #modules = inspect.getmembers(os)
    #results = filter(lambda m: inspect.ismodule(m[1]), modules)

    #print('\nThe list of imported Python modules reported by inspect are :')
    #for o in results:
    #    print(o)
    #print()

    #print('\nThe list of imported Python modules reported by sys.modules :')
    #print(sys.modules.keys())
    #print()

    #modules = dir()
    #print('The list of imported Python modules reported by dir() :', modules)

    ''' The following generates error:
location.py was forced to run g.init()
Traceback (most recent call last):
  File "./m", line 25, in <module>
    import image as img     # Pippim functions for image management
  File "/home/rick/python/image.py", line 76, in <module>
    import monitor              # Screen, Monitor and Window functions
  File "/home/rick/python/monitor.py", line 41, in <module>
    import sql                  # SQLite3 functions
  File "/home/rick/python/sql.py", line 48, in <module>
    from location import FNAME_LIBRARY  # SQL database name (SQLite3 format)
  File "/home/rick/python/location.py", line 101, in <module>
    FNAME_LOCATIONS        = MSERVE_DIR + "locations"
TypeError: unsupported operand type(s) for +: 'NoneType' and 'str'
    
    '''
    ''' from: https://stackoverflow.com/a/4858123/6929343 '''
    try:
        import types
        #print('The list of imported Python modules reported by types.ModuleType :')
        for name, val in globals().items():
            if isinstance(val, types.ModuleType):
                #yield val.__name__
                #print('import %s as %s' % (val.__name__, name))
                pass
    except ImportError:  # No module named types
        print("types cannot be imported")

    ''' from: https://stackoverflow.com/a/40381601/6929343 '''
    #print("\n From: https://stackoverflow.com/a/40381601/6929343 :")
    #after = [str(m) for m in sys.modules]
    #print([m for m in after if m not in before])

    print("\nsys.path:", sys.path)
    return True  # All tests succeeded :)


if __name__ == "__main__":
    main(caller=None)

# End of mserve_configy.py
