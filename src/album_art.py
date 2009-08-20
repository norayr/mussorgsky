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


# Set socket timeout
import socket
import urllib2

timeout = 5
socket.setdefaulttimeout(timeout)

LASTFM_APIKEY = "1e1d53528c86406757a6887addef0ace"
BASE_LASTFM = "http://ws.audioscrobbler.com/2.0/?method=album.getinfo"


BASE_MSN = "http://www.bing.com/images/search?q="
MSN_MEDIUM = "+filterui:imagesize-medium"
MSN_SMALL = "+filterui:imagesize-medium"
MSN_SQUARE = "+filterui:aspect-square"
MSN_PHOTO = "+filterui:photo-graphics"

CACHE_LOCATION = os.path.join (os.getenv ("HOME"), ".cache", "mussorgsky")
# LastFM:
# http://www.lastfm.es/api/show?service=290
#
class MussorgskyAlbumArt:

    def __init__ (self):
        bus = dbus.SessionBus ()
        handle = time.time()

        if (not os.path.exists (CACHE_LOCATION)):
            os.makedirs (CACHE_LOCATION)
            
        if (pil_available):
            self.thumbnailer = LocalThumbnailer ()
        else:
            try:
                self.thumbnailer = bus.get_object ('org.freedesktop.thumbnailer',
                                                   '/org/freedesktop/thumbnailer/Generic')
            except dbus.exceptions.DBusException:
                print "No thumbnailer available"
                self.thumbnailer = None

    def get_album_art (self, artist, album, force=False):
        """
        Return a tuple (album_art, thumbnail_album_art)
        """
        filename = getCoverArtFileName (album)
        thumbnail = getCoverArtThumbFileName (album)

        album_art_available = False
        if (os.path.exists (filename) and not force):
            print "Album art already there " + filename
            album_art_available = True
        else:
            results_page = self.__msn_images (artist, album)
            for online_resource in self.__get_url_from_msn_results_page (results_page):
                print "Choosed:", online_resource
                content = self.__get_url (online_resource)
                if (content):
                    print "Albumart: %s " % (filename)
                    self.__save_content_into_file (content, filename)
                    album_art_available = True
                    break

        if (not album_art_available):
            return (None, None)

        if (os.path.exists (thumbnail) and not force):
            print "Thumbnail exists " + thumbnail
        else:
            if (not self.__request_thumbnail (filename)):
                print "Failed doing thumbnail. Probably album art is not an image!"
                os.remove (filename)
                return (None, None)
            
        return (filename, thumbnail)


    def get_alternatives (self, artist, album, no_alternatives):
        """
        return a list of paths of possible album arts
        """
        results_page = self.__msn_images (artist, album)
        valid_images = []
        for image_url in self.__get_url_from_msn_results_page (results_page):
            image = self.__get_url (image_url)
            if (image):
                image_path = os.path.join (CACHE_LOCATION, "alternative-" + str(len(valid_images)))
                self.__save_content_into_file (image, image_path)
                valid_images.append (image_path)
                if (len (valid_images) > no_alternatives):
                    return valid_images
        return valid_images

    def save_alternative (self, artist, album, path):
        if (not os.path.exists (path)):
            print "**** CRITICAL **** image in path", path, "doesn't exist!"

        filename = getCoverArtFileName (album)
        thumbnail = getCoverArtThumbFileName (album)

        os.rename (path, filename)
        if (not self.__request_thumbnail (filename)):
            print "Something wrong creating the thumbnail!"
        

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
            return result

        if (album):
            if (album.lower ().find ("greatest hit") != -1):
                print "Ignoring '%s': too generic" % (album)
                pass
            else:
                album_try = BASE_MSN + good_album + MSN_MEDIUM + MSN_SQUARE
                print "Searching (album): %s" % (album_try)
                result = self.__get_url (album_try)
                return result
            
        if (artist):
            artist_try = BASE_MSN + good_artist + "+CD+music"  + MSN_SMALL + MSN_SQUARE + MSN_PHOTO
            print "Searching (artist CD): %s" % (artist_try)
            result = self.__get_url (artist_try)
            return result
        
        return None


    def __get_url_from_msn_results_page (self, page):

        if (not page):
            return

        current_option = None
        starting_at = 0

        # 500 is just a safe limit
        for i in range (0, 500):
            # Iterate until find a jpeg
            start = page.find ("furl=", starting_at)
            if (start == -1):
                yield None
            end = page.find ("\"", start + len ("furl="))
            current_option = page [start + len ("furl="): end].replace ("amp;", "")
            if (current_option.lower().endswith (".jpg") or
                current_option.lower().endswith (".jpeg")):
                yield current_option
            starting_at = end
        yield None
        

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
    parser.add_option ("-m", "--multiple", dest="multiple",
                       action="store_true", default=False,
                       help="Show more than one option")
    parser.add_option ("-a", "--artist", dest="artist", type="string",
                       help="ARTIST to look for", metavar="ARTIST")
    parser.add_option ("-b", "--album", dest="album", type="string",
                       help="ALBUM to look for", metavar="ALBUM")

    (options, args) = parser.parse_args ()
    print options
    if (not options.artist and not options.album):
        parser.print_help ()
        sys.exit (-1)

    if (options.multiple and options.retrieve):
        print "Multiple and retrieve are incompatible"
        parser.print_help ()
        sys.exit (-1)
        
    if options.print_paths and not options.retrieve:
        print "Album art:", getCoverArtFileName (options.album)
        print "Thumbnail:", getCoverArtThumbFileName (options.album)

    if options.retrieve:
        maa = MussorgskyAlbumArt ()
        maa.get_album_art (options.artist, options.album)

    if options.multiple:
        maa = MussorgskyAlbumArt ()
        alt = maa.get_alternatives (options.artist, options.album, 5)
        for a in alt:
            print a
