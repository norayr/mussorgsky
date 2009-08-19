#!/usr/bin/env python2.5
import dbus
import os

TRACKER = 'org.freedesktop.Tracker'
TRACKER_OBJ = '/org/freedesktop/Tracker/Metadata'
TRACKER_SEARCH_OBJ = '/org/freedesktop/Tracker/Search'

RDF_NO_PROPX = """
<rdfq:Condition>
  <rdfq:and>
    <rdfq:equals>
      <rdfq:Property name="%s" />
      <rdf:String></rdf:String> 
    </rdfq:equals>
  </rdfq:and>
</rdfq:Condition>
"""

RDF_NO_ARTIST = RDF_NO_PROPX % "Audio:Artist"
RDF_NO_ALBUM = RDF_NO_PROPX % "Audio:Album"
RDF_NO_TITLE = RDF_NO_PROPX % "Audio:Title"

RDF_ANY_MISSING_METADATA = """
<rdfq:Condition>
  <rdfq:or>
    <rdfq:equals>
      <rdfq:Property name="Audio:Artist" />
      <rdf:String></rdf:String> 
    </rdfq:equals>
    <rdfq:equals>
      <rdfq:Property name="Audio:Title" />
      <rdf:String></rdf:String> 
    </rdfq:equals>
    <rdfq:equals>
      <rdfq:Property name="Audio:Album" />
      <rdf:String></rdf:String> 
    </rdfq:equals>
  </rdfq:or>
</rdfq:Condition>
"""


class TrackerBackend:

    def __init__ (self):
        print "Tracker backend up"
        bus = dbus.SessionBus ()
        self.tracker_metadata = bus.get_object (TRACKER, TRACKER_OBJ)
        self.iface_metadata = dbus.Interface (self.tracker_metadata,
                                              "org.freedesktop.Tracker.Metadata")

        self.tracker_search = bus.get_object (TRACKER, TRACKER_SEARCH_OBJ)
        self.iface_search = dbus.Interface (self.tracker_search,
                                            "org.freedesktop.Tracker.Search")
        
    def count_songs_wo_artist (self):
        return self.iface_metadata.GetCount ("Music", "*", RDF_NO_ARTIST)

    def count_songs_wo_title (self):
        return self.iface_metadata.GetCount ("Music", "*", RDF_NO_TITLE)

    def count_songs_wo_album (self):
        return self.iface_metadata.GetCount ("Music", "*", RDF_NO_ALBUM)

    def __run_rdf_query (self, rdf_query):
        results = self.iface_search.Query (-1, "Music",
                                           ["Audio:Artist",
                                            "Audio:Title",
                                            "Audio:Album",
                                            "File:Mime"],
                                           "", [], rdf_query, False,
                                           [], False, 0, 32000)
        return results

    def get_all_broken_songs (self):
        """
        Return tuples with the following fields:
        (uri, "Music", artist, title, album, mimetype)
        """
        return self.__run_rdf_query (RDF_ANY_MISSING_METADATA)
    
    def get_all_songs (self):
        return self.__run_rdf_query ("")


    def get_list_of_known_albums (self):
        return self.iface_metadata.GetUniqueValues ("Music",
                                                    ["Audio:Album"],
                                                    "", False, 0, 32000)

    def get_list_of_known_artists (self):
        return self.iface_metadata.GetUniqueValues ("Music",
                                                    ["Audio:Artist"],
                                                    "", False, 0, 32000)

    def get_all_pairs_artist_album (self):
        return self.iface_metadata.GetUniqueValues ("Music",
                                                    ["Audio:Artist", "Audio:Album"],
                                                    "", False, 0, 32000)

# Test
if __name__ == "__main__":

    tracker = TrackerBackend ()

    print "Songs without artist: " + str(tracker.count_songs_wo_artist ())

    results = tracker.get_songs_without_artist ()
    for r in results:
        print "'%s', '%s', '%s', '%s', '%s'" % (r[0], r[2], r[3], r[4], r[5])

    
    print "Songs without album " + str(tracker.count_songs_wo_album ())
    print "Songs without title " + str(tracker.count_songs_wo_title ())

    albums = tracker.get_list_of_known_albums ()
    print "%d different albums" % (len (albums))
    for a in albums:
        print a[0]
    
    print "\nAll songs:"
    print tracker.get_all_songs ()
