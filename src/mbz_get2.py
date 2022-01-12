# -*- coding: utf-8 -*-

#       mbz_get2.py - Standalone python program to run in background.
#                     Get Musicbrainz disc information - Pass 2 of 2.

#       Called with: 'python mbz_get2.py <release-list>'
#       Parameters:  Pickle file contains object disc of libdiscid type
#       Returns:     Dictionary of images

from __future__ import with_statement       # Error handling for file opens

import re
import time
import datetime
from PIL import Image, ImageTk, ImageDraw, ImageFont
import musicbrainzngs as mbz
import requests
import json
import pickle
import sys
import os

# Homegrown
import location as lc

# IPC pickle filename shouldn't end with .pkl because it's used for playlists.
IPC_PICKLE_FNAME = lc.MSERVE_DIR + "ipc.pickle"
# THESE TWO ARE IDENTICAL FILENAMES
DICT_FNAME = sys.argv[1]            # Pickle filename to save to
RESOLUTION = sys.argv[2]            # Image resolution to select (IGNORED)


def get_image_info(toplevel=None):

    # Our last program has just finished. Get dictionary results
    with open(IPC_PICKLE_FNAME, 'rb') as f:
        # read the data as binary data stream
        release_list = pickle.load(f)

#   PRODUCTION VERSION will use this instead:
#    mbz.set_useragent("mserve", "0.1")
#    mbz.auth(u=input('Musicbrainz username: '), p=getpass())

    image_dict = {}

    for d in release_list:

        if not type(d) is dict:
            return {'error': '7', 'data': d}    # Not a dictionary

        rel_id = d['id']        # release_list, release entry, release Id
        url = 'http://coverartarchive.org/release/' + rel_id

        try:
            art = json.loads(requests.get(url, allow_redirects=True).content)
        except Exception as x:
            # Some images simply don't exist and there really is a connection.
            # return { 'error': '99' }    # No internet connection
            continue

        ''' FROM encoding.py: self.cd_tree_insert(relId, mbzId...): '''
        # Download images to build image list dictionary entry
        for i, image in enumerate(art['images']):

            if 'thumbnails' in image:
                if 'small' in image['thumbnails']:
                    art['images'][i]['thumbnails']['small-data'] = \
                            download_art(image['thumbnails']['small'], d)

                if 'large' in image['thumbnails']:
                    art['images'][i]['thumbnails']['large-data'] = \
                            download_art(image['thumbnails']['large'], d)
            if 'image' in image:
                art['images'][i]['image-data'] = \
                        download_art(image['image'], d)

        image_dict[rel_id] = art

    return image_dict


''' ======================    PSEUDO-PRETTY PRINT   =======================
{u'release': 
        u'https://musicbrainz.org/release/3749c6d5-030f-43f8-a4af-054fc8cc3446', 
 u'images': [{
        u'comment': u'From Jim Steinman web site', 
        u'thumbnails':{
            u'large': u'http://coverartarchive.org/release/3749c6d5-030f-43f8-a4af-054fc8cc3446/12044925472-500.jpg', 
            u'small': u'http://coverartarchive.org/release/3749c6d5-030f-43f8-a4af-054fc8cc3446/12044925472-250.jpg'
                      }, 
        u'edit': 36027155, 
        u'image': u'http://coverartarchive.org/release/3749c6d5-030f-43f8-a4af-054fc8cc3446/12044925472.jpg', 
        u'back': False, 
        u'id': u'12044925472', 
        u'front': True, 
        u'approved': True, 
        u'types': [u'Front']
             }, 
             {
        u'comment': u'', 
        u'thumbnails': {
            u'large': u'http://coverartarchive.org/release/3749c6d5-030f-43f8-a4af-054fc8cc3446/14217519641-500.jpg', 
            u'small': u'http://coverartarchive.org/release/3749c6d5-030f-43f8-a4af-054fc8cc3446/14217519641-250.jpg'
                       }, 
        u'edit': 39967251, 
        u'image': u'http://coverartarchive.org/release/3749c6d5-030f-43f8-a4af-054fc8cc3446/14217519641.png', 
        u'back': False, 
        u'id': u'14217519641', 
        u'front': False, 
        u'approved': True, 
        u'types': [u'Medium']
             }
            ]
}

May 8, 2021 ERROR above and below:


Traceback (most recent call last):
  File "mbz_get2.py", line 129, in <module>
    pass_back = get_image_info()
  File "mbz_get2.py", line 68, in get_image_info
    download_art(image['thumbnails']['small'], d)
  File "mbz_get2.py", line 119, in download_art
    if int(d['ext:score']) == 100:
KeyError: 'ext:score'
Exception in Tkinter callback
Traceback (most recent call last):
  File "/usr/lib/python2.7/lib-tk/Tkinter.py", line 1540, in __call__
    return self.func(*args)
  File "/usr/lib/python2.7/lib-tk/Tkinter.py", line 590, in callit
    func(*args)
  File "/home/rick/python/encoding.py", line 605, in cd_run_to_close
    if self.image_dict.get('error'):
AttributeError: 'list' object has no attribute 'get'
'''


def download_art(name, d):
    # TODO on except create dummy "Download Error" image to pass back
    #      Match on image resolution 250, 500, original (small, large, image)

    # Filter has no matching score
    if d.get('ext:score'):
        match_score = int(d['ext:score'])
    else:
        match_score = 100

    if match_score == 100:
        # We only want to get images if dictionary has 100% score
        return requests.get(name, allow_redirects=True).content
    else:
        # Reduce pickle size from 155.2 MB to 4.4 MB
        # Button in CD treeview allows them to manually download this
        return "Not 100% Score"


if __name__ == "__main__":

    pass_back = get_image_info()

    with open(DICT_FNAME, "wb") as f:
        # store the data as binary data stream
        pickle.dump(pass_back, f)           # Save dictionary as pickle file

# End of mbz_get2.py
