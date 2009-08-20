# This file came originally from
# Picard, the next-generation MusicBrainz tagger
#   This specific file didn't contain a Copyright notice
#   but the whole project is under GPL 2 or later
#
# Original project URL:
# https://code.launchpad.net/picard
#
# Original file URL:
# http://bazaar.launchpad.net/~garyvdm/picard/keep_copy/annotate/head%3A/picard/parsefilename.py
#
# Modifications by Ivan Frade <ivan.frade@gmail.com>
#   Added new regular expresion
#   Added function to clean a little bit the filename before processing
#

# ParseFilename - Infer metadata from filepath
# Copyright (C) 2008?, Picard 
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
import re

_patterns = [
    # AlbumArtist/1999 - Album/01-TrackTitle.ext
    re.compile(r"(?:.*(/|\\))?(?P<artist>.*)(/|\\)((?P<year>\d{4}) - )(?P<album>.*)(/|\\)(?P<tracknum>\d{2})-(?P<title>.*)\.(?:\w{2,5})$"),
    # AlbumArtist - Album/01 - TrackTitle.ext
    re.compile(r"(?:.*(/|\\))?(?P<artist>.*) - (?P<album>.*)(/|\\)(?P<tracknum>\d{2}) - (?P<title>.*)\.(?:\w{2,5})$"),
    # AlbumArtist - Album/01-TrackTitle.ext
    re.compile(r"(?:.*(/|\\))?(?P<artist>.*) - (?P<album>.*)(/|\\)(?P<tracknum>\d{2})-(?P<title>.*)\.(?:\w{2,5})$"),
    # AlbumArtist - Album/01. TrackTitle.ext
    re.compile(r"(?:.*(/|\\))?(?P<artist>.*) - (?P<album>.*)(/|\\)(?P<tracknum>\d{2})\. (?P<title>.*)\.(?:\w{2,5})$"),
    # AlbumArtist - Album/01 TrackTitle.ext
    re.compile(r"(?:.*(/|\\))?(?P<artist>.*) - (?P<album>.*)(/|\\)(?P<tracknum>\d{2}) (?P<title>.*)\.(?:\w{2,5})$"),
    # AlbumArtist - Album/01_Artist_-_TrackTitle.ext
    re.compile(r"(?:.*(/|\\))?(?P<albumartist>.*) - (?P<album>.*)(/|\\)(?P<tracknum>\d{2})_(?P<artist>.*)_-_(?P<title>.*)\.(?:\w{2,5})$"),
    # Album/Artist - Album - 01 - TrackTitle.ext
    re.compile(r"(?:.*(/|\\))?(?P<artist>.*)(/|\\)(?P=artist) - (?P<album>.*) - (?P<tracknum>\d{2}) - (?P<title>.*)\.(?:\w{2,5})$"),
    # AlbumArtist/Album/Artist - 01 - TrackTitle.ext
    re.compile(r"(?:.*(/|\\))?(?P<albumartist>.*)(/|\\)(?P<album>.*)(/|\\)(?P<artist>.*) - (?P<tracknum>\d{2}) - (?P<title>.*)\.(?:\w{2,5})$"),
    # AlbumArtist/Album/01. Artist - TrackTitle.ext
    re.compile(r"(?:.*(/|\\))?(?P<albumartist>.*)(/|\\)(?P<album>.*)(/|\\)(?P<tracknum>\d{2})\. (?P<artist>.*) - (?P<title>.*)\.(?:\w{2,5})$"),
    # AlbumArtist/Album/01 - Artist - TrackTitle.ext
    re.compile(r"(?:.*(/|\\))?(?P<albumartist>.*)(/|\\)(?P<album>.*)(/|\\)(?P<tracknum>\d{2}) - (?P<artist>.*) - (?P<title>.*)\.(?:\w{2,5})$"),
    # AlbumArtist/Album/01 - TrackTitle.ext
    re.compile(r"(?:.*(/|\\))?(?P<artist>.*)(/|\\)(?P<album>.*)(/|\\)(?P<tracknum>\d{2}) - (?P<title>.*)\.(?:\w{2,5})$"),
    # AlbumArtist/Album/01. TrackTitle.ext
    re.compile(r"(?:.*(/|\\))?(?P<artist>.*)(/|\\)(?P<album>.*)(/|\\)(?P<tracknum>\d{2})\. (?P<title>.*)\.(?:\w{2,5})$"),
    # AlbumArtist/Album/01 TrackTitle.ext
    re.compile(r"(?:.*(/|\\))?(?P<artist>.*)(/|\\)(?P<album>.*)(/|\\)(?P<tracknum>\d{2}) (?P<title>.*)\.(?:\w{2,5})$"),
    # AlbumArtist/Album/Album-01-TrackTitle.ext
    re.compile(r"(?:.*(/|\\))?(?P<albumartist>.*)(/|\\)(?P<album>.*)(/|\\)(?P=album)-(?P<tracknum>\d{2})-(?P<artist>.*)-(?P<title>.*)\.(?:\w{2,5})$"),
    # AlbumArtist/Album/Album-01-Artist-TrackTitle.ext
    re.compile(r"(?:.*(/|\\))?(?P<artist>.*)(/|\\)(?P<album>.*)(/|\\)(?P=album)-(?P<tracknum>\d{2})-(?P<title>.*)\.(?:\w{2,5})$"),
    # AlbumArtist/Album/Artist-01-TrackTitle.ext
    re.compile(r"(?:.*(/|\\))?(?P<albumartist>.*)(/|\\)(?P<album>.*)(/|\\)(?P<artist>.*)-(?P<tracknum>\d{2})-(?P<title>.*)\.(?:\w{2,5})$"),
    # Artist/Album/TrackTitle.ext
    re.compile(r"(?:.*(/|\\))?(?P<artist>.*)(/|\\)(?P<album>.*)(/|\\)(?P<title>.*)\.(?:\w{2,5})$"),
]

