#!/usr/bin/env python2.5
import hildon
import gtk, gobject
from tracker_backend import TrackerBackend
from album_art_panel import MussorgskyAlbumArtPanel
from browse_panel import MussorgskyBrowsePanel
from fancy_button import FancyButton

class MussorgskyMainWindow (hildon.StackableWindow):

    def __init__ (self):
        hildon.StackableWindow.__init__ (self)
        self.tracker = TrackerBackend ()
        self.set_title ("MussOrgsky")
        self.set_border_width (12)
        self.connect ("destroy", gtk.main_quit)
        self.__create_view ()
        self.show_all ()
        
    def show_browse_panel (self, songs):
        panel = MussorgskyBrowsePanel (songs)
        panel.show_all ()

    def broken_files_clicked (self, widget):
        list_songs = self.tracker.get_all_broken_songs ()
        self.show_browse_panel (list_songs)

    def browse_clicked (self, widget):
        list_songs = self.tracker.get_all_songs ()
        self.show_browse_panel (list_songs)

    def album_art_clicked (self, widget):
        album_artists = self.tracker.get_all_pairs_album_artist ()
        panel = MussorgskyAlbumArtPanel (album_artists)
        panel.show_all ()

    def __create_view (self):

        image1 = gtk.Image ()
        # "app_install_applications" "app_install_browse"
        image1.set_from_icon_name ("app_install_applications", gtk.ICON_SIZE_MENU)
        image1.set_pixel_size (164)

        image2 = gtk.Image ()
        image2.set_from_icon_name ("app_install_browse", gtk.ICON_SIZE_MENU)
        image2.set_pixel_size (164)

        hbox = gtk.HBox ()

        align1 = gtk.Alignment (xalign=0.5, yalign=0.5)
        button1 = FancyButton (image1, "Browse metadata")
        button1.connect ("clicked", self.browse_clicked)
        align1.add (button1)
        hbox.pack_start (align1)

        align2 = gtk.Alignment (xalign=0.5, yalign=0.5)
        button2 = FancyButton(image2, "Album art")
        button2.connect ("clicked", self.album_art_clicked)
        align2.add (button2)
        hbox.pack_start (align2)

        self.add (hbox)


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

