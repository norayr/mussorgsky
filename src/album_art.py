#!/usr/bin/env python2.5
import urllib2, urllib
import libxml2
import os
from album_art_spec import getCoverArtFileName, getCoverArtThumbFileName, get_thumb_filename_for_path
import dbus, time

try:
    import PIL
    import Image
    pil_available = True
except ImportException:
    pil_available = False
    

LASTFM_APIKEY = "1e1d53528c86406757a6887addef0ace"
BASE_LASTFM = "http://ws.audioscrobbler.com/2.0/?method=album.getinfo"

# LastFM:
# http://www.lastfm.es/api/show?service=290
#
class MussorgskyAlbumArt:

    def __init__ (self):
        bus = dbus.SessionBus ()
        handle = time.time()
        if (pil_available):
            self.thumbnailer = LocalThumbnailer ()
        else:
            try:
                self.thumbnailer = bus.get_object ('org.freedesktop.thumbnailer',
                                                   '/org/freedesktop/thumbnailer/Generic')
            except dbus.exceptions.DBusException:
                print "No thumbnailer available"
                self.thumbnailer = None

    def get_album_art (self, artist, album):
        """
        Return a tuple (album_art, thumbnail_album_art)
        """
        filename = getCoverArtFileName (album)
        thumbnail = getCoverArtThumbFileName (album)

        if (os.path.exists (filename)):
            print "Album art already there " + filename
        else:
            online_resource = self.__last_fm (artist, album)
            if (online_resource):
                self.__save_url_into_file (online_resource, filename)
            else:
                return (None, None)

        if (os.path.exists (thumbnail)):
            print "Thumbnail exists"
        else:
            print "Requesting thumbnail"
            self.__request_thumbnail (filename)

        return (filename, thumbnail)

    def __last_fm (self, artist, album):
        if (not album or len (album) < 1):
            return
        
        URL = BASE_LASTFM + "&api_key=" + LASTFM_APIKEY
        if (artist and len(artist) > 1):
            URL += "&artist=" + urllib.quote(artist)
        if (album):
            URL += "&album=" + urllib.quote(album)
            
        print "Retrieving: %s" % (URL)
        result = self.__get_url (URL)
        if (not result):
            return None
        doc = libxml2.parseDoc (result)
        image_nodes = doc.xpathEval ("//image[@size='large']")
        if len (image_nodes) < 1:
            return None
        else:
            return image_nodes[0].content

    def __save_url_into_file (self, url, filename):
        image = self.__get_url (url)
        output_image = open (filename, 'w')
        output_image.write (image)
        output_image.close ()
        print "Saved %s -> %s " % (url, filename)
        
    def __get_url (self, url):
        request = urllib2.Request (url)
        request.add_header ('User-Agent', 'Mussorgsky/0.1 Test')
        opener = urllib2.build_opener ()
        try:
            return opener.open (request).read ()
        except:
            return None

    def __request_thumbnail (self, filename):
        if (not self.thumbnailer):
            print "No thumbnailer available"
            return
        uri = "file://" + filename
        handle = time.time ()
        print "Call to thumbnailer"
        self.thumbnailer.Queue ([uri], ["image/jpeg"], dbus.UInt32 (handle))


class LocalThumbnailer:
    def __init__ (self):
        self.THUMBNAIL_SIZE = (124,124)

    def Queue (self, uris, mimes, handle):
        print "Queue"
        for i in range (0, len(uris)):
            uri = uris[i]
            fullCoverFileName = uri[7:]
            print fullCoverFileName
            if (os.path.exists (fullCoverFileName)):
                thumbFile = get_thumb_filename_for_path (fullCoverFileName)
                
                image = Image.open (fullCoverFileName)
                image = image.resize (self.THUMBNAIL_SIZE, Image.ANTIALIAS )
                image.save( thumbFile, "JPEG" )
                print "Thumbnail: " + thumbFile


if __name__ == "__main__":
    import sys
    if ( len (sys.argv) > 2):
        artist = sys.argv[1]
        album = sys.argv[2]
    else:
        print "ARTIST ALBUM"
        sys.exit (-1)
    maa = MussorgskyAlbumArt ()
    print "Artist %s - Album %s" % (artist, unicode(album))
    print maa.get_album_art (artist, unicode(album))
    #assert (None, None) == maa.get_album_art ("muse", "absolution")
