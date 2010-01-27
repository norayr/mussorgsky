#!/usr/bin/env python2.5
import hildon
import gtk, gobject
import os
from album_art_spec import getCoverArtThumbFileName
from download_dialog import MussorgskyAlbumArtDownloadDialog
from utils import escape_html
from aa_selection_dialog import AlbumArtSelectionDialog, RESPONSE_CLICK

import time

EMPTY_PIXBUF = gtk.gdk.Pixbuf (gtk.gdk.COLORSPACE_RGB, False, 8, 64, 64)

class MussorgskyAlbumArtPanel (hildon.StackableWindow):

    def __init__ (self, album_artists):
        hildon.StackableWindow.__init__ (self)
        self.set_title ("Album art handling")
        self.set_border_width (12)
        print "Create view       :",time.time ()
        self.__create_view ()
        print "Create view (DONE):", time.time ()
        self.downloader = None
        # Visible string, image, artist, album, painted!
        self.model = gtk.ListStore (str, gtk.gdk.Pixbuf, str, str, bool)
        print "Populate model      :", time.time ()
        for p in album_artists:
            if (not p[0]):
                continue
            t = ("".join (["<b>", escape_html (p[0]),"</b>\n<small>",
                           escape_html(p[1]), "</small>"]), None, p[1], p[0], False)
            self.model.append (t)
        print "Populate model (DONE):", time.time ()
            
        self.treeview.set_model (self.model)

    def __create_view (self):
        self.treeview = gtk.TreeView ()
        self.treeview.connect ("row-activated", self.row_activated_cb)

        artist_column = gtk.TreeViewColumn ("Artist", gtk.CellRendererText (), markup=0)
        artist_column.set_expand (True)
        self.treeview.append_column (artist_column)

        renderer = gtk.CellRendererPixbuf ()
        album_art = gtk.TreeViewColumn ("Album art", renderer, pixbuf=1)
        # This doesn't have real effect:
        album_art.set_sizing (gtk.TREE_VIEW_COLUMN_FIXED)
        album_art.set_fixed_width (64)
        
        album_art.set_cell_data_func (renderer, self.album_art_cell_data_cb)
        self.treeview.append_column (album_art)

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

    def album_art_cell_data_cb (self, column, cell, model, iter):
        pixbuf, album, not_first_time = model.get (iter, 1, 3, 4)
        if (not_first_time):
            if (pixbuf == None):
                #print "Calling album art cell data cb", model.get (iter, 3)
                album_art_path = getCoverArtThumbFileName (album)
                if (os.path.exists (album_art_path)):
                    pxb = gtk.gdk.pixbuf_new_from_file_at_size (album_art_path, 64, 64)
                    model.set (iter, 1, pxb)
                else:
                    #print "Cannot find thumbnail in '%s'" % (album_art_path)
                    model.set (iter, 1, EMPTY_PIXBUF) 
                    
        else:
            model.set (iter, 4, True)

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
        if (response == RESPONSE_CLICK):
            (img, thumb) = dialog.get_selection ()
            if img and thumb:
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_size (thumb, 64, 64)
                treeview.get_model ().set (it, 1, pixbuf)
            else:
                treeview.get_model ().set (it, 1, EMPTY_PIXBUF)
        dialog.destroy ()

            
if __name__ == "__main__":
    import random
    
    artists_albums = [("Artist %d the greatest bolero singer in the universe" % i, "Album <%d>" % i) for i in range (0, 10000)]

    # Overwrite the get thumb path for testing
    def local_file (path):
        return "../thumb%d.124.jpeg" % (random.randint (0, 3))

    global getCoverArtThumbFileName
    getCoverArtThumbFileName = local_file

    window = MussorgskyAlbumArtPanel (artists_albums)
    window.connect ("destroy", gtk.main_quit )
    window.show_all ()
    gtk.main ()
