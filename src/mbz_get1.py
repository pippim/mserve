# -*- coding: utf-8 -*-

#       mbz_get1.py - Standalone python program to run in background.
#                     Get Musicbrainz disc information - Pass 1 of 2.

#       Called with: 'python mbz_get1.py <Musicbrainz id>'
#       Parameters:  Pickle file contains object disc of libdiscid type
#       Returns:     Dictionary of Musicbrainz 'release-list' entries

# identical imports in mserve
from __future__ import print_function   # Must be first import
from __future__ import with_statement   # Error handling for file opens


import subprocess32 as sp
#import threading
import re
import time
import datetime
from PIL import Image, ImageTk, ImageDraw, ImageFont
import musicbrainzngs as mbz
import libdiscid as discid
import pickle
import sys
import os

from pprint import pprint

# Homegrown
import location as lc
import message
import image as img

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

# IPC pickle filename shouldn't end with .pkl because it's used for playlists.
IPC_PICKLE_FNAME = lc.MSERVE_DIR + "ipc.pickle"
# Above and below are TWO IDENTICAL FILENAMES
DICT_FNAME = sys.argv[1]            # Pickle filename to save to
SEARCH_LIMIT = sys.argv[2]          # Number of search results to return when
                                    # less than 3 only CD's searched. When more
                                    # then vinyl (which may have artwork!) are
                                    # included. EG Jim Steinem Bad for Good


def get_release_by_mbzid(mbz_id, toplevel=None):

    try:
        # This actually doesn't generate any errors...
        mbz.set_useragent("mserve", "0.1", "RickLee518@gmail.com")
    except mbz.NetworkError:
        return { 'error': '99' }
    except:
        return { 'error': '2' }

#   PRODUCTION VERSION will use this instead:
#    mbz.set_useragent("mserve", "0.1")
#    mbz.auth(u=input('Musicbrainz username: '), p=getpass())

    try:

        release = mbz.get_release_by_id(mbz_id,
                includes=['recordings'])
    except:
        return { 'error': '5' }

    #print('\n===================== release ====================')
    #pprint(release)
    """
===================== release ====================
{'release': {
     'asin': 'B0000025IQ',
     'barcode': '074643653121',
     'country': 'US',
     'cover-art-archive': {'artwork': 'false',
                   'back': 'false',
                   'count': '0',
                   'front': 'false'},
     'date': '1993-01-26',
     'id': '9241985f-efdf-40a7-8734-3fa88150090c',
     'medium-count': 1,
     'medium-list': [
             {'format': 'CD',
              'position': '1',
              'track-count': 10,
              'track-list': [
                   {'id': 'e76f6660-decb-3215-888c-fb8b1fff4e59',
                      'length': '524466',
                      'number': '1',
                      'position': '1',
                      'recording': {'id': '847b4e09-8839-4ce9-b352-8370da920f39',
                                    'length': '525000',
                                    'title': 'Bad for Good'
                                   },
                      'track_or_recording_length': '524466'
                   },
                   {'id': '90120c36-5ab1-39ff-b0b3-3b61991aaa83',
                      'length': '276506',
                      'number': '2',
                      'position': '2',
                      'recording': {'id': '0140c7a2-edac-41c7-9747-7907d5a32d39',
                                    'length': '276800',
                                    'title': 'Lost Boys and Golden Girls'
                                   },
                      'track_or_recording_length': '276506'
                    },
    
    """
    return release


def get_disc_info(toplevel=None):
    #with open(IPC_PICKLE_FNAME, 'r') as fin:
    #    print(fin.read())
    # Our last program has just finished. Get dictionary results
    with open(IPC_PICKLE_FNAME, 'rb') as f:
        # read the data as binary data stream
        disc = pickle.load(f)

    # Valid Musicbrainz ID?
    if len(disc.id) != 28:
        return {'error': '1'}

    mbz_id = disc.id

    track_lengths = disc.track_lengths

    # If you plan to submit data, authenticate
    #mbz.auth("user", "password")

    # Tell musicbrainz what your app is, and how to contact you
    # (this step is required, as per the webservice access rules
    # at http://wiki.musicbrainz.org/XML_Web_Service/Rate_Limiting )
    try:
        mbz.set_useragent("mserve", "0.1", "RickLee518@gmail.com")
    except:
        #print('useragent failed for mserve')
        return {'error': '2'}

