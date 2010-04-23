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
                                           ["Audio:DateAdded"], False, 0, 32000)
        return results

    def get_all_broken_songs (self):
        """
        Return tuples with the following fields:
        (uri, "Music", artist, title, album, mimetype)
        """
        return self.__run_rdf_query (RDF_ANY_MISSING_METADATA)
    
    def get_all_songs (self):
        """
        Return tuples with the following fields:
        (uri, "Music", artist, title, album, mimetype)
        """
        return self.__run_rdf_query ("")


    def get_list_of_known_albums (self):
        return self.iface_metadata.GetUniqueValues ("Music",
                                                    ["Audio:Album"],
                                                    "", False, 0, 32000)

    def get_list_of_known_artists (self):
        return self.iface_metadata.GetUniqueValues ("Music",
                                                    ["Audio:Artist"],
                                                    "", False, 0, 32000)

    def get_all_pairs_album_artist (self):
        return self.iface_metadata.GetUniqueValuesWithAggregates ("Music",
                                                                  ["Audio:Album"],
                                                                  "",
                                                                  ["CONCAT"],
                                                                  ["Audio:Artist"],
                                                                  False, 0, 32000)

# Test
if __name__ == "__main__":

    import sys
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option ("-n", "--numbers", dest="print_numbers",
                       action="store_true", default=True,
                       help="Print stats about broken files")
    
    parser.add_option ("-p", "--pairs", dest="pairs_artist_album",
                       action="store_true", default=True,
                       help="Print all pairs (album, artist)")

    (options, args) = parser.parse_args ()

    if (not options.print_numbers and not options.pairs_artist_album):
        parser.print_help ()
        sys.exit (-1)

    tracker = TrackerBackend ()
    if (options.print_numbers):
        print tracker.count_songs_wo_artist (), "Songs without artist"
        print tracker.count_songs_wo_title (), "Songs without title"
        print tracker.count_songs_wo_album (), "Songs without album"

    if (options.pairs_artist_album):
        for (album, artist) in tracker.get_all_pairs_artist_album ():
            print album,"-",artist

    
