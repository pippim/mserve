#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: Pippim
License: GNU GPLv3
Source: This repository
Description: mserve - Music Server - Dependencies Checker and Setup
"""

from __future__ import print_function  # Must be first import
from __future__ import with_statement  # Error handling for file opens

# ==============================================================================
#
#       mserve_config.py - Check modules to be imported are available.
#
#       July 10 2023 - Initial version.
#       Sep. 08 2023 - Add new module calc.py to mserve.py dependencies
#       Sep. 11 2023 - Generate line counts for Website Dashboard
#       Jan. 17 2024 - "locale" required by mserve.py and toolkit.py
#       Feb. 17 2024 - "math" required by sql.py. Fix version 2.7.12 testing
#
# ==============================================================================
# from __future__ import unicode_literals  # Not needed.

try:
    import warnings  # 'warnings' advises which commands aren't supported
    warnings.simplefilter('default')  # in future Python versions.
except ImportError:
    pass

""" Called by 'm' or called by 'mserve.py' if 'm' was skipped. """

''' Check Python version is minimal 2.7.12 '''
import sys

current_version = "Python 2.7.12 or a more recent version is required.\n" + \
    "           Version installed is: " + str(sys.version_info[0]) + "." + \
    str(sys.version_info[1]) + "." + str(sys.version_info[2])
# Test notes below will force failure even if you are already on version 2.7.12
if sys.version_info[0] < 2:  # test change 2 to 4
    raise Exception("001: " + current_version)
if sys.version_info[0] == 2 and sys.version_info[1] < 7:  # test change 7 to 8
    raise Exception("002: " + current_version)
if sys.version_info[0] == 2 and sys.version_info[1] == 7 and \
        sys.version_info[2] < 12:
    raise Exception("003: " + current_version)

import os
import inspect
import importlib

''' Code duplicated in global_variables.py '''
import platform as plat  # Gets OS Name, Version, Release
OS_PLATFORM = plat.platform()  # 'Linux-4.14.216-0414216-generic-x86_64-with-Ubuntu-16.04-xenial'
OS_NAME = plat.system()  # 'Linux'
OS_VERSION = plat.release()  # '4.14.216-0414216-generic'
OS_RELEASE = plat.version()  # '#202101171339 SMP Sun Jan 17 13:56:04 UTC 2021'


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


def main(caller=None):
    """
    Load saved configuration if it exists. Otherwise create new configuration.
    Loop through every configuration dictionary and tests if it exists.

    Set flags on what packages/modules exist. The flags are used to check which
    features will work. E.G. if 'xdo-tool' is not available 'kid3' window cannot
    be moved.

    Save configuration so tests can be skipped next time. Whenever an error
    occurs, mserve can be called with 'fix' option and saved configuration is
    deleted and the process repeats.

    """
    # print("mserve_config.py startup called from:", caller)
    make_default_cfg()  # Create default configuration

    if True is False:
        print("caller:", caller)
        print("len(sys.argv):", len(sys.argv))

    parm1 = parm2 = None
    if (len(sys.argv)) >= 2:
        parm1 = sys.argv[1]
        # print("parm1:", parm1)

    if (len(sys.argv)) >= 3:
        parm2 = sys.argv[2]
        # print("parm2:", parm2)

    ''' 
    cfg_dict = \
        {"module": module,
         "imp_as": imp_as,
         "imp_from": imp_from,
         "developer": developer,
         "version": version,
         "ubuntu": ubuntu,
         "required": required}
    '''
    pippim_modules = []
    for cfg_dict in DEFAULT_CFG:  # "ubuntu"
        # print("Default Configuration Dictionary for:", cfg_dict['module'])
        for key in cfg_dict:
            if key is not "module":
                if key is "developer" and cfg_dict[key] and cfg_dict[key] == "pippim.com":
                    if not cfg_dict['imp_from'] + ".py" in pippim_modules:
                        pippim_modules.append(cfg_dict['imp_from'] + ".py")

    """ mserve Python Modules Line Counts for Website 

        Called from ~/website/sede/refresh.sh (programs/mserve.md NOT refreshed):

            python mserve_config.py line_count ~/website/programs/mserve_incl.md

        Inside ~/website/programs/mserve.md (NOT refreshed by refresh.sh):
            ## Programs at a Glance
            {:.no_toc}
            {% include_relative mserve_incl.md %}

        NOTE: If you change ~/website/programs/mserve.md, you must manually commit
              as ~/website/sede/refresh.sh NEVER refreshes markdown in pippim.com.
              If you change ~/website2/programs/mserve.md, GitHub will probably
              update when refresh.sh runs, but this hasn't been tested.

    """
    pippim_modules.sort()  # Alphanumeric sort
    total = 0
    #                   12345678901234567890
    # Longest module:   global_variables.py
    MOD = 145  # Module Name maximum width
    LINE = 7  # Maximum line count size 999,999, align right
    DATE = 19  # Date fixed size, align center
    DESC = 39  # Program description
    pippim_report = "## Python Modules used in {{ site.title }} **mserve** "
    if parm1 and parm1 == "line_count":
        import global_variables as g
        g.init()
        pippim_report += "Version " + g.MSERVE_VERSION + "\n{:.no_toc}\n\n"
        pippim_report += "| Python Module" + " " * (MOD - 12) + "|   Lines |      Modified       |"
        pippim_report += " Description                             |\n"
        pippim_report += "|-" + "-" * MOD + "-|--------:|:-------------------:|"
        pippim_report += "-----------------------------------------|\n"
    for module in pippim_modules:
        # print("module:", module)
        if module == "m.py":
            module = "m"  # remove `.py` extension automatically applied earlier
        if parm1 and parm1 == "line_count":
            name = "[`" + module + "`]"  # ' ⧉' needs unicode, skip it Sep 20/23
            name += "(https://github.com/pippim/mserve/blob/main/src/" + module
            name += ' "View mserve Python source code"){:target="_blank"}'
            line = os.popen("wc -l " + module).read().strip()
            if len(line) < 2:  # Shortest is "83 m"
                line = "Missing"

            desc = os.popen("grep ^'Description: mserve' " + module).read().strip()
            if len(desc) < 20:
                desc = "Description not found!"
            desc = desc.replace("Description: mserve - Music Server - ", "")

            date = os.popen('date -r ' + module + ' "+%Y-%m-%d %H:%M:%S"'). \
                read().strip()
            if len(date) < 10:
                date = "No Date!"
            if line != "Missing":
                val = int(line.split()[0])  # Drop program name at end
                total += val
                line = '{:,}'.format(val)  # int to string
            pippim_report += "| " + name.ljust(MOD)
            pippim_report += " | " + line.rjust(LINE)
            pippim_report += " | " + date.ljust(DATE)
            pippim_report += " | " + desc.ljust(DESC) + " |\n"

    if parm1 and parm1 == "line_count":
        pippim_report += "| " + "ALL Modules".ljust(MOD)
        pippim_report += " | " + '{:,}'.format(total).rjust(LINE)
        pippim_report += " | " + " ".ljust(DATE)  # Fake empty date & description
        pippim_report += " | " + " ".ljust(DESC) + " |\n"

        if parm2:
            ''' Parameter 2 has output filename:
                ~/website2/programs/mserve_incl.md '''
            import external as ext
            # ext calls timefmt which calls g.init() so want to rewrite
            ext.write_from_string(parm2, pippim_report)
        else:
            # No output file so print instead
            print("\nmserve_config.py - No output filename passed in parm #2\n")
            print(pippim_report)

    """
        REVIEW:

            Note that the exact times you set here may not be returned by a 
            subsequent stat() call, depending on the resolution with which 
            your operating system records access and modification times; see stat().

            import os
            os.utime(path_to_file, (access_time, modification_time))
            https://www.tutorialspoint.com/python/os_utime.htm
            How is atime and mtime formatted? 
            The exact meaning and resolution of the st_atime, st_mtime, and 
            st_ctime attributes depend on the operating system and the file 
            system. For example, on Windows systems using the FAT or FAT32 
            file systems, st_mtime has 2-second resolution, and st_atime has 
            only 1-day resolution. See your operating system documentation 
            for details. '''
        time_fmt = os.stat_float_times()
        print("time_fmt:", time_fmt)
    """

    time_fmt = os.stat_float_times()
    if not time_fmt:
        print("os.utime cannot be used to reset access time")

    # print(pippim_modules)
    # noinspection SpellCheckingInspection
    ''' os.walk() path and merge results with default configuration dictionary to 
        make machine configuration dictionary

        sys.path = ['/home/rick/python',  # Also walk subdirs /pulsectl, etc.
        '/usr/lib/python2.7', 
        '/usr/lib/python2.7/plat-x86_64-linux-gnu',
        '/usr/lib/python2.7/lib-tk', 
        '/usr/lib/python2.7/lib-old', 
        '/usr/lib/python2.7/lib-dynload', 
        '/home/rick/.local/lib/python2.7/site-packages', 
        '/usr/local/lib/python2.7/dist-packages', 
        '/usr/lib/python2.7/dist-packages', 
        '/usr/lib/python2.7/dist-packages/PILcompat', 
        '/usr/lib/python2.7/dist-packages/gtk-2.0']        

    '''

    ''' from: https://www.tutorialspoint.com/
    How-to-find-which-Python-modules-are-being-imported-from-a-package '''
    # modules = inspect.getmembers(os)
    # results = filter(lambda m: inspect.ismodule(m[1]), modules)

    # print('\nThe list of imported Python modules reported by inspect are :')
    # for o in results:
    #    print(o)
    # print()

    # print('\nThe list of imported Python modules reported by sys.modules :')
    # print(sys.modules.keys())
    # print()

    # modules = dir()
    # print('The list of imported Python modules reported by dir() :', modules)

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
        import types  # Part of Python standard library
        # print('The list of imported Python modules reported by types.ModuleType :')
        for name, val in globals().items():
            if isinstance(val, types.ModuleType):
                # yield val.__name__
                # print('import %s as %s' % (val.__name__, name))
                pass
    except ImportError:  # No module named types
        # print("types cannot be imported")
        pass

    ''' from: https://stackoverflow.com/a/40381601/6929343 '''
    # print("\n From: https://stackoverflow.com/a/40381601/6929343 :")
    # after = [str(m) for m in sys.modules]
    # print([m for m in after if m not in before])

    # print("\n sys.path:", sys.path)
    return True  # All tests succeeded :)