#   PRODUCTION VERSION will use this instead:
#    mbz.set_useragent("mserve", "0.1")
#    mbz.auth(u=input('Musicbrainz username: '), p=getpass())

    #release = mbz.get_recordings_by_isrc(isrc)
    #print('isrc:\n',release)

    try:
        release = mbz.get_releases_by_discid(mbz_id, includes=
                                             ['artists', 'recordings'])
        # There doesn't appear to be an error when no internet connection
    except mbz.NetworkError:
        #print('Network error')
        return {'error': '99'}
    except mbz.ResponseError:
        return {'error': '3', 'message': 'disc not found or bad response'}
    except Exception as err:
        #print('mbz.get_releases_by_discid Error:', err)
        return {'error': '3', 'message': '404 Response Error'}


    # print('\nget_disc_info() result by mbz_id:', mbz_id)
    # TODO: Set flag to indicate of 'disc' or 'cdstub' found.
    if release.get('disc'):
    
        # NOT TESTED YET !!!
        #pprint(release)
        return release['disc']['release-list']

    """ TODO: Incorporate cd stub logic below, not sure what immediate code
        below is supposed to do anymore.

        this_release = release['disc']['release-list'][0]
        title = this_release['title']
        artist = this_release['artist-credit'][0]['artist']['name']
     
        if this_release['cover-art-archive']['artwork'] == 'true':
          url = 'http://coverartarchive.org/release/' + this_release['id']
          art = json.loads(requests.get(url, allow_redirects=True).content)
          for image in art['images']:
             if image['front'] == True:
                cover = requests.get(image['image'], 
                                     allow_redirects=True)
                fname = '{0} - {1}.jpg'.format(artist, title)
                print('COVER="{}"'.format(fname))
                f = open(fname, 'wb')
                f.write(cover.content)
                f.close()
                break
     
        #print('TITLE="{}"'.format(title))
        #print('ARTIST="{}"'.format(artist))
        #print('YEAR="{}"'.format(this_release['date'].split('-')[0]))
        for medium in this_release['medium-list']:
          for disc in medium['disc-list']:
             if disc['id'] == this_disc.id:
                tracks=medium['track-list']
                for track in tracks:
                   print('TRACK[{}]="{}"'.format(track['number'], 
                                                 track['recording']['title']))
                break

    #print(release)
    #print('\n')
    # TODO: Set flag to indicate of 'disc' or 'cdstub' found.
    track_dict = {}                         # name: Xxxx and length: 999
    if release.get('cdstub'):
        # TODO: This information is disgarded, should be passed back to parent
        count = release['cdstub']['track-count']
        title = release['cdstub']['title']
        artist = release['cdstub']['artist']
        # print('track-count:',count,' title:',title,' artist:',artist)
        track_list = release['cdstub']['track-list']
        for i, track in enumerate(track_list):
            # print(i+1, ": ", track['title'], ' length:',track['length'])

            # Output file name based on MusicBrainz values
            fmt = "m4a"
            FORMAT_TRACK_NAME="{:02} {}.{}"
            # What if two tracks have same name?
            track_dict [track['title']] = track_lengths[i]
            outfname = FORMAT_TRACK_NAME.format(i+1, track['title'], \
                       fmt).replace('/', '-')

        track_count = len(track_lengths)            # list of track lengths

        # Override 'cdstub' with query for releases
        # Track count will limit our results if we have no artwork on good match
        #release_list = match_album(artist, title, tracks=track_count, \
        #                           toplevel=toplevel)
        release_list = match_album(artist, title, toplevel=toplevel)
        return release_list
    """


