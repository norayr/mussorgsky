#!/usr/bin/env python2.5
import gtk, gobject
from album_art import MussorgskyAlbumArt
from utils import escape_html

class MussorgskyAlbumArtDownloadDialog (gtk.Dialog):

    def __init__ (self, parent, downloader=None):
        gtk.Dialog.__init__ (self,
                             "Downloading album art", parent,
                             gtk.DIALOG_DESTROY_WITH_PARENT,
                             (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT)
                        )
        if (downloader):
            self.downloader = downloader
        else:
            self.downloader = MussorgskyAlbumArt ()
            
        self.set_title ("Downloading album art")
        self.connect ("response", self.handle_response)
        self.__create_view ()
        self.cancel = False

    def __create_view (self):

        hbox = gtk.HBox (homogeneous=False)

        self.album_art = gtk.Image ()
        self.album_art.set_size_request (124, 124)
        
        hbox.pack_start (self.album_art, expand=False, fill=True)

        labels = gtk.VBox ()
        self.previous_label = gtk.Label ("")
        labels.pack_start (self.previous_label)
        self.current_label = gtk.Label ("")
        labels.pack_start (self.current_label)

        hbox.pack_start (labels, expand=True, fill=False)
        
        self.vbox.add (hbox)


    def do_the_job (self, artist_albums_model):
        """
        each row: ("Visible text", pixbuf, Artist, Album)
        """
        TOTAL = len (artist_albums_model)
        current = 1

        it = artist_albums_model.get_iter_first ()
        while (it):
            while (gtk.events_pending()):
                gtk.main_iteration()

            if (self.cancel):
                break

            artist = artist_albums_model.get_value (it, 2)
            album = artist_albums_model.get_value (it, 3)
            
            self.current_label.set_markup ("<small>Trying: %s - %s</small>" % (escape_html(artist),
                                                                                   escape_html(album)))
            
            try:
                while (gtk.events_pending()):
                    gtk.main_iteration()

                if (self.cancel):
                    break
                
                (image, thumb) = self.downloader.get_album_art (artist, album)
                if thumb:
                        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size (thumb, 64, 64)
                        artist_albums_model.set_value (it, 1, pixbuf)
            except Exception, e:
                print "Error processing %s - %s" % (artist, album)
                print str(e)
                thumb = None
            
            self.set_title ("Downloading album art (%d/%d)" % (current, TOTAL))
            self.previous_label.set_markup ("<b>%s - %s</b>" % (escape_html(artist), escape_html(album)))
              
            if (thumb):
                self.album_art.set_from_file (thumb)
            else:
                self.album_art.set_from_stock (gtk.STOCK_CDROM, gtk.ICON_SIZE_DIALOG)

            current += 1
            it = artist_albums_model.iter_next (it)

        
    def handle_response (self, widget, response_id):
        if (response_id == gtk.RESPONSE_DELETE_EVENT):
            print "Cancel the work!"
        self.cancel = True
        self.destroy ()

if __name__ == "__main__":

    import time
    import random
    class MockDownloader:
        def __init__ (self):
            self.alt = [("../hendrix.jpeg", "../hendrix-thumb.jpeg"),
                        ("../hoover.jpeg", "../hoover-thumb.jpeg"),
                        ("../backbeat.jpeg", "../backbeat-thumb.jpeg"),
                        ("../dylan.jpeg", "../dylan-thumb.jpeg")]
            self.counter = 0
        def get_album_art (self, artist, album, force=False):
            time.sleep (3)
            return  self.alt [random.randint (0, len (self.alt)-1)]

    PAIRS_store = gtk.ListStore (str, gtk.gdk.Pixbuf, str, str)
    for i in range (0, 100):
        PAIRS_store.append (("blablabal", None, "Artist %d" % i, "Album %d" %i))

    def clicked_button (self):
        aadd = MussorgskyAlbumArtDownloadDialog (w, MockDownloader ())
        aadd.show_all ()
        aadd.do_the_job (PAIRS_store)
        
    w = gtk.Window ()
    box = gtk.VBox ()

    button = gtk.Button ("click")
    button.connect ("clicked", clicked_button)
    box.add (button)

    w.add (box)
    w.show_all ()


    gtk.main ()
