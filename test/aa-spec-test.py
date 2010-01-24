#  -*- coding: utf-8 -*-
import sys
import os

SRC_DIR = os.path.join(os.path.dirname(__file__), "../src")

if not SRC_DIR in sys.path:
    sys.path.insert(0, SRC_DIR)
from album_art_spec import getCoverArtFileName
from album_art_spec import getCoverArtThumbFileName
from album_art_spec import get_thumb_filename_for_path


MAEMO = "/home/ivan/.cache/media-art/album-7215ee9c7d9dc229d2921a40e899ec5f-"


#
# This MD5 come from the C library used by MAFW
TESTS = [("Absolution", MAEMO + "854b819e796f656947340d8110d13c31.jpeg"),
         ("Blue & sentimental", MAEMO + "0f6877d9eeb9355ce809eff120dbec11.jpeg"),
         ("L'orient est rouge", MAEMO + "d570b1a382401ddd5fe31bec72a9fd1b.jpeg"),
         ("Björk", MAEMO + "39e89a9ca4ab8d6214b240446aeb5cd1.jpeg")]

for (album, expected_md5) in TESTS:

    cover_art = getCoverArtFileName (album)
    if cover_art != expected_md5:
        print "Error album '%s'" % (album)
        print " Expected: ...%s" % (expected_md5[len(MAEMO)-1:])
        print " Obtained: ...%s" % (cover_art[len(MAEMO)-1:])
    else:
        print "Pass  ('%s')" % (album)