def match_album(artist, album, tracks=None, limit=SEARCH_LIMIT, toplevel=None):
    """Searches for a single album ("release" in MusicBrainz parlance)
    and returns an iterator over AlbumInfo objects. May raise a
    MusicBrainzAPIError.
 
    The query consists of an artist name, an album name, and,
    optionally, a number of tracks on the album.
    """
    # Build search criteria.
    criteria = {'release': album.lower().strip()}
    if artist is not None:
        criteria['artist'] = artist.lower().strip()
    else:
        # Various Artists search.
        criteria['arid'] = "various"        # Not tested
    if tracks is not None:
        criteria['tracks'] = str(tracks)
 
    # Abort if we have no search terms.
    if not any(criteria.itervalues()):
        return None
 
    if SEARCH_LIMIT <= 3:
        strict = True         # Match words in order
    else:
        strict = False        # Match words with Lucene fuzzy logic

    try:
        # There is no format option on this method. Maybe type works?
        # res = mbz.search_releases(limit=limit, format='CD', **criteria)
        # To do get 25 limit from engine and filter down to 3 results to return
        res = mbz.search_releases(limit=limit, strict=strict, **criteria)
    except mbz.MusicBrainzError as exc:
        raise MusicBrainzAPIError(exc, 'release search', criteria,
                                  traceback.format_exc())
        return {'error': '4'}         # Error searching releases

    """
    for release in res['release-list']:
        # The search result is missing some data (namely, the tracks),
        # so we just use the ID and fetch the rest of the information.
        print('\n', '=' * 35, 'Release', '=' * 35)
        pprint(release)
    """
    #print('\n======================= res: =========================')
    #pprint(res)
    """
======================= res: =========================
{'release-count': 1386079,
 'release-list': [
    {'artist-credit': [{'artist': {'id': '80e7cb60-3ed8-46dd-8eec-9052606306f2',
                                   'name': 'Jim Steinman',
                                   'sort-name': 'Steinman, Jim'},
                        'name': 'Jim Steinman'}],
     'artist-credit-phrase': 'Jim Steinman',
     'asin': 'B0000025IQ',
     'barcode': '5099747204227',
     'country': 'DE',
     'date': '1993-12-20',
     'ext:score': '100',
     'id': 'de031a18-e2c9-3c15-8649-20dda77980da',
     'label-info-list': [{'catalog-number': '472042 2',
                          'label': {'id': '8f638ddb-131a-4cc3-b3d4-7ebdac201b55',
                                  'name': 'Epic'}}],
     'medium-count': 1,
     'medium-list': [{},
                     {'disc-count': 2,
                      'disc-list': [],
                      'format': 'CD',
                      'track-count': 10,
                      'track-list': []}],
     'release-event-list': [{'area': {'id': '85752fda-13c4-31a3-bee5-0e5cb1f51dad',
                                      'iso-3166-1-code-list': ['DE'],
                                      'name': 'Germany',
                                      'sort-name': 'Germany'},
                             'date': '1993-12-20'}],
     'release-group': {'id': '285209d6-ead9-36fc-9a84-7ca7b1493cba',
                       'primary-type': 'Album',
                       'title': 'Bad for Good',
                       'type': 'Album'},
     'status': 'Official',
     'text-representation': {'language': 'eng',
                             'script': 'Latn'},
     'title': 'Bad for Good'},
    """
    return res['release-list']


#        album_info = album_for_id(release['id'])
#        if album_info:
#            yield album_info

def match_recording(artist, album, tracks=None, limit=10, toplevel=None):
    """ Searches for a single album ("release" in MusicBrainz parlance)
    and returns an iterator over AlbumInfo objects. May raise a
    MusicBrainzAPIError.
 
    The query consists of an artist name, an album name, and,
    optionally, a number of tracks on the album.
    """
    # Build search criteria.
    criteria = {'release': album.lower().strip()}
    if artist is not None:
        criteria['artist'] = artist.lower().strip()
    else:
        # Various Artists search.
        criteria['arid'] = "various"        # Not tested
    if tracks is not None:
        criteria['tracks'] = str(tracks)
 
    # Abort if we have no search terms.
    if not any(criteria.itervalues()):
        return None
 
    try:
        # Vinyl has our image CD has no artwork
        #res = mbz.search_recordings(limit=limit, format='CD', **criteria)
        res = mbz.search_recordings(limit=limit, **criteria)
    except mbz.MusicBrainzError as exc:
        raise MusicBrainzAPIError(exc, 'release search', criteria,
                                  traceback.format_exc())
    """
    for release in res['release-list']:
        # The search result is missing some data (namely, the tracks),
        # so we just use the ID and fetch the rest of the information.
        print('\n', '=' * 35, 'Release', '=' * 35)
        pprint(release)
    """
    return res

#        album_info = album_for_id(release['id'])
#        if album_info is not None:
#            yield album_info


def album_for_id(mb_id):
    """ Get the recording with mb_id as a dict with a 'recording' key """
    try:
        res = mbz.get_recording_by_id(mb_id)
    except mbz.MusicBrainzError as exc:
        raise MusicBrainzAPIError(exc, 'get recording by id', criteria,
                                  traceback.format_exc())