def make_default_cfg():
    """ When no configuration exists, create this default version. """
    global DEFAULT_CFG
    DEFAULT_CFG += make_g_cfg()  # Configuration for global_variables.py
    DEFAULT_CFG += make_m_cfg()  # Splash screen 'm' un-fudged in stats from "m.py"
    DEFAULT_CFG += make_mserve_cfg()  # for mserve.py
    DEFAULT_CFG += make_vup_cfg()  # for vu_pulse_audio.py
    DEFAULT_CFG += make_vum_cfg()  # for vu_meter.py
    DEFAULT_CFG += make_toolkit_cfg()  # toolkit.py
    DEFAULT_CFG += make_tmf_cfg()  # for timefmt.py
    DEFAULT_CFG += make_ext_cfg()  # for external.py
    DEFAULT_CFG += make_msg_cfg()  # for message.py
    DEFAULT_CFG += make_sql_cfg()  # for sql.py
    DEFAULT_CFG += make_lc_cfg()  # for location.py
    DEFAULT_CFG += make_mon_cfg()  # for monitor.py
    DEFAULT_CFG += make_img_cfg()  # for image.py
    DEFAULT_CFG += make_x11_cfg()  # for x11.py
    DEFAULT_CFG += make_web_cfg()  # for webscrape.py
    ''' All the modules used by encoding.py '''
    DEFAULT_CFG += make_encoding_cfg()  # for encoding.py
    DEFAULT_CFG += make_disc_cfg()  # for disc_get.py
    DEFAULT_CFG += make_mbz1_cfg()  # for mbz_get1.py
    DEFAULT_CFG += make_mbz2_cfg()  # for mbz_get2.py


