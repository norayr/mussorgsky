#!/usr/bin/env python2.5
import urllib2, urllib
import os
from album_art_spec import getCoverArtFileName, getCoverArtThumbFileName, get_thumb_filename_for_path
import dbus, time
import string

try:
    import libxml2
    libxml_available = True
except ImportError:
    libxml_available = False

try:
    import PIL
    import Image
    pil_available = True
except ImportError:
    pil_available = False
    

LASTFM_APIKEY = "1e1d53528c86406757a6887addef0ace"
BASE_LASTFM = "http://ws.audioscrobbler.com/2.0/?method=album.getinfo"


BASE_MSN = "http://www.bing.com/images/search?q="
MSN_MEDIUM = "+filterui:imagesize-medium"
MSN_SMALL = "+filterui:imagesize-medium"
MSN_SQUARE = "+filterui:aspect-square"
MSN_PHOTO = "+filterui:photo-graphics"

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
            online_resource = self.__msn_images (artist, album)
            if (online_resource):
                print "Choosed:", online_resource
                content = self.__get_url (online_resource)
                if (content):
                    print "Albumart: %s " % (filename)
                    self.__save_content_into_file (content, filename)
                else:
                    return (None, None)
            else:
                return (None, None)

        if (os.path.exists (thumbnail)):
            print "Thumbnail exists " + thumbnail
        else:
            if (not self.__request_thumbnail (filename)):
                print "Failed doing thumbnail. Probably album art is not an image!"
                os.remove (filename)
                return (None, None)
            
        return (filename, thumbnail)

    def __last_fm (self, artist, album):

        if (not libxml_available):
            return None
        
        if (not album or len (album) < 1):
            return None
        
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

    def __msn_images (self, artist, album):

        good_artist = self.__clean_string_for_search (artist)
        good_album = self.__clean_string_for_search (album)

        if (good_album and good_artist):
            full_try = BASE_MSN + good_album + "+" + good_artist + MSN_MEDIUM + MSN_SQUARE
            print "Searching (album + artist): %s" % (full_try)
            result = self.__get_url (full_try)
            if (result):
                return self.__get_first_url_from_msn_results_page (result)

        if (album):
            if (album.lower ().find ("greatest hit") != -1):
                print "Ignoring '%s': too generic" % (album)
                pass
            else:
                album_try = BASE_MSN + good_album + MSN_MEDIUM + MSN_SQUARE
                print "Searching (album): %s" % (album_try)
                result = self.__get_url (album_try)
                if (result):
                    return self.__get_first_url_from_msn_results_page (result)

        if (artist):
            artist_try = BASE_MSN + good_artist + "+CD+music"  + MSN_SMALL + MSN_SQUARE + MSN_PHOTO
            print "Searching (artist CD): %s" % (artist_try)
            result = self.__get_url (artist_try)
            if (result):
                return self.__get_first_url_from_msn_results_page (result)
            
        return None


    def __get_first_url_from_msn_results_page (self, page):

        current_option = None
        starting_at = 0
        security_limit = 20

        while (security_limit > 0):
            # Iterate until find a jpeg
            start = page.find ("furl=", starting_at)
            if (start == -1):
                return None
            end = page.find ("\"", start + len ("furl="))
            current_option = page [start + len ("furl="): end].replace ("amp;", "")
            if (current_option.lower().endswith (".jpg") or
                current_option.lower().endswith (".jpeg")):
                return current_option
            starting_at = end
            security_limit -= 1
        return None
            
        

    def __clean_string_for_search (self, text):
        if (not text or len (text) < 1):
            return None
            
        bad_stuff = "_:?\\-~"
        clean = text
        for c in bad_stuff:
            clean = clean.replace (c, " ")

        clean.replace ("/", "%2F")
        clean = clean.replace (" CD1", "").replace(" CD2", "")
        return urllib.quote(clean)

    def __save_content_into_file (self, content, filename):
        output = open (filename, 'w')
        output.write (content)
        output.close ()
        
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
        return self.thumbnailer.Queue ([uri], ["image/jpeg"], dbus.UInt32 (handle))
            


class LocalThumbnailer:
    def __init__ (self):
        self.THUMBNAIL_SIZE = (124,124)

    def Queue (self, uris, mimes, handle):
        for i in range (0, len(uris)):
            uri = uris[i]
            fullCoverFileName = uri[7:]
            if (os.path.exists (fullCoverFileName)):
                thumbFile = get_thumb_filename_for_path (fullCoverFileName)
                try:
                    image = Image.open (fullCoverFileName)
                    image = image.resize (self.THUMBNAIL_SIZE, Image.ANTIALIAS )
                    image.save( thumbFile, "JPEG" )
                    print "Thumbnail: " + thumbFile
                except IOError, e:
                    print e
                    return False
        return True
            


if __name__ == "__main__":
    import sys
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option ("-p", "--print", dest="print_paths",
                       action="store_true", default=True,
                       help="Print the destination paths")
    parser.add_option ("-r", "--retrieve", dest="retrieve",
                       action="store_true", default=False,
                       help="Try to retrieve the online content")
    parser.add_option ("-a", "--artist", dest="artist", type="string",
                       help="ARTIST to look for", metavar="ARTIST")
    parser.add_option ("-b", "--album", dest="album", type="string",
                       help="ALBUM to look for", metavar="ALBUM")

    (options, args) = parser.parse_args ()
    print options
    if (not options.artist and not options.album):
        parser.print_help ()
        sys.exit (-1)
        
    if options.print_paths and not options.retrieve:
        print "Album art:", getCoverArtFileName (options.album)
        print "Thumbnail:", getCoverArtThumbFileName (options.album)

        
    if options.retrieve:
        maa = MussorgskyAlbumArt ()
        maa.get_album_art (options.artist, options.album)