def find_covers(self, track, limit=-1):
    """
        Performs the search
    """
    try:
        artist = track.get_tag_raw('artist')[0]
        album = track.get_tag_raw('album')[0]
    except (AttributeError, TypeError):
        return []
 
    result = musicbrainzngs.search_releases(
        release=album,
        artistname=artist,
        # format='CD',
        limit=3  # Unlimited search is slow
    )
 
    if result['release-list']:
        mb_ids = [a['id'] for a in result['release-list']]
         
        # Check the actual availability of the covers
        for mb_id in mb_ids[:]:
            try:
                url = self.__caa_url.format(mb_id=mb_id, size=250)
                 
                headers = {'User-Agent': self.user_agent}
                req = urllib2.Request(url, None, headers)
                response = urllib2.urlopen(req)
            except urllib2.HTTPError:
                mb_ids.remove(mb_id)
            else:
                response.close()
 
        # For now, limit to medium sizes
        mb_ids = [mb_id + ':500' for mb_id in mb_ids]
 
        return mb_ids
 
    return []  # Nothing found return empty list

    """
        Programmer Creek tons of examples:
        https://www.programcreek.com/python/example/73822/mutagen.id3.APIC

    """

    """
    Embed Album Cover to mp3 with Mutagen in Python 3:
        https://stackoverflow.com/questions/42473832/
        embed-album-cover-to-mp3-with-mutagen-in-python-3

import requests
import shutil

from mutagen.id3 import ID3, TPE1, TIT2, TRCK, TALB, APIC
# ImportError: No module named mutagen.id3


def addMetaData(url, title, artist, album, track):

    response = requests.get(url, stream=True)
    with open('img.jpg', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

    audio = ID3(music_file.mp3)
    audio['TPE1'] = TPE1(encoding=3, text=artist)
    audio['TIT2'] = TALB(encoding=3, text=title)
    audio['TRCK'] = TRCK(encoding=3, text=track)
    audio['TALB'] = TALB(encoding=3, text=album)

    with open('img.jpg', 'rb') as albumart:
        audio['APIC'] = APIC(
                          encoding=3,
                          mime='image/jpeg',
                          type=3, desc=u'Cover',
                          data=albumart.read()
                        )            
    audio.save()

    """
    """
    Mutagen's save() does not set or change cover art for MP3 files:
        https://stackoverflow.com/questions/59815698/
        mutagens-save-does-not-set-or-change-cover-art-for-mp3-files
from mutagen.mp3 import MP3
# ImportError: No module named mutagen.mp3

from mutagen.id3 import APIC

file = MP3(filename)

with open('Label.jpg', 'rb') as albumart:
    file.tags['APIC'] = APIC(
        encoding=3,
        mime='image/jpeg',
        type=3, desc=u'Cover',
        data=albumart.read()
    )
file.save(v2_version=3)    
    """

"""
    #
    # From Fedora Magazine
    #
"""
import musicbrainzngs as mb
import libdiscid
import requests
import json
from getpass import getpass


def get_contents():
    this_disc = libdiscid.read(libdiscid.default_device())
#    mb.set_useragent(app='get-contents', version='0.1')
#    mb.auth(u=input('Musicbrainz username: '), p=getpass())
    mb.set_useragent("mserve", "0.1", "RickLee518@gmail.com")

    release = mb.get_releases_by_discid(this_disc.id, toc=this_disc.toc, \
                                        includes=['artists', 'recordings'])

    print('\nget_contents() release:\n',release)

    if release.get('disc'):
       this_release=release['disc']['release-list'][0]
       title = this_release['title']
       artist = this_release['artist-credit'][0]['artist']['name']
     
       if this_release['cover-art-archive']['artwork'] == 'true':
          url = 'http://coverartarchive.org/release/' + this_release['id']
          art = json.loads(requests.get(url, allow_redirects=True).content)
          for image in art['images']:
             if image['front'] == True:
                cover = requests.get(image['image'], 
                                     allow_redirects=True)
                fname = '{0} - {1}.jpg'.format(artist, title)
                print('COVER="{}"'.format(fname))
                f = open(fname, 'wb')
                f.write(cover.content)
                f.close()
                break
     
       print('TITLE="{}"'.format(title))
       print('ARTIST="{}"'.format(artist))
       print('YEAR="{}"'.format(this_release['date'].split('-')[0]))
       for medium in this_release['medium-list']:
          for disc in medium['disc-list']:
             if disc['id'] == this_disc.id:
                tracks=medium['track-list']
                for track in tracks:
                   print('TRACK[{}]="{}"'.format(track['number'], 
                                                 track['recording']['title']))
                break

"""
Fedora Magazine: https://fedoramagazine.org/use-gstreamer-python-rip-cds/

"""
import os, sys
import subprocess
from argparse import ArgumentParser
import libdiscid
import musicbrainzngs as mb
import requests
import json
from getpass import getpass


