#!/usr/bin/env python2.5
 
from distutils.core import setup

import os

SCRIPTS=  ['data/mussorgsky']

DATA = [('share/applications/hildon', ['data/mussorgsky.desktop']),
        ('share/dbus-1/services', ['data/mussorgsky.service']),
        ('share/pixmaps',['data/mussorgsky-icon.png']),
        ('lib/mussorgsky', ['src/aa_selection_dialog.py',
                            'src/album_art_panel.py',
                            'src/album_art_spec.py',
                            'src/album_art_thread.py',
                            'src/browse_panel.py',
                            'src/download_dialog.py',
                            'src/edit_panel_tm.py',
                            'src/fancy_button.py',
                            'src/mussorgsky.py',
                            'src/mutagen_backend.py',                            
                            'src/player_backend.py',
                            'src/tracker_backend.py',
                            'src/utils.py'])]
 
setup(name         = 'mussorgsky',
      version      = '0.3',
      description  = 'Music Organizer: metadata editor',
      author       = 'Ivan Frade',
      author_email = '<ivan.frade@gmail.com>',
      url          = 'http://mussorgsky.garage.maemo.org',
      license      = 'GPL v2 or later',
      data_files   = DATA,
      scripts      = SCRIPTS
      )
