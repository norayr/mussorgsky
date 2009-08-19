#!/usr/bin/env python2.5
import hildon
import gtk, gobject
from tracker_backend import TrackerBackend
from edit_panel import MussorgskyEditPanel
from download_dialog import MussorgskyAlbumArtDownloadDialog

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
        
    def show_edit_panel (self, songs, albums, artists):
        panel = MussorgskyEditPanel (songs, albums, artists)
        panel.connect ("destroy", self.back_to_main_view)
        panel.show_all ()

    def back_to_main_view (self, widget):
        print "Waiting to update"
        gobject.timeout_add_seconds (3, self.update_values, None)

    def broken_files_clicked (self, widget):
        list_songs = self.tracker.get_all_broken_songs ()
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

    def get_all_album_art (self, user_data):
        print "Get all album art"
        artist_album= self.tracker.get_all_pairs_artist_album ()
        dialog = MussorgskyAlbumArtDownloadDialog (self)
        dialog.show_all ()
        dialog.do_the_job (artist_album)
        
    def browse_clicked (self, widget):
        list_songs = self.tracker.get_all_songs ()
        list_albums = self.tracker.get_list_of_known_albums ()
        list_artists = self.tracker.get_list_of_known_artists ()
        self.show_edit_panel (list_songs, list_albums, list_artists)

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
        album_art.connect ("clicked", self.get_all_album_art)
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

