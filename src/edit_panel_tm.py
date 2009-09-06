#!/usr/bin/env python2.5
import hildon
import gtk, gobject
from mutagen_backend import MutagenBackend
from player_backend import MediaPlayer
import album_art_spec
import os

# Fields in the tuple!
FILE_URI = 0
ARTIST_KEY = 2
TITLE_KEY = 3
ALBUM_KEY = 4
MIME_KEY = 5

class MussorgskyEditPanel (hildon.StackableWindow):

    def __init__ (self):
        hildon.StackableWindow.__init__ (self)
        self.set_border_width (12)
        self.album_callback_id = -1
        self.album_change_handler = -1
        self.artist_change_handler = -1
        self.writer = MutagenBackend ()
        self.player = MediaPlayer ()
        self.__create_view ()
        self.data_loaded = False

    def update_title (self):
        self.set_title ("Edit (%d/%d)" % (self.model.get_path (self.current)[0] + 1,
                                          len (self.model)))

    def get_current_row (self):
        if (not self.current):
            return 6 * (None,)
        return self.model.get (self.current, 0, 1, 2, 3, 4, 5)

    def set_model (self, model, current=None):
        self.model = model
        if (current):
            self.current = current
        else:
            self.current = self.model.get_iter_first ()

        self.set_data_in_view (self.get_current_row ())
        self.update_title ()

    def set_artist_alternatives (self, alternatives):
        self.artists_list = alternatives
        artist_selector = hildon.TouchSelectorEntry (text=True)
        for a in self.artists_list:
            artist_selector.append_text (a)
        self.artist_button.set_selector (artist_selector)

    def set_album_alternatives (self, alternatives):
        self.albums_list = alternatives
        album_selector = hildon.TouchSelectorEntry (text=True)
        for a in self.albums_list:
            album_selector.append_text (a)
        self.album_button.set_selector (album_selector)


    def press_back_cb (self, widget):
        if (self.player.is_playing ()):
            self.player.stop ()

        if (self.album_callback_id != -1):
            gobject.source_remove (self.album_callback_id)
            self.album_callback_id = -1

        if self.__is_view_dirty ():
            print "Modified data. Save!"
            self.save_metadata ()
            
        self.current = self.model.iter_next (self.current)
        if (not self.current):
            self.destroy ()
            
        self.set_data_in_view (self.get_current_row ())

    def press_next_cb (self, widget):
        if (self.player.is_playing ()):
            self.player.stop ()

        if (self.album_callback_id != -1):
            gobject.source_remove (self.album_callback_id)
            self.album_callback_id = -1

        if self.__is_view_dirty ():
            print "Modified data. Save!"
            self.save_metadata ()

        self.current = self.model.iter_next (self.current)
        if (not self.current):
            print "Destroy"
            self.destroy ()
        else:
            self.set_data_in_view (self.get_current_row ())
            self.update_title ()
            
    def save_metadata (self):
        # Save the data in the online model to show the appropiate data
        # in the UI while tracker process the update.

        # 0 - filename -> doesn't change
        # 1 - "Music"  -> doesn't change
        # 5 - mimetype -> doesn't change
        if (type (self.model) == gtk.TreeModelFilter):
            m = self.model.get_model ()
        else:
            m = self.model
        m.set (self.current,
               2, self.artist_button.get_value (),
               3, self.title_entry.get_text (),
               4, self.album_button.get_value ())
        new_song = self.get_current_row ()
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
        song = self.get_current_row ()

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
        self.artist_button = hildon.PickerButton (hildon.BUTTON_STYLE_NORMAL,
                                                  hildon.BUTTON_ARRANGEMENT_HORIZONTAL)
        self.artist_button.set_title ("Artist: ")
        # Set data will set the selector
        table.attach (self.artist_button, 0, 2, 1, 2)


        # Album row
        self.album_button = hildon.PickerButton (hildon.BUTTON_STYLE_NORMAL,
                                                 hildon.BUTTON_ARRANGEMENT_HORIZONTAL)
        self.album_button.set_title ("Album: ")
        # set_data will set the selector
        table.attach (self.album_button, 0, 2, 2, 3) 
        

        # Album art space
        self.album_art = gtk.Image ()
        self.album_art.set_size_request (124, 124)
        central_panel.pack_start (self.album_art, expand=False, fill=False)
        
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
        
        self.add (view_vbox)


    def go_to_cb (self, widget):
        pass

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
        self.set_album_art (song[ALBUM_KEY])

        if (not song[MIME_KEY] in self.writer.get_supported_mimes ()):
            self.artist_button.set_sensitive (False)
            self.album_button.set_sensitive (False)
            self.title_entry.set_sensitive (False)
        else:
            self.artist_button.set_sensitive (True)
            self.album_button.set_sensitive (True)
            self.title_entry.set_sensitive (True)

    def set_album_art (self, album):
        has_album = False
        if (album):
            thumb = album_art_spec.getCoverArtThumbFileName (album)
	    print "%s -> %s" % (album, thumb)
            if (os.path.exists (thumb)):
                self.album_art.set_from_file (thumb)
                has_album = True
            
        if (not has_album):
            self.album_art.set_from_stock (gtk.STOCK_CDROM, gtk.ICON_SIZE_DIALOG)

        
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
        song = self.get_current_row ()
        if (not widget.get_value () in self.albums_list):
            print "Inserting ", widget.get_value ()
            widget.get_selector ().prepend_text (widget.get_value ())
            self.albums_list.insert (0, widget.get_value ())
        self.set_album_art (widget.get_value ())

    def artist_selection_cb (self, widget):
        """
        On artist change, add the artist the local list of artists and the selector
        if it doesn't exist already. So we show the new entry in the selector next time
        """
        song = self.get_current_row ()
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

    model = gtk.ListStore (str, str, str, str, str, str)
    for t in TEST_DATA:
        model.append (t)

    window = MussorgskyEditPanel ()
    window.set_model (model)
    window.connect ("destroy", gtk.main_quit)
    window.show_all ()
    gtk.main ()
