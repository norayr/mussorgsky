import os
import md5
import unicodedata
import string

COVERS_LOCATION = os.getenv ("HOME") + "/.cache/media-art/"
THUMBS_LOCATION = os.getenv ("HOME") + "/.thumbnails/cropped/"

def getCoverArtFileName (album):
    """Returns the cover art's filename that is formed from the album name."""
    album = unicode (album)
    albumString=dropInsideContent(album,"[","]" )
    albumString=dropInsideContent(albumString,"{","}" )
    albumString=dropInsideContent(albumString,"(",")" )    
    albumString=albumString.strip('()_{}[]!@#$^&*+=|\\/"\'?<>~`')
    albumString=albumString.lstrip(' ')
    albumString=albumString.rstrip(' ')
    albumString=dropInsideContent(albumString,"{","}" )
    albumString=albumString.lower()
    albumString=string.replace(albumString,"\t"," ")
    albumString=string.replace(albumString,"  "," ")    
    
    try:
        albumString=unicodedata.normalize('NFKD',albumString).encode()
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
    thumbFile = THUMBS_LOCATION + md5.new(artFile).hexdigest()+".jpeg"
    return thumbFile

def get_thumb_filename_for_path (path):
    thumbnail = THUMBS_LOCATION + md5.new (path).hexdigest () + ".jpeg"
    return thumbnail

def dropInsideContent(s, startMarker, endMarker):
    startPos=s.find(startMarker)
    endPos=s.find(endMarker)
    if startPos>0 and endPos>0 and endPos>startPos:
            return s[0:startPos]+s[endPos+1:len(s)]
    return s

if __name__ == "__main__":

    print "album art: %s" % (getCoverArtFileName (unicode("Absolution")))
    print "thumbnail: %s" % (getCoverArtThumbFileName (u"Absolution"))