def read_cd():      
    parser = ArgumentParser()
    parser.add_argument('-f', '--flac', action='store_true', dest='flac',
                        default=False, help='Rip to FLAC format')
    parser.add_argument('-w', '--wav', action='store_true', dest='wav',
                        default=False, help='Rip to WAV format')
    parser.add_argument('-o', '--ogg', action='store_true', dest='ogg',
                        default=False, help='Rip to Ogg Vorbis format')
    options = parser.parse_args()

    # Set up output varieties
    if options.wav + options.ogg + options.flac > 1:
        raise parser.error("Only one of -f, -o, -w please")
    if options.wav:
        fmt = 'wav'
        encoding = 'wavenc'
    elif options.flac:
        fmt = 'flac'
        encoding = 'flacenc'
        from mutagen.flac import FLAC as audiofile
    elif options.ogg:
        fmt = 'oga'
        quality = 'quality=1'
        encoding = 'vorbisenc {} ! oggmux'.format(quality)
        from mutagen.oggvorbis import OggVorbis as audiofile

    # Get MusicBrainz info
    this_disc = libdiscid.read(libdiscid.default_device())
    mb.set_useragent(app='get-contents', version='0.1')
    mb.auth(u=input('Musicbrainz username: '), p=getpass())

    release = mb.get_releases_by_discid(this_disc.id, includes=['artists',
                                                                'recordings'])
    if release.get('disc'):
        this_release=release['disc']['release-list'][0]

        album = this_release['title']
        artist = this_release['artist-credit'][0]['artist']['name']
        year = this_release['date'].split('-')[0]

        for medium in this_release['medium-list']:
            for disc in medium['disc-list']:
                if disc['id'] == this_disc.id:
                    tracks = medium['track-list']
                    break

        # We assume here the disc was found. If you see this:
        #   NameError: name 'tracks' is not defined
        # ...then the CD doesn't appear in MusicBrainz and can't be
        # tagged.  Use your MusicBrainz account to create a release for
        # the CD and then try again.
                
        # Get cover art to cover.jpg
        if this_release['cover-art-archive']['artwork'] == 'true':
            url = 'http://coverartarchive.org/release/' + this_release['id']
            art = json.loads(requests.get(url, allow_redirects=True).content)
            for image in art['images']:
                if image['front'] == True:
                    cover = requests.get(image['image'], allow_redirects=True)
                    fname = '{0} - {1}.jpg'.format(artist, album)
                    print('Saved cover art as {}'.format(fname))
                    f = open(fname, 'wb')
                    f.write(cover.content)
                    f.close()
                    break

    for trackn in range(len(tracks)):
        track = tracks[trackn]['recording']['title']

        # Output file name based on MusicBrainz values
        fmt = "m4a"
        FORMAT_TRACK_NAME="{:02} {}.{}"
        outfname = FORMAT_TRACK_NAME.format(i+1, track['title'], \
                   fmt).replace('/', '-')

        print('Ripping track {}...'.format(outfname))
        cmd = 'gst-launch-1.0 cdiocddasrc track={} ! '.format(trackn+1) + \
                'audioconvert ! {} ! '.format(encoding) + \
                'filesink location="{}"'.format(outfname)
        msgs = subprocess.getoutput(cmd)

        if not options.wav:
            audio = audiofile(outfname)
            print('Tagging track {}...'.format(outfname))
            audio['TITLE'] = track
            audio['TRACKNUMBER'] = str(trackn+1)
            audio['ARTIST'] = artist
            audio['ALBUM'] = album
            audio['DATE'] = year
            audio.save()

"""
recursively process subdirectories of given directory, downloading
appropriate cover images from Google Images if .mp3 files are found
"""

__author__ = "James Stewart"
__homepage__ = "https://launchpad.net/coverlovin"

import os
import sys
""" Note done yet
import urllib.request
import urllib.parse
import urllib.error
import urllib.request
import urllib.error
import urllib.parse
"""
from pprint import pformat
import simplejson
#import logging         # Aug 13/2021 - lost sys.stderr
""" Note done yet
from mutagen.easymp4 import EasyMP4
from mutagen.easyid3 import EasyID3
"""
from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter

# logging
#log = logging.getLogger('coverlovin')
#log.setLevel(logging.INFO)
#handler = logging.StreamHandler()
#formatter = logging.Formatter("%(message)s")
#handler.setFormatter(formatter)
#log.addHandler(handler)

# google images
defaultReferer = "https://launchpad.net/coverlovin"
googleImagesUrl = "https://ajax.googleapis.com/ajax/services/search/images"

# audio file types (i.e. file name extensions)
audioTypes = ['mp3', 'm4a']


def sanitise_for_url(inputString):
    """sanitise a string for use within a url"""
    if inputString is None:
        return ''
    return urllib.parse.quote_plus(inputString)


