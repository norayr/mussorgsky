import hildon
import gtk
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
        self.__create_view (size)

        if (downloader):
            self.downloader = downloader
        else:
            self.downloader = MussorgskyAlbumArt ()
        self.paths = self.downloader.get_alternatives (album, artist, 4)
        self.selection_img = None
        self.selection_thumb = None
        self.__populate (self.paths)


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

    def __populate (self, paths):

        for i in range (0, self.size):
            if (len(paths) > i):
                self.images[i].set_from_file (paths[i])
                self.event_boxes[i].set_sensitive (True)
            else:
                self.images[i].set_from_stock (gtk.STOCK_CDROM, gtk.ICON_SIZE_DIALOG)

    def click_on_img (self, widget, event, position):
        self.selection_img, self.selection_thumb = self.downloader.save_alternative (self.artist,
                                                                                     self.album,
                                                                                     self.paths[position])
        self.response (position)

    def get_selection (self):
        return (self.selection_img, self.selection_thumb)

    

if __name__ == "__main__":

    class MockDownloader:
        def __init__ (self):
            self.alt = ["../hendrix.jpeg", "../hoover.jpeg", "../dylan.jpeg"]
        def get_alternatives (self, album, artist, amount):
            return self.alt [0:amount]
        def save_alternative (self, artist, album, img):
            return ("/home/user/.cache/media-art/" + img, "/home/user/.thumbnails/normal/" + img)
                              

    def clicked_button (self):
        aadd = AlbumArtSelectionDialog (w, "rory gallagher", "irish tour", 4, MockDownloader (ALTERNATIVES))
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