# noinspection SpellCheckingInspection
def make_g_cfg():
    """ Configuration for: 'import global_variables as g' """
    cfg = list()  # Return list of dictionaries
    m = "global_variables"  # Module name to python interpreter
    cfg.append(make_dict(m, "user_data_dir", "appdirs"))
    cfg.append(make_dict(m, "user_config_dir", "appdirs"))
    cfg.append(make_dict(m, None, "tempfile"))
    cfg.append(make_dict(m, None, "os"))
    cfg.append(make_dict(m, None, "pwd"))
    cfg.append(make_dict(m, None, "webbrowser"))
    return cfg


def make_m_cfg():
    """ Configuration for: 'm' which is never imported """
    cfg = list()  # Return list of dictionaries
    m = "m"  # Module name to python interpreter
    cfg.extend(make_tk_cfg(m))  # All the tkinter stuff, only need first though
    cfg.append(make_dict(m, None, "sys"))
    cfg.append(make_dict(m, None, "os"))
    cfg.append(make_dict(m, "g", "global_variables", "pippim.com"))
    cfg.append(make_dict(m, "img", "image", "pippim.com"))
    cfg.append(make_dict(m, "mon", "monitor", "pippim.com"))
    cfg.append(make_dict(m, None, "mserve", "pippim.com"))
    # Modules not imported. Add here for statistics.
    cfg.append(make_dict(m, None, "m", "pippim.com"))  # 'm' for stats
    cfg.append(make_dict(m, None, "vu_meter", "pippim.com"))  # also for stats
    cfg.append(make_dict(m, None, "webscrape", "pippim.com"))  # also for stats
    cfg.append(make_dict(m, "cfg", "mserve_config", "pippim.com"))  # also for stats
    return cfg


def make_mserve_cfg():
    """ Configuration for: 'import mserve' called by 'm' """
    cfg = list()  # Return list of dictionaries
    m = "mserve"  # Module name to python interpreter
    d1 = "https://github.com/TkinterEP/ttkwidgets"

    cfg.extend(make_tk_cfg(m))  # All the tkinter stuff (7 modules)
    cfg.extend(make_PIL_cfg(m))  # More than needed 
    cfg.append(make_dict(m, "CheckboxTreeview", "ttkwidgets", d1, None, 
                         "python-ttkwidgets"))

    #cfg.append(make_dict(m, None, "signal"))  # only in python 3.5, 3.6, 3.7
    #TypeError: <module 'signal' (built-in)> is a built-in module - version 2.7
    cfg.append(make_dict(m, None, "signal", required=False))

    cfg.append(make_dict(m, None, "subprocess32", required=False))
    cfg.append(make_dict(m, None, "threading"))  # Confirm it's used?
    cfg.append(make_dict(m, None, "sys"))
    cfg.append(make_dict(m, None, "os"))
    cfg.append(make_dict(m, None, "shutil"))
    cfg.append(make_dict(m, None, "json"))  # sudo apt install simplejson [auto]
    cfg.append(make_dict(m, None, "glob"))
    cfg.append(make_dict(m, None, "time"))
    cfg.append(make_dict(m, None, "datetime"))
    cfg.append(make_dict(m, None, "re"))
    cfg.append(make_dict(m, None, "traceback"))
    cfg.append(make_dict(m, None, "locale"))
    # noinspection SpellCheckingInspection
    cfg.append(make_dict(m, None, "webbrowser"))
    cfg.append(make_dict(m, None, "requests"))
    cfg.append(make_dict(m, "BytesIO", "io"))
    cfg.append(make_dict(m, None, "random"))
    cfg.append(make_dict(m, None, "string"))
    cfg.append(make_dict(m, "OrderedDict", "collections"))
    cfg.append(make_dict(m, None, "pickle"))
    cfg.append(make_dict(m, "shuffle", "random"))
    cfg.append(make_dict(m, None, "locale"))

    d2 = "https://github.com/numpy/numpy"
    d3 = "https://pypi.org/project/notify2/"
    d4 = "https://www.selenium.dev/documentation/webdriver/"
    cfg.append(make_dict(m, "np", "numpy", d2, "3", "python3-numpy"))
    cfg.append(make_dict(m, "np", "numpy", d2, "2", "python-numpy"))
    cfg.append(make_dict(m, None, "notify2", d3, "3", "python3-notify2"))
    cfg.append(make_dict(m, None, "notify2", d3, "2", "python-notify2"))
    cfg.append(make_dict(m, None, "selenium", d4, "3", "python3-selenium"))
    cfg.append(make_dict(m, None, "selenium", d4, "2", "python-selenium"))

    cfg.append(make_dict(m, "g", "global_variables", "pippim.com"))
    cfg.append(make_dict(m, "lc", "location", "pippim.com"))
    cfg.append(make_dict(m, None, "message", "pippim.com"))
    cfg.append(make_dict(m, None, "encoding", "pippim.com"))
    cfg.append(make_dict(m, "ext", "external", "pippim.com"))
    cfg.append(make_dict(m, "img", "image", "pippim.com"))
    cfg.append(make_dict(m, None, "sql", "pippim.com"))
    cfg.append(make_dict(m, None, "monitor", "pippim.com"))  # Not "as mon"
    cfg.append(make_dict(m, None, "toolkit", "pippim.com"))
    cfg.append(make_dict(m, "tmf", "timefmt", "pippim.com"))
    cfg.append(make_dict(m, None, "webscrape", "pippim.com"))
    cfg.append(make_dict(m, None, "vu_pulse_audio", "pippim.com"))
    cfg.append(make_dict(m, None, "calc", "pippim.com"))
    return cfg