def dl_cover(urlList, directory, fileName, overWrite=False):
    """download cover image from url in list to given directory/fileName"""

    coverImg = os.path.join(directory, fileName)
    # move existing file if overWrite enabled
    if os.path.isfile(coverImg) and overWrite:
        log.info("%s exists and overwrite enabled - moving to %s.bak", \
                 coverImg, coverImg)
        os.rename(coverImg, (coverImg + '.bak'))
    # download cover image from urls in list
    for url in urlList:
        log.debug('opening url: "%s"', url)
        urlOk = True
        # open connection
        try:
            coverImgWeb = urllib.request.urlopen(url, None, 10)
        except Exception as err:
            log.error('exception: ' + str(err))
            urlOk = False
        # download file
        if urlOk:
            log.info('downloading cover image\n from: "%s"\n to: "%s"', \
                     url, coverImg)
            coverImgLocal = open(os.path.join(directory, fileName), 'w')
            coverImgLocal.write(coverImgWeb.read())
            coverImgWeb.close()
            coverImgLocal.close()
            # cover successfully downloaded so return
            return True

    # no cover image downloaded
    return False


def get_img_urls(searchWords, fileType='jpg', fileSize='small', \
                 resultCount=8, referer=defaultReferer):
    """
    return list of cover urls obtained by searching
    google images for searchWords
    """

    imgUrls = []

    # sanitise searchwords
    searchWords = [sanitise_for_url(searchWord) for searchWord in searchWords]
    # construct url
    url = googleImagesUrl + '?v=1.0&q='
    # add searchwords
    for searchWord in searchWords:
        url += searchWord + '+'
    url = url[:-1]
    # add other parameters
    url += '&as_filetype=' + fileType
    url += '&imgsz=' + fileSize
    url += '&rsz=' + str(resultCount)
    request = urllib.request.Request(url, None, {'Referer': referer})

    # make request from the provided url
    try:
        log.debug('requesting url: "%s"', url)
        response = urllib.request.urlopen(request, None, 10)
    except Exception as err:
        log.error('exception: ', str(err))
        return imgUrls

    # load json response results into python dict
    try:
        results = simplejson.load(response)
    except Exception as err:
        log.error('exception: ', str(err))
        return imgUrls

    # add results to list
    result_ok = False
    try:
        if results and 'responseData' in results:
            rd = results['responseData']  # responseData is a dict
            if rd and 'results' in rd:
                for result in rd['results']:
                    result_ok = True
                    imgUrls.append(result['url'])
        # if not result_ok, see if an explanation can be found
        if not result_ok and results:
            if 'responseStatus' in results:
                log.debug('returned results had no data; status "%s"',
                          results['responseStatus'])
            elif 'responseDetails' in results:
                log.debug('returned results had no data; message "%s"',
                          results['responseDetails'])
    except Exception as err:
        log.exception(err, exc_info=True)

    return imgUrls


def process_dir(thisDir, results=[], coverFiles=[]):
    """
    Recursively process sub-directories of given directory,
    gathering artist/album info per-directory.

    Call initially with empty results. Results will be
    gradually populated by recursive calls. Provide coverFiles
    list to ignore directories where cover files already exist.
    """

    dirs = []
    files = []

    # read directory contents
    if os.path.exists(thisDir):
        try:
            for item in os.listdir(thisDir):
                itemFullPath = os.path.join(thisDir, item)
                if os.path.isdir(itemFullPath):
                    dirs.append(itemFullPath)
                else:
                    files.append(item)
        except OSError as err:
            log.error(err)
            return results
    else:
        log.error('directory does not exist: "%s"', thisDir)
        return results
    # sort dirs and files to be processed in order
    dirs.sort()
    files.sort()
    # recurse into subdirs
    for dir in dirs:
        results = process_dir(dir, results=results, coverFiles=coverFiles)
    # continue processing this dir once subdirs have been processed
    log.debug('evaluating "%s"', thisDir)
    # if any of the given cover files exist, no further work required
    for coverFile in coverFiles:
        if coverFile in files:
            log.debug('cover file "%s" exists - skipping "%s"', \
                      coverFile, thisDir)
            return results
    for file_ in files:
        mp4Audio = False
        mp3Audio = False
        fileFullPath = os.path.join(thisDir, file_)
        fileName, fileExtension = os.path.splitext(file_)
        # check file for id3 tag info
        try:
            if fileExtension == '.m4a':
                mp4Audio = EasyMP4(fileFullPath)
            elif fileExtension == '.mp3':
                mp3Audio = EasyID3(fileFullPath)
        except Exception as err:
            log.exception(err)
            continue
        # get values and sanitise nulls
        artist = None
        album = None
        if mp4Audio:
            artist = mp4Audio['artist'][0]
            album = mp4Audio['album'][0]
        elif mp3Audio:
            artist = mp3Audio['artist'][0]
            album = mp3Audio['album'][0]
        if artist is None:
            artist = ''
        if album is None:
            album = ''
        # if either artist or album found, append to results and return
        if artist or album:
            log.info('Album details found: "%s" / "%s" within file "%s"', \
                     artist, album, file_)
            results.append((thisDir, artist, album,))
            return results

    log.debug('no Artist or Album found within "%s"', thisDir)
    return results


