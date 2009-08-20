#!/usr/bin/env python2.5
 
from distutils.core import setup

import os

SCRIPTS=  ['data/mussorgsky']

DATA = [('share/applications/hildon', ['data/mussorgsky.desktop']),
        ('share/dbus-1/services', ['data/mussorgsky.service']),
        ('share/pixmaps',['data/mussorgsky-icon.png']),
        ('lib/mussorgsky', ['src/album_art.py',
                            'src/album_art_panel.py',
                            'src/album_art_spec.py',
                            'src/download_dialog.py',
                            'src/edit_panel.py',
                            'src/mussorgsky.py',
                            'src/mutagen_backend.py',                            
                            'src/player_backend.py',
                            'src/tracker_backend.py',
                            'src/utils.py'])]
 
setup(name         = 'mussorgsky',
      version      = '0.1',
      description  = 'Music Organizer: metadata editor',
      author       = 'Ivan Frade',
      author_email = '<ivan.frade@gmail.com>',
      url          = 'http://mussorgsky.garage.maemo.org',
      license      = 'GPL v2 or later',
      data_files   = DATA,
      scripts      = SCRIPTS
      )