def make_vup_cfg():
    """ Configuration for: 'import vu_pulse_audio as vup' """
    cfg = list()  # Return list of dictionaries
    m = "vu_pulse_audio"  # Module name to python interpreter
    d = "github.com/mk-fg/python-pulse-control"
    cfg.append(make_dict(m, None, "os"))
    cfg.append(make_dict(m, None, "time"))
    cfg.append(make_dict(m, "OrderedDict", "Collections"))
    cfg.append(make_dict(m, "namedtuple", "Collections"))
    cfg.append(make_dict(m, "pulsectl", "pulsectl", d))
    cfg.append(make_dict(m, "g", "global_variables", "pippim.com"))
    cfg.append(make_dict(m, "ext", "external", "pippim.com"))
    cfg.append(make_dict(m, "tmf", "timefmt", "pippim.com"))
    cfg.append(make_dict(m, None, "toolkit", "pippim.com"))
    return cfg


def make_vum_cfg():
    """ Configuration for: 'os.popen("vu_meter.py... &")' """
    cfg = list()  # Return list of dictionaries
    m = "vu_meter"  # Module name to python interpreter
    d1 = "https://github.com/jleb/pyaudio/tree/master"
    d2 = "https://github.com/numpy/numpy"
    cfg.append(make_dict(m, None, "sys"))
    cfg.append(make_dict(m, None, "math"))
    cfg.append(make_dict(m, None, "struct"))
    cfg.append(make_dict(m, None, "pyaudio", d1, "3", "python3-pyaudio"))
    cfg.append(make_dict(m, None, "pyaudio", d1, "2", "python-pyaudio"))
    cfg.append(make_dict(m, "np", "numpy", d2, "3", "python3-numpy"))
    cfg.append(make_dict(m, "np", "numpy", d2, "2", "python-numpy"))
    cfg.append(make_dict(m, "g", "global_variables", "pippim.com"))
    return cfg


def make_toolkit_cfg():
    """ Configuration for: 'import toolkit' """
    '''
        Optional gnome_screenshot() for MoveTreeviewColumn function imports:
            import gi
            gi.require_version('Gdk', '3.0')
            gi.require_version('Gtk', '3.0')
            gi.require_version('Wnck', '3.0')
            # gi.require_versions({"Gtk": "3.0", "Gdk": "3.0", "Wnck": "3.0"})
            from gi.repository import Gdk, Gdk Pix buf, Gtk, Wnck
    '''
    cfg = list()  # Return list of dictionaries
    m = "toolkit"  # Module name to python interpreter
    d = "https://github.com/TkinterEP/ttkwidgets"
    cfg.extend(make_tk_cfg(m))
    cfg.extend(make_PIL_cfg(m))
    cfg.append(make_dict(m, "CheckboxTreeview", "ttkwidgets", d, None, 
                         "python-ttkwidgets"))
    cfg.append(make_dict(m, None, "os"))
    cfg.append(make_dict(m, None, "time"))
    cfg.append(make_dict(m, None, "datetime"))
    cfg.append(make_dict(m, "namedtuple", "collections"))
    cfg.append(make_dict(m, "OrderedDict", "collections"))
    cfg.append(make_dict(m, None, "re"))
    cfg.append(make_dict(m, None, "traceback"))
    cfg.append(make_dict(m, None, "locale"))
    cfg.append(make_dict(m, "g", "global_variables", "pippim.com"))
    cfg.append(make_dict(m, "ext", "external", "pippim.com"))
    cfg.append(make_dict(m, "img", "image", "pippim.com"))
    return cfg


def make_tmf_cfg():
    """ Configuration for: 'import timefmt as tmf' """
    cfg = list()  # Return list of dictionaries
    m = "monitor"  # Module name to python interpreter
    cfg.append(make_dict(m, None, "time"))
    cfg.append(make_dict(m, None, "datetime"))
    cfg.append(make_dict(m, "namedtuple", "collections"))
    return cfg


def make_ext_cfg():
    """ Configuration for: 'import external as ext' """
    cfg = list()  # Return list of dictionaries
    m = "external"  # Module name to python interpreter
    #cfg.append(make_dict(m, None, "signal"))  # only in python 3.5, 3.6, 3.7
    #TypeError: <module 'signal' (built-in)> is a built-in module - version 2.7
    cfg.append(make_dict(m, None, "signal", required=False))
    cfg.append(make_dict(m, None, "subprocess32", required=False))
    cfg.append(make_dict(m, None, "subprocess"))
    cfg.append(make_dict(m, None, "os"))
    cfg.append(make_dict(m, None, "errno"))
    cfg.append(make_dict(m, None, "json"))
    cfg.append(make_dict(m, None, "glob"))
    cfg.append(make_dict(m, None, "datetime"))
    cfg.append(make_dict(m, None, "pickle"))

    cfg.append(make_dict(m, None, "toolkit", "pippim.com"))
    return cfg


