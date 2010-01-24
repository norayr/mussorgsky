import hildon
import gtk
import gobject
from album_art_thread import MussorgskyAlbumArt

RESPONSE_CLICK = 1

class ClickableImage (gtk.EventBox):

    def __init__ (self, isRemoveOption=False):
        gtk.EventBox.__init__ (self)

        self.isRemoveOption = isRemoveOption

        self.img = gtk.Image ()
        self.img.set_size_request (124, 124)
        self.add (self.img)
        self.set_sensitive (False)

        self.img_path = None
        self.thumb_path = None

        if (self.isRemoveOption):
            self.img.set_from_icon_name ("mediaplayer_default_album",
                                         gtk.ICON_SIZE_MENU)
            self.img.set_pixel_size (124)
            self.set_sensitive (True)
            
    def set_image (self, tmp_img, tmp_thumb):
        assert not self.isRemoveOption
        self.img_path = tmp_img
        self.thumb_path = tmp_thumb
        self.img.set_from_file (self.thumb_path)
        self.set_sensitive (True)

    def set_default_image (self):
        self.img.set_from_stock (gtk.STOCK_CDROM, gtk.ICON_SIZE_DIALOG)

    def get_paths (self):
        return self.img_path, self.thumb_path

    def is_remove_option (self):
        return self.isRemoveOption
        

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
        for i in range (0, size):
            image = ClickableImage ()
            image.connect ("button-release-event", self.click_on_img)
            self.images.append (image)
            hbox.pack_start (image, expand=False, fill=True)
            
        # default empty option
        image = ClickableImage (isRemoveOption=True)
        image.connect ("button-release-event", self.click_on_img)
        self.images.append (image)
        hbox.pack_start (image, expand=False, fill=True)
        self.vbox.pack_start (hbox, padding=6)
        
        label = gtk.Label ("New search:")
        self.entry = hildon.Entry (gtk.HILDON_SIZE_FINGER_HEIGHT)
        self.entry.set_text (self.artist + " " +  self.album)

        img = gtk.Image ()
        img.set_from_icon_name ("general_search", gtk.ICON_SIZE_LARGE_TOOLBAR)
        button = hildon.Button (gtk.HILDON_SIZE_FINGER_HEIGHT,
                                hildon.BUTTON_ARRANGEMENT_HORIZONTAL)
        button.set_image (img)
        button.connect ("clicked", self.user_text_search_cb, self.entry)
        self.hbox_research = gtk.HBox (homogeneous=False, spacing=6)
        self.hbox_research.pack_start (label, expand=False)
        self.hbox_research.pack_start (self.entry)
        self.hbox_research.pack_start (button, expand=False)
        self.hbox_research.set_sensitive (False)
        self.vbox.pack_start (self.hbox_research, padding=6)

    def __get_alternatives_async (self):
        results = self.downloader.get_alternatives (self.album,
                                                    self.artist,
                                                    self.size)
        self.__show_results (results)
        
    def __show_results (self, generator):
        counter = 0
        for (path, thumb) in generator:
            print path, thumb
            if (self.cancel):
                return False
            if (thumb):
                print "Setting", thumb, "as image"
                self.images[counter].set_image (path, thumb)
            else:
                continue
            counter += 1
            while (gtk.events_pending()):
                gtk.main_iteration()

        while (counter < self.size):
                self.images[counter].set_default_image ()
                counter += 1
                
        hildon.hildon_gtk_window_set_progress_indicator (self, 0)
        self.hbox_research.set_sensitive (True)
        self.entry.grab_focus ()
        self.entry.select_region (0, -1)
        
    def user_text_search_cb (self, w, entry):
        user_text = entry.get_text ()
        if user_text and len (user_text) > 0:
            hildon.hildon_gtk_window_set_progress_indicator (self, 1)
            for ev in self.images[:-1]:
                ev.set_sensitive (False)
            self.hbox_research.set_sensitive (False)
            while (gtk.events_pending()):
                gtk.main_iteration()

            results = self.downloader.get_alternatives_free_text (user_text,
                                                                  self.size)
            self.__show_results (results)
            

    def click_on_img (self, image, event):
        if (image.is_remove_option ()):
            self.selection_img = None
            self.selection_thumb = None
            self.downloader.reset_alternative (self.artist, self.album)
        else:
            tmp_img, tmp_thumb = image.get_paths ()
            img, thumb = self.downloader.save_alternative (self.artist,
                                                           self.album,
                                                           tmp_img,
                                                           tmp_thumb)
            self.selection_img, self.selection_thumb = img, thumb
        self.response (RESPONSE_CLICK)

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
        def get_alternatives_free_text (self, user_text, amount=4):
            for a in [("free%d" % i, "thumb%d" %i) for i in range (0, amount)]:
                time.sleep (1)
                yield a
        def save_alternative (self, artist, album, img, thumb):
            return ("/home/user/.cache/media-art/" + img, "/home/user/.thumbnails/normal/" + thumb)
        def reset_alternative (self, artist, album):
            print "Removing the album-art and the thumbnail"
                              

    def clicked_button (self):
        aadd = AlbumArtSelectionDialog (w, "rory gallagher", "irish tour", 4, MockDownloader ())
        aadd.show_all ()
        response = aadd.run ()
        if response == gtk.RESPONSE_CLOSE or response == gtk.RESPONSE_DELETE_EVENT or response == gtk.RESPONSE_REJECT:
            print "Noooo"
        else:
            print "RESPONSE_CLICK", response == RESPONSE_CLICK
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

