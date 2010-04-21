import os
import md5
import unicodedata
import string

COVERS_LOCATION = os.getenv ("HOME") + "/.cache/media-art/"
THUMBS_LOCATION = os.getenv ("HOME") + "/.thumbnails/cropped/"

# Hardcoded locations for testing in scratchbox 
#
#COVERS_LOCATION = "/home/user/.cache/media-art/"
#THUMBS_LOCATION = "/home/user/.thumbnails/cropped/"

# Do this only once...
import ctypes
clib = ctypes.CDLL ("libhildonthumbnail.so.0")

album_art_func = clib.hildon_albumart_get_path
album_art_func.restype = ctypes.c_char_p

def getCoverArtFileName (album):
    return album_art_func (None, album, "album")
    
def getCoverArtThumbFileName (album):
    artFile = getCoverArtFileName (album)
    if not artFile.startswith ("file://"):
        artFile = "file://" + artFile
    thumbFile = THUMBS_LOCATION + md5.new (artFile).hexdigest() + ".jpeg"
    return thumbFile

def get_thumb_filename_for_path (path):
    if not path.startswith ("file://"):
        path = "file://" + path
    thumbnail = THUMBS_LOCATION + md5.new (path).hexdigest () + ".jpeg"
    return thumbnail

if __name__ == "__main__":
    import sys
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option ("-a", "--artist", dest="artist", type="string",
                       help="ARTIST to look for", metavar="ARTIST")
    parser.add_option ("-b", "--album", dest="album", type="string",
                       help="ALBUM to look for", metavar="ALBUM")

    (options, args) = parser.parse_args ()
    print options
    if (not options.artist and not options.album):
        parser.print_help ()
        sys.exit (-1)

    print "Album art        :", getCoverArtFileName (options.album)
    print "Thumbnail (album):", getCoverArtThumbFileName (options.album)
    print "Thumbnail (path) :", get_thumb_filename_for_path (getCoverArtFileName(options.album))
