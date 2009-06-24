#!/usr/bin/env python2.5
import hildon
import gtk
from mutagen_backend import MutagenBackend
from player_backend import MediaPlayer

# Fields in the tuple!
FILE_URI = 0
ARTIST_KEY = 2
TITLE_KEY = 3
ALBUM_KEY = 4
MIME_KEY = 5

class MussorgskyEditPanel (hildon.StackableWindow):

    def __init__ (self, songs_list=None, albums_list=None, artists_list=None):
        hildon.StackableWindow.__init__ (self)
        self.set_title ("Edit")
        self.set_border_width (12)
        self.writer = MutagenBackend ()
        self.player = MediaPlayer ()
        self.albums_list = albums_list
        self.artists_list = artists_list
        self.add (self.__create_view ())
        if (songs_list):
            self.set_songs_list (songs_list)
        self.banner = None

        self.artists_selector = None
        self.artists_dialog = None

        self.albums_selector = None
        self.albums_dialog = None
        
    def set_songs_list (self, songs_list):
            self.songs_list = songs_list
            self.set_data_in_view (songs_list [0])
            self.song_counter = 0

    def press_back_cb (self, widget):
        if (self.player.is_playing ()):
            self.player.stop ()

        if (self.banner and self.banner.get_property("visible")):
            self.banner.destroy ()

        if self.__is_view_dirty ():
            print "Modified data. Save!"
            self.save_metadata ()
            
        if (self.song_counter > 0):
            self.song_counter -= 1
            self.set_data_in_view (self.songs_list [self.song_counter])

    def press_next_cb (self, widget):
        if (self.player.is_playing ()):
            self.player.stop ()

        if (self.banner and self.banner.get_property("visible")):
            self.banner.destroy ()

        if self.__is_view_dirty ():
            print "Modified data. Save!"
            self.save_metadata ()

        if (self.song_counter < len (self.songs_list) -1):
            self.song_counter += 1
            self.set_data_in_view (self.songs_list [self.song_counter])
        else:
            self.destroy ()

    def save_metadata (self):
        # Save the data in the online model to show the appropiate data
        # in the UI while tracker process the update.
        song = self.songs_list [self.song_counter]

        new_song = (song[FILE_URI], song[1],
                    self.artist_entry.get_text (),
                    self.title_entry.get_text (),
                    self.album_entry.get_text (),
                    song[MIME_KEY])
        self.songs_list [self.song_counter] = new_song
        try:
            self.writer.save_metadata_on_file (new_song[FILE_URI],
                                               new_song[MIME_KEY],
                                               self.artist_entry.get_text (),
                                               self.title_entry.get_text (),
                                               self.album_entry.get_text ())
        except IOError, e:
            # This error in case of tracker returning unexistent files.
            # Uhm.... for instance after removing a memory card we are editing!
            dialog = gtk.MessageDialog (self,
                                        gtk.DIALOG_DESTROY_WITH_PARENT,
                                        gtk.MESSAGE_ERROR,
                                        gtk.BUTTONS_CLOSE,
                                        "%s" % str(e));
            dialog.run ()

        

    def __is_view_dirty (self):
        """
        True if the data has been modified in the widgets
        """
        song = self.songs_list [self.song_counter]

        return not (self.filename_data.get_text() == song[FILE_URI] and
                    self.artist_entry.get_text () == song[ARTIST_KEY] and
                    self.title_entry.get_text () == song[TITLE_KEY] and
                    self.album_entry.get_text () == song[ALBUM_KEY] )
        

    def __create_view (self):
        view_vbox = gtk.VBox (homogeneous=False, spacing = 12)

        filename_row = gtk.HBox ()
        filename_label = gtk.Label ("Filename:")
        filename_row.pack_start (filename_label, expand=False, padding=12);
        self.filename_data = gtk.Label ("")
        filename_row.pack_start (self.filename_data, expand=True)

        #play_button = gtk.Button (stock=gtk.STOCK_MEDIA_PLAY)
        play_button = hildon.Button (hildon.BUTTON_STYLE_NORMAL, hildon.BUTTON_ARRANGEMENT_HORIZONTAL)
        img = gtk.image_new_from_stock (gtk.STOCK_MEDIA_PLAY, gtk.ICON_SIZE_BUTTON)
        play_button.set_image (img)
        play_button.connect ("clicked", self.clicked_play)
        filename_row.pack_start (play_button, expand=False, fill=False)
        view_vbox.pack_start (filename_row, expand=False);

        central_panel = gtk.HBox (spacing=12)

        table = gtk.Table (3, 2, False)
        table.set_col_spacings (12)
        table.set_row_spacings (12)

        central_panel.pack_start (table)
        view_vbox.pack_start (central_panel, expand=True, fill=True)

        # Artist row
        button_artist = gtk.Button ("Artist:")
        if (not self.artists_list):
            button_artist.set_sensitive (False)
        button_artist.connect ("clicked", self.artist_selection_cb)
        table.attach (button_artist, 0, 1, 0, 1, 0, gtk.FILL|gtk.EXPAND)
        self.artist_entry = gtk.Entry()
        table.attach (self.artist_entry, 1, 2, 0, 1)

        # Title row
        label_title = gtk.Label ("Title:")
        table.attach (label_title, 0, 1, 1, 2, 0)
        self.title_entry = gtk.Entry()
        table.attach (self.title_entry, 1, 2, 1, 2)

        # Album row
        button_album = gtk.Button ("Album:")
        if (not self.albums_list):
            button_album.set_sensitive (False)
        button_album.connect ("clicked", self.album_selection_cb)
        table.attach (button_album, 0, 1, 2, 3, 0)
        self.album_entry = gtk.Entry()
        table.attach (self.album_entry, 1, 2, 2, 3)

        # Album art space
        album_button = gtk.Button ()
        self.album_art = gtk.Image ()
        self.album_art.set_size_request (124, 124)
        album_button.add (self.album_art)
        album_button.connect ("clicked", self.clicked_album_art)
        central_panel.pack_start (album_button, expand=False, fill=False)
        
        # Buttons row
        button_box = gtk.HButtonBox ()
        button_box.set_layout (gtk.BUTTONBOX_END)

        back_button = hildon.Button (hildon.BUTTON_STYLE_NORMAL, hildon.BUTTON_ARRANGEMENT_HORIZONTAL)
        img = gtk.image_new_from_stock (gtk.STOCK_GO_BACK, gtk.ICON_SIZE_BUTTON)
        back_button.set_image (img)
        back_button.connect ("clicked", self.press_back_cb)
        button_box.pack_start (back_button, expand=True, fill=True, padding=6)
        
        next_button = hildon.Button (hildon.BUTTON_STYLE_NORMAL, hildon.BUTTON_ARRANGEMENT_HORIZONTAL)
        img = gtk.image_new_from_stock (gtk.STOCK_GO_FORWARD, gtk.ICON_SIZE_BUTTON)
        next_button.set_image (img)
        next_button.connect ("clicked", self.press_next_cb)
        button_box.pack_start (next_button, expand=True, fill=True, padding=6)
        
        view_vbox.pack_start (button_box, expand=False, fill=True, padding=6)
        
        return view_vbox


    def set_data_in_view (self, song):
        """
        Place in the screen the song information.
        Song is a tuple like (filename, 'Music', title, artist, album, mime)
        """
        assert len (song) == 6
        self.filename_data.set_text (song[FILE_URI])
        self.artist_entry.set_text (song[ARTIST_KEY])
        self.title_entry.set_text (song[TITLE_KEY])
        self.album_entry.set_text (song[ALBUM_KEY])

        self.album_art.set_from_file ("/home/ivan/cover-sample.jpeg")

        if (not song[MIME_KEY] in self.writer.get_supported_mimes ()):
            print "show notification"
            self.banner = hildon.Banner ()
            self.banner.set_text ("Unsupported format (%s)" % song[MIME_KEY])
            self.banner.show_all ()

    def clicked_play (self, widget):
        if (self.player.is_playing ()):
            self.player.stop ()
        else:
            song = self.songs_list [self.song_counter]
            self.player.play ("file://" + song[FILE_URI])

    def clicked_album_art (self, widget):
        print "implement me, please"

    def album_selection_cb (self, widget):
        if (not self.albums_selector):
            self.albums_selector = hildon.hildon_touch_selector_new_text ()
            for album in self.albums_list :
                self.albums_selector.append_text (album[0])

        if (not self.albums_dialog):
            self.albums_dialog = hildon.PickerDialog (self)
            self.albums_dialog.set_title ("Choose album...")
            self.albums_dialog.set_selector (self.albums_selector)

        response = self.albums_dialog.run ()
        if (response == gtk.RESPONSE_OK):
            print "Ok (%s)" % (self.albums_selector.get_current_text ())
            self.album_entry.set_text (self.albums_selector.get_current_text ())
        self.albums_dialog.hide ()

    def artist_selection_cb (self, widget):
        if (not self.artists_selector):
            self.artists_selector = hildon.hildon_touch_selector_new_text ()
            for artist in self.artists_list :
                self.artists_selector.append_text (artist[0])
                
        if (not self.artists_dialog):
            self.artists_dialog = hildon.PickerDialog (self)
            self.artists_dialog.set_title ("Choose artist...")
            self.artists_dialog.set_selector (self.artists_selector)

        response = self.artists_dialog.run ()

        if (response == gtk.RESPONSE_OK):
            print "Ok (%s)" % (self.artists_selector.get_current_text ())
            self.artist_entry.set_text (str(self.artists_selector.get_current_text ()))
        self.artists_dialog.hide ()

# Testing porpuses
if __name__ == "__main__":

    TEST_DATA = [("/a/b/c/d.mp3", "Music", "", "title", "album", "audio/mpeg"),
                 ("/home/user/mufix/dejame.mp3", "Music", "", "title", "album 2", "a/b"),
                 ("/home/user/mufix/3.mp2", "Music", "", "titlex", "album 3", "audio/mpeg")]
    ALBUMS = [["Album %d" % i] for i in range (0, 10)]
    ARTISTS = [["Artist %d" % i] for i in range (0, 10)]
    window = MussorgskyEditPanel (TEST_DATA, ALBUMS, ARTISTS)
    window.connect ("destroy", gtk.main_quit)
    window.show_all ()
    gtk.main ()
