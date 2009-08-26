#!/usr/bin/env python2.5
import hildon
import gtk, gobject
from album_art_spec import getCoverArtThumbFileName
from download_dialog import MussorgskyAlbumArtDownloadDialog
from utils import escape_html
from aa_selection_dialog import AlbumArtSelectionDialog

class MussorgskyAlbumArtPanel (hildon.StackableWindow):

    def __init__ (self, album_artists):
        hildon.StackableWindow.__init__ (self)
        self.set_title ("Album art handling")
        self.set_border_width (12)
        self.__create_view ()
        self.downloader = None
        self.model = gtk.ListStore (str, gtk.gdk.Pixbuf, str, str)

        for p in album_artists:
            if (not p[1]):
                continue
            album_art_path = getCoverArtThumbFileName (p[1])
            try:
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_size (album_art_path, 64, 64)
            except gobject.GError:
                pixbuf = None
            t = ("<b>%s</b>\n<small>%s</small>" % (escape_html(p[1]), escape_html(p[0])), pixbuf, p[0], p[1])
            self.model.append (t)
            
        self.treeview.set_model (self.model)

    def __create_view (self):
        vbox = gtk.VBox (spacing=12, homogeneous=False)

        self.treeview = gtk.TreeView ()
        self.treeview.connect ("row-activated", self.row_activated_cb)

        artist_column = gtk.TreeViewColumn ("Artist", gtk.CellRendererText (), markup=0)
        artist_column.set_expand (True)
        self.treeview.append_column (artist_column)

        album_art = gtk.TreeViewColumn ("Album art", gtk.CellRendererPixbuf (), pixbuf=1)
        self.treeview.append_column (album_art)

        #vbox.add (self.treeview)

        pannable_area = hildon.PannableArea ()
        pannable_area.add (self.treeview)
        self.add (pannable_area)

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
        it = treeview.get_model ().get_iter (path)
        album = treeview.get_model ().get_value (it, 3)
        artist = treeview.get_model ().get_value (it, 2)

        dialog = AlbumArtSelectionDialog (self, artist, album, 5)
        dialog.show_all ()
        
        response = dialog.run ()
        if (response > -1):
            (img, thumb) = dialog.get_selection ()
            if img and thumb:
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_size (thumb, 64, 64)
                treeview.get_model ().set (it, 1, pixbuf)
        dialog.destroy ()
            
if __name__ == "__main__":

    artists_albums = [("Artist %d the greatest bolero singer in the universe" % i, "Album <%d>" % i) for i in range (0, 100)]


    window = MussorgskyAlbumArtPanel (artists_albums)
    window.connect ("destroy", gtk.main_quit )
    window.show_all ()
    gtk.main ()
