#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Pippim
License: GNU GPLv3
Source: This repository
Description: mserve - Music Server - Get discid of CD
"""

from __future__ import print_function  # Must be first import
from __future__ import with_statement  # Error handling for file opens

# ==============================================================================
#
#       disc_get.py - Poor man's multiprocessing for python.
#                     Use shell to run program in background
#       Documentation https://pythonhosted.org/python-libdiscid/api.html
#
#       July 12 2023 - Interface to/from mserve_config.py
#       June 01 2025 - Remove "env" from shebang to for script name in top
#
# ==============================================================================
import libdiscid
import sys                                  # System argument for save filename
import pickle                               # Save discid dictionary to file
import libdiscid as discid                  # C program to read CD's TOC

DICT_FNAME = sys.argv[1]                    # Pickle filename to save to


def get_discid():
    """ Use discid to get CD information"""
    try:
        disc = discid.read()                # use default device
    except libdiscid.DiscError:
        # NOT POSSIBLE to expand error with no drive, no cd, cd read error
        #       https://pythonhosted.org/python-libdiscid/api.html
        return {'error': '1'}

    return disc


if __name__ == "__main__":

    pass_back = get_discid()
    with open(DICT_FNAME, "wb") as f:
        # store the data as binary data stream
        pickle.dump(pass_back, f)           # Save dictionary as pickle file
