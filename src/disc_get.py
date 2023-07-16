#!/usr/bin/env python
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
#
# ==============================================================================
import libdiscid
import sys                                  # System argument for save filename
import pickle                               # Save discid dictionary to file
import libdiscid as discid                  # C program to read CD's TOC

DICT_FNAME = sys.argv[1]                    # Pickle filename to save to
# noinspection SpellCheckingInspection
"""

From: https://buildmedia.readthedocs.org/media/pdf/python-discid/v1.1.0/python-discid.pdf

1.2.4 Fetching Metadata
=======================

You can use python-musicbrainz-ngs to fetch metadata for your disc.
The relevant function is musicbrainzngs.get_releases_by_discid():

import discid
import musicbrainzngs

musicbrainzngs.set_useragent("python-discid-example", "0.1", "your@mail")

disc = discid.read()
try:
    result = musicbrainzngs.get_releases_by_discid(disc.id,
    includes=["artists"])
except musicbrainzngs.ResponseError:
    print("disc not found or bad response")
else:
    if result.get("disc"):
        print("artist:\t%s" %
            result["disc"]["release-list"][0]["artist-credit-phrase"])

    elif result.get("cdstub"):
        print("artist:\t" % result["cdstub"]["artist"])
        print("title:\t" % result["cdstub"]["title"])
        
You can fetch much more data. See musicbrainzngs for detail
"""


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
