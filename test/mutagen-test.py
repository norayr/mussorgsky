#  -*- coding: utf-8 -*-
import sys
import os

SRC_DIR = os.path.join(os.path.dirname(__file__), "../src")

if not SRC_DIR in sys.path:
    sys.path.insert(0, SRC_DIR)

import unittest
from mutagen_backend import MutagenBackend


import os

def verify_MP3 (filename, expected_artist, expected_title, expected_album):
    from mutagen.easyid3 import EasyID3
    audio = EasyID3 (filename)
    assert audio["artist"][0] == expected_artist
    assert audio["title"][0] == expected_title
    assert audio["album"][0] == expected_album

def verify_wma (filename, expected_artist, expected_title, expected_album):
    from mutagen.asf import ASF
    audio = ASF (filename)
    assert str(audio["Author"][0]) == expected_artist
    assert str(audio["Title"][0]) == expected_title
    assert str(audio["WM/AlbumTitle"][0]) == expected_album
        
def verify_autoguess (filename, expected_artist, expected_title, expected_album):
    from mutagen import File
    audio = File (filename)
    assert audio["artist"][0] == expected_artist
    assert audio["title"][0] == expected_title
    assert audio["album"][0] == expected_album


class MutagenWritingTest (unittest.TestCase):

    def setUp (self):
        self.writer = MutagenBackend ()

    def general_test (self, original, result, mime, verify_func = verify_autoguess):
        """
        Copy 'original' to 'result', modify metadat in 'result' and read again from there
        """
        
        out = open (result, 'w')
        out.write (open (original,'r').read ())
        out.close ()
    
        self.writer.save_metadata_on_file (result, mime,
                                           "artist_test", "title_test", "album_test")
        verify_func (result, "artist_test", "title_test", "album_test")
    
        self.writer.save_metadata_on_file (result, mime,
                                           "artist_test_2", "title_test_2", "album_2")
        verify_func (result, "artist_test_2", "title_test_2", "album_2")

        os.unlink (result)
        

    def test_FLAC (self):
        TEST_FILE = "../test-files/empty.flac"
        TEST_FILE_TO_BREAK = "../test-files/test-result.flac"
        MIME = "audio/x-flac"
        self.general_test (TEST_FILE, TEST_FILE_TO_BREAK, MIME)

    def test_OGG (self):
        TEST_FILE = "../test-files/empty.oga"
        TEST_FILE_TO_BREAK = "../test-files/test-result.oga"
        MIME = "audio/ogg"
        self.general_test (TEST_FILE, TEST_FILE_TO_BREAK, MIME)

    def test_OGG_VORBIS (self):
        TEST_FILE = "../test-files/empty-ogg-vorbis.ogg"
        TEST_FILE_TO_BREAK = "../test-files/test-result.ogg"
        MIME = "audio/ogg+vorbis"
        self.general_test (TEST_FILE, TEST_FILE_TO_BREAK, MIME)

    def test_MP3 (self):
        TEST_FILE = "../test-files/empty.mp3"
        TEST_FILE_TO_BREAK = "../test-files/test-result.mp3"
        MIME = "audio/mpeg"
        self.general_test (TEST_FILE, TEST_FILE_TO_BREAK, MIME, verify_MP3)
        

if __name__ == "__main__":
    unittest.main ()
