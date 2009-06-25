#!/usr/bin/env python2.5
import hildon
import gtk, gobject
from tracker_backend import TrackerBackend
from edit_panel import MussorgskyEditPanel


class MussorgskyMainWindow (hildon.StackableWindow):

    def __init__ (self):
        hildon.StackableWindow.__init__ (self)
        self.tracker = TrackerBackend ()
        self.set_title ("Mussorgsky")
        self.connect ("destroy", gtk.main_quit)
        main_view_box = self.create_main_view ()
        self.add (main_view_box)
        self.update_values (None)
        self.show_all ()
        
    def show_edit_panel (self, songs, albums, artists):
        panel = MussorgskyEditPanel (songs, albums, artists)
        panel.connect ("destroy", self.back_to_main_view)
        panel.show_all ()

    def back_to_main_view (self, widget):
        print "Waiting to update"
        gobject.timeout_add_seconds (3, self.update_values, None)

    def artists_clicked (self, widget):
        list_songs = self.tracker.get_songs_without_artist ()
        list_albums = self.tracker.get_list_of_known_albums ()
        list_artists = self.tracker.get_list_of_known_artists ()
        self.show_edit_panel (list_songs, list_albums, list_artists)

    def titles_clicked (self, widget):
        list_songs = self.tracker.get_songs_without_title ()
        list_albums = self.tracker.get_list_of_known_albums ()
        list_artists = self.tracker.get_list_of_known_artists ()
        self.show_edit_panel (list_songs, list_albums, list_artists)

    def albums_clicked (self, widget):
        list_songs = self.tracker.get_songs_without_album ()
        list_albums = self.tracker.get_list_of_known_albums ()
        list_artists = self.tracker.get_list_of_known_artists ()
        self.show_edit_panel (list_songs, list_albums, list_artists)

    def update_values (self, user_data):
        print "Updating labels"
        self.label_no_artist.set_text ("%s songs without artist" %
                                       self.tracker.count_songs_wo_artist ())
        self.label_no_title.set_text ("%s songs without title" %
                                      self.tracker.count_songs_wo_title ())
        self.label_no_album.set_text ("%s songs without album" %
                                      self.tracker.count_songs_wo_album ())
        return False

    def browse_clicked (self, widget):
        list_songs = self.tracker.get_all_songs ()
        list_albums = self.tracker.get_list_of_known_albums ()
        list_artists = self.tracker.get_list_of_known_artists ()
        self.show_edit_panel (list_songs, list_albums, list_artists)

    def create_main_view (self):
        vbox = gtk.VBox ()

        # Artist row
        artist_row = gtk.HBox (homogeneous=True)
        self.label_no_artist = gtk.Label ("")
        artist_row.add (self.label_no_artist)
        button_artists = gtk.Button ("Fix empty artists!")
        button_artists.connect ("clicked", self.artists_clicked)
        artist_row.add (button_artists)
    
        vbox.add (artist_row)

        # Title row
        title_row = gtk.HBox (homogeneous=True)
        self.label_no_title = gtk.Label ("")
        title_row.add (self.label_no_title)
        button_titles = gtk.Button ("Fix empty titles!")
        button_titles.connect ("clicked", self.titles_clicked)
        title_row.add (button_titles)
    
        vbox.add (title_row)

        # Album row
        album_row = gtk.HBox (homogeneous=True)
        self.label_no_album = gtk.Label ("")
        album_row.add (self.label_no_album)
        button_albums = gtk.Button ("Fix empty albums!")
        button_albums.connect ("clicked", self.albums_clicked)
        album_row.add (button_albums)

        vbox.add (album_row)

        # All songs row
        all_songs_row = hildon.Button (hildon.BUTTON_STYLE_NORMAL, hildon.BUTTON_ARRANGEMENT_HORIZONTAL)
        all_songs_row.set_title ("Browse the music collection")
        all_songs_row.connect ("clicked", self.browse_clicked)
        vbox.add (all_songs_row)

        return vbox

if __name__ == "__main__":

    try:
        window = MussorgskyMainWindow ()
        gtk.main ()
    except Exception, e:
        dialog = gtk.MessageDialog (None,
                                    gtk.DIALOG_DESTROY_WITH_PARENT,
                                    gtk.MESSAGE_ERROR,
                                    gtk.BUTTONS_CLOSE,
                                    "Error (%s)" % str(e));
        dialog.run ()

