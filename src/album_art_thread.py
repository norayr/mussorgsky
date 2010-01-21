#!/usr/bin/env python2.5
import os
from album_art_spec import getCoverArtFileName, getCoverArtThumbFileName, get_thumb_filename_for_path
from utils import UrllibWrapper
import dbus, time
import string
import urllib

try:
    import libxml2
    libxml_available = True
except ImportError:
    libxml_available = False

try:
    import PIL
    import Image
except ImportError:
    import sys
    print "Please install python-imaging package"
    sys.exit (-1)


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


import threading
class AADownloadThread (threading.Thread):

    def __init__ (self, url, counter):
        threading.Thread.__init__ (self, target=self.grab_image, args=(url,))
        self.thumbnailer = LocalThumbnailer ()
        self.counter = counter
        self.image_path = None
        self.thumb_path = None
        self.urllib_wrapper = UrllibWrapper ()

    def grab_image (self, image_url):
        print "Working", self.counter
        image = self.urllib_wrapper.get_url (image_url)
        if (image):
            self.image_path = os.path.join (CACHE_LOCATION, "alternative-" + str(self.counter))
            self.thumb_path = os.path.join (CACHE_LOCATION, "alternative-" + str(self.counter) + "thumb")
            self.urllib_wrapper.save_content_into_file (image, self.image_path)
            self.thumbnailer.create (self.image_path, self.thumb_path)
        
    def get_result (self):
        return self.image_path, self.thumb_path



class MussorgskyAlbumArt:

    def __init__ (self):
        bus = dbus.SessionBus ()

        if (not os.path.exists (CACHE_LOCATION)):
            os.makedirs (CACHE_LOCATION)
            
        self.thumbnailer = LocalThumbnailer ()
        self.urllib_wrapper = UrllibWrapper ()

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
                content = self.urllib_wrapper.get_url (online_resource)
                if (content):
                    print "Albumart: %s " % (filename)
                    self.urllib_wrapper.save_content_into_file (content, filename)
                    album_art_available = True
                    break

        if (not album_art_available):
            return (None, None)

        if (not os.path.exists (thumbnail) or force or album_art_available):
            if (not self.__request_thumbnail (filename)):
                print "Failed doing thumbnail. Probably album art is not an image!"
                os.remove (filename)
                return (None, None)
        else:
            print "Thumbnail exists (and probably valid) " + thumbnail
            
        return (filename, thumbnail)


    def get_alternatives (self, artist, album, max_alternatives=4):
        """
        return a list of paths of possible album arts
        """
        counter = 0
        results_page = self.__msn_images (artist, album)
        threads = []
        for image_url in self.__get_url_from_msn_results_page (results_page):
            if (not image_url):
                # Some searches doesn't return anything at all!
                break

            if (counter >= max_alternatives):
                break
            
            t = AADownloadThread (image_url, counter)
            t.start ()
            threads.append (t)
            counter += 1

        for t in threads:
            t.join (5)
            if (t.isAlive ()):
                yield (None, None)
            else:
                yield t.get_result ()
            

    def save_alternative (self, artist, album, img_path, thumb_path):
        if not os.path.exists (img_path) or not os.path.exists (thumb_path):
            print "**** CRITICAL **** image in path", path, "doesn't exist!"
            return (None, None)
        
        filename = getCoverArtFileName (album)
        thumbnail = getCoverArtThumbFileName (album)

        os.rename (img_path, filename)
        os.rename (thumb_path, thumbnail)

        return (filename, thumbnail)

    def reset_alternative (self, artist, album):

        for filepath in [getCoverArtFileName (album),
                         getCoverArtThumbFileName (album)]:
            if os.path.exists (filepath):
                os.remove (filepath)

    def __msn_images (self, artist, album):

        good_artist = self.__clean_string_for_search (artist)
        good_album = self.__clean_string_for_search (album)

        if (good_album and good_artist):
            full_try = BASE_MSN + good_album + "+" + good_artist + MSN_MEDIUM + MSN_SQUARE
            print "Searching (album + artist): %s" % (full_try)
            result = self.urllib_wrapper.get_url (full_try)
            if (result and result.find ("no_results") == -1):
                return result

        if (album):
            if (album.lower ().find ("greatest hit") != -1):
                print "Ignoring '%s': too generic" % (album)
                pass
            else:
                album_try = BASE_MSN + good_album + MSN_MEDIUM + MSN_SQUARE
                print "Searching (album): %s" % (album_try)
                result = self.urllib_wrapper.get_url (album_try)
                if (result and result.find ("no_results") == -1):
                    return result
            
        if (artist):
            artist_try = BASE_MSN + good_artist + "+CD+music"  + MSN_SMALL + MSN_SQUARE + MSN_PHOTO
            print "Searching (artist CD): %s" % (artist_try)
            result = self.urllib_wrapper.get_url (artist_try)
            if (result and result.find ("no_results") == -1):
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

    def __request_thumbnail (self, filename):
        thumbFile = get_thumb_filename_for_path (filename)
        return self.thumbnailer.create (filename, thumbFile)
            


class LocalThumbnailer:
    def __init__ (self):
        self.THUMBNAIL_SIZE = (124,124)

    def create (self, fullCoverFileName, thumbFile):
        if (os.path.exists (fullCoverFileName)):
            try:
                image = Image.open (fullCoverFileName)
                image = image.resize (self.THUMBNAIL_SIZE, Image.ANTIALIAS )
                image.save (thumbFile, "JPEG")
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
        start = time.time ()
        maa = MussorgskyAlbumArt ()
        for (img, thumb) in  maa.get_alternatives (options.artist, options.album, 5):
            print img
            print thumb
        end = time.time ()
        print end - start
