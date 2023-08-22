#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: Pippim
License: GNU GPLv3
Source: This repository
Description: mserve - Music Server - Get musicbrainzngs artwork
"""

from __future__ import print_function  # Must be first import
from __future__ import with_statement  # Error handling for file opens

# ==============================================================================
#
#       mbz_get2.py - Standalone python program to run in background.
#                     Get Musicbrainz disc information - Pass 2 of 2.
#
#       Called with: 'python mbz_get2.py <release-list>'
#       Parameters:  Pickle file contains MusicBrainz release list
#       Returns:     Dictionary of images
#
#       July 12 2023 - Interface to/from mserve_config.py
#       Aug. 21 2023 - Don't download images > 4 MB
#
# ==============================================================================

# Python Standard Library
import sys
import os
import re
import time
import datetime
import json
import pickle

# Dist-packages
from PIL import Image, ImageTk, ImageDraw, ImageFont
# Reference: https://buildmedia.readthedocs.org/media/pdf/
# python-musicbrainz-ngs-jonnyjd/latest/python-musicbrainz-ngs-jonnyjd.pdf
import musicbrainzngs as mbz
import requests

import global_variables as g
if g.USER is None:
    g.init()

''' File with dictionaries in pickle format passed between background jobs '''
DICT_FNAME = sys.argv[1]  # Pickle filename with release list
RESOLUTION = sys.argv[2]  # Image resolution to select (IGNORED)


def get_image_info():
    """ Get Images using Release list passed in Pickle file parameter 1 """
    with open(DICT_FNAME, 'rb') as rel_info:
        # read the data as binary data stream
        release_list = pickle.load(rel_info)

    image_dict = {}

    for d in release_list:

        if not type(d) is dict:
            return {'error': '7', 'data': d}  # Not a dictionary

        rel_id = d['id']  # release_list, release entry, release Id
        url = 'http://coverartarchive.org/release/' + rel_id

        try:
            art = json.loads(requests.get(url, allow_redirects=True).content)
        except Exception as x:
            print("Exception:", x)
            # Some images simply don't exist and there really is a connection.
            # return { 'error': '99' }    # No internet connection
            continue

        print("mbz_get2.py art:", "\n", art)

        ''' FROM encoding.py: self.cd_tree_insert(relId, mbzId...): '''
        # Download images to build image list dictionary entry
        for i, image in enumerate(art['images']):

            print("mbz_get2.py image i:", i, "\n",
                  image)

            if 'thumbnails' in image:
                if 'small' in image['thumbnails']:
                    if verify_download(image['thumbnails']['small'], d):
                        art['images'][i]['thumbnails']['small-data'] = \
                                download_art(image['thumbnails']['small'])

                if 'large' in image['thumbnails']:
                    if verify_download(image['thumbnails']['large'], d):
                        art['images'][i]['thumbnails']['large-data'] = \
                                download_art(image['thumbnails']['large'])
            if 'image' in image:
                if verify_download(image['image'], d):
                    art['images'][i]['image-data'] = \
                        download_art(image['image'])

        image_dict[rel_id] = art

    return image_dict


def verify_download(name, d):
    """ Download single art file if less than 4 MB & 100% 'ext:score' match """

    # Filter has no matching score
    if d.get('ext:score'):
        match_score = int(d['ext:score'])
    else:
        match_score = 100

    ''' Get file size before downloading '''
    response = requests.head(name, allow_redirects=True)
    size = response.headers.get('content-length', -1)
    if size and int(size) > 4000000:
        print("Image is over 4 MB.  Skipping.", size)
        return False

    if match_score != 100:
        # Reduce pickle size from 155.2 MB to 4.4 MB
        # Button in CD treeview allows them to manually download this
        print("Not 100% Score.  Skipping.")
        return False

    return True


def download_art(name):
    """ Download single art file if less than 4 MB """
    return requests.get(name, allow_redirects=True).content


if __name__ == "__main__":

    pass_back = get_image_info()

    with open(DICT_FNAME, "wb") as f:
        # store the data as binary data stream
        pickle.dump(pass_back, f)           # Save dictionary as pickle file

# End of mbz_get2.py
