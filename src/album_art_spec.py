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

def getCoverArtFileName (album):
    """Returns the cover art's filename that is formed from the album name."""
    album = unicode (album)
    albumString=dropInsideContent(album,"[","]" )
    albumString=dropInsideContent(albumString,"{","}" )
    albumString=dropInsideContent(albumString,"(",")" )
    for special_char in '()_{}[]!@#$^&*+=|\\/"\'?<>~`':
        albumString=albumString.replace(special_char, "")
    albumString=dropInsideContent(albumString,"{","}" )
    albumString=albumString.lower()
    albumString=string.replace(albumString,"\t"," ")
    albumString=" ".join (albumString.split ())
    try:
        albumString=unicodedata.normalize('NFKD',albumString).encode("utf8")
        albumString=albumString.encode()
    except:
        try:
            albumString=albumString.encode('latin-1', 'ignore')
            albumString=unicodedata.normalize('NFKD',albumString).encode("ascii")
            albumString=str(albumString)
            print albumString
        except Exception, e:
            albumString=str(albumString)
            print "DEBUG: Using plain string"
    if len(albumString)==0: albumString=" "
     
    albumMD5=md5.new(albumString).hexdigest()    
    emptyMD5=md5.new(" ").hexdigest()
    albumArt=COVERS_LOCATION + "album-" + emptyMD5 + "-" + albumMD5 + ".jpeg"
    return albumArt


def getCoverArtThumbFileName (album):
    artFile = getCoverArtFileName(album)
    if not artFile.startswith ("file://"):
        artFile = "file://" + artFile
    thumbFile = THUMBS_LOCATION + md5.new(artFile).hexdigest() + ".jpeg"
    return thumbFile

def get_thumb_filename_for_path (path):
    if not path.startswith ("file://"):
        path = "file://" + path
    thumbnail = THUMBS_LOCATION + md5.new (path).hexdigest () + ".jpeg"
    return thumbnail

def dropInsideContent(s, startMarker, endMarker):
    startPos=s.find(startMarker)
    endPos=s.find(endMarker)
    if startPos>0 and endPos>0 and endPos>startPos:
            return s[0:startPos]+s[endPos+1:len(s)]
    return s

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
