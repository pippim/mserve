#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
#
#       mserve_config.py - Check dependencies
#
#       July 10 2023 - Initial version
#
# ==============================================================================

from __future__ import print_function       # Must be first import

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

before = [str(m) for m in sys.modules]
import os               # USER_ID = str(os.get uid())

try:
    import inspect
    INSPECT_INSTALLED = True
except ImportError:     # No module named inspect
    print("No module named inspect")
    INSPECT_INSTALLED = False


def init():
    """
    Delete .pyc from directory /ttkwidgets:

$ ll *.pyc
-rw-r--r-- 1 rick rick  6997 Oct 24  2020 autohidescrollbar.pyc
-rw-r--r-- 1 rick rick  9586 Oct 24  2020 calendarwidget.pyc
-rw-r--r-- 1 rick rick 10638 Oct 24  2020 checkboxtreeview.pyc
-rw-r--r-- 1 rick rick  4511 Oct 24  2020 debugwindow.pyc
-rw-r--r-- 1 rick rick   928 Oct 24  2020 __init__.pyc
-rw-r--r-- 1 rick rick 11708 Oct 24  2020 itemscanvas.pyc
-rw-r--r-- 1 rick rick  5186 Oct 24  2020 linklabel.pyc
-rw-r--r-- 1 rick rick 10922 Oct 24  2020 scaleentry.pyc
-rw-r--r-- 1 rick rick  2859 Oct 24  2020 scrolledlistbox.pyc
-rw-r--r-- 1 rick rick 23270 Oct 24  2020 table.pyc
-rw-r--r-- 1 rick rick 22410 Oct 24  2020 tickscale.pyc
-rw-r--r-- 1 rick rick 53268 Oct 24  2020 timeline.pyc
-rw-r--r-- 1 rick rick   794 Oct 24  2020 utilities.pyc

After deleting on July 10, 2023 you will see:

$ ll *.pyc
-rw-r--r-- 1 rick rick  6877 Jul 10 10:16 autohidescrollbar.pyc
-rw-r--r-- 1 rick rick  9316 Jul 10 10:16 calendarwidget.pyc
-rw-r--r-- 1 rick rick 10347 Jul 10 10:16 checkboxtreeview.pyc
-rw-r--r-- 1 rick rick  4376 Jul 10 10:16 debugwindow.pyc
-rw-r--r-- 1 rick rick   913 Jul 10 10:16 __init__.pyc
-rw-r--r-- 1 rick rick 11442 Jul 10 10:16 itemscanvas.pyc
-rw-r--r-- 1 rick rick  5006 Jul 10 10:16 linklabel.pyc
-rw-r--r-- 1 rick rick 10622 Jul 10 10:16 scaleentry.pyc
-rw-r--r-- 1 rick rick  2784 Jul 10 10:16 scrolledlistbox.pyc
-rw-r--r-- 1 rick rick 22736 Jul 10 10:16 table.pyc
-rw-r--r-- 1 rick rick 22050 Jul 10 10:16 tickscale.pyc
-rw-r--r-- 1 rick rick 52233 Jul 10 10:16 timeline.pyc
-rw-r--r-- 1 rick rick   749 Jul 10 10:16 utilities.pyc


    """

    if INSPECT_INSTALLED:
        ''' from: https://www.tutorialspoint.com/
        How-to-find-which-Python-modules-are-being-imported-from-a-package '''
        modules = inspect.getmembers(os)
        results = filter(lambda m: inspect.ismodule(m[1]), modules)

        print('\nThe list of imported Python modules reported by inspect are :')
        for o in results:
            print(o)
        print()

        print('\nThe list of imported Python modules reported by sys.modules :')
        print(sys.modules.keys())
        print()

        module = dir()
        print('The list of imported Python modules reported by dir() :', module)

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
        print('The list of imported Python modules reported by types.ModuleType :')
        for name, val in globals().items():
            if isinstance(val, types.ModuleType):
                #yield val.__name__
                print('import %s as %s' % (val.__name__, name))
    except ImportError:  # No module named types
        print("types cannot be imported")

    ''' from: https://stackoverflow.com/a/40381601/6929343 '''
    print("\n From: https://stackoverflow.com/a/40381601/6929343 :")
    after = [str(m) for m in sys.modules]
    print([m for m in after if m not in before])

    print("\nsys.path:", sys.path)
    
# End of global_variables.py
