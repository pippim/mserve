#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: Pippim
License: GNU GPLv3
Source: This repository
Description: mserve - Music Server - Get musicbrainzngs 'release-list'
"""

from __future__ import print_function  # Must be first import
from __future__ import with_statement  # Error handling for file opens

# ==============================================================================
#
#       mbz_get1.py - Standalone python program to run in background.
#                     Get Musicbrainz disc information - Pass 1 of 2.
#
#       Called with: 'python mbz_get1.py <Musicbrainz id>'
#       Parameters:  Pickle file contains object disc of libdiscid type
#       Returns:     Dictionary of Musicbrainz 'release-list' entries
#
#       July 12 2023 - Interface to/from mserve_config.py
#       July 14 2023 - Save original mbz dictionary in JSON format
#       July 17 2023 - Get MBZ FirstDate from all releases.
#       Aug. 21 2023 - Major Scrub and support Composer ['work-relation-list']
#
# ==============================================================================


# Python Standard Library
try:
    import subprocess32 as sp
    SUBPROCESS_VER = '32'
except ImportError:  # No module named subprocess32
    import subprocess as sp
    SUBPROCESS_VER = 'native'
import sys
import os
import re
import json
import pickle
import time
import datetime

# Dist-packages
from PIL import Image, ImageTk, ImageDraw, ImageFont
import musicbrainzngs as mbz
import libdiscid as discid

# Pippim modules
import message
import image as img

import global_variables as g        # should be self-explanatory
if g.USER is None:
    g.init()  # Background job so always runs

TMP_MBZ_GET1A = g.TEMP_DIR + "mserve_mbz_get1_releases_json"
TMP_MBZ_GET1B = g.TEMP_DIR + "mserve_mbz_get1_recordings_json"
TMP_MBZ_GET1C = g.TEMP_DIR + "mserve_mbz_get1_release_by_id_results_json"
TMP_MBZ_GET1D = g.TEMP_DIR + "mserve_mbz_get1_releases_with_work_json"
TMP_MBZ_GET1E = g.TEMP_DIR + "mserve_mbz_get1_releases_with_dates_json"
TMP_MBZ_GET1F = g.TEMP_DIR + "mserve_mbz_get1_release_by_id_error_json"
TMP_MBZ_DEBUG = g.TEMP_DIR + "mserve_mbz_get1_dates_list"
if os.path.isfile(TMP_MBZ_GET1A):
    os.remove(TMP_MBZ_GET1A)
if os.path.isfile(TMP_MBZ_GET1B):
    os.remove(TMP_MBZ_GET1B)
if os.path.isfile(TMP_MBZ_GET1C):
    os.remove(TMP_MBZ_GET1C)
if os.path.isfile(TMP_MBZ_GET1D):
    os.remove(TMP_MBZ_GET1D)
if os.path.isfile(TMP_MBZ_GET1E):
    os.remove(TMP_MBZ_GET1E)
if os.path.isfile(TMP_MBZ_GET1F):
    os.remove(TMP_MBZ_GET1F)
if os.path.isfile(TMP_MBZ_DEBUG):
    os.remove(TMP_MBZ_DEBUG)

# Preferred method to view Debug files gedit  "Format JSON" plugin
# See website: https://connorgarvey.com/blog/?p=264

# $ cd /run/user/1000
# $ cat mserve_mbz_get1_release_by_id_results_json | python -m json.tool | less

DICT_FNAME = sys.argv[1]            # IPC pickle filename read from/saved to
SEARCH_LIMIT = sys.argv[2]          # Number of search results to return when
                                    # less than 3 only CD's searched. When more
                                    # then vinyl (which may have artwork!) are
                                    # included. EG Jim Steinem Bad for Good
EMAIL_ADDRESS = sys.argv[3]         # May 5, 2023 - Not tested yet


def get_releases_then_work_rels():
    """ All encompassing function to get release lists with one read.
        Many more functions were written for situations where information
        had to be spliced together from multiple reads.

        Note there is an 8 character 'disc.freedb_id' as well from CDDB
    """
    with open(DICT_FNAME, 'rb') as disc_info:
        # read the data as binary data stream
        disc = pickle.load(disc_info)

    # Valid Musicbrainz ID?
    if len(disc.id) != 28:
        return {'error': '1'}


    # Tell musicbrainz what your app is, and how to contact you
    # (this step is required, as per the webservice access rules
    # at http://wiki.musicbrainz.org/XML_Web_Service/Rate_Limiting )
    try:
        mbz.set_useragent("mserve", g.MSERVE_VERSION, EMAIL_ADDRESS)
    except mbz.NetworkError:
        print("mbz.NetworkError")
        return {'error': '99'}
    except Exception as err:
        print("Exception:", err)
        return {'error': '2'}

    try:
        # Check command is reported in error message correctly
        releases_by_discid = mbz.get_releases_by_discid(
            disc.id, includes=['release-groups', 'artist-credits', 'recordings'])

        # https://github.com/alastair/python-musicbrainzngs/issues/202
        # includes=["artists", "artist-rels", "recording-level-rels", "recordings"]

        '''
        For compilations, includes=['release-groups']

        "release-group": {
            "title": "Greatest Hits of the 80\u2019s",
            "type": "Compilation"
        },
        "title": "Greatest Hits of the 80\u2019s"
        '''

    except mbz.NetworkError:
        print("mbz.NetworkError")
        return {'error': '99'}
    except mbz.ResponseError:
        print("mbz.ResponseError")
        print("MBZ disc ID not found?:", disc.id)
        return {'error': '3', 'message': 'disc not found or bad response'}
    except Exception as err:
        print("Exception:", err)
        return {'error': '3', 'message': '404 Response Error'}

    if releases_by_discid.get('disc'):
        try:
            releases = releases_by_discid['disc']['release-list']
            with open(TMP_MBZ_GET1A, "wb") as rec_file:
                rec_file.write(json.dumps(releases))  # Debugging info
        except KeyError:
            print("FAILED: releases = releases_by_discid['disc']['release-list']")
            return {'error': '3', 'message': "releases_by_discid['disc']"}
    else:
        print("FAILED: if releases_by_discid.get('disc'):")
        return {'error': '3', 'message': "releases_by_discid.get('disc')"}

    ''' Clear out missing release_by_id error message file '''
    with open(TMP_MBZ_GET1F, "wb") as rec_file:  # Cleaned for loop bottom
        text = "mserve_mbz_get1_release_by_id_error_json\n"
        rec_file.write(text)  # Dump recording


    #print("inserting work-relation-list into releases")

    release_by_id_results = []  # List of

    for i, release in enumerate(releases):
        try:
            # https://github.com/alastair/python-musicbrainzngs/issues/202
            #print("\n\nNEW release i:", i)
            #print("===================\n")

            # https://github.com/alastair/python-musicbrainzngs/issues/202
            result = mbz.get_release_by_id(
                release['id'],
                includes=["artists", "artist-rels", "work-rels", 'work-level-rels',
                          "release-groups", "recording-level-rels", "recordings"])

            release_by_id_results.append(result['release'])  # for debug only
            release2 = result['release']

            #print("len(result):", len(result), "len(release2):", len(release2),
            #      "release['id']", release['id'])
            #print("len(release['medium-list']:", len(release['medium-list']))

            try:
                test = release2['id']
                text = "\nrelease2['id'] IS: " + test
                #print(text, "\n")
            except KeyError:
                text = "\nrelease2['id'] NOT FOUND !!!"
                text += "NEW release['id'] works though !!" + release['id']
                print(text, "\n")

            for j, medium in enumerate(release['medium-list']):
                tracks_list = medium['track-list']
                #print("i:", i, "j:", j, "len(tracks_list):", len(tracks_list))
                for k, track in enumerate(tracks_list):

                    ''' Sanity check original list '''
                    try:
                        recording = track['recording']
                        if True is False:
                            print("len(recording):", len(recording))
                    except KeyError:
                        print("FAILED: recording = track['recording']")
                        continue

                    # Progress display. For i=0 & i=1: stops at j=1 and k=6 ??
                    #print("i:", i, "j:", j, "k:", k)
                    # recording['artist-credit'][0]['artist']['name'])  UNICODE !!

                    ''' Sanity check list elements to insert '''
                    try:
                        works_list = release2['medium-list'][j]['track-list'][k]['recording']['work-relation-list']
                    except KeyError:
                        print("FAILED: works_list.")
                        continue
                    try:
                        work0 = works_list[0]['work']
                        if True is False:
                            print(work0)
                    except KeyError:
                        print("FAILED: work- = works_list[0]['work']")
                        continue


                    try:
                        extension = release2['medium-list'][j]['track-list'][k]['recording']['work-relation-list']
                        if True is False:
                            print("len(extension):", len(extension))
                    except KeyError:
                        print("FAILED: extension = release2['medium-list'][j]['track-list'][k]\n",
                              recording2)
                        continue

                    try:
                        releases[i]['medium-list'][j]['track-list'][k]['recording']['work-relation-list'] =\
                            release2['medium-list'][j]['track-list'][k]['recording']['work-relation-list']
                        #print("SUCCESS: releases[i] = release2")
                        #try:
                        #    new = releases[i]['medium-list'][j]['track-list'][k]['recording']['work-relation-list']
                        #    print("len(new = releases[i]...['work-relation-list']):",
                        #          len(new))
                        #except:
                        #    print("ERROR: new = releases[i]...['work-relation-list'] has no length")
                        #    continue
                    except KeyError:
                        print("FAILED: releases[i] = release2")
                        continue

        except Exception as err:
            with open(TMP_MBZ_GET1F, "a") as rec_file:  # Cleaned at top of loop
                text = "\n\nFAILED: result = musicbrainzngs.get_release_by_id(...)"
                text += "\nreleases[" + str(i) + "]['id'],"
                text += '\nincludes=["artists", "artist-rels", "work-rels", "work-level-rels",'
                text += '\n          "release-groups", "recording-level-rels", "recordings"])'
                text += "\nresulted in error: "
                print("Exception:", err)
                text += "\n\nTrying releases[" + str(i) + "]['id']"
                try:
                    test = releases[i]['id']
                    text += "\nreleases[" + str(i) + "]['id'] resulted in: " + test
                except KeyError:
                    text += "\nreleases[" + str(i) + "]['id'] is an ERROR"

                text += "\n"
    
                rec_file.write(text)  # Dump recording

    #print("\n\nEnd of function. Starting next function\n\n")

    if len(release_by_id_results) > 0:  # For debug only
        with open(TMP_MBZ_GET1C, "wb") as rec_file:
            rec_file.write(json.dumps(release_by_id_results))

    with open(TMP_MBZ_GET1D, "wb") as rec_file:
        rec_file.write(json.dumps(releases))  # Releases with work-relation-list

    return releases  # Releases dumped to GET1D ok, but not used in pass_back?


# noinspection PyBroadException
def get_date_info(passed):
    """ Find first year date by parsing all releases for recording """

    prt_dates = []  # Printing to debug file
    recordings = {}

    for d in passed:
        for medium in d['medium-list']:
            tracks_list = medium['track-list']  # Grab tracks
            for track_d in tracks_list:
                rec_id = track_d['recording']['id']
                try:
                    recordings = get_releases_by_recording_id(rec_id)
                except:
                    prt_dates.append("Invalid rec_id:" + str(rec_id))
                    print("get_date_info(): Invalid rec_id: " + str(rec_id))
                    continue
                if "artist-credit-phrase" in recordings:
                    prt_dates.append("artist-credit-phrase in recordings")
                for _ in recordings:
                    """" RECORDINGS from get_releases_by_recording_id() !!! 
                         NOT the recordings in release_by_id_results dictionary.
                         The format is DIFFERENT !
                    """
                    ''' Only 1 recording record exists but still have to loop: 
                        { 
                            "recording", { 
                                "id": "5b7be2d3-965e-4e43-8a1b-83be019a1c46", 
                                "length": "300573", 
                                "release-count": 19, 
                                "release-list":[{
                                    "title": "The Amazing Kamikaze Syndrome", 
                                    "country": "XE", 
                                    "date": "1983-12-03", 
                    '''
                    rec_dict = recordings['recording']  # Needs loop to work?
                    if "artist-credit-phrase" in rec_dict:
                        prt_dates.append("artist-credit-phrase in rec_dict")
                    rel_list = rec_dict['release-list']
                    if "artist-credit-phrase" in rel_list:
                        prt_dates.append("artist-credit-phrase in rel_list")
                    first_date = None

                    for rel_entry in rel_list:
                        if "artist-credit-phrase" in rel_entry:
                            prt_dates.append("artist-credit-phrase in rel_entry")
                        try:
                            str_date = rel_entry["date"]
                            prt_dates.append("str_date: " + str(str_date))
                        except:
                            continue
                        try:
                            year = int(str_date[:4])
                            if first_date:
                                if year < first_date:
                                    first_date = year
                            else:
                                first_date = year
                        except:
                            prt_dates.append("invalid str_date[:4]: " + str(str_date[:4]))
                            pass

                    prt_dates.append("#: " + medium['position'] + "-" +
                                     track_d['position'] +
                                     " | Title: " + track_d['recording']['title'] +
                                     " | Date: " + d['date'] +
                                     " | Year: " + str(first_date))

                    ''' Insert into existing track as 'first-date' '''
                    track_d['recording']['first-date'] = str(first_date)

    if recordings:
        with open(TMP_MBZ_GET1B, "wb") as rec_file:
            rec_file.write(json.dumps(recordings))  # Dump recordings

    with open(TMP_MBZ_GET1E, "wb") as rec_file:
        rec_file.write(json.dumps(passed))  # releases with dates

    if prt_dates:
        with open(TMP_MBZ_DEBUG, "wb") as rec_file:
            rec_file.write(json.dumps(prt_dates))

    return  # pass_back modified in place, not passed back (:~)


def get_releases_by_recording_id(mbz_id):
    """ Get all releases of a recording to find oldest date """
    try:
        recording = mbz.get_recording_by_id(
            mbz_id,
            includes=['releases', 'release-rels', 'work-rels']
        )
    except Exception as err:
        print("Exception:", err)
        return {'error': '5'}
    return recording


def filter_releases(passed):
    """ When more than one release, try to reduce hits for getting recordings """
    del_list = []
    for ndx, d in enumerate(passed):
        if d['title'] != d['release-group']['title']:
            # The first release group for disc #3 is invalid.
            # d['title'] = "Greatest Hits of the Eighties, Volume 1"
            # d['release-group']['title'] = "Greatest Hits of the 80's"
            del_list.append(ndx)
    for i in reversed(del_list):
        pass_back.pop(del_list[i])


if __name__ == "__main__":

    pass_back = get_releases_then_work_rels()

    ''' An error dictionary MAY have been passed back '''
    if type(pass_back) is list:
        ''' If more than one release, filter out mismatched titles. '''
        if len(pass_back) > 1:
            filter_releases(pass_back)  # No return, modified in place

        ''' Find first release date '''
        get_date_info(pass_back)  # No return, modified in place

    with open(DICT_FNAME, "wb") as f:
        pickle.dump(pass_back, f)   # Write good list or error dictionary


# End of mbz_get1.py
