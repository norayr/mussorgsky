#!/usr/bin/env python2.5
import hildon
import gtk, gobject
from tracker_backend import TrackerBackend
from album_art_spec import getCoverArtThumbFileName
from download_dialog import MussorgskyAlbumArtDownloadDialog

class MussorgskyAlbumArtPanel (hildon.StackableWindow):

    def __init__ (self):
        hildon.StackableWindow.__init__ (self)
        self.set_title ("Album art handling")
        self.set_border_width (12)
        self.__create_view ()
        self.model = gtk.ListStore (str, gtk.gdk.Pixbuf, str, str)

        self.tracker = TrackerBackend ()
        
        pairs = self.tracker.get_all_pairs_artist_album ()
        for p in pairs:
            if (not p[1]):
                continue
            album_art_path = getCoverArtThumbFileName (p[1])
            try:
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_size (album_art_path, 124, 124)
            except gobject.GError:
                pixbuf = None
            t = ("<b>%s</b>\n<small>%s</small>" % (p[1], p[0]), pixbuf, p[0], p[1])
            self.model.append (t)
                
            
        self.treeview.set_model (self.model)

    def __create_view (self):
        vbox = gtk.VBox (spacing=12, homogeneous=False)

        self.treeview = gtk.TreeView ()
        self.treeview.connect ("row-activated", self.row_activated_cb)

        artist_column = gtk.TreeViewColumn ("Artist", gtk.CellRendererText (), markup=0)
        self.treeview.append_column (artist_column)

        album_art = gtk.TreeViewColumn ("Album art", gtk.CellRendererPixbuf (), pixbuf=1)
        self.treeview.append_column (album_art)

        vbox.add (self.treeview)
        
        self.add (vbox)

        # Menu
        menu = hildon.AppMenu ()
        automatic_retrieval = hildon.Button (hildon.BUTTON_STYLE_NORMAL,
                                             hildon.BUTTON_ARRANGEMENT_HORIZONTAL)
        automatic_retrieval.set_title ("Automatic retrieval")
        automatic_retrieval.connect ("clicked", self.get_all_album_art)
        menu.append (automatic_retrieval)
        menu.show_all ()
        self.set_app_menu (menu)

    def get_all_album_art (self, user_data):
        dialog = MussorgskyAlbumArtDownloadDialog (self)
        dialog.show_all ()
        dialog.do_the_job (self.model)

    def row_activated_cb (self, treeview, path, view_colum):
        print "Get alternatives for..."
        it = treeview.get_model ().get_iter (path)
        print treeview.get_model ().get_value (it, 3)



if __name__ == "__main__":

    window = MussorgskyAlbumArtPanel ()
    window.connect ("destroy", gtk.main_quit )
    window.show_all ()
    gtk.main ()