def make_msg_cfg():
    """ Configuration for: 'import message' """
    cfg = list()  # Return list of dictionaries
    m = "message"  # Module name to python interpreter
    cfg.append(make_dict(m, None, "pprint"))  # Not sure why first...
    cfg.extend(make_tk_cfg(m))
    #cfg.append(make_dict(m, None, "signal"))  # only in python 3.5, 3.6, 3.7
    #TypeError: <module 'signal' (built-in)> is a built-in module - version 2.7
    cfg.append(make_dict(m, None, "signal", required=False))
    cfg.append(make_dict(m, None, "os"))
    cfg.append(make_dict(m, None, "errno"))
    cfg.append(make_dict(m, None, "subprocess32", required=False))
    cfg.append(make_dict(m, None, "re"))
    cfg.append(make_dict(m, None, "time"))
    cfg.append(make_dict(m, None, "datetime"))
    # noinspection SpellCheckingInspection
    cfg.append(make_dict(m, None, "webbrowser"))
    cfg.append(make_dict(m, "g", "global_variables", "pippim.com"))
    cfg.append(make_dict(m, "img", "image", "pippim.com"))
    cfg.append(make_dict(m, "ext", "external", "pippim.com"))
    cfg.append(make_dict(m, "tmf", "timefmt", "pippim.com"))
    cfg.append(make_dict(m, None, "toolkit", "pippim.com"))
    return cfg


def make_sql_cfg():
    """ Configuration for: 'import sql' """
    cfg = list()  # Return list of dictionaries
    m = "sql"  # Module name to python interpreter
    cfg.append(make_dict(m, None, "os"))
    cfg.append(make_dict(m, None, "re"))
    cfg.append(make_dict(m, None, "json"))
    cfg.append(make_dict(m, None, "math"))
    cfg.append(make_dict(m, None, "time"))
    cfg.append(make_dict(m, None, "datetime"))
    cfg.append(make_dict(m, "namedtuple", "collections"))
    cfg.append(make_dict(m, "OrderedDict", "collections"))
    cfg.append(make_dict(m, None, "sqlite3/__init__",
                         "https://docs.python.org/3/library/sqlite3.html"))
    # Module - /usr/lib/python2.7/sqlite3/__init__.py
    cfg.append(make_dict(m, "g", "global_variables", "pippim.com"))
    cfg.append(make_dict(m, "tmf", "timefmt", "pippim.com"))
    cfg.append(make_dict(m, "ext", "external", "pippim.com"))
    cfg.append(make_dict(m, "FNAME_LIBRARY", "location", "pippim.com"))
    return cfg


def make_lc_cfg():
    """ Configuration for: 'import location as lc' """
    cfg = list()  # Return list of dictionaries
    m = "location"  # Module name to python interpreter
    cfg.extend(make_tk_cfg(m))
    cfg.extend(make_PIL_cfg(m))
    # Python Standard Library
    cfg.append(make_dict(m, None, "os"))
    cfg.append(make_dict(m, None, "sys"))
    cfg.append(make_dict(m, None, "errno"))
    cfg.append(make_dict(m, None, "shutil"))
    cfg.append(make_dict(m, None, "time"))
    cfg.append(make_dict(m, None, "pickle"))
    cfg.append(make_dict(m, None, "time"))
    cfg.append(make_dict(m, None, "datetime"))
    cfg.append(make_dict(m, "OrderedDict", "collections"))

    # Pippim modules
    cfg.append(make_dict(m, "g", "global_variables", "pippim.com"))
    cfg.append(make_dict(m, None, "sql", "pippim.com"))
    cfg.append(make_dict(m, None, "toolkit", "pippim.com"))
    cfg.append(make_dict(m, None, "message", "pippim.com"))
    cfg.append(make_dict(m, None, "monitor", "pippim.com"))  # Not "as mon"
    cfg.append(make_dict(m, "img", "image", "pippim.com"))
    cfg.append(make_dict(m, "tmf", "timefmt", "pippim.com"))
    cfg.append(make_dict(m, "ext", "external", "pippim.com"))
    return cfg


def make_mon_cfg():
    """ Configuration for: 'import monitor as mon' 
        Most times it is simply 'import monitor' """
    cfg = list()  # Return list of dictionaries
    m = "monitor"  # Module name to python interpreter
    cfg.extend(make_tk_cfg(m))
    cfg.append(make_dict(m, None, "os"))
    cfg.append(make_dict(m, None, "sys"))
    cfg.append(make_dict(m, None, "time"))
    cfg.append(make_dict(m, "namedtuple", "collections"))
    cfg.append(make_dict(m, "OrderedDict", "collections"))
    cfg.append(make_dict(m, "g", "global_variables", "pippim.com"))
    cfg.append(make_dict(m, "img", "image", "pippim.com"))
    cfg.append(make_dict(m, None, "sql", "pippim.com"))
    return cfg


def make_img_cfg():
    """ Configuration for: 'import image as img' """
    cfg = list()  # Return list of dictionaries
    m = "image"  # Module name to python interpreter
    cfg.extend(make_tk_cfg(m))
    cfg.extend(make_PIL_cfg(m))
    cfg.append(make_dict(m, None, "os"))
    cfg.append(make_dict(m, None, "re"))
    cfg.append(make_dict(m, None, "time"))
    cfg.append(make_dict(m, None, "datetime"))
    cfg.append(make_dict(m, None, "io"))
    cfg.append(make_dict(m, "namedtuple", "collections"))
    cfg.append(make_dict(m, None, "x11", "pippim.com"))  # Under review
    cfg.append(make_dict(m, "ext", "external", "pippim.com"))
    cfg.append(make_dict(m, None, "monitor", "pippim.com"))
    return cfg


