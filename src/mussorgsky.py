#!/usr/bin/env python2.5
import hildon
import gtk, gobject
from tracker_backend import TrackerBackend
from album_art_panel import MussorgskyAlbumArtPanel
from browse_panel import MussorgskyBrowsePanel

class MussorgskyMainWindow (hildon.StackableWindow):

    def __init__ (self):
        hildon.StackableWindow.__init__ (self)
        self.tracker = TrackerBackend ()
        self.set_title ("MussOrgsky")
        self.set_border_width (12)
        self.connect ("destroy", gtk.main_quit)
        main_view_box = self.create_main_view ()
        self.add (main_view_box)
        self.update_values (None)
        self.show_all ()
        
    def show_edit_panel (self, songs):
        panel = MussorgskyBrowsePanel (songs)
        panel.connect ("destroy", self.back_to_main_view)
        panel.show_all ()

    def back_to_main_view (self, widget):
        print "Waiting to update"
        gobject.timeout_add_seconds (3, self.update_values, None)

    def broken_files_clicked (self, widget):
        list_songs = self.tracker.get_all_broken_songs ()
        self.show_edit_panel (list_songs)

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
        self.show_edit_panel (list_songs)

    def album_art_clicked (self, widget):
        album_artists = self.tracker.get_all_pairs_album_artist ()
        panel = MussorgskyAlbumArtPanel (album_artists)
        panel.show_all ()

    def create_main_view (self):
        vbox = gtk.VBox (spacing=12, homogeneous=False)

        # Labels artist row
        self.label_no_artist = gtk.Label ("")
        vbox.add (self.label_no_artist)

        self.label_no_title = gtk.Label ("")
        vbox.add (self.label_no_title)

        self.label_no_album = gtk.Label ("")
        vbox.add (self.label_no_album)
        
        # Buttons
        all_songs_row = gtk.HBox (homogeneous=True, spacing=12)

        button_broken_files = gtk.Button ("Fix metadata!")
        button_broken_files.connect ("clicked", self.broken_files_clicked)
        all_songs_row.add (button_broken_files)
        
        browse = hildon.Button (hildon.BUTTON_STYLE_NORMAL,
                                hildon.BUTTON_ARRANGEMENT_HORIZONTAL)
        browse.set_title ("Manage\ncollection")
        browse.connect ("clicked", self.browse_clicked)
        all_songs_row.add (browse)

        album_art = hildon.Button (hildon.BUTTON_STYLE_NORMAL,
                                   hildon.BUTTON_ARRANGEMENT_HORIZONTAL)
        album_art.set_title ("Album art")
        album_art.connect ("clicked", self.album_art_clicked)
        all_songs_row.add (album_art)

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