def parse_args_opts():
    """parse command line argument and options"""

    googImgOpts = ['small', 'medium', 'large']
    fileTypeOpts = ['jpg', 'png', 'gif']

    parser = ArgumentParser()
    parser.description = 'Given a list of directories, DIRS, for each directory, search online for a matching album' \
                         ' art cover image file. Write that image file into the passed directory.'
    parser.add_argument(dest='dirs', metavar='DIRS', action='append', type=str, nargs='+',
                        help='directories to scan for audio files (Required)')
    parser.add_argument('-s', '--size', dest='size', action='store', default=googImgOpts[1],
                        choices=googImgOpts,
                        help='file size (default: "%(default)s")')
    parser.add_argument('-i', '--image', dest='image', action='store', default='jpg',
                        choices=fileTypeOpts,
                        help='image format type (default: "%(default)s")')
    parser.add_argument('-n', '--name', dest='name', action='store', default='cover',
                        help='cover image file name. This is the file name that will be created within passed DIRS. '
                             'This will be appended with the preferred TYPE, e.g. ".jpg", ".png", etc. '
                             '(default: "%(default)s")')
    parser.add_argument('-c', '--count', dest='count', action='store', default='8', type=int,
                        help='image lookup count (default: %(default)s)')
    parser.add_argument('-o', '--overwrite', dest='overwrite', action='store_true', default=False,
                        help='overwrite (default %(default)s)')
    parser.add_argument('-r', '--referer', dest='referer', action='store', default=defaultReferer,
                        help='referer url used in HTTP GET requests (default: "%(default)s")')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False,
                        help='print debug logs (default %(default)s)')
    parser.epilog = 'This program processes passed DIRS searching for files that are of the list %s.' % (audioTypes,) \
                    + ' Given a directory with files of that type, the file contents will be read for the Artist name' \
                    + ' and Album name using embedded ID3 tags.  All files will be read and the most common string' \
                    + ' found will be used. If no ID3 tags are present than a reasonable guess will be made based' \
                    + ' on the directory name, e.g. "Artist - Year - Album", or "Artist - Album"'
    args = parser.parse_args()

    return args.dirs[0], args.image, args.name, args.size, args.count, \
           args.overwrite, args.referer, args.debug


def main_function():
    """
    changed from main() to avoid naming confictions

    Recursively download cover images for music files in a
    given directory and its sub-directories
    """

    dirs, image_type, image_name, image_size, search_count, overwrite, \
            referer, debug = parse_args_opts()

    #if debug:
    #    log.setLevel(logging.DEBUG)
    #log.debug('parameters: dirs: "%s"', dirs)
    #log.debug('            image: "%s"', image_type)
    #log.debug('            name: "%s"', image_name)
    #log.debug('            size: "%s"', image_size)
    #log.debug('            search count: "%s"', search_count)
    #log.debug('            overwrite?: %s', overwrite)
    #log.debug('            referer: "%s"', referer)
    #log.debug('            debug?: "%s"', debug)

    # only pass cover filename if overwrite disabled
    coverFiles = []
    if not overwrite:
        coverFiles = [image_name + os.extsep + image_type]

    # gather list of directories with Album/Artist info
    log.debug('')
    musicDirs = []
    for dir_ in dirs:
        daa = process_dir(dir_, coverFiles=coverFiles)
        if daa:
            musicDirs.append(daa)
        log.debug('')

    # download covers
    for musicDir in musicDirs:
        for daa in musicDir:
            dir_, artist, album = daa
            urls = get_img_urls([artist, album], fileType=image_type, \
                                fileSize=image_size, resultCount=search_count)
            if len(urls) > 0:
                log.debug('gathered %i urls for "%s" / "%s":', 
                          len(urls), artist, album)
                for url in urls:
                    log.debug(' %s' % url)
                # download cover image
                dl_cover(urls, dir_, image_name, overWrite=overwrite)
            else:
                log.info('no urls found for "%s" / "%s"', artist, album)

    return 0