def make_x11_cfg():
    """ Configuration for: 'import x11' """
    cfg = list()  # Return list of dictionaries
    m = "x11"  # Module name to python interpreter
    cfg.append(make_dict(m, None, "time"))
    cfg.append(make_dict(m, "namedtuple", "collections"))
    # noinspection SpellCheckingInspection
    '''
        Needs revamping:
            # /usr/lib/python2.7/dist-packages/Xlib/X.py
            import Xlib.X
            # /usr/lib/python2.7/dist-packages/Xlib/__init__.py
            import Xlib
            # /usr/lib/python2.7/dist-packages/Xlib/display.py
            import Xlib.display
            # /usr/lib/python2.7/dist-packages/Xlib/ext/randr.py
            from Xlib.ext import randr

    '''
    # /usr/lib/python2.7/dist-packages/Xlib/X.py
    cfg.append(make_dict(m, None, "Xlib/X",
                         "https://github.com/python-xlib/python-xlib"))
    cfg.append(make_dict(m, None, "Xlib/__init__",
                         "https://github.com/python-xlib/python-xlib"))
    cfg.append(make_dict(m, None, "Xlib/display",
                         "https://github.com/python-xlib/python-xlib"))
    # noinspection SpellCheckingInspection
    cfg.append(make_dict(m, "randr", "Xlib.ext",
                         "https://github.com/python-xlib/python-xlib"))
    # /usr/lib/python2.7/dist-packages/Xlib/ext/r and r.py
    return cfg


def make_web_cfg():
    """ Configuration for: 'popen(webscrape.py...)' """
    cfg = list()  # Return list of dictionaries
    m = "webscrape"  # Module name to python interpreter
    cfg.extend(make_tk_cfg(m))
    cfg.append(make_dict(m, None, "sys"))
    cfg.append(make_dict(m, None, "os"))
    cfg.append(make_dict(m, None, "json"))
    cfg.append(make_dict(m, None, "time"))
    cfg.append(make_dict(m, None, "re"))
    cfg.append(make_dict(m, None, "time"))
    cfg.append(make_dict(m, "namedtuple", "collections"))
    # Dist-packages
    d1 = "https://requests.readthedocs.io/en/latest/"
    d2 = "https://six.readthedocs.io/"
    d3 = "https://www.crummy.com/software/BeautifulSoup/bs4/doc/"
    cfg.append(make_dict(m, None, "requests", d1, "3", "python3-requests"))
    cfg.append(make_dict(m, None, "requests", d1, "2", "python-requests"))
    cfg.append(make_dict(m, None, "six.moves.urllib", d2, "3", "python3-six"))
    cfg.append(make_dict(m, None, "six.moves.urllib", d2, "2", "python-six"))
    cfg.append(make_dict(m, None, "bs4.BeautifulSoup", d3, "3", "python3-bs4"))
    cfg.append(make_dict(m, None, "bs4.BeautifulSoup", d3, "3", "python-bs4"))
    # Pippim modules
    cfg.append(make_dict(m, "g", "global_variables", "pippim.com"))
    cfg.append(make_dict(m, "ext", "external", "pippim.com"))
    cfg.append(make_dict(m, None, "monitor", "pippim.com"))
    cfg.append(make_dict(m, None, "sql", "pippim.com"))
    cfg.append(make_dict(m, None, "toolkit", "pippim.com"))
    cfg.append(make_dict(m, None, "message", "pippim.com"))
    return cfg


def make_encoding_cfg():
    """ Configuration for: 'import encoding' """
    cfg = list()  # Return list of dictionaries
    m = "encoding"  # Module name to python interpreter
    # subprocess
    d = "https://github.com/TkinterEP/ttkwidgets"
    cfg.extend(make_tk_cfg(m))
    cfg.extend(make_PIL_cfg(m))
    cfg.append(make_dict(m, "CheckboxTreeview", "ttkwidgets", d, None,
                         "python-ttkwidgets"))
    cfg.append(make_dict(m, None, "subprocess32", required=False))

    # Python Standard Library
    cfg.append(make_dict(m, None, "sys"))
    cfg.append(make_dict(m, None, "os"))
    cfg.append(make_dict(m, None, "io"))
    cfg.append(make_dict(m, None, "re"))
    cfg.append(make_dict(m, None, "time"))
    cfg.append(make_dict(m, None, "datetime"))
    cfg.append(make_dict(m, None, "pickle"))
    cfg.append(make_dict(m, None, "pprint"))
    # Dist-packages
    d1 = "https://pypi.org/project/python-magic/"
    d2 = "https://pypi.org/project/musicbrainzngs/"
    d3 = "https://github.com/sebastinas/python-libdiscid"
    d4 = "https://mutagen.readthedocs.io/en/latest/"
    cfg.append(make_dict(m, None, "magic", d1, "3", "python3-magic"))
    cfg.append(make_dict(m, None, "magic", d1, "2", "python-magic"))
    cfg.append(make_dict(m, "mbz", "musicbrainzngs", d2, "3", "python3-musicbrainzngs"))
    cfg.append(make_dict(m, "mbz", "musicbrainzngs", d2, "2", "python-musicbrainzngs"))
    cfg.append(make_dict(m, "discid", "libdiscid", d3, "3", "python3-libdiscid"))
    cfg.append(make_dict(m, "discid", "libdiscid", d3, "2", "python-libdiscid"))
    cfg.append(make_dict(m, None, "mutagen", d4, "3", "python3-mutagen"))
    cfg.append(make_dict(m, None, "mutagen", d4, "2", "python-mutagen"))
    # noinspection SpellCheckingInspection
    ''' TODO:
            Buried in functions:
            https://mutagen-specs.readthedocs.io/en/latest/id3/id3v2.3.0.html
                from mutagen.flac import FLAC as audio_file
                from mutagen.oggvorbis import OggVorbis as audio_file
                
                from mutagen.oggvorbis import OggVorbis
                from mutagen.flac import Picture
    '''
    # Pippim modules
    cfg.append(make_dict(m, "g", "global_variables", "pippim.com"))
    cfg.append(make_dict(m, "lc", "location", "pippim.com"))
    cfg.append(make_dict(m, "ext", "external", "pippim.com"))
    cfg.append(make_dict(m, None, "toolkit", "pippim.com"))
    cfg.append(make_dict(m, None, "monitor", "pippim.com"))
    cfg.append(make_dict(m, None, "message", "pippim.com"))
    cfg.append(make_dict(m, "img", "image", "pippim.com"))
    cfg.append(make_dict(m, "tmf", "timefmt", "pippim.com"))
    cfg.append(make_dict(m, None, "sql", "pippim.com"))
    cfg.append(make_dict(m, None, "disc_get", "pippim.com"))
    cfg.append(make_dict(m, None, "mbz_get1", "pippim.com"))
    cfg.append(make_dict(m, None, "mbz_get2", "pippim.com"))
    # gst-launch-1.0 external command needed
    return cfg


