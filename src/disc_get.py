# -*- coding: utf-8 -*-

#       disc_get.py - Poor man's multiprocessing for python.
#                     Use shell to run program in background
#       Documentation https://pythonhosted.org/python-libdiscid/api.html

from __future__ import with_statement       # Error handling for file opens

import libdiscid as discid                  # C program to read CD's TOC
import pickle                               # Save discid dictionary to file
import sys                                  # System argument for save filename

DICT_FNAME = sys.argv[1]                    # Pickle filename to save to
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
    except:
        # TODO: Expand error with no cd drive, no cd in drive, cd read error
        #       NOT POSSIBLE: https://pythonhosted.org/python-libdiscid/api.html
        #print('No CD found')
        return {'error': '1'}

    return disc

if __name__ == "__main__":

    pass_back = get_discid()
    with open(DICT_FNAME, "wb") as f:
        # store the data as binary data stream
        pickle.dump(pass_back, f)           # Save dictionary as pickle file
