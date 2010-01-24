#!/usr/bin/env python2.5
import hildon
import gtk, gobject
from edit_panel_tm import MussorgskyEditPanel
from utils import escape_html, Set, is_empty

# Shared with edit_panel_tm
URI_COLUMN = 0
ARTIST_COLUMN = 2
TITLE_COLUMN = 3
ALBUM_COLUMN = 4
MIME_COLUMN = 5
UI_COLUMN = 6
SEARCH_COLUMN = 7

SHOW_ALL = 1
SHOW_UNCOMPLETE = 2
SHOW_MATCH = 3

import time

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
        full_model = gtk.ListStore (str, str, str, str, str, str, str, str)
        for (uri, category, artist, title, album, mime) in songs_list:
            if is_empty (artist) and is_empty (title) and is_empty (album):
                text = "<small>%s</small>" % (escape_html (uri))
            else:
                text = "<b>%s</b>\n<small>%s</small>" % (escape_html (title),
                                                         escape_html (artist) + " / " + escape_html (album))
            search_str = " ".join ([artist.lower (),
                                   title.lower (),
                                   album.lower ()])
            full_model.append ((uri, None, artist, title, album, mime, text, search_str))
            self.artist_set.insert (artist)
            self.albums_set.insert (album)

        self.filtered_model = full_model.filter_new ()
        self.treeview.set_model (self.filtered_model)
        self.filter_mode = SHOW_ALL
        self.filtered_model.set_visible_func (self.filter_entry)
        self.__set_filter_mode (None, SHOW_ALL)

        self.kpid = self.connect ("key-press-event", self.key_pressed_cb)

    def __create_view (self):
        vbox = gtk.VBox (homogeneous=False)

        menu = hildon.AppMenu ()
        self.all_items = gtk.RadioButton (None, "All")
        self.all_items.set_mode (False)
        self.all_items.connect_after ("toggled", self.__set_filter_mode, SHOW_ALL)
        menu.add_filter (self.all_items)
        self.broken_items = gtk.RadioButton (self.all_items, "Uncomplete")
        self.broken_items.set_mode (False)
        self.broken_items.connect_after ("toggled",
                                         self.__set_filter_mode, SHOW_UNCOMPLETE)
        menu.add_filter (self.broken_items)
        menu.show_all ()
        self.set_app_menu (menu)
        
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
        self.filtered_model.refilter ()

    def close_search_cb (self, widget):
        assert not self.search_box_visible
        self.search_hbox.hide_all ()
        self.search_entry.set_text ("")
        self.search_box_visible = False
        if (self.all_items.get_active ()):
            self.filter_mode = SHOW_ALL
        else:
            self.filter_mode = SHOW_UNCOMPLETE
        self.filtered_model.refilter ()
        self.kpid = self.connect ("key-press-event", self.key_pressed_cb)

    def key_pressed_cb (self, widget, event):
        if (event.type == gtk.gdk.KEY_PRESS):
            if (event.keyval == gtk.gdk.keyval_from_name ("Alt_L")):
                return
            
            if (not self.search_box_visible ):
                self.filter_mode = SHOW_MATCH
                self.search_hbox.set_no_show_all (False)
                self.search_hbox.show_all ()
                
            self.search_entry.grab_focus ()
            self.search_entry.connect ("changed", self.search_type)
            self.disconnect (self.kpid)
    

    def row_activated_cb (self, treeview, path, view_colum):
        edit_view = MussorgskyEditPanel ()
        edit_view.set_artist_alternatives (self.artist_set.as_list ())
        edit_view.set_album_alternatives (self.albums_set.as_list ())
        edit_view.set_model (self.treeview.get_model (), self.treeview.get_model ().get_iter (path))
        edit_view.show_all ()

    def __set_filter_mode (self, button, filter_mode):
        """
        Parameter to use it as callback as well as regular function
        """
        if (filter_mode == self.filter_mode):
            # Don't refilter if there is no change!
            return
        self.filter_mode = filter_mode

        start = time.time ()
        self.treeview.set_model (None)
        self.filtered_model.refilter ()
        self.treeview.set_model (self.filtered_model)
        end = time.time ()
        print "Refiltering ", end - start

    def filter_entry (self, model, it):
        if self.filter_mode == SHOW_ALL:
            return True
        elif self.filter_mode == SHOW_UNCOMPLETE:
            return self.entry_uncomplete (model, it)
        elif self.filter_mode == SHOW_MATCH:
            return self.entry_with_text (model, it)

    def entry_with_text (self, model, it):
        t = self.search_entry.get_text ()
        return t.lower () in model.get_value (it, SEARCH_COLUMN)

    def entry_uncomplete (self, model, it):
        r = filter (lambda x: not x or len(x.strip()) == 0,
                    model.get (it, ARTIST_COLUMN, TITLE_COLUMN, ALBUM_COLUMN))
        return len (r) > 0
        
if __name__ == "__main__":

    import random
    def get_random_path ():
        path = "file://"
        for i in range (0, random.randint (1, 8)):
            path = path + "/" + ("x"* random.randint (4, 12))
        return path

    def get_some_empty_titles (i):
        if random.randint (0, 5) <= 1:
            return ""
        else:
            return "Title <%d>" % i
        

    songs = [(get_random_path (),
              "Music",
              "Artist%d" % i,
              get_some_empty_titles (i),
              "album <%d>" % i,
              "audio/mpeg") for i in range (0, 30000)]

    songs.append (("file:///no/metadata/at/all",
                   "music",
                   "",
                   "",
                   "",
                   "audio/mpeg"))

    window = MussorgskyBrowsePanel (songs)
    window.connect ("destroy", gtk.main_quit )
    window.show_all ()
    gtk.main ()