def make_disc_cfg():
    """ Configuration for: background job 'disc_get.py """
    cfg = list()  # Return list of dictionaries
    m = "disc_get"  # Module name to python interpreter
    cfg.append(make_dict(m, None, "sys"))
    cfg.append(make_dict(m, None, "pickle"))
    d3 = "https://github.com/sebastinas/python-libdiscid"
    cfg.append(make_dict(m, "discid", "libdiscid", d3, "3", "python3-libdiscid"))
    cfg.append(make_dict(m, "discid", "libdiscid", d3, "2", "python-libdiscid"))
    return cfg


def make_mbz1_cfg():
    """ Configuration for: background job 'mbz_get1.py """
    cfg = list()  # Return list of dictionaries
    m = "mbz_get1"  # Module name to python interpreter

    # Python Standard Library
    cfg.append(make_dict(m, None, "subprocess32", required=False))
    cfg.append(make_dict(m, None, "sys"))
    cfg.append(make_dict(m, None, "os"))
    cfg.append(make_dict(m, None, "re"))
    cfg.append(make_dict(m, None, "json"))
    cfg.append(make_dict(m, None, "pickle"))
    cfg.append(make_dict(m, None, "time"))
    cfg.append(make_dict(m, None, "datetime"))
    cfg.append(make_dict(m, None, "pprint"))
    # Dist-packages
    cfg.extend(make_PIL_cfg(m))
    d2 = "https://pypi.org/project/musicbrainzngs/"
    d3 = "https://github.com/sebastinas/python-libdiscid"
    cfg.append(make_dict(m, "mbz", "musicbrainzngs", d2, "3", "python3-musicbrainzngs"))
    cfg.append(make_dict(m, "mbz", "musicbrainzngs", d2, "2", "python-musicbrainzngs"))
    cfg.append(make_dict(m, "discid", "libdiscid", d3, "3", "python3-libdiscid"))
    cfg.append(make_dict(m, "discid", "libdiscid", d3, "2", "python-libdiscid"))
    # Pippim modules
    cfg.append(make_dict(m, None, "message", "pippim.com"))
    cfg.append(make_dict(m, "img", "image", "pippim.com"))
    cfg.append(make_dict(m, "g", "global_variables", "pippim.com"))
    ''' Buried import # 1  Isn't used !!!
            import json
            from getpass import getpass
            
            import musicbrainzngs as mb
            import libdiscid
            import requests
    '''

    ''' Buried import # 2  Isn't used !!!
            import os, sys
            import subprocess
            from argparse import ArgumentParser
            import libdiscid
            import musicbrainzngs as mb
            import requests
            import json
            from getpass import getpass
    '''
    return cfg


def make_mbz2_cfg():
    """ Configuration for: background job 'mbz_get2.py """
    cfg = list()  # Return list of dictionaries
    m = "mbz_get2"  # Module name to python interpreter
    # Python Standard Library
    cfg.append(make_dict(m, None, "sys"))
    cfg.append(make_dict(m, None, "os"))
    cfg.append(make_dict(m, None, "re"))
    cfg.append(make_dict(m, None, "time"))
    cfg.append(make_dict(m, None, "datetime"))
    cfg.append(make_dict(m, None, "json"))
    cfg.append(make_dict(m, None, "pickle"))
    # Dist-packages
    cfg.extend(make_PIL_cfg(m))
    d1 = "https://requests.readthedocs.io/en/latest/"
    d2 = "https://pypi.org/project/musicbrainzngs/"
    cfg.append(make_dict(m, None, "requests", d1, "3", "python3-requests"))
    cfg.append(make_dict(m, None, "requests", d1, "2", "python-requests"))
    cfg.append(make_dict(m, "mbz", "musicbrainzngs", d2, "3", "python3-musicbrainzngs"))
    cfg.append(make_dict(m, "mbz", "musicbrainzngs", d2, "2", "python-musicbrainzngs"))
    # Pippim modules
    cfg.append(make_dict(m, "g", "global_variables", "pippim.com"))
    return cfg


def make_tk_cfg(m):
    """ Common tkinter configuration extended on caller's list. """
    tk = list()  # Return list of dictionaries
    d = "https://github.com/tcltk/tk"
    tk.append(make_dict(m, "tk", "tkinter", d, "3", "python3-tk"))
    tk.append(make_dict(m, "tk", "Tkinter", d, "2", "python-tk"))
    tk.append(make_dict(m, "ttk", "tkinter.ttk", d, "3", "python3-tk"))
    tk.append(make_dict(m, None, "ttk", d, "2", "python-tk"))
    tk.append(make_dict(m, "font", "tkinter.font", d, "3", "python3-tk"))
    tk.append(make_dict(m, "font", "tkFont", d, "2", "python-tk"))
    tk.append(make_dict(m, "filedialog", "tkinter.filedialog", d, "3", "python3-tk"))
    tk.append(make_dict(m, "filedialog", "tkFileDialog", d, "2", "python-tk"))
    tk.append(make_dict(m, "messagebox", "tkinter.messagebox", d, "3", "python3-tk"))
    tk.append(make_dict(m, "messagebox", "tkMessageBox", d, "2", "python-tk"))
    tk.append(make_dict(m, "simpledialog", "tkinter.simpledialog", d, "3", "python3-tk"))
    tk.append(make_dict(m, "simpledialog", "tkSimpleDialog", d, "2", "python-tk"))
    tk.append(make_dict(m, "scrolledtext", "tkinter.scrolledtext", d, "3", "python3-tk"))
    tk.append(make_dict(m, "scrolledtext", "ScrolledText", d, "2", "python-tk"))
    return tk