def parseFileName (filename):
    for pattern in _patterns:
        match = pattern.match(filename)
        if match:
            metadata = {}
            #print "Match with pattern ", counter
            metadata["artist"] = match.group("artist")
            metadata["title"] = match.group("title")
            metadata["album"] = match.group("album")
            return metadata
    return None
        
def clean (filename):
    """
    Some brute force normalization
    """
    f = re.sub (r"\[.*\d\]", r"", filename) # [Disc 1]
    f = re.sub (r"[Dd]isc \d", r"", f)  # Disc 1
    f = re.sub (r"-?[Cc][Dd]\ ?\d", r"", f) # CD1, CD 1 <- Maybe useful!
    f = re.sub (r"([a-z0-9])([A-Z])([a-z0-9])", r"\1 \2\3", f) # PinkFloyd -> Pink Floyd
    return f.replace ("_", " ").replace ("["," ").replace ("]", " ").replace ("-", " ").replace ("  ", " ")


def crawl (path):
    """
    Test function. Crawl a directory trying to guess the metadata from the filepath
    for all music files.
    """
    import os
    print path
    fail = 0
    ok = 0
    for (root, dirs, files) in os.walk (path):
        for f in files:
            if (f.endswith (".mp3")
                or f.endswith (".m4a")
                or f.endswith (".ogg")):
                filename = os.path.join (root, f)
                print filename
                mdata = parseFileName (clean (filename))
                if (not mdata):
                    fail += 1
                else:
                    print "  Artist: ", mdata['artist']
                    print "  Album :", mdata['album']
                    print "  Title :", mdata['title']
                    ok += 1
    print "aprox %d success out of %d" % (ok, ok+fail)
        

if __name__ == "__main__":
    crawl ("/home/ivan/Desktop")
    #crawl ("/media/IPOD/")