def add_track_info(release_list):

    """ Populate empty medium-list with track list. Normally returns None.
        If error return dictionary of error(s).
    """

    """
======================= res: =========================
{'release-list': [{
     'medium-list': [{},
                     {'disc-count': 2,
                      'disc-list': [],
                      'format': 'CD',
                      'track-count': 10,
                      'track-list': []}],
     'title': 'Bad for Good'}]}


- OR for Streetheart -

{'release': {'cover-art-archive': {'artwork': 'true',
                                   'back': 'false',
                                   'count': '1',
                                   'front': 'true'},
             'date': '1982',
             'id': '7a1f7db4-d59a-4722-9394-3edcd6ba24de',
             'medium-count': 1,
             'medium-list': [{'position': '1',
                              'track-count': 9,
                              'track-list': [{'id': '38100742-9e1e-336d-ad69-83d0719fca70',
                                              'length': '303000',
                                              'number': '1',
                                              'position': '1',
                                              'recording': {'id': '436b1916-c613-429a-812a-ffb6cc4b9247',

    """

    for d in release_list:
        # TODO: Get multiple CD medium
        try:
            r = get_release_by_mbzid(d['id'])
        except:
            # We get all the way to bottom of program before no internet is
            # realized because dictionary not setup and original disc object
            # in pickle IPC file? Error Reported:
            #   File "mbz_get1.py", line 983, in add_track_info
            #     r = get_release_by_mbzid(d['id'])
            return {'error': '99'}

        # Must have ['release'] key to be usable dictionary
        if not type(r) is dict:
            return {'error': '6', 'message': d['id'], 'data': d, 'data2': r}
        if r.get('error'):
            return r
        if not r.get('release'):
            return {'error': '6', 'message': d['id'], 'data': d, 'data2': r}

        # Debugging uncomment line below to get screen dump of dictionaries
        #return { 'error': '6', 'message': d['id'], 'data': d, 'data2': r }
        # Replace empty track list with real tracks
        mdm_ndx = len(d['medium-list']) - 1
        # For Filter mdn_ndx = 0. For Jim Steinem mdm_ndx = 1
        # Track list may not be empty
        if len(d['medium-list'][mdm_ndx]['track-list']) == 0:
            d['medium-list'][mdm_ndx]['track-list'].extend(
                                r['release']['medium-list'][0]['track-list'])
        """
===================== release ====================
{'release': {
 'medium-list': [
         {'format': 'CD',
          'position': '1',
          'track-count': 10,
          'track-list': [
               {'id': 'e76f6660-decb-3215-888c-fb8b1fff4e59',
                  'length': '524466',
                  'number': '1',
                  'position': '1',
                  'recording': {'id': '847b4e09-8839-4ce9-b352-8370da920f39',
                                'length': '525000',
                                'title': 'Bad for Good'
                               },
                  'track_or_recording_length': '524466'
               }]
           }]
       }}

        """
        # TODO medium-list is 1 for second CD, etc.

        # Below does nothing !!! - Kept here for educational purposes

        tracks_list = r['release']['medium-list'][0]['track-list']
        for i, track_d in enumerate(tracks_list):
            #print('track_d:\n',track_d)
            position = track_d['position']
            recording_d = track_d['recording']
            song = track_d['recording']['title']
            length = recording_d.get('length', '0')
            # In database some tracks have no length key
            duration = discid.sectors_to_seconds(int(length))
            if length is None:
                length = '0'
            duration = int(length) / 1000

            hhmmss = format_duration(duration)
            FORMAT_TRACK_NAME="    {:02} - {}"
            outfname = FORMAT_TRACK_NAME.format(i+1, song.encode("utf8")) \
                       .replace('/', '-')

    return None


def format_duration(seconds):
    duration = str(datetime.timedelta(seconds=seconds))
    duration = remove_prefix(duration, '0:')
    duration = remove_prefix(duration, '0')
    return duration


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text  # or whatever


if __name__ == "__main__":

    pass_back = get_disc_info()     # Works even with no internet???
    #pprint(pass_back)
    # If a list isn't passed back that means an error dictionary is passed back
    if type(pass_back) is list:
        return_d = add_track_info(pass_back)
        if return_d:
            pass_back = return_d    # Dictionary with {'error': '99'}
    else:
        #print('pass_back is dictionary')
        pass

    with open(DICT_FNAME, "wb") as f:
        # store the data as binary data stream
        pickle.dump(pass_back, f)           # Save dictionary as pickle file
        #pickle.dump(pass_back, f, -1)           # Save dictionary as pickle file

# End of mbz_get1.py
