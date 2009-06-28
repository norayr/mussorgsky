#!/usr/bin/env python2.5
import gtk, gobject
from album_art import MussorgskyAlbumArt

class MussorgskyAlbumArtDownloadDialog (gtk.Dialog):

    def __init__ (self, parent):
        gtk.Dialog.__init__ (self,
                             "Downloading album art", parent,
                             gtk.DIALOG_DESTROY_WITH_PARENT,
                             (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT)
                        )
        self.downloader = MussorgskyAlbumArt ()
        self.set_title ("Downloading album art")
        self.connect ("response", self.handle_response)
        self.create_view ()
        self.cancel = False

    def create_view (self):

        hbox = gtk.HBox (homogeneous=False)

        self.album_art = gtk.Image ()
        self.album_art.set_size_request (124, 124)
        
        hbox.pack_start (self.album_art, expand=False, fill=True)

        labels = gtk.VBox ()
        self.status_label = gtk.Label ("")
        labels.pack_start (self.status_label)
        self.current_label = gtk.Label ("")
        labels.pack_start (self.current_label)

        hbox.pack_start (labels, expand=True, fill=False)
        
        self.vbox.add (hbox)


    def do_the_job (self, artist_albums):
        TOTAL = len (artist_albums)
        current = 1
        
        for (artist, album) in artist_albums:
            while (gtk.events_pending()):
                gtk.main_iteration()

            if (self.cancel):
                break
            
            try:
                (image, thumb) = self.downloader.get_album_art (artist, album)
            except LookupError, e:
                print "Error processing %s - %s" % (artist, album)
                print str(e)
                self.album_art.set_from_stock (gtk.STOCK_CDROM, gtk.ICON_SIZE_DIALOG)
                continue

            self.status_label.set_text ("Retrieved (%d/%d)" % (current, TOTAL))
            self.current_label.set_markup ("<b>%s - %s</b>" % (artist, album))
              
            if (thumb):
                self.album_art.set_from_file (thumb)
            else:
                self.album_art.set_from_stock (gtk.STOCK_CDROM, gtk.ICON_SIZE_DIALOG)

            current += 1

        
    def handle_response (self, widget, response_id):
        if (response_id == gtk.RESPONSE_DELETE_EVENT):
            print "Cancel the work!"
        self.cancel = True
        self.destroy ()

if __name__ == "__main__":

    PAIRS_NO = [("Led Zeppelin", "Led Zeppelin IV"),
             ("Pink Floyd", "The Wall"),
             ("Deep purple", "Made in Japan"),
             ("", "Freakin' out"),
             ("Dinah Washington", "")]

    PAIRS = [ ("Artist %d" % i, "Album %d" %i) for i in range (0, 100)]

    def clicked_button (self):
        aadd = MussorgskyAlbumArtDownloadDialog (w)
        aadd.show_all ()
        aadd.do_the_job (PAIRS)
        
    w = gtk.Window ()
    box = gtk.VBox ()

    button = gtk.Button ("click")
    button.connect ("clicked", clicked_button)
    box.add (button)

    w.add (box)
    w.show_all ()


    gtk.main ()
