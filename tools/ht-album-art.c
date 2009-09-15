/*
 * gcc -o ht-albumart ht-album-art.c `pkg-config --cflags --libs hildon-thumbnail`
 */ 
#include <hildon-albumart-factory.h>
#include <hildon-thumbnail-factory.h>
#include <glib.h>

static gchar *artist = NULL;
static gchar *album = NULL;

static GOptionEntry   entries[] = {
	{ "artist", 'a', 0, G_OPTION_ARG_STRING, &artist,
          "Artist",
	  NULL,
	},
	{ "album", 'b', 0, G_OPTION_ARG_STRING, &album,
          "Album",
	  NULL,
	}
};

gint 
main (gint argc, gchar **argv)
{
        gchar          *album_art, *thumbnail, *album_art_uri;
        GOptionContext *context;

        g_type_init ();

	context = g_option_context_new ("- Ask image/thum path for album art");

	g_option_context_add_main_entries (context, entries, NULL);
	g_option_context_parse (context, &argc, &argv, NULL);


        if (!album) {
		gchar *help;

		g_printerr ("%s\n\n",
			    "Album is a mandatory field");

		help = g_option_context_get_help (context, TRUE, NULL);
		g_option_context_free (context);
		g_printerr ("%s", help);
		g_free (help);

		return -1;
        }

        /*
         * USE NULL for artist!!! (It is what UKMP and media player use!)
         */
        album_art = hildon_albumart_get_path (NULL, album, "album");
        g_print ("album art: %s\n", album_art);

        /*
         * USE uri!!! (Not path)
         */
        album_art_uri = g_filename_to_uri (album_art, NULL, NULL);
        thumbnail = hildon_thumbnail_get_uri (album_art_uri, 124, 124, FALSE);
        g_print ("thumbnail (using uri): %s\n", thumbnail);

        g_free (album_art);
        g_free (thumbnail);
        g_free (album_art_uri);

        return 0;
}
