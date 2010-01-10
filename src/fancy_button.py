import gtk
import gobject

BUTTON_HILIGHT_FILE_NAME = "/etc/hildon/theme/mediaplayer/Button.png"

fancy_button_highlight_pb = None

class FancyButton (gtk.EventBox):

    __gsignals__ = {
        'clicked': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ())
    }

    def __init__ (self, image, text):
        gtk.EventBox.__init__ (self)

        self.pressed = False

        vbox = gtk.VBox ()
        self.image = image
        self.label = gtk.Label (text)

        align = gtk.Alignment (xalign=0.5, yalign=0.5)
        align.add (self.image)

        vbox.pack_start (align, expand=False, fill=False)
        vbox.pack_start (self.label, expand=False, fill=False)

        self.add (vbox)
        self.set_visible_window (False)
        self.set_above_child (True)

        self.connect ("button-press-event", self.custom_button_press_event)
        self.connect ("button-release-event", self.custom_button_release_event)
        self.connect ("enter-notify-event", self.custom_enter_notify_event)
        self.connect ("leave-notify-event", self.custom_leave_notify_event)
        self.image.connect ("expose-event", self.image_expose_event)
        
        
    def custom_button_press_event (self, p, q):
        self.image.set_state (gtk.STATE_ACTIVE)
        self.pressed = True
        print "OK"

    def custom_button_release_event (self, p, q):

        if (self.pressed and self.image.state  == gtk.STATE_ACTIVE):
            self.emit ("clicked")

        self.image.set_state (gtk.STATE_NORMAL)
        self.pressed = False

    def custom_enter_notify_event (self, p, q):
        if (self.pressed):
            self.image.set_state (gtk.STATE_ACTIVE)

    def custom_leave_notify_event (self, p, q):
        self.image.set_state (gtk.STATE_NORMAL)

    def image_expose_event (self, widget, event):
        global fancy_button_highlight_pb
        
        if (widget.state == gtk.STATE_ACTIVE):
            if (fancy_button_highlight_pb):
                widget.window.draw_pixbuf (None,
                                           fancy_button_highlight_pb,
                                           0, 0,
                                           widget.allocation.x,
                                           widget.allocation.y)
            else:
                gtk.Style.paint_flat_box (widget.style,
                                          event.window,
                                          gtk.STATE_ACTIVE,
                                          gtk.SHADOW_NONE,
                                          event.area,
                                          widget,
                                          "eventbox",
                                          event.area.x,
                                          event.area.y,
                                          event.area.width,
                                          event.area.height)


def settings_changed (obj, spec):
    global fancy_button_highlight_pb
    try:
        fancy_button_highlight_pb = gtk.gdk.pixbuf_new_from_file (BUTTON_HILIGHT_FILE_NAME)
    except Exception, e:
        print str(e)
        fancy_button_highlight_pb = None

if __name__ == "__main__":

    w = gtk.Window ()

    settings = gtk.settings_get_default ()
    settings.connect ("notify", settings_changed)
    settings_changed (None, None)


    frame = gtk.Frame ()
    frame.add (FancyButton ())

    align = gtk.Alignment (xalign=0.5, yalign=0.5)
    align.add (frame)
    
    
    w.add (align)
    w.show_all ()
    w.connect ("delete-event", gtk.main_quit)
    gtk.main ()

    
