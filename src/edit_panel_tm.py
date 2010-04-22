#!/usr/bin/env python2.5
import hildon
import gtk, gobject
from mutagen_backend import MutagenBackend
from player_backend import MediaPlayer
from utils import escape_html
import album_art_spec
import os

# Fields in the tuple!
# Shared with browse_panel
URI_COLUMN = 0
ARTIST_COLUMN = 2
TITLE_COLUMN = 3
ALBUM_COLUMN = 4
MIME_COLUMN = 5
UI_COLUMN = 6
SEARCH_COLUMN = 7

THEME_PATH = "/usr/share/themes/default"

import i18n
_ = i18n.language.gettext

class MussorgskyEditPanel (hildon.StackableWindow):

    def __init__ (self):
        hildon.StackableWindow.__init__ (self)
        self.set_border_width (12)
        self.album_change_handler = -1
        self.artist_change_handler = -1
        self.writer = MutagenBackend ()
        self.player = MediaPlayer ()
        self.__create_view ()
        self.data_loaded = False
        self.artist_list = None
        self.albums_list = None
        self.current = None
        self.connect ("delete-event", self.close_function)

    def close_function (self, widget, event):
        if (not self.data_loaded):
            return
        
        if self.__is_view_dirty ():
            self.save_metadata ()

        
    def update_title (self):
        self.set_title (_("Edit song") + " (%d/%d)" % (self.model.get_path (self.current)[0] + 1,
                                                       len (self.model)))

    def get_current_row (self):
        if (not self.current):
            return 6 * (None,)
        return self.model.get (self.current, 0, 1, 2, 3, 4, 5)

    def set_model (self, model, current=None):
        assert type(model) == gtk.TreeModelFilter
        try:
            if self.artists_list or self.albums_list:
                pass
        except AttributeError, e:
            print "**** Set album and artist alternatives before setting a model"
            raise e
        
        self.model = model
        if (current):
            self.current = current
        else:
            self.current = self.model.get_iter_first ()
        self.data_loaded = True
        self.set_data_in_view (self.get_current_row ())
        self.update_title ()

    def set_current (self, current):
        """
        Iterator to current element
        """
        self.current = current
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

        if self.__is_view_dirty ():
            print "Modified data. Save!"
            self.save_metadata ()
            
        path = self.model.get_path (self.current)
        if (path[0] == 0):
            self.destroy ()
        else:
            new_path = ( path[0] -1, )
            self.current = self.model.get_iter (new_path)
            self.set_data_in_view (self.get_current_row ())
            self.update_title ()

    def press_next_cb (self, widget):
        if (self.player.is_playing ()):
            self.player.stop ()

        if self.__is_view_dirty ():
            print "Modified data. Save!"
            self.save_metadata ()

        self.current = self.model.iter_next (self.current)
        if (not self.current):
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
        m = self.model.get_model ()
        c = self.model.convert_iter_to_child_iter (self.current)

        artist = self.artist_button.get_value ()
        title = self.title_entry.get_text ()
        album = self.album_button.get_value ()
        text = "<b>%s</b>\n<small>%s</small>" % (escape_html (title),
                                                 escape_html (artist) + " / " + escape_html (album))
        search_str = artist.lower () + " " + title.lower () + " " + album.lower ()

        uri, mime = m.get (c, URI_COLUMN, MIME_COLUMN)
        m.set (c,
               ARTIST_COLUMN, artist,
               TITLE_COLUMN, title,
               ALBUM_COLUMN, album,
               UI_COLUMN, text,
               SEARCH_COLUMN, search_str)
        try:
            self.writer.save_metadata_on_file (uri,
                                               mime, 
                                               self.artist_button.get_value (),
                                               self.title_entry.get_text (),
                                               self.album_button.get_value ())
        except IOError, e:
            # This error in case of tracker returning unexistent files.
            # Uhm.... for instance after removing a memory card we are editing!
            pass
        

    def __is_view_dirty (self):
        """
        True if the data has been modified in the widgets
        """
        song = self.get_current_row ()

        return not (self.filename_data.get_text() == song[URI_COLUMN] and
                    self.artist_button.get_value () == song[ARTIST_COLUMN] and
                    self.title_entry.get_text () == song[TITLE_COLUMN] and
                    self.album_button.get_value () == song[ALBUM_COLUMN] )
        

    def __create_view (self):
        view_vbox = gtk.VBox (homogeneous=False, spacing = 12)

        filename_row = gtk.HBox ()
        self.filename_data = gtk.Label ("")
        filename_row.pack_start (self.filename_data, expand=True)

        #filename_row.pack_start (play_button, expand=False, fill=False)
        view_vbox.pack_start (filename_row, expand=False);

        central_panel = gtk.HBox (spacing=12)

        table = gtk.Table (3, 2, False)
        table.set_col_spacings (12)
        table.set_row_spacings (12)

        central_panel.pack_start (table, fill=True)
        view_vbox.pack_start (central_panel, expand=True, fill=True)

        # Title row
        label_title = gtk.Label (_("Title:"))
        table.attach (label_title, 0, 1, 0, 1, 0)
        self.title_entry = hildon.Entry(gtk.HILDON_SIZE_FINGER_HEIGHT)
        table.attach (self.title_entry, 1, 2, 0, 1)

        # Artist row
        self.artist_button = hildon.PickerButton (gtk.HILDON_SIZE_THUMB_HEIGHT,
                                                  hildon.BUTTON_ARRANGEMENT_HORIZONTAL)
        self.artist_button.set_title (_("Artist:"))
        # Set data will set the selector
        table.attach (self.artist_button, 0, 2, 1, 2)


        # Album row
        self.album_button = hildon.PickerButton (gtk.HILDON_SIZE_THUMB_HEIGHT,
                                                 hildon.BUTTON_ARRANGEMENT_HORIZONTAL)
        self.album_button.set_title (_("Album:"))
        # set_data will set the selector
        table.attach (self.album_button, 0, 2, 2, 3)
        

        # Album art space
        self.album_art = gtk.Image ()
        self.album_art.set_size_request (124, 124)
        central_panel.pack_start (self.album_art, expand=False, fill=False)
        
        # Buttons row
        button_box = gtk.Toolbar ()
        play_image = os.path.join (THEME_PATH, "mediaplayer", "Play.png")
        play_button = gtk.ToolButton (gtk.image_new_from_file (play_image))
        play_button.connect ("clicked", self.clicked_play)                   
        play_button.set_expand (True)
        button_box.insert (play_button, -1)
        
        separator = gtk.SeparatorToolItem ()
        separator.set_expand (True)
        button_box.insert  (separator, -1)

        back_image = os.path.join (THEME_PATH, "mediaplayer", "Back.png")
        back_button = gtk.ToolButton (gtk.image_new_from_file (back_image))
        back_button.connect ("clicked", self.press_back_cb)
        back_button.set_expand (True)
        button_box.insert (back_button, -1)

        next_image = os.path.join (THEME_PATH, "mediaplayer", "Forward.png")
        next_button = gtk.ToolButton (gtk.image_new_from_file (next_image))
        next_button.connect ("clicked", self.press_next_cb)
        next_button.set_expand (True)
        button_box.insert (next_button, -1)

        self.add_toolbar (button_box)
        
        self.add (view_vbox)


    def set_data_in_view (self, song):
        """
        Place in the screen the song information.
        Song is a tuple like (filename, 'Music', title, artist, album, mime)
        """
        assert len (song) == 6
        
        self.filename_data.set_markup ("<small>" + song[URI_COLUMN] + "</small>")
        self.title_entry.set_text (song[TITLE_COLUMN])
        

        # Disconnect the value-change signal to avoid extra album art retrievals
        if (self.album_button.handler_is_connected (self.album_change_handler)):
            self.album_button.disconnect (self.album_change_handler)
            
        if (self.artist_button.handler_is_connected (self.artist_change_handler)):
            self.artist_button.disconnect (self.artist_change_handler)

        # Set values in the picker buttons
        try:
            self.artist_button.set_active (self.artists_list.index(song[ARTIST_COLUMN]))
        except ValueError:
            print "'%s' not in artist list!?" % (song[ARTIST_COLUMN])
            self.artist_button.set_value ("")
        except AttributeError:
            print "WARNING: Use set_artist_alternatives method to set a list of artists"
            
        try:
            self.album_button.set_active (self.albums_list.index (song[ALBUM_COLUMN]))
        except ValueError:
            print "'%s' is not in the album list!?" % (song[ALBUM_COLUMN])
            self.album_button.set_value ("")
        except AttributeError:
            print "WARNING: Use set_album_alternatives method to set a list of artists"

        # Reconnect the signals!
        self.album_change_handler = self.album_button.connect ("value-changed",
                                                               self.album_selection_cb)

        self.artist_change_handler = self.artist_button.connect ("value-changed",
                                                                 self.artist_selection_cb)

        # Set the album art given the current data
        self.set_album_art (song[ALBUM_COLUMN])

        if (not song[MIME_COLUMN] in self.writer.get_supported_mimes ()):
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
            song = self.get_current_row ()
            self.player.play ("file://" + song[URI_COLUMN])

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

    TEST_DATA = [("/a/b/c/%d.mp3" %i, "Music",
                  "Artist %d" % i, "Title %d" % i, "Album %d" % (i*100),
                  "audio/mpeg",
                  "artist %d album %d" % (i, i*100),
                  "text to be searched artist %d album %d" % (i, i*100)) for i in range (0, 4)]

    model = gtk.ListStore (str, str, str, str, str, str, str, str)
    for t in TEST_DATA:
        print t
        model.append (t)

    window = MussorgskyEditPanel ()
    window.set_artist_alternatives (["Artist %d" % i for i in range (0, 4)])
    window.set_album_alternatives (["Album %d" % (i*100) for i in range (0, 4)])
    window.set_model (model.filter_new ())
    window.connect ("destroy", gtk.main_quit)
    window.show_all ()
    gtk.main ()