def make_PIL_cfg(m):
    """ Common PIL (aka Pillow) configuration extended on caller's list.
        # Optional: python-pil-dbg and python-pil.imagetk-dbg
        #       The debug packages are installed in development but not sure why.
    """
    pil = list()  # Return list of dictionaries
    d = "https://pypi.org/project/Pillow/"
    pil.append(make_dict(m, "Image", "PIL", d, "3", "python3-pil"))
    pil.append(make_dict(m, "Image", "PIL", d, "2", "python-pil"))
    pil.append(make_dict(m, "ImageTk", "PIL", d, "3", "python3-pil.imagetk"))
    pil.append(make_dict(m, "ImageTk", "PIL", d, "2", "python-pil.imagetk"))
    pil.append(make_dict(m, "ImageDraw", "PIL", d, "3", "python3-pil"))
    pil.append(make_dict(m, "ImageDraw", "PIL", d, "2", "python-pil"))
    pil.append(make_dict(m, "ImageFont", "PIL", d, "3", "python3-pil"))
    pil.append(make_dict(m, "ImageFont", "PIL", d, "2", "python-pil"))
    pil.append(make_dict(m, "ImageFilter", "PIL", d, "3", "python3-pil"))
    pil.append(make_dict(m, "ImageFilter", "PIL", d, "2", "python-pil"))
    pil.append(make_dict(m, "ImageOps", "PIL", d, "3", "python3-pil"))
    pil.append(make_dict(m, "ImageOps", "PIL", d, "2", "python-pil"))
    return pil


def make_dict(module, imp_as, imp_from, developer="python", version=None,
              ubuntu=None, required=True):
    """ Make configuration dictionary to be appended to configuration list """
    cfg_dict = \
        {"module": module,
         "imp_as": imp_as,
         "imp_from": imp_from,
         "developer": developer,
         "version": version,
         "ubuntu": ubuntu,
         "required": required}
    return cfg_dict


def whats_installed():
    """
    Walk through sys.path to find all .py and .pyc modules record size & dates.
    :return inst_list:
    """
    pass

    # noinspection SpellCheckingInspection
    '''
    
    Python Standard Library modules are found in:
        /usr/lib/python2.7
        /usr/lib/python3.5 
 
    Pippim modules can be in any directory be it system, program path or user dir.

    3rd party modules are found in:

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
drwxr-xr-x   2 root root   4096 Nov 22  2020 Babel-1.3.egg-info/  # next line middle-truncated to make pycharm happy
lrwxrwxrwx   1 root root     52 Jun 17  2012 BeautifulSoup-3.2.1.egg-info -> ../../../share/pyshared/Beau-3.2.1.egg-info
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
        
Hand-holding user through the 'apt install' process is tedious.

Simply verify package or module is installed and don't teach how to do it.
        
            $ gst-launch-1.0 --gst-version
            GStreamer Core Library version 1.8.3

            $ apt list | grep python-tk
            python-tk/xenial-updates,now 2.7.12-1~16.04 amd64 [installed]
            python-tkcalendar/xenial,xenial,now 1.5.0-1 all [installed]

            $ wc mserve.py
             10826  46134 492518 mserve.py

TO GET installed packages
$ time apt list | grep "[installed" > apt_list_installed.txt
real	0m1.454s
user	0m1.395s
sys	    0m0.095s

$ ll *.txt
-rw-rw-r-- 1 rick rick 3377347 May 18 15:18 apt_list_full.txt
-rw-rw-r-- 1 rick rick  185301 May 18 15:19 apt_list_installed.txt

$ head apt_list_installed.txt
a11y-profile-manager-indicator/xenial,now 0.1.10-0ubuntu3 amd64 [installed]
abi word/xenial-updates,now 3.0.1-6ubuntu0.16.04.1 amd64 [installed]
abi word-common/xenial-updates,xenial-updates,now 3.0.1-6ubuntu0.16.04.1 all [installed,automatic]
abi word-plugin-grammar/xenial-updates,now 3.0.1-6ubuntu0.16.04.1 amd64 [installed,automatic]
account-plugin-facebook/xenial,xenial,now 0.12+16.04.20160126-0ubuntu1 all [installed]
account-plugin-flickr/xenial,xenial,now 0.12+16.04.20160126-0ubuntu1 all [installed]
account-plugin-google/xenial,xenial,now 0.12+16.04.20160126-0ubuntu1 all [installed]
accounts service/xenial-updates,xenial-security,now 0.6.40-2ubuntu11.6 amd64 [installed]
acl/xenial,now 2.2.52-3 amd64 [installed]
acpi/xenial,now 1.7-1 amd64 [installed]

        """
        pass


def verify_chain():
    """ Verify that program is called by 'mserve.py' """
    ''' If not called by 'mserve.py' do nothing '''
    try:
        filename = inspect.stack()[1][1]  # If there is a parent it is 'm'
        #grand_file = inspect.stack()[1][1]  # If there is a parent it is 'm'
        # (<frame object>, './m', 50, '<module>', ['import mserve\n'], 0)
        parent = os.path.basename(filename)
        if parent != "mserve.py":
            print("sql.py must be called by 'mserve.py' but is called by:",
                  parent)
            exit()
    except IndexError:  # list index out of range
        ''' Called from the command line '''
        print("sql.py cannot be called from command line. Aborting...")
        exit()



if __name__ == "__main__":
    main(caller=None)

# End of mserve_configy.py
