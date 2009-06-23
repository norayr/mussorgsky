#!/usr/bin/env python2.5
import mutagen

class MutagenBackend ():

    def __init__ (self):
        self.formats = {"audio/mpeg": self.__id3_writer ,
                        "audio/x-ms-wma" : self.__wma_writer }
    def get_supported_mimes (self):
        return self.formats.keys ()

    def save_metadata_on_file (self, filename, mime, artist, title, album):
        if (self.formats.has_key (mime)):
            return self.formats[mime] (filename, artist, title, album)
        else:
            return False

    def __id3_writer (self, filename, artist, title, album):
        from mutagen.mp3 import MP3
        from mutagen.easyid3 import EasyID3
        audio = MP3 (filename, ID3=EasyID3)
        try:
            audio.add_tags (ID3=EasyID3)
            print "Adding tags to %s" % (filename)
        except mutagen.id3.error:
            # It already has tags!
            pass

        audio["artist"] = artist
        audio["title"] = title
        audio["album"] = album
        try:
            audio.save()
            return True
        except:
            return False

    def __wma_writer (self, filename, artist, title, album):
        from mutagen.asf import ASF
        audio = ASF (filename)
        audio["Author"] = artist
        audio["Title"] = title
        audio["WM/AlbumTitle"] = album
        try:
            audio.save()
            return True
        except:
            return False




if __name__ == "__main__":

    # use id3lib for verification
    import pyid3lib

    def verify (filename, expected_artist, expected_title, expected_album):
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
        

    writer = MutagenBackend ()

    TEST_FILE = "test-files/strange.mp3"
    TEST_FILE_TO_BREAK = "test-files/strange-fixed.mp3"

    out = open (TEST_FILE_TO_BREAK, 'w')
    out.write (open (TEST_FILE,'r').read ())
    out.close ()
    
    writer.save_metadata_on_file (TEST_FILE_TO_BREAK, "audio/mpeg",
                                  "artist_test", "title_test", "album_test")
    verify (TEST_FILE_TO_BREAK, "artist_test", "title_test", "album_test")
    
    writer.save_metadata_on_file (TEST_FILE_TO_BREAK, "audio/mpeg",
                                  "artist_test_2", "title_test_2", "album_2")
    verify (TEST_FILE_TO_BREAK, "artist_test_2", "title_test_2", "album_2")



    READONLY_FILE = "test-files/no-write.mp3"
    assert not writer.save_metadata_on_file (READONLY_FILE, "audio/mpeg",
                                             "artist_test", "title_test", "album_test")


    WMA_FILE = "test-files/hooverphonic.wma"
    assert writer.save_metadata_on_file (WMA_FILE, "audio/x-ms-wma",
                                  "artist_wma", "title_wma", "album_wma")
    verify_wma (WMA_FILE, "artist_wma", "title_wma", "album_wma")

    assert writer.save_metadata_on_file (WMA_FILE, "audio/x-ms-wma",
                                  "artist_wma_2", "title_wma_2", "album_wma_2")
    verify_wma (WMA_FILE, "artist_wma_2", "title_wma_2", "album_wma_2")
