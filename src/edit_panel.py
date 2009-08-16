#!/usr/bin/env python2.5
import hildon
import gtk, gobject
from mutagen_backend import MutagenBackend
from player_backend import MediaPlayer
import album_art_spec
from album_art import MussorgskyAlbumArt
import os

# Fields in the tuple!
FILE_URI = 0
ARTIST_KEY = 2
TITLE_KEY = 3
ALBUM_KEY = 4
MIME_KEY = 5

class MussorgskyEditPanel (hildon.StackableWindow):

    def __init__ (self, songs_list=None, albums_list=None, artists_list=None):
        hildon.StackableWindow.__init__ (self)
        self.set_border_width (12)
        self.song_counter = 0
        self.album_callback_id = -1
        self.album_change_handler = -1
        self.artist_change_handler = -1
        self.writer = MutagenBackend ()
        self.player = MediaPlayer ()
        self.album_art_retriever = MussorgskyAlbumArt ()
        self.albums_list = [a [0] for a in albums_list]
        self.artists_list = [a [0] for a in artists_list]
        self.add (self.__create_view ())
        if (songs_list):
            self.set_songs_list (songs_list)
        self.update_title ()
        self.banner = None

    def update_title (self):
        self.set_title ("Edit (%d/%d)" % (self.song_counter+1, len (self.songs_list)))

        
    def set_songs_list (self, songs_list):
        if (songs_list and len (songs_list) > 0):
            self.songs_list = songs_list
            self.set_data_in_view (songs_list [0])
            self.song_counter = 0

    def press_back_cb (self, widget):
        if (self.player.is_playing ()):
            self.player.stop ()

        if (self.banner and self.banner.get_property("visible")):
            self.banner.destroy ()

        if (self.album_callback_id != -1):
            gobject.source_remove (self.album_callback_id)
            self.album_callback_id = -1

        if self.__is_view_dirty ():
            print "Modified data. Save!"
            self.save_metadata ()
            
        if (self.song_counter > 0):
            self.song_counter -= 1
            self.set_data_in_view (self.songs_list [self.song_counter])
            self.update_title ()
        else:
            self.destroy ()

    def press_next_cb (self, widget):
        if (self.player.is_playing ()):
            self.player.stop ()

        if (self.banner and self.banner.get_property("visible")):
            self.banner.destroy ()

        if (self.album_callback_id != -1):
            gobject.source_remove (self.album_callback_id)
            self.album_callback_id = -1

        if self.__is_view_dirty ():
            print "Modified data. Save!"
            self.save_metadata ()

        if (self.song_counter < len (self.songs_list) -1):
            self.song_counter += 1
            self.set_data_in_view (self.songs_list [self.song_counter])
            self.update_title ()
        else:
            self.destroy ()

    def save_metadata (self):
        # Save the data in the online model to show the appropiate data
        # in the UI while tracker process the update.
        song = self.songs_list [self.song_counter]

        new_song = (song[FILE_URI], song[1],
                    self.artist_button.get_value (),
                    self.title_entry.get_text (),
                    self.album_button.get_value (),
                    song[MIME_KEY])
        self.songs_list [self.song_counter] = new_song
        try:
            self.writer.save_metadata_on_file (new_song[FILE_URI],
                                               new_song[MIME_KEY],
                                               self.artist_button.get_value (),
                                               self.title_entry.get_text (),
                                               self.album_button.get_value ())
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
                    self.artist_button.get_value () == song[ARTIST_KEY] and
                    self.title_entry.get_text () == song[TITLE_KEY] and
                    self.album_button.get_value () == song[ALBUM_KEY] )
        

    def __create_view (self):
        view_vbox = gtk.VBox (homogeneous=False, spacing = 12)

        filename_row = gtk.HBox ()
        filename_label = gtk.Label ("Filename:")
        filename_row.pack_start (filename_label, expand=False, padding=12);
        self.filename_data = gtk.Label ("")
        filename_row.pack_start (self.filename_data, expand=True)

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

        central_panel.pack_start (table, fill=True)
        view_vbox.pack_start (central_panel, expand=True, fill=True)

        # Title row
        label_title = gtk.Label ("Title:")
        table.attach (label_title, 0, 1, 0, 1, 0)
        self.title_entry = gtk.Entry()
        table.attach (self.title_entry, 1, 2, 0, 1)

        # Artist row
        artist_selector = hildon.hildon_touch_selector_new_text ()
        for a in self.artists_list:
            artist_selector.append_text (a)
        self.artist_button = hildon.PickerButton (hildon.BUTTON_STYLE_NORMAL,
                                                  hildon.BUTTON_ARRANGEMENT_HORIZONTAL)
        self.artist_button.set_title ("Artist: ")
        self.artist_button.set_selector (artist_selector)
        table.attach (self.artist_button, 0, 2, 1, 2)


        # Album row
        album_selector = hildon.hildon_touch_selector_new_text ()
        for a in self.albums_list:
            album_selector.append_text (a)
        self.album_button = hildon.PickerButton (hildon.BUTTON_STYLE_NORMAL,
                                                 hildon.BUTTON_ARRANGEMENT_HORIZONTAL)
        self.album_button.set_title ("Album: ")
        self.album_button.set_selector (album_selector)
        table.attach (self.album_button, 0, 2, 2, 3) 
        

        # Album art space
        album_art_button = gtk.Button ()
        self.album_art = gtk.Image ()
        self.album_art.set_size_request (124, 124)
        album_art_button.add (self.album_art)
        album_art_button.connect ("clicked", self.clicked_album_art)
        central_panel.pack_start (album_art_button, expand=False, fill=False)
        
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
        self.title_entry.set_text (song[TITLE_KEY])
        

        # Disconnect the value-change signal to avoid extra album art retrievals
        if (self.album_button.handler_is_connected (self.album_change_handler)):
            self.album_button.disconnect (self.album_change_handler)
            
        if (self.artist_button.handler_is_connected (self.artist_change_handler)):
            self.artist_button.disconnect (self.artist_change_handler)

        # Set values in the picker buttons
        try:
            self.artist_button.set_active (self.artists_list.index(song[ARTIST_KEY]))
        except ValueError:
            print "'%s' not in artist list!?" % (song[ARTIST_KEY])
            self.artist_button.set_value ("")
            
        try:
            self.album_button.set_active (self.albums_list.index (song[ALBUM_KEY]))
        except ValueError:
            print "'%s' is not in the album list!?" % (song[ALBUM_KEY])
            self.album_button.set_value ("")

        # Reconnect the signals!
        self.album_change_handler = self.album_button.connect ("value-changed",
                                                               self.album_selection_cb)

        self.artist_change_handler = self.artist_button.connect ("value-changed",
                                                                 self.artist_selection_cb)

        # Set the album art given the current data
        has_album = False
        if (song[ALBUM_KEY]):
            thumb = album_art_spec.getCoverArtThumbFileName (song[ALBUM_KEY])
	    print "%s -> %s" % (song[ALBUM_KEY], thumb)
            if (os.path.exists (thumb)):
                self.album_art.set_from_file (thumb)
                has_album = True
            else:
                self.album_callback_id = gobject.idle_add (self.retrieve_album_art,
                                                           song[ARTIST_KEY], song[ALBUM_KEY])
                
        if (not has_album):
            self.album_art.set_from_stock (gtk.STOCK_CDROM, gtk.ICON_SIZE_DIALOG)

        if (not song[MIME_KEY] in self.writer.get_supported_mimes ()):
            print "show notification"
            self.banner = hildon.Banner ()
            self.banner.set_text ("Unsupported format (%s)" % song[MIME_KEY])
            self.banner.show_all ()

    def retrieve_album_art (self, artist, album):
        print "trying to get the album art"
        (img, thumb) = self.album_art_retriever.get_album_art (artist, album)
        if (thumb):
            self.album_art.set_from_file (thumb)
        else:
            print "Unable to retrieve album art"

        return False
        
    def clicked_play (self, widget):
        if (self.player.is_playing ()):
            self.player.stop ()
        else:
            song = self.songs_list [self.song_counter]
            self.player.play ("file://" + song[FILE_URI])

    def clicked_album_art (self, widget):
        print "implement me, please"

    def album_selection_cb (self, widget):
        """
        On album change, add the album the local list of albums and the selector
        if it doesn't exist already. So we show the new entry in the selector next time.
        """
        song = self.songs_list [self.song_counter]
        if (not widget.get_value () in self.albums_list):
            print "Inserting ", widget.get_value ()
            widget.get_selector ().prepend_text (widget.get_value ())
            self.albums_list.insert (0, widget.get_value ())
        self.retrieve_album_art (song[ARTIST_KEY], widget.get_value ())

    def artist_selection_cb (self, widget):
        """
        On artist change, add the artist the local list of artists and the selector
        if it doesn't exist already. So we show the new entry in the selector next time
        """
        song = self.songs_list [self.song_counter]
        if (not widget.get_value () in self.artists_list):
            print "Inserting artist", widget.get_value ()
            widget.get_selector ().prepend_text (widget.get_value ())
            self.artists_list.insert (0, widget.get_value ())
    
# Testing porpuses
if __name__ == "__main__":

    TEST_DATA = [("/home/user/Music/dylan.mp3", "Music", "Bob Dylan", "Subterranean homesick blues", "Bring it all back home", "audio/mpeg"),
                 ("/home/user/mufix/a.mp3", "Music", "", "title", "Album 2", "a/b"),
    		 ("/media/mmc1/Attachments/b.m4a", "Music", "", "b", "Album 9", "audio/mpeg"),
                 ("/home/user/mufix/3.mp2", "Music", "", "titlex", "Album 3", "audio/mpeg")]
    #TEST_DATA = []
    ALBUMS = [["Album %d" % i] for i in range (0, 10)] + [["Bring it all back home"]]
    ARTISTS = [["Artist %d" % i] for i in range (0, 10)] + [["Bob Dylan"]]
    window = MussorgskyEditPanel (TEST_DATA, ALBUMS, ARTISTS)
    window.connect ("destroy", gtk.main_quit)
    window.show_all ()
    gtk.main ()
