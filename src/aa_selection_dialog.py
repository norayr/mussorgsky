import hildon
import gtk
import gobject
from album_art import MussorgskyAlbumArt

class AlbumArtSelectionDialog (gtk.Dialog):

    def __init__ (self, parent, artist, album, size, downloader=None):
        """
        parent window, amount of images to offer
        Optionally downloader (for testing porpouses)
        """
        gtk.Dialog.__init__ (self,
                             "Select album art", parent,
                             gtk.DIALOG_DESTROY_WITH_PARENT,
                             (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        self.artist = artist
        self.album = album
        self.size = size
        self.paths = []
        self.__create_view (size)
        self.cancel = False
        self.connect ("response", self.handle_response)

        if (downloader):
            self.downloader = downloader
        else:
            self.downloader = MussorgskyAlbumArt ()

        gobject.idle_add (self.__get_alternatives_async)
        self.selection_img = None
        self.selection_thumb = None
        hildon.hildon_gtk_window_set_progress_indicator (self, 1)


    def __create_view (self, size):
        hbox = gtk.HBox (homogeneous=True)

        self.images = []
        self.event_boxes = []
        for i in range (0, size):
            img = gtk.Image ()
            img.set_size_request (124, 124)
            self.images.append (img)

            event_box = gtk.EventBox ()
            event_box.add (img)
            event_box.connect ("button-release-event", self.click_on_img, i)
            event_box.set_sensitive (False)
            self.event_boxes.append (event_box)
            
            hbox.pack_start (event_box, expand=False, fill=True)

        self.vbox.add (hbox)

    def __get_alternatives_async (self):
        counter = 0
        for (path, thumb) in self.downloader.get_alternatives (self.album, self.artist, self.size):
            if (self.cancel):
                return False
            self.paths.insert (counter, (path, thumb))
            print "Setting", thumb, "as image"
            self.images[counter].set_from_file (thumb)
            self.event_boxes [counter].set_sensitive (True)
            counter += 1
            while (gtk.events_pending()):
                gtk.main_iteration()

        while (counter < self.size):
                self.images[counter].set_from_stock (gtk.STOCK_CDROM, gtk.ICON_SIZE_DIALOG)
                counter += 1
                
        hildon.hildon_gtk_window_set_progress_indicator (self, 0)


    def click_on_img (self, widget, event, position):
        img, thumb = self.paths[position]
        self.selection_img, self.selection_thumb = self.downloader.save_alternative (self.artist,
                                                                                     self.album,
                                                                                     img, thumb)
        self.response (position)

    def get_selection (self):
        return (self.selection_img, self.selection_thumb)

    
    def handle_response (self, widget, response_id):
        self.cancel = True
        # Return False to continue propagating the signal
        return False

if __name__ == "__main__":

    import time
    class MockDownloader:
        def __init__ (self):
            self.alt = [("../hendrix.jpeg", "../hendrix-thumb.jpeg"),
                        ("../hoover.jpeg", "../hoover-thumb.jpeg"),
                        ("../backbeat.jpeg", "../backbeat-thumb.jpeg"),
                        ("../dylan.jpeg", "../dylan-thumb.jpeg")]
        def get_alternatives (self, album, artist, amount):
            for a in self.alt:
                time.sleep (1)
                yield a
        def save_alternative (self, artist, album, img, thumb):
            return ("/home/user/.cache/media-art/" + img, "/home/user/.thumbnails/normal/" + thumb)
                              

    def clicked_button (self):
        aadd = AlbumArtSelectionDialog (w, "rory gallagher", "irish tour", 4, MockDownloader ())
        aadd.show_all ()
        response = aadd.run ()
        if response == gtk.RESPONSE_CLOSE or response == gtk.RESPONSE_DELETE_EVENT or response == gtk.RESPONSE_REJECT:
            print "Noooo"
        else:
            print "Selected", aadd.get_selection ()
        aadd.hide ()
        
    w = gtk.Window ()
    w.connect ("destroy", gtk.main_quit)
    box = gtk.VBox ()

    button = gtk.Button ("click")
    button.connect ("clicked", clicked_button)
    box.add (button)

    w.add (box)
    w.show_all ()


    gtk.main ()

