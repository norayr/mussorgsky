#!/usr/bin/env python2.5
import pygst
pygst.require('0.10')
import gst
import gobject, sys

class MediaPlayer:

    def __init__ (self):
        self.playing = False
        self.player = gst.element_factory_make ("playbin2", "player")

    def play (self, uri):
        self.playing = True
        print 'Playing:', uri
        self.player.set_property ('uri', uri)
        self.player.set_state(gst.STATE_PLAYING)

    def stop (self):
        print 'Stop'
        if (self.playing):
            self.playing = False
            self.player.set_state(gst.STATE_NULL)
        
    def is_playing (self):
        return self.playing
        


def button_clicked_cb (widget, mediaplayer):
    #TESTFILE="file:///scratchbox/users/ivan/home/ivan/mufix/dejame.mp3"
    TESTFILE="file:///home/user/mufix/dejame.mp3"
    if (mediaplayer.is_playing ()):
        mediaplayer.stop ()
    else:
        mediaplayer.play (TESTFILE)

if __name__ == "__main__":

    import gtk
    
    w = gtk.Window ()
    w.connect ("destroy", gtk.main_quit)
    player = MediaPlayer ()

    button = gtk.Button (stock=gtk.STOCK_MEDIA_PLAY)
    button.connect ("clicked", button_clicked_cb, player)

    w.add (button)
    w.show_all ()
    gtk.main ()
