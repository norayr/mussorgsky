import hildon
import gtk

class AlbumArtSelectionDialog (gtk.Dialog):

    def __init__ (self, parent, size):
        gtk.Dialog.__init__ (self,
                             "Select album art", parent,
                             gtk.DIALOG_DESTROY_WITH_PARENT,
                             (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        self.__create_view (size)
        self.size = size

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

    def populate (self, paths):

        for i in range (0, self.size):
            if (len(paths) > i):
                self.images[i].set_from_file (paths[i])
                self.event_boxes[i].set_sensitive (True)
            else:
                self.images[i].set_from_stock (gtk.STOCK_CDROM, gtk.ICON_SIZE_DIALOG)

    def click_on_img (self, widget, event, position):
        self.response (position)

if __name__ == "__main__":

    ALTERNATIVES = ["../hendrix.jpeg", "../hoover.jpeg", "../dylan.jpeg"]

    def clicked_button (self):
        aadd = AlbumArtSelectionDialog (w, 4)
        aadd.show_all ()
        aadd.populate (ALTERNATIVES)
        response = aadd.run ()
        if response == gtk.RESPONSE_CLOSE or response == gtk.RESPONSE_DELETE_EVENT or response == gtk.RESPONSE_REJECT:
            print "Noooo"
        else:
            print "Selected", response
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

