#!/usr/bin/env python2.5
import hildon
import gtk, gobject
from edit_panel_tm import MussorgskyEditPanel
from utils import escape_html, Set

class MussorgskyBrowsePanel (hildon.StackableWindow):

    def __init__ (self, songs_list):
        hildon.StackableWindow.__init__ (self)
        self.set_title ("Browse collection")
        self.set_border_width (12)
        self.__create_view ()

        # Prepare cache of artists and albums
        self.artist_set = Set ()
        self.albums_set = Set ()

        # (uri, "Music", artist, title, album, mimetype) + "string" + search_string
        self.full_model = gtk.ListStore (str, str, str, str, str, str, str, str)
        for (uri, category, artist, title, album, mime) in songs_list:
            text = "<b>%s</b>\n<small>%s</small>" % (escape_html (title),
                                                     escape_html (artist) + " / " + escape_html (album))
            search_str = artist.lower () + " " + title.lower () + " " + album.lower ()
            self.full_model.append ((uri, category, artist, title, album, mime, text, search_str))
            self.artist_set.insert (artist)
            self.albums_set.insert (album)
            
        self.filtered_model = self.full_model.filter_new ()
        self.treeview.set_model (self.filtered_model)
        self.kpid = self.connect ("key-press-event", self.key_pressed_cb)

    def __create_view (self):
        vbox = gtk.VBox (homogeneous=False)
        
        self.treeview = gtk.TreeView ()
        self.treeview.connect ("row-activated", self.row_activated_cb)

        desc_column = gtk.TreeViewColumn ("Song", gtk.CellRendererText (), markup=6)
        desc_column.set_expand (True)
        self.treeview.append_column (desc_column)

        pannable_area = hildon.PannableArea ()
        pannable_area.add (self.treeview)
        
        vbox.pack_start (pannable_area, expand=True)
        
        self.search_hbox = gtk.HBox ()
        self.search_entry = hildon.Entry (gtk.HILDON_SIZE_FINGER_HEIGHT)
        self.search_hbox.pack_start (self.search_entry, expand=True)
        
        self.search_close = gtk.Button (stock=gtk.STOCK_CLOSE)
        self.search_hbox.pack_start (self.search_close, expand=False)
        self.search_close.connect ("clicked", self.close_search_cb)
        
        # Hide it when the window is created
        self.search_box_visible = False
        self.search_hbox.set_no_show_all (True)
        self.search_hbox.hide ()
        vbox.pack_start (self.search_hbox, expand=False)
        self.add (vbox)

    def search_type (self, widget):
        if len (widget.get_text()) == 0:
            self.treeview.set_model (self.full_model)
            return
            
        if (len (widget.get_text ()) < 3):
            return
        self.filtered_model.set_visible_func (self.entry_equals, widget)
        self.filtered_model.refilter ()
        self.treeview.set_model (self.filtered_model)

    def close_search_cb (self, widget):
        assert not self.search_box_visible
        self.search_hbox.hide_all ()
        self.search_entry.set_text ("")
        self.search_box_visible = False
        self.kpid = self.connect ("key-press-event", self.key_pressed_cb)

    def key_pressed_cb (self, widget, event):
        if (event.type == gtk.gdk.KEY_PRESS):
            if (event.keyval == gtk.gdk.keyval_from_name ("Alt_L")):
                return
            
            if (not self.search_box_visible ):
                self.search_hbox.set_no_show_all (False)
                self.search_hbox.show_all ()
                
            self.search_entry.grab_focus ()
            self.search_entry.connect ("changed", self.search_type)
            self.disconnect (self.kpid)
    
    def entry_equals (self, model, it, user_data):
        t = user_data.get_text ()
        return t.lower () in model.get_value (it, 7)

    def row_activated_cb (self, treeview, path, view_colum):
        edit_view = MussorgskyEditPanel ()
        edit_view.set_artist_alternatives (self.artist_set.as_list ())
        edit_view.set_album_alternatives (self.albums_set.as_list ())
        edit_view.set_model (self.treeview.get_model (), self.treeview.get_model ().get_iter (path))
        edit_view.show_all ()


if __name__ == "__main__":

    import random
    def get_random_path ():
        path = "file://"
        for i in range (0, random.randint (1, 8)):
            path = path + "/" + ("x"* random.randint (4, 12))
        return path
            

    songs = [(get_random_path (),
              "Music",
              "Artist%d" % i,
              "Title <%d>" % i,
              "album <%d>" % i,
              "audio/mpeg") for i in range (0, 100)]

    window = MussorgskyBrowsePanel (songs)
    window.connect ("destroy", gtk.main_quit )
    window.show_all ()
    gtk.main ()
